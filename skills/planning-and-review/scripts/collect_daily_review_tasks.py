#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timedelta, timezone

from collect_tasks import RECENTLY_CLOSED_LOOKBACK_HOURS, collect_tasks
from task_triage_common import iso_utc

DEFAULT_STALE_DAYS = 7
DEFAULT_RECENTLY_CLOSED_HOURS = max(RECENTLY_CLOSED_LOOKBACK_HOURS, 72)


def prop_text(prop):
    if not isinstance(prop, dict):
        return None
    if prop.get("type") == "status":
        value = prop.get("status") or {}
        return value.get("name")
    if prop.get("type") == "select":
        value = prop.get("select") or {}
        return value.get("name")
    if prop.get("type") == "title":
        return "".join(part.get("plain_text", "") for part in prop.get("title", [])) or None
    if prop.get("type") == "last_edited_time":
        return prop.get("last_edited_time")
    return None


def status_name(item):
    return prop_text((item.get("properties") or {}).get("Status")) or "Unknown"


def title_text(item):
    props = item.get("properties") or {}
    for value in props.values():
        if isinstance(value, dict) and value.get("type") == "title":
            text = prop_text(value)
            if text:
                return text
    return item.get("id")


def edited_dt(item):
    raw = prop_text((item.get("properties") or {}).get("Edited"))
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw).astimezone(timezone.utc)


def bucket_daily(items, stale_before_dt):
    active = []
    waiting = []
    recent_closed = []
    stale_open = []

    for item in items:
        status = status_name(item)
        edited = edited_dt(item)
        normalized = {
            "id": item.get("id"),
            "url": item.get("url"),
            "title": title_text(item),
            "status": status,
            "edited": iso_utc(edited) if edited else None,
            "properties": item.get("properties", {}),
        }
        if status in {"Done", "Canceled"}:
            recent_closed.append(normalized)
            continue
        if status in {"Waiting", "Backlog"}:
            waiting.append(normalized)
        else:
            active.append(normalized)
        if edited and edited < stale_before_dt:
            stale_open.append(normalized)

    return {
        "active_open": active,
        "waiting_or_backlog": waiting,
        "recent_closed": recent_closed,
        "stale_open": stale_open,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recently-closed-lookback-hours", type=int, default=DEFAULT_RECENTLY_CLOSED_HOURS)
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    recently_closed_after_dt = now - timedelta(hours=args.recently_closed_lookback_hours)
    stale_before_dt = now - timedelta(days=args.stale_days)
    collected = collect_tasks(recently_closed_after_dt=recently_closed_after_dt)
    items = collected.get("items", []) if collected.get("ok") else []

    result = {
        "generated_at": iso_utc(now),
        "lane": "daily_review_tasks",
        "recently_closed_after": iso_utc(recently_closed_after_dt),
        "stale_before": iso_utc(stale_before_dt),
        "ok": collected.get("ok", False),
        "error": collected.get("error"),
        "counts": {
            "total": len(items),
        },
        "buckets": bucket_daily(items, stale_before_dt),
    }
    result["counts"].update({k: len(v) for k, v in result["buckets"].items()})
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
