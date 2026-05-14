#!/usr/bin/env python3
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

TRIAGE_SCRIPTS = Path.home() / ".agents" / "skills" / "triage" / "scripts"
sys.path.insert(0, str(TRIAGE_SCRIPTS))
from task_triage_common import NOTION_TASKS_DATA_SOURCE_ID, iso_utc, notion_key, run

DEFAULT_STATUSES = ["Doing", "Todo"]

def collect(statuses):
    key = notion_key()
    if not key:
        return {"ok": False, "error": "missing notion api key", "items": []}
    status_filters = [{"property": "Status", "status": {"equals": s}} for s in statuses]
    payload = {
        "filter": {"or": status_filters} if len(status_filters) > 1 else status_filters[0],
        "sorts": [
            {"property": "Status", "direction": "ascending"},
            {"property": "Date", "direction": "ascending"},
            {"property": "Edited", "direction": "descending"},
        ],
        "page_size": 100,
    }
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/data_sources/{NOTION_TASKS_DATA_SOURCE_ID}/query",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2026-03-11",
        "-H", "Content-Type: application/json",
        "--data", json.dumps(payload),
    ]
    data = json.loads(run(cmd))
    return {"ok": True, "items": [{"id": r.get("id"), "url": r.get("url"), "properties": r.get("properties", {})} for r in data.get("results", [])]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="append", choices=["Todo", "Doing", "Waiting", "Backlog", "Triage", "Done", "Canceled"], help="Repeatable; defaults to Doing + Todo")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    result = {"generated_at": iso_utc(datetime.now(timezone.utc)), "lane": "execution", "statuses": args.status or DEFAULT_STATUSES, **collect(args.status or DEFAULT_STATUSES)}
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))

if __name__ == "__main__":
    main()
