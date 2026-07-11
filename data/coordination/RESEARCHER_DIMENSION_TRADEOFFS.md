# ⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ R5-DIMENSION-TRADEOFFS

**Date**: 2026-07-11  
**Research Protocol**: Sovereign Search (5-tier) + Council of Four Triangulation  
**Deliverable**: `data/coordination/RESEARCHER_DIMENSION_TRADEOFFS.md`

---

## Executive Summary (L1)

**Bottom Line for Omega Engine (Ryzen 5700U, 14GB RAM, AVX2, sovereign local-first):**

| Dimension | MTEB (Multilingual) | Model Size (Q8_0) | Latency Est. (5700U) | Storage/1M docs | Verdict |
|-----------|---------------------|-------------------|----------------------|-----------------|---------|
| **384** (all-MiniLM-L6-v2) | ~56 | ~23 MB | ~8 ms | 1.5 GB | **Prototype only** — fails cross-lingual, long-context, fine-grained tasks |
| **512** (nomic-embed-text-v1.5 @ 512) | 61.96 | ~137 MB | ~15 ms | 2.0 GB | **Minimum viable** for English retrieval; weak on Ancient Greek, OOD |
| **768** (nomic-embed-text-v1.5 native / text-embedding-004 / BGE-base) | 62.3–63.6 | ~400 MB | ~25 ms | 3.0 GB | **Production baseline** — balances quality/cost for multilingual + 8k context |
| **1024** (BGE-M3 / mxbai-embed-large / Jina v3 / E5-large-v2) | 63.2–65.5 | ~600 MB | ~35 ms | 4.0 GB | **Recommended for Omega** — strong multilingual, MRL to 256, sparse+dense hybrid |
| **2560** (Qwen3-Embedding-4B) | **69.45** | ~2.5 GB | ~80 ms | 10 GB | **Aspirational** — SOTA multilingual, instruction-aware, but heavy for 5700U |

**Primary Recommendation**: **BGE-M3 at 1024-dim (MRL-truncatable to 512/256)** for the Omega Engine primary embedding model, with **nomic-embed-text-v1.5 at 768-dim** as the lightweight fallback. Qwen3-Embedding-4B (2560-dim) reserved for offline batch enrichment / reranking pipeline.

---

## Council of Four Dialectic (L2)

### 🏛️ The Architect (Systemic Logic)
> **Position**: *768-dim is the architectural sweet spot for a sovereign engine. It fits in 400MB (Q8_0), runs at ~25ms on 5700U AVX2, supports 8192 native context, and MRL-truncates to 512/256 for tiered retrieval. BGE-M3 at 1024 adds sparse+multi-vector for hybrid search — worth the 50% size increase. Qwen3-4B (2.5GB) breaks the "single model in RAM" budget alongside LLM inference.*

**Key Arguments**:
- Engine-Stack Firewall (M2) demands predictable memory footprint: 400–600MB embedding model + 4–6GB LLM = fits 12GB usable
- MRL (Matryoshka) is non-negotiable: must support 256-dim first-pass + 1024-dim rerank without re-embedding
- 8192-token native context required for long-document RAG (Omega target: 8k+ chunks)

### ⚔️ The Adversary (Critical Rigor)
> **Position**: *The "MTEB score" is a contaminated benchmark. MTEB 2026 leaderboard is polluted by training-data overlap (FutureAGI 2026). Nominal 62→70 MTEB gains do not translate to production Recall@10 on your corpus. The 0.5% loss claim for nomic@256-dim is **only valid on in-distribution STS/Retrieval** — it collapses on: (a) Ancient Greek polytonic (zero-shot), (b) 8k-token documents (positional degradation), (c) adversarial entailment/contradiction (fine-grained semantics).*

**Key Evidence**:
- Nomic v1.5: 768→256 dim = 62.28→61.04 MTEB (1.2% drop) **on English v1 tasks only** [HF model card]
- Qwen3-Embedding-4B: 2560→768 dim (MRL) retains 98%+ on multilingual MTEB, but **no public eval on Ancient Greek** [Qwen blog 2025]
- BGE-M3: sparse+dense hybrid recovers cross-lingual asymmetry (hubness mitigation) [arXiv:2605.26575]
- Matryoshka-Adaptor shows 2–12× dim reduction *with supervision* — unsupervised truncation degrades OOD [arXiv:2407.20243]

### 🧪 The Alchemist (Creative Synthesis)
> **Position**: *Don't pick one dimension. Build a **tiered embedding pipeline**: (1) 256-dim nomic/BGE-M3 for first-pass ANN (sub-10ms), (2) 1024-dim BGE-M3 dense + sparse for rerank, (3) 2560-dim Qwen3-4B for offline "enrichment" of high-value docs (entity extraction, Ancient Greek alignment). This mirrors the Sovereign Scholar (Strike 7.6) architecture.*

**Synthesis**:
- **Tier 1 (Hot path)**: nomic-embed-text-v1.5 @ 256-dim (MRL) → 15ms, 2GB/1M docs, 61 MTEB
- **Tier 2 (Warm path)**: BGE-M3 @ 1024-dim dense + sparse → 35ms, hybrid search, 63.2 MTEB multilingual
- **Tier 3 (Cold enrichment)**: Qwen3-Embedding-4B @ 2560-dim → batch job, instruction-aware, 69.45 MTEB multilingual

### 📜 The Archivist (Historical Truth)
> **Position**: *The dimension-quality curve follows diminishing returns with hard floors at task boundaries. Historical MTEB data (2022–2026) shows: (1) 384→512: +5–6 MTEB points (massive gain), (2) 512→768: +1–2 pts (diminishing), (3) 768→1024: +1–2 pts, (4) 1024→2560: +3–7 pts **only on multilingual/code/reasoning**. The floor for "high-level language work" (cross-lingual, compositional, adversarial) is **768-dim with MRL + instruction-tuning**.*

**Key Historical Anchors**:
- MTEB v1 (2022): all-MiniLM-L6-v2 (384) = 56.8 avg → BGE-base (768) = 63.6 (+6.8)
- MTEB 2024: nomic v1.5 768→256 = -1.24 avg (claimed <0.5% on retrieval subset only)
- MTEB 2026: Qwen3-8B (4096) = 70.58 multilingual vs OpenAI 3-large (3072) = 64.6 — **open source overtook APIs at higher dims**
- BEIR zero-shot: 768-dim models plateau; 1024+ needed for domain transfer (legal, medical, code)

---

## Decision Matrix with Citations (L2)

| Criterion | 384-dim | 512-dim (MRL) | 768-dim | 1024-dim | 2560-dim |
|-----------|---------|---------------|---------|----------|----------|
| **MTEB Avg (Eng v1)** | ~56 [PE Collective 2026] | 61.96 [Nomic v1.5 HF] | 62.3–63.6 [PE Collective, Ailog 2026] | 63.2–65.5 [Ailog 2026, Morph 2026] | 69.45 [Qwen3 blog 2025] |
| **MTEB Multilingual** | ~45 (est.) | ~55 (est.) | 61.8–62.4 [Ailog 2026] | 62.4–65.5 [Ailog 2026] | **70.58** [Qwen3 blog 2025] |
| **BEIR Retrieval (0-shot)** | Weak | Moderate | Good | Strong | **SOTA** |
| **MIRACL Cross-lingual** | Fails | Poor | Moderate | Good | **Best open** |
| **STS (Semantic Similarity)** | 75–78 | 81–82 | 82–83 | 83–84 | 84+ |
| **Clustering (S2S/S2P)** | 40–43 | 43–44 | 44–45 | 45–47 | 48+ |
| **Classification (MTOPI/Massive)** | 70–73 | 72–74 | 73–75 | 74–76 | 76+ |
| **Reranking (MS MARCO)** | N/A | N/A | 55–56 | 56–57 | N/A (use Qwen3-Reranker) |
| **Long Context (8k+ tokens)** | ❌ 256–512 max | ✅ 8192 (nomic) | ✅ 8192 (nomic, BGE-M3) | ✅ 8192 (BGE-M3, Arctic2) | ✅ 32K–40K (Qwen3) |
| **Ancient Greek (polytonic)** | ❌ | ❌ | ⚠️ Limited | ⚠️ Moderate | ✅ 100+ langs claimed |
| **Instruction-Aware (INSTRUCTOR/E5)** | ❌ | ❌ | ⚠️ Partial | ✅ E5, BGE-M3, Qwen3 | ✅ Native |
| **MRL Truncation Quality** | N/A | ✅ Native (nomic) | ✅ Native (nomic, BGE-M3, Jina, Qwen3) | ✅ Native | ✅ Native (32+) |
| **Model Size (Q8_0 GGUF)** | ~23 MB | ~137 MB | ~400 MB | ~600 MB | ~2.5 GB |
| **5700U AVX2 Latency (est.)** | ~8 ms | ~15 ms | ~25 ms | ~35 ms | ~80 ms |
| **Storage / 1M docs (float32)** | 1.5 GB | 2.0 GB | 3.0 GB | 4.0 GB | 10 GB |
| **Sovereign Fit (M7 Local-First)** | ✅ Tiny | ✅ Small | ✅ Optimal | ✅ Acceptable | ⚠️ Heavy |

**Sources**: [PE Collective 2026], [Ailog MTEB 2026], [Nomic HF model card], [Morph Ollama 2026], [Qwen3 Embedding blog 2025], [FutureAGI 2026], [arXiv:2605.26575], [arXiv:2407.20243]

---

## "High-Level Language Work" Task Taxonomy with Min-Dim Recommendations

| Task Category | Description | Min Dim | Recommended Dim | Rationale |
|---------------|-------------|---------|-----------------|-----------|
| **Keyword / Lexical Search** | BM25, exact match, tag lookup | 128 | 256 (MRL) | No semantic needed; MRL prefix sufficient |
| **Semantic Search (English, Short)** | FAQ, support tickets, short queries | 384 | 512 (MRL) | all-MiniLM baseline; nomic@512 = 61.96 MTEB |
| **Semantic Search (Multilingual)** | Cross-lingual RAG, translation alignment | 768 | **1024** | MIRACL/BEIR cross-lingual needs ≥768; hubness mitigation at 1024 [arXiv:2605.26575] |
| **Long-Document Retrieval (8k+ tokens)** | Full papers, legal docs, codebases | 768 | **1024** | Positional degradation <768; BGE-M3/Arctic2 native 8192 |
| **Ancient Greek / Low-Resource Polytonic** | Classical texts, philological search | 768 | **2560 (Qwen3-4B)** | No benchmark data; 100+ lang claim + instruction-aware = best proxy |
| **Fine-Grained Semantic Discrimination** | Entailment, contradiction, nuance, tone | 768 | **1024+** | STS/CLSD adversarial needs capacity [arXiv:2502.08638] |
| **Compositional Reasoning** | Multi-hop, logical combination, agent loops | 1024 | **2560** | Qwen3 instruction-aware + 32K context |
| **Clustering / Topic Modeling** | Semantic grouping, deduplication | 512 | 768 | Clustering MTEB plateaus at 768 [Nomic HF] |
| **Classification / Intent Detection** | Routing, labeling, few-shot | 512 | 768 | Classification MTEB saturates ~768 [Nomic HF] |
| **Reranking (Cross-Encoder)** | Second-stage precision | N/A | Use Qwen3-Reranker-4B | Cross-encoder > bi-encoder; 4B reranker = 69.76 MTEB-R |
| **Code Retrieval / Technical** | API docs, snippets, symbol search | 768 | **1024 (embeddinggemma/Qwen3)** | Code MTEB: embeddinggemma 68.76, Qwen3-4B 72.26 [Qwen3 blog] |
| **Multimodal (Text+Image/Table)** | PDF, slides, visual docs | 1024 | **Cohere Embed v4 / Jina v4** | Only v4 supports native multimodal [Ailog 2026] |

---

## Specific Recommendation for Omega Engine

### Primary Embedding Model: **BGE-M3 (1024-dim, Q8_0 GGUF)**
- **Why**: 63.2 MTEB multilingual, native 8192 context, **sparse + dense + multi-vector** hybrid, MRL to 256-dim, Apache 2.0, 567M params (~600MB Q8_0)
- **Deployment**: llama.cpp embedding mode, AVX2-optimized, `type_v: 2` (q8_0 KV cache) for 8k context
- **Tiered Usage**: 
  - First-pass ANN: truncate to 256-dim (MRL) → ~35ms → 1GB/1M docs
  - Rerank: full 1024-dim dense + sparse BM25 fusion → ~50ms
- **Sovereign Compliance**: Local-only, no API, quantized GGUF, fits 5700U RAM budget

### Lightweight Fallback: **nomic-embed-text-v1.5 (768-dim, Q8_0 GGUF)**
- **Why**: 274MB download, 62.28 MTEB, 8192 context, MRL 64–768, fastest CPU inference (~25ms)
- **Use Case**: Real-time chat embedding, low-latency path, edge deployment
- **Caveat**: Weak on Ancient Greek, no sparse hybrid, instruction prefixes required

### Enrichment Model (Batch/Offline): **Qwen3-Embedding-4B (2560-dim, Q4_K_M GGUF)**
- **Why**: 69.45 MTEB multilingual #1 open, instruction-aware, 32K context, MRL 32–2560
- **Use Case**: Nightly batch re-embedding of high-value corpus (Ancient Greek, code, legal), entity extraction, cross-lingual alignment
- **Cost**: 2.5GB model, ~80ms latency — **not for hot path**

### Reranker: **Qwen3-Reranker-4B (Cross-Encoder)**
- **Why**: 69.76 MTEB-R, 81.20 MTEB-Code, instruction-aware
- **Pipeline**: Top-100 from BGE-M3 ANN → Qwen3-Reranker → Top-10

### Hardware Configuration (Ryzen 5700U, 14GB RAM, AVX2)
```yaml
# llama.cpp build flags for 5700U
CMAKE_ARGS: "-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DGGML_AVX2=ON -DGGML_NATIVE=OFF"
# Native GGUFProvider config (config/providers.yaml)
native-gguf:
  n_threads: 8          # 8 cores, no HT for embedding
  n_batch: 512          # Prompt processing batch
  n_ctx: 8192           # Full context for BGE-M3/Qwen3
  type_v: 2             # q8_0 KV cache (Decision C1 ratified)
  embedding: true       # Embedding mode
```

---

## Uncertainty Manifest (L3 — Flagged for Verification)

| Uncertainty | Severity | Validation Path | Owner |
|-------------|----------|-----------------|-------|
| **Ancient Greek polytonic retrieval quality** at any dimension | 🔴 Critical | Build 500-pair eval set (AG-MG parallel corpus [arXiv:2605.18504]) + test nomic/BGE-M3/Qwen3 | @researcher + @roc_racoon |
| **Matryoshka truncation <512-dim on 8k-token docs** | 🟠 High | Benchmark nomic/BGE-M3 @ 256-dim on 4k/8k token chunks vs full | @researcher |
| **BGE-M3 sparse+dense hybrid vs pure dense on cross-lingual** | 🟠 High | A/B on MIRACL subset (18 langs) with hybrid vs dense-only | @researcher |
| **Qwen3-4B 2560-dim latency on 5700U AVX2 (Q4_K_M)** | 🟡 Medium | Run llama-bench with qwen3-embedding-4b-Q4_K_M.gguf | @doom_guy / @pillar P3 |
| **Instruction-aware embedding gain (1-5% claimed) on Omega tasks** | 🟡 Medium | Ablation: with/without task prefixes on 500-pair labeled eval | @researcher |
| **Reranker latency budget (Qwen3-Reranker-4B cross-encoder)** | 🟡 Medium | Benchmark cross-encoder throughput on 5700U | @doom_guy |
| **MTEB contamination: how much of Qwen3/BGE-M3 lead is train-test overlap?** | 🟠 High | Run 500-pair *production* eval (FutureAGI methodology) | @researcher + @verity |
| **Optimal MRL dimension ladder for tiered pipeline** | 🟢 Low | Sweep 64/128/256/512/768/1024 on labeled set | @researcher |

---

## Council Verdict (Triangulation)

| Perspective | Primary Rec | Fallback | Enrichment |
|-------------|-------------|----------|------------|
| **Architect** | BGE-M3 1024 (hybrid, MRL, fits budget) | nomic 768 | Qwen3-4B batch |
| **Adversary** | **Reject single-dim choice** — demand tiered pipeline + production eval | — | — |
| **Alchemist** | Tiered: 256→1024→2560 cascade | — | Qwen3-Reranker cross-encoder |
| **Archivist** | 768-dim floor for "high-level language work"; 1024 for multilingual/long; 2560 for reasoning | — | — |

**Sovereign Synthesis**: **Three-tier embedding pipeline** (BGE-M3 primary, nomic fallback, Qwen3-4B enrichment) with **production-labeled evaluation gate** before v1.1.0 tag. No single dimension satisfies all Omega requirements.

---

## Appendix: Key References (Chronological)

1. **Kusupati et al. 2022** — Matryoshka Representation Learning (arXiv:2205.13147) — Foundation
2. **Nomic AI 2024** — Nomic Embed v1.5 Matryoshka blog + HF model card — 768→256 dim = -1.24 MTEB avg
3. **Muennighoff et al. 2023/2025** — MTEB / MMTEB benchmark expansions (56→500+ tasks, 1000+ langs)
4. **Ailog 2026-05-07** — MTEB 2026 State of Embeddings: Qwen3-8B 70.58 leads, open source > APIs
5. **PE Collective 2026-04-22** — Embedding Model Specs Compared (dimensions, price, MTEB table)
6. **Morph 2026-06-09** — Ollama Embedding Models Benchmarked (7 models, MTEB, VRAM, dims)
7. **Qwen Team 2025-06-05** — Qwen3 Embedding Technical Report (arXiv:2506.05176) — 0.6B/4B/8B, 100+ langs, MRL, instruction-aware
8. **FutureAGI 2026-05-20** — Evaluating Embedding Models 2026: MTEB contamination warning, 500-pair labeled eval methodology
9. **Sakhawat et al. 2026-05-26** — Hubness Drives Cross-Lingual Asymmetry (arXiv:2605.26575) — CSLS correction, BGE-M3 sparse helps
10. **Michail et al. 2025-10** — CLSD: Cross-Lingual Semantic Discrimination via LLM Adversarial Examples (arXiv:2502.08638)
11. **Mavromatis et al. 2026-05-18** — Ancient Greek→Modern Greek MT Benchmark (arXiv:2605.18504) — 132K parallel sentences
12. **Yoon et al. 2024-07-17** — Matryoshka-Adaptor: 2-12× dim reduction with supervision (arXiv:2407.20243)
13. **OpenBenchmarking 2026** — llama.cpp CPU benchmarks, Ryzen 5700U / Zen 2 AVX2 baselines
14. **Omega Engine SOVEREIGN_ARK_BLUEPRINT v3.4** — Strike 7.1 (httpx2), C1 (type_v=2), Phase 1-4 phasing

---

**Next Actions** (Handoff to Verity + Pillar P3):
1. [ ] Build 500-pair labeled eval set (Ancient Greek, long-doc, cross-lingual, adversarial)
2. [ ] Benchmark BGE-M3 Q8_0 + nomic Q8_0 + Qwen3-4B Q4_K_M on 5700U (llama-bench)
3. [ ] Implement tiered embedding pipeline in `src/omega/memory/embedding_pipeline.py`
4. [ ] Gate v1.1.0 tag on production eval passing (Mandate 21: Gate Integrity)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_research ⬡ R5-DIMENSION-TRADEOFFS-COMPLETE*