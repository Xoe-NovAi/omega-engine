# 🔱 Tri-Store Implementation Blueprint
**⬡ OMEGA ⬡ ARCHITECT ⬡ trc_impl_tri_store ⬡ BLUEPRINT**

## 1. Data Model

### 1.1 Concept Graph (SQLite-backed Adjacency List)
To maintain sovereignty and portability, the graph is implemented via a optimized SQLite schema.

```sql
-- Concept Nodes
CREATE TABLE concepts (
    id TEXT PRIMARY KEY,           -- UUID or Canonical Name
    gnosis_id TEXT,                -- Link to Gnosis Tree node
    label TEXT NOT NULL,           -- Human-readable concept
    description TEXT,              -- Brief summary
    activation_value REAL DEFAULT 0, -- For runtime SA
    last_activated TIMESTAMP
);

-- Semantic Resonances (Edges)
CREATE TABLE resonances (
    source_id TEXT,
    target_id TEXT,
    resonance_type TEXT,           -- e.g., 'EVOLVES_FROM', 'CONTRADICTS'
    weight REAL CHECK(weight >= 0 AND weight <= 1),
    last_verified TIMESTAMP,
    PRIMARY KEY (source_id, target_id, resonance_type),
    FOREIGN KEY(source_id) REFERENCES concepts(id),
    FOREIGN KEY(target_id) REFERENCES concepts(id)
);
```

### 1.2 Gnosis Tree (Poincaré Embeddings)
The hierarchy is stored as a set of coordinates in the Poincaré disk.

```python
@dataclass
class GnosisNode:
    id: str
    level: int  # 1, 2, or 3
    coords: np.ndarray  # 2D coordinate in the Poincaré disk (x, y)
    summary: str
    children: list[str]
```

### 1.3 Leaf Store (Qdrant Metadata)
Qdrant points are augmented with a `concept_id` to link them to the graph.

```json
{
  "id": "uuid",
  "vector": [0.1, 0.2, ...],
  "payload": {
    "concept_id": "concept_uuid",
    "level": 1,
    "text": "Raw narrative content...",
    "source": "session_id"
  }
}
```

---

## 2. API Contracts: `SovereignMemoryStore`

### 2.1 Spatial Query Interface
```python
class SovereignMemoryStore:
    async def spatial_query(self, query: str, depth: int = 2, lambda_factor: float = 0.8) -> SpatialResultSet:
        """
        Executes the descending-resolution pipeline:
        Gnosis Tree -> Concept Graph -> Leaf Store.
        """
        # 1. Gnosis Anchoring (Poincaré Search)
        anchor_nodes = await self.gnosis_tree.find_closest(query)
        
        # 2. Associative Expansion (Spreading Activation)
        activated_concepts = await self.concept_graph.spread_activation(
            seeds=anchor_nodes, 
            depth=depth, 
            damping=lambda_factor
        )
        
        # 3. Factual Hydration (Vector Retrieval)
        narratives = await self.leaf_store.get_by_concepts(activated_concepts)
        
        return SpatialResultSet(
            hierarchy=anchor_nodes,
            neighborhood=activated_concepts,
            evidence=narratives
        )
```

### 2.2 Gnosis Ingestion Interface
```python
    async def ingest_gnosis(self, l1_text: str, soul_context: Soul):
        """
        Distills L1 -> L2 -> L3 and updates the Tri-Store.
        """
        # 1. Generate L2/L3 summaries via SoulDistiller
        distillation = await soul_distiller.distill(l1_text, soul_context)
        
        # 2. Update Gnosis Tree (Hyperbolic placement)
        await self.gnosis_tree.insert(distillation.l3, distillation.l2)
        
        # 3. Update Concept Graph (Identify resonances)
        resonances = await self.analyze_resonances(distillation.l2)
        await self.concept_graph.add_resonances(resonances)
        
        # 4. Store in Leaf Store
        await self.leaf_store.insert(l1_text, distillation.concept_id)
```

---

## 3. Integration Map (Hot/Warm/Cold Tiers)

The Tri-Store overlays the existing tiers as follows:

| Tier | Tri-Store Component | Storage Backend | Latency | Role |
|------|---------------------|------------------|---------|------|
| **Spirit** | Gnosis Tree | InMemory / YAML | <1ms | Global structural anchor |
| **Warm** | Concept Graph | SQLite / Redis | 1-10ms | Associative neighborhood |
| **Cold** | Leaf Store | Qdrant / Disk | 10-100ms | High-fidelity evidence |

---

## 4. Computational Constraints
- **SA Complexity**: $O(V + E)$ per traversal, where $V$ is activated nodes and $E$ is their edges.
- **Poincaré Distance**: $d(u, v) = \text{acosh}(1 + 2\frac{\|u-v\|^2}{(1-\|u\|^2)(1-\|v\|^2)})$. Computed via NumPy.
- **Damping**: Activation $A_{t+1}(v) = \sum_{u \in N(v)} A_t(u) \cdot W(u, v) \cdot \lambda$.
