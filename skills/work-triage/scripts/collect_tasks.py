#!/usr/bin/env python3
import argparse
from triage_common import NOTION_SPRINTS_DATA_SOURCE_ID, NOTION_TASKS_DATA_SOURCE_ID, add_common_args, base_result, emit, error_obj, notion_query, window_from_args
from notion_helpers import limited_rows, task_item
ACTIVE=["Todo","Doing","Waiting"]

def current_sprint_id():
    rows = limited_rows(notion_query(NOTION_SPRINTS_DATA_SOURCE_ID, {
        "filter": {"property": "Status", "status": {"equals": "Current"}},
        "page_size": 1,
    }))
    return rows[0]["id"] if rows else None

def collect(a,b):
    active=[{"property":"Status","status":{"equals":s}} for s in ACTIVE]
    sprint_id = current_sprint_id()
    filters = active + ([{"property":"Sprint","relation":{"contains":sprint_id}}] if sprint_id else [])
    rows = limited_rows(notion_query(NOTION_TASKS_DATA_SOURCE_ID,{"filter":{"or":filters},"sorts":[{"property":"Edited","direction":"descending"}],"page_size":100}))
    return [task_item(row) for row in rows]

def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args()
    a,b=window_from_args(args.after,args.before)
    r=base_result("tasks","active_or_current_sprint",None,b)
    try: r["items"]=collect(a,b)
    except Exception as exc: err=error_obj("tasks",exc); r["ok"]=False; r["errors"].append(err)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
