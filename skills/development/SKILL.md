---
name: development
description: Always use when implementing, reviewing, verifying or releasing software in Sil's repositories, including previews, CMS and Shopify changes, and anything touching production.
---

# Development

Follow the repository's instructions and relevant framework skills. Match the planning, tools, and amount of work to the request.

## Stack and conventions

- Propose bold ideas when they offer a clear benefit.
- Follow official documentation and guidance.
- Follow existing project conventions. Otherwise, prefer kebab-case and shallow folders grouped by file type.
- Unless the project already specifies otherwise, Sil prefers:
  - Content-driven sites: Astro, Markdown with content-collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm
  - Webapps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, Tanstack libraries, Clerk or WorkOS when B2B/enterprise, Resend with React Email, Stripe, pnpm
  - Ecommerce in Shopify
- Work locally first and in preview by default, with the main branch being production. In Shopify, work on main directly and publish production over CLI, unless the project specifies a different workflow.

## Production and shared environments

You may inspect production, live databases, and builds or previews used for daily work. Changes require explicit authorization. Name the target before changing it.

## Simplicity and scope

- Make the smallest complete change that delivers the requested result. Reuse existing components and dependencies.
- Prefer direct code, even with some duplication. Add an abstraction only when it removes repeated logic or makes the current behavior clearer. Do not build for hypothetical future features.
- Remove unnecessary fallbacks, redundant checks, obvious comments, and boilerplate that adds no behavior. Keep validation and error handling for real failure cases.
- Remove dead code and temporary scaffolding introduced by this task. Report important issues outside the request separately; do not turn them into extra cleanup, migration, or redesign work.
- Review for both correctness and unnecessary complexity. Stop when the requested behavior works and the relevant checks pass.

Use `design` when the task involves visual or interaction decisions. Keep implementation details out of user-facing flows unless they help the user act or decide.

## Tests

Create or extend tests only when Sil explicitly asks. This includes unit, integration, end-to-end and regression tests, fixtures, test infrastructure, and one-off automated test scripts. Building, fixing, reviewing, or verifying software does not by itself authorize new tests. Reviewer feedback does not provide that authorization either.

Run relevant existing tests, linting, type checks, builds, and browser checks when useful. Do not ask to add tests by default; raise it only when a specific unresolved risk makes that decision necessary. An explicit test or benchmark request authorizes the testing it describes.

## Work ownership

Continue in the existing checkout and branch by default. Sil prefers one branch with focused commits. Check Git when resuming; the thread's recorded branch may be outdated. If another task is using the checkout, coordinate or use a separately agreed checkout. Do not switch its branch or mix changes.

Use `work-management` for tracking and Notion routing. Use `t3-code` when dispatching work through T3; local reviewer sub-agents do not need their own T3 threads or Notion Tasks.

## Local review

For substantive code changes, use an independent local Astra reviewer subagent before handoff. Give it the request, repository instructions, diff or PR branch, and access to surrounding code. Ask for a read-only review of defects, regressions, missed requirements, and maintenance problems that matter, each with a location and explanation. Cosmetic preferences alone are not findings.

Evaluate the findings and fix relevant issues within scope. Recheck affected behavior after fixes. Use another review when the fixes change enough code to warrant it. A review does not require a PR, new tests, or a report file. Tiny copy or formatting changes do not need a reviewer.

## Reviewable delivery

Creating, updating, deleting or publishing a Shopify theme requires Sil's explicit authorization for that Shopify action and target, including development and unpublished themes. Permission for local/GitHub work or preview review does not grant permission to change Shopify themes. Check connected-theme effects before pushing or merging GitHub branches; `shopify theme dev` also uploads to Shopify.

Use existing Shopify previews read-only unless theme writes are authorized. For an authorized preview deployment, prefer `shopify theme dev`; create a theme-library draft only when its creation is authorized.

Our CMSes are CloudCannon, Sanity, and Shopify. Use their existing skills for implementation details. For CMS changes, verify the affected editing experience as well as the rendered page: CloudCannon's configured editor, Sanity Studio, or Shopify's theme editor and relevant custom-data fields. Use the project's authorized development environment; test only the editing surfaces the change affects.

For UI changes, give Sil a checked preview, what to inspect, and any access or expiry limits. An Otis localhost URL alone cannot be reviewed from another device. Report what was verified, unresolved issues, and whether the work is committed, pushed, or released. State each separately.

Close task-created research and validation tabs and stop temporary processes no longer needed. Keep requested review previews available and preserve pre-existing resources. Leave lasting work under `~/projects`, not in a temporary directory.
