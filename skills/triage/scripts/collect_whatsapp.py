#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from task_triage_common import MAX_ITEMS_PER_LANE, compact_text, day_bounds_utc, iso_utc, json_cmd



def _wacli_store_dir():
    return Path(os.environ.get("WACLI_STORE_DIR") or Path.home() / ".wacli").expanduser()


def _media_chat_dir(chat_id):
    return chat_id.replace("@", "_") if chat_id else ""


def _local_media(chat_id, msg_id):
    media_dir = _wacli_store_dir() / "media" / _media_chat_dir(chat_id) / msg_id
    existing = []
    if media_dir.exists():
        existing = [str(p) for p in sorted(media_dir.rglob("*")) if p.is_file()]
    return {
        "saved_dir": str(media_dir),
        "saved_paths": existing,
        **({} if existing else {"error": "media_not_downloaded_yet"}),
    }



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
        msg_id = msg.get("MsgID")
        media_type = msg.get("MediaType")
        media = None
        if media_type and chat_id and msg_id:
            download = _local_media(chat_id, msg_id)
            media = {
                "type": media_type,
                "display_text": msg.get("DisplayText"),
                **download,
            }
        elif media_type:
            media = {
                "type": media_type,
                "display_text": msg.get("DisplayText"),
            }
        grouped.setdefault(chat_id, []).append({
            "id": msg_id,
            "from": msg.get("SenderJID"),
            "timestamp": msg.get("Timestamp"),
            "text": compact_text(msg.get("Text") or msg.get("DisplayText") or msg.get("Snippet") or "", 12000),
            "kind": "message" if not media_type else "media",
            "media": media,
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
