#!/usr/bin/env python3
"""Install local health checks and restricted MacBook status submission."""

import argparse
import json
import os
import plistlib
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path


def write_private(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(content)
    path.chmod(0o600)


def unload(target):
    result = subprocess.run(["launchctl", "print", target], capture_output=True, text=True)
    if result.returncode:
        return
    if "state = running" in result.stdout:
        raise SystemExit("Health task is running. Wait for it to finish before installing.")
    subprocess.run(["launchctl", "bootout", target], check=True)
    deadline = time.monotonic() + 5
    while subprocess.run(["launchctl", "print", target], capture_output=True).returncode == 0:
        if time.monotonic() > deadline:
            raise SystemExit("The previous job did not unload.")
        time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", required=True, choices=("otis", "macbook"))
    parser.add_argument("--host", default="otis.tailb5cb80.ts.net")
    parser.add_argument("--user", default="otis")
    parser.add_argument("--project-id", help="Otis T3 project for incident threads")
    parser.add_argument("--public-key", type=Path, help="Authorize this dedicated status key on Otis")
    parser.add_argument("--configure-only", action="store_true")
    args = parser.parse_args()
    if sys.platform != "darwin":
        raise SystemExit("This installer requires macOS.")
    os.umask(0o077)
    home = Path.home()
    python = "/opt/homebrew/bin/python3"
    script = home / ".agents/skills/system-hygiene/scripts/health.py"
    config_dir = home / ".config/fulldev"
    if args.machine == "macbook":
        if not re.fullmatch(r"[a-zA-Z0-9.-]+", args.host) or not re.fullmatch(r"[a-zA-Z0-9_-]+", args.user):
            raise SystemExit("Invalid host or user.")
        key = home / ".ssh/id_ed25519_health"
        key.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not key.exists():
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "macbook-health-submit",
                            "-f", str(key)], check=True)
        known = home / ".ssh/known_hosts"
        if subprocess.run(["ssh-keygen", "-F", args.host, "-f", str(known)], capture_output=True).returncode:
            raise SystemExit("Verify the Otis host key through the existing SSH connection first.")
        write_private(config_dir / "health-ssh.conf", f'''Host health-otis
    HostName {args.host}
    User {args.user}
    IdentityFile {key}
    IdentityAgent none
    IdentitiesOnly yes
    BatchMode yes
    ForwardAgent no
    ClearAllForwardings yes
    StrictHostKeyChecking yes
    UserKnownHostsFile {known}
    ConnectTimeout 5
    ServerAliveInterval 5
    ServerAliveCountMax 2
''')
        print("Dedicated public key: " + str(key) + ".pub")
    else:
        config_path = config_dir / "health.json"
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        if args.project_id:
            config["project_id"] = args.project_id
        if not config.get("project_id"):
            raise SystemExit("Pass the agents T3 project ID with --project-id.")
        write_private(config_path, json.dumps(config, indent=2) + "\n")
        if args.public_key:
            key = args.public_key.read_text().strip().split()
            if len(key) < 2 or key[0] != "ssh-ed25519" or not re.fullmatch(r"[A-Za-z0-9+/=]+", key[1]):
                raise SystemExit("Expected an Ed25519 public key.")
            subprocess.run(["ssh-keygen", "-lf", str(args.public_key)], check=True, capture_output=True)
            command = shlex.join([python, "-B", str(script), "--receive"])
            if '"' in command:
                raise SystemExit("Unsupported home path for authorized_keys.")
            entry = f'restrict,command="{command}" ssh-ed25519 {key[1]} macbook-health-submit'
            authorized = home / ".ssh/authorized_keys"
            old = authorized.read_text().splitlines() if authorized.exists() else []
            matches = [line for line in old if key[1] in line.split()]
            if matches and matches != [entry]:
                raise SystemExit("This key already has different permissions; inspect it first.")
            if not matches:
                write_private(authorized, "\n".join(old + [entry]) + "\n")
            print("Authorized only health-submit; shell, PTY and forwarding are restricted.")
    if args.configure_only:
        return
    subprocess.run([python, "-B", str(script), "--machine", args.machine, "--collect"], check=True)
    domain = f"gui/{os.getuid()}"
    label = "com.fulldev.health"
    unload(domain + "/" + label)
    if args.machine == "otis":
        unload(domain + "/com.fulldev.otis-health")
        old = home / "Library/LaunchAgents/com.fulldev.otis-health.plist"
        if old.exists():
            backup = home / ".local/state/fulldev/health/install-backups"
            backup.mkdir(parents=True, exist_ok=True, mode=0o700)
            old.rename(backup / f"otis-health-{int(time.time())}.plist")
    logs = home / "Library/Logs/fulldev"
    logs.mkdir(parents=True, exist_ok=True)
    path = home / "Library/LaunchAgents" / (label + ".plist")
    path.parent.mkdir(parents=True, exist_ok=True)
    plist = {
        "Label": label,
        "ProgramArguments": [python, "-B", str(script), "--machine", args.machine, "--run"],
        "StartInterval": 900, "RunAtLoad": True, "ProcessType": "Background",
        "EnvironmentVariables": {"PATH": f"{home}/.local/bin:{home}/.vite-plus/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
                                 "PYTHONDONTWRITEBYTECODE": "1"},
        "StandardOutPath": str(logs / "health.log"),
        "StandardErrorPath": str(logs / "health.log"),
    }
    with path.open("wb") as stream:
        plistlib.dump(plist, stream)
    subprocess.run(["plutil", "-lint", str(path)], check=True)
    subprocess.run(["launchctl", "enable", domain + "/" + label], check=True)
    subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True)
    print("Installed health checks at login and every 15 minutes: " + args.machine)


if __name__ == "__main__":
    main()
