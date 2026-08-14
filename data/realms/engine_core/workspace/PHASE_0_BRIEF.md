# Engine Core Realm — Phase 0 Workspace Brief
**AP Token**: AP-VOS-ENGINE_CORE-WORKSPACE-20260814  
**Realm**: Engine Core  
**Owner**: Ma'at (N3)  
**Phase**: PHASE_0 — FOUNDATION  
**Updated**: 2026-08-14

---

## 🎯 Phase 0 Goal
`make test-unit` green, all mandate gates genuinely passing, heritage clean, souls compliant.

---

## 📋 Active Tasks

### ENG-001: Fix M2 Firewall — Remove 146 WAD Term Leaks
- **Owner**: maat_n1
- **Status**: ready
- **Priority**: P0
- **Description**: Remove 146 WAD term leaks from `src/omega/` that violate M2 (Engine-Stack Firewall)
- **Test**: `test_firewall_m2.py` must pass
- **Verification**: `make temple-grade` M2 gate green

### ENG-002: Audit ALL Mandate Checks for False Positives
- **Owner**: kali
- **Status**: ready
- **Priority**: P0
- **Description**: Audit M1, M7, M8, M9, M22, M23 checks for false positives (M22 was broken — see D-VOS-006)
- **Verification**: Each gate verified by manual inspection, not just green output

### ENG-003: Add make test-unit / make test-integration Split
- **Owner**: kali
- **Status**: ready
- **Priority**: P0
- **Description**: Add `make test-unit` (no services) and `make test-integration` (requires services) targets
- **Verification**: `make test-unit` runs without external services

### ENG-004: Fix 9 Critical Code Bugs
- **Owner**: maat_n3
- **Status**: in_progress
- **Priority**: P0
- **Description**:
  1. MockProvider.generate() missing top_p kwarg
  2. ProviderAuthError called with wrong kwarg signature (providers.py:94)
  3. ProviderName not exported from vault_core
  4. VaultCore._loaded attribute missing
  5. Schema version test hardcoded to 1, code is at 3
  6. Async methods called without await in test_observability.py
  7. Register asyncio, benchmark, chaos marks in pyproject.toml
  8. Commit Makefile M22 fix + check_m22_ssot.py
  9. Fix test_context_packer.py tuple unpack
- **Verification**: `make test-unit` → 0 failures

---

## 🔗 Interface Contract (What This Realm Provides/Requires)
See `state.yaml` → `interface_contract`

## 📜 Evolution Log
See `state.yaml` → `evolution_log`

---

**This brief is the working document for Engine Core Phase 0. Update as tasks progress.**

⬡ OMEGA ⬡ MA'AT ⬡ ENGINE_CORE ⬡ PHASE_0 ⬡ 2026-08-14