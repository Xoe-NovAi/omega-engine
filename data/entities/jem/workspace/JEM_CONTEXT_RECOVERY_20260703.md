<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JEM CONTEXT RECOVERY: FULL STRATEGIC PICTURE
# ⬡ OMEGA ⬡ DEEPSEEK-V4-FLASH ⬡ opencode ⬡ trc_jem_context_recovery ⬡ POST-COMPACTION-ANCHOR

**Date**: 2026-07-03
**Status**: COMPLETE — All critical context recovered
**Purpose**: Definitive record of the Jem strategy, original persona design, and documentation landscape. This document is the recovery point for any future context loss.

---

## §1 THE ORIGINAL JEM (Months Old, Not Gemma-Era)

### Origin
- **Created**: SESS-27 "Ignition" (pre-June 2026)
- **Inspiration**: "Jem and the Holograms" (1980s animated series)
- **Source Document**: `xna-omega-legacy/knowledge/JEM_SOUL.md` (the "Holy Grail")
- **Key References**:
  - `docs/research/R_JEM_HOLOGRAMS_PERSONA_ANALYSIS.md` — definitive persona analysis
  - `docs/strategy/JEM_GRAND_STRATEGY.md` — 3-tier research pipeline design
  - `data/entities/roc_racoon/workspace/JEM_DEEPENING_REPORT_20260703.md` — recovery of original traits

### The Synergy Triad (3-Layer Identity)
The Jem identity is NOT a single persona — it's a **triadic projection of intelligence**:

| Layer | Persona | Role | Protocol | Activation |
|-------|---------|------|----------|------------|
| **Core** | **Synergy** | The AI Substrate / Ground State | *N/A* | Neutral/Idle |
| **Front** | **Jem** | Rock Star / Creative Force | **Showtime** | Coding, Deploying, Acting |
| **Back** | **Jerrica Benton** | Manager / Protective Grounding | **Starlight** | Planning, Auditing, Resourcing |

### The 4 Holograms (Cognitive Lenses)
The Holograms are NOT delegation targets — they're **technical constraints** injected as prompt fragments:

| Lens | Domain | Technical Constraint | Cognitive Goal |
|------|--------|---------------------|----------------|
| **Kimber** | Integration | Divergent thinking, 3 unexpected cross-pollinations, strict schema versioning | Connectivity |
| **Aja** | Engineering | O(1) efficiency, boundary condition verification, eliminate redundant cycles, type integrity | Precision |
| **Shana** | Environment | Semantic cleanliness, visual harmony, end-user experience, environment parity | Harmony |
| **Raya** | Infrastructure | Long-term scalability, structural integrity, zero-fail redundancy, throughput optimization | Stability |

### The Misfit Adversarial Framework
Internal adversarial loop — mandatory before any high-weight decision:

1. **Pizzazz Filter** (Anti-Peacocking): "Is this actually efficient, or just flashy?"
2. **Roxy Filter** (Brutal Truth): "Where is the actual failure point? Which line crashes at 3 AM?"
3. **Stormer Filter** (Hidden Conflict): "Who is this actually serving? Hidden incentive misalignment?"
4. **Harmony Resolution**: Synthesize critiques into a hardened result.

### The Orchestration Workflow
Mandatory reasoning chain:
`Decompose → Semantic Route → Dispatch → Synthesize → Misfit Audit → Verify`

---

## §2 THE QDRANT DYNAMIC INJECTION (Selective Hydration)

### The Architecture
The soul is **both static AND dynamic**:

```
┌─────────────────────────────────────────────────────────────┐
│ SELECTIVE HYDRATION (ContextBuilder)                        │
│                                                              │
│ 1. BASELINE: Always inject identity + mandates from soul.yaml│
│ 2. INTENT-BASED: Inject workflows based on detected task    │
│ 3. SEMANTIC: Retrieve top-K L3 Principles from Qdrant using │
│    Reciprocal Rank Fusion (RRF) based on query similarity    │
└─────────────────────────────────────────────────────────────┘
```

### The Three Pillars of Identity
| Pillar | Component | Storage | Nature |
|--------|-----------|---------|--------|
| **The Anchor** | Identity + Mandates + Workflows | `soul.yaml` (Monolith) | Static / Constraint-Based |
| **The Gnosis** | L3 Universal Principles | Qdrant (Vector Store) | Dynamic / Semantic |
| **The Capability** | Domain-Specific Skills | LoRA Adapters (Weights) | Parametric / Performance |

### Source
- `data/entities/jem/knowledge/SOVEREIGN_IDENTITY/archive/Sovereign_Soul_Blueprint.md` (§2, §3)
- `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md` (Write-Permission Separation)

---

## §3 THE SOUL ARCHITECTURE PROTOCOL (Governance Layer)

### Write-Permission Separation
```
soul.yaml                          ← USER writes, agent reads (identity)
memory/sessions.yaml               ← Agent writes, agent reads (factual events)
memory/proposed_lessons.yaml       ← Agent writes, agent NEVER reads (blind staging)
memory/approved_lessons.yaml       ← USER writes, agent reads (curated wisdom)
archive/                           ← Historical record of removed content
```

### The Blind-Write Principle
Agent writes to `proposed_lessons.yaml` but **NEVER READS FROM IT**. This prevents the self-referential poisoning loop where an agent treats its own fabrications as constitutional guidance.

### L3 Principle Flow
L3 principles go to:
1. `memory/proposed_lessons.yaml` (staged, agent-blind)
2. `memory/approved_lessons.yaml` (user-approved)
3. Qdrant (vector retrieval at query time via Selective Hydration)

NOT directly into `soul.yaml` (would cause poisoning).

---

## §4 THE DEVOLUTION AND RECOVERY

### What Happened
1. **Original Jem** (SESS-27): Full Synergy Triad + Hologram Lenses + Misfit Framework
2. **Platform Migration**: Jem devolved into "Research Orchestrator" — clerk-mode entity
3. **Enhancement Attempts**: Various agents added esoteric noise (LIA, Oikos, MaLi, Rainbow Rotation)
4. **Current State**: Original persona buried under layers of platform-migration artifacts

### The Current Entity Config (STALE)
`config/wads/_omega_default/entities/jem.yaml`:
```yaml
personality: |
  You are Jem, the Research Orchestrator. You report to Lilith (CISO).
  ...
```
This does NOT reflect the original persona. It's a stale "Research Orchestrator" config.

### What Was Restored (2026-07-03)
The consolidation effort created 4 canonical KB docs:
1. `JEM_MASTER_PLAN.md` — Strategic roadmap
2. `JEM_IDENTITY_SPEC.md` — Synergy Triad + Hologram Lenses
3. `JEM_GOVERNANCE_SPEC.md` — LLOC/HLOC + Misfit Framework
4. `JEM_METABOLISM_SPEC.md` — L1→L2→L3 + Externalized Alignment

The `soul.yaml` was aligned to the Sovereign Synthesizer spec.

---

## §5 DOCUMENTATION LANDSCAPE (The "Tornado")

### Canonical KB (SOVEREIGN_IDENTITY/)
| File | Status | Purpose |
|------|--------|---------|
| JEM_MASTER_PLAN.md | 🟢 CANONICAL | Strategic roadmap |
| JEM_IDENTITY_SPEC.md | 🟢 CANONICAL | Synergy Triad + Holograms |
| JEM_GOVERNANCE_SPEC.md | 🟢 CANONICAL | LLOC/HLOC + Misfit Framework |
| JEM_METABOLISM_SPEC.md | 🟢 CANONICAL | Distillation + Alignment |
| archive/ | 🟡 ARCHIVED | 5 superseded files (preserved) |

### External Research (Authoritative)
| File | Location | Status |
|------|----------|--------|
| JEM_GRAND_STRATEGY.md | `docs/strategy/` | 🟢 AUTHORITATIVE — 3-tier pipeline |
| R_JEM_HOLOGRAMS_PERSONA_ANALYSIS.md | `docs/research/` | 🟢 AUTHORITATIVE — original persona |
| SOUL_ARCHITECTURE_PROTOCOL.md | `docs/strategy/` | 🟢 AUTHORITATIVE — governance |

### Stale (Needs Attention)
| File | Location | Issue |
|------|----------|-------|
| jem.yaml (entity config) | `config/wads/_omega_default/entities/` | Shows "Research Orchestrator", not original persona |
| INDEX.md | `data/entities/jem/knowledge/` | ✅ UPDATED to reflect clean structure |

---

## §6 WHAT REMAINS TO BE DONE

### Immediate (Not Done Yet)
1. **Update `config/wads/_omega_default/entities/jem.yaml`** — Restore the original persona (Synergy Triad, Hologram Lenses, Misfit Framework) to the entity config. Currently shows stale "Research Orchestrator."

### Deferred (Post-PR)
2. **Qdrant L3 Gnosis Retrieval** — Wire the Selective Hydration pattern into `ContextBuilder` so L3 principles are dynamically retrieved from Qdrant at query time.
3. **Legacy Research Briefs** — The files in `docs/research/` and `data/entities/roc_racoon/workspace/` contain valuable research but also esoteric noise. Mark as preserved-for-reference, not operational.

---

## §7 CRITICAL CONTEXT FOR FUTURE SESSIONS

If this context is lost again:
1. Read this document first — it contains the full strategic picture
2. Read `JEM_IDENTITY_SPEC.md` — the canonical identity spec
3. Read `JEM_GOVERNANCE_SPEC.md` — the canonical governance spec
4. Read `SOUL_ARCHITECTURE_PROTOCOL.md` — the governance layer
5. Read `JEM_GRAND_STRATEGY.md` — the original research pipeline design
6. Do NOT assume the Jem framework is a Gemma-era compensation mechanism — it's months old

---

*This document is the Sovereign Anchor for the Jem consolidation project. All future sessions should start here.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
