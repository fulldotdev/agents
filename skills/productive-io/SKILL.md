---
name: productive-io
description: Work with Productive.io time entries through the Productive API. Use when the user mentions Productive, productive.io, uren, tijdregistratie, time entries, timesheets, or wants to inspect, export, create, update, or delete logged hours.
---

# Productive.io

Use this skill only for Productive.io hours/time-entry work. Do not broaden into projects, invoices, sales, or planning unless the user explicitly asks. When reconstructing hours, contracts and invoices may be used as evidence for exact date ranges and total hours, but this skill should still produce Productive time-entry work rather than finance, sales, or project-planning output.

## Loop integration

Productive.io is a domain skill, not the loop owner. When `agency-work` starts Productive work, this skill defines the Productive-specific evidence model, context collection, time-entry shape, and write safety.

The loop owns timing, sprint/project selection, thread orchestration, Notion writeback, and follow-up scheduling. This skill owns how Productive hours are inspected, reconstructed, proposed, created, updated, and reported.

For Sprint work, use this skill for the Productive part and keep planning, routing, and Notion decisions in `agency-work`.

## Credentials

Preferred credential order:

1. Already-exported shell env vars.
2. Global user config at `~/.config/productive-io/config.env`.
3. Existing repo `.env` only as a legacy fallback.

Store personal Productive credentials in global user config, not in project repos or this skill repo:

```sh
mkdir -p ~/.config/productive-io
cat > ~/.config/productive-io/config.env <<'EOF'
PRODUCTIVE_API_KEY=...
PRODUCTIVE_ORGANIZATION_ID=...
EOF
chmod 600 ~/.config/productive-io/config.env
```

Before API calls, load the global config if env vars are not already exported:

```sh
set -a
[ -f ~/.config/productive-io/config.env ] && . ~/.config/productive-io/config.env
set +a
```

Required variables:

```sh
PRODUCTIVE_API_KEY=...
PRODUCTIVE_ORGANIZATION_ID=...
```

Fallback: if a repo already has these vars in `.env`, they may be used for that repo only. Do not create new project-local `.env` files for Productive credentials unless the user explicitly asks. If Productive credentials are found in a project `.env`, prefer moving them to `~/.config/productive-io/config.env` and removing them from the project file.

Never print the full API key. If confirming config, only say whether it exists and where it was loaded from.

## API basics

- Base URL: `https://api.productive.io/api/v2`
- Time entries endpoint: `/time_entries`
- Auth headers:
  - `X-Auth-Token: $PRODUCTIVE_API_KEY`
  - `X-Organization-Id: $PRODUCTIVE_ORGANIZATION_ID`
  - `Content-Type: application/vnd.api+json`

The API uses JSON:API-style payloads. Time is stored as minutes in the `time` attribute.

## Common calls

List time entries:

```sh
curl -sS "https://api.productive.io/api/v2/time_entries?page[size]=50" \
  -H "X-Auth-Token: $PRODUCTIVE_API_KEY" \
  -H "X-Organization-Id: $PRODUCTIVE_ORGANIZATION_ID" \
  -H "Content-Type: application/vnd.api+json"
```

Date filtering note: Productive currently accepts exact-date filtering (`filter[date]=YYYY-MM-DD`) on `time_entries`, but rejected tested range operators with `unsupported_filter_operation` in July 2026. For ranges, paginate recent entries and filter dates locally, or fetch exact dates individually for short windows.

Exact date example:

```sh
curl -sS "https://api.productive.io/api/v2/time_entries?filter[date]=2026-05-01&page[size]=100" \
  -H "X-Auth-Token: $PRODUCTIVE_API_KEY" \
  -H "X-Organization-Id: $PRODUCTIVE_ORGANIZATION_ID" \
  -H "Content-Type: application/vnd.api+json"
```

Get one time entry:

```sh
curl -sS "https://api.productive.io/api/v2/time_entries/ENTRY_ID" \
  -H "X-Auth-Token: $PRODUCTIVE_API_KEY" \
  -H "X-Organization-Id: $PRODUCTIVE_ORGANIZATION_ID" \
  -H "Content-Type: application/vnd.api+json"
```

Create or update hours only after confirming the required IDs. For manual retroactive writes, show the intended entries to the user first unless Sil explicitly asked to execute directly. For loop-driven routine weekly registration, writes may proceed when the evidence and IDs satisfy the reconstruction rules below. A normal time entry usually needs at least:

- `person_id`
- `service_id`
- `date`
- `time` in minutes
- optional `task_id`
- optional `note`

Use:

- `POST /time_entries` to create
- `PATCH /time_entries/{id}` to update
- `DELETE /time_entries/{id}` to delete

## Workflow

1. Load env vars from the shell or `~/.config/productive-io/config.env`; use repo `.env` only as a fallback when it already exists.
2. For read-only questions, call `GET /time_entries` with date/person/service filters where possible.
3. For named retainers, resolve the selected service with `GET /services/{service_id}?include=deal` and verify the parent deal and entry date before writing.
4. Summarize hours in human units, but keep raw minutes available for calculations.
5. For manual writes, show the intended date, minutes, person/service/task IDs, and note before sending the request unless the user explicitly asked to execute directly. For loop-driven routine weekly registration, write when the reconstruction rules say evidence is strong enough; otherwise report the blocker to the loop/steward.
6. If Productive returns `401`, `403`, or `429`, stop and explain the auth, permission, or rate-limit issue.

## Weekly hours loop

Routine Productive hour reconstruction is driven by the `agency-work` planning workflow. The old standalone cron job named `productive-hours` was retired; do not assume it exists.

The skill name remains `productive-io`. `productive-hours` was only the old cron/job name.

Expected loop setup:

1. A visible Notion Task such as `Productive hours reconcile` owns the weekly Productive workstream.
2. The `agency-work` workflow owns timing, writeback, and any follow-up Task creation.
3. Scope should come from the Task/Project/Sprint context, such as Small Giants, Teveo, Skantrae, Fayn, and the target Monday-Sunday week.
4. The loop may register hours when evidence is good enough, then report a compact project-first summary so Sil can correct the split afterward.
5. After completion, ensure the next weekly Productive Task exists in Notion unless a Notion recurring automation already created it.

Do not recreate vague legacy tasks such as `Uren invullen in Productive` just because a month/week started. If Productive credentials, contract context, or invoice context are missing, report the blocker on the visible Notion Task instead of inventing duplicate planning tasks.

## Context collection

Productive is scoped through the Small Giants work context. Treat Small Giants as the Productive/customer wrapper, and treat Teveo, Skantrae, Fayn, or similar names as project/client filters inside that wrapper. Do not mix unrelated Productive customers into the evidence set.

Collect only the evidence needed for the target project/week. Useful evidence lanes:

1. `moneybird`: invoice/contract target lines for the Small Giants customer/window and relevant project/client.
2. `productive`: existing entries for known Small Giants service IDs, plus the previous few weeks as reference context.
3. `calendar`: all calendar events in the same week/window by default; only filter when an explicit calendar query is provided.
4. `notion`: search context plus tasks/projects/customers edited in the same week/window.
5. `github`: commits by Sil in the same week/window across explicit project repos where possible; local repo scan is acceptable as fallback.

Lane failure means collect the rest, but report the failed lane and do not pretend the evidence is complete. The agent owns reconciliation and Productive writes; no helper script is authoritative.

## Retroactive hours reconstruction

Use this mode when the user wants to fill, audit, or repair Productive hours after work already happened. Productive is the registration endpoint, not the source of truth.

### Source priority

1. Contracts, agreements, retainers, and invoices define the hard boundaries:
   - customer and project
   - date range
   - exact total hours or billable amount converted to hours
   - explicit exclusions, such as fixed-price work where hours should not be logged
2. Existing Productive entries define what is already registered:
   - person
   - project/service/task IDs
   - dates
   - minutes
   - notes
   - approval/status
3. Calendar events indicate meetings, kickoff/setup timing, customer touchpoints, and days when work realistically started.
4. Notion tasks, sprint pages, project pages, comments, and status history indicate what work likely happened and which buckets it belongs to.
5. GitHub commits, pull requests, and merged branches indicate roughly when engineering work happened and which project or task it relates to.
6. Chat or memory context may clarify intent, but should not override contracts, invoices, or live Productive data.

### Reconstruction rules

1. Work contract-total-first: the final Productive total must match the contract/invoice total for the relevant date range.
2. Treat exact dates and per-task durations as estimates unless a source explicitly says otherwise.
3. Use Calendar, Notion, and GitHub evidence to distribute hours over plausible work dates, weeks, projects, services, and notes. Calendar comes first for meeting-heavy setup weeks and start-date reality checks.
4. Preserve existing Productive entries where possible. Fill gaps before changing existing entries.
5. Avoid fake precision. Prefer rounded entries such as 30, 45, 60, 90, 120, or 180 minutes unless existing entries use another pattern.
6. Match the parent Productive deal and entry date before matching a service ID. Never infer a retainer bucket from the time-entry note or service name alone.
7. Keep weekly totals plausible, but prioritize the period total when there is tension.
8. For loop-driven weekly registration, create or update entries when the target total, person, service/project bucket, and weekly allocation are sufficiently clear from contracts/invoices, Productive, Notion, GitHub, or stable prior mappings.
9. Preserve existing Productive entries where possible. Fill gaps before changing existing entries. Do not delete entries unless Sil explicitly asks.
10. Flag overlaps, missing evidence, unclear services, or contract/invoice mismatches as blockers instead of fabricating certainty.
11. For manual retroactive work outside an approved loop run, show the proposed diff first unless Sil explicitly asked to execute directly.

### Teveo automated testing retainer

Keep Teveo automated testing separate from regular Teveo sprint development. Use the automated testing retainer only for BrowserStack/Percy/test-run work, such as:

1. Reviewing daily or weekly BrowserStack test runs.
2. Investigating BrowserStack failures or flaky regression results.
3. Updating tests after feature changes.
4. Adding clearly new test coverage.
5. Sprint QA/release regression checks tied to the automated test setup.

Treat the Productive bucket identity as strict:

1. Require the parent deal name to contain `Automated Testing Retainer` and require its date range to cover the entry date.
2. Reject every `AB testing` service and every service under `Teveo - CRO & Development 2026`; those are CRO experimentation, not automated testing.
3. Use the `Development` service only when its parent deal is the automated testing retainer. The service label alone is not the bucket identity.
4. For July 2026, use deal `#2494` and service ID `15255108`. Resolve later months from the matching dated retainer deal instead of reusing this ID.

Do not use the automated testing retainer for normal feature implementation, theme work, CRO work, wishlist changes, translations, Klaviyo/VWO work, or generic release work unless the note clearly explains the test impact.

When evidence is thin, it is acceptable to reserve about 2h per week for test-run review because the automated suite always needs recurring review. The remaining testing capacity can move across weeks: one week may be 0h and another 4h when a new test is added or a real BrowserStack issue is investigated.

### Teveo weekly contract buckets

For routine Small Giants Productive registration, use the contract baseline before inferred calendar/GitHub distribution:

1. Teveo development: 8h per week.
2. Teveo customer lead: 1h per week.
3. Teveo automated testing: contract line is 4h per week for 12 weeks when extended. Operationally, keep at least 2h in active weeks and about 4h/week average across the run.

### Skantrae contract bucket

For Skantrae ONE project weeks, use the SOW baseline:

1. Skantrae development retainer: 16h per week for 8 weeks.

Name the PM/customer service bucket `customer lead` in summaries.

### Expected output

For loop-driven weekly execution, produce:

1. A compact project-first summary, not a per-day ledger.
2. Omit verification language when verification succeeded; if it is reported, it should be true by default.
3. Group services under each project only when useful, such as customer lead, development, or automated testing.
4. Keep notes to one short line only when they change how Sil should interpret the split.
5. Mention caps, SOW, or Moneybird uncertainty only as one short caveat when it affects billing.
6. Use this shape:

```md
1. Teveo: 13h
   Customer lead 1h, development 8h, automated testing 4h.

2. Skantrae: 16h
   Development retainer.

3. Fayn: 0h apart
   Staat nu verstopt in Teveo-notes.

4. Totaal: 29h
   Week 2026-06-15 t/m 2026-06-21.
```

For write preparation, produce a concrete entry plan with date, minutes, person ID, service ID, optional task ID, and note for every proposed entry.

## Useful fields

- `date`: work date
- `time`: duration in minutes
- `note`: description
- `person_id`: person who tracked time
- `service_id`: budget service
- `task_id`: task, if linked
- `started_at` / `ended_at`: timer-style entries
- `status`: approval status
