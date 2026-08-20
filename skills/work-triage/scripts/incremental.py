#!/usr/bin/env python3
"""Per-lane cursor state and overlap dedupe for recurring work-triage."""

import copy
import hashlib
import json
import os
import tempfile
from datetime import timedelta
from pathlib import Path

from common import iso_utc, parse_iso, prop_time

DEFAULT_STATE_FILE = Path(
    os.environ.get("WORK_TRIAGE_STATE_FILE", Path.home() / ".hermes" / "state" / "work-triage" / "cursors.json")
).expanduser()
DEFAULT_OVERLAP_MINUTES = int(os.environ.get("WORK_TRIAGE_OVERLAP_MINUTES", "10"))
DEFAULT_BOOTSTRAP_HOURS = int(os.environ.get("WORK_TRIAGE_BOOTSTRAP_HOURS", "24"))
MAX_SEEN_PER_LANE = int(os.environ.get("WORK_TRIAGE_MAX_SEEN", "2000"))


def load(path=DEFAULT_STATE_FILE):
    path = Path(path).expanduser()
    if not path.exists():
        return {"version": 1, "lanes": {}}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid triage cursor state {path}: {exc}") from exc
    if data.get("version") != 1 or not isinstance(data.get("lanes"), dict):
        raise RuntimeError(f"unsupported triage cursor state: {path}")
    return data


def save(state, path=DEFAULT_STATE_FILE):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def window(state, lane, before, bootstrap_hours=DEFAULT_BOOTSTRAP_HOURS, overlap_minutes=DEFAULT_OVERLAP_MINUTES, initial_after=None):
    cursor = parse_iso(((state.get("lanes") or {}).get(lane) or {}).get("cursor"))
    floor = initial_after or before - timedelta(hours=bootstrap_hours)
    if cursor:
        floor = max(floor, cursor - timedelta(minutes=overlap_minutes)) if initial_after else cursor - timedelta(minutes=overlap_minutes)
    return min(floor, before), before


def stable_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def nested_edited(item):
    properties = item.get("properties") or {}
    return prop_time({"properties": properties}, "Edited") or prop_time({"properties": properties}, "Created")


def item_signature(lane, item):
    if not isinstance(item, dict) or item.get("ok") is False:
        return None
    if lane == "gmail":
        messages = [msg for msg in item.get("messages") or [] if msg.get("in_window")]
        latest = (messages or item.get("messages") or [{}])[-1]
        value = [item.get("account"), item.get("id"), latest.get("id"), latest.get("date"), item.get("has_unread")]
    elif lane == "slack":
        candidates = []
        if item.get("in_window"):
            candidates.append(item.get("ts"))
        candidates.extend(reply.get("ts") for reply in item.get("thread_replies") or [] if reply.get("in_window"))
        value = [item.get("workspace_id") or item.get("workspace_slug"), item.get("channel_id"), item.get("thread_ts"), max((x for x in candidates if x), default=item.get("ts"))]
    elif lane == "calendar":
        value = [item.get("source_account"), item.get("id") or item.get("ical_uid"), item.get("updated"), item.get("status"), item.get("start")]
    elif lane == "meetings":
        ready_notes = [
            [note.get("block_id"), note.get("status"), note.get("transcript_block_id"), note.get("transcript_revision")]
            for note in item.get("meeting_notes") or []
            if note.get("status") == "notes_ready" and note.get("transcript_block_id")
        ]
        value = [item.get("id"), sorted(ready_notes, key=lambda note: str(note[0]))] if ready_notes else [
            item.get("id"), nested_edited(item), item.get("when"), item.get("meeting_notes")
        ]
    elif lane == "t3_threads":
        value = [item.get("thread_id"), item.get("updated_at"), item.get("state")]
    elif lane == "work_context":
        value = [item.get("id"), item.get("edited"), item.get("status")]
    else:
        value = item
    return stable_hash(value)


def filter_items(lane, items, seen):
    kept, signatures = [], []
    for item in items or []:
        signature = item_signature(lane, item)
        if not signature or signature not in seen:
            kept.append(item)
        if signature:
            signatures.append(signature)
    return kept, signatures


def filter_value(lane, value, seen_values):
    """Return a copy containing only unseen overlap results plus all signatures."""
    result = copy.deepcopy(value)
    seen = set(seen_values or [])
    signatures = []

    if lane in {"gmail", "calendar"}:
        for source in result.get("sources") or []:
            kept, found = filter_items(lane, source.get("items"), seen)
            source["items"] = kept
            source["count"] = len(kept)
            signatures.extend(found)
    elif lane == "whatsapp":
        chats = []
        for chat in result.get("items") or []:
            kept = []
            for message in chat.get("messages") or []:
                signature = stable_hash([chat.get("chat_id"), message.get("id"), message.get("timestamp")])
                signatures.append(signature)
                if signature not in seen:
                    kept.append(message)
            if kept:
                chat["messages"] = kept
                chats.append(chat)
        result["items"] = chats
    elif lane == "work_context":
        for group in (result.get("lanes") or {}).values():
            kept, found = filter_items(lane, group.get("items"), seen)
            group["items"] = kept
            group["count"] = len(kept)
            signatures.extend(found)
    else:
        kept, signatures = filter_items(lane, result.get("items"), seen)
        result["items"] = kept

    result["changed_count"] = count_items(lane, result)
    return result, signatures


def count_items(lane, value):
    if lane in {"gmail", "calendar"}:
        return sum(len(source.get("items") or []) for source in value.get("sources") or [])
    if lane == "whatsapp":
        return sum(len(chat.get("messages") or []) for chat in value.get("items") or [])
    if lane == "work_context":
        return sum(len(group.get("items") or []) for group in (value.get("lanes") or {}).values())
    return len(value.get("items") or [])


def is_saturated(lane, value, limit):
    """Fail closed when a collector may have clipped a cursor window."""
    if lane in {"gmail", "calendar"}:
        return any(len(source.get("items") or []) >= limit for source in value.get("sources") or [])
    if lane == "whatsapp":
        return sum(len(chat.get("messages") or []) for chat in value.get("items") or []) >= limit
    if lane == "slack":
        return any(int(workspace.get("item_count") or 0) >= limit for workspace in value.get("workspaces") or [])
    if lane == "work_context":
        return any(len(group.get("items") or []) >= limit for group in (value.get("lanes") or {}).values())
    return len(value.get("items") or []) >= limit


def advance(state, lane, before, signatures):
    lanes = state.setdefault("lanes", {})
    previous = list((lanes.get(lane) or {}).get("seen") or [])
    combined = []
    for signature in previous + list(signatures):
        if signature not in combined:
            combined.append(signature)
    lanes[lane] = {
        "cursor": iso_utc(before),
        "seen": combined[-MAX_SEEN_PER_LANE:],
    }
