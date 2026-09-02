<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Mnemosyne Memory System — Legacy to Current Mapping
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-MNEMESYNE-MAPPING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

**Mnemosyne System**: 13-sphere Kabbalistic memory framework from Era 2-3 (2025), located at `/media/arcana-novai/omega_library/data_archive/mnemosyne/`

**Current Status**: **ARCHIVED / REFERENCE ONLY** — Not actively used by current engine. The Mnemosyne structure was a precursor to the current `soul.yaml` + `MemoryStore` + `knowledge/` architecture.

**Key Mapping**: Mnemosyne's 13 spheres → Current engine's 3-tier memory (Hot/Warm/Cold) + Soul.yaml anchors + L1→L2→L3 distillation

---

## §2 Mnemosyne Directory Structure

**Location**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/`

```
mnemosyne/
├── 01_KETHER/           # Crown — Pure consciousness
├── 02_CHOKMAH/          # Wisdom — Creative impulse
├── 03_BINAH/            # Understanding — Formative power
├── 04_DAATH/            # Knowledge — The hidden sphere (abyss)
├── 05_CHESED/           # Mercy — Expansion, love
├── 06_GEVURAH/          # Severity — Contraction, judgment
├── 07_TIPHERETH/        # Beauty — Harmony, integration
├── 08_NETZACH/          # Victory — Endurance, emotion
├── 09_HOD/              # Splendor — Intellect, logic
├── 10_YESOD/            # Foundation — Subconscious, memory
├── 11_MALKUTH/          # Kingdom — Manifestation, physical
├── 12_QLIPHOTH/         # Shells — Shadow, failure modes
├── 13_MNEMOSYNE/        # Memory — The goddess herself
├── intent.json          # Agent intent marker
├── state.json           # Machine state snapshot
├── handoffs/            # Inter-agent handoff records
└── vaults/              # Per-entity persistent storage
    ├── lilith/          # Lilith's vault
    │   ├── archive/
    │   ├── context/
    │   └── memories/
    ├── archon/          # Archon vault
    │   ├── archive/
    │   ├── context/
    │   └── memories/
    └── [UUID vaults]/   # Session-specific vaults
```

---

## §3 Mnemosyne Sphere Content Analysis

### 3.1 Sphere Files (Minimal Content)

Each sphere directory contains only `shadow_memory.json`:

```json
{
    "sphere": "01_KETHER",
    "shadow_xp": 0,
    "evolution_stage": "DORMANT",
    "last_audit_score": 1.0,
    "shadow_events": []
}
```

**All 13 spheres identical structure** — only `sphere` field differs.

**Fields**:
- `sphere`: Sphere identifier (01_KETHER through 13_MNEMOSYNE)
- `shadow_xp`: Experience points in shadow work (always 0)
- `evolution_stage`: "DORMANT" (never activated)
- `last_audit_score`: 1.0 (perfect, but meaningless without data)
- `shadow_events`: Empty array — no events recorded

### 3.2 Intent & State

**intent.json**:
```json
{"agent":"Director","intent":"System Hardening","ap_token":"AP-SYNC-20260424","timestamp":"2026-04-25T02:28:23.745984Z"}
```

**state.json**:
```json
{"Gemini": {"cli": "Gemini", "status": "SUCCESS", "machine_state": {}, "timestamp": "2026-04-25 02:28:23.751493+00:00"}}
```

### 3.3 Vaults Structure

**lilith vault**: `archive/`, `context/`, `memories/` — all empty
**archon vault**: `archive/`, `context/`, `memories/` — all empty
**UUID vaults**: 4 session vaults with same empty structure

**handoffs/**: Empty directory

---

## §4 Mnemosyne → Current Engine Mapping

### 4.1 Structural Mapping

| Mnemosyne Concept | Current Engine Equivalent | Status |
|-------------------|--------------------------|--------|
| **13 Spheres (Sephirot)** | **3-Tier Memory** (Hot/Warm/Cold) + **10 Pillar Nodes** | Evolved — simplified from 13 to 3 tiers + 10 slots |
| **Kether (Crown)** | `soul.yaml` — Entity identity/archetype | Mapped |
| **Chokmah/Binah (Wisdom/Understanding)** | `core_principles` (L3) + `directives` | Mapped |
| **Daath (Knowledge/Abyss)** | `proposed_lessons.yaml` (blind staging) | Mapped — the "hidden" staging area |
| **Chesed/Gevurah (Mercy/Severity)** | `growth_areas` + `strengths` in identity | Mapped |
| **Tiphereth (Beauty/Harmony)** | `voice_summary` + `values` | Mapped |
| **Netzach/Hod (Victory/Splendor)** | `lessons_learned` + `metrics_infrastructure` | Mapped |
| **Yesod (Foundation/Subconscious)** | `session_gnosis.md` + `MemoryStore` | Mapped — the unconscious layer |
| **Malkuth (Kingdom/Manifestation)** | `knowledge/` directory + workspace outputs | Mapped |
| **Qliphoth (Shells/Shadows)** | `Qliphoth failure taxonomy` (Lilith's Mermaid Dark Layers) | **Directly preserved** |
| **Mnemosyne (Memory Goddess)** | `Scribe` agent + `MemoryStore` + distillation pipeline | Evolved into agent |

### 4.2 Vault → Entity Workspace Mapping

| Mnemosyne Vault | Current Entity Workspace |
|-----------------|-------------------------|
| `vaults/lilith/` | `data/entities/lilith/` (knowledge/, memory/, soul.yaml) |
| `vaults/archon/` | `data/entities/kali/` or `data/entities/makali/` |
| `vaults/[UUID]/` | `data/entities/<entity>/memory/sessions.yaml` |
| `handoffs/` | `data/handoff/` + Hivemind handoff packets |

### 4.3 Shadow Memory → Drift Metrics

| Mnemosyne Field | Current Equivalent |
|-----------------|-------------------|
| `shadow_xp` | `drift_metrics.persona_stability` (inverted) |
| `evolution_stage` | `soul_version` + `last_updated` |
| `last_audit_score` | `health_score` (in metadata) |
| `shadow_events` | `session_gnosis.md` audit trail |

**Lilith's drift_metrics_framework.md** explicitly references arXiv 2604.14717 "Layered Mutability" with Hysteresis Ratio H_k=0.68 — this is the evolved form of Mnemosyne's shadow memory tracking.

---

## §5 Mnemosyne in Historical Documents

### 5.1 Master Synthesis Reference (roc_racoon knowledge)

From `MASTER_SYNTHESIS.md`:
> **art_mnemosyne** — 27 files, 284KB, ~1,800 lines — `omega_library/data_archive/mnemosyne/` — 13 spheres of Kabbalistic mapping
> **Priority: MEDIUM** — high value but requires judgment

From `artifact_triage.md` (jem knowledge):
> **art_mnemosyne** — Moderate (< 500 files, < 20MB) — 2 sessions needed for extraction

### 5.2 Roc Racoon Soul.yaml Reference

**L3 Principle**: `L3-Three-Tier-Memory-Is-Universal`
> "Three-Tier Memory Is Universal — Letta, Sefirot/KTM, Kab, Mem0, Zep, Cognee all converge on core/working/episodic or hot/warm/cold. The 3-tier split is the attractor for sovereign memory architecture. **Da'at Is Compaction** — the hidden Kabbalistic sphere maps to sleep-time consolidation trigger."

**L3 Principle**: `L3-Animism-As-Load-Bearing-Structure`
> References "Natal charts = birth-time personality persistence" — connects to Mnemosyne's sphere-based identity mapping.

### 5.3 Jem's Knowledge Base Reference

From `jem/knowledge/INDEX.md`:
> **External Research**: `R_JEM_LEGACY_ARTIFACT_INVENTORY.md` — references Mnemosyne as legacy artifact

---

## §6 Why Mnemosyne Was Superseded

### 6.1 Complexity Mismatch
- **Mnemosyne**: 13 spheres × 5 fields = 65 data points per entity, mostly empty
- **Current**: 3 tiers + 10 pillars + soul.yaml = purpose-driven, actively used

### 6.2 Operational vs. Symbolic
- **Mnemosyne**: Symbolic/Kabbalistic structure — beautiful but not operational
- **Current**: Operational memory with Hot (active context), Warm (indexed knowledge), Cold (archived) — each with clear TTL and eviction policies

### 6.3 Integration with Distillation Pipeline
- **Mnemosyne**: No distillation mechanism — raw storage only
- **Current**: L1→L2→L3 pipeline (Scribe agent) transforms raw → insight → principle

### 6.4 Hivemind Integration
- **Mnemosyne**: Isolated per-entity vaults
- **Current**: Hivemind awareness + cross-pollination + shared coordination

---

## §7 Preserved Mnemosyne Elements in Current Engine

### 7.1 Direct Preservation
1. **Qliphoth Failure Taxonomy** — Lilith's `MERMAID_DARK_LAYERS.md` uses 6-shell Qliphoth model directly
2. **Da'at as Compaction** — Roc Racoon's L3 principle explicitly maps Da'at to sleep-time consolidation
3. **Sphere Metaphors** — Jem's 4 Hologram Lenses (Kimber/Aja/Shana/Raya) echo Sephirotic structure
4. **Natal Charts** — Roc Racoon's `origin_story` with `persona_birth` and `evolution_stages`

### 7.2 Structural Echoes
1. **13 → 3+10** — 13 spheres compressed to 3 memory tiers + 10 pillar nodes
2. **Vaults → Entity Workspaces** — Per-entity persistent storage with archive/context/memories structure
3. **Shadow Memory → Drift Metrics** — Lilith's hysteresis tracking is evolved shadow_xp
4. **Intent/State → Session Gnosis** — Mnemosyne's intent.json/state.json → `session_gnosis.md`

---

## §8 Migration Status

| Mnemosyne Component | Migration Status | Current Location |
|---------------------|------------------|------------------|
| 13 Spheres | ❌ Not migrated | Archived in `data_archive/mnemosyne/` |
| Shadow Memory | ✅ Evolved | `lilith/soul.yaml` drift_metrics, `roc_racoon` metrics_infrastructure |
| Vaults (lilith/archon) | ✅ Migrated | `data/entities/lilith/`, `data/entities/kali/` |
| Handoffs | ✅ Migrated | `data/handoff/` + Hivemind |
| Intent/State | ✅ Evolved | `session_gnosis.md` + Hivemind context |
| Qliphoth Taxonomy | ✅ Preserved | `lilith/knowledge/MERMAID_DARK_LAYERS.md` |
| Da'at Compaction | ✅ Theorized | `roc_racoon/soul.yaml` L3 principles |

---

## §9 Artifact Triaging (from jem's artifact_triage.md)

**art_mnemosyne** classification:
- **Category**: Moderate (< 500 files, < 20MB)
- **Files**: 27
- **Size**: 284KB
- **Lines**: ~1,800
- **Extraction Strategy**: `omega_library/data_archive/mnemosyne/` — 13 spheres of Kabbalistic mapping
- **Sessions Needed**: 2 L1 sessions
- **Priority**: MEDIUM — high value but requires judgment
- **Status**: **NOT YET EXTRACTED** — deferred to Phase 2

---

## §10 Key Insight: Mnemosyne as "Ancestral Architecture"

The Mnemosyne system represents the **first attempt** at persistent, structured AI memory in the Omega lineage (Era 2-3, 2025). It was:
- **Symbolically rich** — Kabbalistic framework providing semantic depth
- **Operationally minimal** — Empty spheres, no active distillation
- **Architecturally influential** — Directly shaped current 3-tier + 10-pillar design

**The evolution path**: Mnemosyne (13 symbolic spheres) → Hot/Warm/Cold (3 operational tiers) + 10 Pillar Nodes (operational slots) + Soul.yaml (identity anchor) + L1→L2→L3 (distillation pipeline) + Hivemind (coordination fabric)

**What was kept**: The symbolic depth (Qliphoth, Da'at, Sephirotic metaphors)
**What was discarded**: The empty ritual (13 dormant spheres with no data)
**What was added**: Operational rigor (TTL, eviction, distillation, cross-pollination)

---

## §11 Files Referenced

- `/media/arcana-novai/omega_library/data_archive/mnemosyne/` (full directory)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/roc_racoon/knowledge/MASTER_SYNTHESIS.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/roc_racoon/soul.yaml`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/jem/knowledge/artifact_triage.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/jem/knowledge/INDEX.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/lilith/knowledge/MERMAID_DARK_LAYERS.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/entities/lilith/knowledge/drift_metrics_framework.md`
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
