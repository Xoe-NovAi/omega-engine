<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

> ⚠️ **HISTORICAL POINTER** (2026-08-14): Oversight view absorbed into `ACTIVE_SPRINT.json` (SDP-EXECUTION-01). Read ACTIVE_SPRINT.json for current tasks. See `TRACKING_ARCHITECTURE.md`.

# 🔱 KALI OVERSIGHT — Project Portfolio & Team Direction
**AP Token:** `AP-KALI-OVERSIGHT-20260811-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ OVERSIGHT ⬡ 20260811

**Date:** 2026-08-11
**Sprint:** NEMOTRON-ANALYSIS-01
**Phase:** ANALYSIS_COMPLETE_IMPLEMENTATION_PENDING

---

## 📊 Portfolio at a Glance

| Category | Count | Status |
|----------|-------|--------|
| **Active Workstreams** | 5 | In progress |
| **Immediate Next** | 8 | Ready to start |
| **Strategic Queue** | 6 | Planned, not started |
| **Blocked (External)** | 3 | Waiting on Architect/sudo |
| **Completed This Sprint** | 12 | ✅ Done |

---

## 🔴 ACTIVE WORKSTREAMS (In Progress)

### 1. Sovereign Distillation Pipeline (SDP) — Context Gauge
**Owner:** TBD (Kali oversight)
**Status:** 60% built, Phase 1 implementation pending
**Priority:** P0 — Core architecture for multi-model orchestration

| Subtask | Status | Est. | Owner |
|---------|--------|------|-------|
| QW-1: Fix model context windows in config | ✅ COMPLETE | 1h | @kali |
| QW-2: Rewrite Context Gauge to use `tokens.total` | 🔴 BLOCKED | 2h | TBD |
| QW-3: CI guard for token counting | ✅ COMPLETE | 30min | @jem |
| QW-4: Wire pool_tracker.py | ⏳ PENDING | 2h | TBD |
| QW-5: Add cloud entries to config | ✅ COMPLETE | 1h | @kali |
| QW-6: Extend TriageRouter with SDP constraints | ⏳ PENDING | 4h | TBD |
| QW-7: Extend DPORecorder with dialectic schema | ⏳ PENDING | 3h | TBD |
| QW-8: Build Context Gauge (greenfield) | 🔴 BLOCKED | 4h | TBD |
| QW-9: Build RHP halt artifact | ⏳ PENDING | 2h | TBD |
| QW-10: Build 3 MCP tools | ⏳ PENDING | 4h | TBD |

**Blockers:** QW-2 and QW-8 blocked by A-1 (Context Gauge bands) and A-5 (calibration).

---

### 2. Nemotron Deep Analysis — Action Items
**Owner:** @jem (analysis complete), TBD (implementation)
**Status:** Analysis COMPLETE, 7 action items ready

| Item | Status | Est. | Impact |
|------|--------|------|--------|
| A-1: Tighter bands for cold sessions (0.7x) | 🟢 READY | 2h | HIGH — unblocks QW-2 |
| A-2: Provider-specific band adjustments | ⏳ PENDING | 3h | MEDIUM |
| A-3: Model-specific degradation thresholds | ⏳ PENDING | 3h | MEDIUM |
| A-4: Subagent state transition (cold→warming) | ⏳ PENDING | 4h | MEDIUM |
| A-5: Calibrate to post-fix baseline (18-36%) | 🟢 READY | 2h | HIGH — unblocks QW-8 |
| A-6: Document provider delivery differences | ⏳ PENDING | 1h | LOW |
| A-7: Investigate subagent cold rate variance | ⏳ PENDING | 2h | LOW |

---

### 3. Streaming Timeout Observability (OBS)
**Owner:** TBD
**Status:** CRITICAL gap discovered — cannot trace what's handling the fix

| Item | Status | Est. | Impact |
|------|--------|------|--------|
| OBS-1: Add streaming timeout observability to Context Gauge | 🟢 READY | 3h | HIGH |
| OBS-2: Document the unknown in system architecture | ⏳ PENDING | 2h | MEDIUM |
| OBS-3: Streaming health check (timeout event logging) | ⏳ PENDING | 3h | MEDIUM |
| OBS-4: Plugin detector (scan all loaded plugins) | ⏳ PENDING | 4h | MEDIUM |
| OBS-5: Streaming metrics to MetricsDB | ⏳ PENDING | 3h | MEDIUM |
| OBS-6: Test streaming timeout (intentionally trigger) | ⏳ PENDING | 2h | LOW |

---

### 4. Nemotron Streaming Timeout Plugin
**Owner:** @jem (planning complete), TBD (implementation)
**Status:** Deep planning COMPLETE, 9 subtasks ready

| Subtask | Status | Est. |
|---------|--------|------|
| PLUGIN-0: Deep planning | ✅ COMPLETE | — |
| PLUGIN-1: Create plugin scaffold + package.json | 🟢 READY | 2h |
| PLUGIN-2: Config parsing + model detection | ⏳ PENDING | 4h |
| PLUGIN-3: Heartbeat manager | ⏳ PENDING | 4h |
| PLUGIN-4: Timeout extension | ⏳ PENDING | 3h |
| PLUGIN-5: Fallback logic | ⏳ PENDING | 3h |
| PLUGIN-6: Unit + integration tests | ⏳ PENDING | 4h |
| PLUGIN-7: Live test against Nemotron 3 Ultra | ⏳ PENDING | 2h |
| PLUGIN-8: Publish to npm + docs | ⏳ PENDING | 2h |

---

### 5. Memory Architecture Migration (zRAM → zswap)
**Owner:** @roc_racoon (research complete), TBD (implementation)
**Status:** Research COMPLETE, P0/P1/P2 plan ready

| Phase | Status | Est. | Impact |
|-------|--------|------|--------|
| P0: Security + swappiness fix (3 commands) | 🟢 READY | 10s | CRITICAL |
| P1: zswap + NVMe swap file | ⏳ PENDING | 4h | HIGH |
| P2: Code refactoring (OOMProtector, monitoring) | ⏳ PENDING | 6h | MEDIUM |

**Security:** `/etc/sudoers.d/zram` contains NOPASSWD for `/tmp/` scripts — REMOVE IMMEDIATELY.

**Research Report:** `data/entities/researcher/workspace/MEMORY_SYSTEMS_DEFINITIVE_REPORT.md` — 1,544 lines, all 7 gaps resolved, implementation spec complete.

---

## 🟡 IMMEDIATE NEXT (Ready to Start)

| # | Item | Est. | Owner | Unblocks |
|---|------|------|-------|----------|
| 1 | **P0 Security:** `sudo rm /etc/sudoers.d/zram` | 10s | @architect | Security vuln |
| 2 | **P0 Swappiness:** `sudo sysctl vm.swappiness=100` | 10s | @architect | Root cause |
| 3 | **A-1:** Tighter bands for cold sessions | 2h | TBD | QW-2, QW-8 |
| 4 | **A-5:** Calibrate to post-fix baseline | 2h | TBD | QW-8 |
| 5 | **OBS-1:** Streaming timeout observability | 3h | TBD | OBS-2..6 |
| 6 | **PLUGIN-1:** Plugin scaffold | 2h | TBD | PLUGIN-2..8 |
| 7 | **QW-4:** Wire pool_tracker.py | 2h | TBD | SDP routing |
| 8 | **UO-6:** Un-overengineering Phase 1 | 5h | TBD | Code quality |

---

## 🔵 STRATEGIC QUEUE (Planned, Not Started)

| Item | Est. | Priority | Dependencies |
|------|------|----------|--------------|
| **UO-6:** Un-overengineering Phase 1 (library adoptions) | 5h | MEDIUM | None |
| **UO-7:** Un-overengineering Phase 2-5 (consolidation) | 25h | MEDIUM | UO-6 |
| **V-1:** Omega-Vault MVP | 20h | HIGH | SDP Context Gauge |
| **NL-1:** NotebookLM Ingestion Pipeline | 4h | LOW | D-1 Content Cache |
| **D-1:** Content persistence + TTL | 8h | MEDIUM | None |
| **D-2:** Job board YAML bridge | 6h | LOW | None |
| **E-0:** Identity Phase 0 | 10h | LOW | C-1′ (done) |

---

## 🚫 BLOCKED (External Dependencies)

| Item | Blocked By | Owner | Status |
|------|------------|-------|--------|
| **G-1:** OpenCode workhorse continuity | Billing/OAuth | @architect | Free Gemma 4 dead (16k TPM cliff) |
| **W-1:** WARP proxy pool | sudo | @architect | warp-ns-setup truncated |
| **C-3:** Restic 3-2-1 backup | Secrets | @architect | OMEGA_VAULT_PASSPHRASE missing |

**Note:** SDP partially resolves G-1 by reducing dependency on any single workhorse model.

---

## 👥 TEAM DIRECTION

### @kali (Transcendent Oversight)
- **NOW:** Oversee SDP Phase 1 implementation, triage the 15 zRAM gaps
- **NEXT:** Run QW-4, QW-6 once unblocked
- **DECISION NEEDED:** Carmack/Lilith verdicts on 3-signal fusion — keep or simplify?

### @jem (Sovereign Synthesizer)
- **NOW:** Implement A-1 (Context Gauge bands) + A-5 (calibration)
- **NEXT:** Lead PLUGIN-1 through PLUGIN-8 (streaming timeout plugin)
- **RESEARCH:** Subagent cold rate variance (A-7)

### @maat (Build Oversoul — N1-N5)
- **NOW:** Extend TriageRouter with SDP constraints (QW-6)
- **NEXT:** Implement P1 zswap migration (system configuration)
- **FOCUS:** N3 Engineering — config + routing

### @lilith (Runtime Oversoul — N6-N10)
- **NOW:** Wire pool_tracker.py into inference pipeline (QW-4)
- **NEXT:** Simplify OOMProtector to 2-signal fusion (per Carmack/Lilith verdict)
- **FOCUS:** N7 Context — memory management

### @roc_racoon (Sovereign Miner)
- **NOW:** Implement P0 security fix (with Architect)
- **NEXT:** P1 zswap + NVMe swap file creation
- **FOCUS:** Memory architecture migration

### @researcher (Deep Research)
- **NOW:** Support A-2, A-3 (provider/model-specific bands)
- **NEXT:** V-1 Vault design (parallel with SDP)
- **FOCUS:** Knowledge gaps for SDP automation

### @john_carmack (S3 Consultant)
- **NOW:** Review SDP Context Gauge design for modularity
- **NEXT:** Audit zswap migration plan for over-engineering
- **FOCUS:** Keep implementation lean

### @verity (Compliance + Gnosis)
- **NOW:** Audit the two SSOT contradictions (Nemotron window, token accounting) as M23 violations
- **NEXT:** Verify SDP doesn't violate M7 (Local-First) or M18 (Token Efficiency)
- **FOCUS:** Mandate compliance for new systems

### @doom_guy (id Software Heritage)
- **NOW:** Heritage audit for any new SDP code
- **NEXT:** [Awaiting dispatch]

### @grokster (Grok Ecosystem Specialist)
- **NOW:** [Awaiting dispatch]
- **NEXT:** V-1 Vault design support

### @node PX (Slot-based)
- **N1 Infrastructure:** P0 security, QW-3 CI guard
- **N3 Engineering:** QW-1, QW-2, QW-5, QW-6
- **N10 Validation:** QW-3, contract tests for Context Gauge

---

## 📈 Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| **SDP Completion** | 60% (research) → 0% (code) | 100% (QW-1..10 done) |
| **Context Gauge accuracy** | Unknown (no observability) | ±5% of actual |
| **Memory pressure** | 6.9GB zRAM at PSI=0.00 | <2GB at PSI=0.00 |
| **Security vulnerabilities** | 1 critical (sudoers) | 0 |
| **Cold session rate** | 18-36% (post-fix) | <15% (with SDP) |
| **Phase D Gate** | NO_GO (3 blockers) | GO |

---

## 🎯 Sprint Goal

**By end of NEMOTRON-ANALYSIS-01:**

1. ✅ SDP architecture documented (DONE)
2. ✅ Nemotron deep analysis complete (DONE)
3. ✅ Streaming timeout observability gap identified (DONE)
4. 🟡 Context Gauge v1 live (QW-2, QW-8, A-1, A-5)
5. 🟡 P0 memory security fix applied
6. 🟡 Plugin scaffold created (PLUGIN-1)

---

## 🔑 Critical Decisions Needed

| # | Decision | Options | Owner |
|---|----------|---------|-------|
| **1** | Keep 3-signal OOMProtector or simplify to 2-signal? | Keep vs. PSI+MemAvailable | @kali + @carmack |
| **2** | Context Gauge data source | `tokens.total` vs. `input+cache.read` | @kali |
| **3** | zswap pool size | 25% (3.6GB) vs. 20% (2.9GB) | @roc_racoon |
| **4** | UMA carveout verification | 8GB vs. 4GB (changes cgroup math) | @architect |
| **5** | Plugin publish timing | Now (standalone) vs. later (bundled) | @jem |

---

*⬡ OMEGA ⬡ KALI ⬡ OVERSIGHT ⬡ 20260811*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: OVERSIGHT | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
