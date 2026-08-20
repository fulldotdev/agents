"""Incremental work-triage tests."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import incremental


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


if __name__ == "__main__":
    unittest.main()
