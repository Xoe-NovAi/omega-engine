# 🔱 Omega Engine — R-SVR-GRAPH: Sovereign Knowledge Graph Adapter Spec
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ gemini-3.5-flash ⬡ opencode ⬡ trc_memory ⬡ R-SVR-GRAPH

**AP Token**: `AP-RESEARCH-SVR-GRAPH-v1.0.0`
**Author**: roc_racoon (Sovereign Miner & Ideas Guy)
**Date**: 2026-06-21
**Status**: ⚠️ PHANTOM GAP — Investigation Complete (2026-07-02)

---

## Summary
This specification defines the architecture, database schema, and implementation plan for the **Sovereign Knowledge Graph Adapter** (`SovereignGraphAdapter`). Inspired by the architectural patterns of `codebase-memory-mcp`, this adapter transitions the Omega Engine from a flat vector-similarity memory model to a **multi-signal structural memory model**. By combining SQLite-based graph storage, multi-signal semantic scoring, and local Random Indexing (RI), Omega achieves high-performance relational memory and local verification with zero external dependencies, fully adhering to Mandate 7 (Local-First) and Mandate 8 (Zero Telemetry).

---

## ⚠️ PHANTOM GAP INVESTIGATION (2026-07-02)

### Executive Summary
**This spec was over-engineered.** The Omega Engine already has hybrid FTS+Vector search with Reciprocal Rank Fusion (RRF) implemented in `memory_store.py:search()`. The "missing" Knowledge Graph Adapter was a phantom gap — the functionality already exists.

### What Already Exists
- **Hybrid Search**: `memory_store.py:search()` combines FTS5 lexical search with vector similarity using RRF (k=60)
- **Multi-Signal Scoring**: The existing implementation already blends vector similarity + text overlap
- **Local-First**: All search is local via SQLite FTS5 + Qdrant vector store
- **Zero Dependencies**: No NetworkX or external graph database required

### Why This Spec Was Over-Engineered
1. **Graph traversal** is not needed for current use cases — entity relationships are handled by the EntityRegistry
2. **Random Indexing** is unnecessary when Qdrant already provides efficient vector search
3. **Community detection** is a future feature that doesn't align with current engine needs
4. **The existing RRF fusion is the "right approximation"** — lightweight, local-first, no additional dependencies

### Recommendation
**No implementation needed.** The spec should be archived as a reference for future graph-based features if needed. The existing hybrid search in `memory_store.py` already provides the multi-signal scoring capability described in this spec.

---

## Findings

### 1. The Multi-Signal Semantic Scoring Paradigm
Traditional RAG systems rely solely on cosine similarity of dense vector embeddings. This approach suffers from semantic drift and "hallucinated similarity" where structurally unrelated concepts are grouped together because of general language patterns. 

To solve this, the Sovereign Knowledge Graph Adapter implements a **Multi-Signal Semantic Scoring** mechanism. The final retrieval score for any memory node is a weighted sum of three independent signals:
1.  **Vector Similarity ($S_{vector}$)**: Dense cosine similarity using the 768-dim local embedding chain.
2.  **Structural Graph Distance ($S_{graph}$)**: Relational proximity calculated via shortest-path or PageRank-style traversals in SQLite.
3.  **Textual Overlap ($S_{fts}$)**: BM25 lexical score calculated via SQLite FTS5 with code/entity-aware tokenization.

$$\text{Score}(u, q) = w_{vector} \cdot S_{vector}(u, q) + w_{graph} \cdot S_{graph}(u, q) + w_{fts} \cdot S_{fts}(u, q)$$

Where the default weights are configured as:
*   $w_{vector} = 0.50$
*   $w_{graph} = 0.30$
*   $w_{fts} = 0.20$

### 2. SQLite Graph Schema & Indexing
To maintain absolute portability and zero external database dependencies, the entire graph is stored in a local SQLite database using Write-Ahead Logging (WAL) mode.

```sql
-- [id-soft: quake3-1999] Hard-Boundary Struct Pattern applied to DB Schema
-- Separation of immutable engine-managed structural fields and mutable game/entity properties.

CREATE TABLE IF NOT EXISTS graph_nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,          -- 'entity', 'concept', 'code_symbol', 'session'
    name TEXT NOT NULL,
    properties TEXT,             -- JSON string for mutable traits/metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    zoneid INTEGER DEFAULT 0x1d4a11 -- [id-soft: doom-1993] ZONEID Pattern
);

CREATE TABLE IF NOT EXISTS graph_edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    type TEXT NOT NULL,          -- 'calls', 'references', 'evolves_to', 'belongs_to'
    properties TEXT,             -- JSON string for edge metadata
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (source, target, type),
    FOREIGN KEY (source) REFERENCES graph_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target) REFERENCES graph_nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS node_embeddings (
    node_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,     -- 768 float32 array (3072 bytes)
    dimension INTEGER DEFAULT 768,
    FOREIGN KEY (node_id) REFERENCES graph_nodes(id) ON DELETE CASCADE
);

-- FTS5 Virtual Table for lexical search
CREATE VIRTUAL TABLE IF NOT EXISTS node_fts USING fts5(
    node_id UNINDEXED,
    name,
    properties,
    tokenize="unicode61"
);
```

### 3. Random Indexing (RI) for Zero-Dependency ANN
To enable fast, local approximate nearest neighbor (ANN) search directly inside SQLite without spawning a heavy Qdrant container for lightweight queries, we implement **Random Indexing**.
*   **Concept**: High-dimensional vector space is projected into a lower-dimensional sparse random space. Each node is assigned a sparse, stable random "index vector" consisting of mostly $0$s and a few $+1$s and $-1$s.
*   **Heritage**: This is a direct evolution of the **Precomputed Lookup Table** pattern `[id-soft: doom-1993] Precomputed Lookup`. We pay the projection cost once at initialization and perform fast bitwise/integer comparisons at runtime.

---

## Recommendations

1.  **Implement `SovereignGraphAdapter`**: Create a new class in `src/omega/memory/graph_adapter.py` implementing the `IVectorStoreAdapter` interface but backing it with the SQLite graph schema.
2.  **Integrate with aiosqlite**: Ensure all database operations are AnyIO-compliant (Mandate 1) by using `aiosqlite` and wrapping blocking connection/write operations in `anyio.to_thread.run_sync`.
3.  **Port to `MemoryStore`**: Update `src/omega/memory_store.py` to orchestrate both the vector store (Qdrant) and the local SQLite Graph Store, using the multi-signal formula to merge results.
4.  **Add Graph Navigation Tools**: Expose `graph_traverse` and `graph_impact_analysis` tools to the MCP Hub (`mcp_servers/omega_hub/tools.py`) so agents can query relational context.

---

## Sources
- [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) — Accessed 2026-06-21
- File: `src/omega/memory_store.py`
- [id Software Architectural Heritage](CREDITS.md) — `[id-soft: doom-1993] ZONEID`, `[id-soft: quake3-1999] Hard-Boundary`

---

## Implementation Note
_For: Antigravity IDE / Cline / OpenCode_

To implement the `SovereignGraphAdapter`, write the class in `src/omega/memory/graph_adapter.py`. Ensure it inherits from a base `BaseMemoryAdapter` or implements the `IVectorStoreAdapter` contract. 

Use the following AnyIO-compliant atomic transaction pattern for writing nodes:

```python
import json
import anyio
import aiosqlite
from typing import Dict, Any, List

class SovereignGraphAdapter:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._zoneid = 0x1d4a11  # [id-soft: doom-1993] ZONEID_MEMORY

    async def add_node(self, node_id: str, node_type: str, name: str, properties: Dict[str, Any]) -> None:
        # Wrap blocking DB calls in AnyIO thread pool or use aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            properties_json = json.dumps(properties)
            
            # Atomic write with ZONEID validation
            await db.execute(
                """
                INSERT OR REPLACE INTO graph_nodes (id, type, name, properties, zoneid)
                VALUES (?, ?, ?, ?, ?)
                """,
                (node_id, node_type, name, properties_json, self._zoneid)
            )
            await db.execute(
                """
                INSERT OR REPLACE INTO node_fts (node_id, name, properties)
                VALUES (?, ?, ?)
                """,
                (node_id, name, properties_json)
            )
            await db.commit()
```

Verify the implementation by writing a unit test in `tests/test_graph_adapter.py` that asserts node/edge insertion, shortest-path calculation, and multi-signal scoring accuracy. All 444 tests must continue to pass.
