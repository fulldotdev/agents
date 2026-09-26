#!/usr/bin/env python3
"""Install the local 15-minute account-priority task on macOS."""

import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path


def main():
    if sys.platform != "darwin":
        raise SystemExit("This installer requires macOS launchd.")
    home = Path.home()
    python = "/opt/homebrew/bin/python3"
    script = home / ".agents/skills/t3-code/scripts/pool-routing.py"
    subprocess.run([python, str(script)], check=True)
    label = "com.fulldev.pool-routing"
    domain = f"gui/{os.getuid()}"
    target = f"{domain}/{label}"
    logs = home / "Library/Logs/fulldev"
    logs.mkdir(parents=True, exist_ok=True)
    path = home / "Library/LaunchAgents" / (label + ".plist")
    path.parent.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": label,
        "ProgramArguments": [python, "-B", str(script), "--apply"],
        "RunAtLoad": True,
        "StartInterval": 900,
        "ProcessType": "Background",
        "EnvironmentVariables": {"PYTHONDONTWRITEBYTECODE": "1"},
        "StandardOutPath": str(logs / "pool-routing.log"),
        "StandardErrorPath": str(logs / "pool-routing.log"),
    }
    existing = subprocess.run(["launchctl", "print", target], capture_output=True, text=True)
    if existing.returncode == 0:
        if "state = running" in existing.stdout:
            raise SystemExit("The routing task is running. Wait for it to finish, then install again.")
        subprocess.run(["launchctl", "bootout", target], check=True)
        deadline = time.monotonic() + 5
        while subprocess.run(["launchctl", "print", target], capture_output=True).returncode == 0:
            if time.monotonic() >= deadline:
                raise SystemExit("The old task did not unload within five seconds; installation stopped.")
            time.sleep(0.2)
    with path.open("wb") as file:
        plistlib.dump(plist, file)
    subprocess.run(["plutil", "-lint", str(path)], check=True)
    subprocess.run(["launchctl", "enable", target], check=True)
    subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True)
    print("Installed " + label + ": at login and every 15 minutes, using this machine's proxy.")


if __name__ == "__main__":
    main()
