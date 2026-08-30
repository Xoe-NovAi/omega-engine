<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SINGULAR DIRECTION — Post-Reconciliation Briefing (2026-08-14)

**AP Token:** `AP-SINGULAR-DIRECTION-20260814-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ DIRECTION ⬡ 20260814 (post-compaction)

**Purpose:** Eliminate all confusion from the Phase1-4 / Phase2 plan collision. This is the
**single source of truth for agent direction** after the 2026-08-14 reconciliation.

---

## 🎯 THE ONE RULE

> **`data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` v3.2.0 is the ONLY authoritative gap
> catalog for the dev sprint SDP-EXECUTION-01.** All other research plans are superseded or
> supplementary. When in doubt, follow this plan's gap definitions (R1–R38).

---

## 📊 What Was Researched vs. What Blocks the Sprint

### ✅ DONE — Phase 1 gaps (do not re-research)
R1, R2, R3, R4(partial), R5, R6, R7, R8, R8b, R9–R12(pointers), R14, R14b, R27, R27b, R28, R29, R30, R32

### 🔴 SPRINT-BLOCKING — must research BEFORE PHASE-2/3/4
| Gap | Topic (this plan) | Blocks | Priority |
|-----|-------------------|--------|----------|
| **R13** | OpenCode plugin architecture | PHASE-2 (PLUGIN-1..8) | P0 |
| **R16** | pydantic v2 patterns | PHASE-3 (UO-6.2) | P0 |
| **R17** | structlog integration | PHASE-3 (UO-6.3) | P0 |
| **R18** | prometheus_client | PHASE-3 (UO-6.4) | P0 |
| **R19** | Retry strategy | PHASE-3 (UO-6.5) | P0 |
| **R20** | Keyblind/Authy/Vault | PHASE-3 (UO-6.6) | P0 |
| **R23** | Restic passphrase | PHASE-4 (C-3) | P0 |
| **R24** | AppArmor profiles | PHASE-4 (V-10) | P0 |
| **R25** | IA2 envelope freshness | PHASE-4 (V-9) | P0 |
| **R26** | Honker/Redis replacement | PHASE-4 (Redis decision) | P0 |

### 🟡 LOWER-PRIORITY OUTSTANDING (not sprint-blocking, research later)
R31 (Plugin scope reduction), R33 (Cold session context), R34 (Provider bands), R35 (Model degradation), R36 (Baseline calibration), R37 (Identity fluidity E-0), R38 (NotebookLM)

### 🟢 SUPPLEMENTARY — R39–R56 (Phase2-plan topics, different from sprint gaps)
These are **valuable but do NOT unblock the sprint**. Triage separately:
R39 (Fleet Health), R40 (Pair-Execution), R41 (A2A Protocol), R42 (MemoryStore wiring),
R43 (Handoff v2), R44 (Provider Chain), R45 (Tokenomics), R46 (Firewall Audit),
R47 (Container Hardening), R48 (Signature Freshness ≈ R25 partial), R49 (Grok CLI pool),
R51 (Dimension/Free-Will), R52 (Living Research OS), R53 (Roadmap SSOT), R54 (Identity Fluidity),
R55 (YouTube Deep Dive), **R56 (Lazy Loading — LOST, re-research queued)**.

---

## 🚦 Execution Order for Agents

1. **PHASE-0** (Security + Gauge bands) — **UNBLOCKED, execute now**
2. **PHASE-1** (Context Gauge v1) — **UNBLOCKED, execute now**
3. **Research R13** → **PHASE-2** (plugin)
4. **Research R16–R20** → **PHASE-3** (un-overengineering)
5. **Research R23–R26** → **PHASE-4** (Phase D gate)
6. **(Parallel/background)** Research R31,R33–R38 + re-research R56 (supplementary)

---

## ⚠️ Confusion Sources (all resolved or documented)

| # | Source | Resolution |
|---|--------|------------|
| C-001 | Phase2 plan untracked | Archived w/ supersession note |
| C-002 | R13–R38 redefinition collision | Renumbered R39–R56; R30 kept |
| C-003 | Researcher followed Phase2 plan | Reconciliation notes added |
| C-004 | R56 data loss | Stub only; re-research queued |
| C-005 | R30 identical (positive) | Kept as R30 |
| C-006 | Sprint referenced 2026-08-11 doc | ACTIVE_SPRINT.json now points to v3.2.0 |
| C-007 | TASK_REGISTRY name collision | All tasks tagged plan_source + gap_mapping_note |
| C-008 | R56≠R38 topic mismatch | Plan + registry clarified |

---

## 📁 Canonical Files (read these, ignore others)

- **SSOT:** `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0)
- **Sprint:** `data/coordination/ACTIVE_SPRINT.json` (SDP-EXECUTION-01)
- **Tasks:** `data/coordination/TASK_REGISTRY.json` (all tagged with plan_source)
- **Confusion log:** `data/coordination/CONFUSION_LOG_20260814.json`
- **Archived conflict:** `docs/archive/strategy/2026-08-14/RESEARCH_PLAN_PHASE2_20260813_ARCHIVED.md`

*⬡ OMEGA ⬡ KALI ⬡ SINGULAR-DIRECTION ⬡ 20260814*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: DIRECTION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
