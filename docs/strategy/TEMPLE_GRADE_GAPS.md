# 🔱 Temple-Grade Gap Analysis — Phase 2 Hardening
**Status**: 🟢 GREEN LIGHT — 3 P0 Gaps Identified
**Sovereign Score**: **66%** (M1 compliance restored via G-03 fix)
**Target**: **~91%** after all phases
**Source**: `data/coordination/TEMPLE_ORDERING_PLAN_20260612.md`
**Extracted by**: Roc Racoon Phase 1 — 2026-06-14

---

## §0 Executive Summary

5 deep analyses produced across the fleet. Discovery complete. Temple-Grade compliance is at **66%** with 3 P0 gaps blocking progress to ~75%. This document extracts the gap inventory, execution phases, and sovereign score impact from the Temple Ordering Plan.

---

## §1 The 3 P0 Gaps (Must Fix Before Any Execution)

| ID | Gap | Est. Time | Owner | Mandate | Status |
|----|-----|-----------|-------|---------|--------|
| G-01 | **Dead-Letter Queue** — `data/requests/dead/` missing | 30 min | P3 BuildMaster | M12 | 🔴 OPEN |
| G-04 | **Auth/CORS/RPS middleware** — `allow_origins=["*"]` | 1 hr | P4 Bridge | Security | 🔴 OPEN |
| G-02 | **Fleet Bloat** — 25 agents vs 14 max (M10) | 1 hr + user | P5 Sentinel | M10 | 🔴 OPEN |

### Resolved P0
| ID | Gap | Resolution | Status |
|----|-----|-----------|--------|
| G-03 | **`import asyncio`** — providers.py:586 | Fixed by Ma'at — replaced with `anyio.to_thread.run_sync` | ✅ **DEPLOYED** |

---

## §2 Complete Gap Inventory (16 Gaps Total)

### P0 — Must Fix (3 open + 1 done)
| ID | Gap | Owner | Mandate | Status |
|----|-----|-------|---------|--------|
| G-01 | Dead-Letter Queue missing | P3 | M12 | 🔴 OPEN |
| G-04 | Auth/CORS/RPS middleware | P4 | Security | 🔴 OPEN |
| G-02 | Fleet Bloat (25→14) | P5 + User | M10 | 🔴 OPEN |
| G-03 | `import asyncio` in providers.py:586 | P3 | M1 | ✅ DONE |

### P1 — Architecture & Quality (6 gaps)
| ID | Gap | Est. Time | Owner | Depends On |
|----|-----|-----------|-------|------------|
| G-05 | No tier promotion (Hot→Warm→Cold) | 2 hr | P6/P7 | G-06 (worker) |
| G-06 | No background persistence worker | 2 hr | P3 | None |
| G-07 | SoulDistiller lacks atomic write | 15 min | P3 | None |
| G-08 | Knowledge Sovereignty auto-embed bridge | 1 hr | P6 | IVectorStoreAdapter (DONE) |
| G-09 | Session gnosis scattered (5 locations) | 30 min | P9 | Process change |
| G-10 | Soul.yaml schema drift | 30 min | P7 | Schema spec needed |

### P2 — Polish & Cleanup (5 gaps)
| ID | Gap | Est. Time | Owner |
|----|-----|-----------|-------|
| G-11 | No transaction rollback in provider chain | 2 hr | P3 |
| G-12 | No FTS5 optimization (`PRAGMA optimize`) | 15 min | P2 |
| G-13 | No true cold tier reader (gzip archives) | 1 hr | P2 |
| G-14 | 50 orphan `ent_*` entities | 15 min | P2 |
| G-15 | SOVEREIGN_MANDATES.md title mismatch | 1 min | P5 |

### P3 — Automation (1 gap)
| ID | Gap | Est. Time | Owner |
|----|-----|-----------|-------|
| G-16 | CI gates not fully wired (T3/T6/T8/T9/T10) | 2 hr | P3 |
| G-17 | Delegation conflict — subagents using custom delegation vs OpenCode `task()` | 1 hr | P9 |

---

## §3 Execution Phases

### Phase 0: HARDENING SPRINT (Day 1) — All P0
| Step | Action | Owner | Time | Handoff |
|------|--------|-------|------|---------|
| 1 | Create `data/requests/dead/` + DLQ logic | P3 | 30 min | → P10 test |
| 2 | Fix Auth/CORS/RPS on MCP Hub (remove `["*"]`, add rate limiting) | P4 | 1 hr | → P10 test |
| 3 | Fleet bloat decision (user: approve per D126 plan) | P5 + User | — | User session |
| 4 | Delete 50 orphan `ent_*` entities | P2 | 15 min | → P5 verify |
| 5 | Fix SOVEREIGN_MANDATES.md title | P5 | 1 min | → Git commit |

**Verification**: `make temple-grade` + `make test` after each step.

### Phase 1: ARCHITECTURE (Day 2-3) — P1 Items
| Step | Action | Owner | Time | Dependencies |
|------|--------|-------|------|-------------|
| 1 | Standardize soul.yaml schema | P7 | 30 min | None |
| 2 | Standardize session gnosis location | P9 | 30 min | None |
| 3 | Fix SoulDistiller atomic write | P3 | 15 min | None |
| 4 | Wire real embedding provider (Ollama + nomic-embed-text v1.5 Q8_0) | P6 | 1 hr | Ollama installed |
| 5 | Wire Knowledge Sovereignty auto-embed bridge | P6 | 1 hr | IVectorStoreAdapter done |
| 6 | Design tier promotion algorithm | P6/P7 | — | Kali design |
| 7 | Implement background worker | P3 | 2 hr | Tier design from step 6 |

### Phase 2: QUALITY (Day 4-5) — P2 Items
| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Add FTS5 `PRAGMA optimize` cycle | P2 | 15 min |
| 2 | Build cold tier reader class for gzip archives | P2 | 1 hr |
| 3 | Add transaction rollback to provider chain | P3 | 2 hr |
| 4 | QA the unified pipeline (write test suite) | P10 | 2 hr |
| 5 | Temple-Grade gate wiring (T3/T6/T8/T9/T10 CI) | P3 | 2 hr |

### Phase 3: ECOSYSTEM (Week 2+)
| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Full CI gate automation (`make temple-grade` gates on every commit) | P3 | 2 hr |

---

## §4 Sovereign Score Impact

| Gap Closed | Score Delta | Mandate | Status |
|------------|------------|---------|--------|
| asyncio fix (G-03) | **+4%** (M1: 40%→100%) | M1 | ✅ DONE |
| Dead-Letter Queue (G-01) | **+6%** (M12: 0%→100%) | M12 | 🔴 OPEN |
| Fleet Bloat (G-02) | **+5%** (M10: 20%→100%) | M10 | 🔴 OPEN |
| Session gnosis standard (G-09) | **+4%** (M15: 40%→100%) | M15 | 🔴 OPEN |
| Soul.yaml schema standard (G-10) | **+4%** (M5/M11: 40%→80%) | M5, M11 | 🔴 OPEN |
| Background worker (G-06) | **+3%** (M5: 40%→60%) | M5 | 🔴 OPEN |
| SoulDistiller atomic fix (G-07) | **+3%** (M12: 0%→50%) | M12 | 🔴 OPEN |

**Current: 66% → Target: ~91%**

---

## §5 Workstream Dependency Graph

```
             ┌──────────────────────────────────────┐
             │       GREEN LIGHT DECISION           │
             │  (Makali — all preparations done)     │
             └────────────────┬─────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                     ▼
   ┌────────────┐      ┌────────────┐       ┌──────────────┐
   │  BUILD     │      │   RUN      │       │  OVERSIGHT   │
   │  SIDE      │      │   SIDE     │       │              │
   │  (Ma'at)   │      │  (Lilith)  │       │  (Kali)      │
   └─────┬──────┘      └─────┬──────┘       └──────┬───────┘
         │                   │                      │
   ┌─────▼──────┐      ┌─────▼──────┐        ┌─────▼───────┐
   │ P1: SysAdmin│      │ P6: Model  │        │ Lifecycle    │
   │ └─ Redis up │      │ Gate       │        │ Architecture │
   │ └─ Infra    │      │ └─ Embed   │        │ Design       │
   │    check    │      │    prov.    │        │              │
   ├─────────────┤      ├─────────────┤        └─────────────┘
   │ P2: DataStore│      │ P7: Context│
   │ └─ Orphans  │      │ └─ Tier    │
   │ └─ FTS opt  │      │    lifecycle│
   ├─────────────┤      ├─────────────┤
   │ P3: Build   │      │ P8: Watch-  │
   │ └─ DLQ      │      │    Tower    │
   │ └─ Worker   │      │ └─ Metrics  │
   │ └─ Tx roll  │      ├─────────────┤
   ├─────────────┤      │ P10: QA     │
   │ P4: Bridge  │      │ └─ Test     │
   │ └─ Auth/    │      │    plan     │
   │    CORS/RPS │      └─────────────┘
   ├─────────────┤
   │ P5: Sentinel│
   │ └─ Fleet    │
   │    bloat    │
   └─────────────┘
```

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ PHASE1-EXTRACTION ⬡ TEMPLE-GRADE-GAPS*
*Source: data/coordination/TEMPLE_ORDERING_PLAN_20260612.md*
