#!/usr/bin/env python3
import argparse, importlib, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from triage_common import RUN_LOG_DIR, add_common_args, emit, iso_utc, window_from_args
LANES={"gmail":"collect_gmail","slack":"collect_slack","whatsapp":"collect_whatsapp","calendar":"collect_calendar","meetings":"collect_meetings"}
TRIAGE_TZ = ZoneInfo("Europe/Amsterdam")

def incoming_window(a, b):
    before = b or datetime.now(timezone.utc)
    local_before = before.astimezone(TRIAGE_TZ)
    local_start = datetime.combine(local_before.date(), datetime.min.time(), TRIAGE_TZ)
    return local_start - timedelta(days=1), before

def mark_lane_status(r, lane, val):
    item_errors = [x for x in val.get("items") or [] if isinstance(x, dict) and x.get("ok") is False]
    if item_errors:
        err = {"lane": lane, "ok": False, "errors": item_errors, "items": []}
        val["ok"] = False
        val["errors"] = item_errors
        r["errors"].append(err)
        r["ok"] = False
    else:
        val["ok"] = True

def collect_lane(lane, a, b):
    m=importlib.import_module(LANES[lane])
    if lane=="gmail": return {"sources":[m.collect_account(x,a,b) for x in m.DEFAULT_GMAIL_ACCOUNTS],"ok":True}
    if lane=="calendar": return {"sources":[m.collect_account(x,a,b) for x in m.DEFAULT_CALENDAR_ACCOUNTS],"ok":True}
    return {"items":m.collect(a,b)}

def collect(a, b, lanes=None):
    a, b = incoming_window(a, b)
    selected=lanes or list(LANES)
    r={"generated_at":iso_utc(datetime.now(timezone.utc)),"lane":"incoming","mode":"window","after":iso_utc(a),"before":iso_utc(b),"ok":True,"errors":[],"lanes":{}}
    with ThreadPoolExecutor(max_workers=len(selected)) as executor:
        futures={executor.submit(collect_lane,lane,a,b):lane for lane in selected}
        for future in as_completed(futures):
            lane=futures[future]
            try:
                val=future.result()
                if "items" in val: mark_lane_status(r,lane,val)
                r["lanes"][lane]=val
            except Exception as exc:
                err={"lane":lane,"ok":False,"error":str(exc),"items":[]}; r["lanes"][lane]=err; r["errors"].append(err); r["ok"]=False
    return r

def main():
    p=argparse.ArgumentParser(); add_common_args(p); p.add_argument("--lane",action="append",choices=sorted(LANES)); p.add_argument("--save",action="store_true"); args=p.parse_args()
    a,b=window_from_args(args.after,args.before)
    r=collect(a,b,args.lane)
    if args.save:
        RUN_LOG_DIR.mkdir(parents=True,exist_ok=True); path=RUN_LOG_DIR/f"incoming_{a.date().isoformat()}_{b.date().isoformat()}.json"; path.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n"); r["saved_to"]=str(path)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
