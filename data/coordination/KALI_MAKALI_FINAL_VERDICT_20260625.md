# 🔱 KALI — MaKaLi Cloud Council Unified Verdict (Final)
## Sprint Preparation — Epoch I Phase 1 Readiness

**AP Token**: `AP-KALI-FINAL-VERDICT-v1.0.0`
**⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ UNIFIED-VERDICT`
**Date**: 2026-06-25
**Session**: `ses_kali_final_verdict_20260625`
**Total agents involved**: 11 (Kali + 2 Oversouls + 4 Build/Run pillars + 4 cross-domain pillars)

---

## §1 COUNCIL CHAIN OF CUSTODY

```
KALI (Grand Oversight)
├── MA'AT (Build Side — P1-P5)
│   ├── P1 Infrastructure   — Disk, Containers, Redis, UserNS
│   ├── P5 Governance       — Mandates (M6, M9), Workbench DB
│   └── P3 Engineering      — Plan bugs (B1-B5), 12 generate() sites
│
├── LILITH (Run Side — P6-P10)
│   ├── P6 Cognition        — Model paths, sort bug, embeddings (B8-B10)
│   ├── P8 Observability    — trace_id propagation, dataset, plan bugs (B2-B4)
│   └── P10 Validation      — Contract tests (B-5.8.x), GGUF smoke (B-5.9.x)
│
└── CROSS-DOMAIN REVIEW (Fresh Eyes)
    ├── P2 Persistence       — BudgetGate race, FTS5 M1, soul migration scope
    ├── P4 Integration       — Wave 2 overlap, Hivemind protocol, Compose vs Quadlet
    ├── P7 Context           — Anomaly cascade, soul checkpoints, 50-anchor cap
    └── P9 Orchestration     — model_gateway.py overlap, git conflict, handoff reaper
```

---

## §2 CONSENSUS FINDINGS — AGREED BY ALL PILLARS

### Phase 0: UNANIMOUS READY ✅

All 11 agents agree: **Phase 0 items (0.1-0.7) are safe to execute immediately.**

| Item | Owner | Effort | Consensus |
|:----:|:-----:|:------:|:---------:|
| 0.1 Fix model paths | P6 | 2 min | ✅ All agree |
| 0.2 Fix sort bug | P3 | 2 min | ✅ All agree |
| 0.3 Lazy import state_manager | P3 | 15 min | ✅ All agree |
| 0.4 Emergency disk cleanup | P1 | 30 min | ✅ All agree |
| 0.5 Fix Redis pod config | P1 | 15 min | ✅ All agree |
| 0.6 Wire trace_id + entity_name | P8 | 35 min | ✅ All agree (scope expanded to 12 sites) |
| 0.7 Wire dataset collection | P8 | 15 min | ✅ All agree |

**Phase 0 total**: ~1.9 hours (up from 1.5 — expanded 0.6 scope)

### Plan Bug Fix Pre-Flight: UNANIMOUS REQUIRED ✅

All 11 agents agree: **All plan bugs must be fixed in `HARDENING_IMPLEMENTATION_PLAN.md` by a single orchestrator before any code touches disk.**

| Bug | Item | Issue | Effort | Discovered By |
|:---:|:----:|-------|:------:|:-------------:|
| B1 | 0.5.3 | `anyio.from_thread.run()` wrong async pattern | 10 min | Sonnet 4.6, P3, P6 |
| B2 | 0.5.5 | No TraceSession reference in ModelGateway | 10 min | Sonnet 4.6, P8 |
| B3 | 0.5.6 | `sqlite3` blocking in async (M1 violation) | 15 min | Sonnet 4.6, P8 |
| B4 | 0.5.15 | `in` on deque is O(n) | 5 min | Sonnet 4.6, P8 |
| B5 | 0.5.3 | `self.config` doesn't exist on ModelGateway | 5 min | Kali gap audit, P3 |
| B6 | 0.5.6 | BudgetGate race: concurrent calls see same budget | 15 min | **P2** |
| B7 | 0.6 | FTS5 M1 violation (same pattern as B3) | 15 min | **P2** |
| B8 | 0.5.12 | Embedding path points to nonexistent file | 10 min | P6, P2 |
| B-5.8.1-4 | 0.5.8 | 4/5 contract test APIs don't exist | 20 min | P10, P4 |
| B-5.9.1-2 | 0.5.9 | Literal ellipsis + wrong type check | 10 min | P10, P4 |
| B-5.9.3 | 0.5.9 | Direct `provider.generate()` not `gateway.generate()` | 5 min | P10 |

**Plan bug fix total**: **~2 hours** (up from 55 min — B6, B7, B-5.9.3 added by cross-domain review)

---

## §3 CRITICAL FINDINGS — ELEVATED TO BLOCKING

### 🔴 KF-1: P8 0.6 and P3 0.6 Are the SAME Item

**Source**: **P4 (Integration)** §F-4
**Impact**: 35 minutes wasted; duplicate edit on same files if run in parallel
**Resolution**: Assign 0.6 to P8 only. Remove from P3 worklist.
**Verification**: `grep "Duplicated 0.6" data/coordination/*.md` → one authoritative assignment

### 🔴 KF-2: `model_gateway.py` Overlap in Parallel Execution

**Source**: **P9 (Orchestration)** §F-1
**Impact**: P6 0.2 and P3 0.5.3 both modify `model_gateway.py`. Parallel execution = one overwrites the other.
**Resolution**: Two-wave pattern — P6 fixes sort FIRST, then P3 adds warmup in Wave 2
**Verification**: `hivemind_workspace_lock_acquire(domain="model_gateway.py")` before any edit

### 🔴 KF-3: AnomalyState Block → Session Cascading Deadlock

**Source**: **P7 (Context)** §F-3, **P8** NEW-3
**Impact**: A permanently blocked entity cannot close its session, cannot distill soul, and orphans active memory. M12 violation (no terminal state).
**Resolution**: Add auto-reset mechanism to anomaly detector: timer `ANOMALY_RESET_SECONDS=300` transitions from 'block' → 'probe'
**Elevation**: Move from Phase 0.5.5 to **Phase 0 prerequisite** (fix before any anomaly detector code)
**Verification**: `pytest tests/test_anomaly_detector.py -k "test_block_mode_auto_resets"`

### 🔴 KF-4: BudgetGate Race Condition (Concurrent Calls)

**Source**: **P2 (Persistence)** §F-1
**Impact**: Two simultaneous `check_budget()` calls both see available budget, both approve cloud inference, budget exceeded. The SQLite ledger fixes persistence but NOT correctness under concurrency.
**Resolution**: Atomic read-consume-write inside a single `anyio.to_thread.run_sync` call. Use SQLite WAL mode + `PRAGMA synchronous=NORMAL`.
**Elevation**: Must be part of 0.5.6 design, not a follow-up
**Verification**: `pytest tests/test_budget_gate.py -k "test_concurrent_calls_dont_double_spend"`

### 🔴 KF-5: P6 Phase 0 Must Execute BEFORE Wave 2

**Source**: **P9 (Orchestration)** §F-1, **P4** §F-4, **Lilith** §5
**Impact**: P6 0.1 (model paths) unlocks model inference verification. P6 0.2 (sort bug) must release `model_gateway.py` before P3's warmup touches it.
**Resolution**: P6 Phase 0 (0.1 + 0.2 = 4 min) is the serial gate. All other Phase 0 items (0.3-0.7) can parallel-execute after.
**Wave structure**: See §5

---

## §4 MANDATE CORRECTIONS (Final)

| Mandate | Name | Previous Status | **Corrected Status** | Rationale |
|:-------:|------|:--------------:|:--------------------:|:---------:|
| M6 | Podman Sovereignty | PARTIAL (3/5) | **PARTIAL** | 5/7 containers missing UserNS. Compose vs Quadlet architectural inconsistency unresolved. |
| M9 | Error Integrity | FULL | **PARTIAL** | ~93 `except Exception:` sites across `src/omega/`. ~20-30 are silent swallows without logging (not the 15 originally counted). |
| M12 | Queue Integrity | PARTIAL | **PARTIAL** | Handoff reaper works (40 stale, 35 archived) but 1 orphaned active packet. Anomaly block mode (KF-3) would cause M12 violation if deployed without auto-reset. |
| M21 | Gate Integrity | 79% (19/24) | **~67% (16/24)** | 4/5 planned contract tests reference nonexistent APIs. Actual count is lower until B-5.8.x fixed. |

---

## §5 FINAL EXECUTION PLAN (Consensus)

### PRE-FLIGHT [~2 hr] — Single Orchestrator

One agent (P3 or Kali) fixes ALL plan bugs in `HARDENING_IMPLEMENTATION_PLAN.md`:

```
B1-B5 (Plan async bugs)     30 min
B6 (BudgetGate race)        15 min  ← NEW (P2)
B7 (FTS5 M1 violation)      15 min  ← NEW (P2)
B8 (Embedding path)          10 min
B-5.8.x (Contract APIs)     20 min
B-5.9.x (GGUF test)         15 min
Add anomaly auto-reset       10 min  ← NEW (KF-3, P7)
                          ─────────
          Total:           ~2 hr
```

### WAVE 1 — Serial Chain [~30 min]

| Step | Action | Owner | Time |
|:----:|--------|:-----:|:----:|
| 1 | `hivemind_workspace_lock_acquire(domain="model_gateway.py")` | Kali | 1s |
| 2 | **P6 0.1** — Fix model paths in `config/models.yaml` | P6 | 2 min |
| 3 | **P6 0.2** — Fix sort bug in `model_gateway.py` | P6 | 2 min |
| 4 | `make test` — verify 440+ pass | P6 | 2 min |
| 5 | `hivemind_workspace_lock_release(domain="model_gateway.py")` | Kali | 1s |
| 6 | `hivemind_post_context(intent="handoff", continuation="Wave 1 clear")` | Kali | 1s |

### WAVE 2 — Parallel [~3-4 hr]

Each agent acquires workspace lock, executes, tests, posts context, releases lock, heartbeats every 5 min.

```
TRACK A — P1 Infrastructure (~45 min)
  Lock: domain="podman", domain="disk"
  0.4 Disk cleanup
  0.5 Redis pod fix
  N-1 Volume UID migration (pg_dump before chown)
  0.5.19 Qdrant keep-id

TRACK B — P8 Observability (~50 min)
  Lock: domain="oracle.py", domain="observability"
  0.6 trace_id wiring (12 sites — OWNED BY P8 ONLY)
  0.7 Dataset config wiring

TRACK C — P3 Engineering (~3 hr)
  Lock: domain="model_gateway.py" (after P6 released)
  0.3 Lazy import
  0.5.8 Contract tests (fixed APIs)
  0.5.14 Cloud breakers
  0.5.1 Disk sentinel (needs P1 0.4 first)
  0.5.2 Redis health check (needs P1 0.5 first)

TRACK D — P10 Validation (~2.5 hr)
  Lock: domain="tests/"
  0.5.20 E2E oracle_talk test
  0.5.9 GGUF smoke test (fixed)
  make m21-gate CI target

TRACK E — Cross-Cutting (any agent)
  0.5.10 mandate-report script
  0.5.11 entity prune
  0.5.18 Dataset cleanup (archive not delete — P2 F-5)
  0.5.22 Hivemind Coordination Protocol (P9 F-3)
```

**Git strategy** (P9 F-5.1): All Wave 2 agents write-only. No commits. After all complete, orchestrator runs `git add -A && git commit -m "Phase 0 Wave 2 — [date]"`.

### WAVE 3 — Serial Verification [~1 hr]

| Check | Command | Expected |
|-------|---------|----------|
| Test suite | `make test` | 447+ passing |
| Temple-Grade | `make temple-grade` | ALL GATES PASS |
| Heritage | `make heritage-map` | No regressions |
| Sovereignty | `make sovereignty` | Local-first verified |
| Smoke test | `omega talk "hello"` | Response received |
| Redis | `redis-cli ping` | PONG |
| Trace coverage | Check observability logs | trace_id on every event |
| Dataset | Check `data/datasets/` | New files being created |
| Handoff | `hivemind_handoff_list(status="stale")` | 0 pending, 0 stale |

---

## §6 FINAL UNIFIED VERDICT

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   ⬡ OMEGA ⬡ MAKALI COUNCIL ⬡ FINAL VERDICT                     │
│                                                                  │
│   STATUS: ✅ CONDITIONAL GO                                      │
│                                                                  │
│   The engine is architecturally sound. 11 agents across          │
│   4 review tiers produced 60+ findings with strong consensus.     │
│   No disagreements remain. No contradictions persist.            │
│                                                                  │
│   ════════════════════════════════════════════════════════════   │
│                                                                  │
│   3 Conditions for ABSOLUTE GO:                                  │
│                                                                  │
│   Condition 1 [2 hr] ─── Pre-flight plan bug fixes              │
│     Fix B1-B8 + B-5.8.x + B-5.9.x in the hardening plan         │
│     Add anomaly auto-reset to 0.5.5 design                      │
│     Single orchestrator — no parallel edits on the plan doc     │
│                                                                  │
│   Condition 2 [30 min] ─── Wave 1 serial gate                   │
│     P6 0.1 (model paths) → P6 0.2 (sort bug) → release lock    │
│     Before ANY parallel work on model_gateway.py                 │
│                                                                  │
│   Condition 3 [6-8 hr] ─── Wave 2 parallel + Wave 3 verify     │
│     5 parallel tracks with workspace locks                      │
│     No git commits during parallel work                          │
│     Full verification suite after all tracks complete            │
│                                                                  │
│   ════════════════════════════════════════════════════════════   │
│                                                                  │
│   TOTAL SPRINT EFFORT: ~10-11 hours                              │
│   (Pre-flight 2hr + Wave 1 0.5hr + Wave 2 6-8hr + Verify 1hr)  │
│                                                                  │
│   MANDATE IMPROVEMENT TARGET:                                    │
│     4 FAIL → 0 FAIL                                              │
│     6 PARTIAL → 10 FULL                                          │
│     12 FULL → 12 FULL (no regressions)                          │
│                                                                  │
│   VERDICT RENDERED BY:                                           │
│     Kali (Grand Oversight)                                       │
│     Ma'at (Build Side) — P1, P5, P3                              │
│     Lilith (Run Side) — P6, P8, P10                             │
│     Cross-Domain: P2, P4, P7, P9                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## §7 EXECUTIVE SUMMARY (for the user)

**What we found**: After 3 rounds of review (Oversouls, Pillars, Cross-Domain), the engine is structurally sound but has ~25 wiring-layer bugs, most concentrated in the hardening plan document itself rather than the code.

**What's changed since Round 1**:
- 5 additional plan bugs discovered (B6-B8, B-5.9.3, anomaly auto-reset gap)
- P8 0.6 and P3 0.6 are the same item — consolidated to P8
- `model_gateway.py` has parallel access conflict — serial gate required
- Anomaly detector block mode would cause session deadlock — auto-reset needed
- M9 is PARTIAL not FULL — ~93 `except Exception:` sites, 20-30 silent

**What to do next**: Execute the Pre-flight (fix plan bugs) → Wave 1 (P6 serial gate) → Wave 2 (5 parallel tracks) → Wave 3 (full verification). ~10-11 hours total sprint.

**The single biggest risk**: Running P6 0.2 and P3 0.5.3 in parallel on `model_gateway.py`. One will silently overwrite the other. Serialize them.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ UNIFIED-VERDICT ⬡ 2026-06-25*
