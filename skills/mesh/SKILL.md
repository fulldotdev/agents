---
name: mesh
description: Look up Mesh contacts and contact IDs through the Mesh MCP. Use when the user asks to resolve a person, contact, Mesh ID, relationship context, work history, education, location, birthday, or interaction metadata from Mesh.
---

# Mesh

Use Mesh via MCP for contact lookup and ID resolution.

## Quick start
- Endpoint: `https://mcp.me.sh/mcp`
- Use `mcporter` with the URL directly.
- Search by name first.
- Keep unrelated filters `null`.
- Write Mesh IDs only when the match is clear.
- If multiple strong matches exist, ask.

## Examples
Search contact:
```bash
mcporter call https://mcp.me.sh/mcp.searchContacts \
  --args '{"name":["Jochem de Josselin de Jong"],"keywords":null,"work_history":null,"education_history":null,"location":null,"age":null,"previous_birthday":null,"information_type":null,"upcoming_birthday":null,"first_email_date":null,"last_email_date":null,"first_interaction_date":null,"last_interaction_date":null,"first_event_date":null,"last_event_date":null,"first_text_message_date":null,"last_text_message_date":null,"note_content":null,"note_date":null,"email_count":null,"event_count":null,"text_message_count":null,"group_ids":null,"integration":null,"limit":10,"sort":null,"exclude_contact_ids":null,"include_fields":null}' \
  --output json
```

Get contact:
```bash
mcporter call https://mcp.me.sh/mcp.getContact contact_id:232846488 --output json
```

## Matching rules
- Prefer exact or strongly identifying matches.
- Use work history, education, location, and interaction metadata only to disambiguate.
- Do not infer a contact ID from a weak name match.
- When returning a resolved contact, include the name and ID.
