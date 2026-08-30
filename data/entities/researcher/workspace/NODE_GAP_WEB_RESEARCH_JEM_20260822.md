<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# NODE_GAP_WEB_RESEARCH_JEM_20260822
**AP Token**: `AP-NODE-GAP-WEB-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER (executing @jem dispatch directly — subagent depth limit reached at depth 2) ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_gap_web_research ⬡ ACTIVE

**Date**: 2026-08-22
**Dispatched by**: @researcher → intended @jem; executed directly per Direct Execution First after `task()` returned "Subagent depth limit reached (2)".
**Scope**: PURE WEB-RESEARCH. No code modified. Single deliverable = this file.
**Calibration source**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (read & verified this session; D-586 ratified 2026-08-21).

## Executive Frame

QUESTION: Which ADDITIONAL domain-expert Nodes (N11+) should be chartered to cover (a) full engine depth and (b) Architect personal interests?

Baseline N1–N10: sysadmin · datastore · buildmaster · bridge · sentinel · modelgate · context · watchtower · link · verifier.

---

## Q1 — Agent-Fleet Taxonomies at SOTA

### Per-system survey

| System | Specialist structure | Source (`last_verified: 2026-08-22`) |
|---|---|---|
| **MetaGPT** | Fixed SOP "software company": Product Manager → Architect → Project Manager → Engineer → QA Engineer; structured artifact handoffs (PRD→design→task list→code→tests); publish-subscribe message pool | https://arxiv.org/html/2308.00352v7 ; https://github.com/geekan/MetaGPT-docs/blob/main/src/en/guide/get_started/introduction.md |
| **CrewAI** | Arbitrary specialists defined by role/goal/backstory triple; per-agent tools, memory, delegation flags; task-design > agent-design guidance | https://docs.crewai.com/concepts/agents ; https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/crewai.html |
| **AutoGen / Magentic-One** | Orchestrator (two-loop Task/Progress Ledger) + WebSurfer + FileSurfer + Coder + ComputerTerminal; plug-and-play roster; ablations show surviving agents compensate creatively when a specialist is removed | https://arxiv.org/abs/2411.04468 ; https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html |
| **Anthropic multi-agent research** | Lead Researcher (orchestrator w/ effort-scaling + dedup instructions) → parallel Search Subagents → dedicated **Citation Agent** post-hoc; LLM-as-judge evals; ~15× token cost of chat; early failure mode: lead spawning 50 subagents for simple queries | https://www.anthropic.com/engineering/multi-agent-research-system (pub. 2025-06-13) |
| **OpenAI Agents SDK / Swarm lineage** | Two orchestration primitives: **Handoffs** (triage routes; specialist owns the conversation branch) vs **Agents-as-tools** (manager retains ownership); guardrail agents; explicit guidance: *"Start with one agent whenever you can. Add specialists only when they materially improve capability isolation, policy isolation, prompt clarity, or trace legibility."* | https://openai.github.io/openai-agents-python/handoffs/ ; https://developers.openai.com/api/docs/guides/agents/orchestration |
| **LangGraph supervisor** | Supervisor hub-and-spoke; workers always report back to supervisor, never peer-to-peer; hierarchical teams for scale; community decision-table: *"How many agents? Start with 2-3"*; biggest risk = infinite routing loops | https://pypi.org/project/langgraph-supervisor/ ; https://myengineeringpath.dev/genai-engineer/langgraph-multi-agent |
| **Roo Code / Cline custom modes** | Built-in modes: Code, Architect, Ask, Debug, **Orchestrator (Boomerang)** delegating via `new_task`; custom modes = persona + tool-group ACLs (e.g., docs-writer may edit only `\.(md\|mdx)$`); Cline core is flat (`.clinerules`, no mode discrimination) | https://docs.roocode.com/basic-usage/using-modes ; https://www.thisdot.co/blog/roo-custom-modes ; https://thepromptshelf.dev/blog/roo-code-rules-guide-2026/ |

### Consolidated distinct-role table → coverage vs N1–N10

| # | Distinct specialist role (source systems) | Omega coverage | Verdict |
|---|---|---|---|
| 1 | Orchestrator / lead / triage-router (all 7 systems) | N9 link + Lilith/Ma'at overseers + Kali | ✅ COVERED |
| 2 | QA / test engineer (MetaGPT QA) | N10 verifier | ✅ COVERED — but *code*-test honesty ≠ *model-output* evals (see Q2b) |
| 3 | Security / guardrails specialist (OpenAI guardrail agents; OWASP agentic) | N5 sentinel | ✅ COVERED at appsec depth; agentic-depth gap → Q2c |
| 4 | Context / memory manager (CrewAI memory; Roo memory-bank pattern) | N7 context | ✅ COVERED |
| 5 | Observability / tracing / production debugging (Anthropic reliability lessons) | N8 watchtower | ✅ COVERED |
| 6 | Terminal / infra operator (Magentic-One ComputerTerminal) | N1 sysadmin | ✅ COVERED |
| 7 | Delegation-protocol steward (handoffs, sessions, hop budgets) | N9 link | ✅ COVERED |
| 8 | Data engineering / analysis (MetaGPT Data Interpreter; CrewAI data scientist) | N2 datastore (engine internals, not analysis craft) | 🟡 PARTIAL — acceptable for engine scope |
| 9 | **Citation / provenance auditor** (Anthropic's dedicated Citation Agent) | N8 provenance (M22 `provider_name`) + N10 Skeptical Verifier (future) | 🟡 PARTIAL — no charter owns source-citation audits of research artifacts |
| 10 | **Evals / LLM-as-judge engineer** (Anthropic evals; promptfoo-in-CI culture) | none — N10 governs test honesty of code, not model-output eval harnesses | ❌ NOT COVERED → Q2(b) |
| 11 | **Prompt-injection / agentic-security engineer** (OWASP Agentic Top 10 discipline) | N5 partially (secrets/AppArmor/IA2 = appsec posture) | ❌ DEPTH GAP → Q2(c) |
| 12 | **Documentation writer / DX craft** (Roo docs-writer custom mode; M26 doc standards) | none | ❌ NOT COVERED → Q2(i) |
| 13 | Product manager / requirements (MetaGPT PM) | The Architect personally | ❌ correctly NOT a Node — in a solo-architect engine, requirements originate with the Architect |
| 14 | Software architect / system design (MetaGPT Architect; Roo Architect mode) | Kali / Architect personas | ❌ fleet-level identity, not a Node KB |
| 15 | Web researcher / browser operator (WebSurfer; Anthropic search subagents) | @researcher + sovereign-search fleet | ✅ COVERED at fleet level |

### Convergent findings (Triangulation)

1. **Universal convergence**: every surveyed system lands on *small specialist cast + ONE accountable coordinator + workers that route through the coordinator, never peer-to-peer*. The Omega N1–N10 + universal pager (§1 Universality clause) already matches this canonical shape — N9 is our coordination KB, the pager is our handoff primitive.
2. **Anti-proliferation pressure is explicit across the industry**: OpenAI SDK docs ("add specialists only when the contract changes"), LangGraph community tables ("start with 2–3"), Anthropic (super-linear coordination complexity; the 50-subagent bug), Magentic-One ablations (remaining agents compensate creatively when specialists are removed — i.e., missing coverage self-heals more often than assumed), MetaGPT's own cost table (more roles → fewer human revisions but monotonically higher spend, flattening past ~4 roles). Any N11+ proposal must clear this bar.
3. **Genuinely uncovered domains surfaced by Q1**: model-output evals (→Q2b), agentic-security depth beyond appsec (→Q2c), documentation/DX craft (→Q2i), research-artifact citation auditing (→ foldable into N8/N10 charters rather than a new Node).

---

## Q2 — Emerging Specialist Domains for Local-First AI Runtimes (2026)

Verdict scale: **DURABLE** = multi-year institutional adoption trajectory; **FAD** = hype-cycle artifact. Second axis: *node-worthy* vs *charter-extension* vs *defer*.

### (a) Local model fine-tuning / training ops — 🟢 DURABLE domain / ⏸ DEFER Node → N6 extension

Evidence:
- llama.cpp ships native `llama-finetune`: CPU-only LoRA on GGUF; SLMs ≤3B converge in 15–60 min on 16–32GB RAM (0.5B ≈10–15 min/8GB; SmolLM2-1.7B ≈25–35 min/16GB; pre-training remains unfeasible) — https://meshworld.in/blog/ai/tooling/train-local-llm-cpu-only/ `last_verified: 2026-08-22`
- HF TRL hit v1.0 (Apr 2026): unified SFT/DPO/KTO/ORPO/**GRPO** trainers, pulls Unsloth kernels for 2× SFT speedup — https://codersera.com/blog/fine-tuning-llms-complete-guide-2026/
- Unsloth: 2× faster LoRA, ~70% less VRAM, direct `save_pretrained_gguf` export into llama.cpp/Ollama — https://github.com/unslothai/unsloth ; https://tokoscope.com/articles/unsloth
- LoRA/QLoRA "production-ready across Ollama, LM Studio, vLLM" as of Apr 2026; 500–2,000 curated examples typical — https://www.promptquorum.com/local-llms/fine-tuning-local-llms-lora

Charter sketch if promoted later: *"N-tuner · Training Ops — dataset curation, LoRA/QLoRA/GRPO runs via llama-finetune+Unsloth, adapter→GGUF→model-matrix promotion gates."*
**Ruling**: CPU-feasible for our exact hardware class (Qwen3-1.7B/4B), but the engine has zero training workload today. Fold as dormant sub-domain of **N6 modelgate** (which already owns the model matrix); promote to a real Node only when the first production fine-tune lands.

### (b) Evals & benchmarking harnesses — 🟢 DURABLE / ⭐ STRONGEST NEW-NODE CANDIDATE

Evidence:
- EleutherAI lm-evaluation-harness is the de-facto standard behind the Open LLM Leaderboard; versioned tasks, reproducible JSON results, local HF/vLLM/API backends — https://github.com/EleutherAI/lm-evaluation-harness ; https://lm-evaluation-harness.readthedocs.io/ `last_verified: 2026-08-22`
- promptfoo: open-source eval + red-team CLI built for CI ("test-driven LLM development"), runs entirely locally — https://www.promptfoo.dev/docs/intro/
- LLM-as-judge reaches 80–90% human agreement; 2026 best practice = tiered strategy (automated filter → LLM-judge → human review) + CI regression gating — https://zylos.ai/research/2026-01-16-llm-evaluation-benchmarking
- Anthropic's own production multi-agent system was steered primarily by LLM-as-judge rubrics over ~20 seed queries + human edge-case review — https://www.anthropic.com/engineering/multi-agent-research-system
- Practitioner proof: a solo dev's deterministic tool-calling eval across 13 local models found a harness bug masking the true winner ("check your eval too") — https://www.jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1-local-lm/

Charter sketch: *"N-evaluator · Model Quality — lm-eval/promptfoo harnesses, LLM-as-judge rubrics per task-class, model-matrix selection benchmarks (validates D-585), prompt/model regression gates in CI alongside N10's code tests."*
**Ruling**: N10 verifier explicitly governs *code-test honesty* (C-0/M21/C-11). Nobody owns *model-output* quality — yet the engine's core claims (local-first routing quality, D-585 model matrix, M25 streaming resilience) are all empirical assertions requiring eval infrastructure. Clearest genuine gap found by this study.

### (c) Prompt-injection defense & agentic security — 🟢 DURABLE / 🔧 EXTEND N5 sentinel (not a new Node)

Evidence:
- OWASP GenAI LLM Top 10 **2026** published Aug 3 2026: prompt injection holds #1; excessive agency jumped LLM06→LLM03 (biggest move) — https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ ; https://blog.checkpoint.com/ai-security/reading-the-signals-in-the-owasp-llm-top-10-2026/ `last_verified: 2026-08-22`
- Separate OWASP **Top 10 for Agentic Applications** (Dec 2025): cross-agent prompt injection, persistent-memory tampering, orchestration hijacking, privilege escalation via reasoning, delegated identity abuse — https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security
- Indirect injection present in ~73% of production agentic deployments; only 29% of deploying orgs report security readiness — https://zylos.ai/research/2026-05-16-agentic-ai-security-prompt-injection-defense-stack/
- Architectural defenses (CaMeL dual-LLM taint tracking) neutralize ~⅔ of AgentDojo attacks — containment, never prevention, is the 2026 consensus; red-teaming belongs in CI — https://whysogeek.com/prompt-injection-ai-agents-defense-2026/

N5 amendment sketch: *"agentic threat model (OWASP Agentic Top 10), cross-agent injection surfaces (Hivemind handoffs, MCP tool outputs, web research intake), memory-tamper detection (SoulStore integrity), continuous agent red-team harness."*
**Ruling**: it IS a distinct discipline from classic appsec, but it shares N5's owner and substrate (Tainted Data Protocol ≈ taint-tracking family; IA2 envelopes ≈ agent identity). Extend the charter; revisit a split only if the sentinel queue saturates.

### (d) MCP ecosystem evolution / version-compat management — 🟢 DURABLE / 🔧 DEEPEN N4 bridge

Evidence:
- MCP donated to the Agentic AI Foundation (Linux Foundation) Dec 9 2025, co-founded by Anthropic/Block/OpenAI — governance industrialized — https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation `last_verified: 2026-08-22`
- Revision cadence quarterly-to-biannual: 2024-11-05 → 2025-03-26 (Streamable HTTP, OAuth 2.1) → 2025-06-18 (structured output, elicitation, JSON-RPC batching removed) → 2025-11-25 (tasks, JSON Schema 2020-12) → **2026-07-28** — https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html ; https://github.com/modelcontextprotocol/modelcontextprotocol/releases
- The 2026-07-28 revision is "the largest since launch": stateless core (removes initialize handshake + Mcp-Session-Id), breaking error-code change −32002→−32602, Extensions framework, formal 12-month deprecation policy — https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ ; https://blog.mcpservers.org/posts/mcp-spec-2026-07-28
- Official Registry preview (Sept 2025) adds a federated server-catalog layer to track — https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/

**Ruling**: version churn is now structural, and our own notebooklm-mcp fastmcp/anyio transport crash is the live case study — but the volume fits inside N4's existing MCP Hub ownership. Add standing duty to N4: spec-revision watch (RC→final windows), FastMCP compat pinning, conformance-suite checks.

### (e) WASM / sandboxed code execution — 🟡 Durable industry trend, FAD-for-us-now / ❌ no Node

Evidence:
- Pattern space is mature and well documented: wasmtime fuel/epoch CPU bounds, deny-by-default host imports, host-function-mediated persistent sessions; pattern rated maturity:"adopted" (reviewed 2026-06-08) — https://www.agentpatterns.ai/security/wasm-sandbox-agent-code-execution/ `last_verified: 2026-08-22`
- BUT reference embedders remain alpha-grade (micropython-wasm self-described "not ready to recommend"); Pyodide officially browser/Node-only server-side; full CPython stdlib unavailable — same source
- Escape risk is real: GHSA-2r75-cxrj-cmph (May 2026) WASI `path_open(TRUNCATE)` bypass; hostile-multi-tenant workloads need microVMs instead — same source
- Ecosystem spread confirmed (E2B Firecracker, gVisor, Vercel V8 isolates, Docker ECI) — https://llmwiki.hu/concepts/sandboxed-execution ; NVIDIA's Pyodide browser-sandbox pattern — https://developer.nvidia.com/blog/sandboxing-agentic-ai-workflows-with-webassembly/

**Ruling**: WASM sandboxing solves hostile-tenant / untrusted-third-party-code problems. The engine executes its OWN first-party code under venv sovereignty (M24) with rootless Podman as the existing container boundary — different threat model. Watch-item under N5+N1; revisit only when community WADs can ship third-party executable code.

### (f) Voice / TTS / multimodal I/O — 🟢 DURABLE tech / 📦 product surface, not engine depth / ❌ no Node now

Evidence:
- Kokoro-82M: CPU-only, ~30× real-time, tops local TTS quality charts — https://www.freevoicereader.com/blog/10-minute-local-voice-pipeline `last_verified: 2026-08-22`; Piper edge-optimized (~50× RT, 15–80MB voices) — https://github.com/rhasspy/piper (via https://www.local-llm.net/guides/local-voice-assistant/)
- Full offline assistant stacks commoditized: whisper.cpp+Ollama+Piper documented from ~$100 RPi5 (5–8s latency) to $600–800 tiers (1–2s desktop GPU); measured component RTFs STT≈0.03×, Piper≈0.04× on 8GB fanless hardware — https://www.promptquorum.com/power-local-llm/build-local-voice-assistant-2026 ; https://github.com/tkarim45/offline-speech-translator

**Ruling**: mature commodity components with zero open research frontier for us. This is an Omega Desktop feature (Horizon 4 community tool), not engine depth. No Node; future WAD.

### (g) Semantic compression & context engineering — 🟢 DURABLE / ✅ ALREADY COVERED (N7 + HR workstream)

Evidence:
- Headroom: 62,778 GitHub stars (API-verified 2026-07-27), Apache 2.0, CCR compress-cache-retrieve with SQLite-backed lossless retrieval (~1 ms), 70–95% savings on structured data — https://cc.bruniaux.com/guide/context-engineering-tools ; https://www.alphamatch.ai/blog/headroom-context-compression-ai-agents-2026 `last_verified: 2026-08-22`
- Gateway-layer standardization arriving: agentgateway `contextCompression` wire contract (`/v1/compress`, failOpen guardrails, cache-stability engineering) — https://agentgateway.dev/blog/2026-07-27-optimize-token-cost-with-context-compression ; Edgee Compressor V2 (July 2026)
- Context-rot quantified: instructions deep in a rules file followed ~60% as often as early ones; compact at 70%, not 90% — https://cc.bruniaux.com/guide/context-engineering/
- Deterministic per-tool compression beats session-level LLM summarization on 5 documented failure classes (silent data loss, compression-increases-size, anti-thrashing lockout…) — https://github.com/NousResearch/hermes-agent/issues/39691

**Ruling**: validated as durable AND institutionally ours already (HR post-debut workstream; N7 owns compaction). Amendment: give **N7 context** an explicit "compression-engine evaluation duty" so the HR workstream has a permanent KB home.

### (h) OSS licensing & release compliance — 🟢 DURABLE-but-EPISODIC / 🔧 N3+N5 sub-duty, no Node

Evidence:
- License-change-on-update trap recurs (MIT v1.x → BSL-1.1 v2.x); update automation must diff licenses before merge — https://safeguard.sh/resources/blog/open-source-license-compliance-automation `last_verified: 2026-08-22`
- Transitive-dependency obligations are an automation problem: SPDX identifiers, policy-as-code CI allow/block lists — https://safeguard.sh/resources/blog/open-source-license-compliance-faq
- AI-specific layer emerging fast: EU AI Act Article 53 scanners, AIBOM, model-weight licenses distinct from code licenses — https://github.com/aiexponenthq/license-compliance-checker ; https://arxiv.org/pdf/2606.16292
- MIT vs Apache-2.0 debut decision matrix (patent grant = the decisive difference for infrastructure projects) — https://www.positioniseverything.net/mit-and-apache-2-0-lead-open-source-licensing-in-2025

**Ruling**: one hard gate at public debut (dependency audit, NOTICE files, allowlist policy) then low-frequency maintenance. Assign as **N3 buildmaster** release-gate sub-duty with **N5 sentinel** supply-chain overlap. A full-time licensing Node would be panel bloat.

### (i) Developer-experience / community documentation craft — 🟢 DURABLE / ⚠️ ownership gap → resolve in Q4 synthesis

Evidence:
- llms.txt reached v1.7.0 "Phase 6 standardisation release" (May 2026); Mintlify ships content negotiation serving clean Markdown to agents + `.well-known` conventions — https://codex.danielvaughan.com/2026/06/06/llms-txt-specification-codex-cli-machine-readable-documentation-agent-context/ ; https://www.mintlify.com/blog/context-for-agents `last_verified: 2026-08-22`
- Docs-as-Code 2.0: machine-readable layers (llms.txt + JSON-LD + MCP access) now distinct from human-facing sites — https://www.drexplain.com/press/articles/docs_as_code_2_0_a_new_standard_for_ai_ready_user_documentation/
- Honest adoption read: llms.txt is "a developer-experience play, not an SEO play"; real consumers are IDE agents (Cursor/Cline/Codex CLI) and MCP doc servers (Context7 indexes hundreds of libraries) — https://codersera.com/blog/llms-txt-complete-guide-2026/
- Mastercard-scale reference implementations publish both llms.txt and llms-full.txt with auto-update on doc change — https://developer.mastercard.com/platform/documentation/agent-toolkit/working-with-llmstxt

**Ruling**: durable discipline; internally we already institutionalized it (M26 doc standards, `doc-llm-validate`, sprint `llms-full.txt`). The gap is *community-facing* docs ownership for debut — folded into the final synthesis rather than answered by a standalone Node here.

---

## Q3 — Panel Sizing Science: Coordination Overhead vs Coverage

### Evidence base

| Source | Finding | Source (`last_verified: 2026-08-22`) |
|---|---|---|
| **Brooks, Mythical Man-Month (1975)** | Exact quote: *"If there are n workers on a project, there are (n²−n)/2 interfaces across which there may be communication, and there are potentially almost 2ⁿ teams within which coordination must occur."* Conceptual integrity demands design by one mind / small team; Surgical Team model = 1 chief + specialized support roles | https://stackoverflow.com/questions/1244944/is-the-mythical-man-month-communication-paths-truly-n2 ; https://www.lossless.group/more-about/mythical-man-month |
| **Team Topologies (Skelton & Pais)** | Four team types exist to *reduce cognitive load* on stream-aligned teams; complicated-subsystem teams are justified **only when "complexity is real, not perceived"** — otherwise they become "specialist bunkers" (backlog explodes, stream-aligned keeps waiting); platforms should be "just big enough" | https://martinfowler.com/bliki/TeamTopologies.html ; https://itrevolution.com/articles/four-team-types/ ; https://watchz.io/en-us/insights/team-topologies-four-fundamental-team-types |
| **Brooks' Law applied to agents (2026 practitioner analyses)** | *"Brooks' Law doesn't care whether the actors are carbon-based or silicon-based"*; engineers report that **beyond 2–3 concurrent agents their time shifts to managing agent output**; measured case: 4× individual PR velocity → only 40% cycle-time improvement, delta = pure coordination overhead; remedy = orchestration layer (surgical team: 1 senior + 5 specialized agents ≈ throughput of 5–8 engineers) | https://loomstack.co/blog/mythical-man-month-ai ; https://blog.forret.com/2025/2025-10-26/mythical-agent-month/ |
| **Academic failure data** | Multi-agent LLM systems fail in production at **41–87% rates**, majority attributable to *coordination defects* (spec ambiguity, inter-agent misalignment, verification gaps) rather than base-model capability; MAST taxonomy catalogued 14 failure modes across 1,600+ execution traces; simpler single-agent baselines often match or exceed multi-agent designs at lower cost | https://arxiv.org/html/2605.03310v1 (2026-05-05) |
| **OpenAI practical guide** | *"More agents can provide intuitive separation of concepts, but can introduce additional complexity and overhead, so often a single agent with tools is sufficient"*; split only on complex prompt logic or tool overload (>15 well-differentiated tools manageable; <10 overlapping ones already fail) | https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/ |
| **OpenAI Agents SDK** | *"Start with one agent whenever you can. Add specialists only when they materially improve capability isolation, policy isolation, prompt clarity, or trace legibility."* | https://developers.openai.com/api/docs/guides/agents/orchestration |
| **LangGraph community decision table** | *"How many agents? Start with 2–3. Each additional agent adds latency and cost."* Biggest risk: infinite routing loops | https://myengineeringpath.dev/genai-engineer/langgraph-multi-agent |
| **Anthropic production experience** | Coordination complexity grows super-linearly; early bug: lead spawned 50 subagents for simple queries; required explicit effort-scaling rules and dedup instructions | https://www.anthropic.com/engineering/multi-agent-research-system |
| **Claude Code hard limits** | Max ~10 parallel subagent tasks; nesting depth capped; community rule-of-thumb: delegation earns its cost only when a task reads 10+ files or splits into 3+ independent pieces | https://vibecoding.app/blog/claude-code-subagents-guide |

### DELIVERABLE — Practical ceiling recommendation

**Critical architectural distinction**: our Nodes are *dormant Knowledge Bases paged on demand*, not always-running workers. Brooks' n(n−1)/2 applies to **simultaneously active communicators**, not to the count of chartered domains. A dormant Node costs zero coordination until paged, and our universal pager is hub-and-spoke (any→one), matching the LangGraph/OpenAI supervisor pattern — O(n) routing, not O(n²). This is why 10 Nodes have not (and will not) produce Brooks-style collapse by themselves.

The REAL costs of each additional Node are:
1. **Permanent curation debt** — D-586 Standing Order 8 obliges every Node to maintain a Domain Index + External Sources list forever.
2. **Architect validation bandwidth** — every charter must be written, ratified, and kept fresh (grokster staleness precedent).
3. **Routing ambiguity** — overlapping charters make "which Node do I page?" undecidable, the exact specification-ambiguity class that dominates the 41–87% MAS failure data.

**Recommendation (Triangulated):**
- **Soft ceiling: 13 Nodes. Hard ceiling: 14** (symmetry with the M10 fleet cap of 14 agent files — Nodes are sessions, not files, so no violation either way; the symmetry is deliberate discipline).
- **Charter at most 1–2 new Nodes now** (see Synthesis). Every future proposal must clear the OpenAI test (*"materially improve capability isolation, policy isolation, prompt clarity, or trace legibility"*) AND the Team Topologies test (*"complexity is real, not perceived"*).
- **Growth protocol going forward**: charter a new Node only when ≥3 pages/month hit an existing Node with questions its charter explicitly disclaims (demand evidence, not speculation).
- **Keep concurrently ACTIVE Node sessions ≤3** — this is where the coordination cliff actually bites (LoomStack 2–3 concurrent threshold; Claude Code's own ~10-parallel cap is for shallow fan-out tasks, not deep expert consultations).

---

## Q4 — Personal-Interest Domains as Product Surfaces

### (a) PKM / digital-garden ecosystems (Obsidian/Mem/Logseq)

Evidence: Obsidian remains local-first markdown with the deepest plugin ecosystem (Dataview queries notes like a database, Templater, Smart Connections/Copilot AI plugins — AI arrives via plugins, never native); Logseq is outliner-first with native block references; both plain-text/future-proof; digital-garden publishing actively maintained (oleeskild plugin releasing through Aug 2026) — https://trybuildpilot.com/157-obsidian-vs-logseq-2026 ; https://www.glukhov.org/knowledge-management/tools/obsidian-for-personal-knowledge-management ; https://community.obsidian.md/plugins/digitalgarden `last_verified: 2026-08-22`

Durable expertise if first-class product domain: markdown vault schema design, frontmatter/metadata conventions, Dataview-class query languages, bidirectional-link graph algorithms, sync-conflict resolution, publish pipelines.

**Verdict: MERGE, don't charter.** The engine's MemoryStore (FTS5+sqlite-vec hybrid) already IS a sovereign PKM engine core — N2 datastore and N7 context own the underlying craft. Personal Obsidian usage = user-hobby feature; community PKM integration = future WAD surface.

### (b) Structured esoteric knowledge bases (tarot correspondences, Kabbalah)

Evidence: tarot has genuine structured-data infrastructure TODAY — tarotapi.dev serves card names/descriptions/divinatory meanings keyed to Waite's *Pictorial Key to the Tarot* (1910); tarotoo-tarot ships all 78 RWS meanings as structured PyPI data (Jul 2026); krates98/tarotcardapi (78 cards + images, MIT-class); RoxyAPI commercial tarot API with spreads/upright-reversed semantics — https://tarotapi.dev/ ; https://pypi.org/project/tarotoo-tarot/ ; https://github.com/krates98/tarotcardapi ; https://roxyapi.com/starters/tarot-starter-app `last_verified: 2026-08-22`. Kabbalah software, by contrast, is effectively greenfield: the flagship attempt (SourceForge Astro-Tarot-Kabbalah Tree-of-Life, C#/MSSQL) has been pre-alpha and dead since 2016 — https://sourceforge.net/projects/astrotarotkabbalah/

**Verdict: MERGE into the proposed curator Node as a named domain.** Correspondence-schema design + source-authority discipline (Waite/Golden Dawn traditions) + Mnemosyne migration (D-385) is real, durable, differentiating work — no serious software treats Kabbalistic structures as first-class AI-native data. That makes it a legitimate expert domain; it does NOT make it engine-critical. One Node domain, not four hobbies.

### (c) YouTube/video research automation pipelines

Evidence: pipeline pattern fully commoditized (yt-dlp → 16kHz mono WAV → Whisper/faster-whisper → LLM structuring → cached JSON sidecars) — https://mariusz.blog/blog/building-a-youtube-video-research-pipeline-with-whisper-and-claude ; bulk tooling exists (yt-dlp-transcripts PyPI: playlist/channel/resume support) — https://pypi.org/project/yt-dlp-transcripts/ . BUT hard operational constraints are decisive: YouTube actively blocks cloud/datacenter IPs (HTTP 403 / bot challenges) for audio and video alike since 2024–2025; the only free workaround is browser-cookie auth requiring maintenance every weeks-to-months; CPU transcription of a 60-min talk takes 72–120 min (not GPU-era estimates); ToS gray area acknowledged — https://davidamitchell.github.io/Research/research/2026-02-28-transcript-via-yt-dlp-whisper.html `last_verified: 2026-08-22`

Durable expertise: acquisition-strategy resilience (IP blocks, cookie rot), caching discipline per pipeline stage, WER/model-tier tradeoffs, ToS awareness.

**Verdict: MERGE as sub-domain of the curator Node.** The engine already runs youtube_research_sessions + Carmack strategy work; the expertise is real and ongoing (anti-blocking ops especially), but it is research-plumbing, not a standalone pillar.

### (d) NotebookLM-style AI research curation

Evidence: Google renamed NotebookLM → **Gemini Notebook** (July 2026); **no public consumer API exists**; programmatic access = (1) NotebookLM Enterprise API via Google Cloud (`google-cloud-notebooklm`), or (2) unofficial reverse-engineered wrappers — notebooklm-py (~5.6k stars) with documented session-expiry fragility and invisible rate limits — https://web-clipper-for-notebooklm.com/blog/gemini-notebook-api ; https://gemilab.net/en/articles/gemini-advanced/notebooklm-gemini-api-research-workflow-automation ; https://mlhive.com/2026/04/automating-google-notebooklm-ai-agents-notebooklm-py ; https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks `last_verified: 2026-08-22`

**Verdict: DO NOT charter. Already owned.** The GN post-debut workstream (notebooklm-py[mcp], master_token.json) + NL-1 ticket cover this, and N4 bridge owns the fastmcp/anyio transport-crash case study. Chartering a Node around a vendor integration whose public API doesn't stably exist would be FAD-shaped. Revisit only if the Gemini Notebook API stabilizes into a public contract.

---

## ⚖️ Sovereign Synthesis — Final Recommendation

**CHARTER NOW (evidence-backed):**

> **N11 · evaluator · Model Quality & Evals** — lm-eval/promptfoo harness ownership, LLM-as-judge rubrics per task-class, D-585 model-matrix validation benchmarks, prompt/model regression gates beside N10's code tests. Sole candidate that clears both the OpenAI specialist test and the Team Topologies "real complexity" test on engine-depth grounds alone.

**CHARTER (Architect's call — personal-interest consolidation):**

> **N12 · curator · Knowledge Domains & Personal Corpus** — ONE node unifying four would-be hobbies: PKM craft, esoteric KB stewardship (tarot datasets exist today; Kabbalah/Mnemosyne is greenfield differentiation), yt-dlp/mining ops incl. anti-blocking resilience, and PP-2 web-export mining. Gives the KD post-debut workstream a permanent KB home. If declined, these remain user-hobby features under @researcher — an acceptable outcome.

**AMEND EXISTING CHARTERS (no new Nodes):**
| Node | Amendment | Evidence anchor |
|---|---|---|
| N5 sentinel | += agentic threat model (OWASP Agentic Top 10), cross-agent injection surfaces, memory-tamper detection, red-team-in-CI | OWASP Dec 2025 list; CaMeL containment consensus |
| N4 bridge | += MCP spec-revision watch (RC windows, FastMCP pinning, conformance suite) | 2026-07-28 stateless rewrite |
| N6 modelgate | += training-ops dormant sub-domain (llama-finetune/Unsloth promotion gates) | CPU LoRA feasibility data |
| N7 context | += compression-engine evaluation duty (Headroom-class CCR patterns) | HR workstream needs a KB home |
| N10 verifier | += citation-audit duty (Anthropic Citation-Agent pattern for research artifacts) | Q1 role-gap #9 |
| N3 buildmaster | += licensing/release-compliance gate (SPDX policy, NOTICE, license-diff-on-update) | debut gate + EU AI Act tooling trend |

**DO NOT CHARTER:** WASM sandboxing (threat-model mismatch; watch item under N5+N1) · voice/TTS (Horizon-4 WAD feature) · NotebookLM-specific (GN workstream owns it) · standalone licensing Node (episodic duty).

**CEILING:** soft 13 / hard 14 Nodes; growth only on demonstrated paging demand; active concurrent sessions ≤3.

---

## 📚 Source Register

All sources verified live via websearch/webfetch on **2026-08-22** unless otherwise dated inline. Grouped by question; "evidences" = the specific claim each source supports.

### Q1 — Agent-fleet taxonomies

| # | Source | Date | Evidences |
|---|---|---|---|
| 1 | https://arxiv.org/html/2308.00352v7 | ICLR paper | MetaGPT five SOP roles (PM→Architect→ProjectManager→Engineer→QA); structured artifact handoffs; cost/revisions table |
| 2 | https://docs.crewai.com/concepts/agents | current docs | CrewAI role/goal/backstory triple; per-agent tools/memory/delegation |
| 3 | https://arxiv.org/abs/2411.04468 | 2024-11 | Magentic-One: Orchestrator + WebSurfer/FileSurfer/Coder/ComputerTerminal; Task/Progress Ledger; ablation compensation |
| 4 | https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html | current docs | Magentic-One plug-and-play roster mechanics |
| 5 | https://www.anthropic.com/engineering/multi-agent-research-system | 2025-06-13 | Lead Researcher + parallel subagents + Citation Agent; LLM-as-judge rubrics; 50-subagent bug; effort scaling |
| 6 | https://openai.github.io/openai-agents-python/handoffs/ | current docs | Handoff primitive: triage routes, specialist owns branch |
| 7 | https://developers.openai.com/api/docs/guides/agents/orchestration | current docs | "Start with one agent whenever you can"; specialists only when contract changes |
| 8 | https://pypi.org/project/langgraph-supervisor/ | 2025-02+ | Supervisor hub-and-spoke library |
| 9 | https://myengineeringpath.dev/genai-engineer/langgraph-multi-agent | 2026 guide | Sizing decision table ("start 2–3"); workers never peer-to-peer |
| 10 | https://docs.roocode.com/basic-usage/using-modes | 2025-10/2026 | Roo Code/Architect/Ask/Debug/Orchestrator modes + tool-group ACLs |
| 11 | https://www.thisdot.co/blog/roo-custom-modes | 2025-06 | Custom-mode personas (docs-writer example) |
| 12 | https://thepromptshelf.dev/blog/roo-code-rules-guide-2026/ | 2026-04 | Roo layered rules vs Cline flat `.clinerules` |

### Q2 — Emerging specialist domains

| # | Source | Date | Evidences |
|---|---|---|---|
| 13 | https://meshworld.in/blog/ai/tooling/train-local-llm-cpu-only/ | 2026-07-24 | CPU-only `llama-finetune` LoRA feasible ≤3B on 16–32GB RAM; per-model time/RAM table |
| 14 | https://codersera.com/blog/fine-tuning-llms-complete-guide-2026/ | 2026-05-27 | TRL v1.0 unified SFT/DPO/ORPO/**GRPO** stack; Unsloth/Axolotl/MLX landscape |
| 15 | https://github.com/unslothai/unsloth | current repo | Unsloth speedups, MoE training, GRPO long-context RL |
| 16 | https://tokoscope.com/articles/unsloth | 2026-07-23 | Hardware-tier table; direct GGUF export into llama.cpp/Ollama |
| 17 | https://www.promptquorum.com/local-llms/fine-tuning-local-llms-lora | 2026-06-20 | LoRA/QLoRA production-ready across Ollama/LM Studio/vLLM (Apr 2026); 500–1000 examples norm |
| 18 | https://github.com/EleutherAI/lm-evaluation-harness | current repo | lm-eval = de-facto benchmark standard behind Open LLM Leaderboard |
| 19 | https://lm-evaluation-harness.readthedocs.io/ | current docs | Versioned tasks, reproducible results, local backends |
| 20 | https://www.promptfoo.dev/docs/intro/ | updated 2026-08-21 | promptfoo eval + red-team CLI; CI integration; runs fully locally |
| 21 | https://zylos.ai/research/2026-01-16-llm-evaluation-benchmarking | 2026-01-16 | LLM-as-judge 80–90% human agreement; tiered eval best practice; agent-eval shift |
| 22 | https://www.jdhodges.com/blog/local-llms-on-tool-calling-2026-pt1-local-lm/ | 2026-03-20 | Practitioner deterministic tool-calling eval, 13 local models; harness-bug cautionary tale |
| 23 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | 2026-08-03 | OWASP GenAI LLM Top 10 2026 official release |
| 24 | https://blog.checkpoint.com/ai-security/reading-the-signals-in-the-owasp-llm-top-10-2026/ | 2026-08-17 | Prompt injection #1; excessive agency LLM06→LLM03 biggest move |
| 25 | https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security | 2025-12-09 | Separate OWASP Top 10 for Agentic Applications exists |
| 26 | https://zylos.ai/research/2026-05-16-agentic-ai-security-prompt-injection-defense-stack/ | 2026-05-16 | Indirect injection in ~73% of deployments; only 29% orgs prepared |
| 27 | https://whysogeek.com/prompt-injection-ai-agents-defense-2026/ | 2026-06-22 | CaMeL taint-tracking neutralizes ~⅔ of AgentDojo attacks; defense-in-depth consensus |
| 28 | https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation | 2025-12-09 | MCP donated to Agentic AI Foundation (Linux Foundation) |
| 29 | https://hidekazu-konishi.com/entry/mcp_specification_version_timeline.html | 2026-07-26 | Full MCP revision timeline 2024-11-05 → 2026-07-28 |
| 30 | https://github.com/modelcontextprotocol/modelcontextprotocol/releases | current repo | Official revision releases incl. 2026-07-28 stable |
| 31 | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ | 2026-05-21 | Stateless core; breaking −32002→−32602; Extensions framework; 12-month deprecation policy |
| 32 | https://blog.mcpservers.org/posts/mcp-spec-2026-07-28 | 2026-07-28 | "Largest revision since launch" migration analysis |
| 33 | https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/ | 2025-09-08 | Official federated MCP Registry preview |
| 34 | https://www.agentpatterns.ai/security/wasm-sandbox-agent-code-execution/ | reviewed 2026-06-08 | WASM sandbox four controls; maturity:"adopted"; alpha-implementer + stdlib + CVE caveats |
| 35 | https://llmwiki.hu/concepts/sandboxed-execution | current wiki | Sandbox runtime landscape (E2B/gVisor/V8/WASM trade-space) |
| 36 | https://developer.nvidia.com/blog/sandboxing-agentic-ai-workflows-with-webassembly/ | NVIDIA blog | Pyodide browser-side execution pattern |
| 37 | https://www.freevoicereader.com/blog/10-minute-local-voice-pipeline | 2026-04-21 | Kokoro-82M CPU ~30× RT tops local TTS quality |
| 38 | https://www.local-llm.net/guides/local-voice-assistant/ | 2026-04-08 | Whisper+Ollama+Piper/Kokoro commodity stack; engine comparison table |
| 39 | https://www.promptquorum.com/power-local-llm/build-local-voice-assistant-2026 | 2026-06-19 | Voice assistant hardware tiers $100–$800; latency 1–8s |
| 40 | https://github.com/tkarim45/offline-speech-translator | 2026-06 repo | Measured component RTFs (STT≈0.03×, Piper≈0.04×) on 8GB fanless |
| 41 | https://cc.bruniaux.com/guide/context-engineering-tools | 2026-08-16 | Headroom 62,778 stars (API-verified 2026-07-27); full compression-tool ecosystem map |
| 42 | https://www.alphamatch.ai/blog/headroom-context-compression-ai-agents-2026 | 2026-06-12 | CCR compress-cache-retrieve SQLite-backed reversibility |
| 43 | https://agentgateway.dev/blog/2026-07-27-optimize-token-cost-with-context-compression | 2026-07-27 | Gateway-layer `contextCompression` wire contract; failOpen guardrails; cache stability |
| 44 | https://cc.bruniaux.com/guide/context-engineering/ | 2026-03-25 | Context rot quantified (~60% compliance drop deep in rules files) |
| 45 | https://github.com/NousResearch/hermes-agent/issues/39691 | 2026-06-05 | Deterministic per-tool compression beats LLM summarization on 5 failure classes |
| 46 | https://safeguard.sh/resources/blog/open-source-license-compliance-automation | 2026-07-13 | License-change-on-update trap (MIT→BSL); policy-as-code enforcement |
| 47 | https://safeguard.sh/resources/blog/open-source-license-compliance-faq | 2026-07-05 | SPDX identifiers; transitive-dependency obligations automation |
| 48 | https://github.com/aiexponenthq/license-compliance-checker | current repo | EU AI Act Article 53 + model-license scanning tooling exists |
| 49 | https://arxiv.org/pdf/2606.16292 | 2026-06-15 | AI supply-chain license governance complexity (OSS+CC+model licenses) |
| 50 | https://www.positioniseverything.net/mit-and-apache-2-0-lead-open-source-licensing-in-2025 | 2026-05-26 | MIT vs Apache-2.0 patent-grant decision matrix |
| 51 | https://codex.danielvaughan.com/2026/06/06/llms-txt-specification-codex-cli-machine-readable-documentation-agent-context/ | upd. 2026-08-14 | llms.txt v1.7 standardization phase; DX-not-SEO adoption reality |
| 52 | https://www.mintlify.com/blog/context-for-agents | 2026-01-29 | Content negotiation serving clean Markdown to agents |
| 53 | https://www.drexplain.com/press/articles/docs_as_code_2_0_a_new_standard_for_ai_ready_user_documentation/ | 2026-05-29 | Docs-as-Code 2.0 machine-readable layers |
| 54 | https://codersera.com/blog/llms-txt-complete-guide-2026/ | 2026-05-09 | Honest llms.txt adoption read; IDE-agent/MCP consumers are real |
| 55 | https://developer.mastercard.com/platform/documentation/agent-toolkit/working-with-llmstxt | current docs | Enterprise llms.txt/llms-full.txt reference implementation |

### Q3 — Panel sizing science

| # | Source | Date | Evidences |
|---|---|---|---|
| 56 | https://stackoverflow.com/questions/1244944/is-the-mythical-man-month-communication-paths-truly-n2 | book quote | Exact Brooks formula: (n²−n)/2 interfaces, ~2ⁿ teams |
| 57 | https://www.lossless.group/more-about/mythical-man-month | summary | Brooks' Law mechanisms; Surgical Team; conceptual integrity |
| 58 | https://loomstack.co/blog/mythical-man-month-ai | 2026-03-24 | Brooks' Law for AI agents; 2–3 concurrent-agent coordination cliff; 4× velocity → 40% cycle-time case |
| 59 | https://blog.forret.com/2025/2025-10-26/mythical-agent-month/ | 2025-10-26 | "Adding an autonomous agent to a late project makes it later"; ramp-up→context engineering rebrand |
| 60 | https://arxiv.org/html/2605.03310v1 | 2026-05-05 | MAS production failure 41–87%, majority coordination defects; MAST 14 failure modes / 1600+ traces |
| 61 | https://martinfowler.com/bliki/TeamTopologies.html | 2023-07-25 | Four team types; complicated-subsystem reduces stream-aligned cognitive load |
| 62 | https://itrevolution.com/articles/four-team-types/ | 2023-02-28 | Canonical four-type definitions |
| 63 | https://watchz.io/en-us/insights/team-topologies-four-fundamental-team-types | 2026-06-08 | "Complexity real, not perceived" test; specialist-bunker failure mode |
| 64 | https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/ | current guide | Single-agent default; split criteria (logic complexity, tool overload >15 distinct vs <10 overlapping) |
| 65 | https://vibecoding.app/blog/claude-code-subagents-guide | 2026-08-04 | Claude Code hard limits (~10 parallel, depth caps); delegation break-even rule |

### Q4 — Personal-interest domains

| # | Source | Date | Evidences |
|---|---|---|---|
| 66 | https://trybuildpilot.com/157-obsidian-vs-logseq-2026 | 2026-03-10 | PKM landscape: document-first vs outliner-first; both local-first plain-text |
| 67 | https://www.glukhov.org/knowledge-management/tools/obsidian-for-personal-knowledge-management | 2026-07-15 | Obsidian plugin ecosystem depth (Dataview/Templater/Zettelkasten); privacy posture |
| 68 | https://community.obsidian.md/plugins/digitalgarden | active thru 2026-08 | Digital-garden publishing actively maintained |
| 69 | https://tarotapi.dev/ | current | Structured tarot REST API keyed to Waite's Pictorial Key (1910) |
| 70 | https://pypi.org/project/tarotoo-tarot/ | 2026-07-15 | All 78 RWS meanings as structured open data |
| 71 | https://github.com/krates98/tarotcardapi | current repo | Open-source tarot API w/ 78 cards + images |
| 72 | https://roxyapi.com/starters/tarot-starter-app | 2026 | Commercial tarot API semantics (spreads, upright/reversed) |
| 73 | https://sourceforge.net/projects/astrotarotkabbalah/ | dead since 2016 | Kabbalah software greenfield: flagship attempt pre-alpha/abandoned |
| 74 | https://mariusz.blog/blog/building-a-youtube-video-research-pipeline-with-whisper-and-claude | 2026-02-19 | Canonical yt-dlp→WAV→Whisper→LLM pipeline pattern; per-stage caching |
| 75 | https://pypi.org/project/yt-dlp-transcripts/ | current | Bulk playlist/channel transcript tooling w/ resume |
| 76 | https://davidamitchell.github.io/Research/research/2026-02-28-transcript-via-yt-dlp-whisper.html | 2026-03-07 | Cloud-IP blocking (HTTP 403/bot walls) since 2024–2025; cookie-maintenance burden; CPU transcription reality (72–120 min/60-min talk) |
| 77 | https://web-clipper-for-notebooklm.com/blog/gemini-notebook-api | 2026-03-14 | No public consumer API; NotebookLM→Gemini Notebook rename; notebooklm-py ~5.6k stars |
| 78 | https://gemilab.net/en/articles/gemini-advanced/notebooklm-gemini-api-research-workflow-automation | 2026-03-24 | NotebookLM Enterprise API + Gemini API automation pipeline |
| 79 | https://mlhive.com/2026/04/automating-google-notebooklm-ai-agents-notebooklm-py | 2026-04-07 | Unofficial wrapper fragility: session expiry, invisible rate limits |
| 80 | https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks | upd. 2026-08-18 | Official Enterprise API surface (create/manage notebooks programmatically) |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_gap_web_research ⬡ D-586 calibration ⬡ 2026-08-22*

---

## Continuation 1 — Pre-Onboarding Research (2026-08-22)

**Context**: Architect ratified N11 evaluator · N12 curator · N13 arcana under JEM oversight (third oversight line; §1 amendment pending). This section closes the five remaining external-knowledge gaps before their genesis. Charters feed from Continuation-0 verdicts.

**Local calibration (verified on disk this session)**: `src/omega/eval/` contains `runner.py` (13.4 KB golden-dataset run orchestration), `calibrate.py` (isotonic-regression judge calibration; documents ECE 0.18→0.06 improvement; min judge Mistral-7B Q4_K_M, recommended Qwen3-14B Q4_K_M), `check.py` (`EvalResult` with faithfulness/answer_relevancy/context_precision/context_recall/audience_fit + `EvalChecker` thresholds; `[heritage: ragas-2024]` vocabulary tag).

---

### W1 — Eval tooling SOTA refresh → N11 fuel

| Tool | Current state (`last_verified: 2026-08-22`) | Verdict |
|---|---|---|
| **lm-eval-harness** | **v0.4.12** (2026-05-11; 0.5.0.dev1 pre-release exists). Highlights: 4 new model backends, tensor-parallel for `hf`, TaskManager refactor, BEAR knowledge probe, long-context tasks (LongBench v2, BabiLong, GraphWalks), AIME/MATH500 math reasoning. Python ≥3.10 floor. `local-completions` backend speaks OpenAI-compatible API → works against llama.cpp server; `--device cpu` supported | ⭐ **ADOPT** — model-selection axis |
| **promptfoo** | MIT; YAML-driven test matrices; 40+ red-team plugins (injection, jailbreak, PII); local/custom providers; deterministic + LLM-judge assertions; CI-native | ⭐ **ADOPT (light)** — dual-duty: prompt regression gates AND N5's agentic-security red-team harness |
| **DeepEval** | Apache 2.0; pytest-native; 14+ metrics incl. G-Eval custom rubrics; strongest for CI quality gates in Python teams | 🔍 **TRACK** — overlaps our homegrown `check.py` threshold gating; adopt only if homegrown outgrows |
| **RAGAS** | Purpose-built RAG metrics library | ⛔ **SKIP-as-dependency** — `check.py` already implements the RAGAS metric vocabulary natively; importing would duplicate. Keep as vocabulary reference only |
| **lmms-eval** | Multimodal fork of lm-eval | ⛔ **SKIP** — CPU-only text stack; no multimodal workload |
| **Langfuse / Arize Phoenix** | Eval-plus-observability platforms (self-hostable) | 🔍 **TRACK** — N8 watchtower territory, not N11; revisit if trace-level eval needed |

**Complementarity ruling**: our `eval/` modules own the *application-quality* axis (golden datasets, judge calibration, audience-fit register checks). The two genuine gaps are the *model-selection* axis (lm-eval fills — validate D-585 matrix with small CPU-feasible task subsets) and the *adversarial* axis (promptfoo fills — feeds both N11 and the N5 security amendment). No replacement of homegrown code warranted.

Sources: https://github.com/EleutherAI/lm-evaluation-harness/releases · https://pypi.org/project/lm-eval/ · https://deepeval.com/blog/top-5-llm-evaluation-frameworks · https://qaskills.sh/blog/promptfoo-vs-deepeval-vs-ragas-2026

---

### W2 — yt-dlp anti-blocking SOTA → youtube_worker v1.1.0 knowledge

**Maintainer ground truth** (yt-dlp issue #13067, maintainer absidue): *"The only reliable workaround is downloading a lot less"* — every other workaround is high-maintenance by design. Plan around restraint, not evasion.

**Current playbook (ordered by reliability)**:
1. **Update cadence is load-bearing**: YouTube breaks extractors constantly; fixes land in releases within days but distro packages sit weeks stale. Pin worker to pip/nightly channel; `yt-dlp -U` before every batch run.
2. **PO-token era is canonical**: `wiki/PO-Token-Guide.md` + `wiki/EJS.md` are the authoritative docs; `--extractor-args "youtube:po_token=..."` for strict cases. Player-client tricks rotate — `web_embedded` dodged PO tokens circa Mar 2025 (#12561) but client trust shifts continuously; treat any `player_client=` choice as a perishable config value, not a constant.
3. **Cookie SOP (the incognito trick)**: export cookies for youtube.com from a private window via extension, then close the window WITHOUT logging out (logout kills the session server-side; closing doesn't). Lifespan hours-to-weeks; invalidation accelerates from datacenter IPs. Use a **throwaway account**, never main.
4. **Rate etiquette**: `--sleep-requests 2 --sleep-interval 5 --max-sleep-interval 15 --limit-rate 2M`. Empirical block threshold ≈20–100 downloads per IP before flagging.
5. **Egress reality**: datacenter IPs are heavily bot-flagged (works-on-laptop-fails-on-server is the signature symptom). Residential proxies cost $5–15/GB — uneconomic at scale; the Ryzen host's residential connection is an asset, keep ingestion ON-HOST not in CI/cloud.
6. **Transcript-first strategy**: prefer caption endpoints (`youtube-transcript-api`) over media download where quality suffices — lighter footprint, less flagging surface.

Sources: https://github.com/yt-dlp/yt-dlp/issues/13067 · https://github.com/yt-dlp/yt-dlp/issues/12561 · https://www.cookiehub.pro/guides/youtube-cookies-not-a-bot (2026-08-07) · https://tornadoapi.io/blog/yt-dlp-403-error-fix (2026-03-14) · https://mcp.directory/skills/yt-dlp (PO-Token-Guide/EJS wiki pointers)

---

### W3 — NotebookLM programmatic access: RE-VERDICT

**What changed since Continuation-0**:
- Consumer API: **still not shipped**. Official @Gemini_Notebook confirmed "We are on it!" and even asked followers what MCP servers they'd want (Mar 2025) — but no beta, waitlist, or timeline has materialized since. Enterprise-only API remains the sole official path (GCP project + Gemini Enterprise/Education Premium license).
- Unofficial ecosystem **matured substantially**: `notebooklm-py` v0.8.1 (released 2026-08-14) now ships a 28-tool MCP server, nightly live-API e2e CI against the real service, documented per-tier quota limits, and artifact CRUD. `notebooklm-mcp-cli` (5.8k stars) exposes 43 MCP tools. Known constraints are now characterized: cookies expire every 2–4 weeks; free tier ≈50 queries/day; Google rotates build labels occasionally.

**REVISED VERDICT**: Continuation-0 said "FAD-shaped, do not charter." That **softens to TRACK-with-managed-risk**: the unofficial layer is now production-viable for exactly our regime (low-volume personal curation; the ~50 queries/day free tier fits the GN workstream's 3-account × 30-DR/month envelope). The GN workstream's existing bet (notebooklm-py[mcp] + master_token.json) is validated as correct. **Do not charter a Node for it**; instead give **N12 curator a standing KD-liaison duty**: monitor @Gemini_Notebook announcements + notebooklm-py changelog monthly, and trigger a re-verdict the day an official consumer API ships.

Sources: https://notebookclipper.com/blog/gemini-notebook-api (2026-03-14, still current) · https://pypi.org/project/notebooklm-py/ (v0.8.1, 2026-08-14) · https://github.com/teng-lin/notebooklm-py/blob/main/CHANGELOG.md · https://mcprepository.com/jacob-bd/gemini-notebook-mcp-cli

---

### W4 — Structured esoterica data sources → N13 EXTERNAL_SOURCES P0/P1 queue

**Tarot — mature and licensable**:

| Priority | Source | License | Quality / Maintenance | Notes |
|---|---|---|---|---|
| **P0** | **Tarotoo tarot dataset** — github.com/Tarotoo-com/tarotoo-tarot-dataset (+ HF mirror, PyPI/npm/**MCP server**) | **MIT** | 78 cards × 22 fields; CI-validated; active (created Jul 2026, 72 commits); Zenodo concept DOI 10.5281/zenodo.21268290 | Best-in-class provenance: methodology cites Waite 1911 *Pictorial Key*, Golden Dawn *Book T* decan system for planetary/zodiac attributions, Mathers 1888, Papus 1889. Includes upright/reversed × love/career/mood/spiritual contexts + yes/no values. An MCP server already exists for it — direct N13 integration path |
| P1 | multimodalart/1920-raider-waite-tarot-public-domain (HF) | Public domain | 1920 RWS scans + captions | Image corpus for deck-design work (Era-0 Lilith lineage) |
| P1 | smallcat419/tarot-card-data | **CC0** | Single commit (May 2026) — unmaintained but license-clean | Fallback/merge candidate |
| P1 | Kaggle lsind18/tarot-json | check | 78 cards + RWS scans | Legacy staple |
| P2 | Deckaura 12-dimension dataset (SSRN 6452358, Zenodo 19152918) | check | Kaggle/HF/PyPI/NPM | Adds numerology/archetypal dimensions |

**Kabbalah — the gap is confirmed and it IS the opportunity**:
- Closest existing artifacts: `nosleepcassette/sephiroth` (CLI/TUI study tool cross-referencing Tree of Life vs tarot/Hebrew letters/astrology/**Liber 777** correspondences, with curriculum), `gadicc/magickli` `sephirot.json5` (open-source magick data structures), leweyg correspondence spreadsheets, Global Spiritual Studies' 22-paths/Golden-Dawn attribution tables (July 2026).
- **No maintained, licensed, machine-readable Kabbalah correspondence database exists.** Note the trap: *Liber 777* itself (Crowley) is copyright-encumbered in most editions — correspondences must be sourced from public-domain primaries (Waite, Mathers 1888, Golden Dawn *Book T* c.1890s, Kircher's Oedipus Aegyptiacus for the historical path schema).
- **N13's founding work product**: build the sovereign correspondence database (10 sephiroth × 22 paths × Hebrew letters × tarot × astrology × divine names × archangels) from PD sources, using Tarotoo's methodology documentation + CI-validation pattern as the template. This also serves Mnemosyne migration (D-385).

Sources: https://github.com/Tarotoo-com/tarotoo-tarot-dataset · https://huggingface.co/datasets/Tarotoo/tarotoo-tarot-card-meanings · https://huggingface.co/datasets/multimodalart/1920-raider-waite-tarot-public-domain · https://github.com/smallcat419/tarot-card-data · https://www.kaggle.com/datasets/lsind18/tarot-json · https://github.com/nosleepcassette/sephiroth · https://github.com/gadicc/magickli/blob/master/data/kabbalah/sephirot.json5 · https://globalspiritualstudies.com/kabbalah-tree-of-life-complete-guide (upd. Jul 2026)

---

### W5 — Long-lived expert-session memory patterns → three-tier design review

**VALIDATION — industry converged on our exact shape**: 2026 production consensus is three tiers (in-context / semantic / episodic) mapping cleanly onto ours (live task_id continuation / MemoryStore DB persistence / cold gnosis snapshots). Red Hat's agent-memory architecture adds an agent-scoped-LTM vs shared-LTM hierarchy that mirrors our per-entity `soul.yaml` + shared HALL_OF_RECORDS split. The Node pattern itself (persistent consultable expert sessions with dormant/cold-resume) is consistent with Letta/MemGPT's core-vs-archival OS-memory model. **No structural change recommended.**

**Improvement candidates (selective adoption)**:
1. **Structured gnosis templates** — ADOPT. Zylos/Factory.ai finding: freeform summarization silently loses information; requiring fixed sections (`Session Intent / Files Modified / Key Decisions / Active Goals / Next Steps`) acts as a checklist preventing loss. Amend Standing Order 10's gnosis-file format to mandate these sections.
2. **Write-time fact offload, not compaction-time extraction** — VALIDATES EXISTING; reinforce. Zylos best-practice #4: durable facts belong in structured memory the moment they're established, never retroactively mined from history. This is precisely our soul.yaml L1→L3 pipeline; cite it as precedent in N7/N12 charters.
3. **ACON failure-driven compression loop** — ADOPT (post-debut). Log every failure following a compaction event, diff pre/post context, update compression policy. Measured: 26–54% peak-token reduction while preserving >95% task accuracy (arXiv 2510.00615). Natural fit for the HR workstream's evaluation duty under N7.
4. **Fact-taxonomy + content-addressed IDs** — TRACK. Fastio pattern: classify extracted facts as Facts/Events/Instructions/Tasks with content-addressed IDs retrieved via five channels (FTS, key lookup, raw search, vector, HyDE). Candidate for MemoryStore evolution; HyDE retrieval is the novel channel worth a spike.
5. **Dated JSONL audit trail for compressed context** — VALIDATES EXISTING. AgentScope's ReMe (Apr 2026) persists compressed messages to dated JSONL — same pattern as our `cycle_*.jsonl` background-researcher logs.
6. **Compaction threshold** — VALIDATED. Field consensus ≈75–80% (Zylos) brackets our existing 70% rule; no change needed.

Sources: https://zylos.ai/research/2026-04-21-agent-context-compaction-long-running-sessions/ (2026-04-21) · https://fast.io/resources/ai-agent-memory-compaction-strategies (2026-05-11) · https://next.redhat.com/2026/06/01/from-context-to-dreams-architecting-memory-for-ai-agents/ (2026-06-02) · https://devtoollab.com/blog/ai-agent-memory-architecture (2026-06-22) · https://arxiv.org/pdf/2603.17781v1 (Facts as First-Class Objects; quantifies compaction loss & goal drift) · https://nimblabs.com/blog/persistent-memory-for-llm-agents

---

## Source Register additions (Continuation 1)

| # | Source | Date | Evidences |
|---|---|---|---|
| 81 | https://github.com/EleutherAI/lm-evaluation-harness/releases | v0.4.12 2026-05-11 | Latest lm-eval features: 4 backends, tensor-parallel hf, BEAR, TaskManager refactor |
| 82 | https://pypi.org/project/lm-eval/ | verified 2026-05-11 | Version history 0.4.9→0.4.12; Python ≥3.10 floor; 0.5.0.dev1 pre-release |
| 83 | https://qaskills.sh/blog/promptfoo-vs-deepeval-vs-ragas-2026 | 2026-06-29 | Three-framework triage: ship-choice vs CI-gate vs RAG-debug roles; judge-cost guidance |
| 84 | https://deepeval.com/blog/top-5-llm-evaluation-frameworks | 2026-08-20 | Promptfoo feature set (YAML, red-teaming, local providers); DeepEval Apache-2.0 positioning |
| 85 | https://github.com/yt-dlp/yt-dlp/issues/13067 | 2025-05 | Maintainer position: "only reliable workaround is downloading a lot less" |
| 86 | https://github.com/yt-dlp/yt-dlp/issues/12561 | 2025-03 | `player_client=web_embedded` PO-token dodge; client-trust volatility |
| 87 | https://www.cookiehub.pro/guides/youtube-cookies-not-a-bot | 2026-08-07 | Incognito-window cookie-export recipe; logout-kills-session warning |
| 88 | https://tornadoapi.io/blog/yt-dlp-403-error-fix | 2026-03-14 | Fix-limitation matrix; cat-and-mouse now days-scale; proxy economics ($5–15/GB) |
| 89 | https://mcp.directory/skills/yt-dlp | current | Canonical wiki pointers: PO-Token-Guide.md, EJS.md |
| 90 | https://pypi.org/project/notebooklm-py/ | v0.8.1 2026-08-14 | Active maintenance; MCP guide; quota-tier docs; Gemini Notebook rename note |
| 91 | https://mcprepository.com/jacob-bd/gemini-notebook-mcp-cli | current (upd. ~2026-08-20) | 43 MCP tools; 5.8k stars; internal-API/cookie disclaimer; ~50 queries/day free tier |
| 92 | https://notebookclipper.com/blog/gemini-notebook-api | 2026-03-14 | Consumer API "promised, not materialized"; Enterprise-only official access |
| 93 | https://github.com/Tarotoo-com/tarotoo-tarot-dataset | created 2026-07-07 | MIT 78×22 dataset; Golden Dawn Book T methodology; Zenodo DOI; MCP server; CI validation |
| 94 | https://huggingface.co/datasets/Tarotoo/tarotoo-tarot-card-meanings | 2026 | HF mirror; field schema; RAG-grounding intended use |
| 95 | https://huggingface.co/datasets/multimodalart/1920-raider-waite-tarot-public-domain | current | Public-domain 1920 RWS scan corpus with captions |
| 96 | https://github.com/smallcat419/tarot-card-data | 2026-05-28 | CC0 78-card dataset (unmaintained but license-clean) |
| 97 | https://www.kaggle.com/datasets/lsind18/tarot-json | current | 78 cards + RWS scans legacy dataset |
| 98 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6452358 | 2026-03-22 | 12-dimension tarot interpretation dataset (Zenodo 19152918) |
| 99 | https://github.com/nosleepcassette/sephiroth | current | Tree-of-Life CLI cross-referencing tarot/Hebrew/astrology/Liber 777; curriculum |
| 100 | https://github.com/gadicc/magickli/blob/master/data/kabbalah/sephirot.json5 | current | Open-source sephirot data structures |
| 101 | https://globalspiritualstudies.com/kabbalah-tree-of-life-complete-guide | upd. Jul 2026 | 22-path/Hebrew-letter/tarot attribution system (Golden Dawn); Kabbalah/Cabala/Qabalah distinction |
| 102 | https://zylos.ai/research/2026-04-21-agent-context-compaction-long-running-sessions/ | 2026-04-21 | Four converged compaction strategies; 75–80% threshold; write-time offload principle; MemGPT/Cognee/Zylos patterns |
| 103 | https://fast.io/resources/ai-agent-memory-compaction-strategies | 2026-05-11 | Fact taxonomy (Facts/Events/Instructions/Tasks); 5-channel retrieval incl. HyDE; ACON 26–54% results; ReMe dated-JSONL audit trail |
| 104 | https://next.redhat.com/2026/06/01/from-context-to-dreams-architecting-memory-for-ai-agents/ | 2026-06-02 | Agent-scoped vs shared LTM hierarchy; write-back architecture; memory-type taxonomy |
| 105 | https://devtoollab.com/blog/ai-agent-memory-architecture | 2026-06-22 | In-context/semantic/episodic three-tier convergence; per-use-case architectures |
| 106 | https://arxiv.org/pdf/2603.17781v1 | 2026 | Knowledge Objects for persistent memory; quantified compaction loss & goal drift |
| 107 | https://nimblabs.com/blog/persistent-memory-for-llm-agents | current | Four persistent-memory patterns (curated file/retrieval/scratchpad/summaries) |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_gap_web_research ⬡ Continuation 1 ⬡ N11/N12/N13 pre-genesis ⬡ 2026-08-22*





<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
