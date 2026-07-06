#!/usr/bin/env python3
import argparse
from common import NOTION_PROJECTS_DATA_SOURCE_ID, add_args, base_result, emit, notion_query, project_item

ACTIVE_STATUSES = ["Discovery", "Planned", "In Progress", "Paused"]


def collect(limit):
    filters = [{"property": "Status", "status": {"equals": s}} for s in ACTIVE_STATUSES]
    data = notion_query(NOTION_PROJECTS_DATA_SOURCE_ID, {
        "filter": {"or": filters},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [project_item(row) for row in data.get("results") or []]


def main():
    p = argparse.ArgumentParser(description="List active Projects for planning context.")
    add_args(p)
    args = p.parse_args()
    r = base_result("active_projects", "discovery_planned_in_progress_paused")
    r["statuses"] = ACTIVE_STATUSES
    try:
        r["items"] = collect(args.limit)
        r["count"] = len(r["items"])
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "active_projects", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
