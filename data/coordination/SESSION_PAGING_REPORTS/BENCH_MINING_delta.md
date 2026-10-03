<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# BENCH_MINING delta — roc_racoon paging report
**AP**: AP-ROC_RACOON-v1.0.0 | **Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO)
**Date**: 2026-08-21 | **Scope**: legacy model-benchmark mining → V-1 Vault (Path B, D-562/D-568) + LI Tier 0/1/2 matrix (D-585)
**Incorporates**: sibling BENCHMARK_PLAN delta (pair-comparisons, MDE, Wilcoxon, tiered CPU profiles)
**Status**: IN_PROGRESS

## §1 Forgotten Benchmark Data & Methodology — LI Matrix Relevance

### 1.1 Production benchmark harness (directly adaptable)
- `Old-Stacks/Xoe-NovAi/scripts/query_test.py` (538 lines, dated 2025-10-13)
- Targets: 15–25 tok/s | p95 <1000ms | mem <6GB | cache hit >50%
- Stats: min/max/mean/median/p95 per run; JSON export; `--benchmark` = 50q × 3 iter
- Patterns worth preserving: health-check preflight aborts run; exit-code 0/1 CI gate
- GAP vs BENCHMARK_PLAN: word-count token estimate (no tokenizer), no pair-comparison,
  no significance testing, single-run variance unknown → legacy numbers are ANCHORS,
  NOT evidence. Confirms Wilcoxon-over-t-test + MDE upgrade is the right call.

### 1.2 Measured Ryzen 7 5700U anchors (Zen 2, 16GB) — Tier sanity floors
| Metric | Measured | Source |
|---|---|---|
| Gemma-3-4b-it Q5_K_XL tok/s | 22 mean (target 15–25) | condensed-guide.md App B |
| Peak memory | 5.2GB @ 10k-vector ingest | condensed-guide.md App B |
| Latency p95 | 0.85s (1000-req bench) | condensed-guide.md App B |
| Ingestion rate | 180/h | condensed-guide.md App B |

### 1.3 Complete CPU tier profile (maps to "tiered profiles mandatory on CPU")
LLAMA_CPP_N_THREADS=6 (75% of 8C/16T) · OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1 · OPENBLAS_CORETYPE=ZEN · MKL_DEBUG_CPU_TYPE=5
TOKENIZERS_PARALLELISM=false · NUMEXPR_NUM_THREADS=1 · MALLOC_ARENA_MAX=4
f16_kv=true (~1GB KV savings) · use_mlock=true · use_mmap=true · n_batch=512
Embeddings profile: n_threads=2, n_ctx=512 (dependencies.py:374-375)

### 1.4 Quantization findings (pre-validates LI quant axis)
- Q5_K_M/Q6_K = "Ryzen sweet spot" (90% conf): 95–98% quality, 3–4x smaller,
  ~50% faster (phase3_implementation_guide_research_verified.md:16,101)
- Q8_0 = 98% accuracy, reserved for embeddings (all-MiniLM-L12-v2.Q8_0)
- AWQ INT4: 94% retention, 4x mem reduction (system-prompts changelog:367) — UNVERIFIED locally
- Production pick was UD-Q5_K_XL variant @ 2.8GB

### 1.5 Acceleration deltas (claims-discipline precedent)
- Vulkan iGPU: +36% CLAIMED → corrected +20–25% by Grok adversarial review
  (condensed-guide corrections log) — exactly the MDE-style overclaim risk
- AVX2/F16C/FMA build flags: 25–40% Zen 2 gains (Grok convo 14851)
- cpupower performance governor: +15–30% throughput (Grok convo 14830)
- LM Studio qwen offloadRatio=0.5 → iGPU partial-offload experimented in Era 3

## §2 Legacy Sources Worth Re-Mining (ranked by LI-validation value)

| # | Path | Extract |
|---|------|---------|
| 1 | Old-Stacks/Xoe-NovAi/scripts/query_test.py | Harness skeleton → adapt endpoints + tokenizer |
| 2 | Old-Stacks/.../app/XNAi_rag_app/dependencies.py | LlamaCpp param factory + retry/breaker wiring |
| 3 | Old-Stacks/.../app/XNAi_rag_app/config_loader.py | Pydantic perf schema (targets as validators) |
| 4 | Old-Stacks/Xoe-NovAi/config.toml | Production baseline config (n_ctx=2048 etc.) |
| 5 | Old-Stacks/.../phase3_day567_execution_complete.md:39 | ModelOptimizer.benchmark_model_performance() code |
| 6 | Old-Stacks/.../ml_docker_optimization_guide_v2.md:482 | benchmark_inference() function |
| 7 | omega_library intake XNAI_blueprint.md App B | Baseline tables + `make benchmark` gate spec |
| 8 | omega_library intake condensed-guide.md | Validated metrics + adversarial correction log |
| 9 | grok_unified_index.db (274 convos, FTS5 ~45ms) | Convo 14830/14851: cited Ryzen benchmarks w/ URLs |
| 10 | ~/.lmstudio/.../qwen/config.json | Offload experiment record |
| 11 | ~/.ollama/history | krikri-8B interactive eval pattern (qualitative) |
| 12 | model-guide (2).md (Era 0–1) | Pantheon candidate set: RocRacoon-3B, Phi-2-Omnimatrix,
     Hermes-Trismegistus-Mistral-7B, Krikri-8B, MythoMax-13B, Gemma-3-1B/4B |

NOT yet exhausted (original mission scope):
- ~/Documents/docs-backup/internal_docs/01-strategic-planning/ (ANAi strategy)
- grok exports STRATEGIC_RESERVES/ deep content
- "DR - Top 20 Resources for EmbGemma" + EmbeddingGemma model card (embedding tier)
- test_voice.py voice-latency pattern (if LI adds multimodal tiers later)

## §3 Flagged Important — Never Executed (debt register for LI/V-1)

1. n_ctx scaling experiments: NEVER run. 2048 was pragmatic default
   (config.toml:40); no 1024/4096/8192 comparisons exist anywhere.
   → LI matrix should own this axis explicitly.
2. Vulkan iGPU offload: PHASE2_VULKAN_ENABLED hook + CMAKE_ARGS spec written,
   corrected gain (+20–25%) documented — zero execution evidence found.
3. AWQ INT4 pipeline: awq_quantizer.py + scripts/awq-production-setup.sh
   referenced in phase1-foundation-security.md:128 — files NOT FOUND in any
   archive dump; 94%-retention claim unvalidated locally.
4. Drift/fairness detection (xnai:drift_stream, >10% accuracy alert): fully
   designed, never implemented (Phase 2 casualty).
5. Qdrant migration (+20% retrieval claim): PHASE2_QDRANT_ENABLED hook only.
6. 99.5% uptime / 7-day soak test: asserted in 3 docs, no log artifact in any
   partition — treat as unverified.
7. `make benchmark` CI gate: specified in blueprint CI YAML; no Makefile target
   evidence in archived dumps.
8. Multi-agent Phase 2 (5 agents, Redis Streams): planned Q3'26, superseded by
   Omega fleet architecture — close as superseded, do not resurrect.

Pattern: hooks-and-specs were repeatedly written ahead of execution; Phase 2
prep flags were aspirational. Verify-by-artifact before trusting any legacy
"achieved" column lacking a log/report file.

---
**Status**: COMPLETE — roc_racoon, 2026-08-21
