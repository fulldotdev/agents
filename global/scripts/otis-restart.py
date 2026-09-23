#!/usr/bin/env python3
"""Monthly 05:00 restart, with busy checks and a post-restart health report."""

import argparse
import fcntl
import importlib.util
import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

USER_HOME = Path.home()
STATE_DIR = USER_HOME / '.local/state/fulldev/restart'
STATE_FILE = STATE_DIR / 'state.json'
SCRIPTS = USER_HOME / '.agents'
TZ = ZoneInfo('Europe/Amsterdam')
SHUTDOWN = ['/usr/bin/sudo', '-n', '/sbin/shutdown', '-r', 'now']


def run(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, check=True, timeout=timeout).stdout


def boot_time():
    return int(re.search(r'sec = (\d+)', run(['/usr/sbin/sysctl', '-n', 'kern.boottime']))[1])


def save(state):
    temp = STATE_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(STATE_FILE)


def busy_reasons():
    reasons = []
    status = json.loads(run(['openclaw', 'status', '--json']))
    if not status['gateway']['reachable']:
        raise RuntimeError('Cannot check OpenClaw: gateway unreachable')
    if status['tasks']['active'] or status['queuedSystemEvents']:
        reasons.append('OpenClaw has active or queued work')
    jobs = json.loads(run(['openclaw', 'cron', 'list', '--all', '--json']))['jobs']
    if any(job.get('state', {}).get('runningAtMs') for job in jobs):
        reasons.append('An OpenClaw cron is running')
    sessions = json.loads(run(['openclaw', 'sessions', '--active', '15', '--all-agents', '--json']))
    if sessions['count']:
        reasons.append('OpenClaw conversation activity in the last 15 minutes')
    threads = json.loads(run(['python3', str(SCRIPTS / 'skills/t3-code/scripts/t3_dispatch.py'), 'list']))
    if any(t.get('latestTurnState') in ('running', 'queued', 'pending')
           or t.get('sessionStatus') in ('running', 'starting') for t in threads):
        reasons.append('T3 has active work')
    processes = run(['/bin/ps', '-axo', 'pid=,comm=,args='])
    for line in processes.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3 or int(parts[0]) == os.getpid():
            continue
        _, command, args = parts
        if Path(command).name in ('ffmpeg', 'whisper-cli', 'whisper', 'HandBrakeCLI'):
            reasons.append('Video or audio processing is running')
        elif any(marker in args for marker in ('codex exec', 'claude -p ', 'opencode run ',
                                               'work-triage/scripts/run.py', 'sync-google-google.ts')):
            reasons.append('An agent or contact-sync process is running')
    if time.time() - boot_time() < 900:
        reasons.append('Otis started less than 15 minutes ago')
    return sorted(set(reasons))


def report_recovery(state):
    pending = state.get('pending')
    if not pending or boot_time() == pending['boot_time']:
        return
    spec = importlib.util.spec_from_file_location(
        'otis_health', SCRIPTS / 'skills/system-hygiene/scripts/otis-health.py')
    health = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(health)
    problems = []
    for _ in range(10):
        problems = []
        try:
            if not health.check_gateway():
                problems.append('OpenClaw is not ready')
            issue = health.check_agent_services()
            if issue:
                problems.append(issue)
            whatsapp = {'whatsapp_disconnected_since': int(time.time()) - 601}
            issue = health.check_whatsapp(whatsapp, int(time.time()))
            if issue:
                problems.append(issue)
            issue = health.check_google()
            if issue:
                problems.append(issue)
        except Exception as exc:
            problems.append(str(exc)[:200])
        if not problems:
            break
        time.sleep(30)
    message = ('Otis: restart completed. OpenClaw, T3, account proxy, WhatsApp sync and Google access are ready.'
               if not problems else 'Otis restarted, but recovery needs attention: ' + '; '.join(problems))
    run(['openclaw', 'message', 'send', '--channel', 'telegram', '--target', '-5094134988',
         '--message', message, '--json'])
    state.update(last_restart_month=pending['month'], last_restart_boot=boot_time(),
                 recovery_problems=problems)
    state.pop('pending')
    save(state)
    print(message, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only busy check; never restart')
    parser.add_argument('--restart-now', action='store_true', help='Authorized test, with all busy checks')
    args = parser.parse_args()
    if args.check:
        reasons = busy_reasons()
        print(json.dumps({'ready': not reasons, 'busy': reasons}))
        return 2 if reasons else 0
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / 'lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        now = datetime.now(TZ)
        month = now.strftime('%Y-%m')
        state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {'last_restart_month': month}
        report_recovery(state)
        save(state)
        if not args.restart_now and (now.hour != 5 or now.minute >= 10 or state['last_restart_month'] == month):
            return 0
        reasons = busy_reasons()
        if reasons:
            print(json.dumps({'deferred_until': 'next day at 05:00', 'busy': reasons}), flush=True)
            return 2
        # Check permission without executing shutdown or prompting in the background.
        run(['/usr/bin/sudo', '-n', '-l', '/sbin/shutdown', '-r', 'now'])
        state['pending'] = {'boot_time': boot_time(), 'month': month, 'requested_at': now.isoformat()}
        save(state)
        print('Restarting Otis now.', flush=True)
        try:
            run(SHUTDOWN)
        except Exception:
            state.pop('pending')
            save(state)
            raise
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('Restart skipped: ' + str(exc), flush=True)
        raise SystemExit(1)
