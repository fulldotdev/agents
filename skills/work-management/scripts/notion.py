#!/usr/bin/env python3
"""Notion work-context queries for triage and weekly planning."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from common import (
    MAX_ITEMS, MAX_ITEMS_PER_LANE, NOTION_CUSTOMERS_DATA_SOURCE_ID,
    NOTION_PROJECTS_DATA_SOURCE_ID, NOTION_SPRINTS_DATA_SOURCE_ID,
    NOTION_SOMEDAY_DATA_SOURCE_ID, NOTION_TASKS_DATA_SOURCE_ID, base_result,
    customer_item, error_obj, limited_rows, notion_query, project_item,
    someday_item, sprint_item, task_item,
)

CUSTOMER_STATUSES = ["Prospect", "Active"]
TRIAGE_PROJECT_STATUSES = ["Discovery", "Planned", "In Progress"]
PLANNING_PROJECT_STATUSES = TRIAGE_PROJECT_STATUSES + ["Paused"]
OPEN_TASK_STATUSES = ["Todo", "Doing", "Waiting"]
TRIAGE_TASK_STATUSES = OPEN_TASK_STATUSES


def status_filter(statuses):
    return {"or": [{"property": "Status", "status": {"equals": status}} for status in statuses]}


def query_items(data_source_id, item_fn, statuses, limit, sorts=None):
    data = notion_query(data_source_id, {
        "filter": status_filter(statuses),
        "sorts": sorts or [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [item_fn(row) for row in limited_rows(data, limit)]


def active_customers(limit=MAX_ITEMS_PER_LANE):
    return query_items(NOTION_CUSTOMERS_DATA_SOURCE_ID, customer_item, CUSTOMER_STATUSES, limit)


def active_projects(limit=MAX_ITEMS_PER_LANE, include_paused=False):
    statuses = PLANNING_PROJECT_STATUSES if include_paused else TRIAGE_PROJECT_STATUSES
    return query_items(NOTION_PROJECTS_DATA_SOURCE_ID, project_item, statuses, limit)


def current_sprint_id():
    rows = limited_rows(notion_query(NOTION_SPRINTS_DATA_SOURCE_ID, {
        "filter": {"property": "Status", "status": {"equals": "Current"}},
        "page_size": 1,
    }), 1)
    return rows[0]["id"] if rows else None


def triage_tasks(limit=MAX_ITEMS_PER_LANE):
    filters = [{"property": "Status", "status": {"equals": status}} for status in TRIAGE_TASK_STATUSES]
    sprint_id = current_sprint_id()
    if sprint_id:
        filters.append({"property": "Sprint", "relation": {"contains": sprint_id}})
    data = notion_query(NOTION_TASKS_DATA_SOURCE_ID, {
        "filter": {"or": filters},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [task_item(row) for row in limited_rows(data, limit)]


def open_tasks(limit=MAX_ITEMS):
    return query_items(
        NOTION_TASKS_DATA_SOURCE_ID, task_item, OPEN_TASK_STATUSES, limit,
        [{"property": "Due", "direction": "ascending"}, {"property": "Edited", "direction": "descending"}],
    )


def review_tasks(after, before, limit=MAX_ITEMS):
    data = notion_query(NOTION_TASKS_DATA_SOURCE_ID, {
        "filter": {"property": "Edited", "last_edited_time": {"on_or_after": after, "before": before}},
        "sorts": [{"property": "Edited", "direction": "descending"}],
        "page_size": limit,
    })
    return [task_item(row) for row in limited_rows(data, limit)]


def recent_sprints(limit=MAX_ITEMS):
    data = notion_query(NOTION_SPRINTS_DATA_SOURCE_ID, {
        "sorts": [{"property": "Dates", "direction": "descending"}], "page_size": limit,
    })
    return [sprint_item(row) for row in limited_rows(data, limit)]


def someday(limit=MAX_ITEMS):
    data = notion_query(NOTION_SOMEDAY_DATA_SOURCE_ID, {"page_size": limit})
    return [someday_item(row) for row in limited_rows(data, limit)]


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
    return collect_group("work_context", "customers_projects_active_tasks_active_or_current_sprint", {
        "customers": lambda: active_customers(limit),
        "projects": lambda: active_projects(limit),
        "tasks": lambda: triage_tasks(limit),
    }, after, before)


def collect_planning(after, before, after_text, before_text, limit=MAX_ITEMS):
    return collect_group("planning", "sprint_review_database_health_and_planning", {
        "sprints": lambda: recent_sprints(limit),
        "open_tasks": lambda: open_tasks(limit),
        "review_tasks": lambda: review_tasks(after_text, before_text, limit),
        "active_customers": lambda: active_customers(limit),
        "active_projects": lambda: active_projects(limit, include_paused=True),
        "someday": lambda: someday(limit),
    }, after, before)
