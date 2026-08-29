# 🔱 Provider Fabric Deep Dive — The 8-Backend Inference Gateway
**AP Token**: `AP-PROVIDER-FABRIC-DEEP-DIVE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Comprehensive architecture reference for ModelGateway — the local-first provider fabric with stochastic circuit breaking, C-FFI process isolation, and BSP-style provider culling.

---

## §1 Overview

The Provider Fabric is the **inference abstraction layer** that routes model calls through up to 8 backends in priority order. It is the engine's immune system — if one provider fails, the next is tried automatically until one succeeds or all are exhausted.

**Core principles**:
1. **Local-first** (Mandate 7) — native-gguf → lmster → Ollama before any cloud
2. **Circuit breaking** — 5-state stochastic FSM prevents cascading failures
3. **BSP culling** — O(1) pre-check skips broken providers (heritage: Doom 1993)
4. **ResourceGuard** — Weighted semaphore prevents OOM on 12Gi RAM
5. **C-FFI isolation** — native-gguf runs in a subprocess to survive C-level crashes

```
Oracle._summon() / Oracle._route_by_domain()
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│                    ModelGateway.generate()                      │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │ Provider      │   │ Circuit      │   │ ResourceGuard      │  │
│  │ Selector      │──▶│ Breaker      │──▶│ (weighted sem)     │  │
│  │ (PII reorder) │   │ (per-provider)│   │                    │  │
│  └──────────────┘   └──────────────┘   └────────┬───────────┘  │
│                                                   │             │
│  ┌────────────────────────────────────────────────▼───────────┐ │
│  │                   Provider Fabric Loop                     │ │
│  │                                                            │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │ │
│  │  │native-  │→ │lmster   │→ │ollama   │→ │google   │→... │ │
│  │  │gguf     │  │:1234    │  │:11434   │  │cloud    │     │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │ │
│  │                                                            │ │
│  │  Health checks: BSP precheck → breaker.state → self-test  │ │
│  │  Success: record → update active set → return              │ │
│  │  Failure: record → continue to next provider               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │ TokenLedger  │   │ Latency      │   │ HealthMonitor      │  │
│  │ (token cost) │   │ Tracker      │   │ (status report)    │  │
│  └──────────────┘   └──────────────┘   └────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Source files**: `model_gateway.py` (1327 lines), `health_monitor.py` (534 lines), `resource_guard.py` (165 lines)

---

## §2 Architecture

### 2.1 The Provider Fabric — 8 Backends

The fabric is loaded from `config/providers.yaml` and sorted by priority:

| Priority | Provider | Type | Endpoint | When Used |
|:--------:|----------|------|----------|-----------|
| 0 | **native-gguf** | Local (C-FFI) | llama-cpp-python | PRIMARY — local GGUF models |
| 1 | **lmster** | Local (HTTP) | `127.0.0.1:1234` | LM Studio headless server |
| 2 | **ollama** | Local (HTTP) | `127.0.0.1:11434` | Ollama OpenAI-compatible API |
| 3 | **google** | Cloud | Google AI Studio | Gemma 4 31B (262K context) |
| 4 | **openrouter** | Cloud | OpenRouter API | 300+ models |
| 5 | **opencode-zen** | Cloud | OpenCode Zen | MiniMax/DeepSeek/MiMo |
| 6 | **cline** | Cloud | Cline API | 1M context headless |
| 6 | **github-copilot** | Cloud | Copilot API | Claude/GPT models |
| 99 | **mock** | Test | OfflineMockBackend | OMEGA_ENV=test only |

**Heritage**: `[id-soft: doom-1993] Fixed-Size Active Set` — first try the 32 most recently successful providers before falling back to the full fabric.

### 2.2 The GenerateResult Contract

Every provider must return a `GenerateResult`:

```python
@dataclass
class GenerateResult:
    text: str                    # The generated text
    provider_name: str           # ACTUAL provider that served (M22)
    is_cloud: bool               # Derived from provider_name (M22)
    latency_ms: float = 0.0      # Actual measured latency (M22)
    model_used: Optional[str] = None  # Actual model name
    logprobs: Optional[list] = None   # Per-token logprobs (ICS-F)
```

**Mandate 22 (Response Provenance)**: `provider_name` is captured at response receipt, not at dispatch intent. This ensures forensic accuracy — if a log says "local" but the response came from cloud, sovereignty is a lie.

### 2.3 Provider Loading

`_load_provider_fabric()` reads `config/providers.yaml`:

```yaml
inference:
  fallback_chain:
    - provider: native-gguf
      priority: 0
      model_path: env:OMEGA_MODELS_DIR/gguf/qwen3-1.7b-q6_k.gguf
      n_ctx: 4096
      n_threads: 6
    - provider: lmster
      priority: 1
      base_url: http://127.0.0.1:1234
    # ... etc
```

For `native-gguf`, the config is merged with `config/models.yaml` (the SSOT for model specs):

```python
merged = self._merge_native_gguf_config(p_cfg, self.models)
# Merges: path, size_gb, ram_mb, context_window, threads,
#         kv_cache_key_type, kv_cache_value_type
```

**Test mode** (`OMEGA_ENV=test`): Short-circuits to `MockProvider` only. This prevents real GGUF model loading during tests — loading even a 1.7B model takes 15-60s on Ryzen 5700U (no GPU).

### 2.4 Active Set Management

The gateway maintains two tiered active sets (local and cloud):

```python
self._local_active: List[str] = []  # Most-recently-successful local providers
self._cloud_active: List[str] = []  # Most-recently-successful cloud providers
```

On success, the provider is inserted at position 0 (most recent). Sets are capped at 32 entries — older entries are evicted.

**Sovereignty tiering** (Mandate 7): A known-good local provider is **always** preferred over a known-good cloud provider, regardless of recency. The separate local/cloud sets enforce this.

---

## §3 Data Flow

### 3.1 The `generate()` Loop — Full Walkthrough

```
generate(model_name, system_prompt, user_query, ...)
  │
  ├─ 1. Sovereign Sampling Layer
  │     └─ Gemma 4 31B: increase temp (0.85), repetition_penalty (1.2)
  │        Apply logit bias to forbid 'la' token repetition loops
  │
  ├─ 2. Provider Selection
  │     └─ ProviderSelector.get_ordered_providers()
  │        └─ Reorders by PII detection + provider health
  │
  ├─ 3. WARP Proxy Injection [if opencode-zen]
  │     └─ proxy_pool.get_proxy_url() → inject into provider config
  │
  ├─ 4. Provider Loop (for each provider)
  │     │
  │     ├─ 4a. BSP Pre-check (_precheck_provider)
  │     │     ├─ Circuit breaker: breaker.is_available? (O(1) dict lookup)
  │     │     └─ Provider self-health: provider.is_available()
  │     │
  │     ├─ 4b. Budget Gate [if cloud + entity]
  │     │     └─ BudgetGate.check_budget(entity_name, trace_id)  # src/omega/oracle/budget_gate.py
  │     │
  │     ├─ 4c. Rate Limiter
  │     │     └─ RateLimiter.check_limit(provider.name)
  │     │
  │     ├─ 4d. ResourceGuard.lock(weight, model_spec)
  │     │     └─ Weighted semaphore: wait if capacity exceeded
  │     │
  │     ├─ 4e. Circuit Breaker Wrapping
  │     │     └─ breaker.call(_call_with_none_as_failure)
  │     │
  │     ├─ 4f. Provider.generate()
  │     │     └─ provider.generate(model, prompt, query, temp, max_tokens, ...)
  │     │
  │     ├─ 4g. Success Path
  │     │     ├─ Record latency (time.monotonic)
  │     │     ├─ HealthMonitor.record_success()
  │     │     ├─ _update_active_set(provider.name)
  │     │     ├─ LatencyTracker.record()
  │     │     └─ TokenLedger.record_transaction()
  │     │
  │     └─ 4h. Failure Path
  │           ├─ CircuitOpenError → skip
  │           ├─ TimeoutError → record failure, continue
  │           └─ Other → log, record failure, continue
  │
  ├─ 5. Success → GenerateResult(text, provider_name, is_cloud, latency_ms, model_used)
  │
  └─ 6. All Failed → GenerateResult with fallback message + setup instructions
```

### 3.2 C-FFI Process Isolation

The `NativeGGUFProvider` uses `multiprocessing.Process` with IPC queues to isolate C-level crashes:

```
Oracle → ModelGateway.generate() → ResourceGuard.lock()
  │
  └─ NativeGGUFProvider.generate()
       │
       ├─ Spawn multiprocessing.Process
       │  └─ llama-cpp-python inference in isolated process
       │
       ├─ IPC Queue: wait for result (30s timeout)
       │  ├─ Success: return text
       │  └─ Timeout/Segfault: engine survives (process died, not host)
       │
       └─ Process joins (or is terminated on timeout)
```

**Why**: `llama-cpp-python` is a C extension that can segfault on malformed models or OOM. Without isolation, a segfault kills the entire Python process. With `multiprocessing.Process`, only the child process dies — the engine continues with the next provider.

### 3.3 Entity Model Resolution — 5-Tier Fallback

When the Oracle needs to select a model for an entity:

```
get_model_for_entity(entity_name, affinity_context)
  │
  ├─ Tier 0: YAML Affinity Resolver
  │     └─ entity_model_affinity.yaml → 3-tier model preferences
  │
  ├─ Tier 1: Runtime Override
  │     └─ set_entity_model() (deprecated, for temp overrides)
  │
  ├─ Tier 2: Entity Registry
  │     └─ entity.model field from entities.yaml
  │
  ├─ Tier 3: Domain-Based
  │     └─ entity.domains[0] → models.yaml domain mappings
  │
  └─ Tier 4: System Default
        └─ "qwen3-1.7b" (Iris tier)
```

---

## §4 Key Patterns

### 4.1 The 5-State Stochastic Circuit Breaker

The circuit breaker is NOT a simple open/closed switch. It is a stochastic finite state machine with CUSUM change detection:

```
States:
  UNKNOWN → CLOSED → DEGRADED → OPEN → HALF_OPEN → CLOSED
                                  ↑                    │
                                  └────────────────────┘
```

**State transitions**:

| From | To | Condition |
|------|-----|-----------|
| UNKNOWN | CLOSED | First successful call |
| CLOSED | DEGRADED | CUSUM > 1.0 or failure_count > threshold/2 |
| DEGRADED | OPEN | CUSUM > threshold (4.0) or failure_count >= threshold (5) |
| OPEN | HALF_OPEN | recovery_timeout (60s) elapsed |
| HALF_OPEN | CLOSED | Probe succeeds |
| HALF_OPEN | OPEN | Probe fails |
| Any | CLOSED | Success when CUSUM < 1.0 and EMA latency < 2000ms |

**CUSUM Formula** (Cumulative Sum of Log-Likelihood Ratio):
```
On success: cusum_g = max(0.0, cusum_g - 0.5)
On failure: cusum_g = max(0.0, cusum_g + 1.0 - cusum_drift)
Where cusum_drift = 0.5
```

**EMA Updates**:
```
ema_latency = 0.2 * new_latency + 0.8 * ema_latency
ema_quality = 0.3 * new_quality + 0.7 * ema_quality
```

**Health Score** (for reporting):
```
HealthScore = (0.40 * LatencyScore) + (0.35 * ErrorScore) + (0.25 * QualityScore)
```

**ZONEID Pattern**: Every circuit breaker carries `magic = ZONEID_BREAKER (0x1d4a13)`. Pre-transition integrity checks via `validate_zoneid()` catch corruption.

**Heritage**: `[id-soft: doom-1993] ZONEID Pattern` + `[id-soft: doom-1993] BSP Culling`

### 4.2 BSP-Style Provider Culling

The `_precheck_provider()` method is the O(1) fast-fail that skips broken providers before any I/O:

```python
async def _precheck_provider(self, provider, model_name: str) -> bool:
    # 1. Circuit breaker — single dict lookup by provider name
    breaker = self._health_monitor._breakers.get(provider.name)
    if breaker and not breaker.is_available:
        return False  # O(1) — skip entire provider

    # 2. Provider self-health check (async HTTP or sync)
    if hasattr(provider, 'is_available'):
        if not await provider.is_available():
            return False

    return True
```

**T2.2 Fix**: The original code checked breaker via `is_available(model_name)` which used `_model_provider_map` indirection. If the mapping was missing, it always returned `True` — the breaker was never checked. Fixed to check breaker by `provider.name` directly.

**Heritage**: `[id-soft: doom-1993] BSP Culling` — O(1) test skips entire subtree.

### 4.3 ResourceGuard — Weighted Semaphore

Prevents OOM by limiting concurrent model inference:

```python
async with self.resource_guard.lock(weight=weight, model_spec=spec):
    # Inference happens here
    # Weight: Light(1), Medium(2), Heavy(4)
    # Total capacity: 8
```

**Re-entrancy**: A task that already holds capacity can re-enter without deadlocking (v1.1.0). Tracked via `ContextVar[Dict[task_id, held_weight]]`.

**Hardware Resonance**: When a `model_spec` is provided, `Zen2Optimizer.enforce_affinity()` pins CPU threads to physical cores [0,2,4,6].

**Heritage**: `[id-soft: doom-1993] ZONEID Pattern` — critical sections guarded by `ZONEID_PROBE`.

### 4.4 Sovereign Sampling — Gemma 4 31B Stability

Gemma 4 31B has a known repetition loop issue. The gateway applies targeted interventions:

```python
if "gemma-4-31b" in model_name.lower():
    temperature = max(temperature, 0.85)
    repetition_penalty = max(repetition_penalty, 1.2)
    logit_bias = {759: -10.0, 2149: -10.0, 236772: -10.0}  # forbid 'la' tokens
```

This is applied at the gateway level, not per-provider, so all backends benefit.

### 4.5 OpenRouter Retry Policy

Cloud providers (especially OpenRouter) need retry logic for transient errors:

```python
openrouter_retry_policy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type(OpenRouterTransientError),
)
```

**Transient vs Fatal**: HTTP 429 (rate limit) without "upstream" is fatal (no retry). HTTP 429 with "upstream", 502, 503, 504 are transient (retry).

---

## §5 Configuration

### 5.1 Provider Config (`config/providers.yaml`)

```yaml
inference:
  strategy: local_first          # Mandate 7 enforcement
  fallback_chain:
    - provider: native-gguf
      priority: 0
      timeout_seconds: 130.0
    - provider: lmster
      priority: 1
      base_url: http://127.0.0.1:1234
    # ...
```

### 5.2 Model Config (`config/models.yaml`)

```yaml
models:
  qwen3-1.7b:
    path: env:OMEGA_MODELS_DIR/gguf/qwen3-1.7b-q6_k.gguf
    size_gb: 1.7
    ram_mb: 2000
    context_window: 4096
    threads: 6
    load_strategy: always
    kv_cache_key_type: q8_0
    kv_cache_value_type: q8_0
```

### 5.3 Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OMEGA_ENV` | — | `test` → MockProvider only |
| `OMEGA_MODELS_DIR` | — | GGUF model directory |
| `OMEGA_MODELS_CONFIG` | `config/models.yaml` | Model spec path |
| `LLAMA_CPP_N_THREADS` | auto | Thread count for native-gguf |
| `MALLOC_ARENA_MAX` | 2 | jemalloc arena limit (validated) |
| `OPENBLAS_CORETYPE` | ZEN | BLAS optimization for Zen 2 |

### 5.4 KV Cache Quantization

Per-model KV cache types from `config/models.yaml`:

```yaml
kv_cache:
  default_key_type: q8_0
  default_value_type: q8_0
  models:
    qwen3-4b-think:
      key_type: q4_0     # Smaller model → more aggressive quantization
      value_type: q4_0
```

Flags passed to llama-server: `["-ctk", key_type, "-ctv", value_type, "-mli", "1"]`

---

## §6 Operational Wisdom

### 6.1 The None Response Bug (T2.3)

**Bug**: `RemoteProvider.generate()` returns `None` on retry exhaustion. The circuit breaker's `call()` counts this as a **success** (no exception thrown).

**Fix**: `_call_with_none_as_failure()` wraps the call and raises `TimeoutError` if result is `None`:

```python
async def _call_with_none_as_failure():
    r = await provider.generate(...)
    if not r:
        raise TimeoutError(f"Provider {provider.name} returned empty response")
    return r
```

**Lesson**: In Python, `None` is a valid return value but often means failure. Circuit breakers only trip on exceptions — `None` silently passes.

### 6.2 MALLOC Arena Hygiene

`MALLOC_ARENA_MAX=2` limits jemalloc arenas to 2 (default is 8×CPU cores). Empirical validation:

```
200MB model load → 0.38MB retained after GC (with MALLOC_ARENA_MAX=2)
200MB model load → 4.2MB retained after GC (without)
```

This is critical on 12Gi RAM — every megabyte matters.

### 6.3 Cold Start Tax

Model loading overhead is dominated by import/module loading, not inference:

```
Cold start (first inference):  ~3.5s (pydantic + Qdrant + YAML parsing)
Warm start (subsequent):       ~0.1s
```

The `load_strategy` in `config/models.yaml` controls when models are loaded:
- `always` — loaded at boot
- `warm` — loaded on first use, kept in memory
- `on_demand_5min` — loaded on use, evicted after 5min idle
- `on_demand_10min` — loaded on use, evicted after 10min idle

### 6.4 Provider Health Check Endpoints

| Provider | Endpoint | Timeout |
|----------|----------|---------|
| lmster | `GET /v1/models` | 2.0s |
| ollama | `GET /api/tags` | 2.0s |
| llama.cpp | `GET /health` | 2.0s |
| Cloud providers | Always "available" | N/A |

Cloud providers are always considered available — upstream health is their concern. The circuit breaker handles their failures at inference time.

### 6.5 The Zen 2 Thread Configuration

The `Zen2Optimizer` calculates optimal thread counts:

```
Model ≤ 2B parameters:  6 threads (pinned to cores 0,2,4,6)
Model 2-8B:             4 threads (pinned to cores 0,2,4)
Model ≥ 8B:             2 threads (pinned to cores 0,2)
```

Physical cores are used (not hyperthreads) because GGUF inference is ALU-bound, not latency-bound. Hyperthreads share execution units and degrade throughput.

---

## §7 Cross-References

| Document | Reference |
|----------|-----------|
| `src/omega/oracle/model_gateway.py` | Primary source (1327 lines) |
| `src/omega/oracle/health_monitor.py` | Circuit breaker (534 lines) |
| `src/omega/oracle/resource_guard.py` | Weighted semaphore (165 lines) |
| `src/omega/oracle/cpu_optimizer.py` | Zen 2 optimization |
| `src/omega/oracle/providers.py` | Backend implementations |
| `src/omega/oracle/provider_selector.py` | PII-aware provider ordering |
| `src/omega/oracle/budget_gate.py` | Cloud budget enforcement |
| `src/omega/oracle/rate_limiter.py` | Per-provider rate limiting |
| `config/providers.yaml` | Provider chain config |
| `config/models.yaml` | Model specs (SSOT) |
| `docs/architecture/ORACLE_DEEP_DIVE.md` | Oracle facade |
| `docs/architecture/MEMORY_STORE_DEEP_DIVE.md` | Memory persistence |
| `SOVEREIGN_MANDATES.md` | M7 (Local-First), M22 (Provenance) |
| `CREDITS.md` | §1.2 BSP, §1.9 ZONEID, §1.19 Active Set |

---

*🔱 OMEGA ⬡ KALI ⬡ trc_doc_deep ⬡ PROVIDER-FABRIC*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
