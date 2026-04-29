#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import DEFAULT_GMAIL_ACCOUNTS, MAX_ITEMS_PER_LANE, day_bounds_utc, iso_utc, run


def _json_cmd(cmd):
    return json.loads(run(cmd))


def _event_time(value):
    if not isinstance(value, dict):
        return None
    return value.get("dateTime") or value.get("date")


def _attendee_emails(event):
    emails = []
    for attendee in event.get("attendees") or []:
        email = attendee.get("email")
        if email:
            emails.append(email)
    return emails


def _collect_account_calendar(account, after_dt, before_dt):
    try:
        events = _json_cmd([
            "gog", "-a", account, "--json", "--results-only",
            "calendar", "events",
            "--from", iso_utc(after_dt),
            "--to", iso_utc(before_dt),
            "--all",
            "--max", str(MAX_ITEMS_PER_LANE),
        ])
        items = []
        for event in events[:MAX_ITEMS_PER_LANE]:
            items.append({
                "id": event.get("id"),
                "iCalUID": event.get("iCalUID"),
                "summary": event.get("summary"),
                "description": event.get("description"),
                "location": event.get("location"),
                "status": event.get("status"),
                "eventType": event.get("eventType"),
                "htmlLink": event.get("htmlLink"),
                "start": _event_time(event.get("start")),
                "end": _event_time(event.get("end")),
                "created": event.get("created"),
                "updated": event.get("updated"),
                "organizer": (event.get("organizer") or {}).get("email"),
                "creator": (event.get("creator") or {}).get("email"),
                "attendees": _attendee_emails(event),
                "raw_calendar": ((event.get("organizer") or {}).get("email")) or account,
            })
        return {"account": account, "ok": True, "items": items}
    except Exception as exc:
        return {"account": account, "ok": False, "error": str(exc), "items": []}


def collect_calendar(after_dt=None, before_dt=None, accounts=DEFAULT_GMAIL_ACCOUNTS):
    return [_collect_account_calendar(account, after_dt, before_dt) for account in accounts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)

    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "calendar",
        "mode": "window",
        "after": iso_utc(after_dt),
        "before": iso_utc(before_dt),
        "items": collect_calendar(after_dt, before_dt, DEFAULT_GMAIL_ACCOUNTS),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
