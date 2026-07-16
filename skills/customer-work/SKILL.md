---
name: customer-work
description: "Execute, verify, review, and deliver scoped customer work. Use when implementing customer work, QAing customer-visible changes, preparing or checking previews, handling approval, publishing production changes, releasing, or handing off completed work."
---

# Customer Work

1. Read the owning Task and relevant Project or Customer context through `work-management`. Confirm the agreed outcome, acceptance criteria, delivery target, and authorization; stop when any required boundary is unclear.
2. Verify the customer-visible result against the acceptance criteria on the actual preview or live URL before sharing it.
3. Default to a verified preview before production. While approval is required, set the Task to `Waiting` through `work-management` and preserve the approval source.
4. After approval, complete only the agreed release or handoff and verify the final customer-visible result.
5. Write the result, evidence, useful links, and resulting state back through `work-management`. Mark `Done` only when the agreed delivery outcome is confirmed.

Use `customer-communication` for customer-facing drafts or updates.
