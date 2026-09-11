---
name: cloudcannon
description: Configure and preview CloudCannon projects, work with editable regions and snippets, or inspect and manage CloudCannon sites through its official CLI.
---

# CloudCannon

Prefer the official `cloudcannon` CLI. Check the installed command's `--help` and [CLI documentation](https://cloudcannon.com/documentation/developer-reference/cli/) for commands, installation, and authentication. Use the [SDK](https://cloudcannon.com/documentation/developer-reference/sdk/) or [REST API](https://cloudcannon.com/documentation/developer-reference/api/) for code integrations or unsupported CLI operations.

## Local work

Inspect the existing build output, content model, and CloudCannon configuration before generating changes. Use the [configuration reference](https://cloudcannon.com/documentation/developer-reference/configuration-file/) for unfamiliar keys and run `cloudcannon validate` after edits.

Follow the existing content model for [Editable Regions](https://cloudcannon.com/documentation/developer-reference/editable-regions/) and [snippets](https://cloudcannon.com/documentation/developer-reference/configuration-file/types/_snippets/). The Visual Editor API is for custom editor integrations; ordinary inline editing uses Editable Regions.

Build or watch the site with its normal project command, then run `cloudcannon dev <output-directory>` against the built output. App sync is enabled by default and can write to local files. Use `--no-app-sync` for a read-only preview; enable writes only within the authorized editing task.

## Remote work

Site names may repeat across preview and production. Before a write, resolve the site's UUID, repository branch, domain, and build configuration. Use its UUID in the command.

Reading logs or settings does not authorize a rebuild or configuration change. State the target and effect before changing remote state; production and daily-driver previews require explicit authorization. An existing instruction covering that action is sufficient.

For failures, inspect the relevant failed build or sync log. If several sites fail together, check for a shared cause before changing individual projects. After an authorized change, read back the resulting site or build state. Diagnose failed mutations before retrying.
