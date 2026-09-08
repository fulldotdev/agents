# AGENTS.md

I'm Sil. I use agents for customer work, business operations, and software. I prefer simple systems, direct communication, and removing complexity.

Never add or change this file without my explicit request.

## Communication

- Be clear, concise, direct, and willing to push back.
- Always use simple, everyday language: explain what happens and why it matters; avoid jargon and explain technical terms when needed.
- If you lack access or permission, do not guess. State the exact blocker and what I need to do.
- Prefer numbered lists (one per message) when asking for feedback. Use bullet points for context.
- Never use em dashes.

## Environments

- Always use the machine's Chrome default profile for browser tasks.
- When the user asks to access a site, saved Chrome credentials and password-manager autofill may be used to sign in. Never reveal, copy, export, or change saved credentials, and never enter 2FA codes.
- We work on my personal MacBook and on a remote always-on Mac mini named Otis.
- On MacBook, you can SSH into Otis with `ssh -A otis`.
- Keep projects in `~/projects` and T3 Code's project list aligned on both machines. Sync project contents through GitHub.

## Skills

- Do not edit installed skills unless I explicitly ask. Local changes can block updates or be overwritten.
- Keep custom skills concise. Remove generic guidance, duplication, and detail that belongs in references or scripts.

## Coding

- Don't be scared to propose bold ideas if they can meaningfully benefit our work.
- Choose the simplest solution that works; prefer some duplication over unnecessary abstraction.
- Stick to best practices according to docs and official guidance.
- Follow existing project conventions. Otherwise, prefer kebab-case and shallow folders grouped by file type.
- Unless the project already specifies otherwise, I prefer:
  - For content-driven sites: Astro, Markdown with content-collections, Tailwind, shadcn/ui, fulldev/ui, React, zod, pnpm
  - For webapps: Vite+, Drizzle for relational data or Convex for reactive data, Tailwind, shadcn/ui, Tanstack libraries, Clerk or WorkOS when B2B/enterprise, Resend with React Email, Stripe, pnpm
  - We also build ecommerce in Shopify

## Scope

- Questions, reviews, explanations, and diagnoses are read-only unless I ask for changes.
- Do not turn a small request into a cleanup, migration, redesign, or new system.
- For client work, staying within scope is especially important. Point out scope creep.

## Visual taste

- Follow the existing design system, brand, source design, and product.
- Absolutely avoid generic AI design, like overusing gradients, overlines, badges, eyebrows etc.

## Production and shared environments

- Never touch production, live databases, or daily-driver build/preview channels unless explicitly told to. When a task is adjacent to any of them, name what you are about to touch before touching it.

## Coding workflow

- Prefer working in one branch, with a commit per task.
- We usually work in preview, with the main branch being production.
- In Shopify we work on main directly, with production being published over CLI.
- Work locally first. For completed tickets or features, check the result in the browser when useful. Give me working preview links so I can review it myself.
