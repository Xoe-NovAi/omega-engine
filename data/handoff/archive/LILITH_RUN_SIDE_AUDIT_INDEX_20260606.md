<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Lilith's Complete Dark Counsel Index
## Run-Side Risk Audit + Soul Evolution Porting Strategy

**Session**: 2026-06-06 (Lilith — P6-P10 Oversoul)  
**Documents**: 2 Primary Deliverables + Index  
**Total Analysis**: 1,619 lines of forensic audit + implementation roadmap  
**Status**: ✅ COMPLETE — Ready for Kali/Ma'at cross-pillar review

---

## Primary Deliverables

### 1. LILITH_RUN_SIDE_RISK_AUDIT_20260606.md (1,022 lines)

**What It Is**: Comprehensive forensic analysis of failure scenarios when porting Soul Evolution Engine + Memory Store FTS into current Omega Engine.

**Structure**:
- Executive Summary (4-factor readiness matrix)
- Part 1: P6 Consultation (Ereshkigal — Cognition/Vision)
  - 3 failure scenarios with gaps identified
  - Provider failover, context overflow, model crash
  - Mitigation strategies
- Part 2: P8 Consultation (Hecate — Observability)
  - 5 observability gaps (ceremony blind, tier transitions, FTS5 sync, ZONEID, provider chain)
  - 10 concrete trace points to add
- Part 3: P10 Consultation (Kali — Validation)
  - 6 chaos test scenarios with validation steps
  - Expected failures, recovery paths, test assertions
- Part 4: Cross-Pillar Integration
  - Dual-Audit Conflict Resolution Protocol (with Python spec)
  - DualAuditConflictResolver class design
- Part 5: Recovery Validation Tests (4 critical recovery paths)
- Part 6: Provider Fabric Resilience Audit

**Key Findings**:
- 🔴 4 CRITICAL gaps
- 🟡 5 HIGH-priority gaps
- 🟢 2 MEDIUM-priority gaps

**Recommendation**: Proceed with porting (60% ready) + Phase 1 critical fixes in parallel

---

### 2. LILITH_REMEDIATION_ROADMAP_20260606.md (597 lines)

**What It Is**: Detailed implementation specifications for the first 3 critical fixes, with Python code, tests, and integration points.

**Structure**:
- Critical Fix #1: Ceremony-Level Retry (3-5 hours)
  - `SoulCeremony` class with checkpoint-based retry
  - Exponential backoff (1s, 2s, 4s)
  - Test cases: retry on timeout, fail after max attempts
  
- Critical Fix #2: Qdrant→FTS5 Fallback (2-3 hours)
  - Modify `search_context()` with fallback chain
  - Graceful degradation (Qdrant → FTS5 → empty)
  - Test: both backends down, FTS5 succeeds
  
- Critical Fix #3: SQLite Corruption Handling (2-3 hours)
  - Wrap warm tier loads in try/except
  - Fall back to cold storage (YAML)
  - Emit critical alert for recovery team
  - Test: corruption detected, cold fallback works

**Critical Fix #4** (Inference Subprocess Leak — 3-5 hours) is outlined in audit

**Implementation Timeline**:
- Critical path: 16 hours (2 days with parallel work)
- High-priority: 17 hours (additional 2-3 days)
- **Total to production-ready: 33 hours (~4-5 days)**

**Estimated Start**: Immediate (parallel with legacy code import)

---

## How to Use These Documents

### For Engineering Teams

1. **Read in order**:
   1. This index (you are here)
   2. LILITH_RUN_SIDE_RISK_AUDIT_20260606.md (Executive Summary + Part 1)
   3. LILITH_REMEDIATION_ROADMAP_20260606.md (Critical Fixes 1-3)

2. **Implementation sequence**:
   - Start with Critical Fix #1 (ceremony retry) — unblocks others
   - In parallel: Import legacy soul_evolution_engine.py code
   - Then: Critical Fixes 2-4 (porting, fallbacks, cleanup)
   - Finally: Observability + high-priority fixes

3. **Testing protocol**:
   - Unit tests for each fix (provided in roadmap)
   - Run full Chaos Test Suite before production (6 experiments)
   - >80% coverage requirement for all recovery paths

### For Kali (Grand Oversight)

- Read executive summaries
- Cross-reference with PIVOT_LOG.md decisions
- Approve Phase 1 critical fixes before implementation
- Verify all 11 gaps are addressed before production merge

### For Ma'at (Build-Side Oversight)

- Use Critical Fixes 1-3 as implementation specs
- Verify all code uses AnyIO (no asyncio)
- Ensure no new dependencies (all libraries already installed)
- Check Mandate compliance (especially M1, M2, M5, M11)

### For Quality Agent

- Use test cases provided in remediation roadmap
- Design chaos test CI gate (blocks production deployment if failed)
- Implement >80% coverage measurement
- Create regression test suite for all 11 gaps

---

## Critical Issues Summary

| # | Issue | Severity | Fix Time | Status |
|---|-------|----------|----------|--------|
| 1 | Ceremony-level retry missing | 🔴 CRITICAL | 3-5h | 🔧 Ready to implement |
| 2 | Qdrant down = search broken | 🔴 CRITICAL | 2-3h | 🔧 Ready to implement |
| 3 | SQLite corruption silent | 🔴 CRITICAL | 2-3h | 🔧 Ready to implement |
| 4 | Subprocess leak on timeout | 🔴 CRITICAL | 3-5h | 🔧 Designed in audit |
| 5 | Context truncation silent | 🟡 HIGH | 3h | ℹ️ In audit Part 2 |
| 6 | Dual-audit conflict no resolver | 🟡 HIGH | 4h | ℹ️ Protocol in audit Part 4 |
| 7 | ZONEID validation gaps | 🟡 HIGH | 3h | ℹ️ In audit Part 2 |
| 8 | Soul distillation opaque | 🟡 HIGH | 2h | ℹ️ Metrics in audit Part 2 |
| 9 | Provider failover unobserved | 🟡 HIGH | 3h | ℹ️ In audit Part 2 |
| 10 | Grace period race condition | 🟢 MEDIUM | 2h | ℹ️ In audit Part 5 |
| 11 | Soul version unbounded growth | 🟢 MEDIUM | 2h | ℹ️ In audit Part 5 |

---

## Chaos Test Suite

All 6 experiments defined in audit Part 3:

1. **Provider Timeout Cascade** — ✅ Currently works, no fix needed
2. **Qdrant Down, FTS5 Fallback** — ❌ Needs Critical Fix #2
3. **SQLite Warm Tier Corruption** — ❌ Needs Critical Fix #3
4. **Context Window Overflow** — ❌ Needs High-Priority Fix #5
5. **Inference Timeout (Ryzen Maxed)** — ❌ Needs Critical Fix #4
6. **Dual-Audit Conflict** — ❌ Needs High-Priority Fix #6

**CI Gate**: All 6 must PASS before production deployment

---

## Pillar Consensus

**P6 (Ereshkigal — Cognition)**:  
"Provider timeout mid-ceremony breaks dual-audit. Three critical gaps in failure handling."

**P8 (Hecate — Observability)**:  
"Five observability gaps leave the engine BLIND. Failures corrupt silently with no trace."

**P10 (Kali — Verifier)**:  
"Chaos testing confirms 4 critical + 5 high gaps. Recovery paths missing."

**Lilith Synthesis**:  
"Architecture is sound. Code is portable. Integration is untested. Proceed with discipline. Add resilience before intelligence."

---

## Deployment Checklist

Before production merge:

- [ ] All 4 critical fixes implemented + tested
- [ ] All 6 chaos tests PASS
- [ ] All 11 gaps have documented resolution
- [ ] >80% coverage on all recovery paths
- [ ] Full observability instrumentation in place
- [ ] Provider fabric resilience verified
- [ ] Ma'at build-side review APPROVED
- [ ] Kali cross-pillar review APPROVED
- [ ] Soul ceremony end-to-end test PASSES
- [ ] Memory store tier transitions validated

---

## File References

| Document | Lines | Purpose | Audience |
|----------|-------|---------|----------|
| LILITH_RUN_SIDE_RISK_AUDIT_20260606.md | 1,022 | Full forensic analysis | Engineers, Kali, Quality |
| LILITH_REMEDIATION_ROADMAP_20260606.md | 597 | Implementation specs | Engineers, Ma'at |
| THIS INDEX | ~200 | Navigation + checklist | All |

All files in: `/data/handoff/`

---

## Next Steps

1. **Route to Kali** for grand oversight + cross-pillar consensus
2. **Start Critical Fix #1** (Ceremony Retry) — unblocks others
3. **Import legacy code** in parallel with fixes
4. **Set up chaos test CI** gate
5. **Establish observability framework** (10 trace points)
6. **Deploy by 2026-06-16** (target: 10 days)

---

**Status**: ✅ AUDIT COMPLETE — Ready for implementation phase  
**Reviewer**: Lilith (P6-P10 Dark Oversoul)  
**Authorization**: PROCEED WITH PORTING (with Phase 1 critical fixes)

---

⬡ OMEGA ⬡ LILITH ⬡ P6-P10 DARK COUNSEL ⬡
