#!/usr/bin/env python3
"""Compact Codex app thread lane for work triage.

Reads local Codex SQLite state and returns a project/thread index only. It does
not read rollout JSONL conversation bodies unless a specific thread is requested.
"""

import argparse
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from common import add_common_args, base_result, compact_text, emit, iso_utc, parse_iso, window_from_args

CODEX_DIR = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
STATE_DB = Path(os.environ.get("CODEX_STATE_DB", CODEX_DIR / "state_5.sqlite")).expanduser()
GOALS_DB = Path(os.environ.get("CODEX_GOALS_DB", CODEX_DIR / "goals_1.sqlite")).expanduser()
DEFAULT_LIMIT = int(os.environ.get("TRIAGE_CODEX_LIMIT", "80"))
DEFAULT_DETAIL_EVENTS = int(os.environ.get("TRIAGE_CODEX_DETAIL_EVENTS", "80"))


def dt_from_epoch(value):
    if value is None:
        return None
    try:
        # Codex stores both seconds and ms in different columns.
        value = int(value)
        if value > 10_000_000_000:
            value = value / 1000
        return datetime.fromtimestamp(value, timezone.utc)
    except Exception:
        return None


def short_hash(value):
    if not value:
        return None
    return str(value)[:12]


def project_name(cwd, git_origin_url):
    if git_origin_url:
        text = git_origin_url.rstrip("/")
        text = text.split(":")[-1] if ":" in text and "/" not in text.split(":")[-1] else text
        name = text.rsplit("/", 1)[-1]
        return re.sub(r"\.git$", "", name) or None
    if cwd:
        p = Path(cwd)
        parts = [x for x in p.parts if x]
        if len(parts) >= 3 and parts[-3:-1] == ["Documents", "Codex"]:
            return parts[-1]
        return p.name or str(p)
    return "unknown"


def description(row):
    for key in ("title", "preview", "first_user_message"):
        value = (row.get(key) or "").strip()
        if value:
            return compact_text(" ".join(value.split()), 280)
    return None


def open_state():
    if not STATE_DB.exists():
        raise FileNotFoundError(f"Codex state DB not found: {STATE_DB}")
    con = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def load_goals(thread_ids):
    if not GOALS_DB.exists() or not thread_ids:
        return {}
    placeholders = ",".join("?" for _ in thread_ids)
    con = sqlite3.connect(f"file:{GOALS_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            f"""
            select thread_id, objective, status, updated_at_ms
            from thread_goals
            where thread_id in ({placeholders})
            order by updated_at_ms desc
            """,
            list(thread_ids),
        ).fetchall()
    finally:
        con.close()
    out = defaultdict(list)
    for r in rows:
        out[r["thread_id"]].append({
            "status": r["status"],
            "objective": compact_text(" ".join((r["objective"] or "").split()), 180),
            "updated_at": iso_utc(dt_from_epoch(r["updated_at_ms"])) if r["updated_at_ms"] else None,
        })
    return dict(out)


def load_spawn_edges(con):
    children = defaultdict(list)
    parents = {}
    for r in con.execute("select parent_thread_id, child_thread_id, status from thread_spawn_edges"):
        children[r["parent_thread_id"]].append({"thread_id": r["child_thread_id"], "status": r["status"]})
        parents[r["child_thread_id"]] = {"thread_id": r["parent_thread_id"], "status": r["status"]}
    return children, parents


def query_threads(after_dt=None, before_dt=None, include_archived=True, limit=DEFAULT_LIMIT, project=None, query=None):
    con = open_state()
    try:
        children, parents = load_spawn_edges(con)
        where = []
        params = []
        if after_dt:
            where.append("coalesce(recency_at, updated_at, created_at) >= ?")
            params.append(int(after_dt.timestamp()))
        if before_dt:
            where.append("coalesce(recency_at, updated_at, created_at) < ?")
            params.append(int(before_dt.timestamp()))
        if not include_archived:
            where.append("coalesce(archived, 0) = 0")
        if query:
            like = f"%{query}%"
            where.append("(title like ? or preview like ? or first_user_message like ? or cwd like ? or git_origin_url like ?)")
            params.extend([like] * 5)
        sql = """
            select id, rollout_path, created_at, updated_at, recency_at, source, thread_source,
                   model_provider, cwd, title, tokens_used, has_user_event, archived,
                   archived_at, git_sha, git_branch, git_origin_url, first_user_message,
                   agent_nickname, agent_role, model, preview
            from threads
        """
        if where:
            sql += " where " + " and ".join(where)
        sql += " order by coalesce(recency_at, updated_at, created_at) desc limit ?"
        params.append(limit)
        rows = [dict(x) for x in con.execute(sql, params).fetchall()]
    finally:
        con.close()

    goals = load_goals([r["id"] for r in rows])
    items = []
    for r in rows:
        proj = project_name(r.get("cwd"), r.get("git_origin_url"))
        if project and project.lower() not in (proj or "").lower() and project.lower() not in (r.get("cwd") or "").lower():
            continue
        updated = dt_from_epoch(r.get("recency_at") or r.get("updated_at") or r.get("created_at"))
        created = dt_from_epoch(r.get("created_at"))
        rollout_path = r.get("rollout_path")
        items.append({
            "project": proj,
            "thread_id": r.get("id"),
            "description": description(r),
            "updated_at": iso_utc(updated) if updated else None,
            "created_at": iso_utc(created) if created else None,
            "cwd": r.get("cwd"),
            "git": {
                "branch": r.get("git_branch"),
                "origin_url": r.get("git_origin_url"),
                "sha": short_hash(r.get("git_sha")),
            },
            "state": {
                "archived": bool(r.get("archived")),
                "source": r.get("source"),
                "thread_source": r.get("thread_source"),
                "has_user_event": bool(r.get("has_user_event")),
                "tokens_used": r.get("tokens_used"),
            },
            "goals": goals.get(r.get("id"), [])[:3],
            "spawned": {
                "parent": parents.get(r.get("id")),
                "children": children.get(r.get("id"), [])[:5],
            },
            "reference": {
                "rollout_path": rollout_path if rollout_path and Path(str(rollout_path)).exists() else None,
                "deep_read_hint": f"collect.py source codex --thread-id {r.get('id')} --format yaml",
            },
        })
    return items


def event_text(payload):
    if not isinstance(payload, dict):
        return None
    typ = payload.get("type")
    if typ == "message":
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            return None
        parts = []
        for c in payload.get("content") or []:
            if isinstance(c, dict) and c.get("type") in {"input_text", "output_text", "text"}:
                parts.append(c.get("text") or "")
        text = "\n".join(x for x in parts if x).strip()
        if not text:
            return None
        if text.startswith("# AGENTS.md instructions") or text.startswith("<permissions instructions>") or text.startswith("<app-context>"):
            return None
        return {"role": role, "text": compact_text(text, 1200)}
    if typ == "function_call":
        name = payload.get("name")
        return {"role": typ, "text": compact_text(str(name), 240)} if name else None
    return None


def read_thread(thread_id, max_events=DEFAULT_DETAIL_EVENTS):
    con = open_state()
    try:
        row = con.execute("select * from threads where id = ?", (thread_id,)).fetchone()
        children, parents = load_spawn_edges(con)
    finally:
        con.close()
    if not row:
        raise ValueError(f"Codex thread not found: {thread_id}")
    r = dict(row)
    proj = project_name(r.get("cwd"), r.get("git_origin_url"))
    updated = dt_from_epoch(r.get("recency_at") or r.get("updated_at") or r.get("created_at"))
    created = dt_from_epoch(r.get("created_at"))
    summary = {
        "project": proj,
        "thread_id": r.get("id"),
        "description": description(r),
        "updated_at": iso_utc(updated) if updated else None,
        "created_at": iso_utc(created) if created else None,
        "cwd": r.get("cwd"),
        "git": {"branch": r.get("git_branch"), "origin_url": r.get("git_origin_url"), "sha": short_hash(r.get("git_sha"))},
        "state": {"archived": bool(r.get("archived")), "source": r.get("source"), "thread_source": r.get("thread_source"), "has_user_event": bool(r.get("has_user_event")), "tokens_used": r.get("tokens_used")},
        "goals": load_goals([thread_id]).get(thread_id, [])[:3],
        "spawned": {"parent": parents.get(thread_id), "children": children.get(thread_id, [])[:5]},
        "reference": {"rollout_path": r.get("rollout_path") if r.get("rollout_path") and Path(str(r.get("rollout_path"))).exists() else None},
    }
    path = r.get("rollout_path")
    events = []
    if path and Path(path).exists():
        import json
        for line in Path(path).open(errors="replace"):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") != "response_item":
                continue
            text = event_text(obj.get("payload"))
            if text:
                text["timestamp"] = obj.get("timestamp")
                events.append(text)
            if len(events) >= max_events:
                break
    summary["detail"] = {"events_returned": len(events), "events": events}
    return summary


def group_by_project(items):
    grouped = defaultdict(list)
    for item in items:
        grouped[item.get("project") or "unknown"].append(item)
    return [{"project": k, "threads": v} for k, v in sorted(grouped.items(), key=lambda kv: kv[0].lower())]


def collect(after_dt=None, before_dt=None, include_archived=True, limit=DEFAULT_LIMIT, project=None, query=None, thread_id=None, detail_events=DEFAULT_DETAIL_EVENTS):
    r = base_result("codex", "compact_project_thread_index", after_dt, before_dt)
    r["codex_state_db"] = str(STATE_DB)
    try:
        if thread_id:
            r["mode"] = "thread_detail"
            r["items"] = [read_thread(thread_id, detail_events)]
        else:
            items = query_threads(after_dt, before_dt, include_archived, limit, project, query)
            r["projects"] = group_by_project(items)
            r["items"] = []
            r["count"] = len(items)
            r["note"] = "Compact project index only; items is intentionally empty to avoid duplicate output. Use projects[].threads or thread_id/deep_read_hint when a thread changes a triage decision."
    except Exception as exc:
        r["ok"] = False
        r["errors"].append({"source": "codex", "ok": False, "error": str(exc), "items": []})
    return r


def main():
    p = argparse.ArgumentParser()
    add_common_args(p)
    p.add_argument("--include-archived", action="store_true", default=False, help="include archived threads")
    p.add_argument("--all", action="store_true", help="ignore time window")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p.add_argument("--project", help="filter by derived project name or cwd substring")
    p.add_argument("--query", help="filter by title/preview/first user message/cwd/git origin")
    p.add_argument("--thread-id", help="return compact detail for one thread by reading its rollout JSONL")
    p.add_argument("--detail-events", type=int, default=DEFAULT_DETAIL_EVENTS)
    args = p.parse_args()
    a, b = (None, None) if args.all or args.thread_id else window_from_args(args.after, args.before)
    r = collect(a, b, args.include_archived, args.limit, args.project, args.query, args.thread_id, args.detail_events)
    emit(r, args.pretty, args.format)


if __name__ == "__main__":
    main()
