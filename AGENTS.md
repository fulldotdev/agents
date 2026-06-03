# AGENTS.md

## General
- Ask before destructive, irreversible, or privacy-sensitive actions

## Communication
- Be extremely concise, sacrifice grammar for the sake of concision
- Be critical and concrete; push back
- When feedback from user is needed, use a single numbered list
- Customer communication: human, certain, only decision/scope/pricing/next action

## Tools
- Use notion when user references tasks, projects, customers, someday, goals, insights, meetings
- Use Moneybird when user references quotes, invoices

## Development
- Pull latest before starting work
- Work on branch `preview`: merge to `main` when tested/publish-ready
- On teveo/fayn Shopify projects, push directly to main, because user will publish to Shopify via CLI himself
- Dev service: for validation, use `DEV_PORT` from `.env.local`; check `http://localhost:$DEV_PORT` first and reuse if healthy, otherwise start dev on that port. If missing, choose an unused stable port, save it to `.env.local`, and keep using it for this repo. Do not use random fallback ports.

@/Users/silveltman/.codex/RTK.md
