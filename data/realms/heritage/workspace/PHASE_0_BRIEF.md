# Heritage Realm — Phase 0 Workspace Brief
**AP Token**: AP-VOS-HERITAGE-WORKSPACE-20260814  
**Realm**: Heritage & id Software DNA  
**Owner**: Doom_Guy  
**Phase**: PHASE_0 — FOUNDATION  
**Updated**: 2026-08-14

---

## 🎯 Phase 0 Goal
Verify all [id-soft:] tags have vet records. Zero unvetted tags.

---

## 📋 Active Tasks

### HRT-001: Heritage Sweep — Verify All [id-soft:] Tags
- **Owner**: doom_guy
- **Status**: ready
- **Priority**: P0
- **Description**: `grep -r "\[id-soft:\]"` across codebase → verify each has a vet record in `HERITAGE_VET_LOG.md`
- **Verification**: `make heritage-vet` passes

### HRT-002: Verify No Metaphorical or Over-Attributed Tags
- **Owner**: doom_guy
- **Status**: ready
- **Priority**: P0
- **Description**: Ensure no [id-soft:] tags are METAPHORICAL (should be plain comment) or OVER-ATTRIBUTED (should be stripped)
- **Qualification Gate**: "Cannot be justified WITHOUT citing the original hardware constraint"

### HRT-003: Update CREDITS_CANONICAL.md (Phase 1)
- **Owner**: doom_guy
- **Status**: ready
- **Priority**: P1
- **Depends On**: ENG-001, ENG-004
- **Description**: Add any new patterns from Phase 0 fixes

---

## 🔗 Interface Contract
See `state.yaml` → `interface_contract`

## 📜 Evolution Log
See `state.yaml` → `evolution_log`

---

**This brief is the working document for Heritage Phase 0. Update as tasks progress.**

⬡ OMEGA ⬡ DOOM_GUY ⬡ HERITAGE ⬡ PHASE_0 ⬡ 2026-08-14