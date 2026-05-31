---
name: moneybird
description: Use Moneybird through the Moneybird MCP via mcporter, including shaping and validating estimates, invoices, recurring lines, and other Moneybird-facing commercial documents. Use when working in Moneybird or when the user mentions offers, estimates, invoices, recurring packages, pricing structure, option layout, or finance-document cleanup.
---

# Moneybird

Use this for both Moneybird ops and Moneybird-facing commercial docs.

## Quick start
- Endpoint: `https://moneybird.com/mcp/v1/read_write`
- Use `mcporter` with the URL directly.
- Inspect tool schema when unsure.
- Prefer exact IDs for contacts, projects, invoices, and documents.
- Do not guess write actions.
- After create/update, return direct Moneybird app URLs.

## Write rules
- For create/update writes, send one full JSON payload in `--args`.
- For estimates, use `{"estimate": {...}}`.
- Keep `details_attributes` as a JSON array.
- Avoid forms like `estimate.contact_id=...` or `estimate:=...`.
- Reuse previously working request shapes.
- If a write fails unexpectedly, suspect request shape first.

Example:
```bash
mcporter call https://moneybird.com/mcp/v1/read_write.create_estimate \
  --args '{"estimate":{"contact_id":"<contact_id>","details_attributes":[{"description":"...","amount":"5 uur","price":"90.0"}]}}' \
  --output json
```

## Document rules
- Keep docs short, direct, and commercially believable.
- Prefer a few strong lines over many weak fragments.
- Preserve agreed rates, IDs, titles, and fixed billing lines exactly.
- Do not silently normalize a customer-specific rate.
- Separate:
  - already billed / already covered work
  - one-off work
  - recurring service
  - shared infra/admin work
  - per-company work
- If one cost is shared across brands or companies, prefer a separate shared document.
- If a line looks underpriced, fix scope, hours, or rate. Do not hide it in vague copy.
- Real alternatives must be labeled `Optie 1`, `Optie 2`, etc.

## Structure and copy
- One-off lines above recurring lines.
- Monthly packages at the bottom.
- Default category labels:
  - `Eenmalige werkzaamheden`
  - `Doorlopende service`
- Default cleaned-up line style:
  - heading in bold: `**...**`
  - no blank line under the heading
  - optional short paragraph
  - optional `Kenmerken:` bullets
  - optional `Inbegrepen:` bullets
- Do not add decorative intro text above package headings.
- Keep Dutch copy crisp.
- Avoid filler, hedging, and generic AI phrasing.
- Use `Kenmerken:` for what the line is.
- Use `Inbegrepen:` for explicit included scope.
- If two lines are easy to confuse, sharpen the distinction in the first sentence.

## Moneybird conventions
- Prefer direct app URLs over public/external URLs.
- For proposals/estimates and invoices, add the Moneybird URL inline in the related Notion task body on the relevant context/decision bullet when available. Do not use a separate Notion `References` property.
- When an accepted estimate becomes delivery work, keep/update the same Notion task by default; do not create a separate delivery task unless one estimate creates multiple distinct work packages.
- Link templates:
  - Estimate: `https://moneybird.com/<administration_id>/estimates/<estimate_id>`
  - Sales invoice: `https://moneybird.com/<administration_id>/sales_invoices/<sales_invoice_id>`
  - Recurring sales invoice: `https://moneybird.com/<administration_id>/recurring_sales_invoices/<recurring_sales_invoice_id>`
  - Contact: `https://moneybird.com/<administration_id>/contacts/<contact_id>`
- For recurring invoice periods, use the last day of the month when monthly billing is intended.
- For monthly packages and amounts, use `per maand` as the quantity.
- For partial hours, use clock format:
  - `2:30 uur` not `2,5 uur`
  - `2:15 uur` not `2,25 uur`
  - `2:45 uur` not `2,75 uur`
- Update related products and estimates consistently when shared copy is intentional.
- When changing structure, verify detail ordering.
- Use fewer, stronger edits instead of many cosmetic edits.
- Optional vs mandatory should reflect real sales intent.

## Final check
- option lines clear
- recurring lines at bottom
- shared vs per-company costs split correctly
- headings consistent
- pricing believable
- already-billed work excluded
- related offers still aligned

## Push back / ask first
Push back when:
- work is obviously underpriced
- a shared cost is duplicated across offers
- options lack real tradeoffs
- wording hides a pricing or structure problem

Ask before:
- destructive cleanup of historical finance docs
- external sending/publishing
- creating/changing finance docs unless explicitly requested or required by a high-confidence accepted-proposal handoff
- removing lines when intent is unclear
