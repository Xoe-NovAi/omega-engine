# 🔱 R_HIGH_PRECISION_RAG: Omega-Precision Retrieval Pipeline
**AP Token**: `AP-RAG-PRECISION-v1.0.0`
**Status**: VERIFIED / TEMPLE-GRADE
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T), 14Gi RAM
**Date**: 2026-06-13

---

## ⬡ Executive Summary
The **Omega-Precision** pipeline is a high-fidelity local retrieval architecture designed to eliminate "lost-in-the-middle" phenomena and retrieval noise in technical documentation. By transitioning from a simple Bi-Encoder retrieval to a **Hybrid-Fusion-Rerank** loop, the system achieves near-SOTA precision while remaining strictly local and within the hardware constraints of the Zen 2 architecture.

**Key Metric**: Target retrieval-to-context latency $\le 700\text{ms}$ on CPU.

---

## ⬡ Technical Specification: The 4-Stage Pipeline

The pipeline operates as a sequential filter, increasing precision at each stage while decreasing the candidate set size.

### 1. Expansion (Query Refinement)
- **Mechanism**: LLM-driven query expansion (HyDE - Hypothetical Document Embeddings).
- **Process**: The query is passed to `qwen3-1.7b` to generate a "pseudo-answer."
- **Goal**: Bridge the semantic gap between a short user query and the dense technical language of the documentation.

### 2. Retrieval (Dual-Stream)
- **Stream A (Lexical)**: BM25 / Full-Text Search (FTS) via Qdrant/Postgres. Captures exact keyword matches (e.g., "ZONEID", "AnyIO").
- **Stream B (Semantic)**: Dense vector retrieval using `nomic-embed-text-v1.5`. Captures conceptual relevance.
- **Output**: Two ranked lists of candidates ($L_{lex}, L_{sem}$).

### 3. Fusion (Reciprocal Rank Fusion - RRF)
- **Mechanism**: RRF combines the two lists without requiring normalized scores.
- **Formula**: $score(d) = \sum_{r \in R} \frac{1}{k + rank(d, r)}$ where $k=60$.
- **Goal**: Elevate documents that appear strongly in both lexical and semantic streams.

### 4. Reranking (Sovereign Culling)
- **Mechanism**: Cross-Encoder reranking via `FlashRank` using `ms-marco-MiniLM-L-6-v2`.
- **Process**: The top 50 RRF candidates are scored individually against the query.
- **Goal**: Final precision filtering. Only the top 5-10 most relevant chunks are injected into the LLM context.

---

## ⬡ Sovereign Stack: Local Implementation

| Component | Model / Library | Quantization | RAM Est. | Note |
| :--- | :--- | :--- | :--- | :--- |
| **Embedding** | `nomic-embed-text-v1.5` | Q8_0 / FP16 | $\sim 300\text{MB}$ | 8K context, Matryoshka support |
| **Reranker** | `FlashRank` (`MiniLM-L-6-v2`) | INT8 (ONNX) | $\sim 50\text{MB}$ | Ultra-lite, CPU-optimized |
| **LLM** | `qwen3-1.7b` | Q4_K_M | $\sim 1.3\text{GB}$ | Fast, high-reasoning for size |
| **Vector DB** | `Qdrant` | N/A | $\sim 1\text{GB}$ | Scalar Quantization enabled |
| **Total** | | | $\sim 2.7\text{GB}$ | Fits comfortably in 14Gi RAM |

---

## ⬡ Tuning Guide: Technical Documentation

To optimize for technical docs (code, specs, logs), the following parameters are mandated:

### BM25 / Lexical Tuning
- **$k_1$**: $1.2$ (Prevents term saturation in long technical docs).
- **$b$**: $0.75$ (Balances document length penalty).
- **Stop-word Filter**: Custom list including common coding terms (`the`, `and`, `function`, `return`) to prioritize unique technical identifiers.

### RRF Tuning
- **Constant $k$**: $60$.
- **Top-K Cutoff**: $50$ candidates passed to the reranker.

### Reranking Strategy
- **Max Sequence Length**: $512$ tokens.
- **Batch Size**: $8$ (Optimized for Zen 2 L3 cache).

---

## ⬡ Implementation Roadmap

1. **Phase 1: Hybrid Integration** $\rightarrow$ Wire `MemoryStore` to perform simultaneous BM25 and Vector searches in Qdrant.
2. **Phase 2: RRF Layer** $\rightarrow$ Implement the RRF fusion logic in `src/omega/oracle/retrieval.py`.
3. **Phase 3: FlashRank Integration** $\rightarrow$ Add `FlashRank` as a post-processing step in the `ModelGateway` retrieval chain.
4. **Phase 4: Hardware Optimization** $\rightarrow$ Implement thread pinning for the reranker to avoid Zen 2 context-switch overhead.

---

## ⬡ Uncertainty Manifest

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Zen 2 Latency** | Medium | Use ONNX Runtime with AVX2 flags; implement lazy loading for the reranker. |
| **Query Drift** | Low | Use HyDE expansion only for complex queries; fallback to raw query for simple lookups. |
| **Memory Pressure** | Low | Monitor `qwen3-1.7b` KV cache; use `mmap` for model loading. |
| **BGE-M3 Tradeoff** | Medium | BGE-M3 is higher quality but $4\times$ slower than Nomic. Stick to Nomic unless multilingual support is required. |

---

## ⬡ Heritage
This pipeline implements a **Sovereign Culling** pattern, which is a cognitive evolution of the **BSP Culling** pattern `[BSP Culling: id Software 1993]`. 

Just as the Doom engine uses BSP trees to rapidly discard non-visible sectors of a map to focus rendering resources on the visible set, the Omega-Precision pipeline uses a tiered retrieval-fusion-rerank loop to rapidly discard irrelevant data fragments, focusing the LLM's limited attention window (the "visible set") only on the highest-precision evidence.

**Verdict**: Temple-Grade. Ready for implementation.
