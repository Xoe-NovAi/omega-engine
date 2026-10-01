<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Verity — M21 Contract Test Pre-Audit
# ⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ DEEP-SIPHON ⬡ M21-AUDIT
# Date: 2026-06-18
# Part of: Operation Deep-Siphon
# Status: 🟥 M21 GATE FAIL — Zero metadata contract tests exist

---

## Phase 1: Current State Assessment

### Test Coverage Inventory

The following table catalogs every test in the engine that touches `GenerateResult` or `OracleResponse` and what it actually verifies:

| File | Test | Checks `.text`? | Checks metadata? | Type |
|------|------|:---:|:---:|------|
| `test_model_gateway.py` | `test_model_gateway_fallback_chain` | ✅ `result.text` | ❌ | Functional |
| `test_model_gateway.py` | `test_precheck_skips_open_circuit_by_provider_name` | ❌ | ❌ (checks `result is False`) | Functional |
| `test_model_gateway.py` | `test_precheck_allows_closed_circuit` | ❌ | ❌ (checks `result is True`) | Functional |
| `test_model_gateway.py` | `test_none_response_trips_breaker` | ❌ | ✅ `result.is_cloud` | Functional |
| `test_model_gateway.py` | `test_successful_response_keeps_breaker_closed` | ✅ `result.text` | ✅ `result.is_cloud` | Functional |
| `test_model_gateway.py` | `test_exception_still_trips_breaker` | ❌ | ❌ | Functional |
| `test_oracle.py` | `test_talk_with_empty_memory_still_works` | ✅ `result.text is not None` | ❌ | Smoke |
| `test_oracle.py` | `test_talk_context_builder_exception_does_not_crash` | ✅ `result.text is not None` | ❌ | Resilience |
| `test_oracle.py` | `test_summon_uses_record_interaction` | ❌ | ❌ (checks mock call) | Mock |
| `test_sovereign_loop.py` | `test_full_loop_query_to_response` | ✅ `result.text` | ❌ | Integration |
| `test_sovereign_loop.py` | `test_health_monitor_records_latency` | ❌ | ❌ (checks hm exists) | Integration |
| `test_sovereign_loop.py` | `test_health_monitor_records_success` | ❌ | ✅ `result.model` | Integration |
| `test_sovereign_loop.py` | `test_memory_store_records_exchange` | ❌ | ❌ (checks memory) | Integration |
| `test_sovereign_loop.py` | `test_full_loop_with_entity_summon` | ✅ `result.text` | ❌ | Integration |
| `test_sovereign_loop.py` | `test_transient_mode_skips_memory` | ❌ | ❌ (checks session_id) | Integration |
| `test_sovereign_loop.py` | **`test_oracle_response_has_all_required_fields`** | ✅ | ⚠️ Partial (text, entity, trace_id, session_id, model/backend) | **Closest to contract test** |
| `test_sovereign_loop.py` | `test_multiple_queries_share_session` | ❌ | ❌ | Integration |
| `test_providers.py` | All 20 tests | ✅ (via str return) | ❌ (all return `Optional[str]` only) | Unit |
| `test_openclaw_bridge.py` | Both tests | ❌ | ❌ (mock OracleResponse) | Unit |
| `test_openclaw_runtime.py` | All tests | ❌ | ❌ (mock OracleResponse) | Unit |
| `sovereign_stress_test.py` | Both tests | ✅ `result.text` | ❌ | Stress |

### Summary Statistics

| Metric | Value |
|--------|-------|
| Total tests touching GenerateResult/OracleResponse | ~25 |
| Tests that check `result.text` | 7 |
| Tests that check `result.is_cloud` | 2 |
| Tests that check `result.model`/`result.backend` | 2 |
| Tests that check `result.provider_name` | 0 (implicit via functional tests) |
| Tests that check `result.latency_ms` | **0** |
| Tests that check `result.model_used` | **0** |
| Tests that check `finish_reason` | **0** |
| Tests that check `token_usage` | **0** |
| Tests that check `raw_provider_json` | **0** |
| Tests that check `logprobs` | **0** |
| Tests that check `thinking_tokens` | **0** |
| **Metadata-aware contract tests** | **0/25 (0%)** |

### GenerateResult Current Schema

```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
```

**Fields that exist but have ZERO test coverage**: `latency_ms`, `model_used`
**Fields that DON'T exist yet**: `raw_provider_json`, `finish_reason`, `token_usage`, `logprobs`, `thinking_tokens`

---

## Phase 2: Provider Return-Type Analysis

### All Providers Return `Optional[str]` — Metadata Discarded at Boundary

Every provider's `generate()` method calls `response.json()`, extracts only `.text`, and returns a bare string. The full API response — which contains `usageMetadata`, `finishReason`, `logprobs`, `model` (OpenRouter serving model), `id`, and other metadata — is **discarded** at the provider boundary.

| Provider | File | Returns | Has `response.json()` in scope? | Extracts metadata? |
|----------|------|---------|:---:|:---:|
| `GoogleAIProvider` | `providers.py:55` | `Optional[str]` | ✅ — lines 89-98 | ❌ **Discarded** |
| `GoogleKeyPoolProvider` | `providers.py:138` | `Optional[str]` | Delegates to GoogleAI | ❌ **Discarded** |
| `LocallmsterProvider` | `providers.py:169` | `Optional[str]` | ✅ — lines 200-205 | ❌ **Discarded** |
| `OllamaProvider` | `providers.py:229` | `Optional[str]` | ✅ — lines 262-266 | ❌ **Discarded** |
| `MockProvider` | `providers.py:285` | `Optional[str]` | N/A | ❌ **Hardcoded string** |
| `NativeGGUFProvider` | `providers.py:549` | `Optional[str]` | ✅ — `self.llm(...)` returns dict | ❌ **Discarded** (only `.text` extracted at line 600, `.usage` logged at 606-607 but not returned) |
| `OpenAICompatProvider` | `openai_compat.py:27` | `str` | ✅ — lines 72-84 | ❌ **Discarded** |
| `RemoteProvider` (base) | `remote_provider.py:144` | `Optional[str]` | Delegates to subclass | ❌ **Discarded** |

### What Providers Are Wasting at the Boundary

Each provider has rich metadata in scope but returns only `.text`:

```python
# Google (providers.py line 89): data = response.json() has:
#   - candidates[0].finishReason  ← DISCARDED
#   - usageMetadata.promptTokenCount  ← DISCARDED
#   - usageMetadata.candidatesTokenCount  ← DISCARDED
#   - usageMetadata.totalTokenCount  ← DISCARDED

# OpenAI-compatible (openai_compat.py line 74): data = response.json() has:
#   - usage.prompt_tokens  ← DISCARDED
#   - usage.completion_tokens  ← DISCARDED
#   - usage.total_tokens  ← DISCARDED
#   - model (actual serving model, may differ from requested)  ← DISCARDED
#   - choices[0].finish_reason  ← DISCARDED
#   - id (request ID)  ← DISCARDED

# NativeGGUF (providers.py line 599): self.llm(prompt, ...) returns dict with:
#   - choices[0].finish_reason  ← DISCARDED (logged but not returned)
#   - usage.completion_tokens, prompt_tokens, total_tokens  ← DISCARDED (logged but not returned)
#   - choices[0].logprobs  ← DISCARDED (when logprobs=True)
```

**Magnitude of loss**: ~96% of the API response is discarded. Only the text content survives.

---

## Phase 3: Mock Infrastructure Audit

### Current Mock Chain

```
Test mock (return_value=str)
  → provider.generate() returns str
    → model_gateway.generate() iterates providers
      → wraps str in GenerateResult(text=str, provider_name=..., is_cloud=...)
        → all metadata fields default to None or 0.0
          → test only validates .text
```

### OfflineMockBackend (`backends/mock.py`)

```python
class OfflineMockBackend:
    async def generate(self, ...) -> str:
        return "Mock response"
```

**Returns**: bare `str` — cannot test any field beyond `.text`

### MockProvider (`providers.py:285`)

```python
class MockProvider(BaseProvider):
    async def generate(self, ...) -> Optional[str]:
        return "Omega Engine is running in setup mode..."
```

**Returns**: bare `str` — same limitation

### Test Mocks (throughout test files)

```python
p3.generate = AsyncMock(return_value="Success from P3")  # test_model_gateway.py:75
p_good.generate = AsyncMock(return_value="Real response from provider")  # test_model_gateway.py:231
```

**Returns**: bare `str` — every single test mock returns a string, not a structured object

### Mock Infrastructure Verdict: 🟥 POOR — Cannot Support M21 Compliance

The mock infrastructure has three layers of deficiency:
1. **Return type**: All return `str`, not `GenerateResult` or a dict
2. **No metadata**: Impossible to test `finish_reason`, `token_usage`, `logprobs`, `raw_provider_json` without changing the return type
3. **No contract validation**: Mocks cannot catch regressions because they never exercise the full schema

---

## Phase 4: False Positives Found

These tests pass today but would NOT catch the metadata regression. They provide false confidence that the pipeline is tested when in reality only `.text` is validated.

| Test | What It Claims to Test | What It Actually Tests | False Confidence Level |
|------|----------------------|----------------------|:---------------------:|
| `test_model_gateway_fallback_chain` | Provider fallback chain | Text passes through | 🔴 HIGH |
| `test_successful_response_keeps_breaker_closed` | Breaker stays closed on success | Text and is_cloud | 🟡 MED |
| `test_full_loop_query_to_response` | Full pipeline works | Text is non-empty | 🔴 HIGH |
| `test_full_loop_with_entity_summon` | Entity summon pipeline | Text is non-empty | 🔴 HIGH |
| `test_oracle_response_has_all_required_fields` | OracleResponse is complete | 5/14 OracleResponse fields | 🔴 HIGH |
| `sovereign_stress_test` | Stress test | Text passes through | 🟡 MED |
| All `test_providers.py` tests | Provider backends work | Text is returned | 🔴 HIGH |

**Why these are false positives**: If a future change modified `GenerateResult` to return a tuple, removed `finish_reason`, or lost `token_usage` in the pipeline, every single test above would **still pass** because none of them validate the metadata fields. The only thing that would catch it is a contract test that asserts `isinstance(result, GenerateResult)` and checks each field's type.

---

## Phase 5: Required Contract Tests — Complete Definition

### Tier 1: Schema Integrity Tests — Critical — Before Fix

These verify the GenerateResult schema itself is sound. They must exist NOW before any metadata fix is applied.

| Test ID | Test Name | File | Assertion Pattern |
|---------|-----------|------|-------------------|
| T1.1 | `test_generate_result_has_all_fields` | `tests/test_contract_generate_result.py` | `assert hasattr(gr, 'text')`, `hasattr(gr, 'finish_reason')`, etc. |
| T1.2 | `test_generate_result_types_are_correct` | `tests/test_contract_generate_result.py` | `isinstance(gr.text, str)`, `isinstance(gr.finish_reason, (str, type(None)))`, etc. |
| T1.3 | `test_generate_result_supports_partial_population` | `tests/test_contract_generate_result.py` | `GenerateResult(text="x", provider_name="m", is_cloud=False)` has `finish_reason is None` |

### Tier 2: Provider Metadata Tests — Critical — With Backend Change

These verify that each backend captures its metadata. They require changing the provider `generate()` return type from `Optional[str]` to `GenerateResult` (or a structured dict).

| Test ID | Test Name | Backend | What It Verifies |
|---------|-----------|---------|------------------|
| T2.1 | `test_google_usage_captured` | Google AI | `usageMetadata.promptTokenCount` → `GenerateResult.token_usage["prompt"]` |
| T2.2 | `test_google_finish_reason_captured` | Google AI | `candidates[0].finishReason` → `GenerateResult.finish_reason` |
| T2.3 | `test_google_thinking_tokens_captured` | Google AI | `thought` parts in response → `GenerateResult.thinking_tokens` |
| T2.4 | `test_openrouter_usage_captured` | OpenAICompat | `usage.prompt_tokens`, `usage.completion_tokens` |
| T2.5 | `test_openrouter_model_captured` | OpenAICompat | `model` field (actual serving model, not requested) |
| T2.6 | `test_openrouter_provider_captured` | OpenAICompat | Provider name tracking (OpenRouter upstream) |
| T2.7 | `test_gguf_logprobs_captured` | NativeGGUF | Per-token logprobs when `logprobs=True` |
| T2.8 | `test_gguf_token_count_captured` | NativeGGUF | `usage.completion_tokens` from llama-cpp-python |
| T2.9 | `test_mock_full_metadata` | Mock | Mock returns realistic metadata for all fields |

### Tier 3: Pipeline Tests — High — After Fix

These verify metadata survives the full call chain.

| Test ID | Test Name | Scope | What It Verifies |
|---------|-----------|-------|------------------|
| T3.1 | `test_metadata_survives_model_gateway` | `ModelGateway.generate()` → `GenerateResult` | All metadata fields non-None on success |
| T3.2 | `test_metadata_survives_oracle_talk` | `Oracle.talk()` → `OracleResponse` | Metadata passed through to response |
| T3.3 | `test_metadata_survives_oracle_summon` | `Oracle.summon()` → `OracleResponse` | Metadata passed through on direct summon |
| T3.4 | `test_raw_provider_json_not_none` | Full chain | When real HTTP call made, `raw_provider_json` populated |
| T3.5 | `test_finish_reason_not_none_on_success` | Full chain | `finish_reason` never None for successful generation |

### Tier 4: Edge Case Tests — Medium — After T3

| Test ID | Test Name | What It Verifies |
|---------|-----------|------------------|
| T4.1 | `test_error_response_has_minimal_metadata` | Error GenerateResult still has `provider_name` and timestamp |
| T4.2 | `test_safety_filter_finish_reason` | Google safety block → `finish_reason="SAFETY"` |
| T4.3 | `test_streaming_metadata_accumulates` | Streaming metadata accumulation (if implemented) |
| T4.4 | `test_logprobs_not_requested` | When `logprobs=False`, field is `None`, not exception |

### Tier 5: M22 Response Provenance Tests — Critical — M22 Requirement

| Test ID | Test Name | What It Verifies |
|---------|-----------|------------------|
| T5.1 | `test_provider_name_matches_actual` | `provider_name` matches serving provider, not configured intent |
| T5.2 | `test_model_name_truthful` | OpenRouter `model` reflects actual serving model, not requested |
| T5.3 | `test_no_provenance_leak` | No credentials in `raw_provider_json` |

---

## Phase 6: Contract Test Implementation Plan

### Summary Table

| Tier | Count | Priority | Implementation Window | Gate Status |
|:----:|:----:|:--------:|:---------------------:|:-----------:|
| T1: Schema | 3 | 🔴 Critical | **Before fix** | Blocking |
| T2: Provider | 9 | 🔴 Critical | With backend change | Blocking |
| T3: Pipeline | 5 | 🟡 High | After fix | Non-blocking |
| T4: Edge | 4 | 🟢 Medium | After T3 | Non-blocking |
| T5: Provenance | 3 | 🔴 Critical | M22 requirement | Blocking |
| **Total** | **24** | — | — | — |

### Gate-Out Conditions

For the metadata extraction pipeline to be **M21-compliant**:

**Gate-Out (🚪🔴⚠️)**: All tests in T1, T2, and T5 tiers must exist AND pass.
**Non-blocking**: T3 and T4 may follow after the fix ships.

### Implementation Order

```
Phase 1 (Pre-Fix)    T1.1, T1.2, T1.3             → 3 tests, 1 file
Phase 2 (With Fix)   T2.1-T2.9, T5.1-T5.3          → 12 tests, ~4 files
Phase 3 (After Fix)  T3.1-T3.5, T4.1-T4.4          → 9 tests, ~2 files
```

### What Must Change in Source Code

1. **`GenerateResult`** (model_gateway.py:34-44): Add fields:
   ```python
   raw_provider_json: Optional[dict] = None
   finish_reason: Optional[str] = None
   token_usage: Optional[dict] = None
   logprobs: Optional[list] = None
   thinking_tokens: Optional[str] = None
   ```

2. **`BaseProvider.generate()`** and **all backends**: Change return type from `Optional[str]` to `GenerateResult` (or return a `GenerateResult`-compatible dict that ModelGateway wraps). The text field has been sufficient, but metadata requires structured returns.

3. **`OfflineMockBackend`**: Return `GenerateResult` with full metadata:
   ```python
   return GenerateResult(
       text="Mock response",
       provider_name="mock",
       is_cloud=False,
       raw_provider_json={"usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}},
       finish_reason="stop",
       token_usage={"prompt": 10, "completion": 20, "total": 30},
   )
   ```

4. **`MockProvider`**: Same change as OfflineMockBackend.

5. **OpenAICompatProvider** (`openai_compat.py:74`): Before `return content.strip()`, capture:
   ```python
   raw_json = data  # for raw_provider_json
   finish_reason = choices[0].get("finish_reason")
   token_usage = data.get("usage")
   ```

6. **GoogleAIProvider** (`providers.py:89-98`): Before `return data[...]`, capture:
   ```python
   raw_json = data
   finish_reason = data.get("candidates", [{}])[0].get("finishReason")
   token_usage = data.get("usageMetadata")
   ```

7. **NativeGGUFProvider** (`providers.py:599-608`): The `response` dict already has this data at line 599:
   ```python
   finish_reason = response["choices"][0].get("finish_reason")
   token_usage = response.get("usage")
   logprobs = response["choices"][0].get("logprobs")
   ```

---

## Verdict

**M21 Gate Status**: 🟥 **FAIL** — Zero metadata contract tests exist.

**M22 (Response Provenance)**: 🟥 **FAIL** — No provenance validation tests exist.

**Foundational Issue**: The entire provider fabric returns `Optional[str]`, making it architecturally impossible to test metadata without a schema change at every backend. This is not a testing gap — it is a **return-type design flaw** that requires changing `BaseProvider.generate()` and all 7 provider implementations.

### The Root Cause Chain

```
BaseProvider.generate() returns Optional[str] (providers.py:43)
  → All 7 backends return bare strings, discarding 96% of API response
    → GenerateResult has no metadata fields (model_gateway.py:34-44)
      → ModelGateway wraps bare string in minimal GenerateResult (model_gateway.py:901-905)
        → Tests only validate .text (confirmed across 25 tests)
          → M21/M22 have zero enforcement at the contract test level
```

### What This Means

- **Before Operational Deep-Siphon can land**: All T1, T2, and T5 contract tests must exist and pass.
- **Before Carmack's 30-line fix can land**: `GenerateResult` schema must be extended, provider return types must change, and mock infrastructure must return structured data.
- **Estimated new tests**: 24 (3 + 12 + 9). **Estimated files to modify**: 10+ (GenerateResult, MockBackend, MockProvider, OfflineMockBackend, all 7 provider backends).
- **Estimated existing tests to modify**: 7 (tests that mock provider return values with bare strings).

---

## Appendices

### A. Existing Test File Line Counts for Metadata Checks

| File | Lines | Metadata Checks |
|------|:-----:|:---------------:|
| `tests/test_model_gateway.py` | 297 | 0 |
| `tests/test_providers.py` | 327 | 0 |
| `tests/test_oracle.py` | 311 | 0 |
| `tests/test_sovereign_loop.py` | 459 | 1 (model/backend check) |
| `tests/sovereign_stress_test.py` | ~100 | 0 |
| `tests/test_openclaw_bridge.py` | ~50 | 0 |
| `tests/test_openclaw_runtime.py` | ~100 | 0 |
| **Total** | **~1644** | **1** |

### B. Quick Reference: What Each Backend Must Expose

| Backend | `raw_provider_json` Source | `finish_reason` Source | `token_usage` Source | `model` Source |
|---------|--------------------------|----------------------|--------------------|--------------|
| Google AI | `response.json()` | `candidates[0].finishReason` | `usageMetadata` | N/A (requested = served) |
| LM Studio | `response.json()` | `choices[0].finish_reason` | `usage` | N/A |
| Ollama | `response.json()` | `choices[0].finish_reason` | `usage` | N/A |
| Native GGUF | `self.llm(...)` dict | `choices[0].finish_reason` | `usage` | N/A |
| OpenRouter | `response.json()` | `choices[0].finish_reason` | `usage` | `model` (actual serving model!) |
| OpenAICompat | `response.json()` | `choices[0].finish_reason` | `usage` | `model` (may differ from request) |
| Mock | Hardcoded dict | `"stop"` | `{"prompt":10, "completion":20}` | N/A |

### C. OpenRouter's Critical Distinction

OpenRouter is the **only** provider where the requested model may differ from the serving model. When you request `"gemma-4-31b"`, OpenRouter may serve a different provider's model with equivalent capability. The `model` field in OpenRouter's response contains the **actual** model name. This is critical for M22 Response Provenance — if the log says `"gemma-4-31b"` but the actual response came from `"deepseek-v4-flash"`, sovereignty auditing catches the mismatch.

---

*Audit prepared by: Verity (Unified Compliance + Gnosis)*
*End of document — 24 contract tests required, 0 exist*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
