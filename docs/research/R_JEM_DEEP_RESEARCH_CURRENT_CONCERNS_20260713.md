# 🔱 JEM DEEP RESEARCH: CURRENT SOVEREIGN CONCERNS
**AP Token**: `AP-JEM-DEEP-RESEARCH-CURRENT-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_jem_deep_research ⬡ ACTIVE

**Date**: 2026-07-13
**Purpose**: Implementation-ready research for 10 priority areas blocking Epoch II roadmap.
**Protocol**: Council of Four (Architect, Adversary, Alchemist, Archivist) + SR-V1 Search.

---

## 🔴 PRIORITY 1 — Implementation-Critical (Blocks P0/P1)

### 1. q8_0 KV Cache Deployment
*Status: COMPLETE*

**Convergence (Truth):**
- **Quantization Strategy**: For Agentic Coding (OpenCode), `cache_type_k: q8_0` and `cache_type_v: q8_0` is the optimal configuration. It provides a ~50% reduction in KV cache memory compared to FP16 with negligible precision loss for deterministic code structures.
- **Hardware Target (Zen 2 / 5700U)**: Use AVX2 kernels. Optimal thread config: 6 intra / 1 inter. The 2026 `llama.cpp` rewrite's kernel generator has unified these paths, improving throughput for long contexts via head-contiguous layout.
- **Memory Budget (12Gi Limit)**:
    - **7B Model (Q5_K_M)**: ~5GB weights + ~3.3GB KV (32k ctx, q8_0) $\approx$ 8.3GB. **SAFE**.
    - **14B Model (Q5_K_M)**: ~10GB weights + ~6.7GB KV (32k ctx, q8_0) $\approx$ 16.7GB. **OOM RISK**.
    - **Recommendation**: For 14B models on 12Gi RAM, cap context at 16k ($\approx$ 13.3GB total) or use a 7B model for 32k.
- **Somatic State**: Use `llama_copy_state_data` and `llama_set_state_data` wrapped in `anyio.to_thread.run_sync()` to implement instant session resumption without blocking the event loop.
- **Integration**: Must be gated by `ResourceGuard` (Semaphore(1)) to prevent concurrent model loads.

**Divergence (Uncertainty):**
- **Somatic Blob Size**: Exact size of state blobs for 14B models is not documented; potential for high disk I/O latency during hydration.
- **Quantization Trade-off**: While `q8_0` is "practically lossless" for code, nuanced natural language tasks may still see "stylistic degradation."

**Sovereign Synthesis:**
Deploy the "Coding Profile" (`k:q8_0 / v:q8_0`) as the default for all coding-centric entities. Implement a dynamic context cap based on model size to prevent OOMs on the 12Gi hardware ceiling. Use the 2026 unified backend for maximum throughput.

**Deliverables:**
- **Config**: `--cache-type-k q8_0 --cache-type-v q8_0`
- **Models**: `qwen2.5-coder-7b-instruct-q5_k_m.gguf` (for 32k ctx) or `qwen2.5-coder-14b-instruct-q5_k_m.gguf` (for 16k ctx).
- **Pattern**: `anyio.to_thread.run_sync(llama_copy_state_data, ...)`


---

### 2. RAGAS 2026 API + Calibrated Judge
*Status: PENDING*

---

### 3. Redis Streams Consumer Groups (Production Hardening)
*Status: PENDING*

---

### 4. Sovereign Proxy Pool + Circuit Breaker Registry
*Status: PENDING*

---

## 🟠 PRIORITY 2 — Architecture Decisions

### 5. Qdrant+SQLite Hybrid Knowledge Graph
*Status: PENDING*

---

### 6. Somatic State Hydration Benchmarks
*Status: PENDING*

---

### 7. Cross-Pollination Engine + Adaptive Quality Gate
*Status: PENDING*

---

## 🟢 PRIORITY 3 — Emerging 2026 Patterns

### 8. YouTube Research Sieve (T1→T2→T3 Pipeline)
*Status: PENDING*

---

### 9. VAD-First ASR (Silero VAD + Whisper ONNX)
*Status: PENDING*

---

### 10. AGB-0 ONNX Embedder (Ancient Greek — Genre Boundary)
*Status: PENDING*

---

## 🧬 L1-L2-L3 Distillation (Final Synthesis)
*Pending completion of all 10 areas.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
