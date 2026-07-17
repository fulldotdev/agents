# Planning

Use for Sil's Monday work loop: review the completed Monday-Sunday week, reconcile hours/admin, check Notion database health, and prepare the current Monday-Sunday Sprint. Planning is Notion-first and does not run broad inbox triage or customer delivery.

Normal automation cadence is Monday at 06:00 Europe/Amsterdam through the Hermes `sprint-planning` cron on `otis`. Actual automation metadata wins.

## Inputs

Always inspect live Notion state. Run `scripts/collect.py planning --after <start> --before <end> --format yaml`. It collects recent Sprints, open and review-window Tasks, active Projects/Customers, Someday, and calendar constraints.

Also gather current planning signals from `trackler-nl` and relevant Teveo/Fayn boards through `monday-com`. These sources remain read-only. Continue with other phases when one source is blocked and report the gap.

At the beginning, start a bounded Trackler/business-coach subagent. Inspect recent coach communication and especially Sil's weekplanner/schrift photos. Extract practical review and planning signals, decisions, commitments, blockers, and improvement ideas. If access is blocked, report `Blocked: Trackler login/session required` and continue.

When entering weekly planning, start a bounded monday.com subagent. Inspect relevant Teveo/Fayn sprint and backlog context, always using the `Main table` first as source of truth. Return concrete ticket findings and Notion planning/writeback suggestions. Use other optional subagents only for bounded independent checks that feed the current run; never use them for broad inbox collection.

Do not run broad inbox triage during planning. Use source context already linked in Notion and recent triage outputs only as pattern evidence. If fresh inbox context is essential, run triage as a separate labelled phase only when explicitly requested.

## Workflow

### 1. Review

Inspect the previous Sprint, linked Tasks, completed/canceled/status-changed work, carry-over decisions, blockers, and meaningful Project/Customer movement.

Write a compact review:

```md
## Review

- Completed: ...
- Carried over: ...
- Blocked/waiting: ...
- Notable changes: ...
- Hours/admin: ...
```

Keep this practical; no personal reflection or energy journaling.

### 2. Hours and commercials

Use `productive-io` to reconcile the previous week when evidence is strong enough. Prefer filling gaps over changing existing entries; never delete entries without explicit approval.

The planning loop owns weekly Productive reconciliation. Do not create recurring `Productive hours reconcile` Tasks. When evidence or IDs are insufficient, record the blocker on the owning Sprint/admin context.

Check open commercial loops through Notion and `moneybird`. Link existing documents or create drafts only when scope, contact, price, VAT, and evidence are clear. Never send estimates/invoices without approval.

### 3. Database health

Use the collected Notion picture to correct clear operational inconsistencies that affect planning:

- Check Task status, Sprint commitment, real deadlines, duplicates, and owning Customer or Project where relevant. Todo without a Sprint is valid unscheduled work.
- Check that Project status matches its real phase. Discovery may remain without an open Task. Planned and In Progress need executable work or an explicit decision; Paused only needs a deliberate hold.
- Check active Customer status and relations when current work shows an inconsistency.
- Check Someday only for items that are now clearly executable, duplicated, or no longer useful.
- Check Sprint dates, relations, repeated routing friction, collector/schema failures, and stale automation or skill instructions.

Act only on current evidence. Do not rewrite healthy records, create cleanup work merely because something is old, or turn this into a separate maintenance exercise.

### 4. Plan

1. Fill the current Sprint body with focus, planned work, admin/hours, risks, decisions, and improvements.
2. Include open Tasks due inside the Sprint unless Done, Canceled, or explicitly on hold.
3. Prefer hard commitments, active Projects, Doing work, actionable Waiting items, due-soon work, and Tasks with clear next actions.
4. Add Todo work to the Sprint when committing it for completion this week. Keep executable uncommitted work as Todo without a Sprint and vague ideas in Someday.
5. Recommit unfinished work deliberately; Sprint rollover is a planning decision.
6. Include every Task that must be completed this week. Apply no numeric capacity limit.

Preferred plan:

```md
## Plan

- Focus: ...
- Planned: ...
- Admin/hours: ...
- Watch: ...
- Improvements: ...
```

## Recurring work

- **Teveo/Fayn**: use one sprint Task linked directly to the matching Customer and Sil's Sprint. Individual monday tickets stay in monday; capture selected tickets and state in the sprint Task body. Do not create or link a Project merely because work belongs to a client sprint.
- **Teveo**: name the Task `Teveo sprint N` and infer numbering from previous Tasks.
- **Fayn**: update existing sprint work. Create new Fayn sprint work only when explicitly requested; do not use theme versions as sprint names.
- **Someday**: promote only when a concrete action/outcome or durable Project exists.
- Notion normally opens/closes Sprint pages automatically. Create a missing Sprint only when live schema makes safe creation clear.

## Safety and report

Run autonomously: complete all in-scope, safe, evidence-backed planning actions. Use `Decision:` or `Blocked:` when a hard approval gate or missing evidence prevents action.

Planning may update Sprint bodies, link Tasks, create concrete planning or improvement Tasks, and correct clear low-risk statuses. Apply the main skill's approval gate to messages, documents, customer publishing, deletion, and structural database or template changes.

Planning is complete when the previous Sprint is reviewed, Productive reconciliation is completed or explicitly blocked, commercial loops are resolved or routed, relevant database inconsistencies are corrected or reported, every weekly commitment is linked to the current Sprint, and every unavailable source has its practical consequence reported.

Return one concise numbered list using `Review:`, `Hours:`, `Finance:`, `Plan:`, `Task:`, `Improvement:`, `Automation:`, `Cleaned:`, `Decision:`, `Blocked:`, or `Failed:`.

If nothing changed:

```md
1. Planning: no changes needed.
```
