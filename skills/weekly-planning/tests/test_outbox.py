"""Offline weekly rehearsal: real helpers, fake Notion API and Telegram history."""
import copy
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import outbox
import store


class Notion:
    def __init__(self):
        self.blocks = {}
        self.children = {}

    def add(self, parent, block):
        value = copy.deepcopy(block)
        identifier = 'block-' + str(len(self.blocks) + 1)
        value['id'] = identifier
        nested = value[value['type']].pop('children', [])
        self.blocks[identifier] = value
        self.children.setdefault(parent, []).append(identifier)
        for child in nested:
            self.add(identifier, child)
        return copy.deepcopy(value)

    def api(self, path, method='GET', body=None):
        path = path.split('?')[0]
        parts = path.split('/')
        if parts[0] == 'data_sources':
            return {'results': [{'id': 'sprint', 'properties': {}}], 'has_more': False}
        identifier = parts[1]
        if len(parts) == 3 and parts[2] == 'children':
            if method == 'PATCH':
                return {'results': [self.add(identifier, b) for b in body['children']]}
            return {'results': [copy.deepcopy(self.blocks[i]) for i in self.children.get(identifier, [])], 'has_more': False}
        self.blocks[identifier].update(copy.deepcopy(body))
        return copy.deepcopy(self.blocks[identifier])


class WeeklyRehearsal(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'history.db'
        self.clock = datetime(2026, 9, 13, 10, tzinfo=outbox.TZ)
        self.notion = Notion()
        self.publications = []
        for obj, name, value in [(store, 'api', self.notion.api), (outbox, 'DB', self.db), (outbox, 'RUNTIME', 'hermes'),
                                 (outbox, 'now', lambda: self.clock),
                                 (outbox.subprocess, 'run', self.send)]:
            patcher = patch.object(obj, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        with sqlite3.connect(self.db) as c:
            c.executescript('''CREATE TABLE sessions (id TEXT PRIMARY KEY, source TEXT, chat_id TEXT, user_id TEXT);
                CREATE TABLE messages (id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, timestamp REAL);''')
            c.executemany('INSERT INTO sessions VALUES (?,?,?,?)', [
                ('sil', 'telegram', outbox.CHAT, outbox.SIL),
                ('other', 'telegram', outbox.CHAT, 'not-sil'),
                ('wrong-chat', 'telegram', '-1', outbox.SIL)])
        self.batch = outbox.init('sprint', '2026-09-14')['batch']

    def send(self, args, **kwargs):
        self.assertEqual(args, ['hermes', 'send', '--to', 'telegram:' + outbox.CHAT, '--json'])
        self.publications.append(kwargs['input'])
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            'success': True, 'message_id': str(len(self.publications)), 'chat_id': outbox.CHAT}))

    def draft(self, project='project-1', text='Confirmed progress.'):
        return outbox.draft(self.batch, {'project': project, 'name': project, 'text': text,
            'destination': {'channel': 'gmail', 'label': 'Test recipient', 'account': 'test@example.invalid',
                            'to': ['review@example.invalid'], 'subject': 'Weekly update'},
            'sources': ['https://example.invalid/source']})

    def reply(self, text, session='sil'):
        self.clock += timedelta(seconds=1)
        with sqlite3.connect(self.db) as c:
            c.execute('INSERT INTO messages(session_id,role,content,timestamp) VALUES (?,?,?,?)',
                      (session, 'user', text, self.clock.timestamp()))

    def monday(self):
        self.clock = datetime(2026, 9, 14, 7, tzinfo=outbox.TZ)

    def check(self, section):
        return {'checked_at': self.clock.isoformat(), 'digest': store.load(section)['digest'],
                'unchanged': True, 'sources': ['https://example.invalid/current']}

    def receipt(self, claim):
        return {'digest': claim['digest'], 'channel': 'gmail', 'message_id': 'fake-sent-message',
                'sent_at': self.clock.isoformat()}

    def test_cron_review_is_sent_and_can_be_approved(self):
        self.draft()

        def cron_send(args, **kwargs):
            env = kwargs.get('env', os.environ)
            if env.get('HERMES_CRON_AUTO_DELIVER_PLATFORM') == 'telegram' and env.get('HERMES_CRON_AUTO_DELIVER_CHAT_ID') == outbox.CHAT:
                return SimpleNamespace(returncode=0, stdout=json.dumps({
                    'success': True, 'skipped': True, 'reason': 'cron_auto_delivery_duplicate_target'}))
            self.assertEqual(env['HERMES_SESSION_ID'], 'weekly-test')
            return self.send(args, **kwargs)

        with patch.dict(os.environ, {'HERMES_CRON_AUTO_DELIVER_PLATFORM': 'telegram',
                                     'HERMES_CRON_AUTO_DELIVER_CHAT_ID': outbox.CHAT,
                                     'HERMES_SESSION_ID': 'weekly-test'}), \
             patch.object(outbox.subprocess, 'run', side_effect=cron_send):
            self.assertTrue(outbox.publish(self.batch, '')['published'])
            self.assertEqual(os.environ['HERMES_CRON_AUTO_DELIVER_CHAT_ID'], outbox.CHAT)
        self.assertEqual(len(self.publications), 1)
        self.reply('alles akkoord')
        self.assertEqual(outbox.reconcile(self.batch)['changed'][0]['status'], 'Goedgekeurd')

    def test_full_week_approve_skip_send_and_restart(self):
        one = self.draft()
        self.draft('project-2')
        outbox.publish(self.batch, 'Test cleanup complete.')
        self.reply('1 ok\n2 niet versturen')
        self.assertEqual([i['status'] for i in outbox.reconcile(self.batch)['changed']], ['Goedgekeurd', 'Overslaan'])
        self.monday()
        claimed = outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertEqual(claimed['send_exactly']['text'], one['text'])
        # Simulate delivery, then a crash before its receipt is saved.
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        receipt = self.receipt(claimed)
        outbox.finish(one['section'], receipt)
        outbox.finish(one['section'], receipt)
        self.assertEqual(store.load(one['section'])['status'], 'Verzonden')
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 2, self.check(one['section']))
        self.assertEqual(len(self.publications), 1)

    def test_withdrawal_is_checked_again_at_send(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('alles akkoord')
        outbox.reconcile(self.batch)
        self.reply('1 intrekken')
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertEqual(store.load(one['section'])['status'], 'Overslaan')

    def test_receipt_write_timeout_recovers_without_sending_again(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        self.monday()
        claim = outbox.claim(self.batch, 1, self.check(one['section']))
        receipt = self.receipt(claim)
        real_save = store.save
        def save_then_timeout(identifier, value):
            real_save(identifier, value)
            raise TimeoutError('Reply lost after Notion saved the receipt')
        with patch.object(store, 'save', side_effect=save_then_timeout):
            with self.assertRaises(TimeoutError):
                outbox.finish(one['section'], receipt)
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        outbox.finish(one['section'], receipt)
        self.assertEqual(store.load(one['section'])['receipt'], receipt)

    def test_other_sender_wrong_chat_and_acknowledgement_cannot_approve(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok', 'other')
        self.reply('1 ok', 'wrong-chat')
        self.reply('bedankt')
        self.assertEqual(outbox.reconcile(self.batch)['changed'], [])
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))

    def test_edit_requires_review_but_unchanged_item_keeps_approval(self):
        one, two = self.draft(), self.draft('project-2')
        outbox.publish(self.batch, '')
        self.reply('alles akkoord')
        outbox.reconcile(self.batch)
        self.draft(text='Changed progress.')
        self.assertIsNone(store.load(one['section'])['approval'])
        self.assertEqual(store.load(two['section'])['status'], 'Goedgekeurd')
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        self.monday()
        outbox.claim(self.batch, 1, self.check(one['section']))
        outbox.claim(self.batch, 2, self.check(two['section']))

    def test_send_window_and_old_source_check(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.monday()
        check = self.check(one['section'])
        self.clock += timedelta(minutes=11)
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, check)

    def test_manual_text_change_cannot_send(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        outbox.reconcile(self.batch)
        rows = store.children(one['section'])
        store.update(rows[1]['id'], 'code', 'Manually changed text', language='plain text')
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))

    def fail_batch_once(self, operation):
        real = store.save
        def fail(identifier, value):
            if identifier == self.batch:
                raise RuntimeError('Simulated batch write failure')
            return real(identifier, value)
        with patch.object(store, 'save', side_effect=fail):
            with self.assertRaises(RuntimeError):
                operation()

    def test_existing_draft_recovers_failed_sprint_write(self):
        self.draft()
        self.fail_batch_once(lambda: self.draft(text='Updated progress.'))
        self.draft(text='Updated progress.')
        outbox.publish(self.batch, '')
        self.assertEqual(len(store.children('project-1')), 1)

    def test_new_draft_recovers_without_duplicate_project_section(self):
        self.fail_batch_once(self.draft)
        self.draft()
        self.assertEqual(len(store.children('project-1')), 1)
        outbox.publish(self.batch, '')

    def test_uncertain_publication_is_not_repeated(self):
        self.draft()
        with patch.object(outbox.subprocess, 'run', side_effect=TimeoutError('Simulated timeout')):
            with self.assertRaises(TimeoutError):
                outbox.publish(self.batch, '')
        with self.assertRaises(ValueError):
            outbox.publish(self.batch, '')
        self.assertEqual(self.publications, [])

    def test_fast_plain_approval_is_kept_for_review_not_lost(self):
        one = self.draft()
        def slow_send(args, **kwargs):
            result = self.send(args, **kwargs)
            self.reply('1 ok')
            self.clock += timedelta(seconds=2)
            return result
        with patch.object(outbox.subprocess, 'run', side_effect=slow_send):
            outbox.publish(self.batch, '')
        outbox.reconcile(self.batch)
        self.assertEqual(store.load(one['section'])['status'], 'Review nodig')

    def test_fast_native_reply_approves_the_review_already_received(self):
        one = self.draft()
        def slow_send(args, **kwargs):
            result = self.send(args, **kwargs)
            self.reply('[Replying to your previous message: "'+kwargs['input'][:500]+'"]\n\n1 ok')
            self.clock += timedelta(seconds=2)
            return result
        with patch.object(outbox.subprocess, 'run', side_effect=slow_send):
            outbox.publish(self.batch, '')
        outbox.reconcile(self.batch)
        self.assertEqual(store.load(one['section'])['status'], 'Goedgekeurd')

    def test_native_reply_approves_only_the_quoted_review(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        first = self.publications[-1][:500]
        self.reply('[Replying to your previous message: "'+first+'"]\n\n1 ok')
        outbox.reconcile(self.batch)
        self.assertEqual(store.load(one['section'])['status'], 'Goedgekeurd')
        self.draft(text='New version.')
        outbox.publish(self.batch, '')
        self.reply('[Replying to your previous message: "'+first+'"]\n\n1 ok')
        outbox.reconcile(self.batch)
        self.assertEqual(store.load(one['section'])['status'], 'Review nodig')
        current = self.publications[-1][:500]
        self.reply('[Replying to your previous message: "'+current+'"]\n\n1 ok')
        self.monday()
        outbox.claim(self.batch, 1, self.check(one['section']))


if __name__ == '__main__':
    unittest.main()
