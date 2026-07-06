#!/usr/bin/env python3
import argparse
from common import NOTION_CUSTOMERS_DATA_SOURCE_ID, add_args, base_result, customer_item, emit, notion_query

ACTIVE_STATUSES = ["Prospect", "Active"]


def collect(limit):
    filters = [{"property": "Status", "status": {"equals": s}} for s in ACTIVE_STATUSES]
    data = notion_query(NOTION_CUSTOMERS_DATA_SOURCE_ID, {
        "filter": {"or": filters},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [customer_item(row) for row in data.get("results") or []]


def main():
    p = argparse.ArgumentParser(description="List active/prospect Customers for matching planning work.")
    add_args(p)
    args = p.parse_args()
    r = base_result("active_customers", "prospect_active")
    r["statuses"] = ACTIVE_STATUSES
    try:
        r["items"] = collect(args.limit)
        r["count"] = len(r["items"])
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "active_customers", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
