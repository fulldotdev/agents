---
name: cloudcannon
description: Use the CloudCannon CLI to inspect organizations, sites, build and sync logs, diagnose failures, trigger rebuilds, update build settings, or manage CloudCannon site files. Prefer the CLI over browser work when it supports the requested operation.
---

# CloudCannon CLI

Use the official `cloudcannon` CLI for CloudCannon platform work.

Official documentation: https://cloudcannon.com/documentation/developer-reference/cli/

## Setup and authentication

Check the installed version before use:

```bash
cloudcannon --version
```

The official package is `@cloudcannon/cli` and requires Node.js 24 or newer. Do not install or upgrade global packages unless the user authorizes the system change.

Authenticate each machine separately with:

```bash
cloudcannon login
```

The login flow creates a personal Access Key named `CloudCannon CLI` with the user's CloudCannon permissions and stores it for that machine. Never copy stored credentials between machines or print authorization codes, Access Key IDs, or secrets. Use `cloudcannon logout` to remove local credentials. Revoke an Access Key from CloudCannon Account Settings when access should end or a credential may be exposed.

## Safe inspection

CloudCannon list commands can return large records containing billing and account metadata. Filter output to the fields needed for the task. Do not paste complete organization or site records into chat.

Useful read-only commands:

```bash
cloudcannon orgs list
cloudcannon sites list
cloudcannon sites get --site=<name|id|uuid|domain>
cloudcannon sites builds list --site=<name|id|uuid|domain>
cloudcannon sites print-last-build --site=<name|id|uuid|domain>
cloudcannon sites print-last-failed-build --site=<name|id|uuid|domain>
cloudcannon sites print-last-sync --site=<name|id|uuid|domain>
cloudcannon sites print-last-failed-sync --site=<name|id|uuid|domain>
```

For compact site discovery:

```bash
cloudcannon sites list | jq '[.[] | {
  uuid,
  site_name,
  domain_name,
  branch: .storage_provider_details.branch,
  last_compiled,
  last_compiled_success
}]'
```

Site names may occur more than once for preview and production branches. Before any write, resolve the exact site and confirm its UUID, repository branch, domain, and build configuration. Use the UUID for the write command.

## Diagnosing failed builds

Start with `print-last-failed-build`. If several sites failed around the same time, compare their logs before changing individual repositories. Check for a shared package registry, runtime, dependency, install-command, or CloudCannon platform failure. Use `print-last-failed-sync` when the build log points to repository synchronization.

Reading logs and settings does not authorize a rebuild or configuration change.

## Changes

These commands change external state:

- `cloudcannon sites rebuild`
- `cloudcannon sites create`
- `cloudcannon sites update-build-config`
- `cloudcannon sites files upload|move|clone|delete|restore|discard|commit`

Immediately before running one, state the exact site UUID, branch, domain, and effect. Get explicit user approval when the command affects production, a daily-driver preview, published content, repository files, build settings, or consumes a build. Never use a matching site name as proof that the target is correct.

After an authorized change, read the resulting site or build state and report whether it succeeded. Do not retry a failed mutation repeatedly without diagnosing the failure.
