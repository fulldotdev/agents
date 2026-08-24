# AGENTS.md

I'm Sil. I use agents for customer work, business operations, and software. I like ambitious ideas, simple systems, direct communication, and software that feels obvious. I prefer removing complexity to managing it. Here are some of my preferences, so we can be more aligned as we work together.

## General

- Never add or change this file without my explicit request.

## Communication

- Be extremely clear, consise, direct and willing to push back.
- Ask before destructive, irreversible, or privacy-sensitive actions.
- If you lack access or permission, do not guess. State the exact blocker and what I need to do.
- Prefer numbered lists when asking for feedback. Use bullet points for context.

## Environments

- Always use the machine's existing Chrome work profile for browser tasks on both MacBook and Otis.
- When the user asks to access a site, saved Chrome credentials and password-manager autofill may be used to sign in. Never reveal, copy, export, or change saved credentials, and never enter 2FA codes.
- We work on my personal Macbook and on a remote always-on Mac Mini named Otis.
- On Macbook, you can ssh into otis with `ssh -A otis`.
- Keep projects in `~/projects` and T3 Code's project list aligned on both machines. Sync project contents through Git, never through a cloud folder, and never overwrite uncommitted work.

## Skills

- Do not edit installed skills unless I explicitly ask. Local changes can block updates or be overwritten.
- Keep custom skills concise. Remove generic guidance, duplication, and detail that belongs in references or scripts.

## Coding

- Don't be scared to propose bold ideas if they can meaningfully benefit our work.
- Choose the simplest solution that works.
- KISS over DRY. Avoid over-engineering, over-optimizing, and over-abstracting.
- Stick to best practices according to docs and official guidance.
- Group files by file-type, not by feature. Avoid deep nesting, the flatter the better.
- Use kebab-case for all files and folders.
- Typesafety is useful, take advantage of it.
- `any` is the enemy. Inferred types are our friend. Our systems should adapt to changes, instead of requiring changes everywhere.
- If your TS code looks like a Python dev wrote it, it is bad TS code.
- Avoid one-line functions that are just casting wrappers.
- Write TypeScript in ways that Matt Pocock and Theo T3 would be proud of.
- If not already specified in project, I generally like to use the following tech:
  - For content-driven sites: Astro, Markdown with content-collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm
  - For webapps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, Tanstack libraries, Clerk or WorkOS when B2B/enterprise, Resend with React Email, Stripe, pnpm
  - We also build ecommerce in Shopify

# Sub/multi agents

- Do not spawn subagents or a multi-agent panel for work a single agent finishes in one pass. Delegation is for breadth or adversarial review, not for ordinary tasks.
- When several agents do work in parallel, state file ownership up front so they do not collide.

## Scope

- Questions, reviews, explanations, and diagnoses are read-only unless I ask for changes.
- Do not turn a small request into a cleanup, migration, redesign, or new system.
- For client work, staying within scope is especially important. If you see a scope creep, point it out.
- Do not add tests, logging, or analytics unless I explicitly, disucces or in scope. If you see a need for them, point it out.

## Visual taste

- Follow the existing design system, brand, source design, and product.
- Do not edit real components first.
- Avoid generic AI design, like overusing gradients, overlines, etc. Information-dense, no decorative card/pill chrome, no light-gray subtitle lines above sections. Minimal copy. No em dashes.
- Avoid continuously repainting CSS animations (pulse, shimmer, blur, spinners); they peg the GPU on high-refresh displays.

# Blast radius

- Never touch production, live databases, or daily-driver build/preview channels unless explicitly told to. When a task is adjacent to any of them, name what you are about to touch before touching it.

# Coding workflow

- Prefer working in one branch, with a commit per task.
- We usually work in preview, with the main branch being production.
- In Shopify we work on main directly, with production being published over CLI.
- Work local first. On complete tickets or features, always validate yourself through the browser as well if valueble. Give me back a link or links that are validated to preview your work.
