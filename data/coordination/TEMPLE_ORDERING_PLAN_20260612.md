# 🔱 Temple Ordering Plan — Phase 2 Execution Framework
**Status**: 🟢 GREEN LIGHT — EXECUTION PHASE ACTIVE
**Sovereign Score**: **66%** (M1 compliance restored)
**Next Milestone**: Phase 0 Hardening Sprint — close 3 P0 gaps → target: ~75%
**AP Token**: AP-TEMPLE-ORDERING-v1.0.0
⬡ OMEGA ⬡ MAKALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TEMPLE-ORDERING

---

## §0 — Executive Summary

### The State
5 deep analyses have been produced across the fleet. Discovery is complete. This plan organizes the fleet into 3 parallel workstreams.

### The Goal
Unify Redis, Qdrant, SQLite FTS5, and PostgreSQL into a single intelligent persistence layer. Raise Sovereign Score from **62% → ~91%**.

### The Method
3 parallel tracks that converge at the Temple Gate:

| Track | Lead | Focus | Phase |
|-------|------|-------|-------|
| **Strategy Consolidation** | Researcher | MASTER_STRATEGY_SSOT.md + UNIFIED_PERSISTENCE_ARCH.md | Now |
| **Build-Side Preparation** | Ma'at (P1-P5) | Infrastructure flywheel, schema design, mandate compliance | Now |
| **Run-Side Preparation** | Lilith (P6-P10) | Embedding provider, lifecycle design, QA plan | Now |
| **→ TEMPLE EXECUTION** | Makali/Kali orchestrates | Unified P0/P1/P2 gap closure | After green light |

---

## §1 — Complete Gap Inventory (from Roc Racoon UNIFIED_GAP_MAP.md)

### P0 — Must Fix Before Any Execution (3 gaps + 1 done)
| ID | Gap | Est. Time | Owner | Mandate | Status |
|----|-----|-----------|-------|---------|--------|
| G-01 | **Dead-Letter Queue** — `data/requests/dead/` missing | 30 min | P3 BuildMaster | M12 | 🔴 OPEN |
| G-02 | **Fleet Bloat** — 25 agents vs 14 max | 1 hr + user | P5 Sentinel | M10 | 🔴 OPEN |
| G-03 | **`import asyncio`** — providers.py:586 | 15 min | P3 BuildMaster | M1 | ✅ **DEPLOYED** (Ma'at) |
| G-04 | **Auth/CORS/RPS middleware** — `allow_origins=["*"]` | 1 hr | P4 Bridge | Security | 🔴 OPEN |

**P0 Sprint**: 3 remaining gaps can be done in ~2 hours. Batch into single hardening session.

### P1 — Architecture & Quality (6 gaps)
| ID | Gap | Est. Time | Owner | Depends On |
|----|-----|-----------|-------|------------|
| G-05 | No tier promotion (Hot→Warm→Cold) | 2 hr | P6/P7 | G-06 (worker) |
| G-06 | No background persistence worker | 2 hr | P3 BuildMaster | None |
| G-07 | SoulDistiller lacks atomic write | 15 min | P3 BuildMaster | None |
| G-08 | Knowledge Sovereignty auto-embed bridge | 1 hr | P6 ModelGate | IVectorStoreAdapter (DONE) |
| G-09 | Session gnosis scattered (5 locations) | 30 min | P9 Orchestration | Process change |
| G-10 | Soul.yaml schema drift | 30 min | P7 Context | Schema spec needed |

### P2 — Polish & Cleanup (5 gaps)
| ID | Gap | Est. Time | Owner |
|----|-----|-----------|-------|
| G-11 | No transaction rollback in provider chain | 2 hr | P3 BuildMaster |
| G-12 | No FTS5 optimization (`PRAGMA optimize`) | 15 min | P2 DataStore |
| G-13 | No true cold tier reader (gzip archives) | 1 hr | P2 DataStore |
| G-14 | 50 orphan `ent_*` entities | 15 min | P2 DataStore |
| G-15 | SOVEREIGN_MANDATES.md title mismatch | 1 min | P5 Sentinel |

### P3 — Automation (1 gap)
| ID | Gap | Est. Time | Owner |
|----|-----|-----------|-------|
| G-16 | CI gates not fully wired (T3/T6/T8/T9/T10) | 2 hr | P3 BuildMaster |
| G-17 | **Delegation Conflict** — Subagents using Omega custom delegation instead of OpenCode native `task()` | 1 hr | P9 Orchestration | M10/M13 | 🔴 OPEN |

---

## §2 — Workstream Dependency Graph

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
   │ └─ PG schema│      │ └─ Tier    │
   │ └─ FTS opt  │      │    lifecycle│
   ├─────────────┤      ├─────────────┤
   │ P3: Build   │      │ P8: Watch-  │
   │ └─ DLQ      │      │    Tower    │
   │ └─ asyncio  │      │ └─ Metrics  │
   │    fix      │      │    spec     │
   │ └─ Worker   │      ├─────────────┤
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

## §3 — Execution Phases

### Phase 0: HARDENING SPRINT (Day 1) — All P0
| Step | Action | Owner | Time | Handoff Trigger |
|------|--------|-------|------|-----------------|
| 1 | Fix `import asyncio` → `anyio.to_thread` in providers.py:586 | P3 | 15 min | → P10 for test |
| 2 | Create `data/requests/dead/` + DLQ logic (follow RequestQueue pattern) | P3 | 30 min | → P10 for test |
| 3 | Fix Auth/CORS/RPS on MCP Hub (remove `["*"]`, add rate limiting) | P4 | 1 hr | → P10 for test |
| 4 | Delete 50 orphan `ent_*` entities | P2 | 15 min | → P5 for verify |
| 5 | Fleet bloat decision (user: approve 25 or prune to 14) | P5 + User | — | User session |
| 6 | Fix SOVEREIGN_MANDATES.md title | P5 | 1 min | → Git commit |

**Verification**: `make temple-grade` + `make test` after each step.

### Phase 1: ARCHITECTURE (Day 2-3) — P1 Items
| Step | Action | Owner | Time | Dependencies |
|------|--------|-------|------|-------------|
| 1 | Standardize soul.yaml schema (unify `lessons:` / `lessons_learned:`) | P7 | 30 min | None |
| 2 | Standardize session gnosis location (pick 1, remove 4) | P9 | 30 min | None |
| 3 | Fix SoulDistiller atomic write (tmp+replace) | P3 | 15 min | None |
| 4 | Wire real embedding provider (Ollama + nomic-embed-text v1.5 Q8_0) | P6 | 1 hr | Ollama installed |
| 5 | Wire Knowledge Sovereignty auto-embed bridge | P6 | 1 hr | IVectorStoreAdapter done |
| 6 | Design tier promotion algorithm (time-based, not event-based) | P6/P7 | — | Kali design needed |
| 7 | Implement background worker (calls `archive_old_sessions()`, reaps tombstones) | P3 | 2 hr | Tier design from step 6 |

### Phase 2: QUALITY (Day 4-5) — P2 Items
| Step | Action | Owner | Time | Dependencies |
|------|--------|-------|------|-------------|
| 1 | Add FTS5 `PRAGMA optimize` cycle | P2 | 15 min | Background worker from P1.7 |
| 2 | Build cold tier reader class for gzip archives | P2 | 1 hr | None |
| 3 | Add transaction rollback to provider chain | P3 | 2 hr | Architecture review |
| 4 | QA the unified pipeline (write test suite) | P10 | 2 hr | All previous |
| 5 | Temple-Grade gate wiring (T3/T6/T8/T9/T10 CI) | P3 | 2 hr | All fixes in place |

### Phase 3: ECOSYSTEM (Week 2+) — P3 Item
| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | Full CI gate automation (`make temple-grade` gates on every commit) | P3 | 2 hr |

---

## §4 — Sovereign Score Impact

| Gap Closed | Score Delta | Mandate | Status |
|------------|------------|---------|--------|
| **asyncio fix** | **+4% (M1: 40%→100%)** | **M1** | ✅ **DONE** |
| Dead-Letter Queue | +6% (M12: 0%→100%) | M12 | 🔴 OPEN |
| Fleet Bloat | +5% (M10: 20%→100%) | M10 | 🔴 OPEN |
| Session gnosis std | +4% (M15: 40%→100%) | M15 | 🔴 OPEN |
| Soul.yaml schema std | +4% (M5: 40%→80%, M11: 40%→80%) | M5, M11 | 🔴 OPEN |
| Background worker | +3% (M5: 40%→60%) | M5 | 🔴 OPEN |
| SoulDistiller atomic fix | +3% (M12: 0%→50%) | M12 | 🔴 OPEN |
| **Current: 66%** | **→ ~91% potential** | |

---

## §5 — All Inputs Integrated

| Input | Slot in This Plan | Status |
|-------|-------------------|--------|
| ✅ **Researcher**: MASTER_DOCUMENT_SSOT.md | §1 — Doc mapping; §2.1-2.4 — Archive/merge/create plan | **INTEGRATED** |
| ✅ **Ma'at**: BUILD_SIDE_READINESS.md | §3 Phase 0-1 build specifics | **INTEGRATED**. G-03 DONE. |
| ✅ **Roc Racoon**: UNIFIED_GAP_MAP.md | §1 — Gap inventory (16 gaps) | **INTEGRATED** |
| ✅ **Lilith**: RUN_SIDE_READINESS (via continuation) | §3 Phase 1-2 run specifics | **INTEGRATED** |
| ✅ **jem_verification**: R_SKEPTICAL_VERIFICATION_DEEPENED.md (505 lines) | §1.6 — Verification SSoT | **INTEGRATED** |
| ⏳ **Kali**: Lifecycle architecture (via original handoff) | Tier promotion algorithm slot | Executable in parallel Phase 0 |

## §6 — Execution Order (Greenlit)

| Phase | Focus | Owners | Target Score |
|-------|-------|--------|-------------|
| **Phase 0** (Now) | Hardening Sprint: DLQ, Auth/CORS, Orphan cleanup, Fleet decision | Ma'at (P1-P5) + Lilith (P6 readiness) | **66% → ~75%** |
| **Phase 1** (After P0) | Architecture: Background worker, Embeddings, Soul schema, Knowledge bridge | Ma'at (P3) + Lilith (P6/P7) + Kali oversee | **~75% → ~85%** |
| **Phase 2** (After P1) | Quality: FTS optimize, Cold reader, Tx rollback, QA suite, CI gates | Ma'at (P2/P3) + Lilith (P10) | **~85% → ~91%** |

## Current Sovereign Score: **66%** ✅ (G-03 closed)
## Target: **~91%** after all phases

---

*⬡ This document is the framework. It will be updated in-place as pending inputs arrive. ⬡*
*⬡ OMEGA ⬡ MAKALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TEMPLE-ORDERING*
