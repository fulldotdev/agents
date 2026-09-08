"""Durable triage handoff. JSON + flock; external writes still need reconciliation."""

import copy
import fcntl
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import incremental
from common import iso_utc, parse_iso

REPORT_KINDS = {
    "task_created", "project_created", "company_created", "task_canceled", "task_done",
    "project_status_changed", "company_status_changed",
    "draft_created", "draft_updated", "t3_started", "t3_continued",
}
ACTION_KINDS = REPORT_KINDS | {"context_updated", "other"}


def now():
    return iso_utc(datetime.now(timezone.utc))


@contextmanager
def locked(path):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Another collector/queue command holds the state lock; retry later") from exc
        try:
            yield incremental.load(path)
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def claim(state, owner, previous_owner=None):
    if not owner or not owner.strip():
        raise ValueError("--owner must identify this single worker run")
    current = state.get("owner")
    if current and current != owner and current != previous_owner:
        raise ValueError(f"Queue owned by {current}; resume that worker or verify it stopped before an explicit takeover")
    state["owner"] = owner


def require_owner(state, owner):
    if not owner or state.get("owner") != owner:
        raise ValueError("Queue owner changed or missing; do not perform external actions")


def iter_items(lane, value):
    if lane in {"gmail", "calendar"}:
        for source in value.get("sources") or []:
            yield from source.get("items") or []
    elif lane == "work_context":
        for group in (value.get("lanes") or {}).values():
            yield from group.get("items") or []
    elif lane == "whatsapp":
        for chat in value.get("items") or []:
            for message in chat.get("messages") or []:
                yield {**{k: v for k, v in chat.items() if k != "messages"}, "messages": [message]}
    else:
        yield from value.get("items") or []


def event_signature(lane, item):
    if lane == "whatsapp":
        message = item["messages"][0]
        return incremental.stable_hash([item.get("chat_id"), message.get("id"), message.get("timestamp")])
    return incremental.item_signature(lane, item)


def stage(state, result, proposals):
    events = copy.deepcopy(state.get("backlog") or {})
    values = dict(result["groups"]["incoming"]["sources"])
    values["work_context"] = result["groups"].get("work_context") or {}
    for lane, value in values.items():
        for item in iter_items(lane, value):
            signature = event_signature(lane, item)
            if not signature:
                continue
            event_id = f"{lane}:{signature}"
            events.setdefault(event_id, {
                "lane": lane, "signature": signature, "item": item,
                "status": "pending", "actions": [],
            })
    record_failures(state, result, proposals)
    state["pending"] = {
        "id": uuid4().hex, "collected_at": now(), "result": result,
        "proposals": proposals, "events": events,
    }
    state["backlog"] = {}
    state["last_collected_at"] = now()
    return view(state)


def record_failures(state, result, proposals):
    failures = state.setdefault("failures", {})
    values = dict(result["groups"]["incoming"]["sources"])
    values["work_context"] = result["groups"].get("work_context") or {}
    for lane, value in values.items():
        if proposals.get(lane, {}).get("complete"):
            recovered = failures.pop(lane, None)
            if recovered:
                report = state.get("reports", {}).get(recovered["key"])
                if report and not report.get("reported_at"):
                    report["resolved_at"] = now()
            continue
        previous = failures.get(lane) or {"attempts": 0, "key": f"failure:{lane}:{uuid4().hex}"}
        previous.update(attempts=previous["attempts"] + 1, last_attempt_at=now(),
                        errors=value.get("errors") or [value.get("error") or "incomplete collection"])
        failures[lane] = previous


def view(state):
    batch = state.get("pending")
    result = copy.deepcopy(batch["result"]) if batch else {"ok": True}
    events = (batch or {}).get("events") or state.get("backlog") or {}
    action_keys = {key for event in events.values() for key in event.get("actions", [])}
    result["queue"] = {
        "owner": state.get("owner"), "batch_id": (batch or {}).get("id"),
        "events": events,
        "actions": {key: state.get("actions", {}).get(key) for key in action_keys},
        "pending_count": sum(event["status"] != "done" for event in events.values()),
        "reports": reports(state), "failures": state.get("failures", {}),
        "last_processed_at": state.get("last_processed_at"),
    }
    result["state_committed"] = bool(batch)
    return result


def reports(state):
    return [{"key": key, **report} for key, report in (state.get("reports") or {}).items() if not report.get("reported_at") and not report.get("resolved_at")]


def apply(state, owner, operations):
    """Apply a file of operations atomically; caller saves only after all validate."""
    require_owner(state, owner)
    if not isinstance(operations, list):
        raise ValueError("Decision file must contain a JSON array of operations")
    actions = state.setdefault("actions", {})
    events = (state.get("pending") or {}).get("events") or {}
    for op in operations:
        operation = op["op"]
        if operation == "report_failure":
            if op.get("event"):
                failure = events.get(op["event"])
                failure = {"attempts": failure.get("retry_attempts", 0), "key": failure.get("failure_key")} if failure and failure["status"] != "done" else None
            else:
                failure = state.get("failures", {}).get(op.get("lane"))
            if not failure or failure["attempts"] < 2 or not op.get("title"):
                raise ValueError("Failure reporting requires two failed collection/handling attempts and a practical fix")
            state.setdefault("reports", {}).setdefault(failure["key"], {
                "kind": "failed", "title": op["title"], "url": op.get("url"),
            })
            continue
        if operation == "cancel":
            action = actions.get(op["key"])
            if not action or action["status"] == "done" or not op.get("note") or not op.get("evidence"):
                raise ValueError("cancel requires an unexecuted intent and verified reason/evidence; reconcile uncertain writes first")
            action.update(status="cancelled", note=op["note"], evidence=op["evidence"], cancelled_at=now())
            continue
        if operation == "reported":
            report = state.get("reports", {}).get(op["key"])
            if report is None:
                raise ValueError("Unknown report key")
            report.setdefault("reported_at", now())
            continue
        if operation == "resolve":
            action = actions.get(op["key"])
            if not action or action["status"] == "cancelled" or not op.get("receipt"):
                raise ValueError("resolve requires an active prepared key and verified external receipt")
            if action["status"] == "done" and action["receipt"] != op["receipt"]:
                raise ValueError("Conflicting receipt; reconcile the external action first")
            if action["kind"] in REPORT_KINDS and not op.get("report") and op["key"] not in state.get("reports", {}):
                raise ValueError("Reportable action resolution requires report title and native URL")
            action.update(status="done", receipt=op["receipt"], resolved_at=now())
            if op.get("report"):
                if action["kind"] not in REPORT_KINDS:
                    raise ValueError("This action kind does not meet the reporting gate")
                report = op["report"]
                if not report.get("title") or not report.get("url"):
                    raise ValueError("A report requires title and native URL")
                state.setdefault("reports", {}).setdefault(op["key"], {
                    "kind": action["kind"], "title": report["title"], "url": report["url"],
                })
            continue
        event = events.get(op.get("event"))
        if event is None:
            raise ValueError("Unknown event in current pending batch")
        if operation == "prepare":
            if event["status"] == "done":
                raise ValueError("An acknowledged event cannot acquire new actions")
            key, kind, target = op["key"], op["kind"], op["target"]
            if kind not in ACTION_KINDS or not key or not target:
                raise ValueError("prepare requires stable key, supported kind and reconciliation target")
            existing = actions.get(key)
            if existing and (existing["kind"] != kind or existing["target"] != target):
                raise ValueError("Action key already has a different meaning")
            actions.setdefault(key, {"kind": kind, "target": target, "status": "prepared", "prepared_at": now()})
            if key not in event["actions"]:
                event["actions"].append(key)
        elif operation == "ack":
            if op.get("outcome") not in {"handled", "no_action"} or not op.get("note"):
                raise ValueError("ack requires handled/no_action outcome and decision note")
            if any(actions[key]["status"] not in {"done", "cancelled"} for key in event["actions"]):
                raise ValueError("Unresolved action intent; reconcile external state before acknowledgement")
            if op["outcome"] == "no_action" and any(actions[key]["status"] == "done" for key in event["actions"]):
                raise ValueError("An event with completed actions cannot be acknowledged as no_action")
            event.update(status="done", outcome=op["outcome"], note=op["note"], handled_at=now())
            state["last_processed_at"] = now()
            failure_report = state.get("reports", {}).get(event.get("failure_key"))
            if failure_report and not failure_report.get("reported_at"):
                failure_report["resolved_at"] = now()
        elif operation == "retry":
            if event["status"] == "done" or not op.get("note"):
                raise ValueError("retry requires an unfinished event and reason")
            batch_id = state["pending"]["id"]
            if event.get("last_retry_batch") != batch_id:
                event["retry_attempts"] = event.get("retry_attempts", 0) + 1
                event["last_retry_batch"] = batch_id
                event.setdefault("failure_key", f"failure:{op['event']}:{uuid4().hex}")
            event.update(status="retry", note=op["note"])
        else:
            raise ValueError(f"Unsupported queue operation: {operation}")


def finish(state, owner):
    require_owner(state, owner)
    batch = state.get("pending")
    if not batch:
        return
    events = batch["events"]
    # Deferred events retain their complete payload + action intents, while
    # independent lanes may move forward. Their lane cursor stays behind.
    state["backlog"] = {key: event for key, event in events.items() if event["status"] != "done"}
    for lane in set(batch["proposals"]) | {event["lane"] for event in events.values()}:
        proposal = batch["proposals"].get(lane, {})
        lane_events = [event for event in events.values() if event["lane"] == lane]
        completed = [event["signature"] for event in lane_events if event["status"] == "done"]
        previous = state.setdefault("lanes", {}).setdefault(lane, {"seen": []})
        seen = list(dict.fromkeys(previous.get("seen", []) + completed))
        previous["seen"] = seen[-incremental.MAX_SEEN_PER_LANE:]
        if proposal.get("complete") and all(event["status"] == "done" for event in lane_events):
            incremental.advance(state, lane, parse_iso(proposal["before"]), completed)
    state["last_finished_at"] = now()
    state["last_batch"] = {"id": batch["id"], "finished_at": now(), "handled": {
        key: {k: v for k, v in event.items() if k != "item"}
        for key, event in events.items() if event["status"] == "done"
    }}
    state.pop("pending")


def command(args):
    path = args.state_file or incremental.DEFAULT_STATE_FILE
    with locked(path) as state:
        if args.operation == "status":
            return view(state)
        operations = []
        if args.operation == "claim":
            claim(state, args.owner, args.previous_owner)
        else:
            require_owner(state, args.owner)
            if args.operation == "apply":
                operations = json.loads(Path(args.file).read_text())
                apply(state, args.owner, operations)
            elif args.operation == "finish":
                finish(state, args.owner)
            elif args.operation == "release":
                if state.get("pending"):
                    raise ValueError("Finish or defer the pending batch before releasing ownership")
                state.pop("owner", None)
            elif args.operation == "reports":
                return {"ok": True, "reports": reports(state)}
        incremental.save(state, path)
        events = (state.get("pending") or {}).get("events") or state.get("backlog") or {}
        return {"ok": True, "owner": state.get("owner"),
                "pending_count": sum(event["status"] != "done" for event in events.values()),
                "actions": {op["key"]: state.get("actions", {}).get(op["key"])
                            for op in operations if op.get("op") in {"prepare", "resolve", "cancel"}},
                "reports": reports(state)}
