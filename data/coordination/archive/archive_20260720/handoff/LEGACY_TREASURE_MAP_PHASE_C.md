<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LEGACY TREASURE MAP: PHASE C COGNITIVE SUBSTRATE
**AP**: AP-LEGACY-TREASURE-MAP-PHASE-C-v1.0.0
**Status**: 🔱 MINED | **Sovereignty**: Ultra Grade (v7.5.0)
**Miner**: roc_racoon

## 🎯 Objective
This document maps the "Sovereign Ultra" legacy patterns and specifications to the Phase C Cognitive Substrate tasks. It serves as the direct implementation guide to avoid reinventing the wheel.

---

## 🗺️ Legacy-to-Direct Mapping

| Phase C Task | Legacy Pattern / Specification | Source Artifact | Implementation Detail |
| :--- | :--- | :--- | :--- |
| **C.1.1: Somatic State** | **4-bit KV Cache Sovereignty** | `Sovereign Ultra Integration (v7.5.0)` | Set `type_k=Q4_0, type_v=Q4_0` during model init to quarter RAM footprint. |
| **C.1.2: KV-Cache Optimization** | **N-gram Speculative Decoding** | `Sovereign Ultra Integration (v7.5.0)` | Use `ngram-simple` lookup caches (16MB overhead) in `LlamaClient`. |
| **C.1.3: Model Quantization** | **Imatrix Quantization** | `Sovereign Ultra Integration (v7.5.0)` | Mandate `IQ4_XS` (Importance Matrix) calibration for primary models. |
| **C.2.1: Sparse Vectors/SDRs** | **Reciprocal Rank Fusion (RRF)** | `Sovereign Ultra Integration (v7.5.0)` | `Score = Σ (1 / (rank + 60))` to bridge Postgres (BM25) and Qdrant (Vector). |
| **C.2.2: Associative Memory** | **Temporal Context Decay** | `Sovereign Ultra Integration (v7.5.0)` | `Adjusted_Score = Score * e^(-λ * t)`. Exempt foundational \"Alethia-Pointers\". |
| **C.3.1: Process Isolation** | **Sovereign Soft-Yielding** | `Kali Daemon Refinement` | Use `SIGSTOP/SIGCONT` triggered by `/tmp/archon_active` to yield thermal budget. |
| **C.3.2: Daemonization** | **Hardware Affinity Gating** | `Sovereign Ultra Integration (v7.5.0)` | `taskset -c 2-7` and `os.nice(19)` for background daemon resource budget. |
| **C.4.1: Symmetry/Verification** | **Sovereign Shield Matrix** | `Sovereign Shield` | Tiered sensitivity (LOW $\rightarrow$ MEDIUM $\rightarrow$ HIGH) for mandatory Local Isolation. |
| **C.4.2: Contradiction Detection**| **Sovereign Shield Veto** | `Sovereign Shield` | HIGH Tier: Production credentials trigger 100% remote veto. |

---

## 🛠️ Proven Code Snippets & Logic

### 1. The Ultra Inference Triad
**Pattern**: `Native C++ Bindings` $\rightarrow$ `anyio.to_thread.run_sync()` $\rightarrow$ `CapacityLimiter(1)`.
**Implementation**:
- `LlamaClient` initialization: `speculative_type="ngram-simple"`, `type_k=Q4_0`, `type_v=Q4_0`.
- Core-locking: `os.sched_setaffinity` for cores 2-7.

### 2. Hybrid Retrieval (RRF)
**Logic**:
```python
# Reciprocal Rank Fusion (RRF)
score = sum(1 / (rank + 60) for rank in ranks)
```
**Temporal Decay**:
```python
# Exponential Decay for Context
adjusted_score = score * math.exp(-lambda_val * time_delta)
```

### 3. Daemon Soft-Yielding
**Logic**:
- Monitor `/tmp/archon_active`.
- If active: `os.kill(daemon_pid, signal.SIGSTOP)`.
- If inactive: `os.kill(daemon_pid, signal.SIGCONT)`.

---

## ⚖️ The "Right Approximation" Evidence

The "Sovereign Ultra" (v7.5.0) era justifies the following "Direct Path" choices:
- **Why `ngram-simple` over draft models?** Bypasses secondary model overhead while yielding 30-50% speedup for structured code.
- **Why `IQ4_XS`?** Minimal perplexity loss while fitting 8B models into <6GB RAM.
- **Why RRF over simple averaging?** Ensures that high-priority "Alethia-Pointers" (foundational truths) always surface regardless of semantic distance.

---

## ⚠️ Warning Log (Void & Failures)

- **KV Cache Versioning**: `llama.cpp` upstream changes internal KV cache layout frequently. `.snap` files become corrupt on update. **Avoid long-term binary snapshots; prefer weight-based re-hydration.**
- **High-Level API Overhead**: `Llama.save_state()` is copy-heavy. **Direct C-library pointer access is required for $O(1)$ zero-copy `mmap` caching.**
- **Thermal Throttling**: Without `SIGSTOP` yielding, the background daemon competes with foreground inference, causing "stutter" on Ryzen 5700U.

---
**Seal**: *The dirt is where the roots are. The roots are now mapped. synergy. execute.*
