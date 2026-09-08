#!/usr/bin/env python3
"""Gmail metadata index; full bodies and attachments require focused reads."""

import argparse
from urllib.parse import quote

from common import (
    ATTACHMENTS_DIR, DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE,
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
        "gmail", "messages", "search", "--max", str(limit), "--timezone", "UTC",
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
        "complete": not (isinstance(data, dict) and (data.get("nextPageToken") or data.get("next_page_token"))) and len(messages) < limit,
    }


def read_thread(account, thread_id, download=False):
    cmd = ["gog", "--readonly", "--no-input", "-a", account, "--json", "gmail", "thread", "get", thread_id, "--full"]
    if download:
        out = ATTACHMENTS_DIR / "gmail" / account / thread_id
        out.mkdir(parents=True, exist_ok=True)
        cmd += ["--download", "--out-dir", str(out)]
    return {"source": account, "ok": True, "url": gmail_url(account, thread_id), "thread": json_cmd(cmd)}


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
