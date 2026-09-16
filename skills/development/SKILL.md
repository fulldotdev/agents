---
name: development
description: Always use when implementing, reviewing, verifying, or releasing software in the user's repositories, including previews, CMS and Shopify changes, and anything touching production.
---

# Development

Follow the repository's instructions and the relevant framework skills.

## Stack and conventions

- Follow official documentation. Follow existing project conventions; otherwise use kebab-case and shallow folders grouped by file type.
- Unless the project says otherwise, the user prefers:
  - Content-driven sites: Astro, Markdown with content collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm.
  - Web apps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, TanStack libraries, Clerk or WorkOS for B2B or enterprise, Resend with React Email, Stripe, pnpm.
  - Ecommerce: Shopify.
- Work locally first and in a preview by default. The main branch is production. In Shopify, work on main and publish through the CLI unless the project says otherwise.
- Suggest a bold idea when it has a clear benefit.

## Production and shared environments

You may inspect production, live databases, builds, and previews people use daily. Ask before changing them, and name the target.

Shopify themes are production. Creating, updating, deleting, or publishing a theme needs the user's approval for that action and that theme, including development and unpublished themes. Approval for local, GitHub, or preview work does not cover it. Check which theme a GitHub branch is connected to before pushing or merging. `shopify theme dev` also uploads to Shopify. Use existing Shopify previews read-only unless theme writes are approved. For an approved preview, prefer `shopify theme dev`. Create a theme-library draft only when that was approved.

## Simplicity and scope

- Make the smallest complete change that delivers the request. Reuse existing components and dependencies.
- Prefer direct code, even with some duplication. Add an abstraction only when it removes repeated logic or makes the current behavior clearer. Do not build for hypothetical future features.
- Remove unnecessary fallbacks, redundant checks, obvious comments, and boilerplate that adds no behavior. Keep validation and error handling for real failure cases.
- Remove dead code and scaffolding this task introduced. Report issues outside the request separately. Do not turn them into cleanup, migration, or redesign work.
- Review for correctness and for unnecessary complexity. Stop when the requested behavior works and the relevant checks pass.

Use `design` for visual or interaction decisions. Keep implementation details out of user-facing flows unless they help people act or decide.

## Tests

Add or change tests only when the user asks. A bug fix, a review, or a reviewer's comment is not that request. Run the existing tests, lint, type checks, builds, and browser checks when they help. Only raise the question of new tests when a specific unresolved risk needs it.

## Work ownership

Continue in the existing checkout and branch. The user prefers one branch with focused commits. Check Git when you resume; the thread's recorded branch may be stale. If another task is using the checkout, coordinate or use a separately agreed one. Do not switch its branch or mix changes.

Use `work-management` for tracking and Notion. Use `t3-code` when dispatching work through T3. Local reviewer subagents do not need their own T3 thread or Notion Task.

## Local review

For a substantive change, ask an independent local Astra reviewer subagent for a read-only review before handoff. Give it the request, the repository instructions, the diff or branch, and access to the surrounding code. Ask for defects, regressions, missed requirements, and maintenance problems that matter, each with a location and explanation. Cosmetic preferences are not findings.

Weigh the findings, fix what matters within scope, and recheck the affected behavior. Ask for another review only when the fixes changed enough code. A review does not need a PR, new tests, or a report file. Tiny copy or formatting changes do not need a reviewer.

## Delivery

Our CMSes are CloudCannon, Sanity, and Shopify. Use their skills for details. For a CMS change, check the editing experience as well as the rendered page: CloudCannon's editor, Sanity Studio, or Shopify's theme editor and custom-data fields. Test only the editing surfaces the change touches.

For a UI change, give the user a checked preview, what to look at, and any access or expiry limits. A localhost URL on Otis cannot be opened from another device. Report what you checked, what is unresolved, and whether the work is committed, pushed, or released, each separately.

Close research and validation tabs you opened and stop temporary processes. Keep requested previews running and leave pre-existing resources alone. Lasting work goes under `~/projects`, not in a temporary directory.
