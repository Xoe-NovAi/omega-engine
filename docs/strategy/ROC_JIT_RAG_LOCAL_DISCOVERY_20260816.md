# 🔍 JIT RAG Local Discovery Report (Roc Racoon)
**AP Token**: `AP-ROC-JIT-RAG-DISCOVERY-20260816`
**Date**: 2026-08-16
**Status**: PARKED (DOC-1, 2026-08-17) — research preserved

> **⚠️ DOC-1 STAMP (2026-08-17)**: **PARKED.** Qdrant superseded by sqlite-vec for debut.
> Per `DEBUT_REMEDIATION_MANUAL_20260817.md`.

---

## 1. Vector Store Status

**Qdrant: Configured but NOT running as primary**
- **Primary Vector Store**: `SQLiteVecAdapter` (unified fabric) — `src/omega/memory/sqlite_vec_adapter.py`
- **Fallback**: `MemoryVectorAdapter` (in-memory stub) — `src/omega/memory/vector_adapters.py:72`
- **QdrantAdapter**: Retained as DEPRECATED heritage reference only — `vector_adapters.py:175` ("DEPRECATED: QdrantAdapter retained for heritage reference only. Use SQLiteVecAdapter for unified fabric (D225)")

**Collections (Multi-collection vec0 architecture in `omega_memory.db`):**
| Collection | Dimension | Metric | Quantization | HNSW Params |
|------------|-----------|--------|--------------|-------------|
| `omega_vec_gemma_768` | 768 | cosine | int8_rescore | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_nomic_768` | 768 | cosine | int8_rescore | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_nomic_512` | 512 | cosine | int8_rescore | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_nomic_256` | 256 | cosine | int8_rescore | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_minilm_384` | 384 | cosine | none | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_static_64` | 64 | cosine | none | m=16, ef_construction=200, ef_search=64 |
| `omega_vec_library_256` | 256 | cosine | none | m=16, ef_construction=200, ef_search=64 |

**Embedding Model**: **EmbeddingGemma 300M (768-dim)** — Primary canonical provider
- Model: `embeddinggemma-300m-Q6_K.gguf` at `/media/arcana-novai/omega_library/models/embeddings/`
- Provider: `GemmaGGUFEmbeddingProvider` → `LocalGGUFEmbeddingProvider` via llama-cpp-python
- **Canonical Dimension Lock**: 768-dim enforced at vec0 table creation (M23 Failure Integrity) — `sqlite_vec_adapter.py:280-288`
- **MRL Truncation**: Supported for fallback tiers (512, 256, 128, 64)

**Fallback Chain (EmbeddingManager):**
1. `GemmaGGUFEmbeddingProvider` (768-dim, primary) — `embeddings.py:400`
2. `OllamaEmbeddingProvider` (nomic-embed-text:v1.5, 768-dim) — `embeddings.py:401`
3. `LocalGGUFEmbeddingProvider` (MiniLM, 384-dim native → MRL to 768) — `embeddings.py:402`
4. `StaticEmbeddingProvider` (potion-base-2M, 64-dim native → MRL to 768) — `embeddings.py:403`

---

## 2. Memory Store Wiring

**MemoryStore: FULLY WIRED to Oracle**
- **Location**: `src/omega/memory_store.py` — singleton via `get_memory_store()`
- **Oracle Integration**: `oracle.py:183` — `self.memory_store = get_memory_store()`
- **Persistence**: Called from `oracle.py:699` (`_record_interaction`) → `memory_store.add_exchange()`

**Hybrid Search: FTS5 + Vector RRF WORKING**
- **FTS5 Index**: `ConversationFTSIndex` — `src/omega/memory/fts_index.py` (BM25, Porter stemmer, WAL mode)
- **Vector Search**: `SQLiteVecAdapter.query()` — `sqlite_vec_adapter.py:471`
- **RRF Fusion**: `HybridSearchEngine` — `src/omega/memory/hybrid_search.py` (k=60, Cormack et al. 2009)
- **Unified Helper**: `fetch_and_fuse()` — `hybrid_search.py:214` (concurrent FTS + Vector fetch)
- **MemoryStore.search()**: Uses `fetch_and_fuse()` at line 324-326
- **SQLiteVecAdapter.hybrid_search()**: Uses `fetch_and_fuse()` at line 794-797

**Conversation History Schema:**
- **FTS5 Table**: `exchanges` (session_id, entity_name, role, content, timestamp)
- **SQLiteVec Tables**: `omega_memory_data` (metadata) + multiple `omega_vec_*` vec0 collections
- **Entity Isolation**: Enforced via `entity_name` partition key in vec0 + WHERE clause in FTS5
- **ACP Event Stream**: JSONL `updates.jsonl` + `rewind_points.jsonl` per session — `memory_store.py:714-810`

---

## 3. DPO Dataset Readiness

**Dataset: `data/training/dpo_dataset.jsonl` — 14 pairs**
- **Format**: Standard DPO (prompt, chosen, rejected, metadata)
- **Metadata Completeness**: All 14 pairs have `active_model`, `thinking_level`, `context_usage`, `provider`, `failure_mode_tag`
- **Failure Mode Tags Coverage**:
  - `lazy_import_wrapper_misuse` (2 pairs)
  - `inline_import_hoisting` (2 pairs)
  - `type_checking_violation` (1 pair)
  - `instructional_comment_contamination` (1 pair)
  - `multi_doc_merge_hallucination` (1 pair)
  - `general_remediation` (7 pairs)

**Vectorization Status: NOT EMBEDDED**
- No evidence of DPO pairs being embedded into vector store
- `DPORecorder` writes to JSONL only (`data/training/dpo/`) — `dpo_logger.py:194-220`
- No pipeline exists to index DPO pairs into `SQLiteVecAdapter` or `ConversationFTSIndex`

**Extraction Script**: `scripts/extract_dpo_pairs.py` — extracts from markdown artifacts using regex patterns

---

## 4. Injection Points (Where JIT RAG Hooks In)

| Stage | File:Line | Description |
|-------|-----------|-------------|
| **Dispatch/Context Build** | `oracle.py:650-690` | `_prepare_system_prompt()` — builds system prompt with memory + soul context |
| **Memory Injection** | `context_builder.py:238-295` | `build_context()` — fetches MemoryStore history, L3 gnosis, world state, memory blocks |
| **L3 Gnosis Retrieval** | `selective_hydration.py:175-236` | `hydrate()` — embeds query, searches vector store, returns top-K L3 principles |
| **Context Assembly** | `context_builder.py:287-291` | Combines: world state → gnosis → memory blocks → conversation history |
| **Prompt Prepend** | `context_builder.py:553-559` | `prepend_to_prompt()` — prepends context block to entity personality |
| **Summon Path** | `oracle.py:823-958` | `_summon()` — calls `_prepare_system_prompt()`, resolves affinity, invokes ModelGateway |
| **Talk Path** | `oracle.py:426-546` | `talk()` — speculative decode → escalation → `_route_by_domain()` → `_summon()` |
| **Handoff Context** | `subagent_dispatcher.py:268-323` | `build_dispatch_prompt()` — injects task context, relevant files, heritage mandates |
| **MCP Tool** | `hub_tools/tools.py:2302-2343` | `omega_memory_search()` — exposes hybrid search to agents via MCP |

---

## 5. Gaps & Blockers

| Category | Issue | Impact |
|----------|-------|--------|
| **Missing** | **DPO Vectorization Pipeline** | DPO pairs exist but aren't searchable via RAG — no `embed_and_index_dpo()` function |
| **Missing** | **JIT RAG Trigger Logic** | No explicit "when to retrieve" policy — currently retrieves on EVERY summon/talk via `build_context()` |
| **Missing** | **Query-Aware Retrieval** | `selective_hydration.hydrate()` uses `entity_name` as query (line 313-316), not the actual user query |
| **Missing** | **Relevance Scoring for Memory Blocks** | Memory blocks (D-283 Mnemosyne) always injected — no similarity filtering |
| **Broken** | **QdrantAdapter Deprecated** | Heritage reference only — if Qdrant needed, must re-implement from scratch |
| **Config Gap** | **No JIT RAG Config** | No `config/jit_rag.yaml` — token budgets, retrieval thresholds, trigger conditions hardcoded |
| **Schema Gap** | **L3 Collection Naming** | `L3_COLLECTION_PREFIX = "l3_gnosis_"` but no evidence collections created — `selective_hydration.py:209` expects `l3_gnosis_{entity_name}` |
| **Decision Needed** | **DPO as Training vs Retrieval** | Should DPO pairs be in vector store for RAG, or only for model training? |
| **Decision Needed** | **Retrieval Granularity** | Exchange-level vs session-level vs block-level retrieval? |
| **Decision Needed** | **Cross-Entity Retrieval** | Current: strict entity isolation. Need cross-entity for council synthesis? |

---

## 6. Recommended Implementation Path

**Step 1: Immediate — Fix Query-Aware L3 Retrieval**
```python
# selective_hydration.py:hydrate() line 313-316
# CHANGE: use actual query, not entity_name
principles = await self._selective_hydration.hydrate(
    query=query,  # NOT entity_name
    entity_name=entity_name,
)
```
- **File**: `oracle.py:650-690` (`_prepare_system_prompt`)
- **Effort**: 15 min
- **Impact**: L3 principles become query-relevant

**Step 2: Next — DPO Vectorization Pipeline**
```python
# New: scripts/vectorize_dpo.py
# 1. Read data/training/dpo_dataset.jsonl
# 2. For each pair: embed prompt + chosen + rejected
# 3. Upsert to SQLiteVecAdapter with collection="omega_vec_gemma_768"
# 4. Metadata: {type: "dpo_pair", failure_mode_tag, lineage_id, reward_source}
```
- **Effort**: 2-3 hours
- **Impact**: DPO pairs become retrievable for few-shot prompting

**Step 3: After — JIT RAG Config & Trigger Policy**
```yaml
# config/jit_rag.yaml
jit_rag:
  enabled: true
  trigger:
    - on_summon: true
    - on_talk: true
    - min_query_length: 50  # chars
    - domains: ["engineering", "research", "governance"]
  retrieval:
    l3_top_k: 5
    memory_exchanges: 10
    memory_blocks: "core_only"  # or "all"
    dpo_few_shot: 3
    similarity_threshold: 0.65
  token_budget:
    l3_gnosis: 500
    memory: 2000
    dpo_examples: 1000
    total: 4000
```
- **Effort**: 1-2 hours
- **Impact**: Controllable, tunable JIT RAG behavior

**Step 4: After — Cross-Entity Retrieval for Council**
- Add `entity_filter: Optional[List[str]]` to `selective_hydration.hydrate()`
- Enable MaKaLi council to retrieve principles from peer entities
- **Effort**: 3-4 hours

**Step 5: After — Relevance-Weighted Memory Blocks**
- Score memory blocks against query via embedding similarity
- Only inject blocks above threshold
- **Effort**: 2-3 hours

---

### Summary Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        JIT RAG PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query ──► Oracle.talk() / Oracle.summon()                │
│       │                                                         │
│       ▼                                                         │
│  _prepare_system_prompt(entity, session, query)                │
│       │                                                         │
│       ├─► ContextBuilder.build_context()                       │
│       │     │                                                   │
│       │     ├─► MemoryStore.get_history()  ──► FTS5 (BM25)     │
│       │     │                                                   │
│       │     ├─► SelectiveHydration.hydrate(query)              │
│       │     │     │                                             │
│       │     │     ├─► EmbeddingManager.get_embedding(query)    │
│       │     │     │     │                                       │
│       │     │     │     └─► GemmaGGUFEmbeddingProvider (768)   │
│       │     │     │                                             │
│       │     │     └─► SQLiteVecAdapter.query()                 │
│       │     │           │                                       │
│       │     │           └─► omega_vec_gemma_768 (vec0)         │
│       │     │                                                   │
│       │     ├─► MemoryBlocks (D-283 Mnemosyne)                 │
│       │     │                                                   │
│       │     └─► WorldState (global params + sectors)           │
│       │                                                         │
│       └─► Prepend to entity personality → ModelGateway         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Current State**: Pipeline exists and runs on every turn. **Critical Fix**: `SelectiveHydration.hydrate()` must receive the actual query, not `entity_name`. **Next Value**: Vectorize DPO pairs for few-shot retrieval. **Then**: Config-driven trigger policy.
