#!/usr/bin/env python3
import argparse
from triage_common import NOTION_PROJECTS_DATA_SOURCE_ID, add_common_args, base_result, emit, error_obj, notion_query, window_from_args
from notion_helpers import limited_rows, project_item
ACTIVE=["Discovery","Planned","In Progress"]
def collect(a,b):
    active=[{"property":"Status","status":{"equals":s}} for s in ACTIVE]
    rows = limited_rows(notion_query(NOTION_PROJECTS_DATA_SOURCE_ID,{"filter":{"or":active},"sorts":[{"property":"Edited","direction":"descending"}],"page_size":100}))
    return [project_item(row) for row in rows]
def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args()
    a,b=window_from_args(args.after,args.before)
    r=base_result("projects","active",None,b)
    try: r["items"]=collect(a,b)
    except Exception as exc: err=error_obj("projects",exc); r["ok"]=False; r["errors"].append(err)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
