---
name: system-hygiene
description: Use when reviewing the user's Macs, shared skills, tooling, project leftovers, and automations for periodic maintenance. This is inspection only.
---

# System hygiene

You propose, the user decides. Do not clean up, install, upgrade, change Git, stop processes, restart services, deploy, or change schedulers during a review. Large migrations are separate projects.

## Review

Read [checks.md](references/checks.md) and `~/.local/state/fulldev/system-hygiene/state.json`. Read the user's recent replies in the System chat for decisions.

Read `~/.local/state/fulldev/health/report.json` on Otis first. It combines Otis checks with MacBook's submitted status. Check each machine's timestamp: a stale MacBook report is missing coverage, not a pass or a failure. Use these results for routine service, routing, storage and scheduled-job checks; investigate differences and maintenance needs. Read [health setup](../../global/references/health.md) for commands, thresholds, delivery and incident threads.

MacBook submits status to Otis through a restricted SSH key. Otis has no inbound SSH access to MacBook. For deeper MacBook inspection, work locally when available; otherwise report the gap. Backup setup and personal iCloud sync are intentionally outside this healthcheck.

Cover all eight check areas each week. The skills check in `checks.md` describes what a clean skill looks like; propose edits when a skill drifts from it. Start with an overview, then look closer at changes that could affect work. Review apps, plugins, and models in depth once a month, or sooner for a specific issue. Use CLI help and official docs when needed. Do not scan every project's dependencies, fetch every repository, or propose an upgrade just because a newer version exists.

For each finding, name the machine and the exact target. Give the evidence, the effect on work, the proposed action, and what deleting or stopping it would cost. Prove that something is unused before you propose removing it, and say when you are unsure.

## Boundaries

- Production, Shopify themes, and active previews are inspection-only. Do not upload a theme or create a preview for this review. Prefer local evidence over signing in to customer services.
- Only the continuity file may change. Reports may name paths, sizes, and status, never secrets, customer messages, or database contents.
- Do not message customers or other chats.
- When the user follows up on a finding, recheck the target and its current use before acting with the relevant skill. An old approval is never a new cleanup instruction for a scheduled run.

## Continuity

Keep one small JSON file at `~/.local/state/fulldev/system-hygiene/state.json` with the last run date, the last monthly review, and the findings the user dismissed or deferred, by machine and target. Do not repeat those unless the user asks or the facts changed enough to matter. Do not build a second task system or track report delivery.

## Output

One English message in this format:

```text
System hygiene · 20-09

1. Otis · ~/.cache/fulldev: 14 GB of old triage batches, disk 91% full. Proposal: delete everything older than 30 days, frees 12 GB.
2. MacBook · Node: 18 and 22 are both installed, pnpm sometimes picks 18. Proposal: remove 18; no project uses it.

Covered: Otis and MacBook. Not checked: Shopify CLI on MacBook.
```

- Each finding: machine and target, what you found and why it matters, then `Proposal:` with the action and its cost or saving. One or two short sentences.
- At most five findings, ordered by impact. Urgent findings may exceed five. Group only closely related targets.
- Normally under 1,500 characters. No tables, nested lists, generic advice, or checks that passed.

With no new findings, write `System hygiene · DD-MM: no new action points.` If coverage was incomplete, say what was missing and do not imply everything is healthy.

In a scheduled run, return only this report. In an interactive review, answer in the conversation.
