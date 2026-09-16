---
name: cloudcannon
description: Use when configuring or previewing CloudCannon projects, working with editable regions or snippets, or inspecting and managing CloudCannon sites through the official CLI.
---

# CloudCannon

Prefer the official `cloudcannon` CLI. Check its `--help` and the [CLI documentation](https://cloudcannon.com/documentation/developer-reference/cli/) for unfamiliar operations. Use the [SDK](https://cloudcannon.com/documentation/developer-reference/sdk/) or [REST API](https://cloudcannon.com/documentation/developer-reference/api/) when the CLI does not support the request.

## Local work

Inspect the build output, content model, and CloudCannon configuration before making changes. Use the [configuration reference](https://cloudcannon.com/documentation/developer-reference/configuration-file/) for unfamiliar keys. Run `cloudcannon validate` after edits.

Follow the existing content model for [Editable Regions](https://cloudcannon.com/documentation/developer-reference/editable-regions/) and [snippets](https://cloudcannon.com/documentation/developer-reference/configuration-file/types/_snippets/). Use the Visual Editor API only for custom editor integrations.

Build or watch the site with its normal project command. Then run `cloudcannon dev <output-directory>` against the built output. App sync is enabled by default and can change local files. Use `--no-app-sync` for a read-only preview. Enable sync only when the editing request authorizes local changes.

## Remote work

Site names may repeat across preview and production. Before a write, confirm the site's UUID, repository branch, domain, and build configuration. Use the UUID in the command.

Reading logs or settings does not authorize a rebuild or configuration change. State the target and effect before changing remote state. Production sites and previews used for daily work require explicit authorization. An earlier instruction that clearly covers the action is enough.

For failures, inspect the relevant build or sync log. If several sites fail together, check for a shared cause before changing individual projects. After an authorized change, read back the site or build state. Find the cause of a failed change before retrying it.
