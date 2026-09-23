#!/usr/bin/env python3
"""Read meeting source without summaries, or save an Astra summary."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from common import NOTION_VERSION, json_cmd, notion_blocks


SUMMARY = re.compile(r"^[ \t]*<summary>\n(.*?)^[ \t]*</summary>[^\S\n]*\n?", re.M | re.S)


def source_markdown(markdown):
    source = SUMMARY.sub("", markdown)
    if re.search(r"^[ \t]*</?summary>", source, re.M):
        raise ValueError("Incomplete summary block; fetch complete meeting source")
    return source


def source_fingerprint(markdown):
    return hashlib.sha256(("meeting-source-v1\n" + source_markdown(markdown)).encode()).hexdigest()


def read_page(page_id):
    data = json_cmd(["ntn", "api", f"v1/pages/{page_id}/markdown", "include_transcript==true",
                     "--notion-version", NOTION_VERSION])
    if "markdown" not in data or data.get("truncated") or data.get("unknown_block_ids"):
        raise ValueError("Incomplete meeting page; fetch missing source before summarizing")
    return data["markdown"]


def normalized_summary(value):
    value = re.sub(r"\\([\W])", r"\1", value)
    # Notion turns bare domains into links, while named links must retain their URLs.
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                   lambda match: match[1] if match[1] == re.sub(r"^https?://", "", match[2]) else match[0], value)
    return " ".join(value.split())


def save_summary(page_id, summary, fingerprint):
    meetings = [block["meeting_notes"] for block in notion_blocks(page_id) if block.get("type") == "meeting_notes"]
    if len(meetings) != 1 or meetings[0].get("status") != "notes_ready":
        raise ValueError("Wait for one completed meeting-notes block before saving")
    before = read_page(page_id)
    if source_fingerprint(before) != fingerprint:
        raise ValueError("Meeting source changed; read it again before saving the summary")
    matches = list(SUMMARY.finditer(before))
    if len(matches) != 1 or "<transcript>" not in before:
        raise ValueError("Expected one completed meeting with a summary and transcript")
    summary = summary.strip()
    if not summary or not summary.startswith("Astra summary") or re.search(r"</?(?:summary|notes|transcript|meeting-notes)\b", summary):
        raise ValueError("Supply summary Markdown starting with 'Astra summary', without meeting tags")
    match = matches[0]
    replacement = "\t<summary>\n" + "\n".join("\t\t" + line for line in summary.splitlines()) + "\n\t</summary>\n"
    payload = {"type": "update_content", "update_content": {"content_updates": [
        {"old_str": match.group(0), "new_str": replacement}
    ]}}
    json_cmd(["ntn", "api", f"v1/pages/{page_id}/markdown", "-X", "PATCH", "-d", json.dumps(payload),
              "--notion-version", NOTION_VERSION])
    after = read_page(page_id)
    if source_markdown(after) != source_markdown(before):
        raise ValueError("Source changed during summary save; re-read and retry this meeting")
    saved = list(SUMMARY.finditer(after))
    if len(saved) != 1 or normalized_summary(saved[0].group(1)) != normalized_summary(summary):
        raise ValueError("Summary readback differs; inspect the saved summary before acknowledging")
    return {"saved": True, "page_id": page_id, "source_fingerprint": fingerprint}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("read", help="print source Markdown without the generated summary")
    read.add_argument("page_id")
    save = commands.add_parser("save", help="replace the Summary tab and verify source preservation")
    save.add_argument("page_id")
    save.add_argument("--file", required=True)
    save.add_argument("--source-fingerprint", required=True)
    args = parser.parse_args()
    if args.command == "read":
        markdown = read_page(args.page_id)
        print(json.dumps({"source_fingerprint": source_fingerprint(markdown),
                          "markdown": source_markdown(markdown)}, ensure_ascii=False))
    else:
        print(json.dumps(save_summary(args.page_id, Path(args.file).read_text(), args.source_fingerprint)))


if __name__ == "__main__":
    main()
