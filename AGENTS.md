# AGENTS.md

## General
- Ask before destructive, irreversible, or privacy-sensitive actions
- When you lack permission, say so. Do not guess.
- When login, authentication, permissions, or another user-fixable blocker stops work, notify the user immediately with the exact blocker and the action needed to continue.
- When updating skills or instructions after something went wrong, first remove or tighten the line that caused it before adding override rules.
- Avoid unnecessary negative rules; they can draw attention to the wrong action and create confusion.

## Communication
- Be critical and concrete; push back
- Prefer numbered lists, especially when asking for feedback.
- Customer drafts: use the `customer-communication` skill

## Tools
- Use `work-management` when the user references our Tasks, Projects, Customers, Sprints, Someday, Goals, Insights, Meetings, triage, planning, agency admin, or Productive/Moneybird coordination
- Use `work-execution` when implementing, QAing, previewing, releasing, or handing off scoped work
- Apply its customer branch to customer-owned, customer-visible, or promised delivery
- Use `notion` for Notion API/CLI mechanics
- Use `moneybird` for estimates, invoices, recurring billing, and Moneybird records
- On Otis, use the Chrome profile at `~/.hermes/browser-profiles/otis` for authenticated browser work in both Hermes and T3/Codex. Use T3's in-app browser for public pages and local development.
- Reuse or open a task tab in the Otis profile and close task-created tabs when the work is complete.

## Development
- In a new dev session, check `git status` first; pull latest only when the worktree is clean and there are no open local changes.
- Reuse a responsive project dev server when available. Otherwise start the project's normal dev command and keep it running for the thread. Return the local URL.
- Follow repository-specific branch rules. Otherwise continue the current task branch; use `preview` for normal work when available and `main` for production. On Teveo/Fayn Shopify projects, default to `main`.
- Only use worktrees when user specifically asks for them.
- Verify through the relevant local or preview environment; when done, provide URL(s).
- For Netlify projects, use the repository-linked Netlify site; verify `.netlify/state.json` matches the repo's real site before deploys or preview URLs.
- For visual changes, validate with screenshots in the target environment and iterate until the screenshot matches the intended result.
