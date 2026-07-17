---
name: customer-work
description: "Gate scoped customer delivery through context, preview, approval, release, and closeout. Use when implementing or QAing customer-visible work, preparing previews, handling approval, publishing approved changes, or handing off completed work."
---

# Customer Work

1. **Scope gate.** Read the owning Task and relevant Project or Customer through `work-management`. The gate passes when the agreed outcome, exhaustive acceptance checklist, delivery target, approval rule, and authorization are explicit. Return the exact missing boundary before execution when the gate does not pass.
2. **Preview gate.** Complete or inspect the agreed scope, then verify every acceptance item against the actual preview or customer-visible environment. Record evidence for each item. The gate passes when every item passes or each exception is explicitly reported.
3. **Approval gate.** When release or handoff requires approval, record the approver, source, date, target, and approved scope through `work-management`, and set the Task to `Waiting`. The gate passes when the approved scope and target are unambiguous.
4. **Release gate.** Release or hand off the approved scope, then rerun the complete acceptance checklist on the final customer-visible result. The gate passes when every item passes in the delivery target.
5. **Closeout gate.** Write the result, evidence, useful links, and resulting state through `work-management`. Mark `Done` when every acceptance item passes and the agreed delivery outcome is confirmed.

`work-management` owns Task, Project, and Customer context and state. This skill owns execution and delivery gates.

`customer-communication` owns the content and output format of customer-facing drafts and updates.
