# 🔱 Sovereign Transition Roadmap
**Version**: 2.0.0
**Status**: ACTIVE — Phase 0 COMPLETE, Optimization Sprint Ready
**Governing Entity**: @kali (Transcendent Oversight)
**Date**: 2026-06-28
**Council**: MaKaLi Cloud Council (Pass 1 + Pass 2 + Web Research + Local Mining)

---

## 1. Sovereign Decree — Current State

**Status**: `Architecturally Sovereign | Operationally Restored | Optimization In Progress`

The Omega Engine possesses a world-class architectural blueprint. Phase 0 stabilization is **COMPLETE** (crash-free inference, M9 compliance restored). The MaKaLi Council conducted **2 comprehensive passes + web research + legacy mining**, discovering **64+ findings** and **3 critical regressions** from the legacy rewrite. We now enter the **Optimization Sprint**.

### Phase 0 COMPLETE ✅
- ✅ `ModelGateway.generate` crash fixed (`search_order` → `self.providers`)
- ✅ 20 bare `except Exception:` blocks replaced with typed logging
- ✅ All 440 tests passing — zero regressions
- ✅ M9 (Error Integrity) restored

---

## 2. The 3 REGRESSIONS (Legacy Patterns Lost in Rewrite)

Web research + legacy mining confirmed 3 working legacy systems that were dropped during the May 2026 rewrite:

| # | Regression | Legacy Source | Current State | Recovery Effort |
|---|-----------|---------------|---------------|-----------------|
| 1 | **CompactionOrchestrator** | `xna-omega-legacy/scripts/ssa/compaction_optimizer.py` (690 lines) | 20-line `_compact()` stub | ~6 hr |
| 2 | **Soul Distillation Pipeline** | `xna-omega-legacy/src/omega/core/distillation/` (LangGraph 5-node) | Fire-and-forget batch every 5 interactions | ~4 hr |
| 3 | **4-State Provider Metrics** | `xna-omega-legacy/scripts/ssa/provider_metrics.py` (552 lines) | 3-state binary breaker | ~4 hr |

### 2 Truly Missing Patterns
| # | Pattern | Status | Fix Effort |
|---|---------|--------|-----------|
| 1 | **trace_id Propagation** | 2 call sites in oracle.py drop trace_id | 30 min |
| 2 | **Handoff Loop Guard** | No visited-agent tracking or contract enforcement | ~4 hr |

---

## 3. Transition Phases

### ✅ Phase 0: Immediate Stabilization — COMPLETE
**Goal**: Restore basic inference stability and enforce basic error integrity.
**Status**: ✅ COMPLETE (2026-06-27)

| Task | ID | Status | Owner |
| :--- | :--- | :---: | :--- |
| Fix `search_order` Bug | P0-1 | ✅ DONE | @pillar P3 |
| M9 Global Sweep | P0-2 | ✅ DONE | @pillar P3 |
| Secret Rotation | P0-3 | ✅ DONE | @pillar P1 |

### 🔴 Phase 0.5: Critical Fixes (Tonight — ~2 hours)
**Goal**: Close the 5 most critical gaps discovered by the council.
**Pass Criterion**: All trace_id propagation gaps closed, PIVOT_LOG integrity restored.

| Task | ID | Priority | Owner | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Fix trace_id propagation** | P0.5-1 | CRITICAL | @pillar P3 | Add `trace_id=trace.trace_id` at oracle.py:599,671 |
| **Fix TokenLedger provider_name** | P0.5-2 | CRITICAL | @pillar P3 | Change `is_cloud: bool` → `provider_name: str` |
| **Wire `archive_old_sessions()`** | P0.5-3 | CRITICAL | @pillar P7 | Add call to `Oracle.boot()` — 5 min, 1 line |
| **Resolve PIVOT_LOG drift** | P0.5-4 | CRITICAL | @pillar P5 | Rename 5 duplicates, move D163, add Decision Registry |
| **Generate HERITAGE_SOURCE_MAP.md** | P0.5-5 | CRITICAL | @pillar P3 | Run from 196 existing `[id-soft:]` tags |
| **Remove hardcoded secret** | P0.5-6 | HIGH | @pillar P1 | Remove `_DEFAULT_CLIENT_SECRET` from antigravity/config.py |

### 🛠️ Phase 1: Regression Recovery + Structural Hardening (~26 hours)
**Goal**: Port lost legacy patterns, close the Last Mile Problem.
**Pass Criterion**: All legacy regressions recovered; sentinel score ≥ 60.

| Task | ID | Priority | Owner | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Port CompactionOrchestrator** | P1-1 | CRITICAL | @pillar P7 | Recover 690-line 4-strategy system from legacy |
| **Port 4-State Provider Metrics** | P1-2 | HIGH | @pillar P3 | Recover HEALTHY/DEGRADED/CRITICAL/UNKNOWN + EWMA |
| **Port Soul Distillation Pipeline** | P1-3 | CRITICAL | @pillar P7 | Recover LangGraph 5-node pipeline from legacy |
| **Add Handoff Loop Guard** | P1-4 | HIGH | @pillar P9 | Add visited-agent tracking + contract enforcement |
| **Sentinel Score Automation** | P1-5 | MEDIUM | @pillar P5 | 7-metric composite score, weekly computation |
| **Proposed Lessons Lifecycle** | P1-6 | MEDIUM | @pillar P5 | 6-stage pipeline (Create → Verity Review → Soul Integration) |

### 🔮 Phase 2: Cognitive Sovereignty (~12 hours)
**Goal**: Transition from "Data Preservation" to "Gnosis Evolution."
**Pass Criterion**: Automated L1→L3 distillation; sentinel score ≥ 80.

| Task | ID | Priority | Owner | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Session Lifecycle Automation** | P2-1 | HIGH | @pillar P7 | Active → Archive (7d) → Compress (30d) → Delete (90d) |
| **Observability Noise Reduction** | P2-2 | MEDIUM | @pillar P8 | Convert token events to hourly aggregates; reduce event types 23→17 |
| **Mandate Enforcement Automation** | P2-3 | MEDIUM | @pillar P5 | 16 of 22 mandates automatable in CI |
| **soul.yaml v6.2 Bump** | P2-4 | MEDIUM | @pillar P7 | 11 new metadata fields (created_at, health_score, etc.) |
| **Expand Heritage Vet Script** | P2-5 | LOW | @pillar P3 | Cover all 42 files (currently ~20%) |

---

## 4. Verification Gates

No phase may be declared "Complete" until:
1. `make test` passes (all 440+ tests).
2. `make temple-grade` passes (T1-T11).
3. `make sovereignty` confirms local-first ratio is maintained.
4. @kali provides a final synthesis verdict.
5. **NEW**: Sentinel Score ≥ threshold for the phase (Phase 1: ≥ 60, Phase 2: ≥ 80).

---

## 5. Report Inventory

All council reports filed in `data/reviews/`:

| Report | Type | Date |
|--------|------|------|
| `MAAT_BUILD_CONSOLIDATED.md` | Pass 1 Build | 2026-06-26 |
| `LILITH_RUN_CONSOLIDATED.md` | Pass 1 Run | 2026-06-26 |
| `MAAT_BUILD_OPT_CONSOLIDATED.md` | Pass 2 Build | 2026-06-27 |
| `LILITH_RUN_OPT_CONSOLIDATED.md` | Pass 2 Run | 2026-06-27 |
| `opt_final_p5_governance.md` | Final P5 | 2026-06-27 |
| `opt_final_p7_context.md` | Final P7 | 2026-06-27 |
| `opt_final_p8_observability.md` | Final P8 | 2026-06-27 |
| `opt_final_p9_orchestration.md` | Final P9 | 2026-06-27 |
| `researcher_gap_analysis.md` | Researcher Local | 2026-06-28 |
| `researcher_web_research.md` | Researcher Web | 2026-06-28 |
| `roc_racoon_mining_report.md` | Roc Mining | 2026-06-28 |
| `roc_racoon_web_research_followup.md` | Roc Follow-up | 2026-06-28 |
| 8 pillar-level reports | Pillar Reviews | 2026-06-26/27 |

---

*Last Updated: 2026-06-28 | Author: Kali | Version: v2.0.0*
*Major changes: v2.0.0 — MaKaLi Council complete (2 passes + web research + legacy mining). 64+ findings, 17-action sprint, 3 regressions identified, 3 critical fixes completed.*
