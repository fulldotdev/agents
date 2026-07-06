#!/usr/bin/env python3
import argparse, json, os, re, subprocess
from datetime import datetime, timezone

NOTION_TASKS_DATA_SOURCE_ID = os.environ.get("NOTION_TASKS_DATA_SOURCE_ID", "1cb5979e-268c-80e9-bd7d-000b00ac4424")
NOTION_PROJECTS_DATA_SOURCE_ID = os.environ.get("NOTION_PROJECTS_DATA_SOURCE_ID", "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae")
NOTION_CUSTOMERS_DATA_SOURCE_ID = os.environ.get("NOTION_CUSTOMERS_DATA_SOURCE_ID", "2635979e-268c-8191-b322-000bd3109d1c")
NOTION_SPRINTS_DATA_SOURCE_ID = os.environ.get("NOTION_SPRINTS_DATA_SOURCE_ID", "3555979e-268c-807b-bdb4-000b86b48f90")
MAX_ITEMS = int(os.environ.get("SPRINT_PLANNING_MAX_ITEMS", "250"))


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout


def json_cmd(cmd):
    return json.loads(run(cmd))


def notion_query(data_source_id, payload):
    cmd = ["ntn", "datasources", "query", data_source_id, "--json"]
    if payload.get("page_size"):
        cmd += ["--limit", str(payload["page_size"])]
    for sort in payload.get("sorts") or []:
        prop, direction = sort.get("property"), sort.get("direction", "ascending")
        if prop:
            cmd += ["--sort", f"{prop} {'desc' if direction == 'descending' else 'asc'}"]
    if payload.get("filter"):
        cmd += ["--filter", json.dumps(payload["filter"])]
    return json_cmd(cmd)


def iso_utc(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


def prop(row, name):
    return (row.get("properties") or {}).get(name) or {}


def plain_text(prop_obj):
    values = prop_obj.get(prop_obj.get("type") or "", []) if isinstance(prop_obj, dict) else []
    if not isinstance(values, list):
        return ""
    return "".join(part.get("plain_text", "") for part in values).strip()


def title(row, name="Name"):
    return plain_text(prop(row, name))


def status(row, name="Status"):
    return ((prop(row, name).get("status") or {}).get("name"))


def select(row, name):
    return ((prop(row, name).get("select") or {}).get("name"))


def rich_text(row, name):
    return plain_text(prop(row, name))


def date_start(row, name):
    return ((prop(row, name).get("date") or {}).get("start"))


def date_end(row, name):
    return ((prop(row, name).get("date") or {}).get("end"))


def relation_ids(row, name):
    return [x.get("id") for x in prop(row, name).get("relation", []) if x.get("id")]


def prop_time(row, name):
    p = prop(row, name)
    return p.get("created_time") or p.get("last_edited_time")


def task_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status(row), "type": select(row, "Type"), "summary": rich_text(row, "Summary"),
        "customer": relation_ids(row, "Customer"), "project": relation_ids(row, "Project"),
        "sprint": relation_ids(row, "Sprint"), "meetings": relation_ids(row, "Meetings"),
        "due": date_start(row, "Due"), "created": prop_time(row, "Created"), "edited": prop_time(row, "Edited"),
    }


def project_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status(row), "summary": rich_text(row, "Summary"),
        "customers": relation_ids(row, "Customers"), "tasks": relation_ids(row, "Tasks"),
        "meetings": relation_ids(row, "Meetings"), "start": date_start(row, "Start"),
        "end": date_start(row, "End"), "created": prop_time(row, "Created"), "edited": prop_time(row, "Edited"),
    }


def customer_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row),
        "status": status(row), "created": prop_time(row, "Created"), "edited": prop_time(row, "Edited"),
    }


def sprint_item(row):
    return {
        "id": row.get("id"), "url": row.get("url"), "name": title(row), "status": status(row),
        "start": date_start(row, "Dates"), "end": date_end(row, "Dates"),
        "tasks": relation_ids(row, "Tasks"),
    }


def base_result(lane, mode):
    return {"generated_at": iso_utc(datetime.now(timezone.utc)), "lane": lane, "mode": mode, "ok": True, "errors": [], "items": []}


def yaml_scalar(value):
    if value is None: return "null"
    if value is True: return "true"
    if value is False: return "false"
    if isinstance(value, (int, float)): return str(value)
    text = str(value)
    if text == "" or text.strip() != text or "\n" in text or re.search(r'[:#\[\]{},&*?!|>\'"%@`]', text) or text.lower() in {"null","true","false","yes","no","on","off"}:
        return json.dumps(text, ensure_ascii=False)
    return text


def yaml_lines(value, indent=0):
    space = "  " * indent; lines = []
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{space}{yaml_scalar(k)}:"); lines.extend(yaml_lines(v, indent+1))
            elif isinstance(v, list): lines.append(f"{space}{yaml_scalar(k)}: []")
            elif isinstance(v, dict): lines.append(f"{space}{yaml_scalar(k)}: {{}}")
            else: lines.append(f"{space}{yaml_scalar(k)}: {yaml_scalar(v)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if not item: lines.append(f"{space}- {{}}"); continue
                first = True
                for k, v in item.items():
                    prefix = "- " if first else "  "; first = False
                    if isinstance(v, (dict, list)) and v:
                        lines.append(f"{space}{prefix}{yaml_scalar(k)}:"); lines.extend(yaml_lines(v, indent+2))
                    elif isinstance(v, list): lines.append(f"{space}{prefix}{yaml_scalar(k)}: []")
                    elif isinstance(v, dict): lines.append(f"{space}{prefix}{yaml_scalar(k)}: {{}}")
                    else: lines.append(f"{space}{prefix}{yaml_scalar(k)}: {yaml_scalar(v)}")
            else: lines.append(f"{space}- {yaml_scalar(item)}")
    return lines


def emit(result, fmt="json", pretty=False):
    if fmt == "yaml": print("\n".join(yaml_lines(result)))
    else: print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))


def add_args(parser):
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--limit", type=int, default=MAX_ITEMS)
