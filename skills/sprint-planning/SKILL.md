---
name: sprint-planning
description: "Autonomous Monday sprint-planning loop: review previous week, reconcile hours/admin, improve the system, and plan current Monday-Sunday Sprint."
created_by: agent
---

# Sprint Planning

Use for Sil's early Monday autonomous sprint-planning loop. This replaces separate weekly review, weekly planning, commercial cleanup, Productive hours, and system-improvement crons.

Goal: run like `work-triage`: do the allowed work, update the system, and output a concise numbered report so Sil can quickly steer if anything is wrong. Review the completed Monday-Sunday work week, reconcile admin/hours, clean obvious operational issues, gather coaching/monday planning context, create or suggest system-improvement work, and prepare the current Monday-Sunday Sprint.

Use supporting skills as domain rules:

1. `work-management` for Notion Tasks/Projects/Customers/Sprints and statuses.
2. `work-planning` for Sprint body/planning mechanics, adjusted to Monday-Sunday weeks.
3. `work-execution` for choosing inline work vs subagents vs separate threads.
4. `productive-io` for Productive hours evidence and write safety.
5. `commercial-cleanup` + `moneybird` for finance/commercial safety.
6. `system-improvement` + `system-hygiene` + `hermes-agent` for automation/skill/cron cleanup and prevention improvements.
7. `notion` for Notion API/CLI mechanics.

## Timing model

1. Sprint/work weeks are Monday-Sunday.
2. The Monday 06:00 run reviews the just-completed previous Monday-Sunday week and plans the current Monday-Sunday Sprint.
3. Notion normally creates/closes Sprints automatically. Do not create/close Sprint pages unless a required page is missing and safe creation is clear.
4. Use live Sprint dates/statuses from Notion; do not hardcode Sprint names.

## Required phases

### 0. Mandatory external planning context subagents

Start these two bounded subagents before making final review/planning decisions:

1. **Trackler/business-coach context subagent**
   - Load/use `trackler-nl`.
   - Read the Trackler business-coach track, especially recent communication and weekplanner/schrift photos Sil shared.
   - Extract review/planning signals, decisions, commitments, blockers, and improvement ideas.
   - Trackler is read-only. If login/session blocks access, return `Blocked: Trackler login/session required` and continue with other phases.

2. **monday.com planning context subagent**
   - Load/use `monday-com`.
   - During weekly planning, inspect relevant Monday boards, especially Teveo/Fayn sprint/backlog context.
   - Always inspect the `Main table` first as source of truth, then filtered views/groups only as needed.
   - Return concrete ticket/context findings and Notion writeback suggestions; monday.com is read-only.

Use subagent findings as inputs to review/planning. Verify live Notion state before writing. Do not let subagents make final broad decisions or unsafe writes.

### Collector scripts

Sprint-planning uses small optional read-only collectors, not one broad lane dump. Run only the collectors needed for the current phase:

1. `scripts/collect_sprints.py --format yaml` — recent/current Sprint pages and linked Task ids.
2. `scripts/collect_open_tasks.py --format yaml` — all open Tasks (`Triage`, `Backlog`, `Todo`, `Doing`, `Waiting`) for planning selection.
3. `scripts/collect_review_tasks.py --after <prev-week-start> --before <prev-week-end> --format yaml` — Tasks edited during the review week for completed/carried/blocked review.
4. `scripts/collect_active_projects.py --format yaml` — active Projects for planning/routing context.
5. `scripts/collect_active_customers.py --format yaml` — active/prospect Customers for matching work.
6. `scripts/collect_calendar_context.py --after <week-start> --before <week-end> --format yaml` — calendar constraints/context only when needed.

Do not run all collectors reflexively. Fetch full Notion pages/bodies only before interpreting or writing a specific Sprint/Task/Project/Customer.

### 1. Review last week

Inspect Notion first:

1. Last/current Sprint page and linked Tasks.
2. Tasks completed, canceled, changed, blocked, or carried during the week.
3. Active Projects/Customers with meaningful movement.
4. Recent triage/work-prep outputs only as context for patterns; verify live Notion state before writes.

Write a compact practical review into the completed/current Sprint body:

```md
## Review

- Completed: concise summary.
- Carried over: tasks that still matter and why.
- Blocked/waiting: blockers or decisions needed.
- Notable changes: customer/project/work movement worth remembering.
- Hours/admin: Productive/commercial state if relevant.
```

No personal reflection or energy journaling.

### 2. Reconcile hours/admin

Productive hours are part of sprint-planning, not a hidden separate extra task.

1. Reconcile/register Productive.io hours for the previous Monday-Sunday week when evidence is strong enough.
2. Use visible Notion context, Sprint/Tasks/Projects, Productive existing entries, calendar, GitHub/PR evidence, and Moneybird/contracts/invoices when needed.
3. Preserve existing Productive entries; fill gaps before changing existing entries; do not delete entries unless Sil explicitly asks.
4. Do not create recurring/follow-up Notion Tasks named `Productive hours reconcile`; the sprint-planning cron itself owns this recurring reconciliation.
5. If evidence or IDs are unclear, report `Blocked:` or update the current owning Sprint/admin context instead of spawning a new recurring reconcile task.

Commercial cleanup:

1. Check open Notion commercial loops and Moneybird state.
2. Link existing documents or create draft/concept documents only when `commercial-cleanup` evidence requirements pass.
3. Never send invoices/estimates or destructive finance changes without approval.

### 3. Improve the system

Look for repeated friction from the week:

1. Hidden recurring work that should be visible in Notion.
2. Triage adding too much body text instead of references.
3. Duplicate/stale Tasks or unclear Task bodies.
4. Stale cron/skill prompts or wrong schedules/names.
5. Repeated blockers from auth, schema, context, delivery, or finance evidence.
6. Clearly Hermes-owned generated clutter.

Act when safe. Otherwise create/suggest concrete improvement Tasks. Improvement Tasks should be visible in Notion and linked to the current Sprint when they should be worked on this week.

Known correction: weekly Sprint automation has been set up correctly for Monday-Sunday from 2026-07-06 onward. Do not reopen/create `Fix weekly Sprint automation dates to Monday-Sunday` just because old Sprint pages still show earlier transient dates; only raise a new issue if newly-created future Sprints are still wrong.

### 4. Plan current week

Prepare the current Monday-Sunday Sprint:

1. Fill the current Sprint body with a compact plan.
2. Use Trackler/business-coach signals and monday.com board findings as first-class planning inputs, alongside Notion Tasks/Projects/Sprints.
3. Link/select Todo, Backlog, Triage, Doing, Waiting, due-soon/overdue Tasks that should be in the current Sprint.
4. Create or update planning/improvement Tasks when the review shows concrete follow-up work.
5. Do not overload the Sprint. If everything is important, the plan is fake.
6. Do not do broad inbox triage; triage has its own daily cron.
7. Do not execute customer delivery work in this cycle.

Preferred current Sprint body:

```md
## Plan

- Focus: short practical theme.
- Planned: selected Tasks/work packages.
- Admin/hours: recurring/admin work expected this week.
- Watch: blockers, decisions, deadlines, capacity risks.
- Improvements: system/process improvements planned or proposed.
```

## Subagents and separate threads

Mandatory subagents:

1. Start a Trackler/business-coach subagent at the beginning of the run using `trackler-nl`.
2. Start a monday.com planning subagent when entering weekly planning using `monday-com`.

Additional subagents are optional and only for bounded independent checks that feed this run, for example:

1. Fresh-context review of Notion planning choices.
2. Focused Moneybird/Productive evidence inspection after the owning Task is known.
3. Hermes cron/skill consistency review.
4. Detect duplicate/stale Tasks from a constrained query set.

Do not use subagents for broad private inbox collection; use existing triage outputs and Notion. Subagents cannot ask Sil questions, so they must return evidence, blockers, and exact links/IDs.

Use separate Codex/Hermes threads only for concrete implementation work Sil may inspect/resume later. Seed the thread with Notion links, objective, constraints, and stop conditions.

## Autonomous action policy

Default: act first when the action is inside scope, reversible/low-risk, and evidence is clear. Do not pause to ask for permission for normal sprint-planning work; do the work and report it in the final numbered list so Sil can correct/steer after.

Allowed without asking when evidence is clear:

1. Fill Sprint review/plan bodies.
2. Link Tasks to the current Sprint.
3. Create/update visible Notion Tasks for concrete work/improvements.
4. Update obvious statuses/context from live evidence.
5. Link existing Moneybird documents to Notion.
6. Create draft/concept Moneybird documents only when all commercial-cleanup evidence requirements pass.
7. Patch Hermes skills/prompts when a concrete approved workflow change or repeated failure is clear.
8. Remove clearly obsolete Hermes-generated clutter following `system-hygiene` rules.
9. Create `Decision:` or `Blocked:` output items instead of asking mid-run when context is unclear.

Approval still required before:

1. Sending customer/vendor messages.
2. Sending invoices/estimates.
3. Voiding/deleting/crediting finance documents.
4. Deploying/publishing live customer work.
5. Deleting Notion records, logs, sessions, memories, customer files, repos, or app code.
6. Broad database/schema/template restructuring.

## Output format

Return one clean numbered list, only concrete changes/blockers/decisions, matching the terse `work-triage` style. One item = one action, change, blocker, or decision. No prose intro/outro.

Prefixes:

- `Review:` Sprint review/body update.
- `Hours:` Productive hours result or blocker.
- `Finance:` Moneybird/commercial result or blocker.
- `Plan:` current Sprint body/task planning result.
- `Task:` Task created/linked/updated.
- `Improvement:` prevention/system improvement suggestion or created task.
- `Automation:` cron/skill/config/routing change.
- `Cleaned:` safe cleanup actually done.
- `Decision:` Sil must choose/approve.
- `Blocked:` missing access/context/schema/evidence.
- `Failed:` tool/API failure with practical consequence.

Keep output concise and link useful Notion/Moneybird pages. Suppress internal checks and rediscovered facts.

If nothing meaningful changed, output exactly:

```md
1. Plan: no sprint-planning changes needed.
```
