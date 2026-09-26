#!/usr/bin/env python3
"""Read local CLIProxyAPI subscription limits without exposing credentials."""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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


def management(key, path, payload=None):
    request = urllib.request.Request(
        "http://127.0.0.1:8317/v0/management/" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def window(label, used, reset, seconds=None):
    if isinstance(reset, (int, float)):
        reset = datetime.fromtimestamp(reset, timezone.utc).isoformat()
    return {
        "window": label,
        "remaining_percent": max(0, min(100, 100 - used)) if isinstance(used, (int, float)) else None,
        "resets_at": reset,
        "period_seconds": seconds,
    }


def usage(key, account, provider):
    headers = {"Authorization": "Bearer $TOKEN$", "Content-Type": "application/json"}
    if provider == "codex":
        url = "https://chatgpt.com/backend-api/wham/usage"
        headers.update({"OpenAI-Beta": "codex-1", "Originator": "Codex Desktop"})
        identity = account.get("id_token") or {}
        account_id = identity.get("chatgpt_account_id") if isinstance(identity, dict) else None
        if account_id:
            headers["Chatgpt-Account-Id"] = account_id
    else:
        url = "https://api.anthropic.com/api/oauth/usage"
        headers["anthropic-beta"] = "oauth-2025-04-20"
    result = management(key, "api-call", {
        "auth_index": account["auth_index"], "method": "GET", "url": url, "header": headers,
    })
    if result.get("status_code") != 200:
        raise RuntimeError("upstream HTTP " + str(result.get("status_code")))
    body = json.loads(result["body"])
    windows = []
    if provider == "codex":
        rate = body.get("rate_limit") or {}
        for slot in ("primary_window", "secondary_window"):
            value = rate.get(slot)
            if value:
                seconds = value.get("limit_window_seconds")
                label = {18000: "Session", 604800: "Weekly"}.get(seconds, slot)
                windows.append(window(label, value.get("used_percent"), value.get("reset_at"), seconds))
    else:
        for field, label, seconds in (("five_hour", "Session", 18000), ("seven_day", "Weekly", 604800)):
            value = body.get(field)
            if value:
                windows.append(window(label, value.get("utilization"), value.get("resets_at"), seconds))
        scoped = [v for v in body.get("limits", []) if v.get("kind") == "weekly_scoped"]
        for value in scoped:
            model = ((value.get("scope") or {}).get("model") or {}).get("display_name") or "scoped"
            entry = window("Weekly / " + model, value.get("percent"), value.get("resets_at"), 604800)
            entry["is_active"] = value.get("is_active")
            windows.append(entry)
        legacy = body.get("iguana_necktie")
        if legacy and not any("fable" in v["window"].lower() for v in windows):
            windows.append(window("Weekly / Fable", legacy.get("utilization"), legacy.get("resets_at"), 604800))
    if not windows:
        raise RuntimeError("no usage windows returned")
    return windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("codex", "claude"))
    parser.add_argument("--json", action="store_true", help="print sanitized structured data")
    args = parser.parse_args()
    try:
        key = (Path.home() / ".config/cliproxyapi/management.key").read_text().strip()
        accounts = management(key, "auth-files")["files"]
    except Exception as error:
        print("Cannot read local account pool: " + type(error).__name__, file=sys.stderr)
        return 1
    rows = []
    failed = False
    for account in accounts:
        provider = account.get("provider") or account.get("type")
        if provider not in ("codex", "claude") or (args.provider and provider != args.provider):
            continue
        email = account.get("email")
        row = {"name": NAMES.get((provider, email), provider), "email": email, "provider": provider,
               "disabled": bool(account.get("disabled")), "proxy_status": account.get("status")}
        try:
            row["windows"] = usage(key, account, provider)
        except Exception as error:
            row["error"] = str(error) if isinstance(error, RuntimeError) else type(error).__name__
            failed = True
        rows.append(row)
    rows.sort(key=lambda r: (r["provider"], r["name"], r["email"] or ""))
    observed = datetime.now(timezone.utc).isoformat()
    if args.json:
        print(json.dumps({"observed_at": observed, "accounts": rows}, indent=2))
    else:
        print("Account pool | observed " + datetime.fromisoformat(observed).astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S %Z"))
        print(f"{'Account':<10} {'Window':<20} {'Left':>6}  Reset (Europe/Amsterdam)")
        for row in rows:
            print(f"{row['name']} ({row['email']})" + (" [disabled]" if row["disabled"] else ""))
            if "error" in row:
                print("  ERROR: " + row["error"])
            for value in row.get("windows", []):
                remaining = value["remaining_percent"]
                left = f"{remaining:g}%" if remaining is not None else "?"
                reset = value["resets_at"]
                local = datetime.fromisoformat(reset.replace("Z", "+00:00")).astimezone(TZ).strftime("%Y-%m-%d %H:%M:%S") if reset else "unknown / not started"
                print(f"{'':10} {value['window']:<20} {left:>6}  {local}")
    return 1 if failed or not rows else 0


if __name__ == "__main__":
    sys.exit(main())
