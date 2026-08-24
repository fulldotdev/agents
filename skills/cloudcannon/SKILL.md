---
name: cloudcannon
description: Use CloudCannon's official CLI to configure, validate, and preview local projects or inspect and manage Organizations, Sites, Builds, syncs, inboxes, and site files. Also use for editable regions and snippet configuration. Prefer the CLI; use the SDK or REST API only for code integrations or operations the CLI does not support.
---

# CloudCannon

Use the official `cloudcannon` CLI for local project work and CloudCannon platform operations.

Official references:

- CLI: https://cloudcannon.com/documentation/developer-reference/cli/
- Site configuration: https://cloudcannon.com/documentation/developer-reference/configuration-file/
- Editable Regions: https://cloudcannon.com/documentation/developer-reference/editable-regions/
- Snippets: https://cloudcannon.com/documentation/developer-reference/configuration-file/types/_snippets/
- SDK: https://cloudcannon.com/documentation/developer-reference/sdk/
- REST API: https://cloudcannon.com/documentation/developer-reference/api/

## Tool choice

- Use the CLI for terminal work, scripts, and CI when it supports the operation.
- Use `@cloudcannon/sdk` for a server-side TypeScript integration or a repeated workflow that benefits from typed resources, pagination, sorting, or filtering.
- Call the REST API directly only when the CLI and SDK do not fit, such as another programming language or an uncovered endpoint. The REST API is versioned under `/api/v0/`, so verify the current OpenAPI specification before implementing against it.
- The Visual Editor API is separate from the platform REST API. Use Editable Regions for normal inline editing. Use the Visual Editor API only for custom integrations that run inside the editor.

## Setup and authentication

Check the installed CLI and relevant command help before use:

```bash
cloudcannon --version
cloudcannon <command> --help
```

The official package is `@cloudcannon/cli` and requires Node.js 24 or newer. Do not install or upgrade global packages unless the user authorizes the system change.

`configure`, `validate`, and `dev` operate on local files and do not require authentication. Remote commands require one of these methods:

- Interactive work: `cloudcannon login`
- Organization-scoped automation: `CLOUDCANNON_API_KEY`
- Personal automation: `CC_ACCESS_KEY_ID` and `CC_ACCESS_KEY_SECRET`

Prefer an Organization API Key for CI or server-to-server automation. Use a personal Access Key only when the workflow intentionally needs that user's permissions. Never print, copy between machines, or commit credentials. Use `cloudcannon logout` to remove local credentials and revoke exposed or obsolete keys in CloudCannon.

## Configure and validate a project

Work from the project root. Inspect the existing build scripts, output directory, content model, and CloudCannon files before generating or changing configuration.

Useful discovery and generation commands:

```bash
cloudcannon configure detect-ssg
cloudcannon configure detect-source
cloudcannon configure detect-collections
cloudcannon configure detect-build-commands
cloudcannon configure generate --dry-run
cloudcannon validate
```

Treat generated configuration as a baseline. Do not replace an existing `cloudcannon.config.yml` or `.cloudcannon/initial-site-settings.json` without inspecting the proposed changes. Verify unfamiliar keys against the official reference or published JSON schema, and run `cloudcannon validate` after edits.

For Editable Regions and snippets, follow the site's existing framework, components, and content model. Do not introduce a page builder, restructure content, or make additional fields editable unless the task requires it.

## Preview locally

Build or watch the site with its normal project command, then pass the actual built output directory to:

```bash
cloudcannon dev <output-directory>
```

The dev server enables live sync by default and accepts CloudCannon app writes to local files. Use `--no-app-sync` for a read-only preview. State that local files can change before running with app sync enabled when the task did not already authorize editor-driven file changes.

## Inspect remote state

CloudCannon list commands can return billing and account metadata. Filter output to the fields needed and do not paste complete records into chat.

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
cloudcannon inboxes submissions list --inbox=<name|id|key|uuid>
```

Site names may occur more than once for preview and production branches. Before any remote write, resolve the exact site and confirm its UUID, repository branch, domain, and build configuration. Use the UUID for the write command.

## Diagnose failures

Start with `print-last-failed-build`. If several sites failed around the same time, compare their logs before changing individual repositories. Check for a shared package registry, runtime, dependency, install command, or CloudCannon platform failure. Use `print-last-failed-sync` when the build log points to repository synchronization.

Reading logs and settings does not authorize a rebuild or configuration change.

## Remote changes

These commands change external state:

- `cloudcannon sites rebuild`
- `cloudcannon sites create`
- `cloudcannon sites update-build-config`
- `cloudcannon sites files upload|move|clone|delete|restore|discard|commit`

Immediately before running one, state the exact site UUID, branch, domain, and effect. Get explicit user approval when the command affects production, a daily-driver preview, published content, repository files, build settings, or consumes a build. Never use a matching site name as proof that the target is correct.

After an authorized change, read the resulting site or build state and report whether it succeeded. Do not retry a failed mutation repeatedly without diagnosing the failure.
