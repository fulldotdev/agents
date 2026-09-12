---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, Insights, or the Documents page."
---

# Work management

Owns Notion record selection, source context, files and status. Live Notion owns current records and schema. `work-triage` owns intake, execution and reporting; `weekly-planning` owns weekly cleanup, update drafts, Planning approvals and Monday sending.

Before interpreting or writing a Task body, read [timeline.md](references/timeline.md). Before exact property writes, read [notion-schema.md](references/notion-schema.md).

## Records

- **Task**: one stakeholder and executable outcome, normally hours to a few days and less than one week.
- **Project**: a confirmed outcome with several independent Tasks or more than about one week of work.
- **Company**: reusable organization-level sales, delivery, finance or relationship context.
- **Contact**: Dex owns people, contact details, LinkedIn profiles and relationships. Use `dex-skill`; resolve identity and preserve existing fields when updating. Introductions or chatter alone do not justify creating a contact.
- **Sprint**: a Monday-to-Sunday commitment. New Tasks default to the current Sprint unless explicitly later, backlog, Someday or otherwise outside this week.
- **Goal**: an accepted long-term outcome; read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Insight**: a durable internal finding or research note, not executable work or a customer file.
- **Document**: substantial internal reference material, stored beneath the regular Documents page, never as a database record.

## Sources and record bodies

Read the relevant original source, recent outgoing replies, completion evidence, and destination properties and body before routing. Verify the stakeholder and owning records; similar names and AI summaries are not ownership evidence. Copy source IDs and locators from the source itself. A proposal, meeting suggestion, quoted request or draft does not establish Sil's acceptance.

Task Timelines hold dated requirements, progress, feedback, decisions and verification under the append-only rules in `timeline.md`. Keep incoming requirements distinct from implementation evidence. Store enough context to prevent a wrong decision, not whole conversations. Correct earlier entries with a new source-backed event; do not replace history or write generated current-state summaries.

Project bodies hold agreed outcomes, scope, project-wide agreements and leading document links. Change this frame only when a dated source changes the agreement. Company bodies hold reusable organization context and customer-wide agreements, not project progress or Dex contact details. Properties own status, ownership and planning.

Preserve weekly-planning's helper-managed drafts, approvals and send receipts in Project bodies, with the numbered review linked from the Sprint. They are the only operational-log exception.

## Routing and files

1. Search active Tasks before creating one. Reuse the same stakeholder, outcome and short execution window; keep its preparation, calls, feedback, blockers and follow-up together. Split independently completable work or work for a different stakeholder.
2. Create a Task only for Sil's agreed work that needs tracking beyond its source: a deliverable, multi-step action, deadline, dependency or lasting follow-up. Quick replies, scheduling, questions, reviews, ideas and unconfirmed requests stay at their source unless they establish that work.
3. Tasks completed before today are closure records. New work normally gets a related Task; reopen only when Sil or a newer source reopens the same deliverable. Do not retain dormant Tasks for hypothetical requests or infer work merely because a Paused or Discovery Project has no Tasks.
4. Route missing source context even when no new Task is needed. Keep source relations and reopenable Timeline locators, and verify destination writes before considering routing complete.

Accepted monday tickets remain in monday. Create a Notion Task only for a distinct Sil-owned commitment or overarching delivery outcome, possibly one customer-sprint Task linked to the Company and Sil's Sprint. Record relevant tickets as separate Timeline events with original pulse URLs or IDs.

Use `moneybird` for quote/invoice state and direct URLs. A sent estimate needing follow-up belongs to the Project's sales work. On verified acceptance, finish the sales Task and create or link delivery work; retain the Task if it already represents delivery.

Store customer artifacts in the owning Company or Project's `Files`: reusable customer-wide material on the Company, project-specific material on the Project. Do not mirror files or use the legacy Documents database. Keep editable artifacts at their canonical source: Drive/Docs for uploaded documents, direct durable URLs for Figma, Sheets, Slides, Moneybird and similar sources. Short internal findings belong in Insights; substantial internal references beneath Documents; task-specific context in the Timeline or a child page when needed.

## Planning and status

Choose the Task's single primary Area: **Delivery** for customer work and coordination; **Sales** for qualification, scope and offers; **Growth** for marketing, partnerships, internal products and reusable assets; **Admin** for finance, legal, tooling and internal coordination; **Personal** for non-business work.

Task Status is authoritative:

- **Todo**: accepted, executable, not started.
- **Doing**: started and unfinished. Keep Doing between work sessions, including when some work is blocked but accepted work can continue independently.
- **Waiting**: a concrete dependency prevents execution. Record its owner. When cleared, use Todo if not started, otherwise Doing.
- **Done**: completed and verified; terminal except for reopening the same deliverable above.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable or explicitly dropped. Clear obsolete Sprint and Due values and verify the final write.

Apply source-backed status changes within the authorized workflow without asking again. Keep evidence in the Timeline, not a second status in the body. Use Due only for agreed deadlines or follow-up dates, never an invented reminder.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Paused`, `Completed` and `Canceled`. Move Discovery to Planned when concrete delivery commitment or approval exists.
