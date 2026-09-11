"""Approval provenance and migration regressions using real ingress-shaped rows."""
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import outbox
import store
from planning_history import openclaw_messages, OPENCLAW_ID_BASE
from test_outbox import WeeklyRehearsal


class OpenClawRehearsal(WeeklyRehearsal):
    def setUp(self):
        super().setUp()
        self.ingress = Path(self.temp.name) / 'openclaw.sqlite'
        with sqlite3.connect(self.ingress) as c:
            c.execute('CREATE TABLE channel_ingress_events(queue_name TEXT,event_id TEXT,payload_json TEXT,channel_id TEXT,account_id TEXT,received_at INTEGER)')
        for key, value in [('OPENCLAW_DB', self.ingress), ('RUNTIME', 'openclaw')]:
            p = patch.object(outbox, key, value); p.start(); self.addCleanup(p.stop)
        self.update_id = 200

    def send(self, args, **kwargs):
        from types import SimpleNamespace
        self.assertEqual(args[:8], ['openclaw', 'message', 'send', '--channel', 'telegram', '--target', outbox.CHAT, '--message'])
        self.publications.append(args[8])
        return SimpleNamespace(returncode=0, stdout=json.dumps({'action':'send','channel':'telegram',
            'payload':{'ok':True,'messageId':str(len(self.publications)),'chatId':outbox.CHAT}}))

    def reply(self, text, session='sil', **extra):
        self.clock += timedelta(seconds=1); self.update_id += 1
        message = {'message_id':self.update_id,'text':text,'date':int(self.clock.timestamp()),
                   'chat':{'id':int(outbox.CHAT) if session!='wrong-chat' else -1},
                   'from':{'id':int(outbox.SIL) if session!='other' else 123,'is_bot':False}, **extra}
        self.ingest(message)
        return message['message_id']

    def ingest(self, message, edited=False):
        payload = {'version':1,'updateId':self.update_id,'receivedAt':int(self.clock.timestamp()*1000),
                   'update':{'update_id':self.update_id,'edited_message' if edited else 'message':message}}
        with sqlite3.connect(self.ingress) as c:
            c.execute('INSERT INTO channel_ingress_events VALUES (?,?,?,?,?,?)',
                      ('telegram:default',str(self.update_id).zfill(16),json.dumps(payload),'telegram','default',int(self.clock.timestamp()*1000)))

    def edit_reply(self, message_id, text):
        self.clock += timedelta(seconds=1)
        self.update_id += 1
        with sqlite3.connect(self.ingress) as c:
            payloads = [json.loads(row[0]) for row in c.execute('SELECT payload_json FROM channel_ingress_events')]
        message = next(payload['update']['message'] for payload in payloads
                       if payload['update'].get('message', {}).get('message_id') == message_id)
        message['edit_date'] = int(self.clock.timestamp())
        if text is None:
            message.pop('text')
            message['caption'] = '1 ok'
        else:
            message['text'] = text
        self.ingest(message, edited=True)

    def test_edit_to_acknowledgement_revokes_original_approval_at_claim(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        message_id = self.reply('1 ok')
        outbox.reconcile(self.batch)
        self.edit_reply(message_id, 'bedankt')
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertIsNone(store.load(one['section'])['approval'])

    def test_edit_all_to_one_revokes_omitted_item_but_approves_retained_item(self):
        one, two = self.draft(), self.draft('project-2')
        outbox.publish(self.batch, '')
        message_id = self.reply('alles akkoord')
        outbox.reconcile(self.batch)
        self.edit_reply(message_id, '1 ok')
        self.monday()
        self.assertEqual(outbox.claim(self.batch, 1, self.check(one['section']))['send_exactly']['text'], one['text'])
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 2, self.check(two['section']))
        self.assertIsNone(store.load(two['section'])['approval'])

    def test_edit_without_text_revokes_original_approval(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        message_id = self.reply('1 ok')
        outbox.reconcile(self.batch)
        self.edit_reply(message_id, None)
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertIsNone(store.load(one['section'])['approval'])

    def test_edit_of_old_plain_approval_cannot_approve_new_draft(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        message_id = self.reply('1 ok')
        outbox.reconcile(self.batch)
        self.clock += timedelta(seconds=1)
        self.draft(text='Changed customer message.')
        outbox.publish(self.batch, '')
        self.edit_reply(message_id, '1 akkoord')
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertIsNone(store.load(one['section'])['approval'])

    def test_rollback_processes_hermes_withdrawal_and_fresh_approval(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        outbox.reconcile(self.batch)
        with patch.object(outbox, 'RUNTIME', 'hermes'):
            WeeklyRehearsal.reply(self, '1 intrekken')
            outbox.reconcile(self.batch)
            self.assertEqual(store.load(one['section'])['status'], 'Overslaan')
            WeeklyRehearsal.reply(self, '1 ok')
            self.monday()
            self.assertEqual(outbox.claim(self.batch, 1, self.check(one['section']))['send_exactly']['text'], one['text'])

    def test_rollback_migrates_legacy_native_cursor(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        outbox.reconcile(self.batch)
        batch = store.load(self.batch)
        batch.pop('message_cursors')
        store.save(self.batch, batch)
        with patch.object(outbox, 'RUNTIME', 'hermes'):
            WeeklyRehearsal.reply(self, '1 intrekken')
            self.monday()
            with self.assertRaises(ValueError):
                outbox.claim(self.batch, 1, self.check(one['section']))
            self.assertEqual(store.load(one['section'])['status'], 'Overslaan')

    def test_legacy_native_cursor_does_not_replay_old_hermes_approval(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        WeeklyRehearsal.reply(self, '1 ok')
        outbox.reconcile(self.batch)
        self.reply('1 intrekken')
        outbox.reconcile(self.batch)
        batch = store.load(self.batch)
        batch.pop('message_cursors')
        store.save(self.batch, batch)
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertEqual(store.load(one['section'])['status'], 'Overslaan')

    def test_same_second_native_reply_approves_exact_review(self):
        one = self.draft()
        self.clock = self.clock.replace(microsecond=100000)
        def fast_reply(args, **kwargs):
            receipt = self.send(args, **kwargs)
            self.clock += timedelta(milliseconds=100)
            self.update_id += 1
            self.ingest({'message_id':self.update_id,'text':'1 ok','date':int(self.clock.timestamp()),
                         'chat':{'id':int(outbox.CHAT)}, 'from':{'id':int(outbox.SIL),'is_bot':False},
                         'reply_to_message':{'message_id':1}})
            self.clock += timedelta(milliseconds=100)
            return receipt
        with patch.object(outbox.subprocess, 'run', side_effect=fast_reply):
            outbox.publish(self.batch, '')
        outbox.reconcile(self.batch)
        self.assertEqual(store.load(one['section'])['status'], 'Goedgekeurd')
        self.monday()
        self.assertEqual(outbox.claim(self.batch, 1, self.check(one['section']))['send_exactly']['text'], one['text'])

    def test_forwarded_approval_is_not_authority(self):
        one=self.draft();outbox.publish(self.batch,'')
        self.reply('alles akkoord',forward_origin={'type':'user','sender_user':{'id':int(outbox.SIL)}})
        self.assertEqual(outbox.reconcile(self.batch)['changed'],[])
        self.monday()
        with self.assertRaises(ValueError):outbox.claim(self.batch,1,self.check(one['section']))

    def test_native_reply_targets_exact_review(self):
        self.draft();outbox.publish(self.batch,'')
        self.reply('alles akkoord',reply_to_message={'message_id':999})
        self.assertEqual(outbox.reconcile(self.batch)['changed'][0]['status'],'Review nodig')

    def test_missing_ingress_cannot_claim(self):
        one=self.draft();outbox.publish(self.batch,'');self.reply('alles akkoord');outbox.reconcile(self.batch)
        self.monday();self.ingress.unlink()
        with self.assertRaises(sqlite3.OperationalError):outbox.claim(self.batch,1,self.check(one['section']))

    def test_migration_reads_historical_hermes_approval(self):
        one=self.draft();outbox.publish(self.batch,'')
        WeeklyRehearsal.reply(self,'alles akkoord')
        self.monday()
        self.assertEqual(outbox.claim(self.batch,1,self.check(one['section']))['send_exactly']['text'],one['text'])

    def test_cron_review_is_sent_and_can_be_approved(self):
        self.draft();self.assertTrue(outbox.publish(self.batch,'')['published']);self.reply('alles akkoord')
        self.assertEqual(outbox.reconcile(self.batch)['changed'][0]['status'],'Goedgekeurd')

    def test_fast_native_reply_approves_the_review_already_received(self):
        from datetime import timedelta
        self.draft()
        def slow_send(args, **kwargs):
            receipt=self.send(args, **kwargs)
            self.reply('1 ok',reply_to_message={'message_id':1})
            self.clock += timedelta(seconds=5)
            return receipt
        with patch.object(outbox.subprocess,'run',side_effect=slow_send):outbox.publish(self.batch,'')
        self.assertEqual(outbox.reconcile(self.batch)['changed'][0]['status'],'Goedgekeurd')


if __name__=='__main__':unittest.main()
