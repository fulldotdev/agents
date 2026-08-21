---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, or Documents. Use work-triage for recurring cross-channel intake."
---

# Work management

This skill defines how work is stored and routed. Live Notion owns the current records and schema.

Load only the detail needed for the current operation:

- Before writing or interpreting a Task body, read [references/timeline.md](references/timeline.md).
- Before creating, moving, or indexing mutable authored work, read [references/documents.md](references/documents.md).
- Before exact Notion property writes, read [references/notion-schema.md](references/notion-schema.md).
- For Moneybird actions connected to a work record, read [references/commercial-coordination.md](references/commercial-coordination.md) and use the `moneybird` skill.
- For a stale Notion AI Task Summary, read [references/summary-prompt.md](references/summary-prompt.md).

## Model

- **Task**: executable work for one stakeholder and one outcome. It normally takes hours to a few days and less than one week.
- **Project**: a confirmed outcome with several independent Tasks or more than about one week of work.
- **Company**: an identifiable organization with reusable sales, delivery, finance, or relationship context.
- **Person**: someone whose relationship context is worth retaining even when they are not in Google Contacts. Use Google Contacts as the address book; use Persons for researched or durable context that does not belong there.
- **Sprint**: a Monday to Sunday commitment. Add a Task only when Sil commits to substantial work that week. Todo without a Sprint is valid unscheduled work.
- **Goal**: an accepted long-term outcome. Keep it in `Backlog` until Sil activates it for a time horizon.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Source**: evidence such as a message, meeting, file, decision, blocker, or requirement. It becomes a Task only when Sil owns concrete work.
- **Document**: a findable, mutable work product or index entry, such as a brief, scope, research note, draft, spec, copy, or design.

Tasks may link directly to a Company. Create a Company only when the organization is identifiable and its account context is worth keeping. A mention, an unqualified name, or a person without an organization is not enough. Create `Target` records in bulk only for an explicitly requested prospect or research import.

Create a Project only when the work crosses the Task threshold above. A single draft, message, small fix, or short work package links directly to the Company.

## Routing

1. Read the target record's properties, body, and relevant source before deciding or writing.
2. Reuse an active Task when the stakeholder, outcome, and short execution window are the same.
3. Keep related preparation, calls, feedback, blockers, approvals, follow-up, and files on that Task. Split work when its stakeholder changes or a part can be completed independently.
4. Treat Tasks completed before today as closure records. New work normally gets a related Task. Do not keep dormant Tasks for hypothetical requests.
5. Create a Task for Sil only when Sil owns a concrete action, decision, deliverable, or follow-up. Work owned by someone else remains Company, Project, or source context.
6. Bound recurring work by a period or result. Do not use an indefinite operational Task.
7. Keep source links through relations and compact, reopenable Timeline locators.

Routing is complete when every action has one owner, non-actions have a deliberate destination, and every write retains its source.

## Area

Choose the single Area that owns the Task's primary outcome:

- **Delivery**: customer implementation, support, coordination, QA, communication, or operations.
- **Sales**: qualify a lead, define scope, prepare an offer, or win a commitment.
- **Growth**: marketing, positioning, partnerships, internal products, reusable assets, open source, or demand generation.
- **Admin**: finance, legal, tooling, internal coordination, or the work system itself.
- **Personal**: non-business work.

Expanded business is Sales; other customer work is Delivery.

## Status

- **Todo**: accepted and executable, but not started.
- **Doing**: execution has started and remains unfinished.
- **Waiting**: a concrete dependency prevents execution.
- **Done**: the outcome is completed and verified.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable, or explicitly dropped.

The Status property is authoritative. Record its evidence in the Timeline, but do not keep a second status in the body. A Task remains Doing between work sessions unless a concrete dependency makes it Waiting. When that dependency clears, use Todo if work had not started and Doing if it had.

Append the supporting source event before changing Status. Done is terminal unless Sil or a newer source reopens the same deliverable. When canceling a Task, clear obsolete Sprint and Due values in the final write and verify them. Use Due only for real deadlines or follow-up dates.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Paused`, `Completed`, and `Canceled`. Move Discovery to Planned when a concrete delivery commitment or approval exists.

## Ownership and approval

- Moneybird owns financial documents and open balances; Rabobank owns observed receipts.
- monday.com owns individual customer execution tickets.
- `work-execution` owns scoped implementation, verification, previews, release, and handoff. Its customer rules own customer-visible approval boundaries.
- Customer-communication owns customer-facing messages and their format.

Create a Notion Task around another system only for an explicit action, decision, exception, approval, or cross-system follow-up that the native system does not already surface reliably.

Get explicit approval before:

- sending customer or vendor messages
- publishing customer work or Moneybird documents
- changing unclear finance data
- deleting data
- scanning broad private sources
- restructuring databases or templates
- changing automation schedules

For an authorized change, write body evidence first and canonical properties last. Read back the result, then verify it with the relevant API, test, build, preview, screenshot, document check, or source confirmation.
