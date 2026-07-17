# Slack Web API

## Credentials

For multi-workspace reads, store one file per workspace under `~/.config/slack/workspaces/<slug>.env`. Each file contains `SLACK_WORKSPACE_NAME` and that workspace's token variables. The work-management collector reads every `*.env` file in this directory, emits a success/failure summary per workspace, and labels results with the workspace slug, display name, team ID, and URL.

Set `SLACK_CONFIG_PATH` only when intentionally selecting one config file. If no workspace files exist, exported environment variables are the fallback.

Use `--workspace <slug>` on the work-management source collector for a focused read. Omit it during triage so every workspace is collected.

Token roles:

- `SLACK_USER_TOKEN`: preferred for user-context search, DMs, private channels, and triage reads.
- `SLACK_BOT_TOKEN`: bot-scoped operations when appropriate.
- `SLACK_USER_TOKEN_READONLY`: collector fallback after the user and bot tokens.
- `SLACK_APP_TOKEN`: Socket Mode only, not normal Web API calls.

Keep direct API credentials in the workspace files, not project repos, skills, chat logs, old OpenClaw backups, or Hermes gateway config. Reserve Hermes environment credentials for the gateway itself. Never print a full token.

Validate every configured user or bot token with `auth.test`. The display name and URL slug can differ; use `team_id` as the stable workspace identity. Before sending, select the exact workspace file.

## Requests

Base URL: `https://slack.com/api`. Use `Authorization: Bearer <token>` and, for JSON writes, `Content-Type: application/json; charset=utf-8`.

Useful endpoints:

- `auth.test` — validate the token and identify team/user.
- `search.messages` — locate candidate messages; URL-encode the query.
- `conversations.history` — read channel or DM history.
- `conversations.replies` — read the complete thread using channel ID and parent timestamp.
- `chat.getPermalink` — create a reopenable source link.
- `chat.postMessage` — send only after explicit request or approval.

Paginate until the requested time window or relevant thread is complete. Inspect the returned `ok` and `error` fields for every call.

## Send payload

Send one JSON object containing `channel` and `text`. Add `thread_ts` for a reply. Add `reply_broadcast: true` only when explicitly requested. Slack has no normal Web API saved-draft endpoint, so drafts remain in the response or a temporary local file until approved.

After sending, retain the returned channel and timestamp, call `chat.getPermalink`, and report the link without exposing unrelated response data.
