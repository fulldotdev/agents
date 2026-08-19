#!/usr/bin/env python3
"""Create a native, unsent Slack draft through the undocumented drafts.create API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

API_BASE = "https://slack.com/api/"
CHANNEL_RE = re.compile(r"^[CDG][A-Z0-9]+$")
THREAD_TS_RE = re.compile(r"^\d+\.\d+$")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def api_call(method: str, token: str, params: dict[str, str]) -> dict:
    request = urllib.request.Request(
        API_BASE + method,
        data=urllib.parse.urlencode(params).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Slack HTTP error {exc.code} during {method}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Slack network error during {method}: {exc.reason}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Slack returned a non-object response during {method}")
    return payload


def rich_text_blocks(text: str) -> str:
    blocks = [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": text}],
                }
            ],
        }
    ]
    return json.dumps(blocks, separators=(",", ":"), ensure_ascii=False)


def read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        text = args.text
    elif args.text_file == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.text_file).expanduser().read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Draft text cannot be empty")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Workspace config slug")
    parser.add_argument("--channel", required=True, help="Slack channel, group, or DM ID")
    content = parser.add_mutually_exclusive_group(required=True)
    content.add_argument("--text", help="Draft text")
    content.add_argument("--text-file", help="UTF-8 file path, or - for stdin")
    parser.add_argument("--thread-ts", help="Parent message timestamp for a thread reply")
    parser.add_argument(
        "--broadcast",
        action="store_true",
        help="Mark a threaded draft to also broadcast when the user sends it",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate without creating a draft")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", args.workspace):
            raise ValueError("Invalid workspace slug")
        if not CHANNEL_RE.fullmatch(args.channel):
            raise ValueError("Channel must be a Slack C…, G…, or D… ID")
        if args.thread_ts and not THREAD_TS_RE.fullmatch(args.thread_ts):
            raise ValueError("--thread-ts must look like 1700000000.000100")
        if args.broadcast and not args.thread_ts:
            raise ValueError("--broadcast requires --thread-ts")
        text = read_text(args)

        config_path = Path.home() / ".config" / "slack" / "workspaces" / f"{args.workspace}.env"
        if not config_path.is_file():
            raise ValueError(f"Workspace config not found: {config_path}")
        env = load_env(config_path)
        token = env.get("SLACK_USER_TOKEN", "")
        if not token.startswith("xoxp-"):
            raise ValueError("SLACK_USER_TOKEN must be a Slack xoxp user token")

        destination: dict[str, object] = {"channel_id": args.channel}
        if args.thread_ts:
            destination["thread_ts"] = args.thread_ts
            destination["broadcast"] = args.broadcast

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "ok": True,
                        "dry_run": True,
                        "workspace": args.workspace,
                        "channel_id": args.channel,
                        "thread_ts": args.thread_ts,
                        "text_length": len(text),
                    }
                )
            )
            return 0

        auth = api_call("auth.test", token, {})
        if not auth.get("ok"):
            raise RuntimeError(f"Slack auth.test failed: {auth.get('error', 'unknown_error')}")

        result = api_call(
            "drafts.create",
            token,
            {
                "channel_id": args.channel,
                "client_msg_id": str(uuid.uuid4()),
                "destinations": json.dumps([destination], separators=(",", ":")),
                "blocks": rich_text_blocks(text),
                "file_ids": "[]",
                "is_from_composer": "true",
            },
        )
        if not result.get("ok"):
            raise RuntimeError(f"Slack drafts.create failed: {result.get('error', 'unknown_error')}")

        draft = result.get("draft") or {}
        team_id = draft.get("team_id") or auth.get("team_id")
        output = {
            "ok": True,
            "workspace": auth.get("team") or args.workspace,
            "team_id": team_id,
            "channel_id": args.channel,
            "thread_ts": args.thread_ts,
            "draft_id": draft.get("id"),
            "last_updated_ts": draft.get("last_updated_ts") or draft.get("date_updated"),
            "manage_url": f"https://app.slack.com/client/{team_id}/{args.channel}" if team_id else None,
        }
        print(json.dumps(output, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
