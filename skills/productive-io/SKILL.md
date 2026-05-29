---
name: productive-io
description: Work with Productive.io time entries through the Productive API. Use when the user mentions Productive, productive.io, uren, tijdregistratie, time entries, timesheets, or wants to inspect, export, create, update, or delete logged hours.
---

# Productive.io

Use this skill only for Productive.io hours/time-entry work. Do not broaden into projects, invoices, sales, or planning unless the user explicitly asks.

## Credentials

Prefer global user config, not project repos:

```sh
mkdir -p ~/.config/productive-io
cat > ~/.config/productive-io/config.env <<'EOF'
PRODUCTIVE_API_KEY=...
PRODUCTIVE_ORGANIZATION_ID=...
EOF
chmod 600 ~/.config/productive-io/config.env
```

Before API calls, load it if env vars are not already exported:

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

Fallback: if a repo already has these vars in `.env`, they may be used for that repo only. Do not create new project-local `.env` files for Productive credentials unless the user explicitly asks.

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

## Useful fields

- `date`: work date
- `time`: duration in minutes
- `note`: description
- `person_id`: person who tracked time
- `service_id`: budget service
- `task_id`: task, if linked
- `started_at` / `ended_at`: timer-style entries
- `status`: approval status
