---
name: find-person
description: Find or distinguish a specific person using public or user-authorized sources and direct user feedback. Use when the user has partial details such as a name, organization, role, place, time period, social handle, or appearance.
---

# Find person

## Set the search frame

- Establish why the user is searching and what would count as a match. Stop if the request involves harassment, covert monitoring, live whereabouts, private contact details, or bypassing access controls.
- Separate confirmed facts, the user's recollections, and working inferences. Verify uncertain basics such as spelling, year, role, place, employer, school, or known username before building on them.
- Ask only questions that change the next search step. Useful early questions cover name certainty, last known context, time period, likely age range, known associates, possible username fragments, and visible traits the user would recognize.
- Continue safe public searches while waiting for answers when there is still a useful read-only route.

## Work outward from strong clues

1. Start with direct queries combining the person's name with the strongest context signals.
2. Choose useful starting points from the organization, team, role, event, school, supervisors, colleagues, and public group accounts.
3. Search outward from the strongest starting points through visible followers, connections, tags, mentions, comments, staff pages, and reused usernames.
4. Cross-reference candidates across independent sources. A matching name alone is weak. Prefer a direct role or organization link, then network overlap, geography, timing, work or study context, and finally appearance.
5. Keep a candidate list with `confirmed`, `strong`, `weak`, and `excluded`. Record the source, why the candidate fits, what conflicts, and why an exclusion was made.
6. Treat appearance as a ranking clue, not proof. Hair, clothing, age presentation, and profile photos change. Do not permanently exclude a candidate from one small or old photo unless the user confirms the exclusion.

Read [references/platform-playbook.md](references/platform-playbook.md) when a search spans multiple platforms or direct queries stall.

## Work with the user during the search

- Present candidates in small batches, usually three to eight. Give each a number, direct source links, matching signals, conflicts, and confidence.
- Ask for specific feedback after each useful batch. Example: "Do 2 or 4 look familiar? If neither does, which fact or visible trait rules them out?"
- Turn feedback into search rules immediately. Preserve exclusions so rejected candidates do not keep returning. Reopen one only when new evidence directly challenges the reason for exclusion.
- Ask whether an appearance description is current. An old hairstyle should not outweigh a strong organization and timing match.
- Name privacy-sensitive actions before taking them. A story or highlight view may be visible to its owner. Following a private account sends a request. Connecting, liking, messaging, joining a group, or revealing a friends list can also create a visible trace. Get explicit approval for the exact action.
- Authentication changes what the user can see, not what the agent may do. Stay read-only unless the user separately approves an interaction.

## Present useful results

Show results in the conversation. Do not build an HTML page, local web app, contact sheet, or bulk photo collection. They require extra cleanup, collect more personal data, and make feedback harder to track.

Prefer this candidate format:

```markdown
1. Name, profile link
   Matches: direct organization connection, correct region and dates.
   Conflicts: role is not stated; current photo is inconclusive.
   Confidence: strong lead, not confirmed.
```

For a negative result, report what was actually checked, which routes were blocked or exhausted, and the best remaining optional step. Never turn missing evidence into an identification.

## Boundaries

- Use public information or information the user is authorized to access.
- Do not circumvent privacy settings, collect private contact details, infer sensitive traits, perform face recognition, or identify someone from biometric matching.
- Do not bulk-download or retain profile photos. Open the smallest useful set of source profiles and let the user make recognition judgments.
- Stop when only private or interactive routes remain, the evidence stays ambiguous after reasonable pivots, the same weak candidates repeat, or the user asks to stop.
- When stopping, summarize the strongest leads, exclusions, searched routes, and any next step requiring approval. Remove temporary artifacts created for the search when they are no longer needed.
