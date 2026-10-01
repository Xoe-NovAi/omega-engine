# 🔱 CARMACK REVIEW: Context Pack Update Report
**Date**: 2026-08-09  
**Status**: GAP-0 & GAP-3 Complete | GAP-1 In Progress  
**Context**: Updating sovereign-audit context pack for next Web Claude round

---

## 1. What's Fixed Since Last Audit (Not in Current Packs)

### ✅ GAP-0: ObservabilityEngine Dual-Surface Async API (COMPLETE)
**Root Cause**: `ObservabilityEngine` methods were sync with `anyio.from_thread.run()` bridges. When called from async contexts (90% of callers), the bridge raised `RuntimeError` silently caught → MetricsDB writes dropped. Some callers incorrectly `await`ed sync methods → `TypeError`.

**Fix**: Dual-surface async API
- Core methods now **async** (directly await `MetricsDB`): `record_performance`, `record_breaker_transition`, `record_metrics_error`, `log_event`, `stats`
- Added `_sync` wrappers for genuinely sync callers: `log_event_sync`, `stats_sync`
- **11 callers updated** across 8 files

### ✅ GAP-3: M23 Gate Replacement (COMPLETE)
**Root Cause**: `rg -n` pipeline intersection always empty (line-oriented). `pass` and `except` on different lines → empty pipeline → `!` inverts to success → gate **never fails**.

**Fix**: AST-based Ruff ratchet (`scripts/m23_gate.py`)
- Rules: S110 (try-except-pass), S112 (try-except-continue), BLE001 (blind except), E722 (bare except)
- Ratchet: baseline of 294 violations → fails only on **new** violations
- Mutation tested, wired into `.githooks/pre-commit` using **venv python** (system python3 lacks ruff binary → false pass)
- Mutation test passes: gate correctly detects injected S110 violation

---

## 🔴 Critical Missing from Current Context Packs

### 1. **GAP-0: ObservabilityEngine Dual-Surface Async API** 
**File: `src/omega/observability/__init__.py`** — Entire observability layer refactored from sync-with-bridge to **dual-surface async API**:
- Core methods now **async** (directly await MetricsDB): `record_performance`, `record_breaker_transition`, `record_metrics_error`, `log_event`, `stats`
- Added `_sync` wrappers: `log_event_sync`, `stats_sync`
- **All 11 callers updated** across 8 files

### 2. **GAP-3: M23 Gate Replacement (Ruff Ratchet)**
**New files & updates:**
- `scripts/m23_gate.py` — New AST-based ratchet gate
- `config/m23_baseline.txt` — Baseline of 294 violations across 98 files
- `tests/contract/test_mandate_gates.py` — Mutation tests
- `Makefile` — Replaced broken target + added `m23-baseline` target
- `pyproject.toml` — Added `[tool.ruff]` config
- `.githooks/pre-commit` — M23 gate wired, uses **venv python**

---

## 🟡 In Progress: GAP-1 (Sovereignty Ratio Unification)

### 3. **ProviderRegistry SSOT** — **NEW FILE: `src/omega/oracle/provider_registry.py`**
Single Source of Truth for provider classification, reading `is_cloud` from `config/providers.yaml`.
- **Created but NOT YET WIRED** into 5 divergent call sites
- Replaces 5 divergent hardcoded classifiers causing 73.6% misclassification

**5 call sites still needing update:**
1. `model_gateway.py` — `_cloud_providers` / `_is_cloud_provider` / `_is_cloud_provider_name` (6 call sites)
2. `observability/__init__.py:686` — substring denylist → should accept `is_cloud` param
3. `otel_exporter.py:123` — hardcoded set → delegate to registry
4. `remote_provider.py:387` — `_is_cloud_name` prefix match → delegate
5. `ingestion/pipeline.py:139` — `_is_cloud_model` (model-name match) → delegate by provider name

---

## 📁 Files Needing Regeneration in Context Packs

| File | Change Type |
|------|-------------|
| `src/omega/observability/__init__.py` | Dual-surface async API + `_sync` wrappers |
| `src/omega/observability/token_ledger.py` | `await` added to `log_event` + `record_performance` |
| `src/omega/observability/regression_watcher.py` | `await` added to `log_event` + `record_metrics_error` |
| `src/omega/oracle/oracle.py` | `await` on `record_performance` (2×) + `log_event` |
| `src/omega/oracle/health_monitor.py` | `await` on `log_event` (2×) + `record_breaker_transition`; `_is_cloud_name` removed |
| `src/omega/oracle/model_gateway.py` | `await` on `_record_provider_failure` (4 call sites); method made `async` |
| `src/omega/oracle/sovereign_search_service.py` | `get_stats()` → `stats_sync()` |
| `src/omega/workers/model_updater.py` | 8× `await log_event` + 2× `log_event_sync` |
| `src/omega/ingestion/persistence.py` | `await self.obs.log_event` |
| `src/omega/search/search_persistence.py` | `get_engine().log_event_sync` |
| `tests/contract/test_metrics_db_integration.py` | 10 tests → `async def` + `await` |
| `Makefile` | New `m23-baseline` target; fixed `check-m23-failure-integrity` |
| `pyproject.toml` | `[tool.ruff]` config (S110, S112, BLE001, E722) |
| `.githooks/pre-commit` | M23 gate wired; uses `.venv/bin/python` |
| `config/m23_baseline.txt` | **NEW** — 98 files, 294 violations baseline |
| `src/omega/oracle/provider_registry.py` | **NEW** — SSOT for provider classification |

---

## 🎯 Specific Requests for Web Claude Next Round

1. **GAP-1 Completion Review** — `ProviderRegistry` created but not wired. Review 5 call sites + SQL migration strategy (derived view `v_performance_corrected` + `provider_classification` table, not destructive `UPDATE`).

2. **M22 Provenance Audit** — Verify `GenerateResult.is_cloud` derives from `provider.is_cloud` (populated from `providers.yaml`) everywhere.

3. **M1 AnyIO Re-audit** — Verify all SQLite writes in `metrics_db.py` and `fts_index.py` properly offloaded (async migration fixed `ObservabilityEngine` but `ConversationFTSIndex.index_exchange` in `memory_store.py` still does sync writes in `add_exchange()`).

6. **M9 Error Integrity** — `_resolve_google_api_key()` bare `except Exception: return ""` in `providers.py` still present.

7. **M25 Streaming Config Drift** — `providers.yaml` has `chunk_timeout_ms: 30000` for `opencode-zen` but `opencode.json` has `chunkTimeout: 600000` — two sources of truth.

8. **Dead Config** — `provider.is_cloud` is set on load but was never read (now it will be via `ProviderRegistry`).

---

*⬡ OMEGA ⬡ KALI ⬡ CARMACK-CONTEXT-PACK-UPDATE ⬡ 2026-08-09*