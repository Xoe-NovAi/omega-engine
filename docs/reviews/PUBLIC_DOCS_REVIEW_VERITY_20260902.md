<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Verity-EIS Public Docs Review — Mandate Compliance, Mandate Meter Accuracy

**AP Token**: `AP-VERITY-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fb8c256d9ffeR9BmmnOgG72OEL` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**: All public docs + `scripts/check_mandate_compliance.py` + `SOVEREIGN_MANDATES.md` + `MANDATES_CONDENSED.md`
**Method**: M23 — every compliance claim verified against the meter

---

## §1 MANDATE COMPLIANCE METER ACCURACY

### §1.1 Direct Meter Run (2026-09-02)

```
scripts/check_mandate_compliance.py
Total: 28 | Passed: 18 | Failed: 5 | Untested: 4 | Compliance: 64.3%
```

### §1.2 Mandate-by-Mandate Status

| Mandate | Name | Status | Evidence |
|---------|------|--------|----------|
| M1 | AnyIO | ✅ PASS | Zero `import asyncio` in `src/omega/` |
| M2 | Engine-Stack Firewall | ⚠️ UNTESTED | Requires manual verification |
| M3 | — | — | — |
| M4 | — | — | — |
| M5 | — | — | — |
| M6 | UID Sovereignty | ⚠️ UNTESTED | Podman-specific |
| M7 | Local-First | ✅ PASS | `config/providers.yaml:8` |
| M8 | Zero Telemetry | ✅ PASS | No outbound HTTP in core |
| M9 | Error Integrity | ✅ PASS | Typed catches in 5 scripts |
| M10 | Fleet Integrity | ✅ PASS | 13 agents ≤ 14 cap |
| M11 | Soul Integrity | ⚠️ PARTIAL | Soul store exists, auto-prompt not wired |
| M12 | — | — | — |
| M13 | Temple-Grade | ❌ FAIL | Cascading from M23 |
| M14 | Heritage | ⚠️ PARTIAL | 216 tags, 133 vet records |
| M15 | Continuity | ✅ PASS | session_gnosis.md updated |
| M16 | Modularization | ❌ FAIL | Hardcoded path in `m34_registry.py:75` |
| M17 | — | — | — |
| M18 | — | — | — |
| M19 | — | — | — |
| M20 | Somatic State | ⚠️ UNTESTED | Requires manual test |
| M21 | — | — | — |
| M22 | Provenance | ✅ PASS | `GenerateResult.provider_name` |
| M23 | Failure Integrity | ❌ FAIL | `check_secrets.py` exits 1 |
| M24 | Venv Sovereignty | ✅ PASS | All Python in `.venv/` |
| M25 | Doc Standards | ✅ PASS | `make doc-llm-validate` |
| M26 | Doc Standards | ✅ PASS | `make doc-llm-validate` |
| M27 | Tracking Integrity | ❌ FAIL | Stale `in_progress` task |
| M28 | Spatial | ✅ PASS | R-tree + vec0 dual-index |

---

## §2 PUBLIC DOCS CLAIMS VS METER REALITY

### §2.1 False Compliance Claims

| Doc Claim | Location | Meter Reality | Severity |
|-----------|----------|---------------|----------|
| "All 22 enforced" | README:209 | 64.3% (18/28) | 🔴 CRITICAL |
| "All 27 Sovereign Mandates verified compliant" | README:290 | 64.3% (18/28) | 🔴 CRITICAL |
| "Temple-Grade (T1-T11) ✅ VERIFIED" | README:289 | 6 checks, FAILS | 🔴 CRITICAL |
| "Sovereign Mandates (M1-M27) | All 27 enforced" | README:290 | 64.3% | 🔴 CRITICAL |

### §2.2 Mandate Count Inconsistency

| Source | Mandate Count | Issue |
|--------|---------------|-------|
| `SOVEREIGN_MANDATES.md` | 28 sections (M1-M28) | M28 labeled "M35" internally |
| `MANDATES_CONDENSED.md` | 27 mandates (M1-M27) | Missing M28 |
| Compliance meter | 28 mandates | Denominator 28 |
| README | "M1-M22" then "M1-M27" | Inconsistent |

**Root Cause**: M28 (Spatial Integrity) added after M27, internally labeled "M35" in `SOVEREIGN_MANDATES.md:246`. The mandate numbering is inconsistent across artifacts.

---

## §3 MANDATE METER ACCURACY

### §3.1 Meter Implementation

| Component | Status | Notes |
|-----------|--------|-------|
| `scripts/check_mandate_compliance.py` | ✅ Runs | Direct run verified |
| Denominator | 28 | Correct (M1-M28) |
| Pass threshold | Not defined | No "pass/fail" threshold defined |
| CI integration | `make check-mandate-compliance` | Runs in `sote.yml` |

### §3.2 Meter Gaps

| Gap | Impact |
|-----|--------|
| No pass/fail threshold | Can't gate on compliance % |
| 4 mandates "untested" | Manual verification needed |
| M11 partial | Auto-prompt not wired |
| M14 partial | 216 tags vs 133 vet records |

---

## §4 PUBLIC DOCS MANDATE CLAIMS AUDIT

### §4.1 README Mandate Table (Lines 56-63)

| Mandate | Table Claim | Meter Reality | Match |
|---------|-------------|---------------|-------|
| M1 AnyIO | ✅ | ✅ PASS | ✅ |
| M7 Local-First | ✅ | ✅ PASS | ✅ |
| M8 Zero Telemetry | ✅ | ✅ PASS | ✅ |
| M11 Soul Integrity | ✅ | ⚠️ PARTIAL | ⚠️ |
| M23 Failure Integrity | ✅ | ❌ FAIL | ❌ |
| M28 Spatial | ✅ | ✅ PASS | ✅ |

**Issue**: Table shows all 6 as ✅ but M11 is partial and M23 fails.

### §4.2 Verification Section (Lines 284-295)

| Claim | Reality |
|-------|---------|
| "Temple-Grade (T1-T11) ✅ VERIFIED" | 6 checks, FAILS |
| "Sovereign Mandates (M1-M27) | All 27 enforced" | 64.3% |
| "Agent Fleet | 14 agents" | 13 agents |
| "AnyIO Compliance | Zero import asyncio" | ✅ TRUE |
| "Zero Telemetry | No external phone-home" | ✅ TRUE |
| "UID Sovereignty | keep-id" | ✅ TRUE |
| "Heritage Tags | 113 tags" | 216 tags |

---

## §5 MANDATE METER AS PUBLIC SIGNAL

### §5.1 Current State: Misleading

The mandate meter is currently a **misleading signal** because:
1. Docs claim 100% compliance
2. Meter reads 64.3%
3. No explanation of the gap
4. No "known issues" section for failing mandates

### §5.2 Recommended Public Signal

| Mandate | Public Status | Notes |
|---------|---------------|-------|
| M1 AnyIO | ✅ Enforced | |
| M7 Local-First | ✅ Enforced | |
| M8 Zero Telemetry | ✅ Enforced | |
| M11 Soul Integrity | ⚠️ Partial | Auto-prompt not wired |
| M23 Failure Integrity | ❌ Not Enforced | Secret scan fails |
| M28 Spatial | ✅ Enforced | |
| **Overall** | **64.3% (18/28)** | **5 failing, 4 untested** |

---

## §6 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. False Compliance Claims — CONCEDE

**CONCEDE**: Docs claim 100% compliance; meter reads 64.3%.

**SYNTHESIZE**: **Replace all "all enforced" claims with honest 64.3% (18/28) + failing mandate list.**

### R2. Mandate Count Inconsistency — CONCEDE

**CONCEDE**: 27 vs 28 vs 28 (M35) confusion across artifacts.

**SYNTHESIZE**: **Standardize on 28 mandates (M1-M28) everywhere. Fix M28/M35 labeling in SOVEREIGN_MANDATES.md.**

### R3. Mandate Table Honesty — CONCEDE

**CONCEDE**: Table shows M11 and M23 as ✅ when they're partial/fail.

**SYNTHESIZE**: **Update table with honest ⚠️/❌ markers. Honest table earns more trust than fake green.**

### R4. Temple-Grade Claim — CONCEDE

**CONCEDE**: "T1-T11 ✅ VERIFIED" is false — 6 checks, fails on M23.

**SYNTHESIZE**: **Replace with "6 cross-cutting checks; currently fails on M23 cascade."**

---

*⬡ OMEGA ⬡ VERITY ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*