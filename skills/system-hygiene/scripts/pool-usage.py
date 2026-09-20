#!/usr/bin/env python3
"""Daily account-pool usage report: weekly quota left per pooled account, sent to the Telegram System chat.

Reads the local CLIProxyAPI management API. Run with --print to show the message instead of sending it.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PORT = 8317
KEY_FILE = os.path.expanduser("~/.config/cliproxyapi/management.key")
SYSTEM_CHAT = "-5094134988"
WEEK = 604800
TZ = ZoneInfo("Europe/Amsterdam")
NAMES = {
    ("codex", "sil@full.dev"): "Codex",
    ("codex", "silveltman@gmail.com"): "Codex 0",
    ("codex", "sil+1@full.dev"): "Codex 1",
    ("codex", "sil+2@full.dev"): "Codex 2",
    ("codex", "sil+3@full.dev"): "Codex 3",
    ("claude", "sil@full.dev"): "Claude",
    ("claude", "silveltman@gmail.com"): "Claude 0",
}
ORDER = list(NAMES.values())


def when(moment):
    """Short local reset time: 'Mon 14:00', with the date when it is more than six days away."""
    local = moment.astimezone(TZ)
    if (moment - datetime.now(timezone.utc)).days >= 6:
        return local.strftime("%-d %b %H:%M")
    return local.strftime("%a %H:%M")


def management(path, data=None):
    key = open(KEY_FILE).read().strip()
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/v0/management/{path}",
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def usage(account):
    if account["type"] == "codex":
        url = "https://chatgpt.com/backend-api/wham/usage"
        header = {"Authorization": "Bearer $TOKEN$", "Content-Type": "application/json", "OpenAI-Beta": "codex-1", "Originator": "Codex Desktop"}
        chatgpt_account = (account.get("id_token") or {}).get("chatgpt_account_id")
        if chatgpt_account:
            header["Chatgpt-Account-Id"] = chatgpt_account
    else:
        url = "https://api.anthropic.com/api/oauth/usage"
        header = {"Authorization": "Bearer $TOKEN$", "anthropic-beta": "oauth-2025-04-20"}
    result = management("api-call", {"auth_index": account["auth_index"], "method": "GET", "url": url, "header": header})
    if result.get("status_code") != 200:
        raise RuntimeError(f"HTTP {result.get('status_code')}")
    body = json.loads(result["body"])
    if account["type"] == "codex":
        windows = [w for w in (body["rate_limit"].get("primary_window"), body["rate_limit"].get("secondary_window")) if w]
        weekly = next((w for w in windows if w.get("limit_window_seconds") == WEEK), None) or max(windows, key=lambda w: w.get("limit_window_seconds", 0))
        reset = datetime.fromtimestamp(weekly["reset_at"], timezone.utc)
        return row(100 - int(weekly["used_percent"]), "", reset)
    weekly = body["seven_day"]
    scoped = [l for l in body.get("limits", []) if l.get("kind") == "weekly_scoped"]
    extra = " ".join(
        f"{(((l.get('scope') or {}).get('model') or {}).get('display_name') or 'scoped')[:5]} {100 - int(l['percent'])}%" for l in scoped
    )
    return row(100 - int(round(weekly["utilization"])), extra, datetime.fromisoformat(weekly["resets_at"]))


def row(left, extra, reset):
    """Fixed-width columns so the lines align in a monospace block."""
    return f"{left:>3}%  {extra:<9}  {when(reset)}"


def main():
    files = management("auth-files")
    files = files.get("files") if isinstance(files, dict) else files
    rows = {}
    for account in files:
        name = NAMES.get((account.get("type"), account.get("email")))
        if not name:
            continue
        try:
            rows[name] = usage(account)
        except Exception as error:  # one broken account must not hide the others
            rows[name] = f"??%  {str(error)[:20]}"
    lines = [f"{name:<9} {rows[name]}" for name in ORDER if name in rows]
    missing = [name for name in ORDER if name not in rows]
    if missing:
        lines.append("not in pool: " + ", ".join(missing))
    text = "Weekly left · resets\n```\n" + "\n".join(lines) + "\n```"
    if "--print" in sys.argv:
        print(text)
        return
    subprocess.run(["openclaw", "message", "send", "--channel", "telegram", "--target", SYSTEM_CHAT, "--message", text, "--json"], check=True, capture_output=True)


if __name__ == "__main__":
    main()
