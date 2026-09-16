# Hours reconstruction

Use this to fill, audit, or repair hours after the work happened. Productive stores the entries. The agreement and the work evidence decide what belongs there.

## Evidence order

1. Contracts, agreements, retainers, and invoices define the customer, period, total hours, and exclusions.
2. Existing Productive entries show what is registered and which live IDs were used.
3. Calendar events show meetings, setup, customer contact, and realistic start dates.
4. Notion Tasks, Projects, Sprints, comments, and status history show likely work and categories.
5. GitHub commits, pull requests, and merges show rough engineering activity.
6. Chat or memory can clarify intent but never overrides live commercial or Productive evidence.

Use only the sources the request needs. If one is unavailable, continue with the others, report the gap, and do not write entries that depend on it.

## Rules

1. Match the contract or invoice total for the exact period, unless an explicit exclusion applies.
2. Keep existing entries. Fill gaps before changing anything.
3. Reconstructed dates and durations are estimates. Place them plausibly with calendar and delivery evidence.
4. Prefer rounded durations (30, 45, 60, 90, 120, 180 minutes) unless stronger evidence or existing patterns say otherwise.
5. Check the parent deal and entry date before using a service. A label or a note is not enough.
6. Keep weekly totals plausible. If they conflict with the full-period total, the full period wins.
7. Do not delete entries unless the user asks.
8. Do not write when overlaps, missing IDs, unclear scope, or a contract mismatch remain.

## Small Giants contract buckets

Baselines, valid only when the live contract or invoice for the period supports them:

- Teveo development: 8 hours per week.
- Teveo customer lead: 1 hour per week.
- Teveo automated testing: 4 hours per week over 12 weeks when extended; normally at least 2 hours in active weeks and about 4 per week on average.
- Skantrae development retainer: 16 hours per week for 8 SOW weeks.

Call project-management and customer-service time `customer lead` in summaries.

### Teveo automated testing

Keep automated testing separate from regular Teveo development and CRO. It covers BrowserStack and Percy run review, failure investigation, test maintenance, new coverage, and regression work on the automated suite.

The parent deal name must contain `Automated Testing Retainer` and its dates must cover the entry. Do not use `AB testing` services or services under `Teveo - CRO & Development 2026`. A `Development` service is valid only under the automated-testing deal.

For July 2026 the mapping was deal `#2494`, service `15255108`. Treat that as a hint and check it live. Resolve later periods from the matching dated deal.

Do not put normal features, theme work, CRO, wishlist changes, translations, Klaviyo or VWO work, or generic releases in this bucket unless the note clearly names the test impact.

## Output

For planning, report project totals first, then useful service splits, then the overall total and the exact Monday to Sunday period. For write preparation, list every proposed entry with date, minutes, person ID, service ID, optional task ID, and note.
