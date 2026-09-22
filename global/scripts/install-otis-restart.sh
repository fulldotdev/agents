#!/bin/bash
set -euo pipefail

if [[ "$(id -un)" != otis || "$(uname -s)" != Darwin ]]; then
  echo 'Run this as otis on the Mac mini.' >&2
  exit 1
fi

restart_script="$HOME/.agents/global/scripts/otis-restart.py"
python_bin=/opt/homebrew/bin/python3
"$python_bin" "$restart_script" --check

# Authorize only this exact restart command, not arbitrary root commands.
restart_rule=$(mktemp)
trap 'rm -f "$restart_rule"' EXIT
printf '%s\n' 'otis ALL=(root) NOPASSWD: /sbin/shutdown -r now' > "$restart_rule"
sudo /usr/sbin/visudo -cf "$restart_rule"
sudo /usr/bin/install -o root -g wheel -m 0440 "$restart_rule" /etc/sudoers.d/otis-monthly-restart

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs/fulldev"
"$python_bin" - <<'PY'
import plistlib
from pathlib import Path
user_home = Path.home()
plist = {
    'Label': 'com.fulldev.otis-restart',
    'ProgramArguments': ['/opt/homebrew/bin/python3', str(user_home / '.agents/global/scripts/otis-restart.py')],
    'StartCalendarInterval': {'Hour': 5, 'Minute': 0},
    'RunAtLoad': True,
    'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin', 'TZ': 'Europe/Amsterdam'},
    'StandardOutPath': str(user_home / 'Library/Logs/fulldev/otis-restart.log'),
    'StandardErrorPath': str(user_home / 'Library/Logs/fulldev/otis-restart.log'),
}
with (user_home / 'Library/LaunchAgents/com.fulldev.otis-restart.plist').open('wb') as file:
    plistlib.dump(plist, file)
PY

# Initialize state without restarting, then register the 05:00 schedule.
"$python_bin" "$restart_script"
launchctl bootout "gui/$(id -u)/com.fulldev.otis-restart" 2>/dev/null || true
launchctl enable "gui/$(id -u)/com.fulldev.otis-restart"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.fulldev.otis-restart.plist"
echo 'Monthly 05:00 restart installed. Running the authorized restart test now.'
sleep 2
"$python_bin" "$restart_script" --restart-now
