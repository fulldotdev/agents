---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, Insights, or the Documents page."
---

# Work management

Owns Notion record selection, source context, files and status. Live Notion owns current records and schema. `work-triage` owns intake, execution and reporting; `weekly-planning` owns weekly Notion maintenance and its cleanup report. Sil handles customer updates.

Before interpreting or writing a Task body, read [timeline.md](references/timeline.md). Before exact property writes, read [notion-schema.md](references/notion-schema.md).

## Records

- **Task**: one stakeholder and executable outcome, normally hours to a few days and less than one week.
- **Project**: a reusable home for a maintained site or app, or a confirmed finite outcome with several independent Tasks or more than about one week of work.
- **Company**: reusable organization-level sales, delivery, finance or relationship context.
- **Contact**: Dex owns people, contact details, LinkedIn profiles and relationships. Use `dex-skill`; resolve identity and preserve existing fields when updating. Introductions or chatter alone do not justify creating a contact.
- **Sprint**: a Monday-to-Sunday commitment. New Tasks default to the current Sprint unless explicitly later, backlog, Someday or otherwise outside this week.
- **Goal**: an accepted long-term outcome; read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Insight**: a durable internal finding or research note, not executable work or a customer file.
- **Document**: substantial internal reference material, stored beneath the regular Documents page, never as a database record.

Reuse a Project for routine maintenance, content, feedback and small features on the same site or app. Create a separate Project when a substantial delivery has its own scope and acceptance and benefits from being planned or completed independently. Sharing a repository does not decide this; a new week, quote or invoice alone is not a reason to split. Reusing a Project does not reopen completed Tasks or reactivate old scope.

Use native `Parent project` / `Subprojects` for independently scoped deliveries belonging to a maintained site or app. Keep one level, one parent, and no cycles. Related work without ownership uses a page mention, not another relation field. Tasks link to their actual delivery Project; shared resources stay on the parent.

Assign at most one Project and one Sprint to a Task. Keep its Companies consistent with the delivery's actual stakeholders; an agency and end customer may both be relevant. Insights and Someday keep useful context in the page body, without a separate Summary property.

Meeting titles name the topic; `When` holds the known event date and time. Clean import HTML and appended timestamps only after preserving their date information in `When`, or uncertain original timestamps in the body. Resolve conflicting dates from the original source; page creation alone does not prove when a meeting happened. Link proven Companies and Projects; add Tasks only when the meeting actually relates to tracked work.

## Sources and record bodies

Read the relevant original source, recent outgoing replies, completion evidence, and destination properties and body before routing. Verify the stakeholder and owning records; similar names and AI summaries are not ownership evidence. Copy source IDs and locators from the source itself. A proposal, meeting suggestion, quoted request or draft does not establish Sil's acceptance.

Task Timelines hold dated requirements, progress, feedback, decisions and verification under the append-only rules in `timeline.md`. Keep incoming requirements distinct from implementation evidence. Store enough context to prevent a wrong decision, not whole conversations. Correct earlier entries with a new source-backed event; do not replace history or write generated current-state summaries.

Project bodies hold agreed outcomes, scope, project-wide agreements and leading document links. Change this frame only when a dated source changes the agreement. Company bodies hold reusable organization context and customer-wide agreements, not project progress or Dex contact details. Properties own status, ownership and planning.

Preserve historical customer-message send receipts and uncertain-send evidence in Project bodies. Weekly planning no longer creates drafts, approvals or outboxes; remove obsolete unsent update sections only during an explicitly requested cleanup.

## Routing and files

1. Search active Tasks before creating one. Reuse the same stakeholder, outcome and short execution window; keep its preparation, calls, feedback, blockers and follow-up together. Split independently completable work or work for a different stakeholder.
2. Create a Task only for Sil's agreed work that needs tracking beyond its source: a deliverable, multi-step action, deadline, dependency or lasting follow-up. Quick replies, scheduling, questions, reviews, ideas and unconfirmed requests stay at their source unless they establish that work.
3. Tasks completed before today are closure records. New work normally gets a related Task; reopen only when Sil or a newer source reopens the same deliverable. Do not retain dormant Tasks for hypothetical requests or infer work merely because a Paused or Discovery Project has no Tasks.
4. Route missing source context even when no new Task is needed. Keep source relations and reopenable Timeline locators, and verify destination writes before considering routing complete.

Accepted monday tickets remain in monday. Create a Notion Task only for a distinct Sil-owned commitment or overarching delivery outcome, possibly one customer-sprint Task linked to the Company and Sil's Sprint. Record relevant tickets as separate Timeline events with original pulse URLs or IDs.

Store the direct Moneybird contact link in the Company’s Resources, named `Moneybird`; resolve the administration and contact ID from that URL. Use `moneybird` for quote/invoice state and direct URLs. A sent estimate needing follow-up belongs to the Project's sales work. On verified acceptance, finish the sales Task and create or link delivery work; retain the Task if it already represents delivery.

Use `Resources` (Files & media) for named URLs, files and images on Companies, Projects and Tasks. Company-wide material and ordinary links (Website, Moneybird, LinkedIn, Instagram) belong in Company Resources, using those clear names; site/app repositories, hosting, CMS, database dashboards, Figma and deployment links on the Project; task-specific evidence on the Task. Read the owning record's Resources and then its parent Project's Resources. Notion does not inherit them automatically. Keep one canonical source, preserve existing entries on writes, and do not duplicate shared assets across deliveries. Keep editable documents at their original Drive/Docs/Figma or other source; link them by a useful name. Do not use the legacy Documents database. Short internal findings belong in Insights; substantial internal references beneath Documents.

Native IDs use `TASK`, `PROJECT` and `COMPANY` prefixes. Resolve the actual ID before using its short Notion URL. Task `GitHub PR` is the connected PR field, separate from repository links in Resources; it supports pasting a PR URL manually. For authorized PR work, add `References TASK-n` to the PR description. Automatic task-status mappings stay off: a merged PR alone does not verify delivery. Never create or modify a PR merely to populate this field.

## Planning and status

Choose the Task's single primary Area: **Delivery** for customer work and coordination; **Sales** for qualification, scope and offers; **Growth** for marketing, partnerships, internal products and reusable assets; **Admin** for finance, legal, tooling and internal coordination; **Personal** for non-business work.

Task Status is authoritative:

- **Todo**: accepted, executable, not started.
- **Doing**: started and unfinished. Keep Doing between work sessions, including when some work is blocked but accepted work can continue independently.
- **Waiting**: a concrete dependency prevents execution. Record its owner. When cleared, use Todo if not started, otherwise Doing.
- **Done**: completed and verified; terminal except for reopening the same deliverable above.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable or explicitly dropped. Clear obsolete Sprint and Date values and verify the final write.

Apply source-backed status changes within the authorized workflow without asking again. Keep evidence in the Timeline, not a second status in the body. Sprint owns routine work planning. Use the single Task `Date` sparingly for a real deadline or another commitment that needs a specific date; do not repeat Sprint dates there. Preserve the distinction between a hard cutoff and a scheduled follow-up in the source context. Never invent a date, silently roll overdue planning forward, or drop an existing reminder during a date move.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Maintenance`, `Paused`, `Completed` and `Canceled`. Move Discovery to Planned when concrete delivery commitment or approval exists.

Use `Maintenance` when the main delivery is finished but ongoing support or improvements continue. Small active Tasks can remain under Maintenance; a substantial new delivery can return the Project to In Progress or become a separately scoped subproject. Use Completed for a finished finite initiative with no ongoing work managed there, and Paused for suspended unfinished work. Retainer describes a commercial agreement, not a status. Project `Deadline` is optional and means an agreed overall delivery cutoff. Leave it empty for maintained sites/apps without one; task dates cover individual commitments. Historical start/end dates are context, not new deadlines.
