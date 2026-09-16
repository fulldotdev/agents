---
name: productive-io
description: Use when the user explicitly asks to inspect, export, correct, create, change, or delete Productive.io time entries. Do not use Productive for routine planning, triage, delivery, or commercial scoping.
---

# Productive.io

Read [references/api.md](references/api.md) for credentials, API calls, payloads, and errors. Read [references/reconstruction.md](references/reconstruction.md) when filling, auditing, or repairing hours from contracts and work evidence.

## Workflow

1. Establish the person, customer or project, service, and date window.
2. Load credentials without printing them and look at the existing entries for that scope.
3. Resolve live person, deal, service, and optional task IDs before a write. For a retainer, check that the parent deal covers the entry date.
4. For a read or export, return entries or totals in hours and minutes. Keep raw minutes for calculations.
5. For a requested reconstruction, follow `reconstruction.md`: match the agreed total for the period, keep existing entries, place the remaining time using evidence, and flag any mismatch you cannot resolve.
6. Show the proposed diff before a write, unless the user asked you to run that exact change.
7. Never delete an entry unless the user asks for that.

## Writes

A proposed entry has a date, minutes, person ID, service ID, an optional task ID, and a short note when it helps identify the work.

Do not pick a service from its label or an existing note alone. Confirm that its parent deal covers the entry date. Fill gaps before changing existing entries. Do not give reconstructed durations false precision.

Stop when the person is unknown, the service or deal is unclear, contract totals conflict, or evidence is thin. Name the missing fact.

## Output

Report the period, totals, changed entries, and unresolved issues.
