# Evidence sources

Use the smallest reliable source set. For a full historical comparison, inspect every relevant source below and keep its link or ID.

## Source routing

1. **Notion and meetings**
   - Read the current scope, requirements, decisions, and meeting summaries. Read transcripts when they could change the price or version.
   - Capture the version actually presented to the customer and the time of the presentation.
   - Use the `notion-cli` and `work-management` skills.

2. **monday.com**
   - Read relevant boards, tickets, updates, and comments with `monday-com`.
   - Use the original `Hours` or `Expected hours` scoping field.
   - Exclude `Hours full ticket` from pricing comparisons.
   - Extract agreed deliverables instead of turning each ticket step into a customer line.

3. **Moneybird**
   - Inspect relevant estimates, invoices, lines, and groupings with `moneybird`.
   - Distinguish quoted, invoiced, credited, and paid amounts.
   - Use invoice lines as evidence of what was sold, not proof that every line consumed the same effort.

4. **Slack**
   - Search the relevant workspace, DMs, channels, and full threads with `slack`.
   - Include standalone Small Giants scopes that were never added to monday.com.
   - Preserve sender, timestamp, and permalink for price or scope decisions.

5. **Figma**
   - Locate the supplied design and relevant nodes with `figma`.
   - Determine whether the design is complete, partial, absent, or only a visual reference.
   - Write `incl. design` for customers only when requested. Account for missing design work internally.

6. **Code, CMS, and preview**
   - Inspect the current implementation when reuse or remaining work can change the price.
   - Confirm what already exists, account for reuse in the estimate, and state where it lowers effort.

## Evidence matrix

For a complex pricing comparison, an internal table can help:

| Deliverable | Historical scope | Verified delivered state | Current reusable state | New effort | Uncertainty | Sources |
|---|---|---|---|---:|---|---|

When sources disagree, prefer them in this order:

1. current verified implementation and current written agreement;
2. explicit recent customer or stakeholder decision;
3. matched invoices and verified delivered work;
4. older estimates and analogous work;
5. unsupported assumption.

Distinguish conclusions drawn from evidence from confirmed facts, and label assumptions. Ask for a decision only when the unknown could change the price or delivery.
