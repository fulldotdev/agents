---
name: moneybird
description: Inspect, draft, create, update, validate, or link Moneybird estimates, invoices, recurring billing, contacts, and commercial line structures through the Moneybird MCP. Use for offers, invoices, pricing, VAT/scope checks, recurring packages, finance-document cleanup, or work-management commercial reconciliation.
---

# Moneybird

## Ownership

This skill owns Moneybird evidence, request shape, commercial-document quality, write safety, verification, and direct document links. It does not own weekly scheduling or delivery planning.

When invoked by `work-management`, the parent workflow owns the Notion Task/Project, timing, routing, and follow-up. This skill may inspect live state, link an existing match, or prepare a concept when the evidence is clear.

## References

- Read [references/operations.md](references/operations.md) for MCP calls, payloads, IDs, URLs, and Moneybird field conventions.
- Read [references/documents.md](references/documents.md) when drafting or revising offer/invoice structure, pricing lines, options, or recurring packages.

## Workflow

1. Identify the administration, contact, document type, owning project/scope, period, currency, VAT, rates, and whether the action is read-only, draft, update, or send.
2. Inspect live contacts and related documents before creating anything. Prefer linking a matching document over creating a duplicate.
3. Use prior customer/project documents only as evidence; preserve explicitly agreed rates, fixed lines, IDs, and titles.
4. For a draft or edit, apply the commercial quality rules in `references/documents.md` and show any material uncertainty instead of hiding it in wording.
5. Use exact live IDs and the complete request envelope from `references/operations.md` for a write.
6. Read the document back after creation or update and verify contact, type, period, VAT, amounts, line order, optionality, and total.
7. Return the direct Moneybird app URL and the remaining approval or follow-up action.

## Approval boundary

Ask before external sending/publishing, destructive historical cleanup, rejected/canceled status changes, or removing ambiguous lines. A concept document may be created during an approved workflow only when customer, contact, scope, price/rate, VAT, period, and evidence are unambiguous; otherwise return the proposed structure and exact missing decision.

Push back when work is clearly underpriced, a shared cost is duplicated, alternatives lack a real tradeoff, or wording conceals a scope or pricing problem.

## Work-management handoff

Add the direct Moneybird URL inline to the relevant Notion Task context rather than a separate `References` property. A sent estimate for real commercial scope belongs to a Project-linked sales/follow-up Task.

When an estimate is accepted, finish the sales Task and create or link the concrete Delivery Task(s) under that Project. Keep the original Task only if it was already the delivery work package.

## Completion

The operation is complete when the live document was inspected, duplicates were ruled out, every changed field and total was read back, the direct app URL was returned, and external sending is either explicitly approved and verified or clearly left as the next approval step.
