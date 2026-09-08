#!/usr/bin/env python3
"""Notion-owned weekly drafts, authentic Planning approvals and send claims."""
import argparse
import fcntl
import hashlib
import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import store

CHAT = "-5475360719"
SIL = "8491875812"
TZ = ZoneInfo("Europe/Amsterdam")
DB = Path.home() / ".hermes/state.db"
SPRINTS = "3555979e-268c-807b-bdb4-000b86b48f90"
TERMINAL = {"Verzonden", "Bezig met verzenden", "Verzending controleren"}


def now():
    return datetime.now(timezone.utc)


def stamp():
    return now().isoformat()


def digest(value):
    payload = {key: value[key] for key in ("text", "destination", "send_at", "project", "revision")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def link(project, section):
    return f"https://www.notion.so/{project.replace('-', '')}#{section.replace('-', '')}"


def week_date(value):
    date = datetime.strptime(value, "%Y-%m-%d").date()
    if date.weekday() != 0:
        raise ValueError("Week must be a Monday date")
    return date


def batches(week=None):
    for sprint in store.query(SPRINTS):
        dates = sprint.get("properties", {}).get("Dates", {}).get("date")
        if week and dates and not dates["start"][:10] <= week <= (dates.get("end") or dates["start"])[:10]:
            continue
        for child in store.children(sprint["id"]):
            if child["type"] == "toggle" and store.plain(child).startswith("Weekupdates · "):
                value = store.load(child["id"])
                if value.get("kind") == "batch":
                    yield child["id"], value


def init(sprint, week):
    week_date(week)
    title = f"Weekupdates · {week}"
    for child in store.children(sprint):
        if child["type"] == "toggle" and store.plain(child) == title:
            return {"batch": child["id"], **store.load(child["id"])}
    value = {"kind": "batch", "week": week, "sprint": sprint, "items": [], "reports": [], "last_message": 0, "text": "Nog geen concepten gepubliceerd."}
    return {"batch": store.create(sprint, title, value), **value}


def validate_destination(destination):
    channel = destination.get("channel")
    required = {"slack": ("workspace", "channel_id"), "gmail": ("account", "to", "subject"), "whatsapp": ("jid",)}
    if channel not in required or not destination.get("label"):
        raise ValueError("Destination requires supported channel and readable label")
    if any(not destination.get(key) for key in required[channel]):
        raise ValueError(f"Destination requires {required[channel]}")
    if channel == "whatsapp" and "@" not in destination["jid"]:
        raise ValueError("Use a verified WhatsApp JID")
    if channel == "gmail" and not isinstance(destination["to"], list):
        raise ValueError("Gmail to must be an exact address list")


def draft(batch_id, incoming):
    batch = store.load(batch_id)
    validate_destination(incoming["destination"])
    if not incoming.get("text", "").strip() or not incoming.get("sources"):
        raise ValueError("A draft needs final text and source locators")
    date = week_date(batch["week"])
    scheduled = datetime.combine(date, datetime.min.time(), TZ).replace(hour=7).isoformat()
    existing = next((item for item in batch["items"] if item["project"] == incoming["project"]), None)
    recovered = False
    if not existing:
        candidates = [child for child in store.children(incoming["project"])
                      if child["type"] == "toggle" and store.plain(child) == f"Klantupdate · {batch['week']}"]
        if len(candidates) > 1:
            raise ValueError("Several project updates exist for this week; resolve the duplicate before continuing")
        if candidates:
            existing = {"number": len(batch["items"]) + 1, "project": incoming["project"],
                        "section": candidates[0]["id"], "name": incoming["name"]}
            batch["items"].append(existing)
            recovered = True
    previous = store.load(existing["section"]) if existing else None
    if previous and (previous.get("kind") != "update" or previous.get("project") != incoming["project"]):
        raise ValueError("Existing project section does not match this update")
    if previous and previous["text"] == incoming["text"] and previous["destination"] == incoming["destination"] and previous["send_at"] == scheduled and digest(previous) == previous["digest"]:
        if recovered or existing.get("digest") != previous["digest"]:
            existing["digest"] = previous["digest"]
            existing.pop("published_at", None)
            store.save(batch_id, batch)
        return {"number": existing["number"], "section": existing["section"], "url": link(previous["project"], existing["section"]), "unchanged": True, **previous}
    if previous and previous["status"] in TERMINAL:
        raise ValueError("A sent or uncertain send cannot be replaced")
    revision = previous["revision"] + 1 if previous else 1
    value = {"kind": "update", "project": incoming["project"], "name": incoming["name"], "revision": revision,
             "send_at": scheduled, "text": incoming["text"], "destination": incoming["destination"],
             "sources": incoming["sources"], "status": "Concept", "approval": None, "created_at": stamp()}
    value["digest"] = digest(value)
    if existing:
        store.save(existing["section"], value)
    else:
        section = store.create(value["project"], f"Klantupdate · {batch['week']}", value)
        existing = {"number": len(batch["items"]) + 1, "project": value["project"], "section": section, "name": value["name"]}
        batch["items"].append(existing)
    existing["digest"] = value["digest"]
    existing.pop("published_at", None)
    store.save(batch_id, batch)
    return {"number": existing["number"], "section": existing["section"], "url": link(value["project"], existing["section"]), **value}


def publish(batch_id, notes):
    batch = store.load(batch_id)
    if batch.get("pending_report"):
        raise ValueError("Prior publication is uncertain; inspect Planning and recover its receipt before republishing")
    header = f"Weekupdates {batch['week']} · review {len(batch['reports']) + 1} klaar voor review."
    lines = [header]
    snapshot = {}
    for item in batch["items"]:
        value = store.load(item["section"])
        if digest(value) != item["digest"]:
            raise ValueError(f"Update {item['number']} changed outside the draft command")
        lines.append(f"{item['number']}. {value['name']} · {value['status']} · {value['destination']['label']}\n{link(value['project'], item['section'])}")
        snapshot[str(item["number"])] = value["digest"]
    lines += [notes.strip(), 'Antwoord bijvoorbeeld: "keur 1 en 3 goed", "alles akkoord" of "sla 2 over". Aanpassingen kunnen hier ook.']
    message = "\n\n".join(line for line in lines if line)
    # One review list must be one delivered message. Telegram has a 4096 limit.
    if len(message) > 3900:
        raise ValueError("Review list exceeds one Telegram message; shorten names/notes")
    pending_at = stamp()
    batch["text"] = message
    batch["pending_report"] = {"at": pending_at, "snapshot": snapshot, "header": header}
    store.save(batch_id, batch)
    # This helper owns the review send; the cron ends with [SILENT].
    send_env = {key: value for key, value in os.environ.items() if key not in {
        "HERMES_CRON_AUTO_DELIVER_PLATFORM", "HERMES_CRON_AUTO_DELIVER_CHAT_ID", "HERMES_CRON_AUTO_DELIVER_THREAD_ID"}}
    result = subprocess.run(["hermes", "send", "--to", "telegram:" + CHAT, "--json"], input=message, text=True, capture_output=True, timeout=90, env=send_env)
    if result.returncode:
        raise RuntimeError("Planning delivery uncertain; inspect chat before publishing again")
    receipt = json.loads(result.stdout)
    if receipt.get("error") or receipt.get("success") is not True or not receipt.get("message_id") or str(receipt.get("chat_id")) != CHAT:
        raise RuntimeError("Planning delivery failed")
    at = stamp()
    batch["reports"].append({"at": pending_at, "confirmed_at": at, "header": header, "snapshot": snapshot, "receipt": receipt})
    batch.pop("pending_report", None)
    for item in batch["items"]:
        item["published_at"] = at
    store.save(batch_id, batch)
    return {"published": True, "receipt": receipt, "batch": batch_id}


def messages(after, last=0):
    # Existing Hermes conversation history, read only. No outbox database.
    with sqlite3.connect(f"file:{DB}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT m.id, m.session_id, m.content, m.timestamp, s.chat_id, s.user_id
            FROM messages m JOIN sessions s ON s.id=m.session_id
            WHERE s.source='telegram' AND CAST(s.chat_id AS TEXT)=?
              AND CAST(s.user_id AS TEXT)=? AND m.role='user'
              AND m.timestamp>=? AND m.id>? ORDER BY m.id
        """, (CHAT, SIL, after, last)).fetchall()
    return [dict(row) for row in rows]


def parse(text, numbers):
    text = text.strip().lower().rstrip(".! ")
    if text in {"alles akkoord", "alles goedgekeurd", "keur alles goed", "alles goed"}:
        return {n: "Goedgekeurd" for n in numbers}
    if text in {"niets versturen", "niks versturen", "sla alles over", "alles overslaan"}:
        return {n: "Overslaan" for n in numbers}
    if text in {"thanks", "bedankt", "dankje", "dank je", "top", "nice", "👍"}:
        return {}
    selected = r"(\d+(?:(?:\s*,\s*|\s+en\s+)\d+)*)"
    patterns = [(rf"keur {selected} goed", "Goedgekeurd"), (rf"(?:akkoord|goedkeuren) {selected}", "Goedgekeurd"),
                (rf"{selected}\s*(?:ok|akkoord|goed|goedgekeurd)", "Goedgekeurd"),
                (rf"sla {selected} over", "Overslaan"), (rf"{selected}\s*(?:overslaan|niet versturen|intrekken)", "Overslaan")]
    decisions = {}
    for line in text.splitlines():
        for pattern, status in patterns:
            match = re.fullmatch(pattern, line.strip().rstrip(".! "))
            if match:
                selected_numbers = [int(x) for x in re.findall(r"\d+", match.group(1))]
                if any(n not in numbers for n in selected_numbers):
                    return None
                decisions.update({n: status for n in selected_numbers})
                break
        else:
            # A request about one numbered draft must not revoke the others.
            target = re.match(r"(?:pas\s+|wijzig\s+|update\s+|nummer\s+|bij\s+)?(\d+)\b", line.strip())
            if target and int(target.group(1)) in numbers:
                decisions[int(target.group(1))] = "Review nodig"
            else:
                return None
    return decisions


def reconcile(batch_id):
    batch = store.load(batch_id)
    if not batch["reports"] or batch.get("pending_report"):
        return {"batch": batch_id, "changed": [], "attention": "No confirmed review publication"}
    first = datetime.fromisoformat(batch["reports"][0]["at"]).timestamp()
    changes = []
    for row in messages(first, batch["last_message"]):
        report, choices = review_decisions(row, batch)
        if report is None:
            continue
        evidence = {"hermes_message": row["id"], "session": row["session_id"], "chat": CHAT, "user": SIL,
                    "at": datetime.fromtimestamp(row["timestamp"], timezone.utc).isoformat(), "text": row["content"]}
        for item in batch["items"]:
            if str(item["number"]) not in report["snapshot"]:
                continue
            value = store.load(item["section"])
            if value["status"] in TERMINAL:
                continue
            decision = choices.get(item["number"]) if choices is not None else "Review nodig"
            if not decision:
                continue
            matching = report["snapshot"].get(str(item["number"])) == digest(value) == item["digest"]
            if decision == "Goedgekeurd" and not matching:
                decision = "Review nodig"
            value["status"] = decision
            value["approval"] = {**evidence, "digest": digest(value)} if decision == "Goedgekeurd" else None
            value["last_feedback"] = evidence
            store.save(item["section"], value)
            changes.append({"number": item["number"], "status": decision, "message": row["id"]})
        batch["last_message"] = row["id"]
        store.save(batch_id, batch)
    return {"batch": batch_id, "changed": changes, "items": [{**item, "update": store.load(item["section"])} for item in batch["items"]]}


def review_decisions(row, batch):
    reports = [r for r in batch["reports"] if datetime.fromisoformat(r["at"]).timestamp() <= row["timestamp"]]
    if not reports:
        return None, None
    report, text = reports[-1], row["content"]
    quote = re.fullmatch(r'\[Replying to(?: your previous message)?: "(.*?)"\]\n\n(.*)', text, re.DOTALL)
    if quote:
        header = quote.group(1).splitlines()[0] if quote.group(1) else ""
        matched = [r for r in reports if r.get("header") == header]
        if len(matched) != 1:
            return report, None
        report, text = matched[0], quote.group(2)
    elif row["timestamp"] < datetime.fromisoformat(report.get("confirmed_at", report["at"])).timestamp():
        # A plain reply during delivery could concern the previous review.
        # Keep it for review instead of dropping it or assuming approval.
        return report, None
    return report, parse(text, [int(n) for n in report["snapshot"]])


def check_approval(value, batch):
    approval = value.get("approval")
    if value["status"] != "Goedgekeurd" or not approval or digest(value) != approval["digest"] or value["digest"] != digest(value):
        raise ValueError("Exact current draft has no valid approval")
    records = messages(datetime.fromisoformat(approval["at"]).timestamp() - 1, approval["hermes_message"] - 1)
    row = next((r for r in records if r["id"] == approval["hermes_message"]), None)
    if not row or row["content"] != approval["text"] or row["session_id"] != approval["session"]:
        raise ValueError("Original Sil approval cannot be verified")
    item = next(i for i in batch["items"] if i["project"] == value["project"])
    report, choices = review_decisions(row, batch)
    if not report or report["snapshot"].get(str(item["number"])) != digest(value):
        raise ValueError("Approval did not refer to this published version")
    if not choices or choices.get(item["number"]) != "Goedgekeurd":
        raise ValueError("Message does not approve this update")


def claim(batch_id, number, check):
    reconcile(batch_id)
    batch = store.load(batch_id)
    if batch.get("pending_report"):
        raise ValueError("Resolve uncertain review publication first")
    item = next(i for i in batch["items"] if i["number"] == number)
    value = store.load(item["section"])
    check_approval(value, batch)
    due = datetime.fromisoformat(value["send_at"])
    if not due <= now() <= due + timedelta(hours=5):
        raise ValueError("Send only Monday 07:00–12:00 Amsterdam; late delivery needs a new agreement")
    checked = datetime.fromisoformat(check["checked_at"])
    if not timedelta(0) <= now() - checked <= timedelta(minutes=10) or check.get("digest") != digest(value) or check.get("unchanged") is not True or not check.get("sources"):
        raise ValueError("A fresh source check for this exact draft is required")
    value.update(status="Bezig met verzenden", claim={"at": stamp(), "digest": digest(value), "check": check})
    store.save(item["section"], value)
    return {"section": item["section"], "send_exactly": {"text": value["text"], "destination": value["destination"]}, "digest": digest(value)}


def finish(section, receipt):
    value = store.load(section)
    if value["status"] == "Verzonden" and value.get("receipt") == receipt:
        store.save(section, value)
        return value
    if value["status"] not in {"Bezig met verzenden", "Verzending controleren"} or not value.get("claim"):
        raise ValueError("No pending send claim")
    if digest(value) != value["claim"]["digest"]:
        raise ValueError("Draft changed after the send claim; inspect the original send result before recording delivery")
    if receipt.get("digest") != value["claim"]["digest"] or receipt.get("channel") != value["destination"]["channel"] or not receipt.get("message_id") or not receipt.get("sent_at"):
        raise ValueError("Receipt requires exact digest, channel, native message_id and sent_at")
    value.update(status="Verzonden", receipt=receipt)
    store.save(section, value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["init", "draft", "publish", "recover-publication", "list", "discover", "reconcile", "claim", "receipt", "hold"])
    parser.add_argument("--batch")
    parser.add_argument("--sprint")
    parser.add_argument("--week")
    parser.add_argument("--section")
    parser.add_argument("--number", type=int)
    parser.add_argument("--file", help="JSON input; publish takes a plain-text cleanup note")
    args = parser.parse_args()
    lock = Path.home() / ".hermes/tmp/message-outbox.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        data = json.loads(Path(args.file).read_text()) if args.file and args.operation != "publish" else None
        if args.operation == "init":
            result = init(args.sprint, args.week)
        elif args.operation == "discover":
            result = [{"batch": identifier, **value} for identifier, value in batches(args.week) if not args.week or value["week"] == args.week]
        elif args.operation == "draft":
            result = draft(args.batch, data)
        elif args.operation == "publish":
            result = publish(args.batch, Path(args.file).read_text() if args.file else "")
        elif args.operation == "recover-publication":
            batch = store.load(args.batch)
            pending = batch["pending_report"]
            if str(data.get("chat_id")) != CHAT or not data.get("message_id") or not data.get("sent_at"):
                raise ValueError("Recovery needs the verified native message ID, chat and actual sent_at")
            at = datetime.fromisoformat(data["sent_at"])
            if not datetime.fromisoformat(pending["at"]) - timedelta(seconds=1) <= at <= now():
                raise ValueError("Receipt timestamp is outside the publication window")
            batch["reports"].append({"at": data["sent_at"], "header": pending.get("header"), "snapshot": pending["snapshot"], "receipt": data})
            batch.pop("pending_report")
            for item in batch["items"]:
                item["published_at"] = data["sent_at"]
            store.save(args.batch, batch)
            result = batch
        elif args.operation == "reconcile":
            result = reconcile(args.batch)
        elif args.operation == "list":
            batch = store.load(args.batch)
            result = {**batch, "items": [{**item, "update": store.load(item["section"])} for item in batch["items"]]}
        elif args.operation == "claim":
            result = claim(args.batch, args.number, data)
        elif args.operation == "receipt":
            result = finish(args.section, data)
        else:
            value = store.load(args.section)
            if value["status"] == "Verzonden":
                raise ValueError("A sent message cannot be held")
            value.update(status="Verzending controleren" if value.get("claim") else "Review nodig", approval=None, hold=data)
            store.save(args.section, value)
            result = value
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
