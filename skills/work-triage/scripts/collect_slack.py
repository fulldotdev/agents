#!/usr/bin/env python3
import argparse, json, os, shlex, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlencode
from triage_common import MAX_ITEMS_PER_LANE, add_common_args, base_result, compact_text, emit, error_obj, window_from_args

SLACK_API_TIMEOUT_SECONDS = float(os.environ.get("SLACK_API_TIMEOUT_SECONDS", "8"))
SLACK_CONNECT_TIMEOUT_SECONDS = float(os.environ.get("SLACK_CONNECT_TIMEOUT_SECONDS", "3"))
SLACK_COLLECT_TIMEOUT_SECONDS = float(os.environ.get("SLACK_COLLECT_TIMEOUT_SECONDS", "45"))
SLACK_SEARCH_COUNT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_SEARCH_COUNT", "25")))
SLACK_HISTORY_LIMIT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_HISTORY_LIMIT", "50")))
SLACK_CONVERSATION_LIMIT = min(200, int(os.environ.get("SLACK_CONVERSATION_LIMIT", "100")))
SLACK_ACTIVE_THREAD_LIMIT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_ACTIVE_THREAD_LIMIT", "25")))
SLACK_REPLIES_LIMIT = min(MAX_ITEMS_PER_LANE, int(os.environ.get("SLACK_REPLIES_LIMIT", "50")))
SLACK_WORKERS = max(1, int(os.environ.get("SLACK_WORKERS", "4")))
SLACK_CONFIG_PATH = os.environ.get("SLACK_CONFIG_PATH") or str(Path.home() / ".config" / "slack" / "config.env")
_deadline = None

def load_config_env():
    cfg = Path(SLACK_CONFIG_PATH)
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

def token():
    cfg = load_config_env()
    for key in ("SLACK_USER_TOKEN", "SLACK_BOT_TOKEN", "SLACK_USER_TOKEN_READONLY"):
        value = os.environ.get(key) or cfg.get(key)
        if value and value.strip():
            return value.strip()
    raise RuntimeError("missing slack token")

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
        url,
        "-H",
        f"Authorization: Bearer {token()}",
    ]
    for attempt in range(3):
        check_deadline()
        try:
            p = subprocess.run(
                cmd,
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

def me(): return api("auth.test").get("user_id")
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

def norm(msg, channel=None, channel_name=None, channel_type=None, after_dt=None, before_dt=None):
    if not isinstance(msg, dict): msg = {}
    msg_channel = msg.get("channel") if isinstance(msg.get("channel"), dict) else {}
    ch = channel or channel_id(msg)
    return {"channel_id": ch, "channel_name": channel_name or msg_channel.get("name"), "channel_type": channel_type or ("im" if msg_channel.get("is_im") else "channel"), "ts": msg.get("ts"), "thread_ts": msg.get("thread_ts") or msg.get("ts"), "sender": msg.get("user"), "text": compact_text(msg.get("text"), 12000), "url": msg.get("permalink"), "files": msg.get("files") or [], "in_window": in_window(msg, after_dt, before_dt) if after_dt and before_dt else None}

def replies(ch, thread_ts, a, b):
    if not ch or not thread_ts: return []
    return [norm(m, channel=ch, after_dt=a, before_dt=b) for m in api("conversations.replies", {"channel": ch, "ts": thread_ts, "limit": str(SLACK_REPLIES_LIMIT)}).get("messages") or [] if isinstance(m, dict) and in_window(m, a, b)]

def slack_search_messages(q):
    matches = (api("search.messages", {"query": q, "count": str(SLACK_SEARCH_COUNT), "sort": "timestamp", "sort_dir": "desc"}).get("messages") or {}).get("matches") or []
    return [m for m in matches if isinstance(m, dict)][:MAX_ITEMS_PER_LANE]

def search(q, a, b, filter_window=True, include_replies=True):
    matches = slack_search_messages(q)
    items = []
    for m in matches:
        item = norm(m, after_dt=a, before_dt=b); item["match_query"] = q
        item["thread_replies"] = replies(item["channel_id"], item["thread_ts"], a, b) if include_replies else []
        if not filter_window or item.get("in_window") or item["thread_replies"]:
            items.append(item)
    return items

def dm_channel_history(ch, a, b, oldest, latest):
    items = []
    for m in api("conversations.history", {"channel": ch.get("id"), "oldest": oldest, "latest": latest, "inclusive": "false", "limit": str(SLACK_HISTORY_LIMIT)}).get("messages") or []:
        if not isinstance(m, dict): continue
        item = norm(m, channel=ch.get("id"), channel_name=ch.get("name"), channel_type="mpim" if ch.get("is_mpim") else "im", after_dt=a, before_dt=b)
        item["match_query"] = "dm_history"; item["thread_replies"] = replies(ch.get("id"), item["thread_ts"], a, b) if m.get("reply_count") else []; items.append(item)
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

def active_threads(uid,a,b):
    roots = slack_search_messages(f"from:<@{uid}> before:{b.date().isoformat()}")[:SLACK_ACTIVE_THREAD_LIMIT]
    seen, items, jobs = set(), [], []
    for r in roots:
        key = (channel_id(r), r.get("thread_ts") or r.get("ts"))
        if not key[0] or not key[1] or key in seen: continue
        seen.add(key); jobs.append((key[0], key[1], r.get("permalink")))
    with ThreadPoolExecutor(max_workers=min(SLACK_WORKERS, max(1, len(jobs)))) as executor:
        futures = {executor.submit(replies, ch, ts, a, b):(ch, ts, url) for ch, ts, url in jobs}
        for future in as_completed(futures):
            ch, ts, url = futures[future]
            try:
                rs = future.result()
                if rs: items.append({"channel_id": ch, "thread_ts": ts, "url": url, "reason": "sil_active_thread", "thread_replies": rs})
            except Exception as exc:
                items.append({"ok": False, "query": "active_thread_replies", "error": str(exc), "channel_id": ch, "thread_ts": ts})
    return items[:MAX_ITEMS_PER_LANE]

def collect(a,b,query=None):
    global _deadline
    _deadline = time.monotonic() + SLACK_COLLECT_TIMEOUT_SECONDS
    uid = None if query else me()
    qs = [query] if query else [f"<@{uid}> after:{a.date().isoformat()} before:{b.date().isoformat()}", f"from:<@{uid}> after:{a.date().isoformat()} before:{b.date().isoformat()}"]
    items = []
    for q in qs:
        try: items.extend(search(q,a,b,include_replies=False))
        except Exception as exc: items.append({"ok": False, "query": q, "error": str(exc)})
    if query:
        return items[:MAX_ITEMS_PER_LANE]
    for fn,name in ((dm_history,"dm_history"),(lambda x,y: active_threads(uid,x,y),"active_thread_replies")):
        try: items.extend(fn(a,b))
        except Exception as exc: items.append({"ok": False, "query": name, "error": str(exc)})
    return items[:MAX_ITEMS_PER_LANE]

def main():
    p=argparse.ArgumentParser(); add_common_args(p); p.add_argument("--query"); args=p.parse_args()
    a,b=window_from_args(args.after,args.before,require=not bool(args.query)); r=base_result("slack","dm_mentions_active_threads",a,b)
    try: r["items"]=collect(a,b,args.query)
    except Exception as exc: err=error_obj("slack",exc); r["ok"]=False; r["errors"].append(err)
    item_errors = [x for x in r.get("items") or [] if x.get("ok") is False]
    if item_errors:
        r["ok"] = False
        r["errors"].extend(item_errors)
    emit(r, args.pretty, args.format)
if __name__=="__main__": main()
