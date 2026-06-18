#!/usr/bin/env python3
import argparse, re
from productive_common import DEFAULT_CALENDAR_ACCOUNTS, MAX_ITEMS, add_common_args, base_result, emit, error_obj, iso_utc, json_cmd, parse_iso, window_from_args

def et(value):
    return value.get("dateTime") or value.get("date") if isinstance(value, dict) else None

def collect_account(account, a, b, query):
    raw = json_cmd(["gog", "-a", account, "--json", "--results-only", "calendar", "events", "--from", iso_utc(a), "--to", iso_utc(b), "--all", "--max", str(MAX_ITEMS)]) or []
    rx = re.compile(query, re.I) if query else None
    items = []
    for e in raw:
        hay = " ".join([
            e.get("summary") or "",
            e.get("description") or "",
            e.get("location") or "",
            " ".join(x.get("email", "") for x in e.get("attendees") or []),
        ])
        if rx and not rx.search(hay):
            continue
        items.append({
            "id": e.get("id"),
            "title": e.get("summary"),
            "start": et(e.get("start")),
            "end": et(e.get("end")),
            "organizer": (e.get("organizer") or {}).get("email"),
            "attendees": [x.get("email") for x in e.get("attendees") or [] if x.get("email")],
            "url": e.get("htmlLink"),
            "source_account": account,
        })
    return items

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--account", action="append"); p.add_argument("--query")
    args = p.parse_args(); a, b = window_from_args(args.after, args.before)
    r = base_result("calendar", "events", a, b); r["sources"] = []
    query = args.query or args.customer
    for account in args.account or DEFAULT_CALENDAR_ACCOUNTS:
        try:
            items = collect_account(account, a, b, query)
            r["sources"].append({"source": account, "ok": True, "items": items})
            r["items"].extend(items)
        except Exception as exc:
            err = error_obj(account, exc); r["ok"] = False; r["errors"].append(err); r["sources"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
