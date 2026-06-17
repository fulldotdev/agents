---
name: productive-io
description: Work with Productive.io time entries through the Productive API. Use when the user mentions Productive, productive.io, uren, tijdregistratie, time entries, timesheets, or wants to inspect, export, create, update, or delete logged hours.
---

# Productive.io

Use this skill only for Productive.io hours/time-entry work. Do not broaden into projects, invoices, sales, or planning unless the user explicitly asks. When reconstructing hours, contracts and invoices may be used as evidence for exact date ranges and total hours, but this skill should still produce Productive time-entry work rather than finance, sales, or project-planning output.

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

Filter by date range:

```sh
curl -sS "https://api.productive.io/api/v2/time_entries?filter[date][gte]=2026-05-01&filter[date][lte]=2026-05-31&page[size]=100" \
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

Create or update hours only after confirming the required IDs with the user. A normal manual time entry usually needs at least:

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
3. Summarize hours in human units, but keep raw minutes available for calculations.
4. For writes, show the intended date, minutes, person/service/task IDs, and note before sending the request unless the user explicitly asked to execute directly.
5. If Productive returns `401`, `403`, or `429`, stop and explain the auth, permission, or rate-limit issue.

## Productive-hours ownership

Routine Productive hour reconstruction is owned by the `productive-hours` cron, not by `work-planning`.

Current setup:

1. Cron name: `productive-hours`.
2. Cadence: every Monday at 09:00 Europe/Amsterdam.
3. Delivery: Work Telegram group.
4. Scope: Small Giants, previous complete Monday-Sunday week.
5. Mode: read-only/proposal-only by default. It reports target totals, existing entries, gaps, and proposed allocation. It does not create/update/delete Productive entries unless Sil explicitly asks in a separate manual run.

Do not recreate old Notion routine tasks such as `Uren invullen in Productive` just because a month/week started. If Productive credentials, contract context, or invoice context are missing, report the blocker instead of inventing a manual planning task.

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
3. Notion tasks, sprint pages, project pages, comments, and status history indicate what work likely happened and which buckets it belongs to.
4. GitHub commits, pull requests, and merged branches indicate roughly when engineering work happened and which project or task it relates to.
5. Chat or memory context may clarify intent, but should not override contracts, invoices, or live Productive data.

### Reconstruction rules

1. Work contract-total-first: the final Productive total must match the contract/invoice total for the relevant date range.
2. Treat exact dates and per-task durations as estimates unless a source explicitly says otherwise.
3. Use Notion and GitHub evidence to distribute hours over plausible work dates, weeks, projects, services, and notes.
4. Preserve existing Productive entries where possible. Fill gaps before changing existing entries.
5. Avoid fake precision. Prefer rounded entries such as 30, 45, 60, 90, 120, or 180 minutes unless existing entries use another pattern.
6. Match existing Productive service buckets and naming before creating or requesting new ones.
7. Keep weekly totals plausible, but prioritize the period total when there is tension.
8. Flag overlaps, missing evidence, unclear services, or contract/invoice mismatches before writing.
9. Never create, update, or delete entries silently. Show the proposed diff first unless the user explicitly asked to execute directly.

### Expected output

For read-only reconstruction, produce:

1. Contract/invoice target total and date range.
2. Existing Productive total for that range.
3. Gap or surplus in hours.
4. Evidence summary from Notion and GitHub.
5. Proposed Productive allocation by week, service, project, and note.
6. Blockers or assumptions.

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
