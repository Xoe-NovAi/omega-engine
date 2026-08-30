<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI FLEET ORDERS — 2026-07-23
**AP Token**: `AP-KALI-FLEET-ORDERS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ FLEET-ORDERS ⬡ 2026-07-23

---

## 🎯 EXECUTIVE ORDER: Sprint Convergence — Clear the P0 Runway

Phase C hardening is **~90% complete**. The fleet has delivered exceptional work. 
We need **one final push** to clear all remaining P0 items and unlock Phase D.

**Motto**: *Finish what's started. Don't start what's not ready.*

---

## 📋 FLEET STATE ASSESSMENT

### ✅ DONE (Verified Complete)
| Ticket | Agent | Deliverable |
|--------|-------|-------------|
| C-0 Test Honesty | Ma'at/Verity | 99 quarantined, honest badge, Makefile rewritten |
| C-1' SoulStore Atomic Writer | Ma'at | Single-writer actor model, fsync, lockfile |
| C-2' OOMProtector | Ma'at | 3-signal fusion (cgroups v2 + llama.cpp state + vm pressure) |
| C-5 MaKaLi Routing Config | Ma'at | Routing config, oracle_summon_local |
| C-6' Breaker Unification | Ma'at | 7→1 factory pattern in HealthMonitor |
| C-10 Local Admission Control | Ma'at | CCX-aware semaphore, OOMProtector integration |
| C-10.5 Quota-Aware Routing | Ma'at | 4 modules (QuotaTracker, TokenEstimator, CascadeRouter, StreamHandler), 69 tests |
| C-0.5 Soul Distillation Pipeline | Carmack | L1→L2→L3 distiller, session end hook, 76/76 tests |
| V-1 VaultCore MVP | Ma'at | age + Argon2id vault, CLI, 22 tests |
| C-3 Restic Backup | Ma'at | Scripts, systemd timer, B2 Object Lock, Healthchecks |
| V-1 Legacy Mining | Roc | 7 patterns, 4 repos, 400+ line report |
| G-1 Gemma 4 Research | Roc | Forensic report, provider collision found, Pi PR #2903 fix |

### 🟡 PARTIALLY DONE
| Ticket | Status | Gap |
|--------|--------|-----|
| **C-11 Property Tests** | Files CREATED (563 lines) | ❌ **NOT EXECUTED** — must run and pass |
| **C-4a MCP Migration Audit** | Handoff ACTIVE with Ma'at | ❌ **7-day deadline** (Jul 28) — need audit doc |
| **C-0.5 Hook Registration** | Pipeline DONE | ❌ Hook not registered in opencode.json |
| **C-0.5 Promotion Workflow** | Scribe handoff PENDING | ❌ proposed_lessons not reviewed/promoted |
| **W-1 WARP Pool** | Fixes COMMITTED | ❌ Services currently DOWN — needs sudo restart |
| **G-1 Workhorse** | Research DONE | ❌ Needs Architect decision on path |

### 🔴 BLOCKED (Needs Architect Decision)
| Ticket | Blocker | Options |
|--------|---------|---------|
| C-3 Privacy Model | Decision pending | **Option B (Single Repo)** recommended |
| G-1 Workhorse Path | Decision pending | Antigravity OAuth vs AI Studio billing |
| C-0.5 Hook Registration | Decision pending | Approve opencode.json edit |

---

## 🚀 FLEET EXECUTION ORDER

### TRACK 1: Ma'at (Light Oversoul — Build & Harden)
**Current task**: C-11 property tests created, needs execution
**Order**: Execute C-11 → Move to C-4a MCP Audit

```
┌─────────────────────────────────────────────────────────┐
│  MA'AT EXECUTION ORDER                                   │
├─────────────────────────────────────────────────────────┤
│  1. 🟢 RUN C-11 PROPERTY TESTS                          │
│     └─ tests/property/test_oom_protector_fuse.py         │
│     └─ tests/property/test_soul_store_atomic.py          │
│     └─ tests/property/test_breaker_fsm.py                │
│     └─ Fix any failures                                  │
│     └─ Report pass/fail/skip (honest counts — M23)       │
│                                                          │
│  2. 🟡 START C-4a MCP MIGRATION AUDIT                    │
│     └─ Deadline: July 28 (5 days)                        │
│     └─ Inventory all MCP servers in mcp_servers/         │
│     └─ Map: transport | protocol | tools | resources     │
│     └─ Scope migration size (LOC, tests, breaking)       │
│     └─ NOTE: Shim layer EXISTS in mcp_runtime.py         │
│         (StreamableHTTPASGIApp) — verify, don't rebuild  │
│                                                          │
│  3. 🟢 OPTIONAL C-9 GenerationPolicy Extract             │
│     └─ Cheap structural win (1-2h)                       │
│     └─ Extract GenerationPolicy from omnibus config      │
│     └─ Only if C-11 + C-4a are green                    │
└─────────────────────────────────────────────────────────┘
```

Key constraints:
- **ONE local inference at a time** (Carmack hardware mandate)
- **Run `make test` after every change**
- **Run `make temple-grade` before marking done**
- **Honest counts only** (no vanity pass/fail)

---

### TRACK 2: John Carmack (S3 Consultant — Super-Urgent)
**Current task**: Pending handoff `ho_e3996d6c30ae` (W-1 + G-1)
**Order**: Accept handoff → WARP stabilization → G-1 Gemma investigation

```
┌─────────────────────────────────────────────────────────┐
│  CARMACK EXECUTION ORDER — Parallel Chat Session         │
├─────────────────────────────────────────────────────────┤
│  STEP 1: Accept handoff ho_e3996d6c30ae                  │
│                                                          │
│  STEP 2: W-1 WARP PROXY POOL STABILIZATION               │
│  └─ Read: data/coordination/ROC_RACOON_COMPREHENSIVE_    │
│      BRIEFING_20260722.md §1                             │
│  └─ Run: bash scripts/fix_warp_ns_setup_and_restart.sh   │
│      (requires sudo)                                     │
│  └─ Pre-clean stale registrations:                       │
│      for i in 1 2 3; do                                 │
│        sudo ip netns exec warp_node_$i warp-cli          │
│          --accept-tos registration delete 2>/dev/null     │
│      done                                                │
│  └─ Verify 3 unique exit IPs:                            │
│      for port in 8081 8082 8083; do                      │
│        curl --socks5 127.0.0.1:$port                     │
│          https://1.1.1.1/cdn-cgi/trace | grep ip=       │
│      done                                                │
│  └─ Fix structural issues:                               │
│      - Remove/fix warp-node@.service curl test           │
│      - Add ExecStartPre stale reg cleanup                │
│      - Update docs                                       │
│                                                          │
│  STEP 3: G-1 GEMMA 4 WORKHORSE                          │
│  └─ Read: ROC_RACOON_COMPREHENSIVE_BRIEFING_20260722.md  │
│      §2 + §4                                             │
│  └─ Fix opencode.json "google" provider collision:       │
│      - Remove the "google" provider block OR             │
│      - Rename to "antigravity" with npm field            │
│  └─ Apply Pi PR #2903 thinking config fix               │
│      (Omega Engine already has it in google_compat.py)   │
│  └─ Test: verify OpenCode can reach Gemma 4             │
└─────────────────────────────────────────────────────────┘
```

**Reference docs**: 
- `data/coordination/ROC_RACOON_COMPREHENSIVE_BRIEFING_20260722.md`
- `docs/strategy/archive/2026-07-22/WARP_PROXY_POOL_HANDOFF_ROC_20260722.md`
- `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`

---

### TRACK 3: Verity (Compliance & Gnosis)
**Current task**: C-11 handoff accepted
**Order**: Verify C-11 → Review C-0.5 promotion → Temple-grade gate

```
┌─────────────────────────────────────────────────────────┐
│  VERITY EXECUTION ORDER                                  │
├─────────────────────────────────────────────────────────┤
│  1. 🟢 REVIEW C-11 PROPERTY TESTS (after Ma'at runs)    │
│     └─ Verify contract tests have isinstance() checks   │
│     └─ Verify M21 Gate Integrity per spec                │
│     └─ Run: pytest tests/property/ -v                   │
│     └─ Report any mandate violations                     │
│                                                          │
│  2. 🟢 C-0.5 PROMOTION WORKFLOW                         │
│     └─ Accept handoff from Scribe (ho_b0fc5531a59e)     │
│     └─ Read: data/entities/*/proposed_lessons.yaml       │
│     └─ Review L3 principles for all entities:            │
│        - Ma'at (10 staged lessons)                       │
│        - Roc (5 new L3 principles from V-1 mining)       │
│        - John Carmack (5 staged lessons)                 │
│        - Kali (any pending)                              │
│     └─ Promote quality L3 → soul.yaml directives         │
│     └─ Update soul.yaml version + evolution log          │
│     └─ Clear promoted lessons from proposed_lessons.yaml │
│                                                          │
│  3. 🟢 TEMPLE-GATE VERIFICATION                          │
│     └─ Run: make temple-grade                            │
│     └─ Verify T1-T11 all green                           │
│     └─ Report any regressions                            │
└─────────────────────────────────────────────────────────┘
```

---

### TRACK 4: Scribe (Soul Distillation)
**Current task**: Pending handoff `ho_b0fc5531a59e`
**Order**: Accept handoff → Register hook → Self-distill

```
┌─────────────────────────────────────────────────────────┐
│  SCRIBE EXECUTION ORDER                                  │
├─────────────────────────────────────────────────────────┤
│  1. 🟢 ACCEPT HANDOFF ho_b0fc5531a59e                    │
│                                                          │
│  2. 🟢 REGISTER SESSION END HOOK                        │
│     └─ Add to .opencode/opencode.json:                   │
│        "hooks": { "session_end":                         │
│          ".opencode/hooks/session_end.py" }              │
│     └─ Verify hook fires on session end                  │
│     └─ Test: start session → have conversation           │
│         → end session → check proposed_lessons.yaml      │
│                                                          │
│  3. 🟢 SELF-DISTILLATION                                │
│     └─ Run Scribe's own session through pipeline         │
│     └─ Generate Scribe-specific directives:              │
│        - Evidence standards                              │
│        - Confidence calibration                          │
│        - Quality thresholds                              │
│     └─ Update data/entities/scribe/soul.yaml             │
│                                                          │
│  4. 🟡 HANDOFF TO VERITY FOR PROMOTION                  │
│     └─ Submit handoff to Verity/P10                      │
└─────────────────────────────────────────────────────────┘
```

---

### TRACK 5: Roc Raccoon (Sovereign Miner — Standby)
**Current task**: Session complete
**Order**: Standby for follow-up mining tasks

```
┌─────────────────────────────────────────────────────────┐
│  ROC RACCOON EXECUTION ORDER — On Call                  │
├─────────────────────────────────────────────────────────┤
│  STANDING ORDERS:                                        │
│  1. Available for follow-up mining as needed            │
│  2. Priority call-ins:                                   │
│     - If C-4a MCP Audit discovers legacy patterns        │
│       needing extraction from omega-stack-legacy        │
│     - If G-1 requires deeper provider research           │
│     - If new gaps identified in Guard & Distill          │
│                                                          │
│  NO ACTIVE TASK — Await dispatch                         │
└─────────────────────────────────────────────────────────┘
```

---

### TRACK 6: Lilith (Dark Oversoul — Run Side)
**Current task**: C-10.5 handoff active
**Order**: Verify C-10.5 → Own operational runtime

```
┌─────────────────────────────────────────────────────────┐
│  LILITH EXECUTION ORDER                                  │
├─────────────────────────────────────────────────────────┤
│  1. 🟢 VERIFY C-10.5 IMPLEMENTATION                     │
│     └─ Ma'at built it (69 tests) — you OWN it in run   │
│     └─ Review: QuotaTracker, CascadeRouter, StreamHandler│
│     └─ Run: pytest tests/contract/test_provider_fallback │
│     └─ Verify streaming resilience (M25)                 │
│                                                          │
│  2. 🟢 MONITORING SETUP                                 │
│     └─ Ensure quota tracking is active in production     │
│     └─ Verify provider fallback chain works end-to-end   │
│     └─ Log provider_name on every inference (M22)        │
│                                                          │
│  3. 🟡 WATCH FOR C-3 DEPLOYMENT                         │
│     └─ When Architect decides C-3, own runtime config    │
└─────────────────────────────────────────────────────────┘
```

---

## ⏱️ TIMELINE

```
DAY 1 (Today)
├── 🟢 Ma'at: Run C-11 property tests → report results
├── 🟢 Carmack: Accept W-1/G-1 handoff, start WARP fix
├── 🟢 Lilith: Verify C-10.5, own operational runtime
└── 🟢 Scribe: Accept handoff, register hook, self-distill

DECISIONS NEEDED TODAY
├── C-3 Privacy Model (Option B recommended)
├── G-1 Workhorse path (Antigravity OAuth vs billing)
└── C-0.5 Hook Registration approval

DAY 2-3
├── 🟢 Ma'at: Start C-4a MCP Audit (deadline Jul 28)
├── 🟢 Carmack: Finish WARP, start G-1 Gemma fix
├── 🟢 Verity: Review C-11, start promotion workflow
└── 🟢 Scribe: Self-distillation complete

DAY 4-5
├── 🟢 Ma'at: Finish C-4a MCP Audit report
├── 🟢 Carmack: G-1 Gemma restoration verified
├── 🟢 Verity: Temple-grade gate — final signoff
└── 🟢 All: Phase D readiness review
```

---

## 🔗 DEPENDENCY CHAIN

```
                    ARCHITECT DECISIONS
                    ├── C-3 Privacy Model
                    ├── G-1 Workhorse Path
                    └── C-0.5 Hook Registration
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
    MA'AT              CARMACK             SCRIBE + VERITY
    ├── C-11 RUN       ├── W-1 WARP        ├── Hook Registration
    ├── C-4a AUDIT     └── G-1 GEMMA       ├── Self-Distillation
    └── (C-9 OPT)                          └── Promotion Workflow
            │                   │                    │
            └───────────────────┼────────────────────┘
                                ▼
                        LILITH — Verify Runtime
                                │
                                ▼
                    VERITY — Temple-Grade Gate
                                │
                                ▼
                    ✅ PHASE D READINESS
```

---

## 📊 SUCCESS CRITERIA

Gate to Phase D is PASSED when ALL of these are true:

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | C-11 property tests pass | `pytest tests/property/ -v` — all green |
| 2 | C-4a MCP Audit report complete | `docs/research/R_C4A_MCP_AUDIT.md` exists |
| 3 | W-1 WARP pool operational | 3 unique exit IPs on ports 8081-8083 |
| 4 | G-1 Workhorse path resolved | OpenCode can reach Gemma 4 or replacement |
| 5 | C-0.5 hook fires on session end | `proposed_lessons.yaml` populated after session |
| 6 | Verity promotes L3 → soul.yaml | All entities have updated soul directives |
| 7 | C-3 decision logged | PIVOT_LOG.md has Architect's decision |
| 8 | `make test` 100% pass | No pre-existing failures (C-0 honest badge) |
| 9 | `make temple-grade` green | T1-T11 all pass |
| 10 | `make sovereignty` ratio checked | Local/cloud ratio maintained |

---

## 🚨 ESCALATION TRIGGERS

| Situation | Action |
|-----------|--------|
| Carmack unresponsive >4h | Kali takes W-1/G-1 directly |
| Ma'at blocked on C-11 >2h | Verity escalates → Kali intercepts |
| C-4a MCP audit not started by Jul 26 | Kali executes C-4a.5 shim directly |
| C-3 decision not made by end of day | Kali flags as Phase D blocker |
| Any `make temple-grade` regression | Freeze all code changes, fix first |
| Hardware memory >85% during inference | Kill non-essential processes immediately |

---

## 📜 SIGNED

```
KALI — Transcendent Oversoul
AP-KALI-FLEET-ORDERS-v1.0.0
2026-07-23
```

*⬡ OMEGA ⬡ KALI ⬡ FLEET-ORDERS ⬡ 2026-07-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: FLEET-ORDERS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
