# Chrome connections

The browser preference is in the `browser` skill. This reference covers the integration details that differ by harness. Keep credentials and machine configuration out of the shared skills repository.

## Codex, including Codex inside T3

Use the installed official Chrome plugin through the persistent `node_repl` tool. The tool may be exposed as `mcp__node_repl__js`; discover it before declaring browser control unavailable. The working T3 setup uses this integration directly.

Find the installed `chrome` plugin in the current user's Codex plugin cache. Prefer its `latest` path, not a version copied from another machine. Read its skill if supplied. The installed runtime can initialize and report its own supported API:

```js
const browserRuntime = await import('/absolute/path/to/chrome/latest/scripts/browser-client.mjs');
const agent = await browserRuntime.setupBrowserRuntime();
nodeRepl.write(await agent.browsers.list());
```

Select the returned `extension` browser with `family: 'chrome'` and `profileName: 'sil@full.dev'`. Do not hardcode a browser ID. Read `await browser.documentation()` before controlling tabs, then call `await browser.nameSession('🔎 Short task name')`.

Use `browser.tabs.new()` for task tabs. To use an existing user tab, find it through `browser.user.openTabs()` and pass the returned object to `browser.user.claimTab()`. Reuse the browser and tab handles while valid. Follow the runtime's handoff and deliverable rules so pages waiting for the user remain open.

If browser discovery is empty or connection fails, check the ChatGPT Chrome extension in the correct Chrome profile and its native messaging host. Installation on disk alone does not prove a live connection. A missing `node_repl` tool requires fixing the provider's tool configuration or opening a fresh session, not using the terminal to imitate the browser runtime. Do not rewrite application-managed runtime paths from a remembered version.

Chrome may deny automation on its Web Store or internal pages. Hand those setup steps to the user; do not bypass the restriction.

## Claude Code, including Claude inside T3

Use the official Claude in Chrome extension in the same `sil@full.dev` Chrome profile. It provides its own browser tools and session tab group. It does not use Codex's proprietary runtime.

Claude Code needs a direct Claude account signed in through `/login`. API keys and `claude setup-token` are not sufficient for this integration. Start with `claude --chrome`, then use `/chrome` to select the connected browser and check for `Status: Enabled` and `Extension: Installed`. Enable Chrome by default through that menu when configuring standalone Claude Code.

In T3, add `--chrome` to the Claude provider instance's launch arguments. Check that instance's configured home and account, since it can differ from standalone Claude. The Claude account must match the account signed into the Chrome extension; the Chrome profile's email alone does not establish this. If the browser list is empty, check this match before asking for another Connect attempt. A fresh provider session may be needed to load the flag and browser tools. An installed extension is not proof that a T3 Claude session can control it; verify the connection there.

On macOS, `claude auth status` over SSH can report signed out when Keychain access requires user interaction. If a login was just completed, check the exact instance and Keychain accessibility before asking the user to repeat it. Error `-25308` means interaction is not allowed, not that credentials are absent. Verify through the running T3 provider when possible; do not export credentials or weaken Keychain permissions.

The user has chosen automatic same-machine routing. Claude stores its native browser choice in `chromeExtension.pairedDeviceId` and `chromeExtension.pairedDeviceName` in its configuration JSON (`~/.claude.json` for standalone; `<configured-home>/.claude.json` for a T3 instance). Keep standalone and T3 paired to that machine's verified Chrome extension. These IDs are machine configuration, not shared-skill constants. The built-in connection reuses a saved pairing across fresh sessions; no custom bridge or repeated Connect prompt is needed.

Before the first page action, compare `list_connected_browsers` with the saved pairing. Use the matching saved device automatically; the user has already chosen it. Do not infer the machine from list order, generic names, `isLocal`, or `onThisComputer`. If the paired device is absent, stop with a connection error instead of using another connected browser. Ask for a new pairing only when the saved choice is missing or no longer valid, such as after reinstalling the extension. Use the built-in confirmation screen to establish that new mapping.

If the extension cannot connect, use `/chrome` to reconnect. Claude creates its own native messaging host during setup. Chrome may need a restart after first installation; preserve active work and let the user choose when to restart.

Official documentation: https://code.claude.com/docs/en/chrome

## OpenClaw on Otis

Use OpenClaw's `browser` tool with profile `chrome`, backed by the OpenClaw extension in Otis's existing `sil@full.dev` Chrome profile. For diagnostics:

```bash
openclaw browser status --browser-profile chrome --json
openclaw browser extension status --json
openclaw browser tabs --browser-profile chrome --json
```

The default is `browser.defaultProfile: "chrome"`. The expected driver is `extension`, with `running`, `cdpReady`, and `pageReady` true. Agent-created tabs belong to the OpenClaw group. Keep separate tabs for separate jobs and target the exact tab ID.

Do not switch to the isolated `openclaw` profile or the separate `user` existing-session driver to recover a failed extension connection. The `user` driver is a different Chrome MCP transport, not Codex's ChatGPT Chrome extension. The presence of several browser drivers does not mean their sessions or permissions are interchangeable.

Otis keeps working in its own Chrome while the MacBook is away. Its cookies are local to Otis. A task on MacBook does not give an Otis agent access to MacBook Chrome. Any future remote-browser bridge should be an explicit setup, not an automatic fallback.

### Access failures

On Otis, OpenClaw uses the `chrome` extension connection. Check `openclaw browser status --json` and `openclaw browser extension status --json`. A failing extension connection is no reason to switch to another profile or enable Chrome Remote Debugging.

`Target identities are unavailable` means a Chrome Web Store tab blocked tab enumeration during setup. Close it if it belongs to this task, then retry. Leave the user's tabs alone.

`browser_consent_required`, `consumer_profile_endpoint_requires_grant`, or an approval popup you cannot find means connection approval is blocked. Report the exact blocker and the machine. If the fix is unknown, say so instead of inventing one.

See [Otis](../../../references/otis.md) and https://docs.openclaw.ai/tools/chrome-extension.

## T3 embedded browser

Set `enableAgentBrowserAccess: false` in the owning environment's T3 server settings. This disables T3 preview automation and its browser-routing instructions for new provider sessions; it does not disable the native Chrome extensions or remove the user's Browser panel. Existing sessions may retain their earlier tools until restarted.

Check for per-project overrides when enabling a new project. Keep the setting disabled on both MacBook and Otis. Do not disable the entire `t3-code` MCP server manually: it also serves unrelated thread features. Use T3's supported setting and leave the application bundle intact.
