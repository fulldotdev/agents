#!/usr/bin/env python3
"""Google Calendar collector shared by triage and Sprint planning."""

import os
from datetime import timedelta

from common import DEFAULT_CALENDAR_ACCOUNTS, MAX_ITEMS_PER_LANE, error_obj, iso_utc, json_cmd, parse_iso


def event_time(value):
    return value.get("dateTime") or value.get("date") if isinstance(value, dict) else None


def in_window(value, after, before):
    dt = parse_iso(value)
    return bool(dt and after <= dt < before)


def fetch_events(account, after, before, limit):
    return json_cmd([
        "gog", "-a", account, "--json", "--results-only", "calendar", "events",
        "--from", iso_utc(after), "--to", iso_utc(before), "--all", "--max", str(limit),
    ])


def collect_account(account, after, before, limit=MAX_ITEMS_PER_LANE, context=False):
    lookback = int(os.environ.get("CALENDAR_CONTEXT_LOOKBACK_DAYS", "2")) if context else 0
    lookahead = int(os.environ.get(
        "CALENDAR_CONTEXT_LOOKAHEAD_DAYS", os.environ.get("CALENDAR_UPDATE_LOOKAHEAD_DAYS", "2")
    )) if context else 0
    fetch_after = after - timedelta(days=lookback)
    fetch_before = before + timedelta(days=lookahead)
    items = []
    seen = set()
    for event in fetch_events(account, fetch_after, fetch_before, limit):
        key = event.get("id") or event.get("iCalUID")
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
            "organizer": (event.get("organizer") or {}).get("email"),
            "creator": (event.get("creator") or {}).get("email"),
            "attendees": [x.get("email") for x in event.get("attendees") or [] if x.get("email")],
            "source_account": account,
        }
        if context:
            item.update({
                "event_in_window": in_window(item["start"], after, before) or in_window(item["end"], after, before),
                "event_in_context_window": in_window(item["start"], fetch_after, fetch_before) or in_window(item["end"], fetch_after, fetch_before),
                "changed_in_window": in_window(item["created"], after, before) or in_window(item["updated"], after, before),
            })
        items.append(item)
        if len(items) >= limit:
            break
    result = {"source": account, "ok": True, "items": items}
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
