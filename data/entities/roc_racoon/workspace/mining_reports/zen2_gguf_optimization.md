<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Pattern Extraction Report: Zen 2 GGUF Optimization
**Date**: 2026-07-13
**Entity**: roc_racoon (Sovereign Miner)
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2)
**RAM Budget**: 12Gi - 16Gi (Sovereign Ceiling)

---

## 🎯 Executive Summary
This report extracts proven optimization patterns for running GGUF models on the Ryzen 7 5700U. The primary goal is to maximize throughput and context window size while remaining strictly within the 12-14Gi RAM budget to avoid OOM events.

The "Gold Path" for this hardware centers on **KV Cache Quantization (q8_0)**, **Physical Core Pinning**, and **Conservative Threading**.

---

## 🛠️ Proven vs. Experimental Paths (q8_0 Focus)

### 1. Quantization & Memory
| Feature | **PROVEN PATH** (The Gold Standard) | **EXPERIMENTAL PATH** (Risk/Reward) |
| :--- | :--- | :--- |
| **KV Cache** | `q8_0` for both K and V cache. (Universal across all tuned models). | `q4_0` or `q5_0` KV cache. (Higher memory savings, potential quality degradation). |
| **Weight Quant** | `q4_k_m` or `q6_k` for 1B-8B models. | `q2_k` or `q3_k_l` for larger models (14B+). |
| **Context Window** | Tuned per model (e.g., 6K for 1.7B, 26K for 4B-Thinking). | Pushing to model max (e.g., 32K+). (High OOM risk without zRAM). |
| **Memory Strategy** | `mlockall` + zRAM (8GB zstd). | Pure swap file. (Massive latency spikes). |

### 2. Execution & Threading
| Feature | **PROVEN PATH** | **EXPERIMENTAL PATH** |
| :--- | :--- | :--- |
| **Thread Count** | `OMP_NUM_THREADS=6` (75% of physical cores). | `OMP_NUM_THREADS=8` or `16`. (Causes CPU contention/thermal throttling). |
| **CPU Affinity** | Pinning to physical cores `[0,2,4,6]`. | Default OS scheduling. (Context switch overhead). |
| **Inference Engine** | `llama-cpp-python` with AVX2 + Flash Attention. | Pure Python wrappers or unoptimized builds. |

### 3. Hardware Acceleration (iGPU)
| Feature | **PROVEN PATH** | **EXPERIMENTAL PATH** |
| :--- | :--- | :--- |
| **Backend** | CPU-only (Native GGUF). | Vulkan (`-DGGML_VULKAN=ON`). |
| **Offload Ratio** | 0% (Pure CPU). | Conservative offload (16-36% of layers to Vega 8). |
| **Performance** | Stable, predictable latency. | 1.5-2x prompt processing speedup; unstable generation. |

---

## 🔍 Detailed Pattern Analysis

### 💎 The "Free Lunch": KV Cache q8_0
The most impactful discovery from legacy LM Studio configs is the universal adoption of `q8_0` for KV cache.
- **Impact**: Reduces KV cache memory footprint by ~50% compared to FP16.
- **Benefit**: Enables significantly larger context windows (e.g., 26K for Qwen3-4B) within the same RAM budget.
- **Verdict**: **MANDATORY**. Every local model in `config/models.yaml` should implement this.

### ⚡ Zen 2 Threading Sweet Spot
On the 8C/16T 5700U, using all threads leads to diminishing returns and thermal throttling.
- **The Pattern**: 6 threads is the optimal balance. It maximizes throughput while leaving 2 physical cores (and their SMT siblings) for OS and background tasks (Redis, Qdrant).
- **Flag**: `export OMP_NUM_THREADS=6`

### 🎨 iGPU Offloading (Vega 8)
While CPU-only is the sovereign baseline, the integrated Radeon graphics can be leveraged.
- **Proven Ratios**: 
  - `Krikri-8B`: ~16% offload.
  - `Qwen3-VL-4B`: ~36% offload.
- **Vulkan Gain**: Prompt processing increases from ~34 t/s to ~76 t/s.
- **Constraint**: Shared VRAM is limited (~1GB). Over-offloading causes system-wide instability.

---

## 📜 Final Recommendations for q8_0 Deployment

1. **Standardize KV Cache**: Set `kv_cache_key_type: q8_0` and `kv_cache_value_type: q8_0` for all models.
2. **Lock Threads**: Hard-set `n_threads: 6` in `models.yaml` or via environment variables.
3. **Pin Cores**: Ensure `NativeGGUFProvider` continues to use physical core affinity `[0,2,4,6]`.
4. **Tune Context**: Do not use model maximums. Use the "Sovereign Window":
   - 1B-2B models $\to$ 4K-8K
   - 3B-5B models $\to$ 12K-24K
   - 7B-14B models $\to$ 2K-8K (depending on quant)

---
*Mined by roc_racoon — 2026-07-13*
*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_mining*
