"""WhatsApp media recovery tests for work-triage."""

import contextlib
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import whatsapp


@contextlib.contextmanager
def no_lock():
    yield


class FakeRunner:
    def __init__(self, tmpdir, recovery_fail=False, restore_fail=False):
        self.tmpdir = Path(tmpdir)
        self.commands = []
        self.recovery_fail = recovery_fail
        self.restore_fail = restore_fail
        self.running = True

    def __call__(self, cmd, timeout=None):
        self.commands.append(cmd)
        if cmd[:3] == ["launchctl", "print", whatsapp.launch_service()]:
            if not self.running:
                raise whatsapp.CommandError(cmd, 3, stderr="service not found")
            plist = whatsapp.launch_agent_plist()
            return SimpleNamespace(stdout=f"path = {plist}\nstate = running\n")
        if cmd[:2] == ["launchctl", "bootout"]:
            self.running = False
            return SimpleNamespace(stdout="")
        if cmd[:2] == ["launchctl", "bootstrap"]:
            self.running = not self.restore_fail
            if self.restore_fail:
                raise whatsapp.CommandError(cmd, 5, stderr="bootstrap failed")
            return SimpleNamespace(stdout="")
        if cmd[:3] == ["launchctl", "kickstart", "-k"]:
            return SimpleNamespace(stdout="")
        if cmd[:2] == ["wacli", "--json"]:
            msg_id = cmd[cmd.index("--id") + 1]
            chat_id = cmd[cmd.index("--chat") + 1]
            lock_wait = cmd[cmd.index("--lock-wait") + 1]
            if lock_wait == whatsapp.DIRECT_LOCK_WAIT:
                raise whatsapp.CommandError(cmd, 1, stderr="store lock timeout")
            if self.recovery_fail:
                raise whatsapp.CommandError(cmd, 2, stderr=f"download failed for {msg_id}")
            target = self.tmpdir / "media" / chat_id.replace("@", "_") / msg_id / "media.bin"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("ok")
            return SimpleNamespace(stdout="{}")
        raise AssertionError(f"unexpected command: {cmd}")

    def count(self, *prefix):
        return sum(1 for cmd in self.commands if cmd[: len(prefix)] == list(prefix))


class WhatsAppMediaRecoveryTests(unittest.TestCase):
    def test_collect_existing_media_does_not_recover(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["WACLI_STORE_DIR"] = tmp
            media_path = Path(tmp) / "media" / "chat_example.com" / "m1" / "photo.jpg"
            media_path.parent.mkdir(parents=True)
            media_path.write_text("image")

            def fake_json_cmd(cmd):
                if cmd[3:5] == ["chats", "list"]:
                    return {"data": [{"jid": "chat@example.com", "name": "Chat"}]}
                return {
                    "data": {
                        "messages": [
                            {
                                "ChatJID": "chat@example.com",
                                "MsgID": "m1",
                                "FromMe": True,
                                "MediaType": "image",
                                "Timestamp": "2026-07-31T08:00:00Z",
                            }
                        ]
                    }
                }

            with mock.patch.object(whatsapp, "json_cmd", side_effect=fake_json_cmd), mock.patch.object(whatsapp, "recover_missing_media", return_value={}) as recover:
                items = whatsapp.collect(datetime(2026, 7, 31, tzinfo=timezone.utc), datetime(2026, 8, 1, tzinfo=timezone.utc))

            recover.assert_called_once_with([])
            self.assertTrue(items[0]["messages"][0]["is_sent_by_me"])
            self.assertEqual(items[0]["messages"][0]["media"]["saved_paths"], [str(media_path)])
            self.assertNotIn("recovery", items[0]["messages"][0]["media"])

    def test_successful_batched_recovery_unloads_and_restores_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["WACLI_STORE_DIR"] = tmp
            plist = Path(tmp) / f"{whatsapp.LAUNCH_AGENT_LABEL}.plist"
            plist.write_text("<plist/>")
            runner = FakeRunner(tmp)

            with mock.patch.object(whatsapp.platform, "system", return_value="Darwin"), mock.patch.object(whatsapp, "launch_agent_plist", return_value=plist):
                result = whatsapp.recover_missing_media(
                    [{"chat_id": "chat@example.com", "message_id": "m1"}, {"chat_id": "chat@example.com", "message_id": "m2"}],
                    runner=runner,
                    lock_context=no_lock,
                    sleep=lambda _: None,
                )

            self.assertEqual(runner.count("launchctl", "bootout"), 1)
            self.assertEqual(runner.count("launchctl", "bootstrap"), 1)
            self.assertEqual(runner.count("launchctl", "kickstart", "-k"), 0)
            self.assertEqual(result[("chat@example.com", "m1")]["status"], "recovered")
            self.assertEqual(result[("chat@example.com", "m2")]["status"], "recovered")

    def test_download_failure_still_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["WACLI_STORE_DIR"] = tmp
            plist = Path(tmp) / f"{whatsapp.LAUNCH_AGENT_LABEL}.plist"
            plist.write_text("<plist/>")
            runner = FakeRunner(tmp, recovery_fail=True)

            with mock.patch.object(whatsapp.platform, "system", return_value="Darwin"), mock.patch.object(whatsapp, "launch_agent_plist", return_value=plist):
                result = whatsapp.recover_missing_media(
                    [{"chat_id": "chat@example.com", "message_id": "m1"}],
                    runner=runner,
                    lock_context=no_lock,
                    sleep=lambda _: None,
                )

            self.assertEqual(runner.count("launchctl", "bootout"), 1)
            self.assertEqual(runner.count("launchctl", "bootstrap"), 1)
            self.assertEqual(result[("chat@example.com", "m1")]["status"], "failed")
            self.assertIn("download failed", result[("chat@example.com", "m1")]["error"])

    def test_restore_failure_is_surfaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["WACLI_STORE_DIR"] = tmp
            plist = Path(tmp) / f"{whatsapp.LAUNCH_AGENT_LABEL}.plist"
            plist.write_text("<plist/>")
            runner = FakeRunner(tmp, restore_fail=True)

            with mock.patch.object(whatsapp.platform, "system", return_value="Darwin"), mock.patch.object(whatsapp, "launch_agent_plist", return_value=plist), mock.patch.object(whatsapp, "SERVICE_WAIT_SECONDS", 0.01):
                with self.assertRaises(whatsapp.MediaRecoveryError) as raised:
                    whatsapp.recover_missing_media(
                        [{"chat_id": "chat@example.com", "message_id": "m1"}],
                        runner=runner,
                        lock_context=no_lock,
                        sleep=lambda _: None,
                    )

            self.assertEqual(runner.count("launchctl", "bootout"), 1)
            self.assertEqual(runner.count("launchctl", "bootstrap"), 1)
            self.assertIn("failed to restart", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
