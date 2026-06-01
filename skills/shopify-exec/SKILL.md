---
name: shopify-exec
description: "Run Shopify Admin GraphQL queries through Shopify CLI app execute or bulk execute."
---

# Shopify Exec

Use when an installed Shopify app should query the Admin API from the CLI without manually handling tokens.

## What it is

Shopify CLI command: `shopify app execute`.

It executes an Admin API GraphQL query or mutation on a selected store using the app context. The app must be installed on that store. Shopify docs say mutations are only allowed on dev stores. For large data jobs, use `shopify app bulk execute`.

## Commands

Harmless shop check:

```bash
shopify app execute \
  --config <config> \
  --store <store>.myshopify.com \
  --query 'query { shop { name myshopifyDomain } }'
```

With variables:

```bash
shopify app execute \
  --config <config> \
  --store <store>.myshopify.com \
  --query 'query Product($id: ID!) { product(id: $id) { id title } }' \
  --variables '{"id":"gid://shopify/Product/123"}'
```

Write output to file:

```bash
shopify app execute \
  --config <config> \
  --store <store>.myshopify.com \
  --query '<graphql>' \
  --output-file result.json
```

## Rules

- Run from the app repo or pass `--config` / `--client-id`.
- Start with read-only queries.
- Ask before mutations, bulk operations, or customer-impacting changes.
- Use `--path <api-version>` only when a specific Admin API version matters.
- Never paste secrets; this command should avoid raw token handling.
