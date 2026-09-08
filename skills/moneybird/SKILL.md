---
name: moneybird
description: Inspect, create, update, verify or link Moneybird contacts, quotes, invoices and recurring billing. Use commercial-scoping when the scope or price still needs a decision.
---

# Moneybird

Use this skill to operate Moneybird. `commercial-scoping` defines the offer and price; `customer-communication` guides new customer-facing wording; `work-management` handles related Notion work.

Read [operations.md](references/operations.md) for tool calls, IDs, field conventions and verification. For document layout, read [documents.md](references/documents.md).

Identify the administration, contact, document type, scope, period, currency, VAT and agreed amounts relevant to the request. Inspect existing contacts and related documents before creating a duplicate. Preserve agreed rates, fixed lines, IDs and titles unless the request covers changing them.

Create or edit the requested concept using confirmed values. If a commercial decision is missing, use `commercial-scoping` to develop the proposal; do not guess billing facts. After a write, read the document back using the checks in operations.md and return its direct app URL.

Sending or publishing, destructive history cleanup, rejected or canceled status changes, and removing unclear lines require authorization covering that action and document. Existing authorization remains valid; do not ask again. A request for a concept does not authorize sending it.
