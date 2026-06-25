---
name: work-execution
description: "Run work from Notion through loop-driven Codex threads: orchestrator, project steward, and task executor modes with Notion writeback, confidence gates, sub-agent review, and domain-skill handoff."
---

# Work Execution

Work execution is the loop layer. It decides which work should run, starts the right Codex threads, and records state back to Notion.

Use `work-management` as the source of truth for Notion Tasks, Projects, Customers, Sprints, statuses, body conventions, and safe writes.

Domain skills own domain knowledge:

- Use `moneybird` for offers, invoices, recurring billing, and Moneybird write safety.
- Use `productive-io` for Productive hours, time-entry evidence, and Productive write safety.
- Use project/domain skills such as Shopify, Sanity, frontend, or repo-specific skills when a Task Executor needs that domain.

## Core Model

Notion is state. Codex threads are workers. Loops execute work by reading Notion, doing one bounded cycle, writing back, and scheduling or proposing the next step.

The active thread roles are:

1. **Orchestrator thread**: one top-level execution thread.
2. **Project Steward thread**: one thread per active project or sprint control object.
3. **Task Executor thread**: one thread per concrete task/workstream.

Task Executors may use sub-agents for review, research, and validation. They must not start new Codex threads.

## Orchestrator Thread

The Orchestrator scans Notion and decides which projects need attention.

It may directly act only when the action is clear, low-risk, and inside the allowed scope. Otherwise it reports questions and a proposed next step.

Allowed direct actions:

1. Read open Projects, active Sprints, and open Tasks.
2. Select projects with `Next check` due, fresh source context, active `Doing`/`Waiting` work, or explicit user request.
3. Start or resume Project Steward threads.
4. Produce a compact status/priorities report.
5. Record obvious scheduling state, such as a next check for a project already waiting on known evidence.

The Orchestrator must not perform delivery work, customer communication, finance writes, deploys, or broad inbox/source triage. Existing triage/source crons feed Notion; the Orchestrator consumes Notion state.

When uncertain, the Orchestrator outputs:

1. what it found,
2. what it proposes to start,
3. the questions blocking action,
4. the risk or approval needed.

## Project Steward Thread

A Project Steward owns one project, sprint, retainer, or delivery phase for the current cycle.

It reads:

1. the Project page and body,
2. linked open Tasks,
3. linked source context already captured in Notion,
4. relevant repo/tool references recorded on the Project or Tasks,
5. prior loop notes and current blockers.

It may start Task Executor threads when:

1. the task outcome is concrete,
2. source/context is sufficient,
3. the workstream boundary is clear,
4. allowed actions cover the work,
5. expected output and writeback are clear.

It must ask or propose instead of starting work when:

1. priority is unclear,
2. scope, price, timing, or customer intent is ambiguous,
3. multiple projects could own the work,
4. sources are missing or contradictory,
5. the action touches customer messages, money, deploys, data deletion, or broader private-source scanning.

The Project Steward is the only role that asks the user project-level execution questions. If Task Executors hit blockers, they report them to the Project Steward, which batches questions for the user.

## Task Executor Thread

A Task Executor performs one concrete task or workstream.

It must:

1. read the Task and relevant linked Project/Customer context,
2. load required domain skills before domain work,
3. execute the task within its allowed scope,
4. run appropriate verification such as tests, build, dev server, browser check, screenshot check, API readback, or document validation,
5. use a fresh-context review sub-agent before declaring the work ready,
6. write results back to Notion or report exactly what the Project Steward should write,
7. finish with `Done`, `Waiting`, `Needs approval`, or `Blocked`.

It may use sub-agents for:

1. implementation review,
2. regression or risk review,
3. source/context research inside the task scope,
4. UI/browser/dev-server validation,
5. second-opinion planning for the same task.

It must not start new Codex threads, broaden into unrelated tasks, interview the user directly, send customer messages, publish/deploy, or perform finance writes unless explicitly allowed by the Project Steward and the relevant domain skill.

If blocked, it reports to the Project Steward:

1. the missing fact or decision,
2. why it is required,
3. the safest assumptions if any,
4. a concise proposed question for the user,
5. the practical consequence of waiting.

## Review Rule

Reviewer is not a thread role in v1. It is a required Task Executor step.

Before finalizing user-facing, customer-facing, finance-facing, deploy-facing, or code-facing output, the Task Executor starts a fresh-context review sub-agent and asks it to check:

1. bugs or behavioral regressions,
2. missing tests or weak verification,
3. mismatch with task/project context,
4. unsafe assumptions,
5. Notion writeback completeness,
6. whether approval is required.

The Task Executor then fixes issues or escalates to `Needs approval`/`Blocked`.

## Thread Spawning Rules

Only these roles may start threads:

1. Orchestrator may start Project Steward threads.
2. Project Steward may start Task Executor threads.

Task Executors may start sub-agents only.

Start separate Task Executor threads for independent workstreams, separate repos, separate output types, or implementation versus focused investigation. Keep work sequential or stacked when tasks touch the same files, same checkout, same customer decision, or same deploy path.

## Domain Skill Handoff

Work execution chooses when domain work is needed; domain skills define how to do it.

Examples:

1. For draft invoices, estimates, billing status, or Moneybird links: load `moneybird`.
2. For Productive time entries or weekly hour reconstruction: load `productive-io`.
3. For Notion routing, relations, status, and body conventions: load `work-management`.
4. For repo or frontend work: load the relevant repo/framework/design skill.

Do not duplicate domain-specific write rules inside this skill. If the domain skill and work-execution conflict, the stricter safety rule wins and the worker escalates.

## Notion Writeback

Every Project Steward and Task Executor cycle must leave durable state in Notion or return a precise writeback block for the caller to apply.

Use the body conventions from `work-management`. Keep notes short and traceable.

Minimum writeback:

```md
### YYYY-MM-DD — Work execution

- Role: Orchestrator / Project Steward / Task Executor
- Action: what ran
- Sources: what was read
- Result: what changed or was produced
- Verification: tests/checks/review done
- Status: Done / Waiting / Needs approval / Blocked
- Next: next action or next check date/time
- Links: thread/branch/PR/tool URL when relevant
```

Do not create diary noise. Write the facts needed to resume safely.

## Approval Gates

Ask before:

1. sending customer/vendor messages,
2. sending or publishing Moneybird documents,
3. creating or changing finance documents when price, VAT, contact, scope, or acceptance evidence is unclear,
4. deploying or publishing live customer work,
5. deleting data or destructive cleanup,
6. scanning broader private sources than the current project/task requires,
7. changing cron schedules or disabling existing automations.

When approval is needed, return the proposed action, reason, risk, and exact approval question.

## Outputs

For Orchestrator and Project Steward reports, use a concise numbered list:

1. `Started:` threads or task work started.
2. `Proposed:` work that should run but needs approval or priority confirmation.
3. `Questions:` decisions needed from the user.
4. `Blocked:` missing evidence or failed source/tool.
5. `Notion:` durable state written or writeback needed.

For Task Executors, use:

1. `Done:` completed work and verification.
2. `Waiting:` external review/reaction/source needed plus next check.
3. `Needs approval:` exact approval needed.
4. `Blocked:` missing fact/tool/source and proposed question for Project Steward.
5. `Notion:` writeback completed or required.

If nothing actionable is found:

`1. Execution: no safe execution actions found.`
