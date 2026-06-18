#!/usr/bin/env python3
import argparse, json, os, re, subprocess
from datetime import datetime, time, timezone
from pathlib import Path

MAX_ITEMS = int(os.environ.get("PRODUCTIVE_HOURS_MAX_ITEMS", "300"))
DEFAULT_CALENDAR_ACCOUNTS = ["sil@full.dev", "silveltman@gmail.com"]
DEFAULT_AUTHOR = os.environ.get("PRODUCTIVE_HOURS_GIT_AUTHOR", "Sil")
PRODUCTIVE_CONFIG = Path(os.environ.get("PRODUCTIVE_IO_CONFIG", "~/.config/productive-io/config.env")).expanduser()

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr.strip()}")
    return p.stdout

def json_cmd(cmd, cwd=None):
    out = run(cmd, cwd=cwd)
    return json.loads(out) if out.strip() else None

def parse_iso(value):
    if not value:
        return None
    value = value.strip()
    if len(value) == 10 and "T" not in value:
        return datetime.combine(datetime.fromisoformat(value).date(), time.min, tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def iso_utc(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def window_from_args(after=None, before=None, require=True):
    a = parse_iso(after)
    b = parse_iso(before) or datetime.now(timezone.utc)
    if require and not a:
        raise ValueError("after is required")
    if a and b < a:
        raise ValueError("before must be on or after after")
    return a, b

def load_env_file(path):
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("'\"")
    return env

def productive_env():
    env = dict(os.environ)
    env.update({k: v for k, v in load_env_file(PRODUCTIVE_CONFIG).items() if k not in env})
    if not env.get("PRODUCTIVE_API_KEY") or not env.get("PRODUCTIVE_ORGANIZATION_ID"):
        raise RuntimeError("missing PRODUCTIVE_API_KEY or PRODUCTIVE_ORGANIZATION_ID")
    return env

def productive_headers(env):
    return [
        "-H", f"X-Auth-Token: {env['PRODUCTIVE_API_KEY']}",
        "-H", f"X-Organization-Id: {env['PRODUCTIVE_ORGANIZATION_ID']}",
        "-H", "Content-Type: application/vnd.api+json",
    ]

def strip_html(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()

def base_result(lane, mode, after_dt=None, before_dt=None):
    return {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": lane,
        "mode": mode,
        "after": iso_utc(after_dt) if after_dt else None,
        "before": iso_utc(before_dt) if before_dt else None,
        "ok": True,
        "errors": [],
        "items": [],
    }

def error_obj(source, exc):
    return {"source": source, "ok": False, "error": str(exc), "items": []}

def yaml_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or text.strip() != text or "\n" in text or re.search(r'[:#\[\]{},&*?!|>\'"%@`]', text):
        return json.dumps(text, ensure_ascii=False)
    return text

def yaml_lines(value, indent=0):
    space = "  " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{space}{yaml_scalar(key)}:")
                lines.extend(yaml_lines(item, indent + 1))
            elif isinstance(item, list):
                lines.append(f"{space}{yaml_scalar(key)}: []")
            elif isinstance(item, dict):
                lines.append(f"{space}{yaml_scalar(key)}: {{}}")
            else:
                lines.append(f"{space}{yaml_scalar(key)}: {yaml_scalar(item)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                first = True
                for key, child in item.items():
                    prefix = "- " if first else "  "
                    if isinstance(child, (dict, list)) and child:
                        lines.append(f"{space}{prefix}{yaml_scalar(key)}:")
                        lines.extend(yaml_lines(child, indent + 2))
                    else:
                        lines.append(f"{space}{prefix}{yaml_scalar(key)}: {yaml_scalar(child)}")
                    first = False
            else:
                lines.append(f"{space}- {yaml_scalar(item)}")
    return lines

def emit(result, pretty=False, output_format="json"):
    if output_format == "yaml":
        print("\n".join(yaml_lines(result)))
    else:
        print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))

def add_common_args(parser):
    parser.add_argument("--after", required=True)
    parser.add_argument("--before")
    parser.add_argument("--customer", default="Small Giants")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
