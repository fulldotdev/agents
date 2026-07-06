---
name: work-management
description: "Canonical Notion work model: database roles, routing, relations, body conventions, schema lookup, and safe writes."
---

# Work Management

Global Notion work model. Reference skill only; it does not collect context, plan weeks, run triage, execute Tasks, or authorize writes by itself. Write only when user/automation scope allows.

## Schema

This skill is the source of truth for workflow meaning. Fetch Notion schema only when exact property names, option names, relation targets, IDs, or write validation are needed. Do not rely on Notion schema descriptions for rules.

## Databases

IDs are bootstrap hints. Prefer finding by name, then verify live metadata/schema.

- **Tasks** `collection://1cb5979e-268c-80e9-bd7d-000b00ac4424`
- **Projects** `collection://4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae`
- **Customers** `collection://2635979e-268c-8191-b322-000bd3109d1c`
- **Meetings** `collection://1cb5979e-268c-808d-888d-000bfa3a527c`
- **Someday** `collection://8b6245be-419a-4203-97e4-f7660514c661`
- **Insights** `collection://1d65979e-268c-80a9-9f26-000bcfb57574`
- **Goals** `collection://2005979e-268c-80d1-8ecf-000b841762a2`
- **Sprints** `collection://3555979e-268c-807b-bdb4-000b86b48f90`

## Model

- Task = executable workload: a coherent unit of work that can be picked up as one effort and has a clear outcome.
- Project = native real project/commercial delivery bucket: invoiceable customer work, proposal, prototype, repository, retainer, or durable customer scope.
- Customer = stable account/context layer.
- Meeting/email/Slack/WhatsApp/calendar = source/context, not work bucket.
- Source context = any message, email, meeting, file, link, attachment, quote, decision, blocker, requirement, or reference that may matter later.
- Someday = non-executable idea, maybe-later note, or vague exploration.
- Sprint = Saturday-Friday planning week.

New Customer pages always get a fitting page emoji.

Customer names use lowercase domain/repo-style handles. Prefer the recognizable domain or repository root: strip protocol and `www.`, strip the TLD when that leaves a clear handle, lowercase everything, and keep meaningful hyphens only when they are part of the recognizable domain/brand. Do not title-case Customer names unless Sil explicitly asks for display-name cleanup. Examples: `teveo`, `fayn`, `mandendeco`, `fulldev`, `smallgiants`, `skantrae`. Rationale: Customers started as project/repo-like work anchors, so preserve the compact handle style instead of drifting into mixed display names like `Small Giants` or `Skantrae`.

Treat Tasks as workloads, not atomic message fragments. A good Task is often a small work package: one coherent delivery/admin/sales outcome with the checklist and source context needed to execute it. If multiple small actions belong to the same domain and will naturally be handled together at the same time, capture them in one Task instead of making tiny duplicates.

Examples:

- Two small development fixes for the same customer website -> one Task such as `Small fixes for Customer Website`.
- Create an estimate and send it to the customer -> one Task such as `Prepare and send estimate for Customer`.
- Same admin action for several customers -> one batch Task with a customer checklist, unless timing, responsibility, or risk differs.
- Separate domains, separate timing, separate owner, or separate delivery context -> separate Tasks.

Tasks may link directly to Customer when useful. Create/link a Project for real project/commercial scope: invoiceable customer work, proposals, prototypes, repositories, retainers, or context that must survive multiple tasks. Execution details for one action belong on Tasks.

If work will need billable hours, a proposal/estimate, delivery tracking, or invoice follow-up, create or link a Project even when the first visible action is tiny. The Task can stay small, but the commercial/delivery context belongs in a Project because the workflow usually spans scoping, doing the work, communication, and invoicing.

Whenever creating a Project, create or link at least one concrete Task in the same workflow. If the first Task is unclear, create a scoped planning/scoping Task instead of leaving the Project empty.

## Commercial and Delivery Structure

Projects are the commercial and delivery container for invoiceable customer work. Quotes, estimates, invoice links, accepted scope, billing basis, and payment/follow-up context belong primarily on the Project, even when a Task triggers the commercial action. Keep Tasks executable and independent from the exact invoicing schedule.

Sales/admin Tasks may still exist for work such as preparing and sending a quote, checking invoice status, or syncing Moneybird. Link those Tasks to the Project and capture the resulting quote/invoice context on the Project.

For customer delivery that naturally moves through versions, phases, or feedback rounds, create separate Tasks under the same Project for each concrete delivery effort. Examples:

- `AMB Detailing website - v1`
- `AMB Detailing website - v2`
- `AMB Detailing website - v3`

Each version/phase Task should contain only the work, feedback, checklist, source context, and acceptance criteria needed for that version. The Project keeps durable scope, commercial context, cross-version decisions, and references.

When a meeting, approval, message, or delivery note marks a transition between Tasks, treat it as transition evidence. Link or capture it on:

1. The Project, when it affects durable scope, delivery, or commercial context.
2. The previous Task, when it proves completion, review, cancellation, or supersession.
3. The next Task, when it creates new executable work.

Use the same transition pattern for sales-to-delivery handoffs: the Project is the bridge; the Sales Task closes when accepted; the Delivery Task starts with only delivery-relevant context.

## Routing

1. Read item + source context.
2. Decide: Task, Project/Customer update, source-only context, or Someday.
3. If Task: concrete name, real status, Customer relation when identifiable; Project relation only when durable context is warranted.
4. Prefer updating an existing broader active Task/work package over creating a narrow sibling Task.
5. If new context is just one checklist item inside an active package, append it to that package body instead of creating another Task.
6. If the best matching Task was set to `Done` before the current local date, be more willing to create a new related Task under the same Project/Customer instead of reopening or appending, unless the new source only proves/corrects the completed work.
7. If the best matching Task was set to `Done` on the current local date, it may still be reopened or moved back when the fresh source shows the closure was premature.
8. If the best matching Task is `Waiting`, append related blocker/decision/context to that Task and move its status only when the new source makes the next action executable.
9. Preserve trace via relations/body.

## Context Capture

All new context or references to context must be captured.

Capture context when it includes customer requirements, decisions, approvals, preferences, deadlines, scope, blockers, files, links, technical notes, meeting decisions, source references, or evidence that work is done, waiting, canceled, superseded, or deprioritized.

Capture into the most specific place:

1. Existing active Task, if it affects that workload.
2. Existing Project, if it is durable context but not a specific executable action.
3. Customer, if it is account-level preference/history/context.
4. New Task, if it is executable and not already captured.
5. New Project plus first Task, if it creates a durable bucket and concrete next action.

Completed Tasks older than the current local date are closure records. New executable follow-up after an older `Done` Task should usually become a new related Task, with transition/source context captured on the Project when durable.

Source context should be compact, traceable, and useful: source type, date, sender/source, link/reference when available, and the decision/actionable fact. Do not dump huge raw transcripts unless the source itself is the deliverable.

## Meeting Triage

Notion-generated meeting action points are low-quality hints, not source of truth. They often blur speakers/owners and invent tidy tasks from vague discussion.

For meeting processing, prefer Otis/Hermes triage:

1. Read the meeting title, notes, topics, and transcript references when available.
2. Extract explicit decisions, blockers, requests, durable context, and possible actions.
3. Update/link existing Customer, Project, or active Task before creating new Tasks.
4. Create a new Task only for real executable work with clear ownership/actionability.
5. Preserve ambiguity instead of assigning work to Sil by default.
6. Ignore weak auto-generated action points unless supported by meeting content.

Each processed meeting should resolve to one or more simple outcomes: no action, existing Task updated, new Task created, Project/Customer context updated, or needs Sil clarification.

## Client Sprints vs Weekly Sprints

Sil's `Sprints` database is the personal weekly planning layer. Teveo sprint packages are represented as Tasks named like `Teveo sprint 24` / `Teveo sprint 25`.

For routine client sprint work, create/update one Teveo sprint Task. Link that Task to the Teveo Customer and Sil's own weekly Sprint. Put selected tickets, current execution state, and meeting/monday context in the Task body. Link a Project when there is a real native project/commercial scope behind the work.

## Task Status

- Backlog = executable someday/soon work that is valid to keep, but not ready or important enough for the current Sprint/Todo lane.
- Todo = ready/executable.
- Doing = active work or work ready for Sil review.
- Waiting = blocked on person, dependency, decision, timing, customer, or vendor.
- Triage = unclear actionability, missing decision, or not routed yet.
- Done = work actually completed, verified, or safely finished through low-risk local/admin cleanup.
- Canceled = duplicate, superseded by a broader work package, moved to Someday, no longer executable, or explicitly dropped.

Do not mark customer-facing delivery Done unless explicit.

## Bodies

Read body via Notion markdown/body API before interpreting/changing. Never blind append.

Do not paste full transcripts, duplicate Project scope in Tasks, overwrite execution/review top sections, or edit autogenerated summary fields.

Keep bodies simple. For tiny personal/admin reminders where the title fully explains the action, an empty/light body is acceptable.

For non-trivial customer/work/money/delivery/sales Tasks, use headings and separate concise working context from references. Context should be a synthesized summary across sources, not a copied timeline.

Preferred body shape:

```md
## Next

Concrete next action(s).

## Context

Compact summary of the references: decisions, blockers, requirements, current state, and execution facts needed to do the work. Deduplicate repeated source facts.

## References

- Source/link/thread/file/reference 1.
- Source/link/thread/file/reference 2.
```

Heading order:

1. `## Waiting` when blocked, otherwise `## Next`.
2. `## Next` after `## Waiting` only when there are concrete follow-up actions despite the blocker.
3. `## State` for larger delivery tasks where current progress matters.
4. `## Decisions` only when decisions are the main execution input and need their own section.
5. `## Context` as the concise synthesized summary.
6. `## References` last, always as a bullet list.

Keep headings in English exactly as shown (`## Waiting`, `## Next`, `## State`, `## Decisions`, `## Context`, `## References`). Default task titles and body prose to English for consistency, especially internal/dev/process/agency work or mixed-source work. Use Dutch only when the task is clearly Dutch customer-facing communication/work. Keep source titles, file names, IDs, quotes, and references literal.

Keep `## References` complete enough to reopen the real sources: Slack threads/conversations, WhatsApp chats/messages, Gmail thread IDs, meetings, files, previews, Moneybird links, Discord/Codex/execution threads, and repo/branch refs when they matter. Group related references when needed, but do not drop source types just because Context summarizes them. Add `Done when:` only when it materially clarifies completion.

Tiny personal/admin reminders can still have an empty/light body. Do not force headings when the title fully explains the work.

Due dates mean real deadlines or real follow-up dates, not historical guilt markers. If a follow-up date is fuzzy, write it in the body instead of setting a fake due date.

Avoid dated trace sections in Task bodies. Use them only when a transition/audit note is genuinely needed and cannot be represented as concise Context + References.

Project body is loose durable context. Use only the sections that matter; do not force all sections.

```md
## Outcome

Finishable result.

## Current state

- Where this stands now.

## Open loops

- Unresolved decisions, blockers, follow-ups, or loose ends.

## Commercials

- Quote, estimate, invoice, billing basis, payment, and follow-up context.
```

`Open loops` simply means unresolved loose ends. `Commercials` simply means money/scope/billing context. Skip either section when irrelevant.

Allowed: add/remove/rename sections when clearer. Keep durable decisions, scope, links, and constraints easy to scan.

## Constraints

- Ask before destructive, irreversible, privacy-sensitive action.
- Use real Notion property/status names. Fetch schema when unsure or before writes that need exact names/options.
- Do not hallucinate fields.
- Compress duplicated old task bodies when migrating to Projects.
