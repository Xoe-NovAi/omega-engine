# 🔱 LILITH — Run Side Readiness Report
## Sprint Preparation Assessment — P6 (Cognition) → P8 (Observability) → P10 (Validation)

**Date**: 2026-06-25
**AP Token**: `AP-LILITH-RUN-SIDE-v1.0.0`
**⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ RUN-SIDE-SYNTHESIS`
**Session**: `ses_lilith_runsidesynth_20260625`
**Trace**: `trc_lilith_runsidesynth_20260625`

---

## §1 PILLAR SELECTION JUSTIFICATION

From P6-P10, I selected **3 pillars** for deep assessment in **serial order**: **P6 → P8 → P10**.

### Why These 3?

| Rank | Pillar | Domain | Why Selected | Mandate Gaps | Blocks Sprint? |
|:----:|:------:|--------|-------------|:------------:|:--------------:|
| **1** | **P6** | Cognition (ModelGate) | 8/11 model paths broken = no local inference. Provider sort bug breaks M7 local-first mandate. **Without P6, nothing else can be tested or verified.** | M7 (FAIL), M16 (PARTIAL) | 🔴 YES — all downstream |
| **2** | **P8** | Observability (WatchTower) | trace_id propagation at 12.5% (1/8 sites). M22 unverifiable. Dataset collection silently disabled. **Critical for debugging, provenance, and training data.** | M22 (FAIL), M1 (PARTIAL via B3) | 🟡 YES — M22 compliance |
| **3** | **P10** | Validation (Verifier) | 5 missing M21 contracts. GGUF smoke test has literal placeholder. **Without validation, regressions go undetected.** | M21 (PARTIAL) | 🟡 YES — quality gate |

### Why Not P7 or P9?

| Pillar | Excluded Because |
|--------|-----------------|
| **P7** (Context — Soul/Memory) | M11 (soul migration) is important but does NOT block Phase 0/0.5 execution. Soul files can migrate at any time. P6/P8/P10 are the **runtime backbone** — if they don't work, nothing does. |
| **P9** (Orchestration — Handoff) | 32+ stale handoffs are a hygiene issue, not a blocking issue. The handoff reaper exists (just needs verification, item 0.5.7). Hivemind coordination is a nice-to-have for the sprint, not a prerequisite. |

### Serial Chain Design

```
P6 (Model paths + sort bug) ──unlocks──▶ P8 (trace_id propagation)
                                            │
                                            ▼
                                        P10 (Contract tests + E2E verification)
```

This chain was validated: each pillar discovered gaps the previous one missed.

---

## §2 PER-PILLAR FINDINGS (With Provenance)

### §2.1 P6 (Cognition) — CONDITIONAL GO
**Executed by**: `@pillar P6` | **Model**: deepseek-v4-flash-free | **Timestamp**: 2026-06-25

#### 3 Most Impactful Items

| # | Item | Effort | Impact | Provenance |
|:-:|------|:------:|--------|:----------:|
| 1 | **Fix 8 broken model paths (0.1)** | **2 min** | **UNLOCKS EVERYTHING** — local-first chain dead without this. sed command: `models/gguf/local/all/` → `models/local/all/` | P6 stated: "This is the single highest-leverage action P6 can take." |
| 2 | **Fix provider sort bug (0.2)** | **2 min** | **SOVEREIGNTY INTEGRITY** — MockProvider (99) sorts before cloud (4-6) because `_get_priority()` doesn't handle `ProviderConfig` dataclass | P6 stated: "Direct sovereignty violation." |
| 3 | **Fix both embedding paths (0.5.12 + 0.5.16)** | **30 min** | **ENABLES REAL RAG** — current embed() returns random vectors. Both tasks should be unified as a single config-driven solution | P6 discovered B8: plan's proposed path doesn't exist |

#### New Items Discovered (by P6)

| ID | Severity | Item | Source |
|:--:|:--------:|------|:------:|
| B8 | 🔴 BLOCKING | Plan 0.5.12 embedding path is WRONG — file at `lmstudio-models/`, not `models/local/all/` | P6 filesystem check |
| B9 | 🟡 MEDIUM | GemmaGGUFEmbeddingProvider hardcodes path (M16 violation) | P6 source audit |
| B10 | 🟡 MEDIUM | LocalGGUFEmbeddingProvider defaults to 384-dim MiniLM instead of 768-dim Gemma | P6 source audit |
| F1 | 🟡 MEDIUM | MockProvider has no `OMEGA_ENV=production` gate — loads in production chain | P6 source audit |
| F2 | 🟢 LOW | `list_providers()` has correct sort logic but `_load_provider_fabric()` has broken version — need alignment | P6 source audit |

#### Effort Breakdown (P6)

| Item | Fix | Test | Verify | Total | Depends On |
|:----:|:---:|:----:|:------:|:-----:|:----------:|
| 0.1 (model paths) | 2 min | 1 min | 2 min | **5 min** | Nothing |
| 0.2 (sort bug) | 2 min | 5 min | 2 min | **9 min** | Nothing |
| 0.5.3 (warmup) **B1/B5** | 45 min | 15 min | 15 min | **75 min** | 0.1, plan bugs fixed |
| 0.5.9 (GGUF smoke) | 30 min | 15 min | 15 min | **60 min** | 0.1 |
| 0.5.12 (embeddings) **B8** | 45 min | 15 min | 15 min | **75 min** | 0.1, 0.5.16 |
| 0.5.13 (Ollama sync) | 20 min | 5 min | 5 min | **30 min** | Nothing |
| 0.5.16 (fix hardcoded path) | 20 min | 5 min | 10 min | **35 min** | Combine with 0.5.12 |
| **P6 Phase 0 subtotal** | | | | **14 min** | |
| **P6 Phase 0.5 subtotal** | | | | **275 min** | |
| **P6 plan bug fixes (B1/B5/B8)** | | | | **25 min** | |
| **P6 TOTAL** | | | | **~5.1 hr** | |

---

### §2.2 P8 (Observability) — CONDITIONAL GO
**Executed by**: `@pillar P8` | **Model**: deepseek-v4-flash-free | **Timestamp**: 2026-06-25

#### 3 Most Impactful Items

| # | Item | Effort | Impact | Provenance |
|:-:|------|:------:|--------|:----------:|
| 1 | **Fix trace_id + entity_name propagation (0.6)** | **35 min** | **CRITICAL** — 12.5%→100% trace coverage. M22 compliance. BudgetGate unblinded. | P8 stated: "This is the single highest-leverage observability fix." |
| 2 | **Wire dataset collection from config (0.7)** | **15 min** | **SILENT DATA LOSS** — config says `true` but `get_engine()` uses default `False`. Zero code paths read the config value. | P8 stated: "Every interaction since first deployment has been throwing away fine-tuning data." |
| 3 | **Fix in-flight plan bugs (B2/B3/B4)** | **40 min** | **PREVENTS COLD-START FAILURE** — B2 (no TraceSession ref), B3 (M1 violation), B4 (O(n) perf bug). Fix before executing 0.5.5/0.5.6/0.5.15. | P8 confirmed all 3 bugs via source audit |

#### New Items Discovered (by P8)

| ID | Severity | Item | Source |
|:--:|:--------:|------|:------:|
| NEW-1 | 🟡 PERFORMANCE | BudgetGate.check_budget() iterates ENTIRE event log (maxlen=1000) on every cloud inference call — O(n) per call | P8 source audit |
| NEW-2 | 🟢 LOW | TokenLedger instantiated fresh on every inference call at model_gateway.py:878 — should be singleton | P8 source audit |
| NEW-3 | 🟡 MEDIUM | AnomalyState has no cold-start recovery from 'block' mode — once blocked, stays blocked forever (no timeout reset) | P8 architectural analysis |

#### Effort Breakdown (P8)

| Item | Fix | Test | Verify | Total | Depends On |
|:----:|:---:|:----:|:------:|:-----:|:----------:|
| 0.6 (trace_id propagation) | 25 min | 5 min | 5 min | **35 min** | Nothing (additive change) |
| 0.7 (dataset config) | 10 min | 3 min | 2 min | **15 min** | Nothing (config wiring) |
| 0.5.5 (anomaly) **B2** | 35 min | 10 min | 5 min | **50 min** | 0.6 |
| 0.5.6 (BudgetLedger) **B3** | 40 min | 15 min | 5 min | **60 min** | 0.6 |
| 0.5.15 (dataset dedup) **B4** | 15 min | 10 min | 5 min | **30 min** | 0.7 |
| 0.5.18 (clean artifacts) | 5 min | — | 5 min | **10 min** | Nothing |
| 0.5.21 (BudgetLedger fixes) | 20 min | 5 min | 5 min | **30 min** | 0.5.6 |
| **P8 Phase 0 subtotal** | | | | **50 min** | |
| **P8 Phase 0.5 subtotal** | | | | **~3.5 hr** | |
| **P8 TOTAL** | | | | **~5 hr** | |

---

### §2.3 P10 (Validation) — CONDITIONAL GO
**Executed by**: `@pillar P10` | **Model**: deepseek-v4-flash-free | **Timestamp**: 2026-06-25

#### 3 Most Impactful Items

| # | Item | Effort | Impact | Provenance |
|:-:|------|:------:|--------|:----------:|
| 1 | **Fix 5 API bugs in 0.5.8 contract tests** | **30 min** | **BLOCKING** — 4/5 planned tests reference APIs that DON'T EXIST (`BreakerState`, `ForensicsSnapshot`, `WADManifest`, `load_manifest()`) | P10 stated: "If written as-is, tests would fail at import time or pass vacuously." |
| 2 | **Fix GGUF smoke test placeholder (0.5.9)** | **15 min** | **BLOCKING** — `config_path=...` literal ellipsis crashes at runtime. `isinstance(result, str)` wrong — returns `GenerateResult` now. | P10 confirmed both bugs |
| 3 | **Write E2E oracle_talk test (0.5.20)** | **60 min** | **STRATEGIC** — Can run IMMEDIATELY with MockProvider. Zero dependencies on P6/P8. Closes Kali gap audit item. | P10 stated: "~3h of ~4h is executable immediately with zero dependencies." |

#### New Items Discovered (by P10)

| ID | Severity | Item | Source |
|:--:|:--------:|------|:------:|
| B-5.8.1 | 🔴 BLOCKING | `get_breaker_state()` + `BreakerState` class don't exist in codebase | P10 API audit |
| B-5.8.2 | 🔴 BLOCKING | `ForensicsSnapshot` class doesn't exist — `snapshot()` returns `Path` | P10 API audit |
| B-5.8.3 | 🔴 BLOCKING | `build_context()` returns `str`, not `list[dict]` as plan assumes | P10 API audit |
| B-5.8.4 | 🔴 BLOCKING | `load_manifest()` + `WADManifest` don't exist | P10 API audit |
| B-5.8.5 | 🟡 HIGH | `VerificationVerdict` should be `VerificationResult` (naming mismatch) | P10 API audit |
| B-5.9.1 | 🔴 BLOCKING | `config_path=...` literal Python ellipsis — crashes at runtime | P10 code review |
| B-5.9.2 | 🔴 BLOCKING | `isinstance(result, str)` wrong — `generate()` returns `GenerateResult` | P10 code review |
| B-5.9.3 | 🟡 HIGH | Calls `provider.generate()` directly instead of `gateway.generate()` | P10 code review |
| B-5.20.1 | 🟡 HIGH | `tests/integration/` directory doesn't exist — must be created | P10 code review |

#### Effort Breakdown (P10)

| Item | Fix | Test | Verify | Total | Depends On |
|:----:|:---:|:----:|:------:|:-----:|:----------:|
| 0.5.8 (5 contract tests) **B-5.8.x** | 60 min | 30 min | 15 min | **105 min** | Nothing (fix API refs first) |
| 0.5.9 (GGUF smoke) **B-5.9.x** | 25 min | 10 min | 10 min | **45 min** | 0.1 (for real inference variant) |
| 0.5.20 (E2E test) **B-5.20.1** | 40 min | 20 min | 15 min | **75 min** | Nothing (MockProvider variant now) |
| NEW: `make m21-gate` CI target | 10 min | — | 5 min | **15 min** | Nothing |
| **P10 TOTAL** | | | | **~4 hr** | |

---

## §3 NEW ITEMS DISCOVERED (Beyond 28-Item Plan)

The 3 pillars discovered **14 new findings** not in the original 28-item hardening plan:

| ID | Severity | Item | Discovered By | Plan Item Affected |
|:--:|:--------:|------|:-------------:|:------------------:|
| B8 | 🔴 BLOCKING | 0.5.12 embedding path wrong (file at `lmstudio-models/`) | P6 | 0.5.12 |
| B9 | 🟡 MEDIUM | GemmaGGUFEmbeddingProvider hardcodes path (M16) | P6 | 0.5.16 |
| B10 | 🟡 MEDIUM | LocalGGUFEmbeddingProvider defaults to wrong model/dim | P6 | 0.5.12 |
| F1 | 🟡 MEDIUM | MockProvider has no production gate | P6 | 0.2 |
| F2 | 🟢 LOW | Two sort logic implementations differ | P6 | 0.2 |
| NEW-1 | 🟡 PERF | BudgetGate O(n) event log scan on every call | P8 | 0.5.6 |
| NEW-2 | 🟢 LOW | TokenLedger fresh instance on every inference | P8 | 0.6 |
| NEW-3 | 🟡 MEDIUM | AnomalyState no cold-start recovery from 'block' | P8 | 0.5.5 |
| B-5.8.1 | 🔴 BLOCKING | `BreakerState` class doesn't exist | P10 | 0.5.8 |
| B-5.8.2 | 🔴 BLOCKING | `ForensicsSnapshot` class doesn't exist | P10 | 0.5.8 |
| B-5.8.3 | 🔴 BLOCKING | `build_context()` returns `str` not `list[dict]` | P10 | 0.5.8 |
| B-5.8.4 | 🔴 BLOCKING | `load_manifest()` + `WADManifest` don't exist | P10 | 0.5.8 |
| B-5.9.1 | 🔴 BLOCKING | `config_path=...` literal ellipsis | P10 | 0.5.9 |
| B-5.9.3 | 🟡 HIGH | Direct `provider.generate()` instead of `gateway.generate()` | P10 | 0.5.9 |

**Consolidation impact**: Of these 14 new findings, **8 are BLOCKING** and must be addressed before execution. The remaining 6 are medium/low but should be tracked.

---

## §4 EFFORT RE-ESTIMATES (Updated)

### Original Plan Estimates vs. Actual Pillar Assessments

| Phase | Original | P6 Adj. | P8 Adj. | P10 Adj. | **Adjusted Total** | Delta |
|:-----:|:--------:|:-------:|:-------:|:--------:|:------------------:|:-----:|
| Plan bug fixes | — | 25 min | — | 30 min | **55 min** | +55 min |
| Phase 0 (P6-owned) | 4 min | 14 min | — | — | **14 min** | +10 min |
| Phase 0 (P8-owned) | 50 min | — | 50 min | — | **50 min** | — |
| Phase 0.5 (P6-owned) | 4.5 hr | 275 min | — | — | **4.6 hr** | +0.1 hr |
| Phase 0.5 (P8-owned) | 3 hr | — | 180 min | — | **3.0 hr** | — |
| Phase 0.5 (P10-owned) | 4.25 hr | — | — | 240 min | **4.0 hr** | -0.25 hr |
| New discoveries | — | — | — | included above | **included above** | — |
| **Run Side TOTAL** | **~12.3 hr** | **~5.1 hr** | **~3.8 hr** | **~4.5 hr** | **~13.4 hr** | **+1.1 hr** |

### Key Revisions

1. **P10 0.5.8 reduced from 2.25h to 1.75h** — fewer APIs exist than assumed, so tests are simpler (but different)
2. **P6 0.5.3 increased from 1.5h to 1.25h** — B1 + B5 plan bugs add 15 min to fix before implementation
3. **P6 0.5.12 increased from 2h to 2.25h** — B8 embedding path wrong, needs config-driven refactor instead of simple hardcode
4. **Plan bug fixes added: 55 min** — B1, B5, B8 (P6) + B-5.8.1-4 (P10) must be fixed in plan document before any code execution

---

## §5 DEPENDENCY GRAPH

### Pillar-Level Dependencies

```
P6 Phase 0 (0.1, 0.2) ─── 4 min ─── no deps ─── RUN FIRST
      │
      ├──▶ P6 Phase 0.5 (0.5.3, 0.5.9, 0.5.12, 0.5.13, 0.5.16)
      │         │
      │         ├── 0.5.3, 0.5.9, 0.5.12 ── depends on 0.1 (model paths)
      │         ├── 0.5.13 ── no deps
      │         └── 0.5.16 ── best combined with 0.5.12
      │
      ├──▶ P8 Phase 0 (0.6, 0.7) ─── no deps on P6 ─── CAN RUN IN PARALLEL
      │         │
      │         ├── 0.6 ── additive trace_id params, no behavior change
      │         └── 0.7 ── config wiring only
      │
      └──▶ P10 Phase 0.5 (0.5.8, 0.5.9, 0.5.20) ─── 3h with NO deps
                │
                ├── 0.5.8 ── contract tests ── no deps
                ├── 0.5.9 ── GGUF smoke variant ── needs 0.1 for real inference
                │             Mock variant ── no deps
                └── 0.5.20 ── E2E test ── no deps (MockProvider)
```

### Critical Path Analysis

```
CRITICAL: P6 0.1 (model paths, 2 min) ─── unlocks everything
              │
              ├── P6 0.5.3 (warmup) ─── needs 0.1 + B1/B5 fixed
              ├── P6 0.5.9 (GGUF smoke) ─── needs 0.1
              ├── P6 0.5.12 (embeddings) ─── needs 0.1 + B8 fixed
              ├── P8 trace verification ─── needs 0.1 for real inference
              └── P10 GGUF smoke test variant ─── needs 0.1

NOT CRITICAL (no deps):
  - P8 0.6 (trace_id) ─── additive, no deps
  - P8 0.7 (dataset config) ─── config wiring, no deps
  - P10 0.5.8 (contract tests) ─── mock-backed, no deps
  - P10 0.5.20 (E2E test) ─── mock-backed, no deps
  - P6 0.5.13 (Ollama sync) ─── shell script, no deps
  - P6 0.2 (sort bug) ─── logic change, no deps
```

### Recommended Execution Order

```
STEP 0 [55 min]: Fix plan bugs BEFORE touching any code
  ├─ B1, B5: Fix 0.5.3 warmup async pattern + self.config (15 min)
  ├─ B8: Fix 0.5.12 embedding path to be config-driven (10 min)
  ├─ B-5.8.1-4: Fix 0.5.8 contract test API references (20 min)
  └─ B-5.9.1-3: Fix 0.5.9 GGUF test placeholder + type checks (10 min)

STEP 1 [4 min]: P6 Phase 0 (0.1 + 0.2)
  ├─ 0.1: Fix model paths (2 min) ─── UNLOCKS EVERYTHING
  └─ 0.2: Fix sort bug (2 min)

STEP 2 [50 min]: P8 Phase 0 (0.6 + 0.7) ─── CAN RUN PARALLEL WITH STEP 3
  ├─ 0.6: Wire trace_id to 7 sites (35 min)
  └─ 0.7: Wire dataset collection (15 min)

STEP 3 [3 hr]: Parallel work ─── ALL CAN START AFTER STEP 1
  ├─ P8: Phase 0.5 (0.5.5, 0.5.6, 0.5.15, 0.5.18, 0.5.21) ─── ~3.5 hr
  ├─ P6: Phase 0.5 (0.5.3, 0.5.9, 0.5.12+0.5.16, 0.5.13) ─── ~4.6 hr
  ├─ P10: Phase 0.5 (0.5.8, 0.5.9, 0.5.20, make m21-gate) ─── ~4 hr
  └─ All three pillars are file-independent ─── no lock conflicts

STEP 4 [30 min]: Verification
  ├─ make test (expect 447+ passing)
  ├─ make temple-grade
  ├─ make heritage-map
  ├─ omega talk "hello" (expect response)
  ├─ redis-cli ping (expect PONG)
  └─ omega entity prune --dry-run (expect 0 orphans)
```

---

## §6 READINESS ASSESSMENT

### Overall Verdict: **CONDITIONAL GO** — 3 conditions for Absolute GO

The Run Side (P6-P10) is architecturally sound but has implementation bugs at the wiring layer. All three pillars returned CONDITIONAL GO, meaning they CAN proceed but require plan-bug-fixing before touching code.

### Condition 1: Fix Plan Bugs First [55 min]

Before ANY code execution, 8 plan bugs across 4 items must be fixed in `HARDENING_IMPLEMENTATION_PLAN.md`:

| Bug | Item | Issue | Fix | Effort |
|:---:|:----:|-------|-----|:------:|
| B1 | 0.5.3 | `anyio.from_thread.run()` wrong context | Use `async def start()` pattern | 10 min |
| B5 | 0.5.3 | `self.config` doesn't exist | Read from `self.config_path` + YAML | 5 min |
| B8 | 0.5.12 | Embedding path points to non-existent file | Read from `config/models.yaml:embedding.local_path` | 10 min |
| B-5.8.1 | 0.5.8 | `BreakerState` class doesn't exist | Fix test to match actual API | 5 min |
| B-5.8.2 | 0.5.8 | `ForensicsSnapshot` doesn't exist | Fix test to match actual API | 5 min |
| B-5.8.3 | 0.5.8 | `build_context()` returns `str` | Fix test expectation | 5 min |
| B-5.8.4 | 0.5.8 | `load_manifest()` doesn't exist | Fix test to match actual API | 5 min |
| B-5.9.1 | 0.5.9 | `config_path=...` literal ellipsis | Fill with `Path("config/models.yaml")` | 5 min |
| B-5.9.2 | 0.5.9 | `isinstance(result, str)` wrong type | Use `isinstance(result, GenerateResult)` | 5 min |

### Condition 2: Execute Phase 0 Items First [~1 hr]

All Phase 0 items must execute before Phase 0.5 because they fix the fundamentals:

- **P6 0.1** (model paths): 2 min — transforms M7 from FAIL to PASS
- **P6 0.2** (sort bug): 2 min — restores local-first chain integrity
- **P8 0.6** (trace_id): 35 min — transforms M22 from FAIL to PASS
- **P8 0.7** (dataset config): 15 min — enables fine-tuning data collection

### Condition 3: Verify Each Step

After every Phase 0 item: `make test` (447+ must pass). After all Phase 0 items: `omega talk "hello"` must return a response.

### Readiness Summary

| Dimension | Before Run Side | After Run Side (projected) | Improvement |
|-----------|:--------------:|:--------------------------:|:-----------:|
| Model path correctness | 3/11 | **11/11** | 100% |
| Provider priority order | Broken (Mock before cloud) | **Correct** (native-gguf → ... → cloud → mock) | Restored |
| trace_id propagation | 1/8 sites (12.5%) | **8/8 sites (100%)** | 8x |
| Dataset collection | Silently disabled | **Enabled from config** | Mandate met |
| M22 Response Provenance | FAIL | **PASS** | Compliance |
| M7 Local-First | FAIL | **PASS** | Compliance |
| M21 contract tests | 19/24 | **24/24 (or 18/24 with @skipif)** | Coverage |
| Embeddings | Random vectors | **Real 768-dim via Gemma** | RAG enabled |
| Cold-start first call | 10s+ | **<2s (pre-warmed)** | 5x faster |
| Stale dataset artifacts | 187 files | **0 files** | Clean |
| Plan implementation bugs | 11 found | **All fixed** | Executable |

### Single Blocker

> **The single blocker is: 8 plan bugs across 4 items (0.5.3, 0.5.8, 0.5.9, 0.5.12) must be fixed in the HARDENING_IMPLEMENTATION_PLAN.md document before ANY Phase 0.5 code execution begins. Without this pre-flight, 4 of 21 Phase 0.5 items would fail at runtime.**

This is a **55-minute pre-flight fix** that prevents runtime failures during the hardening sprint.

---

## §7 RECOMMENDATION TO KALI

### Executive Summary

1. **Run Side is CONDITIONAL GO** — All 3 pillars (P6 Cognition, P8 Observability, P10 Validation) returned CONDITIONAL GO. The architecture is correct; the wiring is broken in 8 documented locations.

2. **~13.4 hours total effort** for all Run Side items (Phase 0 + Phase 0.5 + plan bug fixes), plus ~1.5 hours for Plan B Side (P1/P5) items. ~15 hours for the full 28-item sprint.

3. **Three pillars can run in parallel after P6 Phase 0 completes** — The serial dependency is minimal (P6 0.1 unlocks local inference verification, but P8 0.6/0.7 and P10 0.5.8/0.5.20 have ZERO code dependencies and can execute immediately with MockProvider).

### Single Most Important Recommendation

> **Execute P6 Phase 0 (0.1 + 0.2 = 4 min) FIRST, then release all three pillars in parallel. The 55-minute plan-bug pre-flight should be done by a single editor pass through `HARDENING_IMPLEMENTATION_PLAN.md` before any code touches disk.** This minimizes serial wait time while ensuring Phase 0.5 items don't fail at runtime due to plan bugs.

### Final Verdict

```
┌─────────────────────────────────────────────────────────┐
│  RUN SIDE READINESS: ✅ CONDITIONAL GO                  │
│                                                         │
│  Conditions for Absolute GO:                            │
│  1. Fix 8 plan bugs in HARDENING_IMPLEMENTATION_PLAN.md │
│  2. Execute P6 Phase 0 (0.1 + 0.2 = 4 min)             │
│  3. Execute P8 Phase 0 (0.6 + 0.7 = 50 min)            │
│  4. Then all Phase 0.5 items executable in parallel     │
│                                                         │
│  Total: ~13.4 hr Run Side + ~1.5 hr Build Side ≈ 15 hr │
│  Est. Sprint Duration: 2 focused sessions               │
└─────────────────────────────────────────────────────────┘
```

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ RUN-SIDE-SYNTHESIS ⬡ 2026-06-25*
