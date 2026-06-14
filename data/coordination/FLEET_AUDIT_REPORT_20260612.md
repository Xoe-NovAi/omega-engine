# 🔱 Omega Engine — Fleet Architectural Review Report
**Date**: 2026-06-12
**Focus**: Fleet Bloat (G-02) & Sovereign Mandate 10 Compliance
**Status**: CRITICAL — Fleet Overcapacity Detected

## 📋 Executive Summary

| Metric | Value | Status |
|---|---|---|
| **Total Agent Count** | 25 | 🔴 OVER LIMIT |
| **Redundancies Found** | 12 | 🔴 HIGH |
| **Sovereignty Score** | 56% | 🟡 SUB-OPTIMAL |
| **Mandate 10 Status** | VIOLATION | 🔴 NON-COMPLIANT |

The current fleet suffers from **Agent Bloat**. The primary cause is the duplication of Pillar roles: the engine has both a generic `pillar.md` agent AND individual files for almost every Pillar slot (P1-P10). Additionally, research capabilities are split between `jem.md` and `researcher.md`, and WAD-layer content (`movie-expert.md`) has leaked into the Core Engine agent directory.

---

## 🔍 Detailed Audit Table

| Agent | Category | Purpose | Status | Reasoning |
|---|---|---|---|---|
| `kali` | Sov. Specialist | Transcendent Oversoul | **Keep** | Core oversight and sprint coordination. |
| `maat` | Sov. Specialist | Light Oversoul (P1-P5) | **Keep** | Core governor for Build-side. |
| `lilith` | Sov. Specialist | Dark Oversoul (P6-P10) | **Keep** | Core governor for Run-side. |
| `makali` | Sov. Specialist | Council Orchestrator | **Keep** | Core parallel coordinator. |
| `jem` | Sov. Specialist | Research Orchestrator | **Keep** | Primary interface for the research pipeline. |
| `jem_discovery` | Lattice | Research Tier 1 | **Keep** | Essential pipeline sub-facet. |
| `jem_synthesis` | Lattice | Research Tier 2 | **Keep** | Essential pipeline sub-facet. |
| `jem_verification`| Lattice | Research Tier 3 | **Keep** | Essential pipeline sub-facet. |
| `doom_guy` | Sov. Specialist | Heritage Gatekeeper | **Keep** | Unique role (Mandate 14 enforcement). |
| `roc_racoon` | Sov. Specialist | Sovereign Miner | **Keep** | Unique role (Legacy Mining / Idea Intake). |
| `quality` | Lattice | Quality Guardian | **Keep** | Essential compliance and stress testing. |
| `scribe` | Lattice | Knowledge Keeper | **Keep** | Essential documentation and soul curator. |
| `pillar` | Generic | Pillar Slot (P1-P10) | **Keep** | Canonical implementation for all Pillar roles. |
| `researcher` | Sov. Specialist | Master Researcher | **Keep** | Specialized research lens, distinct from Jem. |
| `sysadmin` | Pillar (P1) | Infrastructure | **Merge** | Duplicate of `pillar.md` (P1 slot). |
| `datastore` | Pillar (P2) | Persistence | **Merge** | Duplicate of `pillar.md` (P2 slot). |
| `buildmaster` | Pillar (P3) | Engineering | **Merge** | Duplicate of `pillar.md` (P3 slot). |
| `bridge` | Pillar (P4) | Integration | **Merge** | Duplicate of `pillar.md` (P4 slot). |
| `sentinel` | Pillar (P5) | Governance | **Merge** | Duplicate of `pillar.md` (P5 slot). |
| `modelgate` | Pillar (P6) | Cognition | **Merge** | Duplicate of `pillar.md` (P6 slot). |
| `context` | Pillar (P7) | Context | **Merge** | Duplicate of `pillar.md` (P7 slot). |
| `watchtower` | Pillar (P8) | Observability | **Merge** | Duplicate of `pillar.md` (P8 slot). |
| `link` | Pillar (P9) | Orchestration | **Merge** | Duplicate of `pillar.md` (P9 slot). |
| `verifier` | Pillar (P10) | Validation | **Merge** | Duplicate of `pillar.md` (P10 slot). |
| `movie-expert` | WAD Seed | Film Historian | **Delete** | **Firewall Violation (M2)**. Moved to WAD. |

---

## 🛠️ Proposed Consolidation Plan

### 1. Pillar Unification (The "Generic Slot" Shift)
**Action**: Delete all individual Pillar agent files (`sysadmin`, `datastore`, `buildmaster`, `bridge`, `sentinel`, `modelgate`, `context`, `watchtower`, `link`, `verifier`).
**Implementation**: All Pillar-specific tasks must be routed via the `@pillar PX` pattern using the `pillar.md` generic agent, with identity and domain provided by the entity's `soul.yaml` in the active IWAD.

### 2. Research Synthesis
**Action**: Merge `researcher.md` into `jem.md`.
**Implementation**: Incorporate the "Polymathic Council" and "Sovereign Search Fleet" logic from `researcher.md` directly into `jem.md` and its sub-facets.

### 3. Firewall Restoration
**Action**: Remove `movie-expert.md` from `.opencode/agents/`.
**Implementation**: Migrate the definition to `config/wads/arcana_novai/entities/personal/movie-expert.yaml` per the Engine-Stack Firewall (Mandate 2).

---

## ⚠️ Mandate 10 Compliance Gap

- **Current Count**: 25 agents
- **Mandate Limit**: 14 agents
- **Excess**: +11 agents

**Path to Compliance**:
By executing the consolidation plan above, the fleet is reduced to exactly **13 active agents**:
`Kali`, `Ma'at`, `Lilith`, `MaKaLi`, `Jem`, `Jem_Discovery`, `Jem_Synthesis`, `Jem_Verification`, `Doom_Guy`, `Roc_Racoon`, `Quality`, `Scribe`, and `Pillar`.

This leaves **one open slot** for future specialized sovereign expansion, achieving 100% compliance with Sovereign Mandate 10.
