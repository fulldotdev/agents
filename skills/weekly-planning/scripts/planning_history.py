"""Read original Telegram updates from OpenClaw's durable ingress, never model text."""
from contextlib import closing
import json
import sqlite3

# Existing Notion batches use integer cursors. Keep imported Hermes IDs disjoint.
OPENCLAW_ID_BASE = 1_000_000_000_000


def openclaw_messages(database, chat, sender, after, last=0):
    # Missing/unreadable history must fail closed, including at send-claim time.
    with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True)) as connection:
        rows = connection.execute("""
            SELECT queue_name, event_id, payload_json, received_at FROM channel_ingress_events
            WHERE channel_id='telegram' AND account_id='default'
              AND received_at>=? ORDER BY event_id
        """, (int(after * 1000),)).fetchall()
    result = []
    latest = {}
    for queue, event_id, raw, received_at in rows:
        payload = json.loads(raw)
        if payload.get("version") != 1:
            raise ValueError("Unsupported OpenClaw Telegram ingress version")
        update = payload.get("update", {})
        update_id = update.get("update_id")
        if not isinstance(update_id, int) or payload.get("updateId") != update_id:
            raise ValueError("OpenClaw Telegram update identity mismatch")
        if event_id != str(update_id).zfill(16):
            raise ValueError("OpenClaw Telegram event identity mismatch")
        message = update.get("message") or update.get("edited_message")
        if not isinstance(message, dict):
            continue
        # Record revisions before authority/content filtering, so an edit can
        # revoke earlier evidence even when its replacement cannot approve.
        key = (str(message.get("chat", {}).get("id")), str(message.get("message_id")))
        latest[key] = (queue, event_id, update_id, message, received_at)
    for queue, event_id, update_id, message, received_at in latest.values():
        author = message.get("from", {})
        if (str(message.get("chat", {}).get("id")) != chat or str(author.get("id")) != sender
                or author.get("is_bot") is not False or message.get("sender_chat")):
            continue
        # Forwarded messages and captions cannot grant approval.
        if any(key in message for key in ("forward_origin", "forward_from", "forward_from_chat", "forward_date")):
            continue
        content = message.get("text")
        timestamp = message.get("edit_date", message.get("date"))
        identifier = OPENCLAW_ID_BASE + update_id
        if not isinstance(content, str) or not isinstance(timestamp, (int, float)) or received_at / 1000 < after or identifier <= last:
            continue
        result.append({"id": identifier, "source": "openclaw", "session_id": queue,
                       "event_id": event_id, "message_id": str(message["message_id"]),
                       "chat_id": chat, "user_id": sender, "content": content, "timestamp": received_at / 1000, "sent_at": message.get("date", timestamp),
                       "reply_to_id": str(message["reply_to_message"]["message_id"]) if message.get("reply_to_message") else None})
    return result
