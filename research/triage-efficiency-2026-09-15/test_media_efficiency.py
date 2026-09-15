"""Regression checks for overlap-safe triage attachment recovery."""

import contextlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "work-triage" / "scripts"))
import whatsapp
import gmail


class MediaEfficiencyTests(unittest.TestCase):
    def test_reuses_download_completed_while_waiting_for_recovery_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "media" / "chat_example.com" / "m1" / "photo.jpg"

            @contextlib.contextmanager
            def download_while_waiting():
                target.parent.mkdir(parents=True)
                target.write_bytes(b"image")
                yield

            with mock.patch.dict(os.environ, {"WACLI_STORE_DIR": tmp}):
                result = whatsapp.recover_missing_media(
                    [{"chat_id": "chat@example.com", "message_id": "m1"}],
                    runner=mock.Mock(side_effect=AssertionError("cached media must not be downloaded again")),
                    lock_context=download_while_waiting,
                )

            self.assertEqual(result[("chat@example.com", "m1")], {
                "status": "recovered",
                "method": "existing_download",
                "recovered_paths": [str(target)],
            })

    def test_zero_byte_attachment_remains_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "media" / "chat_example.com" / "m1" / "photo.jpg"
            target.parent.mkdir(parents=True)
            target.touch()

            with mock.patch.dict(os.environ, {"WACLI_STORE_DIR": tmp}):
                info = whatsapp.media("chat@example.com", "m1")

            self.assertEqual(info["saved_paths"], [])
            self.assertEqual(info["error"], "media_not_downloaded_yet")

    def test_gmail_download_cache_is_separated_by_account_and_rereads_source(self):
        calls = []

        def command(cmd):
            calls.append(cmd)
            return {"thread": {"messages": [{"id": f"m{len(calls)}"}]}, "downloaded": []}

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gmail, "TEMP_ROOT", Path(tmp)), mock.patch.object(gmail, "json_cmd", side_effect=command):
            first = gmail.read_thread("one@example.com", "thread/1", True)
            second = gmail.read_thread("two@example.com", "thread/1", True)

        self.assertEqual(first["thread"]["thread"]["messages"][0]["id"], "m1")
        self.assertEqual(second["thread"]["thread"]["messages"][0]["id"], "m2")
        self.assertNotEqual(calls[0][calls[0].index("--out-dir") + 1], calls[1][calls[1].index("--out-dir") + 1])
        self.assertIn("--use-indexed-attachment-ids", calls[0])
        self.assertIn("--download", calls[0])

    def test_gmail_returns_native_cached_paths_and_new_message_attachments(self):
        responses = [
            {"thread": {"messages": [{"id": "m1"}]}, "downloaded": [{"messageId": "m1", "path": "/cache/m1_0_a.pdf", "cached": True}]},
            {"thread": {"messages": [{"id": "m1"}, {"id": "m2"}]}, "downloaded": [{"messageId": "m1", "path": "/cache/m1_0_a.pdf", "cached": True}, {"messageId": "m2", "path": "/cache/m2_0_b.pdf", "cached": False}]},
        ]
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gmail, "TEMP_ROOT", Path(tmp)), mock.patch.object(gmail, "json_cmd", side_effect=responses):
            first = gmail.read_thread("one@example.com", "t1", True)
            second = gmail.read_thread("one@example.com", "t1", True)

        self.assertTrue(first["thread"]["downloaded"][0]["cached"])
        self.assertEqual([item["messageId"] for item in second["thread"]["downloaded"]], ["m1", "m2"])

    def test_gmail_download_failure_returns_no_result(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(gmail, "TEMP_ROOT", Path(tmp)), mock.patch.object(gmail, "json_cmd", side_effect=RuntimeError("download failed")):
            with self.assertRaisesRegex(RuntimeError, "download failed"):
                gmail.read_thread("one@example.com", "t1", True)


if __name__ == "__main__":
    unittest.main()
