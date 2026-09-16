---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, Insights, or the Documents page."
---

# Work management

Check live Notion for current records and fields. This skill handles their context, files, and status. `work-triage` handles intake, action, and reporting; `weekly-planning` handles weekly maintenance. Sil handles customer updates.

Before interpreting or writing a Task body, read [timeline.md](references/timeline.md). Before exact property writes, read [notion-schema.md](references/notion-schema.md).

## Records

- **Task**: one stakeholder and executable outcome, normally hours to a few days and less than one week.
- **Project**: a reusable home for a maintained site or app, or a confirmed finite outcome that has several independent Tasks or takes more than about one week.
- **Company**: reusable organization-level sales, delivery, finance or relationship context.
- **Contact**: keep people, contact details, LinkedIn profiles, and relationships in Dex with `dex-skill`. Verify identity and preserve existing fields. An introduction or casual mention alone does not justify a new contact.
- **Sprint**: a Monday-to-Sunday commitment. New Tasks default to the current Sprint unless explicitly later, backlog, Someday or otherwise outside this week.
- **Goal**: an accepted long-term outcome; read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Insight**: an internal finding or research note worth keeping, not executable work or a customer file.
- **Document**: a detailed internal reference, stored beneath the regular Documents page and never as a database record.

Reuse a Project for maintenance, content, feedback, and small features on the same site or app. Split a large delivery when it has its own scope and acceptance and benefits from separate planning or completion. A shared repository, new week, quote, or invoice alone does not decide this. Reusing a Project does not reopen completed Tasks or old scope.

Use `Parent project` / `Subprojects` for separately scoped deliveries within a maintained site or app. Keep one level, one parent, and no cycles. Use page mentions for related work that does not belong to the Project. Tasks link to their delivery Project; shared resources stay on the parent.

Assign at most one Project and one Sprint to a Task. Keep its Companies consistent with the delivery's actual stakeholders; an agency and end customer may both be relevant. Insights and Someday keep useful context in the page body, without a separate Summary property.

Meeting titles name the topic. `When` holds the known event date and time. Remove imported HTML and appended timestamps only after preserving their date information in `When`, or uncertain original timestamps in the body. Resolve conflicting dates from the original source. Page creation alone does not prove when a meeting happened. Link proven Companies and Projects. Add Tasks only when the meeting actually relates to tracked work.

## Sources and record bodies

Before routing context, read the original source, recent replies from Sil, completion evidence, and the destination's properties and body. Verify the stakeholder and owning records; similar names and AI summaries do not prove ownership. Copy IDs and references from the source. A proposal, meeting suggestion, quoted request, or draft does not prove Sil accepted the work.

Task Timelines hold dated requirements, progress, feedback, decisions, and verification. Follow `timeline.md` for appending events, correcting errors, and preserving history. Keep incoming requirements separate from implementation evidence.

Project bodies hold agreed outcomes, scope, project-wide agreements, and main document links. Update them only when a dated source changes the agreement. Company bodies hold reusable organization context and customer-wide agreements. Keep project progress and Dex contact details out. Put status, ownership, and planning in properties.

Preserve historical customer-message send receipts and uncertain-send evidence in Project bodies. Weekly planning no longer creates drafts, approvals or outboxes; remove obsolete unsent update sections only during an explicitly requested cleanup.

## Routing and files

1. Search active Tasks before creating one. Reuse a Task for the same stakeholder, outcome, and short execution window. Keep its preparation, calls, feedback, blockers, and follow-up together. Split work that can be completed independently or belongs to a different stakeholder.
2. Create a Task only for Sil's agreed work that needs tracking beyond its source: a deliverable, multi-step action, deadline, dependency or lasting follow-up. Quick replies, scheduling, questions, reviews, ideas and unconfirmed requests stay at their source unless they establish that work.
3. Leave Tasks completed before today closed. Give new work a related Task unless Sil or a newer source reopens the same deliverable. Do not keep dormant Tasks for hypothetical requests or infer work because a Paused or Discovery Project has no Tasks.
4. Add missing source context even when no new Task is needed. Keep source relations and Timeline references that can open the source again. Read back each destination before considering the work complete.

Keep accepted monday tickets in monday. Create a Notion Task only for a distinct Sil-owned commitment or overall delivery, such as one customer-sprint Task linked to the Company and Sil's Sprint. Record tickets as separate Timeline events with original pulse URLs or IDs.

Name the Company's direct contact link `Moneybird` in Resources. Resolve the administration and contact ID from that URL. Use `moneybird` for quote or invoice state and links. Track follow-up on sent estimates in the Project's sales work. On verified acceptance, finish the sales Task and create or link delivery work. Keep the Task if it already represents delivery.

Use `Resources` (Files & media) for named URLs, files, and images:

- Company Resources hold shared material and links named Website, Moneybird, LinkedIn, or Instagram.
- Project Resources hold repositories, hosting, CMS, database dashboards, Figma, and deployment links for a site or app.
- Task Resources hold evidence used only for that Task.

Read the record's Resources and its parent Project's Resources; Notion does not inherit them. Preserve existing entries when writing. Keep one source per item without copying shared assets into each delivery. Link editable documents by a useful name at their original Drive, Docs, Figma, or other location. The legacy Documents database is retired.

Notion IDs use `TASK`, `PROJECT`, and `COMPANY` prefixes. Resolve the ID before using its short Notion URL. Paste PR URLs into the Task's connected `GitHub PR` field; keep repository links in Resources. For authorized PR work, add `References TASK-n` to the PR description. Keep automatic status mappings off: merging does not prove delivery. Never create or change a PR just to fill this field.

## Planning and status

Choose the Task's single primary Area: **Delivery** for customer work and coordination; **Sales** for qualification, scope and offers; **Growth** for marketing, partnerships, internal products and reusable assets; **Admin** for finance, legal, tooling and internal coordination; **Personal** for non-business work.

Track progress with Task Status:

- **Todo**: accepted, executable, not started.
- **Doing**: started and unfinished. Keep Doing between work sessions, including when one part is blocked but other accepted work can continue.
- **Waiting**: a concrete dependency prevents execution. Record its owner. When cleared, use Todo if not started, otherwise Doing.
- **Done**: completed and verified. Reopen it only for the same deliverable, as described above.
- **Canceled**: duplicate, replaced, moved to Someday, no longer executable, or explicitly dropped. Clear obsolete Sprint and Date values and verify the final write.

Apply status changes supported by a source within the authorized workflow without asking again. Keep evidence in the Timeline and status in properties. Plan routine work through Sprints. Use the single Task `Date` only for a deadline or commitment needing a specific date, without repeating Sprint dates. Distinguish hard cutoffs from scheduled follow-ups. Never invent dates, silently move overdue planning forward, or drop a reminder when moving its date.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Maintenance`, `Paused`, `Completed` and `Canceled`. Move Discovery to Planned when concrete delivery commitment or approval exists.

Use `Maintenance` when the main delivery is finished but ongoing support or improvements continue. Small active Tasks can remain under Maintenance. A large new delivery can return the Project to In Progress or become a separate subproject. Use Completed for a finished finite initiative with no ongoing work managed there. Use Paused for suspended unfinished work. Retainer describes a commercial agreement, not a status. Project `Deadline` is optional and means an agreed overall delivery cutoff. Leave it empty for maintained sites or apps without one. Task dates cover individual commitments. Historical start and end dates are context, not new deadlines.
