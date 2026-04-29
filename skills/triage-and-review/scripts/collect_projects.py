#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import MAX_ITEMS_PER_LANE, iso_utc, notion_key, run

NOTION_PROJECTS_DATA_SOURCE_ID = "2635979e-268c-8191-b322-000bd3109d1c"


def collect_projects():
    key = notion_key()
    if not key:
        return {"ok": False, "error": "missing notion api key", "items": []}

    payload = {
        "sorts": [{"property": "Last edited time", "direction": "descending"}],
        "page_size": 100,
    }
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/data_sources/{NOTION_PROJECTS_DATA_SOURCE_ID}/query",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2025-09-03",
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
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "Data Source": "projects",
        **collect_projects(),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
