---
name: work-execution
description: Execute planned Notion work from Todo/Doing/Sprint into real deliverables, with context gathering, verification, status updates, and blocker handling. Use when the user asks to work on a Notion task, execute planned work, pick up Todo/Doing items, complete client/admin/sales/grow tasks, or continue from a Notion task prompt.
---

# Work Execution

Use this for doing planned work. Intake belongs to `triage`; system improvement belongs to `planning-and-review`.

Default: execute only an explicitly named task. The skill may suggest candidate tasks, but must not choose and start work unless the user says to pick one or an authorized job/cron explicitly grants that choice.

## Source of truth
- Notion tasks are the execution layer.
- Projects hold durable context; tasks are work packages/workloads that hold executable context, batches of related improvements, approvals, and follow-up state.
- Use the Notion API.
- Read task properties and body before acting.
- For project work, read linked project context when it affects execution.
- Before changing any task/project body, read it first. Never append blind.

## Collectors
Read your workspace `TOOLS.md` if present.

Use:
- `{baseDir}/scripts/collect_execution_tasks.py`
- existing task prompt formula when available: `Work on Notion task <id>. Look into the Notion page for more context, using the notion markdown API.`

## Execution order
1. Identify the exact task and intended deliverable.
2. Read the full task body, references, project, repo/domain, contacts, Moneybird IDs, and recent source links needed to act.
3. Decide: execute now, ask a right-sized grill/clarification, or mark/leave blocked.
4. If context is incomplete, first check the obvious linked sources: task body, references, project, repo/domain, and recent linked communication. If still unclear, ask concise sequential questions until the execution path is safe enough. Do not over-grill simple work; do not under-grill risky, ambiguous, client-facing, production, billing, or commercial work.
5. Move task to `Doing` only when actually starting substantial work.
6. Execute with the right lane/tool.
7. For broad work packages: if the batch is safe, clear, and not complex, complete it in one run; if it is risky, difficult, ambiguous, or likely to affect client trust/production/commercial terms, pause between meaningful batches for feedback or confirmation.
8. Verify with the smallest meaningful gate.
9. Update the task body/status with result, evidence, and next action.

For real task execution, always update Notion so the source of truth stays current. Exception: if the work was only exploratory, drafting, or pre-approval thinking, update only when it adds useful execution context.

## Lane rules
- Delivery: preserve client trust. Verify build/test/screenshot/preview where possible. Do not send client messages unless explicitly asked.
- Sales: produce proposal, scope, estimate, or follow-up draft. Ask before sending or changing external commercial documents.
- Admin: prefer exact, reversible operations. Be careful with billing, domains, credentials, and accounts.
- Grow: turn vague ideas into concrete artifact, research note, prototype, or next task. Avoid pretending exploration is completion.
- Personal: ask before privacy-sensitive, purchase, booking, or external actions.

## Coding work
- Local repos live in the flat repo root `~/projects`. Do not use workspace/state directories for active repo work.
- Resolve the repo from task/project properties, then match it to a directory directly under `~/projects`.
- Default branch policy for local repos: work from `preview` when `origin/preview` exists; otherwise use `main`. Legacy feature/fix branches may remain locally but are not the default execution target.
- Inspect current git status first.
- Use a branch/worktree if the repo is already dirty or task is non-trivial.
- Use coding agents/subagents automatically for non-trivial coding or research when useful.
- Default coding agent/model: Codex 5.5.
- For creative design/frontend direction tasks, use Claude.
- Bound delegated work to one clear task; no external sends, deploys, or irreversible actions.
- Require verification/evidence back from delegated agents.
- Main agent owns final Notion update and user summary.
- Run relevant tests/lint/build/typecheck before claiming done.
- For UI/frontend changes, capture screenshot or browser verification when feasible.
- Do not mark Done without evidence or a named blocker.

## External actions
Ask first before:
- sending email/Slack/WhatsApp/client messages
- creating/sending invoices, estimates, proposals, or contracts, except when the user explicitly requested it or a high-confidence accepted-proposal handoff requires a draft invoice
- deleting, deploying, publishing, billing, buying, booking, or changing credentials
- making irreversible account/domain/DNS/production changes

Drafts are fine; sends are not.

Client/message drafts during execution:
- Email lane: allowed to draft when the task naturally reaches a client response.
- Other lanes for now: do not draft unless explicitly asked; there is no reliable draft system yet.
- Do not use the main Notion task body as a generic draft container; it is primarily execution context.
- Never send without explicit approval.

## Status rules
- Treat each Notion task as a work package, not a tiny todo. A task may contain a batch of related improvements and multiple execution notes.
- `Todo`: ready but not started.
- `Doing`: active work is underway or was just advanced.
- `Waiting`: blocked by named person/system/decision; body states exactly what is needed. Waiting status itself is the follow-up reminder; do not create a separate follow-up task just to remind.
- `Done`: internal/admin/coding deliverable is complete and verified, or explicitly completed by user/source evidence. For client-facing deliverables, use `Waiting` when user/client approval or delivery is still needed; use `Done` only after delivery/approval is clear.
- `Canceled`: explicit cancellation/no-longer-needed only.
- Do not leave understood execution work in `Triage`.

## Sales to delivery handoff
Tasks should be named after the durable work package, not the temporary sales phase. Avoid titles like `... proposal`; prefer outcome/work-package titles like `Ambdetailing website`.

When a proposal task becomes accepted work:
- keep the same Notion task by default so AI execution context stays in one place
- change task Type from `Sales` to `Delivery`; do not mark it `Done` if delivery work remains
- set the Moneybird quote/estimate to accepted when needed
- prepare a new draft invoice in Moneybird when invoicing should follow from the accepted proposal
- add Moneybird references for the accepted quote and draft invoice when available
- restructure the task body for execution: put current delivery scope/next actions at the top, keep relevant proposal context/agreements below, and remove or compress only noise
- create separate Delivery tasks only when one accepted proposal creates multiple distinct work packages

## Follow-up splitting
Create separate follow-up tasks only when the new work is genuinely separate from the current work package: different deliverable, later phase, different owner/context, or too large to keep clear. Do not split out routine waiting, approval, or next-check reminders; keep those inside the existing task and set `Waiting`.

## Completion note
Every completed/advanced task should stand alone:
- what changed or was produced
- evidence: test/build/screenshot/PR/link/file/draft
- decisions made
- remaining blocker or next step
- whether user/client action is required

## Telegram summary
Keep it short:
1. `Done:` / `Advanced:` / `Blocked:` / `Drafted:` prefix
2. task link/name
3. concrete result + evidence
4. one next action if needed

No filler. No long recap.
