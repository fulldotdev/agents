#!/usr/bin/env python3
"""Single public CLI for recurring work-triage collection."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import calendar as calendar_source
import gmail
import incremental
import meetings
import notion
import slack
import t3_threads
import whatsapp
from common import (
    DEFAULT_CALENDAR_ACCOUNTS, DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE,
    base_result, emit, error_obj,
    iso_utc, window_from_args,
)

SOURCES = ("gmail", "slack", "whatsapp", "calendar", "meetings", "t3_threads")
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
        return slack.collect_result(after, before, args.query, getattr(args, "workspace", None))
    if name == "whatsapp":
        return {"items": whatsapp.collect(after, before)}
    if name == "calendar":
        sources = calendar_source.collect(after, before, args.account, args.limit, triage_context)
        return {"sources": sources, "ok": all(item.get("ok", True) for item in sources)}
    if name == "meetings":
        return {"items": meetings.collect(after, before)}
    return t3_threads.collect(
        after, before, args.include_archived, args.limit, args.project,
        args.query, args.thread_id, args.turn_limit,
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
    if args.incremental:
        return incremental_triage(args)
    after, before = window_from_args(args.after, args.before)
    result = base_result("work_triage", "triage", after, before)
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


def incremental_triage(args):
    before = window_from_args(None, args.before)[1]
    initial_after = window_from_args(args.after, args.before)[0]
    state_path = args.state_file or incremental.DEFAULT_STATE_FILE
    state = incremental.load(state_path)
    selected = args.source or list(SOURCES)
    result = base_result("work_triage", "incremental_triage", initial_after, before)
    result.pop("items")
    result["state_file"] = str(state_path)
    result["groups"] = {"incoming": {"ok": True, "sources": {}, "errors": []}}

    calls = {}
    windows = {}
    for name in selected:
        after, lane_before = incremental.window(
            state, name, before, args.bootstrap_hours, args.overlap_minutes, initial_after
        )
        windows[name] = (after, lane_before)
        calls[name] = lambda name=name, after=after, lane_before=lane_before: collect_source(
            name, after, lane_before, args, True
        )

    wc_after, wc_before = incremental.window(
        state, "work_context", before, args.bootstrap_hours, args.overlap_minutes, initial_after
    )
    windows["work_context"] = (wc_after, wc_before)
    calls["work_context"] = lambda: notion.collect_changed_work_context(
        wc_after, wc_before, iso_utc(wc_after), iso_utc(wc_before), args.limit
    )

    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = {executor.submit(fn): name for name, fn in calls.items()}
        for future in as_completed(futures):
            name = futures[future]
            after, lane_before = windows[name]
            try:
                value = future.result()
                saturated = incremental.is_saturated(name, value, args.limit)
                if name != "work_context":
                    lane_result = {"ok": True, "errors": []}
                    mark_errors(lane_result, name, value)
                    if not lane_result["ok"]:
                        value["ok"] = False
                seen = ((state.get("lanes") or {}).get(name) or {}).get("seen") or []
                value, signatures = incremental.filter_value(name, value, seen)
                value["after"] = iso_utc(after)
                value["before"] = iso_utc(lane_before)
                value["cursor_advanced"] = bool(value.get("ok", True) and not saturated)
                if saturated:
                    value["complete"] = False
                    value.setdefault("errors", []).append({
                        "source": name,
                        "ok": False,
                        "error_type": "window_saturated",
                        "error": f"collector reached lane limit {args.limit}; cursor was not advanced",
                        "items": [],
                    })
                if value.get("ok", True) and not saturated:
                    incremental.advance(state, name, lane_before, signatures)
                else:
                    result["ok"] = False
                    result["errors"].extend(value.get("errors") or [{"source": name, "ok": False}])
                    if name != "work_context":
                        result["groups"]["incoming"]["ok"] = False
                        result["groups"]["incoming"]["errors"].extend(value.get("errors") or [])
                if name == "work_context":
                    result["groups"]["work_context"] = value
                else:
                    result["groups"]["incoming"]["sources"][name] = value
            except Exception as exc:
                error = error_obj(name, exc)
                error.update({"after": iso_utc(after), "before": iso_utc(lane_before)})
                result["ok"] = False
                result["errors"].append(error)
                if name == "work_context":
                    result["groups"]["work_context"] = error
                else:
                    result["groups"]["incoming"]["sources"][name] = error
                    result["groups"]["incoming"]["errors"].append(error)
                    result["groups"]["incoming"]["ok"] = False

    if not args.no_commit_state:
        incremental.save(state, state_path)
    result["state_committed"] = not args.no_commit_state
    result["changed_count"] = sum(
        value.get("changed_count", 0)
        for value in result["groups"]["incoming"]["sources"].values()
    ) + (result["groups"].get("work_context") or {}).get("changed_count", 0)
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
    parser = argparse.ArgumentParser(description="Collect work triage or one focused source.")
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
    triage_parser.add_argument("--turn-limit", type=int, default=t3_threads.DEFAULT_TURN_LIMIT)
    triage_parser.add_argument("--incremental", action="store_true", help="use per-lane cursors and overlap dedupe")
    triage_parser.add_argument("--state-file", type=str, help="override incremental cursor state path")
    triage_parser.add_argument("--overlap-minutes", type=int, default=incremental.DEFAULT_OVERLAP_MINUTES)
    triage_parser.add_argument("--bootstrap-hours", type=int, default=incremental.DEFAULT_BOOTSTRAP_HOURS)
    triage_parser.add_argument("--no-commit-state", action="store_true", help="preview incremental results without advancing cursors")
    source_parser = commands.add_parser("source", help="collect one source for focused follow-up")
    source_parser.add_argument("name", choices=SOURCES)
    window_args(source_parser)
    output_args(source_parser)
    source_parser.add_argument("--account", action="append")
    source_parser.add_argument("--query")
    source_parser.add_argument("--workspace", help="Slack workspace slug, such as fulldotdev or small-giants")
    source_parser.add_argument("--context", action="store_true", help="include short context around Calendar window")
    source_parser.add_argument("--all", action="store_true", help="ignore the source time window")
    source_parser.add_argument("--include-archived", action="store_true")
    source_parser.add_argument("--limit", type=int, default=MAX_ITEMS_PER_LANE)
    source_parser.add_argument("--project")
    source_parser.add_argument("--thread-id")
    source_parser.add_argument("--turn-limit", type=int, default=t3_threads.DEFAULT_TURN_LIMIT)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = {"triage": triage, "source": source}[args.command](args)
    except ValueError as exc:
        parser.error(str(exc))
    emit(result, args.pretty, args.format)


if __name__ == "__main__":
    main()
