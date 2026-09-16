---
name: moneybird
description: Use when inspecting, creating, updating, verifying, or linking Moneybird contacts, quotes, invoices, and recurring billing. Use commercial-scoping when the scope or price still needs a decision.
---

# Moneybird

Use this skill to operate Moneybird. `commercial-scoping` defines the offer and price; `customer-communication` guides new customer-facing wording; `work-management` handles related Notion work.

Read [operations.md](references/operations.md) for tool calls, IDs, field conventions and verification. For document layout, read [documents.md](references/documents.md).

Identify the administration, contact, document type, scope, period, currency, VAT, and agreed amounts. Check existing contacts and related documents before creating anything. Preserve agreed rates, fixed lines, IDs, and titles unless the request includes changing them.

Create or edit the requested draft with confirmed values. If a commercial decision is missing, use `commercial-scoping`; do not guess billing facts. After a write, read the document back using the checks in `operations.md` and return its direct app URL.

Sending or publishing, destructive history cleanup, rejected or canceled status changes, and removing unclear lines require authorization covering that action and document. Existing authorization remains valid; do not ask again. A request for a draft does not authorize sending it.
