#!/usr/bin/env python3
"""Create and resume T3-managed threads through a local T3 server.

The script mints a short-lived bearer token with the local T3 CLI and never
prints that token. It intentionally sends thread.create and thread.turn.start
as separate HTTP commands because HTTP bootstrap creation is not reliable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def mint_token(base_dir: str, label: str) -> str:
    command = [
        "t3",
        "auth",
        "session",
        "issue",
        "--base-dir",
        str(Path(base_dir).expanduser()),
        "--ttl",
        "15m",
        "--label",
        label,
        "--token-only",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("T3 did not return a bearer token")
    return token


def request(server: str, token: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        server.rstrip("/") + path,
        data=body,
        headers=headers,
        method="GET" if body is None else "POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"T3 HTTP {error.code}: {response_body}") from error


def model_selection(instance_id: str, model: str, reasoning_effort: str) -> dict[str, Any]:
    return {
        "instanceId": instance_id,
        "model": model,
        "options": [{"id": "reasoningEffort", "value": reasoning_effort}],
    }


def turn_command(
    thread_id: str,
    prompt: str,
    runtime_mode: str,
    instance_id: str,
    model: str,
    reasoning_effort: str,
) -> dict[str, Any]:
    return {
        "type": "thread.turn.start",
        "commandId": str(uuid.uuid4()),
        "threadId": thread_id,
        "message": {
            "messageId": str(uuid.uuid4()),
            "role": "user",
            "text": prompt,
            "attachments": [],
        },
        "modelSelection": model_selection(instance_id, model, reasoning_effort),
        "runtimeMode": runtime_mode,
        "interactionMode": "default",
        "createdAt": utc_now(),
    }


def command_list(args: argparse.Namespace, token: str) -> None:
    shell = request(args.server, token, "/api/orchestration/shell")
    projects = {project["id"]: project for project in shell.get("projects", [])}
    rows = []
    for thread in shell.get("threads", []):
        if args.project_id and thread.get("projectId") != args.project_id:
            continue
        session = thread.get("session") or {}
        latest = thread.get("latestTurn") or {}
        project = projects.get(thread.get("projectId"), {})
        rows.append(
            {
                "threadId": thread.get("id"),
                "title": thread.get("title"),
                "projectId": thread.get("projectId"),
                "project": project.get("title"),
                "workspaceRoot": project.get("workspaceRoot"),
                "branch": thread.get("branch"),
                "worktreePath": thread.get("worktreePath"),
                "provider": session.get("providerName"),
                "providerInstanceId": session.get("providerInstanceId"),
                "model": (thread.get("modelSelection") or {}).get("model"),
                "reasoningEffort": next(
                    (
                        option.get("value")
                        for option in (thread.get("modelSelection") or {}).get("options", [])
                        if option.get("id") == "reasoningEffort"
                    ),
                    None,
                ),
                "runtimeMode": thread.get("runtimeMode"),
                "sessionStatus": session.get("status"),
                "sessionUpdatedAt": session.get("updatedAt"),
                "sessionError": session.get("lastError"),
                "latestTurnState": latest.get("state"),
                "latestTurnId": latest.get("turnId"),
                "latestTurnRequestedAt": latest.get("requestedAt"),
                "latestTurnStartedAt": latest.get("startedAt"),
                "latestTurnCompletedAt": latest.get("completedAt"),
                "createdAt": thread.get("createdAt"),
                "updatedAt": thread.get("updatedAt"),
                "archivedAt": thread.get("archivedAt"),
                "settledOverride": thread.get("settledOverride"),
                "settledAt": thread.get("settledAt"),
                "latestUserMessageAt": thread.get("latestUserMessageAt"),
                "hasPendingApprovals": bool(thread.get("hasPendingApprovals")),
                "hasPendingUserInput": bool(thread.get("hasPendingUserInput")),
                "hasActionableProposedPlan": bool(thread.get("hasActionableProposedPlan")),
            }
        )
    print(json.dumps(rows, indent=2))


def command_create(args: argparse.Namespace, token: str) -> None:
    thread_id = args.thread_id or str(uuid.uuid4())
    created_at = utc_now()
    create = {
        "type": "thread.create",
        "commandId": str(uuid.uuid4()),
        "threadId": thread_id,
        "projectId": args.project_id,
        "title": args.title,
        "modelSelection": model_selection(args.instance_id, args.model, args.reasoning_effort),
        "runtimeMode": args.runtime_mode,
        "interactionMode": "default",
        "branch": args.branch,
        "worktreePath": None,
        "createdAt": created_at,
    }
    create_result = request(args.server, token, "/api/orchestration/dispatch", create)
    result: dict[str, Any] = {"threadId": thread_id, "create": create_result}
    if args.prompt:
        result["turn"] = request(
            args.server,
            token,
            "/api/orchestration/dispatch",
            turn_command(
                thread_id,
                args.prompt,
                args.runtime_mode,
                args.instance_id,
                args.model,
                args.reasoning_effort,
            ),
        )
    print(json.dumps(result, indent=2))


def command_resume(args: argparse.Namespace, token: str) -> None:
    result = request(
        args.server,
        token,
        "/api/orchestration/dispatch",
        turn_command(
            args.thread_id,
            args.prompt,
            args.runtime_mode,
            args.instance_id,
            args.model,
            args.reasoning_effort,
        ),
    )
    print(json.dumps({"threadId": args.thread_id, "turn": result}, indent=2))


def command_settled_state(args: argparse.Namespace, token: str, command_type: str) -> None:
    payload = {
        "type": command_type,
        "commandId": str(uuid.uuid4()),
        "threadId": args.thread_id,
    }
    if command_type == "thread.unsettle":
        payload["reason"] = "user"
    result = request(
        args.server,
        token,
        "/api/orchestration/dispatch",
        payload,
    )
    print(json.dumps({"threadId": args.thread_id, "command": command_type, "result": result}, indent=2))


def command_status(args: argparse.Namespace, token: str) -> None:
    result = request(
        args.server,
        token,
        f"/api/orchestration/threads/{args.thread_id}?turnLimit={args.turn_limit}",
    )
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="http://127.0.0.1:3773")
    parser.add_argument("--base-dir", default="~/.t3")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List T3-managed threads")
    list_parser.add_argument("--project-id")

    create = sub.add_parser("create", help="Create a T3 thread and optionally start its first turn")
    create.add_argument("--project-id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--prompt")
    create.add_argument("--thread-id")
    create.add_argument("--branch", default="preview")
    create.add_argument("--instance-id", default="codex")
    create.add_argument("--model", default=os.environ.get("T3_DEFAULT_MODEL", "gpt-5.6-sol"))
    create.add_argument(
        "--reasoning-effort",
        default=os.environ.get("T3_DEFAULT_REASONING_EFFORT", "high"),
        choices=["low", "medium", "high", "xhigh", "max", "ultra"],
    )
    create.add_argument(
        "--runtime-mode",
        default="full-access",
        choices=["approval-required", "auto-accept-edits", "auto", "full-access"],
    )

    resume = sub.add_parser("resume", help="Start another turn in an existing T3 thread")
    resume.add_argument("--thread-id", required=True)
    resume.add_argument("--prompt", required=True)
    resume.add_argument("--instance-id", default="codex")
    resume.add_argument("--model", default=os.environ.get("T3_DEFAULT_MODEL", "gpt-5.6-sol"))
    resume.add_argument(
        "--reasoning-effort",
        default=os.environ.get("T3_DEFAULT_REASONING_EFFORT", "high"),
        choices=["low", "medium", "high", "xhigh", "max", "ultra"],
    )
    resume.add_argument(
        "--runtime-mode",
        default="full-access",
        choices=["approval-required", "auto-accept-edits", "auto", "full-access"],
    )

    settle = sub.add_parser("settle", help="Mark an existing T3 thread as settled")
    settle.add_argument("--thread-id", required=True)

    unsettle = sub.add_parser("unsettle", help="Re-enable a settled T3 thread without starting a turn")
    unsettle.add_argument("--thread-id", required=True)

    status = sub.add_parser("status", help="Read one thread snapshot")
    status.add_argument("--thread-id", required=True)
    status.add_argument("--turn-limit", type=int, default=10)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        token = mint_token(args.base_dir, f"t3-code skill: {args.command}")
        if args.command == "list":
            command_list(args, token)
        elif args.command == "create":
            command_create(args, token)
        elif args.command == "resume":
            command_resume(args, token)
        elif args.command == "settle":
            command_settled_state(args, token, "thread.settle")
        elif args.command == "unsettle":
            command_settled_state(args, token, "thread.unsettle")
        elif args.command == "status":
            command_status(args, token)
        else:
            parser.error(f"unsupported command: {args.command}")
        return 0
    except (RuntimeError, subprocess.CalledProcessError, urllib.error.URLError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
