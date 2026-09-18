---
name: browser
description: Always use when using the browser or computer, or signing in to sites.
---

# Browser

- Use the user's existing Google Chrome profile signed in as `sil@full.dev` on the current machine. The user wants to see the work, take over easily, and reuse existing logins. This includes local development checks. Use T3's embedded browser or a separate browser profile only when the user explicitly requests it.
- Use the native Chrome integration for the current harness: Codex's Chrome runtime through `node_repl`, Claude in Chrome for Claude Code, and the `chrome` extension profile for OpenClaw. Read [Chrome setup](references/chrome.md) when connecting, troubleshooting, or configuring these integrations. An empty list of browser-named tools does not prove Chrome is unavailable.
- Give each thread a clearly named tab group where the integration supports it. Create task tabs there; claim an existing user tab only when relevant to the request. Close the tabs you opened when you are done. Leave other agents' groups alone and do not have two agents control the same tab.
- Inspect the visible page, use the integration's supported clicks, typing, and mouse/keyboard actions, then check the result. Follow its current guidance for accessibility, page locators, and screenshots. Do not replace a requested browser workflow with hidden API calls or page-state mutations.
- Reuse website sessions in this profile. Open login pages in that same browser and let the user take over for passwords that are not saved, 2FA, passkeys, or CAPTCHAs. Saved autofill is allowed for an authorized login. Never reveal, copy, export, or change saved credentials or session cookies.
- If Chrome is unavailable, report the missing connection and the machine. Do not silently switch profiles, browsers, machines, or route Codex/Claude through OpenClaw. MacBook and Otis have separate website sessions.
