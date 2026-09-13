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
from test_outbox import WeeklyRehearsal


class OpenClawRehearsal(WeeklyRehearsal):
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

    def test_migrates_legacy_native_cursor(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply('1 ok')
        outbox.reconcile(self.batch)
        batch = store.load(self.batch)
        batch.pop('message_cursors')
        store.save(self.batch, batch)
        self.reply( '1 intrekken')
        self.monday()
        with self.assertRaises(ValueError):
            outbox.claim(self.batch, 1, self.check(one['section']))
        self.assertEqual(store.load(one['section'])['status'], 'Overslaan')

    def test_legacy_native_cursor_does_not_replay_old_approval(self):
        one = self.draft()
        outbox.publish(self.batch, '')
        self.reply( '1 ok')
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
