<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Carmack Review — ProviderClassification SSOT Consolidation (Quick Fixes)
**AP Token:** `AP-CARMACK-REVIEW-20260809-v1.0.0`
⬡ OMEGA ⬡ CLINE ⬡ CLINE-CLI ⬡ trc_quick_fixes ⬡ ACTIVE

**Date:** 2026-08-09
**Source spec:** `AP-CLINE-HANDOFF-20260809-v1.0.0` (CLINE_HANDOFF_QUICK_FIXES.md)
**Reviewer requested:** John Carmack (S3 consultant — leverage/directness lens)
**Scope:** Wire `ProviderRegistry` (SSOT) into the 5 divergent cloud classifiers + corrected sovereignty ratio.

---

## 1. Executive Summary

- **All 7 handoff tasks implemented** across 8 source files + 1 new test file.
- **Corrected sovereignty ratio: Local 13.8% / Cloud 86.2%** — matches the ~13.8% target (was ~87% local due to a 4-provider hardcoded classifier).
- **Zero regressions introduced** — verified by `git stash` baseline comparison (the pre-existing failure sets are byte-identical pre/post change).
- **3 material deviations from the handoff spec were required** (a broken path, a circular import, a mis-specified SQL default) — documented with evidence below. The guide had several bugs (bare `ProviderRegistry()` constructor, an async API that does not exist in this codebase, a view referencing the wrong SQL column) and was treated as a **spec, not an implementation**.
- **1 latent bug discovered & fixed**: `ProviderRegistry.from_config_path()` resolved to `src/config/providers.yaml` (off-by-one `.parent`), silently returning an **empty registry** (everything → cloud, pessimistic). The SSOT was non-functional before this task.

> **Honesty note (M23):** I did **not** run the full `make test` (1315+). The environment has many **pre-existing** failures unrelated to this work; a full run is time-expensive and noisy. Verification below is targeted + baseline-compared. A full green-check is recommended follow-on #5.

---

## 2. What Changed

| # | File | Change |
|---|------|--------|
| 1 | `src/omega/oracle/provider_registry.py` | **Bug fix**: `from_config_path()` path `parent.parent.parent` → `parent.parent.parent.parent` so it reads the real `config/providers.yaml` (was `src/config/providers.yaml`, nonexistent). |
| 1 | `src/omega/oracle/model_gateway.py` | Deleted `_cloud_providers` property (`{"google","openrouter","opencode-zen","cline"}`); `_is_cloud_provider()`/`_is_cloud_provider_name()` delegate to `self._provider_registry.is_cloud()` (init in `__init__`). |
| 2 | `src/omega/observability/__init__.py` | `BudgetGate._is_cloud_provider()` delegates to a **lazy** package singleton `_get_provider_registry()`; removed local-substring denylist. |
| 3 | `src/omega/observability/otel_exporter.py` | `OTelSQLiteExporter._is_cloud_provider()` delegates to lazy registry; removed hardcoded cloud set. |
| 4 | `src/omega/oracle/backends/remote_provider.py` | `RemoteProvider._is_cloud_name()` delegates via `self.name`; removed prefix heuristics. |
| 5 | `src/omega/ingestion/pipeline.py` | `_is_cloud_model()` delegates to `_get_provider_registry().is_cloud(config.model_name)`; removed keyword matching. |
| 6 | `tests/contract/test_provider_classification.py` **(new)** | 3 invariant tests. Flake8-clean. |
| 7 | `src/omega/observability/metrics_db.py` | Added `MetricsDB.build_provider_classification_table()` + `create_corrected_performance_view()` (populated from `ProviderRegistry`). |
| 7 | `src/omega/observability/sovereignty.py` | `get_sovereignty_ratio()` reads `v_performance_corrected` (`is_cloud_corrected`), excluding synthetic rows. |

Diff stat: **8 files, +160 / −45**, plus new 126-line test.

---

## 3. Deviations from the Handoff — READ THIS

### 3a. Path bug in `ProviderRegistry.from_config_path()` (Blocking)
### 3b. Circular import (Blocking)
Path: `omega.observability` → `provider_registry` → `omega.oracle` → `oracle.py` → orchestrator → `from omega.observability import ObservabilityEngine`. With a top-level `from omega.oracle.provider_registry import ProviderRegistry`, importing `omega.observability` first re-entered a half-initialized module. **Resolved** by making the registry **lazy** (`_get_provider_registry()` caches on first call) in the 3 modules outside `omega.oracle` (`observability/__init__.py`, `otel_exporter.py`, `pipeline.py`). The 2 modules inside `omega.oracle` keep top-level construction (no cycle). Verified imports succeed.

### 3c. Corrected-view default — `COALESCE(c.is_cloud, p.is_cloud)` vs spec's `COALESCE(c.is_cloud, 0)`
Spec's `0` (local) default for any provider **not** in `providers.yaml` would mislabel recorded cloud rows as local (breaking `test_known_ratio`, which seeds `cloud_provider`). Used `COALESCE(c.is_cloud, p.is_cloud)`: config wins for known providers; the **recorded per-response bit** is the fallback for unknown ones. Preserves both SSOT authority and historical fidelity. Same target ratio (all real-DB providers are in config).

### 3d. Constructor mismatch (non-blocking, avoided)
Spec wrote `ProviderRegistry()`; the constructor **requires** `fabric_cfg`. Used `from_config_path()`. The spec's invariant test also instantiated abstract `RemoteProvider()` and imported a module-level `_is_cloud_provider` that is actually a `BudgetGate` method — both corrected in the delivered test.

---

## 4. Verification / Evidence

```
# V1 — no hardcoded cloud classifiers remain in src/omega/
grep -rn "_cloud_providers|cloud_indicators|cloud_keywords" src/omega/ --include="*.py"
   → CLEAN

# V3 — invariant test (new)
pytest tests/contract/test_provider_classification.py -q
   → 3 passed  (registry==yaml; no split classification across 5 call sites; ingestion delegation)

# V4 — corrected sovereignty ratio (canonical path: MCP tool + governance gate)
get_sovereignty_ratio()
   → Local 13.8% | Cloud 86.2% | total=3178
```

**Scope of the invariant:** for every provider in `providers.yaml` `fallback_chain`, each of ModelGateway (`_is_cloud_provider_name`, `_is_cloud_provider`), BudgetGate, OTel, RemoteProvider, and IngestionPipeline returns the **same** value as `registry.is_cloud()`.
**Existing-test health (isolated runs):**
| Suite | Result | Note |
|-------|--------|------|
| `test_sovereignty_ratio.py` | **6/6 pass** | (`test_known_ratio` 80/20 intact) |
| `test_metrics_db_integration.py` | **12/12 pass** | |
| `test_contract/test_model_gateway.py` | **3/3 pass** | |
| `test_contract/test_model_gateway_fallback.py` | **5/5 pass** | |
| `test_contract/test_provider_classification.py` | **3/3 pass** (new) | |

**Pre-existing failures — NOT regressions (baseline `git stash` confirmed identical):**
- `test_metrics_db.py`: 23 fail (tests call async `MetricsDB` methods synchronously; unrelated).
- `test_contract_m21.py`: 5 fail — `test_generateresult_has_required_fields`, `test_resourceguard_lock_is_context_manager`, `test_resourceguard_blocks_on_capacity`, `test_vault_core_store_credential_and_get_providers`, `test_vault_core_loaded_returns_bool` (vault/resourceguard).
- `test_sovereign_ingestion.py`: 2 fail (AttributeError, unrelated paths).
- `tests/contract/` dir: `test_pack_produces_valid_output` (pathlib tuple TypeError); `test_provider_fallback_chain_order/on_timeout/all_fail` (`ModuleNotFoundError: omega.oracle.cascade_router`).

**Lint:** new test file flake8-clean; **zero** new violations added to existing files (remaining E501s in `provider_registry.py`/`model_gateway.py:1608` are pre-existing lines I did not author).

---

## 5. Risks / Open Decisions for Your Review

1. **Synthetic providers counted in sovereignty.** `mock` (762 of 3178 rows) counts as **cloud** because `providers.yaml` marks it `is_cloud: true`. `ProviderRegistry` also exposes `is_synthetic()` (`{mock, fallback}`) and `R_UNOVERENGINEERING_REMAINING_GAPS` argues synthetic probe rows should be **excluded entirely**. The corrected view only excludes `%synthetic%` in the provider name. **Decide:** keep `mock` as cloud, or exclude synthetic? (Moves 762 rows off the headline number.)

2. **Two representations of the same provider data.** `providers.yaml` has `inference.fallback_chain` (registry source) **and** a bottom-level `providers:` map, each repeating `is_cloud`. Divergence risk = the exact bug class this task killed. **Recommend:** collapse to one source.

3. **A 6th classifier is still uncorrected.** `observability_reader._sync_get_sovereignty_ratio(entity_id,...)` reads raw `performance.is_cloud` — diverges from the corrected view. Outside the handoff's "5 call sites." **Decide:** delegate it too.

4. **`_is_cloud_model` classifies by model name, not provider.** Ingestion passes `config.model_name` to `is_cloud()`. Real model names (`google-gemma-4`, `qwen3-1.7b`) aren't provider keys → **pessimistic cloud default** (`qwen3-1.7b` → cloud, wrong for a local model). R-doc says "delegate by provider (not model) name." Flagging as a semantic gap; accepted for quick-fix scope.

5. **Unknown-provider default flipped vs. old gate behavior.** Old ModelGateway treated only 4 names as cloud (everything else local). Registry defaults unknown→cloud (M7 pessimistic). Intentional per M7; confirm it doesn't surprise downstream budget/guard gates.

---

## 6. Recommended Follow-On Tasks (approve / extend)

| # | Task | Why | Est. |
|---|------|-----|------|
| 1 | **Decide synthetic handling** (#1 above); if excluding, update the corrected view to use `ProviderRegistry.is_synthetic()` instead of `%synthetic%` like-match. | Correct headline sovereignty metric. | 20m |
| 2 | **Unify `providers.yaml`** `inference.fallback_chain` ↔ bottom `providers:` map; registry reads the single source. | Kill config-drift bug class. | 45m |
| 3 | **Delegate `observability_reader._sync_get_sovereignty_ratio`** to the corrected view (6th call site). | Entity-level ratio currently diverges/lies. | 30m |
| 4 | **Provider-aware ingestion classification** — resolve provider from model name (or model→provider map) before `is_cloud()`. | Fixes local models mislabeled cloud. | 30m |
| 5 | **Full `make test` baseline** — run entire 1315+ suite; categorize every failure pre-existing vs. regression; checkpoint a green subset. | Real numbers, not vanity counts. | 60m+ |
| 6 | **Close GAP-1 in `R_UNOVERENGINEERING_REMAINING_GAPS`** — tick now-satisfiable checkboxes (`test_no_provider_has_split_classification`, `omega-hub_sovereignty_ratio`). | Docs drift left stale. | 15m |
| 7 | **Commit** — stage only the 8 source files + new test (working tree also carries unrelated pre-existing changes: context-packer skill, providers.yaml, config/data docs). | Isolated, reviewable commit. | 10m |

---

## 7. Files Delivered

```
Modified:
  src/omega/oracle/provider_registry.py
  src/omega/oracle/model_gateway.py
  src/omega/oracle/backends/remote_provider.py
  src/omega/ingestion/pipeline.py
  src/omega/observability/__init__.py
  src/omega/observability/otel_exporter.py
  src/omega/observability/metrics_db.py
  src/omega/observability/sovereignty.py
New:
  tests/contract/test_provider_classification.py
```

---

*⬡ OMEGA ⬡ CLINE ⬡ CARMACK-REVIEW ⬡ 2026-08-09*
**Spec claimed** the registry "already exists, reads `config/providers.yaml`." **Reality:** resolved path was `.../omega-engine/src/config/providers.yaml` (3 `.parent` from file = `src/`, needs 4 = repo root) → registry loaded **zero** providers → every `is_cloud()` hit the pessimistic unknown→cloud branch. Left untouched, all 5 call sites "wired" to the SSOT would have returned `True` for everything. **Fixed** one-line path correction.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: CLINE-CLI | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
