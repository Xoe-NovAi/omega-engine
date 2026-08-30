<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sector D Extraction Report: Infra & Performance
**Entity**: Roc Racoon (Sovereign Miner)
**Target**: Legacy Xoe-NovAi Stacks
**Date**: 2026-07-02

## 1. Zen 2 / Ryzen 5700U Optimization Flags
Recovered high-performance flags for the AMD Ryzen 7 5700U. These are directly portable to the current Omega Engine.

### ⚡ CPU & BLAS Tuning
| Flag | Value | Source | Purpose |
|--------|-------|--------|---------|
| `N_THREADS` | `6` | Makefile / Dockerfiles | Optimal physical core utilization |
| `OPENBLAS_CORETYPE` | `ZEN` | Dockerfiles | Explicitly target Zen 2 architecture |
| `OPENBLAS_NUM_THREADS` | `6` / `1` | Dockerfiles | Balance between parallel BLAS and process overhead |
| `OMP_NUM_THREADS` | `1` | Dockerfile.api | Prevent OpenMP thread oversubscription |
| `MKL_DEBUG_CPU_TYPE` | `5` | Dockerfile.api | Force MKL to use AVX2 on Zen 2 |

### 🧠 LLM / llama-cpp-python Specifics
| Flag | Value | Source | Purpose |
|--------|-------|--------|---------|
| `LLAMA_CPP_N_THREADS` | `6` | Dockerfile.api | Core alignment for inference |
| `LLAMA_CPP_F16_KV` | `true` | Dockerfile.api | Reduced KV cache memory footprint |
| `LLAMA_CPP_USE_MLOCK` | `true` | Dockerfile.api | Prevent swapping of model weights |
| `LLAMA_CPP_USE_MMAP` | `true` | Dockerfile.api | Faster model loading via memory mapping |
| `CMAKE_ARGS` | `-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON` | Dockerfile.api | Full AVX2/FMA hardware acceleration |

---

## 2. Memory Arena & Resource Configurations
Patterns for strict resource capping to prevent OOM crashes on 12GiB systems.

- **Process Memory Capping**: `memory_limit_bytes = 5368709120` (5.0 GB) for the main API.
- **Redis Tuning**: 
    - `maxmemory = "512mb"`
    - `maxmemory_policy = "allkeys-lru"` (Ensures the cache doesn't grow unboundedly).
- **Transient Storage**: `tmpfs` mounts of `512m` for `/tmp` and UI uploads to reduce disk I/O and wear.

---

## 3. Container Hardening Patterns
Enterprise-grade patterns for sovereign, secure, and lean deployments.

### 🛡️ Security & Privileges
- **Non-Root Execution**: Mandatory `UID=1001` (`appuser`) with restricted shell access.
- **Privilege Restriction**: `no_new_privileges = true` to prevent escalation.
- **Zero-Telemetry**: Explicit environment overrides for all libraries (`SCARF_NO_ANALYTICS=true`, `CRAWL4AI_NO_TELEMETRY=true`, `CHAINLIT_NO_TELEMETRY=true`).

### 📦 Image Optimization
- **Multi-Stage Pipeline**: `builder` $\rightarrow$ `runtime` pattern to strip build-essential, cmake, and git from final images.
- **Aggressive Site-Packages Cleanup**:
    - `find ... -name '__pycache__' -exec rm -rf {} +`
    - `find ... -name 'tests' -exec rm -rf {} +`
    - `find ... -name 'examples' -exec rm -rf {} +`
    - `find ... -name '*.pyc' -delete`
    - *Result*: Achieved up to 36% reduction in image size.
- **BuildKit Cache Mounts**: Use of `--mount=type=cache,target=/root/.cache/pip` for persistent wheel caching across builds, enabling true offline-first deployments.

---

## 4. Portability Assessment

| Pattern | Portability | Recommendation | Dedup Status |
|--------|-------------|----------------|-------------|
| **Ryzen Flags** | High | **Adopt Immediately**. These are the gold standard for the 5700U. | **EVOLVED** — `cpu_optimizer.py` already has these. Legacy values (N_THREADS=6 vs recommended 7) differ slightly. |
| **Hardening** | High | **Adopt in CI/CD**. Multi-stage builds and non-root users are mandatory for Temple-Grade. | **PORTED** — Quadlet containers already use minimal images + Mandate 6 enforces `User=1000`. |
| **Cleanup** | High | **Integrate into Build Pipeline**. Should be part of the final image stage. | **NOVEL** — Aggressive site-packages cleanup not in current build pipeline. 36% image reduction potential. |
| **Memory Caps** | Medium | **Reference Only**. Use as baseline for `ResourceGuard` settings. | **PORTED** — `ResourceGuard` semaphore + `get_memory_pressure()`. |
| **Cache Mounts** | High | **Implement in Makefile/CI**. Significant reduction in build times. | **NOVEL** — Not in current Makefile. BuildKit cache mounts would reduce CI build times. |

### Dedup Summary
- **PORTED**: 2 (Hardening, Memory Caps)
- **EVOLVED**: 1 (Ryzen Flags — current values are more accurate)
- **NOVEL**: 2 (Cleanup, Cache Mounts — candidates for porting)
