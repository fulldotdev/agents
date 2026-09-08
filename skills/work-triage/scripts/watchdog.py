#!/usr/bin/env python3
"""Check triage cron progress independently of the Hermes gateway."""
import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERMES_DIR = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')).expanduser()
JOB_ID = '79d5bed18bab'
JOBS_FILE = HERMES_DIR / 'cron/jobs.json'
TICKER_FILE = HERMES_DIR / 'cron/ticker_heartbeat'
GATEWAY_FILE = HERMES_DIR / 'state/gateway.heartbeat'
TRIAGE_FILE = HERMES_DIR / 'state/work-triage/cursors.json'
STATUS_FILE = HERMES_DIR / 'state/work-triage/watchdog-status.json'
ALERT_TARGET = os.environ.get('WORK_TRIAGE_ALERT_TARGET', 'telegram:-1003914987491')
MAX_AGE = 45 * 60


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp() if value else None


def gateway_health(current):
    value = json.loads(GATEWAY_FILE.read_text())
    age = current - timestamp(value['updated_at'])
    return {'ok': age <= 150, 'age_seconds': age, 'pid': value.get('pid')}


def cron_health(current):
    jobs = json.loads(JOBS_FILE.read_text())['jobs']
    matches = [j for j in jobs if j.get('name') == 'work-triage' or j['id'] == JOB_ID]
    if len(matches) != 1 or matches[0]['id'] != JOB_ID:
        return {'ok': False, 'error': 'Missing or duplicate triage cron'}
    job = matches[0]
    paused = not job.get('enabled') or job.get('state') == 'paused'
    due = timestamp(job.get('next_run_at'))
    claim = timestamp((job.get('fire_claim') or {}).get('at'))
    running = claim is not None and current - claim <= 300
    ticker_age = current - float(TICKER_FILE.read_text())
    scheduled = due is not None and -300 <= due - current <= MAX_AGE
    return {'ok': not paused and ticker_age <= 150 and (running or scheduled),
            'paused': paused, 'running': running, 'ticker_age_seconds': ticker_age,
            'next_run_at': job.get('next_run_at'), 'last_run_at': job.get('last_run_at'),
            'last_status': job.get('last_status')}


def processing_health(current):
    value = json.loads(TRIAGE_FILE.read_text())
    batch = value.get('pending') or {}
    finished = timestamp(value.get('last_finished_at'))
    started = timestamp(batch.get('collected_at'))
    anchor = max(finished or 0, started or 0)
    return {'ok': bool(anchor) and current - anchor <= MAX_AGE,
            'last_finished_at': value.get('last_finished_at'),
            'age_seconds': current - anchor if anchor else None,
            'pending_count': sum(e.get('status') != 'done' for e in batch.get('events', {}).values()),
            'deferred_count': len(value.get('backlog') or {})}


def inspect(current):
    status = {'checked_at': datetime.fromtimestamp(current, timezone.utc).isoformat()}
    for name, read in [('gateway', gateway_health), ('cron', cron_health), ('processing', processing_health)]:
        try:
            status[name] = read(current)
        except Exception as exc:
            status[name] = {'ok': False, 'error': str(exc)}
    status['paused'] = status['cron'].get('paused', False)
    status['ok'] = all(status[name]['ok'] for name in ['gateway', 'cron', 'processing'])
    return status


def message(status):
    if not status['gateway']['ok']:
        return 'Hermes gateway is unavailable. The triage watchdog attempted a restart; check gateway health if triage does not resume.'
    if not status['cron']['ok']:
        return 'Triage cron is missing, duplicated or overdue. Check hermes cron status and job 79d5bed18bab. Preserve the pending queue when recovering.'
    return 'Triage has not completed processing recently. Check its current cron run and pending batch. Source collection alone does not mean the work finished.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read only; no restart, alert or status write')
    args = parser.parse_args()
    status = inspect(time.time())
    if args.check:
        print(json.dumps(status))
        return 0 if status['ok'] or status['paused'] else 2
    previous = {}
    if STATUS_FILE.exists():
        try:
            previous = json.loads(STATUS_FILE.read_text())
        except (ValueError, OSError):
            pass
    if not status['ok'] and not status['paused']:
        alert_text = message(status)
        if previous.get('alert_text') != alert_text or not previous.get('alert_sent'):
            if not status['gateway']['ok']:
                try:
                    subprocess.run([str(Path.home() / '.local/bin/hermes'), 'gateway', 'restart'], capture_output=True, text=True, timeout=90)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            try:
                result = subprocess.run([str(Path.home() / '.local/bin/hermes'), 'send', '--quiet', '--to', ALERT_TARGET, alert_text], capture_output=True, text=True, timeout=45)
                sent = result.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                sent = False
            status.update(alert_text=alert_text, alert_sent=sent)
        else:
            status.update(alert_text=alert_text, alert_sent=True)
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATUS_FILE.with_suffix('.tmp')
    temporary.write_text(json.dumps(status, indent=2) + '\n')
    os.replace(temporary, STATUS_FILE)
    print(json.dumps(status))
    return 0 if status['ok'] or status['paused'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
