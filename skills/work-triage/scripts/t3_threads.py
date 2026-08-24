#!/usr/bin/env python3
"""Compact T3 Code thread index for routing work during work-triage.

The default lane reads only shell metadata. Conversation turns are returned
only when a caller explicitly selects one thread with ``--thread-id``.
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

from common import add_common_args, base_result, compact_text, emit, parse_iso, window_from_args

T3_HELPER = Path(
    os.environ.get(
        "T3_DISPATCH_HELPER",
        Path.home() / ".agents" / "skills" / "t3-code" / "scripts" / "t3_dispatch.py",
    )
).expanduser()
DEFAULT_LIMIT = int(os.environ.get("TRIAGE_T3_LIMIT", "100"))
DEFAULT_TURN_LIMIT = int(os.environ.get("TRIAGE_T3_TURN_LIMIT", "8"))


def helper(*args):
    if not T3_HELPER.exists():
        raise FileNotFoundError(f"T3 dispatch helper not found: {T3_HELPER}")
    process = subprocess.run(
        ["python3", str(T3_HELPER), *args], capture_output=True, text=True, timeout=45
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or f"T3 helper failed ({process.returncode})")
    return json.loads(process.stdout)


def activity_at(item):
    candidates = (
        item.get("updatedAt"),
        item.get("sessionUpdatedAt"),
        item.get("latestTurnCompletedAt"),
        item.get("latestTurnStartedAt"),
        item.get("latestTurnRequestedAt"),
        item.get("createdAt"),
    )
    parsed = [parse_iso(value) for value in candidates if value]
    return max(parsed) if parsed else None


def compact_item(item):
    thread_id = item.get("threadId")
    return {
        "thread_id": thread_id,
        "title": item.get("title"),
        "project": {
            "id": item.get("projectId"),
            "name": item.get("project"),
            "workspace_root": item.get("workspaceRoot"),
        },
        "checkout": {
            "branch": item.get("branch"),
            "worktree_path": item.get("worktreePath"),
        },
        "runtime": {
            "provider": item.get("provider"),
            "provider_instance_id": item.get("providerInstanceId"),
            "model": item.get("model"),
            "mode": item.get("runtimeMode"),
        },
        "state": {
            "session": item.get("sessionStatus"),
            "latest_turn": item.get("latestTurnState"),
            "latest_turn_id": item.get("latestTurnId"),
            "settled": item.get("settledOverride") == "settled" or bool(item.get("settledAt")),
            "archived": bool(item.get("archivedAt")),
            "pending_approval": bool(item.get("hasPendingApprovals")),
            "pending_user_input": bool(item.get("hasPendingUserInput")),
            "actionable_plan": bool(item.get("hasActionableProposedPlan")),
            "last_error": compact_text(item.get("sessionError"), 800),
        },
        "created_at": item.get("createdAt"),
        "updated_at": item.get("updatedAt"),
        "last_activity_at": activity_at(item).isoformat().replace("+00:00", "Z") if activity_at(item) else None,
        "reference": {
            "locator": f"T3 Code · host otis · thread {thread_id}",
            "deep_read_hint": f"collect.py source t3_threads --thread-id {thread_id} --format yaml",
        },
    }


def collect(after_dt=None, before_dt=None, include_archived=False, limit=DEFAULT_LIMIT, project=None, query=None, thread_id=None, turn_limit=DEFAULT_TURN_LIMIT):
    if thread_id:
        return {
            "ok": True,
            "mode": "targeted_thread",
            "thread_id": thread_id,
            "snapshot": helper("status", "--thread-id", thread_id, "--turn-limit", str(turn_limit)),
        }

    rows = helper("list")
    items = []
    for row in rows:
        item = compact_item(row)
        activity = parse_iso(item.get("last_activity_at"))
        if after_dt and (not activity or activity < after_dt):
            continue
        if before_dt and activity and activity >= before_dt:
            continue
        if not include_archived and item["state"]["archived"]:
            continue
        haystack = " ".join(
            str(value or "")
            for value in (
                item.get("title"), item["project"].get("name"), item["project"].get("workspace_root"),
                item["checkout"].get("branch"), item.get("thread_id"),
            )
        ).lower()
        if project and project.lower() not in haystack:
            continue
        if query and query.lower() not in haystack:
            continue
        items.append(item)
    items.sort(key=lambda item: item.get("last_activity_at") or "", reverse=True)
    return {"ok": True, "mode": "thread_index", "count": len(items[:limit]), "items": items[:limit]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--include-archived", action="store_true")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--project")
    parser.add_argument("--query")
    parser.add_argument("--thread-id")
    parser.add_argument("--turn-limit", type=int, default=DEFAULT_TURN_LIMIT)
    args = parser.parse_args()
    after, before = (None, None) if args.all or args.thread_id else window_from_args(args.after, args.before)
    result = base_result("t3_threads", "targeted_thread" if args.thread_id else "thread_index", after, before)
    result.pop("items")
    try:
        result["result"] = collect(after, before, args.include_archived, args.limit, args.project, args.query, args.thread_id, args.turn_limit)
    except Exception as exc:
        result["ok"] = False
        result["errors"].append({"source": "t3_threads", "ok": False, "error": str(exc), "items": []})
    emit(result, args.pretty, args.format)


if __name__ == "__main__":
    main()
