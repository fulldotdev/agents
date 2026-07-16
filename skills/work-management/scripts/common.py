#!/usr/bin/env python3
"""Shared collector configuration, command, time, Notion, and output helpers."""

import argparse
import json
import os
import re
import shutil
import subprocess
import time as time_module
from datetime import datetime, time, timezone
from pathlib import Path

MAX_ITEMS_PER_LANE = int(os.environ.get("TRIAGE_MAX_ITEMS_PER_LANE", "200"))
MAX_ITEMS = int(os.environ.get("SPRINT_PLANNING_MAX_ITEMS", "250"))
TEMP_ROOT = Path(
    os.environ.get(
        "WORK_MANAGEMENT_TEMP_DIR",
        os.environ.get("AGENCY_WORK_TEMP_DIR", Path.home() / ".hermes" / "tmp" / "work-management"),
    )
).expanduser()


def create_run_dir():
    """Create bounded per-run scratch space and remove leftovers older than 24h."""
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    cutoff = time_module.time() - 86400
    for child in TEMP_ROOT.iterdir():
        try:
            if child.stat().st_mtime < cutoff:
                shutil.rmtree(child) if child.is_dir() else child.unlink()
        except FileNotFoundError:
            pass
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = TEMP_ROOT / f"{stamp}-{os.getpid()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


RUN_DIR = create_run_dir()
ATTACHMENTS_DIR = RUN_DIR / "attachments"

DEFAULT_GMAIL_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]
DEFAULT_CALENDAR_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]

NOTION_CUSTOMERS_DATA_SOURCE_ID = os.environ.get("NOTION_CUSTOMERS_DATA_SOURCE_ID", "2635979e-268c-8191-b322-000bd3109d1c")
NOTION_PROJECTS_DATA_SOURCE_ID = os.environ.get("NOTION_PROJECTS_DATA_SOURCE_ID", "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae")
NOTION_TASKS_DATA_SOURCE_ID = os.environ.get("NOTION_TASKS_DATA_SOURCE_ID", "1cb5979e-268c-80e9-bd7d-000b00ac4424")
NOTION_MEETINGS_DATA_SOURCE_ID = os.environ.get("NOTION_MEETINGS_DATA_SOURCE_ID", "1cb5979e-268c-808d-888d-000bfa3a527c")
NOTION_SPRINTS_DATA_SOURCE_ID = os.environ.get("NOTION_SPRINTS_DATA_SOURCE_ID", "3555979e-268c-807b-bdb4-000b86b48f90")
NOTION_VERSION = os.environ.get("NOTION_API_VERSION") or os.environ.get("NOTION_VERSION", "2026-03-11")


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
    if payload.get("filter"):
        cmd += ["--filter", json.dumps(payload["filter"])]
    return json_cmd(cmd)


def notion_blocks(page_id, page_size=100):
    return json_cmd([
        "ntn", "api", f"v1/blocks/{page_id}/children", f"page_size=={page_size}",
        "--notion-version", NOTION_VERSION,
    ]).get("results", [])


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


def rollup_relation_ids(row, name):
    ids = []
    for value in (prop(row, name).get("rollup") or {}).get("array") or []:
        ids.extend(item.get("id") for item in value.get("relation", []) if item.get("id"))
    return ids


def rollup_urls(row, name):
    urls = []
    for value in (prop(row, name).get("rollup") or {}).get("array") or []:
        url = value.get("url")
        if not url and value.get("type") == "formula":
            url = (value.get("formula") or {}).get("string")
        if url and url not in urls:
            urls.append(url)
    return urls


def date_start(row, name):
    return (prop(row, name).get("date") or {}).get("start")


def date_end(row, name):
    return (prop(row, name).get("date") or {}).get("end")


def url_value(row, name):
    return prop(row, name).get("url")


def prop_time(row, name):
    value = prop(row, name)
    return value.get("last_edited_time") or value.get("created_time")


def row_item(row):
    return {"id": row.get("id"), "url": row.get("url"), "properties": row.get("properties", {})}


def customer_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "domain": url_value(row, "Domain"),
        "github_repo_url": url_value(row, "GitHub Repo URL"),
        "contacts": multi_select_names(row, "Contacts"),
        "edited": prop_time(row, "Edited"), "created": prop_time(row, "Created"),
    }


def project_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "summary": plain_text(prop(row, "Summary")),
        "customers": relation_ids(row, "Customers"), "contacts": relation_ids(row, "Contacts"),
        "github_repo_urls": rollup_urls(row, "Github Repo URL"),
        "tasks": relation_ids(row, "Tasks"), "meetings": relation_ids(row, "Meetings"),
        "start": date_start(row, "Start"), "end": date_start(row, "End"),
        "edited": prop_time(row, "Edited"), "created": prop_time(row, "Created"),
    }


def task_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "type": select_value(row, "Type"),
        "summary": plain_text(prop(row, "Summary")), "customer": relation_ids(row, "Customer"),
        "project": relation_ids(row, "Project"), "project_contacts": rollup_relation_ids(row, "Project Contacts"),
        "sprint": relation_ids(row, "Sprint"), "meetings": relation_ids(row, "Meetings"),
        "due": date_start(row, "Due"), "edited": prop_time(row, "Edited"),
        "created": prop_time(row, "Created"),
    }


def sprint_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status_value(row), "start": date_start(row, "Dates"),
        "end": date_end(row, "Dates"), "tasks": relation_ids(row, "Tasks"),
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
