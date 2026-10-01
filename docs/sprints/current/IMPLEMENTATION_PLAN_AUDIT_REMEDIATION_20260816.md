---
schema_version: "1.0"
document_type: sprint_plan
document_id: impl-plan-audit-remediation-20260816
title: Implementation Plan — Hybrid Benchmark Audit Remediation
status: ACTIVE
version: "1.0.0"
date: "2026-08-16"
owner: kali
tags: [audit, remediation, mandate-compliance, sprint, t01-t11]
priority: P0
depends_on: []
blocks: []
acceptance_gates:
  - "T01-T11 tasks complete with verification evidence"
  - "make check-mandate-compliance passes (compliance meter)"
  - "make temple-grade green (T1-T11)"
cross_references:
  - context_packs/hybrid-benchmark-strategy/Web-Claude-response-hybrid-benchmark-r2.md
  - docs/decisions/PIVOT_LOG.md
  - SOVEREIGN_MANDATES.md
llm_metadata:
  token_budget: 8000
  chunk_strategy: section_per_ticket
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Implementation Plan — Hybrid Benchmark Audit Remediation
**AP Token**: `AP-IMPL-AUDIT-REMEDIATION-20260816`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_implementation ⬡ APPROVAL_REQUESTED

**Date**: 2026-08-16
**Source**: Web Claude Sonnet 5 Audit (r1 + r2) — `hybrid-benchmark-strategy` pack
**Status**: Awaiting approval to execute

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 11 |
| **P0 (Mandate Violations)** | 3 |
| **P1 (Safety/Integrity)** | 4 |
| **P2 (Technical Debt)** | 2 |
| **P3 (Process/Tracking)** | 2 |
| **Estimated Effort** | ~6.5 hours |
| **Files to Modify** | 7 |

---

## 🎯 Priority Matrix

| Priority | ID | Task | Mandate | Effort | Risk |
|----------|----|------|---------|--------|------|
| **P0-1** | T01 | `asyncio` → `anyio` regression guard (Ruff rule) | M1 | 15 min | Zero |
| **P0-2** | T02 | `SQLiteVecAdapter.delete()` / `delete_session()` fix | M9/M23 | 30 min | Low |
| **P0-3** | T03 | `quick_check_sync()` fail-safe (PSI read → THROTTLE) | M9 | 20 min | Low |
| **P1-1** | T04 | Fix AGENTS.md mandate count (3 locations) | M27 | 15 min | Zero |
| **P1-2** | T05 | ADR for mandate compliance measurement | M13/M27 | 30 min | Zero |
| **P1-3** | T06 | Build `make check-mandate-compliance` target | M13/M27 | 2.5 hrs | Medium |
| **P1-4** | T07 | `SelectiveHydration.hydrate()` call-site fix (Pass 1) | M17 | 15 min | Low |
| **P2-1** | T08 | Wire PII masker into `ProviderSelector` | M7/M8 | 45 min | Medium |
| **P2-2** | T09 | Delete `hivemind_redis.py` (verify + remove) | M19 | 10 min | Zero |
| **P3-1** | T10 | Update breaker consolidation tracking (redirect callers) | M10 | 10 min | Zero |
| **P3-2** | T11 | Update `UNOVERENGINEERING_PLAN.md` status flags | M19 | 10 min | Zero |

---

## 📋 Task Specifications

### **T01: Regression Guard — Ruff Rule for `asyncio` Import Ban** ✅ P0-1 COMPLETE (fix applied)
**Status**: Fix applied (3 `asyncio.sleep` → `anyio.sleep`, import removed). Need guard.
**Action**: Add to pre-commit / CI:
```yaml
# .pre-commit-config.yaml or Makefile
check-asyncio-import:
	@rg -n '^\s*import asyncio' --glob '!tests/**' --glob '!third_party/**' && exit 1 || true
```
**Verification**: `make check-asyncio-import` exits 0 (no hits).

---

### **T02: SQLiteVecAdapter.delete() / delete_session() Fix** ❌ P0-2
**File**: `src/omega/memory/sqlite_vec_adapter.py`
**Mandate**: M9 (Error Integrity), M23 (Failure Integrity)
**Risk**: Low — `rowid` scoped to exactly one vec0 table per `upsert()` call.

**Implementation** (from audit r2 §2):
```python
# In delete() — replace lines ~200-210:
for collection_name in self._vec_tables_created:
    conn.execute(
        f"DELETE FROM {collection_name} WHERE rowid = ?",
        (rowid,)
    )

# In delete_session() — replace lines ~220-230:
for collection_name in self._vec_tables_created:
    conn.execute(f"DELETE FROM {collection_name} WHERE rowid IN ({placeholders})", rowids)
```

**Verification**: Unit test — insert into collection A, delete by UUID → verify row removed from A, not from B.

---

### **T03: quick_check_sync() Fail-Safe** ❌ P1-1
**File**: `src/omega/oracle/oom_protector.py`
**Mandate**: M9 (Error Integrity)
**Risk**: Low — sync CLI utility, no async callers.

**Implementation** (from audit r2 §3):
```python
# Replace the try/except block (lines ~140-150):
psi_some_avg60 = 0.0
psi_full_avg10 = 0.0
psi_read_failed = False
try:
    psi_some_avg60 = anyio.run(psi.get_pressure("some", "avg60"))
    psi_full_avg10 = anyio.run(psi.get_pressure("full", "avg10"))
except Exception as e:
    logger.warning(
        "quick_check_sync: PSI read failed (%s) — degrading to "
        "THROTTLE per M9 fail-safe policy instead of assuming 0%% "
        "pressure", e,
    )
    psi_read_failed = True

# Add at decision logic end:
if psi_read_failed:
    return AdmissionResult.THROTTLE  # unknown PSI state ≠ healthy PSI state
```

**Verification**: Mock PSI failure → verify `THROTTLE` returned, warning logged.

---

### **T04: Fix AGENTS.md Mandate Count (3 Locations)** ❌ P1-2
**File**: `AGENTS.md`
**Mandate**: M27 (Tracking Integrity)
**Risk**: Zero — documentation only.

**Locations to Fix**:
1. Line ~10: `"SOVEREIGN_MANDATES.md (25 laws v3.7.0 — M1 to M25)"` → `"SOVEREIGN_MANDATES.md (27 laws v3.8.0 — M1 to M27)"`
2. Line ~264: `"26 mandates, M1-M27, v3.8.0"` → `"27 mandates, M1-M27, v3.8.0"`
3. Line ~439: `"25 laws v3.7.0"` → `"27 laws v3.8.0"`

**Verification**: `grep -n "laws v3" AGENTS.md` shows all v3.8.0/27.

---

### **T05: ADR for Mandate Compliance Measurement** ❌ P1-2
**File**: `docs/adr/ADR-XXXX-mandate-compliance-measurement.md` (new)
**Mandate**: M13 (Temple-Grade), M27 (Tracking Integrity)
**Risk**: Zero — documentation.

**Template** (MADR format):
```markdown
# ADR-XXXX: Mandate Compliance Measurement

## Status: Accepted

## Context
`OMEGA_ENGINE.md` hand-reports compliance % (92% vs 84% conflict). No mechanical source of truth.

## Decision
- Compliance % computed ONLY by `make check-mandate-compliance`
- Never hand-edited into `OMEGA_ENGINE.md`
- Script reads `SOVEREIGN_MANDATES.md` for denominator (27), checks each mandate

## Consequences
- `OMEGA_ENGINE.md` §2 table becomes generated, not authored
- CI fails if hand-edited compliance % detected
```

---

### **T06: Build `make check-mandate-compliance` Target** ❌ P1-3
**Files**: `Makefile`, `scripts/check_mandate_compliance.py` (new)
**Mandate**: M13 (Temple-Grade), M27 (Tracking Integrity)
**Risk**: Medium — new script, must be accurate.
**Effort**: 2.5 hrs (per UNOVERENGINEERING_PLAN Phase 5)

**Specification**:
```python
# scripts/check_mandate_compliance.py
# 1. Parse SOVEREIGN_MANDATES.md → count mandates (denominator = 27)
# 2. For each mandate, check compliance indicator:
#    - M1: rg 'import asyncio' (zero hits outside exempted)
#    - M2: rg 'config/wads' in src/omega/ (zero hits)
#    - M7: config/providers.yaml strategy == local_first
#    - M8: rg 'telemetry' in config/ (zero external)
#    - M9: rg 'except Exception:' without logger/trace_id
#    - M13: make temple-grade passes
#    - M14: rg '\[id-soft:' → vet record exists
#    - M22: GenerateResult.provider_name captured at receipt
#    - M23: scripts/m23_gate.py exists + passes
#    - M24: rg 'break-system-packages' (zero hits)
#    - M25: config/providers.yaml streaming.chunk_timeout_ms present
# 3. Output JSON: {"total": 27, "full": N, "partial": N, "fail": N, "details": {...}}
```

**Makefile Target**:
```makefile
check-mandate-compliance:
	@python scripts/check_mandate_compliance.py
```

**Verification**: `make check-mandate-compliance` outputs valid JSON, matches manual audit.

---

### **T07: SelectiveHydration.hydrate() Call-Site Fix (Pass 1)** ✅ VERIFIED-ALREADY-FIXED
**File**: `src/omega/oracle/oracle.py` (lines 650-690)
**Mandate**: M17 (Cognitive Integrity)
**Risk**: Low — call-site variable swap.

**⚠️ 2026-08-16 VERIFICATION**: The audit pack snapshot predated the fix. Current codebase already threads query correctly:
1. `oracle.py:669` → `context_builder.build_context(..., query=query)` ✅
2. `context_builder.py:283` → `_build_gnosis_block(entity_name, query)` ✅
3. `context_builder.py:314-317` → `hydrate(query=query if query else entity_name, entity_name=entity_name)` ✅

Live check: `inspect.signature(SelectiveHydration.hydrate)` → `(self, query: str, entity_name: str)`. **No change required.** Same drift pattern as T09 — audit pack was built from a stale snapshot.

**Original implementation** (for historical record — already landed):
```python
# In _prepare_system_prompt() or equivalent:
# BEFORE:
principles = await self._selective_hydration.hydrate(
    query=entity_name,  # WRONG
    entity_name=entity_name,
)

# AFTER:
principles = await self._selective_hydration.hydrate(
    query=query,  # CORRECT: actual user query
    entity_name=entity_name,
)
```

**Note**: If `hydrate()` signature doesn't accept `query` param, that's Pass 2 (deferred).

**Verification**: Query with known L3 principle → verify relevant principle retrieved.

---

### **T08: Wire PII Masker into ProviderSelector** ❌ P2-1
**Files**: `src/omega/oracle/model_gateway.py`, `src/omega/oracle/provider_selector.py`
**Mandate**: M7 (Local-First), M8 (Zero Telemetry)
**Risk**: Medium — wiring missing component.

**Finding** (audit r2 §6 Q9): `ProviderSelector` has PII penalty logic but `self.pii_masker` always `None` because `ModelGateway` never sets it.

**Implementation**:
```python
# In ModelGateway.__init__():
from .pii_masker import PIIMasker  # or wherever it lives
self.pii_masker = PIIMasker()

# ProviderSelector already receives model_gateway reference:
self.pii_masker = model_gateway.pii_masker if hasattr(model_gateway, "pii_masker") else None
```

**Verification**: Query with PII → verify cloud providers penalized (-100 score).

---

### **T09: Delete hivemind_redis.py** ❌ P2-2
**File**: `src/omega/coordination/hivemind_redis.py` (113 lines)
**Mandate**: M19 (Adversarial Alchemy)
**Risk**: Zero — confirmed dead code.

**Action**:
```bash
# Verify first (M4: Plan → Verify → Execute)
grep -rn "hivemind_redis" --include="*.py"
# If empty:
rm src/omega/coordination/hivemind_redis.py
```

**Verification**: `make test` passes, no import errors.

---

### **T10: Update Breaker Consolidation Tracking** ❌ P3-1
**File**: `UNOVERENGINEERING_PLAN.md` (or tracking doc)
**Mandate**: M10 (Fleet Integrity)
**Risk**: Zero — documentation.

**Finding** (audit r2 §6 Q13): `HealthMonitor.get_breaker()` factory **already exists** since D-376b. Task is redirect callers, not build factory.

**Action**: Update status from "NOT STARTED" to "REDIRECT CALLERS" with list of 6 clone implementations to migrate.

---

### **T11: Update UNOVERENGINEERING_PLAN.md Status Flags** ❌ P3-2
**File**: `docs/strategy/UNOVERENGINEERING_PLAN.md`
**Mandate**: M19 (Adversarial Alchemy)
**Risk**: Zero — documentation.

**Action**: Update status columns for:
- `hivemind_redis.py` → DELETED
- Circuit breaker factory → EXISTS (redirect callers)
- VaultCore → NOT STARTED (no change)
- Phase 5 compliance meter → IN PROGRESS (T05/T06)

---

## 📅 Execution Order (Dependency-Aware)

```
Phase 1: Quick Wins (Zero Risk, <1 hr total)
├── T01: Ruff asyncio guard
├── T04: AGENTS.md mandate count fix
├── T09: Delete hivemind_redis.py (verify first)
├── T10: Update breaker tracking
└── T11: Update UNOVERENGINEERING_PLAN.md

Phase 2: Core Fixes (Low Risk, ~1 hr)
├── T02: SQLiteVecAdapter.delete() fix
├── T03: quick_check_sync() fail-safe
└── T07: SelectiveHydration call-site fix

Phase 3: Process/Infrastructure (Medium Risk, ~3 hrs)
├── T05: ADR for compliance measurement
├── T06: Build check-mandate-compliance script + Makefile target
└── T08: Wire PII masker
```

---

## ✅ Acceptance Criteria (All Must Pass)

| Criterion | Verification |
|-----------|--------------|
| **M1** | `make check-asyncio-import` exits 0 |
| **M9** | `quick_check_sync()` with mocked PSI failure → `THROTTLE` + warning logged |
| **M9/M23** | `SQLiteVecAdapter.delete()` removes from correct collection only |
| **M27** | `AGENTS.md` shows 27 laws v3.8.0 in all 3 locations |
| **M13/M27** | `make check-mandate-compliance` outputs valid JSON with 27 total |
| **M17** | Query with known L3 principle → relevant principle retrieved |
| **M7/M8** | PII query → cloud providers penalized in `ProviderSelector` |
| **All** | `make test` passes (no regressions) |
| **All** | `make temple-grade` passes (T1-T11) |

---

## 🚨 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| `check_mandate_compliance.py` false positives | Start with subset of mandates (M1, M7, M8, M13, M22, M23, M24, M25) — expand iteratively |
| PII masker wiring breaks provider selection | Feature flag: `ENABLE_PII_MASKER=false` default, enable after verification |
| `selective_hydration.py` signature mismatch | Pass 1 is call-site only; if signature lacks `query` param, defer to Pass 2 |
| `make test` timeout | Run focused tests first: `pytest tests/test_mandate_ci_checks.py -v` |

---

## 📝 Approval Request

**Please approve to execute Phase 1 → Phase 2 → Phase 3 in order.**

**Or specify modifications:**
- [ ] Approve as written
- [ ] Modify priority order: _______________
- [ ] Defer specific tasks: _______________
- [ ] Add tasks: _______________

---

*Implementation plan derived from Web Claude Sonnet 5 audit responses (r1 + r2) on `hybrid-benchmark-strategy` context pack (Pack ID: `eaa4d2b1-f20c-47aa-ab81-6787243507f5`).*