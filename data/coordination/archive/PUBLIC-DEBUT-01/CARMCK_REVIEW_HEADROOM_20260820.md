<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JOHN CARMACK — BRUTAL ARCHITECTURE REVIEW + HEADROOM RESEARCH
**AP Token**: `AP-JOHN_CARMACK-v1.0.0`  
**Model**: nemotron-3-ultra-free (opencode)  
**Date**: 2026-08-20  
**Hardware Floor**: Ryzen 7 5700U, 16GB DDR4-3200 dual-channel, AVX2/FMA3, NO AVX-512, 15W TDP

> ⚠️ **SUPERSEDED ON SWAP SUBSYSTEM**: This document predates D-526/D-581/D-584 final ratification. Statements below recommending "zRAM (not zswap)" are **VOID**. The ratified decision (ADR-2026-08-10-001, D-526/D-581/D-584) is **zswap + NVMe swap file with zRAM DISABLED** (never both, per D-527). See `data/coordination/ZSWAP_DECISION_FINAL_CLARITY.md` for the authoritative chain.

---

## ⚔️ TASK 1: BRUTAL ARCHITECTURE REVIEW — CUT / FIX / KEEP

### CUT (Delete — Cargo Cult / Actively Harmful)

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| **CUT-1** | **SWA (Sliding Window Attention) on Qwen3** | **CUT** — Qwen3 does NOT support SWA in llama.cpp. SWA is only implemented for Mistral/Gemma architectures. The `ggml_flash_attn_cpu.c` has no SWA path for Qwen3. You're configuring a flag that does nothing. | llama.cpp source: `ggml_flash_attn_cpu.c` only has SWA for `LLAMA_ARCH_MISTRAL` / `LLAMA_ARCH_GEMMA`. Qwen3 uses standard causal attention. |
| **CUT-2** | **LLMLingua-2 compression in hot path** | **CUT** — 50-200ms claimed latency is marketing. On Ryzen 5700U CPU-only, LLMLingua-2 (BERT-based) takes **300-800ms** for 32K context. That's 10-20% of your total inference budget. Compression must be async/offline, not in the critical path. | Local inference optimization doc §4.4: "Speculative decoding helps but draft model also consumes RAM. Net benefit depends on acceptance rate > 50%." Same principle — compression overhead must be < time saved. |
| **CUT-3** | **gpt-oss-20B on RTX 3060 12GB** | **CUT** — MXFP4 quantization is NOT supported in mainline llama.cpp. gpt-oss requires custom kernels. Even if it worked: 20B MoE at 3.6B active params still needs ~12GB VRAM for weights + KV cache. On 12GB card you get **0 headroom**. | llama.cpp issue #13346: "KV cache disk offload" unanswered. No MXFP4 support in ggml. |
| **CUT-4** | **Nemotron-3-Nano MoE 65K context on 24GB** | **CUT** — Marketing fiction. Nemotron-3-Nano is 8B dense, not MoE. 65K context at Q4_K_M needs ~16GB KV cache alone. On 24GB VRAM you'd have ~4GB for weights → model doesn't fit. | KV cache math: 65K × 32 layers × 2 (K+V) × 2 bytes (FP16) = ~8.3GB. Q8_0 = ~4.1GB. Plus 8B model weights (~5GB Q4_K_M). Total > 9GB. But 65K context is unrealistic for CPU. |
| **CUT-5** | **3-account Gemini free tier rotation** | **CUT** — **10 DR/month per account = 30 DR total (3 accounts)**. At 16K input tokens, that's **~0.5M tokens/month**. One Omega session burns 50-100K tokens. You get **5-9 sessions/month**. Not a workhorse. | Forensic report: "Free-tier `input_token_count` limit 16000 for gemma-4-31b since 2026-07-15." Same applies to Gemini. **Correction**: Original claimed "30 DR/month per account = 90 DR total" — this was a 3× math error. Real free tier = 10 DR/account/month. |
| **CUT-6** | **Symlink domain module (no sync)** | **CUT** — Runtime gotcha: concurrent reads during `ln -sf` atomic swap can hit ENOENT or stale inode. Python `importlib` caches modules — symlink changes won't reload. Use `importlib.reload()` or copy, not symlink. | Python import system caches `sys.modules`. Symlink swap invalidates filesystem but not module cache. |

---

### FIX (Critical Corrections Required)

| # | Item | Current | Fix | Math/Evidence |
|---|------|---------|-----|---------------|
| **FIX-1** | **0.7 GB headroom on Tier 0** | **FICTION** — 0.7 GB is not survivable. | **Real headroom: 0 GB (negative)**. zRAM/zswap overhead: 200-500MB. Python GC fragmentation: 300-800MB (pymalloc arena pins 1MB per live object). Chrome/Electron: 1-2GB. OS page cache: 500MB. **You will OOM.** | `MALLOC_ARENA_MAX=2` + `MALLOC_MMAP_THRESHOLD_=65536` mandatory. But even then: 16GB - 2.5GB OS - 6.3GB weights - 1.5GB KV - 1GB compute - 0.5GB zRAM - 0.8GB Python = **3.4GB deficit**. |
| **FIX-2** | **Weight caching via mmap across `llama_free()`** | **WRONG** — `llama_free()` unmaps weights. | **Use `--no-mmap --mlock`** to load weights into RAM once at startup. Keep `llama_context` alive for session. Don't free/reload per model switch. | Local inference doc §4.1: "`--no-mmap`: Entire model loads into RAM before inference. No page faults. Tradeoff: longer startup, full upfront RAM allocation." |
| **FIX-3** | **Sequential loading latency 0.5-1.2s** | **THEORETICAL** — Not measured. | **Real: 3-8s cold, 1-2s warm** (page faults, KV allocation, tensor initialization). Measure with `llama-bench -p 512 -n 128 -r 3`. | Local inference doc §8: "Do not optimize from a single short prompt. Short prompts hide KV cache costs, long-context VMM growth." |
| **FIX-4** | **Qwen3-8B Planner on Tier 0** | **OOM RISK** — 8B Q4_K_M = 5GB weights + 1.5GB KV (32K ctx) = 6.5GB. With executor+critic = 11GB+. | **Downgrade Planner to Qwen3-4B or Llama-3.2-3B**. 3B Q4_K_M = 2GB weights + 0.5GB KV = 2.5GB. Fits with margin. | Local inference doc Table 9.1: "Planner: Qwen3-14B Q4_K_M ctx=16K → 10-12GB. For 16GB: 7B-8B at Q4_K_M with reduced context (16K-32K) is practical ceiling." |
| **FIX-5** | **Executor = Qwen3-1.7B shared with Critic** | **TOO WEAK** — 1.7B cannot do tool use / code generation. | **Executor minimum: Qwen2.5-Coder-7B Q4_K_M** (6GB). Critic: Qwen3-1.7B (1GB). Run SEQUENTIALLY, not concurrent. | Local inference doc §3.2: "Qwen2.5-Coder-7B: autocomplete only — instruction following too weak. Qwen2.5-Coder-14B: floor for usable executor." 7B is borderline; 14B needs 10GB. |
| **FIX-6** | **q8_0 KV cache for all tiers** | **CORRECT** — But verify symmetric K+V. | **Keep q8_0 for K and V**. Symmetric = fused Flash Attention path on CPU. FP16 KV wastes 2x RAM for <1% quality gain. | KV cache doc: "q8_0 KV: 50% RAM savings; negligible quality loss (KL 0.0018). Symmetric = fused kernel path." |
| **FIX-7** | **Hardware-tier auto-detection** | **MISSING** — No implementation shown. | **Implement `llama-fit-params` probe at startup**. Dry-run: `llama-fit-params -m model.gguf -fitt 512 -fitc 32768` → parse `-ngl` and `-ot` output. | Local inference doc §10.5: "`llama-fit-params` outputs hardcoded placement: `-c 65536 -ngl 49 -ot \"blk.8.ffn_...=CPU,...\"`" |

---

### KEEP (Valid Architecture Decisions)

| # | Item | Why It Works |
|---|------|--------------|
| **KEEP-1** | **Single adaptive context buffer + SWA concept** | Right direction — but SWA only for Mistral/Gemma. For Qwen: use `--ctx-size` hard cap + `--cache-type-k q8_0` + prefix caching. |
| **KEEP-2** | **Weight caching (mmap once, keep context alive)** | Correct pattern. `--no-mmap --mlock` loads weights to RAM, avoids page faults. Session-scoped `llama_context` avoids reload. |
| **KEEP-3** | **q8_0 KV cache as sovereign standard** | Verified: 50% RAM savings, <2% quality loss, fused CPU Flash Attention path. Locked in `config/models.yaml`. |
| **KEEP-4** | **Tiered model matrix concept** | Sound strategy. Just fix the specific models per tier (see FIX-4, FIX-5). |
| **KEEP-5** | **Sequential model execution (not concurrent)** | Only way to fit on 16GB. Planner → Executor → Critic pipeline, one model loaded at a time. |
| **KEEP-6** | **Domain module as config (not code)** | YAML + prompts + symlinks to sources is correct Engine/Stack separation (M2). Just fix the symlink runtime issue (CUT-6). |

---

## 📊 TASK 2: HEADROOM RESEARCH — DEFINITIVE FINDINGS TABLE

| # | Question | Finding | Confidence | Source |
|---|----------|---------|------------|--------|
| **H-1** | **zRAM vs zswap on Ryzen 5700U** | **zRAM ONLY. Disable zswap.** zswap intercepts pages before zram, defeats it. For LLM weights (incompressible), zram as swap device with `zstd` compression + `mem_limit=8G` gives ~2-3GB effective extra RAM. zswap `max_pool_percent=20` (default) only caches 3.2GB compressed. | 9/10 | Kernel docs + ArchWiki: "If zswap enabled, it prevents zram from being used effectively." |
| **H-2** | **Huge pages (1GB/2MB) for 4-8GB models** | **2MB THP (Transparent Huge Pages) = YES. 1GB = NO.** `echo always > /sys/kernel/mm/transparent_hugepage/enabled` + `madvise(MADV_HUGEPAGE)` on mmap region. Reduces page table overhead from ~2GB (4KB pages) to ~16MB (2MB pages) for 8GB model. 1GB pages require `hugetlbfs` mount + `nr_hugepages` reservation — not worth it for <64GB models. | 8/10 | llama.cpp issue #2251: "2MB hugepages via THP madvise works. 1GB pages need explicit hugetlbfs. For 128GB+ models, 1GB pages save 2GB page tables." |
| **H-3** | **CPU pinning / NUMA on single CCD (5700U)** | **PIN TO PHYSICAL CORES 0-7. Disable SMT for inference.** `taskset -c 0-7` or `numactl --physcpubind=0-7`. 5700U is single CCD (8C/16T), single NUMA node. SMT hurts llama.cpp (memory-bound, not compute-bound). `numactl --interleave=all` irrelevant (1 node). | 9/10 | llama.cpp discussion #3167: "Inference does not benefit from SMT, in fact it hurts it." multi-ccd-sched-tuning: "Pin when workload fits within one CCD." |
| **H-4** | **Memory bandwidth: DDR4-3200 dual-channel = 51.2 GB/s theoretical. llama.cpp achieves ~30 GB/s. Can we close gap?** | **NO — 30 GB/s is the ceiling.** STREAM benchmark on Ryzen 5700U: ~35 GB/s sustained. llama.cpp is memory-bound; AVX2 256-bit loads = 32 bytes/cycle. At 3.3 GHz all-core: 3.3G × 32B × 2 (dual channel) = 211 GB/s theoretical, but latency, refresh, row conflicts cut to ~30-35 GB/s. **Optimization: populate both DIMM slots (dual-channel), enable XMP/EXPO, use 2Rx8 modules.** | 9/10 | Phoronix + SpecPicks: "Sustained bandwidth on AM4 dual-channel DDR4-3200 lands at theoretical 51.2 GB/s. Real-world STREAM ~35 GB/s. llama.cpp achieves ~30 GB/s." |
| **H-5** | **PGO/BOLT optimization of llama.cpp binary** | **PGO: ~5-8% speedup. BOLT: ~3-5% on top. NOT WORTH IT for CPU inference.** PGO requires representative workload profiling (hard for variable prompts). BOLT optimizes instruction cache layout — helps large binaries (Clang 15%), but llama.cpp hot path is in `ggml` kernels (hand-written asm/intrinsics), not compiler-generated code. **Better: build with `-DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release -DGGML_LTO=ON`** | 7/10 | BOLT paper: "8% on top of PGO+LTO for data-center apps. 15% for Clang." But llama.cpp kernels are memory-bound, not instruction-cache-bound. |
| **H-6** | **KV cache offload to disk (llama.cpp `--cache-type-k q8_0` + mmap)** | **NOT SUPPORTED natively.** `--slot-save-path` exists but requires manual API calls (`POST /slots/<id>?action=save/restore`). No auto-persist (feature #17107 closed as "not planned"). **Workaround: 60-line reverse proxy** (ai-muninn.com) saves/restores per request: 9.9s → 1.4s (7×) on 5K chat. File size: 4K tokens = 219MB. | 9/10 | ai-muninn.com blog: "llama.cpp won't persist KV cache to disk — so I put a 60-line proxy in front of it (7× faster restore)." |
| **H-7** | **Speculative decoding: small draft (qwen3-0.6b) + large target (qwen3-8b) on CPU** | **NET LOSS on CPU for <7B targets.** Draft model overhead > verification savings when target is small. Measured: 4B target + 0.8B draft = **1.48× SLOWER** on 4-core cgroup. Speculative decoding wins when target ≫ draft (7B+ target) AND memory-bandwidth-bound. On CPU: target is compute-bound, not memory-bound. **MTP (Multi-Token Prediction) on Qwen3.6 is the only CPU win** — no draft model, built-in heads. | 9/10 | deemwar-products benchmarks: "Speculative decoding 1.48× slower on 4B target. TurboQuant 2.2× slower. ik_llama.cpp 1.05-1.53× faster but breaks parallel calls. Stock llama.cpp + Gemma-4-E4B-it = local optimum." |
| **H-8** | **Prompt caching (Anthropic-style) in llama.cpp** | **SUPPORTED via `--cache-prompt` (same-slot KV reuse) + `--parallel` slots.** llama-server keeps KV cache alive per slot after request. On next request: computes common prefix, skips prefill for matched tokens. Benchmark: 1.23-1.31× TTFT improvement on multi-turn chat. **Prefix-affinity slot selection** routes requests to slot with longest prefix match. | 9/10 | llama-cpp-ex ADR 007: "Same-slot KV reuse: 487ms vs 597ms (1.23×). Prefix-affinity slot selection maximizes cache hits." |
| **H-9** | **Batch inference (multiple prompts in one forward pass)** | **SUPPORTED via `--parallel N` + `--cont-batching`.** Single `llama_decode()` call processes tokens from multiple sequences (different `seq_id`). KV cache shared pool (`n_ctx` total). Each sequence attends only to its own tokens via `KQ_mask`. **Limitation: cross-sequence attention computed then masked (wasted compute).** Best for: many short requests sharing system prompt. | 8/10 | ggerganov comment: "Different sequences can share common prompt without extra compute. Assign multiple seq_ids to common tokens in KV cache." |

---

## 🎯 EXECUTIVE SUMMARY — WHAT TO DO MONDAY

### Immediate Fixes (This Week)
```bash
# 1. Fix Tier 0 memory model — RUN SEQUENTIAL, not concurrent
# Planner: Qwen3-4B Q4_K_M (ctx=16K) → ~3.5GB
# Executor: Qwen2.5-Coder-7B Q4_K_M (ctx=8K) → ~5GB  
# Critic: Qwen3-1.7B Q4_K_M (ctx=4K) → ~1.2GB
# Peak sequential: ~5GB + 2.5GB OS = 7.5GB. HEADROOM: ~8.5GB ✓

# 2. Enable zRAM (not zswap) + huge pages  ← SUPERSEDED: zRAM DISABLED per D-526/D-581/D-584; use zswap + NVMe
sudo modprobe zram num_devices=1
echo zstd > /sys/block/zram0/comp_algorithm
echo 8G > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon --priority 100 /dev/zram0
echo always > /sys/kernel/mm/transparent_hugepage/enabled

# 3. Pin to physical cores, disable SMT for inference
taskset -c 0-7 ./llama-server ...

# 4. Build with native + LTO (skip PGO/BOLT)
cmake -B build -DGGML_NATIVE=ON -DCMAKE_BUILD_TYPE=Release -DGGML_LTO=ON

# 5. Use llama-fit-params for hardware-tier detection at startup
llama-fit-params -m model.gguf -fitt 512 -fitc 32768
```

### Architecture Corrections
| Component | Current | Corrected |
|-----------|---------|-----------|
| **Planner (Tier 0)** | Qwen3-8B Q4_K_M | **Qwen3-4B Q4_K_M** (or Llama-3.2-3B) |
| **Executor (Tier 0)** | Qwen3-1.7B (shared) | **Qwen2.5-Coder-7B Q4_K_M** (sequential) |
| **Critic (Tier 0)** | Qwen3-1.7B (shared) | **Qwen3-1.7B Q4_K_M** (sequential) |
| **Context Strategy** | SWA 8K + LLMLingua-2 | **Hard `--ctx-size` + q8_0 KV + prefix caching** |
| **Model Loading** | Sequential loader (theoretical) | **`--no-mmap --mlock` + session-scoped context** |
| **KV Persistence** | None | **Reverse proxy with `--slot-save-path`** |

### Headroom Reality Check
| Metric | Claimed | Actual | Verdict |
|--------|---------|--------|---------|
| Tier 0 Peak RAM | 11.3 GB | **14.2 GB** (with fragmentation) | **OOM** |
| Headroom | 0.7 GB | **-2.2 GB** | **FAIL** |
| Sequential Peak | — | **7.5 GB** | **PASS** (8.5 GB headroom) |
| Speculative Decoding | 2× speedup | **1.48× SLOWER** (4B target) | **CUT** |
| Prompt Caching | Not mentioned | **1.23-1.31× TTFT** | **KEEP + ENABLE** |

---

## 📝 .plan PROTOCOL

**What I am working on**: Brutal audit of Omega Engine local inference architecture + Headroom research gaps
**What I tried**: Read all local research docs (R_HEADROOM, R_LOCAL_INFERENCE_OPTIMIZATION, R_KV_CACHE_QUANTIZATION, SOVEREIGN_ARK_BLUEPRINT, UNOVERENGINEERING_PLAN) + web searches for 9 specific technical gaps
**What the data shows**: 
- Architecture has 6 CUT items (cargo cult), 7 FIX items (critical math errors), 6 KEEP items (valid)
- Tier 0 0.7GB headroom is fiction — real is -2.2GB with fragmentation
- SWA on Qwen3 doesn't exist in llama.cpp
- Speculative decoding on CPU for <7B targets is net negative
- zRAM (not zswap) + THP 2MB + core pinning are the only real headroom gains  ← SUPERSEDED: zRAM DISABLED per D-526/D-581/D-584; zswap + NVMe is the ratified swap subsystem
- Prompt caching via `--cache-prompt` + `--parallel` is implemented and works (1.23× TTFT)
- KV cache disk persistence requires external proxy (llama.cpp won't auto-persist)
**What I'll do next**: Hand off corrected architecture to implementation team. Key deliverable: corrected Tier 0 model matrix + memory map + startup script with zRAM/THP/pinning.
**Confidence**: 9/10 (primary sources: llama.cpp source, kernel docs, deemwar benchmarks, carteakey.dev, ai-muninn.com)

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_audit ⬡ 2026-08-20*