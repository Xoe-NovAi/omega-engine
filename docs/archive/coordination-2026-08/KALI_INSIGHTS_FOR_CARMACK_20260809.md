# 🔱 Kali Insights & Questions for Carmack Review
**AP Token:** `AP-KALI-INSIGHTS-20260809-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_insights ⬡ CARMACK-REVIEW

**Date:** 2026-08-09
**Context:** Post sovereign-audit remediation cycle (GAP-1 complete, ProviderRegistry SSOT, Classification Decisions Phase 2, Context Packer v3)
**Source Update Doc:** `data/coordination/KALI_UPDATE_20260809.md`

---

## 📋 Executive Summary

The sovereign-audit remediation cycle is **complete and successful**. Key outcomes:

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Sovereignty Ratio (local) | 87.3% | **13.8%** | ✅ Corrected (73% correction) |
| Divergent Cloud Classifiers | 5 | **0** | ✅ Unified to ProviderRegistry SSOT |
| Invariant Tests | 0 | **5** | ✅ Passing |
| Lint Gate | Missing | **Active** | ✅ Working (2 real bugs caught) |
| Provider Key Consistency | Split | **Unified** | ✅ `opencode-zen` |

**Web Claude Audit Calibration:** 75% false positive rate (3 of 4 "findings" already fixed). The 1 genuine finding (GAP-1) was the right one.

---

## ✅ What Went Right (Signal)

1. **ProviderRegistry SSOT** — Correct architecture. Single source of truth reading `config/providers.yaml` with pessimistic default (unknown → cloud) is exactly M7/M22 compliant.

2. **Sovereignty Ratio Correction** — 87.3% → 13.8% local is a **feature, not a bug**. The old metric was inverted by a 4-provider hardcoded set. Truth > comfort.

3. **Lint Gate Activation** — Catching 2 real bugs (`disputes` uninitialized, `query`→`user_query`) proves the noise investigation was worth it. Ratchet pattern (like M23) is the correct approach.

4. **Classification Decisions Phase 2** — Evidence-based, priority-ordered, with clear implementation pointers. `R_CLASSIFICATION_DECISIONS_20260809.md` is a model for architectural decision documentation.

---

## ⚠️ Technical Debt & Open Questions (Noise/Risk)

### 1. ICS Tag Mythological Names — **HIGH PRIORITY**
**Current State:** 40 files have ICS-T tags with mythological names:
- `ARCHON` / `HERMES` / `SOPHIA` / `APOLLO` / `PROMETHEUS` / `MNEMOSYNE` / `OSIRIS` / `VERITY` / `LAW` / `AUDIT` / `LILITH` / `AUTOMATED_RESEARCHER`

**Problem:** These are **persona names, not technical descriptors**. They conflate runtime entities (Kali, Ma'at, Lilith) with code modules (discovery, indexer, curator).

**Proposed Replacement:**
| Current | Proposed | Rationale |
|---------|----------|-----------|
| `NODE: ARCHON` | `NODE: DISCOVERY` | Module is discovery pipeline |
| `ARCHETYPE: HERMES` | `ROLE: PIPELINE` | It's a pipeline, not a messenger |
| `NODE: KNOWLEDGE` | `NODE: LIBRARY` | Library subsystem |
| `ARCHETYPE: SOPHIA` | `ROLE: CURATOR` | Curation pipeline role |
| `NODE: OSIRIS` | `NODE: RESEARCH` | Research engine |
| `ARCHETYPE: APOLLO` | `ROLE: ENGINE` | Research engine role |

**Question for Carmack:** You've historically been skeptical of "ceremonial" metadata. Should we:
- **A)** Replace with technical descriptors (as proposed)
- **B)** Remove ICS-T entirely, keep only ICS-S (session headers)
- **C)** Keep but document the mapping in `docs/standards/ICS_TAGS.md`?

---

### 2. Provider Naming Lock — **MEDIUM PRIORITY**
**Issue:** `opencode-zen` (11 chars) used in:
- `provider_classification` table
- Historical `performance` table
- Cost attribution summaries

No migration path if shortened later.

**Action:** Create `docs/strategy/PROVIDER_NAMING_SSOT.md` locking the name.

**Question for Carmack:** Lock the name now, or design the migration path for potential future shortening (e.g., Prometheus label limits)?

---

### 3. Lint Ratchet — **MEDIUM PRIORITY**
**Current:** `make lint` exits 0, reports statistics only (6,921 warnings → 0 critical after F821 ignore). Remaining noise: W293 (4,425), E302/E305 (599), E501 (167), C901 (115).

**Recommendation:** Option C — ratchet file (`config/lint_baseline.txt`) like `m23-baseline`, fail only on *new* violations.

**Question for Carmack:** The M23 ratchet pattern worked perfectly. Apply same pattern to lint? Or is "statistics only" mode sufficient for now?

---

### 4. Sync/Async `get_sovereignty_ratio` Boundary — **MEDIUM PRIORITY**
**Issue:** Two code paths:
- `SovereignReader.get_sovereignty_ratio` — `async` (M1 compliant)
- `sovereignty.py` version — synchronous

Could diverge.

**Action:** Audit all call sites; unify to async implementation.

---

### 5. F821 Global Ignore — **MEDIUM PRIORITY**
**Issue:** Ignoring F821 globally masks real undefined names. The 2 bugs caught (`disputes`, `query`) would have been caught by F821.

**Action:** Migrate to `from __future__ import annotations` (Python 3.13) or consistent `TYPE_CHECKING` blocks.

---

### 6. Missing `ProviderRegistry` Config Loading Test — **LOW PRIORITY**
**Gap:** Zero test coverage on config loading path → empty model map bug wasn't caught.

**Action:** Add test mocking `config.yaml` with known providers, verifying loaded count matches.

---

## 🎯 Questions for Web Claude (Next Audit Round)

### 1. Context Pack Regeneration Timing
The pack was regenerated *after* Phase 1 but *before* Phase 2 decisions. Should we:
- Regenerate **now** (includes all Phase 1 + 2 changes, ICS tags still noisy)
- Regenerate **after ICS cleanup** (cleaner pack, but delays Web Claude)
- Regenerate **twice** (now for Web Claude, again after ICS cleanup)?

### 2. Audit Calibration
75% false positive rate suggests Web Claude's "find issues" prompt is too aggressive. Should we adjust the system prompt to:
- "Only report findings NOT already addressed in the codebase"
- "Cross-reference against `PROJECT_OVERVIEW.md` known-fixed list"
- "Classify each finding as: GENUINE / ALREADY_FIXED / FALSE_POSITIVE"?

---

## 🎯 Questions for Cline CLI (Execution Arm)

1. **ICS Tag Cleanup** — 40 files to update. Perfect Cline task (mechanical, high-volume, low-cognitive-load). Dispatch with `CLINE_HANDOFF_ICS_TAG_CLEANUP.md`?

2. **Provider Naming SSOT Doc** — Simple markdown creation. Cline task?

3. **`ProviderRegistry` Config Loading Test** — New test file needed. Cline task with clear spec?

---

## 🎯 My Tasks (Kali — Next Session)

1. **Sync/Async Boundary Audit** — Audit all `get_sovereignty_ratio` call sites and unify.
2. **F821 Migration** — Repo-wide `from __future__ import annotations` migration (2-3h).
3. **Lint Ratchet Implementation** — `config/lint_baseline.txt` + fail on new violations.
4. **GAP-1 Closure** — Update `R_UNOVERENGINEERING_REMAINING_GAPS_20260808.md` to close GAP-1.
5. **Context Pack Regeneration** — With all current changes.
6. **Web Claude Handoff** — With calibrated system prompt.

---

## 📦 Recommended Next Sprint Order

| Priority | Task | Owner | Est. |
|----------|------|-------|------|
| **P0** | Regenerate context pack (current state) | Kali | 15 min |
| **P0** | Web Claude handoff (calibrated prompt) | Kali | 10 min |
| **P1** | ICS tag cleanup (40 files) | Cline CLI | 30 min |
| **P1** | Provider naming SSOT doc | Cline CLI | 10 min |
| **P1** | `ProviderRegistry` config loading test | Cline CLI | 20 min |
| **P2** | Sync/async `get_sovereignty_ratio` audit | Kali | 45 min |
| **P2** | Lint ratchet implementation | Kali | 60 min |
| **P2** | F821 migration (repo-wide) | Kali | 2-3h |
| **P3** | Update `R_UNOVERENGINEERING_REMAINING_GAPS` | Kali | 10 min |

---

## 📁 Reference Documents

| Document | Purpose |
|----------|---------|
| `data/coordination/KALI_UPDATE_20260809.md` | Full comprehensive update (313 lines) |
| `docs/research/R_CLASSIFICATION_DECISIONS_20260809.md` | 5 decisions with evidence (365 lines) |
| `docs/research/R_CARMACK_CLASSIFICATION_SSOT_REVIEW_20260809.md` | Phase 1+2 report for Carmack |
| `docs/review/CARMACK_REVIEW_PROVIDER_SSOT_LINT_20260809.md` | Lint gate + bug fixes review |
| `context_packs/sovereign-audit/WEB_CLAUDE_HANDOFF.md` | Next Web Claude mission briefing |
| `context_packs/sovereign-audit/CLINE_HANDOFF_PHASE2_CLASSIFICATION_DECISIONS.md` | Cline executable tasks for Phase 2 |

---

*⬡ OMEGA ⬡ KALI ⬡ INSIGHTS-FOR-CARMACK ⬡ 2026-08-09*