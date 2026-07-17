# Hours reconstruction

Use this branch to fill, audit, or repair hours after work occurred. Productive is the registration endpoint, not the source of truth.

## Evidence order

1. Contracts, agreements, retainers, and invoices define customer, date range, total hours, and exclusions.
2. Existing Productive entries define what is already registered and under which live IDs.
3. Calendar shows meetings, setup, customer contact, and realistic start dates.
4. Notion Tasks, Projects, Sprints, comments, and status history show likely work and buckets.
5. GitHub commits, pull requests, and merges show approximate engineering activity.
6. Chat or memory may clarify intent but never overrides live commercial or Productive evidence.

Collect only lanes needed for the target scope. If a lane fails, continue with the others, identify the gap, and withhold writes that depend on it.

## Reconstruction rules

1. Match the contract or invoice total for its exact period unless an explicit exclusion applies.
2. Preserve existing entries and fill gaps before changing them.
3. Treat reconstructed dates and task durations as estimates; use calendar and delivery evidence to distribute them plausibly.
4. Prefer rounded durations such as 30, 45, 60, 90, 120, or 180 minutes unless stronger evidence or existing patterns support another value.
5. Match the parent deal and entry date before using a service. A service label or time-entry note is not enough.
6. Keep weekly totals plausible, but prioritize the agreed period total when the two conflict.
7. Do not delete entries unless Sil explicitly asks.
8. Block the write on overlaps, missing identity/service IDs, unclear scope, or contract/invoice mismatch rather than fabricating certainty.

## Small Giants contract buckets

Use these baselines only when the live contract or invoice for the relevant period supports them:

- Teveo development: 8 hours per week.
- Teveo customer lead: 1 hour per week.
- Teveo automated testing: 4 hours per week over 12 weeks when extended; normally at least 2 hours in active weeks and about 4 hours/week on average across the run.
- Skantrae development retainer: 16 hours per week for 8 SOW weeks.

Name project-management/customer-service time `customer lead` in summaries.

### Teveo automated testing

Keep automated testing separate from regular Teveo development and CRO. It covers BrowserStack/Percy run review, failure investigation, test maintenance, new test coverage, and regression work tied to the automated suite.

Require a parent deal whose name contains `Automated Testing Retainer` and whose dates cover the entry. Reject `AB testing` services and services under `Teveo - CRO & Development 2026`. A `Development` service is valid only under the automated-testing deal.

For July 2026, the known mapping is deal `#2494`, service `15255108`. Treat this as a dated hint and verify it live. Resolve later periods from the matching dated deal.

Do not allocate normal features, theme work, CRO, wishlist changes, translations, Klaviyo/VWO work, or generic releases to this bucket unless the note clearly identifies the test impact.

## Output

For planning, report project totals first, then useful service splits, followed by the overall total and exact Monday-Sunday period. For write preparation, list every proposed entry with date, minutes, person ID, service ID, optional task ID, and note.
