<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NotebookLM Context Pack Inventory — Omega Engine
**AP Token**: `AP-NOTEBOOKLM-INVENTORY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_notebooklm_inventory ⬡ ACTIVE

**Date**: 2026-08-19
**Purpose**: Structured inventory of all strategic, architectural, and code assets for NotebookLM ingestion. Focus on files that give strategic insight into Omega Engine architecture, decisions, and roadmap.

---

## 📊 Inventory Summary

| Category | Files | Total Size | Priority |
|----------|-------|------------|----------|
| Strategy Docs (SSOTs) | 5 | 110 KB | 🔴 Critical |
| Architecture Docs | 2 | 28 KB | 🔴 Critical |
| Research Docs (YouTube Sessions) | 1 | 22 KB | 🔴 Critical |
| Coordination Artifacts | 7 | 165 KB | 🔴 Critical |
| Core Engine Code | 11 | 416 KB | 🟡 High |
| CLI Code | 1 | 44 KB | 🟡 High |
| Config Files | 7 | 62 KB | 🟡 High |
| Mandates & Governance | 2 | 41 KB | 🔴 Critical |
| **TOTAL** | **36** | **~888 KB** | |

---

## 1️⃣ Strategy Docs — Single Sources of Truth (SSOTs)

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 1 | **SOVEREIGN_ARK_BLUEPRINT.md** | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | 17.7 KB | **10/10** | Master strategy SSOT (v5.2). Priority stack, mandates hotspots, provider fabric, decision log (D-354′–D-386), structural debt gates. Current execution authority. |
| 2 | **DEBUT_REMEDIATION_MANUAL_20260817.md** | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | 25.4 KB | **10/10** | Sprint authority for PUBLIC-DEBUT-01. Supersedes Ark §4. Contains ACTIVE_SPRINT.json integration, remediation tasks, gate criteria. |
| 3 | **POST_DEBUT_ROADMAP.md** | `docs/strategy/POST_DEBUT_ROADMAP.md` | 15.4 KB | **9/10** | Post-debut strategic roadmap. Horizons 1-4, community tool vision, 3-horizon timeline. |
| 4 | **STRATEGY_CORPUS_MAP.md** | `docs/strategy/STRATEGY_CORPUS_MAP.md` | 33.4 KB | **10/10** | Mandatory Layer 2 preservation map. Fine-grained agent source tracking, decision cross-references, supersession banners. |
| 5 | **FLEET_TEAM_PLAYBOOK.md** | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | 18.3 KB | **9/10** | Multi-agent coordination playbook. Hivemind protocols, handoff patterns, workspace locks, awareness. |

---

## 2️⃣ Architecture Docs — Canonical Technical Specifications

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 6 | **ORACLE_STACK_CANONICAL.md** | `ORACLE_STACK_CANONICAL.md` | 17.0 KB | **10/10** | Canonical architecture reference. 10 Nodes, Provider Fabric, Observability, Infrastructure. Single source of truth for engine topology. |
| 7 | **EVOLVER_SDP_SUCCESSOR.md** | `docs/architecture/EVOLVER_SDP_SUCCESSOR.md` | 11.0 KB | **8/10** | SDP (Sovereign Distillation Pipeline) successor architecture. Evolution from manual to automated distillation. |

---

## 3️⃣ Research Docs — Deep Technical Evidence

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 8 | **CARMACK_DEFINITIVE_STRATEGY_20260730.md** | `docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md` | 21.9 KB | **10/10** | Carmack YouTube Research Session — 24 proposals → top 5 force multipliers (Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus). 5,000+ lines evidence base across 6 deep-dive docs. Phase 0 strategy complete. |

> **Note**: The YouTube session directory contains 5 additional deep-dive evidence files (HARDENING_DEEP_DIVE.md 48.7 KB, INSTRUCTION_ROUTER_DEEP_DIVE.md 52.9 KB, LLAMA_OPTIMUS_DEEP_DIVE.md 37.8 KB, ORNITH_9B_TECHNICAL_DEEP_DIVE.md 22.1 KB, VULKAN_BACKEND_DEEP_DIVE.md 33.0 KB) — recommended for full ingestion if token budget allows.

---

## 4️⃣ Coordination Artifacts — Live Execution State

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 9 | **ACTIVE_SPRINT.json** | `data/coordination/ACTIVE_SPRINT.json` | 40.9 KB | **10/10** | Current sprint execution state (PUBLIC-DEBUT-01). Tier-0 tracking: backlog/ready/in_progress/blocked/completed/superseded. LLM-native format. |
| 10 | **GAP_REGISTRY.json** | `data/coordination/GAP_REGISTRY.json` | 14.4 KB | **10/10** | Immutable gap registry (R1-R99). Ultimate authority on gap assignment. Referenced by ACTIVE_SPRINT.json. |
| 11 | **UNIFIED_STRATEGIC_PLAN_20260819.md** | `data/coordination/UNIFIED_STRATEGIC_PLAN_20260819.md` | 15.9 KB | **9/10** | Consolidated strategic plan from MaKaLi Council. Execution priorities, resource allocation, risk mitigation. |
| 12 | **MAKALI_COUNCIL_VERDICT_20260817.md** | `data/coordination/MAKALI_COUNCIL_VERDICT_20260817.md` | 9.0 KB | **9/10** | Council verdict on strategy unification. Ratification of SOVEREIGN_ARK_BLUEPRINT as SSOT. |
| 13 | **MAKALI_COUNCIL_AUDIT_20260818.md** | `data/coordination/MAKALI_COUNCIL_AUDIT_20260818.md` | 7.4 KB | **8/10** | Council audit findings. Compliance gaps, mandate adherence, structural debt assessment. |
| 14 | **HMC_COLLABORATION_HUB.md** | `data/coordination/HMC_COLLABORATION_HUB.md` | 21.5 KB | **8/10** | HMC (Human-Machine Collaboration) hub. Cross-agent coordination patterns, session anchors, knowledge transfer protocols. |
| 15 | **PIVOT_LOG.md** | `docs/decisions/PIVOT_LOG.md` | 69.0 KB | **10/10** | Immutable decision history. All architectural pivots (D-series), mandate enforcement records, strategic reversals. Canonical: PIVOT_LOG_CANONICAL.md (187 KB). |

---

## 5️⃣ Core Engine Code — Critical Path Implementation

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 16 | **oracle.py** | `src/omega/oracle/oracle.py` | 62.1 KB | **10/10** | Central Oracle orchestration. `talk()`, `summon()`, intent assessment, entity discovery, provider routing, memory integration, soul evolution. |
| 17 | **model_gateway.py** | `src/omega/oracle/model_gateway.py` | 70.2 KB | **10/10** | Provider fabric gateway. Local-first routing (native-gguf → lmster → Ollama → cloud), streaming resilience (M25), breaker integration, admission control. |
| 18 | **entity_registry.py** | `src/omega/oracle/entity_registry.py` | 43.2 KB | **10/10** | Entity lifecycle, slot assignment (N1-N10), capability registry, WAD loading, soul.yaml binding, agent dispatch. |
| 19 | **memory_store.py** | `src/omega/memory_store.py` | 46.5 KB | **9/10** | Sovereign memory persistence. FTS5 + Vector hybrid search, conversation history, entity-scoped isolation, archival. |
| 20 | **sqlite_vec_adapter.py** | `src/omega/memory/sqlite_vec_adapter.py` | 41.2 KB | **9/10** | SQLite-vec integration. Vector similarity search, scalar quantization, payload indexes, IVectorStoreAdapter implementation. |
| 21 | **hybrid_search.py** | `src/omega/memory/hybrid_search.py` | 9.7 KB | **8/10** | RRF (Reciprocal Rank Fusion) combining BM25 + Vector. Sovereign memory retrieval. |
| 22 | **context_builder.py** | `src/omega/oracle/context_builder.py` | 24.0 KB | **9/10** | Context assembly for inference. Entity affinity, token budgeting, selective hydration, sovereign search integration. |
| 23 | **soul_store.py** | `src/omega/soul_store.py` | 7.9 KB | **9/10** | Atomic soul.yaml writes. 4-layer guarantee (tmp→atomic rename→verify→checkpoint). L1→L2→L3 distillation persistence. |
| 24 | **health_monitor.py** | `src/omega/oracle/health_monitor.py` | 40.8 KB | **9/10** | Canonical HealthMonitor factory. Circuit breaker unification (C-6′), 5/7 clones deprecated. OOMProtector 3-signal fusion. |
| 25 | **resource_guard.py** | `src/omega/oracle/resource_guard.py` | 15.8 KB | **8/10** | Resource admission control. CCX-aware semaphore, RAM pressure monitoring, local-first enforcement. |
| 26 | **skeptical_verifier.py** | `src/omega/oracle/skeptical_verifier.py` | ~25 KB | **9/10** | NLI-based Two-Source Rule. Tainted Data Protocol (TDP) integration. Cognitive sovereignty verification. |

---

## 6️⃣ CLI Code — User-Facing Interface

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 27 | **oracle_cli.py** | `src/omega/cli/oracle_cli.py` | 44.3 KB | **9/10** | Main CLI entry. `omega talk`, `omega summon`, `omega project`, `omega work`, `omega decision`, `omega queue`, `omega soul`, `omega vault`. Workbench integration. |

---

## 7️⃣ Config Files — Runtime Configuration

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 28 | **providers.yaml** | `config/providers.yaml` | 10.3 KB | **10/10** | Provider fabric definition. Priority order, streaming timeouts (M25), model mappings, local-first strategy enforcement. |
| 29 | **models.yaml** | `config/models.yaml` | 3.5 KB | **8/10** | Model registry aliases. Local/cloud model mappings, context windows, capability tags. |
| 30 | **omega.yaml** | `config/omega.yaml` | 2.1 KB | **8/10** | Core engine config. Data directories, logging, observability, hardware profile reference. |
| 31 | **manifest.yaml** | `config/wads/_omega_default/manifest.yaml` | 1.6 KB | **7/10** | Default WAD manifest. Engine identity, version, entity registry bootstrap. |
| 32 | **entities.yaml** | `config/wads/_omega_default/entities.yaml` | 38.7 KB | **9/10** | Default entity definitions (14 agents). Slot assignments, capabilities, model affinities, voice configs. |
| 33 | **hierarchy.yaml** | `config/wads/_omega_default/hierarchy.yaml` | 4.1 KB | **7/10** | Entity hierarchy. Pillar Keepers (N1-N10), Lattice subagents, delegation chains. |
| 34 | **soul.template.yaml** | `config/wads/_omega_default/soul.template.yaml` | 1.9 KB | **8/10** | Soul.yaml template. Lessons structure, L1→L2→L3 fields, proposed_lessons staging. |

---

## 8️⃣ Mandates & Governance — Constitutional Law

| # | File | Path | Size | Relevance (1-10) | Description |
|---|------|------|------|------------------|-------------|
| 35 | **SOVEREIGN_MANDATES.md** | `SOVEREIGN_MANDATES.md` | 23.9 KB | **10/10** | 27 Non-negotiable laws. M1 AnyIO, M2 Engine-Stack Firewall, M7 Local-First, M11 Soul Integrity, M14 Heritage Vetting, M18 Token Efficiency, M19 Adversarial Alchemy, M23 Failure Integrity, M24 Venv Sovereignty, M25 Streaming Resilience, M26 Doc Standards, M27 Tracking Integrity. |
| 36 | **AGENTS.md** | `AGENTS.md` | ~15 KB | **9/10** | OpenCode agent workflow. Delegation protocol, Hivemind-first communication, session hydration, sovereign continuity, tool protocols. |

---

## 🎯 NotebookLM Ingestion Priority Order

### Tier 1: Strategic Context (Must Ingest First)
1. `SOVEREIGN_ARK_BLUEPRINT.md` — Master strategy
2. `DEBUT_REMEDIATION_MANUAL_20260817.md` — Current sprint authority
3. `STRATEGY_CORPUS_MAP.md` — Preservation map & agent sources
4. `ORACLE_STACK_CANONICAL.md` — Architecture reference
5. `SOVEREIGN_MANDATES.md` — Constitutional law
6. `ACTIVE_SPRINT.json` — Live execution state
7. `GAP_REGISTRY.json` — Gap authority
8. `PIVOT_LOG.md` — Decision history

### Tier 2: Technical Deep-Dive (High Value)
9. `oracle.py` — Core orchestration
10. `model_gateway.py` — Provider fabric
11. `entity_registry.py` — Entity system
12. `CARMACK_DEFINITIVE_STRATEGY_20260730.md` — Force multiplier research
13. `memory_store.py` + `sqlite_vec_adapter.py` + `hybrid_search.py` — Memory subsystem
14. `health_monitor.py` + `resource_guard.py` — Resilience patterns
15. `providers.yaml` — Runtime provider config
16. `entities.yaml` — Fleet composition

### Tier 3: Coordination & Operations (Contextual)
17. `UNIFIED_STRATEGIC_PLAN_20260819.md`
18. `MAKALI_COUNCIL_VERDICT_20260817.md`
19. `MAKALI_COUNCIL_AUDIT_20260818.md`
20. `HMC_COLLABORATION_HUB.md`
21. `FLEET_TEAM_PLAYBOOK.md`
22. `POST_DEBUT_ROADMAP.md`
23. `EVOLVER_SDP_SUCCESSOR.md`
24. `oracle_cli.py`
25. `context_builder.py` + `soul_store.py` + `skeptical_verifier.py`
26. Remaining config files

---

## 📝 Ingestion Notes for NotebookLM

### Recommended Notebook Structure
```
Notebook: "Omega Engine — Sovereign AI Runtime"
├── Section: Strategy & Governance
│   ├── SOVEREIGN_ARK_BLUEPRINT.md
│   ├── DEBUT_REMEDIATION_MANUAL_20260817.md
│   ├── STRATEGY_CORPUS_MAP.md
│   ├── SOVEREIGN_MANDATES.md
│   └── PIVOT_LOG.md
├── Section: Architecture
│   ├── ORACLE_STACK_CANONICAL.md
│   ├── EVOLVER_SDP_SUCCESSOR.md
│   └── CARMACK_DEFINITIVE_STRATEGY_20260730.md
├── Section: Live Execution State
│   ├── ACTIVE_SPRINT.json
│   ├── GAP_REGISTRY.json
│   ├── UNIFIED_STRATEGIC_PLAN_20260819.md
│   ├── MAKALI_COUNCIL_VERDICT_20260817.md
│   ├── MAKALI_COUNCIL_AUDIT_20260818.md
│   └── HMC_COLLABORATION_HUB.md
├── Section: Core Implementation
│   ├── oracle.py
│   ├── model_gateway.py
│   ├── entity_registry.py
│   ├── memory_store.py
│   ├── sqlite_vec_adapter.py
│   ├── hybrid_search.py
│   ├── context_builder.py
│   ├── soul_store.py
│   ├── health_monitor.py
│   ├── resource_guard.py
│   └── skeptical_verifier.py
├── Section: CLI & Config
│   ├── oracle_cli.py
│   ├── providers.yaml
│   ├── models.yaml
│   ├── omega.yaml
│   ├── manifest.yaml
│   ├── entities.yaml
│   ├── hierarchy.yaml
│   └── soul.template.yaml
└── Section: Team Playbook
    ├── FLEET_TEAM_PLAYBOOK.md
    ├── POST_DEBUT_ROADMAP.md
    └── AGENTS.md
```

### Query Patterns for NotebookLM
- **"What is the current sprint priority?"** → ACTIVE_SPRINT.json + DEBUT_REMEDIATION_MANUAL
- **"How does the provider fabric route requests?"** → model_gateway.py + providers.yaml + SOVEREIGN_MANDATES.md (M7)
- **"What are the 27 Sovereign Mandates?"** → SOVEREIGN_MANDATES.md
- **"How does entity dispatch work?"** → entity_registry.py + hierarchy.yaml + FLEET_TEAM_PLAYBOOK.md
- **"What is the memory architecture?"** → memory_store.py + sqlite_vec_adapter.py + hybrid_search.py + CARMACK_DEFINITIVE_STRATEGY
- **"What decisions led to current architecture?"** → PIVOT_LOG.md + STRATEGY_CORPUS_MAP.md
- **"How does soul distillation work?"** → soul_store.py + SOVEREIGN_MANDATES.md (M11) + EVOLVER_SDP_SUCCESSOR.md

---

## 🔗 Cross-Reference Index

| Concept | Primary Doc | Implementation | Config |
|---------|-------------|----------------|--------|
| **Local-First Inference** | SOVEREIGN_MANDATES.md (M7) | model_gateway.py | providers.yaml |
| **Entity Slot System (N1-N10)** | ORACLE_STACK_CANONICAL.md | entity_registry.py | hierarchy.yaml |
| **Soul Distillation L1→L2→L3** | SOVEREIGN_MANDATES.md (M11) | soul_store.py | soul.template.yaml |
| **Heritage Vetting [id-soft:]** | SOVEREIGN_MANDATES.md (M14) | audit/firewall_checker.py | — |
| **Streaming Resilience** | SOVEREIGN_MANDATES.md (M25) | model_gateway.py:_stream_completion() | providers.yaml:streaming |
| **Hivemind Coordination** | FLEET_TEAM_PLAYBOOK.md | hub.py + coordination/ | — |
| **Skeptical Verification** | CARMACK_DEFINITIVE_STRATEGY | skeptical_verifier.py | — |
| **Tracking Architecture (5-Tier)** | SOVEREIGN_MANDATES.md (M27) | ACTIVE_SPRINT.json + GAP_REGISTRY.json + TASK_REGISTRY.json | TRACKING_ARCHITECTURE.md |

---

## 📦 Total Token Estimate

| Tier | Files | Est. Tokens |
|------|-------|-------------|
| Tier 1 (Strategic) | 8 | ~45,000 |
| Tier 2 (Technical) | 10 | ~65,000 |
| Tier 3 (Coordination) | 9 | ~35,000 |
| **Total** | **27** | **~145,000** |

*Well within NotebookLM's 500K token limit. Full ingestion recommended.*

---

## 🏷️ Tags for NotebookLM Organization

```
#omega-engine #sovereign-ai #local-first #agent-fleet #mcp #rag #sqlite-vec
#anyio #podman #soul-distillation #heritage-vetting #cognitive-sovereignty
#notebooklm-context-pack #strategic-planning #architecture-docs
```

---

*Generated by roc_racoon (Sovereign Miner) — 2026-08-19*
*Inventory saved to: `data/coordination/NOTEBOOKLM_INVENTORY_20260819.md`*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
