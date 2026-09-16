---
name: development
description: Always use when implementing, reviewing, verifying or releasing software in Sil's repositories, including previews, CMS and Shopify changes, and anything touching production.
---

# Development

Use the repository's instructions and existing framework skills for implementation details. Choose planning, tools, and implementation depth to fit the request.

## Stack and conventions

- Don't be scared to propose bold ideas if they can meaningfully benefit the work.
- Stick to best practices according to docs and official guidance.
- Follow existing project conventions. Otherwise, prefer kebab-case and shallow folders grouped by file type.
- Unless the project already specifies otherwise, Sil prefers:
  - Content-driven sites: Astro, Markdown with content-collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm
  - Webapps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, Tanstack libraries, Clerk or WorkOS when B2B/enterprise, Resend with React Email, Stripe, pnpm
  - Ecommerce in Shopify
- Work locally first and in preview by default, with the main branch being production. In Shopify, work on main directly and publish production over CLI, unless the project specifies a different workflow.

## Production and shared environments

Read-only inspection of production, live databases, and daily-driver build/preview channels is allowed. Changes require explicit authorization; name the target before changing it.

## Simplicity and scope

- Choose the simplest solution that works; prefer some duplication over unnecessary abstraction.
- Implement the requested outcome with the smallest complete change. Prefer existing components, dependencies, and direct code over new layers, packages, helpers, or configuration.
- Add an abstraction only when it removes real duplication or makes the current behavior clearer. Do not build for hypothetical future features.
- Avoid speculative fallbacks, redundant checks, comments that narrate obvious code, and boilerplate that adds no behavior. Preserve validation and error handling needed for real failure cases.
- Remove dead code and temporary scaffolding introduced by this task. Do not turn adjacent problems into a cleanup, migration, or redesign; report material out-of-scope issues separately.
- Review for both correctness and unnecessary complexity. Stop when the requested behavior works and the relevant checks pass.

Use `design` when the task involves visual or interaction decisions. Keep implementation details out of user-facing flows unless they help the user act or decide.

## Tests

Never create tests unless Sil explicitly asks for them. A request to build a feature, fix a bug, review code, or verify a change is not a request to add tests. This applies to unit, integration, end-to-end and regression tests, test fixtures, test infrastructure, and one-off scripts whose purpose is automated testing. Do not add or extend tests as an automatic part of implementation or reviewer feedback.

Run relevant existing tests, linting, type checks, builds, and browser checks when useful. Do not ask to add tests by default; raise it only when a specific unresolved risk makes that decision necessary. An explicit test or benchmark request authorizes the testing it describes.

## Work ownership

Continue in the existing checkout and branch by default. Sil prefers one branch with focused commits, not a worktree per task. Check actual Git state when resuming; thread metadata can be stale. If another implementation is using the checkout, coordinate or use an explicitly agreed isolated checkout rather than switching its branch or mixing changes.

Use `work-management` for tracking and Notion routing. Use `t3-code` when dispatching work through T3; local reviewer sub-agents do not need their own T3 threads or Notion Tasks.

## Local review

For substantive code changes, use an independent local Astra reviewer sub-agent before handoff. Give it the request, applicable repository instructions, and the actual diff or PR branch, with access to relevant surrounding code. Its assignment is read-only: identify concrete defects, regressions, missed requirements, and consequential maintainability issues, with a location and explanation. Cosmetic preferences alone are not findings.

Evaluate its findings and fix relevant issues within scope. Recheck affected behavior after fixes; another review is useful when the fixes materially change the code. A review is not a requirement to create a PR, new tests, or a review report file. Tiny copy or formatting changes do not need a reviewer.

## Reviewable delivery

Creating, updating, deleting or publishing a Shopify theme requires Sil's explicit authorization for that Shopify action and target, including development and unpublished themes. Permission for local/GitHub work or preview review does not grant permission to change Shopify themes. Check connected-theme effects before pushing or merging GitHub branches; `shopify theme dev` also uploads to Shopify.

Use existing Shopify previews read-only unless theme writes are authorized. For an authorized preview deployment, prefer `shopify theme dev`; create a theme-library draft only when its creation is authorized.

Our CMSes are CloudCannon, Sanity, and Shopify. Use their existing skills for implementation details. For CMS changes, verify the affected editing experience as well as the rendered page: CloudCannon's configured editor, Sanity Studio, or Shopify's theme editor and relevant custom-data fields. Use the project's authorized development environment; test only the editing surfaces the change affects.

Give Sil a validated preview when the change has a reviewable UI, with what to inspect and any access or lifetime limitation. On Otis, localhost alone is not a cross-device review link. State relevant verification, unresolved issues, and whether the work is committed, pushed, or released; do not imply that one establishes another.

Close task-created research and validation tabs and stop temporary processes no longer needed. Keep requested review previews available and preserve pre-existing resources. Leave lasting work under `~/projects`, not in a temporary directory.
