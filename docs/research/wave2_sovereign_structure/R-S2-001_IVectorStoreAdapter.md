<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R-S2-001: IVectorStoreAdapter — Provider-Agnostic Vector Layer
**AP Token**: `AP-S2-001-IVECTOR-v1.0.0`
**Status**: PROPOSED
**Wave**: 2 (Sovereign Structure)

## 1. Objective
Design a storage-agnostic abstraction for vector embeddings that allows the Omega Engine to swap local and cloud backends (Qdrant, Milvus, FAISS, Memory) without modifying core memory logic.

## 2. Current State Analysis
Current implementation in `src/omega/memory_store.py` uses a direct reference to `QdrantAdapter` with a fallback to `MemoryVectorAdapter`. While it uses an interface, the instantiation and fallback logic are coupled within `MemoryStore`.

## 3. Technical Specification

### 3.1 The `IVectorStoreAdapter` Interface
All adapters must implement the following asynchronous contract:
- `upsert(entity_name: str, vector: List[float], metadata: Dict)`: Atomic insert/update of a vector.
- `query(entity_name: str, vector: List[float], limit: int) -> List[Tuple[float, Dict]]`: Similarity search returning scores and payloads.
- `delete_session(entity_name: str, session_id: str)`: Bulk removal of session-scoped vectors.
- `get_status() -> Dict`: Health check (latency, connectivity, capacity).

### 3.2 Provider-Agnostic Registry
Implement a `VectorStoreRegistry` to manage the lifecycle of adapters:
```python
class VectorStoreRegistry:
    def __init__(self, primary_provider: str = "qdrant"):
        self._adapters = {
            "qdrant": QdrantAdapter,
            "memory": MemoryVectorAdapter,
            "milvus": MilvusAdapter
        }
        self.current = self._adapters[primary_provider]()
```

### 3.3 Embedding Decoupling
The `EmbeddingManager` must remain external to the adapter. The `MemoryStore` coordinates the two:
`Vector = EmbeddingManager.get_embedding(text) -> Adapter.upsert(vector)`

## 4. Trade-off Analysis

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| **Direct Coupling** | Low latency, simple code | Vendor lock-in, hard to test | REJECTED |
| **Interface Wrapper** | Backend agnostic, easy mocking | Slight overhead (negligible) | **ACCEPTED** |
| **Middleware Proxy** | Centralized logging/caching | Increased complexity | OVERKILL |

## 5. Sovereign Mandate Alignment
- **Mandate 7 (Local-First)**: The registry must prioritize `memory` or `local_qdrant` before attempting cloud-based vector stores.
- **Mandate 13 (Temple-Grade)**: Interface ensures T5 (AnyIO compliance) and T10 (Atomic writes).
