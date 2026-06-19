#!/usr/bin/env python3
import argparse, urllib.parse
from productive_common import MAX_ITEMS, add_common_args, base_result, emit, error_obj, iso_utc, json_cmd, productive_env, productive_headers, strip_html, window_from_args

BASE = "https://api.productive.io/api/v2"
DEFAULT_SMALL_GIANTS_SERVICE_IDS = {
    "14060256", # Teveo Development, earlier period
    "14060257", # Teveo Customer Lead, earlier period
    "14563321", # Teveo Development
    "14563323", # Teveo Customer Lead
    "14392681", # Teveo Automated Testing Retainer
    "13294339", # Skantrae Development Retainer - June
}

def collect(a, b, service_ids=None):
    service_ids = {str(x) for x in service_ids or [] if x}
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
            if service_ids and sid not in service_ids:
                continue
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
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--service-id", action="append")
    p.add_argument("--all-services", action="store_true")
    args = p.parse_args()
    a, b = window_from_args(args.after, args.before, require=False)
    r = base_result("productive", "time_entries", a, b)
    try:
        service_ids = None if args.all_services else (args.service_id or DEFAULT_SMALL_GIANTS_SERVICE_IDS)
        r["service_ids"] = sorted(service_ids) if service_ids else None
        r["items"] = collect(a, b, service_ids)
        r["total_hours"] = round(sum(x["hours"] for x in r["items"]), 2)
    except Exception as exc:
        err = error_obj("productive", exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
