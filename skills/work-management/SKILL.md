---
name: work-management
description: "Manage the Notion-backed work system. Use whenever Tasks, Projects, Customers, Sprints, Someday, triage, weekly planning, statuses, priorities, or work coordination with Productive or Moneybird are involved."
---

# Work Management

This skill owns work-system semantics. Live Notion owns current records and schema.

Read the matching workflow reference before acting:

- Broad Gmail, Slack, WhatsApp, calendar, meeting, Codex, or Notion intake: [triage.md](references/triage.md)
- Weekly review, Productive reconciliation, system review, or Sprint planning: [planning.md](references/planning.md)
- Exact Notion property names, option names, relations, IDs, or write validation: [notion-schema.md](references/notion-schema.md)
- Productive or Moneybird actions coordinated with agency records: [commercial-coordination.md](references/commercial-coordination.md)
- Normal Task, Project, or Customer management and direct Notion updates: use this main skill plus the relevant domain skill.

Load multiple references only when the request genuinely crosses workflows.

## Model

- **Task**: a compact, executable work package, usually spanning hours to a few days and normally less than one week. It may contain several tightly related actions when they serve the same stakeholder and concrete outcome or deliverable. Keep one current next action and checkable completion criteria in the body.
- **Project**: a bounded multi-work-item or multi-week outcome with a clear completion point, usually comprising multiple independently managed Tasks.
- **Customer**: stable account context. Use a lowercase domain/repo-style handle and add a fitting page emoji when creating one.
- **Sprint**: Monday-Sunday commitment containing every Task Sil has explicitly committed to work on substantially that week. Prefer completion within the week, but allow an externally delivered result just after Sunday when substantive execution is deliberately scheduled in the current Sprint. Apply no numeric capacity limit.
- **Goal**: an accepted desired outcome or durable personal/business result. Use Goal status `Backlog` when the outcome is real but has no active horizon or execution plan; move it to `3 maanden`, `1 jaar`, or another horizon only when consciously activated.
- **Someday**: non-executable maybe-later idea, vague exploration, or possible action that is not yet an accepted outcome.
- **Source**: message, email, meeting, file, link, attachment, quote, decision, blocker, requirement, or other evidence. A Source provides context; executable work requires a routed outcome.

Tasks may link directly to a Customer. One Customer may own multiple Projects when the commercial or delivery scopes have independent outcomes or completion points. Keep several actions in one Task when they belong to the same stakeholder, concrete outcome or deliverable, and short execution window. Split work when the stakeholder changes, an outcome can be completed independently, or it has its own blocker, approval, or deliverable. Use a Project when one broader outcome needs multiple Tasks or is likely to span more than about one week.

Projects own the shared outcome, scope, commercials, cross-Task decisions, and delivery history. Tasks own one compact work package, its execution evidence, and acceptance criteria. Do not turn Tasks into indefinite operational buckets; recurring work needs a bounded period or result.

## Area

Use Area to describe where a Task belongs. Choose the single Area that owns its primary outcome:

- **Delivery**: do work for customers, including implementation, support, coordination, QA, communication, and customer-specific operations.
- **Sales**: qualify a lead, define scope, prepare an offer, or win a commitment.
- **Growth**: grow Full.dev through marketing, positioning, partnerships, internal products, reusable assets, open-source work, or demand generation.
- **Admin**: operate the business or work system, including finance, legal, tooling, and internal coordination.
- **Personal**: non-business work.

Choose Area from the primary outcome, not merely from the linked Customer or Project. Work intended to win new or expanded business is Sales; other work done for a customer is Delivery.

## Routing

1. Read the target item's full properties, Markdown body, and relevant source context before deciding or writing.
2. Route to an existing active Task, Project or Customer context, a new Task, a new Project plus first Task, Someday, or no action.
3. Reuse an active Task only when the incoming work belongs to the same stakeholder, concrete outcome or deliverable, and short execution window.
4. Add tightly related calls, preparation, documents, follow-up, blockers, preferences, and files to that Task instead of creating action-level duplicates.
5. Split a separate Task when the stakeholder changes or the work has an independently completable outcome, deliverable, blocker, or approval. Group related Tasks in a Project when the broader outcome has multiple work items or is likely to span more than about one week.
6. Treat Tasks completed before today as closure records. Create a related follow-up Task only when genuinely new execution actually arrives; do not keep or create dormant Tasks for hypothetical future requests.
7. Create a Task for Sil only when Sil owns a concrete action, decision, deliverable, or follow-up. Work owned by another person belongs in Project or source context until Sil receives an executable responsibility.
8. Use `Waiting` while a concrete dependency prevents execution. When it clears, choose `Todo` or `Doing` from whether execution has started; apply no automatic transition.
9. Preserve source trace through relations and compact, reopenable references.

Routing is complete when every actionable source has one owning record, every non-action has a deliberate destination, and every write retains its source trace.

## Status

- **Todo**: accepted and executable, but not started. A Sprint relation expresses weekly commitment; Todo without a Sprint remains unscheduled.
- **Doing**: execution has started and remains unfinished, including between work sessions.
- **Waiting**: a concrete person, dependency, decision, timing condition, customer, vendor, approval, or review prevents execution.
- **Done**: completed and verified; customer work uses the evidence gates in `customer-work`.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable, or explicitly dropped.

Treat the Status property as the sole source of truth. Never write `Status`, `State`, `Todo`, `Doing`, `Waiting`, `Done`, or `Canceled` as a body field or heading, and never infer status from body headings, age, Sprint membership, or activity. Keep blockers, progress facts, decisions, and completion evidence in `## Blocker`, `## Context`, `## Decisions`, or the checklist without restating the status. Apply no limit to Todo, Doing, or Sprint size. Keep started unfinished work in Doing unless a concrete dependency makes it Waiting.

When closing a Task, reconcile the body in the same write. For `Done`, close `## Next`, resolve or intentionally supersede every completion criterion, and preserve verification evidence. For `Canceled`, record the routing or cancellation reason in normal context, remove obsolete Sprint and Due properties, and leave no body text that implies active execution.

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

Keep exactly one first `## Next` action. Keep multiple tightly related steps in the same Task when they serve the same stakeholder and outcome or deliverable; split independently managed work or work for another stakeholder. Keep the body structure stable when the next action or status changes. Add `## Blocker` for a concrete dependency and `## Decisions` when useful, without duplicating the Status property; keep `## References` last. Tiny reminders may have a light or empty body.

Write compact titles that name the work package or observable outcome, not every substep. Prefer English titles unless the work is clearly conducted in Dutch; then use Dutch. Preserve customer language, source titles, filenames, IDs, and quotes literally.

Project bodies are flexible. Use relevant sections such as `## Outcome`, `## Current state`, `## Open loops`, and `## Commercials`.

## Domain ownership

- `moneybird` owns estimates, invoices, recurring billing, open balances, and finance safety; Rabobank owns observed bank receipts. Do not duplicate passive monitoring in Notion when the native system already surfaces it reliably. Create a Task only for an explicit action, decision, exception, approval, or cross-system follow-up that the native system does not own.
- `productive-io` owns hours evidence and time-entry writes.
- `monday-com` owns individual customer execution tickets. Do not copy those tickets into Notion. A bounded weekly Notion Task may still represent Sil's personal Fayn or TEVEO delivery commitment across monday tickets; monday remains the execution-detail source.
- `trackler-nl` owns its read-only coaching context.
- `customer-work` owns scoped customer execution, customer-visible QA, preview, approval, release, and handoff.
- `customer-communication` owns customer-facing messages and their output format.

## Approval and completion

Obtain explicit approval before sending customer or vendor messages, publishing customer work or Moneybird documents, changing unclear finance data, deleting records or data, scanning broad private sources, restructuring databases or templates, or changing automation schedules.

Complete an in-scope change after proportional verification through tests, builds, browser checks, API readback, screenshots, document validation, or source confirmation. Leave the durable result, verification, state, next action, and useful links in Notion.

When updating both a Task body and properties, write the body first and the canonical properties last, then read the page back. Workspace automations or Markdown page updates may reapply Sprint or Due defaults; for `Canceled` Tasks, explicitly clear Sprint and Due in the final property write and verify both are empty.

Use a concise numbered list for operational reports, multiple actions, decisions, blockers, or approval questions. Use `customer-communication` formatting for customer drafts.
