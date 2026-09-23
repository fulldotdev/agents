#!/usr/bin/env python3
"""Collect everything new since the last run, hand it to the OpenClaw agent, keep what must come back."""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import collect
import meeting_pages
from common import iso_utc, parse_iso, yaml_lines

STATE_DIR = Path(os.environ.get("WORK_TRIAGE_STATE_DIR", Path.home() / ".local/state/fulldev/work-triage")).expanduser()
STATE_FILE = STATE_DIR / "state.json"
LOCK_FILE = STATE_DIR / "run.lock"
BATCH_FILE = STATE_DIR / "batch.yaml"
TRIAGE_CHAT = "-1003914987491"
TRIAGE_SESSION_KEY = f"agent:main:telegram:group:{TRIAGE_CHAT}"
FIRST_RUN_HOURS = 24
RETRY_LINE = re.compile(r"^\s*RETRY:\s*(\S+)\s*(.*?)\s*$")
NUMBERED_LINE = re.compile(r"^\s*(\d+)\.\s")
LOCK_HANDLE = None


def load_state():
    if not STATE_FILE.exists():
        return {"lanes": {}, "retry": [], "last_number": 0}
    return json.loads(STATE_FILE.read_text())


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, STATE_FILE)


def lock():
    global LOCK_HANDLE
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOCK_HANDLE = LOCK_FILE.open("a+")
    try:
        fcntl.flock(LOCK_HANDLE, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        LOCK_HANDLE.close()
        LOCK_HANDLE = None
        return False
    LOCK_HANDLE.seek(0)
    LOCK_HANDLE.truncate()
    LOCK_HANDLE.write(str(os.getpid()))
    LOCK_HANDLE.flush()
    return True


def triage_chat_updated_at():
    """Timestamp of the last activity in the Triage chat, or None when unavailable."""
    try:
        result = subprocess.run(["openclaw", "sessions", "--agent", "main", "--limit", "all", "--json"],
                                text=True, capture_output=True, timeout=30, check=True)
        sessions = json.loads(result.stdout).get("sessions") or []
        return int(next(s["updatedAt"] for s in sessions if s.get("key") == TRIAGE_SESSION_KEY))
    except (subprocess.SubprocessError, ValueError, TypeError, KeyError, StopIteration, json.JSONDecodeError):
        return None


def final_text(envelope):
    if envelope.get("status") not in {None, "ok", "completed"}:
        raise RuntimeError("Agent did not complete: " + str(envelope.get("summary") or envelope.get("status")))
    result = envelope.get("result", envelope)
    meta = result.get("meta") or {}
    payloads = result.get("payloads") or []
    if meta.get("aborted") or meta.get("error") or any(p.get("isError") for p in payloads):
        raise RuntimeError("Agent returned an incomplete or failed run")
    text = "\n".join(p["text"] for p in payloads if p.get("text") and not p.get("isReasoning")).strip()
    if not text:
        raise RuntimeError("Agent returned no final text")
    return text


def split_output(text, known_items):
    """Separate the report from RETRY lines; attach the batch item to each retry."""
    report, retries, seen = [], [], set()
    for line in text.splitlines():
        match = RETRY_LINE.match(line)
        if match:
            ref, note = match.group(1).rstrip(".,;:"), match.group(2)
            item = known_items.get(ref)
            if not item or not note.strip() or ref in seen:
                raise RuntimeError(f"Invalid retry: {ref}; use one exact batch ref and reason per item")
            seen.add(ref)
            retries.append({"ref": ref, "note": note.strip(), "item": item})
        elif line.lstrip().startswith("RETRY:"):
            raise RuntimeError("Invalid retry: missing batch ref or reason")
        else:
            report.append(line)
    report_text = "\n".join(report).strip()
    return ("" if report_text == "NO_REPLY" else report_text), retries


def prepare_agent_items(items, state):
    """Group calendar retries with fresh copies and skip acknowledged meeting content."""
    retry = state.get("retry") or []
    old_calendar = [r["item"] for r in retry if r["ref"].startswith("calendar:")]
    grouped = collect.group_calendar_items(old_calendar + items.get("calendar", []))
    by_copy = {copy["ref"]: item for item in grouped for copy in item["calendar_copies"]}
    by_ref = {item["ref"]: item for item in grouped}
    pending = {}
    for entry in retry:
        if not entry["ref"].startswith("calendar:"):
            pending[entry["ref"]] = dict(entry)
            continue
        old = entry["item"]
        item = by_ref.get(entry["ref"])
        if item is None:
            item = next(by_copy[c["ref"]] for c in collect.calendar_copies(old) if c["ref"] in by_copy)
        ref = item["ref"]
        if ref in pending:
            pending[ref]["note"] += "; " + entry["note"]
        else:
            pending[ref] = {"ref": ref, "note": entry["note"], "item": item}
    items["calendar"] = grouped
    handled = state.get("meeting_content") or {}
    items["meetings"] = [item for item in items.get("meetings", []) if
        item["ref"] in pending or item.get("ok") is False or not item.get("content_fingerprint")
        or handled.get(item["id"]) != item["content_fingerprint"]]
    # An unresolved item appears once, with fresh source data when available.
    for lane, lane_items in items.items():
        for item in lane_items:
            if item["ref"] in pending:
                pending[item["ref"]]["item"] = item
        items[lane] = [item for item in lane_items if item["ref"] not in pending]
    return list(pending.values())


def acknowledge_meetings(state, known, retries):
    unresolved = {r["ref"] for r in retries}
    handled = state.setdefault("meeting_content", {})
    for ref, item in known.items():
        if (ref.startswith("meetings:") and ref not in unresolved and item.get("ok") is not False
                and item.get("content_fingerprint")):
            handled[item["id"]] = item["content_fingerprint"]


def run(args):
    started = time.monotonic()
    state = load_state()
    now = datetime.now(timezone.utc)
    windows = {
        lane: (parse_iso((state["lanes"].get(lane) or {}).get("since")) or now - timedelta(hours=FIRST_RUN_HOURS), now)
        for lane in collect.SOURCES
    }
    collected = collect.batch(windows)
    if not args.dry_run:
        collected["items"]["calendar"] = meeting_pages.prepare_batch(
            collected["items"].get("calendar", []), state, lambda: save_state(state),
        )
        errors = [i["meeting_page"]["error"] for i in state.get("meeting_page_retry", [])]
        if errors:
            collected["failed"]["meeting_pages"] = "; ".join(dict.fromkeys(errors))
    failures = state.get("lane_failures") or {}
    for lane in list(failures):
        if lane not in collected["failed"]:
            failures.pop(lane)
    for lane, error in collected["failed"].items():
        failures[lane] = {"error": error, "consecutive": (failures.get(lane) or {}).get("consecutive", 0) + 1}
    state["lane_failures"] = failures

    retry = prepare_agent_items(collected["items"], state)
    chat_ms = triage_chat_updated_at()
    chat_changed = chat_ms is None or chat_ms > (state.get("triage_chat_seen_ms") or 0)
    new_count = sum(len(items) for items in collected["items"].values())
    receipt = {"started_at": iso_utc(now), "model": args.model, "thinking": args.thinking,
               "new_items": new_count, "retry": len(retry), "chat_changed": chat_changed,
               "lanes_failed": collected["failed"]}

    def advance():
        for lane in collect.SOURCES:
            if lane not in collected["failed"]:
                state["lanes"][lane] = {"since": iso_utc(now)}

    if new_count == 0 and not retry and not chat_changed and not args.dry_run:
        advance()
        save_state(state)
        return write_receipt(receipt, "empty", started, "NO_REPLY")

    number = (state.get("last_number") or 0) + 1
    batch = {
        "collected_at": iso_utc(now),
        "window": {lane: {"since": iso_utc(a), "until": iso_utc(b)} for lane, (a, b) in windows.items()},
        "report_numbering_starts_at": number,
        "triage_chat_changed": chat_changed,
        "lanes_failed": failures,
        "retry": retry,
        "items": collected["items"],
        "index": collected["index"],
    }
    BATCH_FILE.write_text("\n".join(yaml_lines(batch)) + "\n")
    if args.dry_run:
        return write_receipt(receipt, "dry-run", started, f"Batch written to {BATCH_FILE} ({BATCH_FILE.stat().st_size:,} bytes)")

    prompt = (
        "Workflow: work-triage\n\n"
        "Run one triage cycle on Otis. Follow ~/.agents/skills/work-triage/SKILL.md, `browser`, "
        "`work-management`, and the tool skills they name. The OpenClaw job owns the schedule "
        "and delivers your final answer to the Triage chat. Do not send messages yourself."
    )
    prompt += f"\n\nBatch file: {BATCH_FILE} (read it once). Start report numbering at {number}."
    if chat_changed:
        prompt += " The Triage chat changed since the last run: read the user's recent messages there first."
    prompt += " Return only the numbered report, or NO_REPLY when there is nothing to report. Put RETRY lines last."
    remaining = max(60, args.timeout - int(time.monotonic() - started))
    command = ["openclaw", "agent", "--agent", "main", "--session-key", f"agent:main:triage:{now.strftime('%Y%m%dT%H%M%SZ')}",
               "--model", args.model, "--thinking", args.thinking, "--timeout", str(remaining), "--message", prompt, "--json"]
    known = {r["ref"]: r.get("item") for r in retry}
    known.update({item["ref"]: item for items in collected["items"].values() for item in items})
    try:
        response = subprocess.run(command, text=True, capture_output=True, timeout=remaining + 30, check=True)
        text = final_text(json.loads(response.stdout))
        report, retries = split_output(text, known)
    except (subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        save_state(state)
        write_receipt(receipt, "error", started, type(exc).__name__)
        raise RuntimeError("Triage agent failed; nothing was marked as handled, the next run retries") from exc

    numbers = [int(m.group(1)) for m in map(NUMBERED_LINE.match, report.splitlines()) if m]
    if numbers:
        state["last_number"] = max(numbers)
    state["retry"] = retries
    acknowledge_meetings(state, known, retries)
    if chat_ms:
        state["triage_chat_seen_ms"] = chat_ms
    advance()
    save_state(state)
    receipt["retry_after"] = len(retries)
    return write_receipt(receipt, "completed", started, report or "NO_REPLY")


def write_receipt(receipt, status, started, output):
    receipt.update(status=status, duration_seconds=round(time.monotonic() - started, 1))
    directory = STATE_DIR / "logs/runs"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / (receipt["started_at"].replace(":", "") + ".json")).write_text(json.dumps(receipt, indent=2) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="openai/gpt-6-astra")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--dry-run", action="store_true", help="collect and write the batch file, no agent, no state change")
    args = parser.parse_args()
    if not lock():
        print("Previous triage run is still active; skipping this one", file=sys.stderr)
        return 0
    try:
        result = run(args)
        if result != "NO_REPLY":
            print(result)
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        LOCK_HANDLE.close()


if __name__ == "__main__":
    raise SystemExit(main())
