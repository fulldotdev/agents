---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, or Documents."
---

# Work management

This skill defines how work is stored and routed. Live Notion owns the current records and schema.

Load only the detail needed for the current operation:

- Before writing or interpreting a Task body, read [references/timeline.md](references/timeline.md).
- Before exact Notion property writes, read [references/notion-schema.md](references/notion-schema.md).

## Model

- **Task**: executable work bucket for one stakeholder and one outcome. It normally takes hours to a few days and less than one week.
- **Project**: a confirmed outcome with several independent Tasks or more than about one week of work.
- **Company**: an identifiable organization with reusable sales, delivery, finance, or relationship context.
- **Contact**: Dex owns people, contact details, LinkedIn profiles, and relationship context. Notion owns company-level sales and delivery context.
- **Sprint**: a Monday to Sunday commitment. When creating a Task, assign it to the current Sprint by default. Leave Sprint empty only when the request clearly belongs later, in the backlog, in Someday, or otherwise outside the current week.
- **Goal**: an accepted long-term outcome. Never edit this, treat as read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Source**: evidence such as a message, meeting, file, decision, blocker, or requirement. It becomes a Task only when Sil owns concrete work.
- **Document**: a findable, mutable work product or index entry, such as a brief, scope, research note, draft, spec, copy, or design.

## Routing

1. Read the target record's properties, body, and relevant source before deciding or writing.
2. Before creating a Task, search active Tasks. Reuse one when the stakeholder, outcome, and short execution window are the same.
3. Keep related preparation, calls, feedback, blockers, approvals, follow-up, and files on that Task. Split work when its stakeholder changes or a part can be completed independently.
4. Treat Tasks completed before today as closure records. New work normally gets a related Task. Do not keep dormant Tasks for hypothetical requests.
5. Create a Task only when Sil owns agreed work that must be tracked outside its source: a deliverable, multi-step action, deadline or dependency, or follow-up that outlives the conversation. Replies, acknowledgements, scheduling, forwarding, quick reviews, questions, ideas, and unconfirmed requests stay in their source unless they create that work.
6. Keep source links through relations and compact, reopenable Timeline locators.

## Area

Choose the single Area that owns the Task's primary outcome:

- **Delivery**: customer implementation, support, coordination, etc.
- **Sales**: qualify a lead, define scope, prepare an offer, etc.
- **Growth**: marketing, positioning, partnerships, internal products, reusable assets, open source, demand generation, etc.
- **Admin**: finance, legal, tooling, internal coordination, or the work system itself.
- **Personal**: non-business work.

## Status

- **Todo**: accepted and executable, but not started.
- **Doing**: execution has started and remains unfinished.
- **Waiting**: a concrete dependency prevents execution.
- **Done**: the outcome is completed and verified.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable, or explicitly dropped.

The Status property is authoritative. Record its evidence in the Timeline, but do not keep a second status in the body. A Task remains Doing between work sessions unless a concrete dependency makes it Waiting. When that dependency clears, use Todo if work had not started and Doing if it had.

Append the supporting source event before changing Status. Done is terminal unless Sil or a newer source reopens the same deliverable. When canceling a Task, clear obsolete Sprint and Due values in the final write and verify them. Use Due only for real deadlines or follow-up dates.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Paused`, `Completed`, and `Canceled`. Move Discovery to Planned when a concrete delivery commitment or approval exists.
