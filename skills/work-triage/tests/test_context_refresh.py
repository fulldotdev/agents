"""Read-only collectors and isolated durable-ledger regression coverage."""
import copy
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import collect
import common
import gmail
import incremental
import notion
import pending
import slack
import t3_threads
import whatsapp


class ContextRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cursors.json"
        self.args = collect.build_parser().parse_args([
            "triage", "--incremental", "--owner", "test", "--source", "whatsapp",
            "--before", "2026-09-11T15:00:00Z", "--state-file", str(self.path),
        ])
        self.item = {"chat_id": "customer", "messages": [
            {"id": "sent", "timestamp": "2026-09-10T07:00:00Z", "text": "Agreed", "is_sent_by_me": True},
        ]}
        self.source = patch.object(collect, "collect_source", return_value={"ok": True, "complete": True, "items": [self.item]}).start()
        self.context = patch.object(collect.notion, "collect_work_context", return_value={
            "ok": True, "complete": True, "lanes": {"tasks": {"items": [
                {"id": "old-active", "status": "Doing", "edited": "2026-01-01", "companies": ["company"]},
            ]}},
        }).start()
        self.addCleanup(patch.stopall)

    def test_old_pending_and_acknowledged_context_survive_refresh_without_double_processing(self):
        first = collect.triage(self.args)
        state = incremental.load(self.path)
        keys = list(first["queue"]["events"])
        sent = next(k for k in keys if k.startswith("whatsapp:"))
        pending.apply(state, "test", [{"op": "ack", "event": sent, "outcome": "no_action", "note": "Original sent reply and destination checked"}])
        pending.finish(state, "test")
        # An unresolved event may predate even the refreshed source window.
        state["backlog"]["meetings:older"] = {"lane": "meetings", "signature": "older", "item": {"id": "older"}, "status": "retry", "actions": []}
        incremental.save(state, self.path)
        second = collect.triage(self.args)
        self.assertNotIn(sent, second["queue"]["events"])
        self.assertIn("meetings:older", second["queue"]["events"])
        self.assertEqual(second["groups"]["incoming"]["sources"]["whatsapp"]["items"], [self.item])
        self.assertEqual(second["groups"]["work_context"]["lanes"]["tasks"]["items"][0]["companies"], ["company"])
        self.assertEqual(common.iso_utc(self.source.call_args.args[1]), "2026-09-09T22:00:00Z")
        third = collect.triage(self.args)
        self.assertEqual(second["queue"]["batch_id"], third["queue"]["batch_id"])
        self.assertEqual(second["queue"]["events"], third["queue"]["events"])

    def test_partial_refresh_preserves_previous_failed_proposal_and_intent(self):
        first = collect.triage(self.args)
        state = incremental.load(self.path)
        event = next(iter(first["queue"]["events"]))
        pending.apply(state, "test", [{"op": "prepare", "event": event, "key": "stable", "kind": "context_updated", "target": "original destination"}])
        state["pending"]["proposals"]["slack"] = {"complete": False, "before": "2026-09-10T10:00:00Z"}
        incremental.save(state, self.path)
        collect.triage(self.args)
        state = incremental.load(self.path)
        self.assertFalse(state["pending"]["proposals"]["slack"]["complete"])
        self.assertEqual(state["pending"]["events"][event]["actions"], ["stable"])
        self.assertEqual(state["actions"]["stable"]["status"], "prepared")

    def test_preview_includes_older_backlog_without_mutating_state(self):
        state = {"version": 2, "lanes": {}, "backlog": {"meetings:older": {
            "lane": "meetings", "signature": "older", "item": {"id": "older"}, "status": "retry", "actions": [],
        }}}
        incremental.save(state, self.path)
        original = self.path.read_bytes()
        self.args.no_commit_state = True
        result = collect.triage(self.args)
        self.assertIn("meetings:older", result["queue"]["events"])
        self.assertFalse(result["state_committed"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_incomplete_refresh_never_advances_cursor(self):
        self.source.return_value = {"ok": True, "complete": False, "items": []}
        collect.triage(self.args)
        state = incremental.load(self.path)
        pending.finish(state, "test")
        self.assertNotIn("cursor", state["lanes"]["whatsapp"])

    def test_default_window_covers_amsterdam_dst_boundary(self):
        after, _ = collect.incoming_window(None, datetime(2026, 3, 30, 7, tzinfo=timezone.utc))
        self.assertEqual(common.iso_utc(after), "2026-03-28T23:00:00Z")


class CollectorTests(unittest.TestCase):
    def test_all_open_t3_includes_stale_and_snoozed_but_not_settled_or_archived(self):
        rows = [
            {"threadId": "stale", "updatedAt": "2020-01-01T00:00:00Z"},
            {"threadId": "snoozed", "snoozedUntil": "2026-09-12T08:00:00Z", "settledAt": "2026-09-01T00:00:00Z"},
            {"threadId": "settled", "settledOverride": "settled"},
            {"threadId": "archived", "archivedAt": "2026-09-01T00:00:00Z"},
        ]
        args = collect.build_parser().parse_args(["triage", "--limit", "1"])
        with patch.object(t3_threads, "helper", return_value=rows):
            result = collect.collect_source("t3_threads", datetime.now(timezone.utc), datetime.now(timezone.utc), args, True)
        self.assertEqual({i["thread_id"] for i in result["items"]}, {"stale", "snoozed"})
        self.assertEqual(result["count"], 2)
        self.assertTrue(result["complete"])
        self.assertTrue(next(i for i in result["items"] if i["thread_id"] == "snoozed")["state"]["snoozed"])

    def test_notion_reads_all_pages_even_beyond_limit(self):
        calls = []
        def query(_id, payload):
            calls.append(dict(payload))
            if not payload.get("start_cursor"):
                return {"results": [{"id": "first", "properties": {}}], "has_more": True, "next_cursor": "next"}
            return {"results": [{"id": "second", "properties": {}}], "has_more": False, "next_cursor": None}
        with patch.object(notion, "notion_query", side_effect=query):
            items = notion.triage_tasks(limit=1)
        self.assertEqual([i["id"] for i in items], ["first", "second"])
        self.assertEqual(calls[1]["start_cursor"], "next")
        self.assertIn("Edited", str(calls[0]["filter"]))
        self.assertIn("Done", str(calls[0]["filter"]))
        self.assertIn("Canceled", str(calls[0]["filter"]))
        self.assertIn("Paused", notion.TRIAGE_PROJECT_STATUSES)

    def test_notion_missing_pagination_cursor_fails_closed(self):
        with patch.object(notion, "notion_query", return_value={"results": [], "has_more": True}):
            with self.assertRaisesRegex(RuntimeError, "pagination"):
                notion.active_projects()

    def test_whatsapp_grows_query_preserving_timestamp_ties_and_outgoing_without_recovery(self):
        messages = [{"ChatJID": "chat", "MsgID": str(i), "Timestamp": "2026-09-10T10:00:00Z", "FromMe": i == 0, "MediaType": "image"} for i in range(5)]
        limits = []
        def command(args):
            if "chats" in args: return {"data": []}
            size = int(args[args.index("--limit") + 1])
            limits.append(size)
            self.assertIn("--read-only", args)
            return {"data": {"messages": messages[:size]}}
        with patch.object(whatsapp, "MAX_ITEMS_PER_LANE", 2), patch.object(whatsapp, "json_cmd", side_effect=command), patch.object(whatsapp, "media", return_value={"saved_paths": []}), patch.object(whatsapp, "recover_missing_media") as recover:
            result = whatsapp.collect(datetime.now(timezone.utc), datetime.now(timezone.utc), recover_media=False)
        self.assertEqual(limits, [2, 4, 8])
        self.assertEqual(len(result[0]["messages"]), 5)
        self.assertTrue(result[0]["messages"][0]["is_sent_by_me"])
        recover.assert_not_called()

    def test_slack_search_and_replies_follow_pages(self):
        with patch.object(slack, "api", side_effect=[
            {"messages": {"matches": [{"ts": "1"}], "total": 2, "paging": {"pages": 2}}},
            {"messages": {"matches": [{"ts": "2"}], "total": 2, "paging": {"pages": 2}}},
        ]) as api:
            self.assertEqual(len(slack.slack_search_messages("query")), 2)
            self.assertEqual(api.call_args.args[1]["page"], "2")
        a, b = datetime.fromtimestamp(0, timezone.utc), datetime.fromtimestamp(10, timezone.utc)
        with patch.object(slack, "api", side_effect=[
            {"messages": [{"ts": "1"}], "has_more": True, "response_metadata": {"next_cursor": "next"}},
            {"messages": [{"ts": "2"}], "has_more": False},
        ]):
            self.assertEqual(len(slack.replies("c", "1", a, b)), 2)

    def test_calendar_does_not_clip_the_all_pages_response(self):
        with patch.object(collect.calendar_source, "fetch_events", return_value=[{"id": str(i)} for i in range(3)]):
            value = collect.calendar_source.collect_account("me", datetime.now(timezone.utc), datetime.now(timezone.utc), limit=1)
        self.assertEqual(len(value["items"]), 3)
        self.assertFalse(incremental.is_saturated("calendar", {"sources": [value]}, 1))

    def test_gmail_all_pages_completion_overrides_page_size(self):
        with patch.object(gmail, "json_cmd", return_value={"messages": [{"id": str(i), "threadId": "t", "labels": ["SENT"]} for i in range(3)]}) as cmd:
            value = gmail.collect_account("me", limit=1)
        self.assertIn("--all", cmd.call_args.args[0])
        self.assertFalse(incremental.is_saturated("gmail", {"sources": [value]}, 1))


class RevisionTests(unittest.TestCase):
    def test_content_edits_are_new_but_downloads_and_legacy_receipts_do_not_replay(self):
        for lane, item in [
            ("slack", {"workspace_id": "w", "channel_id": "c", "thread_ts": "1", "ts": "1", "in_window": True, "text": "original"}),
            ("whatsapp", {"chat_id": "c", "messages": [{"id": "1", "timestamp": "same", "text": "original", "media": {"type": "image"}}]}),
        ]:
            with self.subTest(lane=lane):
                base = pending.event_signature(lane, item)
                state = {"version": 2, "owner": "test", "lanes": {lane: {"seen": [base]}}}
                def stage():
                    return pending.stage(state, {"groups": {"incoming": {"sources": {lane: {"items": [copy.deepcopy(item)]}}}}}, {lane: {"before": "2026-09-11T15:00:00Z", "complete": True}})
                self.assertFalse(stage()["queue"]["events"])
                edited = item if lane == "slack" else item["messages"][0]
                edited["text"] = "corrected"
                result = stage()
                self.assertEqual(len(result["queue"]["events"]), 1)
                event = next(iter(result["queue"]["events"]))
                self.assertNotEqual(event, f"{lane}:{base}")
                pending.apply(state, "test", [{"op": "ack", "event": event, "outcome": "no_action", "note": "Correction reconciled with original and destination"}])
                pending.finish(state, "test")
                edited["local_path"] = "/new/download"
                self.assertFalse(stage()["queue"]["events"])


class ReviewRegressionTests(unittest.TestCase):
    def test_reverting_content_is_new_but_unchanged_reads_do_not_replay(self):
        state = {"owner": "test", "lanes": {}}
        for text, expected in [("A", 1), ("A", 0), ("B", 1), ("B", 0), ("A", 1)]:
            item = {"chat_id": "c", "messages": [{"id": "1", "timestamp": "same", "text": text}]}
            result = pending.stage(state, {"groups": {"incoming": {"sources": {"whatsapp": {"items": [item]}}}}}, {})
            self.assertEqual(result["queue"]["pending_count"], expected)
            pending.apply(state, "test", [{"op": "ack", "event": key, "outcome": "no_action", "note": "Source and destination reconciled"} for key in result["queue"]["events"]])
            pending.finish(state, "test")

    def test_calendar_requests_all_pages_not_just_all_calendars(self):
        with patch.object(collect.calendar_source, "json_cmd", return_value=[]) as command:
            collect.calendar_source.fetch_events("me", datetime.now(timezone.utc), datetime.now(timezone.utc), 1)
        self.assertIn("--all-pages", command.call_args.args[0])
        self.assertIn("--all", command.call_args.args[0])

    def test_real_dispatch_projection_preserves_snoozed_state(self):
        import importlib.util
        import io
        import json
        from contextlib import redirect_stdout
        from types import SimpleNamespace
        path = Path(__file__).parents[2] / "t3-code/scripts/t3_dispatch.py"
        spec = importlib.util.spec_from_file_location("t3_dispatch_review", path)
        assert spec and spec.loader
        dispatch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dispatch)
        shell = {"threads": [{"id": "snoozed", "settledAt": "2026-09-01T00:00:00Z", "snoozedUntil": "2026-09-12T08:00:00Z"}]}
        output = io.StringIO()
        with patch.object(dispatch, "request", return_value=shell), redirect_stdout(output):
            dispatch.command_list(SimpleNamespace(server="test", project_id=None), "test-token")
        rows = json.loads(output.getvalue())
        with patch.object(t3_threads, "helper", return_value=rows):
            result = t3_threads.collect()
        self.assertEqual(result["count"], 1)
        self.assertTrue(result["items"][0]["state"]["snoozed"])

    def test_legacy_pending_edit_supersedes_old_intent_without_losing_it(self):
        old = {"workspace_id": "w", "channel_id": "c", "thread_ts": "1", "ts": "1", "text": "old"}
        base = pending.event_signature("slack", old)
        key = "slack:" + base
        state = {"version": 2, "owner": "test", "lanes": {}, "backlog": {
            key: {"lane": "slack", "signature": base, "item": old, "status": "retry", "actions": ["old-write"]}},
            "actions": {"old-write": {"kind": "context_updated", "target": "original", "status": "prepared"}}}
        fresh = {**old, "text": "corrected"}
        result = pending.stage(state, {"groups": {"incoming": {"sources": {"slack": {"items": [fresh]}}}}}, {})
        events = result["queue"]["events"]
        latest = events[key]["superseded_by"]
        self.assertEqual(events[latest]["item"]["text"], "corrected")
        self.assertEqual(events[key]["actions"], ["old-write"])
        with self.assertRaisesRegex(ValueError, "superseded"):
            pending.apply(state, "test", [{"op": "prepare", "event": key, "key": "another", "kind": "context_updated", "target": "wrong"}])
        pending.apply(state, "test", [{"op": "cancel", "key": "old-write", "note": "Source corrected", "evidence": "Original intent never executed"}])
        self.assertEqual(state["actions"]["old-write"]["status"], "cancelled")

    def test_nested_reply_edit_and_edit_timestamp_change_revision(self):
        item = {"ts": "1", "text": "root", "thread_replies": [{"ts": "2", "text": "old"}]}
        before = pending.source_revision("slack", item)
        item["thread_replies"][0]["text"] = "corrected"
        self.assertNotEqual(before, pending.source_revision("slack", item))
        before = pending.source_revision("slack", item)
        item["edited_at"] = "3"
        self.assertNotEqual(before, pending.source_revision("slack", item))

    def test_calendar_changes_have_verified_deduplicated_reports(self):
        for kind in ("calendar_created", "calendar_updated", "calendar_rescheduled", "calendar_canceled"):
            with self.subTest(kind=kind):
                state = {"owner": "test", "pending": {"events": {"event": {"status": "pending", "actions": []}}}}
                ops = [{"op": "prepare", "event": "event", "key": "calendar-change", "kind": kind, "target": "existing event"},
                       {"op": "resolve", "key": "calendar-change", "receipt": "event-id", "report": {"title": "Event updated", "url": "https://calendar.google.com/calendar/event?eid=test"}}]
                pending.apply(state, "test", ops)
                pending.apply(state, "test", ops)
                self.assertEqual(len(pending.reports(state)), 1)
                self.assertEqual(pending.reports(state)[0]["kind"], kind)


if __name__ == '__main__':
    unittest.main()
