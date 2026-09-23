#!/usr/bin/env python3
"""Collect new work for one triage run, or read one source in detail."""

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import calendar as calendar_source
import gmail
import meetings
import notion
import slack
import t3_threads
import whatsapp
from common import (
    DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE, base_result, emit, error_obj, iso_utc, parse_iso,
    window_from_args, title, prop_time,
)

SOURCES = ("gmail", "slack", "whatsapp", "calendar", "meetings", "t3_threads")
UPCOMING_CALENDAR_DAYS = 2


def with_refs(lane, items, key):
    for item in items:
        item["ref"] = f"{lane}:{item.get(key)}"
    return items


def gmail_items(after, before, retry_items=()):
    items, errors = [], []
    for account in DEFAULT_GMAIL_ACCOUNTS:
        try:
            result = gmail.collect_account(account, after, before)
            if not result["complete"]:
                raise RuntimeError("Incomplete Gmail message index")
            threads = {t["id"]: t for t in retry_items if t.get("account") == account}
            threads.update({t["id"]: t for t in result["items"]})
        except Exception as exc:
            errors.append(f"{account}: {exc}")
            continue
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(gmail.conversation, thread): thread for thread in threads.values()}
            for future in as_completed(futures):
                try:
                    item = future.result()
                    item.pop("collection_error", None)
                    items.append(item)
                except Exception as exc:
                    item = dict(futures[future])
                    item["collection_error"] = str(exc)
                    items.append(item)
    if errors:
        raise RuntimeError("; ".join(errors))
    return with_refs("gmail", items, "id")


def slack_items(after, before, retry_items=()):
    result = slack.collect_result(after, before, retry_items=retry_items)
    failures = [item for item in result["items"] if item.get("ok") is False]
    if failures:
        raise RuntimeError("; ".join(str(item.get("error")) for item in failures))
    for item in result["items"]:
        item["ref"] = slack_ref(item)
    return result["items"]


def slack_ref(item):
    return f"slack:{item.get('workspace_slug')}:{item.get('channel_id')}:{item.get('thread_ts') or item.get('ts')}"


def whatsapp_items(after, before):
    chats = [
        chat for chat in whatsapp.collect(after, before)
        if chat["chat_id"] != "status@broadcast"
    ]
    return with_refs("whatsapp", chats, "chat_id")


def calendar_items(after, before):
    now = datetime.now(timezone.utc)
    items, errors = [], []
    for source in calendar_source.collect(after, before, context=True):
        if source.get("ok") is False:
            errors.append(str(source.get("error")))
            continue
        for event in source["items"]:
            start = parse_iso(event.get("start"))
            upcoming = bool(start and now <= start < now + timedelta(days=UPCOMING_CALENDAR_DAYS))
            if event.get("changed_in_window") or upcoming:
                event["upcoming"] = upcoming
                for key in ("event_in_window", "event_in_context_window"):
                    event.pop(key, None)
                items.append(event)
    if errors:
        raise RuntimeError("; ".join(errors))
    for item in items:
        item["ref"] = f"calendar:{item['source_account']}:{item['calendar_id']}:{item['id']}"
    return items


def calendar_copies(item):
    """Expand a grouped item; each copy stores its differences from the first."""
    base = {k: v for k, v in item.items() if k != "calendar_copies"}
    return [{**base, **copy} for copy in item["calendar_copies"]] if "calendar_copies" in item else [base]


def group_calendar_items(items):
    copies = {}
    for item in items:
        for copy in calendar_copies(item):
            copies[copy["ref"]] = copy
    groups = {}
    for copy in copies.values():
        uid, original = copy.get("ical_uid"), copy.get("original_start")
        # A tombstone without a UID or an occurrence without its original start
        # cannot safely be matched with another calendar.
        if uid and (original or not copy.get("recurring_event_id")):
            key = [uid, parse_iso(original).isoformat() if original else None]
            ref = "calendar:meeting:" + hashlib.sha256(json.dumps(key).encode()).hexdigest()[:24]
        else:
            ref = copy["ref"]
        groups.setdefault(ref, []).append(copy)
    result = []
    for ref, group in groups.items():
        group.sort(key=lambda c: (
            bool((c.get("meeting_page") or {}).get("url")), c.get("updated") or "", c["ref"],
        ), reverse=True)
        item = dict(group[0])
        item["ref"] = ref
        item["calendar_copies"] = [
            {k: v for k, v in copy.items() if k in {"ref", "source_account", "calendar_id", "id"}
             or item.get(k) != v} for copy in group
        ]
        # Preserve a missing field too, rather than inheriting it from another copy.
        for copy, differences in zip(group, item["calendar_copies"]):
            differences.update({k: None for k in item if k not in copy and k != "calendar_copies"})
        result.append(item)
    return result


def meeting_items(after, before):
    items = meetings.collect(after, before, include_body=False)
    for item in items:
        item["name"] = title(item)
        item["created"] = prop_time(item, "Created")
        item["edited"] = prop_time(item, "Edited")
        item.pop("properties", None)
    return with_refs("meetings", items, "id")


def t3_items(after, before):
    return with_refs("t3_threads", t3_threads.collect(
        after, before, include_archived=True, include_settled=True,
    )["items"], "thread_id")


LANES = {
    "gmail": gmail_items, "slack": slack_items, "whatsapp": whatsapp_items,
    "calendar": calendar_items, "meetings": meeting_items, "t3_threads": t3_items,
}


def names(ids, table):
    return [table[i]["name"] for i in ids or [] if i in table]


def work_index():
    """All Tasks (open, plus closed today), Projects and Companies, with names instead of IDs."""
    work = notion.collect_work_context()
    if not work.get("ok"):
        raise RuntimeError("; ".join(str(e.get("error")) for e in work.get("errors") or []) or "Notion index failed")
    lanes = work["lanes"]
    companies = {c["id"]: c for c in lanes["companies"]["items"]}
    projects = {p["id"]: p for p in lanes["projects"]["items"]}
    return {
        "companies": [{
            "id": c["id"], "name": c["name"], "status": c["status"],
            "website": c["website"], "url": c["url"],
        } for c in companies.values()],
        "projects": [{
            "id": p["id"], "name": p["name"], "status": p["status"],
            "companies": names(p["companies"], companies), "parent_project": names(p["parent_project"], projects),
            "deadline": (p.get("deadline") or {}).get("start"), "url": p["url"],
        } for p in projects.values()],
        "tasks": [{
            "id": t["id"], "name": t["name"], "status": t["status"], "area": t["area"],
            "project": names(t["project"], projects), "companies": names(t["companies"], companies),
            "date": (t.get("date") or {}).get("start"), "url": t["url"],
        } for t in lanes["tasks"]["items"]],
    }


def t3_index():
    """All open T3 threads."""
    return [{
        "thread_id": t["thread_id"], "title": t["title"], "project": t["project"]["name"],
        "branch": t["checkout"]["branch"], "session": t["state"]["session"], "latest_turn": t["state"]["latest_turn"],
        "snoozed_until": t["state"]["snoozed_until"], "pending_approval": t["state"]["pending_approval"],
        "pending_user_input": t["state"]["pending_user_input"], "last_activity_at": t["last_activity_at"],
    } for t in t3_threads.collect()["items"]]


def batch(windows, retries=()):
    """Collect every lane in parallel. Returns items per lane, the index, and per-lane errors."""
    result = {"items": {}, "index": {}, "failed": {}}
    calls = {lane: (lambda lane=lane: LANES[lane](*windows[lane])) for lane in windows}
    for lane in ("gmail", "slack"):
        if lane in windows:
            pending = [r["item"] for r in retries if r["ref"].startswith(lane + ":")
                       and r["item"].get("collection_error")]
            calls[lane] = lambda lane=lane, pending=pending: LANES[lane](*windows[lane], retry_items=pending)
    calls["index"] = work_index
    calls["t3_open_threads"] = t3_index
    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = {executor.submit(fn): name for name, fn in calls.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                value = future.result()
            except Exception as exc:
                result["failed"][name] = str(exc)
                continue
            if name == "index":
                result["index"].update(value)
            elif name == "t3_open_threads":
                result["index"]["t3_open_threads"] = value
            else:
                result["items"][name] = value
    return result


def source(args):
    """One focused read, for follow-up during a run."""
    name = args.name
    after, before = (None, None) if args.all or args.thread_id or (args.query and name == "gmail") else window_from_args(
        args.after, args.before, require=name in {"whatsapp", "calendar", "meetings"} or (name == "slack" and not args.query)
    )
    result = base_result(name, "source", after, before)
    result.pop("items")
    try:
        if name == "gmail":
            accounts = args.account or DEFAULT_GMAIL_ACCOUNTS
            result["result"] = [
                gmail.read_thread(account, args.thread_id, args.download) if args.thread_id
                else gmail.collect_account(account, after, before, args.query, args.limit)
                for account in accounts
            ]
        elif name == "slack":
            result["result"] = slack.collect_result(after, before, args.query, args.workspace)
        elif name == "whatsapp":
            result["result"] = whatsapp.collect(after, before, recover_media=False)
        elif name == "calendar":
            result["result"] = calendar_source.collect(after, before, args.account, args.limit, True)
        elif name == "meetings":
            result["result"] = meetings.collect(after, before)
        else:
            result["result"] = t3_threads.collect(after, before, args.include_archived, args.limit, args.project, args.query, args.thread_id, args.turn_limit, args.include_settled)
    except Exception as exc:
        result["ok"] = False
        result["errors"].append(error_obj(name, exc))
    return result


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    batch_parser = commands.add_parser("batch", help="collect all lanes for a window (the runner does this)")
    batch_parser.add_argument("--after", required=True)
    batch_parser.add_argument("--before")
    batch_parser.add_argument("--format", choices=["json", "yaml"], default="yaml")
    source_parser = commands.add_parser("source", help="read one source in detail")
    source_parser.add_argument("name", choices=SOURCES)
    source_parser.add_argument("--after")
    source_parser.add_argument("--before")
    source_parser.add_argument("--format", choices=["json", "yaml"], default="yaml")
    source_parser.add_argument("--pretty", action="store_true")
    source_parser.add_argument("--account", action="append")
    source_parser.add_argument("--query")
    source_parser.add_argument("--workspace", help="Slack workspace slug")
    source_parser.add_argument("--all", action="store_true", help="ignore the time window")
    source_parser.add_argument("--include-archived", action="store_true")
    source_parser.add_argument("--include-settled", action="store_true")
    source_parser.add_argument("--limit", type=int, default=MAX_ITEMS_PER_LANE)
    source_parser.add_argument("--project")
    source_parser.add_argument("--thread-id", help="Gmail or T3 thread")
    source_parser.add_argument("--download", action="store_true", help="download attachments of a Gmail thread")
    source_parser.add_argument("--turn-limit", type=int, default=t3_threads.DEFAULT_TURN_LIMIT)
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "batch":
        after, before = window_from_args(args.after, args.before, require=True)
        result = batch({lane: (after, before) for lane in SOURCES})
        result.update(after=iso_utc(after), before=iso_utc(before))
        emit(result, output_format=args.format)
    else:
        emit(source(args), getattr(args, "pretty", False), args.format)


if __name__ == "__main__":
    main()
