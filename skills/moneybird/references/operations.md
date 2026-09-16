# Moneybird operations

## MCP usage

- Endpoint: `https://moneybird.com/mcp/v1/read_write`, called through `mcporter` with the URL.
- Check the current tool schema when you are unsure about an operation or payload shape.
- Resolve the exact administration, contact, project, invoice, estimate, and recurring-document IDs before a write.

Pass one complete JSON object to create and update calls through `--args`. Use the envelope the tool expects, such as `{"estimate": {...}}`, and keep `details_attributes` as an array. Do not flatten keys into forms like `estimate.contact_id=...`. If a write fails unexpectedly, compare your envelope and fields with the schema or a known working call before you change business data.

## Checks after a write

Fetch the live record and check:

1. administration and contact;
2. document type and status;
3. period, currency, VAT, and due or recurrence settings;
4. quantities, units, rates, discounts, and totals;
5. line order, descriptions, and optional lines.

Return the internal app URL, not a public one:

- Estimate: `https://moneybird.com/<administration_id>/estimates/<estimate_id>`
- Sales invoice: `https://moneybird.com/<administration_id>/sales_invoices/<sales_invoice_id>`
- Recurring invoice: `https://moneybird.com/<administration_id>/recurring_sales_invoices/<recurring_sales_invoice_id>`
- Contact: `https://moneybird.com/<administration_id>/contacts/<contact_id>`

## Field conventions

- For monthly billing, set the recurring period to the last day of the month.
- Use `per maand` as the quantity for monthly packages and amounts.
- For fixed-price work calculated from hours, keep hours and rate internal. Set quantity to `1` and price to the line total.
- Use hour quantities only for time-based billing or when the user asks. Write partial hours as clock time, such as `2:30 uur`.
- Put dates in the period field. Put scope, corrections, and calculation basis in the description.
- Update a product and an estimate together only when they share copy on purpose, then check both.
