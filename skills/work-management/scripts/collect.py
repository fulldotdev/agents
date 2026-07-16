#!/usr/bin/env python3
"""Single public CLI for work-management context collection."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import calendar as calendar_source
import codex
import gmail
import meetings
import notion
import slack
import whatsapp
from common import (
    DEFAULT_CALENDAR_ACCOUNTS, DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS,
    MAX_ITEMS_PER_LANE, base_result, emit, error_obj,
    window_from_args,
)

SOURCES = ("gmail", "slack", "whatsapp", "calendar", "meetings", "codex")
TRIAGE_TZ = ZoneInfo("Europe/Amsterdam")


def output_args(parser):
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    parser.add_argument("--pretty", action="store_true")


def window_args(parser, required=False):
    parser.add_argument("--after", required=required)
    parser.add_argument("--before", required=required)


def incoming_window(after, before):
    before = before or datetime.now(timezone.utc)
    local_before = before.astimezone(TRIAGE_TZ)
    local_start = datetime.combine(local_before.date(), datetime.min.time(), TRIAGE_TZ)
    return after or local_start - timedelta(days=1), before


def collect_source(name, after, before, args, triage_context=False):
    if name == "gmail":
        accounts = args.account or DEFAULT_GMAIL_ACCOUNTS
        sources = []
        for account in accounts:
            try:
                sources.append(gmail.collect_account(account, after, before, args.query))
            except Exception as exc:
                sources.append(error_obj(account, exc))
        return {"sources": sources, "ok": all(item.get("ok", True) for item in sources)}
    if name == "slack":
        return {"items": slack.collect(after, before, args.query)}
    if name == "whatsapp":
        return {"items": whatsapp.collect(after, before)}
    if name == "calendar":
        sources = calendar_source.collect(after, before, args.account, args.limit, triage_context)
        return {"sources": sources, "ok": all(item.get("ok", True) for item in sources)}
    if name == "meetings":
        return {"items": meetings.collect(after, before)}
    return codex.collect(
        after, before, args.include_archived, args.limit, args.project,
        args.query, args.thread_id, args.detail_events,
    )


def mark_errors(result, name, value):
    failures = [item for item in value.get("items") or [] if isinstance(item, dict) and item.get("ok") is False]
    failures += [item for item in value.get("sources") or [] if isinstance(item, dict) and item.get("ok") is False]
    if failures:
        value["ok"] = False
        value["errors"] = failures
        result["errors"].append({"source": name, "ok": False, "errors": failures, "items": []})
        result["ok"] = False
    else:
        value.setdefault("ok", True)


def collect_incoming(after, before, args):
    after, before = incoming_window(after, before)
    selected = args.source or list(SOURCES)
    result = base_result("incoming", "window", after, before)
    result.pop("items")
    result["sources"] = {}
    with ThreadPoolExecutor(max_workers=len(selected)) as executor:
        futures = {executor.submit(collect_source, name, after, before, args, True): name for name in selected}
        for future in as_completed(futures):
            name = futures[future]
            try:
                value = future.result()
                mark_errors(result, name, value)
                result["sources"][name] = value
            except Exception as exc:
                error = error_obj(name, exc)
                result["sources"][name] = error
                result["errors"].append(error)
                result["ok"] = False
    return result


def triage(args):
    after, before = window_from_args(args.after, args.before)
    result = base_result("work_management", "triage", after, before)
    result.pop("items")
    result["groups"] = {}
    calls = {
        "incoming": lambda: collect_incoming(after, before, args),
        "work_context": lambda: notion.collect_work_context(after, before, args.limit),
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(fn): name for name, fn in calls.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                value = future.result()
                result["groups"][name] = value
                if not value.get("ok", False):
                    result["errors"].extend(value.get("errors", []))
                    result["ok"] = False
            except Exception as exc:
                error = error_obj(name, exc)
                result["groups"][name] = error
                result["errors"].append(error)
                result["ok"] = False
    return result


def planning(args):
    after, before = window_from_args(args.after, args.before, require=True)
    result = base_result("work_management", "planning", after, before)
    result.pop("items")
    with ThreadPoolExecutor(max_workers=2) as executor:
        work_future = executor.submit(notion.collect_planning, after, before, args.after, args.before, args.limit)
        calendar_future = executor.submit(calendar_source.collect, after, before, args.account, args.limit, False)
        try:
            result["work"] = work_future.result()
        except Exception as exc:
            result["work"] = error_obj("notion", exc)
        try:
            sources = calendar_future.result()
            result["calendar"] = {"ok": all(item.get("ok", True) for item in sources), "sources": sources}
            if not result["calendar"]["ok"]:
                result["calendar"]["errors"] = [item for item in sources if not item.get("ok", True)]
        except Exception as exc:
            result["calendar"] = error_obj("calendar", exc)
    for value in (result["work"], result["calendar"]):
        if not value.get("ok", False):
            result["errors"].extend(value.get("errors", [value]))
            result["ok"] = False
    return result


def source(args):
    require_window = args.name in {"whatsapp", "calendar", "meetings"} or (args.name == "slack" and not args.query)
    after, before = (None, None) if args.all or args.thread_id or (args.query and args.name == "gmail") else window_from_args(
        args.after, args.before, require=require_window
    )
    result = base_result(args.name, "source", after, before)
    result.pop("items")
    try:
        value = collect_source(args.name, after, before, args, args.context)
        result["result"] = value
        mark_errors(result, args.name, value)
    except Exception as exc:
        error = error_obj(args.name, exc)
        result["result"] = error
        result["errors"].append(error)
        result["ok"] = False
    return result


def build_parser():
    parser = argparse.ArgumentParser(description="Collect agency triage, planning, or one source.")
    commands = parser.add_subparsers(dest="command", required=True)

    triage_parser = commands.add_parser("triage", help="collect incoming lanes plus Notion work context")
    window_args(triage_parser)
    output_args(triage_parser)
    triage_parser.add_argument("--source", action="append", choices=SOURCES)
    triage_parser.add_argument("--account", action="append")
    triage_parser.add_argument("--query")
    triage_parser.add_argument("--limit", type=int, default=MAX_ITEMS_PER_LANE)
    triage_parser.add_argument("--include-archived", action="store_true")
    triage_parser.add_argument("--project")
    triage_parser.add_argument("--thread-id")
    triage_parser.add_argument("--detail-events", type=int, default=codex.DEFAULT_DETAIL_EVENTS)


    planning_parser = commands.add_parser("planning", help="collect Sprint review and planning context")
    window_args(planning_parser, required=True)
    output_args(planning_parser)
    planning_parser.add_argument("--account", action="append")
    planning_parser.add_argument("--limit", type=int, default=MAX_ITEMS)

    source_parser = commands.add_parser("source", help="collect one source for focused follow-up")
    source_parser.add_argument("name", choices=SOURCES)
    window_args(source_parser)
    output_args(source_parser)
    source_parser.add_argument("--account", action="append")
    source_parser.add_argument("--query")
    source_parser.add_argument("--context", action="store_true", help="include short context around Calendar window")
    source_parser.add_argument("--all", action="store_true", help="ignore time window for Codex")
    source_parser.add_argument("--include-archived", action="store_true")
    source_parser.add_argument("--limit", type=int, default=MAX_ITEMS_PER_LANE)
    source_parser.add_argument("--project")
    source_parser.add_argument("--thread-id")
    source_parser.add_argument("--detail-events", type=int, default=codex.DEFAULT_DETAIL_EVENTS)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = {"triage": triage, "planning": planning, "source": source}[args.command](args)
    except ValueError as exc:
        parser.error(str(exc))
    emit(result, args.pretty, args.format)


if __name__ == "__main__":
    main()
