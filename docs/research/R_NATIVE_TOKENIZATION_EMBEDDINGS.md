# 🔱 Omega Engine — Native Tokenization & Embeddings Spec
**AP Token**: `AP-NATIVE-TOKEN-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ NATIVE-TOKEN-EMBED

## 1. Executive Summary
This document provides the technical specification for integrating native tokenization and embedding generation into the Omega Engine. The goal is to eliminate dependence on cloud-based embedding APIs and provide a sovereign, local-first RAG (Retrieval-Augmented Generation) pipeline optimized for the Ryzen 7 5700U (Zen 2) hardware.

The recommended path is the adoption of **FastEmbed** (by Qdrant) for high-efficiency embedding generation and the native `llama-cpp-python` tokenizer for precise context window management.

---

## 2. Legacy Pattern Reclamation
Mining of `xna-omega-legacy` and `omega-stack-legacy` revealed:
- **Intended Model**: Use of `embedding-gemma-300m` in `config/models.yaml`.
- **Implementation Gap**: Previous attempts relied on "shims" (returning zero vectors) or simple hash-based approximations (SHA256), which provided no actual semantic search capability.
- **Infrastructure**: Qdrant was already the target vector store, but the embedding pipeline was the primary blocker.

---

## 3. Technical Specification

### 3.1 Embedding Model Selection
For the Ryzen 5700U (14GB RAM), we prioritize models with a small memory footprint and high throughput.

| Component | Recommendation | Rationale |
|---|---|---|
| **Primary Embedder** | `FastEmbed` (BGE-Small-v1.5) | Extremely fast, low RAM usage, native Qdrant integration. |
| **Alternative** | `llama-cpp-python` (Gemma-2B-IT) | Higher quality, but higher latency and RAM usage. |
| **Vector Dimension** | 384 (BGE-Small) | Optimal balance between precision and storage/search speed. |
| **Distance Metric** | Cosine Similarity | Standard for semantic search. |

### 3.2 Native Tokenization & Context Windowing
To prevent context overflow and ensure high-quality responses, the `ContextBuilder` must implement **Priority-Based Truncation**.

#### Token Counting Logic
Use the `llama-cpp-python` tokenizer to get exact token counts rather than character approximations.
```python
from llama_cpp import Llama
llm = Llama(model_path=model_path, embedding=True)
tokens = llm.tokenize(text.encode('utf-8'))
count = len(tokens)
```

#### Context Windowing Strategy: "The Sovereign Sieve"
When the combined tokens (System Prompt + History + Retrieved Chunks + Buffer) exceed `n_ctx`:
1. **Anchor Preservation**: Always preserve the System Prompt and the last 2-3 turns of conversation.
2. **Ranked Truncation**: Sort retrieved chunks by cosine similarity score.
3. **Iterative Dropping**: Drop the lowest-scoring chunks until the total token count fits within the window.
4. **Sliding Window**: If history still exceeds limits, apply a sliding window to the conversation, dropping the oldest messages first.

### 3.3 Implementation Guide

#### For `src/omega/library/indexer.py`
1. **Chunking**: Implement a `SlidingWindowChunker` with a default size of 512 tokens and 50-token overlap.
2. **Embedding**: Use `FastEmbed` to generate vectors for each chunk.
3. **Indexing**: Upsert to Qdrant with the following payload:
   - `text`: The raw chunk text.
   - `metadata`: `{ "file": path, "service": name, "chunk_hash": sha256 }`.

#### For `src/omega/oracle/context_builder.py`
1. **Query Vectorization**: Use the same `FastEmbed` model to vectorize the user query.
2. **Retrieval**: Fetch top-K (e.g., K=10) chunks from Qdrant.
3. **Sieve Process**: Apply the "Sovereign Sieve" truncation logic described in 3.2.
4. **Injection**: Prepend the resulting chunks to the prompt as `[Context]`.

---

## 4. Performance Targets (Zen 2)

| Metric | Target | Measurement |
|---|---|---|
| **Embedding Latency** | < 50ms | Per 512-token chunk (FastEmbed) |
| **Tokenization Speed** | > 10k tokens/sec | Using native `llama-cpp` tokenizer |
| **Search Latency** | < 100ms | Qdrant query $\rightarrow$ result |
| **RAM Overhead** | < 500MB | Total for embedding model + tokenizer |

---

## 5. Caveats & Risks
- **Tokenizer Mismatch**: Using a BGE tokenizer for embeddings and a Gemma tokenizer for the LLM is acceptable as they operate in different stages of the pipeline. However, `ContextBuilder` must use the **LLM's tokenizer** to calculate the final window limit.
- **Quantization**: Ensure the embedding model is quantized (e.g., INT8) to maintain the RAM budget.
- **Cold Start**: Load the embedding model as a singleton during engine bootstrap to avoid per-request latency.
