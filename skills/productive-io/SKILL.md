---
name: productive-io
description: Use only when the user explicitly asks to inspect, export, correct, create, change, or delete Productive.io time entries. Do not use Productive for routine planning, triage, delivery, or commercial scoping.
---

# Productive.io

## Ownership

This skill keeps on-demand access to Productive time entries. Productive does not participate in routine planning, triage, delivery, commercial scoping, or work-system maintenance. Hours are not inspected, reconstructed, or recorded by default.

Use it only when the current user request explicitly asks for Productive or time-entry work. A request to inspect work, plan a Sprint, deliver a project, prepare an invoice, or price a scope does not authorize a Productive read or write.

## References

- Read [references/api.md](references/api.md) for credentials, API calls, payloads, and error handling.
- Read [references/reconstruction.md](references/reconstruction.md) when filling, auditing, or repairing hours from contracts and work evidence, including Small Giants contract buckets.

## Workflow

1. Establish the requested person, customer/project, service, and date window.
2. Load credentials without printing secrets and inspect the existing entries for that scope.
3. Resolve live person, deal, service, and optional task IDs before a write. For retainers, verify that the parent deal covers the entry date.
4. For a direct read or export, return entries or totals in human units. Keep raw minutes for calculations.
5. For an explicitly requested reconstruction, apply `references/reconstruction.md`: contract-total-first, preserve existing entries, distribute only from evidence, and flag unresolved mismatches.
6. Before any write, show the proposed diff unless Sil explicitly asked to execute that exact Productive change. A read, export, audit, or general work request does not authorize writes.
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

Report the requested period, totals, changed entries, and unresolved issues.

The request is complete after the requested period is inspected, every write has exact live IDs and evidence, successful writes are read back, and the user has a confirmed result or concrete blocker.
