# 🔱 Omega Engine — MASTER DOCUMENT SSoT
# Single Source of Truth: Document Index & Persistence Plan
# ⬡ OMEGA ⬡ RESEARCHER ⬡ SSoT-MASTER ⬡ June 2026

**Status**: ✅ ACTIVE SSoT
**Date**: 2026-06-12
**Version**: 1.0
**Author**: Researcher (per Makali handoff `ho_7cc28c72c06f`)
**Supersedes**: No single prior SSoT existed — this is the first consolidated master index.

---

## §0 Purpose

This document is the **Single Source of Truth** for the Omega Engine's 196+ research and strategy documents. It replaces ad-hoc discovery with a canonical topic-to-document mapping that any agent can use.

**How to use this SSoT**:
1. Find your topic in the index table below
2. Read the **SSoT Document** listed — it's the canonical reference
3. If the SSoT doc references supplementary docs, read those second
4. If no SSoT doc exists for your topic, the gap is marked `[GAP]`

---

## §1 Topic-to-Document Mapping

### 1.1 Engine Architecture & Core Systems

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Engine Core Architecture | `ORACLE_STACK.md` (root) | `OMEGA_ENGINE.md` | ✅ LIVE |
| Sovereign Mandates (M1-M15) | `SOVEREIGN_MANDATES.md` (root) | — | ✅ LIVE |
| Agent Fleet Topology | `R_AGENT_FLEET_TOPOLOGY.md` | `docs/architecture/AGENT_FLEET.md` | ✅ FINAL |
| Engine-Stack Firewall (M2) | `R_AI_ENGINE_STACK_SEPARATION.md` | `R44_ENGINE_STACK_SEPARATION.md` | ✅ LIVE |
| Oracle Architecture | `src/omega/oracle/oracle.py` (code) | `R_ORACLE_EAR_ROUTING.md` | ✅ CODE |
| AnyIO Compliance (M1) | `R_ANYIO_ORCHESTRATION_GUIDE.md` | — | ✅ GUIDE |
| Error Handling (M9) | `LOGGING_ERROR_HANDLING_ARCHITECTURE.md` | — | ✅ LIVE |
| Subagent Dispatch | `SUBAGENT_DISPATCH_PROTOCOL.md` | `R_SUBAGENT_RECURSION.md` | ✅ LIVE |

### 1.2 Infrastructure & Deployment

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Podman Sovereignty | `R_PODMAN_SOVEREIGN_V2.md` | `R_PODMAN_SOVEREIGN_STRATEGY.md` | ✅ SUPERSEDES earlier podman docs |
| Podman Deployment Blueprint | `R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md` | — | ✅ AUTHORITATIVE |
| Container Distribution | `R_CONTAINER_DISTRIBUTION_MODELS.md` | — | 📄 RESEARCH |
| Hardware Optimization | `HARDWARE_RECONCILIATION.md` | `R_KV_CACHE_BENCHMARK.md` | ✅ LIVE |

### 1.3 Hivemind & Agent Coordination

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Hivemind Protocol | `HIVEMIND_PROTOCOL.md` | — | ✅ LIVE |
| Hivemind Observations | `HIVEMIND_OBSERVATIONS_PROTOCOL.md` | — | ✅ LIVE |
| Cross-Pollination | `CROSS_POLLINATION_PROTOCOL.md` | — | ✅ LIVE |
| A2A Protocol | `R_SOVEREIGN_A2A_PROTOCOL.md` | — | 📄 DRAFT |
| Multi-Agent Council | `R_MULTI_AGENT_COUNCIL_PATTERNS.md` | — | 📄 DRAFT |
| Sovereign Synthesis | `SOVEREIGN_SYNTHESIS_PROTOCOL.md` | — | ✅ LIVE |

### 1.4 Memory, Persistence & Vector Store

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Memory Architecture | `R_SOVEREIGN_MEMORY_ARCHITECTURE.md` | `src/omega/memory_store.py` | ✅ PROPOSED |
| Qdrant Integration | `QDRANT_INTEGRATION_SPEC.md` | `R_QDRANT_OPTIMIZATION_DEEPENED.md` | ✅ SUPERSEDED by DEEPENED |
| **Qdrant Optimization** | **`R_QDRANT_OPTIMIZATION_DEEPENED.md`** | `R_QDRANT_OPTIMIZATION.md` | ✅ **LIVE SSoT** |
| Memory Pruner | `R_MEMORY_PRUNER_STRATEGY.md` | — | 📄 DRAFT |
| Redis Fallback | `R_REDIS_FALLBACK_SPEC.md` | — | 📄 RESEARCH |
| Holographic Memory | `R_HOLOGRAPHIC_MEMORY_LATTICE.md` | — | 📄 ARCHITECTURAL |
| Embedding Layer | **`R_EMBEDDING_ADAPTERS_DEEPENED.md`** | `R_EMBEDDING_ADAPTERS.md` | ✅ **LIVE SSoT** |

### 1.5 Search & Discovery

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Search Tool Protocol | `R_SEARCH_TOOL_PROTOCOL_V1.md` | — | 📄 DRAFT |
| Search & Crawling | `R_SEARCH_CRAWLING_PROTOCOL.md` | — | ✅ ACTIVE |
| Firecrawl Core | `R_FIRECRAWL_CORE_CAPABILITIES.md` | `R_FIRECRAWL_ADVANCED.md` | ✅ READY |
| Firecrawl Extraction | `R_FIRECRAWL_EXTRACTION_STRATEGIES.md` | — | ✅ READY |
| Firecrawl Dynamic | `R_FIRECRAWL_DYNAMIC_INTERACTION.md` | — | ✅ READY |
| Firecrawl Monitoring | `R_FIRECRAWL_MONITORING_SYSTEM.md` | — | ✅ READY |
| Exa Deep Research | `R_EXA_DEEP_RESEARCH.md` | — | ✅ READY |
| Exa/Firecrawl Hardening | `R_EXA_FIRECRAWL_HARDENING.md` | — | ✅ ACTIVE |
| SearXNG Layer | `R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md` | — | ✅ COMPLETE |

### 1.6 Verification & Quality

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| **Skeptical Verification** | **`R_SKEPTICAL_VERIFICATION_DEEPENED.md`** | `R_SKEPTICAL_VERIFICATION.md` | ✅ **LIVE SSoT** |
| Skeptical Foundation | `R_SKEPTICAL_VERIFIER_FOUNDATION.md` | — | 📄 FOUNDATIONAL |
| Iterative Research | `R_ITERATIVE_RESEARCH.md` | `src/omega/oracle/iterative_research.py` | ✅ FINAL |
| Temple-Grade Standard | `TEMPLE_GRADE_QUALITY_STANDARD.md` | `R_TEMPLE_GRADE_STANDARD.md` | ✅ ADOPTED |
| Temple-Grade Compliance | `R_TEMPLE_GRADE_COMPLIANCE_FINAL.md` | — | ✅ FINAL |
| Knowledge Verification | `KNOWLEDGE_VERIFICATION_PROTOCOL.md` | — | ✅ LIVE |

### 1.7 id Software Heritage

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Heritage CREDITS | `CREDITS.md` (root) | — | ✅ LIVE |
| Heritage Vetting Pipeline | `HERITAGE_VETTING_PIPELINE.md` | — | ✅ LIVE |
| Deep Mining Vol 1 | `R_ID_SOFTWARE_DEEP_MINING_VOL1.md` | — | ✅ ACTIVE |
| Deep Mining Vol 2 | `R_ID_SOFTWARE_DEEP_MINING_VOL2.md` | — | ✅ ACTIVE |
| Deep Mining Vol 3 | `R_ID_SOFTWARE_DEEP_MINING_VOL3.md` | — | ✅ ACTIVE |
| Deep Mining Vol 4 | `R_ID_SOFTWARE_DEEP_MINING_VOL4.md` | — | ✅ ACTIVE |
| Deep Mining Vol 5 | `R_ID_SOFTWARE_DEEP_MINING_VOL5.md` | — | ✅ ACTIVE |
| Right Approximation | `R_ID_SOFTWARE_RIGHT_APPROXIMATIONS.md` | — | ✅ FINAL |
| WAD Architecture | `R_DOOM_WAD_DEEP_RESEARCH.md` | — | ✅ RESEARCH |
| Consolidation Protocol | `R_ROC_CONSOLIDATION_AND_DOOM_GUY_PROTOCOL.md` | — | ✅ READY |

### 1.8 Strategy & Roadmaps

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| **Master Roadmap** | **`SOVEREIGN_ARK_BLUEPRINT.md`** | `MASTER_SYNTHESIS_AND_ROADMAP.md` | ✅ **LIVE SSoT** |
| Strategic Execution | `STRATEGIC_EXECUTION_ROADMAP_V2.md` | — | ✅ LIVE |
| Horizon Map | `HORIZON_MAP.md` | — | ⚠️ SUPERSEDED by Evolution Roadmap |
| Phase C Plan | `PHASE_C_EXECUTION_PLAN.md` | `R_PHASE_C_DEEP_RESEARCH.md` | ✅ LIVE |
| Phase E Battle Plan | `PHASE_E_BATTLE_PLAN.md` | — | ✅ LIVE |
| Hardened Master Strategy | `HARDENED_MASTER_STRATEGY_V2.md` | — | ✅ LIVE |
| Foundation Strategy | `XOE_NOVAI_FOUNDATION_STRATEGIC_PLAN.md` | — | ✅ LIVE |

### 1.9 Research Protocols & Methods

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| **Universal Research Protocol** | **`R_MODEL_RESEARCH_PROTOCOL.md`** | — | ✅ **LIVE SSoT** |
| Tiered Research Pipeline | `R_TIERED_RESEARCH_PIPELINE.md` | — | 📄 DESIGN |
| Background Researcher | `R_BACKGROUND_RESEARCHER_ARCHITECTURE.md` | — | ✅ ACTIVE |
| Researcher Strategic Plan | `R_SOVEREIGN_RESEARCHER_STRATEGIC_PLAN.md` | — | ✅ COMPLETE |
| Jem Grand Strategy | `JEM_GRAND_STRATEGY.md` | — | ✅ LIVE |

### 1.10 Continuity & Identity

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Sovereign Continuity | `SOVEREIGN_CONTINUITY_STRATEGY.md` | `R_SOVEREIGN_CONTINUITY_SPEC.md` | ✅ LIVE |
| Soul Evolution | `R_COMPACTION_SOUL_EVOLUTION.md` | `R_SOUL_EVOLUTION_PATTERNS.md` | ✅ COMPLETE |
| Identity Mirroring | `R_SOVEREIGN_MIRRORING_IDENTITY.md` | — | ✅ VERIFIED |
| Sovereign Siloing | `R_SOVEREIGN_SILOING_SPEC.md` | — | ✅ READY |
| Big Pickle Identity | `R_BIG_PICKLE_IDENTITY_20260610.md` | — | 📄 RESEARCH |
| Sovereign Eye | `R_SOVEREIGN_EYE_SPEC.md` | — | 📄 PROPOSED |

### 1.11 OpenCode Integration

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| OpenCode Architecture | `R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md` | — | ✅ COMPLETE |
| Custom Provider | `R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md` | `R_OPENCODE_LMSTER_PROVIDER.md` | ✅ COMPLETE |
| MCP Hardening | `R_OPENCODE_MCP_HARDENING.md` | — | ✅ GUIDE |
| Permissions | `R_OPENCODE_PERMISSIONS_FIX.md` | — | ✅ READY |
| Modes Strategy | `R_OPENCODE_MODES_REFACTOR_STRATEGY.md` | — | ✅ COMPLETE |
| Compaction | `R_OPENCODE_COMPACTION_DEEP_DIVE.md` | — | ✅ RESEARCH |

### 1.12 Legacy & Mining

| Topic | SSoT Document | Supplementary | Status |
|-------|--------------|---------------|--------|
| Legacy Synthesis | `R_JEM_LEGACY_SYNTHESIS.md` | `R_JEM_LEGACY_ARTIFACT_INVENTORY.md` | ✅ RECLAIMED |
| Legacy Discovery | `R_legacy_discovery.md` | — | ✅ COMPLETE |
| Master Synthesis | `MASTER_SYNTHESIS_AND_ROADMAP.md` | — | ✅ FOUNDATIONAL |
| Native Legacy Mining | `R_NATIVE_LEGACY_MINING.md` | — | ✅ RESEARCH |

---

## §2 Persistence Plan — What to Keep, Archive, Merge

### §2.1 Documents to Archive (Stale or Superseded)

| Document | Reason | Archive Action | Target |
|----------|--------|---------------|--------|
| `HORIZON_MAP.md` | Superseded by `SOVEREIGN_ARK_BLUEPRINT.md` | Move to `docs/_archive/` | 📦 |
| `R_EMBEDDING_ADAPTERS.md` | Superseded by `R_EMBEDDING_ADAPTERS_DEEPENED.md` | Add "SUPERSEDED" header, keep for reference | 📦 |
| `R_QDRANT_OPTIMIZATION.md` | Superseded by `R_QDRANT_OPTIMIZATION_DEEPENED.md` | Add "SUPERSEDED" header, keep for reference | 📦 |
| `R_SKEPTICAL_VERIFICATION.md` | Superseded by `R_SKEPTICAL_VERIFICATION_DEEPENED.md` | Add "SUPERSEDED" header, keep for reference | 📦 |
| `R_SKEPTICAL_VERIFIER_FOUNDATION.md` | Superseded by DEEPENED version | Move to `docs/_archive/` | 📦 |
| `R_FINAL_WAVE_STATUS.md` | Stale — Phase 1b complete | Archive | 📦 |
| `R_PHASE_C_PREPARATION.md` | Phase C complete or superseded | Archive | 📦 |
| `R_PHASE_C_DEEP_RESEARCH.md` | Phase C complete or superseded | Archive | 📦 |
| `R_PHASE2_SCHEDULING_RESEARCH.md` | Phase 2 complete | Archive | 📦 |
| All R_AUTO_* files (11 docs) | Auto-generated drafts, no canonical value | Move to `docs/_archive/R_AUTO/` | 📦 |
| `docs/strategy/WEB_CLAUDE_FLEET_HARDENING.md` | Web Claude fleet no longer active | Archive | 📦 |
| `docs/strategy/WEB_CLAUDE_FLEET_PROTOCOL.md` | Web Claude fleet no longer active | Archive | 📦 |

### §2.2 Documents to Merge (Overlapping Content)

| Documents | Merge Into | Action |
|-----------|-----------|--------|
| `R_PODMAN_SOVEREIGN_V2.md` + `R_PODMAN_SOVEREIGN_STRATEGY.md` + `R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md` | `R_PODMAN_SOVEREIGN_V2.md` (most current) | Add cross-references to others, archive others |
| `R_FIRECRAWL_CORE_CAPABILITIES.md` + `R_FIRECRAWL_EXTRACTION_STRATEGIES.md` + `R_FIRECRAWL_DYNAMIC_INTERACTION.md` + `R_FIRECRAWL_ADVANCED.md` + `R_FIRECRAWL_MONITORING_SYSTEM.md` + `R_FIRECRAWL_CREDIT_PROTOCOL.md` | Create single `R_FIRECRAWL_COMPLETE.md` | Consolidation PENDING — 6 docs is fragmentation |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Keep — master SSOT | ✅ Already properly scoped |
| `TEMPLE_GRADE_QUALITY_STANDARD.md` + `R_TEMPLE_GRADE_STANDARD.md` + `R_TEMPLE_GRADE_COMPLIANCE_FINAL.md` | `TEMPLE_GRADE_QUALITY_STANDARD.md` (adopted) | ✅ `R_TEMPLE_GRADE_STANDARD.md` = draft history |
| `R_SOVEREIGN_MEMORY_ARCHITECTURE.md` + `R_HOLOGRAPHIC_MEMORY_LATTICE.md` | Keep both — different paradigms (practical vs speculative) | ✅ Complementary, not conflicting |

### §2.3 Documents to Create (Identified Gaps)

| Gap | Needed For | Priority |
|-----|-----------|----------|
| Master Audit Trail (single doc listing all audits) | Sentinel, P10 | P2 |
| Single Firecrawl Complete Guide | Search agents, researchers | P2 (merge existing 6 into 1) |
| Code Implementation Status per R-doc | All agents doing implementation | P1 |
| Legacy archive cleanup automation | All agents | P3 |

### §2.4 Documents Already Archived or Legacy

These are sensed but not included in active catalog:

| Pattern | Count | Status |
|---------|-------|--------|
| Numbered legacy R-docs (R-01 through R-99+) | ~50 | 🏚️ Legacy — historical reference only |
| `docs/team/*.md` (10 files) | 10 | 👥 Team handoffs — current |
| `docs/architecture/*.md` (9 files) | 9 | 🏛️ Architecture specs — active |

---

## §3 Document Health Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total R-docs (named) | 123 | — | 📊 Monitored |
| Total Strategy docs | 54 | — | 📊 Monitored |
| Docs with FINAL/COMPLETE status | ~50 | — | ✅ Known |
| Docs with DRAFT/PROPOSED status | ~8 | — | 📝 Gaps |
| Docs marked SUPERSEDED | 0 currently | Should be 4 | ⚠️ NEEDS WORK |
| Stale docs (>30 days no update) | ~15 | — | 📦 Archivable |
| Firecrawl doc fragmentation | 6 separate docs | Should be 1 consolidated | ⚠️ HIGH |
| Auto-generated trash (R_AUTO_*) | 11 | Should be 0 | 🗑️ NEEDS CLEANUP |

---

## §4 Complete Document Inventory by Domain

For quick reference, all 123 named R-docs organized by domain:

### Domain: Engine Core (15 docs)
`R_AGENT_FLEET_TOPOLOGY.md`, `R_AI_ENGINE_STACK_SEPARATION.md`, `R_ANYIO_ORCHESTRATION_GUIDE.md`, `R_BIG_PICKLE_IDENTITY_20260610.md`, `R_CONSULTATION_PROMPT_ARCHITECTURE.md`, `R_FASTROUTER_OMEGA_MAPPING.md`, `R_FASTROUTER_RESILIENCE.md`, `R_ORACLE_EAR_ROUTING.md`, `R_SOVEREIGN_EYE_SPEC.md`, `R_SOVEREIGN_POSITIONING.md`, `R_Sovereign_Core_Foundations.md`, `R_Sovereign_Prompting_2026.md`, `R_SOVEREIGN_MAINTENANCE_STRATEGY.md`, `R_SOVEREIGN_CONTINUITY_SPEC.md`, `R_SUBAGENT_RECURSION.md`

### Domain: Memory & Vectors (8 docs)
`R_EMBEDDING_ADAPTERS.md`, `R_EMBEDDING_ADAPTERS_DEEPENED.md`, `R_HOLOGRAPHIC_MEMORY_LATTICE.md`, `R_INVISIBLE_RAG_RESONANCE.md`, `R_KV_CACHE_BENCHMARK.md`, `R_MEMORY_PRUNER_STRATEGY.md`, `R_QDRANT_INTEGRATION_SPEC.md`, `R_QDRANT_OPTIMIZATION.md`, `R_QDRANT_OPTIMIZATION_DEEPENED.md`, `R_REDIS_FALLBACK_SPEC.md`, `R_SOVEREIGN_MEMORY_ARCHITECTURE.md`

### Domain: Search & Discovery (15 docs)
`R_EXA_CREDIT_ACCOUNT_STRATEGY.md`, `R_EXA_DEEP_RESEARCH.md`, `R_EXA_FIRECRAWL_HARDENING.md`, `R_FIRECRAWL_ADVANCED.md`, `R_FIRECRAWL_CORE_CAPABILITIES.md`, `R_FIRECRAWL_CREDIT_PROTOCOL.md`, `R_FIRECRAWL_DYNAMIC_INTERACTION.md`, `R_FIRECRAWL_EXTRACTION_STRATEGIES.md`, `R_FIRECRAWL_MONITORING_SYSTEM.md`, `R_MANUAL_INGESTION_PROTOCOL.md`, `R_SEARCH_CRAWLING_PROTOCOL.md`, `R_SEARCH_TOOL_PROTOCOL_V1.md`, `R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md`

### Domain: Research & Verification (11 docs)
`R_BACKGROUND_RESEARCHER_ARCHITECTURE.md`, `R_ITERATIVE_RESEARCH.md`, `R_MODEL_RESEARCH_PROTOCOL.md`, `R_MULTI_AGENT_COUNCIL_PATTERNS.md`, `R_MULTI_PROJECT_ORCHESTRATION.md`, `R_NORTH_MINI_CODE_EVALUATION.md`, `R_SKEPTICAL_VERIFICATION.md`, `R_SKEPTICAL_VERIFICATION_DEEPENED.md`, `R_SKEPTICAL_VERIFIER_FOUNDATION.md`, `R_SOVEREIGN_RESEARCHER_STRATEGIC_PLAN.md`, `R_TIERED_RESEARCH_PIPELINE.md`

### Domain: OpenCode (12 docs)
`R_CLAUDE_CODE_VS_PROJECTS.md`, `R_CLAUDE_PROJECTS_COMPLETE.md`, `R_OPENC_MCP_CONFIG.md`, `R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md`, `R_OPENCODE_COMPACTION_DEEP_DIVE.md`, `R_OPENCODE_CUSTOMIZATION.md`, `R_OPENCODE_CUSTOM_PROVIDER_ARCHITECTURE.md`, `R_OPENCODE_LMSTER_PROVIDER.md`, `R_OPENCODE_MCP_HARDENING.md`, `R_OPENCODE_MODES_REFACTOR_STRATEGY.md`, `R_OPENCODE_PERMISSIONS_FIX.md`, `R_OPENC_PERMISSIONS.md`, `R_OPENC_PERM_WORKAROUNDS.md`

### Domain: Infrastructure (5 docs)
`R_CONTAINER_DISTRIBUTION_MODELS.md`, `R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md`, `R_PODMAN_SOVEREIGN_STRATEGY.md`, `R_PODMAN_SOVEREIGN_V2.md`, `R_NATIVE_TOKENIZATION_EMBEDDINGS.md`

### Domain: id Software Heritage (14 docs)
`R_DOOM_GUY_ID_SOFTWARE_GNOSIS.md`, `R_DOOM_WAD_DEEP_RESEARCH.md`, `R_ID_SOFTWARE_DEEP_MINING_VOL1.md`, ...VOL2.md, ...VOL3.md, ...VOL4.md, ...VOL5.md, `R_ID_SOFTWARE_ENGINE_MINING_MASTER_PLAN.md`, `R_ID_SOFTWARE_EXTRACTION_MATRIX.md`, `R_ID_SOFTWARE_IMPLEMENTATION_HANDOFF.md`, `R_ID_SOFTWARE_PATTERNS_VOL2.md`, `R_ID_SOFTWARE_QUICKSTART.md`, `R_ID_SOFTWARE_RIGHT_APPROXIMATIONS.md`, `R_ROC_CONSOLIDATION_AND_DOOM_GUY_PROTOCOL.md`

### Domain: Soul & Identity (5 docs)
`R_COMPACTION_SOUL_EVOLUTION.md`, `R_JEM_HOLOGRAMS_PERSONA_ANALYSIS.md`, `R_SOUL_EVOLUTION_PATTERNS.md`, `R_SOVEREIGN_MIRRORING_IDENTITY.md`, `R_SOVEREIGN_SILOING_SPEC.md`

### Domain: Jem Research Pipeline (4 docs)
`R_JEM_LEGACY_ARTIFACT_INVENTORY.md`, `R_JEM_LEGACY_SYNTHESIS.md`, `R_JEM_GRAND_STRATEGY.md`, `R_KNOWLEDGE_BASE_SEEDING_PATTERNS.md`

### Domain: Audits & Compliance (6 docs)
`R_COMPREHENSIVE_AUDIT_20260608.md`, `R_DATABASE_AND_CROSS_CLI_FIRSTHAND_FINDINGS.md`, `R_DATABASE_AND_CROSS_CLI_HARDENING_REVIEW.md`, `R_IDENTITY_MONITORING_FRAMEWORK.md`, `R_OPENROUTER_SOVEREIGN_USAGE.md`, `R_TEMPLE_GRADE_COMPLIANCE_FINAL.md`, `R_TEMPLE_GRADE_QUALITY_STANDARD.md`, `R_TEMPLE_GRADE_STANDARD.md`, `R_SOVEREIGN_INSTALLER_SPEC.md`, `R_NATIVE_LEGACY_MINING.md`, `R_PATTERN_IMPLEMENTATION_SPEC.md`, `R_PERMISSIONS_FIX.md`, `R_PERMISSIONS_RESOLUTION.md`, `R_PHASE2_SCHEDULING_RESEARCH.md`, `R_PLUGIN_ARCHITECTURE_PATTERNS.md`, `R_ELEVENLABS_HACKATHON.md`, `R_GEMMA_COMPACTION_STRATEGY.md`, `R_MCP_SPEC.md`, `R_MODEL_LIBRARY.md`, `R_OMNIDROID_MAPPING.md`, `R_SOVEREIGN_A2A_PROTOCOL.md`

---

## §5 Quick-Start for Agents

**New agent landing in the Omega Engine for the first time?** Read in this order:

1. `ORACLE_STACK.md` — What the engine is (5 min)
2. `SOVEREIGN_MANDATES.md` — The 15 non-negotiable rules (3 min)
3. `docs/MASTER_DOCUMENT_SSOT.md` — This index (2 min)
4. `SOVEREIGN_ARK_BLUEPRINT.md` — What we're building toward (5 min)
5. Find your topic in §1 above → read the SSoT document

**Need to contribute a new R-doc?**
1. Check §1 to see if your topic already has an SSoT
2. If the existing SSoT is stale, create a DEEPENED version (see `R_MODEL_RESEARCH_PROTOCOL.md`)
3. If the topic doesn't exist yet, create a new R-doc and add it to this SSoT in a future update

---

## §6 Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-06-12 | Researcher | Initial SSoT — consolidated 177+ docs, mapped 12 domains, produced persistence plan |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SSoT-MASTER ⬡ June 2026 ⬡*
