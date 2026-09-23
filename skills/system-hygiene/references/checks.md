1. **Skills and instructions.** Check the custom skills in `~/.agents/skills` against `~/.agents/global/references/writing-skills.md` and propose fixes for what drifted. Check that links between skills and references resolve, commands still match the installed tools, and no `__pycache__`, empty folders, or stray files sit inside a skill. Installed skills update through their own path, not local edits.

2. **Files and storage.** Measure free space and growth. Look at large temporary files, downloads, trash, caches, and old backups. For each deletion candidate, say what it is for and whether it can be recovered. Report reclaimable space; APFS clones and hard links make it smaller than folder size.

3. **Worktrees and leftovers.** Agents may create worktrees but rarely clean them up. List extra worktrees with `git worktree list --porcelain` on both machines, including those outside `~/projects`. Prune registrations whose folder is gone. For the rest, check for uncommitted files and commits not on the target branch, then propose `git worktree remove` for those whose work landed or was dropped. Also look for abandoned generated output and temporary copies of projects.

4. **Previews and processes.** Find local servers, editor processes, and tunnels that look abandoned. Match each to its project and owner before proposing a shutdown. A `dist` or cache directory may power a preview used daily.

5. **Automations.** Compare `openclaw cron list` and the launchd plists on Otis with `~/.agents/global/references/otis.md`. Flag one-off jobs that ran or expired, duplicates, disabled leftovers, and jobs with recent failures. Do not rerun jobs. Some system-owned jobs cannot be removed through the CLI; leave those.

6. **CLI tooling.** Compare installed and running versions across both Macs for the agent setup: T3 desktop app, CLI and servers, Codex, Claude Code, CLIProxyAPI, OpenClaw, OpenCode, Tailscale, wacli, gh, Node, Python, bun, gog, resend, poppler, flyctl, gcloud, and the npm globals on Otis (netlify-cli, mcporter, ntn, Stripe, Dex, pnpm, npm). Look for stale shims and competing installs. After an OpenClaw update run `openclaw doctor`. Recommend a coordinated update when versions drift; review alone does not install or restart anything.

7. **Sync and Git.** Compare shared skill and instruction commits across both Macs. Find uncommitted or unpushed work that may be forgotten. Compare T3 project registrations on both machines against [project setup](../../t3-code/references/setup.md); check archived threads before proposing removal of a stale entry.

8. **Apps, plugins, and models.** Monthly, look for duplicate or superseded installs and large downloads or models. State the saving and the effect on work. An admin-password prompt means the user must act.
