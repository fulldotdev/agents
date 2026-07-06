#!/usr/bin/env python3
import argparse, json, subprocess
from datetime import datetime, timezone, timedelta
from common import add_args, base_result, emit, iso_utc, json_cmd, parse_iso

DEFAULT_CALENDAR_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]


def et(v): return v.get("dateTime") or v.get("date") if isinstance(v, dict) else None

def fetch_events(account, after, before, limit):
    return json_cmd(["gog", "-a", account, "--json", "--results-only", "calendar", "events", "--from", after, "--to", before, "--all", "--max", str(limit)])

def collect(after, before, limit, accounts):
    items=[]
    for account in accounts:
        source={"source": account, "ok": True, "items": []}
        try:
            for e in fetch_events(account, after, before, limit):
                source["items"].append({
                    "id": e.get("id"), "ical_uid": e.get("iCalUID"), "title": e.get("summary"),
                    "description": e.get("description"), "location": e.get("location"), "status": e.get("status"),
                    "url": e.get("htmlLink"), "start": et(e.get("start")), "end": et(e.get("end")),
                    "organizer": (e.get("organizer") or {}).get("email"),
                    "attendees": [x.get("email") for x in e.get("attendees") or [] if x.get("email")],
                })
        except Exception as exc:
            source={"source": account, "ok": False, "error": str(exc), "items": []}
        items.append(source)
    return items


def main():
    p = argparse.ArgumentParser(description="Calendar window for Sprint planning constraints/context only.")
    add_args(p)
    p.add_argument("--after", required=True)
    p.add_argument("--before", required=True)
    p.add_argument("--account", action="append")
    args = p.parse_args()
    r = base_result("calendar_context", "explicit_window")
    r["after"] = args.after; r["before"] = args.before
    try:
        parse_iso(args.after); parse_iso(args.before)
        r["sources"] = collect(args.after, args.before, args.limit, args.account or DEFAULT_CALENDAR_ACCOUNTS)
    except Exception as exc:
        r["ok"] = False; r["errors"].append({"source": "calendar_context", "error": str(exc), "items": []})
    emit(r, args.format, args.pretty)


if __name__ == "__main__":
    main()
