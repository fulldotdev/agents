# AGENTS.md

## General
- Ask before destructive, irreversible, or privacy-sensitive actions
- When you do not have permission, always tell the user; no sloppy guesswork.
- When updating skills or instructions after something went wrong, first remove or tighten the line that caused it before adding override rules.
- Avoid unnecessary negative rules; they can draw attention to the wrong action and create confusion.

## Communication
- Be critical and concrete; push back
- When sharing a list, prefer a numbered list. Especially when needing feedback from user
- Customer drafts: use the `customer-communication` skill

## Tools
- Use `work-management` when the user references our Tasks, Projects, Customers, Sprints, Someday, Goals, Insights, Meetings, triage, planning, agency admin, or Productive/Moneybird coordination
- Use `customer-work` when executing, QAing, previewing, reviewing, releasing, or handing off scoped customer work
- Use `notion` for Notion API/CLI mechanics
- Use Moneybird for estimates, invoices, recurring billing, and Moneybird records

## Development
- In a new dev session, check `git status` first; pull latest only when the worktree is clean and there are no open local changes.
- Follow repository-specific branch rules. Otherwise continue the current task branch; use `preview` for normal work when available and `main` for production. On Teveo/Fayn Shopify projects, default to `main`.
- Only use worktrees when user specifically asks for them.
- Verify through the relevant local or preview environment; when done, provide URL(s).
