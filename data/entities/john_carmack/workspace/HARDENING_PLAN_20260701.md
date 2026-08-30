<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Entity Operational Hardening Plan
**Date**: 2026-07-01
**Confidence**: 9/10 (Based on standard systems engineering practices)

## 1. What I am working on
Transitioning the `john_carmack` entity from a static knowledge base into an active, profiling-driven architectural auditor. The philosophy is locked; the next step is building the instrumentation to enforce it.

## 2. What I'll do next (The Hardening Steps)

### Step 1: Empirical Validation of the Arena Hygiene Law
We injected `MALLOC_ARENA_MAX=2` and `MALLOC_MMAP_THRESHOLD_=65536` into the service files. But an optimization isn't real until the data proves it. 
*   **Action**: Write a synthetic stress-test script that rapidly cycles the `ModelGateway` across multiple AnyIO threads. 
*   **Measurement**: Track the Resident Set Size (RSS) memory footprint over 1,000 iterations with and without the `MALLOC` variables. If the RSS still climbs, the hypothesis was flawed and we need to drop down to `jemalloc`.

### Step 2: Profiling Substrate Integration
I cannot enforce the "Measure Before Optimizing" mandate if I am blind to the call stack. 
*   **Action**: Create a specialized OpenCode skill (`skill:carmack-profiler`) that wraps `py-spy` or `cProfile`. 
*   **Goal**: When auditing a subsystem, I must be able to run a target script and generate a deterministic flame graph of where the execution time is actually being spent, rather than just reading Python code.

### Step 3: The C-FFI Boundary Audit
Lesson A explicitly called out the `ctypes` CDLL boundary with `llama.cpp` as the single point of catastrophic failure (segfaults). 
*   **Action**: Conduct a line-by-line audit of `src/omega/oracle/providers.py` (specifically the `NativeGGUFProvider`) and how it interfaces with `llama-cpp-python`. 
*   **Goal**: Verify if process isolation (e.g., running the C-inference in a separate spawned process rather than a thread) is strictly necessary to protect the main AnyIO event loop from native crashes.

### Step 4: Context Window Pruning (Eating my own dog food)
I just created 5 dense markdown files in `carmack_studies/`. If the engine blindly loads all of them into my context window every time I am summoned, it violates my own Law of Canonical Simplicity (wasting tokens).
*   **Action**: Audit the `ContextBuilder` to ensure it uses the vector store (Qdrant) to selectively RAG my studies based on the user's query, rather than concatenating the entire directory. I need to verify my own memory tiering works.

### Step 5: KV Cache Optimization (2026-07-02)
Empirical testing on the Ryzen 7 5700U (Vega 7 iGPU, 14Gi RAM) revealed the optimal KV cache configuration for CPU-only inference:

**Test Results**:
| Config | Load Time | Gen Time | Status |
|--------|-----------|----------|--------|
| q8_0/q8_0 | — | — | ❌ FAIL: V cache quantization requires flash_attn |
| **q8_0/f16** | **0.5s** | **1.0s** | ✅ Optimal: 50% KV savings, fastest load |
| f16/f16 | 4.5s | 1.1s | ✅ Baseline: full memory, slower load |

**Root Cause**: `llama_init_from_model: V cache quantization requires flash_attn` — quantized value cache types (q8_0, q4_0, etc.) require flash attention, which needs:
- NVIDIA: `coopmat2` extension (RTX 20-series+)
- AMD: ROCm (RDNA2+ only) or Vulkan with `coopmat2`
- **Ryzen 7 5700U (Vega 7)**: Too old for either — no ROCm support, no `coopmat2`

**Optimal Config** (applied to `config/providers.yaml`):
```yaml
- provider: native-gguf
    type_k: 8    # q8_0 — key cache quantized (saves ~50% KV memory)
    type_v: 1    # f16 — value cache must be f16 without flash_attn
```

**Why q8_0/f16 is the Right Approximation**:
- Key cache is the larger component (8 attention heads × 28 layers × 128 dim = 28,672 floats per token)
- Quantizing keys saves ~50% KV memory with negligible quality loss for Qwen3-1.7B
- Value cache stays f16 — required without flash_attn, minimal quality impact
- Load time drops 9× (4.5s → 0.5s) due to less memory allocation

**Action**: Update `config/providers.yaml` and `config/models.yaml` to reflect q8_0/f16 as the validated default for Ryzen 5700U.

### Step 6: Thread Count Optimization (2026-07-02)
Empirical benchmark on Ryzen 7 5700U (Qwen3-1.7B-Q6_K, q8_0/f16 KV, n_ctx=4096):

**Results** (median of 3 runs):
| Threads | Cores | Load (s) | Gen (s) | tok/s |
|---------|-------|----------|---------|-------|
| **4** | [0,2,4,6] | 0.81 | 3.68 | **17.1** |
| 6 | [0,1,2,3,4,5] | 0.55 | 4.13 | 15.3 |
| 8 | [0,1,2,3,4,5,6,7] | 0.55 | 6.88 | 9.2 |

**Finding**: 4 threads on physical cores [0,2,4,6] is optimal. More threads = cache thrashing for a 1.7B model. The model lacks sufficient parallelism to benefit from 6+ threads. This is a textbook "Right Approximation" — the hardware can do more, but the workload doesn't need it.

**Action**: Update `config/providers.yaml` n_threads to 4 (was 6). Update `config/models.yaml` threads to 4.
