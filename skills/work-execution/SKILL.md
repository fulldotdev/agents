---
name: work-execution
description: Use when the user asks to implement, change, fix, QA, preview, release, deploy, publish, or hand off scoped work.
---

# Work execution

This skill owns execution from agreed scope to a verified result. It does not own planning records or customer message wording.

Use `work-management` when an existing Task, Project, Company, or Document must be read or updated. Do not create a record just because this skill runs. Use `customer-communication` for customer-facing drafts and updates.

## Choose the branch

Apply the customer rules when the work meets any of these conditions:

- It changes a customer's site, app, store, repository, account, environment, or data.
- It creates or changes a deliverable promised to a customer.
- A customer will review, use, or see the result.

Internal tools, personal work, sales exploration, and reusable assets use only the regular rules unless they are part of an agreed customer deliverable. If the branch remains unclear, local investigation may continue. Resolve the branch before publishing or changing a live customer-owned target.

## Regular rules

1. Read the request, repository instructions, and sources that define the outcome. At the start of a development session, inspect `git status`. Preserve unrelated changes, and pull only when the worktree is clean with no open local changes.
2. Confirm the deliverable, target, and stopping boundary. Ask only when missing information would change the result, risk, or authorization.
3. Follow repository-specific branch rules. Otherwise continue the current task branch, use `preview` for normal work when available, and use `main` for production. Teveo and fayn Shopify repositories default to `main`. Use a worktree only when the user asks for one.
4. Reuse a responsive project dev server when available. Otherwise start the project's normal dev command and keep it running for the thread.
5. Implement only the agreed scope in the appropriate local or preview environment. Use specialist skills when the work needs them.
6. Verify in proportion to risk with the relevant test, build, or target environment. For visual changes, inspect screenshots in the target environment and iterate until the result matches the intended design.
7. Commit, push, publish, or release only when the request and repository workflow authorize that step.
8. Return the result, useful URLs including the local or preview URL, verification, and any concrete limitation. When an owning Notion record exists, use `work-management` to record evidence and update its status after verification.

Do not add customer-specific local or preview approval stages to regular work. Follow the approval boundaries in the request, repository, and shared instructions.

## Customer rules

Apply these rules in addition to the regular rules:

1. Derive the agreed outcome and customer-visible requirements from direct sources. Resolve missing business intent before a customer-visible change or release.
2. Choose local review, a shared preview, or both based on the task and repository. One approved shared preview is enough unless the user asks for a separate local review.
3. Before production release, obtain explicit approval for the exact preview, commit, scope, and customer target. Approval already given for that exact release in the current request counts.
4. Release only the approved version and scope. Verify the final customer-visible result on its production target.
5. When an owning Notion record exists, use `work-management` to record the source, approval, preview or commit, and final verification. Keep mutable deliverables in the related Document or canonical external file.
6. Use `customer-communication` for the handoff, status update, approval request, or explanation sent to the customer.

If customer approval is missing, finish the safe preparation and stop before production release. Report the exact approval or business decision still needed.
