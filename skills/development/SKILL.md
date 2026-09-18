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

## Simplicity and scope

- Make the smallest complete change that delivers the request. Reuse existing components and dependencies.
- Prefer direct code, even with some duplication. Add an abstraction only when it removes repeated logic or makes the current behavior clearer. Do not build for hypothetical future features.
- Remove unnecessary fallbacks, redundant checks, obvious comments, and boilerplate that adds no behavior. Keep validation and error handling for real failure cases.
- Remove dead code and scaffolding this task introduced. Report issues outside the request separately instead of fixing them.
- Review for correctness and for unnecessary complexity. Stop when the requested behavior works and the relevant checks pass.

Use `design` for visual or interaction decisions. Keep implementation details out of user-facing flows unless they help people act or decide.

## Tests

Add or change tests only when the user asks. A bug fix, a review, or a reviewer's comment is not that request. Run the existing tests, lint, type checks, builds, and browser checks when they help. Suggest new tests only for a specific unresolved risk.

## Work ownership

Continue in the existing checkout and branch, with focused commits. Check Git when you resume; the recorded branch may be stale. If another task uses the checkout, do not switch its branch or mix changes. Agree on a separate one.

Use `work-management` for tracking and Notion. Use `t3-code` when dispatching work through T3. Local reviewer subagents do not need their own T3 thread or Notion Task.

## Local review

For a substantive change, get a read-only review from an independent local Astra subagent before handoff. Give it the request, the repository instructions, the diff or branch, and access to the surrounding code. Ask for defects, regressions, missed requirements, and maintenance problems, each with a location and explanation. Cosmetic preferences are not findings.

Fix what matters within scope and recheck the affected behavior. Review again only after large fixes. A review needs no PR, new tests, or report file. Tiny copy or formatting changes need no reviewer.

## Delivery

Our CMSes are CloudCannon, Sanity, and Shopify. Use their skills for details. For a CMS change, check the editing experience as well as the rendered page: CloudCannon's editor, Sanity Studio, or Shopify's theme editor and custom-data fields. Test only the editing surfaces the change touches.

For a UI change, give the user a checked preview, what to look at, and any access or expiry limits. A localhost URL on Otis cannot be opened from another device. Report what you checked, what is unresolved, and whether the work is committed, pushed, or released, each separately.

Stop temporary processes you started. Keep requested previews running and leave pre-existing resources alone. Lasting work goes under `~/projects`, not in a temporary directory.
