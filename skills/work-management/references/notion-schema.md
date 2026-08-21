# Notion Schema

Use live Notion metadata as the authority for exact property names, option names, relations, IDs, and write validation. Treat these collection IDs as bootstrap hints and verify live metadata before writing.

- **Tasks** `collection://1cb5979e-268c-80e9-bd7d-000b00ac4424`
- **Documents** `collection://ff6254a8-63f6-42c4-842e-f8f357f3aa5d` — database `231186e2-3735-4e04-8568-fe56136d637b`; hybrid index for Notion-native and external documents; bidirectional relations to Tasks, Projects, and Companies
- **Projects** `collection://4f5bd6fe-452e-4fbc-bcf8-cfcc2d19a2ae`
- **Companies** `collection://2635979e-268c-8191-b322-000bd3109d1c`
- **Persons** `collection://3355979e-268c-80b5-abe9-000b0148c40b` — researched or durable person context that does not belong in Google Contacts, related bidirectionally to Companies
- **Meetings** `collection://1cb5979e-268c-808d-888d-000bfa3a527c`
- **Someday** `collection://8b6245be-419a-4203-97e4-f7660514c661`
- **Insights** `collection://1d65979e-268c-80a9-9f26-000bcfb57574`
- **Goals** `collection://2005979e-268c-80d1-8ecf-000b841762a2`
- **Sprints** `collection://3555979e-268c-807b-bdb4-000b86b48f90`

Documents use only `Name`, optional `Source URL`, automatic `Created` and `Edited`, and bidirectional `Tasks`, `Projects`, and `Companies` relations. Store mutable Notion-native content in the page body; use `Source URL` as the canonical location for external documents.

Tasks use `Area` to identify the owning work domain: `Delivery`, `Sales`, `Growth`, `Admin`, or `Personal`.
