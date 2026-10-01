<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N7 Context / Memory & State Knowledge Base
**AP Token**: `AP-N7-CONTEXT-KB-v1.0.0`
**Date**: 2026-08-21
**Miner**: roc_racoon (sole executor, per `data/entities/lilith/workspace/N7_MINING_BRIEF_20260821.md`)
**Scope**: N7 domain — Context Injection Phase 1, compaction/continuity, soul persistence, semantic compression
**Method**: Read-and-digest only. Every claim cites a file path. All sources verified on disk 2026-08-21.

---

## Source Inventory

Verification method: `ls`/`wc -l` pass over every listed path on 2026-08-21. One brief-listed path does not exist (noted in table + Gotchas).

### P0 — Context Injection Phase 1 core

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `docs/specs/context_injection/00_INDEX.md` | Synthesis index | 75 | P0 | Exec summary: ~75K base tokens problem; converged 3-phase solution; G-1 ruling | 2026-08-21 |
| `docs/specs/context_injection/01_GROUND_TRUTH.md` | Empirical measurements | 111 | P0 | Hard numbers: 30,976 base tokens; 86 MCP tools ≈ 10,750 tok/req; compaction config observed | 2026-08-21 |
| `docs/specs/context_injection/02_BUILD_VERDICTS.md` | Verdict doc | 177 | P0 | Ma'at build-side findings: G-1 instruction resolution, G-2 MCP cost, G-8 AGENTS.md | 2026-08-21 |
| `docs/specs/context_injection/03_RUN_VERDICTS.md` | Verdict doc | 264 | P0 | Lilith run-side findings: G-3 subagent inheritance, G-5 compaction, G-6 model routing | 2026-08-21 |
| `docs/specs/context_injection/04_INDUSTRY_PATTERNS.md` | Research digest | 309 | P0 | Researcher strategic findings: caching, compaction, routing industry patterns | 2026-08-21 |
| `docs/specs/context_injection/05_CONVERGENCE_ANALYSIS.md` | Matrix | 133 | P0 | Cross-agent convergence/divergence matrix across 4 research reports | 2026-08-21 |
| `docs/specs/context_injection/06_PHASE_1_PLAN.md` | Plan | 295 | P0 | Config-only plan → ~57K base target (24% reduction) | 2026-08-21 |
| `docs/specs/context_injection/07_PHASE_2_3_ROADMAP.md` | Roadmap | 289 | P0 | Hydration engine, token budget enforcer, upstream PRs (caching, lazy MCP) | 2026-08-21 |
| `docs/specs/context_injection/08_REMAINING_GAPS.md` | Gap list | 143 | P0 | Unresolved questions feeding Carmack review | 2026-08-21 |
| `docs/specs/context_injection/09_CARMACK_DOMAIN_QUESTIONS.md` | Question set | 315 | P0 | 5 domains posed to Carmack for expert review | 2026-08-21 |
| `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` | Review verdicts | 547 | P0 | Carmack verdicts ACCEPT/MODIFY/REJECT per workstream item (⚠️ filename typo "CARMMACK" is real) | 2026-08-21 |
| `docs/specs/context_injection/CONTEXT_INJECTION_PHASE1_IMPLEMENTATION_SPEC.md` | Monolithic spec | 683 | P0* | *Discovered — not in brief list. Appears to be monolithic companion to the 9-file phase1_spec/ | 2026-08-21 |

### P0 — phase1_spec/ (9-file implementation spec)

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `docs/specs/context_injection/phase1_spec/index.md` | Spec index | 97 | P0 | Navigation + status of the 9-file implementation spec | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/01_MANDATES_CONDENSED.md` | Spec file | 36 | P0 | Tier 0 condensed mandates (57-line target) for local models | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/02_OPENCODE_JSON_DIFF.md` | Spec diff | 275 | P0 | Exact opencode.json changes: instructions swap, compaction retune, routing | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/03_SOVEREIGN_COMPACTION_PLUGIN.md` | Plugin spec | 162 | P0 | sovereign-compaction.ts behaviors: trigger, preserve set, heartbeat, fallback | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/04_SKILLS_OPT_IN.md` | Spec file | 134 | P0 | Skills opt-in mechanism; 3 core skills default; frontmatter interaction | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/05_VERIFICATION_TESTS.md` | Test spec | 242 | P0 | Verification tests proving injection reduction claims | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/06_ROLLBACK_PLAN.md` | Rollback spec | 137 | P0 | Rollback triggers and procedure for Phase 1 | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/07_IMPLEMENTATION_ORDER.md` | Order spec | 232 | P0 | CI-1..CI-5 sequence with dependencies and gates | 2026-08-21 |
| `docs/specs/context_injection/phase1_spec/08_ACCEPTANCE_CRITERIA.md` | Acceptance spec | 193 | P0 | Acceptance criteria per CI step | 2026-08-21 |

### P0 — Raw research inputs

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `data/coordination/RESEARCH_EXPLORE_LOCAL.md` | Raw research | 117 | P0 | Empirical raw: version 1.18.19, token counts, T1-T6 tests | 2026-08-21 |
| `data/coordination/RESEARCH_MAAT_BUILD.md` | Raw research | 178 | P0 | Build-side raw: instruction resolution docs evidence, MCP schema cost | 2026-08-21 |
| `data/coordination/RESEARCH_LILITH_RUN.md` | Raw research | 261 | P0 | Run-side raw: compaction behavior, model routing, inheritance nuance | 2026-08-21 |
| `data/coordination/RESEARCH_RESEARCHER_STRATEGIC.md` | Raw research | 347 | P0 | Industry patterns raw: caching/compaction/routing/measurement | 2026-08-21 |

### P0 — Config reality

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `opencode.json` (repo root) | Config | 324 | P0 | Current state: instructions(5), compaction block, 12 agents, plugins, subagent_depth | 2026-08-21 |
| `scripts/codex/MANDATES_CONDENSED.md` | Mandates | 57 | P0 | Existing condensed mandates — canonicality check vs phase1_spec/01 | 2026-08-21 |
| `~/.config/opencode/plugin/` | Directory | **MISSING** | P0 | Brief says "only cline"; directory does not exist at all → sovereign-compaction.ts not installed (execution gap) | 2026-08-21 |

### P1 — Compaction & continuity (M15/M18 history)

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | Strategy | 63 | P1 | 4-tier redundancy system, hydration sequence, session_gnosis.md pattern | 2026-08-21 |
| `.opencode/hooks/session_end.py` | Hook code | 121 | P1 | Session-end hook writing proposed_lessons.yaml (M5/M11) | 2026-08-21 |
| `src/omega/oracle/entity_workspace.py` | Engine code | 609 | P1 | get_soul_prompt() ~L382 + TAINT-GATE: proposed_lessons never injected into identity prompt | 2026-08-21 |
| `src/omega/soul_utils.py` | Engine code | 96 | P1 | Approved-lessons integration closing distillation loop | 2026-08-21 |
| `scripts/validate_soul.py` | Gate script | 153 | P1 | M5/M11 gate; reads `memory/proposed_lessons.yaml` (dual-path hazard) | 2026-08-21 |
| `scripts/check_mandate_compliance.py` | Gate script | 454 | P1 | Mandate compliance checks incl. M5/M11 | 2026-08-21 |
| `SOVEREIGN_MANDATES.md` §M15,§M18 (+M11,M23) | Law | 239 (file) | P1 | Mandate text bearing on context/memory | 2026-08-21 |
| `data/entities/lilith/workspace/COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md` | Prior plan | 151 | P1 | Lilith's prior compaction remediation thinking | 2026-08-21 |
| `data/entities/lilith/proposed_lessons.yaml` | Soul data | 213 | P1 | Structure only (field names, lesson format) | 2026-08-21 |
| `data/entities/lilith/soul.yaml` | Soul data | 18 | P1 | Structure only | 2026-08-21 |

### P2 — Compression future (HR workstream)

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md` | Research | 476 | P2 | Headroom findings, 40-90% savings claims | 2026-08-21 |
| `docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md` | Spec | 1604 | P2 | Phase 2 trigger gates for headroom integration | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/index.md` | Spec index | 201 | P2 | Middleware architecture overview | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/01_HEADROOM_MIDDLEWARE_CLASS.md` | Spec | 607 | P2 | Middleware class design | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/02_CONTENTROUTER_CONFIG.md` | Spec | 289 | P2 | ContentRouter configuration | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/03_MODELGATEWAY_INTEGRATION.md` | Spec | 387 | P2 | ModelGateway integration points | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/04_RAG_RETRIEVAL_INTEGRATION.md` | Spec | 486 | P2 | RAG retrieval integration | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/05_MCP_TOOL_SCHEMA_COMPRESSION.md` | Spec | 537 | P2 | MCP tool-schema compression (attacks the 10.8K/req cost) | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/06_ENTITY_CONTEXT_COMPRESSION.md` | Spec | 481 | P2 | Entity-context compression | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/07_CCR_STORE_INTEGRATION.md` | Spec | 875 | P2 | CCR store integration | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/08_CONFIGURATION.md` | Spec | 507 | P2 | Configuration surface | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/09_ERROR_HANDLING_METRICS.md` | Spec | 616 | P2 | Error handling + metrics | 2026-08-21 |
| `docs/specs/qdrant_headroom/headroom_middleware/10_VERIFICATION_TESTS.md` | Spec | 983 | P2 | Verification tests for middleware | 2026-08-21 |

### P3 — Related research (2026-08-19 batch)

| Path | Type | Lines | Priority | Relevance | last_verified |
|------|------|-------|----------|-----------|---------------|
| `docs/research/R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md` | Research | 384 | P3 | Compression/distillation techniques survey | 2026-08-21 |
| `docs/research/R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md` | Research | 351 | P3 | Planner/executor window strategy | 2026-08-21 |
| `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md` | Research | 553 | P3 | Role-aware prompting | 2026-08-21 |
| `docs/research/R_DYNAMIC_PROMPT_BUILDERS_20260819.md` | Research | 258 | P3 | Dynamic prompt builders | 2026-08-21 |
| `docs/research/R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md` | Research | 802 | P3 | ⚠️ Not in seed list — discovered by N7; blueprint companion to builders doc | 2026-08-21 |
| `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` | Report | 1544 | P3 | Memory systems definitive report (zswap ADR context) | 2026-08-21 |

**Inventory totals**: 57 rows listed; 56 sources exist on disk; 1 missing (`~/.config/opencode/plugin/`). Two discovered-not-in-brief sources flagged (*).

---

## Per-Source Digests

### docs/specs/context_injection/00_INDEX.md
`last_verified: 2026-08-21` · Author Kali, model nemotron-3-ultra-free, dated 2026-08-20.
- **Problem statement**: Omega injects **~75K tokens base** (up to ~110K with all skills/agents) per session; **86 MCP tool schemas = 10.8K tokens/request** (`00_INDEX.md:47`). Violates M18; threatens local viability (Qwen3-1.7B = 4K–8K ctx).
- **Converged solution**: Phase 1 config-only → **~57K base (24% reduction)** + structural routing saves ~67% on subagent work (`00_INDEX.md:50`). Phase 2 tooling (hydration engine, token budget enforcer, local token counter). Phase 3 upstream PRs (prompt caching topology, lazy MCP loading, dynamic tool registration) (`00_INDEX.md:52-54`).
- **G-1 ruling preview**: Ma'at (docs)=NO vs Explore (test)=YES → **Assume NO**, create `AGENTS.md` as guaranteed injection path (`00_INDEX.md:56-57`).
- **Carmack review targets** (5): MCP schema overhead, compaction architecture (1M ctx / 50K preserved), structural routing + subagent inheritance nuance, per-tier budget enforcement vs per-message tracking, Qwen3-1.7B viability at 31K base prompt (`00_INDEX.md:59-64`).
- Open thread: none — this is pure navigation/exec summary.

### docs/specs/context_injection/01_GROUND_TRUTH.md
`last_verified: 2026-08-21` · Explore agent empirical measurements. Answers Extraction Q1.
- **T1 version**: opencode `1.18.19`, binary at `/home/arcana-novai/.opencode/bin/opencode` (`01_GROUND_TRUTH.md:10`).
- **T2 system prompt sizes** (chars ×0.25 ≈ tokens):
  - Base (instructions + default agent + config + MCP): 123,903 chars ≈ **30,976 tokens** (`01_GROUND_TRUTH.md:18`)
  - Base + all 22 skills: 216,781 chars ≈ **54,195 tokens** (`01_GROUND_TRUTH.md:19`)
  - Base + skills + all 14 agents: 298,773 chars ≈ **74,693 tokens** (`01_GROUND_TRUTH.md:20`)
- **Base component breakdown** (`01_GROUND_TRUTH.md:26-31`): instruction files (5 from opencode.json) 67,895 chars ≈ 16,974 tok; default agent kali.md 3,996 ≈ 999; opencode.json 9,012 ≈ 2,253; MCP schemas 86 tools ≈ 43,000 chars ≈ 10,750 tok.
- **T3 instruction resolution test**: YES empirically (kali quoted SOVEREIGN_MANDATES first sentence without read tool) but flagged as possibly AGENTS.md discovery; **assume NO for planning** (`01_GROUND_TRUTH.md:37-44`).
- **T4 MCP count**: 86 tools via `@mcp.tool()` in `hub_tools/tools.py`; category breakdown Oracle 8, Hivemind 7, GitHub ~10, Project/Workbench ~15, Research/Mining ~15, Legacy ~15 etc. (`01_GROUND_TRUTH.md:50-68`).
- **T5 subagent inheritance**: INHERITANCE=PARENT — full parent system prompt; Lilith nuance: fresh assembly but forked conversation history (~110K) (`01_GROUND_TRUTH.md:76-83`).
- **T6 source findings**: no instruction caching (re-read each session); compaction observed as auto/prune/tail_turns=3/preserve_recent_tokens=40000/reserved=10000; trigger = context exceeds limit minus reserved; skills load on-demand not pre-injected; MCP schemas injected per-request (`01_GROUND_TRUTH.md:89-98`).
- Key insight: 31K base fits Nemotron (1M) but **exceeds Qwen3-1.7B (4K–8K)**; subagent inheritance multiplies cost (`01_GROUND_TRUTH.md:104-108`).

### docs/specs/context_injection/02_BUILD_VERDICTS.md
`last_verified: 2026-08-21` · Ma'at build-side. Answers part of Q9.
- **G-1 verdict NO (docs)**: Official V2 docs quote — "V2 currently parses and retains this field but does not resolve its entries into instruction sources… Use `AGENTS.md` for active V2 instructions" (`02_BUILD_VERDICTS.md:16`). Evidence: GitHub #4758 (closed 2026-03-26), #11317 (glob silently dropped); source `instruction.ts` handles only AGENTS.md/CLAUDE.md/CONTEXT.md, walks up filesystem, stops at first found (`02_BUILD_VERDICTS.md:18-22`).
- **Implication**: our 5 doctrine files (~80K tokens listed in opencode.json instructions) are **not injected** in V2 (`02_BUILD_VERDICTS.md:29-30`).
- **G-2 MCP cost**: 86 tools; per-tool 100–150 tok conservative → **10,320 tok/request**; complex estimate 200/tool → 17,200 (`02_BUILD_VERDICTS.md:62-67`). Benchmarks cited: GitHub #35376 50–200 tok/tool; Playwright 156/tool; Anthropic production 55K–134K for 150+ tools (`02_BUILD_VERDICTS.md:55-57`). Finding: MCP overhead **exceeds the mandate content we're trying to inject**, and it's every request (`02_BUILD_VERDICTS.md:78`). No lazy loading in V2; track #35376; Anthropic "Code Mode"/Bifrost achieves 92–98% reduction but needs gateway (`02_BUILD_VERDICTS.md:81-84`).
- **G-8 AGENTS.md discovery**: loads ALL discovered files combined (global `~/.config/opencode/AGENTS.md` always; project root→Location chain; nested discovery on `read` of target dirs, injected once per session nearest-first). `instructions[]` arrays NOT merged — closest config wins entirely (`02_BUILD_VERDICTS.md:94-109`). Split-file options table: only single concatenated AGENTS.md or nested-on-read work (`02_BUILD_VERDICTS.md:111-119`).
- **Phase 1 build recommendations**: (1) create root AGENTS.md by concatenating SOVEREIGN_MANDATES + ORACLE_STACK + MASTER_SYNTHESIS + ARK_BLUEPRINT + CREDITS (`02_BUILD_VERDICTS.md:128-131`); (2) keep instructions array as documentation/future-proofing; (3) global AGENTS.md for personal rules; (4) accept MCP overhead now; (5) agent-level instructions in `.opencode/agents/*.md` DO work (loaded as agent prompts, not via global array) (`02_BUILD_VERDICTS.md:161-162`).

### docs/specs/context_injection/03_RUN_VERDICTS.md
`last_verified: 2026-08-21` · Lilith run-side. Answers parts of Q3/Q4/Q7.
- **G-3 verdict YES (partial inheritance)**: subagent does not share context 100%; inherits prompt+prior work, own session, filtered permissions (`03_RUN_VERDICTS.md:14`). GitHub #2588 implemented task-tool context inheritance; #6535 shows compaction breaks subagent context (`03_RUN_VERDICTS.md:16-19`). Test: spawned subagent reported ~110K tokens same as parent — conversation history forks, system prompt rebuilt fresh (`03_RUN_VERDICTS.md:31`).
- **Isolation levers** (`03_RUN_VERDICTS.md:24-29`): `mode:"subagent"` clean prompt; custom `prompt:"{file:...}"` overrides entirely; permission deny filters; `hidden:true`.
- **G-5 compaction mechanics**: fires when `token_usage > (context_limit - output_limit)` per `packages/opencode/src/session/compaction.ts`; default reserved buffer 10K configurable; PRUNE_PROTECT protects last 40K of tool output; PRUNE_MINIMUM only prunes if >20K prunable (`03_RUN_VERDICTS.md:39-45`). For nemotron-3-ultra-free (1M ctx/128K out): triggers ~872K; preserves 40K+10K=50K post-compaction (`03_RUN_VERDICTS.md:58-60`).
- **Pre-compaction hook EXISTS**: plugin hook `experimental.session.compacting` fires before LLM generates continuation summary; can push context into `output.context` or replace entire `output.prompt` (`03_RUN_VERDICTS.md:64-87`). Disable switch: `OPENCODE_DISABLE_AUTOCOMPACT=1` (`03_RUN_VERDICTS.md:87`).
- **G-6 routing FULLY SUPPORTED**: `agent.<name>.model` per-agent; **subagents invoked via task() use the invoking primary agent's model, not their own config** (`03_RUN_VERDICTS.md:150-156`). Example config routes researcher→lmstudio/qwen3-4b-thinking, node/verity→qwen3-1.7b (`03_RUN_VERDICTS.md:104-145`). Savings: 4/6 agents local ≈ 67% reduction (`03_RUN_VERDICTS.md:169`).
- **Lilith's proposed compaction retune**: tail_turns 5, preserve_recent_tokens 80000, reserved 20000 for 1M-context models (`03_RUN_VERDICTS.md:241-249`) — NOTE: diverges from spec's buffer 50000/keep 20000 direction (see Gotchas).
- Proposed sovereign-compaction plugin sketch injects M1/M7/M11/M15/M23 + OMEGA_ENTITY/OMEGA_PHASE env + SESSION_ANCHOR pointer into `output.context` (`03_RUN_VERDICTS.md:196-210`).

### docs/specs/context_injection/04_INDUSTRY_PATTERNS.md
`last_verified: 2026-08-21` · Researcher/Jem-Analyst strategic research, 28+ web sources. Answers G-4..G-7 industry context.
- **G-4 caching**: OpenCode V2 has built-in provider-agnostic `applyCaching()` in `transform.ts:170-207` — Anthropic cacheControl ephemeral on first 2 system + last 2 messages; OpenAI promptCacheKey=sessionID; Bedrock cachePoint; OpenRouter ephemeral (`04_INDUSTRY_PATTERNS.md:29,40-57`). Anthropic economics: writes ~1.25×, reads ~0.1× (90% discount), min prefix 1024–2048 tok, max 4 breakpoints (`04_INDUSTRY_PATTERNS.md:59-63`). LangGraph pattern: static-first ordering tools→system→messages, never mutate tools mid-session (`04_INDUSTRY_PATTERNS.md:65`).
- **G-5 compaction comparison**: OpenCode V2 preflight buffer default **20k**, keep.tokens default **15k**; Claude Code ~95% capacity, 3-tier microcompaction→auto→manual; Codex CLI opaque blob + re-read 5 files (~50k); LangGraph composable middleware; CrewAI boolean overflow (`04_INDUSTRY_PATTERNS.md:79-88`). OpenCode formula: `estimated tokens > context limit - max(requested output, buffer)` (`04_INDUSTRY_PATTERNS.md:93-97`). Pre-compaction hook is a universal gap across frameworks (`04_INDUSTRY_PATTERNS.md:106`).
- **G-6 routing**: RouteLLM 85% cost cut at 95% quality; FrugalGPT up to 98% via cascade; **structural routing preferred** — fixed model per role avoids classifier latency/adversarial surface/cascade failures, captures most savings (`04_INDUSTRY_PATTERNS.md:155-160,167`).
- **G-7 measurement**: OpenCode SQLite per-message tokens {input,output,cached,cacheCreation} + cost; OTel GenAI conventions; Langfuse exclusive-bucket conversion critical (OpenAI inclusive vs Anthropic exclusive) (`04_INDUSTRY_PATTERNS.md:177,190-225`). Security rule: never log raw prompts to third-party SaaS — metadata-only satisfies 90% of ops needs (`04_INDUSTRY_PATTERNS.md:242`).
- **Omega applicability**: immediate `buffer:50000` + per-agent model config + OTel export + condensed mandates (57 lines) as Tier 0 cached block + opt-in skills with `auto_load` (`04_INDUSTRY_PATTERNS.md:261-270`). Phase 2: hydration engine checkpoint at 80% usage; token budget enforcer tiers pinned 2k/role 4k/dynamic 8k trim-from-lowest-priority; local token counter tiktoken (`04_INDUSTRY_PATTERNS.md:271-275`).
- Adversary dialectic note: OpenCode's plugin hook fires *during* compaction not before; hydration must checkpoint at 80% via background monitor; SQLite fields are per-message not per-agent so budget enforcement needs aggregation layer (`04_INDUSTRY_PATTERNS.md:285`).

### docs/specs/context_injection/05_CONVERGENCE_ANALYSIS.md
`last_verified: 2026-08-21` · Kali cross-agent matrix.
- **Convergence matrix** (`05_CONVERGENCE_ANALYSIS.md:11-20`): G-1 assume NO→AGENTS.md; G-2 10.8K/request converged number; G-3 YES conversation forks/system prompt fresh; G-4 leverage Phase 3; G-5 build sovereign-compaction plugin; G-6 Phase 1 config; G-7 enable OTel; G-8 single concatenated AGENTS.md.
- **Contradiction resolution G-1**: docs+source > single test; assume NO (`05_CONVERGENCE_ANALYSIS.md:26-32`).
- **Five ADRs accepted** (`05_CONVERGENCE_ANALYSIS.md:70-98`): ADR-001 AGENTS.md primary injection vehicle (loses modularity, guarantees injection); ADR-002 structural routing not dynamic; ADR-003 accept MCP overhead Phase 1; ADR-004 sovereign compaction plugin; ADR-005 skills opt-in core-only — **22 skills = 23K tokens when all loaded; auto_load true only for research, spec-generator, knowledge-miner**.
- **Risk table** (`05_CONVERGENCE_ANALYSIS.md:104-111`): highest-impact risks = subagent inheritance breaks local viability (High/High), compaction loses sovereign context (Medium/Critical).
- **Priority matrix** (`05_CONVERGENCE_ANALYSIS.md:117-130`): Phase 1 five low-effort items incl. compaction threshold tuning; Phase 2 hydration engine/token budget/local counter; Phase 3 caching topology PR, lazy MCP PR, dynamic tool registration.

### docs/specs/context_injection/06_PHASE_1_PLAN.md
`last_verified: 2026-08-21` · Status READY FOR EXECUTION; authority = `DEBUT_REMEDIATION_MANUAL_20260817.md` §5; all config-only, reversible (`06_PHASE_1_PLAN.md:3-6`). Answers part of Q3/Q17.
- **5 deliverables** (`06_PHASE_1_PLAN.md:11-17`): AGENTS.md concat; opencode.json update; sovereign-compaction plugin at `~/.config/opencode/plugin/sovereign-compaction.ts`; skill frontmatter auto_load; debug verification test. All owner Kali, all ⏳ (not done).
- **AGENTS.md recipe**: `cat SOVEREIGN_MANDATES.md ORACLE_STACK.md docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md CREDITS.md > AGENTS.md` → ~80K chars ≈ ~20K tokens (`06_PHASE_1_PLAN.md:23-32`).
- **Target opencode.json state** (`06_PHASE_1_PLAN.md:75-136`): instructions → `["AGENTS.md"]`; compaction → tail_turns 5 / preserve_recent_tokens **80000** / reserved **20000**; plugin array +sovereign-compaction.ts; per-agent model+variant (kali nemotron high, researcher lmstudio/qwen3-4b-thinking high, maat nemotron medium, lilith nemotron high, node qwen3-1.7b low, verity qwen3-1.7b low + mode subagent + prompt file + deny permissions + hidden).
- ⚠️ **Compaction numbers here (80K/20K) differ from phase1_spec's buffer 50000/keep 20000 direction and from Carmack's modification — see Gotchas + Q3 analysis.**
- **Skills opt-in list** (`06_PHASE_1_PLAN.md:188-229`): auto_load true ONLY research, spec-generator, knowledge-miner; false for legacy-pattern-miner, blitz-tunnel, blitz-validate, git-secret-scrub, hf-cli, omega-doc-architect, pr-readiness-checker, provider-validator, sovereign-refinement-protocol, sovereign-search. Rationale: 22 skills = 23K tokens all-loaded → ~150 tokens for 3 core skills metadata (`06_PHASE_1_PLAN.md:231`).
- **Verification tests** (`06_PHASE_1_PLAN.md:237-257`): AGENTS.md injection quote test; per-agent model identity tests; plugin load grep; auto_load grep. Success criteria checklist of 5.
- **Post-Phase-1 token budget table** (`06_PHASE_1_PLAN.md:263-269`): Tier 0 pinned ~45K (AGENTS.md 80K chars + MCP 10.8K + env 3K); Tier 1 role/session ~2K; Tier 2 dynamic 8K budget; Tier 3 observation 2K → **~57K base vs 75K measured = 24% reduction**.
- **Rollback**: git checkout opencode.json; rm AGENTS.md; rm plugin file; revert SKILL.md frontmatter (`06_PHASE_1_PLAN.md:277-292`).

### docs/specs/context_injection/07_PHASE_2_3_ROADMAP.md
`last_verified: 2026-08-21` · Status PLANNED post-debut; deps: Phase 1 complete + PUBLIC-DEBUT-01 shipped (`07_PHASE_2_3_ROADMAP.md:3-4`).
- **Phase 2 components**:
  - **HydrationEngine** `src/omega/hydration/hydration_engine.py` — on_session_start cascade checkpoint→session JSONL(last 400)→daily memory; on_compaction_warning at 80% usage writes SessionCheckpoint{recent_exchanges(5), active_task, pending_proposals, decisions_in_flight}; on_compaction verifies mandates/entity/anchor survived, re-injects from checkpoint if missing (`07_PHASE_2_3_ROADMAP.md:15-49`). SLA: hydration <2s p95 (`07_PHASE_2_3_ROADMAP.md:56`).
  - **TokenBudget** `src/omega/oracle/token_budget.py` — TIER_BUDGETS pinned 2000 / role_session 4000 / dynamic 8000 / observation 2000; complexity multiplier 0.5–2.0; trim from lowest priority preserving pinned; OTel usage report (`07_PHASE_2_3_ROADMAP.md:67-88`). Task-type budgets: classification 50–200 … legal/financial 4000+ (`07_PHASE_2_3_ROADMAP.md:92-98`).
  - **LocalTokenCounter** — model-family tokenizers qwen3/nemotron + tiktoken cl100k fallback; pre-flight warn before `omega talk`/`summon` (`07_PHASE_2_3_ROADMAP.md:109-129`).
  - **SessionSummarizer** — 3-level hierarchy (per-turn → per-task → session); progressive compression L3→L2→L1→raw preserving decisions/active files/pending proposals/entity context (`07_PHASE_2_3_ROADMAP.md:139-151`).
- **Phase 3 upstream PRs**:
  - Caching topology: current assembly `[providerPrompt, envBlock, instructions, agentPrompt, userOverride]` is cache-unfriendly; proposed stable-first order with cache_control breakpoints on providerPrompt/toolSchemas/condensedMandates in `llm.ts`; expected 60–80% input cost cut (`07_PHASE_2_3_ROADMAP.md:162-183`).
  - Lazy MCP loading: `lazy_load` flag + task-based tool filtering in resolveTools(); expected 90%+ schema reduction (only 5–10 tools needed) (`07_PHASE_2_3_ROADMAP.md:192-214`).
  - Tool profiles config sketch: dev/deploy/debug/research profiles mapped per agent (`07_PHASE_2_3_ROADMAP.md:224-238`).
  - Local model caching investigation: llama.cpp prefix caching × GGUF × applyCaching integration open (`07_PHASE_2_3_ROADMAP.md:242-251`).
- **Dependency graph + validation checkpoints** (`07_PHASE_2_3_ROADMAP.md:256-286`): Phase 1 gate = global system prompt <60K tokens; Phase 2 gate = hydration <2s, 95% compaction recovery; Phase 3 gate = cache hit >60%, production canary 10%.

### docs/specs/context_injection/08_REMAINING_GAPS.md
`last_verified: 2026-08-21` · 10 gaps RG-1..RG-10 posed to Carmack pre-review.
- 🔴 Critical (block Phase 1): RG-1 Qwen3-1.7B 4K–8K ctx vs 31K base — 4–8× over context window; options radical reduction/tool profiles/Qwen3-4B/hybrid (`08_REMAINING_GAPS.md:12-22`). RG-2 86 tools 10.8K/req — split servers vs lazy load vs tool profiles vs accept (`08_REMAINING_GAPS.md:24-34`). RG-3 subagent inherits parent model — parent-local/@agent/task-wrapper/accept (`08_REMAINING_GAPS.md:36-46`).
- 🟡 High (block Phase 2): RG-4 heterogeneous compaction thresholds — Qwen3-1.7B 8K ctx with 20K buffer = compaction ALWAYS; options per-model config/dynamic buffer 10%/disable env var/custom plugin (`08_REMAINING_GAPS.md:52-62`). RG-5 per-agent budget enforcement location (`08_REMAINING_GAPS.md:64-73`). RG-6 tiktoken inaccurate for non-OpenAI tokenizers (`08_REMAINING_GAPS.md:75-84`).
- 🟢 Medium: RG-7 local caching worth it? RG-8 gateway vs in-process OTel; RG-9 priority among lazy-load/profiles/split-servers; RG-10 can maat/lilith go local (`08_REMAINING_GAPS.md:90-130`).
- Decision framework requested: Verdict/Rationale/Implementation/Risk per gap (`08_REMAINING_GAPS.md:134-141`).

### docs/specs/context_injection/09_CARMACK_DOMAIN_QUESTIONS.md
`last_verified: 2026-08-21` · 8 question sets targeted at Carmack expertise.
- Q1 hardware-honest local architecture: 31K vs 4K–8K conflict framed as "bug is just a bug" vs "adversarial alchemy"; option 1 = strip to MANDATES_CONDENSED only (~1.5K tok) defer doctrine to Tier 2 (`09_CARMACK_DOMAIN_QUESTIONS.md:30-37`). SequentialModelLoader claims to verify: no-mmap+mlock, n_swa removed (SWA CUT), --cache-prompt compat (`09_CARMACK_DOMAIN_QUESTIONS.md:39-50`). q8_0 KV standard question (`09_CARMACK_DOMAIN_QUESTIONS.md:52-55`).
- Q2 MCP: "Is 86 tools in one MCP server an architectural error?" — monolith violates M2 framing; split domain servers vs lazy PR vs profiles vs accept (`09_CARMACK_DOMAIN_QUESTIONS.md:61-70`). Schema compression options: minimal schema/schema refs/binary encoding (`09_CARMACK_DOMAIN_QUESTIONS.md:72-82`).
- Q3 compaction & hydration: heterogeneous windows; hydration as plugin vs sidecar vs in-process library; "checkpoint BEFORE compaction (at 80%), not during" — what if hook crashes or gets compacted away (`09_CARMACK_DOMAIN_QUESTIONS.md:103-121`).
- Q4 budget enforcement location matrix engine/gateway/plugin/OTel-rules; llama_tokenize() via ctypes vs ±20% error vs OOMProtector-only (`09_CARMACK_DOMAIN_QUESTIONS.md:127-153`).
- Q5 routing completeness: quality floor per role kali/maat/lilith; subagent inheritance workarounds ranked by framework-friendliness (`09_CARMACK_DOMAIN_QUESTIONS.md:159-179`).
- Q6 headroom reality check: synthetic benchmarks (JSON 83%, logs 94%, code 92%, RAG 40–60%) vs real Omega outputs; latency break-even at 10ms (`09_CARMACK_DOMAIN_QUESTIONS.md:185-199`).
- Q7 over-engineering audit M19/M23: which Phase 2/3 items are solution theater; validator service CUT or KEEP (`09_CARMACK_DOMAIN_QUESTIONS.md:205-225`).
- Q8 memory map: recalc with --no-mmap --mlock (no persistent weight cache); zswap+NVMe vs zRAM final verdict (zRAM was locking 4.1GB in compression buffers; ADR-2026-08-10-001, D-526/D-581/D-584 ratified) (`09_CARMACK_DOMAIN_QUESTIONS.md:231-264`).

### docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md
`last_verified: 2026-08-21` · Status FINAL VERDICT, model nemotron-3-ultra-free. **Overall: Phase 1 ACCEPTED WITH MODIFICATIONS; Phase 2/3 ACCEPTED WITH 40% CUTS** (lines 12-14). Primary source for Extraction Q2.

**Per-workstream verdicts**:
| Item | Verdict | Key content |
|------|---------|-------------|
| Q1.1 31K vs 4K–8K | **MODIFY** | Radical base reduction; "accept cloud fallback for Tier 0" DELETED (violates M7); Qwen3-1.7B demoted to critic-only; Tier 0 matrix = Qwen3-4B planner + Qwen3-4B-Thinking executor + Qwen3-1.7B critic (`:22-39`) |
| Q1.2 sequential loading | **ACCEPT** | `--no-mmap --mlock` correct; llama_free() unmaps mmap → persistent mmap cache harmful; one model at a time, peak 7.5GB/headroom 8.5GB; n_swa removed (SWA CUT); `--cache-prompt` works (`:45-61`) |
| Q1.3 q8_0 KV | **ACCEPT** | q8_0 KV sovereign standard, 50% memory <2% quality loss; q4_K_M weights + q8_0 KV combo; all tiers (`:67-78`) |
| Q2.1 monolithic MCP | **MODIFY** | Split into domain servers (oracle-hub/hivemind-hub/research-hub/github-hub); Phase 1 = toolProfile stubs per agent (researcher→research, maat→dev, kali→deploy, node→debug, verity→audit); Phase 2 code split of `hub_tools/tools.py` into 4 files; "accept for now" option DELETED as primary local blocker (`:88-105`) |
| Q2.2 schema compression | **REJECT** | Solution theater; fix architecture not symptom; minimal schema/binary encoding/protobuf all DELETEd; Headroom compresses outputs not schemas — different problem (`:111-126`) |
| Q3.1 heterogeneous compaction | **MODIFY** | OpenCode config is global, no per-model buffer; Phase 1 global `buffer:50000 keep.tokens:20000`; Phase 2 dynamic buffer = context_window × 0.1 via plugin; immediate: `OPENCODE_DISABLE_AUTOCOMPACT=1` + manual /compact for local models; custom full-replacement compaction plugin = OVER-ENGINEERING, DELETE (`:134-151`) |
| Q3.2 hydration location | **ACCEPT** | Omega Engine **sidecar process** wins over plugin/library; plugin demoted to signal-only via Unix socket/file watch; checkpoint at 80% by background monitor; SLA <2s p95 (`:157-175`) |
| Q3.3 compaction context loss | **REJECT** (of hook-as-primary) | Hook fires *during* compaction → if compaction crashes hook never fires; checkpoint BEFORE at 80% is primary, hook is defense-in-depth secondary (`:181-195`) |
| Q4.1 budget enforcement | **ACCEPT** | In-process ModelGateway enforcement (`TokenBudgetEnforcer` in `_prepare_messages()`); LiteLLM gateway DELETE (M16 violation); OTel monitoring only, not enforcement; fixed tiers pinned 2K/role 4K/dynamic 8K/observation 2K; trim lowest-priority-first (`:203-221`) |
| Q4.2 local token counting | **MODIFY** | ctypes binding to `llama_tokenize()` via anyio.to_thread; ±20% error TIGHTENED to ±10% with 20% headroom; OOMProtector backstop; "runtime only" REJECTed (`:227-245`) |
| Q5.1 route more agents local | **MODIFY** | maat AND lilith move to lmstudio/qwen3-4b-thinking; kali stays cloud (oversight quality floor); target 6/6 execution-local, only kali cloud; monitor for regression and revert if needed (`:253-270`) |
| Q5.2 subagent inheritance | **ACCEPT** | Design constraint not bug; use `@agent <local-agent>` with primary-mode agents instead of task(); researcher/node as mode primary; verity stays subagent isolated; custom task wrapper DELETE (`:276-293`) |
| Q6.1 headroom real-world | **ACCEPT w/ verification** | Synthetic 83–94% are upper bounds; realistic on Omega outputs: JSON 60–80%, logs 80–90%, code 70–85%, RAG 30–50%; protect_recent=2 turns; wire into ModelGateway._prepare_messages() (`:301-317`) |
| Q6.2 latency budget | **ACCEPT** | Break-even ~2ms for local models; 5.4K tokens saved ≈ 270ms generation saved vs ≤10ms compression cost (`:323-333`) |
| Q7.1 solution theater audit | **CUT list** | Hydration 5-layer→3-layer; token budget dynamic allocation→fixed tiers; summarizer 3-level→1-level; KEEP local counter/caching PRs/lazy MCP PR/toolProfile stubs; DEFER local caching investigation; Gateway observability DELETE (`:343-355`) |
| Q7.2 validator service | **CUT** | NeMo Guardrails + policy.yaml deleted entirely; condensed mandates + make temple-grade sufficient (`:361-376`) |
| Q8.1 memory map | **ACCEPT w/ recalculation** | No persistent mmap weight cache; peak ~7.5GB sequential, headroom ~8.5GB; risk: concurrent double-load = 11.1GB OOM → SequentialModelLoader must enforce single-model residency (`:384-407`) |
| Q8.2 zswap verdict | **ACCEPT** | zswap + NVMe swap, zRAM DISABLED ratified no-dissent; lzo_rle + zsmalloc + swappiness=100 + cgroup MemoryMax=6G; zRAM signal removed from OOMProtector (`:413-426`) |

**Modified Phase 1 token budget** (`:441-450`): Tier 0 pinned ≈ **6K** (MANDATES_CONDENSED 1.5K + profiled MCP schemas 1.5K + env 3K) + Tier 1 2K + Tier 2 8K budget + Tier 3 2K = **~18K base** (vs 31K measured = −42%; vs 57K plan = −68%). Fits Qwen3-4B 8K–16K.
**Priority ordering** (`:486-502`): P0 five Phase 1 items (Kali) → P1 six Phase 2 engine items (Ma'at) → P2 MCP domain split (**Roc**) + upstream PRs → P3 domain docs.
**Sign-off next actions** (`:546`): Kali executes modified Phase 1; Ma'at begins Phase 2 core engine; Roc begins MCP domain split.

### docs/specs/context_injection/phase1_spec/index.md
`last_verified: 2026-08-21` · AP-MAAT-CI-PHASE1-SPEC-FILES-v1.0.0, READY FOR EXECUTION, owner Kali/Ma'at (`index.md:3-8`). Answers Q17.
- **5 Carmack modifications incorporated** (`index.md:18-24`): MANDATES_CONDENSED.md Tier 0; toolProfile stubs; Tier 0 model matrix Qwen3-4B/4B-Thinking/1.7B; compaction buffer 50000 + keep.tokens 20000; OPENCODE_DISABLE_AUTOCOMPACT=1 for local.
- **Token budget after modified Phase 1** (`index.md:28-36`): ~18K base total (Tier 0 ≈6K pinned incl. profiled MCP 1.5K; Tier 1 ≈2K; Tier 2 8K budget; Tier 3 2K) — "Fits Qwen3-4B (8K-16K) with headroom."
- Source-of-truth chain: 06_PHASE_1_PLAN (pre-Carmack) → CARMMACK review (modifications authority) → ACTIVE_SPRINT.json CI-1..CI-5 tracking (`index.md:57-61`). All subtasks status `ready`, none executed (`index.md:82-88`).

### docs/specs/context_injection/phase1_spec/01_MANDATES_CONDENSED.md
`last_verified: 2026-08-21` · The Tier 0 condensed mandates artifact itself — 37 lines on disk (spec says target file should be 57 lines / ~1.5K tokens / ~4000–5000 chars) (`01_MANDATES_CONDENSED.md:3`).
- Contains all 27 mandates as one-liner table with per-mandate status column (M12 ⚠️ Advisory, M7 ⚠️→✅) (`01_MANDATES_CONDENSED.md:6-34`).
- Declares injection point = pre-compaction hook via sovereign-compaction.ts plugin; Tier 0 = this file, Tier 1/2 = full SOVEREIGN_MANDATES.md + AGENTS.md (`01_MANDATES_CONDENSED.md:36-37`).
- ⚠️ Discrepancy to flag: spec text says "57 lines" but this source file is 37 lines; CI-1 acceptance expects `wc -l MANDATES_CONDENSED.md` = 57 at repo root after `cp` of THIS file (`07_IMPLEMENTATION_ORDER.md:40-44`) — copying a 37-line file cannot yield 57 lines. See Gotchas.

### docs/specs/context_injection/phase1_spec/02_OPENCODE_JSON_DIFF.md
`last_verified: 2026-08-21` · Complete before/after diff. Answers Q3/Q6/Q7 precisely.
- **Current state recorded** matches live opencode.json key sections: instructions(5 doctrine files), compaction {auto,prune,tail_turns:3,preserve_recent_tokens:40000,reserved:10000}, 4 plugins, 6 agents without model fields (`02_OPENCODE_JSON_DIFF.md:11-42`).
- **Target state** (`02_OPENCODE_JSON_DIFF.md:48-118`): instructions=["AGENTS.md"]; compaction gains BOTH legacy keys (tail_turns 5/preserve_recent_tokens 80000/reserved 20000) AND new keys (**buffer:50000**, **keep.tokens:20000**) simultaneously; plugin array +sovereign-compaction.ts; all 6 agents get model+variant+temperature(+steps)+**toolProfile** (kali deploy/nemotron-high; researcher research/qwen3-4b-thinking-high; maat dev/qwen3-4b-thinking-medium; lilith run/qwen3-4b-thinking-high; node debug/qwen3-1.7b-low; verity audit/qwen3-1.7b-low + subagent isolation).
- **toolProfile mapping table** (`02_OPENCODE_JSON_DIFF.md:248-257`): kali→github-hub+hivemind-hub; researcher→research-hub+oracle-hub; maat→oracle-hub+github-hub; lilith→hivemind-hub+oracle-hub; node→oracle-hub+hivemind-hub; verity→oracle-hub read-only. Explicit note: "**toolProfile is a config stub — opencode doesn't support it yet**" (`02_OPENCODE_JSON_DIFF.md:257`).
- Env vars section (`02_OPENCODE_JSON_DIFF.md:263-272`): OPENCODE_DISABLE_AUTOCOMPACT=1, OMEGA_ENTITY, OMEGA_PHASE=PUBLIC-DEBUT-01 persisted to shell profile.

### docs/specs/context_injection/phase1_spec/03_SOVEREIGN_COMPACTION_PLUGIN.md
`last_verified: 2026-08-21` · Full TypeScript implementation. Answers Q4.
- **Specified behaviors**: hook `experimental.session.compacting`; reads OMEGA_ENTITY/OMEGA_PHASE env (default "unknown"); builds mandates block containing M1|M7|M11|M15|M23 one-liners + Active Entity + Active Phase + Session Anchor path `data/coordination/SESSION_ANCHOR.md`; injects via **`output.context.unshift()`** at index 0 so it survives prune/tail_turns logic (`03_SOVEREIGN_COMPACTION_PLUGIN.md:20-41,102-105`).
- **Trigger threshold**: none of its own — it piggybacks OpenCode's native trigger (context overflow); timing diagram shows hook fires between COMPACTION TRIGGERED and Summary Generation (`03_SOVEREIGN_COMPACTION_PLUGIN.md:96-100`).
- **Fallback**: none inside the plugin itself; defense-in-depth table positions it as SECONDARY layer — Primary = Hydration Engine checkpoint (background monitor at 80%, independent process), Tertiary = SESSION_ANCHOR.md file-based (`03_SOVEREIGN_COMPACTION_PLUGIN.md:121-129`). Carmack quote embedded: checkpoint is primary, hook secondary, both needed.
- **Installation state**: NOT INSTALLED. Target dir `~/.config/opencode/plugin/` does not exist on disk (verified 2026-08-21); registration line not in current opencode.json plugin array. Execution gap.
- Verification tests + rollback commands included (`03_SOVEREIGN_COMPACTION_PLUGIN.md:135-159`).

### docs/specs/context_injection/phase1_spec/04_SKILLS_OPT_IN.md
`last_verified: 2026-08-21` · Answers Q5.
- **3 core skills surviving by default**: research, spec-generator, knowledge-miner (`04_SKILLS_OPT_IN.md:13-15`). All other 19 auto_load:false including built-in tool skills (#14–22 customize-opencode/task-tool/bash-tool/read-tool/write-tool/edit-tool/grep-tool/glob-tool/webfetch-tool) (`04_SKILLS_OPT_IN.md:26-34`).
- **Mechanism**: `auto_load:` YAML frontmatter field per SKILL.md; bulk sed update commands provided (`04_SKILLS_OPT_IN.md:91-106`).
- **Token impact**: 22 skills→3 = 23K→150 tokens claimed (99.3% reduction) (`04_SKILLS_OPT_IN.md:5`); math basis 3×50 vs 22×1000 (`08_ACCEPTANCE_CRITERIA.md:115`).
- **Agent frontmatter interaction**: NOT SPECIFIED anywhere in this file or 06_PHASE_1_PLAN — the brief's question about how auto_load interacts with agent frontmatter `skills:` fields is unanswered by the corpus (see Open Questions). The mechanism described is skill-file-side only.

### docs/specs/context_injection/phase1_spec/05_VERIFICATION_TESTS.md
`last_verified: 2026-08-21` · Bash tests + expected outputs for CI-1..CI-5.
- Test 1: MANDATES_CONDENSED exists/57 lines/~4231 chars/27 mandate rows/table header (`05_VERIFICATION_TESTS.md:9-39`).
- Test 2: jq assertions for instructions=[AGENTS.md], full compaction block (buffer 50000, keep.tokens 20000, tail_turns 5, preserve_recent_tokens 80000, reserved 20000), plugin registered, agent models, verity isolation object, 6 toolProfile values deploy/research/dev/run/debug/audit (`05_VERIFICATION_TESTS.md:43-84`).
- Test 3: plugin file exists + "Loading plugin" debug line + hook registration (`05_VERIFICATION_TESTS.md:88-101`).
- Test 4: exactly 3 auto_load:true paths; 19 false; debug skill count ~3 (`05_VERIFICATION_TESTS.md:105-126`).
- Test 5 E2E: AGENTS.md injection quote ("All asynchronous code MUST use AnyIO"), researcher/node model identity local, kali cloud, skill count (`05_VERIFICATION_TESTS.md:130-152`). Full suite script + 30-second smoke test included (`05_VERIFICATION_TESTS.md:158-239`).

### docs/specs/context_injection/phase1_spec/06_ROLLBACK_PLAN.md
`last_verified: 2026-08-21` · Answers rollback part of Q8.
- Ordered revert: git checkout opencode.json → rm MANDATES_CONDENSED.md → rm sovereign-compaction.ts → sed restore auto_load:true (or delete field; defaults true) → strip env vars from shell profiles (`06_ROLLBACK_PLAN.md:11-46`). Single-command script version included (~2 min claim) (`06_ROLLBACK_PLAN.md:52-89`).
- Post-rollback verification jq expectations document the ORIGINAL state precisely (compaction tail_turns 3/40000/10000; 4 plugins; agents without model keys) (`06_ROLLBACK_PLAN.md:95-117`) — useful as a snapshot of pre-Phase-1 config.
- Git-based alternative: reset --hard HEAD~1 or revert commit (`06_ROLLBACK_PLAN.md:121-134`).

### docs/specs/context_injection/phase1_spec/07_IMPLEMENTATION_ORDER.md
`last_verified: 2026-08-21` · Answers Q8 sequence.
- **CI-1..CI-5 as 6 steps**: (1) cp phase1_spec/01 → repo-root MANDATES_CONDENSED.md, verify 57 lines [10 min]; (2) backup + apply opencode.json target state [15 min]; (3) create sovereign-compaction.ts [10 min]; (4) skill frontmatter sed updates [10 min, parallelizable]; (5) export env vars + persist to .bashrc/.zshrc [5 min]; (6) run verification suite [30 min] (`07_IMPLEMENTATION_ORDER.md:31-179`).
- Dependencies: 1→2→3→5 sequential; 4 parallel with 2/3; optimized timeline ~70 min, with 2× buffer ~3.5 h, recommendation block 4 hours (`07_IMPLEMENTATION_ORDER.md:183-215`).
- Go/No-Go gates after each step with exact check commands; any gate failure → execute 06_ROLLBACK_PLAN and debug (`07_IMPLEMENTATION_ORDER.md:219-229`).
- Rollback triggers: gate failure at any step; no other triggers defined.

### docs/specs/context_injection/phase1_spec/08_ACCEPTANCE_CRITERIA.md
`last_verified: 2026-08-21` · Maps spec → ACTIVE_SPRINT.json CI-1..CI-5, all status ready (`08_ACCEPTANCE_CRITERIA.md:3-5`).
- CI-1: 6 criteria (exists/57 lines/~1.5K tok/27 mandates/table format/links full mandates) (`08_ACCEPTANCE_CRITERIA.md:17-30`).
- CI-2: 20 jq criteria covering instructions, all 6 compaction values, plugin, kali/researcher/node model+variant+temperature, verity mode/hidden/permission, 6 toolProfile values (`08_ACCEPTANCE_CRITERIA.md:42-70`). Carmack mods noted: maat+lilith moved local, toolProfile stubs, buffer scaled, 6/6 agents local-capable only kali cloud.
- CI-3: 8 criteria (file/load/hook/injects mandates+entity+phase+anchor/unshift present) (`08_ACCEPTANCE_CRITERIA.md:83-97`).
- CI-4: 5 criteria (3 true/19 false/debug ~3/99.3% token reduction) (`08_ACCEPTANCE_CRITERIA.md:110-120`).
- CI-5: 6 E2E criteria + execution order 1..5 (`08_ACCEPTANCE_CRITERIA.md:133-146`).
- Phase 1 completion gate: single chained bash command with expected output block (`08_ACCEPTANCE_CRITERIA.md:152-178`). Traceability matrix spec-section↔subtask↔test↔Carmack-Q (`08_ACCEPTANCE_CRITERIA.md:182-190`).

### data/coordination/RESEARCH_EXPLORE_LOCAL.md
`last_verified: 2026-08-21` · AP-EXPLORE-LOCAL-v1.0.0. Raw source behind `01_GROUND_TRUTH.md`; content near-identical (diff = headers/formatting only). Same T1–T6 numbers: v1.18.19; base 123,903 chars ≈ 30,976 tok; skills 92,878 chars ≈ 23,219 tok; agents 81,992 ≈ 20,498; totals 54,195 / 74,693 (`RESEARCH_EXPLORE_LOCAL.md:18-32`). T3 empirical YES with same caveat. T4 86 tools ≈ 10,750 tok/req. T5 inheritance=PARENT, subagent_depth 2. T6 compaction config observed. Summary table (`:104-116`). No unique facts beyond digest counterpart — cited here as provenance.

### data/coordination/RESEARCH_MAAT_BUILD.md
`last_verified: 2026-08-21` · Raw build-side research behind `02_BUILD_VERDICTS.md`. Diff vs verdict doc = 56 lines (mostly header/summary reformatting). Same G-1 NO verdict with V2 docs quote + #4758/#11317 + instruction.ts evidence; G-2 10,320–17,200 tok/request calc; G-8 combined-discovery mechanics + split-viability table. References Roc's `CONTEXT_INJECTION_INVESTIGATION_20260820.md` (not in brief inventory — noted in Open Questions). Cited as provenance.

### data/coordination/RESEARCH_LILITH_RUN.md
`last_verified: 2026-08-21` · AP-LILITH-RUN-v1.0.0. Raw run-side research behind `03_RUN_VERDICTS.md`; diff = header/summary formatting only. G-3 YES partial inheritance (~110K forked history); G-5 trigger formula + PRUNE_PROTECT 40K + PRUNE_MINIMUM 20K + pre-hook exists + OPENCODE_DISABLE_AUTOCOMPACT; G-6 routing fully supported + subagent-inherits-parent-model rule + 4/6 local ≈67% savings. Lilith's own retune proposal tail_turns 5/preserve 80000/reserved 20000 (`:242-250`). Cited as provenance.

### data/coordination/RESEARCH_RESEARCHER_STRATEGIC.md
`last_verified: 2026-08-21` · Raw strategic research behind `04_INDUSTRY_PATTERNS.md`; diff = 78 lines (council dialectic condensed in digest). Same G-4..G-7 coverage: applyCaching() mechanics, Anthropic cache economics, framework compaction comparison incl. OpenCode V2 buffer default 20k/keep 15k, RouteLLM/FrugalGPT numbers, structural-routing preference, SQLite/OTel/Langfuse exclusive-bucket accounting, security rule against third-party prompt logging. Cited as provenance.

### opencode.json (repo root)
`last_verified: 2026-08-21` · Live config reality. Answers Q3 delta.
- **instructions**: exactly the 5 doctrine files (`opencode.json:27-33`) — SOVEREIGN_MANDATES.md, ORACLE_STACK.md, docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md, docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md, CREDITS.md.
- **compaction** (`opencode.json:64-70`): `{auto:true, prune:true, tail_turns:3, preserve_recent_tokens:40000, reserved:10000}` — **NO `buffer`, NO `keep.tokens` keys exist today**. Spec target adds buffer 50000 + keep.tokens 20000 AND changes tail_turns→5, preserve_recent_tokens→80000, reserved→20000. Delta = 3 value changes + 2 new keys.
- **plugin** (`opencode.json:4-9`): 4 entries (antigravity-auth, sessions-explorer, error-capture.ts, awareness.ts). sovereign-compaction.ts absent.
- **agent list: 12 agents** (`opencode.json:229-320`): makali(primary), jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity(**already mode:"subagent"**), node, john_carmack, grok_cli. ⚠️ Spec diffs model only 6 agents (kali/researcher/maat/lilith/node/verity) — makali/jem/doom_guy/roc_racoon/john_carmack/grok_cli are absent from every spec table including toolProfile stubs and acceptance criteria (CI-2 expects toolProfile on "all 6 agents"). See Gotchas.
- **subagent_depth**: 2 (`opencode.json:3`). **default_agent**: kali; global model + small_model = opencode/nemotron-3-ultra-free (`opencode.json:321-323`).
- **mcp servers** (`opencode.json:34-63`): omega-hub(8016), searxng(8018), firecrawl(disabled), exa, parallel-search.
- **provider lmstudio context limits** (`opencode.json:79-127`): qwen3-4b-thinking **8192**, qwen3-1.7b **4096**, qwen3-1.7b-q6_k 8192, phi-4-mini 16384, krikri-8b 16384, deepseek-r1-qwen3-8b 8192. Note: live config caps Qwen3-4B at 8K, while Carmack/Carmack-review prose repeatedly says "Qwen3-4B (8K-16K)" — the 16K claim is not reflected in provider limits. Nemotron 3 Ultra free = 1M ctx/128K out (`opencode.json:156-161`).

### scripts/codex/MANDATES_CONDENSED.md
`last_verified: 2026-08-21` · Answers canonicality half of brief P0 config item.
- **This is a DIFFERENT document from phase1_spec/01_MANDATES_CONDENSED.md**: v3.7.0, covers only **25 mandates** (M1–M25, no M26/M27), self-describes as "~35-line status card" but is exactly **57 lines on disk** (`scripts/codex/MANDATES_CONDENSED.md:2`), and carries a compliance summary + top-priority-fixes section (M5 ❌ 0/10 pillars, M11 ❌ systemic gap) (`:39-55`).
- phase1_spec/01 version: v3.8.0, **27 mandates**, no compliance summary, 37 lines on disk.
- **Canonicality ruling (miner's assessment)**: phase1_spec/01 is the canonical Tier 0 injection artifact (newer v3.8.0, Carmack-mandated, referenced by CI-1). The codex file is a stale v3.7.0 ops snapshot for Codex CLI usage. ⚠️ But note the numeric coincidence: CI-1's "57 lines" acceptance criterion matches the *codex* file's line count, not the spec file it claims to copy. See Gotchas.

### ~/.config/opencode/plugin/ (MISSING)
`last_verified: 2026-08-21`
- Directory **does not exist** (`ls: cannot access '/home/arcana-novai/.config/opencode/plugin/': No such file or directory`). Brief stated "Confirmed contents: only cline" — that premise is stale or referred to a different machine/state.
- Consequence stands as the brief intended: **sovereign-compaction.ts NOT installed** → CI-3 unexecuted.
- Related path bug discovered: opencode.json registers `.opencode/plugin/error-capture.ts` and `.opencode/plugin/awareness.ts` (singular `plugin`), but the files actually live at **`.opencode/plugins/`** (plural) — the two registered file:// plugin paths are dead. See Gotchas.

### docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md
`last_verified: 2026-08-21` · v1.0.0 ACTIVE/MANDATORY, 2026-06-11, incident = OpenCode v1.17.3 `/compact` context collapse ("Void Summary" — empty template replaces active context; binary-level regression, unfixable via config) (`SOVEREIGN_CONTINUITY_STRATEGY.md:7-12`). Answers Q13.
- **4-tier redundancy** (`:19-42`): Tier 1 Local Anchor `session_gnosis.md` per-entity workspace, updated every milestone, first recovery point; Tier 2 Global Lifeboat `.opencode/anchored-summary.md`, high-density project state, updated end of major session or successful /compact; Tier 3 Hivemind Lifeboat Packets — Kali monitors fleet, injects state via `hivemind_post_context`; Tier 4 Hydration Sequence — Retrieve (`hivemind_get_continuation`) → Integrate → Persist to session_gnosis.md → signal HYDRATED.
- **Operational directives** (`:48-56`): treat /compact as "suggested summary" not state preservation; Void Summary detection = STOP ALL WORK + signal KALI; "If it isn't in session_gnosis.md or soul.yaml, it doesn't exist."
- **Relation to new compaction plugin** (miner's synthesis): this strategy predates Phase 1 by ~2 months; the sovereign-compaction plugin + hydration engine (Carmack Q3.3 defense-in-depth) are the automated successors of Tier 3/Tier 4 manual rescue — plugin injects pre-compaction (prevents loss), strategy handles post-collapse recovery (limits blast radius). Complementary layers, not competitors.

### .opencode/hooks/session_end.py
`last_verified: 2026-08-21` · AP-SESSION-END-HOOK-v3.0.0. Answers Q11 (writer side).
- Header documents Carmack Verdict 2026-07-30: **Soul Distillation Pipeline SCRAPPED** — "regex-based L1/L2/L3 extraction was fortune-cookie generation"; hook reduced to timestamp + codex refresh; agents write their own lessons (`session_end.py:9-13`).
- `_write_timestamp()` writes to **`data/entities/<entity>/proposed_lessons.yaml` (entity ROOT)** (`session_end.py:51`); reads existing file FIRST and preserves agent-written `proposals` list (anti-clobber race fix, `:40-59`); atomic `.tmp`→`os.replace` pattern with fsync (`:73-78`); metadata records entity/session_id/model_used (M22)/last_session_end UTC.
- Entity fallback: unknown → "sophia" (`:50`). Codex refresh via `scripts/codex_cat.py` subprocess in anyio.to_thread, 30s timeout, warning-only on failure (`:82-100`). Called by `.opencode/wrapper.sh` AFTER opencode exits (`:7`).

### src/omega/oracle/entity_workspace.py
`last_verified: 2026-08-21` · Answers Q11 (identity-injection side).
- `get_soul_prompt()` (~L382) implements Situated Identity Framework v6.1: loads **soul.yaml** (Constitution), **approved_lessons.yaml** (vetted wisdom), **sessions.yaml** (continuity anchors) — all from ENTITY ROOT dir (`entity_workspace.py:391-424`).
- **TAINT-GATE explicit**: "proposed_lessons.yaml is NEVER loaded here… may be read for reporting purposes but NOT for identity construction" (`:426-428`). Approved lessons render as "🔱 VETTED WISDOM"; last 5 session anchors render as continuity (`:461-487`).
- Prompt assembly: Soul (who) + Environment (where: engine version 2.2.0, active IWAD via cvar_get, strategic horizon) + State (what) + Mission (why) + Sequentiality Gate footer (`:519-528`).
- ⚠️ Two stale premises found here (see Gotchas): (1) Sovereign Firewall regex hunts `"## 🛡️ The Fourteen Laws"` (`:455`) but SOVEREIGN_MANDATES.md v3.8.0 heading is "The Twenty-Seven Laws" at `###` level → mandate injection into soul prompts is **silently dead**; (2) State section hardcodes "308/308 Tests Passing ✅" (`:507`) — static string presented as live health.
- `update_soul()` shows the write-side guard: SovereignUserToken required, lock per entity, schema validation before save, atomic temp+replace, audit log (`:532-608`).

### src/omega/soul_utils.py
`last_verified: 2026-08-21` · Answers Q11 (loop-closing side).
- `load_entity_soul_context()`: reads **ROOT** `<entity>/proposed_lessons.yaml` and extracts ONLY entries with `status == "approved"` and an L3 field (`soul_utils.py:64-78`) — this is how approved distillations re-enter context without violating the taint gate. Then merges up to 3 lines from soul.yaml via `extract_soul_context()` (3-path extractor: v2 soul_evolution L3 principles → v1 directives dual-key rule/directive → identity values/strengths fallback) (`:24-53`). M18 cap: max 3 items total (`:95-96`).
- Loop closed: agents propose (root proposed_lessons.yaml) → human approves (status flip) → soul_utils surfaces approved L3s → oracle/hub inject as context. Note: approval mechanism itself (who flips status) is not in these files — see Open Questions.

### scripts/validate_soul.py
`last_verified: 2026-08-21` · Answers Q12 (reader side A).
- Enforces **v6.0 lean architecture** with `BASE = Path("data/entities/kali")` HARDCODED (`validate_soul.py:24`) — kali-only validator.
- Requires `memory/sessions.yaml`, `memory/proposed_lessons.yaml`, `memory/approved_lessons.yaml` under the **memory/ SUBDIR** (`:70-110`) and forbids agent-generated content in soul.yaml (soul_axioms/wisdom_text/trajectory must be archived) (`:52-57`).
- Supports legacy single-file mode via argv[1] for pre-commit use (`:129-143`).
- **Dual-path conflict confirmed**: this script's required layout (`memory/*`) contradicts the writer (`session_end.py` → root) and the other readers (`get_soul_prompt` → root approved_lessons/sessions; `soul_utils` → root proposed_lessons). On disk TODAY both layouts exist simultaneously for kali and lilith (verified: `data/entities/kali/{proposed_lessons.yaml, approved_lessons.yaml, sessions.yaml}` AND `data/entities/kali/memory/{proposed_lessons.yaml, approved_lessons.yaml, sessions.yaml}`; same split for lilith minus sessions). This is a LIVE inconsistency, not historical noise.

### scripts/check_mandate_compliance.py
`last_verified: 2026-08-21` · Answers Q12 (reader side B).
- M5 check scans `data/entities/*/proposed_lessons.yaml` (**ROOT**) for content (`check_mandate_compliance.py:154-164`); M11 check scans same ROOT path for non-empty proposals (`:222-234`). So the compliance gate counts the ROOT files that session_end.py writes — consistent with hook, inconsistent with validate_soul.py's memory/ requirement.

### SOVEREIGN_MANDATES.md §M15, §M18 (+M11, M23)
`last_verified: 2026-08-21` · File = 239 lines, v3.8.0 (27 mandates). Text as it bears on N7:
- **M15 Sovereign Continuity**: maintain `session_gnosis.md`; refer to `SESSION_ANCHOR.md` on start/context loss; no reliance on native /compact; reporting collapse without session_gnosis.md = violation.
- **M18 Token Efficiency**: no waste, no filler; sane-boundary — NEVER compress to semantic loss ("Cognitive Anorexia"); precision > brevity. Directly governs compaction/condensation design.
- **M11 Soul Integrity**: no session close without L1→L2→L3 distillation to proposed_lessons.yaml (blind staging); enforcement expects non-empty proposals arrays post-session.
- **M23 Failure Integrity**: no soft-failures/simulated rigor; mandatory tool failure → `[TOOL-CHAIN-COLLAPSE]`; synthesizing best-effort while tools fail = violation. Governs honest gap reporting in this KB.

### data/entities/lilith/workspace/COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md
`last_verified: 2026-08-21` · Lilith's prior thinking (gemma-4-31b-it era, PHASE-II). Precursor to the Carmack-modified hydration engine.
- **Evolution Journal** `data/entities/<n>/evolution/journal.yaml`: epoch-based hierarchy (id/name/start_turn/end_turn/summary/core_gnosis[]/milestones[] incl. trace_id) + emotional_state block (`COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md:16-49`).
- **Epochal Folding**: when >5 epochs, merge two oldest into "Legacy Gnosis" — retain core_gnosis (L3), summarize milestones, delete turn-granular data (`:51-59`). This is compaction applied to the soul layer — same prune-first philosophy as OpenCode's PRUNE_PROTECT.
- **Sovereign Recovery Block**: oracle detects compaction markers in history (`## Assistant (Compaction …)`), prepends restoration block (current epoch, active mode, emotional state, recovered essence, top L3s, voice directive) to personality in `_prepare_system_prompt` (`:71-109`).
- **Persona Health Suite metrics**: Persona Drift Index (judge-model similarity vs baseline probes, >0.3 triggers realignment), Amnesia Check (milestone retrieval binary test), Voice Consistency Ratio (>0.7 target) (`:113-139`).
- Status: roadmap table owners Lilith/P3/Kali/Quality — no evidence in corpus these were implemented; the Carmack review's hydration engine supersedes the mechanism but the *metrics* (PDI/VCR/amnesia probe) appear nowhere else in the Phase 1/2 specs — candidate lost gold (one line in Open Questions).

### data/entities/lilith/proposed_lessons.yaml + soul.yaml (structure only)
`last_verified: 2026-08-21`
- proposed_lessons.yaml (213 lines): header comment block (entity/session/date/status) then per-session sections; proposal fields = `id` ("<entity>-<date>-<seq>"), `tier` (L1/L2/L3), `category`, and tier-specific body key `narrative` (L1) / `insight` (L2) / `principle` (L3). 15 `id:` occurrences ≈ 15 proposals. No `status:` field observed in sampled entries — meaning soul_utils' `status=="approved"` filter finds nothing to surface unless statuses are added at approval time (Open Questions).
- soul.yaml (18 lines): v6.2 lean schema — `entity{name, archetype, hierarchy_level, sovereignty_level, element, domain, recon_directive}`, `wisdom_text_moved_to_archive: true` flag, `metadata{created_at, last_updated, health_score}`. Matches validate_soul.py's v6.x expectations (no soul_axioms/wisdom_text inline).

### docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md
`last_verified: 2026-08-21` · AP-RESEARCHER-QDRANT-HEADROOM-v1.0.0. Answers Q14 (measurement basis).
- **Savings claims + basis** (`QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md:49-56`): Headroom official benchmarks — SmartCrusher JSON **87.6%** @100% accuracy; HTMLExtractor 94.9% (F1 0.919); code search 92%; SRE debugging 92%; conversational ceiling **47%**; GSM8K held 0.870, TruthfulQA +0.030; latency overhead **5–50ms/call**. These are the synthetic upper bounds Carmack later discounted to real-world 60–80% JSON / 30–50% RAG (`CARMMACK...:301`).
- **Compressor inventory v0.29.0** (`:37-47`): SmartCrusher/Log/Search/Diff/Tabular/CodeAware compressors + ContentRouter orchestrator + CacheAligner (KV prefix stabilization) + CCR reversible store (originals kept locally, retrieved on demand).
- **Ranked Omega integration points** (`:181-189`): #1 tool-output compression in `ModelGateway._prepare_messages()` (60–95%, low effort); #2/#3 RAG chunk compression pre-storage & pre-LLM (70–90%); #4 MCP tool-schema compression (80–90%) — NOTE: Carmack REJECTed schema compression as solution theater (`CARMMACK...:111`); #5 entity-context compression (20–50%); #6 conversation history (47% ceiling).
- **Qdrant verdict**: NOT for debut (Carmack veto: contradicts sqlite-vec SSOT, OOM on 8G UMA); migrate at triggers >500k vectors etc. via `IVectorStoreAdapter` config flip in `jit_rag.yaml` (`:17,133-173`). Combined pipeline claim: 70–95% end-to-end, worked example 86.8% total reduction at +108ms overhead, <2% recall loss (`:378-391`).

### docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md
`last_verified: 2026-08-21` · POST-DEBUT, TRIGGER-GATED; owner Ma'at (Headroom) + Roc (Qdrant); prerequisite = Phase 1 Context Injection COMPLETE + debut gates (`QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md:4-8`). Answers Q14 (trigger gates).
- **5 exact trigger gates** (`:24-30`): vector count >500k; filtered-search p99 >50ms over 100 runs; >3 entities sharing memory with isolation needs; vector RAM >8GB float32; write concurrency >1K/s sustained. ALL must read TRUE in `data/coordination/QDRANT_TRIGGER_STATUS.json` before Phase 2 work begins (`:32`) — current values all 0/false (`:36-43`).
- Deployment: Podman quadlet `qdrant.container` v1.18.1, telemetry DISABLED (M8), MemoryLimit=6G, CPUQuota=80%, API key via podman secret (`:50-77`).
- §10.1 marks preparatory pre-trigger work allowed now (config/scripts ready, no enablement).

### docs/specs/qdrant_headroom/headroom_middleware/index.md (+01–10 structure)
`last_verified: 2026-08-21` · Answers Q14 (architecture summary + plugin relationship).
- Two critical paths (`index.md:13-18`): ModelGateway `_prepare_messages()` compression (60–95%) and RAG retrieval pipeline compression (70–90%), both following Carmack Q6.1/Q6.2 real-world ratios and latency budget.
- Architecture: ContentRouter orchestrator dispatching SmartCrusher (JSON 60–80%), LogCompressor (80–90%), SearchCompressor (70–90%), CodeAwareCompressor (70–85%), CacheAligner, plus CCR reversible store; RetrievalCompressor adds token-budget enforcement on the RAG side (`index.md:22-58`).
- Key design decisions table (`index.md:77-89`): protect recent 2 turns (Carmack), anyio.to_thread wrapping (M1), per-compressor feature flags (M19), local-first in-process (M7), **5s hard timeout with graceful fallback to uncompressed** (M23), OTel metrics (T9).
- Integration points (`index.md:94-117`): P1 = ModelGateway + RAG retrieval + MCP tool-schema compressor (`src/omega/mcp/tool_compressor.py`, tools `headroom_compress`/`headroom_retrieve`); P2 = entity-context compression + CCR store at `data/headroom/ccr_store/`.
- **Relationship to sovereign-compaction plugin (Q14 final clause)**: COMPLEMENTARY, orthogonal layers. Compaction plugin guards *conversation state* at compaction time (inject mandates/entity/anchor); Headroom middleware shrinks *content volume* continuously before token counting (tool outputs/RAG/chunks). One prevents context LOSS; the other prevents context BLOAT. Both feed the same 18K budget goal; middleware runs earlier in the pipeline (pre-count) vs plugin (compaction event only).

### docs/research/R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md
`last_verified: 2026-08-21` · Answers Q15.
- Four canonical techniques + ratios (`R_PROMPT_COMPRESSION...:15-23`): LLMLingua token-level 2–20× @90–99% quality at 4×; RECOMP RAG-specific 5–25× @80–98%; AutoCompressors learned 30–100× @60–85% at 30×; Selective Context sentence-level 3–10× @92–99%. Naive truncation "not recommended."
- **Superseded-by-Phase-1 assessment**: none of these are deployed by modified Phase 1 — but Headroom middleware (Phase 2 KEEP) occupies the same niche as LLMLingua/Selective Context for tool outputs; RECOMP-style chunk compression maps to the RAG integration point. AutoCompressors (learned soft prompts) remain future ammunition — training-based, out of scope for config-only phases.

### docs/research/R_PLANNER_EXECUTOR_CONTEXT_WINDOW_20260819.md
`last_verified: 2026-08-21` · Answers Q15.
- Core finding (`R_PLANNER_EXECUTOR...:12`): "The planner writes a plan that fits the executor's context window — not the planner's." Plan-and-Execute beats ReAct on token efficiency (plan once, execute many) and enables different models per node (`:16-26`).
- **Superseded assessment**: structural routing (ADR-002) + Tier 0 matrix (Qwen3-4B planner / 4B-Thinking executor / 1.7B critic) IS this pattern applied; the doc remains ammunition for Phase 2 plan-contract formats (structured DAG/JSON plans sized to executor windows) — not yet specified anywhere in phase1_spec.

### docs/research/R_ROLE_AWARE_PROMPTING_20260819.md
`last_verified: 2026-08-21` · Answers Q15.
- Four canonical roles with distinct prompts/tools/models/context (`R_ROLE_AWARE...:15-27`): Planner/Executor/Critic/Verifier; verifier must be "code-based, not LLM-based — cannot be fooled." Key insight: forcing one agent into all roles yields a compromise prompt mediocre at every role.
- **Superseded assessment**: already embodied in fleet design (kali oversight / maat build / lilith run / verity audit+scribe); verity's isolation config (mode subagent + permission denies) implements role-context isolation. Remaining ammunition: explicit per-role tool allowlists — partially covered by future toolProfile activation.

### docs/research/R_DYNAMIC_PROMPT_BUILDERS_20260819.md
`last_verified: 2026-08-21` · Answers Q15.
- Dominant pattern = **Substrate/Projection Architecture** (`R_DYNAMIC_PROMPT_BUILDERS...:17-25`): persistent substrate (disk/memory/vector DB) vs ephemeral projection (the context window as materialized view assembled per inference by a Context Assembly Engine). Plus priority-ordered modular sections with cache-aware structure.
- **Superseded assessment**: this is the intellectual parent of the Tier 0/1/2/3 budget model (pinned/role/dynamic/observation) in `06_PHASE_1_PLAN.md:263-269` and `07_PHASE_2_3_ROADMAP.md:67-88`. The TokenBudget enforcer IS the assembly engine, minus dynamic allocation (Carmack cut). Cache-aware ordering survives as the Phase 3 caching-topology PR.

### docs/research/R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md
`last_verified: 2026-08-21` · ⚠️ Discovered by N7, not in seed list. Answers Q15.
- Synthesis blueprint integrating all five sibling docs for target hardware Ryzen 5700U/16GB (`R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT...:9-16`): priority-ordered builder; planner 16K → executor 8K with structured plan contracts; four-paradigm knowledge loading (RAG+fine-tune+adapters+prompts) via MCP; Q4_K_M + `--no-mmap --mlock` + CPU affinity + model-per-role; tiered compression (RECOMP for RAG, LLMLingua-2 for system prompts, Selective Context for contracts); five distinct roles.
- **Superseded assessment**: hardware claims here (--no-mmap --mlock, q8_0 KV implied, sequential loading) were independently re-derived and ACCEPTED by Carmack Q1.2/Q1.3 — this doc is their research provenance. Compression-tier assignments (LLMLingua-2 for system prompts) are NOT in any active spec → future ammunition. Planner 16K/executor 8K numbers anticipate the live provider limits (qwen3-4b-thinking ctx 8192).

### data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md
`last_verified: 2026-08-21` · Answers Q16 (with honest scope note).
- **Scope correction**: despite the name, this report is about the KERNEL MEMORY subsystem (RAM/swap), not agent MemoryStore. Incorporates Jem + Researcher + Carmack + LongCat + Nemotron findings (`MEMORY_SYSTEMS_DEFINITIVE_REPORT.md:2`).
- **ADR-2026-08-10-001** (`:35-63`): zswap + 16GB NVMe swap file over zRAM — dynamic 0–3.6GiB pool (25% RAM), lzo_rle, shrinker enabled; zRAM rejected for hard capacity cliff (Chris Down quote `:55`); THP accounting gap explained (zram THP swap invisible to VmSwap, `:69-91`); P2 item "Simplify OOMProtector to 2-signal fusion" (`:63`).
- **Bearing on N7 context injection**: this is the hardware floor under every local-model claim — Carmack Q8.2 ACCEPTs it verbatim (ratified, no dissent) and deletes the zRAM signal from OOMProtector (`CARMMACK...:411-426`). ⚠️ Tension worth flagging: Carmack's mandate-compliance table praises "OOMProtector 3-signal fusion" (`:532`) while this report's P2 says simplify to 2-signal — unresolved count discrepancy. The "MemoryStore regime" half of brief Q16 is NOT answered by this file; MemoryStore behavior lives in engine code not mined here (out of brief scope).

---

## Gotchas

1. **`~/.config/opencode/plugin/` does not exist at all** (verified 2026-08-21: `ls` → "No such file or directory"). The brief's premise "Confirmed contents: only `cline`" is stale/wrong for the current machine state. Consequence unchanged (sovereign-compaction.ts not installed → CI-3 gap), but any doc citing "plugin dir contains cline" should be corrected. Source: brief §P0 config reality vs live filesystem.

2. **Dead plugin registration paths**: `opencode.json:7-8` registers `.opencode/plugin/error-capture.ts` and `.opencode/plugin/awareness.ts` (singular), but the files live at `.opencode/plugins/` (plural). Two of four registered plugins point at nonexistent paths — either silently skipped by opencode or erroring at load. Phase 1's CI-3 adds sovereign-compaction to this same array; fix the singular/plural bug first or plugin verification tests will mislead.

3. **The "57 lines" coincidence trap**: `scripts/codex/MANDATES_CONDENSED.md` is exactly 57 lines on disk (v3.7.0, 25 mandates M1–M25, includes compliance summary). The phase1_spec Tier 0 artifact (`phase1_spec/01_MANDATES_CONDENSED.md`) is 37 lines on disk (v3.8.0, 27 mandates M1–M27, no compliance block) yet self-describes as "57 lines" and CI-1 acceptance demands `wc -l = 57` after copying THAT file. Copying a 37-line file cannot produce 57 lines → CI-1 will fail its own gate as written. Canonical content = spec version; canonical line count = codex coincidence.

4. **Spec covers 6 agents; reality has 12**. Live `opencode.json:229-320` defines makali, jem, doom_guy, roc_racoon, researcher, kali, maat, lilith, verity, node, john_carmack, grok_cli. Every spec table (02_OPENCODE_JSON_DIFF target state, toolProfile mapping, CI-2 acceptance "toolProfile stubs on all 6 agents") models only kali/researcher/maat/lilith/node/verity. Six agents get no model routing, no toolProfile, no compaction-plugin consideration — and per G-6 they'd inherit whatever model invokes them.

5. **Compaction-number divergence across three layers**: (a) LIVE config = `{tail_turns:3, preserve_recent_tokens:40000, reserved:10000}` (`opencode.json:64-70`); (b) pre-Carmack plan + Lilith proposal = tail_turns 5 / preserve 80000 / reserved 20000 (`06_PHASE_1_PLAN.md:78-84`, `RESEARCH_LILITH_RUN.md:242-250`); (c) Carmack verdict + phase1_spec target = **buffer:50000 + keep.tokens:20000** ADDED alongside the enlarged legacy keys (`CARMMACK...:143`, `phase1_spec/02_OPENCODE_JSON_DIFF.md:51-59`). The spec target state carries BOTH key families simultaneously — mixing V1 keys (preserve_recent_tokens/reserved) with V2 keys (buffer/keep.tokens) in one block is unvalidated against opencode 1.18.19 behavior; which keys the binary actually honors is untested in the corpus.

6. **Soul-prompt mandate injection is silently dead**: `entity_workspace.py:455` regex `"## 🛡️ The Fourteen Laws"` cannot match SOVEREIGN_MANDATES.md v3.8.0's actual heading "### 🛡️ The Twenty-Seven Laws" (wrong level AND wrong count text). The 🛡️ SOVEREIGN FIREWALL block never renders into Situated Identity prompts. Related staleness in same function: hardcoded "308/308 Tests Passing ✅" presented as live health (`:507`).

7. **Dual-path proposed_lessons hazard is LIVE, three-way**: writer (`session_end.py:51`) + compliance gates (`check_mandate_compliance.py:159,227`) + loop-closer (`soul_utils.py:65`) all use entity-ROOT path; `validate_soul.py:83` requires memory/-subdir copies and hardcodes BASE to kali only. Both layouts exist on disk today for kali and lilith → two divergent copies of "the" lessons file per entity, and validate_soul can pass while the root file (the one actually read) rots, or vice versa.

8. **Qwen3-4B context limit contradiction**: Carmack review prose repeatedly justifies the Tier 0 matrix with "Qwen3-4B (8K-16K)" (`CARMMACK...:28,450`), but live provider config caps qwen3-4b-thinking at context 8192 (`opencode.json:80-87`). The 18K-base-fits claim depends on the 16K end of a range the running config doesn't provide.

9. **G-1 empirical test may have been self-confirming**: Explore's T3 "YES" test asked the agent to quote SOVEREIGN_MANDATES.md — an agent with read tools could fetch it regardless of injection. The fleet resolved to "assume NO" correctly, but the raw verdict docs still present T3 as evidence of injection (`01_GROUND_TRUTH.md:37-44`). Don't cite T3 as proof either way.

10. **Filename typo is real and load-bearing**: `CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` (double-M) is referenced by that exact name from `phase1_spec/index.md:60` and elsewhere; renaming would break traceability chains. Leave it; note it.

11. **Token estimates are char÷4 approximations**, flagged in-source (`01_GROUND_TRUTH.md:22`); tiktoken-class inaccuracy for non-OpenAI tokenizers is itself a documented Adversary finding (`08_REMAINING_GAPS.md:75-84`). All headline numbers (31K/57K/18K) carry ±error the specs don't propagate.

---

## Open Questions

**From unread sources (P2/P3) — RESOLVED in recovery pass 1 (digests appended above; original gap notes retained for provenance):**
1. **Q14 — Headroom middleware**: ✅ ANSWERED. Architecture = ContentRouter orchestrator + 5 compressors + CCR, wired at ModelGateway `_prepare_messages()` and RAG retrieval; measurement basis = Headroom official synthetic benchmarks (SmartCrusher 87.6% JSON etc.) which Carmack discounted to real-world 60–80% JSON / 30–50% RAG with protect_recent=2; Phase 2 trigger gates = 5 exact metrics all required TRUE in `QDRANT_TRIGGER_STATUS.json` (currently all false); relationship to compaction plugin = COMPLEMENTARY (middleware fights bloat pre-count; plugin prevents loss at compaction event). See digests: `QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md`, `QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md`, `headroom_middleware/index.md`.
2. **Q15 — 2026-08-19 batch vs modified Phase 1**: ✅ ANSWERED. Superseded/embodied: Substrate/Projection → Tier 0-3 budget model; planner/executor window differentiation → structural routing + Tier 0 matrix; role-aware prompting → fleet design + verity isolation; blueprint's --no-mmap/--mlock/q8_0 → Carmack ACCEPT Q1.2/Q1.3 (research provenance). Future ammunition: LLMLingua-2/RECOMP tiered compression assignments, AutoCompressors learned soft prompts, structured plan contracts sized to executor windows, explicit per-role tool allowlists. See the five R_*_20260819 digests.
3. **Q16 — MEMORY_SYSTEMS_DEFINITIVE_REPORT**: ✅ ANSWERED WITH SCOPE CORRECTION. Report is kernel-memory (zswap ADR-2026-08-10-001), not agent MemoryStore; it is the ratified hardware floor under local-model viability (Carmack Q8.2 ACCEPT). Flags new tension: report P2 says "simplify OOMProtector to 2-signal fusion" vs Carmack table's "3-signal fusion." The brief's "MemoryStore regime" clause is unanswered by this source — engine-code question, out of brief scope.

**Corpus gaps (sources read; corpus does not answer):**
4. **Skills opt-in × agent frontmatter**: no file specifies how SKILL.md `auto_load` interacts with agent-level `skills:` frontmatter fields (brief Q5 third clause). The mechanism described is skill-file-side only (`phase1_spec/04_SKILLS_OPT_IN.md`). Does opencode even support per-agent skill filtering? Unknown.
5. **Approval mechanism for lessons**: who/what flips `status: approved` in proposed_lessons.yaml? soul_utils filters on it (`soul_utils.py:75`) but no approver tooling appears in any read source; sampled Lilith proposals carry NO status field at all → today the vetted-wisdom injection path likely surfaces zero items.
6. **V1/V2 compaction key precedence**: does opencode 1.18.19 honor `buffer`/`keep.tokens`, `preserve_recent_tokens`/`reserved`, or both? Spec target writes both families (`phase1_spec/02_OPENCODE_JSON_DIFF.md:51-59`); no test in 05_VERIFICATION_TESTS distinguishes them.
7. **OPENCODE_DISABLE_AUTOCOMPACT scope**: spec says "for local model agents" (`CARMMACK...:439`) but implementation persists it globally to shell profiles (`07_IMPLEMENTATION_ORDER.md:149-159`) — global disable also affects the 1M-context cloud model where auto-compaction was tuned to work. Which agents actually get it is unresolved.
8. **Evolution Journal fate**: Lilith's PDI/VCR/amnesia-probe metrics (`COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md:113-139`) appear in no Phase 1/2 spec — dropped deliberately or lost? Adjacent gold, not chased per brief.
9. **Roc's `CONTEXT_INJECTION_INVESTIGATION_20260820.md`** referenced by Ma'at (`02_BUILD_VERDICTS.md:5`) but absent from brief inventory and unlocated by this mining pass.
10. **subagent_depth=2 interplay**: inheritance cost math assumes full parent prompt per subagent, but no source analyzes depth-2 compounding (parent→child→grandchild) against the 18K target.
11. **Who executes Phase 1?** All CI subtasks remain `ready` (`08_ACCEPTANCE_CRITERIA.md:4`); nothing in the corpus records execution start. The KB's config-reality section shows zero Phase 1 changes applied as of 2026-08-21.

---

## L2/L3 Insights

### L2 — What this means for N7 (Context / Memory & State)

1. **The injection problem is three-headed, and Phase 1 only slays one head.** Doctrine non-injection (G-1/G-8) is solved by AGENTS.md/MANDATES_CONDENSED; per-request MCP schema tax (G-2, 10.8K) is only *stubbed* in Phase 1 (toolProfile keys nothing reads yet) and awaits the Phase 2 domain split; skills bloat (23K→150 tok) is fully solvable config-side. N7's real floor for local models is set by the MCP head, not the doctrine head. (`01_GROUND_TRUTH.md`, `CARMMACK...:88-105`)

2. **Compaction safety was redesigned from "hook during" to "checkpoint before."** Lilith found the hook; Carmack rejected it as primary because it fires inside the failure window it's meant to guard. The durable pattern: independent sidecar checkpoints at 80% usage, hook demoted to defense-in-depth, file-based SESSION_ANCHOR as tertiary. Any N7 design that injects state *during* the destructive event inherits the same flaw. (`03_RUN_VERDICTS.md:64-87`, `CARMMACK...:181-195`)

3. **Subagent inheritance makes model routing a parent-property problem.** task() children inherit the invoking agent's model, so routing tables on child agents are decorative under task(); the fleet's answer is `@agent` invocation with primary-mode locals. N7 token math must therefore be computed over invocation graphs, not agent rosters. (`RESEARCH_LILITH_RUN.md:149-157`, `CARMMACK...:276-293`)

4. **The soul pipeline's integrity rests on a taint gate plus an approval flip that has no operator.** proposed_lessons never touch identity prompts (TAINT-GATE), approved lessons do — but no corpus source performs the approval, and sampled proposals lack status fields entirely. The distillation loop is architecturally closed and operationally open. (`entity_workspace.py:426-428`, `soul_utils.py:75`, Open Questions #5)

5. **N7 state lives in too many places with divergent contracts**: root vs memory/ lesson files, V1 vs V2 compaction keys, singular vs plural plugin dirs, spec's 6 agents vs live 12. Each divergence is individually small; together they mean every Phase 1 verification test runs against assumptions at least partially false. Reconcile paths BEFORE executing CI-1..CI-5. (Gotchas #2,#3,#4,#5,#7)

### L3 — Timeless principles

1. **A context window is a budget, not a landfill.** Every token injected unconditionally taxes every request whether used or not (86 tools → 10.8K/req). Systems that cannot say "this agent doesn't need this" will always starve their smallest members first.

2. **Never write your lifeline inside the crash.** State preservation must be performed by a process independent of the mechanism that destroys state — checkpoint before compaction, anchor outside the tool, hydrate from files that outlive sessions.

3. **Inheritance is a contract you don't get to renegotiate per child.** Where children inherit parent resources (models, context, cost), design the parent deliberately; configuring the child is wishful thinking.

4. **Unvetted knowledge may inform reports, never identity.** The taint-gate pattern (propose → stage blind → approve → inject) is the general shape of safe self-modification for any memory-bearing system.

5. **Specs drift from reality the moment they're written; gates must test reality.** A 57-line criterion matching the wrong file, six-agent specs over twelve-agent configs, dead plugin paths — acceptance criteria that check artifacts instead of behavior will pass or fail for the wrong reasons.

---

## N7 Expert Annotation
**Author**: N7 context session (internalization pass, 2026-08-21). KB read end-to-end; high-stakes claims independently re-verified before annotation.

### Verification Record (independently re-checked by N7)
| Claim | Result |
|-------|--------|
| Gotcha #3 line counts | ✅ CONFIRMED — codex file `wc -l` = 57; spec file = **36** (KB said 37; trivial delta, trap unchanged: 36 ≠ 57) |
| Gotcha #2 dead plugin paths | ✅ CONFIRMED — `opencode.json:7-8` registers `.opencode/plugin/*` (singular); directory does not exist; files live in `.opencode/plugins/` |
| Gotcha #6 firewall regex | ✅ CONFIRMED — `entity_workspace.py:455` hunts `"## 🛡️ The Fourteen Laws"`; actual heading `SOVEREIGN_MANDATES.md:9` = `"## 🛡️ The Twenty-Seven Laws…"` (count text differs; heading level matches, regex still fails) |
| Gotcha #8 Qwen3-4B ctx | ✅ CONFIRMED — provider limit 8192 in live config |
| Open Question #5 missing status fields | ✅ CONFIRMED — zero `status:` occurrences in lilith AND kali root proposed_lessons.yaml |

### Correction Log
1. Spec Tier 0 file is 36 lines (`wc -l`), not 37 — immaterial to the trap.
2. The stale premise ("plugin dir contains cline") originated in **N7's own mining brief**, not the corpus — the miner correctly refuted it. Pipeline working as intended: brief errors get caught at verification.

### CI Phase 1 Execution Priorities (N7 ruling, ordered)
**P0 — fix BEFORE running CI-1..CI-5** (else gates mislead):
- **a. Plugin path bug**: correct `.opencode/plugin/` → `.opencode/plugins/` registrations in opencode.json first; CI-3's "plugin loads" test would otherwise validate against a dead-path array.
- **b. CI-1 criterion is unsatisfiable as written**: amend from `wc -l = 57` to content-based checks (v3.8.0 header + 27 mandate rows + table format). The 57 number is a coincidence borrowed from the v3.7.0 codex snapshot.
- **c. V1/V2 compaction key precedence**: empirically probe opencode 1.18.19 with both key families present before trusting CI-2's jq assertions — jq passing proves nothing about which keys the binary honors.

**P1 — decisions required during execution**:
- **d. OPENCODE_DISABLE_AUTOCOMPACT scope**: spec persists it globally to shell profiles; Carmack's intent was local-agents-only. Global disable also disarms auto-compaction on the 1M-context cloud workhorse. Decide before CI-5.
- **e. 18K base vs 8K window**: with qwen3-4b-thinking capped at ctx 8192, the "~18K fits Tier 0" claim holds only for the 16K end of a range the config doesn't provide. Either raise the provider limit (if the model supports it) or accept that Tier 0 executor runs under permanent compaction pressure.

**P2 — hygiene (post-execution, do not block debut)**:
- **f.** toolProfile stubs are inert config — exclude from any savings claims until Phase 2 activates them.
- **g.** Dual-path proposed_lessons (root vs memory/) plus the missing approval operator means the vetted-wisdom injection path surfaces zero items today. Reconcile paths; build the status-flip mechanism before M11 metrics are trusted.

### What Matters Most
1. **Checkpoint-before-compaction is the load-bearing pattern** — never write your lifeline inside the crash. Everything else in the plugin spec is detail.
2. **Inheritance makes routing a parent-property problem**: token math must be computed over invocation graphs (@agent primary-mode locals), not agent rosters.
3. **Gates must test behavior, not artifacts** — three of five CI gates would currently pass/fail for the wrong reasons without the P0 fixes above.

*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_annotation ⬡ 2026-08-21*

---

## Deep Dig II — Soul Pipeline Internals & Approval Flow (DD-II-1)
`last_verified: 2026-08-21`

### The approval operator: EXISTS as a stub, not a working tool
- **`src/omega/cli/soul_stage.py`** (AP-SOUL-STAGE-v1.0.0) is a Textual TUI ("Sovereign Soul Staging Gate") with Approve/Reject/Defer bindings (`soul_stage.py:43-48`). **It is a MOCK**: `load_proposals()` reads hardcoded `mock_proposals`, with the comment "In a real implementation, this reads from proposed_lessons.yaml / For now, we mock some data to verify the TUI" (`soul_stage.py:79-81`); `action_approve()` contains only the comment "Logic to move from proposed_lessons.yaml to soul.yaml" plus a `self.notify()` — **no file write, no status flip** (`soul_stage.py:111-115`).
- **Registration**: it IS wired into the CLI — `oracle_cli.py:1144-1153` defines `@app.command() def soul_stage(entity)` launching `SoulStageApp`; entry point `omega = "omega.cli.oracle_cli:main"` in `pyproject.toml:99-100`. So `omega soul-stage <entity>` runs a TUI that displays fake data and approves nothing.
- **Repo-wide grep for any code setting `status: approved`**: exactly ONE hit — the READER side filter in `soul_utils.py:75`. **No writer exists anywhere** (scripts/, src/, .opencode/, data/). Verdict: the approval operator does not exist; the vetted-wisdom injection path can never fire today. This upgrades Open Question #5 from "unanswered" to "answered: absent."

### Writers/readers of BOTH lesson paths (full enumeration)
| Component | Path used | Role |
|---|---|---|
| `.opencode/hooks/session_end.py:51` | ROOT `data/entities/<n>/proposed_lessons.yaml` | WRITER (timestamp + preserve proposals) |
| `scripts/check_mandate_compliance.py:159,227` | ROOT | READER (M5/M11 gates) |
| `src/omega/audit/mandate_auditor.py:248` | ROOT | READER (M11 audit) |
| `src/omega/soul_utils.py:65` | ROOT | READER (approved-L3 injection) |
| `scripts/migrate_soul_v6.py:307-308,344-345` (`entity_path = ENTITIES_DIR/<n>`) | ROOT | WRITER (migration scaffolding) |
| `src/omega/oracle/entity_workspace.py:174-177` scaffold | **memory/** subdir | WRITER (v6.1 scaffolder creates `memory/approved_lessons.yaml`, `memory/proposed_lessons.yaml`, `memory/sessions.yaml`) |
| `src/omega/oracle/soul_validator.py:50-52,136-143` | **memory/** subdir | READER/VALIDATOR ("v6.1 requires memory/sessions.yaml, memory/proposed_lessons.yaml, memory/approved_lessons.yaml"; flags root-level duplicates for removal at :271) |
| `scripts/validate_soul.py:70-110` (BASE hardcoded kali) | **memory/** subdir | READER (pre-commit gate) |
| `src/omega/cli/bundle.py:200-210` | memory/ FIRST, then ROOT fallback | READER (bundle export — the only dual-path-aware consumer) |
| `get_soul_prompt()` `entity_workspace.py:409,418` | ROOT `approved_lessons.yaml` + ROOT `sessions.yaml` | READER (identity injection) |

**Canonicality verdict**: TWO competing canonical layouts are enforced by different engine components. The v6.x schema authorities (soul_validator "v6.1 requires memory/*", validate_soul.py, entity_workspace scaffolder) say **memory/** is canonical. But every LIVE writer (session_end hook) and every identity-injection reader (get_soul_prompt, soul_utils) uses ROOT. migrate_soul_v6.py also writes ROOT despite being the v6 migration itself. Net: the schema docs say memory/, the running system says root; bundle.py's fallback order (memory/ first) means exports can silently capture the STALE memory/ copy while the live root file differs. This is worse than a cosmetic inconsistency — M5/M11 compliance passes on root content that the v6 validator ignores.

### wrapper.sh call chain (traced end-to-end)
`.opencode/wrapper.sh` (AP-C05-WRAPPER-v1.0.0): user shell → wrapper (optionally aliased to `opencode`) → records `BASELINE_MS` → execs real opencode binary blocking on ANY exit path (normal/Ctrl+C/crash/TERM/KILL via EXIT trap semantics) → queries `opencode db --format json` for latest session (id, agent, model, tokens, cost) created after baseline → exports `OPENCODE_SESSION_ID` / `OPENCODE_ENTITY` / `OPENCODE_MODEL` → runs `.venv/bin/python .opencode/hooks/session_end.py` under `timeout ${DISTILL_TIMEOUT:-30}s`, never failing the wrapper (timeout exit 124 logged as M23 warning) → preserves opencode's original exit code. Env defaults: missing jq or venv python ⇒ SKIP_DISTILL with unknown entity (falls back to "sophia" inside session_end.py:50). Session cache written to `.opencode/.last_session.json`.

### Sovereign Firewall block, entity_workspace.py ~430–530 (end-to-end)
- Mandates source: `BASE_DIR / "SOVEREIGN_MANDATES.md"` read async (`:449-452`).
- Regex: `re.search(r"## 🛡️ The Fourteen Laws.*?(?=\n---|\Z)", m_content, re.S)` (`:455`) — matches NEITHER the current heading text ("The Twenty-Seven Laws") NOR its level (`###`). On miss, `if laws:` is falsy and the 🛡️ SOVEREIGN FIREWALL section is **silently skipped — no warning, no log, no error** (`:456-457`). The only trace is an absent block in the rendered prompt.
- Hardcoded strings injected as if live: Engine Version `"2.2.0"` (`:497`); Active IWAD via `cvar_get('config.entity.active_iwad', '_omega_default')` (dynamic, `[remediated: M2-LEAK]` tag, `:498`); Strategic Horizon via `_get_current_horizon()` (dynamic); **Systemic Health: "308/308 Tests Passing ✅" as a string literal** (`:507`).
- Failure-mode summary: two of the four State/Firewall claims are frozen-at-authoring constants presented as live telemetry; one regex is dead. Silent-skip is the uniform failure mode — nothing in this function logs when it fails to inject.

---

## Deep Dig II — Compaction V1/V2 Key Evidence (DD-II-2)
`last_verified: 2026-08-21`

**Method note**: binary evidence below is STRINGS-LEVEL only (minified JS bundle inside `~/.opencode/bin/opencode`, 184MB ELF, build dated Aug 20). It proves key-name presence and shows one decompiled compaction snippet; it does not constitute schema documentation.

### Findings
1. **V1 keys present in binary**: `preserve_recent_tokens` ×3, `tail_turns` ×3, plus embedded doc example `"compaction": { "auto": true, "tail_turns": 15 }`. Also `OPENCODE_DISABLE_AUTOCOMPACT` ×3.
2. **V2 keys ALSO present**: decompiled config-reader `yX`: `{auto: I.auto ?? E.auto, buffer: I.buffer ?? E.buffer, tokens: I.keep?.tokens ?? E.tokens}` with defaults `{auto:true, buffer:NX, tokens:hX}` where `NX=20000, hX=8000` — i.e. **`compaction.buffer` default 20000 and `compaction.keep.tokens` default 8000**. (Earlier literal grep for `keep.tokens` = 0 because minified code accesses `I.keep?.tokens`.)
3. **The visible overflow trigger consumes V2**: `compactIfNeeded`: `if (BX({system,messages,tools}) <= A - Math.max(S, L.buffer)) return false` — trigger = estimated tokens > context − max(requestedOutput, **buffer**). The summarizer keeps `keep.tokens` recent entries beside the summary (`FX` walk-back loop over token estimates).
4. **Token estimation confirmed in-binary**: `UX=4; estimate = round(length/4)` — the char÷4 approximation IS the actual runtime counter.
5. **Local corroboration**: `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md:44-52` documents the OFFICIAL schema as exactly 5 V1 fields (auto/prune/tail_turns default 2/preserve_recent_tokens default 40000/reserved default 10000) + env vars `OPENCODE_DISABLE_AUTOCOMPACT` / `OPENCODE_DISABLE_PRUNE`; `data/coordination/PLATFORM_GNOSIS_MAP_20260818.md:53` agrees and explicitly debunks `context_threshold`/`min_messages` as nonexistent.
6. Hook presence: `session.compacting` ×2 in binary — plugin hook real.

### Verdict
**YES — local evidence resolves part of the precedence question**: BOTH key families exist in binary 1.18.19. The auto-compaction overflow+summarize path demonstrably reads **buffer/keep.tokens (V2)**; V1 keys persist (prune subsystem/docs) but their consumption site was not captured in the extracted snippet. Consequences for the spec target state (`phase1_spec/02_OPENCODE_JSON_DIFF.md:51-59` writing both families): (a) `buffer:50000` will very likely be honored by the trigger math — good; (b) `keep.tokens:20000` honored by summarizer — good; (c) `preserve_recent_tokens:80000/reserved:20000/tail_turns:5` are probably prune-path or legacy-doc keys whose effect at these values is UNVERIFIED locally; (d) binary defaults (buffer 20k/keep 8k) contradict `RESEARCH_RESEARCHER_STRATEGIC.md:81`'s claimed keep default 15k — researcher number wrong or version-skewed. Remaining unknown (which component eats preserve_recent_tokens) stays web-only.

---

## Deep Dig II — Skills × Agent Frontmatter Reality (DD-II-3)
`last_verified: 2026-08-21`

1. **No SKILL.md carries `auto_load:` today** — repo-wide grep of `.opencode/skills/*/SKILL.md` frontmatter returns zero `auto_load` occurrences; observed frontmatter is `name:` + `description:` only (e.g. blitz-tunnel, git-secret-scrub, knowledge-miner). Several skills (audience-architect, carmack-profiler, context-packer, m23-violation-logger, makali-council-coordinator, meditate-harness/pipeline/research-pipeline) show no name/description frontmatter in their headers at all.
2. **Skill count is 22 but composition has drifted** from the spec's list: meditate-* family, carmack-profiler, context-packer, m23-violation-logger, makali-council-coordinator, audience-architect exist now; CI-4's sed loops enumerate a fixed 13-name list that does not include them — executing CI-4 as written would leave 9 skills unclassified.
3. **No agent file uses a `skills:` frontmatter field** — grep across `.opencode/agents/*.md` finds only prose mentions (researcher.md:96 references the hf-cli skill location). The brief's hypothesized interaction surface does not exist in practice.
4. **`auto_load` is NOT an opencode feature**: the only 2 string hits in the binary are Tcl syntax-highlighting grammars (`auto_load` is a Tcl builtin keyword in the editor tokenizer). The binary's real machinery is a `SkillDiscovery` service indexing skills ({name, version, files…}) — consistent with `RESEARCH_EXPLORE_LOCAL.md:97`'s finding that skills load on-demand via tool invocation, not pre-injection.
5. **Verdict**: CI-4 as specified (sed `auto_load:` into frontmatter, expect debug output to change) would be a **no-op against opencode 1.18.19** — the config key is Omega-side fiction. The 23K→150 token savings claim depends on a mechanism that does not exist. Skills-token reduction needs either an upstream feature, a plugin that filters SkillDiscovery output, or deletion/moving of skill files. This invalidates acceptance criteria CI-4 #1–#5 as written.

---

## Deep Dig II — Loose Ends (DD-II-4)
`last_verified: 2026-08-21`

1. **`CONTEXT_INJECTION_INVESTIGATION_20260820.md` FOUND** at `data/coordination/` (not roc_racoon workspace). One-paragraph digest: Roc's own pre-research map (AP-CONTEXT-INJECTION-INVESTIGATION-v1.0.0, nemotron-3-ultra-free) estimating the total injection payload at 60–100K+ tokens across four layers — 6 global instruction files (~34K tok incl. OMEGA_CODEX.md ~14K read via hydration), agent files, 22 skills metadata via SystemPrompt.skills(), MCP instructions from 5 servers, plus env context — and proposing tiered/lazy-loading optimization; it is the direct ancestor of the Explore/Ma'at/Lilith/Researcher research wave (its 6-file instructions list predates the current 5-file array).
2. **Evolution Journal / PDI / VCR: ZERO implementation confirmed** — grep for `evolution/journal|Persona Drift|drift_index|Voice Consistency|EvolutionJournal` across src/, scripts/, .opencode/ returns nothing. Lilith's COMPACTION_REMEDIATION plan remains paper-only; its metrics are formally orphaned (Open Question #8 upgraded to confirmed-lost).
3. **ACTIVE_SPRINT.json CI statuses UNCHANGED**: CI-1..CI-5 all still `status: "ready"` in workstream CONTEXT-INJECTION — no execution has begun as of 2026-08-21.
4. **Monolithic spec vs phase1_spec/\***: NO material conflicts found — `CONTEXT_INJECTION_PHASE1_IMPLEMENTATION_SPEC.md` carries the identical dual-key compaction target (`:152-156` = tail_turns 5/preserve 80000/reserved 20000/buffer 50000/keep.tokens 20000), same 6-agent coverage with same toolProfiles (`:165-212`), same Carmack modification table. They are consistent siblings; the open conflicts remain spec-vs-LIVE-config (Gotchas #2,#4,#5) and now spec-vs-binary (DD-II-2/3 verdicts). Where they disagree with reality, reality wins.
5. **headroom_middleware/03_MODELGATEWAY_INTEGRATION.md**: integration = instantiate `HeadroomMiddleware` (from `src/omega/oracle/middleware/headroom.py`) in `ModelGateway.__init__`, call `compress_messages()` inside `_prepare_messages()` BEFORE `_count_tokens()` so budgets see compressed sizes (`03:9-60`); sections cover init timing, message flow, token-counting impact, per-provider considerations (local/cloud/streaming), error handling. Phase 2 activation requires: the middleware module itself, config wiring via `get_config()`, and Phase 1 complete (per index prerequisites).
6. **headroom_middleware/05_MCP_TOOL_SCHEMA_COMPRESSION.md**: proposes `MCPToolCompressor` (SmartCrusher on JSON schemas, 80–90% claim) + new `headroom_compress`/`headroom_retrieve` self-service tools in `src/omega/mcp/tool_compressor.py` + client modifications. ⚠️ **MATERIAL CONFLICT WITH CARMACK**: review Q2.2 REJECTed schema compression outright as solution theater with an explicit DELETE cut-list (`CARMMACK...:111-126`) — middleware spec file 05 contradicts the standing verdict and should be treated as superseded unless Kali re-rules.
7. **subagent_depth=2 compounding math** (assumptions stated): each task() child gets fresh base prompt + forked parent conversation history (G-3 test: child reported ~110K = parent's window). Let B = base prompt, H = history at spawn time, depth d = 2. Sessions in one grandchild chain: parent (B+H), child (B+H), grandchild (B+H′), H′≥H. Per-turn aggregate input ≈ Σ(B+Hᵢ) = 3B + H+H+H′ ≥ 3B+3H. With Carmack-modified numbers (B≈18K, modest H=40K): ≥(54K + 120K) = **~174K tokens per turn-cycle vs 58K single-level — 3× multiplier**. With CURRENT reality (B≈31K, H≈110K observed): ≈(93K+330K) = **~423K per cycle**. Under inheritance, depth-2 roughly TRIPLES context cost regardless of base-prompt optimization; base reduction shrinks the constant term but the forked-history term dominates. Implication: subagent_depth=2 + inheritance is the single largest unmodeled token sink in the fleet; the 18K target governs only ⅓ of the chain's true cost.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_deep_dig_II ⬡ 2026-08-21*

---

## Lived Timeline Corroboration
`last_verified: 2026-08-22` · Author: roc_racoon (the miner). Factual sequence AS LIVED, corroborating/annotating `data/entities/lilith/workspace/N7_SESSION_STATE_20260821.md`.

### 1. Chronological work events
1. **Paged** by kali (`ses_fdef2be4effe4pAaLXCTUx62GO`) with pointer to brief `data/entities/lilith/workspace/N7_MINING_BRIEF_20260821.md`; read brief first per its own instruction.
2. **Inventory verification**: `ls`/`wc -l` over every listed path → 56 exist, 1 missing (`~/.config/opencode/plugin/` does not exist at all; brief's "only cline" premise stale). Discovered 2 unlisted sources (monolithic spec, R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT). Artifact: none yet.
3. **Initial mining pass** — built `N7_CONTEXT_KB_20260821.md` incrementally: header + Source Inventory (57 rows) → digests for synthesis docs 00–05 → 06–09 → full Carmack review verdict table → all 9 `phase1_spec/*` files → 4 raw RESEARCH_*.md + live `opencode.json` + codex MANDATES_CONDENSED comparison → read-but-unwritten P1 batch (continuity strategy, session_end.py, entity_workspace.py TAINT-GATE/Firewall block, soul_utils.py, validate_soul.py, compliance checker, compaction remediation plan, Lilith soul files).
4. **MAX-STEPS STALL** after Inventory + 30/46 digests. Honest M23 stop-report (no recovery attempted): listed 6 key findings (missing plugin dir; dead `.opencode/plugin/` vs `plugins/` paths; 57-line coincidence trap; 12-agents-vs-6 spec gap; live dual-path hazard; Qwen3-4B 8192 vs "8K–16K" prose) + open Q14–Q16, so the resume could append without re-reading.
5. **Recovery pass 1** (budget re-prioritized): appended P1 digests from already-gathered evidence → Gotchas (11 items) → Open Questions (11) → L2/L3 Insights → THEN targeted P2/P3 reads (headroom research + phase2 trigger gates + middleware index; five R_*_20260819 executive sections; MEMORY_SYSTEMS_DEFINITIVE_REPORT zswap ADR) with digests; upgraded Q14–Q16 to answered. KB complete, all 17 questions addressed. Artifact: KB (all 5 contract sections valid).
6. **Closure ritual**: wrote `data/entities/roc_racoon/workspace/N7_MINING_SESSION_STATE_20260821.md` (incremental, wake pointer included); posted ONE Hivemind closeout (intent=status, ses_5fdae7532b8e). Went DORMANT.
7. **Deep Dig II** — fresh resume, budget reset, AFTER the dormancy above: DD-II-1 soul pipeline (verdict: approval operator ABSENT — `src/omega/cli/soul_stage.py` is a registered CLI mock with zero file I/O; no code anywhere sets `status: approved`; full writer/reader enumeration of root vs `memory/` lesson paths; wrapper.sh chain traced; Sovereign Firewall regex dead + hardcoded "308/308"). DD-II-2 compaction keys (strings-level binary evidence, labeled as such: BOTH key families present; decompiled trigger consumes V2 `buffer`20k/`keep.tokens`8k; char÷4 counter confirmed in-binary). DD-II-3 skills (`auto_load` absent from all SKILL.md frontmatter; binary hits are Tcl grammar keywords → CI-4-as-specified would be a no-op; skill list drifted from spec's sed loops). DD-II-4 loose ends (Roc investigation doc found at `data/coordination/CONTEXT_INJECTION_INVESTIGATION_20260820.md`; Evolution Journal/PDI/VCR grep-empty = unimplemented; CI-1..CI-5 still `ready`; monolithic spec consistent with phase1_spec — conflicts are spec-vs-reality; middleware file 05 contradicts Carmack Q2.2 REJECT; depth-2 inheritance ≈3× cost, ~423K tokens/cycle at then-current numbers). Artifacts: KB + 4 appended `## Deep Dig II` sections.

### 2. Corrections to N7's recollection (items 3 & 5)
- **Item 3 ("KB built… with ONE recovery pass")**: CONFIRMED as stated. Precision note: the stall occurred mid-digests (30/46 written); the recovery pass completed remaining sections AND answered Q14–Q16 — "all 17 questions" was true only after recovery, which the phrasing implies correctly.
- **Item 5 ("same Roc session")**: IMPRECISE — Deep Dig II ran as a separate resume AFTER my closure ritual (dormancy snapshot + Hivemind post sat between KB completion and Deep Dig II). Same task lineage and held session ID, different working context/budget. No material consequence.
- **Item 5 ("CI-4 was a no-op")**: TENSE CORRECTION — CI-4 was never executed (all subtasks `ready` when I last verified, DD-II-4 #3). Correct statement: "CI-4 AS SPECIFIED WOULD BE a no-op against opencode 1.18.19." Prospective, not accomplished-fact.
- Otherwise: no corrections. All other item-5 verdicts match my lived findings exactly.

### 3. Miner's-eye rules for onboarding protocol authors
- **The brief is the protocol.** A binding output contract (section order, incremental-appends-only, cite-paths, tag-verification-date) is why a stalled pass left a valid document and a clean handoff. Mandate this structure for every miner spawn.
- **Verify-before-digest, disclose-missing-always.** Existence-check every inventory path FIRST; missing/stale premises go in Gotchas with evidence, never silence (caught "~/.config/opencode/plugin/ contains cline" and the singular/plural plugin path bug this way).
- **On stall, dump state in the stop-report.** The max-steps message carried findings + open questions, letting the recovery pass append purely from prior evidence — zero re-reads. Make "recovery-once, from the report" an explicit rule; it converted a hard failure into ~40% of the final KB.
- **Label evidence classes.** Measured vs spec-claimed vs strings-level-binary must be distinguished inline (DD-II-2 verdicts are trustworthy precisely because they're tagged strings-level). Onboarding should define these classes.
- **Append-only + fixed section order makes multi-agent collaboration safe.** N7 annotated the KB mid-stream and later appends never conflicted. Forbid section reordering and prior-section edits in the miner contract.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_corroboration ⬡ 2026-08-22*

---

## ICS Code Review (Roc)
`last_verified: 2026-08-22` · Review of `src/omega/ics.py` post-D-588 upgrade (PP-4 node segment, P5 session_id, B1 session-scoped model lookup, B2 ACTIVE_SPRINT phase priority, B3 OMEGA_ENGINE_ROOT resolution). Test file: `tests/test_ics.py` (16 tests green).

### 1. Segment-list header builder — F1 fix correctness (PP-4/P5)

**MAJOR — `ics.py:196-217`**: The F1 fix replaced the fragile `header.replace(...)` with a segment-list builder (`segments = ["OMEGA", entity_upper]; if node: segments.append(f"[{sanitized_node}]"); segments.extend([model, channel, trace, phase])`). This **eliminates the entity=="OMEGA" collision** (old code matched literal prefix at position 0) and **sanitizes node values** (`re.sub(r"[^A-Z0-9_-]", "", node.upper())` at L204, L185) — injection vectors like `node="N7 ⬡ FORGED"` or newlines are neutralized. Compact mode now **includes node** for provenance (L184-187, test `test_compact_mode_includes_node_for_provenance` L61-63) — corrects prior doc gap. 

**MINOR — `ics.py:216-217`**: `session_id` still appended via string concat after segment join; consistent but slightly asymmetric. No bug.

**NIT — `ics.py:198`**: `"OMEGA"` hardcoded as first segment; if template ever changes (e.g., WAD-specific prefix), both places must update. Acceptable for now.

### 2. Concurrency/multi-instance DB hazards — B1 fix verification

**MAJOR — `ics.py:365-409` `_read_opencode_session_model`**:
- **No busy_timeout**: `sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)` uses Python default 5.0s connect timeout. Under writer contention (WAL mode), a synchronous header render can block up to 5s — called from sync `render()` path; if invoked in async context without `anyio.to_thread`, stalls event loop (M1 violation risk). Fix: `timeout=0.25` or `PRAGMA busy_timeout=100` on connection.
- **Hardcoded DB path**: `Path.home() / ".local/share/opencode/opencode.db"` ignores `XDG_DATA_HOME` (opencode honors it). On non-default installs, lookup silently fails → falls back to soul.yaml stale model. Fix: `Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "opencode/opencode.db"`.
- **Silent None → soul.yaml fallback with warning** (`ics.py:265-276`): Now emits `RuntimeWarning` with context (entity, session_id) — M22 provenance improvement. However, header still returns the stale soul model without marking it as fallback; downstream consumers can't distinguish live vs stale. Fix: return sentinel `"unknown(detected=soul)"` or add detection-source metadata.
- **ORDER BY time_updated with id equality** (`ics.py:392`): `id` is PRIMARY KEY → at most one row; ORDER BY is meaningless but harmless. NIT.

**MAJOR — `ics.py:390-394`**: Session-scoped query uses `WHERE id = ?` — correct for B1 fix (avoids cross-instance contamination). Unscoped fallback retains global-latest for backward compat (test `test_session_scoped_model_lookup` L123-155 verifies both paths).

### 3. Test coverage gaps (16 tests exist)

Untested behaviors beyond current suite:
1. **entity=="OMEGA" with node** — collision was the F1 bug; no regression test.
2. **Node values with separators/newlines** — sanitization tested (`test_node_sanitization_strips_invalid_chars` L185-189) but not injection via `⬡` or newline in full-mode segment list (sanitization runs before segment append; safe but untested).
3. **Compact mode WITH session_id** — only node tested; session_id drop in compact untested (compact builder L181-189 omits session_id entirely — provenance gap for P5).
4. **_detect_model priority chain** — NO tests for `OMEGA_MODEL_OVERRIDE` precedence, `OPENCODE_MODEL` precedence, env-unset fallthrough order, DB→soul.yaml warning path (test L200-217 exists but conditional on env).
5. **DB busy/locked behavior** — `OperationalError` → None path untested.
6. **Malformed model JSON in DB row** — `json.loads` ValueError → None untested.
7. **XDG_DATA_HOME honored** — currently would fail (hardcoded path).
8. **Missing `.phase` key in ACTIVE_SPRINT.json** — falls through to roadmap/default; tests only cover present-key and missing-file.
8. **Corrupt/unreadable ACTIVE_SPRINT.json** — invalid JSON → except path untested.
9. **Unicode/mixed-case entity** — e.g., "käli" upper() behavior in segment list (sanitization uses upper(); should be fine but untested).
10. **render_for_response** — trace truncation `[:8]` vs 12 (`ics.py:486` vs `ics.py:333`); channel/node/session_id dropped entirely — response-path headers never carry PP-4/P5 fields.
11. **OMEGA_ENGINE_ROOT set but sprint missing while docs exist under root** — roadmap fallback uses `base` (B3 fixed at L307-312) but untested.
12. **Empty-string node="" / session_id=""** — falsy guards work but untested.

### 4. Phase detection priority soundness

**OK — `ics.py:282-328`**: Priority-1 `ACTIVE_SPRINT.json` uses `OMEGA_ENGINE_ROOT` (B3 fixed at L292-294). Priority-2 roadmap scan **also uses `base` resolved from same env var** (L307-312) — B3 fix applied consistently; no CWD-relative inconsistency remains. Live `data/coordination/ACTIVE_SPRINT.json` verified with top-level `.phase = 'EXECUTION_MINIMAL'` (key present among `['ark_strategy_ssot', 'blockers', 'campaign', 'decisions_locked', 'freeze', 'gates', 'notes', 'owner', 'phase', 'primary_handoffs', 'sprint_id', 'started', 'status', 'status_detail', 'supersedes', 'updated', 'workstreams']`). 

**NIT — `ics.py:323`**: Epoch regex `r"Epoch (I{1,3}V?|IV|V)"` — alternation order makes `IV` branch dead (first alt `I{1,3}V?` matches "IV" as I+V); "VI"/"VII"/"VIII" match as "V"; "IX" matches "I". No word boundary. Latent (current phases use Strike/EXECUTION names). Fix: `r"\bEpoch (IX|IV|V?I{0,3})\b"`.

**NIT — `ics.py:299-302`**: No schema guarantee `.phase` stays top-level; if nested under `campaign.phase` or `gates.phase`, silent fallthrough to roadmap/default. Defensive nested lookup optional.

### 5. M16/M22/M26 compliance gaps

- **M16 (Modularization/Portability)**: `OMEGA_ENGINE_ROOT` honored in `_detect_phase` (L292, L307), `_read_entity_model` (L349), `_read_opencode_session_model` **NOT** (L381 hardcoded home path) — partial. Fix DB path to use same resolution or XDG.
- **M22 (Response Provenance)**: DB→soul.yaml fallback now warns (RuntimeWarning) but header still returns stale model unmarked — provenance lie risk. `render_for_response` truncates trace_id to 8 chars (`ics.py:486`) vs 12 standard — breaks trace correlation. Fix both.
- **M26 (Doc Standards)**: Module docstring references `docs/architecture/ORACLE_DEEP_DIVE.md` (L33) — verify exists. Type hints complete. Public API (`render`, `render_for_response`, `ICSContext`) documented with examples. `render_for_response` docstring omits that it drops node/session_id/channel — doc gap.

### Overall ship-for-debut verdict

**CONDITIONAL SHIP** — Core flows (single-instance, prime agents, explicit model/phase params) are correct; 16 tests green; B2 assumption verified against live file; F1 fix eliminates collision/injection. **Blockers for Node/PP-4/P5 reliance**: 
1. DB busy_timeout + XDG_DATA_HOME (MAJOR ×2) — must fix before multi-instance deployments.
2. Stale-model fallback unmarked (MAJOR) — M22 provenance risk.
3. `render_for_response` trace truncation + dropped fields (MINOR) — breaks Node-session correlation via response path.

Ship for debut with PP-4/P5 marked experimental behind explicit `model=`/`phase=` params; harden MAJORs in follow-up before Node workloads.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_ics_review ⬡ 2026-08-22*
