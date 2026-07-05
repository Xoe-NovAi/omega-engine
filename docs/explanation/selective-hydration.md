# Selective Hydration Architecture

**Module**: `src/omega/oracle/selective_hydration.py`
**Status**: Production (Carmack Session)

## Overview

Selective Hydration is the engine's gnosis retrieval system. It stores L3 (Universal) principles in Qdrant with precomputed embeddings and retrieves them by cosine similarity at query time.

## Why Selective Hydration?

The ContextBuilder has a limited token budget. Injecting all L3 principles would saturate the context window. Selective Hydration solves this by retrieving only the top-K most relevant principles for each query.

## Architecture

```
SoulDistiller
    ↓ store()
SelectiveHydration → Qdrant (l3_gnosis_{entity})
                          ↓
ContextBuilder ← hydrate() ← Query embedding
    ↓
System prompt with relevant L3 principles
```

## Design Decisions

### Precomputed Embeddings

L3 principles are embedded once at store time, not at retrieval time. This means:
- **Store time**: One forward pass through the embedding model (~30ms)
- **Retrieval time**: O(1) cosine similarity against precomputed vectors

This is the `[id-soft: doom-1993] Precomputed Lookup` pattern — pay the cost once, look up forever.

### BSP-Style Culling

The cosine similarity threshold acts as a BSP plane equation:
- Principles with similarity < `MIN_CONFIDENCE` (0.5) are culled immediately
- Only the top-K remaining principles are returned

This is the `[id-soft: doom-1993] BSP Culling` pattern — O(1) test skips entire subtrees.

### Domain Taxonomy (Diátaxis)

L3 principles use the Diátaxis domain taxonomy:
- `tutorial` — Learning-oriented
- `how_to` — Task-oriented
- `reference` — Information-oriented
- `explanation` — Understanding-oriented
- `cross-cutting` — Spans multiple domains

The domain field allows filtering at retrieval time, so a "how_to" query only retrieves "how_to" principles.

### Confidence Threshold

`MIN_CONFIDENCE = 0.5` is the global default. Principles below this threshold are not retrieved. Per-entity tuning is deferred to D16-2 (Parametric Gnosis).

### Write-Path Policy

Agents write to `proposed_lessons.yaml`. Only the user (or user-approved automation) calls `SelectiveHydration.store()`. This is the Staging Gate Protocol — prevent self-referential soul poisoning.

## Integration Points

- **ContextBuilder**: Calls `hydrate()` during context assembly
- **SoulDistiller**: Calls `store()` when distilling L3 principles
- **MemoryStore**: Provides `embedding_manager` and `vector_store`

## Performance

- **Store latency**: ~30ms (one embedding forward pass)
- **Retrieval latency**: ~5ms (Qdrant cosine similarity)
- **Token overhead**: ~100-300 tokens per query (top-5 principles)

## Heritage

`[id-soft: doom-1993] BSP Culling — O(1) culling of irrelevant principles`
`[id-soft: doom-1993] Precomputed Lookup — embeddings precomputed at store time`
`[id-soft: quake-1996] 4-Tier Memory — L3 principles live in the Cache tier`
