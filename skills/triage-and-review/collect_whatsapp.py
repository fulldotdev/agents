#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import MAX_ITEMS_PER_LANE, compact_text, day_bounds_utc, iso_utc, json_cmd



def collect_whatsapp(after_dt, before_dt):
    chats = {c.get("JID"): c for c in ((json_cmd(["wacli", "--json", "chats", "list"]).get("data")) or [])}
    data = json_cmd([
        "wacli", "--json", "messages", "list",
        "--after", iso_utc(after_dt),
        "--before", iso_utc(before_dt),
        "--limit", str(MAX_ITEMS_PER_LANE),
    ])
    grouped = {}
    for msg in (data.get("data") or {}).get("messages") or []:
        chat_id = msg.get("ChatJID")
        grouped.setdefault(chat_id, []).append({
            "from": msg.get("SenderJID"),
            "timestamp": msg.get("Timestamp"),
            "text": compact_text(msg.get("Text") or msg.get("DisplayText") or msg.get("Snippet") or "", 12000),
            "kind": "message" if not msg.get("MediaType") else "media",
            "media": {"type": msg.get("MediaType")} if msg.get("MediaType") else None,
        })
    items = []
    for chat_id, messages in grouped.items():
        chat = chats.get(chat_id) or {}
        items.append({
            "chat": chat.get("Name") or messages[0].get("from") or chat_id,
            "chat_id": chat_id,
            "messages": sorted(messages, key=lambda message: message.get("timestamp") or ""),
        })
    items.sort(key=lambda item: item["messages"][0].get("timestamp") if item.get("messages") else "", reverse=False)
    return {"ok": True, "items": items[:MAX_ITEMS_PER_LANE]}



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)
    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "whatsapp",
        "after": iso_utc(after_dt),
        "before": iso_utc(before_dt),
        **collect_whatsapp(after_dt, before_dt),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
