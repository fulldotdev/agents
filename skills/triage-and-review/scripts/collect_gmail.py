#!/usr/bin/env python3
import argparse
import shutil
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import json

from task_triage_common import (
    ATTACHMENTS_DIR,
    DEFAULT_GMAIL_ACCOUNTS,
    MAX_ITEMS_PER_LANE,
    compact_text,
    day_bounds_utc,
    iso_utc,
    json_cmd,
)


def _header_map(payload):
    headers = (payload or {}).get("headers") or []
    return {h.get("name", "").lower(): h.get("value") for h in headers if h.get("name")}


def _decode_part_body(data):
    if not data:
        return ""
    import base64

    padding = "=" * (-len(data) % 4)
    try:
        raw = base64.urlsafe_b64decode((data + padding).encode("utf-8"))
    except Exception:
        return ""
    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def _message_body(payload):
    if not payload:
        return ""
    mime_type = payload.get("mimeType") or ""
    body = _decode_part_body(((payload.get("body") or {}).get("data")))
    if mime_type.startswith("text/plain") and body.strip():
        return body

    plain_parts = []
    html_parts = []
    for part in payload.get("parts") or []:
        part_text = _message_body(part)
        part_mime = part.get("mimeType") or ""
        if part_mime.startswith("text/plain") and part_text.strip():
            plain_parts.append(part_text)
        elif part_text.strip():
            html_parts.append(part_text)
    if plain_parts:
        return "\n\n".join(plain_parts)
    if body.strip():
        return body
    if html_parts:
        return "\n\n".join(html_parts)
    return ""


def _parse_rfc2822(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except Exception:
        return None


def collect_gmail(after_dt=None, before_dt=None, accounts=DEFAULT_GMAIL_ACCOUNTS, query=None):
    results = []
    if query:
        gmail_query = query
    elif after_dt is not None:
        gmail_after = after_dt.strftime("%Y/%m/%d")
        gmail_before = before_dt.strftime("%Y/%m/%d") if before_dt is not None else datetime.now(timezone.utc).strftime("%Y/%m/%d")
        gmail_query = f"after:{gmail_after} before:{gmail_before}"
    else:
        gmail_query = "in:inbox"
    for account in accounts:
        try:
            threads = json_cmd([
                "gog", "-a", account, "--json", "--results-only",
                "gmail", "search", gmail_query, "--max", str(MAX_ITEMS_PER_LANE),
            ])
            items = []
            for thread_summary in threads[:MAX_ITEMS_PER_LANE]:
                thread_id = thread_summary.get("id")
                if not thread_id:
                    continue
                attachment_dir = ATTACHMENTS_DIR / "gmail" / account / thread_id
                attachment_dir.mkdir(parents=True, exist_ok=True)
                thread_data = json_cmd([
                    "gog", "-a", account, "--json",
                    "gmail", "thread", "get", thread_id,
                    "--full", "--download", "--out-dir", str(attachment_dir),
                ])
                downloaded = thread_data.get("downloaded") or []
                downloaded_by_message = {}
                for item in downloaded:
                    downloaded_by_message.setdefault(item.get("messageId"), []).append(item)
                thread = thread_data.get("thread") or {}
                messages = []
                contains_sent_by_me = False
                contains_in_window = False
                for message in thread.get("messages") or []:
                    payload = message.get("payload") or {}
                    headers = _header_map(payload)
                    date_value = headers.get("date")
                    parsed_date = _parse_rfc2822(date_value)
                    in_window = bool(parsed_date and after_dt is not None and before_dt is not None and after_dt <= parsed_date <= before_dt) if after_dt is not None else True
                    contains_in_window = contains_in_window or in_window
                    labels = message.get("labelIds") or []
                    is_sent_by_me = "SENT" in labels
                    contains_sent_by_me = contains_sent_by_me or is_sent_by_me
                    attachments = []
                    for attachment in downloaded_by_message.get(message.get("id"), []):
                        src_path = Path(attachment.get("path"))
                        dest_path = attachment_dir / src_path.name
                        if src_path.exists() and src_path != dest_path:
                            shutil.copy2(src_path, dest_path)
                        attachments.append({
                            "filename": attachment.get("filename"),
                            "mimeType": attachment.get("mimeType"),
                            "size": attachment.get("size"),
                            "saved_dir": str(attachment_dir),
                        })
                    messages.append({
                        "id": message.get("id"),
                        "labelIds": labels,
                        "From": headers.get("from"),
                        "To": headers.get("to"),
                        "Cc": headers.get("cc"),
                        "Bcc": headers.get("bcc"),
                        "Date": date_value,
                        "Subject": headers.get("subject") or thread_summary.get("subject"),
                        "body": compact_text(_message_body(payload), 20000),
                        "attachments": attachments,
                        "is_sent_by_me": is_sent_by_me,
                        "in_window": in_window,
                    })
                items.append({
                    "id": thread_id,
                    "Subject": thread_summary.get("subject"),
                    "messages": messages,
                    "contains_sent_by_me": contains_sent_by_me,
                    "contains_in_window": contains_in_window,
                    "query": gmail_query,
                })
            results.append({"account": account, "ok": True, "items": items})
        except Exception as exc:
            error_text = str(exc)
            auth_required = "invalid_grant" in error_text or "expired or revoked" in error_text
            keyring_blocked = "KeyUnwrap" in error_text or "keyring" in error_text.lower() or "keychain" in error_text.lower()
            results.append({
                "account": account,
                "ok": False,
                "error": error_text,
                "error_type": "auth_required" if auth_required else "keyring_blocked" if keyring_blocked else "fetch_failed",
                "needs_reauth": auth_required,
                "needs_keyring_access": keyring_blocked,
                "items": [],
            })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--query")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    if args.query:
        after_dt, before_dt = None, None
    elif args.after:
        after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)
    else:
        after_dt, before_dt = None, None

    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "gmail",
        "mode": "query" if args.query else "window" if args.after else "inbox",
        "after": iso_utc(after_dt) if after_dt else None,
        "before": iso_utc(before_dt) if before_dt else None,
        "query": args.query or "in:inbox",
        "items": collect_gmail(after_dt, before_dt, DEFAULT_GMAIL_ACCOUNTS, query=args.query),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
