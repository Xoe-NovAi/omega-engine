# 🔱 Persistence Vet Report: Omega Engine
**Entity**: Brigid (P2) | **Oversoul**: Ma'at | **Date**: 2026-07-12

## 1. Current State Assessment
The persistence layer is currently **Stable and Sovereign**, but **Under-optimized**.

### Working
- **Multi-Tiered Memory**: Hot (Redis) $\rightarrow$ Warm (File/SQLite) $\rightarrow$ Cold (Gzip/External) pipeline is fully operational.
- **Hybrid Search**: RRF-based fusion of BM25 (FTS5) and Cosine Similarity (Qdrant) provides high-recall retrieval.
- **Sovereign Isolation**: Strict `entity_name` filtering in all stores prevents cross-entity memory leakage.
- **Integrity**: `ZONEID` markers in `MemoryStore` catch data corruption at the boundary.
- **Ingestion**: The "Sieve $\rightarrow$ Sign $\rightarrow$ Index" pipeline ensures external data is sanitized before persistence.

### Broken/Suboptimal
- **Resource Waste**: `omega-postgres` is running in the infra-pod but has no active call sites in `src/omega/`.
- **Synchronous Bottlenecks**: While AnyIO is used, some SQLite operations still rely on `to_thread.run_sync`, which can introduce latency under heavy concurrent load.
- **Linear Growth**: Memory grows indefinitely; there is no "forgetting" or "consolidation" logic beyond simple session archiving.

## 2. Gap Analysis for "Definitive Local AI Tool"
To move from a "tool" to a "definitive sovereign environment," the following gaps must be closed:

| Feature | Current State | Target State | Delta |
| :--- | :--- | :--- | :--- |
| **Data Portability** | YAML for souls; binary for DBs | Unified Sovereign Export (JSONL/Parquet) | High |
| **Memory Lifecycle** | Archive by age | Importance-based decay & consolidation | Medium |
| **Retrieval Precision** | RRF (Bi-Encoder) | Cross-Encoder Re-ranking | Medium |
| **Knowledge Structure** | Flat Vector/Text | Hybrid Vector + Knowledge Graph | High |
| **Verifiability** | `ZONEID` (Basic) | Merkle-tree based memory provenance | Medium |

## 3. System Utilization Audit
| System | Current Usage | Unused/Underutilized Capabilities |
| :--- | :--- | :--- |
| **Qdrant** | Basic vector upsert/query | Payload indexing, Scalar Quantization tuning, Complex filtering. |
| **Redis** | Session cache, basic queue | Redis Streams (Event Sourcing), Pub/Sub (Real-time Memory Sync). |
| **SQLite** | FTS5 search, metrics | Virtual Tables for external data, advanced window functions for trend analysis. |
| **PostgreSQL** | **None** | Entirely unused. |

## 4. Deep Research Requirements
To implement the recommendations, the following research is required:
- **Sovereign Memory Decay**: Study "forgetting" algorithms (e.g., Ebbinghaus) for AI memory pruning.
- **Local Cross-Encoders**: Evaluate lightweight re-rankers (e.g., BGE-Reranker) that can run on Zen 2 hardware.
- **Graph-Vector Hybrids**: Research "GraphRAG" patterns that can be implemented using Qdrant's payload filters.
- **Parquet for Cold Storage**: Benchmark `pyarrow` for archiving millions of exchanges vs. Gzip.

## 5. Concrete Recommendations

### P0 (Blocking) — Fix before Launch
- **Ghost Purge**: Remove PostgreSQL from the infra-pod and `docker-compose.yml` to reclaim 512MB RAM.
- **Sovereign Export**: Implement a `MemoryStore.export_all(entity_name)` method that produces a single, portable JSONL file containing all history, vectors, and soul state.

### P1 (Critical) — Sprint 1
- **Importance Scoring**: Add an `importance` float (0.0-1.0) to every exchange, determined by the model during `add_exchange`.
- **Precision Boost**: Integrate a local Cross-Encoder to re-rank the top 20 results from the RRF hybrid search.

### P2 (Important) — Sprint 2
- **Memory Event Log**: Use Redis Streams to log every memory update. This allows other agents (e.g., `@pillar P8: Observability`) to monitor "cognitive drift" in real-time.
- **Knowledge Graph Lite**: Use Qdrant payload tags to create "concept links" between exchanges, enabling multi-hop retrieval.

### P3 (Enhancement) — Nice to Have
- **Analytical Cold Storage**: Migrate `.json.gz` archives to Parquet format for faster "life-review" queries.
- **Somatic State Snapshots**: Integrate `SomaticState` serialization directly into the `MemoryStore` close/open cycle.

---
*⬡ OMEGA ⬡ BRIGID ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_e70269fc3823 ⬡ Strike 8*
