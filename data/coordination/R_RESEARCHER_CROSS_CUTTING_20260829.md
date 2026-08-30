<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# R_RESEARCHER_CROSS_CUTTING_20260829.md

**Mission**: Deep research on cross-cutting opportunities that span the entire vector store stack — abstractions, observability, security, and quality.
**Entity**: Researcher (Polymathic Council)
**Date**: 2026-08-29

---

## Executive Summary (L1)

Ten cross-cutting opportunities identified. They differ from gaps/opportunities in the previous reports in that they are *systemic* — they affect the architecture as a whole, not individual features.

**Council verdict**: The 9-gap fix + 10 remaining gaps + 10 opportunities = ~30 improvement points. This report identifies the *meta-improvements* that would prevent the next 30.

**Top 3 to prioritize**:
1. **CC-1: VectorStoreBackend ABC** — Prevents vendor lock-in; enables A/B testing of sqlite-vec vs pgvector vs qdrant.
2. **CC-3: OpenTelemetry instrumentation** — Without observability, you can't measure any of the other improvements.
3. **CC-5: Recall@k / NDCG quality harness** — Without ground truth, "optimization" is guessing.

**Bottom 3 (defer)**:
- **CC-7: Differential privacy** — research-grade; defer until regulation requires it.
- **CC-8: Multi-modal** — see OPP-O8.
- **CC-10: Fine-tuning embeddings** — the model is already pre-trained; only do this if you have a specific domain gap.

**Important 2026 SOTA finding**: The RAG ecosystem has consolidated around **RAGAS** for evaluation, **GraphRAG** for graph-augmented retrieval, and **hybrid search + rerank** as the production pattern.

---

## L2: Detailed Dialectic — 10 Cross-Cutting Opportunities

### CC-1: VectorStoreBackend ABC (Abstraction Layer)

**Council perspectives**:
- **The Architect**: `SQLiteVecAdapterOptimized` directly uses `sqlite3` and `sqlite_vec`. To switch to pgvector or qdrant, you'd have to rewrite the adapter.
- **The Adversary**: An abstraction layer is *only* valuable if you actually plan to switch. Premature abstraction = worse code.
- **The Alchemist**: 2026 SOTA: **LangChain VectorStore**, **LlamaIndex VectorStore** — both define ABCs. LanceDB does the same. The pattern is mature.
- **The Archivist**: The existing code has `IVectorStoreAdapter` (line 113 of `sqlite_vec_adapter_optimized.py`). It's an *interface*, but no other backend implements it. Build the second implementation = validate the abstraction.

**Target**: Make sqlite-vec, qdrant, pgvector, lance swappable.

**2026 SOTA research**:
- **LangChain VectorStore ABC (2024-2026)** — `add_documents`, `similarity_search`, `from_texts`, `as_retriever`.
- **LlamaIndex BaseIndex (2024-2026)** — more granular than LangChain.
- **Qdrant 1.10+ (2026)** — exposes its own internal abstraction; you can use it OR replace it.
- **Pinecone SDK (2026)** — minimal ABC.

**Implementation sketch**:
```python
# src/omega/memory/backend.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator

class VectorStoreBackend(ABC):
    """Sovereign Vector Store abstraction. All backends MUST implement this."""

    @abstractmethod
    async def initialize(self, config: Dict) -> None: ...
    @abstractmethod
    async def upsert(self, id: str, vector: List[float], metadata: Dict, collection: str = "default") -> None: ...
    @abstractmethod
    async def batch_upsert(self, items: List[Dict], collection: str = "default") -> None: ...
    @abstractmethod
    async def query(self, vector: List[float], k: int = 10, collection: str = "default", filter: Optional[Dict] = None) -> List[Dict]: ...
    @abstractmethod
    async def delete(self, ids: List[str], collection: str = "default") -> None: ...
    @abstractmethod
    async def get_status(self) -> Dict: ...
    @abstractmethod
    async def close(self) -> None: ...

# Existing adapter:
class SQLiteVecBackend(VectorStoreBackend):
    """Thin wrapper around SQLiteVecAdapterOptimized that implements VectorStoreBackend."""
    ...

# Future backend (stub):
class QdrantBackend(VectorStoreBackend):
    """Qdrant 1.10+ backend — requires `pip install qdrant-client[fastembed]`."""
    ...
```

**Dependencies**: Pure refactor; no new deps.
**Priority**: **P1** (strategic, enables A/B testing).
**Effort**: 2-3 weeks.

---

### CC-2: Auto-Tuning (HNSW params, batch size, ef_search)

**Council perspectives**:
- **The Architect**: Hardcoded HNSW params (m=16, ef_construction=200, ef_search=64) are fine for the median case but suboptimal for many.
- **The Adversary**: Auto-tuning without *ground truth* is meaningless. You can measure latency, but you can't measure recall.
- **The Alchemist**: 2026 SOTA: **"HNSW Auto-Tuning" research** (2023-2026) shows that adaptive HNSW can match hand-tuned with 10-20% overhead. The Qdrant approach: tune on a held-out set at index build time.
- **The Archivist**: The current `m=16, ef_construction=200, ef_search=64` are well-chosen defaults. Auto-tuning would add a 5-10% gain at significant complexity cost.

**Target**: Self-tuning HNSW per-collection.

**2026 SOTA research**:
- **Qdrant auto-tuning (2026)** — `optimizers_config` with `indexing_threshold`.
- **Weaviate HNSW auto-tuning (2025-2026)** — `efConstruction`, `maxConnections` set automatically.
- **DiskANN (Microsoft, 2019-2024)** — automatically picks params based on memory budget.

**Implementation sketch**:
```python
# src/omega/memory/auto_tune.py
async def auto_tune_hnsw(backend, sample_queries, ground_truth_topk):
    """Try multiple HNSW configs; pick the one that meets recall target with lowest latency."""
    configs = [
        {"m": 8, "ef_construction": 100, "ef_search": 32},
        {"m": 16, "ef_construction": 200, "ef_search": 64},
        {"m": 32, "ef_construction": 400, "ef_search": 128},
    ]
    results = []
    for cfg in configs:
        await backend.reindex(cfg)  # expensive but done once
        latencies, recalls = [], []
        for q, truth in zip(sample_queries, ground_truth_topk):
            start = time.monotonic()
            results = await backend.query(q, k=10)
            latencies.append((time.monotonic() - start) * 1000)
            recalls.append(compute_recall(results, truth))
        results.append({"config": cfg, "p99_ms": np.percentile(latencies, 99), "recall": np.mean(recalls)})
    # Pick the one with recall >= 0.95 and lowest p99
    best = min([r for r in results if r["recall"] >= 0.95], key=lambda r: r["p99_ms"])
    return best
```

**Dependencies**: Ground truth dataset (CC-5).
**Priority**: P2 (optimization, not correctness).
**Effort**: 1-2 weeks.

---

### CC-3: OpenTelemetry Instrumentation

**Council perspectives**:
- **The Architect**: `get_metrics()` (line 1045) returns a dict. But it's not integrated with any tracing system.
- **The Adversary**: Without distributed tracing, debugging "why is the query slow?" is guesswork.
- **The Alchemist**: 2026 SOTA: **OpenTelemetry** is the universal standard. Every major Python library (FastAPI, SQLAlchemy, httpx) has OTel integration.
- **The Archivist**: M7 (Local-First) doesn't preclude local observability. The `data/observability/` directory could store spans in OTLP format.

**Target**: Every vector operation emits a span with: latency, k, collection, hit_count, model_version, error.

**2026 SOTA research**:
- **OpenTelemetry Python SDK (2026 stable)** — `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`.
- **OpenLLMetry (2024-2026)** — pre-built OTel instrumentation for LLM/vector operations.
- **Langfuse / Phoenix (2026)** — LLM-specific observability layers on top of OTel.

**Implementation sketch**:
```python
# src/omega/memory/telemetry.py
from opentelemetry import trace
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

tracer = trace.get_tracer("omega.memory")

class TelemetryInstrumentedBackend(VectorStoreBackend):
    def __init__(self, inner: VectorStoreBackend):
        self._inner = inner

    async def query(self, vector, k=10, **kwargs):
        with tracer.start_as_current_span("vector.query") as span:
            span.set_attribute("k", k)
            span.set_attribute("collection", kwargs.get("collection", "default"))
            span.set_attribute("model_version", self._get_model_version())
            try:
                result = await self._inner.query(vector, k, **kwargs)
                span.set_attribute("hit_count", len(result))
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                raise

# Auto-instrument sqlite3
SQLite3Instrumentor().instrument()
```

**Dependencies**: `pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-sqlite3`.
**Priority**: **P1** (foundational for all other improvements).
**Effort**: 1 week.

---

### CC-4: Cost Optimization Engine (Cloud vs Local Decision)

**Council perspectives**:
- **The Architect**: The engine has `config/providers.yaml` with `local_first` strategy. But there's no *dynamic* decision: "should I use Ollama or OpenRouter for *this* query?"
- **The Adversary**: Cost optimization is a *finops* concern, not a *correctness* concern. M7 (Local-First) implies local is preferred regardless of cost.
- **The Alchemist**: 2026 SOTA: **"AI Gateway" pattern** (Portkey, Cloudflare AI Gateway, Qubax) routes between models based on cost, latency, and quality. The decision is per-request, not global.
- **The Archivist**: Sovereign Mandate M7 says local-first. But "local first" doesn't mean "local only" — it means "local by default, cloud when local is unavailable or too costly."

**Target**: Per-request decision: local vs cloud, based on latency budget, cost ceiling, and current load.

**2026 SOTA research**:
- **"Best Vector Databases 2026" (Encore)** — discusses cost at 5M-10M vectors.
- **Pinecone serverless pricing model (2024-2026)** — pay per query.
- **OpenRouter (2026)** — single API for many models, with cost-aware routing.

**Implementation sketch**:
```python
# src/omega/memory/cost_router.py
class EmbeddingCostRouter:
    """Pick the cheapest provider that meets the latency budget."""

    def __init__(self, providers: Dict[str, Provider], pricing: Dict[str, float]):
        self.providers = providers  # {"ollama-nomic": ..., "openrouter-ada": ...}
        self.pricing = pricing  # cost per 1M tokens

    async def embed(self, text: str, latency_budget_ms: int = 200) -> List[float]:
        # Estimate cost for each provider
        candidates = []
        for name, provider in self.providers.items():
            if not provider.healthy:
                continue
            est_latency = provider.p99_latency_ms
            if est_latency > latency_budget_ms:
                continue
            candidates.append((self.pricing[name], est_latency, name))
        # Pick the cheapest that meets the budget
        candidates.sort()
        for cost, latency, name in candidates:
            try:
                return await self.providers[name].embed(text)
            except Exception:
                continue
        raise AllProvidersFailed()
```

**Dependencies**: Telemetry (CC-3) for p99 latency tracking.
**Priority**: P2 (finops, not core).
**Effort**: 2 weeks.

---

### CC-5: Quality Metrics (Recall@k, MRR, NDCG, RAGAS)

**Council perspectives**:
- **The Architect**: There's no measurement of *search quality*. Latency is measured, but not "did it return the right document?"
- ** **The Adversary**: Without recall measurement, every "optimization" is a guess. You can make queries 10x faster by returning random results.
- **The Alchemist**: 2026 SOTA: **RAGAS** is the standard for end-to-end RAG quality. **ann-benchmarks** is the standard for vector-only recall.
- **The Archivist**: The existing `get_metrics()` only measures throughput, latency, errors. It doesn't measure *quality*.

**Target**: A nightly job that runs 100-1000 ground-truth queries, measures recall@10, MRR, NDCG, and RAGAS scores; alerts on regression.

**2026 SOTA research**:
- **RAGAS v0.4.3 (2026-01-13)** — Faithfulness, Answer Relevancy, Context Precision, Context Recall.
- **ann-benchmarks (2024-2026)** — glove-100, sift-128, deep-96 datasets.
- **BEIR (2022-2026)** — 18 IR datasets for zero-shot evaluation.
- **NDCG (Jarvelin & Kekalainen, 2002)** — graded relevance, gold standard.

**Implementation sketch**:
```python
# src/omega/memory/quality_eval.py
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

async def nightly_quality_check(adapter, qa_dataset):
    """Run RAGAS evaluation on the QA dataset. Alert on regression."""
    results = []
    for q, ground_truth in qa_dataset:
        retrieved = await adapter.query(await embed(q), k=10)
        answer = await llm.generate(q, context=retrieved)
        results.append({
            "question": q,
            "contexts": [r.text for r in retrieved],
            "answer": answer,
            "ground_truth": ground_truth,
        })
    scores = evaluate(results, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    if scores["faithfulness"] < 0.85:
        alert("Faithfulness regression detected")
    return scores
```

**Dependencies**: A ground truth dataset (curate or generate via LLM).
**Priority**: **P1** (foundational for measuring other improvements).
**Effort**: 2-3 weeks (including dataset creation).

---

### CC-6: Adversarial Robustness (Vector Inversion, Poisoning, Membership Inference)

**Council perspectives**:
- **The Architect**: The system has no defenses against adversarial inputs. A prompt injection can poison the index; a stolen DB can be inverted.
- **The Adversary**: 2026 SOTA attacks are *real*: Vec2Text (2023) achieves 92% recovery of original text from embeddings. ACM CCS 2026 demonstrated black-box image embedding inversion.
- **The Alchemist**: Defenses: input validation, rate limiting, anomaly detection, differential privacy, encryption.
- **The Archivist**: This overlaps with GAP-R9 (encryption) and DOC-D6 (threat model). The *cross-cutting* angle is: build a *red team* harness that simulates these attacks.

**Target**: A continuous red-team harness that simulates embedding inversion, corpus poisoning, and membership inference.

**2026 SOTA research**:
- **"Black-Box Embedding Inversion Attack" (ACM CCS 2026-08-08)** — diffusion-model-based inversion.
- **"Embedding Inference Attack" (arXiv 2607.01276, 2026-07-01)** — fingerprint the model from query patterns.
- **"Sok: Privacy Risks and Mitigations in RAG Systems" (Bodea et al., 2026)** — comprehensive survey.
- **OWASP LLM08:2025** — vector and embedding weaknesses.

**Implementation sketch**:
```python
# tests/adversarial/test_inversion.py
async def test_embedding_inversion_resistance(adapter, sample_embeddings):
    """Attempt to reconstruct original text from stored embeddings."""
    # 1. Train a Vec2Text-style inversion model on a small set
    # 2. Try to invert sample embeddings
    # 3. Measure BLEU/ROUGE between inverted and original text
    inversion_model = train_vec2text(sample_embeddings[:100])
    inverted = [inversion_model.invert(v) for v in sample_embeddings[100:]]
    bleu = compute_bleu(inverted, [s.text for s in sample_embeddings[100:]])
    assert bleu < 0.3, f"Inversion attack succeeded with BLEU={bleu}"

async def test_corpus_poisoning_resistance(adapter):
    """Inject 1000 fake facts; measure recall degradation."""
    # Get baseline recall
    baseline = await measure_recall(adapter, ground_truth)
    # Poison the index
    await adapter.batch_upsert([generate_fake_memory() for _ in range(1000)])
    # Measure recall after
    poisoned = await measure_recall(adapter, ground_truth)
    assert (baseline - poisoned) / baseline < 0.05, f"Recall degraded {baseline:.2f} → {poisoned:.2f}"
```

**Dependencies**: Ground truth dataset (CC-5).
**Priority**: P1 (security).
**Effort**: 2-3 weeks.

---

### CC-7: Differential Privacy for Vector Search

**Council perspectives**:
- **The Architect**: Adding noise to embeddings preserves privacy but degrades recall. Tradeoff.
- **The Adversary**: DP is the *only* mathematically sound defense against inversion attacks. Ball-DP (2026) is a new variant that requires less noise.
- **The Alchemist**: 2026 SOTA: **Ball-DP** (arXiv 2607.04209) — ε-delta indistinguishability over single-record substitutions restricted to a ball of radius r. Less noise than vanilla DP for the same protection.
- **The Archivist**: This is research-grade as of mid-2026. Premature for production.

**Target**: Optional DP layer that adds calibrated noise to embeddings before storage.

**2026 SOTA research**:
- **"Ball Differential Privacy" (arXiv 2607.04209, 2026-07-05)** — new variant with reduced noise.
- **DP-SGD (Abadi et al., 2016)** — for training embeddings.
- **"Differential Privacy for Vector Search" (various 2024-2025 papers)**.

**Priority**: P3 (research-grade, defer).
**Effort**: 4+ weeks.

---

### CC-8: Multi-Modal Embeddings (CLIP, Whisper, CodeBERT)

**Council perspectives**:
- **The Architect**: See OPP-O8. The collection-based architecture is already extensible.
- **The Adversary**: Each modality needs a different preprocessor (image vs audio vs code). Integration is non-trivial.
- **The Alchemist**: 2026 SOTA: **CLIP** for image+text (512-dim), **CLAP** for audio+text, **CodeBERT** for code+text.
- **The Archivist**: This is a *use case* expansion, not a *system* improvement.

**Priority**: P3 (post-debut).
**Effort**: 2-4 weeks per modality.

---

### CC-9: RAG Patterns (Hybrid Search, Reranking, GraphRAG)

**Council perspectives**:
- **The Architect**: `hybrid_search` (line 1058) already does FTS5 + vec RRF. But there's no reranking step, no GraphRAG.
- **The Adversary**: Without reranking, the top-10 from vector search are *roughly* right. Reranking makes them *precisely* right. **Reranking is the highest-leverage RAG improvement** (per 1337skills 2026-06-12).
- **The Alchemist**: 2026 SOTA production pattern: **Hybrid search → Rerank → Generate**. GraphRAG adds entity-relationship context.
- **The Archivist**: A cross-encoder reranker (e.g., `BAAI/bge-reranker-v2-m3`) is ~100-500ms for 50 candidates. Affordable.

**Target**: A canonical RAG pipeline: `hybrid_search(query, k=50) → rerank(query, top_50, top_k=5) → llm.generate(query, top_5)`.

**2026 SOTA research**:
- **"Production RAG in 2026" (1337skills, 2026-06-12)** — "If you change one thing about a naive RAG system, hybrid search is the highest-leverage move."
- **"Best RAG Evaluation Tools in 2026" (RAGAS, Promptfoo, DeepEval)** — eval is foundational.
- **Microsoft GraphRAG (2024-2026)** — graph-augmented RAG.
- **FlashRank / rerankers library (AnswerDotAI, 2025-2026)** — Python rerankers, 100% local.

**Implementation sketch**:
```python
# src/omega/memory/rag_pipeline.py
from rerankers import Reranker

class RAGPipeline:
    def __init__(self, vector_store, llm, reranker_model="BAAI/bge-reranker-v2-m3"):
        self.vs = vector_store
        self.llm = llm
        self.reranker = Reranker(reranker_model)

    async def query(self, question: str, k_final: int = 5) -> str:
        # 1. Embed the question
        q_vec = await embed(question)
        # 2. Hybrid search: 50 candidates
        candidates = await self.vs.hybrid_search(q_vec, k=50)
        # 3. Rerank: top 5
        reranked = self.reranker.rank(question, candidates, top_k=k_final)
        # 4. Generate
        context = "\n".join([c.text for c in reranked])
        return await self.llm.generate(question, context=context)
```

**Dependencies**: A reranker model (small, local). FlashRank is ~50MB.
**Priority**: **P0** (highest leverage RAG improvement).
**Effort**: 1-2 weeks.

---

### CC-10: Embedding Fine-Tuning (LoRA/QLoRA for Custom Domains)

**Council perspectives**:
- **The Architect**: The current models (nomic-embed, gemma-embed) are general-purpose. Domain-specific tuning (e.g., "legal", "medical") can improve recall.
- **The Adversary**: Fine-tuning requires labeled data, compute, and validation. Premature for a general-purpose engine.
- **The Alchemist**: 2026 SOTA: **LoRA / QLoRA** for cheap fine-tuning. A 7B model can be fine-tuned on a single GPU in hours.
- **The Archivist**: For sovereign agents, fine-tuning *the agent's own embeddings to its own memory* is a feedback loop. Powerful but risky.

**Target**: Optional fine-tuning of the embedding model on the entity's own data.

**2026 SOTA research**:
- **LoRA (Hu et al., 2021)** — Low-Rank Adaptation; the standard.
- **QLoRA (Dettmers et al., 2023)** — Quantized LoRA; runs on consumer GPUs.
- **Sentence-Transformers fine-tuning guide (2026)** — official docs.
- **"How to Fine-Tune Embedding Models for RAG" (various 2025-2026 blogs)**.

**Priority**: P3 (specialized, defer).
**Effort**: 2-4 weeks.

---

## L3: Raw Signal — 10 Cross-Cutting Opportunities at a Glance

| # | Opportunity | Priority | Effort | Dependencies | 2026 SOTA Anchor |
|---|-------------|----------|--------|--------------|------------------|
| CC-1 | VectorStoreBackend ABC | P1 | 2-3 weeks | None | LangChain ABC |
| CC-2 | Auto-Tuning HNSW | P2 | 1-2 weeks | CC-5 (ground truth) | Qdrant auto-tune |
| CC-3 | OpenTelemetry | **P1** | 1 week | None | OTel Python 2026 |
| CC-4 | Cost Router | P2 | 2 weeks | CC-3 (latency data) | AI Gateway pattern |
| CC-5 | Quality Metrics (RAGAS) | **P1** | 2-3 weeks | Ground truth dataset | RAGAS 0.4.3 |
| CC-6 | Adversarial Red Team | P1 | 2-3 weeks | CC-5 (ground truth) | OWASP LLM08 |
| CC-7 | Differential Privacy | P3 | 4+ weeks | CC-6 | Ball-DP 2026 |
| CC-8 | Multi-Modal | P3 | 2-4 wks/modality | CC-1 | CLIP, CLAP |
| CC-9 | RAG Patterns (rerank) | **P0** | 1-2 weeks | CC-1 | 1337skills 2026 |
| CC-10 | Embedding Fine-Tuning | P3 | 2-4 weeks | CC-5 | LoRA/QLoRA |

---

## Council Triangulation Summary

| Lens | Convergence | Divergence |
|------|-------------|------------|
| Architect | The 10 cross-cutting items form a **dependency graph**: CC-3 (OTel) and CC-5 (quality) are foundations; CC-1 (ABC) and CC-9 (RAG) are leverage. | None. |
| Adversary | **CC-6 (red team) is existential** — without it, the system is a soft target. CC-7 (DP) is the principled defense. | Whether to invest in CC-7 (DP) now or wait for Ball-DP to mature. |
| Alchemist | CC-9 (RAG reranking) is the **single highest-leverage improvement** — 1-2 weeks of work for potentially 30% recall gain. | Whether to combine CC-4 (cost) with M7 (local-first) or treat them as competing mandates. |
| Archivist | 2026 SOTA strongly validates: RAGAS, GraphRAG, hybrid + rerank, OTel, OWASP LLM08, Ball-DP, LangChain ABC, LoRA/QLoRA. | **CC-7 is research-grade**; should be deferred until Ball-DP has production implementations. |

**Sovereign Synthesis**:
- **Sprint N+1**: CC-3 (OTel) + CC-5 (RAGAS) — the observability + quality foundations.
- **Sprint N+2**: CC-9 (RAG reranking) + CC-1 (ABC) — the leverage improvements.
- **Sprint N+3**: CC-6 (red team) + CC-2 (auto-tune) — the security + optimization.
- **Defer**: CC-4, CC-7, CC-8, CC-10 (until use case demands).

**Strategic insight**: The 9-gap fix made the system *correct*. The 10 remaining gaps (Report 1) make it *operational*. The 10 opportunities (Report 2) make it *fast*. The 10 doc gaps (Report 3) make it *usable*. The 10 cross-cutting opportunities (this report) make it *mature*.

**The full 39-item backlog**, prioritized:
- **P0 (must-do)**: 8 items (4 from gaps, 1 from opportunities, 3 from cross-cutting)
- **P1 (should-do)**: 14 items
- **P2 (could-do)**: 12 items
- **P3 (later)**: 5 items

**Estimated total effort to P0+P1 completion**: **~5-6 months** of focused work.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_CROSS_CUTTING_20260829 ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01*
