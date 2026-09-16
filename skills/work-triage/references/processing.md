# Processing protocol

The state file is the ledger for a run: which events are open, which external writes were started, and which reports are not yet delivered. Change it only through `collect.py queue ...`, never by editing the JSON. Pass `--state-file STATE` to every queue command.

## Owner

One owner per run. The scheduler supplies it; keep it for the whole run, also after an interruption.

If the state is owned by another worker, prove that worker stopped before taking over: its session in `openclaw sessions --agent main --limit all --json` is failed or stopped with no recent activity, and the cron run history shows it ended. Age alone is not proof. Then run `queue claim --owner NEW --previous-owner OLD`. If you cannot prove it stopped, make no external writes and return.

## Reading events

Only events whose status is not `done` need a decision. Read the full event with `queue show --event ID`. Read a Notion record, T3 thread or chat with `queue context --lane companies|projects|tasks|gmail|slack|whatsapp|calendar|meetings|t3_threads --id ID` (repeatable) or `--query TEXT`. WhatsApp events include the refreshed chat with Sil's outgoing messages. When the context lookup finds nothing, check the live source before concluding that no record exists.

Events acknowledged in an earlier run stay visible as context; never redo their actions. When an event has `superseded_by`, decide on the newer event and acknowledge the old one with `no_action`. A message edited after it was handled becomes a new event: compare it with what was already written to the destination and add only the difference.

## Recording writes

Apply decisions with `queue apply --owner RUN --file /absolute/path/decisions.json`. The file is a JSON array; put independent operations in one file. Use real event IDs from the queue.

**Gmail drafts.** Gmail itself is the ledger. Before writing, read the thread's latest sent reply and its existing drafts. After writing, read the draft back and record it:

```json
[
  {"op":"record_draft","event":"gmail:EVENT_HASH","kind":"draft_created","receipt":"GMAIL_DRAFT_ID","report":{"title":"Draft created: subject","url":"VERIFIED_DRAFT_URL"}},
  {"op":"ack","event":"gmail:EVENT_HASH","outcome":"handled","note":"Draft read back"}
]
```

Use `draft_updated` for a material update of an existing draft. Recording the same draft twice does not duplicate its report. Saving a draft never authorizes sending.

**Every other external write** (Notion, Dex, T3, Calendar) takes three steps:

1. Before writing, `prepare` with a stable key and a target that a later worker can search for:

```json
[{"op":"prepare","event":"EVENT_ID","key":"ACTION_KEY","kind":"task_created","target":"Notion Task for SOURCE_URL; search before creating"}]
```

2. Write, then read the result back.
3. `resolve` with the real ID, then `ack` the event:

```json
[
  {"op":"resolve","key":"ACTION_KEY","receipt":"NOTION_PAGE_ID","report":{"title":"Task created: outcome","url":"VERIFIED_NOTION_URL"}},
  {"op":"ack","event":"EVENT_ID","outcome":"handled","note":"Task read back"}
]
```

Kinds that appear in the report: `task_created`, `project_created`, `company_created`, `task_canceled`, `task_done`, `project_status_changed`, `company_status_changed`, `draft_created`, `draft_updated`, `t3_started`, `t3_continued`, `calendar_created`, `calendar_updated`, `calendar_rescheduled`, `calendar_canceled`. These need a `report` with title and native URL; status titles include `old → new`. Quiet writes such as a Timeline append or a Resources link use `context_updated` or `other` without `report`. `t3_started` needs Sil's authorization per `t3-routing.md`.

**A prepared action without a resolve.** This happens when a run stopped between prepare and resolve, or when an earlier run left one behind. Do this, in this order:

1. Search the target named in the prepare: the Notion database, Gmail thread, T3 thread list or Calendar.
2. Found: `resolve` it with the ID you found. Do not create a second one.
3. Not found: do the write now, read it back, then `resolve`.
4. No longer needed, for example Sil already did it or the request was withdrawn: `cancel` it with a note and evidence.

```json
[{"op":"cancel","key":"ACTION_KEY","note":"Sil already answered","evidence":"Sent message LOCATOR; no Task found in search"}]
```

5. Cannot search the target because the service is down: leave the action prepared, mark its event `retry` with a note naming the target that still has to be checked, and finish the batch.

Never acknowledge an event while one of its prepared actions is still open.

**No action:** `{"op":"ack","event":"EVENT_ID","outcome":"no_action","note":"what was checked"}`.

**Not finished:** `{"op":"retry","event":"EVENT_ID","note":"what is missing"}`.

**Failure report.** After a lane failed to collect in two runs in a row: `{"op":"report_failure","lane":"slack","title":"What is broken and what Sil must do"}`. For an event that needed `retry` in two different batches, use `"event":"EVENT_ID"` instead of `lane`. Only report when Sil has to act. A later success removes an undelivered failure report.

## Finish

1. `queue finish --owner RUN` saves the decisions. Unfinished events and open prepared actions stay in the backlog for the next run. Only complete lanes whose events are all done move their cursor forward.
2. `queue reports --owner RUN` lists reports that are not yet confirmed delivered. Check the Triage chat history or the cron run receipt (`openclaw cron runs --id JOB_ID --json` with `delivered: true` and `deliveryStatus: "delivered"`). Mark an entry `{"op":"reported","key":"ACTION_KEY"}` only when that earlier message is proven delivered. Reports you put in this run's final answer stay unmarked; the next run confirms them. A `NO_REPLY` or a successful run is not delivery.
3. `queue release --owner RUN`.
4. Return the numbered report or `NO_REPLY`. The scheduler delivers it; do not send a separate message.

Per-run downloads in the cache directory are scratch files, not document storage. Runtime and scheduler alerts belong to the watchdog.
