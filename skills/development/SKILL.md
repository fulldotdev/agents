---
name: development
description: Always use when implementing, reviewing, verifying, or releasing software in the user's repositories, including previews, CMS and Shopify changes, and anything touching production.
---

# Development

Follow the repository's instructions and the relevant framework skills.

## Stack and conventions

- Follow official documentation and the project's conventions. Without a convention, use kebab-case and shallow folders grouped by file type.
- Unless the project says otherwise, the user prefers:
  - Content-driven sites: Astro, Markdown with content collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm.
  - Web apps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, TanStack libraries, Clerk or WorkOS for B2B or enterprise, Resend with React Email, Stripe, pnpm.
  - Ecommerce: Shopify.
- Work locally first and in a preview by default. The main branch is production. In Shopify, work on main and publish through the CLI unless the project says otherwise.

## Production and shared environments

You may inspect production, live databases, builds, and previews people use daily. Ask before changing them, and name the target.

Shopify themes are production, including development and unpublished themes. Creating, updating, deleting, or publishing one needs the user's approval for that action and that theme. Approval for local, GitHub, or preview work does not cover it.

- Check which theme a GitHub branch is connected to before pushing or merging.
- `shopify theme dev` also uploads to Shopify. Prefer it for an approved preview.
- Use existing Shopify previews read-only unless theme writes are approved.
- Create a theme-library draft only when that was approved.

## Simplicity

- Prefer direct code, even with some duplication. Add an abstraction only when it removes repeated logic or makes the current behavior clearer.
- Remove unnecessary fallbacks, redundant checks, obvious comments, and boilerplate that adds no behavior. Keep validation and error handling for real failure cases.

Use `design` for visual or interaction decisions.

## Tests

Add or change tests only when the user asks. Run the existing tests, lint, type checks, builds, and browser checks when they help.

## Pull requests and review

A thread that changes a repository delivers one PR. A plan, review, investigation, or answer stays in the thread and Notion, with no commit and no PR. When a plan is approved, implementation continues in that thread and opens the PR then.

The PR is the record. Open a draft PR from the first code commit. Keep its description current with the preview URL, screenshots, open questions, and unresolved work. Request customer feedback on the PR's preview. A Task may have several threads over time. Use `work-management` for Notion and `t3-code` for thread dispatch.

1. Before marking ready, run the CodeRabbit CLI review once in the background while doing QA. For customer-facing work, check the changed flow on mobile and desktop and take screenshots. Use `browser` for the browser choice.
2. Fix major CLI findings without another CLI review loop.
3. Mark the PR ready to trigger CodeRabbit and Codex. Address their comments, push, and request one re-review by comment from each bot. No third round.
4. Hand off with the PR, checked preview URL, screenshots, unresolved work, and a draft customer message written with `customer-communication`. Do not send it or release.

Internal work, experiments, and tiny copy or formatting changes do not need QA screenshots.

## Delivery

Our CMSes are CloudCannon, Sanity, and Shopify. Use their skills for details. For a CMS change, check the editing experience as well as the rendered page: CloudCannon's editor, Sanity Studio, or Shopify's theme editor and custom-data fields. Test only the editing surfaces the change touches.

For a UI change, give the user a checked preview, what to look at, and any access or expiry limits. A localhost URL on Otis cannot be opened from another device.

Stop temporary processes you started. Keep requested previews running and leave pre-existing resources alone. Lasting work goes under `~/projects`, not in a temporary directory.
