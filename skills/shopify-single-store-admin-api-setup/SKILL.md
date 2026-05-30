---
name: shopify-single-store-admin-api-setup
description: Sets up Admin API access for one Shopify customer store using Shopify CLI, a Dev Dashboard app, custom distribution, and either client-credentials or OAuth offline token flow. Use when a user wants Codex to create or link a Shopify app, deploy broad Admin scopes, install it for a customer store, write credentials into a repo `.env`, or troubleshoot `shop_not_permitted`.
---

# Shopify Single-Store Admin API Setup

## Outcome

Create or link one Shopify app for a customer store, deploy Admin API scopes, write local credentials into the current repo `.env`, and verify Admin GraphQL access. Choose the auth path that matches store ownership.

## Defaults

- Treat the current working directory as the customer repo.
- Use `../fulldev-shopify-app` if it exists; scaffold/create a helper repo only if a Dev Dashboard app is needed.
- Name the app after the customer store/repo.
- Pause before account-bound create/link steps until the user confirms Shopify CLI is logged into the correct account.
- Keep `.env` ignored. Never echo tokens, secrets, or raw `.env` contents.

## Workflow

### 1. Identify Access

- Determine the exact `<store>.myshopify.com` domain.
- If `.env` has `SHOPIFY_ADMIN_ACCESS_TOKEN`, verify it first with a harmless shop query.
- If `.env` has `SHOPIFY_API_KEY` and `SHOPIFY_API_SECRET`, treat them as app credentials, not an Admin token.
- Ensure `.gitignore` excludes `.env` before writing secrets.

### 2. Choose Auth Path

- If the app and store are owned by the same Shopify organization, try client-credentials first.
- If client-credentials returns `shop_not_permitted`, stop retrying and use OAuth authorization-code to obtain an offline Admin token.
- If the user can create a store-owned custom app directly in Shopify Admin, a manually copied Admin API access token is simpler than a Dev Dashboard app.

### 3. Create or Link App

```bash
cd ../fulldev-shopify-app
shopify app config link --reset
```

- Select the correct organization and create/link an app named for the customer.
- In a shared helper repo, prefer a separate config such as `shopify.app.<customer>.toml`.
- Re-open generated TOML after linking; CLI can overwrite local edits.

### 4. Deploy Scopes

- Use the broad validated scope string in [references/validated-scopes.md](references/validated-scopes.md), or derive minimal task scopes.
- Avoid rejected scopes listed in that reference unless explicitly retesting.

```bash
shopify app deploy --config <customer> --allow-updates --allow-deletes --no-build --no-color
```

- Capture the version URL and derive:

```txt
https://partners.shopify.com/org/<org_id>/org_apps/<app_numeric_id>/distribution
```

### 5. Store App Credentials

```bash
shopify app env show --config <customer> --no-color
```

Write to the customer repo `.env`:

```env
SHOPIFY_STORE_DOMAIN=<store>.myshopify.com
SHOPIFY_API_KEY=...
SHOPIFY_API_SECRET=...
```

### 6. Distribution Install

- For Partner-org apps, hand off the distribution URL; CLI cannot finish custom distribution.
- Steps for user: choose `Custom distribution`, paste store domain, save, continue to install.
- After user confirms install, verify token acquisition.

### 7. Verify Client Credentials

```bash
curl -sS -X POST "https://${SHOPIFY_STORE_DOMAIN}/admin/oauth/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=client_credentials" \
  --data-urlencode "client_id=${SHOPIFY_API_KEY}" \
  --data-urlencode "client_secret=${SHOPIFY_API_SECRET}"
```

- If it returns `access_token`, use it for Admin API calls.
- If it returns `shop_not_permitted`, use the OAuth fallback.

### 8. OAuth Offline-Token Fallback

- Temporarily deploy local callback config: `application_url = "http://localhost:3456"` and `redirect_urls = [ "http://localhost:3456/auth/callback" ]`.
- Start a local server that builds `/admin/oauth/authorize`, verifies `state` and HMAC, exchanges `code`, and writes `SHOPIFY_ADMIN_ACCESS_TOKEN=...` to `.env`.
- Open the authorization URL for user approval.
- After success, restore the app URL/redirects and redeploy.

### 9. Verify Admin API

Run a harmless Admin GraphQL shop query. Report shop name/domain and whether errors returned. Do not show token values.

## Final Handoff

Include app name/org, scope deploy status, credentials/token written to `.env`, Admin GraphQL verification, remaining manual steps, and helper repo files left untracked.
