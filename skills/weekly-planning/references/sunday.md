# Sunday preparation

Run Sunday at 10:00 Europe/Amsterdam. Complete cleanup, drafting and review publication consecutively in one run.

## Review and clean up Notion

Use `work-management` and `notion-cli` to read the current active Projects, related Tasks and Companies, and the upcoming Sprint. Read their properties and bodies, including the recorded planning, agreements and dependencies. Follow pagination to cover all active records.

Clean up active records using the information in Notion: outdated project scope or agreements (not progress summaries), duplicate active work, broken relations, incorrect statuses, missing dependency owners, obsolete dates and accepted work that lacks an owner. Preserve historical Timeline entries and commercial decisions. Ignore terminal history and Reservations. Read-only Goals remain read-only. Do not auto-delete ambiguous work or invent commitments, deadlines or a new weekly proposal. Sprint changes must follow an existing agreement; unresolved choices go in the short Telegram note.

## Draft and publish

Account for every active customer Project. Cover In Progress and Planned; inspect Discovery and Paused for an active customer commitment before deciding whether an update is useful. Explicitly list projects without a draft and the reason, such as no work planned for the coming week or an unclear weekly priority. Exclude internal/personal projects based on their actual context. Never silently drop a project because it has no Tasks. Already agreed work, a handoff or ongoing work this week is a reason for an update, even without new results or customer questions.

Draft in the customer's language and Sil's voice, from Monday's perspective: "Deze week gaan we ...". Lead with the concrete work we will pick up or continue that week, based on the upcoming Sprint and the planning recorded in Notion. Mention a day or delivery date only when confirmed; starting work does not promise finishing it that week. Past progress is only brief context for what comes next. Include a customer dependency when it affects that work. If the week's work is unclear, ask Sil in the Planning review. Use the recipient, account, channel and thread recorded in the Project or Company; include any missing details in that review.

Select the Sprint whose `Dates` contain the upcoming Monday. Native Notion future Sprints can have no dates yet: in that case use the unique `Next` Sprint after verifying the `Current` Sprint ends this Sunday. Do not create a duplicate Sprint just because `Next` has no dates. Initialize the week's outbox under that Sprint using the [update commands](operations.md); store each exact draft in the corresponding Project body through its script. Do not create a separate update database or Gmail/Slack drafts in parallel. If the Sprint is missing or ambiguous, resolve that through `work-management`, without filling it with unconfirmed commitments.

Publish one numbered review list through the outbox script to Planning, with direct links to the Project sections. Its canonical copy and numbered version mapping remain on the Sprint. Add a short cleanup result and any skipped/blocked projects. Sil reviews and gives numbered approvals or edits in that Telegram chat. Do not send customer messages on Sunday. After script publication, avoid a second cron summary: end with `NO_REPLY`. If preparation or publication fails before a successful report, return a short actionable error for cron delivery to Planning.
