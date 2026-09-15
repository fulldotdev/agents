Process every synthetic triage case in the supplied batch. This is a read-only decision exercise. Do not call network services or make live changes.

Apply the supplied triage and work-management instructions exactly. Inspect source and destination evidence whenever it can change a decision. Return only JSON matching `output-schema.json`.

For each case, choose the current queue disposition, all required durable actions, the exact existing or proposed target, report behavior, and the source or destination locators that prove the decision. Use `proposed:TYPE:CASE_ID` for a target that does not exist yet. Do not invent receipts or claim a write was performed.

Treat case decisions independently, while respecting batch lane and report state. The benchmark time is 2026-09-15 12:00 Europe/Amsterdam.
