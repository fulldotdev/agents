"""Small views over the complete persisted triage evidence; never a second ledger."""

import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from common import parse_iso, title

SOURCE_LANES = ("gmail", "slack", "whatsapp", "calendar", "meetings", "t3_threads")
WORK_LANES = ("companies", "projects", "tasks")
INDEX_FIELDS = (
    "id", "code", "name", "title", "subject", "url", "status", "state", "area",
    "companies", "project", "projects", "parent_project", "subprojects", "sprint", "date", "deadline",
    "edited", "updated", "updated_at", "created", "start", "end", "when",
    "account", "source_account", "workspace_id", "workspace_slug", "channel_id",
    "chat_id", "chat_name", "thread_id", "thread_ts", "ts", "sender", "from",
    "is_sent_by_me", "event_in_window", "changed_in_window", "transcript_ready",
)


def rows(result, lane):
    groups = result.get("groups") or {}
    if lane in WORK_LANES:
        return ((groups.get("work_context") or {}).get("lanes", {}).get(lane) or {}).get("items") or []
    value = (groups.get("incoming") or {}).get("sources", {}).get(lane) or {}
    if lane in {"gmail", "calendar"}:
        return [item for source in value.get("sources") or [] for item in source.get("items") or []]
    return value.get("items") or []


def header(item):
    value = {key: item[key] for key in INDEX_FIELDS if item.get(key) is not None}
    if item.get("properties") and not value.get("name"):
        value["name"] = title(item)
    for key in ("messages", "thread_replies", "files", "resources", "meeting_notes"):
        if item.get(key):
            value[key + "_count"] = len(item[key])
    text = item.get("text") or item.get("snippet") or item.get("description")
    if text:
        value["preview"] = str(text)[:180]
        value["preview_truncated"] = len(str(text)) > 180
    return value


def gate(state, at=None):
    """Only a complete, empty batch without time-sensitive work can skip the model."""
    batch = state.get("pending") or {}
    result = batch.get("result") or {}
    proposals = batch.get("proposals") or {}
    reasons = []
    if not batch or result.get("ok") is not True:
        reasons.append("missing_or_failed_collection")
    for lane in (*SOURCE_LANES, "work_context"):
        if not proposals.get(lane, {}).get("complete"):
            reasons.append("incomplete:" + lane)
    for lane in WORK_LANES:
        value = ((result.get("groups") or {}).get("work_context") or {}).get("lanes", {}).get(lane)
        if not isinstance(value, dict) or value.get("ok") is not True:
            reasons.append("incomplete:" + lane)
    if any(e.get("status") != "done" for e in batch.get("events", {}).values()) or state.get("backlog"):
        reasons.append("unfinished_events")
    if any(a.get("status") == "prepared" for a in state.get("actions", {}).values()):
        reasons.append("unresolved_actions")
    if state.get("failures"):
        reasons.append("source_failures")
    if any(not r.get("reported_at") and not r.get("resolved_at") for r in state.get("reports", {}).values()):
        reasons.append("undelivered_reports")
    current = at or parse_iso(result.get("before")) or datetime.now(timezone.utc)
    last = parse_iso(state.get("last_finished_at"))
    if last is None:
        reasons.append("no_completed_baseline")
    for event in rows(result, "calendar"):
        if event.get("status") == "cancelled":
            continue
        try:
            start, end = parse_iso(event.get("start")), parse_iso(event.get("end"))
            if not start:
                reasons.append("calendar_date_unreadable")
                break
            if start and (end or start) >= (last or current) and start <= current + timedelta(days=1):
                reasons.append("calendar_due")
                break
        except (TypeError, ValueError):
            reasons.append("calendar_date_unreadable")
            break
    today = current.astimezone(ZoneInfo("Europe/Amsterdam")).date().isoformat()
    for task in [*rows(result, "tasks"), *rows(result, "projects")]:
        date = task.get("date") or task.get("deadline")
        if task.get("status") not in {"Done", "Completed", "Canceled"} and date:
            due = date.get("start") if isinstance(date, dict) else date
            try:
                parsed = parse_iso(due)
            except (TypeError, ValueError):
                parsed = None
            if parsed is None or due[:10] <= today:
                reasons.append("task_due")
                break
    return {"run_model": bool(reasons), "reasons": list(dict.fromkeys(reasons))}


def view(state):
    batch = state.get("pending") or {}
    result = batch.get("result") or {}
    events = batch.get("events") or state.get("backlog") or {}
    groups = result.get("groups") or {}
    sources = (groups.get("incoming") or {}).get("sources") or {}
    work = (groups.get("work_context") or {}).get("lanes") or {}
    return {
        "ok": result.get("ok", not bool(state.get("failures"))), "compact": True,
        "errors": result.get("errors", []),
        "owner": state.get("owner"), "batch_id": batch.get("id"),
        "collected_at": batch.get("collected_at"), "after": result.get("after"), "before": result.get("before"),
        "lanes": {lane: {"ok": value.get("ok", True), "count": len(rows(result, lane)),
                          "complete": batch.get("proposals", {}).get(lane if lane in SOURCE_LANES else "work_context", {}).get("complete", False),
                          "errors": value.get("errors", [])}
                  for lane, value in {**sources, **work}.items()},
        "work_index": {lane: [header(item) for item in rows(result, lane)] for lane in WORK_LANES},
        "source_index": {lane: [header(item) for item in rows(result, lane)] for lane in SOURCE_LANES},
        "queue": {"pending_count": sum(e.get("status") != "done" for e in events.values()),
                  "events": {key: {**{k: v for k, v in event.items() if k != "item"},
                                   "source": header(event["item"])}
                             for key, event in events.items() if event.get("status") != "done"},
                  "actions": {key: value for key, value in state.get("actions", {}).items()
                              if value.get("status") == "prepared" or any(key in e.get("actions", []) for e in events.values() if e.get("status") != "done")},
                  "reports": [{"key": key, **value} for key, value in state.get("reports", {}).items()
                              if not value.get("reported_at") and not value.get("resolved_at")],
                  "failures": state.get("failures", {})},
        "gate": gate(state),
        "read": "queue show --event ID (repeatable); queue context --lane LANE --id ID or --query TEXT. Index/preview is not full evidence; read source and destination before deciding.",
    }


def context(state, lane, identifiers=None, query=None):
    if lane not in (*SOURCE_LANES, *WORK_LANES):
        raise ValueError("Unknown context lane")
    if not identifiers and not query:
        raise ValueError("Context requires --id or --query; use the compact index to select evidence")
    result = (state.get("pending") or {}).get("result") or {}
    def matches(item):
        ids = {str(item[k]) for k in ("id", "code", "thread_id", "chat_id", "thread_ts", "ts") if item.get(k) is not None}
        return (not identifiers or bool(ids.intersection(identifiers))) and (not query or query.casefold() in json.dumps(item, ensure_ascii=False).casefold())
    return {"lane": lane, "items": [item for item in rows(result, lane) if matches(item)]}


def show(state, identifiers):
    if not identifiers:
        raise ValueError("Show requires at least one --event")
    events = (state.get("pending") or {}).get("events") or state.get("backlog") or {}
    if any(key not in events for key in identifiers):
        raise ValueError("Unknown event; refresh queue status before deciding")
    selected = {key: events[key] for key in identifiers}
    chats = {e["item"].get("chat_id") for e in selected.values() if e["lane"] == "whatsapp"}
    return {"events": selected,
            "actions": {key: state.get("actions", {}).get(key) for e in selected.values() for key in e.get("actions", [])},
            "whatsapp_context": context(state, "whatsapp", chats)["items"] if chats else []}
