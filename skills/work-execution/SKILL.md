---
name: work-execution
description: "Run Notion-backed work with flexible execution judgment: choose inline work, subagents, or separate agent sessions/threads such as Codex app or Hermes based on scope, freshness of context, reviewability, and follow-up needs."
---

# Work Execution

Work execution turns Notion work into action. It is not a rigid mode system. Pick the smallest working structure that gives the agent enough fresh context, keeps risk controlled, and leaves Sil with something easy to inspect or continue.

Use `work-management` as the source of truth for Notion Tasks, Projects, Customers, Sprints, statuses, body conventions, and safe writes.

Domain skills own domain rules:

1. Use `moneybird` for offers, invoices, recurring billing, and Moneybird write safety.
2. Use `productive-io` for Productive hours, time-entry evidence, and Productive write safety.
3. Use project/domain skills such as Shopify, Sanity, frontend, repo, or customer-communication skills when the work enters that domain.

## Domain Preflight

Do not call Moneybird or Productive during broad exploration. First prove all three facts from the Notion source context:

1. **Executable candidate**: the task/project has a concrete next action, not just a possible domain to inspect.
2. **Allowed action**: the cycle is allowed to do that action now, or is explicitly limited to read-only preflight.
3. **Source owner**: the Notion task/project/customer that owns the action is known and should receive the writeback.

If any of those are missing, stop before loading `moneybird` or `productive-io` and return `Blocked:` or `no safe execution actions found`. Domain preflight may read Notion and local notes only; it must not create, update, send, publish, or sync customer-system records.

## Core Principle

Fresh context makes agents smarter. Split work when a fresh thread or subagent will materially improve reasoning, reduce contamination from old assumptions, or make the result easier to check.

Do not split work for theater. If the task is small, local, and low-risk, do it inline.

## Choosing The Shape

Choose one of these shapes per cycle:

1. **Inline work**: best for small reads, simple updates, clear status summaries, or one-step fixes.
2. **Subagent**: best for focused research, review, validation, second opinions, or independent context gathering inside the current task.
3. **Separate agent session/thread**: best for a concrete workstream Sil may want to inspect, resume, branch from, or follow up on later; this can be Codex app, Hermes, or another appropriate agent surface.

Prefer a separate thread when:

1. the work is a distinct task or workstream,
2. the agent needs fresh context to avoid being biased by the current conversation,
3. follow-up questions or iterations are likely,
4. the result should be independently reviewable by Sil,
5. the work touches a separate repo, customer, output type, or delivery lane,
6. the work may take long enough that progress and state deserve their own place.

Prefer a subagent when:

1. the result feeds the current answer or current thread,
2. the subtask is bounded and does not need direct user follow-up,
3. you want fresh-context review before calling work ready,
4. you need parallel collection of facts from known sources.

Keep work inline when:

1. the context is already present and reliable,
2. the action is reversible and low-risk,
3. splitting would add more coordination than clarity.

## Running A Cycle

For any meaningful execution cycle:

1. Read the relevant Notion task/project/customer context.
2. Pass domain preflight before loading Moneybird or Productive.
3. Load only the domain skills needed for the proven next action.
4. Decide the execution shape: inline, subagent, or separate thread.
5. Do one bounded piece of work.
6. Verify at a level matching risk: tests, build, dev server, browser check, API readback, screenshot, document validation, or fresh-context review.
7. Leave durable state in Notion or return an exact writeback block.
8. End with a clear next state: done, waiting, needs approval, blocked, or ready for follow-up.

## Separate Threads

Separate threads are for user-checkable work lanes, not mandatory roles. Use the surface that best fits the work: Codex app for coding threads Sil may continue there; Hermes for tool-heavy or gateway-scheduled work; subagents for bounded current-answer research/review.

When starting one, give it a concrete name based on the work, for example:

1. `Teveo checkout QA`
2. `Moneybird estimate cleanup`
3. `Fayn sprint ticket 123 implementation`

Avoid artificial prefixes such as fixed modes unless the user asked for that structure.

The starter should pass enough context for the thread to operate independently:

1. objective,
2. Notion task/project links or IDs,
3. known constraints and approvals,
4. relevant sources already read,
5. expected output,
6. writeback expectations,
7. when to stop and ask.

Use separate threads especially when the first output is likely a start, draft, investigation, or implementation that Sil will want to open and continue from.

## Subagents

Use subagents for sharp, bounded work:

1. review an implementation,
2. check regressions or missing tests,
3. inspect a specific source or repo area,
4. validate UI/browser behavior,
5. compare assumptions against Notion/source context,
6. produce a second-opinion plan.

Keep subagent prompts narrow. Do not leak your intended conclusion when asking for review. Ask for findings, risks, and concrete evidence.

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

## Notion Writeback

Every meaningful cycle should leave resumable state in Notion, or return a precise writeback block for the caller to apply.

Use body conventions from `work-management`. Keep notes short and traceable.

Minimum writeback:

```md
### YYYY-MM-DD — Work execution

- Action: what ran
- Sources: what was read
- Result: what changed or was produced
- Verification: tests/checks/review done
- Status: Done / Waiting / Needs approval / Blocked / Ready for follow-up
- Next: next action or next check date/time
- Links: thread/branch/PR/tool URL when relevant
```

Do not create diary noise. Write the facts needed to resume safely.

## Output Style

Default to short, natural status messages.

Use numbered lists when asking Sil to choose, approve, or answer multiple items. Keep each item concrete and replyable.

Include thread IDs, paths, branches, Notion links, and tool links only when they help Sil decide, inspect, or resume work.

If nothing actionable is found:

`1. Execution: no safe execution actions found.`
