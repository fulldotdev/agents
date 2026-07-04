#!/usr/bin/env python3
import argparse, json, os, re, subprocess
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

MAX_ITEMS_PER_LANE = int(os.environ.get("TRIAGE_MAX_ITEMS_PER_LANE", "200"))
STATE_DIR = Path(os.environ.get("TRIAGE_STATE_DIR", Path.cwd() / "state" / "triage")).expanduser()
ATTACHMENTS_DIR = STATE_DIR / "attachments"
RUN_LOG_DIR = STATE_DIR / "runs"

DEFAULT_GMAIL_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]
DEFAULT_CALENDAR_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]

NOTION_CUSTOMERS_DATA_SOURCE_ID = os.environ.get("NOTION_CUSTOMERS_DATA_SOURCE_ID", "2635979e-268c-8191-b322-000bd3109d1c")
NOTION_PROJECTS_DATA_SOURCE_ID = os.environ.get("NOTION_PROJECTS_DATA_SOURCE_ID", "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae")
NOTION_TASKS_DATA_SOURCE_ID = os.environ.get("NOTION_TASKS_DATA_SOURCE_ID", "1cb5979e-268c-80e9-bd7d-000b00ac4424")
NOTION_MEETINGS_DATA_SOURCE_ID = os.environ.get("NOTION_MEETINGS_DATA_SOURCE_ID", "1cb5979e-268c-808d-888d-000bfa3a527c")
NOTION_SPRINTS_DATA_SOURCE_ID = os.environ.get("NOTION_SPRINTS_DATA_SOURCE_ID", "3555979e-268c-807b-bdb4-000b86b48f90")
NOTION_VERSION = os.environ.get("NOTION_API_VERSION") or os.environ.get("NOTION_VERSION", "2026-03-11")

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout

def json_cmd(cmd):
    return json.loads(run(cmd))

def iso_utc(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def parse_iso(value):
    if not value:
        return None
    value = value.strip()
    if len(value) == 10 and "T" not in value:
        return datetime.combine(datetime.fromisoformat(value).date(), time.min, tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def window_from_args(after=None, before=None, require=False):
    after_dt = parse_iso(after)
    before_dt = parse_iso(before) or datetime.now(timezone.utc)
    if require and not after_dt:
        raise ValueError("after is required")
    if after_dt and before_dt < after_dt:
        raise ValueError("before must be on or after after")
    return after_dt, before_dt

def compact_text(value, limit=12000):
    text = (value or "").replace("\r", "")
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"

def error_obj(source, exc):
    text = str(exc)
    typ = "auth_required" if "invalid_grant" in text or "expired or revoked" in text else "keyring_blocked" if "keyring" in text.lower() or "keychain" in text.lower() or "KeyUnwrap" in text else "fetch_failed"
    return {"source": source, "ok": False, "error_type": typ, "error": text, "items": []}

def notion_query(data_source_id, payload):
    cmd = ["ntn", "datasources", "query", data_source_id, "--json", "--notion-version", NOTION_VERSION]
    if payload.get("page_size"):
        cmd += ["--limit", str(payload["page_size"])]
    for sort in payload.get("sorts") or []:
        prop, direction = sort.get("property"), sort.get("direction", "ascending")
        if prop:
            cmd += ["--sort", f"{prop} {'desc' if direction == 'descending' else 'asc'}"]
    if payload.get("filter"):
        cmd += ["--filter", json.dumps(payload["filter"])]
    return json_cmd(cmd)

def notion_blocks(page_id, page_size=100):
    return json_cmd([
        "ntn", "api", f"v1/blocks/{page_id}/children",
        f"page_size=={page_size}",
        "--notion-version", NOTION_VERSION,
    ]).get("results", [])

def base_result(lane, mode, after_dt=None, before_dt=None):
    return {"generated_at": iso_utc(datetime.now(timezone.utc)), "lane": lane, "mode": mode, "after": iso_utc(after_dt) if after_dt else None, "before": iso_utc(before_dt) if before_dt else None, "ok": True, "errors": [], "items": []}

def yaml_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    needs_quotes = (
        text == ""
        or text.strip() != text
        or "\n" in text
        or re.search(r'[:#\[\]{},&*?!|>\'"%@`]', text)
        or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}
    )
    return json.dumps(text, ensure_ascii=False) if needs_quotes else text

def yaml_lines(value, indent=0):
    space = "  " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = yaml_scalar(key)
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{space}{key_text}:")
                lines.extend(yaml_lines(item, indent + 1))
            elif isinstance(item, list):
                lines.append(f"{space}{key_text}: []")
            elif isinstance(item, dict):
                lines.append(f"{space}{key_text}: {{}}")
            else:
                lines.append(f"{space}{key_text}: {yaml_scalar(item)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{space}- {{}}")
                    continue
                first = True
                for key, child in item.items():
                    prefix = "- " if first else "  "
                    key_text = yaml_scalar(key)
                    if isinstance(child, (dict, list)) and child:
                        lines.append(f"{space}{prefix}{key_text}:")
                        lines.extend(yaml_lines(child, indent + 2))
                    elif isinstance(child, list):
                        lines.append(f"{space}{prefix}{key_text}: []")
                    elif isinstance(child, dict):
                        lines.append(f"{space}{prefix}{key_text}: {{}}")
                    else:
                        lines.append(f"{space}{prefix}{key_text}: {yaml_scalar(child)}")
                    first = False
            elif isinstance(item, list):
                lines.append(f"{space}-")
                lines.extend(yaml_lines(item, indent + 1))
            else:
                lines.append(f"{space}- {yaml_scalar(item)}")
    return lines

def emit(result, pretty=False, output_format="json"):
    if output_format == "yaml":
        print("\n".join(yaml_lines(result)))
        return
    print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))

def add_common_args(parser):
    parser.add_argument("--after")
    parser.add_argument("--before")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
