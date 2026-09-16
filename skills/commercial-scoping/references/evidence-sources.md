# Evidence sources

Use the smallest set of sources that answers the question. For a full historical comparison, check every relevant source below and keep its link or ID.

## Sources

1. **Notion and meetings.** Read the current scope, requirements, decisions, and meeting summaries. Read transcripts when they could change the price or version. Note which version the customer saw and when. Use `notion-cli` and `work-management`.
2. **monday.com.** Read the boards, tickets, updates, and comments with `monday-com`. Use the original `Hours` or `Expected hours` field, not `Hours full ticket`. Extract agreed deliverables instead of turning each ticket step into a customer line.
3. **Moneybird.** Read estimates, invoices, lines, and groupings with `moneybird`. Keep quoted, invoiced, credited, and paid amounts apart. Invoice lines show what was sold, not how much effort each line took.
4. **Slack.** Search the workspace, DMs, channels, and full threads with `slack`. Include Small Giants scopes that never reached monday. Keep sender, timestamp, and permalink for price or scope decisions.
5. **Figma.** Find the supplied design with `figma`. Decide whether it is complete, partial, absent, or only a visual reference. Write `incl. design` for the customer only when asked. Account for missing design work internally.
6. **Code, CMS, and preview.** Look at the current implementation when reuse or remaining work can change the price. Confirm what exists, count reuse in the estimate, and say where it lowers effort.

## Weighing evidence

For a complex comparison, an internal table helps:

| Deliverable | Historical scope | Verified delivered state | Current reusable state | New effort | Uncertainty | Sources |
|---|---|---|---|---:|---|---|

When sources disagree, trust them in this order:

1. the current implementation and the current written agreement;
2. a recent explicit decision by the customer or stakeholder;
3. matched invoices and verified delivered work;
4. older estimates and similar work;
5. an assumption.

Keep facts, conclusions, and assumptions labeled as such. Ask for a decision only when the unknown could change the price or delivery.
