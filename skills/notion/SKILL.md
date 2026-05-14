---
name: notion
description: Notion API for creating and managing pages, data sources/databases, markdown page bodies, and blocks.
homepage: https://developers.notion.com
metadata:
  {
    "openclaw":
      { "emoji": "📝", "requires": { "env": ["NOTION_API_KEY"] }, "primaryEnv": "NOTION_API_KEY" },
  }
---

# notion

Use the Notion API to create/read/update pages, data sources (databases), markdown page bodies, and blocks.

## Setup

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store it:

```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```

4. Share target pages/databases with your integration (click "..." → "Connect to" → your integration name)

## API Basics

All requests need:

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json"
```

> **Note:** The `Notion-Version` header is required. This skill uses `2026-03-11`, which includes the enhanced markdown page-body API. In current versions, databases are called data sources in the API.

## Reading Notion work context

Use two calls when both fields and body are needed:

1. **Page/data source properties:** `GET /v1/pages/{page_id}` or `POST /v1/data_sources/{data_source_id}/query`
2. **Page body markdown:** `GET /v1/pages/{page_id}/markdown`

The markdown read endpoint returns only:

- `object`
- `id`
- `markdown`
- `truncated`
- `unknown_block_ids`

It does **not** include page properties, relation fields, status, select values, rollups, etc.

## Common Operations

**Search for pages and data sources:**

```bash
curl -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

Use this for discovery only. Do not use `/v1/search` as the final method for structured questions like which projects belong to a contact, which tasks belong to a project, or which meetings involve a person. For those, query the relevant data source directly with filters/relations.

**Get page properties:**

```bash
curl "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11"
```

**Get page body as markdown:**

```bash
curl "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11"
```

Use `?include_transcript=true` only when meeting-note transcript text is needed. If the response has `truncated: true`, inspect `unknown_block_ids`; inaccessible child content may still return `object_not_found`.

**Get page content as blocks:**

```bash
curl "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11"
```

Use blocks when structured block data is required, or when markdown output contains unsupported `<unknown>` blocks that need block-level inspection.

**Create page in a data source with properties and markdown body:**

```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    },
    "markdown": "# Context\n\nUseful body content."
  }'
```

`markdown` is mutually exclusive with `children` and `content`, not with `properties`. If `properties.title` is omitted, Notion can extract the title from the first `# h1`.

**Query a data source (database):**

```bash
curl -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

**Create a data source (database):**

```bash
curl -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

**Update page properties:**

```bash
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

**Update page body with markdown:**

```bash
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "update_content",
    "update_content": {
      "old_str": "Old exact markdown text",
      "new_str": "New exact markdown text"
    }
  }'
```

Prefer `update_content` for exact search/replace and `replace_content` for full body replacement. Read the body first and avoid blind appends. Updates return the full page content as markdown.

**Add blocks to page:**

```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2026-03-11" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
    ]
  }'
```

## Property Types

Common property formats for database items:

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "a@b.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## Key API Differences

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries and retrieval.
- **Two IDs:** Each database has both a `database_id` and a `data_source_id`.
  - Use `database_id` when creating pages (`parent: {"database_id": "..."}`).
  - Use `data_source_id` when querying (`POST /v1/data_sources/{id}/query`).
- **Search results:** Databases return as `"object": "data_source"` with their `data_source_id`.
- **Parent in responses:** Pages show `parent.data_source_id` alongside `parent.database_id`.
- **Finding the data_source_id:** Search for the database, or call `GET /v1/data_sources/{data_source_id}`.

## Contacts and structured queries

If a user mentions a person name in a Notion context, prefer this order:
1. resolve the person in the Notion `Contacts` database
2. use relations/filters from Contacts, Projects, Meetings, or Tasks
3. use `/v1/search` only if the database or page is unknown

## Notes

- Page/database IDs are UUIDs (with or without dashes).
- The API cannot set database view filters — that's UI-only.
- Rate limit: ~3 requests/second average, with `429 rate_limited` responses using `Retry-After`.
- Append block children: up to 100 children per request, up to two levels of nesting in a single append request.
- Payload size limits: up to 1000 block elements and 500KB overall.
- Use `is_inline: true` when creating data sources to embed them in pages.
