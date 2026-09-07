#!/usr/bin/env python3
"""Script-only health check for the work-triage Hermes heartbeat."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
GATEWAY_HEARTBEAT = HERMES_HOME / "state" / "gateway.heartbeat"
SESSION_DB = HERMES_HOME / "state.db"
TRIAGE_STATE = HERMES_HOME / "state" / "work-triage" / "cursors.json"
STATUS_FILE = HERMES_HOME / "state" / "work-triage" / "watchdog-status.json"
WORKFLOW_ID = "work-triage"
# Conversation identity survives prompt edits and session resets. Compression
# children are included through their parent, even before their key is saved.
SESSION_KEY = os.environ.get(
    "WORK_TRIAGE_SESSION_KEY", "agent:main:telegram:group:-1003914987491:8491875812"
)
ALERT_TARGET = os.environ.get("WORK_TRIAGE_ALERT_TARGET", "telegram:-1003914987491")
GATEWAY_MAX_AGE_SECONDS = 150
TRIAGE_MAX_AGE_SECONDS = 45 * 60


def parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()


def gateway_health(now):
    try:
        data = json.loads(GATEWAY_HEARTBEAT.read_text())
        updated_at = parse_time(data.get("updated_at"))
        age = now - updated_at if updated_at else None
        return {"ok": age is not None and age <= GATEWAY_MAX_AGE_SECONDS, "age_seconds": age, "pid": data.get("pid")}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def heartbeat_health(now):
    if not SESSION_DB.exists():
        return {"ok": False, "error": f"session DB missing: {SESSION_DB}"}
    con = sqlite3.connect(f"file:{SESSION_DB}?mode=ro", uri=True, timeout=5)
    try:
        rows = con.execute(
            """WITH RECURSIVE workflow_sessions(id) AS (
                SELECT id FROM sessions WHERE session_key = ?
                UNION
                SELECT s.id FROM sessions s
                JOIN workflow_sessions parent ON s.parent_session_id = parent.id
            )
            SELECT s.id, m.value, s.ended_at
            FROM workflow_sessions w JOIN sessions s ON s.id = w.id
            JOIN state_meta m ON m.key = 'heartbeat:' || s.id""",
            (SESSION_KEY,),
        ).fetchall()
    finally:
        con.close()
    matches = []
    for session_id, raw, ended_at in rows:
        try:
            state = json.loads(raw)
        except json.JSONDecodeError:
            continue
        anchor = float(state.get("last_fired_at") or state.get("created_at") or 0)
        matches.append({
            "session_id": session_id,
            "status": state.get("status"),
            "session_ended": ended_at is not None,
            "fire_count": int(state.get("fire_count") or 0),
            "interval_seconds": int(state.get("interval_seconds") or 0),
            "age_seconds": now - anchor if anchor else None,
        })
    active = [row for row in matches if row["status"] == "active"]
    current = [row for row in matches if not row["session_ended"] and row["status"] in {"active", "paused"}]
    paused = len(current) == 1 and current[0]["status"] == "paused" and not active
    fresh = [row for row in active if not row["session_ended"] and row["age_seconds"] is not None and row["age_seconds"] <= max(TRIAGE_MAX_AGE_SECONDS, row["interval_seconds"] + 15 * 60)]
    ok = len(active) == 1 and len(current) == 1 and len(fresh) == 1
    return {"ok": ok, "status": "paused" if paused else "active" if ok else "unhealthy", "workflow_id": WORKFLOW_ID, "active_count": len(active), "matches": matches}


def cursor_health(now):
    if not TRIAGE_STATE.exists():
        return {"ok": False, "status": "not_bootstrapped"}
    try:
        data = json.loads(TRIAGE_STATE.read_text())
        lanes = data.get("lanes") or {}
        cursors = {name: value.get("cursor") for name, value in lanes.items() if value.get("cursor")}
        newest = parse_time(data.get("last_collected_at")) or max((parse_time(value) for value in cursors.values()), default=None)
        age = now - newest if newest else None
        failures = {
            name: {"attempts": value.get("attempts", 0), "last_attempt_at": value.get("last_attempt_at")}
            for name, value in (data.get("failures") or {}).items()
            if value.get("attempts", 0) >= 2
        }
        return {"ok": age is not None and age <= TRIAGE_MAX_AGE_SECONDS and not failures, "age_seconds": age, "lane_count": len(cursors), "lanes": sorted(cursors), "repeated_failures": failures}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def processing_health(now):
    """Collection and a fired timer are not evidence of completed decisions."""
    try:
        data = json.loads(TRIAGE_STATE.read_text())
        finished_at = data.get("last_finished_at") or data.get("last_processed_at")
        processed_at = parse_time(finished_at)
        batch = data.get("pending") or {}
        collected_at = parse_time(batch.get("collected_at"))
        events = batch.get("events") or {}
        pending_count = sum(event.get("status") != "done" for event in events.values())
        deferred_count = len(data.get("backlog") or {})
        processed_age = now - processed_at if processed_at else None
        batch_age = now - collected_at if collected_at else None
        # A new batch gets time to finish, including the first run after rollout.
        anchor = max(value for value in (processed_at, collected_at, 0) if value is not None)
        ok = bool(anchor) and now - anchor <= TRIAGE_MAX_AGE_SECONDS
        return {
            "ok": ok,
            "status": "processing" if batch else "processed" if processed_at else "awaiting_first_batch",
            "last_processed_at": data.get("last_processed_at"),
            "last_finished_at": data.get("last_finished_at"),
            "processed_age_seconds": processed_age,
            "batch_age_seconds": batch_age,
            "pending_count": pending_count,
            "deferred_count": deferred_count,
            "unreported_count": sum(not report.get("reported_at") and not report.get("resolved_at") for report in (data.get("reports") or {}).values()),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def repair_gateway():
    process = subprocess.run(
        [str(Path.home() / ".local" / "bin" / "hermes"), "gateway", "restart"],
        capture_output=True, text=True, timeout=90,
    )
    return {
        "attempted": True,
        "ok": process.returncode == 0,
        "returncode": process.returncode,
        "output": (process.stdout or process.stderr).strip()[-1000:],
    }


def transition_alert_message(status):
    failed = [name for name in ("gateway", "heartbeat", "cursors", "processing") if not status[name]["ok"]]
    if "heartbeat" in failed:
        cursor_age = status.get("cursors", {}).get("age_seconds")
        age_note = ""
        if cursor_age is not None:
            age_note = f" Sources were last collected about {round(cursor_age / 60)} minutes ago; this does not prove processing completed."
        return (
            "Work triage heartbeat has stopped."
            + age_note
            + " Restart it in this Triage chat with:\n\n"
            + "/heartbeat resume\n\n"
            + "The next run resumes pending work and saved cursors. The legacy cron remains paused."
        )
    if "cursors" in failed or "processing" in failed:
        return (
            "Work triage has no recent collection or completed processing. "
            "Check the pending batch and source errors in Triage. "
            "Keep pending work intact; a fired heartbeat alone does not mean the work completed."
        )
    return (
        "The Hermes gateway is unavailable, so the work triage heartbeat cannot run. "
        "The watchdog attempted a gateway restart. Check Triage again if no heartbeat appears."
    )


def send_transition_alert(status):
    message = transition_alert_message(status)
    process = subprocess.run(
        [str(Path.home() / ".local" / "bin" / "hermes"), "send", "--quiet", "--to", ALERT_TARGET, message],
        capture_output=True, text=True, timeout=45,
    )
    return {"attempted": True, "ok": process.returncode == 0, "target": ALERT_TARGET, "returncode": process.returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only status: no restart, alert, or status-file write")
    args = parser.parse_args()
    now = time.time()
    previous = None
    if STATUS_FILE.exists():
        try:
            previous = json.loads(STATUS_FILE.read_text())
        except Exception:
            previous = None
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "gateway": gateway_health(now),
        "heartbeat": heartbeat_health(now),
        "cursors": cursor_health(now),
        "processing": processing_health(now),
    }
    if not args.check and not status["gateway"]["ok"]:
        status["gateway_repair"] = repair_gateway()
    status["ok"] = all(status[key]["ok"] for key in ("gateway", "heartbeat", "cursors", "processing"))
    # Triage owns actionable source failures. The watchdog alerts on runtime
    # staleness; a fresh collection with a failed source must not notify twice.
    collection_age = status["cursors"].get("age_seconds")
    status["alert_ok"] = all(status[key]["ok"] for key in ("gateway", "heartbeat", "processing")) and collection_age is not None and collection_age <= TRIAGE_MAX_AGE_SECONDS
    status["paused"] = status["heartbeat"].get("status") == "paused"
    # Give the first deployed batch one cadence plus a processing grace. Keep
    # the deadline in watchdog state so subsequent timer ticks cannot extend it.
    if status["processing"].get("status") == "awaiting_first_batch" and not status["paused"]:
        deadline = (previous or {}).get("first_batch_deadline")
        if deadline is None:
            intervals = [item["interval_seconds"] for item in status["heartbeat"].get("matches", []) if item.get("status") == "active"]
            deadline = now + max(intervals or [1800]) + 900
        status["first_batch_deadline"] = deadline
        if now < deadline and status["gateway"]["ok"] and status["heartbeat"]["ok"]:
            status["alert_ok"] = True
    if args.check:
        print(json.dumps(status, sort_keys=True))
        return 0 if status["ok"] or status["paused"] else 2
    if previous and previous.get("alert_ok", previous.get("ok")) is True and not status["alert_ok"] and not status["paused"]:
        status["alert"] = send_transition_alert(status)
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, STATUS_FILE)
    print(json.dumps(status, sort_keys=True))
    return 0 if status["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
