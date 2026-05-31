#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timedelta, timezone

from task_triage_common import MAX_ITEMS_PER_LANE, NOTION_TASKS_DATA_SOURCE_ID, iso_utc, notion_key, parse_window, parse_iso, run


RECENTLY_CLOSED_LOOKBACK_HOURS = 48


def collect_tasks(recently_closed_after_dt=None):
    key = notion_key()
    if not key:
        return {"ok": False, "error": "missing notion api key", "items": []}

    open_filter = {
        "and": [
            {"property": "Status", "status": {"does_not_equal": "Done"}},
            {"property": "Status", "status": {"does_not_equal": "Canceled"}}
        ]
    }
    if recently_closed_after_dt is not None:
        payload_filter = {
            "or": [
                open_filter,
                {
                    "and": [
                        {"property": "Status", "status": {"equals": "Done"}},
                        {"property": "Edited", "last_edited_time": {"on_or_after": iso_utc(recently_closed_after_dt)}}
                    ]
                },
                {
                    "and": [
                        {"property": "Status", "status": {"equals": "Canceled"}},
                        {"property": "Edited", "last_edited_time": {"on_or_after": iso_utc(recently_closed_after_dt)}}
                    ]
                }
            ]
        }
    else:
        payload_filter = open_filter

    payload = {
        "filter": payload_filter,
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": 100
    }
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/data_sources/{NOTION_TASKS_DATA_SOURCE_ID}/query",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2026-03-11",
        "-H", "Content-Type: application/json",
        "--data", json.dumps(payload),
    ]
    data = json.loads(run(cmd))

    items = []
    for row in data.get("results", [])[:MAX_ITEMS_PER_LANE]:
        items.append({
            "id": row.get("id"),
            "url": row.get("url"),
            "properties": row.get("properties", {}),
        })
    return {"ok": True, "items": items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--recently-closed-after")
    ap.add_argument("--recently-closed-lookback-hours", type=int, default=RECENTLY_CLOSED_LOOKBACK_HOURS)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    _, before_dt = parse_window(args.after, args.before)
    recently_closed_after_dt = parse_iso(args.recently_closed_after) if args.recently_closed_after else before_dt - timedelta(hours=args.recently_closed_lookback_hours)
    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "tasks",
        "recently_closed_after": iso_utc(recently_closed_after_dt),
        **collect_tasks(recently_closed_after_dt=recently_closed_after_dt),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
