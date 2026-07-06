---
name: work-triage
description: "Runs inbound work triage with concurrent deterministic collectors and references-first context capture."
---

# Work Triage

Use for broad incoming triage across Gmail, Slack, WhatsApp, calendar, meetings, and Notion work context.

Triage is not execution. It captures source references, routes work, updates Notion, creates low-risk drafts, and reports concrete changes. Context capture means preserving traceability with links/references and one-line facts, not copying inbound content into Notion bodies.

Scripts collect context only. The parent agent decides Notion writes, archives, drafts, and the final report.

Use `work-management` as the source of truth for work model, routing, relations, body conventions, context capture, and safe writes.

## Run

1. Determine one triage window.
   - Cron/current run: previous successful checkpoint/run time as `after`, current run time as `before`.
   - Manual current run without explicit dates: last 24 hours until now.
   - Work-context lanes are state based: active Customers, active Projects, and open/current-sprint Tasks.
   - Use half-open windows where time windows still apply: `after <= item < before`.
2. Run `scripts/collect_all_context.py --after <iso/date> --before <iso/date> --format yaml`.
3. Read all lane outputs together.
4. Apply `work-management` for matching and writes.

The combined collector runs incoming lanes and work context concurrently, waits for all output, then returns one combined result. Do not use subagents for lane collection.

Collector output is YAML for agent readability. Work-context output is intentionally compact. Customers are an identity/index lane (`id`, `name`, `status`, `domain`, links/timestamps), while Tasks and Projects include only routing/action fields such as name, status, summary, relations, dates, and links. Fetch full Notion pages/bodies only for specific writes or context capture decisions.

Current cron cadence:

- 07:00 Europe/Amsterdam: normally captures 17:00 previous day -> 07:00.
- 17:00 Europe/Amsterdam: normally captures 07:00 -> 17:00.

Actual cron metadata wins over these normal windows.

## Lanes

The collector scripts define lane-specific fetching details. Triage treats these output lanes as required inputs:

- Gmail
- Slack
- WhatsApp
- Calendar
- Meetings
- Codex
- Customers
- Projects
- Tasks

Meeting AI notes: use the Meetings lane `body_excerpt` as the default source. If the excerpt is insufficient and the full transcript matters for a write/decision, fetch the transcript from the provided transcript block ID. The Meetings data source has a `When` property; set it on new/generated meetings when known. The collector uses `When` as the primary window and includes created/edited meetings only when `When` is missing.

Calendar notes: the Calendar lane includes events in the triage window plus a small context window around it to link messages and meeting notes. Defaults: 2 days back and 2 days ahead via `CALENDAR_CONTEXT_LOOKBACK_DAYS` / `CALENDAR_CONTEXT_LOOKAHEAD_DAYS`. Do not collapse recurring events; weekly instances may have different meaning.

Codex thread notes: use the Codex lane as a compact project/thread index, not a conversation dump. It groups local Codex app threads by derived project and includes thread id, description, cwd/git metadata, goals, spawn edges, and a rollout reference. Read into a specific thread only when the compact index can change a triage decision: blocked/needs Sil, ready for review, failed, merged/shipped, or new executable scope. Prefer `scripts/collect_codex.py --thread-id <id> --format yaml` for deep reads. Do not create Notion work from intermediate Codex chatter alone.

Regenerated meeting summaries work best when triage reads them as structured evidence:

- Prefer explicit `Decisions`, `Open questions / blockers`, and cited topic details over generic action lists.
- Treat `Confirmed Sil-owned execution` or clearly Sil-owned high-confidence possible actions as Task candidates.
- Treat external-owner, waiting, unclear-owner, and context-only items as Project/Customer/Task context or blockers.
- When related Notion items are mentioned, check their current status before writing; prefer active Tasks over Done/Canceled/Completed links.
- Teveo sprint-package context belongs on a `Teveo sprint N` Task linked to the Teveo Customer and Sil's weekly Sprint.

## Reliability

- All lanes are required: Gmail, Slack, WhatsApp, Calendar, Meetings, Codex, Customers, Projects, Tasks.
- Lane failure means collect the rest, but do not write based on incomplete context unless the write is clearly local, safe, and independent of the failed lane.
- If any lane fails, report `Failed:` or `Blocked:` with the practical consequence.
- Schema/property/status mismatch must return structured lane failure. No fake empty success.
- Treat collector output as context hints, not full schema. Fetch Notion metadata only when exact property names/options/relation targets are still unknown after reading the target item.

## Writes

Use `work-management` for Customer/Project/Task routing, context capture, body format, status meaning, dedupe, and write safety.

### References-first capture

Default to references, not body dumps. Every useful source should be preserved as a compact reference on the most specific Customer, Project, or Task. Add only the minimum human-readable fact needed to make the reference useful.

Preferred Task body shape:

```md
## Next / Waiting

Concrete next action, or who/what is blocking the task.

## Context

Concise synthesized summary across all relevant references: decisions, blockers, requirements, current state, and execution facts needed to do the work. Deduplicate repeated facts; do not write a timeline.

## References

- <Gmail/Slack/WhatsApp/meeting/calendar/thread/file> <date/sender/title> <link/reference>.
- <Another source/reference>.
```

Use `## State`, `## Decisions`, or `## Done when` only when they make a larger delivery task clearer. Keep `## References` as a bullet list.

Use this heading order:

1. `## Waiting` when blocked, otherwise `## Next`.
2. `## Next` after `## Waiting` only when there are concrete follow-up actions despite the blocker.
3. `## State` for larger delivery tasks where current progress matters.
4. `## Decisions` only when decisions are the main execution input and need their own section.
5. `## Context` as the concise synthesized summary.
6. `## References` last, always as a bullet list.

Rules:

1. Keep headings in English exactly as shown (`## Waiting`, `## Next`, `## State`, `## Decisions`, `## Context`, `## References`). Default task titles and body prose to English for consistency, especially internal/dev/process/agency work or mixed-source work. Use Dutch only when the task is clearly Dutch customer-facing communication/work. Keep source titles, file names, IDs, quotes, and references literal.
2. Prefer source links/references over copying message text.
3. Do not paste long emails, Slack threads, transcripts, meeting summaries, or repeated context into bodies.
4. Context may summarize all references, but it must be compact, deduplicated, and useful for execution/routing; references carry the trace.
5. Keep References complete enough to reopen real sources: Slack threads/conversations, WhatsApp chats/messages, Gmail thread IDs, meetings, files, previews, Moneybird links, Discord/Codex/execution threads, and repo/branch refs when they matter.
6. Add exact body detail only when the source cannot be reliably reopened later, the exact wording is contractually/customer important, or the detail is needed to execute without re-reading the source.
7. For existing Tasks, rewrite/maintain the body as concise Context + complete References instead of appending chronological source sections.
8. For Projects/Customers, capture durable decisions, scope, links, and blockers; avoid turning them into chronological inbox logs.
9. If multiple sources say the same thing, synthesize it once in Context and list/group the sources under References.

Before modifying an existing Task, Project, or Customer, fetch that full page and body with the Notion Markdown API. Use the item properties/body as the primary write context.

Do not create a Task for every customer question. Create or reopen a Task only when there is clear confirmation that CIL/agency work will be executed, or when the next action is already explicitly agreed. If the inbound item is only a question, proposal, idea, or unconfirmed request, capture context on the relevant Customer/Project or report `Blocked:` with the missing confirmation.

Task status changes are conservative:

- Reopening is allowed only when fresh inbound context contains executable work for that same Task.
- Never reopen or move into an active status when the Task belongs only to a previous Sprint.
- If Sprint membership is unclear, capture context without changing status and report the missing decision.
- Current-Sprint Tasks may be reopened when the fetched Task and source context both support it.

Prefer updating an existing broader active Task/work package over creating a narrow sibling Task. If the inbound item is one implementation point, blocker, preference, file, or checklist item inside an active or `Waiting` package, append it to that package body and keep the package as the executable Task. If that package is `Waiting`, move its status only when the new source makes the next action executable.

When triage touches an existing Task, do small opportunistic cleanup if it is clearly safe: remove fake/stale due dates, add a short `Waiting:` / `Follow-up:` note for meaningful Waiting tasks, add a minimal `Next:` / `Context:` note for non-trivial work tasks, or correct an obvious Type mismatch. Do not run broad backlog cleanup during triage unless Sil explicitly asks; leave broad active-list cleanup to work-planning or a dedicated cleanup pass.

If the strongest matching Task was set to `Done` before the current local date, treat it as a closure record. Create a new related Task under the same Project/Customer more aggressively for fresh executable follow-up, and capture only the source/transition note on the completed Task or Project when useful. If it was set to `Done` on the current local date, it may still be reopened or moved back when the fresh source shows the closure was premature.

For repeated admin work with the same action across multiple customers, create or update one batch Task with a customer checklist instead of duplicate same-title Tasks. Split only when timing, owner, risk, customer promise, or execution path is materially different.

When creating a new Task, add it to the current Sprint only when it should be picked up soon: explicit urgency, active customer commitment, due date inside the current Sprint, or direct follow-up needed before the next planning run. Otherwise leave Sprint empty so work-planning can decide.

### Delivery version transitions

When triage finds clear evidence that customer delivery moved from one version, phase, or feedback round to the next:

1. Fetch the existing Project and relevant Task bodies before writing.
2. Mark the previous version/phase Task `Done` only when the source confirms it is delivered, reviewed, accepted enough to close, or superseded by the next version.
3. Create a new version/phase Task for the next concrete delivery effort when there is agreed executable work.
4. Link the new Task to the same Project and Customer as the previous Task when possible.
5. Copy only next-version context into the new Task:
   - agreed next version/phase
   - feedback and requested changes
   - deadline or promised delivery moment
   - source evidence such as meeting/email/chat/reference links
   - clear next action
6. Capture transition evidence on the Project.
7. Capture the same source on the previous Task when it explains closure/supersession, and on the new Task when it explains the next work.

Do not create version Tasks from vague ideas alone. Use Project context or `Blocked:` when the next delivery is not yet agreed.

### Sales to delivery handoff

When triage finds clear evidence that a Sales task has become accepted work:

1. Mark or move the Sales task to `Done` when the sales phase is genuinely complete.
2. Create a new Delivery task when actual execution work follows.
3. Link the Delivery task to the same Project as the Sales task when possible; the Project is the connection between sales and delivery.
4. Copy only delivery-relevant context into the Delivery task:
   - accepted scope
   - customer/project
   - agreed price or billing basis when explicit
   - source evidence such as email/chat/meeting/reference links
   - clear next action
5. Capture quote, estimate, invoice, and billing context on the Project as the commercial source of truth.
6. Capture transition evidence on the Sales task when it explains closure, on the Delivery task when it explains execution, and on the Project for durable scope/commercial context.
7. Add a short execution TODO when finance follow-up is likely, for example: `Execution: prepare/sync Moneybird invoice or quote if needed.`

Do not make a separate Admin/Moneybird task by default. The Delivery task should normally become the central follow-up task, and work-execution can attach Moneybird links/status there later.

## Lane Actions

- Archive: for every Gmail inbox thread collected in the run, make an explicit keep/archive decision. Archive after useful value is captured, or when the item is clearly low-value and no response/action is needed. Never archive task-needed mail.
- Gmail archive calibration from Sil cleanup: on `silveltman@gmail.com`, treat obvious no-action personal/promotional/transactional threads as archive-by-default after reading, especially promotions/discounts, newsletters/announcements, social notifications, package pickup confirmations, and telecom/invoice-available notices that do not need payment/action in triage.
- Keep personal appointment confirmations/reminders in inbox when they still help Sil show up or remember timing/location; archive only after the appointment is clearly past or handled.
- Keep `sil@full.dev` conservative: security/account notices, CI failures, customer/project mail, applicant mail, payment/routing issues, intake, and attachments stay in inbox unless captured and clearly no longer needing follow-up.
- Archive full Gmail threads with `gog -a <account> gmail thread modify <threadId> --remove INBOX --force --no-input`; use the Gmail lane thread `id`.
- Draft: email/Slack only when useful and low-risk. Keep external customer messages as drafts unless explicitly asked to send.
- Calendar/meeting: capture decisions/action items into existing work where possible. When a meeting marks a handoff or version transition, capture it on the Project and on both affected Tasks when it explains old-task closure and new-task creation. Create follow-up Tasks only for executable outcomes.
- Blocked/Triage: use when actionability is unclear; capture the exact missing decision.

## Report

One concise numbered list. One item = one concrete action/change/blocker. Use `Customer:`, `Project:`, `Task:`, `Archive:`, `Draft:`, `Failed:`, `Blocked:`. Suppress rediscovered facts and internal run metadata.

When archiving mail, include a concrete `Archive:` item unless it is part of a large grouped cleanup.

Preferred item shape:

```md
1. Type: [Title](link) optional description.
```
