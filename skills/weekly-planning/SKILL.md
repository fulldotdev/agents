---
name: weekly-planning
description: "Use when reviewing the past week’s incoming sources against Notion and cleaning up active work records."
---

# Weekly review

The user makes the planning decisions. Use `work-management` and `notion-cli` for every Notion read and write.

Start by comparing the previous seven days of incoming sources with Notion, following [Assess triage quality](../work-triage/references/assess-quality.md). Fix the review window at the run’s start in Europe/Amsterdam. Collect all source pages, outgoing replies, relevant media and T3 activity, including settled or archived threads. Use the source collectors directly so daily triage bookmarks and retries stay unchanged. Read full meeting transcripts for this weekly check.

Find missed accepted work, later corrections, delivery evidence, wrong routing and duplicates. Compare the actual owning records, including records not edited this week. Save missing context and make source-supported corrections through `work-management`, then perform the maintenance below. Flag ambiguous scope, ownership or planning instead of choosing for the user. A failed or incomplete source stays a reported gap, not an empty result. This review does not execute the work it discovers.

1. Read all active Projects with their Tasks and Companies, and the upcoming Sprint: properties, bodies, agreements, dependencies, and every results page. The upcoming Sprint is the one whose dates include next Monday. If Next has no dates, use it only when there is one Next Sprint and Current ends this Sunday. Do not create a duplicate Sprint.
2. Repair broken or missing relations when the record's own evidence shows the right Task, Project, Company, or Sprint.
3. Correct a stale status only when a source proves completion, cancellation, pausing, or resumed work. Inactivity is not completion. Keep the Updates or existing Timeline history and append corrections as `work-management` describes.
4. Merge clear duplicate active work: keep context and links in the surviving record and cancel the other. Flag uncertain matches. Do not delete ambiguous work.
5. Remove obsolete dates and fix Sprint assignments only under existing agreements. Flag overdue work and unclear planning. Do not roll unfinished work forward on your own.
6. Fill in known owners and dependency owners from recorded agreements. Flag accepted work without an owner or a clear next action. Do not turn an inferred next action into a commitment; keep the Brief limited to supported facts.
7. Update Project scope and agreements only when a newer dated decision replaces them. Keep Updates or existing Timeline entries and commercial decisions. Ignore finished or canceled history and Reservations. Goals are read-only.
8. Return one numbered list, first the `Changed` lines, then `Needs you`, then `Blocked`. One line per item, related changes grouped, link on the title:

   ```text
   1. Changed: [Title](notion-url) · Doing → Done
   2. Needs you: [Title](notion-url) · the decision or question
   3. Blocked: [Title](notion-url) · the blocker
   ```

   Skip unchanged records and per-project recaps. Include one short `Checked` line with the source-review dates and coverage. Name unavailable or incomplete sources in `Blocked`; do not claim a complete check when a source could not be read. With no changes or questions, return only the coverage line.

Do not create customer drafts or send customer messages.
