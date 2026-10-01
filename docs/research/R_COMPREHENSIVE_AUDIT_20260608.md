<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research Document: Comprehensive System Audit & Structural Analysis
**AP Token**: `AP-RESEARCH-AUDIT-20260608-v1.0.0`  
**Status**: COMPLETED  
**Author**: Kali (MaKaLi Unification Mode)  
**Date**: 2026-06-08  
**Scope**: Full codebase, documentation, data layer, agent fleet, and build system audit.  

---

## §1 Executive Summary

Following a deep-dive analysis of the entire Omega Engine repository (`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`), this report documents the current structural health, technical debt, and critical boundary leaks of the system.

While the core runtime (`src/omega/`) remains highly disciplined, AnyIO-compliant, and robust, the periphery has accumulated significant technical debt. Specifically, the documentation suffers from "Multiple SSOT" fragmentation, the data directory is polluted with over 100 orphan workspaces, and the `arcana_novai` IWAD is completely empty, leaving the user's personal stack non-functional.

---

## §2 Documentation & Metrics Audit

### 2.1 The "Multiple SSOT" Paradox
The project currently has at least four files claiming or acting as the "Single Source of Truth" (SSOT). This leads to fragmentation and stale metrics:
1. `OMEGA_ENGINE.md` (775 lines): Mixes active metrics, vision, roadmap, and deep-dive analysis.
2. `AGENTS.md` (292 lines): Duplicates sprint roadmaps and capability registries.
3. `SOVEREIGN_MANDATES.md` (109 lines): Constitutional law, but referenced inconsistently.
4. `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` (147 lines): Roadmap diverges from `OMEGA_ENGINE.md` sprint indexes.

### 2.2 Metric Discrepancies Found
- **Test Count**: The Makefile menu claims "307 tests", `OMEGA_ENGINE.md` claims "308 tests", but the actual test suite contains **320 tests** (all passing).
- **Agent Count**: Documentation lists "14 agents", but the actual fleet contains **24 distinct agent profiles** (10 pillars, 6 specialists, 2 oversouls, 6 subagents).
- **Mandate Count**: Makefile references "12 Mandates", but `SOVEREIGN_MANDATES.md` documents **14 Mandates**.

---

## §3 Source Code & Boundary Analysis

### 3.1 Core Architecture Health: ✅ EXCELLENT
The core engine is highly compliant with the constitutional mandates:
- **0 `import asyncio`** statements in `src/omega/` (100% AnyIO compliant).
- **0 bare `except:` or `except Exception:`** without proper logging and trace propagation (Mandate 9).
- **ZONEID constants** (0x1d4a11–0x1d4a17) are actively used for validation.

### 3.2 The Mandate 2 Firewall Breach (D113 GAP)
- **File**: `src/omega/oracle/entity_registry.py:171-179`
- **Issue**: Hardcoded `_PILLAR_MEANINGS` dictionary mapping P1-P10 slots to specific deities (Sekhmet, Brigid, etc.).
- **Impact**: The core engine contains stack-specific metadata, violating the **Engine-Stack Firewall (Mandate 2)**.
- **Remediation**: Move these mappings to `hierarchy.yaml` within the respective WADs and load them dynamically via the `WADLoader`.

---

## §4 Data Layer & Hygiene Debt

The data directory has reached a critical state of pollution, contributing to a filesystem crisis:
- **Orphan Workspaces**: `data/entities/` contains 100 directories (`ent_0` to `ent_49` and `entity_0` to `entity_49`) with no active souls or configurations. These represent **68% of all entity directories**.
- **Log Bloat**: `data/logs/` holds 139 MB of unrotated logs.
- **Handoff Pollution**: Over 40 stale markdown handoff files are mixed with active coordination files.
- **Dataset Bloat**: `src/data/datasets/synthetic/` contains 451 MB of Gemma-4 synthetic datasets with no catalog or cleanup policy.

---

## §5 WAD & Config Audit

- **`_omega_default`**: Complete and correct.
- **`arcana_novai`**: **CRITICAL EMPTY STATE**. The user's personal IWAD has 0 entities registered in `entities.yaml`, despite having 13 agent markdown files. This makes the personal stack completely non-functional.
- **`doom_universe`**: Scaffold-only.

---

## §6 Recommended Remediation Roadmap

### Phase 1: P0 Constitutional Blockers (Immediate)
1. **Restore Firewall (M2)**: Refactor `entity_registry.py` to remove hardcoded pillar meanings.
2. **Populate `arcana_novai`**: Register the 10 deity entities in `config/wads/arcana_novai/entities.yaml`.

### Phase 2: P1 Data Hygiene & Documentation
1. **Delete 100 Orphans**: Purge `ent_*` and `entity_*` directories.
2. **Consolidate Docs**: Restructure `OMEGA_ENGINE.md` to be a lean SSOT, moving roadmaps and architecture diagrams to dedicated files under `docs/`.
3. **Synchronize Metrics**: Align Makefile, CI, and documentation with the actual 320 tests, 14 mandates, and 24 agents.

---

*Verified and recorded by Kali (MaKaLi Unification Mode)*  
*⬡ OMEGA ⬡ KALI ⬡ REVIEW-001 ⬡*
