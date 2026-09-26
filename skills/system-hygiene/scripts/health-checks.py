#!/usr/bin/env python3
"""Local checks shared by health reporting and Otis restart recovery."""

import json
import shutil
import os
import sqlite3
import subprocess
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HOME = Path.home()
STATE_FILE = HOME / ".local/state/fulldev/health/state.json"
CONTACT_HEALTH = HOME / "projects/contact-enrichment/.local/sync-health.json"
OPENCLAW_DB = HOME / ".openclaw/state/openclaw.sqlite"
SYSTEM_CHAT = "-5094134988"
TZ = ZoneInfo("Europe/Amsterdam")
TRIAGE_GRACE = timedelta(minutes=45)
CONTACT_SLOT = (4, 15)
CONTACT_GRACE = timedelta(hours=1)
WHATSAPP_DISCONNECT_TOLERANCE = 600


def run(cmd, timeout=45):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_gateway():
    result = run(["openclaw", "health", "--json"])
    return result.returncode == 0 and json.loads(result.stdout).get("ok") is True


def check_google():
    result = run(["gog", "auth", "list", "--check", "--json", "--no-input"])
    try:
        accounts = json.loads(result.stdout).get("accounts") or []
    except (ValueError, AttributeError):
        return "Google-toegang kon niet worden gecontroleerd"
    if result.returncode or not accounts:
        return "Google-toegang ontbreekt; controleer gog auth"
    configured = {account.get("email"): account for account in accounts}
    required = ("sil@full.dev", "silveltman@gmail.com")
    invalid = [email for email in required if configured.get(email, {}).get("valid") is not True]
    if invalid:
        return "Google-toegang werkt niet voor " + ", ".join(invalid)
    return None


def check_whatsapp(state, now):
    service = run(["launchctl", "print", f"gui/{os.getuid()}/com.fulldev.wacli-sync"])
    if service.returncode or "state = running" not in service.stdout:
        return "WhatsApp-sync (wacli) draait niet"
    pid = next((line.split("=")[1].strip() for line in service.stdout.splitlines() if line.strip().startswith("pid =")), None)
    sockets = run(["lsof", "-nP", "-a", "-p", pid or "0", "-iTCP", "-sTCP:ESTABLISHED"])
    if sockets.returncode == 0 and len(sockets.stdout.splitlines()) > 1:
        state.pop("whatsapp_disconnected_since", None)
    else:
        since = state.setdefault("whatsapp_disconnected_since", now)
        if now - since >= WHATSAPP_DISCONNECT_TOLERANCE:
            return f"WhatsApp-sync heeft al {(now - since) // 60} minuten geen verbinding"
    auth = run(["/opt/homebrew/bin/wacli", "auth", "status", "--json"])
    try:
        if not json.loads(auth.stdout).get("data", {}).get("authenticated"):
            return "wacli is niet meer gekoppeld aan WhatsApp"
    except (ValueError, AttributeError):
        return "wacli-koppeling kon niet worden gecontroleerd"
    return None



def check_service(label, port, name):
    service = run(["launchctl", "print", f"gui/{os.getuid()}/{label}"])
    if service.returncode or "state = running" not in service.stdout:
        return f"{name} draait niet"
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
            if response.status != 200:
                return f"{name} is niet bereikbaar"
    except OSError:
        return f"{name} is niet bereikbaar"
    return None


def check_proxy():
    return check_service("com.fulldev.cliproxyapi", 8317, "Accountproxy")


def check_t3():
    problem = check_service("com.t3tools.t3code.service", 3773, "T3")
    if problem:
        return problem
    status = run(["t3", "connect", "status", "--base-dir", str(HOME / ".t3"), "--json"])
    config = json.loads(status.stdout)
    if status.returncode or not all(config.get(key) for key in ("desired", "authenticated", "linked")):
        return "T3 Connect is niet volledig gekoppeld of ingelogd"
    return None


def check_agent_services():
    return check_proxy() or check_t3()


def check_routing(now, grace_until=0):
    try:
        data = json.loads((HOME / ".local/state/fulldev/pool-routing/state.json").read_text())
        checked = datetime.fromisoformat(data["checked_at"]).timestamp()
        if checked > now + 60 or (now - checked > 2700 and now >= grace_until):
            return "Routing heeft geen recente run"
        if data.get("ok") is not True or data.get("apply") is not True:
            return "Routing is mislukt"
    except (OSError, ValueError, KeyError, TypeError):
        return "Routingstatus ontbreekt of is ongeldig"
    return None


def check_disk():
    usage = shutil.disk_usage(HOME)
    if usage.free < 10 * 1024**3 or usage.free / usage.total < 0.05:
        return "Minder dan 10 GB of 5% vrije schijfruimte"
    return None


def latest_slot(hours, minute, now_local, grace):
    slots = [(now_local - timedelta(days=d)).replace(hour=h, minute=minute, second=0, microsecond=0)
             for d in (0, 1, 2) for h in hours]
    return max(slot for slot in slots if slot + grace <= now_local)


def check_job(name, now_local):
    with sqlite3.connect(f"file:{OPENCLAW_DB}?mode=ro", uri=True) as db:
        rows = db.execute("SELECT job_json, state_json FROM cron_jobs WHERE name=?", (name,)).fetchall()
    if len(rows) != 1:
        return f"{name}: cronjob ontbreekt of staat dubbel"
    job, state = json.loads(rows[0][0]), json.loads(rows[0][1])
    if not job.get("enabled", True):
        return None
    schedule = job["schedule"]
    minute, hours, day, month, weekday = schedule["expr"].split()
    if schedule.get("kind") != "cron" or day != "*" or month != "*":
        return f"{name}: controleschema wordt niet ondersteund"
    minute = int(minute)
    hours = [int(h) for h in hours.split(",")]
    weekdays = set(range(7)) if weekday == "*" else {int(d) % 7 for d in weekday.split(",")}
    if not 0 <= minute < 60 or any(not 0 <= h < 24 for h in hours):
        return f"{name}: ongeldig controleschema"
    local = now_local.astimezone(ZoneInfo(schedule.get("tz", "Europe/Amsterdam")))
    slots = [(local - timedelta(days=d)).replace(hour=h, minute=minute, second=0, microsecond=0)
             for d in range(9) for h in hours]
    due = max(s for s in slots if (s.weekday() + 1) % 7 in weekdays and s + TRIAGE_GRACE <= local)
    if (state.get("scheduleActivatedAtMs") or 0) / 1000 > due.timestamp():
        return None
    running = (state.get("runningAtMs") or 0) / 1000
    if running and 0 <= local.timestamp() - running < TRIAGE_GRACE.total_seconds():
        return None
    if (state.get("lastRunAtMs") or 0) / 1000 < due.timestamp():
        return f"{name}: geplande run is niet uitgevoerd"
    if state.get("lastRunStatus") != "ok":
        return f"{name}: laatste run is mislukt"
    if state.get("lastDelivered") is False:
        return f"{name}: rapport is niet afgeleverd"
    return None


def check_triage(now_local):
    return check_job("work-triage", now_local)


def check_contacts(now_local):
    try:
        health = json.loads(CONTACT_HEALTH.read_text())
    except (OSError, ValueError):
        return "contactsync: geen leesbare status"
    due = latest_slot([CONTACT_SLOT[0]], CONTACT_SLOT[1], now_local, CONTACT_GRACE)
    completed = health.get("lastCompletedAt")
    if not completed or datetime.fromisoformat(completed.replace("Z", "+00:00")) < due:
        return "contactsync full.dev → Gmail van vannacht is niet afgerond"
    if health.get("status") == "failed":
        return "contactsync full.dev → Gmail is mislukt"
    if health.get("issues"):
        return f"contactsync heeft {len(health['issues'])} waarschuwingen, zie ~/projects/contact-enrichment/reports"
    return None

