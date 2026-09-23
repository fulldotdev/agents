#!/usr/bin/env python3
"""Shared work-triage collector helpers."""

import argparse
import hashlib
import tempfile
import json
import os
import re
import subprocess
from datetime import datetime, time, timezone
from pathlib import Path

MAX_ITEMS_PER_LANE = int(os.environ.get("TRIAGE_MAX_ITEMS_PER_LANE", "200"))
TEMP_ROOT = Path(
    os.environ.get("WORK_TRIAGE_TEMP_DIR")
    or os.environ.get("WORK_MANAGEMENT_TEMP_DIR")
    or Path.home() / ".cache" / "fulldev" / "work-triage"
).expanduser()


# Imports and --help must not mutate or garbage-collect runtime state. Attachment
# directories are created only by focused downloads. Keep them until reviewed;
# a pending event may outlive an arbitrary 24-hour scratch retention window.
RUN_DIR = TEMP_ROOT / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{os.getpid()}"
ATTACHMENTS_DIR = RUN_DIR / "attachments"

DEFAULT_GMAIL_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]
DEFAULT_CALENDAR_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]

NOTION_COMPANIES_DATA_SOURCE_ID = os.environ.get(
    "NOTION_COMPANIES_DATA_SOURCE_ID",
    os.environ.get("NOTION_CUSTOMERS_DATA_SOURCE_ID", "2635979e-268c-8191-b322-000bd3109d1c"),
)
NOTION_PROJECTS_DATA_SOURCE_ID = os.environ.get("NOTION_PROJECTS_DATA_SOURCE_ID", "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae")
NOTION_TASKS_DATA_SOURCE_ID = os.environ.get("NOTION_TASKS_DATA_SOURCE_ID", "1cb5979e-268c-80e9-bd7d-000b00ac4424")
NOTION_MEETINGS_DATA_SOURCE_ID = os.environ.get("NOTION_MEETINGS_DATA_SOURCE_ID", "1cb5979e-268c-808d-888d-000bfa3a527c")
NOTION_SPRINTS_DATA_SOURCE_ID = os.environ.get("NOTION_SPRINTS_DATA_SOURCE_ID", "3555979e-268c-807b-bdb4-000b86b48f90")
NOTION_VERSION = os.environ.get("NOTION_API_VERSION") or os.environ.get("NOTION_VERSION", "2026-03-11")


def save_snapshot(source, identity, content, suffix=".json"):
    """Save immutable source text so retries keep the snapshot they refer to."""
    directory = TEMP_ROOT / source
    directory.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256((identity + "\0" + content).encode()).hexdigest()
    path = directory / (digest + suffix)
    if not path.exists():
        with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False) as temp:
            temp.write(content)
        os.replace(temp.name, path)
    return str(path)


def run(cmd):
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(cmd)}\n{process.stderr.strip()}")
    return process.stdout


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
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def error_obj(source, exc):
    text = str(exc)
    if "invalid_grant" in text or "expired or revoked" in text:
        error_type = "auth_required"
    elif "keyring" in text.lower() or "keychain" in text.lower() or "KeyUnwrap" in text:
        error_type = "keyring_blocked"
    else:
        error_type = "fetch_failed"
    return {"source": source, "ok": False, "error_type": error_type, "error": text, "items": []}


def notion_query(data_source_id, payload):
    cmd = ["ntn", "datasources", "query", data_source_id, "--json", "--notion-version", NOTION_VERSION]
    if payload.get("page_size"):
        cmd += ["--limit", str(payload["page_size"])]
    for sort in payload.get("sorts") or []:
        prop_name = sort.get("property")
        if prop_name:
            direction = "desc" if sort.get("direction") == "descending" else "asc"
            cmd += ["--sort", f"{prop_name} {direction}"]
    if payload.get("start_cursor"):
        cmd += ["--start-cursor", payload["start_cursor"]]
    if payload.get("filter"):
        cmd += ["--filter", json.dumps(payload["filter"])]
    return json_cmd(cmd)


def notion_blocks(page_id, page_size=100):
    blocks, cursor, cursors = [], None, set()
    while True:
        cmd = ["ntn", "api", f"v1/blocks/{page_id}/children", f"page_size=={page_size}",
               "--notion-version", NOTION_VERSION]
        if cursor:
            cmd.append(f"start_cursor=={cursor}")
        data = json_cmd(cmd)
        if "results" not in data:
            raise RuntimeError("Incomplete Notion block response")
        blocks.extend(data["results"])
        cursor = data.get("next_cursor")
        if not data.get("has_more") and not cursor:
            return blocks
        if not cursor or cursor in cursors:
            raise RuntimeError("Incomplete Notion blocks: missing or repeated pagination cursor")
        cursors.add(cursor)


def notion_block(block_id):
    return json_cmd([
        "ntn", "api", f"v1/blocks/{block_id}",
        "--notion-version", NOTION_VERSION,
    ])


def prop(row, name):
    return (row.get("properties") or {}).get(name) or {}


def plain_text(prop_obj):
    values = prop_obj.get(prop_obj.get("type") or "", []) if isinstance(prop_obj, dict) else []
    return "" if not isinstance(values, list) else "".join(part.get("plain_text", "") for part in values).strip()


def title(row, name="Name"):
    return plain_text(prop(row, name))


def status_value(row, name="Status"):
    return (prop(row, name).get("status") or {}).get("name")


def select_value(row, name):
    return (prop(row, name).get("select") or {}).get("name")


def relation_ids(row, name):
    return [item.get("id") for item in prop(row, name).get("relation", []) if item.get("id")]


def multi_select_names(row, name):
    return [item.get("name") for item in prop(row, name).get("multi_select", []) if item.get("name")]


def resources(row):
    return prop(row, "Resources").get("files", [])



def resource_url(row, name):
    return next((item.get("external", {}).get("url") for item in resources(row)
                 if item.get("name", "").casefold() == name.casefold() and item.get("type") == "external"), None)


def prop_time(row, name):
    value = prop(row, name)
    return value.get("last_edited_time") or value.get("created_time")


def row_item(row):
    return {"id": row.get("id"), "url": row.get("url"), "properties": row.get("properties", {})}


def company_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "website": resource_url(row, "Website"),
        "resources": resources(row),
        "edited": prop_time(row, "Edited"), "created": prop_time(row, "Created"),
    }


def project_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row),
        "companies": relation_ids(row, "Companies"),
        "resources": resources(row),
        "parent_project": relation_ids(row, "Parent project"),
        "subprojects": relation_ids(row, "Subprojects"),
        "tasks": relation_ids(row, "Tasks"), "meetings": relation_ids(row, "Meetings"),
        "deadline": prop(row, "Deadline").get("date"),
        "edited": prop_time(row, "Edited"), "created": prop_time(row, "Created"),
    }


def task_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "area": select_value(row, "Area"),
        "companies": relation_ids(row, "Companies"),
        "project": relation_ids(row, "Project"),
        "sprint": relation_ids(row, "Sprint"), "meetings": relation_ids(row, "Meetings"),
        "resources": resources(row),
        "date": prop(row, "Date").get("date"),
        "edited": prop_time(row, "Edited"),
        "created": prop_time(row, "Created"),
    }


def limited_rows(data, limit=MAX_ITEMS_PER_LANE):
    if "results" not in data:
        raise RuntimeError(data.get("message") or str(data))
    return [row_item(row) for row in data.get("results", [])[:limit]]


def in_window_value(value, after_dt, before_dt):
    dt = parse_iso(value)
    return bool(dt and after_dt <= dt < before_dt)


def base_result(lane, mode, after_dt=None, before_dt=None):
    return {
        "generated_at": iso_utc(datetime.now(timezone.utc)), "lane": lane, "mode": mode,
        "after": iso_utc(after_dt) if after_dt else None,
        "before": iso_utc(before_dt) if before_dt else None,
        "temporary_files_dir": str(RUN_DIR),
        "ok": True, "errors": [], "items": [],
    }


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
    needs_quotes = text == "" or text.strip() != text or "\n" in text or re.search(
        r'[:#\[\]{},&*?!|>\'"%@`]', text
    ) or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}
    return json.dumps(text, ensure_ascii=False) if needs_quotes else text


def yaml_lines(value, indent=0):
    space = "  " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{space}{yaml_scalar(key)}:")
                lines.extend(yaml_lines(item, indent + 1))
            elif isinstance(item, list):
                lines.append(f"{space}{yaml_scalar(key)}: []")
            elif isinstance(item, dict):
                lines.append(f"{space}{yaml_scalar(key)}: {{}}")
            else:
                lines.append(f"{space}{yaml_scalar(key)}: {yaml_scalar(item)}")
    elif isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                lines.append(f"{space}- {yaml_scalar(item)}")
                continue
            if not item:
                lines.append(f"{space}- {{}}")
                continue
            for index, (key, child) in enumerate(item.items()):
                prefix = "- " if index == 0 else "  "
                if isinstance(child, (dict, list)) and child:
                    lines.append(f"{space}{prefix}{yaml_scalar(key)}:")
                    lines.extend(yaml_lines(child, indent + 2))
                elif isinstance(child, list):
                    lines.append(f"{space}{prefix}{yaml_scalar(key)}: []")
                elif isinstance(child, dict):
                    lines.append(f"{space}{prefix}{yaml_scalar(key)}: {{}}")
                else:
                    lines.append(f"{space}{prefix}{yaml_scalar(key)}: {yaml_scalar(child)}")
    return lines


def emit(result, pretty=False, output_format="json"):
    print("\n".join(yaml_lines(result)) if output_format == "yaml" else json.dumps(
        result, indent=2 if pretty else None, ensure_ascii=False
    ))


def add_common_args(parser):
    parser.add_argument("--after")
    parser.add_argument("--before")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
