<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Hybrid Search Integration Specification
## Wiring Local Knowledge Base into the Oracle's Context Assembly Pipeline

**AP Token**: `AP-HYBRID-SEARCH-INTEGRATION-v1.0.0`
**Date**: 2026-07-04
**Author**: Sovereign Master Researcher
**Status**: SPECIFICATION (Ready for P7 Context pillar implementation)

---

## §1 Executive Summary

The Omega Engine currently has three search backends, but they operate in silos:

| Backend | What It Searches | MCP Tool | Used By Oracle? |
|---------|-----------------|----------|-----------------|
| **Conversation Memory FTS5** | User/assistant exchanges | `memory_search`, `omega_memory_search` | ⚠️ Indirectly (via MemoryStore) |
| **Library FTS5** | Curated research documents | `library_fts_search` (NEW) | ❌ NOT wired |
| **Web Search** | Internet (SearXNG, Exa, Firecrawl) | `sovereign_search` | ❌ NOT wired |

When a user asks "how does the circuit breaker work?", the Oracle routes to an LLM with conversation history injected as context. But the engine has a 252-document knowledge base covering circuit breakers, heritage patterns, provider architecture — none of it reaches the LLM.

**This spec defines how to wire all three search backends into the Oracle's context assembly, creating a unified hybrid search that gives LLMs access to the engine's full knowledge.**

---

## §2 Architecture: The Three-Backend Hybrid

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│          Oracle.talk() / summon()       │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │    ContextBuilder.build()       │    │
│  │                                 │    │
│  │  ┌───────────┐ ┌───────────┐   │    │
│  │  │ Conversation│ │ Library  │   │    │
│  │  │ Memory FTS5 │ │ FTS5     │   │    │
│  │  │ (recent)   │ │ (knowledge)│  │    │
│  │  └─────┬─────┘ └─────┬─────┘   │    │
│  │        │              │         │    │
│  │        ▼              ▼         │    │
│  │  ┌─────────────────────────┐   │    │
│  │  │   RRF Score Fusion      │   │    │
│  │  │   k=60                  │   │    │
│  │  └────────────┬────────────┘   │    │
│  │               │                │    │
│  │               ▼                │    │
│  │  ┌─────────────────────────┐   │    │
│  │  │  Token Budget Allocator │   │    │
│  │  │  (conversation: 30%)    │   │    │
│  │  │  (knowledge: 40%)       │   │    │
│  │  │  (reserve: 30%)         │   │    │
│  │  └────────────┬────────────┘   │    │
│  │               │                │    │
│  └───────────────┼────────────────┘    │
│                  │                      │
│                  ▼                      │
│         LLM System Prompt              │
│    (soul + context + knowledge)        │
└─────────────────────────────────────────┘
```

---

## §3 Integration Point: ContextBuilder

The integration point is `src/omega/oracle/context_builder.py` — the `ContextBuilder.build()` method that assembles the system prompt before LLM inference.

### Current Flow (Simplified)
```python
class ContextBuilder:
    async def build(self, entity, query, session_history) -> str:
        # 1. Load soul.yaml (entity personality)
        soul = self._load_soul(entity)
        
        # 2. Inject conversation history
        history = await self._get_history(session_history)
        
        # 3. Build system prompt
        return f"{soul}\n\n{history}"
```

### Proposed Flow
```python
class ContextBuilder:
    async def build(self, entity, query, session_history) -> str:
        # 1. Load soul.yaml
        soul = self._load_soul(entity)
        
        # 2. Search all three backends (parallel)
        conv_results, lib_results = await anyio.create_task_group(
            self._search_conversations(query, entity),
            self._search_library(query),
        )
        
        # 3. RRF fusion
        fused = self._rrf_fuse(conv_results, lib_results, k=60)
        
        # 4. Token budget allocation
        context = self._allocate_tokens(fused, budget=self.max_context_tokens)
        
        # 5. Build system prompt
        return f"{soul}\n\n{context}"
```

---

## §4 Scoring: Reciprocal Rank Fusion

### Formula
For each document $d$ appearing in ranked lists from multiple backends:

$$\text{RRF}(d) = \sum_{i=1}^{N} \frac{1}{k + \text{rank}_i(d)}$$

Where:
- $N$ = number of backends returning the document
- $k = 60$ (standard RRF constant, balances high-rank vs low-rank contributions)
- $\text{rank}_i(d)$ = position of document $d$ in backend $i$'s results (1-indexed)

### Implementation
```python
def _rrf_fuse(self, conv_results, lib_results, k=60):
    """Fuse results from conversation memory and library search."""
    scores = {}
    
    for rank, doc in enumerate(conv_results, 1):
        doc_id = doc.get("doc_id", doc.get("session_id", ""))
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    
    for rank, doc in enumerate(lib_results, 1):
        doc_id = doc.get("doc_id", "")
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    
    # Sort by RRF score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked
```

### Why RRF Over Weighted Sum
- RRF is **rank-based**, not score-based — avoids normalization issues between BM25 (0-10) and vector similarity (0-1)
- RRF naturally handles **missing backends** — if a doc only appears in one backend, it still gets a score
- RRF is the approach used by Pinecone, Weaviate, and ColBERT — battle-tested in production

---

## §5 Token Budget Allocation

The engine must fit conversation history, knowledge context, and system prompt into the LLM's context window. The budget is dynamic based on the model's context window.

### Allocation Formula
```
Total Budget = Model Context Window (e.g., 16384 tokens)

System Prompt (soul.yaml) = 10-15%    (~1500 tokens)
Conversation History      = 25-30%    (~4000 tokens)
Knowledge Context         = 35-40%    (~6000 tokens)
Reserve (safety margin)   = 15-20%    (~2500 tokens)
```

### Knowledge Context Sizing
Each knowledge document consumes tokens based on:
- **Title**: ~10 tokens
- **Summary**: ~50-100 tokens
- **Body excerpt**: ~200-500 tokens (first relevant section)

With a 16K context window:
- ~6000 tokens for knowledge = ~10-15 documents (with summaries + excerpts)
- With 252 documents in the index, RRF ranking ensures the most relevant 10-15 surface

### Budget Pressure
If total exceeds the budget:
1. Trim knowledge context first (drop lowest RRF-scored docs)
2. Then trim conversation history (keep last N turns)
3. Never trim soul.yaml (entity personality is non-negotiable)

---

## §6 Oracle Integration

### Integration in `oracle.py`

The Oracle's `talk()` and `summon()` methods call `ContextBuilder.build()` before inference. The integration point is straightforward:

```python
# In oracle.py, talk() method (simplified):
async def talk(self, query, entity_name=None):
    entity = self._resolve_entity(entity_name)
    
    # Build context WITH hybrid search
    context = await self.context_builder.build(
        entity=entity,
        query=query,  # NEW: pass query for knowledge search
        session_history=self._get_session_history(entity),
    )
    
    # Generate response
    response = await self.model_gateway.generate(
        system_prompt=context,
        user_message=query,
    )
    
    return response
```

### Key Change
Currently, `ContextBuilder.build()` does NOT receive the user query — it only gets session history. The query is needed to search the knowledge base. This is a **signature change** that affects the method's contract.

### Migration Path
1. Add `query` parameter to `ContextBuilder.build()` with default `None`
2. If `query is None`, skip knowledge search (backward compatible)
3. Update `oracle.py` to pass `query` to `ContextBuilder.build()`
4. Add `query` parameter to `ContextBuilder._search_library()` method

---

## §7 Fallback Chain

When a search backend is unavailable:

```
Library FTS5 unavailable?
    ├── Yes: Skip library search, use conversation results only
    └── No: Include library results in RRF fusion

Conversation Memory empty? (new session)
    ├── Yes: Use library results only
    └── No: Include conversation results in RRF fusion

Both unavailable?
    └── Fallback to existing behavior (soul-only context)
```

This ensures **zero regression** — the engine works exactly as before if the knowledge base is empty or unavailable.

---

## §8 Implementation Plan

### Phase A: ContextBuilder Signature Change (P7 Context pillar)
**Effort**: 1 hour
**Files**: `src/omega/oracle/context_builder.py`, `src/omega/oracle/oracle.py`

1. Add `query: Optional[str] = None` parameter to `ContextBuilder.build()`
2. Add `_search_library(query)` method that calls `Library.search()`
3. Add `_search_conversations(query, entity)` method that calls `MemoryStore.search()`
4. Add `_rrf_fuse()` method
5. Update `oracle.py` to pass `query` to `ContextBuilder.build()`
6. Write tests for `_rrf_fuse()` and `_search_library()`

### Phase B: Token Budget Allocator (P7 Context pillar)
**Effort**: 2 hours
**Files**: `src/omega/oracle/context_builder.py`

1. Implement `_allocate_tokens(fused_results, budget)` method
2. Size knowledge documents (title + summary + excerpt)
3. Implement budget pressure (trim lowest RRF docs first)
4. Write tests for token budget allocation

### Phase C: Integration Testing (P10 Validation pillar)
**Effort**: 2 hours
**Files**: `tests/test_hybrid_search_integration.py`

1. Test RRF fusion with mock search results
2. Test token budget allocation under pressure
3. Test fallback chain (library unavailable, conversation empty, both unavailable)
4. Test end-to-end: query → search → fusion → context → LLM prompt

---

## §9 Sovereignty Considerations

### M7 (Local-First) Compliance
- Library FTS5 is 100% local — no cloud dependency
- Conversation memory is 100% local
- Web search is the ONLY cloud dependency — and it's the fallback, not the primary

### M18 (Token Efficiency) Compliance
- Token budget allocation prevents context window overflow
- RRF fusion ensures only the most relevant 10-15 documents are injected
- Knowledge context is capped at 40% of total budget

### M8 (Zero Telemetry) Compliance
- All search is local — no queries leave the machine
- No analytics on search patterns

---

## §10 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Relevance** | Top-3 results contain the answer | Manual evaluation on 20 test queries |
| **Latency** | <500ms for hybrid search | Profile `ContextBuilder.build()` before/after |
| **Token overhead** | <15% increase in prompt size | Compare prompt lengths before/after |
| **Fallback reliability** | 0 regressions when library is empty | Test with empty FTS5 index |

---

## §11 Relationship to Existing Work

| Existing Component | How It Connects |
|-------------------|-----------------|
| `ConversationFTSIndex` | Provides conversation search backend |
| `Indexer.hybrid_search()` | Provides library search backend (FTS5 + vector) |
| `Library.search()` | Entry point for library search |
| `MemoryStore.search()` | Entry point for conversation search |
| `ContextBuilder` | Integration point — receives all search results |
| `ModelGateway` | Downstream — receives assembled context |
| `EphemeralWarpPool` | Unrelated — web search backend only |

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ HYBRID-SEARCH-INTEGRATION ⬡ SPEC-v1.0.0 ⬡ P7-READY*
