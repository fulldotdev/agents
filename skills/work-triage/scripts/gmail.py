#!/usr/bin/env python3
"""Index changed Gmail threads and collect their conversations for triage."""

import argparse
import base64
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from email.message import Message
from urllib.parse import quote

from common import (
    DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE, TEMP_ROOT,
    add_common_args, base_result, emit, error_obj, json_cmd, window_from_args,
)


def gmail_url(account, thread_id):
    return f"https://mail.google.com/mail/?authuser={quote(account, safe='')}#all/{thread_id}"


def collect_account(account, after_dt=None, before_dt=None, query=None, limit=MAX_ITEMS_PER_LANE):
    # Gmail's default search includes archived received mail. Exclude drafts,
    # spam and trash explicitly; neither Inbox nor Sent is a complete inbox log.
    terms = [query] if query else []
    terms += ["-in:spam", "-in:trash", "-in:drafts"]
    if after_dt:
        terms.append(f"after:{int(after_dt.timestamp())}")
    if before_dt:
        terms.append(f"before:{int(before_dt.timestamp())}")
    search = " ".join(terms)
    data = json_cmd([
        "gog", "--readonly", "--no-input", "-a", account, "--json",
        "gmail", "messages", "search", "--all", "--max", str(limit), "--timezone", "UTC",
        # Queries can start with -in:spam; stop CLI flag parsing first.
        "--", search,
    ])
    messages = data if isinstance(data, list) else data.get("messages") or []
    threads = {}
    for message in messages:
        thread_id = message.get("threadId") or message.get("thread_id")
        if not message.get("id") or not thread_id:
            raise ValueError("Gmail message index lacks id/threadId; cannot acknowledge an incomplete index")
        thread = threads.setdefault(thread_id, {
            "id": thread_id, "account": account, "url": gmail_url(account, thread_id),
            "subject": message.get("subject"), "index_only": True,
            "requires_thread_read_for_decision": True, "messages": [],
        })
        labels = message.get("labels") or message.get("labelIds") or []
        thread["messages"].append({
            "id": message["id"], "date": message.get("date"),
            "from": message.get("from"), "subject": message.get("subject"),
            "labels": labels, "is_sent_by_me": "SENT" in labels,
            "in_window": True,
        })
    for thread in threads.values():
        thread["messages"].sort(key=lambda message: (message.get("date") or "", message["id"]))
    return {
        "source": account, "ok": True, "mode": "message_index", "query": search,
        "items": list(threads.values()), "message_count": len(messages),
        "complete": not (isinstance(data, dict) and (data.get("nextPageToken") or data.get("next_page_token"))),
    }


def read_thread(account, thread_id, download=False):
    cmd = ["gog", "--readonly", "--no-input", "-a", account, "--json", "gmail", "thread", "get", thread_id, "--full"]
    if download:
        out = TEMP_ROOT / "attachments" / "gmail" / quote(account, safe="") / quote(thread_id, safe="")
        out.mkdir(parents=True, exist_ok=True)
        cmd += ["--download", "--use-indexed-attachment-ids", "--out-dir", str(out)]
    return {"source": account, "ok": True, "url": gmail_url(account, thread_id), "thread": json_cmd(cmd)}


class MailText(HTMLParser):
    """Keep visible email text and links without HTML layout or styles."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "head"}:
            self.hidden += 1
        if self.hidden:
            return
        if tag in {"p", "div", "br", "tr", "li"}:
            self.parts.append("\n")
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href:
                self.parts.append(" " + href + " ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "head"} and self.hidden:
            self.hidden -= 1
        elif not self.hidden and tag in {"p", "div", "tr", "li"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def message_parts(part):
    """Prefer plain text alternatives; retain attachment metadata separately."""
    mime = part.get("mimeType", "")
    body = part.get("body") or {}
    if part.get("filename") or body.get("attachmentId"):
        return [], [{"filename": part.get("filename"), "mime_type": mime,
                     "attachment_id": body.get("attachmentId"), "size": body.get("size"),
                     "part_id": part.get("partId")}]
    if part.get("parts"):
        parts = [message_parts(p) for p in part.get("parts", [])]
        attachments = [a for _, group in parts for a in group]
        bodies = [b for group, _ in parts for b in group]
        if mime == "multipart/alternative" and any(m == "text/plain" and t.strip() for m, t in bodies):
            bodies = [(m, t) for m, t in bodies if m == "text/plain"]
        return bodies, attachments
    if mime.startswith("text/") and body.get("data"):
        encoded = body["data"]
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        headers = {h["name"].lower(): h.get("value", "") for h in part.get("headers", [])}
        message = Message()
        message["content-type"] = headers.get("content-type", mime)
        value = raw.decode(message.get_content_charset() or "utf-8")
        if mime == "text/html":
            parser = MailText()
            parser.feed(value)
            value = "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())
        return [(mime, value)], []
    return [], []


def conversation(item, max_chars=60000):
    data = read_thread(item["account"], item["id"])["thread"]
    thread = data.get("thread", data)
    messages = thread.get("messages") or []
    expected = {m["id"] for m in item["messages"]}
    if not messages or not expected.issubset({m.get("id") for m in messages}):
        raise RuntimeError("Full Gmail thread is missing indexed messages")
    result = []
    for message in sorted(messages, key=lambda m: (int(m.get("internalDate") or 0), m["id"])):
        payload = message.get("payload") or {}
        headers = {h["name"].lower(): h.get("value", "") for h in payload.get("headers", [])}
        bodies, attachments = message_parts(payload)
        if message.get("snippet") and not bodies and not attachments:
            raise RuntimeError(f"Gmail message {message['id']} has no readable body or attachment")
        result.append({"id": message["id"], "date": headers.get("date"),
                       **{k: headers.get(k) for k in ("from", "to", "cc", "subject")},
                       "labels": message.get("labelIds", []),
                       "is_sent_by_me": "SENT" in message.get("labelIds", []),
                       "in_window": message["id"] in expected,
                       "body": "\n\n".join(text for _, text in bodies), "attachments": attachments})
    item = {k: v for k, v in item.items() if k not in {"index_only", "requires_thread_read_for_decision"}}
    item.update(messages=result, conversation_fetched_at=datetime.now(timezone.utc).isoformat(),
                conversation_complete=True)
    if len(json.dumps(result)) > max_chars:
        directory = TEMP_ROOT / "gmail" / quote(item["account"], safe="")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / (quote(item["id"], safe="") + ".json")
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n")
        path.chmod(0o600)
        # Keep the headers and attachment inventory for every message in the batch.
        remaining = max_chars
        for message in item["messages"]:
            body = message["body"]
            message["body"] = body[:remaining]
            message["body_truncated"] = len(body) > remaining
            remaining = max(0, remaining - len(message["body"]))
        item.update(conversation_complete=False, conversation_file=str(path))
    return item


def main():
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    parser.add_argument("--query")
    parser.add_argument("--account", action="append")
    parser.add_argument("--thread-id")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download and not args.thread_id:
        parser.error("--download requires a focused --thread-id")
    after, before = (None, None) if args.query or args.thread_id else window_from_args(args.after, args.before)
    result = base_result("gmail", "thread" if args.thread_id else "index", after, before)
    result["sources"] = []
    for account in args.account or DEFAULT_GMAIL_ACCOUNTS:
        try:
            result["sources"].append(read_thread(account, args.thread_id, args.download) if args.thread_id else collect_account(account, after, before, args.query))
        except Exception as exc:
            error = error_obj(account, exc)
            result["sources"].append(error)
            result["errors"].append(error)
            result["ok"] = False
    emit(result, args.pretty, args.format)


if __name__ == "__main__":
    main()
