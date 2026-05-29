---
name: productive-io
description: Work with Productive.io time entries through the Productive API. Use when the user mentions Productive, productive.io, uren, tijdregistratie, time entries, timesheets, or wants to inspect, export, create, update, or delete logged hours.
---

# Productive.io

Use this skill only for Productive.io hours/time-entry work. Do not broaden into projects, invoices, sales, or planning unless the user explicitly asks.

## Required env vars

Read credentials from the current repo or shell environment:

```sh
PRODUCTIVE_API_KEY=...
PRODUCTIVE_ORGANIZATION_ID=...
```

Never print the full API key. If confirming config, only say whether it exists.

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

1. Load env vars from `.env` if they are not already exported.
2. For read-only questions, call `GET /time_entries` with date/person/service filters where possible.
3. Summarize hours in human units, but keep raw minutes available for calculations.
4. For writes, show the intended date, minutes, person/service/task IDs, and note before sending the request unless the user explicitly asked to execute directly.
5. If Productive returns `401`, `403`, or `429`, stop and explain the auth, permission, or rate-limit issue.

## Useful fields

- `date`: work date
- `time`: duration in minutes
- `note`: description
- `person_id`: person who tracked time
- `service_id`: budget service
- `task_id`: task, if linked
- `started_at` / `ended_at`: timer-style entries
- `status`: approval status
