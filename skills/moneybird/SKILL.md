---
name: moneybird
description: Use when inspecting, creating, updating, verifying, or linking Moneybird contacts, quotes, invoices, and recurring billing.
---

# Moneybird

This skill operates Moneybird. `commercial-scoping` decides the offer and price. `customer-communication` writes new customer-facing text. `work-management` handles related Notion work.

Read [operations.md](references/operations.md) for tool calls, IDs, field conventions, and checks.

Find the administration, contact, document type, scope, period, currency, VAT, and agreed amounts. Check existing contacts and related documents before you create anything. Keep agreed rates, fixed lines, IDs, and titles as they are unless the request changes them.

Create or edit the draft with confirmed values. If a price or scope decision is missing, use `commercial-scoping` instead of guessing. After a write, check the document with the list in `operations.md` and return its app URL.

Ask the user before you send a document, change its status, delete history, or remove a line you do not understand.

## Document layout

Keep the introduction short and put the scope in the lines. A line has a bold heading and one short paragraph. Name the quote or agreement and its date in the reference. Fixed-price lines have quantity `1`:

```text
Reference: VDA pakket incl. opties en brochurepagina's | akkoord 08-09-2026
1 × € 1.600
**VDA websiteverbeteringen, vertalingen en brochurepagina's**
Vast pakket volgens offerte 2026-09-0037 en de WhatsApp-afspraken van 8 september 2026. Inclusief …
```

- One-off work first, monthly packages last, under `Eenmalige werkzaamheden` and `Doorlopende service` when they fit. Agreed service is never optional.
- Work billed in parts: quantity `1 termijn`, and `Termijn 2/2 conform de bijgevoegde Statement of Work.` as the text.
- Several workstreams on one invoice: one line each, named by customer or workstream.
- Do not repeat prices in headings or scope in the introduction. Keep fixed billing descriptions unchanged.
