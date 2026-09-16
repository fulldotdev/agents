---
name: weekly-planning
description: "Use when running weekly Notion maintenance to clean up active records and report changes or decisions. Does not create customer updates."
---

# Weekly cleanup

Run this maintenance routine on Otis on Sunday at 10:00 Europe/Amsterdam. Sil handles customer updates and planning decisions. Use `work-management` and `notion-cli` for all Notion reads and writes.

1. Read all active Projects, their related Tasks and Companies, and the upcoming Sprint. Include properties, bodies, agreements, and dependencies. Read every results page. Find the Sprint whose dates include the upcoming Monday. If Next has no dates, use it only when there is one Next Sprint and Current ends this Sunday. Do not create a duplicate Sprint.
2. Repair broken or missing relations when recorded evidence establishes the correct Task, Project, Company, or Sprint. Verify every write.
3. Correct an outdated status only when a source proves completion, cancellation, pausing, or resumed work. Inactivity is not completion. Keep Task Timeline history and append corrections according to `work-management`.
4. Consolidate clear duplicate active work, preserving context and links in the retained record and canceling the duplicate. Flag uncertain matches; do not delete ambiguous work.
5. Remove obsolete dates and correct Sprint assignments only under existing agreements. Flag overdue work and unclear planning. Never invent deadlines or commitments, and never roll unfinished work forward automatically.
6. Fill in known owners and dependency owners from recorded agreements. Flag accepted work without an owner or clear next action. Do not turn inferred next actions into new commitments or generated Task-body summaries.
7. Update Project scope and agreements only when newer dated decisions replace them. Keep historical Timeline entries and commercial decisions. Ignore finished or canceled history and Reservations. Goals remain read-only. Read back every changed record.
8. Return one concise numbered list for the cron to deliver to Telegram Planning. Group related changes in one line, link affected records, and prefix every item with **Changed**, **Needs you**, or **Blocked**. Put changes first, decisions second, and blockers last. Omit empty categories, unchanged records, and per-project coverage recaps. If nothing changed or needs attention, return `NO_REPLY`. Do not send a second report yourself.

Do not create customer drafts, outboxes, approval lists, or send claims, process old Planning approvals, or send customer messages. The Sunday preparation and Monday sending workflows are retired. Follow `work-management` for preserving send evidence; remove legacy unsent updates only during an explicitly requested cleanup.
