# 🔱 Omega Engine — H2-S Sovereign Structure Specification
**AP Token**: `AP-H2S-STRUCT-v1.0.0`
**Status**: DRAFT / ARCHITECTURAL FOUNDATION
**Governed by**: Ma'at (Light Oversoul)
**Date**: 2026-06-21

## 1. Executive Summary
Horizon 2 - Sovereign Structure (H2-S) aims to transition the Omega Engine from a specific implementation (Qdrant/Ollama) to a database-agnostic, secure, and provider-independent cognitive substrate. The goal is to ensure that the engine's "senses" (embeddings) and "memory" (vector stores) can be swapped without altering the core Oracle logic.

---

## 2. IVectorStoreAdapter Interface
To ensure database agnosticism, all vector operations must flow through a formal adapter.

### 2.1 Interface Definition
The `IVectorStoreAdapter` must be defined as an `AnyIO`-native asynchronous interface.

**Required Methods**:
- `async def upsert(entity_name: str, vector: List[float], metadata: Dict[str, Any]) -> str`: Inserts or updates a vector. Must return the unique document ID.
- `async def query(entity_name: str, vector: List[float], limit: int = 20) -> List[Tuple[float, Dict[str, Any]]]`: Returns a list of (score, metadata) tuples. Must enforce sovereign isolation via `entity_name` filtering.
- `async def delete_session(entity_name: str, session_id: str) -> int`: Deletes all vectors associated with a specific session. Returns count of deleted items.
- `async def get_status() -> Dict[str, Any]`: Returns health status (`{"status": "healthy" | "unhealthy", "error": str}`).
- `async def create_collection(name: str, dimension: int) -> None`: Initializes a new vector space.

### 2.2 Mandate Compliance
- **M1 (AnyIO)**: All methods must be `async` and use `anyio.to_thread.run_sync` for blocking driver calls.
- **M2 (Firewall)**: Adapters must live in `src/omega/memory/vector_adapters.py` and never import from WADs.

---

## 3. Tainted Data Protocol (TDP)
The TDP protects the Oracle from "cognitive poisoning" via malicious or untrusted web search payloads.

### 3.1 The Taint Pipeline
All external content must pass through the following sequential gates before entering the `MemoryStore`:

1. **Ingest Gate**: Content is wrapped in a `TaintedPayload` object.
2. **Sanitization Gate**:
    - `StripHTML`: Remove `<script>`, `<iframe>`, and style tags.
    - `LinkValidator`: Identify and neutralize high-risk redirects or known malicious domains.
    - `LengthGuard`: Enforce a hard limit on payload size (e.g., 100KB per page) to prevent OOM.
3. **Semantic Sieve**:
    - A lightweight local model (e.g., Qwen3-0.6B) scans for prompt injection patterns (e.g., "Ignore all previous instructions").
    - If detected, the payload is flagged as `HIGH_TAINT`.
4. **Provenance Marking**:
    - Add `_is_tainted: bool` and `_taint_source: str` to the metadata of the resulting memory exchange.

### 3.2 Oracle Interaction
When the Oracle retrieves context containing `_is_tainted: True`, it must enter **Skeptical Mode**:
- Increase the threshold for "truth" (require 2+ non-tainted sources for verification).
- Append a warning to the internal reasoning trace: `[SKEPTICAL: Tainted context detected from {source}]`.

---

## 4. Provider-Agnostic Embedding Layer
The embedding layer must decouple the vectorization process from the specific provider.

### 4.1 IEmbeddingProvider Interface
```python
class IEmbeddingProvider(Protocol):
    dimension: int
    model_name: str
    async def get_embedding(self, text: str) -> List[float]: ...
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]: ...
```

### 4.2 EmbeddingManager Strategy
The `EmbeddingManager` implements the **Local-First Chain (Mandate 7)**:
1. **Primary**: Native GGUF / Ollama (Local).
2. **Secondary**: LM Studio (Local).
3. **Tertiary**: Sovereign Fallback (Deterministic Feature Hashing).

**Sovereign Fallback**: A non-neural, MD5-based hashing trick that maps tokens to a fixed 256-dimensional space. This ensures that the engine can still perform basic retrieval even if all LLM backends are offline.

---

## 5. Temple-Grade Verification Gates (T-Gates)
The H2-S implementation is not "Temple-Grade" until the following gates are passed:

| Gate | Requirement | Verification Method |
|-------|-------------|-------------------|
| **T3 (Testing)** | 100% coverage of `IVectorStoreAdapter` methods. | `pytest` with mock and real Qdrant providers. |
| **T5 (AnyIO)** | Zero `import asyncio` in the memory/embedding stack. | `grep -r "import asyncio" src/omega/memory/` |
| **T6 (Telemetry)** | Zero external calls in the `SovereignFallback` provider. | Network trace audit during fallback execution. |
| **T8 (Resilience)** | Vector store timeouts trigger the `MemoryVectorAdapter` fallback. | Fault injection in `QdrantAdapter`. |
| **T10 (Integrity)** | Vector metadata updates are atomic. | Concurrent write stress test. |
| **T12 (Semantic)** | Fallback embeddings maintain >30% retrieval recall vs. Neural. | Benchmark against `SovereignFallback` vs `Ollama`. |

---

## 6. Implementation Roadmap
1. **Phase 1**: Refactor `IVectorStoreAdapter` into a formal `Protocol`.
2. **Phase 2**: Implement `TDP` in `src/omega/oracle/` as a middleware.
3. **Phase 3**: Implement `IEmbeddingProvider` and the `SovereignFallback` provider.
4. **Phase 4**: Execute T-Gate audits and finalize Temple-Grade certification.
