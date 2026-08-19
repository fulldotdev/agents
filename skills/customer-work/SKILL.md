---
name: customer-work
description: "Gate scoped customer delivery through context, preview, approval, release, and closeout. Use when implementing or QAing customer-visible work, preparing previews, handling approval, publishing approved changes, or handing off completed work."
---

# Customer Work

1. **Scope gate.** Read the owning Task and relevant Project or Customer through `work-management`. The gate passes when the agreed outcome, exhaustive source-grounded acceptance conditions, delivery target, approval rule, and authorization can be derived explicitly from direct Timeline events and live sources. Do not invent missing criteria or treat absence as agreement; return the exact missing boundary before execution when the gate does not pass.
2. **Local review gate.** Implement the agreed scope locally and keep the code changes uncommitted and unpushed. Verify every source-grounded acceptance condition locally, provide a localhost URL, and set the Task to `Waiting` for review. Append the local-review result only as a source-specific Timeline event through `work-management`, using a stable Codex locator for the execution session; a localhost URL alone is not durable provenance. The gate passes only after the user explicitly approves the local result.
3. **Preview gate.** After local approval, commit and push the approved changes to the repository's preview branch or create the agreed shared preview. Verify all source-grounded acceptance conditions on that preview. Append the preview URL, commit, and direct verification evidence as source-specific Timeline events through `work-management`, then request explicit approval for the production target. The gate passes only after that preview approval.
4. **Release gate.** Merge or release only the preview-approved commit and scope to the production branch or target. Rerun all source-grounded acceptance conditions on the final customer-visible result and append the direct release evidence as a source-specific Timeline event.
5. **Closeout gate.** Append the result, evidence, useful links, approvals, and resulting state only as source-specific Timeline events through `work-management`. Mark `Done` when every source-grounded acceptance condition passes and the agreed delivery outcome is confirmed. Never create or restore Task body sections such as `Next`, `Done when`, `Context`, `State`, `References`, `Delivery plan`, `Local review`, or acceptance checklists; derive them at read time from Timeline events and live sources.

For mutable authored deliverables such as copy, briefs, scopes, specifications, research, or designed assets, create or reuse a related `Documents` record through `work-management`. Keep the full work product and attachments in that Document or its canonical external `Source URL`; keep the Task body limited to source-grounded lifecycle and delta events that link the Document. Never paste the complete mutable artifact into the Task Timeline.

`work-management` owns Task, Project, Customer, and Document context and state. This skill owns execution and delivery gates.

`customer-communication` owns the content and output format of customer-facing drafts and updates.
