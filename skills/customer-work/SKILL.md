---
name: customer-work
description: "Gate scoped customer delivery through context, preview, approval, release, and closeout. Use when implementing or QAing customer-visible work, preparing previews, handling approval, publishing approved changes, or handing off completed work."
---

# Customer Work

1. **Scope gate.** Read the owning Task and relevant Project or Customer through `work-management`. The gate passes when the agreed outcome, exhaustive acceptance checklist, delivery target, approval rule, and authorization are explicit. Return the exact missing boundary before execution when the gate does not pass.
2. **Local review gate.** Implement the agreed scope locally and keep the code changes uncommitted and unpushed. Verify every acceptance item locally, provide a localhost URL, and set the Task to `Waiting` for review. The gate passes only after the user explicitly approves the local result.
3. **Preview gate.** After local approval, commit and push the approved changes to the repository's preview branch or create the agreed shared preview. Verify the complete acceptance checklist on that preview, record the URL and evidence through `work-management`, and request explicit approval for the production target. The gate passes only after that preview approval.
4. **Release gate.** Merge or release only the preview-approved commit and scope to the production branch or target. Rerun the complete acceptance checklist on the final customer-visible result.
5. **Closeout gate.** Write the result, evidence, useful links, approvals, and resulting state through `work-management`. Mark `Done` when every acceptance item passes and the agreed delivery outcome is confirmed.

`work-management` owns Task, Project, and Customer context and state. This skill owns execution and delivery gates.

`customer-communication` owns the content and output format of customer-facing drafts and updates.
