# Productive API

## Credentials

Use credentials in this order:

1. Existing shell environment.
2. `~/.config/productive-io/config.env`.
3. An existing project `.env` as a legacy fallback only.

Required variables are `PRODUCTIVE_API_KEY` and `PRODUCTIVE_ORGANIZATION_ID`. Keep reusable personal credentials in the global config, never in this skill or a new project-local file. Never print the API key; report only whether configuration was found and loaded.

## Request basics

- Base URL: `https://api.productive.io/api/v2`
- Time entries: `/time_entries`
- Headers: `X-Auth-Token`, `X-Organization-Id`, and `Content-Type: application/vnd.api+json`
- Time is stored as minutes in the `time` attribute.

Use:

- `GET /time_entries` to list entries.
- `GET /time_entries/{id}` to verify one entry.
- `POST /time_entries` to create.
- `PATCH /time_entries/{id}` to update.
- `DELETE /time_entries/{id}` only after explicit approval.

Productive uses JSON:API payloads. A normal time entry includes `person_id`, `service_id`, `date`, and `time`; `task_id` and `note` are optional. Inspect a known live record or current API response rather than guessing relationship or attribute shape.

## Filtering

Exact-date filtering uses `filter[date]=YYYY-MM-DD`. Tested date-range operators returned `unsupported_filter_operation` in July 2026, so for a range either fetch exact dates individually or paginate recent entries and filter locally. Revalidate this behavior if the API starts accepting ranges.

Resolve a named retainer service with `GET /services/{service_id}?include=deal` and confirm the parent deal and date window before writing.

## Errors and verification

- `401`: credentials are invalid or absent.
- `403`: the identity lacks permission.
- `429`: stop and report the rate limit.
- `unsupported_filter_operation`: change the retrieval strategy; do not treat it as an empty result.

After any create or update, fetch the affected entry and confirm date, minutes, person, service, task, and note. Never expose credentials in commands, logs, or the final report.
