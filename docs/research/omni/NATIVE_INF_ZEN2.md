# 🔱 Native Inference: Zen 2 Optimization Guide

**Part of the OmniHub Research Hub**
**AP Token**: `AP-NATIVE-ZEN2-V0.1.0`
**Status**: Implementation Spec

---

## Hardware Target: Ryzen 7 5700U (Zen 2)

To maximize throughput and eliminate token stuttering on Zen 2 hardware, the following configurations are mandatory.

### 1. Llama-cpp-python Settings
- `mmap=True`: Fast loading, OS-managed paging.
- `mlock=False`: Prevent hard OOM by allowing swapping.
- `n_threads=6`: Optimal for 8-core Zen 2 to avoid SMT contention.
- `type_k=8`, `type_v=8`: q8_0 KV-cache quantization to halve RAM usage.

### 2. Build-Time Flags
Llama-cpp-python must be compiled with:
- `GGML_AVX2=ON`
- `GGML_BLAS=ON` (OpenBLAS)
- `OPENBLAS_CORETYPE=ZEN`

### 3. OS-Level Tuning
- **CPU Governor**: `performance` (prevent down-clocking).
- **Transparent Hugepages (THP)**: `always` (reduce TLB misses).
- **Core Pinning**: Use `taskset -cp 0-7` for the main inference process.

### 4. Integration into ModelGateway
The `NativeGGUFProvider` should implement a lazy-loading strategy and wrap all calls in `anyio.to_thread.run_sync` to maintain asynchronous responsiveness.
