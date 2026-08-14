# Fleet Realm — Phase 0 Workspace Brief
**AP Token**: AP-VOS-FLEET-WORKSPACE-20260814  
**Realm**: Agent Fleet  
**Owner**: Kali  
**Phase**: PHASE_0 — FOUNDATION  
**Updated**: 2026-08-14

---

## 🎯 Phase 0 Goal
Soul compliance, distillation pipeline enforced, LIVE_FEED leaks eliminated.

---

## 📋 Active Tasks

### FLT-001: Migrate kali & roc_racoon Souls to v6.1 Lean Schema
- **Owner**: kali
- **Status**: ready
- **Priority**: P0
- **Description**: Migrate kali (v7.2) and roc_racoon (v7.1) souls to v6.1 lean schema
- **Note**: soul_validator.py now has VALID_SOUL_VERSIONS={6.1,7.0,7.1,7.2} — these entities now receive strict validation (D-VOS-003)
- **Verification**: `make soul-audit` passes

### FLT-002: Fix session_end.py — Preserve Proposals (COMPLETED)
- **Owner**: kali
- **Status**: completed
- **Priority**: P0
- **Commit**: 2b3b2803
- **Description**: Preserve agent-written proposals instead of overwriting with `[]` (D-VOS-002)

### FLT-003: Fix soul_validator.py — LIVE_FEED → HMC_COLLABORATION_HUB (COMPLETED)
- **Owner**: kali
- **Status**: completed
- **Priority**: P0
- **Commit**: 2b3b2803
- **Description**: Replace LIVE_FEED with HMC_COLLABORATION_HUB in fallback soul (D-VOS-004)

### FLT-004: Enforce Distillation Pipeline (Scribe Agent)
- **Owner**: verity
- **Status**: ready
- **Priority**: P0
- **Depends On**: FLT-001
- **Description**: Implement Scribe agent L1→L2→L3 gate; ensure proposed_lessons.yaml has new entries per session

### FLT-005: Document Skipped Tests
- **Owner**: jem
- **Status**: ready
- **Priority**: P0
- **Description**: Mark Class B/C test failures with `@pytest.mark.skip(reason="tracked: TEST-DRIFT-XXX")` — honest, documented, not silent

---

## 🔗 Interface Contract
See `state.yaml` → `interface_contract`

## 📜 Evolution Log
See `state.yaml` → `evolution_log`

---

**This brief is the working document for Fleet Phase 0. Update as tasks progress.**

⬡ OMEGA ⬡ KALI ⬡ FLEET ⬡ PHASE_0 ⬡ 2026-08-14