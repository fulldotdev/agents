# Commercial Rules

## Vocabulary

- **layout**: a complete page or route composition.
- **block**: a pagebuilder or full-width content section.
- **component**: a smaller reusable interface or functional element.

Use these terms consistently in scopes and calculations.

## Decomposition

- Group customer-facing work into categories with one category price.
- List smaller deliverables beneath the category without individual customer-facing prices.
- Keep the detailed subitem prices and effort in the internal calculation.
- Keep an independently optional outcome as its own category.
- Describe what is delivered, not internal ceremonies or feedback rounds.

## Current state

- Separate already completed work, reusable foundations, remaining work, and genuinely new work.
- Recheck code and source records before adding an item that sounds similar to prior work.
- Account for reuse explicitly when lowering a price.
- Scope only the delta when an existing layout, block, component, lister, query, or integration can be adapted.

## Bugs, improvements, and versions

- **Bug/correction**: agreed behavior exists but does not work as intended. Restore it within the existing delivery without a new price line.
- **Small completion**: needed to finish an explicitly sold outcome. Include it in the affected category or add a bounded completion category.
- **Improvement**: behavior works, but the requested experience is better or broader. Price it or assign it to v2.
- **New feature**: new business behavior, data, role, filter, integration, or workflow. Scope separately unless explicitly approved for v1.

When one request has a small and large variant, name both. Include the bounded small variant and move the broader architectural version to v2 when that protects the agreed budget.

## Uncertainty wording

Use `❓ Open punt` for a genuine unresolved dependency. Phrase it as a question or confirmation still needed, not as a hidden exclusion or certainty.

Examples:

- confirm whether a usable endpoint and required fields already exist;
- confirm whether an integration is a simple embed or needs authentication and data exchange;
- confirm whether test, preview, production, and cloud environments already exist.

If either answer changes the price materially, show a provisional price, alternative, or separate follow-up scope.

## Change control

Maintain a price-change ledger during every revision:

| Field | Required value |
|---|---|
| Changed at | Exact timestamp and timezone when available |
| Baseline | Version or document presented before the change |
| Category | Customer-facing category |
| Previous | Previous price and internal effort |
| Proposed | Proposed price and internal effort |
| Source | Meeting, Slack, ticket, historical evidence, user decision, or agent recommendation |
| Status | Proposed, user-approved, customer-presented, superseded, or removed |
| Reason | One concrete sentence |

- Label an agent risk adjustment as a proposal until the user explicitly approves it.
- Do not attribute an internally proposed change to a meeting or customer source.
- When the user asks what changed after a call, compare timestamps against the exact version presented in that call.
- Preserve earlier presented values after later revisions so the commercial sequence can be reconstructed.
- Reconcile the ledger, customer document, and internal calculation after every approved price change.

## Documents

Customer version:

- euros and category prices;
- unpriced subitems;
- concise open points;
- no separate feedback, testing, or release lines;
- no detailed internal effort unless requested.

Internal version:

- hours and price per subitem;
- rate used;
- historical analogue and actuals;
- risk and assumptions;
- price-change ledger;
- same category totals as the customer version.

Verify every category sum and grand total. After an update, read both documents back and compare totals and category names.
