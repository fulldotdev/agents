#!/usr/bin/env python3
"""Order the local account pool by upcoming weekly reset. Dry-run unless --apply."""

import argparse
import fcntl
import importlib.util
import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("pool_usage", Path(__file__).with_name("pool-usage.py"))
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)
STATE_DIR = Path.home() / ".local/state/fulldev/pool-routing"


def patch_priority(key, name, priority):
    request = urllib.request.Request(
        "http://127.0.0.1:8317/v0/management/auth-files/fields",
        data=json.dumps({"name": name, "priority": priority}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="PATCH",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if json.load(response).get("status") != "ok":
            raise RuntimeError("priority update not acknowledged")


def weekly_reset(windows, now):
    matches = [w for w in windows if w["window"] == "Weekly" and w["period_seconds"] == 604800]
    if len(matches) != 1:
        raise ValueError("expected one all-models weekly window")
    value = matches[0]
    left = value["remaining_percent"]
    if not isinstance(left, (int, float)) or not math.isfinite(left) or not 0 <= left <= 100:
        raise ValueError("missing or invalid remaining quota")
    reset = datetime.fromisoformat(value["resets_at"].replace("Z", "+00:00"))
    if reset.tzinfo is None or not now < reset.timestamp() <= now + 8 * 86400:
        raise ValueError("missing, expired or implausible weekly reset")
    # Claude's reset timestamps vary by fractions of a second around a minute boundary.
    # Equal reset minutes keep a stable filename order instead of swapping each poll.
    return int((reset.timestamp() + 30) // 60), reset.isoformat()


def pool_accounts(key):
    return [a for a in usage.management(key, "auth-files")["files"]
            if (a.get("provider") or a.get("type")) in ("codex", "claude") and not a.get("disabled")]


def provider_of(account):
    return account.get("provider") or account.get("type")


def error_label(error):
    # Never print raw upstream bodies, headers or credential-bearing exceptions.
    return str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__


def apply_group(key, provider, plan):
    current = [a for a in pool_accounts(key) if provider_of(a) == provider]
    expected = {r["name"]: r["old_priority"] for r in plan}
    if {a["name"]: a.get("priority", 0) for a in current} != expected:
        raise RuntimeError("account list or priorities changed during read; waiting for next run")
    attempted = []
    try:
        for row in plan:
            if row["old_priority"] == row["priority"]:
                continue
            attempted.append(row)
            patch_priority(key, row["name"], row["priority"])
        actual = {a["name"]: a.get("priority", 0) for a in pool_accounts(key) if provider_of(a) == provider}
        if actual != {r["name"]: r["priority"] for r in plan}:
            raise RuntimeError("priority readback mismatch")
    except Exception:
        rollback_failed = False
        for row in reversed(attempted):
            try:
                patch_priority(key, row["name"], row["old_priority"])
            except Exception:
                rollback_failed = True
        if rollback_failed:
            raise RuntimeError("priority update failed and rollback is incomplete") from None
        raise
    return len(attempted)


def run(apply):
    started = time.time()
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "apply": apply, "providers": {}}
    key = (Path.home() / ".config/cliproxyapi/management.key").read_text().strip()
    routing = usage.management(key, "config")["routing"]
    if routing.get("strategy") != "fill-first" or routing.get("session-affinity") is not True:
        raise RuntimeError("expected fill-first with session affinity; settings left unchanged")
    accounts = pool_accounts(key)
    if not accounts:
        raise RuntimeError("no enabled Codex or Claude accounts returned")
    for provider in ("codex", "claude"):
        group = [a for a in accounts if provider_of(a) == provider]
        if not group:
            continue
        result = {"status": "unchanged", "order": []}
        report["providers"][provider] = result
        try:
            plan = []
            for account in group:
                windows = usage.usage(key, account, provider)
                minute, reset = weekly_reset(windows, time.time())
                plan.append({"name": account["name"], "email": account.get("email"),
                             "reset_minute": minute, "resets_at": reset,
                             "old_priority": account.get("priority", 0)})
            plan.sort(key=lambda row: (row["reset_minute"], row["name"]))
            for index, row in enumerate(plan):
                row["priority"] = (len(plan) - index) * 100
            result["order"] = [{k: row[k] for k in ("email", "resets_at", "priority")} for row in plan]
            if time.time() - started > 300:
                raise RuntimeError("usage read took too long; waiting for next run")
            now = time.time()
            if any(datetime.fromisoformat(row["resets_at"]).timestamp() <= now for row in plan):
                raise RuntimeError("weekly reset crossed during read; waiting for next run")
            if apply:
                result["changed"] = apply_group(key, provider, plan)
                result["status"] = "updated" if result["changed"] else "unchanged"
            else:
                result["status"] = "dry-run"
                result["would_change"] = sum(r["priority"] != r["old_priority"] for r in plan)
        except Exception as error:
            result["status"] = "error"
            result["error"] = error_label(error)
    report["ok"] = all(r["status"] != "error" for r in report["providers"].values())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="persist changed priorities through the local API")
    args = parser.parse_args()
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (STATE_DIR / "run.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({"ok": True, "status": "another run is active"}))
            return 0
        try:
            report = run(args.apply)
        except Exception as error:
            report = {"checked_at": datetime.now(timezone.utc).isoformat(), "apply": args.apply,
                      "ok": False, "error": error_label(error)}
        if args.apply:
            temporary = STATE_DIR / "state.json.tmp"
            temporary.write_text(json.dumps(report, indent=2) + "\n")
            temporary.chmod(0o600)
            os.replace(temporary, STATE_DIR / "state.json")
        print(json.dumps(report))
        return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
