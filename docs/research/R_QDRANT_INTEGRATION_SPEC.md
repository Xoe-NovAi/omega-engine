# 🔱 R-QDRANT: Qdrant Vector Integration Specification (Option B)

**AP Token**: `AP-QDRANT-SPEC-v1.0.0`
**Status**: APPROVED | **Version**: 1.0.0
**Author**: DeepSeek V4 (Overseer)
**Date**: 2026-05-23

---

## §1 Executive Summary

This specification outlines **Option B** for resolving the architectural discrepancy identified in Fleet Review 3 (`C-MEM-003`). The current "vector search" implementation is a lightweight, in-memory bag-of-words TF-frequency index stored in `vectors.json`. While functional for local testing, it lacks semantic neural embeddings and approximate nearest-neighbor scaling.

To align the codebase with our canonical architecture documentation, we will integrate a true local **Qdrant** vector database running in the `omega-infra` pod on port `6333`, using the version-locked `qdrant-client==1.17.1`.

---

## §2 Current State vs. Target Architecture

```
CURRENT STATE (Bag-of-Words)
Document Curated → Tokenize → TF-Frequency Vector → Cosine Similarity (Linear Scan) → vectors.json

TARGET ARCHITECTURE (Qdrant Option B)
Document Curated → Local Embedding Model (Fastembed) → Dense Vector (384-dim) 
                 → Qdrant Client (Async) → Qdrant DB (:6333) → HNSW Index (Fast Search)
```

### 1. The Qdrant Infrastructure
*   **Container**: `omega-qdrant` running rootless inside the `omega-infra` pod.
*   **Port**: `6333` (HTTP API) / `6334` (gRPC API).
*   **Storage**: Persistent volume mounted at `/media/arcana-novai/omega_library/podman-storage/qdrant_data/`.
*   **Client**: `qdrant-client==1.17.1` (strict version-lock).

### 2. Local Embedding Generation
To maintain **Zero Telemetry** and **Local-First Sovereignty**, embeddings must be generated locally on the Ryzen 5700U CPU.
*   **Library**: `fastembed` (by Qdrant) or `sentence-transformers` running via ONNX Runtime.
*   **Model**: `BAAI/bge-small-en-v1.5` (384-dim, highly optimized for CPU inference, ~100MB footprint).
*   **Hardware Tuning**: Thread pool limited to 4 threads to prevent interference with the main inference loop.

---

## §3 Implementation Specification

### 1. AnyIO-Compliant Async Client
The `qdrant-client` library provides an `AsyncQdrantClient` which natively supports async operations. All database calls must use this client to maintain **AnyIO Absolute** compliance.

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantVectorIndex:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection_name = "omega_library"

    async def initialize(self):
        """Ensure the collection exists with correct parameters."""
        exists = await self.client.collection_exists(self.collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # BGE-small-en-v1.5 dimension
                    distance=Distance.COSINE
                )
            )
```

### 2. Document Indexing Pipeline
When a document is curated, it must be embedded and upserted to Qdrant.

```python
async def index_document(self, doc_id: str, text: str, metadata: dict):
    # 1. Generate embedding locally (offloaded to thread pool to prevent blocking)
    embedding = await anyio.to_thread.run_sync(self._generate_embedding, text)
    
    # 2. Upsert to Qdrant
    await self.client.upsert(
        collection_name=self.collection_name,
        points=[
            PointStruct(
                id=doc_id,
                vector=embedding,
                payload=metadata
            )
        ]
    )
```

### 3. Hybrid Search Scoring Correction (`C-MEM-013`)
To combine SQLite FTS5 BM25 ranks (negative, closer to 0 is better) with Qdrant cosine similarity scores (positive, 0 to 1, higher is better), we must negate the FTS5 rank before linear combination:

$$\text{Score}_{\text{hybrid}} = -\text{Rank}_{\text{FTS5}} + (\text{Score}_{\text{Qdrant}} \times 10)$$

```python
# Re-ranking logic in Indexer.hybrid_search
combined.sort(
    key=lambda r: -r.get("_fts_score", 0) + r.get("_vec_score", 0) * 10,
    reverse=True,
)
```

---

## §4 Migration & Rollout Plan

1.  **Step 1: Dependency Update**: Add `qdrant-client==1.17.1` and `fastembed` to the project dependencies.
2.  **Step 2: Indexer Refactor**: Replace the bag-of-words logic in `src/omega/library/indexer.py` with the `QdrantVectorIndex` implementation.
3.  **Step 3: Database Migration**: Write a migration script (`scripts/migrate_vectors.py`) that reads existing documents from `data/library/documents/`, generates dense embeddings, and upserts them to Qdrant.
4.  **Step 4: Verification**: Run the `omega-infra` pod, execute the migration, and verify search latency and accuracy via `make test`.

---

*Guard the memory. Elevate the search.*
