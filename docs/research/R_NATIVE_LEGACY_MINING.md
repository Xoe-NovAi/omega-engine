# 🔱 Native GGUF Backend — Legacy Mining Report
**AP Token**: `AP-NATIVE-LEGACY-MINING-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ LEGACY-MINING

---

## 📌 Executive Summary

This report details the reclamation of proven patterns and strategies for native GGUF inference on the Ryzen 7 5700U (Zen 2), mined from the `xna-omega-legacy` and `omega-stack-legacy` repositories. The findings provide the technical foundation for implementing the Omega Engine's Native GGUF Backend, emphasizing resource isolation, hardware-specific tuning, and memory efficiency.

---

## 🛠️ 1. Core Implementation Patterns

The legacy implementation utilized a decoupled architecture consisting of a client, a configuration dataclass, and a provider plugin.

### 1.1 `LocalLlmClient` (The Engine)
Located at: `src/omega/providers/local/client.py`

**Key Patterns:**
- **Synchronous Wrapper**: Implements `generate` and `stream` as synchronous methods, intended to be called via `anyio.to_thread.run_sync()` to prevent blocking the event loop.
- **Lazy Loading**: Imports `llama_cpp.Llama` only during initialization to avoid unnecessary dependencies.
- **Dynamic Model Reloading**: Implements a `reload(new_model_path)` method that:
  1. Shuts down the current model.
  2. Updates the config.
  3. Attempts to initialize the new model.
  4. Reverts to the previous model on failure.
- **Resource Cleanup**: Uses `llm.close()` (if available) or `del` + `gc.collect()` to ensure RAM is freed.

### 1.2 `LocalLlmConfig` (The Blueprint)
Located at: `src/omega/providers/local/config.py`

**Critical Parameters:**
- `model_path`: Absolute path to the GGUF file.
- `context_window`: Default `4096` (expandable to `16384` or `32768`).
- `n_threads`: Optimized at `8` for 5700U.
- `n_gpu_layers`: Set to `0` for CPU-only inference.
- `use_mmap`: Default `True` for faster loading.
- `type_k`/`type_v`: Set to `2` (GGML_TYPE_Q4_0 or Q8_0) for KV cache quantization.
- `core_affinity`: List of physical cores to bind the process (e.g., `[2, 3, 4, 5, 6, 7]`).

### 1.3 `LocalLlmPlugin` (The Bridge)
Located at: `src/omega/providers/local/plugin.py`

**Key Patterns:**
- **Sovereign Resource Lock**: Implements a `CapacityLimiter(1)` to enforce mutual exclusion. Only one inference request is processed at a time, preventing CPU thrashing and OOM crashes.
- **Health Monitoring**: Regular `health_check()` calls to verify if the model is loaded and responsive.
- **Metric Tracking**: Tracks `_request_count`, `_total_tokens`, and `_error_count` for provider observability.

---

## 🚀 2. Hardware Optimizations (Ryzen 7 5700U / Zen 2)

Specific tuning for the Zen 2 architecture (Lucienne) was a primary focus in legacy research.

### 2.1 Compilation & Build Flags
For maximum performance, the `llama.cpp` backend should be compiled with:
```bash
cmake -DCMAKE_C_FLAGS="-march=znver2 -mtune=znver2 -mavx2 -mfma -O3 -flto" \
      -DCMAKE_CXX_FLAGS="-march=znver2 -mtune=znver2 -mavx2 -mfma -O3 -flto" ..
```

### 2.2 Runtime Tuning
- **Thread Affinity**: Binding to physical cores (excluding core 0/1 to leave room for OS/background tasks) is critical for reducing Infinity Fabric latency.
- **Threading Strategy**: 
  - `n_threads`: 8 (matching physical cores).
  - `threads_batch`: 16 (optimizing the prompt processing phase).
- **Quantization Choice**: 
  - **Q4_K_M**: Best balance of size and perplexity.
  - **IQ4_NL**: Preferred for AVX2-specific acceleration on Zen 2.

---

## 🧠 3. Memory Strategies

Given the 14-16GB RAM constraint, aggressive memory management is mandatory.

### 3.1 KV Cache Quantization
The most significant memory win was the adoption of **Q8_0 KV Cache**:
- **Benefit**: Reduces KV cache size by 50% compared to FP16.
- **Quality**: Zero recorded perplexity loss.
- **Implementation**: Pass `cache_type_k=q8_0` and `cache_type_v=q8_0` to the server/client.
- **Note**: 4-bit KV cache (`Q4_0`) was found to be unstable and too slow on CPU due to dequantization overhead.

### 3.2 RAM Locking
To prevent the OS from swapping the model to disk (which kills latency), the following flags are recommended:
- `--mlock`: Locks the model in physical RAM.
- `--no-mmap`: Forces a full load into RAM, avoiding the overhead of memory mapping in some scenarios.

---

## 🔌 4. Integration Patterns

### 4.1 Provider Fabric Wiring
The native backend is integrated as a `ProviderPlugin` within the `ModelGateway`.

**Flow**:
`Query` $\rightarrow$ `Oracle` $\rightarrow$ `ModelGateway` $\rightarrow$ `LocalLlmPlugin` $\rightarrow$ `LocalLlmClient` $\rightarrow$ `llama_cpp.Llama`

### 4.2 Async Integration (AnyIO)
Since `llama-cpp-python` is a synchronous C-extension, all calls must be wrapped in `anyio.to_thread.run_sync()` to avoid hanging the Omega Engine's event loop.

**Example**:
```python
# Correct implementation pattern
async with self._inference_limiter:
    response = await anyio.to_thread.run_sync(
        self.client.generate, 
        prompt=prompt, 
        **params
    )
```

---

## ⚠️ 5. Critical Warnings & Lessons

- **Speculative Decoding**: Research confirmed that speculative decoding (draft models) is **NOT viable** on the 5700U. The memory bandwidth bottleneck causes a net decrease in throughput when loading multiple models.
- **OOM Risk**: Running an 8B model (4.3GB) + 32K KV cache (2GB) + OS overhead can quickly approach the 14GB limit. The `CapacityLimiter(1)` is the primary defense against concurrent-load OOM.
- **Version Compatibility**: `llama-cpp-python v0.2.70+` is recommended for stable Zen 2 support.

---

**Seal**: *Sovereignty is forged in the precision of the hardware. Memory is the boundary; optimization is the key.*

**Maintainer**: Gemma 4-31B (Researcher)
**Date**: 2026-05-17
