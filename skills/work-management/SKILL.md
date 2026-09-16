---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Sprints, Goals, Someday items, Insights, or the Documents page."
---

# Work management

Check live Notion for current records and fields. This skill owns their context, files, and status. `work-triage` handles intake and drafts, `weekly-planning` handles weekly maintenance, and the user sends customer updates himself.

Read [timeline.md](references/timeline.md) before you read or write a Task body. Read [notion-schema.md](references/notion-schema.md) before exact property writes.

## Records

- **Task**: one stakeholder and one executable outcome, usually hours to a few days and under a week.
- **Project**: a lasting home for a maintained site or app, or a confirmed finite outcome with several independent Tasks or more than about a week of work.
- **Company**: organization-level sales, delivery, finance, or relationship context.
- **Contact**: people, contact details, LinkedIn profiles, and relationships live in Dex, through `dex-skill`. Check identity and keep existing fields. An introduction or a casual mention is not a reason for a new contact.
- **Sprint**: a Monday to Sunday commitment. A new Task goes in the current Sprint unless it is explicitly later, backlog, Someday, or otherwise outside this week.
- **Goal**: an accepted long-term outcome. Read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Insight**: an internal finding or research note worth keeping. Not work, not a customer file.
- **Document**: a detailed internal reference, stored under the Documents page, never as a database record.

Reuse a Project for maintenance, content, feedback, and small features on the same site or app. Split off a large delivery when it has its own scope and acceptance and benefits from separate planning. A shared repository, a new week, a quote, or an invoice alone does not decide this. Reusing a Project does not reopen finished Tasks or old scope.

Use `Parent project` / `Subprojects` for separately scoped deliveries inside a maintained site or app: one level, one parent, no cycles. Use page mentions for related work that belongs elsewhere. Tasks link to their delivery Project; shared resources stay on the parent.

A Task has at most one Project and one Sprint. Its Companies are the delivery's real stakeholders, which can be both an agency and an end customer. Insights and Someday items keep their context in the page body, without a Summary property.

Meeting titles name the topic. `When` holds the event date and time. Remove imported HTML and appended timestamps only after saving their date in `When`, or an uncertain timestamp in the body. Resolve conflicting dates from the source. Page creation does not prove when a meeting happened. Link proven Companies and Projects. Add Tasks only when the meeting relates to tracked work.

## Sources and record bodies

Before routing context, read the original source, the user's recent replies, completion evidence, and the destination's properties and body. Check the stakeholder and owning records. A similar name or an AI summary does not prove ownership. Copy IDs and references from the source. A proposal, meeting suggestion, quoted request, or draft does not prove the user accepted the work.

Task Timelines hold dated requirements, progress, feedback, decisions, and verification. Follow `timeline.md` for appending, correcting, and keeping history. Keep incoming requirements apart from implementation evidence.

Project bodies hold agreed outcomes, scope, project-wide agreements, and main document links. Update them only when a dated source changes the agreement. Company bodies hold organization context and customer-wide agreements, not project progress or Dex contact details. Status, ownership, and planning live in properties.

Keep old send receipts for customer updates in the Project body, including ones where sending is uncertain.

## Routing and files

1. Search active Tasks before creating one. Reuse a Task for the same stakeholder, outcome, and short execution window, keeping its preparation, calls, feedback, blockers, and follow-up together. Split work that can be finished independently or belongs to another stakeholder.
2. Create a Task only for agreed work that needs tracking beyond its source: a deliverable, a multi-step action, a deadline, a dependency, or a lasting follow-up. Quick replies, scheduling, questions, reviews, ideas, and unconfirmed requests stay at their source unless they create such work.
3. Leave Tasks completed before today closed. Give new work a related Task unless the user or a newer source reopens the same deliverable. Do not keep dormant Tasks for hypothetical requests, and do not infer work because a Paused or Discovery Project has no Tasks.
4. Add missing source context even when no new Task is needed. Keep source relations and Timeline references that can reopen the source.

Accepted monday tickets stay in monday. Create a Notion Task only for a distinct commitment of the user or an overall delivery, such as one customer-sprint Task linked to the Company and the user's Sprint. Record tickets as separate Timeline events with their pulse URLs or IDs.

Name the Company's Moneybird contact link `Moneybird` in Resources, and resolve the administration and contact ID from that URL. Use `moneybird` for quote and invoice state and links. Track follow-up on sent estimates in the Project's sales work. On verified acceptance, finish the sales Task and create or link delivery work, or keep the Task if it already represents delivery.

`Resources` (Files & media) holds named URLs, files, and images:

- Company Resources: shared material and links named Website, Moneybird, LinkedIn, or Instagram.
- Project Resources: repositories, hosting, CMS, database dashboards, Figma, and deployment links.
- Task Resources: evidence used only for that Task.

Read the record's Resources and its parent Project's Resources; Notion does not inherit them. Keep existing entries when writing. One source per item, without copying shared assets into each delivery. Link editable documents by a useful name at their Drive, Docs, Figma, or other location.

Notion IDs use `TASK`, `PROJECT`, and `COMPANY` prefixes. Resolve the ID before using its short URL. Paste PR URLs into the Task's `GitHub PR` field; repository links go in Resources. For approved PR work, add `References TASK-n` to the PR description. Keep automatic status mappings off, since merging does not prove delivery. Never create or change a PR just to fill this field.

## Planning and status

Give each Task one Area: **Delivery** for customer work and coordination, **Sales** for qualification, scope, and offers, **Growth** for marketing, partnerships, internal products, and reusable assets, **Admin** for finance, legal, tooling, and internal coordination, **Personal** for non-business work.

Task Status:

- **Todo**: accepted, executable, not started.
- **Doing**: started and unfinished. Stays Doing between sessions, also when one part is blocked but other work can continue.
- **Waiting**: a concrete dependency blocks execution. Record its owner. When cleared, Todo if not started, otherwise Doing.
- **Done**: completed and verified. Reopen only for the same deliverable.
- **Canceled**: duplicate, replaced, moved to Someday, no longer executable, or explicitly dropped. Clear the Sprint and Date.

Apply a status change that a source supports within the authorized workflow without asking again. Evidence goes in the Timeline, status in properties. Plan routine work through Sprints. Use the Task `Date` only for a deadline or commitment that needs a specific date, not to repeat Sprint dates. Tell hard cutoffs apart from scheduled follow-ups. Never invent dates, silently move overdue planning forward, or drop a reminder when moving its date.

Project statuses are `Discovery`, `Planned`, `In Progress`, `Maintenance`, `Paused`, `Completed`, and `Canceled`. Move Discovery to Planned when there is a concrete commitment or approval. Use `Maintenance` when the main delivery is done but support or improvements continue; small active Tasks can stay under it, and a large new delivery returns the Project to In Progress or becomes a subproject. Use Completed for a finished finite initiative with nothing ongoing. Use Paused for suspended unfinished work. A retainer is a commercial agreement, not a status.

Project `Deadline` is optional and means an agreed overall delivery cutoff. Leave it empty for maintained sites or apps. Task dates cover individual commitments. Historical start and end dates are context, not new deadlines.
