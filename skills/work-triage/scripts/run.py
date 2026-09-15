#!/usr/bin/env python3
"""Collect once, skip proven-empty batches, otherwise run the existing Codex agent."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import collect
import compact
import incremental
import pending


def final_text(envelope):
    if envelope.get("status") not in {None, "ok", "completed"}:
        raise RuntimeError("Codex did not complete: " + str(envelope.get("summary") or envelope.get("status")))
    result = envelope.get("result", envelope)
    meta = result.get("meta") or {}
    payloads = result.get("payloads") or []
    if meta.get("aborted") or meta.get("error") or meta.get("yielded") or any(p.get("isError") for p in payloads):
        raise RuntimeError("Codex returned an incomplete or failed triage run; retain the batch for recovery")
    text = "\n".join(p["text"] for p in payloads if p.get("text") and not p.get("isReasoning")).strip()
    if not text:
        raise RuntimeError("Codex returned no final text; delivery outcome is unknown")
    return text


def run(args):
    started = time.monotonic()
    path = Path(args.state_file or incremental.DEFAULT_STATE_FILE).expanduser()
    owner = "triage-" + uuid4().hex
    with pending.locked(path) as state:
        previous_owner = state.get("owner")
    if previous_owner:
        decision = {"run_model": True, "reasons": ["retained_owner_requires_recovery"]}
    else:
        collection_args = collect.build_parser().parse_args([
            "triage", "--incremental", "--compact", "--owner", owner, "--state-file", str(path),
        ])
        collect.triage(collection_args)
        with pending.locked(path) as state:
            pending.require_owner(state, owner)
            decision = compact.gate(state)
            if not decision["run_model"]:
                pending.finish(state, owner)
                state.pop("owner")
                incremental.save(state, path)
    receipt = {"owner": owner, "model": args.model, "thinking": args.thinking, "gate": decision}
    if not decision["run_model"]:
        receipt.update(status="empty", duration_seconds=round(time.monotonic() - started, 2))
        write_receipt(path, receipt)
        return "NO_REPLY"
    skill = Path(__file__).resolve().parents[1]
    prompt = (skill / "references/cron-prompt.txt").read_text()
    if previous_owner:
        prompt += (
            f"\nRecovery required: state {path} is still owned by {previous_owner}. No collection or "
            "takeover was performed. Verify that worker has stopped using native session and cron run "
            "history before claiming its queue. Age alone is not proof. If it is still active or its "
            "status is uncertain, do not take over or write external data. Once verified stopped, use "
            f"queue claim --owner {owner} --previous-owner {previous_owner}, then collect with "
            f"triage --incremental --compact --owner {owner} --state-file {path}. "
        )
    else:
        prompt += (
            "\nCollection has already completed and the full evidence is persisted. "
            "Do not collect a second time unless you identify stale evidence. "
        )
    prompt += (
        "This is the authorized scheduled triage worker. "
        f"Use owner {owner}, state file {path}, with queue status --compact, then use queue show/context "
        "for full evidence. Pass this --state-file to every queue command. Finish and release this owner "
        "under the processing protocol. Read recent Triage chat history from telegram:-1003914987491 "
        "when reconciling feedback or delivery. Return only the final report or NO_REPLY; "
        "the existing work-triage scheduler delivers it. Do not send a separate report."
    )
    remaining = max(1, args.timeout - int(time.monotonic() - started))
    command = [
        "openclaw", "agent", "--agent", "main", "--session-key", f"agent:main:triage:{owner}",
        "--model", args.model, "--thinking", args.thinking, "--timeout", str(remaining),
        "--message", prompt, "--json",
    ]
    try:
        response = subprocess.run(command, text=True, capture_output=True,
                                  timeout=remaining + 30, check=True)
        envelope = json.loads(response.stdout)
        text = final_text(envelope)
        with pending.locked(path) as state:
            if state.get("pending") or state.get("owner"):
                raise RuntimeError("Codex returned before finishing and releasing its triage batch")
        receipt.update(status="completed", meta=(envelope.get("result", envelope).get("meta") or {}))
        return text
    except (subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        receipt.update(status="error", error=type(exc).__name__)
        raise RuntimeError(f"Triage worker {owner} failed; inspect its native session and retained queue before retrying") from exc
    finally:
        receipt["duration_seconds"] = round(time.monotonic() - started, 2)
        write_receipt(path, receipt)


def write_receipt(path, receipt):
    directory = path.parent / "logs" / "runs"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / (receipt["owner"] + ".json")).write_text(json.dumps(receipt, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file")
    parser.add_argument("--model", default="openai/gpt-5.6-sol")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    try:
        print(run(args))
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
