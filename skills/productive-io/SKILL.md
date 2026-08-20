---
name: productive-io
description: Use when Productive.io time entries or hours must be inspected, exported, reconstructed, created, changed, deleted, or reconciled for timesheets, missing hours, retainers, audits, or weekly planning.
---

# Productive.io

## Ownership

This skill owns Productive time-entry evidence, reconstruction, request shape, write safety, and reporting. It does not own project planning, invoicing, or workflow scheduling.

When `work-management` calls this skill, the weekly planning loop owns scope, timing, Notion context, and follow-up. Record the result or blocker on the owning Sprint or admin context. Do not create a recurring Productive reconciliation Task.

## References

- Read [references/api.md](references/api.md) for credentials, API calls, payloads, and error handling.
- Read [references/reconstruction.md](references/reconstruction.md) when filling, auditing, or repairing hours from contracts and work evidence, including Small Giants contract buckets.

## Workflow

1. Establish the requested person, customer/project, service, and date window.
2. Load credentials without printing secrets and inspect the existing entries for that scope.
3. Resolve live person, deal, service, and optional task IDs before a write. For retainers, verify that the parent deal covers the entry date.
4. For a direct read or export, return entries or totals in human units. Keep raw minutes for calculations.
5. For reconstruction, apply `references/reconstruction.md`: contract-total-first, preserve existing entries, distribute only from evidence, and flag unresolved mismatches.
6. Before a manual retroactive write, show the proposed diff unless Sil asked to execute it. A routine weekly planning run may write directly when its evidence and IDs meet the reconstruction rules.
7. Verify created or updated entries by reading them back. Never delete entries without Sil's explicit request.

## Write requirements

A proposed entry must include:

- date
- minutes
- person ID
- service ID
- optional task ID
- a short note when it helps identify the work

Do not infer a service from its label or an existing note alone. Match the parent deal and entry date first. Fill gaps before changing existing entries. Do not invent precision in reconstructed durations.

Stop when identity is missing, service or deal ownership is unclear, contract totals conflict, or evidence is insufficient. Report the exact missing fact.

## Output and completion

For direct operations, report the period, totals, changed entries, and unresolved issues. For weekly planning, summarize by project. Mention a caveat only when it changes billing or interpretation.

The task is complete after the requested period is inspected, every write has exact live IDs and evidence, successful writes are read back, and the planning owner has a confirmed result or concrete blocker.
