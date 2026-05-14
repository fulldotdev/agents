#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime, time, timedelta, timezone
from pathlib import Path


def _path_from_env(name, default):
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


CONFIG_PATH = _path_from_env("TRIAGE_CONFIG_PATH", Path.home() / ".config" / "triage" / "config.json")
STATE_DIR = _path_from_env("TRIAGE_STATE_DIR", Path.cwd() / "state" / "triage")
RUN_LOG_DIR = STATE_DIR / "runs"
ATTACHMENTS_DIR = STATE_DIR / "attachments"
CHECKPOINT_PATH = _path_from_env("TRIAGE_CHECKPOINT_PATH", STATE_DIR / "checkpoint.json")
DEFAULT_GMAIL_ACCOUNTS = [
    "sil@full.dev",
    "silveltman@gmail.com",
    "sil@smallgiants.nl",
]
MAX_ITEMS_PER_LANE = 200
SLACK_SURROUNDING_LIMIT = 2
SLACK_THREAD_REPLY_LIMIT = 50
SLACK_SENT_CONTEXT_LIMIT = 12
NOTION_MEETINGS_DATA_SOURCE_ID = "1cb5979e-268c-808d-888d-000bfa3a527c"
NOTION_TASKS_DATA_SOURCE_ID = "1cb5979e-268c-80e9-bd7d-000b00ac4424"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_config():
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())


def iso_utc(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value):
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    return datetime.fromisoformat(v).astimezone(timezone.utc)


def parse_dateish(value):
    v = value.strip()
    if "T" not in v and len(v) == 10:
        return datetime.combine(datetime.fromisoformat(v).date(), time.min, tzinfo=timezone.utc)
    return parse_iso(v)


def day_bounds_utc(after_value=None, before_value=None, default_before=None, require_after=False):
    after_dt = parse_dateish(after_value) if after_value else None
    if before_value:
        before_base = parse_dateish(before_value)
    else:
        before_base = default_before or datetime.now(timezone.utc)
    before_day_start = datetime.combine(before_base.date(), time.min, tzinfo=timezone.utc)
    before_dt = before_day_start + timedelta(days=1)
    if require_after and after_dt is None:
        raise ValueError("after is required")
    if after_dt is not None and before_dt < after_dt:
        raise ValueError("before must be on or after after")
    return after_dt, before_dt


def parse_window(after_value=None, before_value=None, default_after=None, default_before=None, require_after=False):
    after_dt = parse_dateish(after_value) if after_value else default_after
    before_dt = parse_dateish(before_value) if before_value else default_before or datetime.now(timezone.utc)
    if require_after and after_dt is None:
        raise ValueError("after is required")
    if after_dt is not None and before_dt < after_dt:
        raise ValueError("before must be on or after after")
    return after_dt, before_dt


def filename_time_tag(value):
    return value.replace(":", "").replace("+00:00", "Z")


def notion_key():
    notion_key_path = Path.home() / ".config" / "notion" / "api_key"
    if not notion_key_path.exists():
        return None
    return notion_key_path.read_text().strip()


def compact_text(value, limit=4000):
    text = (value or "").replace("\r", "")
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def json_cmd(cmd):
    return json.loads(run(cmd))
