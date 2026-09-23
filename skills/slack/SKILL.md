---
name: "slack"
description: "Use when work requires searching or reading Slack messages, DMs, channels, threads, or permalinks, drafting a Slack message in chat, or sending one after explicit approval. Use this for the direct Slack API, not the OpenClaw gateway."
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

Use the Slack Web API. Leave the OpenClaw Slack gateway alone unless the user asks for a gateway, bot, or channel change. Read [references/api.md](references/api.md) before you call the API.

## Reading

For a focused read, use `python3 ~/.agents/skills/work-triage/scripts/collect.py source slack --workspace <slug>`.

Read the full history and complete threads. Keep timestamps and permalinks, and report any workspace you could not reach.

## Drafting and sending

Keep Slack drafts in the chat and say which workspace, channel, and thread they are for. Do not create drafts inside Slack.

Before sending, pick one workspace and confirm it with `auth.test`. Unless asked otherwise, send with `unfurl_links: false` and `unfurl_media: false`. Check the API response and return the permalink.

Do not delete, schedule, edit, or broadcast a message unless the user asks for that.

## Safety

- Keep tokens, private channel names, and unrelated private content out of your output.
- On `invalid_auth`, name only the failing variable. On `missing_scope`, name the operation or scope.
