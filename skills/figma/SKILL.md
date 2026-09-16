---
name: figma
description: Use when inspecting or editing Figma files, or when using a Figma design as an implementation reference through computer or browser control.
---

# Figma

Use computer or browser control. Open Figma in the primary work Chrome profile defined by `environment` and follow its sign-in rules. Follow the control tool's instructions. Do not use Figma MCP, the API, or a Figma connector for this workflow.

Open the supplied link and confirm the file, page, frame, and variant. Inspect the relevant canvas, layers, properties, and prototype interactions. Zoom in as needed and capture useful screenshots. Report anything that access restrictions hide.

Export needed assets through Figma's visible controls. Reuse matching project assets. Keep the source frame link with the work.

For implementation, use `design` and `development`. Follow the supplied design and existing project patterns, then compare the result with the Figma reference. Do not redesign nearby screens or invent missing functionality. Mark estimates as estimates when they could affect the result.

Reading a design or implementing it in code does not authorize changing the Figma file. Make Figma edits only when requested, within the specified frames and scope, and verify the visible result. If access is blocked, report the exact blocker; do not switch to a different integration.
