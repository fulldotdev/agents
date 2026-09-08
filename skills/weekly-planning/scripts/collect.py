#!/usr/bin/env python3
"""Read-only weekly inventory, source coverage and next-week calendar. No triage cursors."""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SKILLS = Path(__file__).resolve().parents[2]
import store

SOURCES = ("gmail", "slack", "whatsapp", "calendar", "meetings", "t3_threads")
IDS = {"projects": "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae", "tasks": "1cb5979e-268c-80e9-bd7d-000b00ac4424",
       "companies": "2635979e-268c-8191-b322-000bd3109d1c", "sprints": "3555979e-268c-807b-bdb4-000b86b48f90"}
TZ = ZoneInfo("Europe/Amsterdam")


def inventory(kind):
    terminal = {"projects": ["Completed", "Canceled"], "tasks": ["Done", "Canceled"]}.get(kind)
    filters = {"and": [{"property": "Status", "status": {"does_not_equal": status}} for status in terminal]} if terminal else None
    return {"ok": True, "complete": True, "items": store.query(IDS[kind], filters)}


def problems(value):
    if isinstance(value, dict):
        if value.get("ok") is False or value.get("complete") is False or value.get("has_more") or value.get("nextPageToken") or value.get("next_cursor") or value.get("truncated") or value.get("body_error"):
            return True
        # Existing collectors have multiple shapes. Saturation is unresolved
        # coverage, even when an API returned success at the requested cap.
        for key, child in value.items():
            if key == "thread_replies" and isinstance(child, list) and len(child) >= 50:
                return True
            if key in {"message_count", "item_count"} and isinstance(child, int) and child >= 200:
                return True
            if key in {"items", "messages", "threads", "events"} and isinstance(child, list) and len(child) >= 200:
                return True
            if problems(child):
                return True
    elif isinstance(value, list):
        return any(problems(child) for child in value)
    return False


def source(name, after, before, depth=0):
    command = [sys.executable, str(SKILLS / "work-triage/scripts/collect.py"), "source", name,
               "--after", after.isoformat(), "--before", before.isoformat(), "--limit", "200"]
    environment = {**os.environ, "SLACK_TRIAGE_MODE": "all"}
    process = subprocess.run(command, capture_output=True, text=True, timeout=420, env=environment)
    if process.returncode:
        raise RuntimeError(process.stderr[:1200])
    value = json.loads(process.stdout)
    saturated = name == "whatsapp" and sum(len(chat.get("messages", [])) for chat in value.get("result", {}).get("items", [])) >= 200
    saturated = saturated or (name == "meetings" and len(value.get("result", {}).get("items", [])) >= 100)
    if name in {"gmail", "calendar"}:
        saturated = saturated or any(s.get("complete") is False or s.get("message_count", 0) >= 200 or len(s.get("items", [])) >= 200 for s in value.get("result", {}).get("sources", []))
    if saturated and depth < 5 and before - after > timedelta(hours=1):
        midpoint = after + (before - after) / 2
        parts = [source(name, after, midpoint, depth + 1), source(name, midpoint, before, depth + 1)]
        complete = all(part["complete"] for part in parts)
        return {"ok": complete, "complete": complete, "after": after.isoformat(), "before": before.isoformat(), "parts": parts}
    complete = not problems(value) and not saturated
    return {"ok": complete, "complete": complete, "after": after.isoformat(), "before": before.isoformat(), "data": value}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notion-only", action="store_true")
    parser.add_argument("--source", action="append", choices=SOURCES)
    parser.add_argument("--output", required=True, help="Temporary raw collection file; Notion owns durable outcomes")
    args = parser.parse_args()
    current = datetime.now(TZ)
    monday = (current + timedelta(days=(7 - current.weekday()) % 7 or 7)).replace(hour=0, minute=0, second=0, microsecond=0)
    calls = {kind: lambda kind=kind: inventory(kind) for kind in IDS}
    if not args.notion_only:
        calls.update({name: lambda name=name: source(name, current - timedelta(days=7), current) for name in args.source or SOURCES})
        calls["upcoming_calendar"] = lambda: source("calendar", monday, monday + timedelta(days=7))
    result = {"generated_at": current.isoformat(), "week": monday.date().isoformat(), "lanes": {},
              "monday_boards": {"status": "requires_browser_read", "boards": {"teveo": "1853861128", "fayn": "1780576681"}},
              "triage_state_changed": False}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fn): name for name, fn in calls.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result["lanes"][name] = future.result()
            except Exception as exc:
                result["lanes"][name] = {"ok": False, "complete": False, "error": str(exc)[:1500]}
    result["complete"] = all(lane["complete"] for lane in result["lanes"].values())
    destination = Path(args.output).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    destination.chmod(0o600)
    print(json.dumps({"file": str(destination), "week": result["week"], "source_collection_complete": result["complete"],
                      "coverage": {name: {key: value for key, value in lane.items() if key in {"ok", "complete", "error"}} for name, lane in result["lanes"].items()},
                      "monday_boards": result["monday_boards"]}, indent=2))


if __name__ == "__main__":
    main()
