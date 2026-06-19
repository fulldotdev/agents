#!/usr/bin/env python3
import argparse, json
from productive_common import add_common_args, base_result, emit, error_obj, iso_utc, json_cmd, window_from_args

TASKS_DS = "1cb5979e-268c-80e9-bd7d-000b00ac4424"
PROJECTS_DS = "4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae"
CUSTOMERS_DS = "2635979e-268c-8191-b322-000bd3109d1c"

def title_of(row):
    props = row.get("properties") or {}
    for prop in props.values():
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title") or [])
    return None

def prop_text(prop):
    if not prop:
        return None
    if prop.get("type") == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title") or [])
    if prop.get("type") == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text") or [])
    if prop.get("type") == "status":
        return (prop.get("status") or {}).get("name")
    if prop.get("type") == "select":
        return (prop.get("select") or {}).get("name")
    if prop.get("type") == "url":
        return prop.get("url")
    return None

def page_summary(row):
    props = row.get("properties") or {}
    return {
        "id": row.get("id"),
        "object": row.get("object"),
        "title": title_of(row),
        "url": row.get("url"),
        "created_time": row.get("created_time"),
        "last_edited_time": row.get("last_edited_time"),
        "status": prop_text(props.get("Status")),
        "type": prop_text(props.get("Type")),
        "summary": prop_text(props.get("Summary")),
        "customer_ids": [x.get("id") for x in (props.get("Customer") or props.get("Customers") or {}).get("relation") or []],
        "project_ids": [x.get("id") for x in (props.get("Project") or props.get("Projects") or {}).get("relation") or []],
        "task_ids": [x.get("id") for x in (props.get("Tasks") or {}).get("relation") or []],
        "meeting_ids": [x.get("id") for x in (props.get("Meetings") or {}).get("relation") or []],
        "repo_url": prop_text(props.get("GitHub Repo URL")),
        "start": ((props.get("Start") or {}).get("date") or {}).get("start"),
        "end": ((props.get("End") or {}).get("date") or {}).get("start"),
        "due": ((props.get("Due") or {}).get("date") or {}).get("start"),
    }

def search(query, page_size):
    data = json_cmd(["ntn", "api", "v1/search", "--data", json.dumps({"query": query, "page_size": page_size})]) or {}
    return [page_summary(row) for row in data.get("results") or []]

def query_datasource(ds_id, filter_obj, page_size):
    data = json_cmd([
        "ntn", "datasources", "query", ds_id,
        "--limit", str(page_size),
        "--filter", json.dumps(filter_obj),
        "--json",
    ]) or {}
    return [page_summary(row) for row in data.get("results") or []]

def edited_window_filter(a, b):
    return {"and": [
        {"timestamp": "last_edited_time", "last_edited_time": {"on_or_after": iso_utc(a)}},
        {"timestamp": "last_edited_time", "last_edited_time": {"on_or_before": iso_utc(b)}},
    ]}

def collect(a, b, queries, page_size):
    search_items = []
    for query in queries:
        search_items.extend(search(query, page_size))
    return {
        "search_items": search_items,
        "recent_tasks": query_datasource(TASKS_DS, edited_window_filter(a, b), page_size),
        "recent_projects": query_datasource(PROJECTS_DS, edited_window_filter(a, b), page_size),
        "recent_customers": query_datasource(CUSTOMERS_DS, edited_window_filter(a, b), page_size),
    }

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--query", action="append"); p.add_argument("--page-size", type=int, default=25)
    args = p.parse_args(); a, b = window_from_args(args.after, args.before, require=False)
    r = base_result("notion", "context", a, b)
    try:
        r.update(collect(a, b, args.query or [args.customer], args.page_size))
    except Exception as exc:
        err = error_obj("notion", exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
