---
name: weekly-planning
description: "Use when running weekly Notion maintenance to clean up active records and report changes or decisions."
---

# Weekly cleanup

The user makes the planning decisions. Use `work-management` and `notion-cli` for every Notion read and write.

1. Read all active Projects with their Tasks and Companies, and the upcoming Sprint: properties, bodies, agreements, dependencies, and every results page. The upcoming Sprint is the one whose dates include next Monday. If Next has no dates, use it only when there is one Next Sprint and Current ends this Sunday. Do not create a duplicate Sprint.
2. Repair broken or missing relations when the record's own evidence shows the right Task, Project, Company, or Sprint.
3. Correct a stale status only when a source proves completion, cancellation, pausing, or resumed work. Inactivity is not completion. Keep the Timeline history and append corrections as `work-management` describes.
4. Merge clear duplicate active work: keep context and links in the surviving record and cancel the other. Flag uncertain matches. Do not delete ambiguous work.
5. Remove obsolete dates and fix Sprint assignments only under existing agreements. Flag overdue work and unclear planning. Never invent deadlines or commitments, and never roll unfinished work forward on your own.
6. Fill in known owners and dependency owners from recorded agreements. Flag accepted work without an owner or a clear next action. Do not turn an inferred next action into a commitment; keep the Brief limited to supported facts.
7. Update Project scope and agreements only when a newer dated decision replaces them. Keep Timeline entries and commercial decisions. Ignore finished or canceled history and Reservations. Goals are read-only.
8. Return one numbered list, first the `Changed` lines, then `Needs you`, then `Blocked`. One line per item, related changes grouped, link on the title:

   ```text
   1. Changed: [Title](notion-url) · Doing → Done
   2. Needs you: [Title](notion-url) · the decision or question
   3. Blocked: [Title](notion-url) · the blocker
   ```

   Skip unchanged records and per-project recaps. With nothing to report, return `NO_REPLY`.

Do not create customer drafts or send customer messages.
