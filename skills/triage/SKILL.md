---
name: triage
description: Turn new inbound communication into clean Notion work-package and project updates with correct status, context, references, and follow-up state. Use for incoming triage across Gmail, Slack, WhatsApp, calendar, meetings, attachments, approvals, blockers, and tasks left in Triage by weaker capture tools.
---

# Triage

Use for the incoming lane only: new communication, captured work, and tasks still in `Triage`.

Notion `Tasks` are work packages/workloads, not tiny todos. One task can contain a batch of related improvements, approvals, delivery notes, and follow-up state.

## Default order
1. enrich existing work package/task
2. handle quick mailbox-only work directly from the inbox
3. apply clear status/lifecycle change
4. create concrete separate follow-up only when it is outside the current work package
5. enrich existing project
6. create new work package/task
7. ignore

Overlapping triage runs are expected. Prefer missing nothing over perfect separation, but deduplicate before writing or reporting: existing task, source artifact, fact, reference, and status change all count.

## Source of truth
- Notion tasks are the execution layer, but treat them as work packages/workloads rather than tiny todos.
- Important context belongs in the task body, not only in mail/chat/meetings.
- Projects hold durable context; executable context, batches of related improvements, approvals, and waiting/follow-up state go on the task people will use.
- Use the Notion API.
- Read properties through Tasks or Projects.
- Read bodies through `GET /v1/pages/{page_id}/markdown`.
- Before changing a task/project body, read it first. Never append blind or duplicate source facts.
- Never create Notion comments; Telegram summaries are the human-facing updates.

## Collectors
Resolve bundled collector paths relative to this skill directory.

Default order:
1. `scripts/collect_communication_lanes.py`
2. `scripts/collect_tasks.py`
3. `scripts/collect_projects.py`

Debug: `scripts/collect_work_lanes.py`

## Matching
### Existing task
Match only with high confidence: same work, deliverable, follow-up chain, or revision round.
- enrich body with missing execution context
- before adding context, read the body and references and verify the fact/source/status is not already captured
- if the item is already captured, do not rewrite it just to make a fresh update
- keep status by default, except do not preserve `Triage` by default
- treat `Triage` as inbox signal: assign real status unless still genuinely unprocessed
- change status when the source clearly proves it
- preserve/correct project/date only when explicit
- treat `Waiting` and `Backlog` as strong signs the work already exists

### Existing project
Use only for durable project context that does not belong on one task.

### New task
Create only for concrete commitments, deliverables, decisions, or unresolved work worth tracking that does not fit an existing work package.
- if an email task is quick enough to complete directly from the mailbox, do not create a Notion task; keep it in the inbox and report it as mailbox work to do from Gmail
- check `Waiting`, `Backlog`, and existing `Triage` first
- also check active/recent related tasks by client/project/deliverable/source before creating anything new
- if an existing task can hold the work without losing clarity, update that task instead of creating a sibling
- do not create a separate task for routine awaiting, approval, or next-check reminders; put that state in the existing task and set `Waiting`
- split only when the new work is genuinely separate: different deliverable, later phase, different owner/context, or too large to keep clear
- give every new task an initial status
- use `Triage` only when the item is still unprocessed incoming work
- assign real execution status whenever readiness is clear

Ignore non-actionable, low-value context.

## Status and derived actions
Triage must finish obvious state work now. Do not leave it for review.

With high-confidence source evidence, directly:
- unblock `Waiting` work
- move work into active status
- mark confirmed work `Done`
- mark declined/canceled/no-longer-relevant work `Canceled`
- convert accepted proposal/kickoff tasks from `Sales` to `Delivery`
- create invoice/admin follow-up when required
- remove stale blockers when resolved

Every touched task should end with a status. Do not use `Triage` as a resting status for understood work.

## Sales to delivery handoff
Tasks should be named after the durable work package, not the temporary sales phase. Avoid titles like `... proposal`; prefer outcome/work-package titles like `Ambdetailing website`.

When triage finds that a proposal task is accepted/done and should become execution work:
- keep the same Notion task by default so AI execution context stays in one place
- change task Type from `Sales` to `Delivery`
- set the Moneybird quote/estimate to accepted when needed
- prepare a new draft invoice in Moneybird when invoicing should follow from the accepted proposal
- add Moneybird references for the accepted quote and draft invoice when available
- restructure the task body for execution: put current delivery scope/next actions at the top, keep relevant proposal context/agreements below, and remove or compress only noise
- create separate Delivery tasks only when one accepted proposal creates multiple distinct work packages

## Body, summary, and references
A finished update must stand alone, with execution state easy to read at the top and append-only source context at the bottom.

Use Notion fields this way:
- `Summary` = current state / short assignment. Update it whenever the current state materially changes.
- `References` = all provenance and source artifacts: email, Slack, WhatsApp, meeting notes/recordings, shared docs, files, images, PDFs, attachments, preview links, repos, and other source URLs. Include both parent conversation and specific artifact links when both add value.
- Do not dump source links/files/threads in the body when they belong in `References`; the body may mention the source briefly in prose, but `References` is the actual link/provenance field.

Default task body structure:
```md
## Todo
[ ] Next concrete action
[ ] Second action if known
[ ] Reply / deliver / verify

## Scope / agreements
- Confirmed scope, decisions, price, deadline, owner.
- Keep this short. No full history here.

## Waiting
- Who/what we are waiting for, since when, and what unblocks it.
- Remove if not relevant.

---

## Context log
### YYYY-MM-DD — Triage update
- Append new context here.
- Summarize source content, decisions, asks, timing, and follow-up state.
- Put actual source links/files/threads in the `References` field, not here.
```

Body rules:
- keep the top sections clean, current, and execution-oriented
- append new communication/context under `Context log` with the date
- include source, key people, ask/decision, timing, blocker, and expected follow-up/waiting state when known
- copy quoted asks, decisions, attachment details, and source context when needed for execution
- explain status changes and follow-ups in plain language
- never lose context; compress or restructure only obvious duplication/noise

## Lane rules
- Gmail: never archive emails or threads that clearly still need a reply from Sil
- Gmail: archive only when safe and no reply is needed
- Gmail: if a thread contains a concrete ask, proposal, collaboration request, scheduling request, approval request, unanswered client/vendor message, or any other reply-needed signal, keep it in the inbox unless Sil explicitly says to archive it
- Gmail: before archiving, confirm the thread is currently in inbox
- Gmail: already archived/context-only threads are never reported as fresh archive actions
- Slack: never archive/hide
- WhatsApp: input only; never send from triage
- never send Gmail, Slack, or WhatsApp replies unless explicitly told

## Telegram summary
Send exactly one visible message: one continuous numbered list. No intro/outro, no separate status/checkpoint summary.
- prefixes: `Task:`, `Project:`, `Archived:`, `Done:` when clearer
- use markdown links first, then short action phrase
- every standalone archived email gets its own line: `Archived: [mailtitel](link)`
- if an archived email is the same source already reported in a task/project line, fold the archive action into that line instead of creating a duplicate-looking `Archived:` line
- include only mails triage actually archived in this run
- include task/project lines only for net-new writes, real status changes, new references, or newly discovered action-relevant facts
- suppress lines for facts/status/references that were already present before the run, even if this run rediscovered them
- when a source email/thread was already archived before the run, do not report it again as archived
- do not include checkpoint success, run-result paths, internal completion metadata, or other runtime-only status
- keep the real source link when one exists
- if nothing changed, send one short line saying no triage changes were needed

## State
- State and checkpoints belong to the caller/runtime, not the skill.
- If bundled scripts need local state, pass it via runtime configuration such as `TRIAGE_STATE_DIR`.
- Advance checkpoints only after the full requested run succeeds.
