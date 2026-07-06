#!/usr/bin/env python3
import argparse
from common import NOTION_SPRINTS_DATA_SOURCE_ID, add_args, base_result, emit, notion_query, sprint_item


def collect(limit):
    data = notion_query(NOTION_SPRINTS_DATA_SOURCE_ID, {
        "sorts": [{"property": "Dates", "direction": "descending"}],
        "page_size": limit,
    })
    rows = data.get("results") or []
    items = [sprint_item(row) for row in rows]
    return items


def main():
    p = argparse.ArgumentParser(description="List recent/current Sprint pages for weekly planning.")
    add_args(p)
    args = p.parse_args()
    r = base_result("sprints", "recent_sprints")
    try:
        r["items"] = collect(args.limit)
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "sprints", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
