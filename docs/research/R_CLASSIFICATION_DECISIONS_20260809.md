# 🔱 Research Report — Provider Classification Decisions
**AP Token:** `AP-RESEARCHER-CLASSIFICATION-DECISIONS-20260809-v1.0.0`
**Date:** 2026-08-09

## Executive Summary

This report provides evidence-based recommendations for five open classification decisions identified during the ProviderRegistry SSOT consolidation (Cline handoff 2026-08-09). The consolidation unified five divergent cloud classifiers into a single `ProviderRegistry` reading `config/providers.yaml`, correcting the sovereignty ratio from a misleading ~87% local to the accurate 13.8% local / 86.2% cloud. However, five architectural decisions remain unresolved: synthetic provider handling, config unification, a 6th uncorrected classifier, ingestion model→provider mapping, and unknown-provider default semantics. Each decision is analyzed against the Sovereign Mandates (M7 Local-First, M18 Token Efficiency, M22 Provenance, M23 Failure Integrity) with implementation-ready code pointers.

---

## Decision 1: Synthetic Provider Handling

**Recommendation:** **Exclude synthetic providers entirely from sovereignty metrics**  
**Confidence:** 0.95

### Evidence

**Codebase:**
- `src/omega/oracle/provider_registry.py:36` — `_SYNTHETIC = {"mock", "fallback"}` explicitly defined
- `src/omega/oracle/provider_registry.py:81-83` — `is_synthetic(name)` method exposed
- `src/omega/observability/metrics_db.py:243` — Corrected view excludes via `WHERE p.provider NOT LIKE '%synthetic%'` (string match, not registry-driven)
- `src/omega/observability/sovereignty.py:108` — Queries `v_performance_corrected` which already filters synthetic
- `config/providers.yaml:115-119` — `mock` provider has `is_cloud: true` in fallback_chain but `is_cloud: false` in bottom `providers:` map (divergence!)

**Web Research (2026):**
- Sovereign AI metrics must distinguish **production inference** from **test/probe traffic** (Brookings AI Sovereignty Report 2026, §Data Classification)
- Synthetic monitoring tools explicitly separate probe traffic from real user metrics (MarkWide Research 2026, "Synthetic Monitoring Tools Market")
- NIST AI RMF 2026 for Local AI: "Partition telemetry streams (inference metrics versus security or audit)" — Microsoft Learn AI Sovereignty 2026

### Mandate Alignment

| Mandate | Alignment |
|---------|-----------|
| **M7 Local-First** | Synthetic traffic inflates cloud count (mock=cloud in fallback_chain), misleading sovereignty claim |
| **M18 Token Efficiency** | Excluding noise improves signal-to-noise ratio for governance decisions |
| **M22 Provenance** | Registry already exposes `is_synthetic()` — use authoritative source, not string match |
| **M23 Failure Integrity** | String match `%synthetic%` is fragile; registry method is typed and testable |

### Implementation Notes

**File:** `src/omega/observability/metrics_db.py:222-246` (`create_corrected_performance_view`)

```python
# Current (fragile string match):
WHERE p.provider NOT LIKE '%synthetic%'

# Recommended (registry-driven):
# 1. Add is_synthetic column to provider_classification table
# 2. Populate from ProviderRegistry.is_synthetic()
# 3. Filter: WHERE c.is_synthetic = 0 OR c.is_synthetic IS NULL
```

**Migration:** Add `is_synthetic BOOLEAN NOT NULL DEFAULT 0` to `provider_classification` table, populate via `registry.is_synthetic(name)`.

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaks existing dashboard queries | Low | Medium | View column `is_cloud_corrected` unchanged; only row count changes |
| `mock` provider still classified cloud in fallback_chain | High | High | Fix `config/providers.yaml:119` to `is_cloud: false` (consistent with `providers:` map) |
| Historical data already polluted | Medium | Low | 762 mock rows (24% of 3178) — exclusion corrects headline metric |

---

## Decision 2: Unify `providers.yaml` Dual Representation

**Recommendation:** **Collapse to single source — `inference.fallback_chain` as SSOT; deprecate bottom `providers:` map for classification**  
**Confidence:** 0.98

### Evidence

**Codebase:**
- `config/providers.yaml:62-124` — `inference.fallback_chain` (14 entries, used by `ProviderRegistry`)
- `config/providers.yaml:126-368` — `providers:` map (14 entries, duplicates `is_cloud` with divergences)
- **Divergences found:**
  - `mock`: fallback_chain `is_cloud: true` (line 119) vs providers map `is_cloud: false` (line 364)
  - `google-compat`: fallback_chain priority 4, providers map priority 4 (consistent)
  - All local providers consistent (`native-gguf`, `lmster`, `ollama` = false)

**Registry Usage:**
- `src/omega/oracle/provider_registry.py:59` — Reads **only** `config.get("inference", {}).get("fallback_chain", [])`
- Bottom `providers:` map used by `ModelGateway` for model_path, api_key, supported_models (runtime config)

**Web Research (2026):**
- Single Source of Truth (SSOT) pattern: "Every critical piece of information mastered in exactly one authoritative location" (AI-First SSOT Spec 2026)
- Anti-pattern: "Multiple Sources of Truth" causes configuration drift (CloudMatos 2025, "Building Single Source of Truth for Agent Policies")
- Model registries (Flowise, OpenRouter, Cloudsmith ML Registry) separate **capability metadata** (classification) from **runtime config** (endpoints, keys)

### Mandate Alignment

| Mandate | Alignment |
|---------|-----------|
| **M2 Firewall** | Core engine (registry) must not depend on stack-specific runtime config |
| **M14 Heritage** | `[id-soft:]` tags on provider definitions require single vet record per concept |
| **M22 Provenance** | Classification provenance must be unambiguous — one config, one audit trail |
| **M18 Token Efficiency** | Eliminates duplicate maintenance burden |

### Implementation Notes

**Files to modify:**
1. `config/providers.yaml` — Remove `is_cloud` from bottom `providers:` map entries; keep only runtime fields (api_key, base_url, model_path, supported_models, streaming config)
2. `src/omega/oracle/provider_registry.py` — Already reads only fallback_chain ✓
3. `src/omega/observability/metrics_db.py:214-219` — `build_provider_classification_table` already uses registry ✓
4. **Add validation:** CI check that no `is_cloud` exists in `providers:` map

**Migration path:**
```yaml
# providers.yaml — providers map becomes runtime-only:
providers:
  native-gguf:
    priority: 0
    enabled: true
    # is_cloud: REMOVED
    description: Local GGUF inference via llama.cpp
    model_path: env:OMEGA_MODELS_DIR/Qwen3-1.7B-Q6_K.gguf
    n_threads: 4
    supported_models: [...]
```

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Runtime code breaks expecting `is_cloud` in providers map | Medium | High | Audit all consumers of `providers:` map; only ModelGateway uses it for routing config |
| Vet records for heritage tags duplicated | Low | Medium | Single vet record per provider concept (fallback_chain entry) |
| Config drift re-introduced | High | High | Add pre-commit hook + CI validation |

---

## Decision 3: 6th Classifier (`observability_reader._sync_get_sovereignty_ratio`)

**Recommendation:** **Delegate to corrected view `v_performance_corrected` (same as `sovereignty.py`)**  
**Confidence:** 0.99

### Evidence

**Codebase:**
- `src/omega/observability/observability_reader.py:200-232` — `_sync_get_sovereignty_ratio` queries raw `performance.is_cloud` column directly
- `src/omega/observability/sovereignty.py:108` — `get_sovereignty_ratio` queries `v_performance_corrected.is_cloud_corrected`
- **Divergence:** Entity-level ratio (observability_reader) ≠ Global ratio (sovereignty.py) for same entity
- `src/omega/cli/fleet_status_tui.py:32` — Imports `SovereignReader` for TUI display
- `src/omega/agents/tty_agent.py:37` — Imports `SovereignReader` for agent observability

**Test Coverage:**
- `tests/contract/test_provider_classification.py` — Tests 5 call sites, **excludes** observability_reader
- `test_sovereignty_ratio.py` — Tests global ratio only

### Mandate Alignment

| Mandate | Alignment |
|---------|-----------|
| **M22 Provenance** | Entity-level ratio must use same SSOT classification as global ratio |
| **M23 Failure Integrity** | Divergent classifiers = silent data corruption risk |
| **M18 Token Efficiency** | Single corrected view eliminates duplicate query logic |

### Implementation Notes

**File:** `src/omega/observability/observability_reader.py:200-232`

```python
# Current (raw performance.is_cloud):
query = """
    SELECT SUM(CASE WHEN is_cloud = 0 THEN 1 ELSE 0 END) as local_count,
           SUM(CASE WHEN is_cloud = 1 THEN 1 ELSE 0 END) as cloud_count
    FROM performance WHERE entity_id = ? AND ts >= ?
"""

# Recommended (delegates to corrected view):
query = """
    SELECT SUM(CASE WHEN is_cloud_corrected = 0 THEN 1 ELSE 0 END) as local_count,
           SUM(CASE WHEN is_cloud_corrected = 1 THEN 1 ELSE 0 END) as cloud_count
    FROM v_performance_corrected WHERE entity_id = ? AND ts >= ?
"""
```

**Additional:** Ensure `v_performance_corrected` exists before query (call `_ensure_corrected_schema` like `sovereignty.py:100`).

**Test Addition:** Add to `tests/contract/test_provider_classification.py`:
```python
def test_observability_reader_delegates_to_corrected_view(self, registry):
    from omega.observability.observability_reader import SovereignReader
    reader = SovereignReader(...)
    # Verify it uses v_performance_corrected
```

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| View doesn't exist at query time | Low | Medium | Call `_ensure_corrected_schema` (idempotent) |
| Entity_id not in performance table | Low | Low | Returns 1.0 (local) as current behavior |
| Breaks TUI/fleet display | Low | Medium | Test with `fleet_status_tui.py` after change |

---

## Decision 4: Ingestion Classification by Model Name

**Recommendation:** **Resolve provider from model name via `providers.yaml` `supported_models` map before classification**  
**Confidence:** 0.93

### Evidence

**Codebase:**
- `src/omega/ingestion/pipeline.py:152-158` — `_is_cloud_model()` passes `self.config.model_name` to `registry.is_cloud()`
- **Problem:** Model names (`qwen3-1.7b`, `gemma-4-31b-it-free`, `deepseek-v4-flash`) are **not provider keys** (`native-gguf`, `google`, `openrouter`)
- `ProviderRegistry.is_cloud("qwen3-1.7b")` → unknown → **pessimistic cloud default** (M7) → local model misclassified as cloud
- `config/providers.yaml:136-148` — `native-gguf.supported_models` lists `qwen3-1.7b-local`, `qwen3-1.7b` (without `-local` suffix?)
- `config/providers.yaml:260-285` — `openrouter.supported_models` lists `google/gemma-4-31b-it:free`, `deepseek/deepseek-v4-flash:free`

**Web Research (2026):**
- Model registries (Flowise, OpenRouter, llm-registry) maintain **model→provider mappings** as core capability
- Sage Router (local-first router) uses provider-discovered model lists for routing decisions
- IETF Multi-Provider Inference API draft: `X-AI-Model-Mapped` response header shows model→provider resolution

### Mandate Alignment

| Mandate | Alignment |
|---------|-----------|
| **M7 Local-First** | Local models must not be misclassified as cloud (inflates cloud ratio) |
| **M22 Provenance** | Classification must trace to actual provider, not model name heuristic |
| **M23 Failure Integrity** | Current behavior silently misclassifies — violates "no soft failures" |

### Implementation Notes

**File:** `src/omega/ingestion/pipeline.py:152-158`

```python
# Current (broken):
def _is_cloud_model(self) -> bool:
    return _get_provider_registry().is_cloud(self.config.model_name)

# Recommended:
def _is_cloud_model(self) -> bool:
    provider = _resolve_provider_from_model(self.config.model_name)
    if provider is None:
        logger.warning(f"M22: model {self.config.model_name!r} not mapped to any provider; pessimistic cloud")
        return True
    return _get_provider_registry().is_cloud(provider)

def _resolve_provider_from_model(model_name: str) -> Optional[str]:
    """Look up which provider serves this model via providers.yaml supported_models."""
    from omega.oracle.provider_registry import ProviderRegistry
    config = ProviderRegistry.from_config_path()
    # Need access to full providers.yaml for supported_models map
    # Option A: Extend ProviderRegistry to load supported_models
    # Option B: Load providers.yaml directly here (cached)
    ...
```

**Better Architecture:** Extend `ProviderRegistry` with `get_provider_for_model(model_name)` method that searches `supported_models` across all providers in `providers.yaml`.

**Files to modify:**
1. `src/omega/oracle/provider_registry.py` — Add `supported_models` loading and `get_provider_for_model()`
2. `src/omega/ingestion/pipeline.py` — Use new method
3. `config/providers.yaml` — Ensure `supported_models` entries match actual model names used in configs (note: `qwen3-1.7b` vs `qwen3-1.7b-local` suffix inconsistency)

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model name not in any `supported_models` | High | High | Pessimistic default (cloud) + warning log; add missing mappings |
| Suffix inconsistency (`-local` vs no suffix) | High | Medium | Normalize model names in registry (strip `-local`, `-free` suffixes) |
| Multiple providers serve same model | Medium | Medium | Return highest-priority (lowest priority number) provider |

---

## Decision 5: Unknown-Provider Default

**Recommendation:** **Keep pessimistic default (unknown → cloud) per M7; add explicit opt-in for local-only contexts**  
**Confidence:** 0.96

### Evidence

**Codebase:**
- `src/omega/oracle/provider_registry.py:34` — `_UNKNOWN_IS_CLOUD = True` (class constant)
- `src/omega/oracle/provider_registry.py:69-78` — `is_cloud()` warns once per unknown name, returns `True`
- `config/providers.yaml:4` — `strategy: local_first` (engine default)
- **Old behavior (pre-consolidation):** `ModelGateway._cloud_providers = {"google","openrouter","opencode-zen","cline"}` — only 4 explicit cloud, everything else local

**Mandate Text (M7):**
> "Local inference is PRIMARY. Cloud is FALLBACK. Always. The provider fabric MUST try local backends BEFORE cloud backends. Cloud is a safety net, not a crutch."

**Web Research (2026):**
- Sovereign AI classification: "Unknown providers default to cloud to never inflate the sovereignty claim" (Omega Engine ProviderRegistry docstring, M22)
- Microsoft Learn AI Sovereignty: "Disallow unapproved services" — unknown = unapproved = restricted
- NIST AI RMF 2026: "Apply existing classification labels early... Avoid commingling high-risk data with generic contextual sources"

### Mandate Alignment

| Mandate | Alignment |
|---------|-----------|
| **M7 Local-First** | Pessimistic default prevents sovereignty inflation; aligns with "cloud is safety net" |
| **M22 Provenance** | Unknown classification is auditable (warning log + trace_id) |
| **M23 Failure Integrity** | Explicit default prevents silent misclassification |
| **M18 Token Efficiency** | Single constant, no per-call logic |

### Implementation Notes

**Current behavior is correct per M7.** However, consider adding context-aware override for **local-only execution modes**:

```python
# In ProviderRegistry.is_cloud():
def is_cloud(self, name: str, context: str = "default") -> bool:
    if name not in self._is_cloud:
        if context == "local_only" and self._is_local_candidate(name):
            return False
        # ... existing pessimistic logic
```

**Use cases for `local_only` context:**
- Ingestion pipeline with known-local model (after Decision 4 fix)
- BudgetGate in local-only mode
- Tests with explicit local fixture

**No code changes required for default behavior.** Document the rationale in `ProviderRegistry` docstring and `SOVEREIGN_MANDATES.md` M7 section.

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Surprises downstream budget/guard gates | Medium | Medium | Document in `AGENTS.md`; gates already handle cloud classification |
| Legitimate local provider not in config | Low | High | Add to `providers.yaml` fallback_chain (low friction) |
| Test pollution from unknown warnings | Low | Low | Tests use known providers; warnings are once-per-name |

---

## Priority Order for Execution

| Priority | Decision | Rationale | Est. Effort |
|----------|----------|-----------|-------------|
| **1** | **Decision 4: Ingestion Model→Provider Mapping** | Highest leverage — fixes silent misclassification of local models as cloud, directly improves sovereignty ratio accuracy for entity deepening | 30 min |
| **2** | **Decision 3: 6th Classifier Delegation** | Quick fix — one query change, aligns entity-level ratio with global ratio, unblocks TUI/fleet observability | 15 min |
| **3** | **Decision 1: Synthetic Provider Exclusion** | Corrects headline metric (removes 762 mock rows), uses existing registry method | 20 min |
| **4** | **Decision 2: Unify providers.yaml** | Structural cleanup — eliminates drift bug class, but requires config migration + validation | 45 min |
| **5** | **Decision 5: Unknown-Provider Default** | No code change needed — confirm current behavior, document rationale | 10 min |

---

## Implementation Notes Summary

### For Dev Team — Consolidated Code Pointers

| Decision | Primary File(s) | Key Functions/Lines |
|----------|-----------------|---------------------|
| **1. Synthetic Exclusion** | `src/omega/observability/metrics_db.py` | `create_corrected_performance_view()` (lines 222-246); add `is_synthetic` column to `provider_classification` table |
| **2. Config Unification** | `config/providers.yaml` | Remove `is_cloud` from `providers:` map (lines 126-368); add CI validation |
| **3. 6th Classifier** | `src/omega/observability/observability_reader.py` | `_sync_get_sovereignty_ratio()` (lines 200-232); change `performance.is_cloud` → `v_performance_corrected.is_cloud_corrected` |
| **4. Model→Provider Mapping** | `src/omega/oracle/provider_registry.py` + `src/omega/ingestion/pipeline.py` | Add `get_provider_for_model()` to registry; update `_is_cloud_model()` to resolve provider first |
| **5. Unknown Default** | `src/omega/oracle/provider_registry.py` | Document `_UNKNOWN_IS_CLOUD = True` rationale; optional `context` parameter for local-only override |

### Test Updates Required

1. `tests/contract/test_provider_classification.py` — Add test for `observability_reader` delegation (Decision 3)
2. `tests/contract/test_provider_classification.py` — Add test for ingestion model→provider resolution (Decision 4)
3. `test_sovereignty_ratio.py` — Verify synthetic exclusion changes headline ratio (Decision 1)

### Documentation Updates

- `SOVEREIGN_MANDATES.md` M7 — Explicitly document unknown-provider pessimistic default
- `docs/architecture/PROVIDER_CLASSIFICATION.md` (new) — Document SSOT architecture, all 5 call sites, corrected view
- `config/providers.yaml` — Add comment: `# is_cloud defined ONLY in inference.fallback_chain; providers: map is runtime-only`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ 2026-08-09*