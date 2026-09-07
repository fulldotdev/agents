"""Incremental work-triage tests."""

import sys
import json
import os
import subprocess
import tempfile
from unittest.mock import patch
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import incremental
import pending
import collect
import gmail


class IncrementalTests(unittest.TestCase):
    def test_t3_threads_are_filtered_by_thread_state(self):
        value = {
            "ok": True,
            "items": [
                {"thread_id": "old", "updated_at": "2026-08-19T10:00:00Z", "state": {}},
                {"thread_id": "new", "updated_at": "2026-08-19T11:00:00Z", "state": {}},
            ],
        }
        old_signature = incremental.item_signature("t3_threads", value["items"][0])
        filtered, signatures = incremental.filter_value("t3_threads", value, [old_signature])

        self.assertEqual([thread["thread_id"] for thread in filtered["items"]], ["new"])
        self.assertEqual(filtered["changed_count"], 1)
        self.assertEqual(len(signatures), 2)

    def test_whatsapp_overlap_dedupes_messages_individually(self):
        value = {"items": [{"chat_id": "chat", "messages": [
            {"id": "1", "timestamp": "2026-08-19T10:00:00Z"},
            {"id": "2", "timestamp": "2026-08-19T10:01:00Z"},
        ]}]}
        seen = [incremental.stable_hash(["chat", "1", "2026-08-19T10:00:00Z"])]
        filtered, signatures = incremental.filter_value("whatsapp", value, seen)

        self.assertEqual([message["id"] for message in filtered["items"][0]["messages"]], ["2"])
        self.assertEqual(filtered["changed_count"], 1)
        self.assertEqual(len(signatures), 2)

    def test_lane_window_replays_only_configured_overlap(self):
        state = {"version": 1, "lanes": {"slack": {"cursor": "2026-08-19T12:00:00Z", "seen": []}}}
        before = datetime(2026, 8, 19, 12, 30, tzinfo=timezone.utc)
        after, _ = incremental.window(state, "slack", before, bootstrap_hours=24, overlap_minutes=10)

        self.assertEqual(after, datetime(2026, 8, 19, 11, 50, tzinfo=timezone.utc))

    def test_saturated_lane_blocks_cursor_advance_decision(self):
        value = {"items": [{"id": "1"}, {"id": "2"}]}
        self.assertTrue(incremental.is_saturated("meetings", value, limit=2))
        self.assertFalse(incremental.is_saturated("meetings", value, limit=3))

    def test_ready_meeting_signature_uses_transcript_revision_not_page_edit(self):
        item = {
            "id": "meeting",
            "when": "2026-08-20T10:00:00Z",
            "properties": {"Edited": {"last_edited_time": "2026-08-20T11:00:00Z"}},
            "meeting_notes": [{
                "block_id": "notes",
                "status": "notes_ready",
                "transcript_block_id": "transcript",
                "transcript_revision": "2026-08-20T10:55:00Z",
            }],
        }
        original = incremental.item_signature("meetings", item)
        item["properties"]["Edited"]["last_edited_time"] = "2026-08-20T12:00:00Z"

        self.assertEqual(incremental.item_signature("meetings", item), original)

        item["meeting_notes"][0]["transcript_revision"] = "2026-08-20T12:01:00Z"
        self.assertNotEqual(incremental.item_signature("meetings", item), original)


class DurableHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cursors.json"
        self.state = {"version": 1, "lanes": {"slack": {
            "cursor": "2026-09-07T09:00:00Z", "seen": ["legacy"],
        }}}
        incremental.save(self.state, self.path)
        self.args = collect.build_parser().parse_args([
            "triage", "--incremental", "--owner", "worker-a", "--source", "slack",
            "--before", "2026-09-07T10:00:00Z", "--state-file", str(self.path),
        ])
        self.item = {"workspace_id": "w", "channel_id": "c", "thread_ts": "t", "ts": "1", "in_window": True}
        self.source = patch.object(collect, "collect_source", return_value={"ok": True, "items": [self.item]})
        self.context = patch.object(collect.notion, "collect_changed_work_context", return_value={"ok": True, "lanes": {}})
        self.source_mock = self.source.start()
        self.context.start()
        self.addCleanup(self.source.stop)
        self.addCleanup(self.context.stop)

    def batch(self):
        result = collect.incremental_triage(self.args)
        return result, next(iter(result["queue"]["events"]))

    def test_crash_after_fetch_keeps_cursor_and_replays_same_batch_without_sources(self):
        first, event_id = self.batch()
        persisted = incremental.load(self.path)
        self.assertEqual(persisted["version"], 2)
        self.assertEqual(persisted["lanes"]["slack"], self.state["lanes"]["slack"])
        self.assertNotIn("cursor", persisted["lanes"]["work_context"])
        second = collect.incremental_triage(self.args)
        self.assertEqual(first["queue"]["batch_id"], second["queue"]["batch_id"])
        self.assertIn(event_id, second["queue"]["events"])
        self.assertEqual(self.source_mock.call_count, 1)

    def test_claim_survives_process_exit_and_explicit_takeover_fences_old_owner(self):
        self.batch()
        self.args.owner = "worker-b"
        with self.assertRaises(ValueError):
            collect.incremental_triage(self.args)
        state = incremental.load(self.path)
        pending.claim(state, "worker-b", previous_owner="worker-a")
        incremental.save(state, self.path)
        with self.assertRaises(ValueError):
            pending.apply(state, "worker-a", [])
        self.assertEqual(collect.incremental_triage(self.args)["queue"]["owner"], "worker-b")

    def test_help_does_not_create_scratch_or_delete_old_pending_attachments(self):
        scratch = Path(self.temp.name) / "scratch"
        scratch.mkdir()
        attachment = scratch / "pending-attachment.txt"
        attachment.write_text("Still needed by deferred event")
        os.utime(attachment, (1, 1))
        result = subprocess.run([sys.executable, str(SCRIPTS / "collect.py"), "--help"],
                                env={**os.environ, "WORK_TRIAGE_TEMP_DIR": str(scratch)},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(scratch.iterdir()), [attachment])
        self.assertEqual(attachment.read_text(), "Still needed by deferred event")

    def test_state_lock_rejects_other_process(self):
        with pending.locked(self.path):
            result = subprocess.run([sys.executable, "-c",
                "import pending,sys; pending.locked(sys.argv[1]).__enter__()", str(self.path)],
                cwd=SCRIPTS, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("holds the state lock", result.stderr)

    def test_external_success_before_ack_requires_reconciliation_then_reuses_receipt(self):
        _, event_id = self.batch()
        state = incremental.load(self.path)
        preparation = {"op": "prepare", "event": event_id, "key": "draft:thread:message", "kind": "draft_created", "target": "account/thread existing drafts"}
        pending.apply(state, "worker-a", [preparation])
        incremental.save(state, self.path)
        # External draft creation succeeds, then the process dies before recording it.
        state = incremental.load(self.path)
        with self.assertRaises(ValueError):
            pending.apply(state, "worker-a", [{"op": "ack", "event": event_id, "outcome": "handled", "note": "draft created"}])
        pending.apply(state, "worker-a", [preparation])
        self.assertEqual(state["actions"][preparation["key"]]["status"], "prepared")
        pending.apply(state, "worker-a", [
            {"op": "resolve", "key": preparation["key"], "receipt": "existing-draft-id", "report": {"title": "Reply", "url": "https://mail.google.com/example"}},
            {"op": "ack", "event": event_id, "outcome": "handled", "note": "Found and verified the existing draft"},
        ])
        pending.finish(state, "worker-a")
        incremental.save(state, self.path)
        state = incremental.load(self.path)
        self.assertEqual(state["lanes"]["slack"]["cursor"], "2026-09-07T10:00:00Z")
        self.assertFalse(state["backlog"])
        self.assertEqual(len(pending.reports(state)), 1)
        pending.apply(state, "worker-a", [{"op": "reported", "key": preparation["key"]}])
        incremental.save(state, self.path)
        self.assertEqual(pending.reports(incremental.load(self.path)), [])

    def test_cancel_unneeded_intent_keeps_evidence_without_false_created_report(self):
        _, event_id = self.batch()
        state = incremental.load(self.path)
        pending.apply(state, "worker-a", [
            {"op": "prepare", "event": event_id, "key": "reply", "kind": "draft_created", "target": "thread"},
            {"op": "cancel", "key": "reply", "note": "Already answered before write", "evidence": "sent-message-id; no draft exists"},
            {"op": "ack", "event": event_id, "outcome": "no_action", "note": "Sil answered"},
        ])
        pending.finish(state, "worker-a")
        self.assertEqual(state["actions"]["reply"]["status"], "cancelled")
        self.assertEqual(pending.reports(state), [])
        self.assertEqual(state["lanes"]["slack"]["cursor"], "2026-09-07T10:00:00Z")
        with self.assertRaises(ValueError):
            pending.apply(state, "worker-a", [{"op": "resolve", "key": "reply", "receipt": "unexpected"}])

    def test_execution_failure_requires_distinct_attempts_and_clears_on_recovery(self):
        _, event_id = self.batch()
        state = incremental.load(self.path)
        retry = {"op": "retry", "event": event_id, "note": "T3 runtime unavailable"}
        report = {"op": "report_failure", "event": event_id, "title": "Restart T3 runtime"}
        pending.apply(state, "worker-a", [retry, retry])
        with self.assertRaises(ValueError):
            pending.apply(state, "worker-a", [report])
        pending.finish(state, "worker-a")
        incremental.save(state, self.path)
        collect.incremental_triage(self.args)
        state = incremental.load(self.path)
        pending.apply(state, "worker-a", [retry, report])
        self.assertEqual(len(pending.reports(state)), 1)
        pending.apply(state, "worker-a", [{"op": "ack", "event": event_id, "outcome": "no_action", "note": "No longer needed"}])
        self.assertEqual(pending.reports(state), [])

    def test_deferred_event_keeps_payload_and_does_not_block_healthy_lane(self):
        _, event_id = self.batch()
        state = incremental.load(self.path)
        pending.apply(state, "worker-a", [{"op": "retry", "event": event_id, "note": "Waiting for full evidence"}])
        pending.finish(state, "worker-a")
        self.assertEqual(state["lanes"]["slack"]["cursor"], "2026-09-07T09:00:00Z")
        self.assertEqual(state["lanes"]["work_context"]["cursor"], "2026-09-07T10:00:00Z")
        self.assertEqual(state["backlog"][event_id]["item"], self.item)
        incremental.save(state, self.path)
        self.source_mock.return_value = {"ok": False, "error": "offline", "items": []}
        resumed = collect.incremental_triage(self.args)
        self.assertIn(event_id, resumed["queue"]["events"])
        self.assertEqual(resumed["queue"]["events"][event_id]["note"], "Waiting for full evidence")

    def test_invalid_batched_ack_does_not_persist_prior_operation(self):
        _, event_id = self.batch()
        operations = Path(self.temp.name) / "operations.json"
        operations.write_text(json.dumps([
            {"op": "ack", "event": event_id, "outcome": "no_action", "note": "No open question"},
            {"op": "ack", "event": "missing", "outcome": "no_action", "note": "invalid"},
        ]))
        args = collect.build_parser().parse_args(["queue", "apply", "--owner", "worker-a", "--state-file", str(self.path), "--file", str(operations)])
        with self.assertRaises(ValueError):
            pending.command(args)
        self.assertEqual(incremental.load(self.path)["pending"]["events"][event_id]["status"], "pending")

    def test_failed_save_leaves_previous_complete_state_readable(self):
        with patch.object(incremental.os, "replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                incremental.save({"version": 2, "lanes": {}}, self.path)
        self.assertEqual(incremental.load(self.path)["lanes"], self.state["lanes"])

    def test_failure_reporting_requires_two_attempts_and_dedupes_until_recovery(self):
        self.source_mock.return_value = {"ok": False, "error": "offline", "items": []}
        collect.incremental_triage(self.args)
        state = incremental.load(self.path)
        report = {"op": "report_failure", "lane": "slack", "title": "Reconnect Slack"}
        with self.assertRaises(ValueError):
            pending.apply(state, "worker-a", [report])
        pending.finish(state, "worker-a")
        incremental.save(state, self.path)
        collect.incremental_triage(self.args)
        state = incremental.load(self.path)
        pending.apply(state, "worker-a", [report, report])
        self.assertEqual(len(pending.reports(state)), 1)
        self.assertEqual(state["failures"]["slack"]["attempts"], 2)
        pending.finish(state, "worker-a")
        incremental.save(state, self.path)
        self.source_mock.return_value = {"ok": True, "items": []}
        recovered = collect.incremental_triage(self.args)
        self.assertEqual(recovered["queue"]["reports"], [])
        self.assertNotIn("slack", recovered["queue"]["failures"])

    def test_failed_first_collection_preserves_bootstrap_floor_days_later(self):
        incremental.save({"version": 1, "lanes": {}}, self.path)
        self.source_mock.return_value = {"ok": False, "error": "offline", "items": []}
        collect.incremental_triage(self.args)
        state = incremental.load(self.path)
        first_floor = state["lanes"]["slack"]["bootstrap_after"]
        self.assertNotIn("cursor", state["lanes"]["slack"])
        pending.finish(state, "worker-a")
        incremental.save(state, self.path)
        self.args.before = "2026-09-10T10:00:00Z"
        collect.incremental_triage(self.args)
        self.assertEqual(incremental.iso_utc(self.source_mock.call_args.args[1]), first_floor)

    def test_preview_does_not_claim_or_stage_or_advance(self):
        self.args.no_commit_state = True
        before = self.path.read_bytes()
        result = collect.incremental_triage(self.args)
        self.assertFalse(result["state_committed"])
        self.assertEqual(self.path.read_bytes(), before)


class GmailIndexTests(unittest.TestCase):
    def test_archived_received_index_does_not_fetch_bodies_or_attachments(self):
        after = datetime(2026, 9, 7, 9, tzinfo=timezone.utc)
        before = datetime(2026, 9, 7, 10, tzinfo=timezone.utc)
        with patch.object(gmail, "json_cmd", return_value={"messages": [{
            "id": "m", "threadId": "t", "date": "2026-09-07 09:30", "labels": ["UNREAD"], "from": "customer@example.com",
        }]}) as command:
            result = gmail.collect_account("me@example.com", after, before)
        args = command.call_args.args[0]
        query = args[args.index("search") + 1]
        self.assertNotIn("in:inbox", query)
        self.assertNotIn("in:sent", query)
        self.assertIn("-in:spam", query)
        self.assertIn("-in:trash", query)
        self.assertNotIn("--full", args)
        self.assertNotIn("--download", args)
        self.assertEqual(command.call_count, 1)
        self.assertEqual(result["items"][0]["messages"][0]["id"], "m")
        self.assertNotIn("body", result["items"][0]["messages"][0])

    def test_message_pagination_saturates_even_one_large_thread(self):
        value = {"sources": [{"items": [{"id": "one-thread"}], "message_count": 200, "complete": False}]}
        self.assertTrue(incremental.is_saturated("gmail", value, 200))

    def test_unread_change_does_not_reprocess_same_mail(self):
        item = {"id": "t", "account": "me", "has_unread": True, "messages": [{"id": "m", "date": "d", "in_window": True}]}
        signature = incremental.item_signature("gmail", item)
        item["has_unread"] = False
        self.assertEqual(signature, incremental.item_signature("gmail", item))


if __name__ == "__main__":
    unittest.main()
