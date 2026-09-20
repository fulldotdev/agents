---
name: cloudcannon
description: Use when configuring or previewing CloudCannon projects, working with editable regions or snippets, or inspecting and managing CloudCannon sites through the official CLI.
---

# CloudCannon

Use the official `cloudcannon` CLI. Check `--help` and the [CLI docs](https://cloudcannon.com/documentation/developer-reference/cli/) for anything unfamiliar. Fall back to the [SDK](https://cloudcannon.com/documentation/developer-reference/sdk/) or [REST API](https://cloudcannon.com/documentation/developer-reference/api/) only when the CLI cannot do it.

## Local work

Look at the build output, content model, and CloudCannon config before you change anything. Use the [configuration reference](https://cloudcannon.com/documentation/developer-reference/configuration-file/) for unfamiliar keys. Run `cloudcannon validate` after edits.

In `.cloudcannon/routing.json` the `match` of a headers rule is an anchored regex: `/.*` covers the whole site, `/*` only the homepage. Header changes only show on a CloudCannon deploy, so verify them with curl on a subpage there.

Follow the existing content model for [editable regions](https://cloudcannon.com/documentation/developer-reference/editable-regions/) and [snippets](https://cloudcannon.com/documentation/developer-reference/configuration-file/types/_snippets/). Use the Visual Editor API only for custom editor integrations.

Build or watch the site with its normal project command, then run `cloudcannon dev <output-directory>` on the built output. App sync is on by default and can change local files. Use `--no-app-sync` for a read-only preview, and turn sync on only when the request allows local edits.

## Remote work

Site names repeat across preview and production. Before a write, confirm the site's UUID, branch, domain, and build config, and use the UUID in the command.

When a build fails, read its build or sync log. If several sites fail at once, look for a shared cause before fixing them one by one. Find the cause of a failed change before you retry it.
