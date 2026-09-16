#!/usr/bin/env python3
"""Every five minutes: is the gateway up, is the triage job scheduled, did the last run finish on time?"""

import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

OPENCLAW_DIR = Path(os.environ.get("OPENCLAW_STATE_DIR", Path.home() / ".openclaw")).expanduser()
STATE_DIR = Path.home() / ".local/state/fulldev/work-triage"
STATUS_FILE = STATE_DIR / "watchdog-status.json"
ALERT_TARGET = os.environ.get("WORK_TRIAGE_ALERT_TARGET", "telegram:-1003914987491").removeprefix("telegram:")
GRACE = 45 * 60


def gateway_ok():
    result = subprocess.run(["openclaw", "health", "--json"], capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and json.loads(result.stdout).get("ok") is True


def triage_job():
    with sqlite3.connect(f"file:{OPENCLAW_DIR / 'state/openclaw.sqlite'}?mode=ro", uri=True) as connection:
        rows = connection.execute("SELECT job_json, state_json FROM cron_jobs WHERE name=?", ("work-triage",)).fetchall()
    if len(rows) != 1:
        raise ValueError("Missing or duplicate work-triage job")
    job = json.loads(rows[0][0])
    job["state"] = json.loads(rows[0][1])
    return job


def latest_due_slot(job, current):
    """The most recent scheduled slot whose grace period has passed."""
    minute, hours, *_ = job["schedule"]["expr"].split()
    local = datetime.fromtimestamp(current, ZoneInfo("Europe/Amsterdam"))
    slots = [(local - timedelta(days=d)).replace(hour=int(h), minute=int(minute), second=0, microsecond=0).timestamp()
             for d in (0, 1, 2) for h in hours.split(",")]
    return max(slot for slot in slots if slot + GRACE <= current)


def inspect(current):
    status = {"checked_at": datetime.fromtimestamp(current, timezone.utc).isoformat(), "problems": []}
    try:
        status["gateway_ok"] = gateway_ok()
    except Exception as exc:
        status["gateway_ok"], status["gateway_error"] = False, str(exc)
    if not status["gateway_ok"]:
        status["problems"].append("gateway")
    try:
        job = triage_job()
        state = job["state"]
        status["paused"] = not job.get("enabled", True)
        running = state.get("runningAtMs") and current * 1000 - state["runningAtMs"] <= GRACE * 1000
        status["cron_ok"] = status["paused"] or bool(running) or (state.get("nextRunAtMs") or 0) >= (current - 300) * 1000
        if not status["cron_ok"]:
            status["problems"].append("cron")
        last_run = state.get("lastRunAtMs") or 0
        status["run_ok"] = status["paused"] or bool(running) or (
            last_run / 1000 >= latest_due_slot(job, current) and state.get("lastRunStatus") == "ok")
        if not status["run_ok"]:
            status["problems"].append("run")
    except Exception as exc:
        status.update(paused=False, cron_ok=False, run_ok=False, cron_error=str(exc))
        status["problems"].append("cron")
    status["ok"] = not status["problems"]
    return status


MESSAGES = {
    "gateway": "OpenClaw gateway is down. The triage watchdog restarted it; check gateway health if triage does not resume.",
    "cron": "The work-triage job is missing, disabled or overdue. Check `openclaw cron list` on Otis.",
    "run": "The last scheduled triage run did not finish successfully. Check `openclaw cron runs --id <work-triage>` on Otis.",
}


def main():
    status = inspect(time.time())
    previous = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
    if not status["ok"] and not status.get("paused"):
        text = MESSAGES[status["problems"][0]]
        if previous.get("alert_text") != text:
            if "gateway" in status["problems"]:
                subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, text=True, timeout=90)
            subprocess.run(["openclaw", "message", "send", "--channel", "telegram", "--target", ALERT_TARGET,
                            "--message", text, "--json"], capture_output=True, text=True, timeout=45)
        status["alert_text"] = text
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status))
    return 0 if status["ok"] or status.get("paused") else 2


if __name__ == "__main__":
    raise SystemExit(main())
