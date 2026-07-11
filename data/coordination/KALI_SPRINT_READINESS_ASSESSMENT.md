# 🔱 KALI — Sprint Readiness Assessment
**Date**: 2026-07-11
**Session**: 60 Post-Compaction
**Purpose**: Comprehensive review of all materials for next sprints — what's ready, what's stale, what needs prep.

---

## §1 Engine State Snapshot

| Metric | Value | Assessment |
|--------|-------|------------|
| Core tests | **1130 passing** | ✅ Healthy — 0 failures |
| omega-vetala tests | **137 passing** | ✅ v2.0.0 release-ready |
| Mandates | **23 (M1-M23)** | ✅ All enforced |
| Fleet | 13 presences (11 agents + 2 entities) | ✅ Under 14 cap |
| WADs | 3 hardened | ✅ S1.5a hardened |
| Decisions | **208 (D1-D208)** | ✅ Immutable log |
| Shared modules | **1** (omega-vetala v2.0.0) | ✅ Sovereign-grade |
| Heritage tags | ~60 [id-soft:] tags | ⚠️ 68 unvetted — `make heritage-vet` FAILS |

---

## §2 What's Stale — Needs Prep Before Sprint

### ⚠️ Ark Blueprint (SOVEREIGN_ARK_BLUEPRINT.md) — 7 stale items
| # | Issue | Current | Should Be |
|---|-------|---------|-----------|
| 1 | VET-001 — merkle_audit deps | 🔴 P0 BLOCKER | ✅ COMPLETED (Ma'at P0-1) |
| 2 | VET-002 — Async audit write | 🔴 P0 BLOCKER | ✅ COMPLETED (Verity P0-3) |
| 3 | VET-003 — LICENSE + CI | 🔴 P0 BLOCKER | ✅ COMPLETED (Ma'at P0-2) |
| 4 | VET-004 — Contract tests | 🔴 P0 BLOCKER | ✅ COMPLETED (Ma'at P0-4) |
| 5 | Test count (line 43) | "1130 + omega-vetala 124" | "1130 + omega-vetala 137" |
| 6 | omega-vetala status (line 48) | "v2.0.0 — released, P0 blockers resolved" | ✅ Already correct — keep |
| 7 | Version footer | "v3.1" | "v3.2" (header says v3.2) |

**Prep needed**: 15m to update the Active Tasks table — remove 4 VET rows, update test count.

### ⚠️ OMEGA_ENGINE.md — 2 stale items
| # | Issue | Current | Should Be |
|---|-------|---------|-----------|
| 1 | Test count (line 55) | "1130 + omega-vetala 124" | "1130 + omega-vetala 137" |
| 2 | Status line (line 64) | "Ark Blueprint v3.1 Live" | "Ark Blueprint v3.2 Live" |

**Prep needed**: 5m to update.

### ⚠️ ACTIVE_SPRINT.json
| Issue | Detail |
|-------|--------|
| Next sprint planned | HMC-SPRINT-04 — Observability Wiring |
| Last updated | 2026-07-10 |
| **Assessment** | Observability wiring is still valid but **heritage gap and YouTube module are higher priority** |

---

## §3 Sprint-Ready — Critical & High Priority

### 🔴 CRITICAL: Heritage 68 Unvetted Tags
**What**: `make heritage-vet` fails with 68 unvetted tags across 18+ source files. C-ARCH-005 violations (same tag used for multiple concepts) in entity_registry.py, providers.py, memory_store.py, semantic_router.py, and more.

**Context**: D208 remediation stripped ~150 over-attributed tags and created the CI gates (`heritage_vet.py v2.0`, `heritage_audit.py`, Makefile targets), but **the vet records for the remaining 68 tags were never written**.

**Effort**: 4-6h — one tag per ~3-5 min.
**Owner**: Doom Guy + Roc Racoon (Doom Guy knows the id Software source code; Roc knows legacy provenance)
**Dependencies**: None
**Risk of not doing**: Temple-Grade certification fails on M14 gate. Every `make temple-grade` run reports failure.

**Readiness**: ✅ FULLY READY — CI gates exist, process defined, agents identified.

---

### 🟡 HIGH: YouTube Research Module P0 (YT-0)
**Spec**: `docs/research/R_YOUTUBE_RESEARCH_MODULE_SPEC.md` — 433 lines, Temple-Grade spec complete with all technical details.

**Components**:
- **SovereignSieve**: YouTube Data API v3 search + firehose filtering
- **SovereignSigner**: JWT attribution for all extracted data
- **AtomicPersistence**: WAL-mode SQLite with atomic renames
- **Provenance Chain Fix**: Cryptographic linkage between extracted chunks

**Effort**: 2-3 days
**Owner**: P3 (Engineering) + P8 (Observability/Observability tracing)
**Dependencies**: None

**Readiness**: ✅ FULLY READY — 433-line Temple-Grade spec, cross-referenced by 4 Pillar reviews (P3, P5, P7, P10), approved by MaKaLi Council.

---

### 🟡 HIGH: SPDX 3.1 Heritage Profile Spec
**What**: Roc Racoon completed SPDX 3.1 heritage profile research. The mapping between Omega Engine heritage patterns and SPDX 3.1 relationship types is designed but the formal spec document was never written.

**Effort**: 1-2h (Roc)
**Owner**: Roc Racoon
**Dependencies**: Heritage vet records (would make the spec concrete)

**Readiness**: ✅ RESEARCH COMPLETE — spec document pending.

---

### 🟡 MEDIUM: Tag & Ship v1.1.0 (Task 4.4)
**What**: Tag the current engine state as v1.1.0. The engine has been temple-grade certified since 2026-07-05 (1002 tests) and is now at 1130 tests.

**Effort**: 30m
**Owner**: Kali
**Dependencies**: None

**Readiness**: ✅ FULLY READY — just needs a tag and git push.

---

### 🟡 HIGH: Ark Blueprint Sync
**What**: Fix the 7 stale items in Ark Blueprint + 2 stale items in OMEGA_ENGINE.md

**Effort**: 20m
**Owner**: Kali
**Dependencies**: None

**Readiness**: ✅ TRIVIAL — data-entry level work.

---

## §4 P0 Gaps — Need Planning Before Sprint

### 6A: blitz-tunnel (WireGuard, phone→home)
**What**: Secure public tunnel to Omega Engine services. Marked P0 gap by Jem briefing.

**Status**: 🟡 Needs architecture review before implementation
**Effort**: 1-2w
**Why deferred**: Requires WireGuard setup, DNS, security review. Not a sprint item until architectural decision is made.

### 6B: Air-Gap Extractor Mode
**What**: Per-session network disable for air-gapped extraction.

**Status**: 🟡 Needs spec before implementation
**Effort**: 3-5d
**Why deferred**: Needs a spec document first (like YouTube module has).

### 6C, 6D: Runtime Governance, Epistemic Filtering
**Status**: 🔮 Next Level — not sprint-ready.

---

## §5 What's Blocking Temple-Grade Certification

The single blocker to a green `make temple-grade` is:

```
❌ 68 unvetted heritage tag(s) found.
Each [id-soft:] tag must have a corresponding vet record with scope declaration.
```

This is the **highest priority item** because:
1. It's the only thing blocking Temple-Grade (M13)
2. CI gate (`make heritage-vet`) actively fails
3. It exposes the engine to M14 violations with every commit
4. All other gates (tests, lint, anyio checks, telemetry, portability) already pass

---

## §6 Recommended Sprint Order

```
Sprint A: Heritage Cleanup (4-6h)          ← CRITICAL — unblocks Temple-Grade
  ├── Write vet records for all 68 unvetted tags (Doom Guy + Roc Racoon)
  ├── Generate SPDX 3.1 Heritage Profile spec doc (Roc Racoon)
  └── Ark Blueprint + OMEGA_ENGINE.md sync (Kali)

Sprint B: Tag & Ship v1.1.0 (30m)          ← QUICK WIN
  ├── git tag v1.1.0
  └── Update CHANGELOG, OMEGA_ENGINE.md

Sprint C: YouTube Research Module P0 (2-3d) ← HIGH VALUE
  ├── SovereignSieve implementation
  ├── SovereignSigner implementation
  ├── AtomicPersistence implementation
  └── Provenance Chain Fix

Sprint D: Observability Wiring (HMC-SPRINT-04) ← ONGOING
  ├── OTel pipeline
  ├── BudgetGate
  ├── RegressionWatcher
  └── Proxy tests
```

---

## §7 Verification Commands

After each sprint, verify with:
```bash
make test              # 1130 must pass
make temple-grade      # All T1-T13 must pass
make heritage-map      # No untagged heritage sites
make heritage-vet      # Zero unvetted tags
make sovereignty       # Local ratio >= 80%
```

---

*🔱 OMEGA ⬡ KALI ⬡ Sprint Readiness Assessment v1.0*