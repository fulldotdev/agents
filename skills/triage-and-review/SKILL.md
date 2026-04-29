---
name: triage-and-review
description: General workflow skill for turning incoming communication and existing Notion context into clean task and project updates, plus periodic review and cleanup of the broader work system. Use for triaging new inbound items, finding the right existing task, matching context to current work, enriching tasks or projects, creating a new task only when needed, and running weekly reviews to clean, reset, and prioritize work.
---

# Triage and review

## Goal
Keep work context clean and usable.

This skill is the general workflow layer between:
- incoming communication
- existing Notion tasks and projects
- execution-ready work

Use it in three modes:
- normal conversations that need task/context lookup or matching
- full triage runs that process new incoming items
- weekly review runs that clean, reset, and prioritize the broader work system

## Source of truth
The Tasks database is the execution layer and should be treated as the main source of truth for actionable work context.

That means:
- important context should be written into the task itself
- tasks should stand on their own without reopening Slack, WhatsApp, Gmail, or meeting notes
- links to source systems are useful as references, but they are not a substitute for putting the real context in the task
- when work is actionable, the execution-relevant context belongs in the task body, not only in external channels

Projects can hold durable background context, but executable context should still be placed on the task that someone will act from.

## Notion body access
Use the Notion API when reading or writing Notion content for this workflow.

Important distinction:
- data source and page queries return structured properties
- full human-readable page bodies should be read through the markdown endpoint: `GET /v1/pages/{page_id}/markdown`

The markdown endpoint returns page body content only. It does not include task properties like status, project relations, dates, assignee, formulas, or rollups.

So for a complete task view:
1. read properties through the Tasks data source or page API
2. read the real page body through the markdown API when body context matters
3. combine those results in the caller or collector layer

## Available collectors
Read `/Users/otis/.openclaw/workspace/TOOLS.md` before acting so lane and tool assumptions come from the current workspace.

### Incoming collectors
- `/Users/otis/.openclaw/skills/triage-and-review/collect_communication_lanes.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_slack.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_gmail.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_whatsapp.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_calendar.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_meetings.py`

Lane-specific collection logic lives in the lane files themselves. Shared utilities and constants live in `task_triage_common.py`.

### Existing work collectors
- `/Users/otis/.openclaw/skills/triage-and-review/collect_work_lanes.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_tasks.py`
- `/Users/otis/.openclaw/skills/triage-and-review/collect_projects.py`

## What each collector is for
### `collect_communication_lanes.py`
Canonical incoming collector.
Use this when you want the full incoming set for an explicit window.

It collects:
- Slack
- Gmail
- WhatsApp
- calendar
- meetings

Pass `--after <YYYY-MM-DD>` and optionally `--before <YYYY-MM-DD>`.
Treat these as date boundaries, not exact timestamps.
For overlapping triage runs, it is correct to include the previous day and the current day again so multi-day conversations remain visible.
The caller is responsible for choosing the date window.
The collector should be treated as stateless with respect to cron success checkpoints.

### `collect_work_lanes.py`
Canonical existing-work collector.
Use this when you want the main execution context set in one pass.

It collects:
- tasks
- projects

Use this as the default existing-work lookup for full triage runs and cron wrappers.
Reach for the individual collectors only when you specifically need one source in isolation.

Important: this collector does not fetch full Notion page bodies. For tasks, it gives the Notion `properties` object, not the real page body. If the actual task body may contain execution-relevant context, fetch it separately through the markdown API.

### `collect_tasks.py`
Canonical existing-task collector.
Use this when you need to know what work already exists before matching, enriching, or creating tasks.

It collects:
- open tasks
- recently closed tasks that were edited recently, so premature closure can still surface

Important: this collector does not fetch full Notion page bodies. It returns the Notion `properties` object only. If a task's real body content matters, read it separately through `GET /v1/pages/{page_id}/markdown`.

### `collect_projects.py`
Direct project-context collector.
Use this when project-level context is useful for matching, resolving ambiguity, or enriching durable background context.

It is a standalone utility, not part of the incoming collector.

### Lane-specific collectors
Use the standalone incoming collectors when you want to inspect, debug, or rerun one source in isolation.

`collect_calendar.py` is the calendar-events collector.
Use this when you want actual calendar entries for an explicit window, including items that are not represented in the Meetings database.

It collects:
- Google Calendar events across the configured calendar accounts

Pass `--after <YYYY-MM-DD>` and optionally `--before <YYYY-MM-DD>`.
Treat these as date boundaries, not exact timestamps.

`collect_gmail.py` supports three modes:
- default with no params: current inbox (`in:inbox`)
- `--query "..."`: explicit Gmail query
- `--after <YYYY-MM-DD> [--before <YYYY-MM-DD>]`: explicit date window

For Slack, WhatsApp, meetings, and combined incoming collection, pass explicit date windows. Do not rely on hidden cron defaults in those scripts.

## Core workflow
### General workflow
When handling work context:
1. collect the relevant source context
2. collect existing tasks if matching against current work matters
3. collect projects too when project-level ambiguity or durable project context matters
4. decide whether the new info belongs on an existing task, an existing project, a new task, or nowhere
5. write the useful context into Notion cleanly
6. leave the execution layer with clearer work than before

### Full triage run
For a cron or full triage pass:
1. run `collect_communication_lanes.py` with an explicit window
2. run `collect_work_lanes.py`
3. compare incoming items against existing tasks and relevant project context
4. enrich existing work where confidence is high
5. create a new task only when needed
6. decide lane follow-up actions from the triage result
7. send a short Telegram summary after a successful run

If a caller only needs one slice of existing work, it may still use `collect_tasks.py` or `collect_projects.py` directly, but the default full-run path should use `collect_work_lanes.py`.

The cron is responsible for its own windowing, checkpoint logic, scheduling behavior, and exact step order.
For overlapping date-based runs, keep the windows simple and let the triage logic recognize recurring context across days.
Those concerns should not live implicitly inside the general triage scripts.
Use one cron-owned checkpoint for the whole workflow, not separate collector-owned checkpoints.
Write that checkpoint only after the full triage run succeeds, including lane actions.

### Weekly review run
For a weekly review pass:
1. run `collect_work_lanes.py`
2. collect any extra project, task-body, or calendar context needed to judge the real state of work
3. scan for stale, duplicate, blocked, misframed, or misplaced items
4. clean up statuses, project relations, and task framing where confidence is high
5. close, cancel, merge, or de-prioritize work when clearly justified
6. surface blockers, waiting items, and priority decisions for the coming week
7. send a short Telegram summary after a successful run

A weekly review is broader than inbound triage.
It is allowed to improve the existing work system even when there is no new incoming communication.
Prefer conservative cleanup over aggressive reshaping.
When a meaningful decision is unclear, surface it instead of forcing a change.

## Core decision order
### For inbound triage
For each inbound item, decide in this order:
1. Enrich an existing task
2. Enrich an existing project
3. Create a new task
4. Ignore it

Prefer enriching over creating.
Prefer one task per meaningful work chunk, not per small message.
When an inbound item maps to an existing task that is `Waiting` or `Backlog`, treat that as the primary destination unless there is strong evidence that the inbound item created a separate workstream.

### For weekly review
For each existing work item, decide in this order:
1. Keep and enrich it
2. Correct its status, project relation, date, or framing
3. Merge it into a stronger existing task when it is clearly duplicate or fragmented
4. Mark it `Done` or `Canceled` when the work is clearly complete, dead, or notification-only
5. Leave it unchanged and surface it as a decision if confidence is not high

Prefer cleanup and clarification over creating new tasks.
Do not create weekly-review tasks just to restate existing messy work unless a genuinely new tracked work item is needed.

## Matching rules
### Existing task
Use a high confidence threshold. Match only when the item clearly belongs to the same executable work, deliverable, revision round, or follow-up sequence.

When multiple plausible tasks exist, prefer the already-existing task with the strongest execution match over creating anything new. Default to adding onto an existing task when the topic, deliverable, or follow-up sequence is clearly the same.

If matched:
- enrich the task body with the useful context
- add a short Notion comment only when it adds real audit value
- do not mention @Sil Veltman by default
- preserve or add the right project relation
- preserve the existing status by default
- change status only when the new source context clearly proves the work state changed
- treat `Waiting` and `Backlog` as strong signals that the work already exists but is not active now
- preserve or correct dates when the intended timing is explicit from source context or user feedback
- when later user feedback corrects a triage decision, update the existing task directly instead of leaving the earlier triage interpretation in place

### Existing project
Use when the item is durable project context but not one specific task.

If matched:
- enrich the project body with durable context
- add a short Notion comment only when it adds real audit value
- do not mention @Sil Veltman by default
- add useful relations when relevant

### New task
Create one only for concrete next actions, follow-ups, commitments, deliverables, or unresolved work worth tracking.
Be conservative. Do not create a new task just because something might matter.
Before creating a task, explicitly check whether the item should instead be appended to an existing task in `Waiting` or `Backlog`.
Default to `Triage` for newly created tasks unless readiness for execution is explicit and high-confidence.
Use `Todo` only when the next action is concrete, scoped, and clearly ready to execute without Sil first needing to review, clarify, or prioritize it.
Do not create a task for a notification-only item when there is no meaningful follow-up, decision, or tracking value. Prefer ignoring it, or if already created and later clarified as notification-only, cancel the task.

### Ignore
If it is not actionable and not genuinely useful as task or project context, do not store it.

If the match is ambiguous, do not force it. Prefer project enrichment or a new task in `Triage`.

## Writing rules
The Notion page must stand on its own. Do not rely on reopening WhatsApp, Slack, Gmail, or meeting notes later.

When you create or enrich a task or project:
- copy the important context into the body
- summarize the ask, decision, blocker, follow-up, or change
- include the meaningful content from emails, Slack messages, WhatsApp messages, and meetings directly in the task when that content matters for execution
- include source channel and source link when available
- store important source links and artefacts in the `References` property when that property exists
- preserve enough detail that future humans or agents can understand the work without reopening the source

Do not dump raw noise.
Do not write “see WhatsApp”, “see Slack”, “see email”, or similar as a substitute for context.
Links and references support the task, but the task itself must contain the execution-relevant context.

## Task statuses
Use only:
- Backlog
- Triage
- Todo
- Doing
- Waiting
- Done
- Canceled

Status guidance:
- Todo: clear next action, fully scoped, and ready to execute now without Sil first needing to review, clarify, or prioritize it
- Doing: already underway
- Waiting: blocked on someone else, approval, or dependency
- Backlog: relevant, not active yet
- Done: clearly completed and worth preserving
- Canceled: clearly canceled, notification-only, or otherwise not worth tracking further, but worth preserving as a record
- Triage: relevant, but status, framing, priority, or execution-readiness is still uncertain

Bias toward `Triage` over `Todo`.
When unsure, use `Triage`.

## Allowed updates
You may:
- enrich existing tasks and projects directly
- write context into page bodies
- add source artefacts to the `References` property when available
- add short Notion comments
- change task statuses when justified
- create task-project relations when useful
- create new tasks when needed
- sharpen task framing so the execution skill can act with less ambiguity
- archive Gmail inbox items after successful task capture when it is clearly safe

## Lane follow-up actions
After triage decisions are made, a caller may take lane-specific follow-up actions based on the outcome.

The general pattern is:
1. capture or route the useful context first
2. decide whether a reply is needed
3. decide whether the inbox item still needs to stay visible in its source lane
4. only then perform safe follow-up actions such as archiving

Do not let lane actions replace triage.
Lane actions happen after the task and project decisions, not instead of them.

## Reply-needed rule
Treat an item as reply-needed when Sil still owes a meaningful response, confirmation, answer, or decision back into the source lane.

A reply-needed item should not be treated as archiveable just because its context was copied into Notion.
Capturing context and replying are separate decisions.

When in doubt, bias toward leaving the item visible rather than silent cleanup.

## Gmail rules
### Gmail archiving rule
Archive a Gmail item only after the task or project has been successfully created or enriched, or the mail has been confidently judged as low-value non-actionable inbox noise.

For triage-captured email, archive only when all of the following are true:
- the relevant context is now captured in Notion well enough that reopening the email is not necessary for normal execution
- a source link to the email or thread is preserved when available
- the context is safe to rely on outside the mailbox
- the email does not require a reply from Sil
- Sil does not still need the email to remain visible in inbox for reading or reply nuance
- the mail is not emotionally sensitive, legally sensitive, or otherwise high-risk to hide
- confidence is high

For non-actionable email that does not belong in Notion, archiving is also allowed when:
- no reply is needed
- it is clearly low-value, informational, promotional, transactional, or otherwise not worth keeping visible in inbox
- confidence is high

When in doubt, do not archive the mail.

## Slack rules
Leave Slack messages alone after triage capture.

## WhatsApp rules
Use WhatsApp as an input lane for triage context.

`wacli` supports reading history and sending messages, including quoted replies.
For this workflow:
- do not send WhatsApp replies
- do not treat WhatsApp as an outbound action lane

## Notion querying rule
Prefer targeted queries over broad search.

- Use the Tasks data source directly when seeding task context.
- Pull only a small batch first when possible.
- Expand into full page detail only for tasks that look actionable or relevant.
- If a reference is indirect or ambiguous, enumerate plausible candidates before picking one.
- When you need the actual human-readable task or project body, use the markdown API instead of block-children reads.
- Do not assume `collect_tasks.py` or `collect_work_lanes.py` already included the full body. They did not.

## Commenting rule
Use Notion comments sparingly as the page-local audit trail.

- Do not add a Notion comment by default just because a page changed.
- Add a short comment only when it adds real audit value that is useful on the page itself.
- Do not mention @Sil Veltman by default.
- Since the main notification stream is now Telegram, avoid Notion comments that only duplicate that notification.
- If a comment is added, it should say what changed in a compact way so the page still makes sense later.

## Weekly review guidance
A weekly review should look across the whole work system, not just recent inbound.

Focus areas:
- stale tasks that should be clarified, moved, closed, or canceled
- `Waiting` items that need follow-up or no longer deserve active attention
- `Backlog` and `Triage` items that are underspecified, duplicated, or misplaced
- tasks that are in the wrong status or missing the right project context
- project pages missing durable context that would reduce future ambiguity
- recently completed work that should be marked `Done`
- dead or notification-only tasks that should be marked `Canceled`
- next-week priorities, blockers, and open decisions worth surfacing

Review principles:
- be conservative with destructive cleanup
- prefer direct correction over leaving known bad states in place
- prefer merging into the strongest existing task over keeping fragmented duplicates
- preserve useful history and context when closing or canceling items
- avoid creating artificial work just to make the system look tidy
- when the right change is unclear, surface the ambiguity instead of guessing

## Telegram summary
After a successful full triage or weekly review run, send Sil a short Telegram summary.

This format is mandatory for both daily triage and weekly review. Do not switch to prose sections, headings, or generic recap text when reporting completed changes.

Use one continuous numbered list that may include:
- changed Notion tasks
- changed Notion projects
- archived emails

Use these prefixes as the default set:
- `Task:`
- `Project:`
- `Archived:`
- `Done:` when that reads clearer than a normal task update

The agent may add a new prefix when a specific use case clearly benefits from it, but the list should stay compact, logical, and easy to scan.
Do not invent extra prefixes casually.

Format lines like:
- `Task: [Task title](Notion link) aangevuld met ...`
- `Task: [Task title](Notion link) nieuw aangemaakt`
- `Task: [Task title](Notion link) op Done gezet`
- `Project: [Project title](Notion link) aangevuld met ...`
- `Archived: [Short human title](Gmail link)`

Ordering rule:
- group the numbered list by type instead of pure execution order
- first all `Task:` items
- then all `Project:` items
- then all `Archived:` items

Rules:
- include changed pages and any lane actions actually performed by the caller
- always use markdown links in the form `[Title](URL)`
- always put the link first and the action text after it
- use the task or project title as the Notion link text
- put the Notion URL in the markdown link target
- for emails, use a short human-readable title and the real Gmail link
- keep each line to one short human sentence fragment about what changed
- never guess, embellish, or invent missing context in the shared list
- if an item is vague or unclear, list it compactly as unclear and ask Sil for the missing context instead of pretending to know the action
- when an existing task was matched, mention status context when that is important to avoid implying active execution, especially for `Waiting` or `Backlog` tasks
- keep one continuous numbered list when there is more than one item
- if there is exactly one item, one single line is fine
- if a lane action did not happen, do not mention it
- if extra review notes, risks, or decisions are needed, put them after the numbered list as a separate very short block, not instead of the list

If nothing changed, send one short line saying no triage or review changes were needed.

## Feedback correction rule
When Sil gives direct feedback on a triage summary or numbered list, treat that feedback as authoritative correction for the affected items.

Examples:
- if Sil gives a specific date or day, set it
- if Sil says an item was only a notification, do not track it as an active task
- if Sil says an item should wait, set Waiting when that matches the actual state
- if Sil says the work already had an existing task, prefer that existing task and merge the context there
- if Sil says the prior status or sprint placement should have been respected, preserve that status or sprint by default for similar cases

Apply the correction directly and keep future runs aligned with that preference or rule when the same pattern appears again.

## State
- run logs: `/Users/otis/.openclaw/workspace/state/triage/runs/`
- checkpoint path exists if a cron or wrapper wants to use one: `/Users/otis/.openclaw/workspace/state/triage/checkpoint.json`
- use a single checkpoint for the full triage workflow
- checkpoint ownership belongs to the caller, not implicitly to the general collectors
- write the checkpoint only after the full workflow succeeds, not after collection alone
