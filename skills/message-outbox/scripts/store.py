"""Small Notion block store. Notion is the only workflow state owner."""
import json
import subprocess
from urllib.parse import urlencode

VERSION = "2026-03-11"


def api(path, method="GET", body=None):
    command = ["ntn", "api", "v1/" + path, "-X", method, "--notion-version", VERSION]
    if body is not None:
        command += ["-d", json.dumps(body, ensure_ascii=False)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError(f"Notion {method} {path}: {result.stderr[:500]}")
    value = json.loads(result.stdout)
    if value.get("object") == "error":
        raise RuntimeError(value.get("message", "Notion error"))
    return value


def query(source, filters=None):
    rows, cursor = [], None
    while True:
        payload = {"page_size": 100}
        if filters:
            payload["filter"] = filters
        if cursor:
            payload["start_cursor"] = cursor
        value = api(f"data_sources/{source}/query", "POST", payload)
        rows.extend(value["results"])
        if not value.get("has_more"):
            return rows
        following = value.get("next_cursor")
        if not following or following == cursor:
            raise RuntimeError("Notion pagination did not advance")
        cursor = following


def children(parent):
    rows, cursor = [], None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        value = api(f"blocks/{parent}/children?{urlencode(params)}")
        rows.extend(value["results"])
        if not value.get("has_more"):
            return rows
        following = value.get("next_cursor")
        if not following or following == cursor:
            raise RuntimeError("Block pagination did not advance")
        cursor = following


def rich(text):
    return [{"type": "text", "text": {"content": text[i:i + 1900]}} for i in range(0, len(text), 1900)]


def block(kind, text, **fields):
    return {"object": "block", "type": kind, kind: {"rich_text": rich(text), **fields}}


def plain(value):
    return "".join(x.get("plain_text", x.get("text", {}).get("content", "")) for x in value[value["type"]].get("rich_text", []))


def append(parent, blocks):
    return api(f"blocks/{parent}/children", "PATCH", {"children": blocks})["results"]


def update(identifier, kind, text, **fields):
    return api(f"blocks/{identifier}", "PATCH", {kind: {"rich_text": rich(text), **fields}})


def load(identifier):
    rows = children(identifier)
    if len(rows) != 3 or [r["type"] for r in rows] != ["paragraph", "code", "code"]:
        raise ValueError("Unexpected update layout; repair before proceeding")
    value = json.loads(plain(rows[2]))
    value["text"] = plain(rows[1])
    return value


def save(identifier, value):
    rows = children(identifier)
    metadata = {k: v for k, v in value.items() if k != "text"}
    update(rows[2]["id"], "code", json.dumps(metadata, ensure_ascii=False), language="json")
    update(rows[1]["id"], "code", value.get("text", ""), language="plain text")
    update(rows[0]["id"], "paragraph", summary(value))
    if load(identifier) != value:
        raise RuntimeError("Notion readback mismatch")


def summary(value):
    if value["kind"] == "batch":
        return f"Week {value['week']} · review in Telegram Planning · {len(value['items'])} updates"
    destination = value["destination"]
    return f"{value['status']} · versie {value['revision']} · {destination['channel']} · {destination['label']} · gepland {value['send_at']}"


def create(parent, title, value):
    metadata = {k: v for k, v in value.items() if k != "text"}
    rows = append(parent, [block("toggle", title, children=[
        block("paragraph", summary(value)),
        block("code", value.get("text", ""), language="plain text"),
        block("code", json.dumps(metadata, ensure_ascii=False), language="json"),
    ])])
    return rows[0]["id"]
