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
- **Updates** `collection://3715979e-268c-8068-8d90-000bb913f2d2`
- **Insights** `collection://1d65979e-268c-80a9-9f26-000bcfb57574`
- **Goals** `collection://2005979e-268c-80d1-8ecf-000b841762a2`
- **Sprints** `collection://3555979e-268c-807b-bdb4-000b86b48f90`

## Model

- Task = executable workload: a coherent unit of work that can be picked up as one effort and has a clear outcome.
- Project = durable finishable work bucket, scope, delivery phase, sprint package, proposal, prototype, or important internal outcome.
- Customer = stable account/context layer.
- Meeting/email/Slack/WhatsApp/calendar = source/context, not work bucket.
- Source context = any message, email, meeting, file, link, attachment, quote, decision, blocker, requirement, or reference that may matter later.
- Someday = non-executable idea, maybe-later note, or vague exploration.
- Sprint = Saturday-Friday planning week.

New Customer pages always get a fitting page emoji.

Treat Tasks as workloads, not atomic message fragments. A good Task is often a small work package: one coherent delivery/admin/sales outcome with the checklist and source context needed to execute it. If multiple small actions belong to the same domain and will naturally be handled together at the same time, capture them in one Task instead of making tiny duplicates.

Examples:

- Two small development fixes for the same customer website -> one Task such as `Small fixes for Customer Website`.
- Create an estimate and send it to the customer -> one Task such as `Prepare and send estimate for Customer`.
- Same admin action for several customers -> one batch Task with a customer checklist, unless timing, responsibility, or risk differs.
- Separate domains, separate timing, separate owner, or separate delivery context -> separate Tasks.

Tasks may link directly to Customer when useful. Create/link a Project only for durable scope, multi-step delivery, retainers/sprints, proposals, repositories, invoiceable customer work, or context that must survive multiple tasks. Execution details for one action belong on Tasks.

If work will need billable hours, a proposal/estimate, delivery tracking, or invoice follow-up, create or link a Project even when the first visible action is tiny. The Task can stay small, but the commercial/delivery context belongs in a Project because the workflow usually spans scoping, doing the work, communication, and invoicing.

Whenever creating a Project, create or link at least one concrete Task in the same workflow. If the first Task is unclear, create a scoped planning/scoping Task instead of leaving the Project empty.

## Routing

1. Read item + source context.
2. Decide: Task, Project/Customer update, source-only context, or Someday.
3. If Task: concrete name, real status, Customer relation when identifiable; Project relation only when durable context is warranted.
4. Prefer updating an existing broader Task/work package over creating a narrow sibling Task.
5. If new context is just one checklist item inside an active package, append it to that package body instead of creating another Task.
6. Preserve trace via relations/body.

## Context Capture

All new context or references to context must be captured.

Capture context when it includes customer requirements, decisions, approvals, preferences, deadlines, scope, blockers, files, links, technical notes, meeting decisions, source references, or evidence that work is done, waiting, canceled, superseded, or deprioritized.

Capture into the most specific place:

1. Existing Task, if it affects an active workload.
2. Existing Project, if it is durable context but not a specific executable action.
3. Customer, if it is account-level preference/history/context.
4. New Task, if it is executable and not already captured.
5. New Project plus first Task, if it creates a durable bucket and concrete next action.

Source context should be compact, traceable, and useful: source type, date, sender/source, link/reference when available, and the decision/actionable fact. Do not dump huge raw transcripts unless the source itself is the deliverable.

## Task Status

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

Task trace pattern. Source/routing context belongs in dated trace/context, usually below any active execution/review section.

```md
### YYYY-MM-DD - Source/update label

- Captured change/action context.
- Links, dates, people, source page/thread.
- Status/project/sprint reason, if relevant.
```

Project body is loose durable context. Use headings that fit the project; do not force all sections.

```md
## Outcome

Finishable result.

## Scope / agreements

- Commercial, timing, ownership, agreed scope.

## Current context / decisions

- Current state, decisions, blockers, constraints.

## Delivery notes

- Notes that survive across tasks.

## References

Primary source links/mentions.
```

Allowed: add/remove/rename sections when clearer. Keep durable decisions, scope, links, and constraints easy to scan.

## Constraints

- Ask before destructive, irreversible, privacy-sensitive action.
- Use real Notion property/status names. Fetch schema when unsure or before writes that need exact names/options.
- Do not hallucinate fields.
- Compress duplicated old task bodies when migrating to Projects.
