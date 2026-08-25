#!/usr/bin/env python3
# Slack collection for work-triage.
import argparse, json, os, shlex, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from common import MAX_ITEMS_PER_LANE, add_common_args, base_result, compact_text, emit, error_obj, window_from_args

SLACK_API_TIMEOUT_SECONDS = float(os.environ.get("SLACK_API_TIMEOUT_SECONDS", "8"))
SLACK_CONNECT_TIMEOUT_SECONDS = float(os.environ.get("SLACK_CONNECT_TIMEOUT_SECONDS", "3"))
SLACK_COLLECT_TIMEOUT_SECONDS = float(os.environ.get("SLACK_COLLECT_TIMEOUT_SECONDS", "45"))
SLACK_SEARCH_COUNT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_SEARCH_COUNT", "25")))
SLACK_ALL_SEARCH_COUNT = min(100, MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_ALL_SEARCH_COUNT", "100")))
SLACK_HISTORY_LIMIT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_HISTORY_LIMIT", "50")))
SLACK_CONVERSATION_LIMIT = min(200, int(os.environ.get("SLACK_CONVERSATION_LIMIT", "100")))
SLACK_REPLIES_LIMIT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_REPLIES_LIMIT", "50")))
SLACK_WORKERS = max(1, int(os.environ.get("SLACK_WORKERS", "4")))
SLACK_CONFIG_PATH = os.environ.get("SLACK_CONFIG_PATH")
SLACK_WORKSPACES_DIR = os.environ.get("SLACK_WORKSPACES_DIR") or str(Path.home() / ".config" / "slack" / "workspaces")
_deadline = None
_token_value = None
_users = {}
_workspace = {}

def user_display(user_id):
    user = _users.get(user_id) or {}
    profile = user.get("profile") or {}
    return (
        profile.get("display_name_normalized") or profile.get("display_name") or
        profile.get("real_name_normalized") or profile.get("real_name") or
        user.get("real_name") or user.get("name") or user_id
    )

def load_users():
    users, cursor = {}, None
    while True:
        params = {"limit": "200"}
        if cursor:
            params["cursor"] = cursor
        data = api("users.list", params)
        for user in data.get("members") or []:
            if isinstance(user, dict) and user.get("id"):
                users[user["id"]] = user
        cursor = (((data.get("response_metadata") or {}).get("next_cursor")) or "").strip()
        if not cursor:
            return users

def load_config_env(path):
    cfg = Path(path)
    if not cfg.exists():
        return {}
    values = {}
    for raw_line in cfg.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        try:
            value = shlex.split(raw_value, posix=True)[0] if raw_value.strip() else ""
        except ValueError:
            value = raw_value.strip().strip("'\"")
        values[key] = value
    return values

def workspace_configs(selected=None):
    if SLACK_CONFIG_PATH:
        path = Path(SLACK_CONFIG_PATH)
        configs = [{"slug": path.stem, "path": str(path), "values": load_config_env(path), "use_environment": True}]
    else:
        workspace_paths = sorted(Path(SLACK_WORKSPACES_DIR).glob("*.env"))
        configs = (
            [
                {"slug": path.stem, "path": str(path), "values": load_config_env(path), "use_environment": False}
                for path in workspace_paths
            ]
            if workspace_paths
            else [{"slug": "environment", "path": None, "values": {}, "use_environment": True}]
        )
    if selected:
        configs = [config for config in configs if config.get("slug") == selected]
        if not configs:
            raise ValueError(f"unknown Slack workspace: {selected}")
    return configs

def select_token(config):
    values = config.get("values") or {}
    for key in ("SLACK_USER_TOKEN", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN_READONLY"):
        candidates = [values.get(key)]
        if config.get("use_environment"):
            candidates.insert(0, os.environ.get(key))
        for value in candidates:
            if value and value.strip():
                return value.strip()
    raise RuntimeError(f"missing slack token for workspace {config.get('slug')}")

def triage_mode(config):
    values = config.get("values") or {}
    value = values.get("SLACK_TRIAGE_MODE")
    if config.get("use_environment"):
        value = os.environ.get("SLACK_TRIAGE_MODE") or value
    mode = (value or "signals").strip().lower()
    if mode not in {"signals", "all"}:
        raise ValueError(f"invalid SLACK_TRIAGE_MODE for workspace {config.get('slug')}: {mode}")
    return mode

def token():
    if not _token_value:
        raise RuntimeError("missing active slack token")
    return _token_value

def tag_item(item):
    if not isinstance(item, dict):
        return item
    item.update({key: value for key, value in _workspace.items() if value})
    for reply in item.get("thread_replies") or []:
        tag_item(reply)
    return item

def check_deadline():
    if _deadline and time.monotonic() > _deadline:
        raise TimeoutError(f"slack collector exceeded {SLACK_COLLECT_TIMEOUT_SECONDS:g}s")

def api(method, params=None):
    check_deadline()
    url = "https://slack.com/api/" + method + (("?" + urlencode(params)) if params else "")
    cmd = [
        "curl",
        "-sS",
        "--connect-timeout",
        str(SLACK_CONNECT_TIMEOUT_SECONDS),
        "--max-time",
        str(SLACK_API_TIMEOUT_SECONDS),
        "--config",
        "-",
        url,
    ]
    curl_config = f'header = "Authorization: Bearer {token()}"\n'
    for attempt in range(3):
        check_deadline()
        try:
            p = subprocess.run(
                cmd,
                input=curl_config,
                capture_output=True,
                text=True,
                timeout=SLACK_API_TIMEOUT_SECONDS + 2,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"slack {method} timed out after {SLACK_API_TIMEOUT_SECONDS:g}s") from exc
        if p.returncode:
            stderr = compact_text(p.stderr.strip(), 500)
            raise RuntimeError(f"slack {method} curl failed ({p.returncode}): {stderr}")
        try:
            data = json.loads(p.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"slack {method} returned invalid JSON") from exc
        if data.get("ok"):
            return data
        if data.get("error") == "ratelimited" and attempt < 2:
            time.sleep(min(2 ** attempt, 2))
            continue
        raise RuntimeError(f"slack {method} failed: {data.get('error','unknown error')}")

def in_window(msg,a,b):
    if not isinstance(msg, dict): return False
    try: ts = float(msg.get("ts") or 0)
    except Exception: return False
    return a.timestamp() <= ts < b.timestamp()
def permalink(ch, ts):
    try: return api("chat.getPermalink", {"channel": ch, "message_ts": ts}).get("permalink")
    except Exception: return None

def channel_id(msg):
    if not isinstance(msg, dict): return None
    ch = msg.get("channel")
    if isinstance(ch, dict): return ch.get("id")
    return ch if isinstance(ch, str) else None

def thread_root_ts(msg):
    if not isinstance(msg, dict): return None
    if msg.get("thread_ts"):
        return msg.get("thread_ts")
    permalink_url = msg.get("permalink") or ""
    if permalink_url:
        values = parse_qs(urlparse(permalink_url).query).get("thread_ts") or []
        if values:
            return values[0]
    return msg.get("ts")

def norm(msg, channel=None, channel_name=None, channel_type=None, after_dt=None, before_dt=None):
    if not isinstance(msg, dict): msg = {}
    msg_channel = msg.get("channel") if isinstance(msg.get("channel"), dict) else {}
    ch = channel or channel_id(msg)
    sender = msg.get("user")
    resolved_channel_name = channel_name or msg_channel.get("name")
    if resolved_channel_name in _users:
        resolved_channel_name = user_display(resolved_channel_name)
    resolved_channel_type = channel_type or ("im" if msg_channel.get("is_im") else "channel")
    return {"channel_id": ch, "channel_name": resolved_channel_name, "channel_type": resolved_channel_type, "ts": msg.get("ts"), "thread_ts": thread_root_ts(msg), "sender": sender, "sender_name": user_display(sender), "text": compact_text(msg.get("text"), 12000), "url": msg.get("permalink"), "files": msg.get("files") or [], "in_window": in_window(msg, after_dt, before_dt) if after_dt and before_dt else None}

def replies(ch, thread_ts, a, b, channel_name=None):
    if not ch or not thread_ts: return []
    messages = api("conversations.replies", {"channel": ch, "ts": thread_ts, "limit": str(SLACK_REPLIES_LIMIT)}).get("messages") or []
    return [
        norm(m, channel=ch, channel_name=channel_name, after_dt=a, before_dt=b)
        for m in messages
        if isinstance(m, dict) and (m.get("ts") == thread_ts or in_window(m, a, b))
    ]

def slack_search_messages(q):
    matches = (api("search.messages", {"query": q, "count": str(SLACK_SEARCH_COUNT), "sort": "timestamp", "sort_dir": "desc"}).get("messages") or {}).get("matches") or []
    return [m for m in matches if isinstance(m, dict)][:MAX_ITEMS_PER_LANE]

def search_date_bounds(a, b):
    return f"after:{(a.date() - timedelta(days=1)).isoformat()} before:{(b.date() + timedelta(days=1)).isoformat()}"

def search(q, a, b, filter_window=True, include_replies=True):
    matches = slack_search_messages(q)
    items = []
    for m in matches:
        item = norm(m, after_dt=a, before_dt=b); item["match_query"] = q
        item["thread_replies"] = replies(item["channel_id"], item["thread_ts"], a, b, item.get("channel_name")) if include_replies else []
        if not filter_window or item.get("in_window") or item["thread_replies"]:
            items.append(item)
    return items

def all_search(a, b):
    q = search_date_bounds(a, b)
    items, page = [], 1
    while len(items) < MAX_ITEMS_PER_LANE:
        messages = api("search.messages", {
            "query": q,
            "count": str(SLACK_ALL_SEARCH_COUNT),
            "page": str(page),
            "sort": "timestamp",
            "sort_dir": "desc",
        }).get("messages") or {}
        matches = [m for m in messages.get("matches") or [] if isinstance(m, dict)]
        for match in matches:
            if in_window(match, a, b):
                item = norm(match, after_dt=a, before_dt=b)
                item["match_query"] = "all_search"
                item["thread_replies"] = []
                items.append(item)
                if len(items) >= MAX_ITEMS_PER_LANE:
                    break
        paging = messages.get("paging") or messages.get("pagination") or {}
        pages = int(paging.get("pages") or paging.get("page_count") or 1)
        if not matches or page >= pages:
            break
        timestamps = [float(m.get("ts") or 0) for m in matches]
        if timestamps and min(timestamps) < a.timestamp():
            break
        page += 1
    return items

def list_conversations(types):
    channels, cursor = [], None
    while True:
        params = {"types": types, "exclude_archived": "true", "limit": str(SLACK_CONVERSATION_LIMIT)}
        if cursor:
            params["cursor"] = cursor
        data = api("conversations.list", params)
        channels.extend(ch for ch in data.get("channels") or [] if isinstance(ch, dict) and ch.get("id"))
        cursor = (((data.get("response_metadata") or {}).get("next_cursor")) or "").strip()
        if not cursor:
            return channels

def conversation_history(ch, a, b):
    items, cursor = [], None
    channel_type = "mpim" if ch.get("is_mpim") else "im" if ch.get("is_im") else "private_channel" if ch.get("is_private") else "public_channel"
    channel_name = ch.get("name") or (user_display(ch.get("user")) if channel_type == "im" else None)
    while len(items) < MAX_ITEMS_PER_LANE:
        params = {
            "channel": ch.get("id"),
            "oldest": str(a.timestamp()),
            "latest": str(b.timestamp()),
            "inclusive": "false",
            "limit": str(SLACK_HISTORY_LIMIT),
        }
        if cursor:
            params["cursor"] = cursor
        data = api("conversations.history", params)
        for message in data.get("messages") or []:
            if not isinstance(message, dict):
                continue
            item = norm(message, channel=ch.get("id"), channel_name=channel_name, channel_type=channel_type, after_dt=a, before_dt=b)
            item["match_query"] = "all_history"
            item["thread_replies"] = replies(ch.get("id"), item["thread_ts"], a, b, channel_name) if message.get("reply_count") else []
            items.append(item)
        cursor = (((data.get("response_metadata") or {}).get("next_cursor")) or "").strip()
        if not cursor:
            return items
    return items

def all_history(a, b):
    items = []
    channels = list_conversations("public_channel,private_channel,im,mpim")
    with ThreadPoolExecutor(max_workers=min(SLACK_WORKERS, max(1, len(channels)))) as executor:
        futures = [executor.submit(conversation_history, ch, a, b) for ch in channels]
        for future in as_completed(futures):
            try:
                items.extend(future.result())
            except Exception as exc:
                items.append({"ok": False, "query": "all_history", "error": str(exc)})
    return items

def deduplicate(items):
    result, seen = [], set()
    for item in items:
        if item.get("ok") is False:
            result.append(item)
            continue
        nested_keys = {
            (reply.get("channel_id"), reply.get("ts"))
            for reply in item.get("thread_replies") or []
            if reply.get("channel_id") and reply.get("ts")
        }
        key = (item.get("channel_id"), item.get("ts"))
        if key[0] and key[1] and key in seen:
            continue
        result.append(item)
        if key[0] and key[1]:
            seen.add(key)
        seen.update(nested_keys)
    return result

def dm_channel_history(ch, a, b, oldest, latest):
    items = []
    channel_type = "mpim" if ch.get("is_mpim") else "im"
    channel_name = ch.get("name") or (user_display(ch.get("user")) if channel_type == "im" else None)
    for m in api("conversations.history", {"channel": ch.get("id"), "oldest": oldest, "latest": latest, "inclusive": "false", "limit": str(SLACK_HISTORY_LIMIT)}).get("messages") or []:
        if not isinstance(m, dict): continue
        item = norm(m, channel=ch.get("id"), channel_name=channel_name, channel_type=channel_type, after_dt=a, before_dt=b)
        item["match_query"] = "dm_history"; item["thread_replies"] = replies(ch.get("id"), item["thread_ts"], a, b, channel_name) if m.get("reply_count") else []; items.append(item)
    return items

def dm_history(a,b):
    items, oldest, latest = [], str(a.timestamp()), str(b.timestamp())
    raw_channels = api("conversations.list", {"types": "im,mpim", "limit": str(SLACK_CONVERSATION_LIMIT)}).get("channels") or []
    channels = [ch for ch in raw_channels if isinstance(ch, dict) and ch.get("id")]
    with ThreadPoolExecutor(max_workers=min(SLACK_WORKERS, max(1, len(channels)))) as executor:
        futures = [executor.submit(dm_channel_history, ch, a, b, oldest, latest) for ch in channels]
        for future in as_completed(futures):
            try: items.extend(future.result())
            except Exception as exc: items.append({"ok": False, "query": "dm_history", "error": str(exc)})
    return items[:MAX_ITEMS_PER_LANE]

def collect_workspace(a,b,query,config):
    global _deadline, _token_value, _users, _workspace
    _deadline = time.monotonic() + SLACK_COLLECT_TIMEOUT_SECONDS
    _token_value = select_token(config)
    mode = triage_mode(config)
    _workspace = {
        "workspace_slug": config.get("slug"),
        "workspace_name": (config.get("values") or {}).get("SLACK_WORKSPACE_NAME") or config.get("slug"),
        "triage_mode": mode,
    }
    identity = api("auth.test")
    _workspace.update({
        "workspace_name": identity.get("team") or _workspace["workspace_name"],
        "workspace_id": identity.get("team_id"),
        "workspace_url": identity.get("url"),
    })
    _users = load_users()
    items = []
    if query:
        try: items.extend(search(query,a,b,include_replies=False))
        except Exception as exc: items.append({"ok": False, "query": query, "error": str(exc)})
    elif mode == "all":
        try: items.extend(all_history(a,b))
        except Exception as exc: items.append({"ok": False, "query": "all_history", "error": str(exc)})
        try: items.extend(all_search(a,b))
        except Exception as exc: items.append({"ok": False, "query": "all_search", "error": str(exc)})
    else:
        uid = identity.get("user_id")
        bounds = search_date_bounds(a, b)
        for q in (f"<@{uid}> {bounds}", f"from:<@{uid}> {bounds}"):
            try: items.extend(search(q,a,b,include_replies=False))
            except Exception as exc: items.append({"ok": False, "query": q, "error": str(exc)})
        try: items.extend(dm_history(a,b))
        except Exception as exc: items.append({"ok": False, "query": "dm_history", "error": str(exc)})
    tagged = [tag_item(item) for item in deduplicate(items)[:MAX_ITEMS_PER_LANE]]
    failures = [item for item in tagged if item.get("ok") is False]
    summary = dict(_workspace)
    summary.update({"ok": not failures, "item_count": len(tagged) - len(failures)})
    return tagged, summary

def collect_result(a,b,query=None,workspace=None):
    items = []
    workspaces = []
    for config in workspace_configs(workspace):
        try:
            workspace_items, summary = collect_workspace(a, b, query, config)
            items.extend(workspace_items)
            workspaces.append(summary)
        except Exception as exc:
            values = config.get("values") or {}
            failure = {
                "ok": False,
                "query": "workspace",
                "workspace_slug": config.get("slug"),
                "workspace_name": values.get("SLACK_WORKSPACE_NAME") or config.get("slug"),
                "error": str(exc),
            }
            items.append(failure)
            workspaces.append({key: value for key, value in failure.items() if key != "query"})
    return {"ok": all(workspace.get("ok") for workspace in workspaces), "workspaces": workspaces, "items": items}

def collect(a,b,query=None,workspace=None):
    return collect_result(a, b, query, workspace)["items"]

def main():
    p=argparse.ArgumentParser(); add_common_args(p); p.add_argument("--query"); p.add_argument("--workspace"); args=p.parse_args()
    a,b=window_from_args(args.after,args.before,require=not bool(args.query)); r=base_result("slack","workspace_triage_mode",a,b)
    try: r.update(collect_result(a,b,args.query,args.workspace))
    except Exception as exc: err=error_obj("slack",exc); r["ok"]=False; r["errors"].append(err)
    item_errors = [x for x in r.get("items") or [] if x.get("ok") is False]
    if item_errors:
        r["ok"] = False
        r["errors"].extend(item_errors)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
