---
name: triage
description: Turn new inbound communication into clean Notion work-package and project updates with correct status, context, references, and follow-up state. Use for incoming triage across Gmail, Slack, WhatsApp, calendar, meetings, attachments, approvals, blockers, and tasks left in Triage by weaker capture tools.
---

# Triage

Use for the incoming lane only: new communication, captured work, and tasks still in `Triage`.

Notion `Tasks` are concrete execution pieces under a Project. Small tasks are fine when they are actionable and belong to a clear Project; broad context belongs on the Project, and customer relationship context belongs on the Customer.

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
- Workspace model: Customers hold relationship context; Projects hold durable work context; Tasks and Meetings hang off Projects.
- Notion tasks are the execution layer: create them for concrete pieces of work that can be linked to the right Project.
- Important context belongs in the task body, not only in mail/chat/meetings.
- Projects hold durable context; executable context, batches of related improvements, approvals, and waiting/follow-up state go on the task people will use.
- Use the Notion API.
- Read current data source schemas before relying on relation/property names.
- Read properties through Tasks or Projects; use Customer context through Projects, not direct Task <> Customer links.
- Every new Delivery/Admin/Follow-up task must have a Project relation before the run is considered complete. If the right Project does not exist yet, create or update the smallest durable Project first, link it to the right Customer, then create/link the task.
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

Project collector rule:
- the default Projects lane is active context only: `Discovery`, `Planned`, `In Progress`, and `Paused`
- do not include `Completed` or `Canceled` projects as ordinary matching candidates
- the default Projects lane returns properties only, not body markdown, to keep context compact
- fetch project body markdown only for a likely match, an existing relation, or a project you are about to update
- closed projects may still be fetched through exact relations/search when needed to explain historical context, but do not link new execution tasks to them unless Sil explicitly says the closed project is being reopened

## Matching
### Existing task
Match only with high confidence: same work, deliverable, follow-up chain, or revision round.
- enrich body with missing execution context
- before adding context, read the body and verify the fact/source/status is not already captured
- if the item is already captured, do not rewrite it just to make a fresh update
- keep status by default, except do not preserve `Triage` by default
- treat `Triage` as inbox signal: assign real status unless still genuinely unprocessed
- change status when the source clearly proves it
- preserve/correct project/date only when explicit
- treat `Waiting` and `Backlog` as strong signs the work already exists

### Existing project
Use for durable work context and as the required parent for concrete tasks.
- if a task-worthy item clearly belongs to an existing project, link/update that project before touching the task
- if no suitable project exists but the work is real, create a compact project named after the durable work stream, not the single tiny action
- make sure the project is linked to the right Customer; if the Customer is missing but identifiable from domain/company/source context, create it with minimal properties

### New task
Create only for concrete commitments, deliverables, decisions, or unresolved work worth tracking that does not fit an existing work package.
- if an email task is quick enough to complete directly from the mailbox, do not create a Notion task; keep it in the inbox and report it as mailbox work to do from Gmail
- check `Waiting`, `Backlog`, and existing `Triage` first
- also check active/recent related tasks by customer/project/deliverable/source before creating anything new
- find or create the matching Project first, and link the task to it; do not leave new tasks projectless
- link Customer through the Project; avoid filling legacy direct Task <> Customer relations
- if an existing task can hold the work without losing clarity, update that task instead of creating a sibling
- do not create a separate task for routine awaiting, approval, or next-check reminders; put that state in the existing task and set `Waiting`
- split only when the new work is genuinely separate: different deliverable, later phase, different owner/context, or too large to keep clear
- give every new task an initial status
- use `Triage` only when the item is still unprocessed incoming work
- assign real execution status whenever readiness is clear

### Existing projectless tasks
If triage finds a concrete task without a Project relation:
- resolve the right existing Project from source context, customer/domain, meetings, related tasks, or inline source links in task bodies
- if no suitable Project exists and the work is still valid, create the smallest durable Project and link it to the right Customer
- link the task to that Project before reporting the task as handled

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
- add Moneybird source links inline in the task body for the accepted quote and draft invoice when available
- restructure the task body for execution: put current delivery scope/next actions at the top, keep relevant proposal context/agreements below, and remove or compress only noise
- create separate Delivery tasks only when one accepted proposal creates multiple distinct work packages

## Body, summary, and source traces
A finished update must stand alone, with execution state in `Summary` and only useful source/context traces in the body.

Use Notion fields this way:
- `Summary` = current state / short assignment. Update it whenever the current state materially changes.
- Body = only context that is not already obvious from title/properties. Prefer short trace bullets with the source URL inline on the same line as the fact it supports.
- Do not create property-metadata filler in the body. If there is no extra context/source beyond title, status, assignee, dates, project, or summary, leave the body blank.
- Source links/artifacts belong in the body, inline with the relevant context bullet. Use clickable URLs where possible; use raw URIs for schemes Notion strips, such as `whatsapp://` and local `file://`.

Default task body structure:
```md
### <mention-date start="YYYY-MM-DD"/> - Triage update
- Concrete source-backed context or decision. [Source label](https://source-url)
- Follow-up or blocker only if it is not already obvious from properties.
```

Body rules:
- use Notion date mentions in trace headings when writing via API, e.g. `<mention-date start="2026-05-31"/>`
- use the original source/context date, not the migration/write date
- attach sources inline to the relevant bullet; do not create a separate source list unless one source supports the whole trace
- include key people, ask/decision, timing, blocker, and expected follow-up/waiting state when known and useful
- copy quoted asks, decisions, attachment details, and source context only when needed for execution
- never add body content that only repeats title/properties; blank is better than duplicate noise
- never lose real source context; compress only obvious duplication/noise

## Lane rules
- Gmail: never archive emails or threads that clearly still need a reply from Sil
- Gmail: archive only when safe and no reply is needed
- Gmail: if a thread contains a concrete ask, proposal, collaboration request, scheduling request, approval request, unanswered customer/vendor message, or any other reply-needed signal, keep it in the inbox unless Sil explicitly says to archive it
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
- include task/project lines only for net-new writes, real status changes, new inline source traces, or newly discovered action-relevant facts
- suppress lines for facts/status/source traces that were already present before the run, even if this run rediscovered them
- when a source email/thread was already archived before the run, do not report it again as archived
- do not include checkpoint success, run-result paths, internal completion metadata, or other runtime-only status
- keep the real source link when one exists
- if nothing changed, send one short line saying no triage changes were needed

## State
- State and checkpoints belong to the caller/runtime, not the skill.
- If bundled scripts need local state, pass it via runtime configuration such as `TRIAGE_STATE_DIR`.
- Advance checkpoints only after the full requested run succeeds.
