# Delivery

Use for customer-facing previews, fixes, releases, site/webshop changes, production publishing, review handoffs, and final customer updates.

## Core rule

Default to preview and approval before production. Publish immediately only when Sil explicitly requests it or has clearly authorized that exact low-risk production pattern.

## Workflow

1. Read the relevant Task, Project, Customer, acceptance criteria, approvals, and source context.
2. Make the scoped change using the relevant project/domain skills.
3. Verify locally with appropriate build, typecheck, lint, tests, dev server, browser, responsive, console, form, link, and task-specific checks. Use `shared-dev-server` for local servers.
4. Use an independent review for non-trivial changes when it materially improves confidence. Tests, CI, and browser QA remain authoritative.
5. Deploy to preview/staging when applicable and verify the live preview in a browser.
6. Draft a concise update with the preview URL, what changed, and what the reviewer should check. Use `customer-communication`.
7. Set the Task to Waiting when approval is needed. Do not publish production before approval.
8. After approval, publish through the project's normal process and verify the production deployment and changed flow.
9. Send or draft the final update according to authorization. Mark Done only when completion and required production verification are clear.
10. Update Notion with compact result, verification, state, next action, and useful links.

## Customer update shape

```md
[Title] staat klaar ✅

Preview: [link]

Aangepast:
- ...

Let vooral op:
- ...
```

Include only sections that add value. Do not expose internal build, branch, schema, or implementation language unless the customer asked for technical detail.

## Guardrails

- Draft external customer messages unless explicitly asked to send.
- Never claim a preview or production result without verifying the URL.
- Do not mark customer-facing work Done merely because implementation is local.
- Do not merge, deploy, or publish production solely because checks pass; approval remains a separate gate.
- Keep delivery evidence concise and customer-visible.

## Report

Return a concise report covering result, verification, preview, approval, production, blockers, customer message, and Notion state. Omit empty sections.
