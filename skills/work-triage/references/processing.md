# Durable processing

Use the collector CLI for state changes, never edit its JSON state manually. This is recoverable processing with reconciliation of external writes, not an atomic transaction across Gmail, Notion, T3 and message delivery.

## Claim and collect

Choose one unique owner for this worker run. Keep it when resuming an interrupted run. `triage --incremental --owner RUN --format yaml` persists the batch before returning it; repeating the command refreshes context while preserving the batch ID, decisions, action intents and all unresolved older events. `queue status` shows ownership, pending events, action intents and reports.

Another owner blocks execution. Verify the old worker has actually stopped before `queue claim --owner NEW --previous-owner OLD`. Age alone is not permission to take over. After a normally released run, `queue claim --owner NEW` can claim outstanding reports before collecting.

`groups` is refreshed context, including acknowledged revisions; only unfinished `queue.events` require decisions. Never reexecute an acknowledged revision just because it remains visible. When an event has `superseded_by`, use the newer source for decisions; reconcile its old intents, then acknowledge the obsolete event without new execution or drafts. Older pending payloads stay in the ledger even when absent from today's context. Read each event's current source and relevant existing artifacts before deciding. On the first deployment, the overlap may include events already handled under the old collector; reconcile them. Old checkpoints do not prove that historical processing completed. On migration, the first refreshed WhatsApp/Slack content seeds the edit baseline for legacy receipts without replaying them. Earlier edits cannot be distinguished from previously handled content; reconcile suspected corrections against the destination. Later same-ID content edits create new action revisions.

## Record outcomes

`queue apply --owner RUN --file /absolute/path/decisions.json` accepts a JSON array. Batch independent acknowledgments in one file. Use event IDs from the queue, not invented examples below.

For Gmail drafts, use the persisted source event and Gmail's actual thread/drafts to recover: inspect the latest sent reply and matching drafts before creating or updating, preserve Sil's edits, and verify the result through readback. No separate pre-write intent is needed. Record the native draft ID and acknowledge the event once all its work is handled:

```json
[
  {"op":"record_draft","event":"gmail:EVENT_HASH","kind":"draft_created","receipt":"GMAIL_DRAFT_ID","report":{"title":"Draft created: concrete subject","url":"VERIFIED_NATIVE_URL"}},
  {"op":"ack","event":"gmail:EVENT_HASH","outcome":"handled","note":"Matching draft verified"}
]
```

Use `draft_updated` for a material update. After interruption, reconcile Gmail before retrying a write; an unchanged pre-existing draft is not a newly created outcome. The record key is derived from the event and draft ID, so repeating the same record does not duplicate its report. An existing prepared draft action from an older run still needs `resolve` or `cancel` below; do not also record it as a new action. Saving a draft never authorizes sending.

For other external writes, save an intent with a stable key identifying the result and source revision, plus a target that lets a future worker find it:

```json
[{"op":"prepare","event":"EVENT_ID","key":"ACTION_KEY","kind":"task_created","target":"Notion Task for source SOURCE_URL; search before creating"}]
```

Reportable kinds are `task_created`, `project_created`, `company_created`, `task_canceled`, `task_done`, `project_status_changed`, `company_status_changed`, `draft_created`, `draft_updated`, `t3_started`, `t3_continued`, `calendar_created`, `calendar_updated`, `calendar_rescheduled`, and `calendar_canceled`. Use `context_updated` or `other` for quiet actions. `t3_started` requires work covered by Sil's authorization.

Inspect an existing intent and external state before retrying a write with uncertain outcome. Reuse a verified artifact, preserve human edits, and never create a duplicate merely because its receipt is missing. After successful readback:

```json
[
  {"op":"resolve","key":"ACTION_KEY","receipt":"VERIFIED_EXTERNAL_ID","report":{"title":"Task created: concrete outcome","url":"VERIFIED_NATIVE_URL"}},
  {"op":"ack","event":"EVENT_ID","outcome":"handled","note":"Task verified"}
]
```

Reportable action kinds require a title and native URL; status-change titles include the verified `old → new` transition. Omit `report` for quiet context updates. Every prepared action must be resolved or explicitly canceled before acknowledging its event.

For no action, first pass the main skill's destination, media, Files and context completion checks, then use `ack` with `outcome: "no_action"` and a factual `note` identifying the checked evidence. For an unfinished event, use `retry` with its event ID and the missing evidence or failure in `note`. A prepared intent that has become unnecessary needs `{"op":"cancel","key":"ACTION_KEY","note":"Sil already answered before the write","evidence":"Verified sent-message locator and absence of an existing artifact"}`, not a fabricated success receipt. Reconcile an uncertain external write before canceling; completed actions cannot be canceled.

Before finishing the batch, a qualifying failure can be queued with `{"op":"report_failure","lane":"slack","title":"Practical problem and required fix"}` after two consecutive failed collections. For failed execution, replace `lane` with the `event` ID; this requires retry decisions in at least two distinct batches, not two repeated calls in one run. Only escalate when Sil needs to act. Source recovery or event completion suppresses an undelivered stale failure report.

## Finish and report

`queue finish --owner RUN` saves completed decisions. Only complete, successfully collected lanes advance their checkpoint. Unfinished events, source payloads and action intents remain in the backlog, so independent lanes can progress. A failed or saturated lane remains incomplete; never advance its checkpoint merely to clear an error. Per-run downloads are retained for pending work and are not canonical document storage.

Read `queue reports --owner RUN` and apply the main skill's reporting gate. Reconcile outstanding reports against actual Triage chat messages or matching OpenClaw run receipts (`openclaw cron runs --id JOB_ID --json`). A receipt must confirm delivery (`delivered: true` and `deliveryStatus: "delivered"`) to the intended Triage chat and identify the reported output. A successful run or a silent `NO_REPLY` is not delivery evidence. Retained Hermes receipts apply only to historical deliveries. Mark an entry with `{"op":"reported","key":"ACTION_KEY"}` only when delivery is verified. A prepared answer is not delivery evidence.

Runtime and scheduler alerts belong to the watchdog. Triage owns actionable source and execution failure reports.

Release with `queue release --owner RUN` after finishing the batch, then return the concise final response or `NO_REPLY`. Leave reports first emitted in that final response unmarked until the next run can observe it. If a session change makes delivery uncertain, inspect available conversation history before repeating or acknowledging. This preserves recovery without pretending final-message delivery is exactly once.
