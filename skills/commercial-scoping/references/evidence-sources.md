# Evidence Sources

Use the smallest source set that can answer the request reliably. For a full historical calibration, inspect every relevant source below and retain reopenable links or IDs.

## Source routing

1. **Notion and meetings**
   - Read the current scope, requirements, decisions, meeting summaries, and transcripts when the transcript can change a price or version decision.
   - Capture the version actually presented to the customer and the time of the presentation.
   - Use the `notion` and `work-management` skills.

2. **monday.com**
   - Read relevant boards, tickets, updates, and comments with `monday-com`.
   - Use the original `Hours` or `Expected hours` scoping field.
   - Exclude `Hours full ticket` from commercial calibration.
   - Extract scoped deliverables rather than copying full ticket lifecycle work as separate customer lines.

3. **Moneybird**
   - Inspect relevant estimates, invoices, line items, and commercial groupings with `moneybird`.
   - Distinguish quoted, invoiced, credited, and paid amounts.
   - Use invoice lines as evidence of what was sold, not proof that every line consumed the same effort.

4. **Slack**
   - Search the relevant workspace, DMs, channels, and full threads with `slack`.
   - Include standalone Small Giants scopes that never reached monday.com.
   - Preserve sender, timestamp, and permalink for price or scope decisions.

5. **Figma**
   - Locate the supplied design and relevant nodes with `figma`.
   - Determine whether the design is complete, partial, absent, or only a visual reference.
   - Do not expose `incl. design` in customer wording unless requested, but account for missing design work internally.

6. **Code, CMS, and preview**
   - Inspect current implementation state before pricing.
   - Confirm which layouts, blocks, components, queries, routes, schemas, integrations, and environments already exist.
   - Reuse existing foundations in the estimate and state where reuse lowers effort.

## Evidence matrix

Build an internal matrix for each proposed deliverable:

| Deliverable | Historical scope | Verified delivered state | Current reusable state | New effort | Uncertainty | Sources |
|---|---|---|---|---:|---|---|

Prefer evidence in this order when sources disagree:

1. current verified implementation and current written agreement;
2. explicit recent customer or stakeholder decision;
3. matched invoices and verified delivered work;
4. older estimates and analogous work;
5. unsupported inference.

State an inference as an inference. Ask for a decision only when the unknown materially changes price or delivery.
