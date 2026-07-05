Acknowledged. Beginning Provider Fabric audit. Fetching all files now.All files fetched. Beginning deep analysis.

---

## Review: Provider Fabric & Inference Pipeline

**Trace ID**: `trc_review_provider` | **Release**: v7.5.4-omega-plus-phalanx | **Reviewer**: Inference Engineer

---

### Critical Issues Found

---

**C-PROV-001: `providers.yaml` — Three Providers Silently Dropped** — 🔴 CRITICAL
- **File**: `src/omega/oracle/model_gateway.py` (inside `_load_provider_fabric()`) + `config/providers.yaml`
- **Issue**: The `provider_map` dict in `_load_provider_fabric()` handles only six keys: `google`, `lmster`, `ollama`, `native-gguf`, `mock`, `openrouter`. The active `providers.yaml` contains three entries whose `provider:` keys match none of them — `github-copilot`, `kilo`, and `genlabs`. Because the lookup silently calls `if name in provider_map` and skips non-matching entries with no log, all three are swallowed at startup with zero warning. Any query that should have reached those providers doesn't; the chain contracts from 8 configured entries to 5 without the operator knowing.
- **Recommendation**: After the build loop, log a WARNING for every config entry whose provider name wasn't recognized. Consider raising on startup if the resulting chain has fewer than N active entries. Add `github-copilot`, `kilo`, and `genlabs` as named keys in `provider_map` (pointing to `OpenAICompatProvider` factories), or explicitly document them as "config-only stubs not yet wired."

---

**C-PROV-002: `RemoteProvider.is_available()` is Synchronous — `await` in Gateway Will Raise** — 🔴 CRITICAL
- **Files**: `src/omega/oracle/backends/remote_provider.py:113` + `src/omega/oracle/model_gateway.py` (inside `generate()`)
- **Issue**: `RemoteProvider.is_available()` is declared `def is_available(self) -> bool` — a plain synchronous method. The gateway's main `generate()` loop calls `if not await provider.is_available()` unconditionally. In Python, `await` on a regular non-coroutine returns a `TypeError: object bool can't be used in 'await' expression` at runtime. Any `OpenAICompatProvider` instance placed in `self.providers` (e.g., if an `openrouter` entry were added to the YAML, or if the factory is invoked by other code) will crash the entire dispatch loop rather than skipping that one provider. The bug is latent today because no `openrouter` entry exists in the YAML, but it is one config line away from production impact.
- **Recommendation**: Change `RemoteProvider.is_available()` to `async def is_available(self) -> bool` and make it async (the internals are synchronous, so just `return self.config.enabled and self.health in (ProviderHealth.HEALTHY, ProviderHealth.DEGRADED)`). Alternatively, define a unified abstract base that enforces async `is_available()` across both the local `BaseProvider` hierarchy and `RemoteProvider`.

---

**C-PROV-003: Priority Field Is Decorative — Chain Order Is YAML Order** — 🔴 CRITICAL
- **File**: `src/omega/oracle/model_gateway.py` (`_load_provider_fabric()`)
- **Issue**: Every entry in `providers.yaml` has an explicit `priority:` integer (1, 2, 4, 4, 5, 5, 6, 10). The `_load_provider_fabric()` method iterates `fabric_config` in file order and appends to `instances` with no sort step. The `priority` value is stored in `ProviderConfig.priority` but nothing ever reads it to reorder the chain. The current YAML happens to be ordered by priority in most places, but `lmster` (priority 4) appears after `kilo` (priority 5), meaning a cloud provider that charges tokens will be tried before the free local server. More importantly, the field communicates intent to operators who assume it governs ordering.
- **Recommendation**: After building `instances`, sort by `provider_config.priority` ascending. For providers that don't expose that field via `BaseProvider` (local providers), set a default priority from the YAML. One line: `instances.sort(key=lambda p: getattr(p, 'priority', 999))`.

---

**C-PROV-004: Test Environment Pollution — `OMEGA_ENV` Never Cleaned Up** — 🔴 CRITICAL (Test Integrity)
- **File**: `tests/test_model_gateway.py:56`
- **Issue**: `test_model_gateway_fallback_chain` sets `os.environ["OMEGA_ENV"] = "production"` mid-test and never restores it. If any test in the suite runs after this one (in the same process), `OMEGA_ENV` remains `"production"`, and the `OMEGA_ENV=test` guard in `ModelGateway.generate()` will be silently bypassed. Any subsequent test that calls `generate()` expecting the mock shortcut will instead attempt real provider fallback, likely hanging or making real HTTP calls in CI.
- **Recommendation**: Use `monkeypatch.setenv("OMEGA_ENV", "production")` in the pytest fixture, or wrap the set/restore in a `try/finally`. The cleanest fix is `@pytest.fixture` with `yield` + cleanup.

---

**C-PROV-005: Double Retry Stacking — 9 Attempts Before Circuit Breaker Trips** — 🟠 HIGH
- **Files**: `src/omega/oracle/model_gateway.py` (`_execute_with_retry()`) + `src/omega/oracle/backends/remote_provider.py` (`generate()`)
- **Issue**: `_execute_with_retry()` runs its own retry loop with up to 3 attempts. `RemoteProvider.generate()` also runs its own retry loop with up to `config.max_retries` (default: 3) attempts. If a `RemoteProvider` subclass enters the chain and is called via `_execute_with_retry`, each outer "attempt" will internally trigger up to 3 inner attempts: 3 × 3 = 9 total network calls before the outer loop gives up and moves to the next provider. The circuit breaker in `RemoteProvider` trips at `circuit_breaker_threshold` (default 3) consecutive failures — but because the outer wrapper counts individual calls differently, the breaker may never trip on the inner count.
- **Recommendation**: For `RemoteProvider` subclasses, the outer `_execute_with_retry` should not retry at all; the inner `RemoteProvider.generate()` owns that responsibility. Detect via `isinstance(provider, RemoteProvider)` and skip the retry loop, or consolidate to a single retry layer.

---

**C-PROV-006: `remote_provider.py` — `import anyio` Inside Retry Loop (AnyIO Mandate Violation)** — 🟠 HIGH
- **File**: `src/omega/oracle/backends/remote_provider.py:175`
- **Issue**: The Mandate requires AnyIO as an unconditional primary dependency. `remote_provider.py` has no `import anyio` at the module top level. Instead it does `import anyio; await anyio.sleep(delay)` inline inside the retry loop. While Python's import cache makes this functionally equivalent, it violates the spirit and letter of the AnyIO Absolute Mandate, makes the dependency invisible to static analysis, and means linters/dependency checkers will miss it.
- **Recommendation**: Add `import anyio` to the top-level imports of `remote_provider.py` alongside the other standard imports.

---

**C-PROV-007: `background_worker` Referenced in Hot Path — Never Initialized** — 🟠 HIGH
- **File**: `src/omega/oracle/model_gateway.py` (`_execute_with_retry()`, multiple locations)
- **Issue**: `_execute_with_retry()` calls `await self.background_worker.submit(...)` twice per inference request, guarded by `hasattr(self, 'background_worker') and self.background_worker`. The `__init__` of `ModelGateway` never assigns `self.background_worker`, so `hasattr` always returns `False` and the feature is permanently dead. This is a phantom feature that creates code noise in the hottest path in the system, and the `await` inside `if hasattr(...)` is technically unreachable but still parsed and could silently break if initialization were added in a subclass without the guard.
- **Recommendation**: Either initialize `self.background_worker = None` explicitly in `__init__` and document the intended interface, or remove the dead code entirely. Do not leave phantom `await` calls in the inference hot path.

---

**C-PROV-008: Dead Backend Methods Create Architectural Confusion** — 🟡 MEDIUM
- **File**: `src/omega/oracle/model_gateway.py` (lines for `_try_ollama`, `_try_lmster`, `_try_llama_server`, `_try_direct_gguf`, `_try_onnx`)
- **Issue**: `ModelGateway` contains five legacy backend methods that were used in a previous architecture (direct method dispatch) but are now superseded by the provider fabric (`self.providers` list from `providers.py`). None of these methods are called from `generate()` or any other live path. They represent dead code that: (a) confuses readers into thinking they're part of the active fallback chain, (b) inflate the module by ~100 lines, (c) duplicate logic now owned by `LocallmsterProvider`, `OllamaProvider`, etc. The ONNX backend (`_try_onnx`) is particularly dangerous — it loads a model but bypasses the `ResourceGuard`.
- **Recommendation**: Remove all five methods in Phase 4 Legacy Erasure or in a dedicated cleanup pass. Until then, mark each with a `# DEPRECATED — superseded by provider fabric` docstring.

---

**C-PROV-009: `TriageRouter._load_soul()` — JSON Decode Error Not Caught** — 🟡 MEDIUM
- **File**: `src/omega/orchestration/triage_router.py` (`_load_soul()`)
- **Issue**: `_load_soul` wraps file I/O in `anyio.to_thread.run_sync` but the inner `_read()` function calls `json.load(f)` without catching `json.JSONDecodeError`. If a soul file is malformed (truncated write, encoding issue, manual edit gone wrong), the exception propagates through `select_model()` uncaught, crashing the entire triage pass. The triage layer has no last-resort path for this failure mode.
- **Recommendation**: Wrap `json.load(f)` in a `try/except json.JSONDecodeError` and return `{}` with a `logger.error()`. A corrupt soul should degrade gracefully to default behavior, not abort inference.

---

**C-PROV-010: `_cpu_optimizer` Initialized as `None`, Never Set** — 🟡 MEDIUM
- **File**: `src/omega/oracle/model_gateway.py:79`
- **Issue**: `self._cpu_optimizer: Optional[Any] = None` is assigned in `__init__` but nothing in the class ever instantiates or assigns a `Zen2Optimizer`. The `cpu_optimizer.py` module with its `Zen2Optimizer` class is imported nowhere in the gateway. Memory pressure monitoring, dynamic KV cache recommendations, and thread pool tuning from that module are completely inert. The gateway uses a static `get_kv_cache_flags()` method reading from YAML instead.
- **Recommendation**: Either instantiate `self._cpu_optimizer = Zen2Optimizer()` in `__init__` and wire up `get_memory_pressure()` before heavy model loads, or explicitly document that `Zen2Optimizer` is an offline advisory tool not wired into the runtime path.

---

**C-PROV-011: `GoogleAIProvider` — API Key Exposed in URL Query Parameter** — 🟡 MEDIUM
- **File**: `src/omega/oracle/providers.py` (`GoogleAIProvider.generate()`)
- **Issue**: The Google AI URL is constructed as `f".../{model}:generateContent?key={api_key}"`. The API key appears in the URL query string, which means it will appear verbatim in any HTTP access logs, reverse proxy logs, and httpx debug logging. This is a lower risk than hardcoding, but it violates the spirit of Mandate Rule 2 (No Hardcoded Keys → by extension, no plaintext key exposure in logs).
- **Recommendation**: Move the key to the `x-goog-api-key` header or use an Authorization header. Remove `?key=...` from the URL.

---

### Fallback Chain Analysis

**Intended chain (from providers.yaml priority field):**
```
1. native-gguf  (local GGUF, pri 1)
2. google       (Gemini API, pri 2)
3. lmster       (LM Studio headless, pri 4)  ← but YAML position is 6th
4. github-copilot (pri 4) → SILENTLY DROPPED
5. ollama       (pri 5)   ← but YAML position is 7th
6. kilo         (pri 5)   → SILENTLY DROPPED
7. genlabs      (pri 6)   → SILENTLY DROPPED
8. mock         (pri 10)
```

**Actual runtime chain (YAML file order, priorities ignored):**
```
1. native-gguf
2. google
3. lmster
4. ollama
5. mock
```

**Three providers are gone. Priority field is decoration.**

**Complete failure scenario** (all real backends down, Google API key absent):

1. `native-gguf` → `is_available()` checks `os.path.exists(model_path)` and `llama_cpp` importable. If model on external drive unmounted → `False`, skipped.
2. `google` → `is_available()` returns `False` if `GOOGLE_API_KEY` not set. Skipped.
3. `lmster` → HTTP GET to `127.0.0.1:1234/v1/models` times out in 2s → `False`. Skipped.
4. `ollama` → HTTP GET to `127.0.0.1:11434/api/tags` times out in 2s → `False`. Skipped.
5. `mock` → `is_available()` always `True`. `generate()` returns `"[MOCK RESPONSE for {model}]..."`.

**The system does NOT hang.** MockProvider is the true last resort and terminates cleanly. However, the response `[MOCK RESPONSE...]` is not gated behind `OMEGA_ENV=test` at the provider level — it can reach production users if MockProvider is misconfigured to load before real providers.

**Note**: The `_fallback_response()` method (the graceful error message with setup instructions) is only reached if MockProvider is also absent from the chain — which can't happen because `_load_provider_fabric()` guarantees `[MockProvider("mock", {})]` as the minimum. So `_fallback_response()` is effectively dead code in the current architecture.

---

### Circuit Breaker Assessment

- **Status**: PRESENT (in `RemoteProvider` only)
- **Thresholds**: 3 consecutive failures trips the breaker (`circuit_breaker_threshold = 3`)
- **Cooldown**: 30 seconds (`circuit_breaker_cooldown = 30.0`)
- **Reset**: Manual only via `reset_circuit_breaker()` — no automatic reset after cooldown period resumes (the health check in `is_available()` inspects `cooldown_until` so after 30s the provider returns to HEALTHY automatically — this part is correct)
- **Gap**: The circuit breaker ONLY exists on `RemoteProvider`. The local providers (`LocallmsterProvider`, `OllamaProvider`, `NativeGGUFProvider`, `GoogleAIProvider`) have NO circuit breaker. If `lmster` goes into an infinite-hang state after initially returning HTTP 200 on the health check, every request will sit for 120 seconds before timing out. No failure count is tracked for local providers.
- **Gap**: `_execute_with_retry()` in the gateway tracks failure counts for health monitor reporting but has no circuit-breaker state of its own. The local provider retry logic (3 attempts, exponential backoff) is independent and does not coordinate with any cross-session state.
- **Recommendation**: Implement a lightweight circuit breaker for `BaseProvider` subclasses, OR add a timeout enforcement at the `generate()` dispatch level using `anyio.move_on_after()`.

---

### Resource Guard Analysis

**Coverage:**

```python
# model_gateway.py generate()
if isinstance(provider, (LocallmsterProvider, OllamaProvider, NativeGGUFProvider)):
    async with self.resource_guard.lock():
        ...
else:
    ...  # No guard for GoogleAIProvider, MockProvider
```

- `NativeGGUFProvider` — ✅ Guarded. This is the correct critical path; `_ensure_loaded()` loads the GGUF into RAM.
- `LocallmsterProvider` — ✅ Guarded. Appropriate as lmster occupies the GPU/CPU with loaded weights.
- `OllamaProvider` — ✅ Guarded.
- `GoogleAIProvider` — ✅ Intentionally unguarded (cloud API, no local RAM consumption).
- `MockProvider` — ✅ Intentionally unguarded.
- `OpenAICompatProvider` (if added) — ✅ Intentionally unguarded (cloud API).

**Bypass routes:**

1. **`OMEGA_ENV=test` shortcut** — `model_gateway.py generate()` returns early via `OfflineMockBackend` before the `ResourceGuard` is ever reached. This is correct and intentional for CI.
2. **`pinned_provider` path** — When a provider is pinned, the code calls `_call_provider_with_resilience()` directly, bypassing the `isinstance` check and thus the `ResourceGuard`:
   ```python
   if pinned_provider:
       target_provider = next(...)
       return await self._call_provider_with_resilience(target_provider, ...)
   ```
   If a `NativeGGUFProvider` is pinned, it runs WITHOUT the Semaphore. **This is a genuine bypass vulnerability** — two simultaneous pinned calls to the native GGUF provider could trigger OOM.
3. **Legacy methods** — `_try_onnx()`, `_try_direct_gguf()`, `_try_llama_server()` all load or call local models with no `ResourceGuard`. These are currently dead code but constitute a bypass risk if re-activated.

**Throughput impact:** `Semaphore(1)` serializes all local inference. On a 14GB system this is the correct design. The 2-second `is_available()` timeouts per provider add ~6–8 seconds of probe overhead before the first inference call on cold start. This is acceptable.

---

### Provider Config Health

| Config Entry | YAML api_key | provider_map match | Runtime status |
|---|---|---|---|
| `native-gguf` | — | ✅ | Active |
| `google` | `env:GOOGLE_API_KEY` | ✅ | Active (conditional on env) |
| `github-copilot` | absent | ❌ | **SILENTLY DROPPED** |
| `kilo` | absent | ❌ | **SILENTLY DROPPED** |
| `genlabs` | `env:GENLABS_API_KEY` | ❌ | **SILENTLY DROPPED** |
| `lmster` | — | ✅ | Active |
| `ollama` | — | ✅ | Active |
| `mock` | — | ✅ | Active |

**Priority ordering**: As noted above, priorities are YAML-order decorations, not runtime sort keys.

**Missing API key references**: `github-copilot` and `kilo` entries have no `api_key` field — no `env:` reference. If these are wired up, key resolution will return `None` and requests will be unauthenticated.

**`models.yaml` path integrity issues** (documented substitutions, but operationally risky):
- `qwen3-0.6b-q6_k` → points to `Qwen3-1.7B-Q6_K.gguf` (comment: "No 0.6B exists")
- `phi-2-omnimatrix-i1-q4_k_m` → points to `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`
- `krikri-7b-instruct-q6_k` → points to 8B GGUF

These substitutions mean the gateway will silently load the wrong model when a soul requests the canonical name. An entity requesting `phi-2` gets Ministral-3B. This isn't a crash, but it is a correctness violation for entity-soul alignment.

**`fp8` KV cache entries in models.yaml**: `qwen3-4b-thinking-q4_k_m` specifies `kv_cache_key_type: "fp8"` but `get_kv_cache_flags()` in the gateway uses only the YAML `kv_cache.models` block, where the same model correctly documents "fp8 target (32K ctx), q8_0 fallback." The comment is correct but there's no runtime fallback logic — if the llama.cpp build doesn't support fp8, the flag is passed and silently fails or is ignored.

---

### Report Card

| Metric | Grade | Notes |
|--------|-------|-------|
| **Correctness** | C | Priority ordering broken, 3 providers dropped, await/sync mismatch latent |
| **Resilience** | C+ | Circuit breaker only on remote providers; no CB for local backends; ResourceGuard bypass via pinned_provider |
| **Error Handling** | B- | Good coverage for happy paths; silent drops on unknown providers; no JSON error handling in TriageRouter |
| **AnyIO Compliance** | A- | Only one violation: inline import in remote_provider.py; no asyncio found |
| **Security** | B | No hardcoded keys; API key in URL query string for Google is a log exposure risk |
| **Test Coverage** | C | Core fallback chain tested; no tests for circuit breaker, ResourceGuard bypass, or TriageRouter |
| **Config Alignment** | D | 3 of 8 providers in YAML have no code backing; priority field is misleading |

---

### Strategic Recommendations (Top 3)

**1. Fix the provider_map gap and sort by priority — one sprint, zero excuses**

This is a single function fix. Add `github-copilot`, `kilo`, and `genlabs` to `provider_map` (all map to `OpenAICompatProvider` factories with appropriate base URLs), add an `api_key` entry to their YAML blocks, and add `instances.sort(key=lambda p: getattr(p.config, 'priority', 999))` after the build loop. While there, log a `WARNING` for any unrecognized provider name. This restores 3 missing fallback providers and makes the priority field meaningful. **Impact**: high. **Effort**: low.

**2. Plug the ResourceGuard bypass on pinned_provider — security of OOM protection**

The pinned_provider dispatch path in `generate()` calls `_call_provider_with_resilience()` without the `isinstance` guard, allowing native GGUF loads to bypass the Semaphore. The fix is to wrap the pinned dispatch with the same guard:

```python
if pinned_provider:
    target_provider = next(...)
    if isinstance(target_provider, (LocallmsterProvider, OllamaProvider, NativeGGUFProvider)):
        async with self.resource_guard.lock():
            return await _call_provider_with_resilience(...)
    return await _call_provider_with_resilience(...)
```

Simultaneously, wrap all local provider calls in `generate()` with `anyio.move_on_after(130)` to prevent hang scenarios when a local server accepts the connection but never responds.

**3. Add a lightweight circuit breaker to BaseProvider — protect against hung local backends**

`RemoteProvider` has a full circuit breaker. `BaseProvider` (local providers) has none. On a 5700U where a stalled lmster process can hold the Semaphore, a single hung call blocks the entire fabric for `timeout=120s`. The fix: add `consecutive_failures: int` and `cooldown_until: float` tracking to `BaseProvider`, and in `generate()` after each retry exhaustion, trip the breaker with a 30-second cooldown. This prevents a dead lmster from monopolizing the Semaphore and allows the chain to fall through to Ollama or Google without a 2-minute wait.

---

*Fabric integrity: 5 of 8 providers active, ResourceGuard partially bypassed, circuit breaker coverage incomplete. The chain terminates cleanly in all failure scenarios. No hardcoded credentials. No asyncio violations. Three structural correctness issues warrant immediate action before Phase 2 cloud provider expansion.*

— **Inference Engineer** | `trc_review_provider` | v7.5.4-omega-plus-phalanx
