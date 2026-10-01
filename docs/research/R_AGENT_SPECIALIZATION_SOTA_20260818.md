# R_AGENT_SPECIALIZATION_SOTA: Agent Specialization & Long-Term Knowledge Management — 2025–2026 SOTA Survey
**Version**: 1.0.0
**Status**: FINAL
**Date**: 2026-08-18
**Author**: researcher (Sovereign Researcher — Council of Four)
**Classification**: Sovereign Research Gnosis
**Companion docs**: `R_AGENT_FLEET_TOPOLOGY.md` (fleet architecture), `R_AGENT_SOUL_FILE_HARDENING_20260725.md` (soul.yaml design)

---

## 1. Executive Summary

**Core question**: Does a domain-specialist agent (e.g., Grokster, Kali, Ma'at) need sub-specialists? How do we manage research/knowledge-bases for long-term expertise?

**The SOTA answer, triangulated across 30+ sources (2025–2026)**:

1. **Specialization is a knowledge problem, not a role problem.** The dominant production pattern is *not* "spawn a sub-agent per domain role" — it is "keep a generalist orchestrator, and specialize the **context** (rules, memory, knowledge bases) per task." Anthropic's official guidance: split by **context boundaries**, not by roles. Cursor/Cline/Copilot all converged on the same architecture: one agent + layered persistent instruction files (AGENTS.md, rules, skills).

2. **Multi-agent parallelism pays only for parallelizable, independent sub-problems.** Google DeepMind's scaling study (180 configurations, Jan 2026): multi-agent improves parallelizable tasks (+80.9%) but *degrades* sequential ones (−39% to −70%). Anthropic: multi-agent uses ~15× tokens vs. single-agent chat; only worth it for high-value tasks. The decision rule is **task topology**, not domain.

3. **Long-term expertise lives in memory + knowledge bases, not in more agents.** CoALA (cognitive architecture framework) and Letta/MemGPT (three-tier memory: core/recall/archival, self-editing) are the academic grounding. The 2026 production consensus: **prompt = brain (always loaded), RAG/KB = encyclopedia (conditionally retrieved), memory = episodic record (self-managed)**. Knowledge **freshness** is the #1 failure mode — 60% of RAG failures trace to stale content (single-source claim, flagged).

4. **Persistent expertise requires "rules as memory" discipline.** The #1 repeated lesson across Cursor/Cline/Claude Code: a correction that lives only in chat is lost; it must be encoded as a persistent rule with imperative format ("Do X, not Y, because Z") + example. This maps directly to Omega's L1→L2→L3 soul distillation — the same pattern, formalized.

5. **Local-first is viable and proven for the full stack.** Ollama + smolagents, Ollama + Cline air-gapped, OpenClaw 100% offline — all documented working stacks in 2026. The constraint is model capability (small local models need tighter context discipline), not architecture.

**Top 3 recommendations for Omega** (detailed in §8):
- **R1**: Keep the Pillar Lattice as-is (no sub-specialist explosion); add a **Context Specialization Layer** — per-entity `rules/` + `knowledge/` + `memory/` that specialize the *context* per task, not new agents.
- **R2**: Adopt the **three-tier memory model** (core = soul.yaml + session_gnosis, recall = conversation history, archival = knowledge/ + library FTS5) with **self-editing memory tools** — the agent manages its own memory hierarchy (Letta pattern).
- **R3**: Implement **freshness SLAs** on knowledge bases: classify sources by rot speed, add `last_verified` timestamps, expire/refresh stale docs, and make freshness a ranking signal in retrieval.

---

## 2. Specialization Architectures (2025–2026 SOTA)

### 2.1 Generalist vs. Specialist: The Empirical Case

| Source | Finding | Verifiability |
|---|---|---|
| Google DeepMind — "Towards a science of scaling agent systems" (Jan 2026, arXiv 2512.08296) | 180 agent configurations tested; multi-agent coordination dramatically improves **parallelizable** tasks (+80.9% avg) but **degrades sequential** tasks (−39% to −70%); error amplification 17.2× (independent) vs 4.4× (centralized); a predictive model selects the optimal architecture for **87% of unseen tasks** (R²=0.513–0.524) | ✅ Primary (research blog + arXiv) |
| Tian Pan — "When the Generalist Beats the Specialists" (Apr 2026) | Cites 2025 Google DeepMind/MIT study; empirical data favors unified single-agent in many production cases; coordination/token overhead erodes specialist gains | ✅ Secondary analysis (URL verified) |
| arXiv 2601.13671 — "The Orchestration of Multi-Agent Systems" | Coordination overhead, message congestion, and performance bottlenecks scale with agent count | ✅ Primary (arXiv) |
| ToolHalla — "Single Agent vs Multi-Agent" (Mar 2026) | Heuristic: single agent wins for sequential tasks under ~20K tokens; multi-agent wins for independent parallel sub-problems; cites Anthropic 10–15× token cost | ⚠️ Practitioner heuristic (flag: "20K tokens" is not a published threshold) |

**Council verdict (Architect + Adversary)**: The empirical consensus is unambiguous — **task topology decides architecture**. Sequential, tightly-coupled work (most engineering) wants one agent with rich context. Parallel, independent exploration (research, multi-angle analysis) wants orchestrator + fan-out. Domain expertise alone is never sufficient justification for a new agent.

### 2.2 Production Orchestration Patterns

| Pattern | Description | Where it's used |
|---|---|---|
| **Orchestrator–Worker** | Lead agent decomposes task, spawns 3–5 parallel subagents with structured objectives, synthesizes results | Anthropic multi-agent research system (Claude Opus lead + Sonnet workers) |
| **Handoffs** | Agent transfers control to another agent with context; manager-in-control variant keeps a supervisor | OpenAI Agents SDK (primary primitive) |
| **Agents-as-Tools** | Orchestrator calls other agents as tools, retains full control | OpenAI Agents SDK, LangGraph |
| **Hierarchical / Governor–Expert** | Root orchestrator → mid-tier coordinators → leaf workers; different models per tier | Google ADK, Omega's own MaKaLi → Pillar topology (R_AGENT_FLEET_TOPOLOGY) |
| **Loop/Critic** | Executor + critic agent loop until quality rubric passes | OpenAI o1-style internalized critic; production QA gates |
| **Sequential Pipeline** | A→B→C, strict data dependencies | Simple deterministic workflows |
| **Single reasoning model** | One RL-trained model plans, searches, reads, synthesizes — no subagents | OpenAI Deep Research (o3-mini/o3-deep-research), Gemini Deep Research |

**Framework landscape (2026)**: LangGraph = production standard (stateful graphs, checkpointing); CrewAI = fastest role-based prototyping (teams often migrate CrewAI→LangGraph); AutoGen = conversational/free-form; OpenAI Agents SDK = lightweight primitives (Agent, Runner, Tool, Handoff); Google ADK = hierarchical with automatic routing. (Source: appstackbuilder.com, innervationai.com, aiworkflowlab.dev)

**Key insight for Omega**: The engine already implements the **Governor–Expert (HMAS)** pattern per R_AGENT_FLEET_TOPOLOGY.md — this is the SOTA-stable topology. The gap is not topology; it is **context specialization** (see §4–§5).

### 2.3 The Deep Research Architectures (the closest analog to Omega's research loop)

| System | Architecture | Token economics |
|---|---|---|
| **Anthropic multi-agent research** | Lead agent + 3–5 parallel subagents; subagents use 3+ parallel tool calls; explicit scaling rules in prompt (1 agent for fact-finding, 2–4 for comparisons, 10+ for comprehensive research); CitationAgent verifies sources | ~4× tokens vs chat (agents), ~15× (multi-agent); reported 90.2% improvement over single-agent on internal evals |
| **OpenAI Deep Research** | Single reasoning model (o3-mini/o3-deep-research) trained via RL to plan/search/read/synthesize; clarification round before research; mid-flight interruption supported | $10/M input, $40/M output (o3-deep-research); typical run $5–30 |
| **Gemini Deep Research** | Single multimodal model with unified intent-planning (editable research plan surfaced); streaming progress | ~250K input tokens standard task (50–70% cached), ~900K complex |
| **Perplexity Deep Research** | Iterative retrieval loop; hybrid model selection per subtask | 193K reasoning tokens documented for a 21-search query |
| **GPT-Researcher / STORM** | Open-source; parallel sub-graphs per subtopic (LangGraph); STORM: multiple "expert" agents answer, "writer" agents synthesize | — |

**Critical limitation (documented)**: Anthropic's lead agents execute subagent batches **synchronously** — slow subagents block the pipeline, lead cannot steer mid-task. Asynchronous parallel execution is identified as a major unsolved challenge (arXiv 2506.18096). (Source: Zylos Research deep-dive, Apr 2026)

**Council verdict (Alchemist)**: The research-agent space has converged on **ReAct loop + external memory + parallel fan-out as the performance lever**. Omega's background researcher loop + sovereign_search + local worker pool already matches this shape. The gap: explicit **scaling rules in the prompt** (Anthropic's "1/2–4/10+" rule) and a **citation verification pass** before synthesis.

---

## 3. Sub-Specialist Patterns (When to Spawn, How to Structure)

### 3.1 When sub-specialists are justified (evidence-based)

✅ **Justified**:
- **Parallel independent exploration** (research angles, comparisons, multi-source verification) — DeepMind +80.9% parallel gain
- **Context isolation** — subagent with its own context window prevents context clash (ToolHalla, Cursor subagents since v2.4)
- **Verification/critique loops** — separate critic agent with rubric (Loop/Critic pattern; Anthropic CitationAgent)
- **Long-horizon autonomous work** where a dedicated context prevents drift (Planner–Worker–Judge with external `tasks.md` ground truth)

❌ **Not justified**:
- **Role-based splitting by domain alone** ("we need a Python agent and a Rust agent") — Anthropic: split by context boundaries, not roles
- **Sequential dependent work** — multi-agent degrades −39% to −70% (DeepMind)
- **Shared-context, highly-coupled domains** — Anthropic explicitly flags as bad fit
- **Simple tasks** — 1 agent, 3–10 tool calls (Anthropic scaling rules)

### 3.2 Sub-specialist structure best practices

1. **Explicit scaling rules in the system prompt** — don't leave spawn-count to model judgment: "use 1 subagent for simple tasks, 2–4 for comparisons, 10+ for comprehensive research" (Anthropic, via Zylos).
2. **Structured subagent objectives** — lead defines decomposition + per-subagent objective before spawning (Anthropic).
3. **Parallelism limits** — Cursor: max 8 parallel agents, recommend 2–3 (merge complexity scales non-linearly); Claude Code: max 10 parallel subagents; Anthropic: 3–5 typical.
4. **Verification subagent pattern** — a dedicated subagent that checks the main agent's output against a rubric; the single most recommended pattern in Claude Code best practices.
5. **Compression filters** — subagents act as context compressors: they return distilled findings, not raw dumps (Anthropic multi-agent system: subagents return summaries; R_AGENT_FLEET_TOPOLOGY: Governor passes Compressed State Vector, not full history).
6. **"Return to Router" trigger** — every specialist must detect out-of-domain tasks and return to the router (R_AGENT_FLEET_TOPOLOGY §4.2).

### 3.3 The "Temporary Pillar" question (Omega-specific)

R_AGENT_FLEET_TOPOLOGY §5 Open Question 1: *Can the engine auto-spawn a Temporary Pillar for a one-time task, then distill its gnosis into the permanent fleet?*

**SOTA answer**: Yes — this is exactly the **orchestrator-worker + distillation** pattern. The worker is ephemeral (spawned per task, context-scoped), but its findings are distilled into the permanent knowledge base (EvolveR's closed-loop experience lifecycle: distill abstract principles from trajectories, retrieve to guide future actions — ICML 2026). **The fleet stays lean; the knowledge grows.** This aligns with M10 (Fleet Integrity — no new agents without verified gap).

---

## 4. Knowledge Management for Agents

### 4.1 The CoALA framework (academic grounding)

**CoALA — Cognitive Architectures for Language Agents** (Sumers, Yao, Narasimhan, Griffiths; arXiv 2309.02427, TMLR 2024): the reference framework organizing language agents into:
- **Modular memory components** (working, episodic, semantic, procedural)
- **Structured action space** (internal memory operations + external environment tools)
- **Generalized decision-making process** (planning → execution → observation)

**Why it matters for Omega**: CoALA is the academic formalization of what Omega already does — soul.yaml (semantic memory), session_gnosis (working memory), knowledge/ (procedural + semantic), conversation history (episodic). It validates the architecture and provides vocabulary for gaps.

### 4.2 Three-tier memory: the Letta/MemGPT pattern

**MemGPT: Towards LLMs as Operating Systems** (arXiv 2310.08560) → commercialized as **Letta**. The OS analogy:
- **Core memory (= RAM)** — always in context; structured labeled blocks (human, persona); agent self-edits with safeguards (read-only protection, uniqueness checks)
- **Recall memory (= page cache)** — searchable conversation history
- **Archival memory (= disk)** — vector store, unlimited, tool-based retrieval

**Key differentiator**: the **agent self-manages its memory** — it decides what to remember, forget, archive, retrieve (proactive, not passive RAG). Git-backed evolution for versioning. "Sleeptime agents" run background memory compaction.

**2026 comparison** (TokenMix Research Lab, Apr 2026): Mem0 = bolt-on memory layer (low lock-in, fast integration, 78% fact recall accuracy on personalization benchmarks); Letta = full agent runtime (high lock-in, best episodic coherence — maintains context across 500+ interactions vs RAG baselines fragmenting after ~50); MemGPT = reference implementation for full control.

**Council verdict (Archivist)**: Omega's MemoryStore (FTS5 + vector hybrid), soul.yaml, and session_gnosis.md already approximate the three tiers. The missing piece is **self-editing**: the agent should have explicit memory-management tools (promote insight → soul, archive stale, compact history) rather than only passive append.

### 4.3 Prompt vs. RAG vs. Knowledge Base (the 2026 consensus)

| Layer | Role | Load timing | Failure mode |
|---|---|---|---|
| **Prompt / system instructions** | Agent's brain — behavior, guardrails, identity | Always loaded | Bloat degrades reliability; context rot |
| **RAG / retrieval** | Encyclopedia — conditional reference | On-demand retrieval | Freshness (60% of failures — flagged); wrong chunking |
| **Memory** | Episodic record — what happened | Self-managed | Fragmentation without consolidation |

(Source: Regal.ai context engineering guide; AgentForgeHub knowledge freshness; heycc.cn agent memory taxonomy)

**The 2026 rule**: don't bloat context. Keep always-loaded instructions lean (<200 words per rule block, <2,000 tokens total always-apply — Cursor best practices); push everything else into retrievable knowledge with freshness management.

### 4.4 Zettelkasten / second-brain patterns

Atomic notes + bi-directional links + distillation + MCP retrieval (zettelkasten.de; OpenClaw Zettelkasten plugin; godmodeai2025 Zettelkasten-2Brain). Relevant to Omega's knowledge/ directories: **atomic, linked, distilled** notes beat monolithic docs for agent retrieval.

---

## 5. Platform Expertise Maintenance

### 5.1 The rules ecosystem (AGENTS.md, .cursor/rules, .clinerules)

**AGENTS.md became the cross-platform standard mid-2025** (co-promoted by Anthropic, OpenAI, Google, Sourcegraph, Cursor, JetBrains), replacing .cursorrules/.clinerules/CLAUDE.md as the universal project-context file. (Source: promptless.ai)

**The 2026 hierarchy** (Cursor docs + design.dev + morphllm):
1. Team Rules (highest) → 2. Project Rules (.cursor/rules/*.mdc, version-controlled) → 3. User Rules (global) → 4. Legacy .cursorrules → 5. AGENTS.md

**AGENTS.md vs rules distinction** (baeseokjae/RockB):
- **AGENTS.md** = project context: "what is this project?" (architecture, module map, WIP, test commands)
- **.cursor/rules/*.mdc** = behavioral rules: "how should the agent write code?" (patterns, security constraints, conventions)
- Overlap wastes tokens — keep distinct.

**Rule format that works** (Cursor/Cline docs, converged):
- **Imperative with example**: "Do X, not Y, because Z" + concrete example — agents follow this reliably
- **Passive/abstract rules are ignored**: "Follow clean architecture principles" fails
- **Token budget**: always-apply rules <200 words each, <2,000 tokens total; verbose content → auto-attached (glob-scoped) or agent-requested rules
- **Keep rules current** — outdated rules confuse agents and waste context (Cline docs)

### 5.2 The #1 lesson: corrections must become rules

**"Why does my Cursor agent keep making the same mistake after I correct it?"** — Because corrections in chat are not persisted. The fix: encode every correction as a persistent rule. (Cursor best practices FAQ, 2026)

**This is exactly Omega's L1→L2→L3 soul distillation** — the same principle formalized: session insight (L1) → distilled principle (L2) → universal rule (L3) written to soul.yaml/proposed_lessons.yaml. The SOTA tools do this manually; Omega does it systematically. **This is a genuine architectural advantage.**

### 5.3 Knowledge freshness (the #1 knowledge failure mode)

**AgentForgeHub — "Knowledge Freshness for AI Agents"** (John Babich, Mar 2026):
- Freshness must be a **first-class ranking signal** in retrieval
- Classify sources by **rot speed** (fast: APIs, pricing, news; slow: math, architecture principles)
- **Freshness SLAs** per source class; **expiration rules**; **hot/warm/cold knowledge lanes**
- **Freshness checkpoint before action** — verify the knowledge is current before acting on it
- Self-maintaining knowledge bases: doc drift detection, periodic re-verification, LLM-Wiki paradigm

**Council verdict (Adversary)**: This is the highest-leverage gap for Omega. The engine's knowledge/ directories and HALL_OF_RECORDS accumulate without freshness metadata. Without `last_verified` + rot classification, the fleet will confidently act on stale facts — the exact failure the Skeptical Verifier (M17) exists to catch.

---

## 6. Economics of Specialization

| Metric | Value | Source |
|---|---|---|
| Agent vs. chat token cost | ~4× | Anthropic engineering (multi-agent research system) |
| Multi-agent vs. chat | ~15× | Anthropic engineering |
| Parallel gain (independent tasks) | +80.9% | DeepMind scaling study |
| Sequential degradation | −39% to −70% | DeepMind scaling study |
| Error amplification (independent) | 17.2× | DeepMind scaling study |
| Error amplification (centralized) | 4.4× | DeepMind scaling study |
| Deep research run cost | $5–30 (o3-deep-research); $2–5 (Gemini standard) | Zylos Research pricing table |
| Token budget for always-apply rules | <2,000 tokens | Cursor best practices |
| Parallel agent limit | 8 (Cursor), 10 (Claude Code), 3–5 (Anthropic recommended) | Respective docs |

**Decision rules**:
1. **Model tiering**: orchestrator on strong model, workers on cheaper model (Anthropic: Opus lead + Sonnet workers; "a better model beats a larger token budget")
2. **Prompt caching**: target 50–70% cache hit rates on repeated context (Gemini Deep Research caches 50–70% of ~250K input tokens)
3. **Parallel fan-out only when latency matters more than token spend** — "a 3× latency reduction often justifies a 3× cost increase for user-facing features" (RockB multi-agent design guide)
4. **Local-first economics**: local inference has near-zero marginal cost — the token multipliers matter less for Omega than for cloud-only systems, but the **context-window discipline** still applies (small local models).

---

## 7. Sovereign / Local-First Patterns

### 7.1 Documented working local stacks (2026)

| Stack | Description | Source |
|---|---|---|
| Ollama + smolagents | Local agent loop with HuggingFace smolagents on Ollama models | github.com/scriptstar/Local-AI-Agent-Ollama |
| OpenClaw 100% offline | Full agent (formerly Clawdbot/Moltbot) on Ollama + Llama 3, no cloud | inspiredwebandai.wordpress.com (Aug 2026) |
| Ollama + Cline air-gapped | VS Code agent fully offline | baeseokjae.github.io local-ai-agents-guide-2026 |
| Letta self-hosted | Three-tier memory runtime, self-hostable (OSS core) | TokenMix comparison; Letta docs |

### 7.2 Sovereignty implications

- **Memory and knowledge are the sovereignty surface**: the Letta/MemGPT pattern (self-managed, git-backed, self-hosted memory) is the reference for sovereign long-term expertise. Omega's soul.yaml + knowledge/ + MemoryStore already implement this locally.
- **No telemetry constraint (M8)**: OpenAI Agents SDK tracing must be disabled for ZDR orgs (`OPENAI_AGENTS_DISABLE_TRACING=1`) — Omega's zero-telemetry mandate is stricter and aligns with the ZDR pattern.
- **Freshness without cloud**: local freshness verification (re-crawl, re-verify against local sources) is fully feasible; the background researcher loop is the natural freshness engine.
- **The 15× token multiplier is a feature, not a bug, for local**: local inference is free marginal cost; the constraint is RAM/VRAM and context window, so **context discipline** (lean prompts, three-tier memory, freshness) matters more than token spend.

---

## 8. Recommendations for Omega Engine

### R1 — Context Specialization Layer (not sub-specialist explosion)
**Adopt the SOTA pattern**: keep the Pillar Lattice (M10 Fleet Integrity), specialize **context** per task:
- Per-entity `rules/` directory (imperative, with examples, <200 words each) alongside existing `knowledge/` and `workspace/`
- Distinguish: `AGENTS.md`-equivalent (project context) vs. rules (behavioral constraints) — currently conflated in system prompts
- Encode every session correction as a persistent rule (the Cursor lesson) — formalize via the existing L1→L2→L3 pipeline

### R2 — Three-tier memory with self-editing
- **Core**: soul.yaml + session_gnosis.md (always in context, structured blocks — Letta "human/persona" block pattern)
- **Recall**: conversation history (MemoryStore FTS5 + vector — already exists)
- **Archival**: knowledge/ + library (FTS5-first search — already exists)
- **Add**: explicit memory-management tools — promote insight → soul, archive stale, compact history; agent self-manages (Letta pattern), with safeguards (read-only blocks, uniqueness checks)

### R3 — Freshness SLAs on knowledge
- Add `last_verified` + `rot_class` (fast/slow) metadata to knowledge docs and HALL_OF_RECORDS entries
- Classify sources by rot speed; set expiration rules per class
- Make freshness a ranking signal in FTS5/vector retrieval (extend C-MEM-013 hybrid scoring)
- Wire the background researcher loop as the freshness engine (re-verify stale docs on cycle)
- Freshness checkpoint before acting on knowledge (AgentForgeHub pattern)

### R4 — Research-loop upgrades (from §2.3)
- Add explicit **scaling rules to the researcher prompt**: 1 agent for fact-finding, 2–4 for comparisons, 10+ for comprehensive research
- Add a **citation verification pass** before synthesis (Anthropic CitationAgent pattern) — aligns with M23 (no unverified claims)
- Consider **async parallel subagent execution** for the background researcher (documented as the field's open challenge — Omega could lead here)

### R5 — Temporary Pillar protocol (answer to R_AGENT_FLEET_TOPOLOGY §5 Q1)
- Formalize: ephemeral worker spawn (context-scoped, per-task) + mandatory distillation of findings into permanent knowledge before worker teardown (EvolveR closed-loop pattern)
- Fleet stays lean; knowledge grows — satisfies M10 and M11 simultaneously

---

## 9. Source Index

### Primary sources (papers, official docs, engineering blogs)
1. Google DeepMind — "Towards a science of scaling agent systems" — https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work (Jan 2026) + arXiv 2512.08296
2. Anthropic — "How we built our multi-agent research system" — https://www.anthropic.com/engineering/multi-agent-research-system (Jun 2025)
3. Anthropic — "Effective context engineering for AI agents" — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (Sep 2025)
4. Sumers, Yao, Narasimhan, Griffiths — CoALA — arXiv 2309.02427 (TMLR 2024)
5. Packer et al. — MemGPT: Towards LLMs as Operating Systems — arXiv 2310.08560
6. arXiv 2601.13671 — "The Orchestration of Multi-Agent Systems"
7. arXiv 2607.02606 — ChainSWE (SWE-bench family survey)
8. arXiv 2510.16079 — EvolveR (ICML 2026, closed-loop experience lifecycle)
9. arXiv 2603.24639 — Experiential Reflective Learning
10. OpenAI Agents SDK orchestration docs — https://developers.openai.com/api/docs/guides/agents/orchestration
11. OpenAI Deep Research cookbook — https://developers.openai.com/cookbook/examples/deep_research_api/introduction_to_deep_research_api_agents
12. OpenAI Deep Research announcement — https://openai.com/index/introducing-deep-research/ + system card https://cdn.openai.com/deep-research-system-card.pdf
13. Cursor docs — Rules — https://cursor.com/docs/rules
14. Cline docs — Rules — https://docs.cline.bot/customization/cline-rules
15. ByteByteGo — "How OpenAI, Gemini, and Claude use agents for deep research" — https://blog.bytebytego.com/p/how-openai-gemini-and-claude-use

### Secondary sources (practitioner analyses — used for synthesis, cross-checked)
16. Tian Pan — "When the Generalist Beats the Specialists" — https://tianpan.co/blog/2026-04-10-when-generalist-beats-specialists-single-agent-architecture
17. Zylos Research — "Deep Research Agent Architectures" — https://zylos.ai/research/2026-04-21-deep-research-agent-architectures/
18. TokenMix — "Mem0 vs Letta vs MemGPT 2026" — https://tokenmix.ai/blog/ai-agent-memory-mem0-vs-letta-vs-memgpt-2026
19. AgentForgeHub — "Knowledge Freshness for AI Agents" — https://www.agentforgehub.com/posts/knowledge-freshness-for-ai-agents
20. Regal.ai — "Context engineering for AI agents" — https://www.regal.ai/blog/context-engineering-for-ai-agents
21. heycc.cn — "AI Agent Memory 2026" — https://heycc.cn/en/posts/ai-agent-memory-2026/
22. promptless.ai — "Agent context files explained" — https://promptless.ai/blog/technical/agent-context-files-explained/
23. appstackbuilder — "LangGraph vs CrewAI vs AutoGen 2026" — https://appstackbuilder.com/blog/langgraph-vs-crewai-vs-autogen-2026
24. baeseokjae (RockB) — "Cursor Agent Best Practices 2026" — https://baeseokjae.github.io/posts/cursor-agent-best-practices-2026
25. baeseokjae (RockB) — "Multi-Agent System Design 2026" — https://baeseokjae.github.io/posts/multi-agent-system-design-guide-2026
26. baeseokjae (RockB) — "Local AI Agents Guide 2026" — https://baeseokjae.github.io/posts/local-ai-agents-guide-2026
27. ToolHalla — "Single Agent vs Multi-Agent 2026" — https://toolhalla.ai/blog/single-agent-vs-multi-agent-2026
28. innervationai — "Single vs. Multi-Agent Architecture: The 2026 Guide" — https://www.innervationai.com/blog/single-vs-multi-agent-architecture-2026-guide/
29. cursor-alternatives — "Cline Rules: Complete .clinerules Guide with Templates (2026)" — https://cursor-alternatives.com/blog/cline-rules
30. morphllm — "Cursor Rules Best Practices: The Complete Guide to .mdc Rules (2026)" — https://www.morphllm.com/cursor-rules-best-practices
31. design.dev — "Cursor Rules Guide" — https://design.dev/guides/cursor-rules
32. Stackviv — "Reflection AI Agents Self-Improvement" — https://stackviv.ai/blog/reflection-ai-agents-self-improvement (Aug 2026)
33. GitHub — "Claude Code subagent best practices" (Anthropic guidance mirror) — https://github.com/rvalen1123/ai-resources-and-guides/blob/main/guides/claude-code/subagent-best-practices.md
34. GitHub — EvolveR — https://github.com/KnowledgeXLab/EvolveR
35. GitHub — Local AI Agent with Ollama — https://github.com/scriptstar/Local-AI-Agent-Ollama
36. OpenClaw 100% offline — https://inspiredwebandai.wordpress.com/2026/08/14/going-100-offline-running-openclaw-locally-with-ollama-and-llama-3/
37. Zettelkasten method — https://zettelkasten.de/ ; OpenClaw Zettelkasten plugin — https://github.com/cx2002302-lang/zettelkasten-second-memory
38. team400.ai — "OpenAI Agent Orchestration: Handoffs Guide" — https://team400.ai/blog/2026-04-openai-agent-orchestration-handoffs-guide
39. cuizhanming — "Anthropic Multi-Agent Research Architecture analysis" — https://cuizhanming.com/anthropic-multi-agent-research-architecture/
40. Letta docs / repo — https://github.com/letta-ai/letta ; https://docs.letta.com/
41. aiworkflowlab — "Multi-Agent AI Systems: 2026 Guide" — https://aiworkflowlab.dev/article/building-multi-agent-ai-systems-2026-architecture-patterns-mcp-production-orchestration
42. apiscout — "OpenAI Agents SDK: Architecture Patterns 2026" — https://apiscout.dev/guides/openai-agents-sdk-architecture-patterns-2026
43. singularitymoments — "OpenAI Deep Research Guide 2026" — https://singularitymoments.com/openai-deep-research-guide-2026/
44. Wavise OpenLLM — "Cursor Agent Best Practices" — https://openllm.wavise.com/blog/cursor-agent-best-practices
45. murataslan1 — "cursorrules 2026 best practices" — https://github.com/murataslan1/cursor-ai-tips/blob/main/rules/cursorrules-2026-best-practices.md

---

## Appendix A — Unverified / Flagged Claims (M23)

| Claim | Source | Flag |
|---|---|---|
| "60% of RAG failures trace to freshness" | AgentForgeHub (single practitioner source) | ⚠️ Single-source; treat as directional, not measured |
| "Single agent wins for sequential tasks under 20K tokens" | ToolHalla (practitioner heuristic) | ⚠️ Not a published threshold; use as rule-of-thumb only |
| "Mem0 78% fact recall; Letta maintains 500+ interactions vs RAG fragmenting at 50" | TokenMix (vendor-adjacent benchmark roundup) | ⚠️ Vendor-adjacent; not independently audited |
| "Companies merge 39% more PRs after agent-first workflows" (Univ. of Chicago study) | baeseokjae/RockB citing | ⚠️ Unverifiable secondary citation; not independently confirmed |
| "90.2% improvement of multi-agent over single-agent" | Anthropic engineering blog (via Zylos secondary analysis) | ✅ Reported by Anthropic; exact figure from internal evals, not peer-reviewed |
| "DeepMind predictive model selects optimal architecture for 87% of unseen tasks" | DeepMind blog + arXiv 2512.08296 | ✅ Primary source; figure is from the paper |
| "Async parallel execution is a major unsolved challenge (arXiv 2506.18096)" | Zylos citing | ⚠️ Secondary citation of arXiv ID; ID not directly verified in this session |

---

*⬡ OMEGA ⬡ Sovereign Researcher ⬡ Council of Four (Architect · Adversary · Alchemist · Archivist) ⬡ 2026-08-18*