# Reference: Selective Hydration

> Qdrant-backed L3 gnosis retrieval — how distilled principles flow from Qdrant into the context window.

---

## Overview

Selective Hydration retrieves L3 (Universal) principles from Qdrant by cosine similarity and injects them into the ContextBuilder's context window. This provides relevant distilled wisdom for every query without manual retrieval.

**Heritage**: `[id-soft: doom-1993] BSP Culling` — O(1) culling of irrelevant principles, similar to how BSP trees cull half the geometry with a single plane equation.

---

## Architecture

```
Query
    │
    ▼
┌─────────────────────────────────────────┐
│  EmbeddingManager                       │
│  - Embed query via SovereignFallback    │
│  - GemmaGGUF → Ollama → Local → Static  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  IVectorStoreAdapter (Qdrant)           │
│  - Search l3_gnosis_{entity}            │
│  - Cosine similarity                    │
│  - Filter: confidence >= 0.5            │
│  - Top-K (default K=5)                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  L3Principle objects                    │
│  - Sorted by similarity descending      │
│  - Formatted for context injection      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ContextBuilder                         │
│  - Injects gnosis_block between         │
│    world_block and memory_block         │
│  - Auto-called on every query           │
└─────────────────────────────────────────┘
```

---

## L3Principle

**File**: `src/omega/oracle/selective_hydration.py`

The atomic unit of distilled gnosis.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `principle_id` | `str` | Auto-generated SHA-256[:24] of `entity_name:content` |
| `entity_name` | `str` | Entity namespace isolation |
| `content` | `str` | The L3 principle text |
| `domain` | `str` | Classification tag (default: "general") |
| `confidence` | `float` | 0.0-1.0 validated score |
| `source` | `str` | Provenance metadata (session ID, vet record) |
| `created_at` | `str` | ISO timestamp |
| `category` | `str` | L3 classification (default: "universal_principle") |
| `similarity` | `float` | Cosine similarity to query (populated at retrieval) |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_payload()` | `Dict` | Serialize for Qdrant storage |
| `from_payload(payload, similarity)` | `L3Principle` | Deserialize from Qdrant |
| `format()` | `str` | Format for context injection |

---

## SelectiveHydration

**File**: `src/omega/oracle/selective_hydration.py`

### Constructor

```python
SelectiveHydration(
    embedding_manager: EmbeddingManager,
    vector_adapter: IVectorStoreAdapter,
    top_k: int = 5,
    min_confidence: float = 0.5,
    collection_prefix: str = "l3_gnosis_",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `embedding_manager` | `EmbeddingManager` | — | Embedding chain (SovereignFallback) |
| `vector_adapter` | `IVectorStoreAdapter` | — | Qdrant or InMemory adapter |
| `top_k` | `int` | `5` | Number of principles to retrieve |
| `min_confidence` | `float` | `0.5` | Minimum confidence threshold |
| `collection_prefix` | `str` | `"l3_gnosis_"` | Qdrant collection prefix |

### Methods

#### `hydrate(query: str, entity_name: str) -> List[L3Principle]`

Retrieves top-K L3 principles similar to the query.

```python
hydration = SelectiveHydration(embedding_manager, vector_adapter)
principles = await hydration.hydrate(
    query="How do I optimize provider health?",
    entity_name="kali"
)

for p in principles:
    print(f"[{p.similarity:.2f}] {p.content}")
```

**Pipeline**:
1. Embed query via EmbeddingManager chain
2. Search vector adapter filtered by entity_name
3. Filter by confidence threshold (>= min_confidence)
4. Deserialize to L3Principle objects
5. Sort by similarity descending, return top-K

**Returns**: `List[L3Principle]` — empty if no principles found or embedding fails.

#### `store(principle: L3Principle) -> str`

Stores an L3 principle in Qdrant.

```python
from omega.oracle.selective_hydration import L3Principle

principle = L3Principle(
    entity_name="kali",
    content="The right approximation is better than the exact solution you can't afford.",
    domain="engineering",
    confidence=0.95,
    source="session_42_distillation",
)

principle_id = await hydration.store(principle)
print(f"Stored: {principle_id}")
```

**Returns**: `str` — the principle ID.

#### `get_all(entity_name: str) -> List[L3Principle]`

Retrieves all L3 principles for an entity.

```python
all_principles = await hydration.get_all(entity_name="kali")
print(f"Total principles: {len(all_principles)}")
```

#### `remove(principle_id: str, entity_name: str) -> bool`

Removes an L3 principle from Qdrant.

```python
removed = await hydration.remove(principle_id, entity_name="kali")
```

#### `format_principles_block(principles: List[L3Principle]) -> str` *(static)*

Formats principles for context injection.

```python
block = SelectiveHydration.format_principles_block(principles)
print(block)
# Output:
# ## Distilled Wisdom (L3)
# - [0.92] "The right approximation..." (engineering)
# - [0.87] "Cross-entity coordination..." (governance)
```

---

## Write Permission Protocol

**Agent writes to `proposed_lessons.yaml`, NOT to Qdrant directly.**

The flow:
1. Agent distills L1→L2→L3 during a session
2. Agent writes L3 principles to `proposed_lessons.yaml` (blind staging)
3. User reviews and approves
4. Approved principles are stored in Qdrant via `store()`

This separation ensures the user maintains sovereignty over what enters the knowledge base.

---

## Entity Namespace Isolation

Each entity's L3 principles are stored under `l3_gnosis_{entity_name}` Qdrant collection. No cross-entity contamination.

```
Qdrant Collections:
├── l3_gnosis_kali
├── l3_gnosis_maat
├── l3_gnosis_lilith
├── l3_gnosis_researcher
└── ...
```

---

## Embedding Provider Chain

Query embedding uses the existing SovereignFallback chain:

| Priority | Provider | Type |
|----------|----------|------|
| 0 | GemmaGGUF | Local |
| 1 | Ollama | Local |
| 2 | LocalGGUF | Local |
| 3 | Static fallback | Hash-based (test only) |

In test mode (`OMEGA_ENV=test`), zero vectors are accepted as valid test data.

---

## Heritage

| Pattern | Source | Omega Adaptation |
|---------|--------|------------------|
| BSP Culling | id Software (Doom, 1993) | O(1) similarity threshold culling |
| Precomputed Lookup | id Software (Doom, 1993) | Embeddings precomputed at store time |
| 4-Tier Memory | id Software (Quake, 1996) | L3 principles live in the Cache tier |
