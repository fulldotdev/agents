---
name: moneybird
description: Use when inspecting, creating, updating, verifying, or linking Moneybird contacts, quotes, invoices, and recurring billing.
---

# Moneybird

This skill operates Moneybird. `commercial-scoping` decides the offer and price. `customer-communication` writes new customer-facing text. `work-management` handles related Notion work.

Read [operations.md](references/operations.md) for tool calls, IDs, field conventions, and checks. Read [documents.md](references/documents.md) for document layout.

Find the administration, contact, document type, scope, period, currency, VAT, and agreed amounts. Check existing contacts and related documents before you create anything. Keep agreed rates, fixed lines, IDs, and titles as they are unless the request changes them.

Create or edit the draft with confirmed values. If a price or scope decision is missing, use `commercial-scoping` instead of guessing. After a write, check the document with the list in `operations.md` and return its app URL.

Ask the user before you send a document, change its status, delete history, or remove a line you do not understand.
