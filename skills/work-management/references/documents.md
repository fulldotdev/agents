# Work Documents

Use the `Documents` database for mutable authored work products and external documents that must be findable from the work system.

- Keep Notion-native work in the Document body.
- For Google Docs, Drive, Figma, or another canonical external file, keep the Notion body minimal and set `Source URL` to the canonical location.
- Relate Documents bidirectionally to Tasks, Projects, and Companies.
- Keep the schema minimal: `Name`, those relations, optional `Source URL`, and automatic `Created` and `Edited` fields.

Store full copy, evolving requirements, research, designs, briefs, scopes, specs, drafts, and attached assets in the Document rather than the Task body. The Task Timeline records only a direct lifecycle event—creation, meaningful update, review, approval, publication, or archival—with the exact Document/source and a compact description of the delta.

When migrating a mutable artifact out of a Task, create and relate the Document, preserve its content and files, verify the relation and artifacts, and only then replace the Task content with a source-grounded Timeline event. Preserve Task properties and the AI-generated Summary.
