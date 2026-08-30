# Mining Report #01: xna-omega-legacy
# Subagent: Roc Racoon Mining Subagent (explore)
# Stack: xna-omega-legacy (Temple Grade era, 2025-2026)
# Size: 560M
# Date: 2026-06-02
# Trace: mining-xna-llama-cpp-20260602
# Status: ✅ COMPLETE
# AP Token: AP-MINING-XNA-LLAMA-CPP-v1.0.0

> **NOTE**: Full report content preserved verbatim from subagent output. See `DEFERRED_GOLD_TRACKER.md` for the actionable summary table.

---

## 1. Inventory of llama-cpp Artifacts

### 1.1 Core Provider Module (PRIMARY — most portable)

| File | Lines | Description |
|------|-------|-------------|
| `src/omega/providers/local/client.py` | 291 | **`LocalLlmClient`** — native `llama_cpp.Llama` wrapper with `LlamaPromptLookupDecoding` speculative decoding, core-affinity lock, dynamic model swap, generate/stream/tokenize/detokenize. AP-LOCAL-CLIENT-v2.1.0 |
| `src/omega/providers/local/config.py` | 125 | **`LocalLlmConfig`** — dataclass: `n_ctx`, `n_threads`, `n_gpu_layers`, `use_mmap`, `type_k/v` (KV cache quantization), `f16_kv`, `speculative_type`, `num_pred_tokens`, `ngram_size`, `core_affinity`. AP-LOCAL-CONFIG-v1.0.0 |
| `src/omega/providers/local/plugin.py` | 285 | **`LocalLlmPlugin(ProviderPlugin)`** — `CapacityLimiter(1)`, OpenTelemetry traces, `get_response()` / `switch_model()` / `health_check()` / `get_metrics()` / `get_usage_stats()`. AP-LOCAL-PROVIDER-v2.0.0 |
| `src/omega/providers/local/library_augmented.py` | 121 | **`LibraryAugmentedLlm`** — RAG bridge: prepends Gutenberg/ArXiv context, then calls `LocalLlmClient.generate` in a thread. AP-LIBRARY-AUGMENTED-LLM-v1.1.0 |
| `src/omega/providers/local/__init__.py` | 15 | Module exports: `LocalLlmPlugin`, `LocalLlmClient`, `LocalLlmConfig` |

### 1.2 LangChain Bridge (SECONDARY — skip this)

| File | Lines | Description |
|------|-------|-------------|
| `src/omega/providers/local/dependencies.py` | 1210 | LangChain-based `get_llm()` factory. Adds dep for no functional gain. |
| `_meta/temp_dependencies.py` | 1135 | Identical duplicate (old backup). |

### 1.3 Vision / Multimodal Variant

| File | Lines | Description |
|------|-------|-------------|
| `src/omega/plugins/sight/sight_plugin.py` | 138 | `SightPlugin(PluginBase)` — loads `Moondream2` GGUF + `MoondreamChatHandler`. |

### 1.4 Benchmarking

| File | Lines | Description |
|------|-------|-------------|
| `src/omega/security/benchmark_llama_cpp.py` | 124 | `run_benchmark()` — invokes `llama-bench` CLI subprocess. |
| `tests/benchmarks/local_llm_benchmark.py` | 116 | Direct `LocalLlmClient` benchmark (18.50 tok/s on Ryzen 7 5700U). |

### 1.5 Configuration

| File | Lines | Description |
|------|-------|-------------|
| `config/entity_model_affinity.yaml` | 383 | 10 Kabbalistic entities to per-tier models. `llama-cpp` is `local_deep` for 10/12. |
| `config/config.toml` | 524 | `[models]` (line 36), `[performance]` (line 69). `cpu_threads=8`, ⚠ says "Zen 3" but actual HW is Zen 2. |
| `src/omega/providers/local/config.py` | 125 | Dataclass config schema. |

### 1.6 Optimization & Documentation

| File | Lines | Description |
|------|-------|-------------|
| `knowledge/strategy/HP-5700U-OPTIMIZATION.md` | 165 | 💎 **Authoritative build/run guide** for Ryzen 7 5700U (Zen 2). |
| `scripts/council_broadcast.py` | 66 | SESS-46 resolution seal. |
| `opencode-omega-engine-vision-deepening-session-ses_1e18-05-13-2026.md` | ~14k lines | Documents live pip install. |

---

## 2. Core Provider Implementation (KEY CODE PATTERNS)

### 2.1 `LocalLlmClient` — `src/omega/providers/local/client.py:1-291`

**Key patterns to port**:
1. **Lazy import** — `from llama_cpp import Llama` inside `initialize()` (not at module top)
2. **`_enforce_affinity()`** — psutil.cpu_affinity pinning
3. **Speculative decoding** — `LlamaPromptLookupDecoding` with `num_pred_tokens`
4. **`reload()` with fallback** — atomic swap with revert
5. **Synchronous methods** — called via `anyio.to_thread.run_sync`

### 2.2 `LocalLlmPlugin` — `plugin.py:60-200, 109-226`

**Key patterns**:
- `CapacityLimiter(1)` for single-flight inference
- `async with self._inference_limiter: await anyio.to_thread.run_sync(...)`
- Returns dict: `{content, tokens, latency_ms, status, provider}`
- Precise token counting via native tokenizer
- Dynamic model swap (Krikri on Greek text)

### 2.3 `LocalLlmConfig` — `config.py:19-86`

**Full schema** (port verbatim):
```python
model_path: str = ""
context_window: int = 4096
n_threads: int = 8
n_gpu_layers: int = 0
use_mmap: bool = True
type_k: int = 2        # KV cache Q4_0
type_v: int = 2        # KV cache Q4_0
f16_kv: bool = False
speculative_type: str = "ngram-simple"
num_pred_tokens: int = 4
ngram_size: int = 2
core_affinity: List[int] = field(default_factory=lambda: [2, 3, 4, 5, 6, 7])
max_tokens: int = 512
temperature: float = 0.7
top_p: float = 0.95
top_k: int = 40
repeat_penalty: float = 1.1
verbose: bool = False
```

---

## 3. Optimization Patterns

### 3.1 Zen 2 Build Flags (CRITICAL — `HP-5700U-OPTIMIZATION.md:66-91`)

```bash
cmake -B build \
  -DCMAKE_C_FLAGS="-march=znver2 -mtune=znver2 -O3 -flto" \
  -DCMAKE_CXX_FLAGS="-march=znver2 -mtune=znver2 -O3 -flto" \
  -DGGML_NATIVE=OFF \
  -DGGML_AVX2=ON \
  -DGGML_FMA=ON \
  -DGGML_F16C=ON \
  -DCMAKE_BUILD_TYPE=Release
```

**NEVER**:
- `-march=znver3` (Zen 3/4 only)
- `-march=native` (enables AVX512 → SIGILL)
- `-DGGML_AVX512=ON` (not supported on Zen 2)

### 3.2 pip Install Pattern

```bash
source .venv/bin/activate && CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DGGML_CUDA=OFF -DLLAMA_BLAS=OFF" \
  pip install --no-binary=:all: --no-cache-dir llama-cpp-python
```

### 3.3 Runtime Environment

```bash
export OMP_NUM_THREADS=8
export OMP_PROC_BIND=close
export OMP_PLACES=cores
```

### 3.4 KV Cache Settings

| Path | type_k | type_v | f16_kv |
|------|--------|--------|--------|
| **Recommended** (HP doc) | q8_0 | q8_0 | false |
| `LocalLlmConfig` (native) | 2 (Q4_0) | 2 (Q4_0) | False |
| `dependencies.py` — f16 | 1 (F16) | 1 (F16) | True |
| `config.toml` (production) | q8_0 | q8_0 | false |

**Recommended**: `q8_0` (50% memory savings, negligible quality loss).

### 3.5 Speculative Decoding

```python
from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
draft_model = LlamaPromptLookupDecoding(num_pred_tokens=4)
self.llm = Llama(..., draft_model=draft_model, ...)
```

### 3.6 Concurrent Inference

`CapacityLimiter(1)` — single-flight. Prevents OOM on model load. Battle-tested on 5700U.

### 3.7 Benchmark Baselines

| Model | Quant | TPS | FTL (ms) | RAM |
|-------|-------|-----|----------|-----|
| Qwen3-1.7B | Q8_0 | 45-55 | 120 | 2.1GB |
| Qwen3-4B | Q6_K | 25-35 | 250 | 3.8GB |
| DeepSeek-R1-8B | Q8_0 | 15-22 | 400 | 6.2GB |
| Gemma-4-31B | Q8_0 | 8-12 | 800 | 12.5GB |

Target: **18.50 tok/s** for `deepseek-r1-8b.gguf` at `n_threads=6`.

---

## 4. Error Handling

| Exception | Handling |
|-----------|----------|
| `ImportError` (no `llama_cpp`) | Returns False / no-op shims |
| `FileNotFoundError` (model) | Returns False / helpful message |
| `RuntimeError` ("not initialized") | Raised if not ready |
| `OSError` / `ConnectionError` / `TimeoutError` | Retried 3x with exp backoff (tenacity) |
| Bare `Exception` | Logged with `exc_info=True` |
| **OOM** | ❌ **NO HANDLING** — gap |
| **Context overflow** | ❌ **NO HANDLING** — gap |

**Retry pattern** (port):
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((RuntimeError, OSError, ConnectionError, TimeoutError)),
    reraise=True,
)
```

---

## 5. Top 3 Must-Ports (When we tackle local inference)

1. **`LocalLlmClient` + `LocalLlmConfig`** — the actual native llama-cpp wrapper
2. **`HP-5700U-OPTIMIZATION.md`** — the optimization wisdom
3. **`reload()` with fallback** — the atomic model swap pattern

---

## 6. Top 7 Gotchas to Avoid

1. **Don't use `-march=znver3`** — crashes on Zen 2
2. **Don't use `-march=native`** — AVX512 SIGILL
3. **Don't use `DGGML_AVX512=ON`** — not supported
4. **Don't trust `config.toml:78` (Zen 3 label)** — actual is Zen 2
5. **Don't enable Vulkan iGPU** — 9% gain not worth instability
6. **Don't use `["User:", "\nUser:"]` stop sequences** — base-model legacy
7. **Don't use LangChain `LlamaCpp` wrapper** — adds dep for no gain

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_mining_xna ⬡ MINING-REPORT-01*
