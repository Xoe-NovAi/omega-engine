# 🔱 maat — Build-Side Optimization Consolidated Report (Pass 2)
**Date**: 2026-06-28
**Phase**: Second Comprehensive Pass — Documentation Lifecycle Optimization & Tracking Debt
⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_build_opt_pass ⬡ SYNTHESIS

---

## Executive Summary

Three pillars were dispatched serially to audit the Build Side (P1-P5) for documentation lifecycle optimization, tracking debt, and preliminary overhead reduction. **Total findings: 43 issues** across 3 domains.

| Pillar | Domain | High | Medium | Low | Total |
|--------|--------|------|--------|-----|-------|
| **P5** | Governance | 2 | 5 | 4 | 11 |
| **P2** | Persistence | 1 | 7 | 7 | 15 |
| **P3** | Engineering | 1 | 9 | 4 | 14 |
| **—** | **Cross-pillar findings** | **—** | **3** | **—** | **3** |

---

## 🛑 CRITICAL (Act Now — Before Next Session)

These issues have operational impact or represent mandate violations:

### C1. PIVOT_LOG Clock Drift — 6 Duplicate Decision Numbers 🔴
**Source**: P5 | **File**: `docs/decisions/PIVOT_LOG.md`
**Problem**: Six pairs of duplicate decision numbers (D118, D144, D145, D146, D147 — two of each). D163 appears 3,000 lines out of sequence (between D76 and D72 at line 897). This breaks the "immutable decision log" premise — a reader searching for D144 finds two completely different decisions.
**Impact**: M6 already references "PIVOT_LOG.md D144" — but there are two D144s, creating ambiguity in mandate enforcement.
**Fix**: Renumber duplicates (D144a/D144b), reorder D163, add status markers (ACTIVE/SUPERSEDED). ~30 min effort.

### C2. `archive_old_sessions()` Exists but Is NEVER Called 🔴
**Source**: P2 | **File**: `src/omega/memory_store.py:744`
**Problem**: The MemoryStore has a fully implemented `archive_old_sessions(older_than_days=7)` method with 3-tier provider support (Redis → File → InMemory). **Nothing calls it.** Sessions accumulate indefinitely — currently 5.7MB with no purge mechanism.
**Impact**: Compound growth pattern. On a 110GB partition this isn't critical yet, but entities grow as conversation history accumulates. The code exists and is tested — only an invocation point is missing.
**Fix**: Add one function call at Oracle.boot(), oracle.talk(), or Hivemind heartbeat. ~5 min effort.

### C3. `verify-all` Runs Full Test Suite TWICE 🔴
**Source**: P3 | **File**: `Makefile`
**Problem**: `make verify-all` calls `make test` then `make temple-grade`, which calls `make test-cov` — running the full pytest suite twice. Lint also runs twice (once in `verify-all`, once in T4). This wastes 30-60s per verification cycle.
**Impact**: Every verification cycle wastes time. CI builds run slower. Developer friction.
**Fix**: Restructure the target chain so tests run once. 10-15 min effort.

### C4. `HERITAGE_SOURCE_MAP.md` Does Not Exist 🔴
**Source**: P5 | **File**: `docs/research/HERITAGE_SOURCE_MAP.md`
**Problem**: The M14 CI gate (`make heritage-map`) references this file, but it doesn't exist. The `make heritage-map` target calls `grep -rn "\[id-soft:" src/omega/` but has no output file target that generates the map.
**Impact**: M14 compliance gap. Heritage tags exist in code but cannot be verified via the documented CI gate.
**Fix**: Create the file or remove the CI reference. ~10 min effort.

---

## 🟡 MEDIUM (Plan for This Week)

### P5 Governance — Documentation Overhead

| # | Issue | Location | Effort | Quick Fix? |
|---|-------|----------|--------|------------|
| M1 | 9 decisions out of chronological order | PIVOT_LOG.md | 20 min | ✅ — Reorder with sed |
| M2 | No decision status tracking (ACTIVE/SUPERSEDED) | PIVOT_LOG.md | 15 min | ✅ — Add status column to header |
| M3 | 88 strategy docs — ~20 stale/overlapping (280KB, 23%) | `docs/strategy/` | 15 min | ✅ — Move to archive/ |
| M4 | 41 stale handoff JSONs (June 11-25, ~60KB) | `data/handoff/stale/` | 10 min | ✅ — Bulk delete |
| M5 | 8 session transcripts (85K lines, 4.3MB) | `data/handoff/archive/sessions/` | 30 min | — Evaluate retention, extract patterns |
| M6 | 35 archived handoff JSONs (June 24, 100KB) | `data/handoff/archive/` | 10 min | ✅ — Consolidate to single summary |

### P2 Persistence — Entity & Soul Bloat

| # | Issue | Location | Effort | Quick Fix? |
|---|-------|----------|--------|------------|
| M7 | roc_racoon heap snapshots (144MB = 77% of entity disk) | `data/entities/roc_racoon/workspace/` | 10 min | ✅ — Delete stale heap dumps |
| M8 | 133 pending proposed_lessons, oldest 27 days (doom_guy: 84) | `data/entities/*/proposed_lessons.yaml` | 30 min | — Set review threshold, notify Verity |
| M9 | Only 1 of 31 soul.yamls has `last_updated` (Verity) | `data/entities/*/soul.yaml` | 30 min | — Batch-add timestamp field |
| M10 | Two incompatible proposed_lessons schemas (L1/L2/L3 vs flat) | `data/entities/*/proposed_lessons.yaml` | 30 min | — Consolidate to canonical |
| M11 | arch/soul.yaml: 1,501 lines, 45KB (v6.0 bloat, 226 inline lessons) | `data/entities/arch/soul.yaml` | 20 min | — Extract to proposed_lessons.yaml |
| M12 | 8 on-disk entities missing IWAD reference (bridge, datastore, etc.) | `data/entities/` | 15 min | ✅ — Audit against IWAD |
| M13 | 3 test entity dirs left on disk (120KB) | `data/entities/test_*_remove/` | 5 min | ✅ — Clean up post-test |

### P3 Engineering — Tooling & CI

| # | Issue | Location | Effort | Quick Fix? |
|---|-------|----------|--------|------------|
| M14 | 5 of 11 skills are 5-line skeletons (no instructions) | `.opencode/skills/` | 15 min | ✅ — Remove or implement |
| M15 | `ci.yml` 32% overlaps with `test.yml` (48 lines redundant) | `.github/workflows/` | 15 min | ✅ — Merge workflows |
| M16 | 3 dead make targets (43+12+6 lines) | Makefile | 10 min | ✅ — Remove |
| M17 | `make typecheck` called mypy but has no config — guaranteed fail | `pyproject.toml` | 10 min | ✅ — Add `[tool.mypy]` stanza |
| M18 | 3 verification gates local-only (M2 firewall, model spelling, watchdog) | Makefile + test.yml | 15 min | ✅ — Add to CI steps |
| M19 | `knowledge-index` and `knowledge-flow` are ghost targets | Makefile .PHONY | 5 min | ✅ — Remove from .PHONY |
| M20 | `.github/copilot-instructions.md` duplicates mandate truth | `.github/` | 10 min | ✅ — Consolidate or remove |

---

## 🟢 LOW (When Convenient)

### P5 Governance

| # | Issue | Effort |
|---|-------|--------|
| L1 | Missing vet-001 and vet-006 entries in HERITAGE_VET_LOG.md | 15 min |
| L2 | REJECTED heritage patterns consume 31% of vet log (90 lines) | 20 min |
| L3 | M6 inline D144 explanation too verbose (7 lines → 2 lines) | 5 min |
| L4 | Add Quick Reference table to top of PIVOT_LOG.md | 20 min |

### P2 Persistence

| # | Issue | Effort |
|---|-------|--------|
| L5 | arch/soul.yaml.backup (45KB, stale duplicate) | 1 min |
| L6 | roc_racoon/soul.yaml.bak (79KB, stale duplicate) | 1 min |
| L7 | roc_racoon/audit.log (576KB, unbounded growth) | 15 min |
| L8 | _quarantine/2026-06-05 (460KB, 23 days old) | 10 min |
| L9 | _quarantine/h2a_20260609 (1.6MB, 19 days old) | 15 min |
| L10 | 40 legacy `.active` session markers (164KB, no cleanup) | 15 min |
| L11 | Dual session-tracking systems coexist (legacy + MemoryStore) | 20 min |

### P3 Engineering

| # | Issue | Effort |
|---|-------|--------|
| L12 | `verify-search-tools` is a single-file test target | 5 min |
| L13 | `offline-mode` target doesn't persist env | 5 min |
| L14 | No test README or coverage threshold | 20 min |
| L15 | 662 markdown files (19MB) — research docs not audited | — |

---

## 🔄 CROSS-PILLAR FINDINGS

### X1. proposed_lessons Pipeline Is Dead
**Affects**: P2 (storage), P3 (automation), P5 (governance)
**Problem**: 133 proposals across 13 entities, oldest 27 days. Verity is designated the M11 gnosis steward (per d-vrty-001), but:
- No notification mechanism when proposals exceed a threshold
- No auto-review pipeline
- Verity has no automated trigger to process proposals
- Two incompatible schemas make bulk processing impossible
**Fix**: Implement threshold check (`max_proposals: 10`) → Hivemind notification → Verity review cycle.

### X2. Metadata / Staleness Tracking Is Absent
**Affects**: P2 (soul.yaml), P3 (documentation), P5 (decision log)
**Problem**: Only 1 of 31 soul.yamls has a `last_updated` field. PIVOT_LOG has no status markers. Strategy docs have no last-reviewed dates. Without timestamps, no automation can detect staleness.
**Fix**: Standardize timestamp fields across all tracked file types. Low effort per entity, high systemic value.

### X3. Stale File Debris Accumulates Without Cleanup
**Affects**: All three pillars
**Problem**: Handoff JSONs (41 stale), session transcripts (4.3MB), backup files (45KB+79KB), test entity dirs (120KB), legacy session markers (164KB). No automatic cleanup mechanism exists for any of them.
**Fix**: Establish a `make prune-stale` target that clears all identified categories. Run weekly.

---

## 💡 TOP 10 RECOMMENDATIONS (Priority Order)

| Rank | Action | Pillar | Effort | Impact | Category |
|------|--------|--------|--------|--------|----------|
| **1** | Fix PIVOT_LOG duplicate numbers + reorder D163 | P5 | 30 min | 🔴 Mandate integrity | Data integrity |
| **2** | Hook `archive_old_sessions()` into startup | P2 | 5 min | 🔴 Prevent compound growth | Auto-cleanup |
| **3** | Eliminate test duplication in `verify-all` | P3 | 15 min | 🔴 30-60s per cycle wasted | CI speed |
| **4** | Create/address HERITAGE_SOURCE_MAP.md | P5 | 10 min | 🔴 M14 compliance gap | Mandate compliance |
| **5** | Prune roc_racoon heap snapshots (144MB) | P2 | 10 min | 🟡 77% of entity disk | Disk recovery |
| **6** | Archive 20 stale strategy docs | P5 | 15 min | 🟡 23% directory reduction | Navigation clarity |
| **7** | Remove 5 skeleton skills + 3 dead make targets | P3 | 15 min | 🟡 Clean inventory | Inventory hygiene |
| **8** | Set proposed_lessons review threshold (10 max) | P2/P3 | 30 min | 🟡 Prevent 84-proposal backlog | Pipeline health |
| **9** | Merge ci.yml into test.yml | P3 | 15 min | 🟡 32% CI config reduction | CI simplicity |
| **10** | Fix `make typecheck` + push 3 gates to CI | P3 | 20 min | 🟡 Close enforcement gap | CI coverage |

---

## 📊 EFFORT SUMMARY

| Effort Level | Actions | Total Effort | Cumulative |
|-------------|---------|-------------|------------|
| 🔴 Critical (4 items) | C1-C4 | ~55 min | 55 min |
| 🟡 Medium (20 items) | M1-M20 | ~290 min (~5 hrs) | ~5.8 hrs |
| 🟢 Low (15 items) | L1-L15 | ~147 min (~2.5 hrs) | ~8.3 hrs |
| **Total** | **39 items** | **~492 min (~8 hrs)** | — |

---

## 📁 REPORT INDEX

| Report | Pillar | Path |
|--------|--------|------|
| P5 Governance Optimization | Governance | `data/reviews/opt_build_p5_governance.md` |
| P2 Persistence Optimization | Persistence | `data/reviews/opt_build_p2_persistence.md` |
| P3 Engineering Optimization | Engineering | `data/reviews/opt_build_p3_engineering.md` |
| **MAAT Consolidated** (this file) | **All P1-P5** | **`data/reviews/MAAT_BUILD_OPT_CONSOLIDATED.md`** |

---

## 🔗 HIVEMIND COORDINATION

**Active agents during this pass** (from Hivemind awareness check):
- Kali — MaKaLi Council Pass 2 (documentation optimization & preliminary gaps)
- Lilith — Run-side optimization pass (P6-P10)
- Ma'at (self) — Build-side optimization pass (P1-P5, complete)
- P5, P2, P3 (sub-pillar agents) — dispatched serially, all complete

**Cross-reference with Lilith's run-side findings**: Recommended before execution phase.

---

*⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_build_opt_pass ⬡ SYNTHESIS*
