# Notion AI Task Summary prompt

The `Summary` property is AI-generated. Never edit it manually or treat it as evidence. Ask Sil to regenerate it in Notion with this prompt when it is stale or misleading:

```text
Write a concise plain-text summary of this Task in at most 2 sentences, using the same language as the Task.

Use only facts explicitly present in the Task properties and Timeline. The Timeline is append-only and possibly incomplete: missing information is unknown, not implicitly decided.

Rules:
- Never invent or infer requirements, acceptance criteria, owners, deadlines, blockers, decisions, status, next steps, or completion.
- Use the Status property as the only source for Task status.
- Process explicit correction or supersession entries before summarizing older entries.
- Do not treat an older superseded claim as current.
- Do not claim to have read linked sources; summarize only the source-grounded information captured in the Timeline.
- Preserve uncertainty such as “concept”, “not tested”, “reported by the PR”, “scheduled”, or “unknown”.
- Phrase volatile information as a dated observation rather than a timeless fact.
- Mention an unknown only when it materially limits understanding or execution.
- Do not output bullets, headings, Markdown, recommendations, or a newly generated next action.
```

Prefer omission over plausible completion: source fidelity is more important than completeness.
