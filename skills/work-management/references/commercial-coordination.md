# Commercial Coordination

Use when a Moneybird action must connect to agency work in Notion.

Before calling Moneybird, establish:

1. The concrete executable action.
2. Current authorization for that action.
3. The owning Task, Project, or Company for writeback.

The coordination gate passes when all three are explicit. Otherwise return the exact missing boundary before calling Moneybird through this coordination branch.

Use `moneybird` for estimates, invoices, recurring billing, and financial-document operations.

After an action, write the durable result, evidence, source link or identifier, and resulting agency-work state to the owning Notion record.
