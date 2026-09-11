#!/usr/bin/env python3
"""Notion work-context queries for triage."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from zoneinfo import ZoneInfo

from common import (
    MAX_ITEMS_PER_LANE, NOTION_COMPANIES_DATA_SOURCE_ID,
    NOTION_PROJECTS_DATA_SOURCE_ID, NOTION_SPRINTS_DATA_SOURCE_ID,
    NOTION_TASKS_DATA_SOURCE_ID, base_result, company_item, error_obj,
    in_window_value, limited_rows, notion_query, parse_iso, project_item,
    task_item,
)

COMPANY_STATUSES = ["Prospect", "Active"]
TRIAGE_PROJECT_STATUSES = ["Discovery", "Planned", "In Progress", "Paused"]
OPEN_TASK_STATUSES = ["Todo", "Doing", "Waiting"]
TRIAGE_TASK_STATUSES = OPEN_TASK_STATUSES


def status_filter(statuses):
    return {"or": [{"property": "Status", "status": {"equals": status}} for status in statuses]}


def query_items(data_source_id, item_fn, statuses, limit, sorts=None, query_filter=None):
    payload = {
        "sorts": sorts or [{"property": "Edited", "direction": "descending"}],
        "page_size": min(limit, 100),
    }
    if query_filter or statuses:
        payload["filter"] = query_filter or status_filter(statuses)
    items, cursors = {}, set()
    while True:
        data = notion_query(data_source_id, payload)
        if len(data.get("results") or []) > payload["page_size"]:
            raise RuntimeError("Notion returned more rows than requested; pagination boundary is ambiguous")
        for row in limited_rows(data, payload["page_size"]):
            items[row["id"]] = item_fn(row)
        cursor = data.get("next_cursor")
        if not data.get("has_more") and not cursor:
            return list(items.values())
        if not cursor or cursor in cursors:
            raise RuntimeError("Incomplete Notion index: missing or repeated pagination cursor")
        cursors.add(cursor)
        payload["start_cursor"] = cursor


def active_companies(limit=MAX_ITEMS_PER_LANE):
    # Include inactive companies too: active work can still link to them.
    return query_items(NOTION_COMPANIES_DATA_SOURCE_ID, company_item, None, limit)


def active_projects(limit=MAX_ITEMS_PER_LANE):
    return query_items(NOTION_PROJECTS_DATA_SOURCE_ID, project_item, TRIAGE_PROJECT_STATUSES, limit)


def current_sprint_id():
    rows = limited_rows(notion_query(NOTION_SPRINTS_DATA_SOURCE_ID, {
        "filter": {"property": "Status", "status": {"equals": "Current"}},
        "page_size": 1,
    }), 1)
    return rows[0]["id"] if rows else None


def triage_tasks(limit=MAX_ITEMS_PER_LANE):
    today = datetime.now(ZoneInfo("Europe/Amsterdam")).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    query_filter = status_filter(OPEN_TASK_STATUSES)
    query_filter["or"].extend({"and": [
        {"property": "Status", "status": {"equals": status}},
        {"property": "Edited", "last_edited_time": {"on_or_after": today}},
    ]} for status in ["Done", "Canceled"])
    return query_items(NOTION_TASKS_DATA_SOURCE_ID, task_item, None, limit, query_filter=query_filter)


def changed_items(data_source_id, item_fn, after, before, limit):
    data = notion_query(data_source_id, {
        "filter": {"property": "Edited", "last_edited_time": {"on_or_after": after, "before": before}},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    items = [item_fn(row) for row in limited_rows(data, limit)]
    after_dt, before_dt = parse_iso(after), parse_iso(before)
    return [item for item in items if in_window_value(item.get("edited") or item.get("created"), after_dt, before_dt)]


def collect_group(lane, mode, calls, after=None, before=None):
    result = base_result(lane, mode, after, before)
    result.pop("items")
    result["lanes"] = {}
    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = {executor.submit(fn): name for name, fn in calls.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                items = future.result()
                result["lanes"][name] = {"ok": True, "items": items, "count": len(items)}
            except Exception as exc:
                error = error_obj(name, exc)
                result["lanes"][name] = error
                result["errors"].append(error)
                result["ok"] = False
    return result


def collect_work_context(after=None, before=None, limit=MAX_ITEMS_PER_LANE):
    result = collect_group("work_context", "all_companies_active_projects_tasks", {
        "companies": lambda: active_companies(limit),
        "projects": lambda: active_projects(limit),
        "tasks": lambda: triage_tasks(limit),
    }, after, before)
    result["complete"] = result["ok"]
    return result


def collect_changed_work_context(after, before, after_text, before_text, limit=MAX_ITEMS_PER_LANE):
    return collect_group("work_context", "changed_companies_projects_tasks", {
        "companies": lambda: changed_items(NOTION_COMPANIES_DATA_SOURCE_ID, company_item, after_text, before_text, limit),
        "projects": lambda: changed_items(NOTION_PROJECTS_DATA_SOURCE_ID, project_item, after_text, before_text, limit),
        "tasks": lambda: changed_items(NOTION_TASKS_DATA_SOURCE_ID, task_item, after_text, before_text, limit),
    }, after, before)
