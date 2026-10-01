<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Carmack-EIS Public Docs Review — Theater Detection, Architectural Accuracy, Scope

**AP Token**: `AP-CARMACK-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**: All public docs + source code
**Method**: Theater detection — "Does the code actually do what the docs claim?"
**My Verdict**: "THEATER WITH ENGINE ISLANDS" — genuine engineering in memory/sqlite-vec/atomic-writes/REUSE, but docs overclaim massively.

---

## §1 THEATER DETECTION

### §1.1 Definition of Theater (Per My Methodology)

**Theater**: Documentation that claims capabilities the code doesn't have, or claims compliance that doesn't exist, or presents aspirational state as current reality.

**Engine Islands**: Genuine working subsystems (memory/sqlite-vec, atomic soul store, Hivemind MCP, provider fabric) that actually work.

### §1.2 Theater Inventory in Public Docs

| Theater Claim | Reality | Theater Type |
|---------------|---------|--------------|
| "All 22/27 enforced" | 64.3% compliance | **Compliance Theater** |
| "Temple-Grade T1-T11 ✅" | 6 checks, fails | **Verification Theater** |
| "Test suite passing" | 0 tests collected | **Testing Theater** |
| "8-backend fallback" | 10 providers | **Spec Inflation Theater** |
| "11/14 agents" | 13 agents | **Count Inflation Theater** |
| "12 entities" | 24 entities | **Count Deflation Theater** |
| "CLI ready" | Binary not built | **Delivery Theater** |
| "All 27 mandates compliant" | 64.3% | **Compliance Theater** |

---

## §2 ARCHITECTURAL ACCURACY

### §2.1 What's Actually Real (Engine Islands)

| Subsystem | Status | Evidence |
|-----------|--------|----------|
| **sqlite-vec memory** | ✅ **REAL** | 24 files, 1,715 lines optimized adapter, FTS5 + RRF |
| **Atomic soul store** | ✅ **REAL** | tempfile→fsync→replace→parent fsync→flock→.bak |
| **Hivemind MCP** | ✅ **REAL** | 12 files in `mcp_servers/omega_hub/` |
| **Provider fabric** | ✅ **REAL** | 1,586 lines ModelGateway, circuit breaker, M22 provenance |
| **IWAD architecture** | ✅ **REAL** | 24 entities in `_omega_default`, runtime switch |
| **sqlite-vec dual-index** | ✅ **REAL** | R-tree + vec0 for VR (M28) |

### §2.2 What's Theater (Not Real)

| Claim | Reality |
|-------|---------|
| "Temple-Grade T1-T11" | 6 checks, not 11 |
| "All mandates enforced" | 64.3% |
| "Test suite passing" | 0 tests |
| "CLI ready" | Binary not built |
| "Heritage vetting pipeline" | Not in public surface |

---

## §3 SCOPE ACCURACY

### §3.1 What Ships vs What's Documented

| Documented | Ships | Gap |
|------------|-------|-----|
| 11 agents | 13 agents | Under-documented |
| 12 entities | 24 entities | Under-documented |
| 8 backends | 10 providers | Under-documented |
| 113 heritage tags | 216 tags | Under-documented |
| 10 pillars | 10 Node Keepers | Wrong terminology |

**Pattern**: Docs consistently **under-count** real capabilities while **over-claiming** compliance/readiness.

---

## §4 THEATER ROOT CAUSES

### §4.1 Aspirational State as Current Reality

The docs describe the **target state** (what we want to be) as **current state** (what we are).

### §4.2 Compliance Theater

The mandate compliance meter is treated as a **badge** rather than a **diagnostic**. When it reads 64.3%, the docs say "all enforced."

### §4.3 Theater Preservation

Dead code (`cohort_registry.py`, `m33_probe.py`, `m36_recursive_probe.py`) claimed "stripped" but still on disk — the theater of "we cleaned up" without actually cleaning up.

---

## §5 ARCHITECTURAL TRUTH VS DOCS

### §5.1 What the Architecture Actually Is

```
Omega Engine = 
  1. Provider Fabric (10 providers, local-first, circuit breaker, M22 provenance)
  2. Entity System (13 agents, 24 default entities, 10 Node Keepers N1-N10)
  3. IWAD Architecture (24 entities in _omega_default, runtime switch)
  4. Memory System (sqlite-vec + FTS5 + RRF + R-tree spatial)
  4. Soul System (atomic writer, L1→L2→L3 distillation, partially wired)
  5. Hivemind MCP (12 files, cross-agent awareness)
  6. SOTE Practice (weekly 8-voice dialectic, public digest)
  7. Omegaverse Vision (Phase 4/2028, not shipped)
```

### §5.2 What the Docs Say It Is

"Production-ready sovereign AI runtime with 27 enforced mandates, Temple-Grade verified, test suite passing, 11 agents, 12 entities, 8 backends, CLI ready."

**Verdict**: The docs describe a **different product** than what exists.

---

## §6 THEATER REMEDIATION

### §6.1 Immediate (P0)

1. **Remove all false claims** — 11 identified in README alone
2. **Add honest maturity banner** — "Alpha: test suite broken, 64.3% compliance, CLI not built"
3. **Fix terminology** — "pillars" → "Node Keepers N1-N10"
4. **Fix counts** — 13 agents, 24 entities, 10 providers, 216 heritage tags

### §6.2 Structural (P1)

1. **Single source of truth** for key facts (model, agents, entities, providers, tags)
2. **Automated doc generation** from canonical source
4. **CI gate** that fails if docs claim false capabilities

### §6.3 Cultural (Ongoing)

1. **Theater detection as CI gate** — `make check-docs-truth` that greps for known-false patterns
2. **Quarterly theater audit** — Carmack review of docs vs code
3. **Theater detection as mandate** — M29: "No aspirational claims in public docs"

---

## §5 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. All False Claims — CONCEDE

**CONCEDE**: Every theater claim verified.

**SYNTHESIZE**: **Remove all theater. The engine islands are impressive enough without theater.**

### R2. Terminology Drift — CONCEDE

**CONCEDE**: "Pillars" retired, "Node Keepers N1-N10" is actual architecture.

**SYNTHESIZE**: **Fix terminology everywhere.** "Pillars" is theater — it describes a target state, not reality.

### R3. Compliance Theater — CONCEDE

**CONCEDE**: 64.3% ≠ "all enforced."

**SYNTHESIZE**: **Honest compliance badge: "64.3% (18/28 mandates passing)" — earns more trust than fake green bar.**

### R4. Theater Detection as Mandate — SYNTHESIZE

**SYNTHESIZE**: **Add M29: "No aspirational claims in public docs. Every public claim must have file:line evidence in code."**

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*