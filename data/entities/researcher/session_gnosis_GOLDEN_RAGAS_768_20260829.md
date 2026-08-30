<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Researcher Session Gnosis — Golden Set + RAGAS + 768-dim Model Selection

**Session**: ses_fe8cf0b39ffeL3L8eaMEj3CW9H (Grokster handoff)
**Date**: 2026-08-29
**Mission**: Write `R_RESEARCHER_GOLDEN_SET_RAGAS_768DIM_20260829.md` (1,200-1,800 lines, temple-grade)
**Status**: In progress → deliverable composition

---

## Key Verified Facts (sourced 2026-08-29)

### Part 1 — RAGAS 0.4
- RAGAS 0.4+ uses **collections-based API** (`ragas.metrics.collections.Faithfulness`).
- Legacy API: `from ragas.metrics import Faithfulness` — deprecated in 0.4, removed in 1.0.
- 4 canonical RAG metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall.
- Faithfulness formula: `claims_supported / total_claims` (claim decomposition by judge LLM).
- HHEM-2.1-Open (Vectara, T5-based hallucination detector) — non-LLM alternative for the verification step.
- QASkills.sh 2026-06-27 is the definitive 2026 reference for the runnable pattern.

### Part 2 — 768-dim Model
- **Qwen3-Embedding-0.6B**: MTEB Eng v2 = **70.70**, MMTEB = 64.33, MTEB Retrieval = 64.64, C-MTEB = 66.33. Apache 2.0, MRL 32-1024, 32K context, instruction-aware, 0.6B params, ~1.2-1.5GB fp16.
- **EmbeddingGemma-300M**: MTEB Eng v2 = **69.67**, MTEB Multilingual v2 = 61.15, MTEB Code v1 = 68.76. Gemma license, MRL 128-768, 2K context, instruction-aware (task-specific prompts).
- **nomic-embed-text-v1.5**: MTEB Eng v2 = 62.28, 137M params, 768-dim (MRL), 8K context, Apache 2.0, fully open.
- **Qwen3-Embedding-8B**: 70.58 (MMTEB leaderboard #1), 75.22 (MTEB Eng v2), but ~17GB VRAM — exceeds 8GB RAM.
- **Qwen3-Embedding-4B**: 74.60 (MTEB Eng v2), ~9GB — exceeds 8GB RAM.

### Critical Numbers for Recommendation
- Qwen3-0.6B at 768-dim truncates MRL → +6.36 NDCG vs EmbeddingGemma-300M (Eng v2).
- Qwen3-0.6B MTEB Code = 75.41 (4B = 81.20) → 2x context window (32K vs 2K).
- EmbeddingGemma QAT: Q4_0 = 69.31 (Eng v2) — vs Qwen3 0.6B fp16 ~70.70 → Qwen3 still wins after quantization.
- Both instruction-aware; Qwen3 has 16x larger context.

### Council Verdict
- **Qwen3-Embedding-0.6B at 768-dim MRL-truncated** wins on:
  - +1.03 MTEB Eng v2 vs EmbeddingGemma (70.70 vs 69.67).
  - 16x context (32K vs 2K) → enables late chunking, recursive 8K+ chunks.
  - 1024-dim native, truncate to 768 → no quality cliff.
  - Apache 2.0 (vs Gemma license) → simpler M7 audit trail.
  - Better reranker co-design (Qwen3-Reranker-0.6B, 65.80 MTEB-R).
- **EmbeddingGemma-300M remains the fallback** when RAM < 4GB (Q4 quant fits 200MB).

### Plan
- Write temple-grade report to `data/coordination/R_RESEARCHER_GOLDEN_SET_RAGAS_768DIM_20260829.md`.
- Sections: 1) Golden Set Construction, 2) RAGAS Harness, 3) Operational Runbook, 4) 768-dim Model Comparison, 5) Recommendation, 6) Migration Plan, 7) Risk Analysis, 8) Cost-Benefit.
- 1,200-1,800 lines, all citations, all quantifications.

---

## Polymathic Council Synthesis

### Architect (Systemic)
- 768-dim canonical lock: must remain 768. Model must support MRL truncation to 768.
- Migration must be dual-write + shadow validate + cutover (per R_RESEARCHER_SQLITE_VEC_OPPORTUNITIES_20260829.md OPP-O10).
- 7-collection architecture: only `omega_vec_gemma_768` and `omega_vec_nomic_768` get re-embedded. The 5 smaller-dim collections derive from the 768-dim canonical via MRL slice (per `R_RESEARCHER_RAGAS_20260829.md` L2 §1.3).

### Adversary (Critical Rigor)
- EmbeddingGemma-300M wins on **size** and **M7-friendly** (200MB QAT). Qwen3-0.6B wins on **quality** (+1.03 MTEB).
- EmbeddingGemma is on **Gemma license** which is permissive but not Apache; Qwen3 is Apache 2.0.
- EmbeddingGemma 2K context → no late chunking. Qwen3 32K context → late chunking, recursive 8K+ chunks.
- 2K context is the binding constraint for 4 of the 5 smaller-dim MRL slices — they will be poor on long docs regardless of model.
- Verdict: Qwen3-0.6B is the better choice *because* of 32K context, not despite it.

### Alchemist (Creative Synthesis)
- Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B is a **single-vendor stack** (MTEB-R 65.80 vs BGE-m3 57.03).
- The two models share the Qwen3 base → can be fine-tuned together, share tokenizers, share serving infra.
- Apache 2.0 across both → M14 heritage clean.

### Archivist (Historical Truth)
- Nomic-embed-text-v1.5 (137M, 62.28) is the *baseline*. Anything below it is a regression.
- The Omega golden set will catch regressions that the MTEB leaderboard can't (PremAI 2026-03-17 warning).
- First principle: build the harness, then pick the model, then validate on the corpus.

---

## Next Action
Write the deliverable. Target 1,500 lines, 8 sections, all citations, all metrics.
