# Outbox commands

Run on Otis, where Hermes and channel credentials live:

```sh
python3 ~/.agents/skills/message-outbox/scripts/outbox.py discover --week YYYY-MM-DD
python3 ~/.agents/skills/message-outbox/scripts/outbox.py init --sprint SPRINT_ID --week YYYY-MM-DD
python3 ~/.agents/skills/message-outbox/scripts/outbox.py draft --batch BATCH_ID --file /tmp/update.json
python3 ~/.agents/skills/message-outbox/scripts/outbox.py publish --batch BATCH_ID --file /tmp/cleanup-note.txt
python3 ~/.agents/skills/message-outbox/scripts/outbox.py recover-publication --batch BATCH_ID --file /tmp/verified-planning-receipt.json
python3 ~/.agents/skills/message-outbox/scripts/outbox.py reconcile --batch BATCH_ID
python3 ~/.agents/skills/message-outbox/scripts/outbox.py list --batch BATCH_ID
python3 ~/.agents/skills/message-outbox/scripts/outbox.py claim --batch BATCH_ID --number 1 --file /tmp/source-check.json
python3 ~/.agents/skills/message-outbox/scripts/outbox.py receipt --section SECTION_ID --file /tmp/receipt.json
python3 ~/.agents/skills/message-outbox/scripts/outbox.py hold --section SECTION_ID --file /tmp/reason.json
```

Week is the Monday date. Sunday drafts belong to the next day; Monday sends belong to today. `init` is idempotent. `draft` replaces the same project's unsent draft, increments its revision and clears approval. Publication is a single Telegram message; shorten names/notes if the review list exceeds the limit. Numbers stay fixed within the week. Draft source locators are internal, never appended to customer text automatically.

Draft input:

```json
{
  "project": "notion-project-id",
  "name": "Project name",
  "text": "Exact customer message",
  "destination": {
    "channel": "slack",
    "label": "Company · #project · existing thread",
    "workspace": "verified-workspace-slug",
    "channel_id": "verified-channel-id",
    "thread_ts": "verified-parent-ts"
  },
  "sources": ["actual conversation permalink", "actual delivery evidence"]
}
```

Other destinations: Gmail `{channel, label, account, to: [address], cc: [address], bcc: [address], subject, reply_to_message_id}`; WhatsApp `{channel, label, jid, reply_to_id?}`. Omit optional fields only when actually absent. These fields and the exact text, project, revision and Monday 07:00 timestamp are included in the approval digest. The readable destination label must expose who receives the message and whether it is a reply. Never infer IDs from display names alone.

The Project toggle contains a status line, the exact text in a plain-text code block, and operational JSON. The Sprint toggle contains the review list and its mapping/receipts. Keep edits through the helper: a manual text change intentionally fails digest checks until stored as a new draft and reviewed again. Avoid directly editing the JSON. A local file lock only serializes helper invocations; it contains no workflow state.

Fresh check input:

```json
{"checked_at": "current ISO timestamp with timezone", "digest": "current draft digest", "unchanged": true, "sources": ["latest conversation locator", "current delivery evidence"]}
```

Do the actual check first. A claim requires a source check less than ten minutes old, exact approval verified against the real incoming Hermes row and published review, and Monday 07:00–12:00 Amsterdam. Claim output is the sole send payload. The helper does not call customer send APIs; the agent follows the channel skill using this exact payload. Never invoke a channel sender when claim fails.

Receipt input:

```json
{"digest": "claim digest", "channel": "slack", "message_id": "native sent message ID", "sent_at": "actual ISO timestamp", "url": "verified message URL if available"}
```

`hold` takes a short JSON object with `reason` and supporting `sources`. A claimed message remains uncertain, not resendable. On a receipt-write failure, retry only the receipt write using the existing native send result. Check an uncertain publication in Planning before republishing; its pending marker blocks claims until the review's delivery is resolved. Do not invent a success receipt from a command's exit code alone.

`recover-publication` records an actually verified Planning publication after its Notion write failed. Supply the original native `message_id`, `chat_id` and actual `sent_at` from delivery evidence, after checking that the message contains the pending review list. It does not send. If delivery cannot be established, keep the batch held and ask Sil to resolve it; do not simply clear the marker.

Publication and Notion are two separate external systems. An uncertain review publication or customer send is deliberately held for inspection, not represented as exactly-once delivery. Never use a new local state database to hide this limitation.
