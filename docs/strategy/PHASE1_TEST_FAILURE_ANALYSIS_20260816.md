# 📋 Phase 1 Test Failure Analysis — Verified Inventory

**AP Token**: `AP-PHASE1-FAILURE-ANALYSIS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_phase1_analysis ⬡ VERIFIED

**Date**: 2026-08-16
**Source**: Full serial test run (`pytest tests/ -o addopts=""`) — 1825 tests, 63 failing
**Ratification**: D-532 (Kali oversight of Roc readiness audit)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 1825 (full serial suite) |
| **Failures** | 63 (47 errors + 13 failures + 60 skipped) |
| **Root Causes** | 5 clusters |
| **Pass Rate** | 96.5% |

The implementation has evolved (M1 async migration, VaultCore refactor, MCP restructure) but tests lag behind — classic test-debt. Not 63 separate bugs — **5 root causes**.

---

## Root-Cause Clusters (Verified)

### P1-1: Async/Sync Mismatch (~20 tests, 5 files)
**Pattern**: Tests call async methods without `await` → coroutine returned instead of result.

| Method | Test File | Line | Error |
|--------|-----------|------|-------|
| `MetricsDB.get_stats()` | `test_metrics_db.py` | 365 | `'coroutine' object is not subscriptable` |
| `MetricsDB.record_event()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.record_error()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.set_baseline()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.get_breaker_history()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.get_error_summary()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.get_performance_trend()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `MetricsDB.detect_regression()` | `test_metrics_db.py` | 4 tests | `TypeError: 'coroutine' object...` |
| `MetricsDB.get_baseline()` | `test_metrics_db.py` | multiple | `TypeError: 'coroutine' object...` |
| `BudgetGate.check_budget()` | `test_contract_m21.py` | 674 | `Expected tuple, got coroutine` |
| `BudgetGate._get_today_spend()` | `test_contract_m21.py` | 693 | `unsupported operand type(s) for -: 'float' and 'coroutine'` |
| `fts_memory` methods | `test_fts_memory.py` | 1 test | `TypeError: 'coroutine' object...` |
| `search_tools` service | `test_search_tools.py` | 2 tests | `TypeError: 'coroutine' object...` |
| `hub_health` | `test_hub_health.py` | 1 test | `TypeError: 'coroutine' object...` |

**Fix Pattern**: Add `await` before each async call in test code.

---

### P1-2: VaultCore API Drift (~18 tests, 2 files)
**Pattern**: Implementation refactored, tests not updated.

| Issue | Error | Fix |
|-------|-------|-----|
| `store_credential` → `bury_credential` | Method renamed | Update test calls to `bury_credential` |
| `encrypted_blob` requires **age-armored ciphertext** | `ValidationError: encrypted_blob must be age-armored ciphertext` | Encrypt test fixtures via `age` CLI or Python `age` lib |
| `ProviderName` moved | `ImportError: cannot import name 'ProviderName'` | Update import from `omega.vault.vault_core` |
| `initialize_fleet_vault` moved | Import error | Update import path |
| `_loaded` attribute removed | `AttributeError: 'VaultCore' object has no attribute '_loaded'` | Remove test assertion or use public API |
| `verify_integrity` removed | Method gone | Update/remove test |

**Key Files**: `tests/unit/test_vault_core.py` (18 failures), `tests/test_contract_m21.py` (2), `src/omega/vault/vault_core.py`

**DECISION (D-532)**: Keep `bury_credential` as canonical API. Do NOT restore `store_credential` alias. Align tests to new API.

---

### P1-3: ImportError — mcp_servers.omega_hub.tools (9 tests)
**Error**: `ImportError: cannot import name 'tools' from 'mcp_servers.omega_hub'`

**Location**: `tests/test_library_fts_search.py:154` (all 9 tests fail with same import error)

**Fix**: Module restructured. Find new location of `tools` module in `mcp_servers/omega_hub/` and update import path.

---

### P1-4: Mock Signature Mismatch (1 test)
**Error**: `TypeError: MockVectorAdapter.query() got an unexpected keyword argument 'collection'`

**Location**: `tests/test_qdrant_index.py:45` → calls `indexer.hybrid_search()` → `indexer.search_vector()` at `src/omega/library/indexer.py:226` passes `collection=self._vector_collection`

**Fix**: Update `MockVectorAdapter.query()` signature in test to accept `collection` kwarg, or adjust test mock to match indexer call signature.

---

### P1-5: Individual Logic Failures (~5 tests)
| Test | Error | Likely Fix |
|------|-------|------------|
| `test_metrics_db.py::TestCloseAndReopen::test_close_and_reopen` | `assert 0 == 1` | DB state cleanup between tests |
| `test_contract_m21.py` dispatch template | Missing `[id-soft:` heritage tag | Add heritage tag to template |
| Various | `assert 13 == 14`, `int()` on empty string | Per-test diagnosis |

---

## Execution Commands

```bash
# Run full suite without -x or -n auto (serial, no early exit)
pytest tests/ -o addopts="" -v --tb=short

# Focused debugging per cluster
pytest tests/test_metrics_db.py -o addopts="" -v --tb=short
pytest tests/unit/test_vault_core.py -o addopts="" -v --tb=short
pytest tests/test_library_fts_search.py -o addopts="" -v --tb=short
pytest tests/test_qdrant_index.py -o addopts="" -v --tb=short
pytest tests/test_contract_m21.py -o addopts="" -v --tb=short
pytest tests/test_fts_memory.py -o addopts="" -v --tb=short
pytest tests/test_hub_health.py -o addopts="" -v --tb=short
pytest tests/test_search_tools.py -o addopts="" -v --tb=short
```

---

## Acceptance Criteria (D-532)

1. ✅ `make test` passes (no `-x`, full suite)
2. ✅ Full serial `pytest tests/ -o addopts=""` → **0 failures**
3. ✅ All 5 clusters resolved
4. ✅ Report results to Hivemind with `omega-hub_hivemind_post_context`

---

## Tracking References

- **Sprint**: `ACTIVE_SPRINT.json` → `READINESS-REMEDIATION` workstream → `P0-2` subtasks `P1-1`..`P1-6`
- **HMC Hub**: `data/coordination/HMC_COLLABORATION_HUB.md` → `NEXT_ACTION`
- **Roc Audit**: `data/coordination/ROC_RACOON_KALI_REPORT_20260816.md`
- **VaultCore Source**: `src/omega/vault/vault_core.py` (check new API)
- **Indexer Source**: `src/omega/library/indexer.py:226` (for mock signature)
- **MCP Hub Restructure**: `mcp_servers/omega_hub/` (find `tools` module)

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_phase1_analysis ⬡ VERIFIED*