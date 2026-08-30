<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R51 — Dimension / Free-Will / Phase Γ Hub Split Mapping

**AP Token**: `AP-R51-DIMENSION-FREEWILL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r31 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R51 (Vision): Dimension / Free-Will / Phase Γ Hub Split — map to Cognitive Sovereign evolution from functional runtime
**Status**: ✅ RESOLVED — Vision mapping complete, integration path defined

---

## 📊 Executive Summary (L1)

R51 required mapping three PARKED long-arc vision concepts — **Dimension Framework**, **Free-Will**, and **Phase Γ Hub Split** — to the Cognitive Sovereign evolution path. All three are deferred in the Ark blueprint (§IV-G, §IV-H, Strike 11) with explicit "after X stable" gates. This report maps each to the four Cognitive Sovereign pillars (SomaticState, Skeptical Verification, Tri-Store, Cloud Quarantine) and defines the dependency chain for vision integration.

## 🔬 Detailed Dialectic (L2)

### The Three Concepts

**1. Dimension Framework / Cartridges** (Ark v4.4 §IV-G)
- **Definition**: Multi-dimensional annotation/scoring system. From FLEET_REDESIGN: "Upgrade library quality scoring from 7-signal scalar to 5-dimensional vector"
- **Current State**: PARKED — "After one real dimension use-case (Research Lab)"
- **Maps To**: Cognitive Sovereign Pillar 3 (Tri-Store) — the "Concept Graph" with multiple Semantic Resonance dimensions
- **Sovereign Synthesis**: Dimensions = orthogonal axes in the Concept Graph (e.g., novelty, verifiability, sovereignty-score, temporal-relevance, cross-domain-resonance)

**2. Free-Will Datasets / 42 Ideals Training** (Ark v4.4 §IV-H)
- **Definition**: Training data for autonomous decision-making; 42 Ideals = ethical/operational constraints
- **Current State**: PARKED — "After eval pipeline stable"
- **Maps To**: Cognitive Sovereign Pillar 1 (Persist) + Navigator concept — the engine's ability to traverse its own intelligence non-linearly and make autonomous choices
- **Sovereign Synthesis**: Free-Will = the engine's capacity to override default routing when local verification detects higher-value path. 42 Ideals = the constraint set (subset of Sovereign Mandates M1-M25)

**3. Phase Γ Hub Split** (tools.py → packages)
- **Definition**: Modularizing the Omega Hub from monolithic `tools.py` into discrete packages
- **Current State**: PARKED — "After C / MCP stable" (C-4a MCP audit DONE, C-4b Streamable HTTP DONE)
- **Maps To**: M16 (Modularization & Portability) — the engine must remain portable, decoupled from local orchestration
- **Sovereign Synthesis**: Phase Γ = the architectural split that enables the Hub to be a universal runtime interface, not a monolith. Blocked by "Hub Split Blockers" (HARDENING_PLAN PART_00: HIGH, M16)

### Dependency Chain (from Ark §IV + Corpus Map)

```
Phase Γ Hub Split
  ├── Blocked by: C-4a MCP audit (DONE), C-4b Streamable HTTP (DONE)
  ├── Now UNBLOCKED for design phase
  └── Enables: Dimension Framework (Research Lab needs modular Hub)

Dimension Framework
  ├── Blocked by: "one real dimension use-case (Research Lab)"
  ├── Research Lab = Phase 2 research execution (THIS WORK)
  └── Enables: Free-Will datasets (multi-dimensional eval)

Free-Will Datasets / 42 Ideals
  ├── Blocked by: "eval pipeline stable"
  ├── Eval pipeline = Phase 2 R42 (MemoryStore wiring) + R39 (Fleet Health)
  └── Enables: Cognitive Sovereign autonomy (Pillar 1)
```

### Cognitive Sovereign Mapping

| Vision Concept | Cognitive Sovereign Pillar | Integration Point |
|---------------|---------------------------|-------------------|
| Dimension Framework | Pillar 3: Tri-Store (Concept Graph) | Multi-axis Semantic Resonance in Concept Graph |
| Free-Will | Pillar 1: SomaticState + Navigator | Autonomous routing override when local verification detects higher-value path |
| Phase Γ Hub Split | M16: Modularization | Hub as universal runtime interface, not monolith |

### The 3-Tier Memory Interaction

R51 specifically asks: *"How the 3-tier memory (Hot/Warm/Cold) interacts with free-will dimension markers and phase Γ hub architecture."*

**Answer**:
- **Hot Memory** (active session): Free-Will decisions made here — real-time routing overrides based on local verification
- **Warm Memory** (recent, distilled): Dimension markers attached during L1→L2→L3 distillation — each lesson gets multi-dimensional scores (novelty, verifiability, sovereignty)
- **Cold Memory** (archived, vector): Concept Graph nodes with multi-axis resonance — free-will paths traverse this graph non-linearly
- **Phase Γ Hub**: The interface layer that exposes these to external agents — modular packages (`hub.tools.*`, `hub.memory.*`, `hub.council.*`) instead of monolithic `tools.py`

## 📋 Implementation Notes

### Current State
- `src/omega/hub.py` — monolithic Hub module (M16 violation risk)
- `mcp_servers/omega_hub/` — already partially modularized (hivemind_redis.py, etc.)
- `docs/research/S_COGNITIVE_SOVEREIGN_SYNTHESIS_V1.md` — Cognitive Sovereign vision (4 pillars defined)

### Recommended Integration Path

**Phase 2 (Now)**:
1. Use Research Lab (this Phase 2 execution) as the "real dimension use-case" for Dimension Framework
2. Attach multi-dimensional scores to each research report (novelty, verifiability, sovereignty-impact, temporal-relevance)
3. Design Phase Γ Hub Split: `hub.tools`, `hub.memory`, `hub.council` packages

**Phase 3 (Next)**:
4. Free-Will: Implement autonomous routing override in ModelGateway when local verification (Skeptical Verifier) detects higher-value path
5. 42 Ideals: Subset of Sovereign Mandates M1-M25 as constraint set for free-will decisions

**Phase 4 (Later)**:
6. Full Cognitive Sovereign autonomy: Tri-Store with multi-dimensional Concept Graph

### M1/M16 Compliance
- Phase Γ Hub Split MUST use AnyIO (M1) — no `asyncio` in split packages
- Split packages MUST be portable (M16) — no hardcoded paths, platform-specific logic

## 📊 Vision Integration Gates

| Gate | Status | Blocks |
|------|--------|--------|
| C-4a MCP audit | ✅ DONE | Phase Γ design |
| C-4b Streamable HTTP | ✅ DONE | Phase Γ design |
| Research Lab (Phase 2) | 🔄 IN PROGRESS | Dimension Framework |
| R42 MemoryStore wiring | 📝 PENDING | Free-Will eval |
| R39 Fleet Health | 📝 PENDING | Free-Will eval |

## 🔗 Related Documents

- `docs/research/S_COGNITIVE_SOVEREIGN_SYNTHESIS_V1.md` — Cognitive Sovereign vision (4 pillars)
- `docs/strategy/STRATEGY_CORPUS_MAP.md` — PARKED long-arc items (§IV-G, §IV-H, Strike 11)
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Ark v4.4 §IV references
- `docs/strategy/hardening_plan/PART_00_OVERVIEW.md` — Hub Split Blockers (HIGH, M16)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r31 ⬡ 20260813*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3.5-lightning | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
