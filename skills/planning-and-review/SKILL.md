---
name: planning-and-review
description: Review the work system for workflow improvements, missed follow-ups, automation opportunities, stale structure, and recurring blockers. Use for weekly review, system review, planning hygiene, workflow-improvement scans, and careful follow-up identification; not for routine inbound triage.
---

# Planning and Review

Use this to improve the work system around Notion tasks/projects. Not for daily status churn; incoming work belongs to `triage`.

## Source of truth
- Notion tasks are the execution layer.
- Projects hold durable context; tasks hold executable context.
- Use the Notion API.
- Read properties through Tasks or Projects.
- Read page bodies through `GET /v1/pages/{page_id}/markdown`.
- Before changing any task/project body, read it first. Never append blind.

## Collectors
Read your workspace `TOOLS.md` if present.

Use:
- `{baseDir}/scripts/collect_weekly_review_tasks.py`
- `{baseDir}/scripts/collect_projects.py`
- `{baseDir}/scripts/collect_tasks.py`

## Review focus
Look for:
- missed follow-up tasks from completed work
- recurring blockers, handoff failures, noisy loops
- stale, duplicated, fragmented, or unclear task/project structure
- patterns where triage/planning/execution keeps failing
- clear automation, simplification, or deduplication opportunities
- short workflow-improvement signals worth acting on

Do not infer priority from task state alone.
Do not create review tasks that only restate messy work.

## Allowed outcomes
Prefer this order:
1. leave unchanged and note the system issue
2. enrich an existing task/project with genuinely missing context
3. create a follow-up only when completed work clearly produced new tracked work
4. surface a short workflow-improvement recommendation
5. make a high-confidence structural correction already proven by Notion evidence

## Writing rules
Notion pages must stand alone.
- copy useful execution context into the body
- summarize the pattern, blocker, decision, or next step
- preserve enough detail to act without reopening the source trail
- avoid duplicate context and overwritten structure

## Telegram summary
Always use:
1. one short paragraph looking back
2. numbered list with 1–3 concrete actions
3. one short paragraph looking ahead

Rules:
- no filler
- paragraphs short and specific
- numbered list is action-only, not recap
- if no action is needed, use one item saying no direct action is needed

## State
- run logs: workspace `state/review/runs/`
- checkpoint: workspace `state/review/checkpoint.json`
- checkpoint ownership belongs to the caller or cron wrapper
