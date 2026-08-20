---
name: moneybird
description: Use when a Moneybird estimate, invoice, recurring billing record, contact, VAT setup, or commercial line must be inspected, drafted, changed, validated, or linked. Use commercial-scoping to decide scope or price.
---

# Moneybird

## Ownership

This skill owns Moneybird evidence, request shape, document quality, write safety, verification, and direct links. It does not own weekly scheduling or delivery planning.

When `work-management` calls this skill, it owns the Notion record, timing, routing, and follow-up. This skill may inspect live state, link a match, or prepare a concept when the evidence is clear.

## References

- Read [references/operations.md](references/operations.md) for MCP calls, payloads, IDs, URLs, and Moneybird field conventions.
- Read [references/documents.md](references/documents.md) when drafting or revising offer/invoice structure, pricing lines, options, or recurring packages.

## Workflow

1. Identify the administration, contact, document type, owning project/scope, period, currency, VAT, rates, and whether the action is read-only, draft, update, or send.
2. Inspect live contacts and related documents before creating anything. Link a match instead of creating a duplicate.
3. Use prior customer/project documents only as evidence; preserve explicitly agreed rates, fixed lines, IDs, and titles.
4. For a draft or edit, apply `references/documents.md`. State material uncertainty plainly.
5. Use exact live IDs and the complete request envelope from `references/operations.md` for a write.
6. After a write, read the document back. Verify its contact, type, period, VAT, amounts, line order, optionality, and total.
7. Return the direct Moneybird app URL and the remaining approval or follow-up action.

## Approval boundary

Ask before sending or publishing, destructive history cleanup, rejected or canceled status changes, or removing unclear lines. Create a concept during an approved workflow only when the customer, contact, scope, price or rate, VAT, period, and evidence are clear. Otherwise return the proposed structure and exact missing decision.

Push back when work is clearly underpriced, a shared cost is duplicated, alternatives lack a real tradeoff, or wording conceals a scope or pricing problem.

## Work-management handoff

Under `work-management`, add Moneybird facts to the relevant Task as a source-specific Timeline event. Use the direct Moneybird URL as its source. Do not add a `References` property or unsupported commercial context. A sent estimate for real scope belongs to a Project-linked sales or follow-up Task.

When an estimate is accepted, finish the sales Task and create or link its Delivery Tasks. Keep the original Task only if it already was the delivery work package.

## Completion

The operation is complete after the live document is inspected, duplicates are ruled out, changed fields and totals are read back, and the direct app URL is returned. External sending must be approved and verified or named as the next step.
