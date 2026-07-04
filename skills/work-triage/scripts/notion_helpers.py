#!/usr/bin/env python3
from triage_common import MAX_ITEMS_PER_LANE

def row_item(row):
    return {"id": row.get("id"), "url": row.get("url"), "properties": row.get("properties", {})}

def plain_text(prop):
    values = prop.get(prop.get("type") or "", []) if isinstance(prop, dict) else []
    if not isinstance(values, list):
        return ""
    return "".join(part.get("plain_text", "") for part in values).strip()

def title(row, name="Name"):
    return plain_text(((row.get("properties") or {}).get(name) or {}))

def status_value(row, name="Status"):
    status = (((row.get("properties") or {}).get(name) or {}).get("status") or {})
    return status.get("name")

def select_value(row, name):
    select = (((row.get("properties") or {}).get(name) or {}).get("select") or {})
    return select.get("name")

def relation_ids(row, name):
    prop = ((row.get("properties") or {}).get(name) or {})
    return [item.get("id") for item in prop.get("relation", []) if item.get("id")]

def multi_select_names(row, name):
    prop = ((row.get("properties") or {}).get(name) or {})
    return [item.get("name") for item in prop.get("multi_select", []) if item.get("name")]

def rollup_relation_ids(row, name):
    prop = ((row.get("properties") or {}).get(name) or {})
    ids = []
    for value in ((prop.get("rollup") or {}).get("array") or []):
        ids.extend(item.get("id") for item in value.get("relation", []) if item.get("id"))
    return ids

def date_value(row, name):
    date = (((row.get("properties") or {}).get(name) or {}).get("date") or {})
    return date.get("start")

def url_value(row, name):
    return (((row.get("properties") or {}).get(name) or {}).get("url"))

def edited_value(row):
    return prop_time(row, "Edited")

def created_value(row):
    return prop_time(row, "Created")

def customer_item(row):
    return {
        "id": row.get("id"),
        "url": row.get("url"),
        "name": title(row),
        "status": status_value(row),
        "domain": url_value(row, "Domain"),
        "contacts": multi_select_names(row, "Contacts"),
        "edited": edited_value(row),
        "created": created_value(row),
    }

def project_item(row):
    return {
        "id": row.get("id"),
        "url": row.get("url"),
        "name": title(row),
        "status": status_value(row),
        "summary": plain_text(((row.get("properties") or {}).get("Summary") or {})),
        "customers": relation_ids(row, "Customers"),
        "contacts": relation_ids(row, "Contacts"),
        "tasks": relation_ids(row, "Tasks"),
        "start": date_value(row, "Start"),
        "end": date_value(row, "End"),
        "edited": edited_value(row),
        "created": created_value(row),
    }

def task_item(row):
    return {
        "id": row.get("id"),
        "url": row.get("url"),
        "name": title(row),
        "status": status_value(row),
        "type": select_value(row, "Type"),
        "summary": plain_text(((row.get("properties") or {}).get("Summary") or {})),
        "customer": relation_ids(row, "Customer"),
        "project": relation_ids(row, "Project"),
        "project_contacts": rollup_relation_ids(row, "Project Contacts"),
        "sprint": relation_ids(row, "Sprint"),
        "due": date_value(row, "Due"),
        "edited": edited_value(row),
        "created": created_value(row),
    }

def limited_rows(data):
    if "results" not in data:
        raise RuntimeError(data.get("message") or str(data))
    return [row_item(row) for row in data.get("results", [])[:MAX_ITEMS_PER_LANE]]

def prop_time(row, name):
    prop = (row.get("properties") or {}).get(name) or {}
    return prop.get("last_edited_time") or prop.get("created_time")

def in_window_value(value, after_dt, before_dt):
    from triage_common import parse_iso
    dt = parse_iso(value)
    return bool(dt and after_dt <= dt < before_dt)

def filter_created_or_edited(rows, after_dt, before_dt):
    return [
        row for row in rows
        if in_window_value(prop_time(row, "Created"), after_dt, before_dt)
        or in_window_value(prop_time(row, "Edited"), after_dt, before_dt)
    ][:MAX_ITEMS_PER_LANE]

def status_name(row):
    status = ((row.get("properties") or {}).get("Status") or {}).get("status") or {}
    return status.get("name")

def filter_status_or_edited(rows, active_statuses, after_dt, before_dt):
    active = set(active_statuses)
    return [
        row for row in rows
        if status_name(row) in active
        or in_window_value(prop_time(row, "Edited"), after_dt, before_dt)
    ][:MAX_ITEMS_PER_LANE]
