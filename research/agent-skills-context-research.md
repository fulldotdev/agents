# Research memo: agent skills, reusable prompts, context files, tools, and progressive disclosure

Research date: 2026-07-16. Primary sources are prioritized. Labels distinguish **vendor guidance**, **practitioner opinion**, and **empirical research**.

## Executive synthesis

The strongest common recommendation is not “write more instructions.” It is **put the smallest amount of durable, non-discoverable, broadly applicable guidance in always-loaded context, and reveal task-specific workflows only when needed**.

A useful division of labor:

- **CLAUDE.md / AGENTS.md:** small, durable operating agreements that apply to most work in that scope: non-obvious commands, repository landmines, architectural boundaries, verification requirements, and pointers to deeper material.
- **Skill:** a repeatable task-specific workflow with a recognizable trigger, explicit steps, reusable resources, and a verifiable exit condition. Its metadata is always visible; details load only on activation.
- **Tool or script:** deterministic behavior, access to an external system, enforcement, or transformations that should not be entrusted to prose.
- **Ordinary docs / code:** discoverable facts, background reference, architecture already evident from the repository, and material primarily for humans.
- **One-off prompt:** an ephemeral task with no demonstrated recurrence or stable successful procedure.

A skill earns its maintenance cost when the workflow recurs, the model otherwise misses important steps, the organization has distinctive process/taste, or determinism/resources materially improve reliability. Do not create one merely to restate model knowledge, duplicate docs, preserve a one-off prompt, or paper over a defect better fixed in code/tooling.

## Established vendor / specification guidance

### 1. Anthropic Claude Code documentation — CLAUDE.md is always-on context, not enforcement

**Creator:** Anthropic / Claude Code team<br>
**Source:** https://code.claude.com/docs/en/memory

Concrete guidance:

- Add guidance when Claude repeats a mistake, a review reveals missing project knowledge, a correction recurs across sessions, or a new teammate would need the same context.
- Keep CLAUDE.md to facts needed in every session: build commands, conventions, project layout, and “always do X” rules.
- Move multi-step procedures to a skill; move file-specific guidance to path-scoped rules.
- Target **under 200 lines per CLAUDE.md**; use headers/bullets; make rules concrete and verifiable; remove contradictions and stale rules.
- Scope by audience: managed organization policy, personal global instructions, project-shared instructions, and private local instructions.
- CLAUDE.md is context, not hard enforcement. Use hooks for actions that must be blocked or guaranteed.
- Claude Code does not directly read AGENTS.md; import it from CLAUDE.md to share cross-tool instructions.

Implication: “must always happen” is usually not a prose problem. Put policy in context for judgment, but enforcement in hooks, tests, CI, or tooling.

### 2. OpenAI Codex documentation — AGENTS.md for durable layered guidance

**Creator:** OpenAI Codex team<br>
**Source:** https://developers.openai.com/codex/guides/agents-md.md

Concrete guidance:

- Codex builds an instruction chain from global guidance through repository root to the current directory; closer files override broader files.
- Use global files for personal working agreements, root AGENTS.md for repository norms, and nested overrides for specialized services/modules.
- The combined default budget is 32 KiB; split instructions by directory when needed.
- Verify discovery by asking Codex to summarize active instructions and report source files.

Implication: company-wide defaults, repo norms, and local module rules should be separated by scope rather than combined in one universal file.

### 3. OpenAI Codex documentation — skills are reusable workflows, progressively disclosed

**Creator:** OpenAI Codex team<br>
**Source:** https://learn.chatgpt.com/docs/build-skills

Concrete guidance:

- A skill packages instructions, resources, and optional scripts for a task-specific capability.
- Codex initially sees only name, description, and path; full SKILL.md loads only after selection.
- Skill metadata receives a bounded initial-context budget (at most 2% of the context window or 8,000 characters when unknown).
- Write descriptions with clear scope, boundaries, trigger terms, and front-loaded use cases because descriptions may be shortened.
- Keep each skill focused on one job; prefer instructions over scripts unless deterministic behavior or external tooling is required.
- Write imperative steps with explicit inputs and outputs; test both positive and negative trigger prompts.
- Use repo scope for team/module workflows, user scope for personal cross-repo workflows, admin scope for shared machine defaults, and plugins for distribution.

### 4. Agent Skills open specification — three-level progressive disclosure

**Creator:** Agent Skills maintainers / open standard<br>
**Source:** https://agentskills.io/specification

Concrete guidance:

1. Metadata (~100 tokens) is loaded for every skill.
2. Full SKILL.md instructions load on activation (recommended under 5,000 tokens and under 500 lines).
3. Scripts, references, and assets load only as needed.

Descriptions should explain both **what** the skill does and **when** to use it, with keywords that support correct routing. Keep reference files focused and one link-hop from SKILL.md; avoid deep chains.

### 5. Anthropic Applied AI — context is a finite attention budget

**Creators:** Prithvi Rajasekaran, Ethan Dixon, Carly Ryan, Jeremy Hadfield, Anthropic Applied AI<br>
**Source:** https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

Concrete guidance:

- Start with the minimal prompt that fully specifies expected behavior, then add instructions/examples only in response to observed failures.
- Treat longer context as having diminishing returns (“context rot”); seek the smallest set of high-signal tokens that improves the desired outcome.
- Progressive disclosure lets agents retrieve context layer by layer rather than drowning in exhaustive background.
- Prefer a hybrid: small stable context up front, filesystem/search primitives for just-in-time retrieval.
- Runtime retrieval is slower and can produce dead ends; preloading vs retrieval is a task-dependent trade-off, not a dogma.
- Use compaction, structured notes, or focused subagents for long-horizon work; do the simplest thing that works.

### 6. Anthropic engineering — tool descriptions and outputs are context engineering

**Creator:** Anthropic engineering<br>
**Source:** https://www.anthropic.com/engineering/writing-tools-for-agents

Concrete guidance:

- Build a few high-impact tools based on evaluated workflows; too many overlapping tools create ambiguous choices.
- Prefer workflow-shaped tools (`schedule_event`, `search_logs`, `get_customer_context`) over low-level API wrappers when that removes repeated intermediate steps and context.
- Namespace tools to make boundaries clear, but evaluate prefix/suffix schemes because results differ by model.
- Return high-signal, semantically meaningful fields; use pagination, filtering, ranges, concise/detailed modes, and actionable error messages.
- Write tool descriptions as if onboarding a new hire: make implicit domain knowledge, input/output semantics, and limitations explicit.
- Evaluate accuracy, runtime, call count, token use, and errors; do not rely only on the model’s self-explanation.

## Practitioner recommendations and opinions

### 7. Dex Horthy / HumanLayer — keep CLAUDE.md universally applicable and hand-crafted

**Creator:** Dex Horthy / HumanLayer<br>
**Source:** https://www.humanlayer.dev/blog/writing-a-good-claude-md

Opinion and recommendations:

- CLAUDE.md should onboard the agent to project **WHAT, WHY, and HOW**, especially repository map, purpose, unusual tooling, and verification commands.
- Keep it concise and universally applicable. HumanLayer’s root file was under 60 lines; the post cited a practitioner consensus of under 300 lines (not an Anthropic rule).
- Use progressive disclosure: keep task-specific material in descriptively named documents and make CLAUDE.md a routing layer pointing to them.
- Prefer pointers over copied snippets because copies rot.
- “Claude is not a linter”: use linters, formatters, hooks, and commands for deterministic enforcement.
- Avoid auto-generating the highest-leverage instruction file; curate every line.

### 8. Simon Willison — skills are simple, token-efficient, portable, and easy to iterate

**Creator:** Simon Willison<br>
**Sources:**
- https://simonwillison.net/2025/Oct/16/claude-skills/
- https://simonwillison.net/2025/Jun/27/context-engineering/

Opinion and recommendations:

- Skills may be a bigger deal than MCP precisely because they are simple: markdown plus optional documents/scripts stored on disk.
- Frontmatter provides cheap discovery; the model loads full details only when relevant.
- Skills are easy to inspect and iterate, and scripts can encode reliable operations rather than repeatedly regenerating them.
- “Context engineering” better names the real work than prompt engineering: assembling task description, examples, retrieval, tools, state, history, and compaction for the next step.

### 9. Tobi Lütke and Andrej Karpathy — context engineering is broader than prompt writing

**Creators:** Tobi Lütke (Shopify), Andrej Karpathy<br>
**Primary quotes linked and reproduced by Simon Willison:** https://simonwillison.net/2025/Jun/27/context-engineering/

Practitioner definitions:

- Lütke: context engineering is providing all the context needed for a task to be plausibly solvable.
- Karpathy: industrial LLM systems require carefully filling the context window with task descriptions, examples, retrieved data, tools, state/history, and compaction—an iterative system-design concern rather than a clever one-shot prompt.

### 10. Addy Osmani — skills should be workflows, not essays

**Creator:** Addy Osmani<br>
**Sources:**
- https://addyosmani.com/blog/agent-skills/
- https://addyosmani.com/blog/agents-md/

Opinion and recommendations:

- A skill is not reference documentation. It is a workflow with ordered steps, checkpoints that produce evidence, and a defined exit criterion.
- Prefer process over prose: a testing essay invites plausible text; a TDD loop tells the agent what to do and how completion is proven.
- Every skill should end in concrete evidence (tests, build output, runtime trace, review), not “seems right.”
- Load skills by task/phase, not all at startup; a small router can select focused skills.
- Start with the four or five workflows closest to current pain rather than installing a giant library.
- AGENTS.md should contain only non-discoverable information: tooling gotchas, non-obvious conventions, and landmines. Auto-generated codebase overviews duplicate README/code and add noise.
- A useful mental model: AGENTS.md is a living list of codebase smells not yet fixed; delete guidance after fixing the underlying ergonomics when possible.

### 11. Greg Isenberg with Ras Mic — build a skill only after a successful run

**Creator/channel:** Greg Isenberg interviewing Ras Mic (@rasmic), who presents the detailed method<br>
**Video:** https://www.youtube.com/watch?v=S_oN3vlzpMw<br>
**Useful timestamps:** context files vs skills 04:12; skill creation 09:17; recursive improvement 20:40; context efficiency 29:23.

Practitioner opinion from the video:

- Do not jump from “I have a workflow” directly to writing a skill. Walk the agent through the workflow step by step, correct failures, repeat until a successful run, then ask it to review the transcript and codify the successful procedure.
- Update the skill after later failures are diagnosed and corrected (“recursive skill building”).
- Do not handwrite generic instructions the model already knows; capture personal/company workflow, taste, acceptance criteria, and proprietary knowledge.
- Strong dissent from conventional setup advice: the speaker argues roughly 95% of people do not need a large AGENTS.md/CLAUDE.md, except for knowledge needed every turn, and says many technical-stack reminders are redundant because code is already context.
- He avoids installing random third-party skills: they lack his workflow’s successful-run context and introduce supply-chain/prompt-injection risk. He prefers reviewing them for ideas and rebuilding locally.

This is a forceful practitioner opinion, not vendor guidance. It directly conflicts with Addy Osmani’s recommendation that most people start by installing his skills marketplace, and with vendor encouragement to generate initial context files.

### 12. Armin Ronacher — ordinary scripts/logs can be better than MCP; tools must fail forward

**Creator:** Armin Ronacher (Flask creator)<br>
**Source:** https://lucumr.pocoo.org/2025/6/12/agentic-coding/

Opinion and recommendations:

- Use MCP only when ordinary command-line tools are too unreliable or difficult; each MCP server is another failure surface.
- Anything observable/actionable can be a tool: script, Make target, log file, CLI, or MCP server.
- Tools should be fast, produce little useless output, clearly explain misuse, resist arbitrary agent behavior, and expose logs/debuggability.
- Design the environment so the agent can complete loops independently—for example, log development emails and tell the agent in CLAUDE.md where to find them.
- Prefer simple code and straightforward workflows because agents navigate them more reliably.

## Empirical evidence: the AGENTS.md disagreement is real

### 13. ETH Zürich-led AGENTbench study — generated context often hurts success and cost

**Authors:** Thibaud Gloaguen, Niels Mündler, Mark Müller, Veselin Raychev, Martin Vechev<br>
**Source:** https://arxiv.org/abs/2602.11988

**Empirical research, not vendor guidance.** Across multiple agents/models, repository context files tended to reduce task success and increase inference cost by over 20%. Both generated and developer files encouraged broader exploration and were generally followed, but unnecessary requirements made tasks harder. The authors recommend that human-written context contain only minimal requirements.

Caveat: the benchmark covers issue resolution, mostly Python repositories, and a finite set of agents/models. It does not prove context files are universally harmful.

### 14. Lulla et al. — maintained AGENTS.md reduced runtime and output tokens

**Authors:** Jai Lal Lulla, Seyedmoein Mohsenimofidi, Matthias Galster, Jie M. Zhang, Sebastian Baltes, Christoph Treude<br>
**Source:** https://arxiv.org/abs/2601.20404

**Empirical research.** In 10 repositories and 124 pull requests, AGENTS.md was associated with 28.64% lower median runtime and 16.58% lower output-token consumption, with comparable completion behavior.

Caveat: the study measures efficiency rather than broad correctness, uses repositories with maintained files, and is observational/benchmark-specific. It does not contradict AGENTbench so much as show that **content quality and study design matter**: maintained non-obvious guidance can save exploration, while generated redundant guidance can add cost.

## Key disagreements

1. **Generate an initial context file or curate manually?**
   - Anthropic docs: `/init` can create a useful starting point and then be refined.
   - HumanLayer and Addy Osmani: avoid auto-generated root files; they duplicate discoverable facts and deserve careful manual curation.
   - Evidence: AGENTbench supports the skeptics for generated files; Lulla et al. supports maintained human-authored files for efficiency.

2. **How much belongs in CLAUDE.md / AGENTS.md?**
   - Vendors support durable layered guidance and provide relatively generous mechanical limits.
   - HumanLayer targets very short universal files; the Greg Isenberg video’s speaker goes further, claiming most people barely need one.
   - Convergence beneath the rhetoric: keep only broadly applicable, non-discoverable, high-value guidance in always-loaded context.

3. **Install shared skills or build your own?**
   - OpenAI and Addy Osmani support curated distribution/marketplaces.
   - Greg Isenberg’s guest says do not install random skills: derive them from your own successful workflow and treat third-party skills as untrusted reference material.
   - Practical reconciliation: shared skills fit standardized tool/vendor procedures; personal/company judgment workflows should be forked, reviewed, tested, and adapted locally.

4. **Instructions or scripts/tools?**
   - OpenAI: default to instructions, add scripts for determinism/external tooling.
   - Anthropic and Armin Ronacher strongly emphasize workflow-shaped, token-efficient tools and ordinary scripts.
   - Reconciliation: use prose for judgment and sequence; code for deterministic transforms, enforcement, and system access.

5. **Preload context or retrieve it?**
   - Skills/specs favor on-demand loading.
   - Anthropic explicitly notes that retrieval is slower and can fail; the optimal design is often a hybrid with minimal stable context plus just-in-time exploration.

## Decision guide: when to write a skill

Write a skill when most of these are true:

- The task recurs across sessions, projects, teammates, or customers.
- You can identify a stable trigger and meaningful “should not trigger” boundaries.
- A successful workflow has been demonstrated at least once, preferably more than once.
- The model otherwise skips steps, uses the wrong tool/order, or produces inconsistent artifacts.
- The workflow contains personal/company taste, acceptance criteria, domain heuristics, or proprietary process not in model knowledge.
- There are reusable scripts, templates, schemas, examples, or reference files.
- Completion can be verified by concrete evidence.
- The benefit exceeds maintenance, routing, security-review, and context-metadata costs.

Do not write a skill when:

- It is a one-off task or the procedure is still being discovered.
- It merely restates generic model knowledge or a tool’s public documentation.
- The information belongs in code, README/docs, tests, CI, a formatter, a hook, or a deterministic script.
- It duplicates another skill or creates ambiguous triggers.
- The source material changes too often to maintain safely.
- You cannot define successful output or an exit condition.
- A prompt plus current task context is already reliable.

### Personal skills

Good fits: recurring research format, writing/editing taste, personal review checklist, invoicing/report workflow, preferred project bootstrap, repeated data cleanup. Keep at user scope. Build from actual successful work; avoid encoding generic facts.

### Company/team skills

Good fits: release process, incident triage, security review, customer-response workflow, design-system implementation, client onboarding, migration playbook. Version-control them, assign owners, include verification, test triggers, and review third-party content as executable supply-chain input.

### Tool/vendor skills

Good fits: APIs/CLIs with non-obvious sequences, domain terms, common errors, schemas, and helper scripts. Prefer links/references that can be updated centrally. If the operation can be made deterministic and compact as a tool, do that and make the skill explain when/how to invoke it.

## Recommended guide thesis

“Write a skill after a workflow proves itself—not before. Keep always-loaded instructions small and non-discoverable; turn recurring task-specific procedures into progressively disclosed workflows; move determinism and enforcement into tools. Delete or revise instructions when the underlying code, tooling, or process changes.”
