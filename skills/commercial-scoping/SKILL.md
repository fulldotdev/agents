---
name: commercial-scoping
description: "Build, review, price, and revise commercial customer scopes from historical estimates, invoices, actual hours, project records, designs, code state, meetings, and Slack decisions. Use for offertebedragen, fixed-price delivery scopes, scope-versus-actual calibration, v1/v2 decisions, price changes after calls, or customer and internal scope documents."
---

# Commercial Scoping

Produce a defensible customer price and a traceable internal calculation. Ground every conclusion in current delivery state and historical evidence.

## Workflow

1. Establish the requested outcome, customer, project, currency, pricing model, target version, and relevant time window.
2. Identify the latest customer-presented baseline before proposing changes. Record its URL, total, category prices, and presentation time when known.
3. Gather the evidence needed for the requested confidence level. For historical or multi-source work, read [evidence-sources.md](references/evidence-sources.md).
4. Inspect what already exists in tickets, code, preview, CMS, Figma, deployments, and recorded work. Remove completed work and reused foundations from the new estimate.
5. Decompose the remaining outcome into customer-recognizable categories and smaller internal subitems. Apply [commercial-rules.md](references/commercial-rules.md).
6. Estimate internal effort first. Compare analogous historical estimates with Productive actuals, invoices, and delivered state. Explain material deviations from those analogues.
7. Convert effort to price using the engagement's verified rate. For Skantrae through Small Giants, use €100/hour when that remains the agreed rate; verify other engagements instead of carrying this rate across customers.
8. Classify uncertainty as one of:
   - known and included;
   - open point with bounded work;
   - provisional price pending a named dependency;
   - separate v2 or follow-up scope.
9. Produce two synchronized views when a document is requested:
   - customer scope with category prices and unpriced subitems;
   - internal calculation with subitem effort and prices.
10. Validate arithmetic, terminology, current-state deduplication, source links, and change history before presenting or writing.

## Pricing decisions

- Price deliverable outcomes. Include normal implementation, coordination, feedback processing, testing, and release inside each deliverable.
- Treat defects in already agreed or delivered behavior as corrective work without an added commercial line. Treat new or broadened behavior as v1, v2, or a separately priced option.
- Use historical actuals as calibration, not as an automatic multiplier. Adjust for reuse, code familiarity, supplied designs, data readiness, environments, and integration uncertainty.
- Keep a risk allowance inside the affected deliverable instead of selling generic feedback or contingency rounds.
- Make integration and cloud assumptions explicit when they can change the implementation path.
- Prefer one category price over separately priced technical actions. Price a subitem separately only when it is independently optional or independently deliverable.

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

Apply these rules:

- Label an agent risk adjustment as a proposal until the user explicitly approves it.
- Do not attribute an internally proposed change to a meeting or customer source.
- When the user asks what changed after a call, compare timestamps against the exact version presented in that call.
- Preserve earlier presented values even after later revisions so the commercial sequence can be reconstructed.
- Reconcile the ledger, customer document, and internal calculation after every approved price change.

## Output

Lead with the recommended total and whether it is sharp, realistic, or conservative. Then provide:

1. category prices;
2. included subitems;
3. material open points;
4. v1/v2 classification when relevant;
5. comparison with historical estimates and actuals;
6. the exact changes from the last presented version.

Use euros in customer-facing scopes unless the user requests hours. Keep internal hours available for calculation and audit. End the customer document at the total table unless the user explicitly requests notes below it.
