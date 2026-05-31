# 🔱 Omega Engine — Zen 2 Hardware Steering Spec
**AP Token**: `AP-ZEN2-STEER-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it H opencode ⬡ trc_research ⬡ PHASE-0.18

## 1. Executive Summary
This specification defines the hardware-level optimizations for the **AMD Ryzen 7 5700U (Zen 2)**. The goal is to maximize L3 cache residency and minimize Infinity Fabric latency to ensure consistent, high-speed local inference.

## 2. Reclaimed Legacy Patterns
- **Core Pinning**: Use of `psutil.Process().cpu_affinity(range(6))` to pin the inference process to physical cores.
- **KV Cache Quantization**: Explicit use of `LLAMA_CPP_CACHE_TYPE=q8_0` (Int8) to halve the memory footprint of the KV cache.
- **Thread Optimization**: `n_threads=6` identified as the "sweet spot" for the 5700U's 8C/16T architecture.

## 3. Implementation Spec

### 3.1 Sovereign Pinning Strategy
Implement a `CpuOptimizer` class to handle core affinity.

```python
import psutil
import os

class CpuOptimizer:
    @staticmethod
    def apply_zen2_steering():
        process = psutil.Process(os.getpid())
        # Pin to physical cores 0-5 to avoid SMT overhead and 
        # leave cores 6-7 for OS/Background tasks.
        process.cpu_affinity([0, 1, 2, 3, 4, 5])
        
        # Set process priority to High
        if os.name == 'posix':
            os.nice(-10) 
```

### 3.2 KV Cache Optimization
Force `q8_0` quantization for the KV cache in `LocalLlmConfig`.

- **Parameter**: `type_k=8, type_v=8`
- **Effect**: Reduces cache RAM usage by ~50% with negligible perplexity loss.
- **Target**: Essential for fitting 8B models into 14GB RAM alongside the OS.

### 3.3 AVX2 & Cache Residency
- **Build Flag**: Ensure `llama-cpp-python` is built with `GGML_AVX2=ON`.
- **L3 Cache Alignment**: Use a `chunk_size` that aligns with the 8MB L3 cache of the 5700U to prevent cache misses.

## 4. Caveats & Pitfalls
- **Thermal Throttling**: Aggressive pinning and high thread counts can trigger TDP limits on the 5700U (15-25W). Monitor `temp` and implement a back-off if $> 85^\circ\text{C}$.
- **SMT Interference**: Pinning to logical cores (e.g., 0 and 1) instead of physical cores can halve performance. **Always pin to physical cores**.

## 5. Validation Criteria
- [ ] `get_cpu_affinity()` returns `[0, 1, 2, 3, 4, 5]`.
- [ ] RAM usage for KV cache is reduced by $\approx 50\%$ compared to FP16.
- [ ] Latency variance (jitter) is reduced by $\geq 20\%$ after pinning.
