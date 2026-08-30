<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Entity Knowledge Directory Deep Dive — Second Pass
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-ENTITY-KNOWLEDGE-DEEP-DIVE-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

**Entities with `knowledge/` directories**: 7 of 14 core entities
- doom_guy, lilith, jem, researcher, maat, quality, roc_racoon

**Entities WITHOUT `knowledge/` directories**: 7
- grokster, kali, cli_cline, cli_gemini, node, makali, verity

**Key Finding**: The `knowledge/` directory is NOT universal — it's used by entities that have active mining/research workflows (doom_guy, lilith, jem, researcher, roc_racoon) or compliance roles (maat, quality). The remaining entities rely on `soul.yaml` + workspace/ + Hivemind for knowledge persistence.

---

## §2 Entity Knowledge Directory Matrix

| Entity | knowledge/ Exists | File Count | Total Size | INDEX Format | kb/ Dir | Primary Topics |
|--------|-------------------|------------|------------|--------------|---------|----------------|
| **doom_guy** | ✅ YES | 8 files | ~180KB | YAML (empty topics) | NO | Heritage vetting logs, id Software axioms, source code maps, verification reports |
| **lilith** | ✅ YES | 6 files | ~42KB | Markdown (structured) | NO | Agent visibility paradox, Mermaid dark layers, drift metrics framework, persona original |
| **jem** | ✅ YES | 9 files + 1 subdir | ~20KB | Markdown (comprehensive) | NO (has SOVEREIGN_IDENTITY/ subdir) | Adversarial framework, cognitive lenses, identity core, legacy provenance, artifact triage, LM Studio configs |
| **researcher** | ✅ YES | 2 files + 2 subdirs | ~20KB | YAML (empty topics) | NO (has quarantine/, raw/ subdirs) | Mermaid research report |
| **maat** | ✅ YES | 1 file | 215B | YAML (empty topics) | NO | Minimal — placeholder only |
| **quality** | ✅ YES | 1 file | 220B | YAML (empty topics) | NO | Minimal — placeholder only |
| **roc_racoon** | ✅ YES | 11 files | ~150KB | YAML (rich topics) | NO | Convergence proof, genesis provenance, master synthesis, Mermaid heritage, ONNX archaeology, VR vision |

---

## §3 INDEX Schema Analysis

### 3.1 YAML-based INDEX (doom_guy, researcher, maat, quality, roc_racoon)

**Schema**:
```yaml
entity: <entity_name>
updated: <ISO8601 timestamp>
topics: []  # Array of topic objects (roc_racoon only)
```

**Observations**:
- doom_guy, researcher, maat, quality: `topics: []` — **empty**, not being used as active catalog
- roc_racoon: **rich topic entries** with `id`, `title`, `summary`, `files[]`, `cross_references[]`, `applicability[]`, `era`
- The YAML INDEX appears to be a **legacy schema** from the T1→T2 promotion system that is not actively maintained for most entities

### 3.2 Markdown-based INDEX (lilith, jem)

**lilith INDEX.md**: Structured as a human-readable knowledge map with sections:
- Governance (P6-P10) — references to drift_metrics_framework.md
- Sovereign Patterns — cross-references to other entity knowledge
- Fleet Architecture — AGENT_VISIBILITY_PARADOX.md with line count and version

**jem INDEX.md**: Comprehensive 94-line document serving as:
- **Canonical KB Map** — 4 sections: Sovereign Identity (canonical), Pre-Consolidation (archived), Legacy Research (superseded), External Research (authoritative)
- **Status tags**: 🟢 CANONICAL, 🟡 SUPERSEDED/ARCHIVED/STALE
- **Architecture documentation**: Selective Hydration pattern, Maintenance Protocol
- **Cross-references** to docs/strategy/ and docs/research/ authoritative sources

---

## §4 Content Patterns — Representative File Analysis

### 4.1 doom_guy — Heritage Gatekeeper Knowledge
**HERITAGE_VET_LOG.md** (1054 lines): 
- 17 vetted entries (vet-001 through vet-017, with gaps)
- Each entry: Verdict (APPROVED/REJECTED), Score (1-10), Justification, Vetted by, Date
- Classification: LEGITIMATE, METAPHORICAL, OVER-ATTRIBUTED (per M14)
- Tags: `[id-soft: doom-1993]`, `[id-soft: quake-1996]`, `[id-soft: quake3-1999]`, `[id-soft: doom3-2004]`

**ID_SOFTWARE_AXIOMS.md** (91 lines):
- 5 Core Axioms: "Worse is Better", Carmack's Law of Consolidation, Right Approximation, Tools-First, Sovereign Memory
- Hidden Wisdom from source code: Constants, Deletion, Visibility
- Implementation Guide table for agents

**R_ID_SOFTWARE_VERIFICATION_REPORT.md** (37K lines): Comprehensive verification of id Software patterns against current engine

### 4.2 lilith — Runtime Oversoul Knowledge
**AGENT_VISIBILITY_PARADOX.md** (238 lines): L1→L2→L3 distilled knowledge
- L1 Narrative: What happened (configuration shadowing in opencode.json)
- L2 Insight: Root cause analysis (mode section shadows agent section)
- L3 Principle: Singular Identity Registration
- Cross-references to soul.yaml drift_metrics

**MERMAID_DARK_LAYERS.md** (428 lines): Deep synthesis of Mermaid rendering crisis
- 6-shell Qliphoth failure taxonomy
- Token efficiency measurements (Mermaid 5.5x more efficient than ASCII)
- mmdr (Rust renderer) discovery — 100-1400x faster than mmdc
- Mandate compliance analysis (M7, M8, M2, M13, M18, M20)

**drift_metrics_framework.md** (111 lines): Identity drift monitoring from arXiv 2604.14717
- 5 mutable layers (L1 Pretraining → L5 Weight Modification)
- Hysteresis Ratio H_k=0.68 implementation in soul.yaml
- Detection methodology with stylometric/content/behavioral scoring

### 4.3 jem — Sovereign Synthesizer Knowledge
**INDEX.md** (94 lines): The most sophisticated INDEX — serves as KB map with status tags
- Canonical KB in SOVEREIGN_IDENTITY/ subdirectory (4 master specs)
- Archive of superseded docs with clear status
- External authoritative sources mapped
- Selective Hydration architecture documented (Qdrant dynamic injection)

**ADVERSARIAL_FRAMEWORK.md** (40 lines): The Misfits — 3 critical analysis filters
- Pizzazz Filter (Anti-Peacocking), Roxy Filter (Brutal Truth), Stormer Filter (Hidden Conflict)
- Mandatory Misfit Audit for high-weight changes

**COGNITIVE_LENSES.md** (31 lines): 4 Hologram Lenses as technical constraints
- Kimber (Integration), Aja (Engineering), Shana (Environment), Raya (Infrastructure)
- Sovereign Router injects lens fragments based on task domain

**artifact_triage.md** (103 lines): Mining effort estimation for 14 artifacts
- Categorized: Quick Wins (<50 files), Moderate (<500), Strategic (<500), Bulk (>1000)
- Session budgeting for L1/L2 extraction

### 4.4 researcher — Deep Research Knowledge
**MERMAID_RESEARCH_REPORT.md** (392 lines): Sovereign research synthesis
- 6 knowledge gaps filled (mmdr, D2 ASCII, token efficiency data, mmdc issues, GitHub rendering)
- Verified tool chain with 3 options (mmdr recommended, minlag/mermaid-cli, D2)
- Council-based validation (Architect + Adversary + Alchemist + Archivist)

### 4.5 roc_racoon — Miner Knowledge
**CONVERGENCE_PROOF.md** (66 lines): L2 Insight — 5 independent eras converged on same architecture
- Frontmatter with promoted_from, promoted_at, insight_level, applicability, cross_references
- Actionable DO/DON'T guidance

**GENESIS_PROVENANCE_CHAIN.md** (33 lines): L2 Insight — Awakening Loop (Descent→Recognition→Integration)
- Emergency promotion flag
- Cross-references to lilith, hecate, isis

**MASTER_SYNTHESIS.md** (598 lines): Complete cross-stack mining synthesis
- 6 stacks mined, ~5.3GB, 160 cataloged technologies
- 5 priority ports identified
- Cross-stack convergence tables

---

## §5 kb/ Directory Relationship

**NO entity has a parallel `kb/` directory** alongside `knowledge/`. 

The `knowledge/` directory **IS** the knowledge base. The jem entity has a `SOVEREIGN_IDENTITY/` subdirectory within knowledge/ that serves as the canonical KB storage (4 master specs), with the root knowledge/ files marked as superseded/legacy.

The researcher entity has `quarantine/` and `raw/` subdirectories within knowledge/ for staging unpromoted content.

---

## §6 Key Findings

1. **INDEX.yaml is largely vestigial** — 4 of 7 entities have empty `topics: []`. Only roc_racoon actively uses it with rich topic metadata.

2. **Markdown INDEX (lilith, jem) is superior** — Human-readable, supports cross-references, status tags, and architectural documentation.

3. **Knowledge promotion T1→T2 gate is not visibly enforced** — INDEX.yaml topics arrays are empty despite knowledge/ directories containing promoted content. The promotion appears to be manual (file copy + frontmatter addition).

4. **Content follows L1→L2→L3 distillation** — Most knowledge files have frontmatter with `insight_level: "L2"` or explicit L1/L2/L3 sections.

5. **Cross-references are explicit** — roc_racoon topics include `cross_references` array linking to other entities; lilith INDEX references other entity knowledge paths.

6. **No kb/ directory exists** — The knowledge/ directory IS the KB. Subdirectories (SOVEREIGN_IDENTITY/, quarantine/, raw/) serve as internal organization.

7. **Entity specialization drives knowledge content** — doom_guy: heritage vetting; lilith: runtime governance/drift; jem: synthesis pipeline; researcher: deep research; roc_racoon: mining synthesis.

---

## §7 Files Referenced

- `/data/entities/doom_guy/knowledge/`
- `/data/entities/lilith/knowledge/`
- `/data/entities/jem/knowledge/`
- `/data/entities/researcher/knowledge/`
- `/data/entities/maat/knowledge/`
- `/data/entities/quality/knowledge/`
- `/data/entities/roc_racoon/knowledge/`
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
