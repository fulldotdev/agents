#!/usr/bin/env python3
import argparse, urllib.parse
from productive_common import MAX_ITEMS, add_common_args, base_result, emit, error_obj, iso_utc, json_cmd, productive_env, productive_headers, strip_html, window_from_args

BASE = "https://api.productive.io/api/v2"

def collect(a, b):
    env = productive_env()
    headers = productive_headers(env)
    docs = []
    page = 1
    while len(docs) * 200 < MAX_ITEMS:
        url = f"{BASE}/time_entries?page[size]=200&page[number]={page}&include=person,service,task"
        doc = json_cmd(["curl", "-g", "-sS", url, *headers])
        docs.append(doc)
        if not (doc.get("links") or {}).get("next"):
            break
        page += 1
    services = {
        s.get("id"): (s.get("attributes") or {}).get("name")
        for d in docs for s in d.get("included", [])
        if s.get("type") == "services"
    }
    items = []
    for d in docs:
        for row in d.get("data", []):
            attrs = row.get("attributes") or {}
            date = attrs.get("date")
            if not date:
                continue
            if not (iso_utc(a)[:10] <= date <= iso_utc(b)[:10]):
                continue
            sid = (((row.get("relationships") or {}).get("service") or {}).get("data") or {}).get("id")
            pid = (((row.get("relationships") or {}).get("person") or {}).get("data") or {}).get("id")
            items.append({
                "id": row.get("id"),
                "date": date,
                "minutes": attrs.get("time"),
                "hours": round((attrs.get("time") or 0) / 60, 2),
                "person_id": pid,
                "service_id": sid,
                "service": services.get(sid),
                "note": strip_html(attrs.get("note")),
                "approved": attrs.get("approved"),
                "invoiced": attrs.get("invoiced"),
            })
    return sorted(items, key=lambda x: (x["date"], x.get("service") or ""))

def main():
    p = argparse.ArgumentParser(); add_common_args(p); args = p.parse_args()
    a, b = window_from_args(args.after, args.before)
    r = base_result("productive", "time_entries", a, b)
    try:
        r["items"] = collect(a, b)
        r["total_hours"] = round(sum(x["hours"] for x in r["items"]), 2)
    except Exception as exc:
        err = error_obj("productive", exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
