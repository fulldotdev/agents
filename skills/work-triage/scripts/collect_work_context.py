#!/usr/bin/env python3
import argparse, collect_customers, collect_projects, collect_tasks
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from triage_common import add_common_args, emit, error_obj, iso_utc, window_from_args

def collect(a,b):
    r={"generated_at":iso_utc(datetime.now(timezone.utc)),"lane":"work_context","mode":"customers_projects_active_tasks_active_or_current_sprint","after":iso_utc(a) if a else None,"before":iso_utc(b),"ok":True,"errors":[],"lanes":{}}
    calls={"customers":lambda:collect_customers.collect(a,b),"projects":lambda:collect_projects.collect(a,b),"tasks":lambda:collect_tasks.collect(a,b)}
    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures={executor.submit(fn):lane for lane,fn in calls.items()}
        for future in as_completed(futures):
            lane=futures[future]
            try: r["lanes"][lane]={"ok":True,"items":future.result()}
            except Exception as exc: err=error_obj(lane,exc); r["lanes"][lane]=err; r["errors"].append(err); r["ok"]=False
    return r

def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args()
    a,b=window_from_args(args.after,args.before)
    r=collect(a,b)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
