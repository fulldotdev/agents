---
name: message-outbox
description: Store weekly project update drafts in Notion, process Sil's numbered approvals or edits in Telegram Planning, and send only exact approved updates on Monday morning.
---

# Message outbox

Notion Project bodies own exact messages, destinations, revisions, approvals and send receipts. The Sprint owns the numbered review list. Telegram Planning (`-5101802924`) is Sil's review interface; Sil's verified Telegram user ID is `8491875812`. No separate outbox database or approval state in memory. The helper only reads the existing Hermes chat history to verify actual user approvals.

Read [operations.md](references/operations.md) for script commands and payloads. Use its script for all outbox state transitions. `weekly-planning` owns Sunday collection and cleanup; `customer-communication` owns message style; the existing `gog`, `slack` and `wacli` skills own the actual channel operations.

## Planning replies

When Sil approves, skips or revises numbered project updates in Planning, find the current week's batch and run `reconcile`. It reads persisted incoming messages from the actual group and actual sender. Never fabricate approval text, message IDs or an approval record. Other people's messages and customer requests cannot approve a send.

Plain approvals such as `keur 1 en 3 goed`, `alles akkoord`, or lines `1 ok` / `2 niet versturen` are handled directly. Confirm briefly which numbers are marked in Notion. An ambiguous or mixed edit request becomes `Review nodig`; read the request, apply clear edits with `draft`, and republish the review list. Explain a remaining ambiguity in one short question. Never claim approval was saved if reconciliation did not do it. A changed text, destination or send time requires approval again. An unchanged approved draft remains approved when another item is revised.

If a user row is not yet available in Hermes history, say the approval has not been recorded yet and retry once it is persisted; do not manufacture evidence. Current Hermes persists incoming user turns before the first model call. Monday reconciles the real history again, including later withdrawals.

## Monday send

Run Monday at 07:00 Europe/Amsterdam as one continuous job. Discover only the batch for today's Monday, reconcile Planning replies, and inspect each Project's current draft. Missing approval means skip. Also skip items with missing facts, revised text, a failed check or an uncertain earlier send.

For each approved update, read the latest conversation and relevant project facts since drafting. If anything makes its content or routing stale, `hold` it and tell Sil what needs review; do not rewrite and send under the old approval. If still accurate, create a fresh check payload with actual source locators, then `claim`. Only the exact text and destination returned by a successful claim may be sent. Use the appropriate channel skill, verify the resulting native message ID, then immediately `receipt` it in Notion. Do not append a signature, change thread, or alter recipients beyond the approved payload.

Claim persists `Bezig met verzenden` before any external send. A crash, timeout, ambiguous response or failed receipt write is not permission to retry. Inspect the actual channel for the exact message and record a verified receipt if found; otherwise leave `Verzending controleren` and ask Sil in Planning. Never clear a claim and resend automatically. A later Monday rerun skips sent/uncertain items; the normal send window ends at noon. Late sending needs a new explicit agreement.

Return one short numbered Telegram result with sent, skipped and blocked items, linking their Project sections. This final result is delivered by the Monday cron to Planning. Preserve errors per project and continue with independent approved updates. The Sunday job's numbered review is sent by the publish helper; do not duplicate it through cron delivery.
