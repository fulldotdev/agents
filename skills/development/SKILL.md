---
name: development
description: Apply Sil's development, local review, and handoff conventions when implementing or reviewing software in his repositories.
---

# Development

Use the repository's instructions and existing framework skills for implementation details. Choose planning, tools, and implementation depth to fit the request; there is no required planner/executor split.

## Work ownership

Continue in the existing checkout and branch by default. Sil prefers one branch with focused commits, not a worktree per task. Check actual Git state when resuming; thread metadata can be stale. If another implementation is using the checkout, coordinate or use an explicitly agreed isolated checkout rather than switching its branch or mixing changes.

Notion owns Sil's commitments; an existing customer ticket in monday remains there. Use `work-management` when tracking needs an update, without creating a parallel ticket. Use `t3-code` when dispatching work through T3; local reviewer sub-agents do not need their own T3 threads or Notion Tasks.

## Local review

For substantive code changes, use an independent local Astra reviewer sub-agent before handoff. Give it the request, applicable repository instructions, and the actual diff or PR branch, with access to relevant surrounding code. Its assignment is read-only: identify concrete defects, regressions, missed requirements, and consequential maintainability issues, with a location and explanation. Cosmetic preferences alone are not findings.

Evaluate its findings and fix relevant issues within scope. Recheck affected behavior after fixes; another review is useful when the fixes materially change the code. A review is not a requirement to create a PR, new tests, or a review report file. Tiny copy or formatting changes do not need a reviewer.

## Reviewable delivery

For CMS or visual-editor changes, verify the relevant editing experience as well as the rendered page, using an authorized development environment. A rendered example alone does not establish that the customer can edit it.

Give Sil a validated preview when the change has a reviewable UI, with what to inspect and any access or lifetime limitation. On Otis, localhost alone is not a cross-device review link. State relevant verification, unresolved issues, and whether the work is committed, pushed, or released; do not imply that one establishes another.

Close task-created research and validation tabs and stop temporary processes no longer needed. Keep requested review previews available and preserve pre-existing resources. Leave lasting work under `~/projects`, not in a temporary directory.
