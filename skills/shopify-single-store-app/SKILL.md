---
name: shopify-single-store-app
description: "Create or link one single-store Shopify app as a server-side proxy for storefront actions and Admin API access."
---

# Shopify Single-Store App

Use when one customer store needs a small Shopify app for Admin API access, app extensions, or server-side actions the theme/frontend cannot safely do.

Think of it as a store-owned proxy, not a productized multi-tenant app. The frontend asks for a named action; the app validates it, uses Shopify server-side, and returns only the result the frontend needs.

## Rules

- Treat the current repo as the customer repo.
- Prefer an existing app/helper repo over scaffolding.
- Pause before Shopify account-bound create/link/install steps.
- Keep `.env` ignored. Never print tokens, secrets, or raw `.env`.
- Use minimum scopes unless broad access is explicitly needed.
- Keep the app single-store unless the user explicitly asks for multi-tenant.
- Do not expose a generic Admin API proxy. Expose named, allowlisted actions only.

## Proxy Pattern

- Theme/frontend stays thin: render UI, collect handles/IDs/cart/customer context, call one app endpoint, render returned state.
- App owns secrets, Admin GraphQL, app extensions, and one-off setup actions.
- Routes map to concrete actions such as `wishlist-sync`, `discount-activate`, `customer-metafield-update`, or `product-fragment`.
- Validate method, shop, origin/app-proxy signature, body shape, customer/cart ownership, and idempotency before touching Shopify.
- Return small JSON or rendered fragments. Never return tokens, raw Admin errors, or broad Shopify objects.
- Put Shopify calls in server modules (`*.server.*`) so route handlers stay small.
- Prefer app proxy/storefront-domain calls when theme JS needs same-origin requests; otherwise lock CORS/origin to the exact store.
- Keep an embedded admin shell minimal: useful for auth, scope grants, status checks, and one-time activation buttons. No fake dashboard.

## Workflow

1. Identify exact `<store>.myshopify.com`.
2. Name the concrete server-side actions the frontend needs. If it is only wishlist today, still design it as a general proxy app.
3. Check existing `.env` for `SHOPIFY_ADMIN_ACCESS_TOKEN`, `SHOPIFY_API_KEY`, and `SHOPIFY_API_SECRET`.
4. Verify existing Admin token first with a harmless `shop { name myshopifyDomain }` query.
5. If no token exists, link/create app config:

```bash
shopify app config link --reset
```

6. Deploy app config/scopes:

```bash
shopify app deploy --config <config> --allow-updates --allow-deletes --no-color
```

7. Pull/show app env and write needed keys to local `.env` only:

```bash
shopify app env show --config <config> --no-color
```

8. Install/distribute the app for the target store. If custom distribution requires browser approval, give the user the distribution URL and wait.
9. Wire the theme/frontend to action endpoints. Keep browser state as a cache, not the source of truth for privileged actions.
10. Prefer client credentials when app/store ownership permits; if Shopify returns `shop_not_permitted`, stop retrying and use OAuth offline token or a store-created custom app token.
11. Verify Admin GraphQL access and each frontend action. Report app/config/store/routes and verification result, never secret values.
