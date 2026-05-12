---
name: triage
description: Turn new inbound communication into clean Notion task and project updates with correct status, context, references, and follow-up work. Use for incoming triage across Gmail, Slack, WhatsApp, calendar, meetings, attachments, approvals, blockers, and tasks left in Triage by weaker capture tools.
---

# Triage

Use for the incoming lane only: new communication, captured work, and tasks still in `Triage`.

## Default order
1. enrich existing task
2. apply clear status/lifecycle change
3. create concrete follow-up caused by that change
4. enrich existing project
5. create new task
6. ignore

## Source of truth
- Notion tasks are the execution layer.
- Important context belongs in the task body, not only in mail/chat/meetings.
- Projects hold durable context; executable context goes on the task people will use.
- Use the Notion API.
- Read properties through Tasks or Projects.
- Read bodies through `GET /v1/pages/{page_id}/markdown`.
- Before changing a task/project body, read it first. Never append blind or duplicate source facts.

## Collectors
Read `/Users/otis/.openclaw/workspace/TOOLS.md` first.

Default order:
1. `{baseDir}/scripts/collect_communication_lanes.py`
2. `{baseDir}/scripts/collect_tasks.py`
3. `{baseDir}/scripts/collect_projects.py`

Debug: `{baseDir}/scripts/collect_work_lanes.py`

## Matching
### Existing task
Match only with high confidence: same work, deliverable, follow-up chain, or revision round.
- enrich body with missing execution context
- keep status by default, except do not preserve `Triage` by default
- treat `Triage` as inbox signal: assign real status unless still genuinely unprocessed
- change status when the source clearly proves it
- preserve/correct project/date only when explicit
- treat `Waiting` and `Backlog` as strong signs the work already exists

### Existing project
Use only for durable project context that does not belong on one task.

### New task
Create only for concrete follow-up, commitments, deliverables, decisions, or unresolved work worth tracking.
- check `Waiting`, `Backlog`, and existing `Triage` first
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
- create execution task after accepted proposal/kickoff
- create invoice/admin follow-up when required
- remove stale blockers when resolved

Every touched task should end with a status. Do not use `Triage` as a resting status for understood work.

## Body and references
A finished update must stand alone.
- body includes source, key people, ask/decision, timing, blocker, expected follow-up when known
- copy quoted asks, decisions, attachment details, and source context when needed for execution
- explain status changes and follow-ups in plain language
- `References` is provenance, not a substitute for body context

Fill `References` when source artifacts matter: email, Slack, WhatsApp, meeting notes/recordings, shared docs, files, images, PDFs, attachments. Include both parent conversation and specific artifact links when both add value.

## Lane rules
- Gmail: archive only when safe and no reply is needed
- Gmail: before archiving, confirm the thread is currently in inbox
- Gmail: already archived/context-only threads are never reported as fresh archive actions
- Slack: never archive/hide
- WhatsApp: input only; never send from triage
- never send Gmail, Slack, or WhatsApp replies unless explicitly told

## Telegram summary
Use one continuous numbered list. No intro/outro.
- prefixes: `Task:`, `Project:`, `Archived:`, `Done:` when clearer
- use markdown links first, then short action phrase
- every archived email gets its own line: `Archived: [mailtitel](link)`
- include only mails triage actually archived in this run
- keep the real source link when one exists
- if nothing changed, send one short line saying no triage changes were needed

## State
- run logs: `/Users/otis/.openclaw/workspace/state/triage/runs/`
- checkpoint: `/Users/otis/.openclaw/workspace/state/triage/checkpoint.json`
- checkpoint ownership belongs to the caller or cron wrapper
