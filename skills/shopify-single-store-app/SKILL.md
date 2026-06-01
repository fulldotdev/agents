---
name: shopify-single-store-app
description: "Create or link one Shopify app for one customer store, deploy scopes, install it, and verify Admin API access."
---

# Shopify Single-Store App

Use when one customer store needs a Shopify app for Admin API access, app extensions, or store-specific automation.

## Rules

- Treat the current repo as the customer repo.
- Prefer an existing app/helper repo over scaffolding.
- Pause before Shopify account-bound create/link/install steps.
- Keep `.env` ignored. Never print tokens, secrets, or raw `.env`.
- Use minimum scopes unless broad access is explicitly needed.

## Workflow

1. Identify exact `<store>.myshopify.com`.
2. Check existing `.env` for `SHOPIFY_ADMIN_ACCESS_TOKEN`, `SHOPIFY_API_KEY`, and `SHOPIFY_API_SECRET`.
3. Verify existing Admin token first with a harmless `shop { name myshopifyDomain }` query.
4. If no token exists, link/create app config:

```bash
shopify app config link --reset
```

5. Deploy app config/scopes:

```bash
shopify app deploy --config <config> --allow-updates --allow-deletes --no-color
```

6. Pull/show app env and write needed keys to local `.env` only:

```bash
shopify app env show --config <config> --no-color
```

7. Install/distribute the app for the target store. If custom distribution requires browser approval, give the user the distribution URL and wait.
8. Prefer client credentials when app/store ownership permits; if Shopify returns `shop_not_permitted`, stop retrying and use OAuth offline token or a store-created custom app token.
9. Verify Admin GraphQL access. Report app/config/store and verification result, never secret values.
