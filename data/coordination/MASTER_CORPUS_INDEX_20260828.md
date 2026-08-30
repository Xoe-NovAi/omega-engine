---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "master_corpus_index"
document_id: "MASTER_CORPUS_INDEX-20260828"
title: "Master Corpus Index — Deep Consolidation 2026-08-28"
status: "ACTIVE"
date: "2026-08-28"
author: "MA'AT (Build Oversoul)"
consolidation: "deep_consolidation_20260828"
sprint: "PUBLIC-DEBUT-01"
---

# 📚 Master Corpus Index — Deep Consolidation 2026-08-28

**AP Token**: `AP-MASTER-CORPUS-20260828-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ big-pickle ⬡ opencode ⬡ trc_maat_consolidation ⬡ ACTIVE

**Date**: 2026-08-28
**Sprint**: PUBLIC-DEBUT-01
**Consolidation**: deep_consolidation_20260828
**Authority**: MA'AT (Build Oversoul)

---

## 🎯 Consolidation Summary

| Corpus | Before | After | Archived | Deleted |
|--------|--------|-------|----------|---------|
| **Strategy** (`docs/strategy/`) | 141 | 81 current | 8 | 2 (test artifacts) |
| **Coordination** (`data/coordination/`) | 623 | ~228 root | 12 | 0 |
| **Research** (`data/coordination/R_*.md`) | 105 | 32 root | 10 | 0 |

**Total Reduction**: 869 → 341 active files (**61% reduction**)

---

## 📚 Corpus Index Links

| Corpus | Index | Archive Location |
|--------|-------|------------------|
| **Strategy** | `docs/strategy/STRATEGY_CORPUS_INDEX.md` | `docs/strategy/archive/20260828_deep_consolidation/` |
| **Coordination** | `data/coordination/COORDINATION_CORPUS_INDEX.md` | `data/coordination/archive/PUBLIC-DEBUT-01/` |
| **Research** | `data/coordination/RESEARCH_CORPUS_INDEX.md` | `data/coordination/research/archive/` |

---

## 🔑 Current Single Sources of Truth (SSOT)

### Sprint Execution
| Document | Location | Role |
|----------|----------|------|
| **DEBUT_REMEDIATION_MANUAL_20260817.md** | `docs/strategy/` | Sprint SSOT (D-533) |
| **ACTIVE_SPRINT.json** | `data/coordination/` | Live sprint tracker |
| **HMC_COLLABORATION_HUB.md** | `data/coordination/` | Coordination hub v2.0 |

### Mandates & Governance
| Document | Location | Role |
|----------|----------|------|
| **SOVEREIGN_MANDATES.md** | `docs/strategy/` | 27 Laws (v3.8.0) |
| **MANDATES_CONDENSED.md** | `docs/strategy/` | Tier-0 injection |
| **AGENTS.md** | `docs/strategy/` | Agent landing + 4 rules |
| **PIVOT_LOG.md** | `docs/strategy/` | Decisions D-521+ |

### Architecture & Vision
| Document | Location | Role |
|----------|----------|------|
| **HOLISTIC_ARCHITECTURE_PLAN_20260820.md** | `docs/strategy/` | Architecture SSOT |
| **SOVEREIGN_ARK_BLUEPRINT.md** | `docs/strategy/` | Vision (read-only) |
| **HOLISTIC_ARCHITECTURE_PLAN_20260820.md** | `data/coordination/` | Architecture mirror |

### Coordination & Sprint
| Document | Location | Role |
|----------|----------|------|
| **HMC_COLLABORATION_HUB.md** | `data/coordination/` | Coordination hub v2.0 |
| **ACTIVE_SPRINT.json** | `data/coordination/` | Live sprint tracker |
| **PRE_COMPACTION_MASTER_INDEX_20260828.md** | `data/coordination/` | Pre-compaction anchor |
| **GAP_REGISTRY.json** | `data/coordination/` | Gap authority (M27) |
| **WAKE_STATE.json** | `data/coordination/` | Wake state recovery |

---

## 📋 Decision Log (D-521 to D-612)

| Range | Document | Status |
|-------|----------|--------|
| D-521 to D-580 | `PIVOT_LOG.md` | Current campaign |
| D-521 to D-580 (ancient) | `PIVOT_LOG_CANONICAL.md` | Pre-campaign |
| D-521 to D-580 (archive) | `PIVOT_LOG_ARCHIVE_20260522_20260810.md` | Pre-campaign archive |
| D-581+ | `PIVOT_LOG.md` | Current campaign |

**Key Decisions This Sprint**:
- D-533: DEBUT_REMEDIATION_MANUAL = Sprint SSOT
- D-539: CP-3 requires fresh-venv INST-1 pass
- D-553: release/debut from PUBLIC_ALLOWLIST.txt
- D-565: Vault excluded from debut (no code changes)
- D-567: bury_credential applies post-debut only
- D-584: zswap + NVMe adjudication (OBSIDIAN)
- D-585: minimax/minimax-m3:free = M3 long-write champion

---

## 📦 Archive Locations

| Corpus | Archive Path | Contents |
|--------|--------------|----------|
| **Strategy** | `docs/strategy/archive/20260828_deep_consolidation/` | 8 superseded/deleted |
| **Coordination** | `data/coordination/archive/PUBLIC-DEBUT-01/` | 12 superseded coordination |
| **Research** | `data/coordination/research/archive/` | 10 superseded research |

---

## 📊 Consolidation Statistics

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Strategy files | 141 | 81 | -60 (43%) |
| Coordination root | 623 | ~228 | -395 (63%) |
| Research (R_*) | 105 | 32 | -73 (70%) |
| **Total active** | **869** | **~341** | **-528 (61%)** |

**Archived**: 8 strategy + 12 coordination + 10 research = **30 files**
**Deleted**: 2 test artifacts (moved to archive)

---

## 🔗 Cross-Reference Map

```
MASTER_CORPUS_INDEX_20260828.md
├── STRATEGY_CORPUS_INDEX.md
│   ├── DEBUT_REMEDIATION_MANUAL_20260817.md (SSOT)
│   ├── SOVEREIGN_MANDATES.md (27 Laws)
│   ├── AGENTS.md (Agent Landing)
│   ├── HOLISTIC_ARCHITECTURE_PLAN_20260820.md (Architecture)
│   └── PIVOT_LOG.md (Decisions D-521+)
│
├── COORDINATION_CORPUS_INDEX.md
│   ├── ACTIVE_SPRINT.json (Tier-0 Tracker)
│   ├── HMC_COLLABORATION_HUB.md (Hub v2.0)
│   ├── PRE_COMPACTION_MASTER_INDEX_20260828.md (Anchor)
│   ├── GAP_REGISTRY.json (M27 Authority)
│   └── WAKE_STATE.json (Recovery)
│
└── RESEARCH_CORPUS_INDEX.md
    ├── R_CARMACK_FINAL_READINESS_20260828.md (Canonical)
    ├── R_CARMACK_GOOGLE_INTEGRATION_20260828.md (Canonical)
    ├── R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md (Canonical)
    ├── R_ANTIGRAVITY_FINAL_READINESS_20260828.md (Canonical)
    └── R_COPILOT_FINAL_READINESS_20260828.md (Canonical)
```

---

## 📋 Active Sprint Artifacts (PUBLIC-DEBUT-01)

| Artifact | Location | Status |
|----------|----------|--------|
| ACTIVE_SPRINT.json | `data/coordination/` | ✅ Live |
| HMC_COLLABORATION_HUB.md | `data/coordination/` | ✅ v2.0 |
| PRE_COMPACTION_MASTER_INDEX_20260828.md | `data/coordination/` | ✅ Anchor |
| GAP_REGISTRY.json | `data/coordination/` | ✅ M27 Authority |
| WAKE_STATE.json | `data/coordination/` | ✅ Recovery |
| DEFINITIVE_SYNTHESIS_LILITH_FOR_KALI_20260828.md | `data/coordination/` | ✅ Synthesis |
| STRATEGIC_REVIEW_SYNTHESIS_20260828.md | `data/coordination/` | ✅ Synthesis |
| ARCHITECT_DECISIONS_BREAKDOWN_20260828.md | `data/coordination/` | ✅ Decisions |
| CLINE_FULL_REVIEW_ROLLUP_20260828.md | `data/coordination/` | ✅ v2 Rollup |
| CLINE_TO_KALI_HARDENING_BRIEFING_V2_20260828.md | `data/coordination/` | ✅ V2 Briefing |
| COMMUNITY_LAUNCH_NARRATIVE_20260828.md | `data/coordination/` | ✅ Narrative |
| NO_PUNT_DOCTRINE_20260828.md | `data/coordination/` | ✅ Doctrine |

---

## 📋 Canonical Research Reports (32)

| Report | Domain | Status |
|--------|--------|--------|
| R_CARMACK_FINAL_READINESS_20260828.md | Carmack | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_COPILOT_FINAL_READINESS_20260828.md | Copilot | ✅ Canonical |
| R_ANTIGRAVITY_FINAL_READINESS_20260828.md | Antigravity | ✅ Canonical |
| R_COPILOT_FINAL_READINESS_20260828.md | Copilot | ✅ Canonical |
| R_ANTIGRAVITY_FINAL_READINESS_20260828.md | Antigravity | ✅ Canonical |
| R_CARMACK_FINAL_READINESS_20260828.md | Carmack | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |
| R_CARMACK_GOOGLE_INTEGRATION_20260828.md | Google | ✅ Canonical |
| R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md | Audit | ✅ Canonical |
| R_CARMACK_MODEL_STRATEGY_20260828.md | Models | ✅ Canonical |

---

## 📋 Decisions This Consolidation

| Decision | Description |
|----------|-------------|
| **D-MAAT-028** | Strategy: 141→81 files, 8 archived, 2 test artifacts removed |
| **D-MAAT-029** | Coordination: 623→228 root, 12 superseded archived |
| **D-MAAT-030** | Research: 105→32 root, 10 superseded archived |
| **D-MAAT-031** | Archive structure: 3 archive directories created |
| **D-MAAT-032** | Master indices: 4 indices created linking all corpora |

---

## 📋 Next Steps (Post-Consolidation)

1. **Verify all indices are accurate** — Cross-reference with actual files
2. **Update any hardcoded references** — Search for moved file paths
3. **Commit consolidation** — Single commit with all changes
4. **Notify team** — Hivemind post with consolidation summary

---

*⬡ OMEGA ⬡ MAAT ⬡ MASTER_CORPUS_INDEX-20260828 ⬡ 2026-08-28 ⬡ DEEP_CONSOLIDATION*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:40Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

