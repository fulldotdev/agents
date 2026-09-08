---
name: weekly-planning
description: Run Sunday Notion cleanup and project-update drafts, process Sil's numbered approvals or edits in Telegram Planning, and send approved updates on Monday morning.
---

# Weekly planning

One weekly routine on Otis: prepare Sunday at 10:00, review in Telegram Planning, and send approved updates Monday at 07:00 Europe/Amsterdam. Updates tell each customer what we will work on in the coming week, so they know what to expect without asking. Use `work-management` for Notion decisions and `customer-communication` for voice.

Read the instructions for the current stage:

- [Sunday preparation](references/sunday.md): collect sources, clean up Notion, draft useful updates and publish one numbered review.
- [Planning replies](references/approvals.md): handle Sil's approvals, edits, skips and withdrawals.
- [Monday sending](references/monday.md): check current facts, send only approved messages and report the result.

Read [operations.md](references/operations.md) for the helper commands used in each stage. Use that helper for storing drafts, approvals, review publication and send results. Use the existing `gog`, `slack` or `wacli` skill for the actual channel operation.

Notion Project bodies hold exact messages, destinations, revisions, approvals and send receipts. The Sprint holds the numbered review list. Telegram Planning is chat `-5475360719`; Sil's verified user ID is `8491875812`. Use these IDs, not name searches. The helper reads actual Hermes chat history to verify approvals; no separate approval database or approval state in memory.

Only the exact text and destination returned by a successful send claim may be sent. Missing approval, changed text or an uncertain earlier send blocks sending that item. Sunday never sends customer messages. Follow the current stage's instructions to avoid duplicate Planning summaries.
