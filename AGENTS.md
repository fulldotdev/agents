# AGENTS.md

I'm Sil. I use agents for customer work, business operations, and software. I value ambitious ideas, simple systems, direct communication, and software that feels obvious. I prefer removing complexity to managing it. These preferences help us stay aligned.

## General

- Never add or change this file without my explicit request.

## Communication

- Be extremely clear, concise, direct, and willing to push back.
- Ask before destructive, irreversible, or privacy-sensitive actions.
- If you lack access or permission, do not guess. State the exact blocker and what I need to do.
- Prefer numbered lists when asking for feedback. Use bullet points for context.

## Environments

- We work on my personal MacBook and a remote, always-on Mac mini named Otis.
- On Otis, use `~/.hermes/browser-profiles/otis` for authenticated browser work.
- On MacBook, SSH into Otis with `ssh -A otis`.
- Keep `~/projects` and T3 Code's project list aligned on both machines. Sync project contents through Git, never through a cloud folder. Never overwrite uncommitted work.
- Shared video files live in `~/Google Drive/My Drive/Video Edits/{inbox,review,final}` on both machines. Keep jobs and caches local. Copy approved reviews and finals into Drive for automatic sync.

## Skills

- Do not edit installed skills unless I explicitly ask. Local changes can block updates or be overwritten.
- Keep custom skills concise. Remove generic guidance, duplication, and detail that belongs in references or scripts.

## Coding

- Propose bold ideas when they can meaningfully improve our work.
- Choose the simplest solution that works.
- KISS over DRY. Avoid over-engineering, over-optimizing, and over-abstracting.
- Follow official docs and established best practices.
- Group files by file type, not by feature. Avoid deep nesting. Flatter is better.
- Use kebab-case for all files and folders.
- Use type safety.
- `any` is the enemy. Prefer inference. Systems should adapt to changes without requiring edits everywhere.
- If your TS code looks like a Python dev wrote it, it is bad TS code.
- Avoid one-line functions that are just casting wrappers.
- Write TypeScript in ways that Matt Pocock and Theo T3 would be proud of.
- When a project does not specify a stack, I prefer:
  - Content-driven sites: Astro, Markdown with content collections, Tailwind, shadcn/ui, fulldev/ui, React, Zod, pnpm
  - Web apps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, TanStack libraries, Clerk or WorkOS for B2B or enterprise, Resend with React Email, Stripe, pnpm
  - E-commerce: Shopify

## Multi-agent work

- Do not spawn subagents or a multi-agent panel for work a single agent finishes in one pass. Delegation is for breadth or adversarial review, not for ordinary tasks.
- When several agents do work in parallel, state file ownership up front so they do not collide.

## Scope

- Questions, reviews, explanations, and diagnoses are read-only unless I ask for changes.
- Do not turn a small request into a cleanup, migration, redesign, or new system.
- For client work, staying within scope is especially important. Point out scope creep.
- Do not add tests, logging, or analytics unless requested or already in scope. Point out when they would help.

## Visual taste

- Follow the existing design system, brand, source design, and product.
- Do not edit real components first.
- Avoid generic AI design: excessive gradients, overlines, decorative cards or pills, and light-gray subtitle lines above sections. Prefer dense information, minimal copy, and no em dashes.
- Avoid continuously repainting CSS animations (pulse, shimmer, blur, spinners); they peg the GPU on high-refresh displays.

## Blast radius

- Never touch production, live databases, or daily-driver build or preview channels unless explicitly told. When a task is adjacent to them, state exactly what you will touch first.

## Coding workflow

- Prefer one branch and one commit per task.
- We usually work in preview. The main branch is production.
- In Shopify, work directly on main and publish production through the CLI.
- Work locally first. For completed tickets or features, validate through the browser when applicable and return validated preview links.
