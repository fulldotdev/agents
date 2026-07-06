#!/usr/bin/env python3
import argparse
from common import NOTION_TASKS_DATA_SOURCE_ID, add_args, base_result, emit, notion_query, parse_iso, prop_time, task_item

REVIEW_STATUSES = ["Done", "Canceled", "Waiting", "Doing"]


def collect(after, before, limit):
    filters = [{"property": "Edited", "last_edited_time": {"on_or_after": after, "before": before}}]
    data = notion_query(NOTION_TASKS_DATA_SOURCE_ID, {
        "filter": {"and": filters},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    rows = []
    for row in data.get("results") or []:
        item = task_item(row)
        # Keep all edited tasks; status field lets planning decide completed/carried/blocked.
        rows.append(item)
    return rows


def main():
    p = argparse.ArgumentParser(description="Tasks edited in a review window for Sprint review/carry-over.")
    add_args(p)
    p.add_argument("--after", required=True, help="ISO start of previous review week")
    p.add_argument("--before", required=True, help="ISO end of previous review week")
    args = p.parse_args()
    r = base_result("review_tasks", "tasks_edited_in_window")
    r["after"] = args.after; r["before"] = args.before
    try:
        # Validate timestamps early.
        parse_iso(args.after); parse_iso(args.before)
        r["items"] = collect(args.after, args.before, args.limit)
        r["count"] = len(r["items"])
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "review_tasks", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
