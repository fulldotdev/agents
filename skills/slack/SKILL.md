---
name: "slack"
description: "Slack Web API via curl using user-level config/env credentials."
metadata:
  {
    "openclaw":
      {
        "emoji": "💬",
        "requires": { "bins": ["curl", "jq"] },
        "primaryEnv": "SLACK_USER_TOKEN"
      }
  }
---

# Slack

Use this skill for direct Slack Web API work through `curl`, not for running Slack as an OpenClaw chat channel.

Prefer this skill when Slack should be a tool/lane for search, triage, context gathering, drafts, or explicit sends. Do not use or re-enable the OpenClaw Slack channel runtime for this.

## Credentials

Preferred credential order:

1. Already-exported shell env vars.
2. Global user config at `~/.config/slack/config.env`.

Store Slack credentials in global user config, not in OpenClaw channel config, project repos, skills, or chat logs:

```sh
mkdir -p ~/.config/slack
chmod 700 ~/.config/slack
cat > ~/.config/slack/config.env <<'EOF'
SLACK_USER_TOKEN=xoxp-or-xoxc-token
SLACK_BOT_TOKEN=xoxb-token-if-needed
SLACK_APP_TOKEN=xapp-token-if-needed
EOF
chmod 600 ~/.config/slack/config.env
```

Before API calls, load the global config if env vars are not already exported:

```sh
set -a
[ -f ~/.config/slack/config.env ] && . ~/.config/slack/config.env
set +a
```

Credential use:

- `SLACK_USER_TOKEN`: preferred for user-context search, DMs, private channels, and triage collector reads.
- `SLACK_BOT_TOKEN`: use for bot-scoped operations when user token is unnecessary or unavailable.
- `SLACK_APP_TOKEN`: only for Socket Mode/App-level flows. Do not use for normal Web API calls.

Never print full tokens. If confirming config, only report which variable names exist and whether `auth.test` succeeds.

## API basics

Base URL: `https://slack.com/api`

Common headers:

```sh
-H "Authorization: Bearer $SLACK_USER_TOKEN"
-H "Content-Type: application/json; charset=utf-8"
```

Test auth:

```sh
curl -sS https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" | jq '{ok, team, user_id}'
```

## Search and read

Search messages:

```sh
curl -sS "https://slack.com/api/search.messages?query=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' 'from:me after:2026-06-01')&count=20&sort=timestamp&sort_dir=desc" \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" | jq '.messages.matches[] | {channel:.channel.name, ts, user, text, permalink}'
```

Read channel or DM history:

```sh
curl -sS "https://slack.com/api/conversations.history?channel=$CHANNEL_ID&limit=50" \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" | jq '.messages[] | {ts, user, text}'
```

Read thread replies:

```sh
curl -sS "https://slack.com/api/conversations.replies?channel=$CHANNEL_ID&ts=$THREAD_TS&limit=50" \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" | jq '.messages[] | {ts, user, text}'
```

Get permalink:

```sh
curl -sS "https://slack.com/api/chat.getPermalink?channel=$CHANNEL_ID&message_ts=$TS" \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" | jq -r '.permalink'
```

## Drafts and sends

Slack Web API does not have a normal saved-draft endpoint. For drafts, prepare text in the response or in a local temp file and ask before sending unless the user explicitly asked to send.

Send message only after explicit user approval:

```sh
curl -sS https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data @message.json
```

`message.json` shape:

```json
{
  "channel": "C123",
  "text": "Message text"
}
```

For replies, add `thread_ts`. For channel broadcast of a thread reply, add `reply_broadcast: true` only when explicitly requested.

## Triage collector convention

Triage collectors should read Slack credentials in this order:

1. Env vars: `SLACK_USER_TOKEN`, `SLACK_BOT_TOKEN`, optional `SLACK_USER_TOKEN_READONLY`.
2. `~/.config/slack/config.env`.

Do not read Slack tokens from `~/.openclaw/openclaw.json`. That file is for OpenClaw channel configuration, not reusable API credentials.

Collector reads should prefer `SLACK_USER_TOKEN`, then `SLACK_BOT_TOKEN`, then `SLACK_USER_TOKEN_READONLY` if present and valid.

## Safety

- Ask before sending, deleting, scheduling, or modifying Slack messages unless the user explicitly asked for that exact action.
- Do not expose tokens, private channel names, or private message contents beyond what is needed for the task.
- For broad searches, summarize and cite Slack permalinks where possible instead of dumping raw message bodies.
- If Slack returns `invalid_auth`, test each configured token by variable name only; remove or replace stale credentials.
- If Slack returns `missing_scope`, report the required operation and stop instead of trying unrelated tokens blindly.
