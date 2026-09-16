---
name: productive-io
description: Use when the user explicitly asks to inspect, export, correct, create, change, or delete Productive.io time entries. Do not use Productive for routine planning, triage, delivery, or commercial scoping.
---

# Productive.io

## References

- Read [references/api.md](references/api.md) for credentials, API calls, payloads, and error handling.
- Read [references/reconstruction.md](references/reconstruction.md) when filling, auditing, or repairing hours from contracts and work evidence, including Small Giants contract buckets.

## Workflow

1. Establish the requested person, customer/project, service, and date window.
2. Load credentials without printing secrets and inspect the existing entries for that scope.
3. Resolve live person, deal, service, and optional task IDs before a write. For retainers, verify that the parent deal covers the entry date.
4. For a direct read or export, return entries or totals in human units. Keep raw minutes for calculations.
5. For an explicitly requested reconstruction, follow `references/reconstruction.md`. Match the agreed total for the period, preserve existing entries, use evidence to place the remaining time, and flag any mismatch you cannot resolve.
6. Before a write, show the proposed diff unless Sil explicitly asked to execute that exact change.
7. Verify created or updated entries by reading them back. Never delete entries without Sil's explicit request.

## Write requirements

A proposed entry must include:

- date
- minutes
- person ID
- service ID
- optional task ID
- a short note when it helps identify the work

Do not choose a service from its label or an existing note alone. First confirm that its parent deal covers the entry date. Fill gaps before changing existing entries. Do not give reconstructed durations false precision.

Stop when identity is missing, service or deal ownership is unclear, contract totals conflict, or evidence is insufficient. Report the exact missing fact.

## Output

Report the requested period, totals, changed entries, and unresolved issues.
