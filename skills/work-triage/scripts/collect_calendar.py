#!/usr/bin/env python3
import argparse, os
from datetime import timedelta
from triage_common import DEFAULT_CALENDAR_ACCOUNTS, MAX_ITEMS_PER_LANE, add_common_args, base_result, emit, error_obj, iso_utc, json_cmd, parse_iso, window_from_args


def et(v): return v.get("dateTime") or v.get("date") if isinstance(v,dict) else None

def in_window(value,a,b):
    dt=parse_iso(value)
    return bool(dt and a <= dt < b)

def fetch_events(account,a,b,max_items):
    return json_cmd(["gog","-a",account,"--json","--results-only","calendar","events","--from",iso_utc(a),"--to",iso_utc(b),"--all","--max",str(max_items)])

def collect_account(account,a,b):
    lookback_days=int(os.environ.get("CALENDAR_CONTEXT_LOOKBACK_DAYS","2"))
    lookahead_days=int(os.environ.get("CALENDAR_CONTEXT_LOOKAHEAD_DAYS", os.environ.get("CALENDAR_UPDATE_LOOKAHEAD_DAYS","2")))
    context_after=a-timedelta(days=lookback_days)
    context_before=b+timedelta(days=lookahead_days)
    raw_events=fetch_events(account,context_after,context_before,MAX_ITEMS_PER_LANE)
    items=[]; seen=set()
    for e in raw_events:
        key=e.get("id") or e.get("iCalUID")
        if not key or key in seen:
            continue
        event_in_window = in_window(et(e.get("start")),a,b) or in_window(et(e.get("end")),a,b)
        event_in_context_window = in_window(et(e.get("start")),context_after,context_before) or in_window(et(e.get("end")),context_after,context_before)
        changed_in_window = in_window(e.get("created"),a,b) or in_window(e.get("updated"),a,b)
        if not event_in_context_window and not changed_in_window:
            continue
        seen.add(key)
        items.append({"id": e.get("id"), "ical_uid": e.get("iCalUID"), "title": e.get("summary"), "description": e.get("description"), "location": e.get("location"), "status": e.get("status"), "event_type": e.get("eventType"), "url": e.get("htmlLink"), "start": et(e.get("start")), "end": et(e.get("end")), "created": e.get("created"), "updated": e.get("updated"), "event_in_window": event_in_window, "event_in_context_window": event_in_context_window, "changed_in_window": changed_in_window, "organizer": (e.get("organizer") or {}).get("email"), "creator": (e.get("creator") or {}).get("email"), "attendees": [x.get("email") for x in e.get("attendees") or [] if x.get("email")], "source_account": account})
        if len(items) >= MAX_ITEMS_PER_LANE:
            break
    return {"source": account, "ok": True, "items": items, "context_lookback_days": lookback_days, "context_lookahead_days": lookahead_days}

def main():
    p=argparse.ArgumentParser(); add_common_args(p); p.add_argument("--account",action="append"); args=p.parse_args(); a,b=window_from_args(args.after,args.before,require=True); r=base_result("calendar","window_with_short_context",a,b); r["sources"]=[]
    for acct in args.account or DEFAULT_CALENDAR_ACCOUNTS:
        try: r["sources"].append(collect_account(acct,a,b))
        except Exception as exc: err=error_obj(acct,exc); r["sources"].append(err); r["errors"].append(err); r["ok"]=False
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
