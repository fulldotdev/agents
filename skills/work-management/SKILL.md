---
name: work-management
description: "Use when reading, creating, routing, or updating Notion Tasks, Projects, Companies, Persons, Sprints, Goals, Someday items, Insights, or the Documents page."
---

# Work management

Check live Notion for current records and fields. This skill owns their context, files, and status. `work-triage` handles intake and drafts, `weekly-planning` handles weekly maintenance, and the user sends customer updates himself.

Read [timeline.md](references/timeline.md) before you read or write a Task body. Read [notion-schema.md](references/notion-schema.md) before exact property writes.

## Records

- **Task**: one stakeholder and one executable outcome, usually hours to a few days and under a week.
- **Project**: a lasting home for a maintained site or app, or a confirmed finite outcome with several independent Tasks or more than about a week of work.
- **Company**: organization-level sales, delivery, finance, or relationship context.
- **Person**: use Notion Persons for names, linked Companies, and relationship context. Google Contacts in `sil@full.dev` owns phone numbers, email addresses, and other contact details. Match names and company links first; fetch Google details through `gog` only to resolve identity or use a contact detail. A person can belong to several companies, so use the message topic to choose the work owner. Keep uncertain matches unresolved. Do not write to Dex or create a parallel contact cache. An introduction or casual mention alone does not require a new contact.
- **Sprint**: a Monday to Sunday commitment. A new Task goes in the current Sprint unless it is explicitly later, backlog, Someday, or otherwise outside this week.
- **Goal**: an accepted long-term outcome. Read-only.
- **Someday**: a vague or maybe-later idea that is not executable yet.
- **Insight**: an internal finding or research note worth keeping. Not work, not a customer file.
- **Document**: a detailed internal reference, stored under the Documents page, never as a database record.

Reuse a Project for maintenance, content, feedback, and small features on the same site or app. Split off a large delivery only when it has its own scope and acceptance. Reusing a Project does not reopen finished Tasks.

Use `Parent project` / `Subprojects` for separately scoped deliveries inside a maintained site or app: one level, one parent, no cycles. Use page mentions for related work that belongs elsewhere. Tasks link to their delivery Project; shared resources stay on the parent.

A Task has at most one Project and one Sprint. Its Companies are the delivery's real stakeholders, which can be both an agency and an end customer. Insights and Someday items keep their context in the page body, without a Summary property.

Meeting titles name the topic. `When` holds the event date and time. Resolve conflicting dates from the source, not from the page's creation date. Link proven Companies and Projects. Link confirmed participants through Persons; that relation appears as Meetings on each Person. A mentioned name or a calendar invitation alone does not establish attendance. Resolve identities through existing Persons and Google Contacts; leave uncertain matches unlinked. Add Tasks only when the meeting relates to tracked work.

## Sources and record bodies

Before routing, read the source, the user's recent replies, completion evidence, and the destination record. Confirm the owner from the sender and topic, not from a similar name or an AI summary. Copy IDs and references from the source. A proposal, meeting suggestion, quoted request, or draft does not prove the user accepted the work.

- **Task body**: a current Brief and dated Updates, written as `timeline.md` describes. Existing Timeline sections remain the event log. Triage and T3 read the current record and add only missing facts.
- **Project body**: agreed outcomes, scope, project-wide agreements, and main document links. Update it only when a dated source changes the agreement.
- **Company body**: organization context and customer-wide agreements, not project progress or a second editable list of Google contact details.
- **Properties**: status, ownership, and planning.

## Routing and files

1. Search active Tasks before creating one. Reuse a Task for the same stakeholder, outcome, and short execution window, keeping its preparation, calls, feedback, blockers, and follow-up together. Split work that can be finished independently or belongs to another stakeholder.
2. Create a Task only for agreed work that needs tracking beyond its source: a deliverable, a multi-step action, a deadline, a dependency, or a lasting follow-up. Quick replies, scheduling, questions, reviews, ideas, and unconfirmed requests stay at their source.
3. Leave Tasks completed before today closed. Give new work a related Task unless the user or a newer source reopens the same deliverable. Do not keep dormant Tasks for hypothetical requests, and do not infer work because a Paused or Discovery Project has no Tasks.
4. Add missing source context even when no new Task is needed. Keep source relations and source references that can reopen the source.

Accepted monday tickets stay in monday. Create a Notion Task only for a distinct commitment of the user or an overall delivery, such as one customer-sprint Task linked to the Company and the user's Sprint. Record tickets as dated updates with their pulse URLs or IDs.

Name the Company's Moneybird contact link `Moneybird` in Resources, and resolve the administration and contact ID from that URL. Use `moneybird` for quote and invoice state and links. Track follow-up on sent estimates in the Project's sales work. On verified acceptance, finish the sales Task and create or link delivery work, or keep the Task if it already represents delivery.

`Resources` (Files & media) holds the named links, files, and images that help with a record: on a Company shared material such as Website, Moneybird, LinkedIn, or Instagram; on a Project the repository, hosting, CMS, design, and deployment links; on a Task the evidence for that Task, including PRs and issues. Name each entry by what it is, such as `Moneybird` or `PR #79`. Read the record's Resources and its parent Project's Resources; Notion does not inherit them. Keep existing entries when writing, and keep one source per item. Save the original of media that defines requirements or proves approval, delivery, or completion, including video. A durable original URL is enough; expiring download URLs and local scratch paths are not durable references. Use a body link or embed when the context belongs next to an update. Upload once and reuse that file. Incidental media stays at its source.

## Planning and status

Give each Task one Area:

- **Delivery**: customer work and coordination.
- **Sales**: qualification, scope, and offers.
- **Growth**: marketing, partnerships, internal products, and reusable assets.
- **Admin**: finance, legal, tooling, and internal coordination.
- **Personal**: non-business work.

Task Status:

- **Todo**: accepted, executable, not started.
- **Doing**: started and unfinished. Stays Doing between sessions, also when one part is blocked but other work can continue.
- **Waiting**: a concrete dependency blocks execution. Record its owner. When cleared, Todo if not started, otherwise Doing.
- **Done**: completed and verified. Reopen only for the same deliverable.
- **Canceled**: duplicate, replaced, moved to Someday, no longer executable, or explicitly dropped. Clear the Sprint and Date.

Apply a status change that a source supports without asking again. Evidence goes in Updates (or the existing Timeline), status in properties. Plan routine work through Sprints. Use the Task `Date` only for a deadline or commitment that needs a specific date. Tell hard cutoffs apart from scheduled follow-ups. Never invent dates, silently move overdue planning forward, or drop a reminder when moving its date.

Project Status:

- **Discovery**: no commitment yet. Move to Planned on a concrete commitment or approval.
- **Planned**, **In Progress**: committed, not started or running.
- **Maintenance**: main delivery done, support continues. Small Tasks stay under it. A large new delivery moves it back to In Progress or becomes a subproject.
- **Paused**: unfinished work is suspended.
- **Completed**: a finished finite initiative with nothing ongoing.
- **Canceled**: dropped.

A retainer is a commercial agreement, not a status. Project `Deadline` is optional and means an agreed overall delivery cutoff. Leave it empty for maintained sites or apps. Task dates cover individual commitments. Historical start and end dates are context, not new deadlines.
