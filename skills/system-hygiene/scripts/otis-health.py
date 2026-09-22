#!/usr/bin/env python3
"""Every 15 minutes on Otis: gateway up, WhatsApp synced, triage ran on time, contact sync finished, T3 and local proxy reachable. One Telegram message when that changes."""

import json
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



def check_agent_services():
    for label, port, name in (
        ("com.t3tools.t3code.service", 3773, "T3"),
        ("com.fulldev.cliproxyapi", 8317, "CLIProxyAPI"),
    ):
        service = run(["launchctl", "print", f"gui/{os.getuid()}/{label}"])
        if service.returncode or "state = running" not in service.stdout:
            return f"{name} draait niet; controleer de launchd-service"
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
                if response.status != 200:
                    return f"{name} antwoordt niet normaal op poort {port}"
        except OSError:
            return f"{name} is niet bereikbaar op lokale poort {port}"
    status = run(["t3", "connect", "status", "--base-dir", str(HOME / ".t3"), "--json"])
    try:
        config = json.loads(status.stdout)
    except ValueError:
        return "T3 Connect-configuratie kon niet worden gecontroleerd"
    if status.returncode or not all(config.get(key) for key in ("desired", "authenticated", "linked")):
        return "T3 Connect is niet volledig gekoppeld of ingelogd"
    return None


def latest_slot(hours, minute, now_local, grace):
    slots = [(now_local - timedelta(days=d)).replace(hour=h, minute=minute, second=0, microsecond=0)
             for d in (0, 1, 2) for h in hours]
    return max(slot for slot in slots if slot + grace <= now_local)


def check_triage(now_local):
    with sqlite3.connect(f"file:{OPENCLAW_DB}?mode=ro", uri=True) as db:
        rows = db.execute("SELECT job_json, state_json FROM cron_jobs WHERE name='work-triage'").fetchall()
    if len(rows) != 1:
        return "triage-cronjob ontbreekt of staat dubbel in OpenClaw"
    job, state = json.loads(rows[0][0]), json.loads(rows[0][1])
    if not job.get("enabled", True):
        return None
    if state.get("runningAtMs") and now_local.timestamp() * 1000 - state["runningAtMs"] < TRIAGE_GRACE.total_seconds() * 1000:
        return None
    minute, hours, *_ = job["schedule"]["expr"].split()
    due = latest_slot([int(h) for h in hours.split(",")], int(minute), now_local, TRIAGE_GRACE)
    if (state.get("lastRunAtMs") or 0) / 1000 < due.timestamp():
        return f"triage van {due.strftime('%H:%M')} is niet gedraaid"
    if state.get("lastRunStatus") != "ok":
        return "laatste triage-run is mislukt"
    return None


def check_contacts(now_local):
    try:
        health = json.loads(CONTACT_HEALTH.read_text())
    except (OSError, ValueError):
        return "contactsync: geen leesbare status"
    due = latest_slot([CONTACT_SLOT[0]], CONTACT_SLOT[1], now_local, CONTACT_GRACE)
    completed = health.get("lastCompletedAt")
    if not completed or datetime.fromisoformat(completed.replace("Z", "+00:00")) < due:
        return "contactsync Dex → Google van vannacht is niet afgerond"
    if health.get("status") == "failed":
        return "contactsync Dex → Google is mislukt: " + str(health.get("error") or health.get("phase") or "")[:120]
    if health.get("issues"):
        return f"contactsync heeft {len(health['issues'])} waarschuwingen, zie ~/projects/contact-enrichment/reports"
    return None


def main():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    now = int(time.time())
    now_local = datetime.now(TZ)
    problems = []
    gateway_ok = False
    try:
        gateway_ok = check_gateway()
    except Exception:
        pass
    if not gateway_ok:
        problems.append("OpenClaw gateway is down; herstart geprobeerd")
        run(["openclaw", "gateway", "restart"], timeout=90)
    for check in (lambda: check_whatsapp(state, now), lambda: check_triage(now_local), lambda: check_contacts(now_local), check_agent_services, check_google):
        try:
            problem = check()
        except Exception as exc:
            problem = f"controle mislukt: {exc}"[:160]
        if problem:
            problems.append(problem)
    if problems != state.get("problems", []):
        text = ("Otis: " + "\n".join(f"{i}. {p}" for i, p in enumerate(problems, 1))) if problems else "Otis: alles is weer in orde."
        if gateway_ok or not problems:
            run(["openclaw", "message", "send", "--channel", "telegram", "--target", SYSTEM_CHAT, "--message", text, "--json"])
    state.update(problems=problems, checked_at=now)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps({"ok": not problems, "problems": problems}))
    return 0 if not problems else 2


if __name__ == "__main__":
    raise SystemExit(main())
