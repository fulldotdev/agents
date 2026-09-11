"""Read-only watchdog regressions for twice-daily processing."""
import importlib.util
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location('triage_watchdog', Path(__file__).parents[1] / 'scripts/watchdog.py')
assert spec is not None and spec.loader is not None
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)


def ts(value):
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo('Europe/Amsterdam')).timestamp()


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.jobs = root / 'jobs.json'
        self.state = root / 'cursors.json'
        self.ticker = root / 'ticker'
        self.job = {'id': watchdog.JOB_ID, 'name': 'work-triage', 'enabled': True,
                    'schedule': {'kind': 'cron', 'expr': '0 7,17 * * *'},
                    'next_run_at': '2026-09-12T07:00:00+02:00'}
        self.jobs.write_text(json.dumps({'jobs': [self.job]}))
        self.state.write_text(json.dumps({'last_finished_at': '2026-09-11T17:20:00+02:00'}))
        for key, value in [('RUNTIME', 'hermes'), ('JOBS_FILE', self.jobs), ('TRIAGE_FILE', self.state), ('TICKER_FILE', self.ticker)]:
            patcher = patch.object(watchdog, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_overnight_is_not_overdue(self):
        now = ts('2026-09-12T06:30:00')
        self.ticker.write_text(str(now))
        self.assertTrue(watchdog.cron_health(now)['ok'])
        self.assertTrue(watchdog.processing_health(now)['ok'])

    def test_morning_grace_then_missing_finish(self):
        self.assertTrue(watchdog.processing_health(ts('2026-09-12T07:44:00'))['ok'])
        self.assertFalse(watchdog.processing_health(ts('2026-09-12T07:45:00'))['ok'])

    def test_collection_does_not_count_as_finish(self):
        self.state.write_text(json.dumps({'last_finished_at': '2026-09-11T17:20:00+02:00',
                                         'pending': {'collected_at': '2026-09-12T07:44:00+02:00'}}))
        self.assertFalse(watchdog.processing_health(ts('2026-09-12T08:00:00'))['ok'])

    def test_afternoon_requires_new_finish(self):
        self.state.write_text(json.dumps({'last_finished_at': '2026-09-12T07:20:00+02:00'}))
        self.assertTrue(watchdog.processing_health(ts('2026-09-12T17:44:00'))['ok'])
        self.assertFalse(watchdog.processing_health(ts('2026-09-12T17:45:00'))['ok'])

    def test_dst_uses_local_clock(self):
        for day in ('2026-03-29', '2026-10-25'):
            self.assertEqual(watchdog.processing_due(ts(day + 'T08:00:00')), ts(day + 'T07:00:00'))

    def test_past_due_scheduler_fails(self):
        now = ts('2026-09-12T07:06:00')
        self.ticker.write_text(str(now))
        self.assertFalse(watchdog.cron_health(now)['ok'])

    def test_openclaw_state_and_duplicate_detection(self):
        root = Path(self.temp.name) / 'openclaw'
        (root / 'state').mkdir(parents=True)
        (root / 'openclaw.json').write_text('{"cron":{"enabled":true}}')
        database = root / 'state/openclaw.sqlite'
        job = {'id':'native-id','name':'work-triage','enabled':True,'schedule':self.job['schedule']}
        state = {'nextRunAtMs':int(ts('2026-09-12T07:00:00')*1000)}
        with sqlite3.connect(database) as c:
            c.execute('CREATE TABLE cron_jobs(name TEXT,job_json TEXT,state_json TEXT)')
            c.execute('INSERT INTO cron_jobs VALUES (?,?,?)',('work-triage',json.dumps(job),json.dumps(state)))
        with patch.object(watchdog,'RUNTIME','openclaw'), patch.object(watchdog,'OPENCLAW_DIR',root):
            self.assertTrue(watchdog.cron_health(ts('2026-09-12T06:30:00'))['ok'])
            self.assertFalse(watchdog.cron_health(ts('2026-09-12T07:06:00'))['ok'])
            self.assertEqual(watchdog.processing_due(ts('2026-09-12T08:00:00')),ts('2026-09-12T07:00:00'))
            with sqlite3.connect(database) as c:
                c.execute('INSERT INTO cron_jobs VALUES (?,?,?)',('work-triage',json.dumps(job),json.dumps(state)))
            with self.assertRaises(ValueError):watchdog.cron_health(ts('2026-09-12T06:30:00'))


if __name__ == '__main__':
    unittest.main()
