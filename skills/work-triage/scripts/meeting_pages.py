#!/usr/bin/env python3
"""Prepare and attach meeting pages before the triage agent runs."""

import json
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from calendar import google, event_time
from common import (
    DEFAULT_CALENDAR_ACCOUNTS, NOTION_MEETINGS_DATA_SOURCE_ID, NOTION_VERSION,
    json_cmd, notion_blocks, notion_query, parse_iso, plain_text, title,
)

EVENT_KEY = "Calendar event ID"
CANCELED = "Canceled"
OWN_EMAILS = {*DEFAULT_CALENDAR_ACCOUNTS, "sil@smallgiants.nl"}
PAGE_ID = re.compile(r"([0-9a-f]{32}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:$|[?#])", re.I)


def notion(path, body=None):
    cmd = ["ntn", "api", "v1/" + path, "--notion-version", NOTION_VERSION]
    if body is not None:
        cmd += ["-X", "POST" if path == "pages" else "PATCH", "-d", json.dumps(body)]
    return json_cmd(cmd)


def query(query_filter):
    rows, cursor, seen = [], None, set()
    while True:
        payload = {"filter": query_filter, "page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        data = notion_query(NOTION_MEETINGS_DATA_SOURCE_ID, payload)
        rows.extend(data["results"])
        cursor = data.get("next_cursor")
        if not data.get("has_more") and not cursor:
            return rows
        if not cursor or cursor in seen:
            raise RuntimeError("Incomplete meeting-page query")
        seen.add(cursor)


def ensure_schema():
    path = "data_sources/" + NOTION_MEETINGS_DATA_SOURCE_ID
    properties = notion(path)["properties"]
    wanted = {EVENT_KEY: "rich_text", CANCELED: "checkbox"}
    missing = {}
    for name, kind in wanted.items():
        if name not in properties:
            missing[name] = {kind: {}}
        elif properties[name]["type"] != kind:
            raise RuntimeError(f"Meetings.{name} must be {kind}")
    if missing:
        notion(path, {"properties": missing})
        actual = notion(path)["properties"]
        if any(actual.get(k, {}).get("type") != v for k, v in wanted.items()):
            raise RuntimeError("Meeting-page schema readback failed")


def rich(value):
    return [{"type": "text", "text": {"content": value}}]


def key_for(event):
    uid = event.get("iCalUID")
    if not uid:
        return None
    original = event_time(event.get("originalStartTime"))
    return uid + ("|" + parse_iso(original).isoformat() if original else "")


def page_key(page):
    return plain_text(page.get("properties", {}).get(EVENT_KEY, {}))


def page_id_from_url(url):
    if urlparse(url).hostname not in {"notion.so", "www.notion.so", "notion.com", "www.notion.com", "app.notion.com"}:
        return None
    match = PAGE_ID.search(url)
    return match.group(1) if match else None


def meeting_block(page):
    blocks = [b for b in notion_blocks(page["id"]) if b["type"] == "meeting_notes"]
    if len(blocks) != 1:
        raise RuntimeError("Expected exactly one native meeting-notes block; review the existing page")
    return blocks[0]


def sync_block_title(page, block, name):
    current = "".join(t.get("plain_text", "") for t in block["meeting_notes"].get("title", []))
    if current == name:
        return block
    data = notion("pages/" + page["id"] + "/markdown")
    matches = list(re.finditer(r"(<meeting-notes[^>]*>\n\t)([^\n]+)", data["markdown"]))
    if data.get("truncated") or len(matches) != 1:
        raise RuntimeError("Cannot safely locate the existing meeting block title")
    match = matches[0]
    notion("pages/" + page["id"] + "/markdown", {
        "type": "update_content", "update_content": {"content_updates": [{
            "old_str": match.group(0), "new_str": match.group(1) + name.replace("\n", " "),
        }]},
    })
    updated = meeting_block(page)
    if updated["id"] != block["id"] or "".join(t.get("plain_text", "") for t in updated["meeting_notes"].get("title", [])) != name:
        raise RuntimeError("Meeting block title readback failed")
    return updated


def choose_page(event, key):
    rows = query({"property": EVENT_KEY, "rich_text": {"equals": key}})
    attached = []
    for attachment in event.get("attachments") or []:
        pid = page_id_from_url(attachment.get("fileUrl", ""))
        if pid:
            page = notion("pages/" + pid)
            if page.get("in_trash"):
                raise RuntimeError("Event points to a trashed Notion page; review before recreating")
            attached.append(page)
    if not rows:
        start = event_time(event.get("start"))
        # Older native notes have no event key. Never create beside a possible match.
        candidates = query({"property": "When", "date": {"equals": start}})
        candidates = [p for p in candidates if parse_iso((p["properties"]["When"].get("date") or {}).get("start")) == parse_iso(start)]
        candidates += attached
        candidates = list({p["id"]: p for p in candidates}.values())
        for page in candidates:
            if page_key(page) == key:
                rows.append(page)
            elif not page_key(page) and title(page) == event.get("summary"):
                when = (page.get("properties", {}).get("When", {}).get("date") or {}).get("start")
                if parse_iso(when) == parse_iso(start):
                    rows.append(page)
        if candidates and not rows:
            raise RuntimeError("Possible existing meeting page; match it before creating another")
    if len(rows) > 1:
        raise RuntimeError("Multiple meeting pages match this event; review duplicates")
    page = rows[0] if rows else None
    if any(not page or p["id"] != page["id"] for p in attached):
        raise RuntimeError("Another Notion page is already attached; keep it and review the intended meeting note")
    if page:
        if page.get("parent", {}).get("data_source_id") != NOTION_MEETINGS_DATA_SOURCE_ID:
            raise RuntimeError("Attached page is outside the Meetings database")
        if page.get("in_trash"):
            raise RuntimeError("Meeting page is in trash; restore it or explicitly skip the event")
        meeting_block(page)
    return page


def set_canceled(key):
    pages = query({"property": EVENT_KEY, "rich_text": {"equals": key}})
    for page in pages:
        if not page["properties"].get(CANCELED, {}).get("checkbox"):
            notion("pages/" + page["id"], {"properties": {CANCELED: {"checkbox": True}}})
            if not notion("pages/" + page["id"])["properties"][CANCELED]["checkbox"]:
                raise RuntimeError("Cancellation readback failed")
    return pages


def prepare(item, bindings, save):
    account, calendar_id = item["source_account"], item["calendar_id"]
    params = {"calendarId": calendar_id, "eventId": item["id"]}
    event = google(account, "events.get", params)
    item.update(title=event.get("summary"), status=event.get("status"),
                start=event_time(event.get("start")), end=event_time(event.get("end")))
    previous = bindings.get(item["ref"], {})
    key = key_for(event) or previous.get("key")
    if event.get("status") == "cancelled":
        # A deleted series may contain only its ID. Bindings retain its known occurrences.
        keys = {key} if key else set()
        keys.update(b["key"] for b in bindings.values()
                    if b.get("account") == account and b.get("calendar_id") == calendar_id
                    and b.get("series_id") == item["id"]
                    and parse_iso(b.get("start")) >= datetime.now(timezone.utc))
        pages = [p for k in keys for p in set_canceled(k)]
        return {"status": "canceled", "pages": [{"id": p["id"], "url": p["url"]} for p in pages]}
    start, end = event_time(event.get("start")), event_time(event.get("end"))
    if not start or "T" not in start or parse_iso(start) <= datetime.now(timezone.utc):
        return {"status": "skipped", "reason": "Not a future timed meeting"}
    attendees = event.get("attendees") or []
    if event.get("eventType", "default") not in {"default", "fromGmail"} or not any(
        a.get("email", "").lower() not in OWN_EMAILS and not a.get("self") and not a.get("resource")
        and a.get("responseStatus") != "declined" for a in attendees
    ):
        return {"status": "skipped", "reason": "No other participant"}
    if any(a.get("self") and a.get("responseStatus") == "declined" for a in attendees):
        return {"status": "skipped", "reason": "Invitation declined"}
    if item.get("calendar_access") not in {"owner", "writer"}:
        raise RuntimeError(f"Calendar {calendar_id} is read-only through {account}; calendar write access is needed")
    if not key:
        raise RuntimeError("Calendar event has no stable iCalUID")
    known = next((b["page_id"] for b in bindings.values() if b.get("key") == key), None)
    if known and notion("pages/" + known).get("in_trash"):
        return {"status": "skipped", "reason": "Previously prepared page is in trash"}
    page = choose_page(event, key)
    properties = {
        "Name": {"title": rich(event.get("summary") or "Meeting")},
        "When": {"date": {"start": start, "end": end}},
        EVENT_KEY: {"rich_text": rich(key)}, CANCELED: {"checkbox": False},
    }
    created = page is None
    if created:
        safe_title = (event.get("summary") or "Meeting").replace("\n", " ")
        page = notion("pages", {
            "parent": {"data_source_id": NOTION_MEETINGS_DATA_SOURCE_ID}, "properties": properties,
            "markdown": f"<meeting-notes>\n\t{safe_title}\n\t<notes>\n\t\t## Preparation\n\t\t## Notes\n\t</notes>\n</meeting-notes>",
        })
    else:
        changed = {}
        for name, value in properties.items():
            old = page["properties"].get(name, {})
            differs = (title(page) != event.get("summary")) if name == "Name" else (
                page_key(page) != key if name == EVENT_KEY else
                old.get("checkbox", False) if name == CANCELED else
                any(parse_iso((old.get("date") or {}).get(k)) != parse_iso(v) for k, v in value["date"].items())
            )
            if differs:
                changed[name] = value
        if changed:
            page = notion("pages/" + page["id"], {"properties": changed})
    page = notion("pages/" + page["id"])
    if page_key(page) != key:
        raise RuntimeError("Meeting identity readback failed")
    dates = page["properties"]["When"]["date"]
    if parse_iso(dates.get("start")) != parse_iso(start) or parse_iso(dates.get("end")) != parse_iso(end):
        raise RuntimeError("Meeting date readback failed")
    block = sync_block_title(page, meeting_block(page), event.get("summary") or "Meeting")
    bindings[item["ref"]] = {"key": key, "page_id": page["id"], "account": account,
                              "calendar_id": calendar_id, "series_id": event.get("recurringEventId"), "start": start}
    save()
    # Re-read immediately before a write, preserving every attachment and its metadata.
    current = google(account, "events.get", params)
    if current.get("status") == "cancelled" or current.get("start") != event.get("start"):
        raise RuntimeError("Event changed while preparing its note; retry with the current event")
    attachments = current.get("attachments") or []
    compact_id = page["id"].replace("-", "")
    if not any((page_id_from_url(a.get("fileUrl", "")) or "").replace("-", "") == compact_id for a in attachments):
        if any(page_id_from_url(a.get("fileUrl", "")) for a in attachments):
            raise RuntimeError("A different Notion page was attached during this run; review before changing it")
        if len(attachments) >= 25:
            raise RuntimeError("Calendar event already has 25 attachments")
        google(account, "events.patch", {**params, "supportsAttachments": True, "sendUpdates": "none"},
               {"attachments": attachments + [{"fileUrl": page["url"], "title": title(page)}]})
        current = google(account, "events.get", params)
        if not any((page_id_from_url(a.get("fileUrl", "")) or "").replace("-", "") == compact_id
                   for a in current.get("attachments") or []):
            raise RuntimeError("Calendar attachment readback failed")
    return {"status": "created" if created else "ready", "page_id": page["id"], "url": page["url"],
            "notes_block_id": block["meeting_notes"]["children"].get("notes_block_id")}


def prepare_batch(items, state, save):
    """Keep failed writes independently of the agent's intake retry list."""
    pending = {i["ref"]: i for i in state.get("meeting_page_retry", [])}
    pending.update({i["ref"]: i for i in items})
    bindings = state.setdefault("meeting_page_bindings", {})
    retry, result = [], []
    state["meeting_page_retry"] = list(pending.values())
    save()
    try:
        if pending:
            ensure_schema()
        schema_error = None
    except Exception as exc:
        schema_error = str(exc)
    for item in pending.values():
        item = dict(item)
        try:
            if schema_error:
                raise RuntimeError(schema_error)
            item["meeting_page"] = prepare(item, bindings, save)
        except Exception as exc:
            item["meeting_page"] = {"status": "error", "error": str(exc)}
            retry.append(item)
        result.append(item)
    state["meeting_page_retry"] = retry
    save()
    return result
