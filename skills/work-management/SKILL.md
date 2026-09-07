---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, Insights, or the Documents page."
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
- **Insight**: a durable internal note, finding, or piece of research that is not executable work and does not belong to a customer file.
- **Document**: a substantial internal reference or long-form working page. Store it as a child of the regular Documents page, never as a database record.
- **Source**: evidence such as a message, meeting, file, decision, blocker, or requirement. It becomes a Task only when Sil owns concrete work.

## Files

- Store customer work products and references in the `Files` property of their owning Company or Project. Do not create records in the legacy Documents database.
- Put reusable customer-wide material on the Company. Put project-specific material on the Project. Do not mirror a file across both by default.
- Keep the mutable artifact at its canonical source. Use Drive or Google Docs for uploaded and editable documents, and direct URLs for Figma, Sheets, Slides, Moneybird, or other durable sources.
- Put a short standalone finding in Insights. Put substantial internal reference material under the regular Documents page. Keep task-specific context in the Task Timeline or as a child page when it needs its own page.

## Routing

1. Read the target record's properties, body, and relevant source before deciding or writing.
2. Before creating a Task, search active Tasks. Reuse one when the stakeholder, outcome, and short execution window are the same.
3. Keep related preparation, calls, feedback, blockers, approvals, follow-up, and files on that Task. Split work when its stakeholder changes or a part can be completed independently.
4. Treat Tasks completed before today as closure records. New work normally gets a related Task. Do not keep dormant Tasks for hypothetical requests.
5. Create a Task only when Sil owns agreed work that must be tracked outside its source: a deliverable, multi-step action, deadline or dependency, or follow-up that outlives the conversation. Replies, acknowledgements, scheduling, forwarding, quick reviews, questions, ideas, and unconfirmed requests stay in their source unless they create that work.
6. Keep source links through relations and compact, reopenable Timeline locators.

An accepted customer ticket already tracked in monday stays there. Create a Notion Task only for a distinct Sil-owned commitment or an overarching delivery outcome, not a copy of each ticket. A proposal, meeting suggestion, draft, or quoted request does not establish Sil's acceptance. Check recent outgoing replies and completion evidence before creating or reopening work.

Keep active Project introductions current: replace superseded planning prose using dated sources, preserve decisions and commercial references, and let the Status property own status. Do not infer a new Task merely because a Project has none. Paused or Discovery projects may legitimately have no executable work. For Waiting work, identify the dependency and its owner; use Due only for an agreed follow-up or deadline, not an invented reminder.

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

The Status property is authoritative. Record its evidence in the Timeline, but do not keep a second status in the body. A Task remains Doing between work sessions unless a concrete dependency makes it Waiting. When that dependency clears, use Todo if work had not started and Doing if it had. A partially blocked work package remains Doing when accepted work can continue independently; preserve the specific dependency rather than hiding all remaining work behind Waiting.

Append the supporting source event before changing Status. Done is terminal unless Sil or a newer source reopens the same deliverable. When canceling a Task, clear obsolete Sprint and Due values in the final write and verify them. Use Due only for real deadlines or follow-up dates.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Paused`, `Completed`, and `Canceled`. Move Discovery to Planned when a concrete delivery commitment or approval exists.
