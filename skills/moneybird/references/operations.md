# Moneybird operations

## MCP usage

- Endpoint: `https://moneybird.com/mcp/v1/read_write`
- Use `mcporter` with the URL directly.
- Inspect the current tool schema when the operation or payload shape is uncertain.
- Resolve exact administration, contact, project, invoice, estimate, and recurring-document IDs before writes.

Create and update calls receive one complete JSON object through `--args`. Use the resource envelope expected by the tool, for example `{"estimate": {...}}`, and keep `details_attributes` as an array. Do not flatten keys into forms such as `estimate.contact_id=...`. If a write fails unexpectedly, compare its envelope and field shape with the current tool schema or a known working call before changing business data.

## Verification

After every create or update, fetch the live record and verify:

1. administration and contact;
2. document type and status;
3. period, currency, VAT, and due/recurrence settings;
4. quantities, units, rates, discounts, and totals;
5. line order, descriptions, and optional lines.

Return a direct app URL:

- Estimate: `https://moneybird.com/<administration_id>/estimates/<estimate_id>`
- Sales invoice: `https://moneybird.com/<administration_id>/sales_invoices/<sales_invoice_id>`
- Recurring invoice: `https://moneybird.com/<administration_id>/recurring_sales_invoices/<recurring_sales_invoice_id>`
- Contact: `https://moneybird.com/<administration_id>/contacts/<contact_id>`

Prefer these internal URLs over public/external variants.

## Field conventions

- For monthly recurring periods, use the last day of the month when monthly billing is intended.
- Use `per maand` as the quantity for monthly packages and amounts.
- Include the unit in all quantities, such as `37 uur`, `4 weken`, or `per maand`.
- Express partial hours in clock format: `2:30 uur`, `2:15 uur`, or `2:45 uur`.
- Use the period field for dates; use descriptions for scope, corrections, and calculation basis.
- Update related products and estimates together only when their copy is intentionally shared, then verify both live records.
