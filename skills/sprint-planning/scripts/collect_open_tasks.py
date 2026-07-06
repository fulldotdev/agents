#!/usr/bin/env python3
import argparse
from common import NOTION_TASKS_DATA_SOURCE_ID, add_args, base_result, emit, notion_query, task_item

OPEN_STATUSES = ["Triage", "Backlog", "Todo", "Doing", "Waiting"]


def collect(limit):
    filters = [{"property": "Status", "status": {"equals": s}} for s in OPEN_STATUSES]
    data = notion_query(NOTION_TASKS_DATA_SOURCE_ID, {
        "filter": {"or": filters},
        "sorts": [{"property": "Due", "direction": "ascending"}, {"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [task_item(row) for row in data.get("results") or []]


def main():
    p = argparse.ArgumentParser(description="List all open Tasks useful for Sprint planning.")
    add_args(p)
    args = p.parse_args()
    r = base_result("open_tasks", "triage_backlog_todo_doing_waiting")
    r["statuses"] = OPEN_STATUSES
    try:
        r["items"] = collect(args.limit)
        r["count"] = len(r["items"])
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "open_tasks", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
