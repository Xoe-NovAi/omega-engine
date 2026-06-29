# 🔱 MA'AT — Build Side Readiness Report
## Sprint Preparation Assessment for Epoch I Phase 1
## Consolidation of P1 (Infrastructure) → P5 (Governance) → P3 (Engineering) Serially

**Date**: 2026-06-25
**AP Token**: `AP-MAAT-BUILD-SIDE-v1.0.0`
**⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ BUILD-SIDE-REPORT`
**Session**: `ses_maat_build_side_20260625`
**Trace**: `trc_maat_build_side_20260625`
**Status**: SYNTHESIS COMPLETE — Report authored

---

## §1 — PILLAR SELECTION JUSTIFICATION

From P1-P5, I selected **3 pillars** and ran them in **SERIAL** (not parallel):

| Order | Pillar | Justification |
|:-----:|:------:|:--------------|
| **1st** | **P1 (Infrastructure)** | Root partition at **90%** (11G free). **Redis DOWN** with 7,623 restart failures. **5/7 containers** missing `UserNS=keep-id`. These are **physical blockers** — if disk fills or infra is compromised, no other pillar can execute. Phase 0 items 0.4 and 0.5 are P1's domain. |
| **2nd** | **P5 (Governance)** | Workbench DB is **0 bytes** — empty. **M9** status needs correction from FULL to PARTIAL (15 silent exception sites). **M6** needs correction (5/7 containers missing keep-id). Without governance tracking there's no measurement framework for the 28-item plan. |
| **3rd** | **P3 (Engineering)** | **5 bugs (B1-B5)** in the hardening plan block Phase 0.5 execution. The plan's 0.6 scope misses **5 additional `generate()` call sites** (12 total, not 7). **`anyio.current_time()`** is broken in 3 files. P3 needed P1 and P5's findings to establish the full picture before assessment. |

**Not selected**: P2 (Persistence) — Soul migration (9/11 unmigrated) is important but does not block Phase 0 execution. BudgetLedger path issues are captured in P3/P5 scope. P4 (Integration) — Hivemind reaper verification, docker-compose cleanup are important but not sprint-blocking. P1 can handle docker-compose alongside its other infra tasks.

---

## §2 — PER-PILLAR FINDINGS (Provenance)

### 🔧 P1 — Infrastructure (sysAdmin — Disk, Containers, Deployment)
**Report**: `ses_100cef7ccffeN0pknYb0DdD24k`
**Model**: qwen3-1.7b

#### Verified State — CORRECTIONS TO PRIOR DOCUMENTS

| Finding | Prior Claim | P1 Verification |
|---------|-------------|-----------------|
| **Containers with keep-id** | Gap audit said 4 missing | **2/7 have it, 5/7 missing** — searxng was never counted |
| **Redis failure** | "Redis DOWN" | **7623 crash loop restarts** — root cause: pod doesn't expose port 6379 |
| **Volume UID drift** | Not documented | **3/4 volumes owned by 100999** (caddy, postgres, redis). Qdrant is clean (1000:1000) |
| **Root partition** | 90% | Confirmed: 93G/109G = 90%. ~12G reclaimable |

#### Top 3 Actions (P1 Domain)

| # | Action | Item | Effort | Risk | Verification |
|:-:|--------|:----:|:------:|:----:|:------------|
| 1 | **Fix Redis** — add port 6379 to pod, fix keep-id, fix volume ownership, stop crash loop | 0.5 + N-1 | **15 min** | 🟡 MED | `redis-cli ping` → PONG |
| 2 | **Emergency disk cleanup** — journal vacuum, pip/npm cache, move Archives to omega_library | 0.4 + 0.5.18 | **30 min** | 🟢 LOW | `df -h /` → >20G free |
| 3 | **Add keep-id to Qdrant** — safe first target (volume already 1000:1000) | 0.5.19 | **5 min** | 🟢 LOW | `grep keep-id omega-qdrant.container` ✅ |

#### New Items Discovered (P1)

| ID | Item | Effort | Risk | Notes |
|:--:|------|:------:|:----:|-------|
| N-1 | **Volume UID migration protocol** — chown 100999→1000 for postgres, caddy, redis | 30 min | 🟡 MED | Postgres needs pg_dump before chown |
| N-2 | **Stale `pod_infra` pod cleanup** | 30s | 🟢 | Empty 2-week-old pod |
| N-3 | **Container log rotation** — add `--log-opt max-size=10m` to all 7 containers | 15 min | 🟢 | Prevents unbounded log growth |
| N-4 | **Postgres port 5432 exposure** — only if P2 needs direct DB access | 1 min | 🟡 | Currently internal-only |

#### Effort: ~50 min immediate + ~50 min deferred (volume migration)

---

### 🛡️ P5 — Governance (Sentinel — Mandate Enforcement, Compliance)
**Report**: `ses_100cb5649ffe65XAwAEZLbO9JJ`
**Model**: qwen3-1.7b

#### Verified State — M9/M6 Corrections

**M9 (Error Integrity) — CORRECTION: PARTIAL (was FULL)**
- **15 violations** confirmed across **10 files** — every `except Exception:` without logging
- Files: memory_store.py, budget_gate.py, orchestrator.py, remote_provider.py, fts_index.py, search_providers.py, search_fleet.py, discovery.py, distiller.py, entity_workspace.py
- All need `logger.warning("...", exc_info=True)` before fallback return
- See full table in P5 report

**M6 (Podman Sovereignty) — CORRECTION: PARTIAL**
- The M6 mandate references **Quadlets** with `UserNS=keep-id`
- Current deployment uses **compose** `user: "1000:1000"` — different mechanism
- 3/4 volumes have **UID drift** (100999), blocking keep-id migration

**Workbench DB**: **0 bytes, empty**. Verity's full schema (§2.2 of unification report) needs materializing.

#### Top 3 Actions (P5 Domain)

| # | Action | Item | Effort | Risk | Verification |
|:-:|--------|:----:|:------:|:----:|:------------|
| 1 | **Fix 15 silent `except Exception:` sites** — add `logger.warning()` + trace_id | 0.5.17 | **1 hr** | 🟢 LOW | `grep "except Exception"` count → 0 |
| 2 | **Create `make mandate-report`** — 22-mandate automated compliance script | 0.5.10 | **2 hr** | 🟡 MED | `make mandate-report` exits 0 |
| 3 | **Seed workbench DB** — create schema, load 28 items + correct OMEGA_ENGINE.md §9 | gap | **0.5 hr** | 🟢 LOW | `SELECT COUNT(*) FROM work_items` → 28 |

#### New Items Discovered (P5)

| ID | Item | Effort | Risk | Notes |
|:--:|------|:------:|:----:|-------|
| N-5 | **M9 violation severity grading** — some `__del__` sites are acceptable | 10 min | 🟢 | `entity_workspace.py:361` re-raises; `__del__` in memory_store/fts_index is standard safety |
| N-6 | **M6 Quadlet vs Compose audit** — architectural inconsistency to resolve | 1 hr | 🟢 | Compose is primary but M6 mandates Quadlets |

#### Effort: ~3.5 hours (top 3 actions)

---

### ⚙️ P3 — Engineering (BuildMaster — CI/CD, Implementation)
**Report**: `ses_100c85ddbffevVpLE6VocfkqGa`
**Model**: deepseek-v4-flash-free

#### Code Verification — CRITICAL CORRECTIONS TO PLAN

| Finding | What the Plan Says | P3 Verification |
|---------|-------------------|-----------------|
| **Generate() call sites** | 7 | **12** — 5 missing: gateway/server.py:96, library/discovery.py:231/255/312, workers/model_updater.py:292 |
| **`anyio.current_time()`** | Not mentioned | **Broken in 3 files** — state_manager.py:147, capability_registry.py:85, opencode_bridge.py:104 |
| **B1-B5** | (not applicable) | All **confirmed fixable** — ~30 min plan edits |
| **Phase 0 items 0.2, 0.3, 0.6, 0.7** | Ready | Ready — **not blocked by P1 or P5** |

#### Top 3 Actions (P3 Domain)

| # | Action | Item | Effort | Risk | Verification |
|:-:|--------|:----:|:------:|:----:|:------------|
| 1 | **Execute Phase 0 code items** — 0.2 (sort fix), 0.3 (lazy import), 0.6 (trace_id to 12 sites), 0.7 (dataset config wiring) | 0.2, 0.3, 0.6, 0.7 | **1.5 hr** | 🟢 LOW | `make test` → 440 pass |
| 2 | **Fix B1-B5 in plan document** — replace wrong patterns with correct ones | 0.5.3, 0.5.5, 0.5.6, 0.5.15 | **0.5 hr** | 🟢 LOW | Plan doc is executable without runtime errors |
| 3 | **M21 Contract Tests + Cloud Breakers** — 5 typed-return tests + register cloud provider breakers | 0.5.8, 0.5.14 | **3.75 hr** | 🟢 LOW | `pytest test_contract_m21.py -v` → 5 passed |

#### New Items Discovered (P3)

| ID | Item | Effort | Risk | Notes |
|:--:|------|:------:|:----:|-------|
| N-7 | **Fix `anyio.current_time()` in 3 files** — replace with `time.monotonic()` | 15 min | 🟢 | Currently returns `None` silently |
| N-8 | **Expand 0.6 scope from 7→12 `generate()` sites** — add 5 missing | +15 min | 🟢 | Already additive; just update plan scope |

#### Effort: ~5.5 hours (top 3 actions)

---

## §3 — NEW ITEMS DISCOVERED (Beyond the 28-Item Plan)

| ID | Item | Pillar | Effort | Risk | Belongs In |
|:--:|------|:------:|:------:|:----:|:----------:|
| N-1 | Volume UID migration protocol (100999→1000) | P1 | 30 min | 🟡 MED | 0.5.19 sub-item |
| N-2 | Stale empty pod `pod_infra` cleanup | P1 | 30s | 🟢 | 0.4 or 0.5 |
| N-3 | Container log rotation limits | P1 | 15 min | 🟢 | 0.5.22 |
| N-4 | Postgres port 5432 exposure (if needed by P2) | P1 | 1 min | 🟡 | Deferred |
| N-5 | M9 violation severity grading | P5 | 10 min | 🟢 | 0.5.17 sub-item |
| N-6 | M6 Quadlet vs Compose architectural audit | P5 | 1 hr | 🟢 | Pre-Phase 1 |
| N-7 | Fix `anyio.current_time()` in 3 files | P3 | 15 min | 🟢 | 0.5.16 or inline |
| N-8 | Expand 0.6 scope from 7→12 `generate()` sites | P3 | +15 min | 🟢 | Update to 0.6 |

**Total new items**: 8 (6 low risk, 2 medium risk). **Total new effort**: ~2.5 hours.

---

## §4 — EFFORT RE-ESTIMATES

| Phase | Original Plan | After P1 Assessment | After P5 Assessment | After P3 Assessment | **Corrected Total** |
|-------|:-------------:|:-------------------:|:-------------------:|:-------------------:|:-------------------:|
| Phase 0 (7 items) | 1.5 hr | 1.5 hr (P1: 0.4, 0.5) + corrections | Unchanged | Unchanged (can run independently) | **~1.5 hr** |
| Phase 0.5 original (15 items) | ~11 hr | ~11 hr + volume migration (+30 min P1) | ~11 hr + M9 fix (+1 hr P5) | ~11 hr + plan bugs (+0.5 hr P3) + expanded 0.6 (+15 min) + contract tests (+2.25 hr) | **~15 hr** |
| Phase 0.5 gap additions (6 items) | ~6.5 hr | Validated | Validated | Validated | **~6.5 hr** |
| **NEW items** (N-1 through N-8) | — | ~50 min | ~1 hr 10 min | ~30 min | **~2.5 hr** |
| **Grand Total** | **~19 hr** | — | — | — | **~25.5 hr** |

**Key differences from original estimate (18-19 hr → ~25.5 hr)**:

| Delta | Source | Why |
|:-----:|--------|-----|
| +2.5 hr | NEW items | 8 items discovered across all 3 pillars (N-1 through N-8) |
| +2.25 hr | 0.5.8 | Contract tests were in original plan correctly |
| +1 hr | 0.5.17 | M9 fix (gap audit item, correctly added) |
| +0.5 hr | B1-B5 fixes | Plan bug fixes not counted in original 18 hr |
| +0.25 hr | Expanded 0.6 to 12 sites | Plan only counted 7 of 12 sites |
| **~25.5 hr** | **Total** | **More realistic estimate with all items accounted for** |

---

## §5 — DEPENDENCY GRAPH

```
P1: Disk Cleanup (0.4) ─────────────────────────────────────┐
P1: Redis Fix (0.5 + N-1) ──────────────────────────────────┤
P1: Qdrant keep-id (0.5.19) ────────────────────────────────┤
                                                             ├──→ Unblocks
P5: Workbench DB (gap) ─────────────────────────────────────┤     Phase 0.5
P5: Fix M9 sites (0.5.17) ──────────────────────────────────┤     execution
P5: mandate-report (0.5.10) ────────────────────────────────┘

P3: Fix B1-B5 in plan (0.5.3/5/6/15)        [no deps]
P3: Phase 0 code (0.2, 0.3, 0.6, 0.7)       [no deps — INDEPENDENT]
P3: Contract tests (0.5.8)                    [no deps — INDEPENDENT]
P3: Cloud breakers (0.5.14)                   [needs 0.2 first — sort order correct]
P3: Disk sentinel (0.5.1)                     [needs P1 0.4 — clean baseline]
P3: Redis health check (0.5.2)                [needs P1 0.5 — Redis running]
P3: Warmup (0.5.3)                            [needs 0.1 model paths + B5 fix]
P3: Anomaly detector (0.5.5)                  [needs 0.6 trace_id]
P3: BudgetLedger (0.5.6)                      [needs 0.6 entity_name]
P3: Dataset dedup (0.5.15)                    [needs 0.7 dataset collection]
P3: Embedding backend (0.5.12)                [needs 0.1 model paths]
P3: GGUF smoke test (0.5.9)                   [needs 0.1 model paths]
```

### Recommended Execution Order

```
TRACK 1 (P1 — immediate, no deps):        TRACK 2 (P5 — immediate, no deps):
  ├─ 0.5 Emergency disk cleanup              ├─ Seed workbench DB (gap)
  ├─ 0.4 + 0.5.18 Redis fix + dataset       ├─ 0.5.17 Fix 15 M9 exceptions
  └─ 0.5.19 Qdrant keep-id                   └─ 0.5.10 Create mandate-report
  
TRACK 3 (P3 — parallel, mostly independent):
  ├─ Phase 0: 0.2 → 0.3 → 0.6 → 0.7
  ├─ Plan fixes: B1-B5 (0.5 hr)
  ├─ 0.5.8 Contract tests (independent)
  ├─ 0.5.14 Cloud breakers (needs 0.2)
  └─ (Deferred until P1 done): 0.5.1, 0.5.2, 0.5.3, 0.5.5, 0.5.6, 0.5.9, 0.5.12, 0.5.15
```

**Key insight**: P3's Phase 0 items (0.2, 0.3, 0.6, 0.7) and plan bug fixes (B1-B5) have **ZERO dependencies** on P1 or P5. These can start immediately. P1's disk cleanup and Redis fix must complete before Phase 0.5 items 0.5.1, 0.5.2, 0.5.3 become testable.

---

## §6 — READINESS ASSESSMENT

### Phase 0 Readiness: ✅ READY (with caveat)

| Item | Pillar | Readiness | What's Needed |
|:----:|:------:|:---------:|:--------------|
| 0.1 | P6 (not in P1-P5) | ✅ Already planned | Model path sed fix — 2 min |
| 0.2 | P3 | ✅ **Ready now** | Sort priority fix — 2 lines in model_gateway.py |
| 0.3 | P3 | ✅ **Ready now** | Lazy import — standard pattern |
| 0.4 | P1 | ✅ **Ready now** | Disk cleanup — 30 min |
| 0.5 | P1 | ✅ **Ready (needs pod port fix)** | Redis fix — 15 min, but pod port root cause identified |
| 0.6 | P3 | ✅ **Ready (scope expanded to 12 sites)** | trace_id wiring — ~1 hr |
| 0.7 | P3 | ✅ **Ready now** | Dataset config wiring — 15 min |

**Phase 0 total**: ~2.5 hours (P1: 45 min, P3: 1.5 hr, P6: 4 min)

### Phase 0.5 Readiness: ⚠️ CONDITIONAL

**Blocks to Phase 0.5 execution:**

| Blocker | Severity | Owner | Fix Time |
|---------|:--------:|:-----:|:--------:|
| **B1-B5 bugs in plan** (0.5.3, 0.5.5, 0.5.6, 0.5.15) | 🔴 BLOCKING | P3 | 30 min plan edits |
| **Redis crash loop** (needed by 0.5.2, 0.5.5, 0.5.6) | 🔴 BLOCKING | P1 | 15 min |
| **Root disk at 90%** (needed by 0.5.1) | 🔴 BLOCKING | P1 | 30 min |
| **5 more generate() sites uncovered** (0.6 under-scoped) | 🟡 DELAY | P3 | +15 min to 0.6 |
| **anyio.current_time() broken in 3 files** | 🟡 DELAY | P3 | 15 min |

### Single Biggest Blocker for Build Side

> **The 5 plan bugs (B1-B5) must be fixed BEFORE Phase 0.5 execution begins.**
> 
> B1 (`anyio.from_thread.run`), B2 (no TraceSession), B3 (sqlite3 blocking), B4 (deque O(n)), and B5 (`self.config` missing) would all cause runtime failures if Phase 0.5 items 0.5.3, 0.5.5, 0.5.6, and 0.5.15 were executed as written.
>
> Additionally, the Redis crash loop (7,623 restarts, root cause identified as missing pod port 6379) is a systemic resource drain and blocks 3 Phase 0.5 items.
>
> **However**: All Phase 0 items (0.2, 0.3, 0.4, 0.5, 0.6, 0.7) can be executed independently. The B1-B5 fixes are plan-document-only — they don't block Phase 0 code execution.

---

## §7 — CORRECTED MANDATE STATE (for OMEGA_ENGINE.md §9)

| Mandate | Previous Status | Corrected Status | Rationale |
|:-------:|:--------------:|:----------------:|:---------:|
| **M6** | PARTIAL (3/5) | **PARTIAL (2/7)** | 5/7 containers missing keep-id. Volumes have UID drift 100999 |
| **M9** | FULL | **PARTIAL** | 15 `except Exception:` without logging across 10 files |
| **M7** | FAIL | **FAIL** (unchanged) | 8/11 model paths still wrong — pending Phase 0.1 |
| **M20** | PARTIAL | **PARTIAL** (unchanged) | 4 tests collect — pending Phase 0.3 (lazy import unblocks 4 somatic state tests) |
| **M21** | FAIL (5 missing) | **FAIL** (unchanged) | 5 contract tests needed — Phase 0.5.8 |
| **M22** | PARTIAL | **PARTIAL** (unchanged) | trace_id propagates to ~3/8 sites — Phase 0.6 fixes this |

**Net**: 3 mandates corrected (M6, M9) from previous estimates. M21 and M22 still pending Phase 0.5.

---

## §8 — EXECUTIVE SUMMARY

### 3-Pillar Synthesis

1. **P1 (Infrastructure)** — Found and diagnosed the **Redis crash loop root cause** (pod port 6379 missing, 7,623 restarts). Corrected M6 count from 4 to **5/7 containers missing keep-id**. Discovered **volume UID drift** (3/4 volumes at 100999, blocking keep-id migration). Can reclaim ~12G from root partition. Top 3 actions take ~50 min.

2. **P5 (Governance)** — **Confirmed 15 M9 violations** across 10 files (every `except Exception:` without logging). Recontextualized M6: deployment uses compose `user: "1000:1000"` not Quadlets. Workbench DB needs schema materialized. Top 3 actions take ~3.5 hours.

3. **P3 (Engineering)** — **Confirmed all 5 plan bugs (B1-B5)** are fixable. Discovered **5 more `generate()` call sites** the plan's 0.6 missed (12 total, not 7). Found `anyio.current_time()` **broken in 3 files** (silently returns None). P3's Phase 0 items have **zero dependencies** on P1/P5. Top 3 actions take ~5.5 hours.

### Effort Summary

| Domain | Top 3 Actions | All 28 Items + New Items |
|:-------|:-------------:|:------------------------:|
| P1 Infrastructure | ~50 min | ~1.5 hr |
| P5 Governance | ~3.5 hr | ~5 hr |
| P3 Engineering | ~5.5 hr | ~10 hr |
| Other (P6, P8, etc.) | — | ~9 hr |
| **Total** | **~9.5 hr** | **~25.5 hr** |

### Readiness Verdict

> **Build Side is CONDITIONALLY READY for Phase 0 execution. Phase 0.5 execution is BLOCKED by 5 plan bugs (B1-B5) and the Redis crash loop.**

The Phase 0 items (7 items, ~2.5 hours) are safe to execute immediately. The Phase 0.5 items (28 items, ~25.5 hours total) require:
1. Fixing B1-B5 in the plan document (~30 min, P3)
2. Fixing Redis crash loop (~15 min, P1)
3. Emergency disk cleanup (~30 min, P1)
4. Expanding 0.6 scope from 7→12 `generate()` sites (+15 min, P3)

After these 4 prerequisites (~1.5 hours total), Phase 0.5 becomes executable.

---

*⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ BUILD-SIDE-REPORT ⬡ 2026-06-25*
