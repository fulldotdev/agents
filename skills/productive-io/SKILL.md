---
name: productive-io
description: Inspect, export, reconstruct, create, update, or delete Productive.io time entries through the Productive API. Use for Productive hours, time registration, timesheets, missing-hours reconciliation, retainer allocation, or audits; use the weekly-planning branch when work-management invokes Productive reconciliation.
---

# Productive.io

## Ownership

This skill owns Productive time-entry evidence, reconstruction, request shape, write safety, and reporting. It does not own project planning, invoicing, or recurring workflow scheduling.

When invoked by `work-management`, the weekly planning loop owns scope, timing, Notion context, and follow-up. Record completion or a blocker on the owning Sprint/admin context. Do not create a separate recurring Productive reconciliation Task.

## References

- Read [references/api.md](references/api.md) for credentials, API calls, payloads, and error handling.
- Read [references/reconstruction.md](references/reconstruction.md) when filling, auditing, or repairing hours from contracts and work evidence, including Small Giants contract buckets.

## Workflow

1. Establish the requested person, customer/project, service, and date window.
2. Load credentials without printing secrets and inspect the existing entries for that scope.
3. Resolve live person, deal, service, and optional task IDs before a write. For retainers, verify that the parent deal covers the entry date.
4. For a direct read/export, return the requested entries or totals in human units while retaining raw minutes for calculations.
5. For reconstruction, apply `references/reconstruction.md`: contract-total-first, preserve existing entries, distribute only from evidence, and flag unresolved mismatches.
6. Before manual retroactive writes, show the concrete proposed diff unless Sil explicitly asked to execute it. A routine weekly planning run may write directly when its evidence and IDs meet the reconstruction criteria.
7. Verify created or updated entries by reading them back. Never delete entries without Sil's explicit request.

## Write requirements

A proposed entry must include:

- date
- minutes
- person ID
- service ID
- optional task ID
- a short note when it helps identify the work

Do not infer a service from its label or an existing note alone. Match the parent deal and entry date first. Prefer filling gaps over changing existing entries, and avoid fake precision in reconstructed durations.

Stop on missing identity, unclear service/deal ownership, contradictory contract totals, or insufficient evidence. Report the exact missing fact to the calling workflow.

## Output and completion

For direct operations, report the affected period, totals, entries changed, and any unresolved issue. For weekly planning, use a compact project-first summary and mention a caveat only when it changes billing or interpretation.

The task is complete when the requested period has been inspected, every intended write has exact live IDs and evidence, successful writes have been read back, and the planning owner has either a confirmed result or a concrete blocker.
