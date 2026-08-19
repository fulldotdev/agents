# Planning

Use for Sil's minimal Monday work reset. The goal is only to make live Task statuses accurate and commit the right Tasks to the current Monday-Sunday Sprint.

Normal automation cadence is Monday at 06:00 Europe/Amsterdam through the Hermes `work-planning` cron. Actual automation metadata wins.

## Scope

Inspect live Notion only:

- the current Sprint;
- open Tasks and their authoritative `Status`;
- Tasks related to the previous or current Sprint;
- hard due dates inside the current week;
- concrete `Waiting` blockers that affect this week's work.

Do not run broad inbox, calendar, Trackler, monday.com, Productive, Moneybird, Customer, Project, Someday, database-health, or personal-review scans. Do not write Sprint reviews or planning narratives. Handle those workflows separately when explicitly requested.

## Workflow

1. Resolve the current Sprint and its Monday-Sunday dates from live Notion. Notion creates and advances Sprint pages automatically: never create, duplicate, date, rename, close, or otherwise manage Sprint pages manually. If the expected current Sprint is missing or ambiguous, report the blocker instead of creating one.
2. Inspect relevant open Tasks and read full pages only when needed for a safe status or Sprint decision.
3. Correct only clearly wrong Status properties from direct evidence or an explicit user decision:
   - `Todo`: executable but not started;
   - `Doing`: started and unfinished;
   - `Waiting`: blocked by a concrete dependency;
   - `Done`: completed and verified;
   - `Canceled`: explicitly dropped, superseded, externally owned, or duplicate.
   The Status property is the sole source of truth. Never maintain a body `State` or status label. Append blocker, progress, decision, and verification facts only as direct source-specific Timeline events under the main skill's rules; do not infer them from missing context.
4. Put every explicit commitment to substantial work this week in the current Sprint. Include active `Doing` work, hard due dates inside the week, and consciously committed `Todo` work. Prefer completion within the week, but allow an external delivery just after Sunday when execution is deliberately scheduled this week.
5. Recommit unfinished work deliberately; do not roll everything forward automatically. Todo without a Sprint remains valid unscheduled work.
6. Do not add work merely because it is urgent or due next week. Check only whether a hard deadline or concrete `Waiting` blocker would otherwise disappear from view.

Do not create new Tasks, alter Projects or Customers, reconcile hours or finance, rewrite healthy records, or broaden the run beyond statuses and Sprint membership unless explicitly requested.

## Report

Return one compact numbered list. One line equals one concrete Task change or blocker. Every Task name must link to its Notion page. Use the same structure as triage:

```md
1. **Task updated** — [Productive-uren fixen](url) — Status corrected to `Doing`.
2. **Task planned** — [Teveo sprint 14](url) — Moved into Sprint 15.
3. **Blocked** — [Send estimate](url) — Waiting on the confirmed scope before Friday.
```

Use only concise labels such as `Task updated`, `Task planned`, `Task removed`, `Blocked`, or `Failed`. Keep the description to one short sentence. Omit reviews, totals, unchanged facts, implementation detail, source metadata, and headings.

If nothing changed:

```md
1. **Planning** — No changes needed.
```
