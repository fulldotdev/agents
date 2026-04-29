#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import MAX_ITEMS_PER_LANE, NOTION_MEETINGS_DATA_SOURCE_ID, day_bounds_utc, iso_utc, notion_key, run


def notion_get_blocks(key, page_id):
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2025-09-03",
    ]
    return json.loads(run(cmd)).get("results", [])


def notion_get_block(key, block_id):
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/blocks/{block_id}",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2025-09-03",
    ]
    return json.loads(run(cmd))


def rich_text_text(obj):
    if not isinstance(obj, dict):
        return ""
    return "".join(part.get("plain_text", "") for part in (obj.get("rich_text") or []))


def block_plain_text(block):
    btype = block.get("type")
    if not btype:
        return ""
    node = block.get(btype) or {}
    if "rich_text" in node:
        return rich_text_text(node).strip()
    return ""


def extract_summary_block(key, blocks):
    for block in blocks:
        if block.get("type") != "transcription":
            continue
        meta = block.get("transcription") or {}
        children = meta.get("children") or {}
        summary_block_id = children.get("summary_block_id")
        if not summary_block_id:
            continue
        try:
            summary_block = notion_get_block(key, summary_block_id)
            descendants = notion_get_blocks(key, summary_block_id) if summary_block.get("has_children") else []
        except Exception:
            continue
        lines = []
        head = block_plain_text(summary_block)
        if head:
            lines.append(head)
        for child in descendants:
            text = block_plain_text(child)
            if text:
                lines.append(text)
        text = "\n".join(lines).strip()
        if text:
            return text
    return ""


def collect_meetings(after_dt, before_dt):
    key = notion_key()
    if not key:
        return {"ok": False, "error": "missing notion api key", "items": []}
    payload = {
        "filter": {
            "and": [
                {"property": "Created", "created_time": {"on_or_after": iso_utc(after_dt)}},
                {"property": "Created", "created_time": {"on_or_before": iso_utc(before_dt)}}
            ]
        },
        "sorts": [{"property": "Last edited time", "direction": "descending"}],
        "page_size": 50
    }
    cmd = [
        "curl", "-sS", f"https://api.notion.com/v1/data_sources/{NOTION_MEETINGS_DATA_SOURCE_ID}/query",
        "-H", f"Authorization: Bearer {key}",
        "-H", "Notion-Version: 2025-09-03",
        "-H", "Content-Type: application/json",
        "--data", json.dumps(payload),
    ]
    data = json.loads(run(cmd))

    items = []
    for row in data.get("results", [])[:MAX_ITEMS_PER_LANE]:
        props = row.get("properties", {})
        title = "".join(part.get("plain_text", "") for part in ((props.get("Name") or {}).get("title") or []))
        summary = ""
        try:
            blocks = notion_get_blocks(key, row.get("id"))
            summary = extract_summary_block(key, blocks)
        except Exception:
            summary = ""
        items.append({
            "id": row.get("id"),
            "url": row.get("url"),
            "Name": title,
            "Summary": summary,
            "Last edited time": ((props.get("Last edited time") or {}).get("last_edited_time")),
            "Calendar event URL": ((props.get("Calendar event URL") or {}).get("url")),
        })
    return {"ok": True, "items": items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)
    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "Data Source": "meetings",
        **collect_meetings(after_dt, before_dt),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
