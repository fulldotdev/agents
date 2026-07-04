#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import collect_incoming_lanes, collect_work_context
from triage_common import add_common_args, emit, iso_utc, window_from_args

def run_group(name, fn):
    try:
        return name, fn(), None
    except Exception as exc:
        return name, None, str(exc)

def main():
    p=argparse.ArgumentParser(); add_common_args(p); args=p.parse_args()
    a,b=window_from_args(args.after,args.before)
    r={"generated_at":iso_utc(datetime.now(timezone.utc)),"mode":"combined_context","after":iso_utc(a) if a else None,"before":iso_utc(b),"ok":True,"errors":[],"groups":{}}
    jobs={
        "incoming":lambda:collect_incoming_lanes.collect(a,b),
        "work_context":lambda:collect_work_context.collect(a,b),
    }
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        futures=[executor.submit(run_group,name,fn) for name,fn in jobs.items()]
        for future in as_completed(futures):
            name,val,error=future.result()
            if error:
                err={"group":name,"ok":False,"error":error}
                r["groups"][name]=err; r["errors"].append(err); r["ok"]=False
            else:
                r["groups"][name]=val
                if not val.get("ok",False):
                    r["errors"].extend(val.get("errors",[])); r["ok"]=False
    emit(r, args.pretty, args.format)

if __name__=="__main__": main()
