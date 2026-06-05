---
name: work-execution
description: "Execute or prepare Notion Tasks with concise assignee instructions, evidence, and Sil review handoff."
---

# Work Execution

Use with `work-management`. Existing or newly triaged Tasks only. No broad inbox triage.

## Core Rule

Do only work that directly reduces execution/review friction. No filler steps, no generic structure, no invented work.

If a step could fit 100 random tasks, delete it.

## Scope

Use work-management for database roles, schema lookup, relations, status routing, and body trace rules.

This skill adds only:
- readiness to execute
- top-of-task assignee/review instructions
- evidence/work log
- AI/Sil handoff

## Body Rules

Always read current body before changing it. Never blind append.

Task body has two zones:
- Top = execution surface for current assignee/reviewer.
- Bottom/context = dated trace/evidence/source context.

When preparing/executing a Task, add or update the top execution section. Otherwise keep the work-management dated trace pattern.

```md
## Next steps
1. Concrete useful step.
2. Concrete useful step.

---
```

For Sil review after AI/background work:

```md
## Review
1. Check artifact/link.
2. Decide approve/change/reject.

---
```

Below the divider is context. Put work logs, evidence, original context, and source trace there.

```md
## Context
### YYYY-MM-DD - Source/update label
- Trace from work-triage/work-management/source context.

### AI work log
- What AI actually did.

### Evidence
- PR/diff/test/screenshot/output links or facts.

### Original context
- Preserve source context.
```

Do not put `AI work log` in the top section.

## Sil Review

Sil review artifacts: PR/diff, screenshot/screencapture, Notion doc/checklist, terminal/test output, browser QA log, or draft external message/offer that was not sent.

If AI/background work is ready for Sil, keep Doing and put `## Review` at the top with artifact/evidence and concrete review asks. No artifact = no review handoff.

## Instruction Bar

Each top-section step must contain at least one: direct link, concrete file/page/source, exact command, specific decision/check, output location, or acceptance criterion.

Bad: "Open the notes and make a checklist."
Good: "Draft checklist using sections: Agent discovery, machine-readable content, actions/API, auth/errors, URLs/performance."

## Safety

- Ask before destructive, irreversible, privacy-sensitive, external, money/account, or customer-impacting actions.
- For messages that need to be sent, create/place drafts only. Never send external messages unless explicit.
- Do not read private content unless needed and allowed. Prefer metadata/schema/evidence when enough.
- Preserve original language in source/customer context. Default new instructions/context to English.

## Reporting

Report only net changes: task URL, status change, artifact/evidence, or blocker if status update failed.
