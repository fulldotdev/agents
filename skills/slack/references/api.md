# Slack Web API

## Credentials

Store one file per workspace under `~/.config/slack/workspaces/<slug>.env`, with `SLACK_WORKSPACE_NAME` and that workspace's tokens. The work-triage collector reads every `*.env` file there, reports success or failure per workspace, and labels results with slug, name, team ID, and URL.

`SLACK_TRIAGE_MODE=signals` (the default) collects DMs, mentions, and the user's own messages. `SLACK_TRIAGE_MODE=all` collects every reachable message in the window, including channel messages and thread replies.

Set `SLACK_CONFIG_PATH` only to pick one config file on purpose. Without workspace files, exported environment variables are the fallback.

Token roles:

- `SLACK_USER_TOKEN`: searches, DMs, private channels, and triage reads.
- `SLACK_BOT_TOKEN`: bot-scoped operations.
- `SLACK_USER_TOKEN_READONLY`: collector fallback after the user and bot tokens.
- `SLACK_APP_TOKEN`: Socket Mode only, not the Web API.

Keep these files separate from OpenClaw gateway credentials and out of repos, skills, and chat logs. Never print a full token.

Check each user or bot token with `auth.test`. Display name and URL slug can differ, so use `team_id` as the workspace identity. Before sending, pick the exact workspace file.

## Requests

Base URL `https://slack.com/api`, header `Authorization: Bearer <token>`, and for JSON writes `Content-Type: application/json; charset=utf-8`.

- `auth.test`: check the token and identify team and user.
- `search.messages`: find candidate messages. URL-encode the query.
- `conversations.history`: read channel or DM history.
- `conversations.replies`: read a full thread by channel ID and parent timestamp.
- `chat.getPermalink`: make a link that reopens a message.
- `chat.postMessage`: send, only after approval.

Paginate until the time window or thread is complete. Check `ok` and `error` on every response.

## Sending

Send one JSON object with `channel` and `text`. Add `thread_ts` for a reply, and `reply_broadcast: true` only when asked. Add `unfurl_links: false` and `unfurl_media: false` unless the user wants previews.

Keep the returned channel and timestamp, call `chat.getPermalink`, and report the link without the rest of the response.
