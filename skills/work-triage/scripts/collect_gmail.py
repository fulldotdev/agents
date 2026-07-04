#!/usr/bin/env python3
import argparse, base64, shutil
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from triage_common import ATTACHMENTS_DIR, DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE, add_common_args, base_result, compact_text, emit, error_obj, json_cmd, window_from_args

def headers(payload):
    return {h.get("name","").lower(): h.get("value") for h in (payload or {}).get("headers", []) if h.get("name")}

def decode(data):
    if not data: return ""
    raw = base64.urlsafe_b64decode((data + "=" * (-len(data) % 4)).encode())
    for enc in ("utf-8", "latin-1"):
        try: return raw.decode(enc)
        except UnicodeDecodeError: pass
    return raw.decode("utf-8", errors="replace")

def body(payload):
    if not payload: return ""
    mime = payload.get("mimeType") or ""
    text = decode((payload.get("body") or {}).get("data"))
    if mime.startswith("text/plain") and text.strip(): return text
    parts = [body(p) for p in payload.get("parts") or [] if (p.get("mimeType") or "").startswith("text/plain")]
    return "\n\n".join([p for p in parts if p.strip()]) or text

def mail_dt(value):
    try: return parsedate_to_datetime(value).astimezone(timezone.utc) if value else None
    except Exception: return None

def search_threads(account, q):
    return json_cmd(["gog", "-a", account, "--json", "--results-only", "gmail", "search", q, "--max", str(MAX_ITEMS_PER_LANE)])

def collect_account(account, after_dt=None, before_dt=None, query=None):
    if query:
        queries, mode = [query], "query"
    elif after_dt:
        from datetime import timedelta
        search_before = before_dt.date() + timedelta(days=1)
        window_query = f"in:inbox after:{after_dt.strftime('%Y/%m/%d')} before:{search_before.strftime('%Y/%m/%d')}"
        queries, mode = [window_query], "inbox_window"
    else:
        queries, mode = ["in:inbox"], "inbox"
    threads, seen = [], set()
    for q in queries:
        for summary in search_threads(account, q):
            tid = summary.get("id")
            if not tid or tid in seen:
                continue
            seen.add(tid)
            summary["matched_query"] = q
            threads.append(summary)
            if len(threads) >= MAX_ITEMS_PER_LANE:
                break
        if len(threads) >= MAX_ITEMS_PER_LANE:
            break
    items = []
    for summary in threads[:MAX_ITEMS_PER_LANE]:
        tid = summary.get("id")
        if not tid: continue
        out = ATTACHMENTS_DIR / "gmail" / account / tid
        out.mkdir(parents=True, exist_ok=True)
        data = json_cmd(["gog", "-a", account, "--json", "gmail", "thread", "get", tid, "--full", "--download", "--out-dir", str(out)])
        downloaded = {}
        for att in data.get("downloaded") or []:
            downloaded.setdefault(att.get("messageId"), []).append(att)
        messages, has_sent, has_window, has_inbox, has_unread = [], False, False, False, False
        for msg in (data.get("thread") or {}).get("messages") or []:
            hs, labels = headers(msg.get("payload") or {}), msg.get("labelIds") or []
            dt = mail_dt(hs.get("date"))
            in_window = bool(dt and after_dt and before_dt and after_dt <= dt < before_dt) if after_dt else True
            has_sent, has_window = has_sent or "SENT" in labels, has_window or in_window
            has_inbox, has_unread = has_inbox or "INBOX" in labels, has_unread or "UNREAD" in labels
            atts = []
            for att in downloaded.get(msg.get("id"), []):
                src = Path(att.get("path")) if att.get("path") else None
                dest = out / src.name if src else None
                if src and src.exists() and dest and src != dest: shutil.copy2(src, dest)
                saved = dest if dest and dest.exists() else src if src and src.exists() else None
                atts.append({"filename": att.get("filename"), "mime_type": att.get("mimeType"), "size": att.get("size"), "saved_path": str(saved) if saved else None})
            messages.append({"id": msg.get("id"), "date": hs.get("date"), "from": hs.get("from"), "to": hs.get("to"), "cc": hs.get("cc"), "bcc": hs.get("bcc"), "subject": hs.get("subject") or summary.get("subject"), "labels": labels, "is_sent_by_me": "SENT" in labels, "in_window": in_window, "body": compact_text(body(msg.get("payload") or {}), 20000), "attachments": atts})
        if not query and not has_inbox:
            continue
        if query and after_dt and not has_window:
            continue
        items.append({"id": tid, "url": f"https://mail.google.com/mail/u/{account}/#all/{tid}", "account": account, "subject": summary.get("subject"), "query": summary.get("matched_query"), "queries": queries, "mode": mode, "contains_sent_by_me": has_sent, "contains_in_window": has_window, "is_in_inbox": has_inbox, "is_archived": not has_inbox, "has_unread": has_unread, "messages": messages})
    return {"source": account, "ok": True, "mode": mode, "queries": queries, "items": items}

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--query"); p.add_argument("--account", action="append"); args = p.parse_args()
    after_dt, before_dt = (None, None) if args.query else window_from_args(args.after, args.before)
    result = base_result("gmail", "query" if args.query else "window" if after_dt else "inbox", after_dt, before_dt); result["sources"] = []
    for account in args.account or DEFAULT_GMAIL_ACCOUNTS:
        try: result["sources"].append(collect_account(account, after_dt, before_dt, args.query))
        except Exception as exc:
            err = error_obj(account, exc); result["sources"].append(err); result["errors"].append(err); result["ok"] = False
    emit(result, args.pretty, args.format)
if __name__ == "__main__": main()
