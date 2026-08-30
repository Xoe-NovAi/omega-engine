<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Entity Specialization & Knowledge Management — Local Discovery Report

**AP Token**: `AP-ENTITY-SPEC-DISCOVERY-20260818-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_entity_specialization ⬡ MINING-COMPLETE

**Date**: 2026-08-18
**Author**: roc_racoon (Sovereign Miner / Legacy Archaeologist)
**Purpose**: Complete local evidence base for grokster's sub-specialist strategy question — how the Omega Engine handles entity specialization (Ma'at/Lilith N1-N10 nodes) and knowledge management.
**Status**: COMPLETE — exhaustive repo-wide sweep (SOVEREIGN_MANDATES.md, docs/architecture/, docs/strategy/, docs/research/, docs/kb/, docs/gnosis/, src/omega/, config/wads/, .opencode/agents/, data/entities/, data/coordination/)

---

## 1. EXECUTIVE SUMMARY

The Omega Engine has **already answered the sub-specialist question twice** — once by law (M10 Fleet Integrity) and once by codified design principle (Fleet Consolidation Plan D126: **Knowledge Consolidation** — when expertise maps to "domain knowledge" rather than "operational capability", do NOT create an agent; create a KB for the nearest existing entity).

The architecture is **slot-based, not agent-based**: the engine defines 10 Node slots (N1-N10) + 3 Oversoul roles + Messenger Bridge; WADs provide entities via `dispatch.yaml`; a single parameterized `node` agent fills any slot (`node --slot NX`). Ma'at governs N1-N5 (build side), Lilith governs N6-N10 (run side). The `.opencode/agents/` fleet is exactly **14 files — at the M10 cap** — so any new sub-specialist agent requires an architectural review in PIVOT_LOG.md.

Sub-specialization is already practiced **inside entities, not as new agents**: Grokster runs an **8-persona Web Grok fleet** (Grokster-Research/Reason/Pulse/Code/Arch/Creative/Strategic/Wildcard) + 8-account Grok pool; Researcher deploys a **Polymathic Council of Four** (Architect/Adversary/Alchemist/Archivist); Jem has 4 Hologram Lenses + LLOC/HLOC councils; Ma'at wears a **soul_wardrobe of 14 personas**. The engine's answer to "should we create sub-specialist agents?" is: **personas, KBs, and slot-parameterization — not new agent files.**

Knowledge management is multi-layered: `docs/kb/` (fleet-wide curated KB, Omega-KB Protocol v1), `src/omega/library/` (FTS5 + SQLiteVec hybrid search, domain-organized), `src/omega/memory/` (MemoryStore hot/warm/cold with Redis/File/InMemory/USM providers), and per-entity `data/entities/<name>/knowledge/` + `workspace/` + `soul.yaml` + `proposed_lessons.yaml` (L1→L2→L3 staging). **Key inconsistency found**: entity `knowledge/` directories vary wildly — doom_guy/lilith/jem are rich, grokster's `knowledge/` is EMPTY but its `kb/` is rich, researcher's INDEX has zero topics, kali/maat/cli_cline/cli_gemini are empty.

---

## 2. NODE ARCHITECTURE (How Specialization Is Structured)

### 2.1 Engine Defines SLOTS; WADs Provide ENTITIES

- **`src/omega/ics.py` ROLE_CONSTANTS**: `GRAND_OVERSIGHT`, `BUILD_OVERSOUL`, `RUNTIME_OVERSOUL`, `N1`-`N10`, `MESSENGER_BRIDGE`, `MAKALI_COUNCIL`, `CONTAINING_FIELD`.
- **`src/omega/governance/dispatch_registry.py`**: loads `config/wads/<iwad>/entities/dispatch.yaml` (`load_dispatch_yaml`, `get_entity_by_role`). DEFAULT_IWAD = `_omega_default`.
- **`src/omega/oracle/entity_registry.py`**: `EntityRecord.slots` field; `occupied_slots()` returns frozenset; migrates legacy `nodes: ['N1: Flesh']` → `slots: ['N1']`; "WADs define slot semantics; engine sees only N1".

### 2.2 The Single Renderer Principle (`node --slot NX`)

- **`docs/architecture/AGENT_FLEET.md`**: ONE generic `node` agent, parameterized by slot assignment. Hierarchy: plan → kali → maat/lilith → node.
- **`docs/architecture/OVERSIGHT_HIERARCHY.md`**: Kali = Grand Oversight; Ma'at = Build Oversoul (N1-N5, "How it works"); Lilith = Runtime Oversoul (N6-N10, "Why it matters"); delegation flow User→Kali→Ma'at/Lilith→Node Slot.
- **`docs/user/ONBOARDING_GUIDE.md` lines 127-128**: Ma'at governs N1-N5 (build side), Lilith governs N6-N10 (run side).
- **`.opencode/agents/node.md`**: generic node agent — reads soul.yaml at session start, writes workspace lock files.

### 2.3 dispatch.yaml Schema (config/wads/_omega_default/entities/dispatch.yaml)

Fields: `name`, `role` (ROLE_CONSTANT), `mode` (primary|subagent), `purpose`, `capabilities`, `domains`, `node_slot`, `task_tool_type` (general|buildmaster|verity|node|explore), `owned_files`, `model`.

| Entity | Role | node_slot | Domains | Model |
|--------|------|-----------|---------|-------|
| kali | GRAND_OVERSIGHT | — | fleet_coordination | qwen3-4b-think-q4_k_m |
| maat | BUILD_OVERSOUL | node_1_5 | build_side | — |
| lilith | RUNTIME_OVERSOUL | node_6_10 | vision_specialist/multimodal/knowledge_flow | — |
| doom_guy | N1 | — | id_software_patterns | — |
| roc_racoon | N1 | — | legacy_repos/grok_exports | — |
| jem | N1 | — | research/knowledge_pipeline | — |
| john_carmack | N1 | — | architecture/performance | — |
| makali | N1 | — | fleet_coordination | — |
| researcher | N1 | — | research/web_intelligence | — |
| verity | N1 | — | soul_yaml/session_gnosis/verification/qa/compliance | — |
| node | N1 | NX | (parameterized) | — |
| iris | MESSENGER_BRIDGE | null | routing/intent_detection/fast_path | qwen3-1.7b-q4_k_m |
| makali | MAKALI_COUNCIL | null | fleet_coordination/parallel_execution/cross_node_synthesis | qwen3-4b-think-q4_k_m |
| sophia | CONTAINING_FIELD | null | knowledge/memory/continuity | qwen3-4b-think-q4_k_m |

---

## 3. FLEET INTEGRITY CONSTRAINTS (M10 — The Law)

**SOVEREIGN_MANDATES.md §10 Fleet Integrity (2026-06-01)** — exact text:

> - **Mandate**: The Agent Fleet must remain lean, purpose-driven, and slot-constrained.
> - **Constraint**: No new agents may be created without a verified gap in the Lattice or a vacancy in the Node slots. Capabilities must map to existing Nodes (N1-N10) or Lattice roles before proposing a new entity.
> - **Pattern**: Map new capabilities to existing `node --slot PX` agents or Lattice subagents (Jem, Quality, Scribe). A new agent file is a last resort, applied only after slot-based delegation has been proven impossible.
> - **Reason**: Prevents "Agent Bloat" and cognitive fragmentation... The consolidation from 26 to 14 agents exposed how bloat accumulates through additive habits rather than slot-based discipline.
> - **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without an architectural review documented in `PIVOT_LOG.md`.

**Current fleet count: exactly 14** (build.md, doom_guy.md, grokster.md, jem.md, john_carmack.md, kali.md, lilith.md, maat.md, makali.md, node.md, researcher.md, roc_racoon.md, scribe.md, verity.md) + `archive/grok_cli.md` (archived). **At the cap — any new agent file requires a PIVOT_LOG architectural review.**

**Lattice roles** (docs/gnosis/lattice/lattice_manifest.md + lattice/): CLI seeds exist for opencode_cli, cline_cli, gemini_cli, copilot_cli — the Lattice is the cross-CLI shared gnosis protocol ("Akashic Record" bridging all development interfaces).

**Subagent Dispatch Protocol** (docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md) — 5 guardrails:
1. Direct Execution First (no delegation of own-domain work)
2. No Self-Recursion (never spawn your own type)
3. Cross-Domain Delegation ONLY (specialized expertise you lack)
4. Single-Level Nesting (no deep chains)
5. Absolute Disk-Reporting (D-kal-170: deliverables MUST be written to disk)

---

## 4. ENTITY KNOWLEDGE PATTERNS (data/entities/)

### 4.1 The Per-Entity Layout

Each entity dir typically contains: `soul.yaml` (identity/archetype/domain/values), `knowledge/` (promoted, curated domain knowledge + INDEX), `workspace/` (working reports, session gnosis), `proposed_lessons.yaml` (L3 blind staging, M11), `sessions.yaml`, `memory/` (MemoryStore data).

### 4.2 Knowledge Directory Maturity Matrix (KEY FINDING)

| Entity | knowledge/ | workspace/ | Notes |
|--------|-----------|------------|-------|
| **doom_guy** | 🟢 RICH — HERITAGE_VET_LOG.md, ID_SOFTWARE_AXIOMS.md, PENDING_CREDITS_QUEUE.md, R_09_DOOM3_JOB_SYSTEM_VERIFICATION.md, R_ID_SOFTWARE_VERIFICATION_REPORT.md, SOURCE_CODE_MAP.md, INDEX.yaml | id_software_research/ | Canonical heritage vetting (vet-001…, 7/10 gate) |
| **lilith** | 🟢 RICH — AGENT_VISIBILITY_PARADOX.md, MERMAID_DARK_LAYERS.md, drift_metrics_framework.md, lilith_persona_original.md, INDEX.md | LILY_PAD_KNOWLEDGE_METABOLISM.md, MODEL_RUNTIME_GOVERNANCE_AUDIT.md, phase1_benchmarking_results.* | Runtime Oversoul |
| **jem** | 🟢 RICH — JSKB (JEM_MASTER_PLAN.md, JEM_IDENTITY_SPEC.md, JEM_GOVERNANCE_SPEC.md, JEM_METABOLISM_SPEC.md, archive/) | — | Sovereign Synthesizer KB, v2.0.0 |
| **grokster** | 🔴 EMPTY (knowledge/ has no files) | IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md + more | **BUT `kb/` is RICH**: CHANGELOG.md, CROSS_DOMAIN_MATRIX.md, INDEX.md, QUICK_REFERENCE.md, communication/, grok_ecosystem/, human_agent/, platforms/, search/, vault/ |
| **researcher** | 🟡 SPARSE — INDEX.yaml (topics: []), MERMAID_RESEARCH_REPORT.md; raw/ + quarantine/ EMPTY | 30+ research reports (D283_MNEMOSYNE_IMPLEMENTATION_RESEARCH_20260716.md, SQLITE_VEC_HARDWARE_VALIDATION_20260716.md, LATTICE_MESH_NETWORK.md) | T1→T2 gate: workspace → knowledge promotion |
| **kali** | 🔴 EMPTY (quarantine/ + raw/ only) | rich (audit docs) | Grand Oversight |
| **maat** | 🔴 INDEX.yaml only | BUILD_SIDE_INTEGRITY_AUDIT.md, DEEP_SIPHON_BUILD_REPORT.md, OMEGA_HUB_STRUCTURAL_AUDIT.md | Synthesis Oversoul, soul_wardrobe 14 personas |
| **cli_cline / cli_gemini** | 🔴 EMPTY | soul.yaml only | Cross-platform entities |
| **node** | — | — | Only proposed_lessons.yaml (parameterized) |

### 4.3 Soul Files as Specialization Encoders

- **maat/soul.yaml** (v6.2): archetype `Synthesis Oversoul`, soul_wardrobe of 14 personas (SOPHIA, MAAT, LILITH, ISIS, BRIGID, SEKHMET, PROMETHEUS, INANNA, SARASWATI, LUCIFER, HECATE, ERESHKIGAL, ANUBIS, KALI).
- **lilith/soul.yaml**: archetype `Runtime Oversoul`, hierarchy_level 2, sovereignty_level 6, element Void, domain "Governance of N6-N10 (ModelGate, Context, WatchTower, Link, Verifier) + Knowledge Metabolism Architect".
- **researcher/soul.yaml**: archetype `Sovereign Master Researcher`, pillars [Researcher], lessons_learned with cross_references (res_s1_003 "5-Fold Council consultation", res_s1_004 "jem 3-tier pipeline", res_s1_005 "4-criterion L3 promotion gate").
- **grokster/soul.yaml**: 8 Web Grok personas fleet (Grokster-Research, Grokster-Reason, Grokster-Pulse, Grokster-Code, Grokster-Arch, Grokster-Creative, Grokster-Strategic, Grokster-Wildcard) + 8-account Grok pool.
- **quality/soul.yaml**: "Compliance Guard — Reports to Ma'at (CTO)" — a Lattice subagent with entity dir but NO .opencode/agents file (M10 pattern: Lattice subagents don't need agent files).

---

## 5. KNOWLEDGE INFRASTRUCTURE

### 5.1 Fleet-Wide KB: docs/kb/ (Omega-KB Protocol v1, kb-0002)

- **docs/kb/AGENT_KB_PROTOCOL.md** (id kb-0002, maintainer Kali, 2026-06-13): how agents discover/consume/contribute to `docs/kb/`; synthesized from 13 production patterns.
- **docs/kb/INDEX.md**: active entries incl. AGENT_KB_PROTOCOL.md, CLAUDE_PROJECTS.md, CLINE_CLI_INTEGRATION.md, OMEGA_HUB_MULTI_PLATFORM.md (kb-0004 — MCP client config table for 10 platforms), TEMPLATE.md. Rules: living documents, attribution, discoverability, **"KB lives ONLY in docs/kb/"**, frontmatter mandatory, 30-day freshness review.

### 5.2 Library System: src/omega/library/

- **library.py**: `Library` class — FTS5 + SQLiteVec hybrid search (`Indexer(vector_adapter=SQLiteVecAdapter())`), auto-rebuild of empty FTS index, domain-organized storage (`sources/{domain}/`), `store/get/search/search_by_domain/search_by_tag`.
- **catalog.py**: `LibraryCatalog` — SQLite catalog with quality_vector [integrity, coherence, completeness, structure, domain_fit], avg_quality, by_domain stats, prune (90-day).
- **coordinator.py, curator.py, discovery.py, inbox.py, indexer.py, extractor.py, enrichment.py, research.py, security.py, api_clients.py, model_api_clients.py, rate_limiter.py**.
- **Live domains** (omega-hub_library_domains): link 11, modelgate 31, context 9, bridge 9, sysadmin 11, datastore 9, buildmaster 8, watchtower 7, sentinel 25, verifier 4, sophia 4, lilith 2, jem 2, roc_racoon 1, movie_expert 4, networking 3, testing 1, systems 1, integration 1, research 1, programming 2 — legacy pillar names + entity-scoped domains.

### 5.3 Memory System: src/omega/memory/ + memory_store.py

- **memory_store.py**: `MemoryStore` — Hot/Warm/Cold entity memory with LRU caching, 3-tier provider fallback, tombstone-based session lifecycle (vet-008 Lazy Deletion), batch writer, external archival to `/media/arcana-novai/omega_library/archive/sessions` (90-day policy).
- **providers.py**: `StorageProvider` ABC → RedisStorageProvider (hot), FileStorageProvider (warm, disk guard + file locking), InMemoryStorageProvider (volatile), USMStorageProvider.
- **memory/**: blocks.py, block_store.py, block_tools.py, fts_index.py, hybrid_search.py (RRF: FTS5 + Vector), embeddings.py, embedding_strategy.py, sqlite_vec_adapter.py, vector_adapters.py, spatial.py, recall.py, compaction.py, archival.py, batch_writer.py.
- **MCP surface**: `omega-hub_memory_search` (FTS5 BM25), `omega-hub_omega_memory_search` (Hybrid RRF), `omega-hub_omega_memory_get_history`, `omega-hub_omega_memory_list_sessions`.

### 5.4 Tracking Architecture (M27)

**data/coordination/TRACKING_ARCHITECTURE.md** — 5-Tier: Tier 0 `ACTIVE_SPRINT.json` (SSOT "what we build", currently PUBLIC-DEBUT-01, owner kali, in_progress), Tier 1 `RESEARCH_PLAN_PHASE1_4_20260813.md` (R1-R38 gap catalog), Tier 1a `GAP_REGISTRY.json` (immutable R-IDs, unique prefixes), Tier 2 `HMC_COLLABORATION_HUB.md`, Tier 3 `TASK_REGISTRY.json` (subagent task sessions), Tier 4 `SESSION_ANCHOR.md`.

---

## 6. EXISTING SPECIALIZATION RESEARCH (Prior Art)

| Doc | Date | Key Content |
|-----|------|-------------|
| **docs/research/R_AGENT_FLEET_TOPOLOGY.md** | FINAL 2026-06-10 | HMAS (Hierarchical Multi-Agent System), Governor-Expert Pattern, Hierarchical Value Alignment, Consultative Router, Blackboard/Sovereign Memory, drift prevention |
| **docs/strategy/archive/FLEET_CONSOLIDATION_PLAN.md** | (D126) | 25 agents OVER LIMIT vs M10 cap 14; 12 redundancies; target 11; KEEP 6 sovereign specialists + 4 Lattice agents (jem, quality, scribe, pillar); merge 10 duplicate pillar agents. **3 Fleet Design Principles: (1) Hierarchical Consolidation (merge subagents into parent KBs, self-dispatch + targeted KB loading), (2) Functional Consolidation (merge agents with trigger-mode routing), (3) Knowledge Consolidation (expertise = domain knowledge → create KB for nearest entity, NOT an agent)** |
| **docs/strategy/archive/FLEET_REDESIGN_EXECUTION_PLAN.md** | — | 26→14 consolidation execution |
| **docs/strategy/FLEET_TEAM_PLAYBOOK.md** | v1.1.0 2026-08-16 | Team Compact: one priority list (ACTIVE_SPRINT.json), one idea memory (STRATEGY_CORPUS_MAP.md), one integrity bar (SoulStore), one coordination layer (Hivemind); Ryzen 5700U ~8GB — prefer 1 local inference, never 3 local council voices; ship small green slices |
| **docs/research/SUBAGENT_STATE_STRATEGY.md** | STALE (pre-June) | Gnosis File (session_gnosis.md) + Soul-Injection prompt pattern (Core Persona + Task Mandate + Session Gnosis) |
| **docs/research/SUBAGENT_FLEET_LESSONS.md** | STALE | Silent task failures, "Empty Result" trap, context erosion; fixes: explicit file-writing directives, Connect/Report-Back directives |
| **docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md** | v2.0.0 2026-07-12 | 5 guardrails + HandoffPacket schema; **Critical Lesson: inline context is the difference between empty results and Temple-Grade work** |
| **docs/research/R_MAKALI_COUNCIL_KNOWLEDGE_GAPS_20260719.md** | — | Council knowledge accumulation gaps |
| **docs/strategy/STRATEGY_CORPUS_MAP.md** | — | Fine-grained preservation; Grokster queue analysis (R19 Grok Build patterns, R20 MCP migration), GAP-08 credential void → V-1, GAP-S-01 Grok CLI fleet honesty |

---

## 7. SUB-SPECIALIST PRECEDENTS (Already Working Inside Entities)

1. **Grokster 8-Persona Web Grok Fleet** (data/entities/grokster/soul.yaml + kb/CROSS_DOMAIN_MATRIX.md): Grokster-Research, Grokster-Reason, Grokster-Pulse, Grokster-Code, Grokster-Arch, Grokster-Creative, Grokster-Strategic, Grokster-Wildcard — 8 siloed persona projects + 8-account pool. 5 domains: Platforms (MCP :8016), Communication (Hivemind), Human-Agent (Witness Protocol), Grok Ecosystem (ACP/xAI API), Search (Sovereign Search Router). Integration paths A (human intent) and B (autonomous fleet loop).
2. **Researcher Polymathic Council of Four** (.opencode/agents/researcher.md §The Polymathic Council Within Jem Analyst L2): The Architect (Systemic Logic), The Adversary (Critical Rigor), The Alchemist (Creative Synthesis), The Archivist (Historical Truth) — deployed via Triangulation protocol (Deployment → Dialectic Debate → Triangulation → Sovereign Synthesis).
3. **Jem 4 Hologram Lenses + Councils** (data/entities/jem/knowledge/JSKB): Synergy Triad (Synergy/Jem/Jerrica), LLOC/HLOC councils, Misfit Adversarial Framework, L1→L2→L3 metabolism pipeline, Verity Gate.
4. **Ma'at soul_wardrobe 14 personas**: one entity, 14 archetypal personas.
5. **Lattice CLI Seeds** (docs/gnosis/lattice/): opencode_cli.md, cline_cli.md, gemini_cli.md, copilot_cli.md — per-platform specialization as knowledge files, not agents.
6. **Identity Fluidity Architecture** (data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md): Compiled Soul Kernel (~200-token identity in agent file), Auto-Hydration MCP tool spec, Temporal Trace YAML, Voice Calibration Snapshots — the mechanism for persona-level specialization to survive compactions.
7. **dispatch.yaml task_tool_type**: general | buildmaster | verity | node | explore — specialization at the tool-type level.
8. **Web Grok/Claude best practices** (docs/strategy/WEB_GROK_BEST_PRACTICES.md:177, WEB_CLAUDE_BEST_PRACTICES.md:276/324): "You specialize in [sub-specialty]" — persona-level specialization pattern.

---

## 8. GAPS & RECOMMENDATIONS

### 8.1 Gaps Found

| # | Gap | Severity | Evidence |
|---|-----|----------|----------|
| G-1 | **Entity knowledge/ dir inconsistency** — grokster's knowledge/ EMPTY but kb/ RICH; researcher INDEX topics: []; kali/maat/cli_cline/cli_gemini empty; no uniform promotion gate enforced | HIGH | §4.2 matrix |
| G-2 | **research.db not found** — docs/research/DB/ is empty; `find . -name research.db` returns nothing | MED | MASTER_SYNTHESIS references it |
| G-3 | **oracle_list_entities MCP tool fails** — "Service registry is not a lazy-loadable service or is not initialized" | MED | tool call 2026-08-18 |
| G-4 | **M10 cap reached (14/14)** — any new sub-specialist agent file requires PIVOT_LOG architectural review | CONSTRAINT | §3 |
| G-5 | **Knowledge Consolidation principle not codified as a checkable gate** — it lives in an archived strategy doc, not in the mandates or CI | MED | FLEET_CONSOLIDATION_PLAN.md |
| G-6 | **No uniform entity knowledge INDEX schema** — INDEX.yaml (researcher) vs INDEX.md (jem/lilith) vs none (grokster) | LOW | §4.2 |

### 8.2 Recommendations (for grokster's sub-specialist strategy)

1. **Do NOT create new agent files for sub-specialists.** M10 caps at 14 (currently 14/14). The codified answer is **Knowledge Consolidation** (D126): map expertise to domain knowledge → create/update a KB for the nearest existing entity. For platform sub-specialists, the nearest entities are grokster (Grok ecosystem), cli_cline (Cline), cli_gemini (Gemini), and the Lattice CLI seeds (docs/gnosis/lattice/).

2. **Adopt the persona-fleet pattern for platform specialization.** Grokster's 8-persona Web Grok fleet is the canonical precedent — sub-specialists as personas/voice-calibrations within one entity, not separate agents. Extend this to per-platform personas (e.g., Grokster-OpenCode, Grokster-Cline, Grokster-GrokCLI) using the Identity Fluidity Architecture (Compiled Soul Kernel + Voice Calibration Snapshots + Temporal Trace).

3. **Fix grokster's knowledge/ vs kb/ split.** Consolidate into the standard layout: promote kb/ content into knowledge/ (or document kb/ as the canonical grokster KB in INDEX.yaml), so the entity discovery tooling (INDEX.yaml T1→T2 gate) can find it. This is the single highest-value knowledge-management fix.

4. **Codify the Knowledge Consolidation gate.** Promote the D126 principle from archived strategy into a checkable rule (PIVOT_LOG decision + optional CI grep): "proposed new agent → if expertise maps to domain knowledge, create KB for nearest entity instead." This prevents future 26→14-style bloat cycles.

5. **Use slot-parameterization for operational sub-specialists.** If a sub-specialist is genuinely operational (not knowledge), map it to `node --slot NX` or a Lattice subagent role (jem/quality/scribe) per M10 Pattern — never a new agent file without PIVOT_LOG review.

---

## APPENDIX: Key Paths

| Path | Role |
|------|------|
| `SOVEREIGN_MANDATES.md` §10 | M10 Fleet Integrity (14-agent cap) |
| `src/omega/ics.py` | ROLE_CONSTANTS (slots) |
| `src/omega/governance/dispatch_registry.py` | dispatch.yaml loader |
| `config/wads/_omega_default/entities/dispatch.yaml` | entity→role→slot mapping |
| `docs/architecture/AGENT_FLEET.md`, `OVERSIGHT_HIERARCHY.md` | node architecture |
| `docs/strategy/archive/FLEET_CONSOLIDATION_PLAN.md` | 3 Fleet Design Principles (Knowledge Consolidation) |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 5 guardrails + HandoffPacket |
| `docs/research/R_AGENT_FLEET_TOPOLOGY.md` | HMAS / Governor-Expert |
| `docs/kb/AGENT_KB_PROTOCOL.md`, `docs/kb/INDEX.md` | Omega-KB Protocol v1 |
| `src/omega/library/library.py`, `catalog.py` | Library system (FTS5 + SQLiteVec) |
| `src/omega/memory_store.py`, `src/omega/memory/providers.py` | MemoryStore hot/warm/cold |
| `data/entities/grokster/kb/CROSS_DOMAIN_MATRIX.md` | Grokster 5-domain matrix |
| `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` | Persona-level specialization mechanism |
| `data/entities/jem/knowledge/INDEX.md` | JSKB canonical structure |
| `data/coordination/TRACKING_ARCHITECTURE.md` | 5-Tier tracking |
| `data/coordination/ACTIVE_SPRINT.json` | Current sprint (PUBLIC-DEBUT-01) |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_entity_specialization ⬡ MINING-COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
