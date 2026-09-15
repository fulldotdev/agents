#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
FREEZE = ROOT / "private" / "freeze.json"
BASELINE = json.loads((ROOT / "baseline-snapshot.json").read_text())
TRIALS = (
    ("a1", "full", "gpt-5.6-sol"),
    ("a2", "full", "gpt-5.6-sol"),
    ("b1", "compact", "gpt-5.6-sol"),
    ("b2", "compact", "gpt-5.6-sol"),
    ("c1", "compact", "gpt-5.6-terra"),
    ("c2", "compact", "gpt-5.6-terra"),
    ("d1", "full", "gpt-5.6-terra"),
    ("d2", "full", "gpt-5.6-terra"),
)
TRIAL_TIMEOUT_SECONDS = 600


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def freeze_expected():
    payload = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "expected_sha256": sha256(ROOT / "private" / "expected.json"),
        "evidence_sha256": sha256(ROOT / "fixtures" / "evidence.json"),
        "compact_index_sha256": sha256(ROOT / "fixtures" / "compact-index.json"),
        "output_schema_sha256": sha256(ROOT / "model" / "output-schema.json"),
        "baseline_commit": BASELINE["commit"]
    }
    if FREEZE.exists():
        existing = json.loads(FREEZE.read_text())
        for key in ("expected_sha256", "evidence_sha256", "compact_index_sha256", "output_schema_sha256", "baseline_commit"):
            if existing[key] != payload[key]:
                raise SystemExit(f"Frozen benchmark changed: {key}")
        return existing
    write_json(FREEZE, payload)
    return payload


def git_show(commit, path):
    result = subprocess.run(
        ["git", "-C", BASELINE["repository"], "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def stage_instructions(stage, mode):
    docs = stage / "instructions"
    docs.mkdir()
    if mode == "full":
        for source in BASELINE["paths"]:
            target = docs / source.replace("/", "__")
            target.write_text(git_show(BASELINE["commit"], source))
        snapshot = {"kind": "git", "commit": BASELINE["commit"], "paths": BASELINE["paths"]}
    else:
        sources = [
            ROOT.parents[1] / "AGENTS.md",
            ROOT.parents[1] / "skills" / "development" / "SKILL.md",
            ROOT.parents[1] / "skills" / "work-triage" / "SKILL.md",
            ROOT.parents[1] / "skills" / "work-triage" / "references" / "media.md",
            ROOT.parents[1] / "skills" / "work-triage" / "references" / "processing.md",
            ROOT.parents[1] / "skills" / "work-triage" / "references" / "t3-routing.md",
            ROOT.parents[1] / "skills" / "work-management" / "SKILL.md",
            ROOT.parents[1] / "skills" / "work-management" / "references" / "timeline.md",
        ]
        for source in sources:
            if not source.exists():
                raise SystemExit(f"Missing compact instruction source: {source}")
            (docs / source.name.replace(".md", "") .replace("SKILL", source.parent.name + "-SKILL") .replace("AGENTS", "AGENTS") .lower()).with_suffix(".md").write_text(source.read_text())
        implementation_sources = [
            ROOT.parents[1] / "skills" / "work-triage" / "scripts" / name
            for name in ("collect.py", "compact.py", "pending.py", "run.py")
        ]
        snapshot = {
            "kind": "working_tree",
            "files": {str(p): sha256(p) for p in sources},
            "implementation_files": {str(p): sha256(p) for p in implementation_sources},
        }
    return snapshot


def stage_trial(mode):
    stage = Path(tempfile.mkdtemp(prefix="triage-trial-"))
    shutil.copy2(ROOT / "model" / "task.md", stage / "task.md")
    shutil.copy2(ROOT / "model" / "output-schema.json", stage / "output-schema.json")
    snapshot = stage_instructions(stage, mode)
    evidence = ROOT / "fixtures" / "evidence.json"

    if mode == "full":
        shutil.copy2(evidence, stage / "full-packet.json")
        access = "Read every file in instructions/ and the complete full-packet.json before deciding."
    else:
        shutil.copy2(ROOT / "fixtures" / "compact-index.json", stage / "compact-index.json")
        shutil.copy2(ROOT / "model" / "triage.py", stage / "triage.py")
        (stage / ".data").mkdir()
        shutil.copy2(evidence, stage / ".data" / "evidence.json")
        access = (
            "Read every file in instructions/ and start from compact-index.json. The index is an inventory, not enough evidence for final decisions. "
            "Retrieve decision-relevant full source with `python3 triage.py show --event EVENT_ID` and destination/history context with "
            "`python3 triage.py context --case CASE_ID` or `--query TEXT`. Do not read files under .data directly."
        )

    prompt = (stage / "task.md").read_text() + "\n\nInput access:\n" + access
    return stage, snapshot, prompt


def parse_usage(events):
    usage_objects = []
    for event in events:
        stack = [event]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                if "input_tokens" in value or "output_tokens" in value:
                    usage_objects.append(value)
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)
    if not usage_objects:
        return {}
    latest = usage_objects[-1]
    keys = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
    return {key: latest[key] for key in keys if key in latest}


def run_trial(trial_id, mode, model, remote=None):
    run_dir = RUNS / trial_id
    if run_dir.exists():
        old_meta = run_dir / "metadata.json"
        if old_meta.exists() and json.loads(old_meta.read_text()).get("returncode") == 0:
            raise SystemExit(f"Run already exists: {run_dir}")
        failed = ROOT / "failed-attempts"
        failed.mkdir(exist_ok=True)
        shutil.move(run_dir, failed / f"{trial_id}-{int(time.time())}")
    run_dir.mkdir(parents=True)
    stage, snapshot, prompt = stage_trial(mode)
    codex_args = [
        "codex", "exec", "-",
        "--model", model,
        "--sandbox", "read-only",
        "--ignore-user-config",
        "--skip-git-repo-check",
        "--cd", str(stage),
        "--output-schema", str(stage / "output-schema.json"),
        "--json",
        "--color", "never",
        "-c", 'model_reasoning_effort="high"',
        "-c", "project_doc_max_bytes=0",
    ]
    remote_stage = None
    if remote:
        remote_stage = subprocess.run(
            ["ssh", "-A", remote, "mktemp", "-d", "/tmp/triage-benchmark.XXXXXX"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if not remote_stage.startswith("/tmp/triage-benchmark."):
            raise SystemExit(f"Unexpected remote staging path: {remote_stage}")
        subprocess.run(["scp", "-rq", str(stage) + "/.", f"{remote}:{remote_stage}/"], check=True)
        codex_args[codex_args.index(str(stage))] = remote_stage
        codex_args[codex_args.index(str(stage / "output-schema.json"))] = remote_stage + "/output-schema.json"
        command = ["ssh", "-A", remote, *codex_args]
    else:
        command = codex_args
    metadata = {
        "trial_id": trial_id,
        "condition": mode,
        "model": model,
        "reasoning_effort": "high",
        "sandbox": "read-only",
        "command": command,
        "remote": remote,
        "instruction_snapshot": snapshot,
        "staged_input_hashes": {str(p.relative_to(stage)): sha256(p) for p in stage.rglob("*") if p.is_file()},
    }
    write_json(run_dir / "metadata.before.json", metadata)
    shutil.copytree(stage, run_dir / "staged-inputs")

    started = time.monotonic()
    try:
        try:
            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=TRIAL_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode(errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")
            result = subprocess.CompletedProcess(
                command,
                124,
                stdout=stdout,
                stderr=stderr + f"\nTrial timed out after {TRIAL_TIMEOUT_SECONDS} seconds.\n",
            )
    finally:
        if remote_stage:
            subprocess.run(["ssh", "-A", remote, "rm", "-rf", "--", remote_stage], check=False)
    elapsed = time.monotonic() - started
    (run_dir / "events.jsonl").write_text(result.stdout)
    (run_dir / "stderr.txt").write_text(result.stderr)
    events = []
    for line in result.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    final_text = ""
    for event in events:
        if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            final_text = event["item"].get("text", "")
    (run_dir / "final.json").write_text(final_text + ("\n" if final_text else ""))
    usage = parse_usage(events)
    returncode = result.returncode
    failure = None
    if returncode == 0 and (not final_text.strip() or not usage):
        returncode = 2
        failure = "Codex exited without a final response and usage record"
    metadata.update({
        "returncode": returncode,
        "process_returncode": result.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "usage": usage,
        "failure": failure,
    })
    write_json(run_dir / "metadata.json", metadata)
    shutil.rmtree(stage)
    if returncode != 0:
        raise SystemExit(f"Trial {trial_id} failed with code {returncode}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run-all", action="store_true")
    parser.add_argument("--trial", choices=[trial[0] for trial in TRIALS])
    parser.add_argument("--remote", help="run Codex on a named SSH host after staging model-visible inputs")
    args = parser.parse_args()
    freeze = freeze_expected()
    write_json(ROOT / "prepared.json", {"freeze": freeze, "trials": TRIALS})
    if args.prepare and not args.run_all and not args.trial:
        return
    selected = TRIALS if args.run_all else [trial for trial in TRIALS if trial[0] == args.trial]
    if not selected:
        raise SystemExit("Choose --prepare, --run-all, or --trial")
    for trial in selected:
        run_trial(*trial, remote=args.remote)


if __name__ == "__main__":
    main()
