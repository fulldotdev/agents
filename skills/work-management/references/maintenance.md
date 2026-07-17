# Monthly Maintenance

Use for the monthly health review of the work system. This workflow reviews state; age or inactivity alone never changes a status.

## Review

1. Inspect Todo without a current or future Sprint. Keep executable work as Todo, commit it to a Sprint, move a non-executable idea to Someday, or cancel it when evidence supports that decision.
2. Inspect older Doing and Waiting Tasks. Keep Doing when execution has started and remains unfinished. Keep Waiting when a concrete dependency still prevents execution. Correct status only from current evidence.
3. Inspect Someday for ideas that became executable, irrelevant, duplicated, or owned by an active Task or Project.
4. Inspect Discovery, Planned, In Progress, and Paused Projects for a current outcome, delivery commitment, and executable Task. Preserve Discovery for active sales work.
5. Inspect repeated routing friction, stale skill or automation instructions, recurring access/schema failures, and obsolete generated clutter. Create a Todo only for concrete improvement work.

Use `scripts/collect.py planning --after <start> --before <end> --format yaml` for compact Notion and calendar context. Load Productive, Moneybird, monday.com, or Trackler only when a concrete review decision depends on that source.

## Completion

Maintenance is complete when every reviewed item is deliberately kept, committed, moved, canceled, corrected, or recorded with the exact unresolved decision; every write retains its source and evidence.

Return one concise numbered list using `Todo:`, `Someday:`, `Project:`, `Status:`, `Skill:`, `Automation:`, `Cleaned:`, `Decision:`, `Blocked:`, or `Failed:`.
