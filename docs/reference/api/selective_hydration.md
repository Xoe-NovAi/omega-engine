# Selective Hydration API Reference

**Module**: `src/omega/oracle/selective_hydration.py`
**Status**: Production (Carmack Session)
**Tests**: `tests/test_gnosis_proxy.py` (13 tests)

## Overview

`SelectiveHydration` retrieves L3 (Universal) principles from Qdrant by cosine similarity and injects them into the ContextBuilder's context window. It uses precomputed embeddings for O(1) retrieval.

## Architecture

```
Oracle.talk() → ContextBuilder → SelectiveHydration.hydrate()
                                      ↓
                                 Qdrant (l3_gnosis_{entity})
                                      ↓
                                 Top-K L3 Principles
                                      ↓
                                 Injected into system prompt
```

## Classes

### L3Principle

```python
@dataclass
class L3Principle:
    principle_id: str        # Hash of entity_name + content
    entity_name: str         # Owning entity
    content: str             # The L3 principle text
    domain: str              # Diátaxis domain (tutorial/how_to/reference/explanation)
    confidence: float        # 0.0-1.0 from distillation pipeline
    source: str              # Session ID, vet record, etc.
    created_at: str          # ISO timestamp
    category: Optional[str]  # "general", "heritage", "technical"
    similarity: float        # Cosine similarity (populated at retrieval)
```

### SelectiveHydration

```python
class SelectiveHydration:
    def __init__(self, embedding_manager: EmbeddingManager,
                 vector_adapter: IVectorStoreAdapter)
    
    async def hydrate(self, query: str, entity_name: str,
                      top_k: int = 5, min_confidence: float = 0.5,
                      domain: Optional[str] = None) -> List[L3Principle]
    
    async def store(self, principle: L3Principle) -> str  # Returns principle_id
    
    async def list_principles(self, entity_name: str,
                              domain: Optional[str] = None) -> List[L3Principle]
    
    async def delete_principle(self, principle_id: str) -> bool
```

## Key Methods

### hydrate()

Retrieves top-K relevant L3 principles for a query.

```python
selective_hydration = SelectiveHydration(
    embedding_manager=memory_store.embedding_manager,
    vector_adapter=memory_store.vector_store,
)

principles = await selective_hydration.hydrate(
    query="How do I configure providers?",
    entity_name="kali",
    top_k=5,
    min_confidence=0.5,
    domain="how_to"
)

for p in principles:
    print(f"[{p.similarity:.2f}] {p.content[:80]}...")
```

### store()

Stores a new L3 principle with precomputed embedding.

```python
principle_id = await selective_hydration.store(L3Principle(
    entity_name="kali",
    content="Always use socks5h:// for DNS leak prevention",
    domain="how_to",
    confidence=0.9,
    source="ses_20260705_kali_1"
))
```

## Domain Taxonomy (Diátaxis)

L3 principles use the Diátaxis domain taxonomy:

| Domain | Description | Example |
|--------|-------------|---------|
| `tutorial` | Learning-oriented | "How to create an entity" |
| `how_to` | Task-oriented | "How to configure providers" |
| `reference` | Information-oriented | "Oracle API parameters" |
| `explanation` | Understanding-oriented | "Why local-first matters" |
| `cross-cutting` | Spans multiple domains | "Always use atomic writes" |

## Confidence Threshold

`MIN_CONFIDENCE = 0.5` (global default). Principles below this threshold are not retrieved. Per-entity tuning is deferred to D16-2 (Parametric Gnosis).

## Integration Points

- **ContextBuilder**: Calls `hydrate()` during context assembly
- **SoulDistiller**: Calls `store()` when distilling L3 principles
- **MemoryStore**: Provides `embedding_manager` and `vector_store`

## Heritage

`[id-soft: doom-1993] BSP Culling — O(1) culling of irrelevant principles`
`[id-soft: doom-1993] Precomputed Lookup — embeddings precomputed at store time`
`[id-soft: quake-1996] 4-Tier Memory — L3 principles live in the Cache tier`
