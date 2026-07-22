# 🔱 Model Registry Implementation Review & Gap Analysis
**AP Token**: `AP-MODEL-REGISTRY-GAP-ANALYSIS-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ GAP-ANALYSIS ⬡ 2026-07-19

---

## 1. Executive Summary

The Model Registry (`config/model_registry/` + `src/omega/model_registry/`) is a **production-grade hybrid file+DB system** with 35 model cards, 9 provider configs, and 9 research profiles. The architecture follows the Hybrid Model Registry design from `MODEL_REGISTRY_INTEGRATION_ARCHITECTURE.md` — YAML frontmatter model cards as source of truth, SQLite index as queryable derived artifact.

**Overall Assessment**: **Solid foundation with critical schema gaps and integration disconnects**. The registry loads and validates correctly (276/276 tests pass), but key fields are missing from the dataclass schema, provider mappings are inaccurate, and the ModelGateway still reads `config/providers.yaml` instead of the registry.

### Key Metrics
| Metric | Value |
|--------|-------|
| Model Cards | 35 (30 cloud, 4 local, 1 stealth) |
| Provider Configs | 9 |
| Research Profiles | 9 |
| SQLite Index | 35 models, 9 providers, 9 profiles |
| Validation Gates | 8 defined, 7 passing (PROVIDER_CHAIN_COMPLETE fails) |

---

## 2. Schema Completeness Matrix

### 2.1 ModelCard Dataclass vs. Model Card Files vs. CURRENT_MODELS.md

| Field Category | ModelCard Dataclass | Model Card Files (YAML) | CURRENT_MODELS.md Schema | Status |
|----------------|---------------------|-------------------------|--------------------------|--------|
| **Core Identity** | ✅ model_id, display_name, version, provider, platform, tier, status | ✅ All present | ✅ All present | **COMPLETE** |
| **Capabilities** | ✅ reasoning, code_generation, knowledge, creative, tool_use, structured_output, multimodal | ⚠️ **EXTRA fields**: code_execution, parallel_search, workspace_integration (Gemini 2.5 Pro) | ✅ Base 4 + tool_use, structured_output | **INCOMPLETE** — Dataclass missing 3 capability fields |
| **Economics** | ✅ pricing (input/output/cached/batch), free_tier, cost_per_1k_tokens_usd, latency_p99_ms, uptime_percent | ✅ All present | ✅ All present | **COMPLETE** |
| **Routing** | ✅ engine_routable, opencode_cli_only, recommended_engine_alternative | ✅ All present | ✅ All present | **COMPLETE** |
| **Identity** | ✅ IdentityHistory (original, current, swap_detected, last_verified) | ✅ Present for stealth models | ✅ Present for big-pickle | **COMPLETE** |
| **Community** | ✅ CommunityIntelligence (rating, notes) | ✅ All present | ✅ All present | **COMPLETE** |
| **Live API State** | ✅ LiveAPIState (source, last_verified, last_verified_free) | ✅ All present | ✅ All present | **COMPLETE** |
| **Research Profile** | ✅ ResearchProfile (reasoning_depth, tool_fidelity, failure_signature, shadow_focus, guardrails) | ✅ All present | ❌ Not in CURRENT_MODELS.md | **REGISTRY-ONLY** |
| **Empirical Evidence** | ✅ EmpiricalEvidence (test_runs[], synergies[]) | ✅ Present (some empty) | ❌ Not in CURRENT_MODELS.md | **REGISTRY-ONLY** |
| **Provider Fabric** | ✅ ProviderFabric (available_via[], local_first_priority) | ✅ All present | ❌ Not in CURRENT_MODELS.md | **REGISTRY-ONLY** |
| **Metadata** | ✅ tags, created_at, updated_at, schema_version | ✅ All present | ✅ last_updated, last_verified_free | **COMPLETE** |
| **❌ MISSING: Parameters** | **NO** | **NO** | **NO** | **CRITICAL GAP** |

### 2.2 Critical Missing Field: `parameters`

**The `parameters` field is completely absent** from:
- ModelCard dataclass
- All 35 model card YAML files
- CURRENT_MODELS.md schema
- SQLite index schema

**What should be in `parameters`:**
```yaml
parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.1
  max_tokens: 4096  # or model-specific default
  stop_sequences: ["User:", "\n\n"]
  # Model-specific overrides
  gemma_4_31b:
    temperature: 0.85
    repetition_penalty: 1.2
    logit_bias: {759: -10.0, 2149: -10.0}  # Anti-repetition tokens
```

**Impact**: ModelGateway hardcodes sampling parameters per-model (see `model_gateway.py` Gemma 4 31B special case). No centralized parameter configuration exists.

---

## 3. Per-Model Gap Table (35 Models)

| # | Model ID | Platform | Tier | Missing `parameters` | Provider Mapping Issues | Context Window Verified | Capability Scores Sourced | Pricing Verified | Release Date | Identity History |
|---|----------|----------|------|---------------------|------------------------|------------------------|--------------------------|------------------|--------------|------------------|
| 1 | anthropic/claude-sonnet-5-high-thinking | cloud | T3 | ❌ | Provider: antigravity (should be anthropic/opencode-zen) | 1M ✅ | No source cited | Intro pricing cited | 2026-06-30 | null |
| 2 | anthropic/claude-opus-4.8 | cloud | T3 | ❌ | Provider: antigravity | 1M ✅ | No source cited | $5/$25 cited | Unknown | null |
| 3 | anthropic/claude-haiku-4.5-extended | cloud | T2 | ❌ | Provider: antigravity | 200K ✅ | No source cited | $0.25/$1.25 cited | Unknown | null |
| 4 | google/gemini-2.5-pro | cloud | T3 | ❌ | Provider: google ✅ | 1M ✅ | No source cited | $1.25/$5.00 cited | 2026-06-15 | null |
| 5 | google/gemini-2.5-flash | cloud | T2 | ❌ | Provider: google ✅ | 1M ✅ | No source cited | $0.075/$0.30 cited | Unknown | null |
| 6 | google/gemma-4-31b-it:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 262K ✅ | No source cited | Free ✅ | 2026-05-17 | null |
| 6 | google/gemma-4-26b-a4b-it:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 262K ✅ | No source cited | Free ✅ | Unknown | null |
| 7 | xai/grok-4.3-web | cloud | T3 | ❌ | Provider: xai ✅ | 1M ✅ | No source cited | $1.25/$2.50 cited | Unknown | null |
| 8 | xai/grok-4.1-fast-web | cloud | T2 | ❌ | Provider: xai ✅ | 2M ✅ | No source cited | $0.125/$0.25 cited | Unknown | null |
| 9 | deepseek/deepseek-v4-flash:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 1M ✅ | No source cited | Free ✅ | 2026-04-24 | null |
| 10 | minimax/minimax-m2.5:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 204K ✅ | No source cited | Free ✅ | Unknown | null |
| 11 | nvidia/nemotron-3-super-120b-a12b:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 1M ✅ | No source cited | Free ✅ | Unknown | null |
| 12 | qwen/qwen3-next-80b-a3b-instruct:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 262K ✅ | No source cited | Free ✅ | Unknown | null |
| 13 | openai/gpt-oss-120b:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 14 | arcee-ai/trinity-large-thinking:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 262K ✅ | No source cited | Free ✅ | Unknown | null |
| 15 | nousresearch/hermes-3-llama-3.1-405b:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 16 | qwen/qwen3-coder:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 262K ✅ | No source cited | Free ✅ | Unknown | null |
| 17 | meta-llama/llama-3.3-70b-instruct:free | cloud | T3 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 18 | nvidia/nemotron-3-nano-30b-a3b:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 256K ✅ | No source cited | Free ✅ | Unknown | null |
| 19 | nvidia/nemotron-3-nano-omni-30b-a3b:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 256K ✅ | No source cited | Free ✅ | Unknown | null |
| 20 | nvidia/nemotron-nano-12b-v2-vl:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 128K ✅ | No source cited | Free ✅ | Unknown | null |
| 21 | nvidia/nemotron-nano-9b-v2:free | cloud | T1 | ❌ | Provider: openrouter ✅ | 128K ✅ | No source cited | Free ✅ | Unknown | null |
| 22 | openai/gpt-oss-20b:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 23 | z-ai/glm-4.5-air:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 24 | cognitivecomputations/dolphin-mistral-24b-venice-edition:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 32K ✅ | No source cited | Free ✅ | Unknown | null |
| 25 | poolside/laguna-m.1:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 26 | poolside/laguna-xs.2:free | cloud | T2 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 27 | liquid/lfm-2.5-1.2b-instruct:free | cloud | T1 | ❌ | Provider: openrouter ✅ | 32K ✅ | No source cited | Free ✅ | Unknown | null |
| 28 | meta-llama/llama-3.2-3b-instruct:free | cloud | T1 | ❌ | Provider: openrouter ✅ | 131K ✅ | No source cited | Free ✅ | Unknown | null |
| 29 | openrouter/free | cloud | T2 | ❌ | Provider: openrouter (router, not model) | 200K ❓ | No source cited | Free ✅ | Unknown | null |
| 30 | opencode/big-pickle | stealth | T2 | ❌ | Provider: opencode-zen ✅ | 200K ✅ | No source cited | Free ✅ | 2026-05-04 | ✅ Complete |
| 31 | nemotron-3-ultra-local | local | T3 | ❌ | Provider: antigravity ❌ (should be native-gguf) | 128K ✅ | No source cited | Free ✅ | 2026-06-10 | null |
| 32 | qwen-3.5-72b-local | local | T3 | ❌ | Provider: qwen ❌ (should be native-gguf) | 128K ✅ | No source cited | Free ✅ | 2026-06-15 | null |
| 33 | gpt-oss-120b-local | local | T3 | ❌ | Provider: openai ❌ (should be native-gguf) | 128K ✅ | No source cited | Free ✅ | Unknown | null |
| 34 | llama-4-scout-local | local | T3 | ❌ | Provider: native-gguf ✅ | 10M ✅ | No source cited | Free ✅ | Unknown | null |
| 35 | qwen-3.5-72b-local (duplicate?) | local | T3 | ❌ | Provider: qwen | 128K | No source cited | Free ✅ | Unknown | null |

### Summary of Per-Model Gaps

| Gap Category | Count | Severity |
|--------------|-------|----------|
| **Missing `parameters` field** | 35/35 | **CRITICAL** |
| **Provider mapping incorrect** | 4/35 (nemotron-3-ultra-local, qwen-3.5-72b-local, gpt-oss-120b-local, plus 3 Anthropic models mapped to antigravity) | **HIGH** |
| **Capability scores without benchmark sources** | 35/35 | **HIGH** |
| **Pricing/free tier unverified** | ~20/35 | **MEDIUM** |
| **Release dates unknown** | ~25/35 | **LOW** |
| **Identity history incomplete** | 34/35 (only big-pickle has it) | **LOW** |
| **Extra capability fields not in schema** | 1 model (Gemini 2.5 Pro) | **MEDIUM** |

---

## 4. Registry-Level Issues

### 4.1 Duplicate Provider Priority (CRITICAL)
```yaml
# registry.yaml fallback_chain:
- provider: "google"
  priority: 4
- provider: "openrouter"
  priority: 4  # DUPLICATE!
```
**Impact**: Validation gate `PROVIDER_CHAIN_COMPLETE` fails. Non-deterministic provider ordering when priorities collide.

### 4.2 Research Profile Coverage Gap
- **9 research profiles** vs **35 models** = 26 models without dedicated research profile
- Models fall back to `default.yaml` profile (generic settings)
- No automatic linking between model cards and research profiles

### 4.3 Provider Availability Matrix Incomplete
- Provider configs list `supported_models` but no cross-validation against model cards
- Model cards list `provider_fabric.available_via` but no validation against provider configs
- No matrix showing which provider serves which model at which priority

### 4.4 Registry Metadata Missing Verification Fields
`registry.yaml` lacks:
- `last_validation_run`
- `validation_gate_results` (per-gate pass/fail)
- `data_freshness` timestamps per model
- `schema_migration_history`

### 4.5 SQLite Index Schema Gaps
Missing columns in `models` table:
- `parameters` (JSON blob)
- `capability_code_execution`, `capability_parallel_search`, `capability_workspace_integration`
- `identity_original`, `identity_current`, `identity_swap_detected`, `identity_last_verified`
- `community_rating`, `community_notes` (stored as JSON)
- `live_api_source`, `live_api_last_verified`, `live_api_last_verified_free`
- `research_profile_*` fields (currently in separate table only)
- `empirical_evidence` (JSON blob)
- `provider_fabric` (JSON blob)

---

## 5. Service Implementation Gaps

### 5.1 `ModelRegistry.load_all()` — Legacy Model DB Warning
```python
# registry.py:107-108
except Exception as e:
    print(f"Warning: Failed to load legacy model DB: {e}")
```
**Issue**: Silent failure with generic warning. The legacy `CURRENT_MODELS.md` has YAML parsing errors (backticks in markdown). Should:
- Log structured error with line/column
- Continue loading other models
- Report which models failed to load

### 5.2 `ModelRegistry.build_index()` — Doesn't Index New Fields
The SQLite index only includes the 28 columns defined in `CREATE TABLE models`. It **does not index**:
- `parameters` field (doesn't exist in dataclass)
- Extra capability fields (code_execution, etc.)
- Identity history fields
- Community intelligence fields
- Live API state fields
- Research profile fields (separate table only)
- Empirical evidence (JSON blob)
- Provider fabric (JSON blob)

### 5.3 `query.py` — No Parameter Querying
```python
# query.py - no method for querying by parameters
def get_capability_leaders(self, capability: str, limit: int = 5):
    # Only supports: reasoning, code_generation, knowledge, creative
```
Cannot query/filter by `parameters` (doesn't exist) or by extra capabilities.

### 5.4 No `make model-sync` Target
**Missing**: Makefile target to regenerate `config/providers.yaml` from registry data.
Current flow: `providers.yaml` → ModelGateway (one-way)
Needed flow: Registry → `providers.yaml` (generated artifact)

### 5.5 Validation Script Gaps
`scripts/model_registry_validate.py` only checks:
- Required fields present
- No duplicate model_ids
- Provider chain priorities (fails due to duplicate 4)
- Index sync count

**Missing validations**:
- `parameters` field presence
- Capability scores in range [0,1]
- Context window > 0 and reasonable (< 10M)
- Pricing non-negative
- Provider mappings consistent (model.provider in registry._providers)
- Research profile exists for each model
- Synergies bidirectional
- Identity history format valid

---

## 6. Integration Gaps

### 6.1 ModelGateway Reads `config/providers.yaml`, Not Registry
**File**: `src/omega/oracle/model_gateway.py`
```python
providers_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "providers.yaml"
with open(providers_path, "r") as f:
    config = yaml.safe_load(f)
fabric_config = config.get("inference", {}).get("fallback_chain", [])
```
**Impact**: 
- Registry is **not the source of truth** for provider fabric
- Changes to registry don't propagate to runtime
- Duplicate maintenance burden

### 6.2 No Provider Config Generation from Registry
Needed: `scripts/generate_providers_yaml.py` that:
1. Loads registry
2. Builds fallback_chain from `registry.yaml` + provider configs
3. Merges model-specific overrides from model cards
4. Outputs `config/providers.yaml`

### 6.3 Research Profiles Not Used by Oracle Routing
**File**: `src/omega/oracle/oracle.py` — `assess_intent()` and routing logic
- Oracle uses hardcoded model selection
- Research profiles (`reasoning_depth`, `tool_fidelity`, `failure_signature`) not consulted
- Shadow Protocol guardrails not applied automatically

### 6.4 Model Study KB Not Integrated
- `docs/kb/MODEL_STUDY_KNOWLEDGE_BASE.md` has 12 models, 5 synergy patterns
- `data/model_study/model_study.db` has test runs, findings
- Registry has `empirical_evidence` field but **no automated ingestion** from Model Study KB
- Synergies in model cards are manually maintained, not synced

---

## 7. Testing Gaps

### 7.1 No Unit Tests for ModelRegistry
**Location**: `tests/` — no `test_model_registry.py` exists
**Required tests**:
- `test_load_all_loads_all_models`
- `test_load_all_handles_malformed_yaml`
- `test_build_index_creates_all_tables`
- `test_build_index_includes_all_fields`
- `test_get_model_returns_correct_model`
- `test_get_models_filters_correctly`
- `test_query_executes_sql_safely`

### 7.2 No Contract Tests for Query Interface
**Required tests**:
- `test_get_all_models_returns_all`
- `test_get_models_by_tier_filters`
- `test_get_models_by_platform_filters`
- `test_get_models_by_provider_filters`
- `test_get_free_models_filters`
- `test_get_engine_routable_models_filters`
- `test_get_model_by_id_returns_none_for_missing`
- `test_search_models_finds_partial_matches`
- `test_get_capability_leaders_validates_capability`
- `test_get_provider_chain_orders_by_priority`
- `test_get_stats_returns_correct_counts`

### 7.3 No Validation Tests for Parameter Field
Since `parameters` doesn't exist, no tests exist. Once added:
- `test_model_card_has_parameters_field`
- `test_parameters_schema_valid`
- `test_parameters_used_by_model_gateway`

### 7.4 No Integration Tests
- Registry → ModelGateway provider fabric generation
- Registry → Oracle routing with research profiles
- Registry → Model Study KB sync

---

## 8. Prioritized Task List for Cline

### P0 — Critical (Blockers)
| Task | Description | Effort | Files |
|------|-------------|--------|-------|
| **T1** | Add `parameters` field to ModelCard dataclass + all 35 model cards + SQLite index | 4h | `models.py`, 35 `.yaml.md`, `registry.py`, `query.py` |
| **T2** | Fix duplicate provider priority (google=4, openrouter=4) | 30m | `registry.yaml` |
| **T3** | Fix provider mappings for 4 local models (nemotron-3-ultra-local, qwen-3.5-72b-local, gpt-oss-120b-local, 3 Anthropic models) | 1h | 7 model cards |
| **T4** | Create `make model-sync` to generate `providers.yaml` from registry | 2h | `scripts/generate_providers_yaml.py`, `Makefile` |
| **T5** | Update ModelGateway to read provider fabric from registry (or generated providers.yaml) | 2h | `model_gateway.py` |

### P1 — High (Schema & Data Quality)
| Task | Description | Effort | Files |
|------|-------------|--------|-------|
| **T6** | Add extra capability fields to Capabilities dataclass (code_execution, parallel_search, workspace_integration) | 1h | `models.py`, Gemini model card |
| **T7** | Add benchmark sources for all capability scores (cite paper/benchmark) | 8h | 35 model cards |
| **T8** | Verify pricing/free tier for all models against live APIs | 4h | 35 model cards, `live_api_state` |
| **T9** | Complete identity history for stealth models | 1h | Model cards |
| **T10** | Add research profiles for 26 models missing them | 4h | `research_profiles/`, model cards |
| **T11** | Extend SQLite index schema to include all model card fields | 2h | `registry.py` (build_index) |
| **T12** | Enhance validation script with comprehensive checks | 2h | `scripts/model_registry_validate.py` |

### P2 — Medium (Integration & Testing)
| Task | Description | Effort | Files |
|------|-------------|--------|-------|
| **T13** | Write unit tests for ModelRegistry (10+ tests) | 3h | `tests/test_model_registry.py` |
| **T14** | Write contract tests for ModelRegistryQuery (12+ tests) | 3h | `tests/test_model_registry_query.py` |
| **T15** | Integrate research profiles into Oracle routing | 3h | `oracle.py`, `model_gateway.py` |
| **T16** | Build Model Study KB → Registry sync pipeline | 2h | `scripts/sync_model_study_kb.py` |
| **T17** | Add provider availability matrix generation | 1h | `scripts/generate_provider_matrix.py` |

### P3 — Low (Polish & Automation)
| Task | Description | Effort | Files |
|------|-------------|--------|-------|
| **T18** | Add registry metadata (validation timestamps, freshness) | 1h | `registry.yaml`, `registry.py` |
| **T19** | Add CI gate for model registry validation | 30m | `.github/workflows/`, `Makefile` |
| **T20** | Document model card authoring guide | 1h | `docs/reference/MODEL_CARD_AUTHORING.md` |

---

## 9. Recommended Schema Changes

### 9.1 ModelCard Dataclass Additions
```python
@dataclass
class Capabilities:
    reasoning: float
    code_generation: float
    knowledge: float
    creative: float
    tool_use: bool = False
    structured_output: bool = False
    multimodal: bool = False
    # NEW:
    code_execution: bool = False
    parallel_search: bool = False
    workspace_integration: bool = False

@dataclass
class ModelCard:
    # ... existing fields ...
    # NEW:
    parameters: dict = field(default_factory=dict)  # Sampling params + model-specific overrides
    benchmark_sources: dict = field(default_factory=dict)  # capability -> source URL/citation
```

### 9.2 SQLite Index Schema Migration
```sql
ALTER TABLE models ADD COLUMN parameters TEXT;  -- JSON
ALTER TABLE models ADD COLUMN capability_code_execution BOOLEAN DEFAULT 0;
ALTER TABLE models ADD COLUMN capability_parallel_search BOOLEAN DEFAULT 0;
ALTER TABLE models ADD COLUMN capability_workspace_integration BOOLEAN DEFAULT 0;
ALTER TABLE models ADD COLUMN benchmark_sources TEXT;  -- JSON
ALTER TABLE models ADD COLUMN identity_original TEXT;
ALTER TABLE models ADD COLUMN identity_current TEXT;
ALTER TABLE models ADD COLUMN identity_swap_detected BOOLEAN DEFAULT 0;
ALTER TABLE models ADD COLUMN identity_last_verified TEXT;
ALTER TABLE models ADD COLUMN community_rating TEXT;
ALTER TABLE models ADD COLUMN community_notes TEXT;  -- JSON
ALTER TABLE models ADD COLUMN live_api_source TEXT;
ALTER TABLE models ADD COLUMN live_api_last_verified TEXT;
ALTER TABLE models ADD COLUMN live_api_last_verified_free TEXT;
ALTER TABLE models ADD COLUMN empirical_evidence TEXT;  -- JSON
ALTER TABLE models ADD COLUMN provider_fabric TEXT;  -- JSON
```

### 9.3 Registry.yaml Fixes
```yaml
provider_fabric:
  fallback_chain:
    - provider: "native-gguf"
      priority: 0
    - provider: "lmster"
      priority: 1
    - provider: "ollama"
      priority: 2
    - provider: "antigravity"
      priority: 3
    - provider: "google"
      priority: 4
    - provider: "openrouter"
      priority: 5  # CHANGED from 4
    - provider: "opencode-zen"
      priority: 6
    - provider: "cline"
      priority: 7
    - provider: "mock"
      priority: 99
```

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **ModelGateway breaks if providers.yaml generation fails** | Medium | High | Keep providers.yaml as fallback; validate generated output before write |
| **Schema migration breaks existing model cards** | Low | High | Add migration script; version schema; backward-compatible defaults |
| **Capability scores are fabricated (no benchmarks)** | High | Medium | Audit all 35 models; require citation for each score; flag unverified |
| **Provider mappings drift over time** | High | Medium | Add cross-validation in `model-validate`; CI gate |
| **Research profiles become stale** | Medium | Low | Link profile `updated_at` to model card `updated_at`; alert on drift > 30 days |
| **Model Study KB sync never runs** | Medium | Low | Add to CI pipeline; make `model-index` depend on KB sync |
| **Cline implements fixes without coordination** | Low | High | This gap analysis is the coordination artifact; Cline must acknowledge tasks |

---

## 11. Verification Checklist for Cline

Before marking tasks complete, Cline must verify:

- [ ] `make model-validate` passes all 8 gates (including PROVIDER_CHAIN_COMPLETE)
- [ ] `make model-index` builds index with all new columns populated
- [ ] `make model-query ARGS="model <id>"` shows `parameters` field for all 35 models
- [ ] `make model-query ARGS="leaders reasoning"` works with new capability fields
- [ ] ModelGateway starts and uses generated `providers.yaml` (or registry directly)
- [ ] All 35 model cards have `benchmark_sources` for each capability score
- [ ] Provider mappings verified: local models → native-gguf/lmster/ollama; Anthropic models → anthropic/opencode-zen
- [ ] Unit tests pass: `pytest tests/test_model_registry.py -v`
- [ ] Contract tests pass: `pytest tests/test_model_registry_query.py -v`
- [ ] No regression in `make test` (276 tests)

---

## 12. Appendix: Model Card Template with All Fields

```yaml
---
model_id: "provider/model-name:variant"
display_name: "Human Readable Name"
version: "2026-07-19"
provider: "canonical_provider_name"
platform: "cloud|local|cli|stealth"
tier: "T1|T2|T3"
status: "active|deprecated|experimental|stealth"
context_window: 128000
max_output_tokens: 32000
capabilities:
  reasoning: 0.85
  code_generation: 0.90
  knowledge: 0.88
  creative: 0.82
  tool_use: true
  structured_output: true
  multimodal: false
  code_execution: false
  parallel_search: false
  workspace_integration: false
pricing:
  input_per_mtok: 0.0
  output_per_mtok: 0.0
  cached_input_per_mtok: 0.0
  batch_discount: 0.0
  intro_pricing: null
free_tier: true
cost_per_1k_tokens_usd: 0.0
latency_p99_ms: 5000
uptime_percent: 99.0
routing:
  engine_routable: true
  opencode_cli_only: false
  recommended_engine_alternative: null
identity_history: null  # or IdentityHistory object
community_intelligence:
  rating: "4.5/5.0"
  notes: ["Note 1", "Note 2"]
live_api_state:
  source: "provider_name"
  last_verified: "2026-07-19"
  last_verified_free: "2026-07-19"
research_profile:
  reasoning_depth: "deep|iterative|fast"
  tool_fidelity: "high|medium|low"
  failure_signature: "shallow|over_analysis|tool_drift|hallucination|memory_contamination"
  shadow_focus: "force_deepening|force_persistence|verify_tool_use|verify_facts|ignore_memory"
  guardrails: ["Guardrail 1", "Guardrail 2"]
empirical_evidence:
  test_runs: []
  synergies: []
provider_fabric:
  available_via:
    - provider: "native-gguf"
      priority: 0
  local_first_priority: 0
parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.1
  max_tokens: 4096
  stop_sequences: ["User:", "\n\n"]
  model_specific_overrides: {}
benchmark_sources:
  reasoning: "https://huggingface.co/spaces/.../leaderboard"
  code_generation: "https://github.com/.../benchmark"
  knowledge: "https://arxiv.org/abs/..."
  creative: "https://..."
tags: ["tag1", "tag2"]
created_at: "2026-07-19"
updated_at: "2026-07-19"
schema_version: "1.1.0"
---

# Model Card Body (Markdown)
```

---

*⬡ OMEGA ⬡ JEM ⬡ GAP-ANALYSIS ⬡ 2026-07-19 ⬡ DELIVERABLE FOR CLINE VERIFICATION MISSION*
