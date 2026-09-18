1. **Skills and instructions.** Check the custom skills in `~/.agents/skills` against `environment/references/writing-skills.md` and propose fixes for what drifted. Also check that links between skills and references resolve, commands still match the installed tools, and no `__pycache__`, empty folders, or stray files sit inside a skill.
   Installed skills update through their own path, not local edits. Shared conventions belong in `~/.agents`, project instructions in their repositories.

2. **Files and storage.** Measure free space and meaningful growth. Look at large temporary files, downloads, trash, caches, and old backups. For each deletion candidate, say what it is for and whether it can be recovered. `~/Library` holds settings and app data, not cache. Report reclaimable space, which APFS clones and hard links make smaller than folder size.

3. **Projects.** Look for abandoned generated output, temporary copies, and stale checkouts. Read Git status, worktree ownership, and process use. Keep uncommitted files and unique commits. A Git bundle can keep unique history when removal is approved separately. pnpm already shares package data, so do not propose deduplication. `.dev` can hold source and review work.

4. **Previews and processes.** Find local servers, editor processes, and tunnels that look abandoned. Match each to its project, output path, and owner before proposing a shutdown. A `dist` or cache directory may power a preview used daily.

5. **Automations.** Compare `openclaw cron list` and the launchd plists on Otis with `environment/references/otis.md`. Flag one-off jobs that ran or expired, duplicates, disabled leftovers, and jobs with recent failures, and propose deleting them. Do not rerun jobs or rebuild a workflow as maintenance. Some system-owned jobs cannot be removed through the CLI; leave those.

6. **CLI tooling.** Compare command resolution, installed versions, and dependencies across both Macs. Look for stale shims and competing installs. Different Node versions or machine-specific tools are fine unless they cause a problem. Use each machine's own package manager. Credentials and machine config stay local.

7. **Sync and Git.** Compare shared skill and instruction commits across both Macs. Find uncommitted or unpushed work that may be forgotten. Tell intentional divergence apart from active work before suggesting a sync.

8. **Apps, plugins, and models.** Monthly, look for duplicate or superseded installs and large downloads or models. State the saving and the effect on work. An admin-password prompt means the user must act; do not bypass macOS.
