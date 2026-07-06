---
name: client-delivery
description: "Use when delivering customer-facing work, previews, fixes, releases, site updates, webshop/site changes, or review-ready changes. Guides execution, local dev server/browser checks, preview QA, approval before production, production QA, customer updates, and Notion follow-up."
---

# Client Delivery

Use when delivering customer-facing work, previews, fixes, releases, site updates, webshop/site changes, or review-ready changes.

## Core rule

Waiting for customer/Sil approval before publishing to production is the default.

Only skip approval and publish immediately when Sil explicitly says to publish/go live without waiting, or when the task is clearly a safe non-customer-impacting production fix and Sil has authorized that pattern.

## Flow

1. Understand task/context
   - Read Notion Task/Project/Customer context when available.
   - Identify what must be delivered and what the customer/Sil should check.
   - Keep scope tight.

2. Execute
   - Make the requested change/work.
   - Preserve relevant context and evidence.

3. Local check
   - Run relevant build/check/test/lint commands.
   - Start or reuse the dev server when useful.
   - Open the local site/app in the browser, not just terminal output.
   - Verify the main changed flow locally.
   - Check desktop/mobile when relevant.
   - Check browser console errors when relevant.
   - Check links, buttons, forms, and task-specific acceptance points.

3b. Independent review gate when useful
   - For non-trivial code changes, use an independent fresh-context review before preview/customer handoff.
   - Prefer the `requesting-code-review` skill for the full subagent/static-scan/test workflow.
   - Treat AI review as advisory; CI/build/tests/browser QA remain the blocking source of truth.
   - CodeRabbit can be used as a persistent GitHub PR reviewer, but does not replace local/preview QA.

4. Preview deploy
   - Deploy to preview/staging when applicable.
   - Verify the preview URL is live.

5. Preview QA
   - Check the actual preview in the browser, not only local.
   - Check desktop/mobile when relevant.
   - Check console errors, links, buttons, forms, and task-specific acceptance points.
   - Fix issues and repeat local + preview checks when needed.

6. Customer update draft
   - Draft a short customer/Sil update with preview link and what to check.
   - Use the template below as a loose shape, not fixed wording.

7. Wait for approval
   - Default status after preview delivery is Waiting when approval/check is needed.
   - Do not publish production until approval unless explicitly instructed.

8. After approval: publish
   - Publish/merge/deploy to production using the project’s normal process.
   - Verify the production deploy completed.

9. Production QA
   - Run the relevant test/check flow again on production.
   - Open production in the browser.
   - Recheck the changed flow, important pages, forms/buttons/links, mobile/desktop, and console errors as relevant.
   - Confirm production matches the approved preview.

10. Final customer update + Notion update
   - Draft/send final message when appropriate.
   - Suggest or perform Notion status update according to scope:
     - Waiting when customer/Sil still needs to check.
     - Done only when approved, published, verified, or safely completed.
   - Add compact evidence/context, not a long report.

## Customer update template

```md
[Titel] staat klaar ✅

Preview: [link]

Aangepast:
- ...
- ...

Let vooral op:
- ...
- ...

Laat me weten wat je ervan vindt!
```

Parts are optional. Only include sections that add value.

- `Preview` only when there is a preview/link.
- `Aangepast` only when it is useful to summarize changes.
- `Let vooral op` only when the customer/Sil should check specific points.
- Exact wording may be adapted to the situation, channel, customer, and tone.

Possible variants:

- `Preview staat klaar ✅`
- `Is gefixt ✅`
- `Check vooral ff ...`
- `Als dit zo klopt, zet ik 'm live.`
- `Laat maar weten of dit zo akkoord is.`
- `Deze staat live ✅`

## Default output

Return a concise delivery report:

1. Result: ready for review / blocked / published / done.
2. Local checks: commands, dev server/browser checks, notable result.
3. Preview: link and QA result, if applicable.
4. Approval: waiting / received / explicitly skipped.
5. Production: publish result and production QA, if applicable.
6. Issues/blockers: only concrete issues.
7. Customer message draft.
8. Suggested Notion update.

## Constraints

- Do not mark customer-facing delivery Done unless explicit, approved, or production has been verified when production was part of scope.
- Do not publish production by default. Wait for approval after preview.
- Do not send external customer messages unless explicitly asked; draft by default.
- Use browser/dev server verification when it materially improves confidence.
- Keep communication short, direct, and practical.
