"""Quality invariants for compact evidence access and the pre-model gate."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compact
import incremental
import pending
import run


def empty_state():
    sources = {lane: {"ok": True, "complete": True, "items": []} for lane in compact.SOURCE_LANES}
    for lane in ("gmail", "calendar"):
        sources[lane] = {"ok": True, "sources": [{"ok": True, "complete": True, "items": []}]}
    return {"version": 2, "lanes": {}, "owner": "test", "last_finished_at": "2026-09-15T04:00:00Z",
            "pending": {"id": "batch", "events": {},
                        "proposals": {lane: {"complete": True, "before": "2026-09-15T05:00:00Z"}
                                      for lane in (*compact.SOURCE_LANES, "work_context")},
                        "result": {"ok": True, "before": "2026-09-15T05:00:00Z",
                                   "groups": {"incoming": {"sources": sources}, "work_context": {"lanes": {
                                       lane: {"ok": True, "items": []} for lane in compact.WORK_LANES}}}}}}


class CompactQualityTests(unittest.TestCase):
    def test_complete_index_and_full_resources_remain_retrievable_without_mutating_state(self):
        state = empty_state()
        tasks = [{"id": f"id-{i}", "code": f"TASK-{i}", "name": "Same name", "status": "Doing",
                  "project": [f"project-{i}"], "resources": [{"url": f"source://{i}", "name": "Original " + "x" * 500}]}
                 for i in range(120)]
        state["pending"]["result"]["groups"]["work_context"]["lanes"]["tasks"]["items"] = tasks
        before = copy.deepcopy(state)
        output = compact.view(state)
        self.assertEqual(len(output["work_index"]["tasks"]), 120)
        self.assertEqual(output["work_index"]["tasks"][80]["project"], ["project-80"])
        self.assertEqual(compact.context(state, "tasks", ["TASK-80"])["items"], [tasks[80]])
        self.assertEqual(compact.context(state, "tasks", query="source://119")["items"], [tasks[119]])
        self.assertEqual(state, before)
        self.assertLess(len(json.dumps(output)), len(json.dumps(pending.view(state))))

    def test_event_read_includes_sent_chat_context_and_pending_old_evidence(self):
        state = empty_state()
        chat = {"chat_id": "customer", "messages": [
            {"id": "request", "text": "Please do this"},
            {"id": "sent", "text": "Already handled", "is_sent_by_me": True}]}
        state["pending"]["result"]["groups"]["incoming"]["sources"]["whatsapp"]["items"] = [chat]
        state["pending"]["events"] = {
            "new": {"lane": "whatsapp", "status": "pending", "actions": ["intent"], "item": {**chat, "messages": chat["messages"][:1]}},
            "old": {"lane": "gmail", "status": "retry", "actions": [], "item": {"id": "old-thread", "body": "Older evidence"}},
        }
        state["actions"] = {"intent": {"status": "prepared", "target": "TASK-1"}}
        result = compact.show(state, ["new", "old"])
        self.assertEqual(result["whatsapp_context"], [chat])
        self.assertEqual(result["events"]["old"]["item"]["body"], "Older evidence")
        self.assertEqual(result["actions"]["intent"]["target"], "TASK-1")
        with self.assertRaises(ValueError):
            compact.show(state, ["new", "missing"])

    def test_empty_complete_batch_is_only_safe_skip(self):
        self.assertFalse(compact.gate(empty_state())["run_model"])
        mutations = [
            lambda s: s["pending"]["proposals"].pop("slack"),
            lambda s: s["pending"]["proposals"]["gmail"].update(complete=False),
            lambda s: s["pending"]["result"].update(ok=False),
            lambda s: s["pending"]["result"]["groups"]["work_context"]["lanes"].pop("companies"),
            lambda s: s["pending"]["events"].update(old={"status": "retry"}),
            lambda s: s.update(backlog={"older": {"status": "pending"}}),
            lambda s: s.update(actions={"uncertain": {"status": "prepared"}}),
            lambda s: s.update(failures={"slack": {"attempts": 1}}),
            lambda s: s.update(reports={"undelivered": {"title": "Done"}}),
            lambda s: s.pop("last_finished_at"),
        ]
        for change in mutations:
            state = empty_state()
            change(state)
            with self.subTest(change=change):
                self.assertTrue(compact.gate(state)["run_model"])

    def test_due_calendar_tasks_and_project_deadlines_are_not_skipped(self):
        for event in [{"start": "2026-09-15T09:00:00Z"}, {"start": "unreadable"}, {}]:
            state = empty_state()
            state["pending"]["result"]["groups"]["incoming"]["sources"]["calendar"]["sources"][0]["items"] = [event]
            self.assertTrue(compact.gate(state)["run_model"])
        for lane, field in [("tasks", "date"), ("projects", "deadline")]:
            for value in [{"start": "2026-09-15"}, {"start": "bad"}, {}]:
                state = empty_state()
                item = {"id": "due", "status": "Doing", field: value or {"start": None}}
                state["pending"]["result"]["groups"]["work_context"]["lanes"][lane]["items"] = [item]
                self.assertTrue(compact.gate(state)["run_model"])

    def test_delivered_and_resolved_reports_do_not_force_model(self):
        state = empty_state()
        state["reports"] = {"sent": {"reported_at": "today"}, "fixed": {"resolved_at": "today"}}
        self.assertFalse(compact.gate(state)["run_model"])


class RunnerQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cursors.json"
        self.args = SimpleNamespace(state_file=str(self.path), model="openai/gpt-5.6-sol", thinking="high", timeout=3600)

    def collect(self, args, actionable=False):
        state = empty_state()
        state["owner"] = args.owner
        if actionable:
            state["reports"] = {"report": {"title": "Outstanding report"}}
        incremental.save(state, self.path)

    def test_empty_run_finishes_checkpoints_without_model(self):
        feedback = {"changed": False, "reason": None, "updated_at_ms": 100}
        with patch.object(run.collect, "triage", side_effect=self.collect), \
             patch.object(run, "feedback_status", return_value=feedback), \
             patch.object(run.subprocess, "run") as model:
            self.assertEqual(run.run(self.args), "NO_REPLY")
            model.assert_not_called()
        state = incremental.load(self.path)
        self.assertNotIn("owner", state)
        self.assertNotIn("pending", state)
        self.assertEqual(len(state["lanes"]), 7)

    def test_actionable_run_uses_native_gateway_without_direct_delivery(self):
        def model(command, **kwargs):
            self.assertEqual(command[:3], ["openclaw", "agent", "--agent"])
            self.assertIn("openai/gpt-5.6-sol", command)
            self.assertNotIn("--deliver", command)
            self.assertIn("Collection has already completed", command[command.index("--message") + 1])
            state = incremental.load(self.path)
            pending.finish(state, state["owner"])
            state.pop("owner")
            incremental.save(state, self.path)
            return subprocess.CompletedProcess(command, 0, json.dumps({"status": "ok", "result": {"payloads": [{"text": "1. Verified report"}], "meta": {}}}), "")
        feedback = {"changed": False, "reason": None, "updated_at_ms": 100}
        with patch.object(run.collect, "triage", side_effect=lambda a: self.collect(a, True)) as collector, \
             patch.object(run, "feedback_status", return_value=feedback), \
             patch.object(run.subprocess, "run", side_effect=model):
            self.assertEqual(run.run(self.args), "1. Verified report")
            collector.assert_called_once()
        self.assertNotIn("triage_feedback_seen_at_ms", incremental.load(self.path))

    def test_new_or_unreadable_triage_feedback_runs_model(self):
        def model(command, **kwargs):
            state = incremental.load(self.path)
            pending.finish(state, state["owner"])
            state.pop("owner")
            incremental.save(state, self.path)
            return subprocess.CompletedProcess(
                command, 0,
                json.dumps({"status": "ok", "result": {"payloads": [{"text": "NO_REPLY"}], "meta": {}}}),
                "",
            )
        for feedback in [
            {"changed": True, "reason": "triage_feedback_changed", "updated_at_ms": 200},
            {"changed": True, "reason": "triage_feedback_unavailable", "updated_at_ms": None},
        ]:
            with self.subTest(feedback=feedback), \
                 patch.object(run.collect, "triage", side_effect=self.collect), \
                 patch.object(run, "feedback_status", return_value=feedback), \
                 patch.object(run.subprocess, "run", side_effect=model):
                self.assertEqual(run.run(self.args), "NO_REPLY")

    def test_feedback_status_uses_the_triage_session_checkpoint(self):
        payload = {"sessions": [{"key": run.TRIAGE_SESSION_KEY, "updatedAt": 200}]}
        response = subprocess.CompletedProcess([], 0, json.dumps(payload), "")
        with patch.object(run.subprocess, "run", return_value=response):
            self.assertFalse(run.feedback_status(200)["changed"])
            self.assertTrue(run.feedback_status(199)["changed"])
        with patch.object(run.subprocess, "run", side_effect=subprocess.SubprocessError):
            self.assertEqual(run.feedback_status(200)["reason"], "triage_feedback_unavailable")

    def test_feedback_checkpoint_advances_only_after_model_acknowledgement(self):
        feedback = {"changed": True, "reason": "triage_feedback_changed", "updated_at_ms": 200}
        def model(command, **kwargs):
            prompt = command[command.index("--message") + 1]
            marker = prompt.split("write exactly 200 to ", 1)[1].split(". Do not write", 1)[0]
            Path(marker).write_text("200\n")
            state = incremental.load(self.path)
            pending.finish(state, state["owner"])
            state.pop("owner")
            incremental.save(state, self.path)
            return subprocess.CompletedProcess(
                command, 0,
                json.dumps({"status": "ok", "result": {"payloads": [{"text": "NO_REPLY"}], "meta": {}}}),
                "",
            )
        with patch.object(run.collect, "triage", side_effect=self.collect), \
             patch.object(run, "feedback_status", return_value=feedback), \
             patch.object(run.subprocess, "run", side_effect=model):
            self.assertEqual(run.run(self.args), "NO_REPLY")
        self.assertEqual(incremental.load(self.path)["triage_feedback_seen_at_ms"], 200)

    def test_retained_owner_reaches_recovery_without_automatic_takeover(self):
        state = empty_state()
        state["owner"] = "previous-worker"
        incremental.save(state, self.path)
        def model(command, **kwargs):
            self.assertEqual(incremental.load(self.path)["owner"], "previous-worker")
            self.assertIn("Age alone is not proof", command[command.index("--message") + 1])
            raise subprocess.TimeoutExpired(command, 1)
        with patch.object(run.collect, "triage") as collector, patch.object(run.subprocess, "run", side_effect=model):
            with self.assertRaises(RuntimeError):
                run.run(self.args)
            collector.assert_not_called()
        self.assertEqual(incremental.load(self.path)["owner"], "previous-worker")

    def test_failed_or_unfinished_output_cannot_be_delivered_as_success(self):
        for envelope in [{"status": "error"}, {"result": {"payloads": []}},
                         {"result": {"payloads": [{"text": "Done", "isError": True}]}},
                         {"result": {"payloads": [{"text": "Done"}], "meta": {"yielded": True}}}]:
            with self.subTest(envelope=envelope), self.assertRaises(RuntimeError):
                run.final_text(envelope)


if __name__ == "__main__":
    unittest.main()
