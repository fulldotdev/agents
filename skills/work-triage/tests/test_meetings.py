"""Meeting collector behavior tests."""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import meetings


class MeetingTests(unittest.TestCase):
    def test_changed_meeting_is_included_after_its_start_window(self):
        row = {"properties": {
            "When": {"date": {"start": "2026-08-20T10:00:00Z"}},
            "Created": {"created_time": "2026-08-20T09:55:00Z"},
            "Edited": {"last_edited_time": "2026-08-20T11:25:00Z"},
        }}
        after = datetime(2026, 8, 20, 11, 20, tzinfo=timezone.utc)
        before = datetime(2026, 8, 20, 11, 30, tzinfo=timezone.utc)

        self.assertTrue(meetings.include_row(row, after, before))

    def test_meeting_notes_metadata_exposes_ready_transcript_revision(self):
        original = meetings.notion_block
        meetings.notion_block = lambda block_id: {
            "id": block_id,
            "last_edited_time": "2026-08-20T11:25:00Z",
        }
        try:
            result = meetings.meeting_notes_metadata([{
                "id": "notes",
                "type": "meeting_notes",
                "meeting_notes": {
                    "status": "notes_ready",
                    "children": {"transcript_block_id": "transcript"},
                },
            }])
        finally:
            meetings.notion_block = original

        self.assertEqual(result, [{
            "block_id": "notes",
            "status": "notes_ready",
            "transcript_block_id": "transcript",
            "transcript_revision": "2026-08-20T11:25:00Z",
        }])


if __name__ == "__main__":
    unittest.main()
