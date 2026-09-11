# OpenClaw verification, 11 September 2026

Historical test evidence. Use [the operations guide](../openclaw-otis.md) for current configuration and recovery steps.

## Migration verification, 11 September 2026

- 54 weekplanning and 60 triage tests passed, with independent Astra review.
- Native Codex turns reported `agentHarnessId: codex` and executed native terminal and `node_repl` tools.
- A silent native cron test completed with `NO_REPLY`; its one-shot job was removed automatically.
- The migrated WhatsApp watchdog completed with exit 0 and no output or message.
- All three channels reconnected after a managed gateway restart. Eight jobs retained their next-run times; the triage watchdog passed with existing pending/deferred state preserved.
- T3's authenticated helper still listed its 57 threads. The independent transcription environment imported faster-whisper 1.2.1.
- Computer Use diagnosis corrected after inspecting `operator_approvals`: the Chrome requests were rejected by OpenClaw with `terminal_reason: no-route`, not a demonstrated missing macOS permission. Plugin approval forwarding is now configured for agent `main` to Sil's private Telegram chat. Sil subsequently authorized the Chrome approval, which was resolved through the official OpenClaw CLI (`allow-always`). The native Codex fixture test then successfully typed `native-codex-ok`, clicked Verify and captured the visible result; the screenshot was independently inspected. The temporary tab and fixture server were closed. Telegram approval delivery also succeeded on this run. Evidence: `/Users/otis/.openclaw/validation/native-codex-ok-screenshot.jpeg`, native session `migration-native-ui-approved`. This validates Chrome control for the tested session; new apps or session-scoped permissions can still require their own approval.
- MacBook's older duplicate `.codex/skills/social-posts` was archived under `~/backups/openclaw-migration-20260911`; canonical `.agents/skills/social-posts` remains.

## Native runtime update, 11 September 2026

- Official ChatGPT/Codex desktop 26.908.31748 (build 8720) is installed on both Macs; OpenAI signing was verified. Codex CLI is 0.154.0 on both machines; the desktop bundles 0.154.0-alpha.6.1.
- Otis T3 service and CLI are 0.0.41-nightly.20260911.1533. The MacBook desktop runs the same release after a verified update and automatic resumption of this maintenance thread; its restart is tracked in `~/backups/codex-native-cleanup-20260911/t3-restart.log`.
- MacBook native `cua_repl` opened a fixture in the default Chrome profile, typed `native-codex-ok`, clicked Verify and captured the visible result. Native Chrome app state was also readable.
- Otis OpenClaw native `cua_repl` passed the same browser test. The terminal receipt confirms requested/effective/response model `gpt-6-astra`, `agentHarnessId: codex`, and no rerouting. Screenshot: `~/.openclaw/validation/updated-cua-browser.png`.
- Otis native desktop input/click and screenshots also passed after Sil unlocked the console, producing `native-codex-desktop-ok`. The same app returned `cgWindowNotFound` while locked, whereas Chrome extension control worked. The official authorization plugin for Locked use is installed, but locked desktop control through T3/OpenClaw remains unverified. OpenAI documents Locked use specifically for active trusted turns from connected devices; no bypass is configured.
- Hermes history remains readable after archival, all eight enabled cron jobs retain next-run times, and the triage watchdog passes with 44 deferred items and no pending batch.
- MacBook's unused older `/Applications/Codex.app` was archived as a verified ZIP outside Applications. Previous desktop bundles and configuration backups are retained under `~/backups/codex-native-cleanup-20260911`.
- After the MacBook T3 restart, the original maintenance thread directly called `mcp__cua_repl.js` and passed Chrome create/type/click/screenshot verification (`t3-native-cua-ok`). The temporary tab was closed.
- The previously failing Otis VDA T3 thread subsequently completed native `cua_repl` browser interactions, including mobile sidebar opening/closing and navigation-menu verification. Customer work continued in its own thread.
- Otis Locked use is registered in macOS: `system.login.screensaver` references `com.openai.sky.CUAService.AuthorizationPlugin.remote`. Registration alone did not make the tested standalone/native T3/OpenClaw desktop calls work while locked. Keep that limitation separate from the verified locked Chrome-extension operation.
- Follow-up inspection distinguished two Chrome instances. The obsolete `com.otis.hermes-sil-work-browser` ran a separate `.hermes/browser-profiles/otis` profile with remote debugging on port 9223. It has now been booted out; the label and port are gone. The ordinary default-profile Chrome process was preserved.
- Three obsolete T3 runtime installations and unused alternate-browser/ClawHub/old-ACP npx caches were removed. Current T3 and its immediate previous release remain. Otis had approximately 3.9 GiB free after this cleanup. Customer workspaces and archived history were retained.
- Final native OpenClaw/Astra validation after cleanup passed Chrome type/click/screenshot twice, including `locked-browser-ok` while `ioreg` reported both `IOConsoleLocked` and `CGSSessionScreenIsLocked`. Native desktop access still returned `-10005: cgWindowNotFound`. The Mac was already locked when the test inspected it, so no lock shortcut or unlock attempt was performed. Both owned tabs and the fixture server were closed. Evidence: `~/.openclaw/validation/cleanup-native-locked-browser.png`, session `native-cua-cleanup-final-20260911`. The terminal receipt confirms Codex, `gpt-6-astra`, `cua_repl.js`, and no rerouting.
- OpenAI documents automatic unlock as an active trusted ChatGPT turn from a connected device, not general permission for other local processes. The native harness and official `cua_repl` alone do not establish that trust context. Locked desktop operation remains blocked on this T3/OpenClaw route; Chrome extension operations and shell work do function while locked. Reference: <https://learn.chatgpt.com/docs/computer-use#locked-use>.

## Telegram steering verification

- Verified with four updates during a native Codex tool call: one combined final answer, `rood, blauw, groen, geel`. The installed inbound debouncer, using the actual Telegram configuration, independently produced one FIFO batch 2002 ms after the last of four inputs. The transport itself was not tested by sending messages to Telegram.
