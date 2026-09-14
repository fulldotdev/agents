---
name: weekly-planning
description: "Weekly Notion maintenance: clean up active records and report changes and decisions in one concise list. No customer updates."
---

# Weekly cleanup

Run one maintenance routine on Otis, Sunday at 10:00 Europe/Amsterdam. Sil handles customer updates and planning decisions. Use `work-management` and `notion-cli` for Notion reads and writes.

1. Read all active Projects, related Tasks and Companies, and the upcoming Sprint, including properties, bodies, recorded agreements and dependencies. Follow pagination. Resolve the Sprint by the dates containing the upcoming Monday; when Next has no dates, use the unique Next only after checking Current ends this Sunday. Do not create a duplicate Sprint.
2. Repair broken or missing relations when the correct Task, Project, Company or Sprint is established by recorded evidence. Verify each write.
3. Correct outdated statuses only where evidence establishes completion, cancellation, pausing or resumed work. Inactivity is not completion. Preserve Task Timeline history and append source-backed corrections under `work-management`.
4. Consolidate clear duplicate active work, preserving context and links in the retained record and canceling the duplicate. Flag uncertain matches; do not delete ambiguous work.
5. Remove obsolete dates and correct Sprint assignments only under existing agreements. Flag overdue work and unclear planning without inventing deadlines, commitments or automatically rolling unfinished work forward.
6. Fill in known owners and dependency owners from recorded agreements. Flag accepted work without an owner or a clear next action. Do not turn inferred next actions into new commitments or generated Task-body summaries.
7. Refresh Project scope and agreements only when newer dated decisions supersede them. Preserve historical Timeline entries and commercial decisions. Ignore terminal history and Reservations; Goals remain read-only. Confirm all changes by reading the affected records back.
8. Return one concise numbered list for delivery to Telegram Planning by the cron. Group related changes in one line, link affected records, and prefix each item with **Changed**, **Needs you**, or **Blocked**. Put changes first, decisions second, blockers last. Omit empty categories, unchanged records and per-project coverage recaps. If nothing changed or needs attention, return `NO_REPLY`. Do not send a second report yourself.

This workflow does not create customer-update drafts, outboxes, approval lists or send claims, process old Planning approvals, or send customer messages. Do not run the retired Sunday preparation or Monday sending workflow. Preserve verified sent-message receipts and uncertain-send evidence; legacy unsent updates are removed only during an explicitly requested cleanup.
