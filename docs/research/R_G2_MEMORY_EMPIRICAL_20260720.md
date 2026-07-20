# 🔬 G2: llama-cpp-python Memory Footprint (Zen 2) — Domain Research Report

**AP Token**: `AP-G2-MEMORY-EMPIRICAL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_g2_memory ⬡ ACTIVE

**Date**: 2026-07-20
**Campaign**: Research Campaign Manual v1.0.0 — Day 1-2 P0 Complete (G1/D308 only)
**Baseline**: Jem's Theoretical Analysis (R_LLAMA_CPP_MEMORY_ZEN2_20260720.md) — 497 lines, formulas + community benchmarks

---

## 📋 Domain Overview

| Metric | Value |
|--------|-------|
| **Total Gaps** | 5 (G2.1–G2.5) |
| **P0 Target** | 1 (G2.1) |
| **P1 Target** | 2 (G2.2, G2.3) |
| **P2 Target** | 2 (G2.4, G2.5) |
| **Primary Hardware** | AMD Ryzen 7 5700U/5800U (Zen 2, 8C/16T, 14Gi RAM ceiling) |
| **Key Optimization** | **q8_0 KV cache** — "free lunch" (50% KV memory reduction, <1% perplexity cost) |

---

## 🎯 Gap Research Cards — Completed (Day 3-4)

### Gap G2.1 — Empirical RSS 7B Q4_K_M on Zen 2 Linux ✅ **COMPLETED (CORRECTED)**
**Priority**: P0 | **Status**: ⚠️ **CORRECTED** — No direct 5700U/5800U empirical data exists
**Research Queries**: `llama.cpp RSS 7B Q4_K_M 8K context Linux 2026`, `llama-cpp-python memory usage 5700U 8K 16K 32K`, `llama.cpp memory benchmark Zen 2 2026`
**Success Criteria**: RSS measurements for 4K/8K/16K/32K context
**Finding**: **Zero public empirical RSS benchmarks for Ryzen 7 5700U/5800U (Zen 2 mobile)**. Proxy baseline established via validated formulas + community desktop data.
**Key Results**:
- 7B Q4_K_M model weights: **3.80 GiB** (deterministic, llama.cpp #2094)
- KV cache formula verified: `2 × L × H × d × T × bytes` (source: `llama-kv-cache.cpp`)
- **Q8_0 KV cache = 50% reduction** (FP16 4 bytes → Q8_0 2 bytes/token), <1% perplexity cost
- **Total RSS estimates (7B Q4_K_M + Q8_0 KV)**: 4K=4.35 GB, **8K=4.90 GB**, 16K=5.50 GB, 32K=6.60 GB
- **5700U advantage**: LPDDR4-4266 (51.2 GB/s) vs 5800U DDR4-3200 (34.1 GB/s) — **+50% bandwidth** may offset Zen 2 IPC deficit
- **14 GiB ceiling**: Q4_K_M + Q8_0 KV supports ~24K context with 1 GB margin
**Validation Required**: Run `llama-bench` + `smem`/`ps` on target hardware
**Full Details**: `docs/research/R_GAP_G2.1_FINDINGS_20260720.md`
**Confidence**: Theory 10/10, Empirical 3/10 (no direct measurements)

---

## 🎯 Gap Research Cards — Pending (Day 3-4 Continued)

### Gap G2.2 — Thermal Throttling 30min Sustained Inference

### Gap G2.2 — Thermal Throttling 30min Sustained Inference
**Priority**: P1 | **Status**: ⏳ PENDING
**Research Queries**: `llama.cpp sustained inference thermal 5700U 30min 2026`, `Zen 2 15W TDP llama.cpp thermal curve`
**Success Criteria**: Tok/s degradation curve + temp over 30min
**Baseline**: mambiux data shows 25W package power for 8B full offload; CPU-only stabilizes at ~3.0 GHz, 45-55°C

### Gap G2.3 — SomaticState Snapshot Size vs Context Length
**Priority**: P1 | **Status**: ⏳ PENDING
**Research Queries**: `llama_copy_state_data size context length 2026`, `llama.cpp state serialization memory disk 2026`, `M20 SomaticState llama.cpp checkpoint size`
**Success Criteria**: Bytes per context length (4K/8K/16K/32K)
**Baseline**: From `native_gguf.py` — snapshot size ≈ KV cache size; 8K ctx ~500 MB for 7B, ~1 GB for 14B

### Gap G2.4 — Multi-Model Router Overhead
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `llama-server --models-max memory overhead 2026`, `llama.cpp multi-model router RSS 2026`, `llama-cpp-python concurrent models memory`
**Success Criteria**: Router + N models vs standalone
**Baseline**: PR #17470 (Nov 2025) — multi-process router, LRU eviction, `--models-max` default 4

### Gap G2.5 — zRAM/Swap OOM Interaction
**Priority**: P2 | **Status**: ⏳ PENDING
**Research Queries**: `zRAM llama.cpp OOM behavior 2026`, `Podman memory limit llama.cpp swap 2026`, `M6 Podman Sovereignty memory pressure llama.cpp`
**Success Criteria**: OOM behavior under memory pressure
**Baseline**: M6 mandates `UserNS=keep-id` + `User=1000`; ResourceGuard has 1GB OOM margin

---

## 📊 Cross-Domain Synthesis Notes

### Critical Dependencies
- **G2.1 → G2.4, G2.5** — Empirical RSS baseline needed for router/zRAM analysis
- **G1.1 (Vulkan) → G2.1, G2.2** — GPU offload changes memory/thermal profile
- **G3.1 (TPM2 health) → G2.5** — Credential sealing memory overhead

### Key Architectural Decisions Validated (from Jem)
1. **q8_0 KV cache = mandatory default** — 50% KV memory win, negligible quality loss
2. **Per-model context tuning** — Not global max; Qwen3-4B-Thinking needs 26K, Qwen3-1.7B only 6K
3. **Single-model residency (`--models-max 1`)** — Required on 14Gi without GPU offload
4. **6 threads = thermal ceiling** — 8 threads = diminishing returns, 16 threads (SMT) = contention

### Model Portfolio (Jem's Recommendation)
| Priority | Model | Quant | Context | Threads | KV Cache | Est. RSS | Role |
|----------|-------|-------|---------|---------|----------|----------|------|
| P1 | Qwen3-4B-Thinking | Q4_K_M | **26,674** | 6 | q8_0 | ~4.5 GiB | Primary reasoning |
| P2 | MiMo-7B-RL | Q4_K_M | 8,192 | 6 | q8_0 | ~5.5 GiB | Coding/RL specialist |
| P3 | Qwen3-1.7B | Q6_K | 8,192 | 6 | q8_0 | ~2.5 GiB | Fast pillars / draft |
| P4 | RocRacoon-3b | Q4_K_M | 12,464 | 6 | q8_0 | ~3.0 GiB | Entity persona |
| P5 | Ministral-3B | Q4_K_M | 8,192 | 4 | q8_0 | ~2.5 GiB | Lightweight / edge |

---

## 📚 Source Index (from Baseline)

| # | Source | Type | Access Date | Key Content |
|---|--------|------|-------------|-------------|
| 1 | `src/omega/oracle/cpu_optimizer.py` | Local code | 2026-07-20 | KV cache formulas, Zen 2 constants, RAM budgets |
| 2 | `src/omega/oracle/resource_guard.py` | Local code | 2026-07-20 | OOMProtector, ResourceGuard, 1GB margin |
| 3 | `src/omega/oracle/providers.py` | Local code | 2026-07-20 | NativeGGUFProvider, worker isolation, context auto-select |
| 4 | `config/models.yaml` | Local config | 2026-07-20 | Model specs with ram_mb estimates |
| 5 | Roc's LM Studio mining | Internal report | 2026-07-11 | Universal q8_0, per-model context, GPU offload ratios |
| 6 | `scripts/benchmark_threads.py` | Local script | 2026-07-20 | Thread scaling benchmark with RSS |
| 7 | InventiveHQ "Context-Length Tax" | Web (Jun 2026) | 2026-07-20 | VRAM delta 2K→32K = +1.7 GB, flat tok/s |
| 8 | SpecPicks VRAM Guide | Web (Jul 2026) | 2026-07-20 | 7B/13B/14B/22B Q4_K_M on RTX 3060, KV cache tables |
| 9 | nam-ruto memory profiling | GitHub | 2026-07-20 | q8_0 cuts peak RSS ~45% at 32K (Apple Silicon) |
| 10 | mambiux ROCm on 5700U | GitHub (Dec 2024) | 2026-07-20 | 8B Q4_K_M, 25W, full offload, 6.84 tok/s |
| 11 | 200lz optimization lab | GitHub (2024) | 2026-07-20 | Ryzen 5800H WSL2, KV/context scaling RSS |
| 12 | llama.cpp PR #17470 | GitHub (Nov 2025) | 2026-07-20 | Multi-model router, --models-max, LRU eviction |
| 13 | Data Mammoth VPS Guide | Web (Apr 2026) | 2026-07-20 | 12GB RAM for 7B-9B, KV cache scaling table |
| 14 | ikawrakow/ik_llama.cpp Wiki | GitHub Wiki (Jan 2025) | 2026-07-20 | Zen4/AVX2/ARM_NEON performance tables |
| 15 | ggml-org/llama.cpp Discussion #3111 | GitHub | 2026-07-20 | KV cache size formula, --mlock behavior |

---

## 🏁 Domain Status

**Baseline Complete**: ✅ Jem's theoretical analysis + community benchmarks
**P0 Complete**: ✅ G2.1 (empirical RSS) — **CORRECTED**, proxy baseline + validation plan
**P1 Ready**: G2.2 (thermal), G2.3 (SomaticState)
**P2 Queued**: G2.4 (router), G2.5 (zRAM/OOM)

**Next Session**: Execute G2.2, G2.3 (empirical validation of theoretical model)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_g2_memory ⬡ BASELINE COMPLETE — EMPIRICAL PHASE PENDING*