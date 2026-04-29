#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import (
    MAX_ITEMS_PER_LANE,
    SLACK_SENT_CONTEXT_LIMIT,
    SLACK_SURROUNDING_LIMIT,
    SLACK_THREAD_REPLY_LIMIT,
    compact_text,
    day_bounds_utc,
    iso_utc,
    load_config,
    run,
)


class SlackClient:
    def __init__(self, config):
        slack_cfg = ((config or {}).get("channels") or {}).get("slack") or {}
        self.bot_token = slack_cfg.get("botToken")
        self.user_token = slack_cfg.get("userToken")
        self.team_id = slack_cfg.get("teamId") or "T2JGQ9YBV"
        self.my_user_id = slack_cfg.get("allowFrom", ["U09UMU4TUN8"])[0] if slack_cfg.get("allowFrom") else "U09UMU4TUN8"
        self._users = {}
        self._channels = {}
        self._me = None

    def _api(self, method, params=None, token=None):
        token = token or self.user_token or self.bot_token
        if not token:
            raise RuntimeError("missing slack token")
        cmd = [
            "curl", "-sS", "https://slack.com/api/" + method,
            "-H", f"Authorization: Bearer {token}",
        ]
        params = params or {}
        if params:
            cmd.extend(["--get"])
            for key, value in params.items():
                cmd.extend(["--data-urlencode", f"{key}={value}"])
        data = json.loads(run(cmd))
        if not data.get("ok"):
            raise RuntimeError(f"slack {method} failed: {data.get('error', 'unknown error')}")
        return data

    def auth(self):
        if self._me is None:
            self._me = self._api("auth.test")
            self.team_id = self._me.get("team_id") or self.team_id
            self.my_user_id = self._me.get("user_id") or self.my_user_id
        return self._me

    def user_name(self, user_id):
        if not user_id:
            return None
        if user_id in self._users:
            return self._users[user_id]
        try:
            profile = self._api("users.info", {"user": user_id}).get("user") or {}
            name = profile.get("real_name") or profile.get("name") or user_id
        except Exception:
            name = user_id
        self._users[user_id] = name
        return name

    def channel_meta(self, channel_id):
        if not channel_id:
            return {"name": None, "chat_type": None}
        if channel_id in self._channels:
            return self._channels[channel_id]
        try:
            convo = self._api("conversations.info", {"channel": channel_id}).get("channel") or {}
            chat_type = "channel"
            if convo.get("is_im"):
                chat_type = "im"
            elif convo.get("is_mpim"):
                chat_type = "mpim"
            elif convo.get("is_group"):
                chat_type = "group"
            meta = {"name": convo.get("name") or convo.get("user") or channel_id, "chat_type": chat_type}
        except Exception:
            meta = {"name": channel_id, "chat_type": "channel"}
        self._channels[channel_id] = meta
        return meta

    def search_messages(self, query, count=100):
        return (((self._api("search.messages", {"query": query, "count": count}).get("messages") or {}).get("matches")) or [])

    def replies(self, channel_id, thread_ts):
        return (self._api("conversations.replies", {"channel": channel_id, "ts": thread_ts, "limit": SLACK_THREAD_REPLY_LIMIT}).get("messages") or [])

    def history(self, channel_id, latest, limit):
        return (self._api("conversations.history", {
            "channel": channel_id,
            "latest": latest,
            "inclusive": True,
            "limit": limit,
        }).get("messages") or [])



def _slack_permalink(team_id, channel_id, ts):
    return f"slack://channel?team={team_id}&id={channel_id}&message={str(ts).replace('.', '')}"



def _slack_message_obj(client, raw, channel_id=None):
    channel_id = channel_id or raw.get("channel", {}).get("id") or raw.get("channel_id")
    meta = client.channel_meta(channel_id)
    user_id = raw.get("user") or raw.get("user_id")
    return {
        "ts": raw.get("ts"),
        "user": user_id,
        "user_name": client.user_name(user_id) if user_id else None,
        "text": compact_text(raw.get("text") or "", 12000),
        **({"thread_ts": raw.get("thread_ts")} if raw.get("thread_ts") else {}),
        **({"channel": channel_id} if channel_id else {}),
        **({"channel_name": meta.get("name")} if channel_id else {}),
        **({"channel_type": meta.get("chat_type")} if channel_id else {}),
        "permalink": _slack_permalink(client.team_id, channel_id, raw.get("ts")) if channel_id and raw.get("ts") else None,
        "files": raw.get("files") or [],
    }



def collect_slack(config, after_dt, before_dt):
    workspace = {"team": "Small Giants", "team_id": "T2JGQ9YBV", "user": "sil", "user_id": "U09UMU4TUN8"}
    try:
        client = SlackClient(config or load_config())
        auth = client.auth()
        workspace = {
            "team": auth.get("team") or workspace["team"],
            "team_id": auth.get("team_id") or workspace["team_id"],
            "user": auth.get("user") or workspace["user"],
            "user_id": auth.get("user_id") or workspace["user_id"],
        }
        date_query = f"after:{after_dt.strftime('%Y-%m-%d')} before:{before_dt.strftime('%Y-%m-%d')}"
        sent_matches = client.search_messages(f"from:me {date_query}", count=MAX_ITEMS_PER_LANE)
        me = auth.get("user") or workspace.get("user") or "sil"
        mention_queries = [
            f"mentioned:{me} {date_query}",
            f"<@{client.my_user_id}> {date_query}",
        ]
        mention_matches = []
        mention_seen = set()
        for query in mention_queries:
            for match in client.search_messages(query, count=MAX_ITEMS_PER_LANE):
                key = ((match.get("channel") or {}).get("id"), match.get("ts"), match.get("user"), (match.get("text") or ""))
                if key in mention_seen:
                    continue
                mention_seen.add(key)
                mention_matches.append(match)
        items = []
        seen = set()

        for raw in sent_matches:
            channel_id = (raw.get("channel") or {}).get("id")
            key = (channel_id, raw.get("ts"), "sent")
            if key in seen:
                continue
            seen.add(key)
            message = _slack_message_obj(client, raw, channel_id)
            thread_ts = raw.get("thread_ts") or raw.get("ts")
            thread_messages = [_slack_message_obj(client, msg, channel_id) for msg in client.replies(channel_id, thread_ts)]
            is_root = raw.get("ts") == thread_ts
            has_other_reply = any(msg.get("user") and msg.get("user") != client.my_user_id for msg in thread_messages[1:])
            kind = "my_thread" if is_root and has_other_reply else "sent"
            history = client.history(channel_id, raw.get("ts"), SLACK_SENT_CONTEXT_LIMIT + SLACK_SURROUNDING_LIMIT + 1)
            history = list(reversed(history))
            surrounding = []
            for msg in history:
                if msg.get("ts") == raw.get("ts"):
                    continue
                surrounding.append({
                    "ts": msg.get("ts"),
                    "user": msg.get("user"),
                    "user_name": client.user_name(msg.get("user")) or msg.get("user"),
                    "text": compact_text(msg.get("text") or "", 4000),
                })
            items.append({
                "lane": "slack",
                "kind": kind,
                "channel": channel_id,
                "channel_name": message.get("channel_name"),
                "channel_type": message.get("channel_type"),
                "message": message,
                "surrounding_messages": surrounding[-SLACK_SENT_CONTEXT_LIMIT:] if kind != "mention" else surrounding[-SLACK_SURROUNDING_LIMIT:],
                "thread_messages": thread_messages,
                "sent_context": [],
                "contains_my_participation": True,
            })

        for raw in mention_matches:
            if raw.get("user") == client.my_user_id:
                continue
            channel_id = (raw.get("channel") or {}).get("id")
            key = (channel_id, raw.get("ts"), "mention")
            if key in seen:
                continue
            seen.add(key)
            message = _slack_message_obj(client, raw, channel_id)
            thread_ts = raw.get("thread_ts") or raw.get("ts")
            thread_messages = [_slack_message_obj(client, msg, channel_id) for msg in client.replies(channel_id, thread_ts)]
            items.append({
                "lane": "slack",
                "kind": "mention",
                "channel": channel_id,
                "channel_name": message.get("channel_name"),
                "channel_type": message.get("channel_type"),
                "message": message,
                "surrounding_messages": [],
                "thread_messages": thread_messages,
                "sent_context": [],
                "contains_my_participation": any(msg.get("user") == client.my_user_id for msg in thread_messages),
            })

        items.sort(key=lambda item: item.get("message", {}).get("ts") or "", reverse=False)
        return {"ok": True, "workspace": workspace, "items": items[:MAX_ITEMS_PER_LANE]}
    except Exception as exc:
        return {"ok": False, "workspace": workspace, "error": str(exc), "items": []}



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)
    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "slack",
        "after": iso_utc(after_dt),
        "before": iso_utc(before_dt),
        **collect_slack(load_config(), after_dt, before_dt),
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
