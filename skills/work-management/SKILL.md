---
name: work-management
description: "Route and maintain Notion-backed agency work. Use for Tasks, Projects, Customers, Sprints, Someday, direct Notion updates, source triage, weekly planning, monthly maintenance, prioritization, statuses, or Productive/Moneybird coordination tied to agency Tasks, Projects, or Customers."
---

# Work Management

This skill owns agency-work semantics. Live Notion owns current records and schema.

Read the matching workflow reference before acting:

- Broad Gmail, Slack, WhatsApp, calendar, meeting, Codex, or Notion intake: [triage.md](references/triage.md)
- Weekly review, Productive reconciliation, system review, or Sprint planning: [planning.md](references/planning.md)
- Monthly Todo, Someday, status, Project, skill, and automation maintenance: [maintenance.md](references/maintenance.md)
- Exact Notion property names, option names, relations, IDs, or write validation: [notion-schema.md](references/notion-schema.md)
- Productive or Moneybird actions coordinated with agency records: [commercial-coordination.md](references/commercial-coordination.md)
- Normal Task, Project, or Customer management and direct Notion updates: use this main skill plus the relevant domain skill.

Load multiple references only when the request genuinely crosses workflows.

## Model

- **Task**: accepted, executable work with one coherent outcome. Keep one next action and checkable acceptance criteria in the body.
- **Project**: a bounded outcome or commercial delivery scope with a clear completion point, usually comprising multiple independently managed Tasks.
- **Customer**: stable account context. Use a lowercase domain/repo-style handle and add a fitting page emoji when creating one.
- **Sprint**: Monday-Sunday commitment containing every Task intended for completion that week. Apply no numeric capacity limit.
- **Someday**: non-executable idea, maybe-later note, or vague exploration.
- **Source**: message, email, meeting, file, link, attachment, quote, decision, blocker, requirement, or other evidence. A Source provides context; executable work requires a routed outcome.

Tasks may link directly to a Customer. Use a Project when several Tasks contribute to one shared outcome or planned completion. Keep a larger coherent effort as one Task when a body checklist is enough to execute it.

Projects own the shared outcome, scope, commercials, cross-Task decisions, and delivery history. Tasks own execution, evidence, and acceptance criteria.

## Routing

1. Read the target item's full properties, Markdown body, and relevant source context before deciding or writing.
2. Route to an existing active Task, Project or Customer context, a new Task, a new Project plus first Task, Someday, or no action.
3. Prefer the existing active work package that owns the same outcome or commercial scope.
4. Add implementation points, blockers, preferences, and files to that package instead of creating duplicates.
5. Treat Tasks completed before today as closure records. Create a related follow-up Task for genuinely new execution; reopen today's completion when fresh evidence proves closure was premature.
6. Use `Waiting` while a concrete dependency prevents execution. When it clears, choose `Todo` or `Doing` from whether execution has started; apply no automatic transition.
7. Preserve source trace through relations and compact, reopenable references.

Routing is complete when every actionable source has one owning record, every non-action has a deliberate destination, and every write retains its source trace.

## Status

- **Todo**: accepted and executable, but not started. A Sprint relation expresses weekly commitment; Todo without a Sprint remains unscheduled.
- **Doing**: execution has started and remains unfinished, including between work sessions.
- **Waiting**: a concrete person, dependency, decision, timing condition, customer, vendor, approval, or review prevents execution.
- **Done**: completed and verified; customer work uses the evidence gates in `customer-work`.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable, or explicitly dropped.

Treat the Status property as authoritative; never infer status from body headings, age, Sprint membership, or activity. Apply no limit to Todo, Doing, or Sprint size. Keep started unfinished work in Doing unless a concrete dependency makes it Waiting.

Use due dates for real deadlines and follow-up dates.

## Project status

- **Discovery**: active sales, scoping, and proposal period before delivery commitment.
- **Planned**: delivery is approved or committed but has not started.
- **In Progress**: delivery has started.
- **Paused**: a deliberate project-level hold.
- **Completed**: the agreed Project outcome is delivered.
- **Canceled**: the Project is explicitly stopped.

Move Discovery to Planned when a concrete delivery commitment or approval exists.

## Context and bodies

Capture durable requirements, decisions, approvals, preferences, deadlines, scope, blockers, files, technical notes, and completion evidence in the most specific relevant Task, Project, or Customer. Preserve source titles, filenames, IDs, and quotes literally.

Change canonical properties and body content. Leave autogenerated summary fields to their generator.

For every non-trivial Task, use this status-independent body:

```md
## Next

Concrete next action.

## Done when

- [ ] Checkable completion criterion.

## Context

Compact, deduplicated execution context.

## References

- Reopenable source/link/thread/file reference.
```

Keep exactly one first `## Next` action. Keep multiple steps toward one outcome in the same Task; split independently managed outcomes. Keep the body structure stable when status changes. Add `## State` or `## Decisions` when useful, and keep `## References` last. Tiny reminders may have a light or empty body.

Write titles as observable outcomes and use the Task's working language. Preserve customer language, source titles, filenames, IDs, and quotes literally.

Project bodies are flexible. Use relevant sections such as `## Outcome`, `## Current state`, `## Open loops`, and `## Commercials`.

## Domain ownership

- `moneybird` owns estimates, invoices, recurring billing, and finance safety.
- `productive-io` owns hours evidence and time-entry writes.
- `monday-com` and `trackler-nl` own their read-only external context.
- `customer-work` owns scoped customer execution, customer-visible QA, preview, approval, release, and handoff.
- `customer-communication` owns customer-facing messages and their output format.

## Approval and completion

Obtain explicit approval before sending customer or vendor messages, publishing customer work or Moneybird documents, changing unclear finance data, deleting records or data, scanning broad private sources, restructuring databases or templates, or changing automation schedules.

Complete an in-scope change after proportional verification through tests, builds, browser checks, API readback, screenshots, document validation, or source confirmation. Leave the durable result, verification, state, next action, and useful links in Notion.

Use a concise numbered list for operational reports, multiple actions, decisions, blockers, or approval questions. Use `customer-communication` formatting for customer drafts.
