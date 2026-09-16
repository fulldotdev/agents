# Productive API

## Credentials

Look for credentials in this order:

1. The shell environment.
2. `~/.config/productive-io/config.env`.
3. A project `.env`, as a last resort.

You need `PRODUCTIVE_API_KEY` and `PRODUCTIVE_ORGANIZATION_ID`. Keep them in the global config, never in this skill or a new project file. Never print the key. Say only whether config was found and loaded.

## Requests

- Base URL: `https://api.productive.io/api/v2`
- Headers: `X-Auth-Token`, `X-Organization-Id`, `Content-Type: application/vnd.api+json`
- Time is stored as minutes in the `time` attribute.

Endpoints:

- `GET /time_entries` to list.
- `GET /time_entries/{id}` to check one entry.
- `POST /time_entries` to create.
- `PATCH /time_entries/{id}` to update.
- `DELETE /time_entries/{id}` only after the user approves.

Payloads are JSON:API. A time entry has `person_id`, `service_id`, `date`, and `time`; `task_id` and `note` are optional. Check a live record or a current response instead of guessing the shape.

## Filtering

`filter[date]=YYYY-MM-DD` filters one date. Date-range operators returned `unsupported_filter_operation` when last tested (July 2026). For a range, fetch day by day or paginate recent entries and filter locally. Try a range again if the API may have changed.

To resolve a retainer service, call `GET /services/{service_id}?include=deal` and confirm the parent deal and its date window before writing.

## Errors

- `401`: credentials invalid or missing.
- `403`: no permission.
- `429`: stop and report the rate limit.
- `unsupported_filter_operation`: change how you fetch. This is not an empty result.

After a create or update, fetch the entry and check date, minutes, person, service, task, and note. Keep credentials out of commands, logs, and the report.
