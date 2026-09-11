---
name: figma
description: Inspect or edit Figma files and use Figma designs as implementation references through computer or browser control.
---

# Figma

Use computer or browser control. Open Figma in the machine's Chrome default profile under the global browser and sign-in rules. Use the available control tool and follow its returned instructions. Do not use Figma MCP, the API, or a Figma connector for this workflow.

Open the supplied link and confirm the correct file, page, frame, and variant. Inspect the visible canvas, layer panel, properties, and prototype interactions relevant to the request. Zoom or navigate to read details; capture useful screenshots rather than inferring a design from a distant overview. Report properties or assets that access restrictions prevent you from inspecting.

Export needed assets through Figma's visible export controls. Reuse supplied project assets when they already match. Keep the source frame link with the work so the design can be reopened.

For implementation, use `design` and `development`: follow the supplied design and existing project patterns, then compare the affected result against the Figma reference. Do not redesign adjacent screens or invent missing functionality. Distinguish measured properties from estimates when that difference matters.

Reading a design or implementing it in code does not authorize changing the Figma file. Make Figma edits only when requested, within the specified frames and scope, and verify the visible result. If access is blocked, report the exact blocker; do not switch to a different integration.
