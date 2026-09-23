#!/usr/bin/env python3
"""Google Calendar collector for work triage."""

import json
import os
from datetime import timedelta

from common import DEFAULT_CALENDAR_ACCOUNTS, MAX_ITEMS_PER_LANE, error_obj, iso_utc, json_cmd, parse_iso


def event_time(value):
    return value.get("dateTime") or value.get("date") if isinstance(value, dict) else None


def in_window(value, after, before):
    dt = parse_iso(value)
    return bool(dt and after <= dt < before)


def google(account, method, params, body=None):
    cmd = ["gog", "--no-input", "--gmail-no-send", "-a", account, "--json"]
    if body is None:
        cmd.append("--readonly")
    cmd += ["api", "call", "calendar", "v3", "calendar." + method,
            "--params", json.dumps(params), "--scope", "https://www.googleapis.com/auth/calendar" +
            (".readonly" if body is None else "")]
    if body is not None:
        cmd += ["--allow-write", "--force", "--body", json.dumps(body)]
    return json_cmd(cmd)


def google_pages(account, method, params):
    params = dict(params)
    rows, seen = [], set()
    while True:
        data = google(account, method, params)
        rows.extend(data.get("items") or [])
        token = data.get("nextPageToken")
        if not token:
            return rows
        if token in seen:
            raise RuntimeError("Repeated Google Calendar pagination token")
        seen.add(token)
        params["pageToken"] = token


def fetch_events(account, after, before, limit, changed_after=None):
    rows = []
    for cal in google_pages(account, "calendarList.list", {"maxResults": 250}):
        if cal.get("accessRole") == "freeBusyReader":
            continue
        base = {"calendarId": cal["id"], "maxResults": min(limit, 2500)}
        events = google_pages(account, "events.list", {
            **base, "timeMin": iso_utc(after), "timeMax": iso_utc(before),
            "singleEvents": True, "showDeleted": True,
        })
        if changed_after:
            # No event-date bound: a new invitation next month is still incoming work.
            changes = google_pages(account, "events.list", {
                **base, "updatedMin": iso_utc(changed_after), "showDeleted": True,
                "singleEvents": False,
            })
            for event in changes:
                if event.get("recurrence") and event.get("status") != "cancelled":
                    events.extend(google_pages(account, "events.instances", {
                        **base, "eventId": event["id"], "timeMin": iso_utc(changed_after),
                        "timeMax": iso_utc(before + timedelta(days=30)), "showDeleted": True,
                    }))
                else:
                    events.append(event)
        for event in events:
            event["calendar_id"] = cal["id"]
            event["calendar_access"] = cal.get("accessRole")
            rows.append(event)
    return rows


def collect_account(account, after, before, limit=MAX_ITEMS_PER_LANE, context=False):
    lookback = int(os.environ.get("CALENDAR_CONTEXT_LOOKBACK_DAYS", "2")) if context else 0
    lookahead = int(os.environ.get(
        "CALENDAR_CONTEXT_LOOKAHEAD_DAYS", os.environ.get("CALENDAR_UPDATE_LOOKAHEAD_DAYS", "2")
    )) if context else 0
    fetch_after = after - timedelta(days=lookback)
    fetch_before = before + timedelta(days=lookahead)
    items = []
    seen = set()
    for event in fetch_events(account, fetch_after, fetch_before, limit, after if context else None):
        key = (event.get("calendar_id"), event.get("id"))
        if not key or key in seen:
            continue
        seen.add(key)
        item = {
            "id": event.get("id"), "ical_uid": event.get("iCalUID"),
            "title": event.get("summary"), "description": event.get("description"),
            "location": event.get("location"), "status": event.get("status"),
            "event_type": event.get("eventType"), "url": event.get("htmlLink"),
            "start": event_time(event.get("start")), "end": event_time(event.get("end")),
            "created": event.get("created"), "updated": event.get("updated"),
            "calendar_id": event["calendar_id"], "calendar_access": event["calendar_access"],
            "recurring_event_id": event.get("recurringEventId"),
            "original_start": event_time(event.get("originalStartTime")),
            "recurrence": event.get("recurrence"),
            "organizer": {
                "email": (event.get("organizer") or {}).get("email"),
                "name": (event.get("organizer") or {}).get("displayName"),
            },
            "creator": {
                "email": (event.get("creator") or {}).get("email"),
                "name": (event.get("creator") or {}).get("displayName"),
            },
            "attendees": [
                {
                    "email": attendee.get("email"),
                    "name": attendee.get("displayName"),
                    "response_status": attendee.get("responseStatus"),
                    "organizer": bool(attendee.get("organizer")),
                    "self": bool(attendee.get("self")),
                    "optional": bool(attendee.get("optional")),
                }
                for attendee in event.get("attendees") or []
                if attendee.get("email") or attendee.get("displayName")
            ],
            "source_account": account,
        }
        if context:
            item.update({
                "event_in_window": in_window(item["start"], after, before) or in_window(item["end"], after, before),
                "event_in_context_window": in_window(item["start"], fetch_after, fetch_before) or in_window(item["end"], fetch_after, fetch_before),
                "changed_in_window": in_window(item["created"], after, before) or in_window(item["updated"], after, before),
            })
        items.append(item)
    result = {"source": account, "ok": True, "complete": True, "items": items}
    if context:
        result.update({"context_lookback_days": lookback, "context_lookahead_days": lookahead})
    return result


def collect(after, before, accounts=None, limit=MAX_ITEMS_PER_LANE, context=False):
    results = []
    for account in accounts or DEFAULT_CALENDAR_ACCOUNTS:
        try:
            results.append(collect_account(account, after, before, limit, context))
        except Exception as exc:
            results.append(error_obj(account, exc))
    return results
