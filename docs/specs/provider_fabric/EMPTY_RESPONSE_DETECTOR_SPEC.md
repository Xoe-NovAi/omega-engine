# Empty-Response Detector — Provider Fabric Spec

**Status**: DRAFT (FT-1) · **Scope**: `src/omega/oracle/model_gateway.py` · **Mandates**: M9, M23, M7
**Problem**: On upstream stream failure/stall-echo artifacts, cloud gateways may return an
empty or whitespace-only string as a *successful* response instead of raising. The gateway's
receipt path treats any truthy `result` as success (`model_gateway.py:1324`), so a severed
draft is recorded as a healthy provider interaction and the fallback chain never advances.

## 1. Detection Criteria

A response is EMPTY (detector fires) when ANY of:

| # | Criterion | Check |
|---|-----------|-------|
| E1 | Empty string | `text == ""` |
| E2 | Whitespace-only | `text.strip() == ""` and `len(text) > 0` |
| E3 | Below-min token threshold | `len(text.split()) < min_tokens` where `min_tokens` defaults to 1; configurable per provider via `providers.yaml` → `empty_response.min_tokens` (opt-in; providers without the key use E1/E2 only) |

E3 is intentionally conservative: a threshold >1 risks classifying legitimate terse answers
(e.g. "4") as failures for local models. Default rollout enables E1+E2 only.

## 2. Hook Point — Response Receipt Path in ModelGateway.generate()

Single insertion site inside the provider loop of `ModelGateway.generate()`
(`model_gateway.py:1055`, receipt block at `:1324`), BEFORE the success bookkeeping
(`record_success`, `_update_active_set`, `tracker.record(status="success")`,
`TokenLedger.record_transaction`) executes:

```
if result:
+   if self._is_empty_response(result, provider):
+       errors.append(f"{provider.name}: empty response detected")
+       await self._record_provider_failure(provider, model_name, trace_id)
+       continue
    _latency_ms = (time.monotonic() - _start_time) * 1000
    ...
```

New private method on `ModelGateway`:

```python
def _is_empty_response(self, text: str, provider) -> bool:
    """True if text meets empty-response criteria E1-E3 (see
    docs/specs/provider_fabric/EMPTY_RESPONSE_DETECTOR_SPEC.md)."""
```

Rationale for this hook point:
- It covers ALL backends uniformly (breaker path at `:1290`, retry path at `:1294/:1309`)
  without touching each backend class.
- The existing breaker wrapper `_call_with_none_as_failure` (`model_gateway.py:1271-1288`)
  only catches falsy results (`not r`). Whitespace-only `"   "` is truthy and slips through
  today — the detector closes exactly this gap.
- Placement before success recording keeps M22 provenance honest: no success rows are
  logged for responses that carry no content.

Out of scope (no change): backend classes themselves (`openai_compat.py` already raises
`ValueError` on empty choices/content at `:111`/`:115`; those raises remain).

## 3. Retry / Fallback Semantics

An empty response is treated as a PROVIDER FAILURE, identical to a timeout:

1. **Advance chain**: `continue` moves to the next provider in `ordered_provider_names`.
2. **Record failure**: reuse `_record_provider_failure()` (`model_gateway.py:983`) — feeds
   `HealthMonitor.record_failure` (circuit breaker counts it) and logs a
   `BACKEND_FALLBACK` observability event with `event: "provider_failed"`.
3. **No same-provider retry**: unlike transient network errors handled by
   `call_with_retry` (`retry_policy.py`, imported at `model_gateway.py:95`), an empty
   response does NOT retry against the same provider within this call — stall-echo
   re-dispatch usually reproduces the artifact.
4. **Exhaustion**: if all providers return empty, existing exhaustion logic applies —
   last `OmegaError` propagated if present (`:1419`), otherwise the graceful
   `_fallback_response` GenerateResult with `provider_name="fallback"` (`:1426`).
5. **Error typing (M9)**: the detector itself raises nothing; it appends to `errors[]`
   and records failure. No bare except introduced.

## 4. Minimal Test Plan

Location: `tests/oracle/test_model_gateway.py` (extend existing gateway test module).
All tests run with `OMEGA_ENV=test` MockProvider fabric or stub providers.

| ID | Test | Asserts |
|----|------|---------|
| T1 | `test_empty_string_advances_fallback` | Stub provider A returns `""`; provider B returns valid text. Result: `GenerateResult.provider_name == "B"`; A has a recorded failure event. |
| T2 | `test_whitespace_only_is_failure` | A returns `"   \n\t "` → falls through to B; A failure recorded. |
| T3 | `test_all_empty_returns_graceful_fallback` | Every provider returns `""` → `provider_name == "fallback"`, text contains "no inference backend". |
| T4 | `test_min_tokens_threshold_opt_in` | With `empty_response.min_tokens: 3` on provider config, `"hi"` triggers advance; without the key, `"hi"` is accepted. |
| T5 | `test_detector_unit` | Direct `_is_empty_response()` table test over E1/E2/E3 boundaries (`""`, `" "`, `"ok"`, multi-word). |
| T6 | `test_no_success_metrics_on_empty` | `tracker.record` NOT called with `status="success"` for the empty provider; `TokenLedger` transaction not recorded for it. |

Gate: full suite `.venv/bin/python -m pytest tests/ -k "provider or gateway" -q` green.

## 5. Non-Goals

- No changes to streaming chunk-level timeouts (M25 lives in `openai_compat._stream_completion`).
- No new exception subclass — detection is a routing decision, not an error condition.
- No per-model thresholds (per-provider config key only).
