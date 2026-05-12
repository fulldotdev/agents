#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from task_triage_common import ATTACHMENTS_DIR, MAX_ITEMS_PER_LANE, compact_text, day_bounds_utc, iso_utc, json_cmd



def _download_media(chat_id, msg_id):
    output_dir = ATTACHMENTS_DIR / "whatsapp" / chat_id / msg_id
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = json_cmd([
            "wacli", "--json", "media", "download",
            "--chat", chat_id,
            "--id", msg_id,
            "--output", str(output_dir),
        ])
    except Exception as exc:
        return {"error": str(exc), "saved_dir": str(output_dir)}
    data = result.get("data")
    paths = []
    if isinstance(data, dict):
        for key in ("path", "file", "saved_path"):
            value = data.get(key)
            if value:
                paths.append(value)
        for key in ("paths", "files"):
            value = data.get(key)
            if isinstance(value, list):
                paths.extend(v for v in value if isinstance(v, str) and v)
    elif isinstance(data, str):
        paths.append(data)
    existing = [str(Path(p)) for p in paths if Path(p).exists()]
    if not existing:
        existing = [str(p) for p in sorted(output_dir.iterdir()) if p.is_file()]
    return {
        "saved_dir": str(output_dir),
        "saved_paths": existing,
        **({"meta": data} if data is not None else {}),
        **({"error": result.get("error")} if result.get("error") else {}),
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
            download = _download_media(chat_id, msg_id)
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
