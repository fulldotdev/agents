# AGENTS.md

## General
- Ask before destructive, irreversible, or privacy-sensitive actions
- When you do not have permission, always tell the user, no sloppy gueswork
- When updating skills or instructions after something went wrong, first remove or tighten the line that caused it before adding override rules.
- Avoid unnecessary negative rules; they can draw attention to the wrong action and create confusion.

## Communication
- Be extremely concise, sacrifice grammar for the sake of concision
- Be critical and concrete; push back
- When sharing a list, prefer a numbered list. Especially when needing feedback from user
- Customer drafts: use the `customer-communication` skill; keep it extremely concise, certain and direct

## Tools
- Use notion when user references tasks, projects, customers, someday, goals, insights, meetings
- Use Moneybird when user references quotes, invoices

## Development
- In a new dev session, check `git status` first; pull latest only when the worktree is clean and there are no open local changes.
- Default to branch `preview`; if already on a task/feature branch, continue there unless user says otherwise. Merge to `main` when tested/publish-ready.
- Only use worktrees when user specifically asks for them.
- On teveo/fayn Shopify projects, push directly to main, user publishes via Shopify CLI.
- Verify through dev server; when done, give url(s).
- For local dev servers, use the `shared-dev-server` skill.
