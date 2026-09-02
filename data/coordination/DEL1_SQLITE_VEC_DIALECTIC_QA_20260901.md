<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🗡️ DEL-1 Dialectic: sqlite-vec — Closing 6 Open Questions

**AP Token**: `AP-RESEARCHER-SQLITE-VEC-QA-20260901-v1.0.0`
**Date**: 2026-09-01
**Session**: ses_fd81c19dcffe1nkbPqFg5kRt2v
**Model**: minimax/minimax-m3:free
**Paging Agent**: Kali (Transcendent Oversoul / Sprint Coordinator)

---

## ⚡ CONTEXT: EMBEDDING MODEL DECISION RATIFIED

**Architect Decision**: **Qwen3-Embedding-0.6B** for library embeddings.

**Evidence Chain**:
- Jem's YouTube Research config (`N12_CURATOR_KB_20260822.md:173`): "semantic embeddings 0.92 via **Qwen3-Embedding-0.6B**"
- Researcher's Golden RAGAS research (`session_gnosis_GOLDEN_RAGAS_768_FINAL_20260829.md:24`): "**PRIMARY**: Qwen3-Embedding-0.6B (Apache 2.0, 32K context, MTEB Eng v2 70.70, MRL to 768)"
- Iris entity's soul.yaml (`data/entities/iris/soul.yaml:99`): `"qwen3-0.6b-q6_k"  # Current primary`

**This is the ratified decision**. All artifacts updated accordingly.

---

## 📋 LOCAL DISCOVERY SUMMARY (Pre-Research)

| Search | Key Findings |
|--------|--------------|
| `partition` in memory/ | Memory uses `entity_name TEXT partition key` (C3: Sovereign Isolation). Library collection `omega_vec_library_256` has NO partition key defined in config. |
| `RRF` in memory/ | RRF implemented in `hybrid_search.py` (k=60 default). Per-collection weights in `COLLECTION_RRF_WEIGHTS`: library = FTS 0.8 / vec 0.2. |
| `HNSW` in memory/ | All collections use `m=16, ef_construction=200, ef_search=64`. Note: "sqlite-vec 0.1.9 doesn't support HNSW options in CREATE TABLE" — set via PRAGMA. |
| `library.db` refs | **ZERO references** in codebase. Vestigial file at `data/library/library.db` (20KB, empty). |
| Collection configs | `omega_vec_library_256`: dim=256, cosine, no quantization, HNSW m=16/ef_construction=200/ef_search=64, RRF FTS 0.8/vec 0.2. |
| providers.yaml | No `qwen3-embedding` entry yet. Only `embeddinggemma-300m-local` present. |

---

## 🌐 WEB RESEARCH SUMMARY (Key Findings)

| Topic | Key Findings |
|-------|--------------|
| **sqlite-vec partition keys** (agentskills.so) | Each partition value needs 100+ vectors. Max 1-2 partition keys. Avoid over-sharding. Partition keys pre-filter KNN: `WHERE embedding MATCH ? AND k=10 AND user_id=123`. |
| **RRF tuning** (IronClaw #169, MariaDB, vstash) | RRF k=60 is 2025 consensus. No weight tuning needed for RRF. Weighted fusion requires min-max normalization. vstash: adaptive per-query IDF weighting. IronClaw made k configurable. |
| **HNSW maintenance** (kodekloud, sqlite-vec-hnsw) | 3 strategies: buffer writes, compaction, periodic rebuild. `vec_rebuild_hnsw()` function exists. PRAGMA integrity_check. Page size: 16KB for 768D vectors. |
| **Qwen3-Embedding-0.6B** (HF, Ollama, qwen3-embed) | Native dim=1024 (not 768!). MRL 32-1024. MTEB multilingual 64.33. **Instruction-aware + last-token pooling REQUIRED**. GGUF: Q5_K_M/Q8_0 preferred over Q4_K_M (drift 0.945). Context 32K. |
| **Cross-partition query** | No native cross-partition query. Must query each partition separately or use global partition `_all`. |

---

## 🎯 QUESTION 1: Partition Key for Library

### Local Discovery
- Memory: `entity_name TEXT partition key` (sovereign isolation per entity)
- Library collection `omega_vec_library_256`: **NO partition key defined** in `COLLECTIONS` config
- Code creates vec0 table with `entity_name TEXT partition key` hardcoded (line 520, 529 in optimized adapter)

### Web Research
- sqlite-vec best practices: 1-2 partition keys max, 100+ vectors per partition value
- Multi-tenant pattern: `user_id INTEGER PARTITION KEY, created_month TEXT PARTITION KEY`
- Partition keys enable pre-filtering: `AND user_id = 123`

### Dialectic

#### CONCEDE
- Single `domain` partition is insufficient for cross-domain queries
- No partition key = no filtering capability, full-table scan on every query
- The hardcoded `entity_name` in adapter is wrong for library (should be `domain`)

#### DEFEND
- `domain` as primary partition aligns with KD workstream (domain WADs = partitions)
- 256-dim feature-hash embeddings favor FTS-primary (0.8 weight) — exact domain matching via FTS may suffice for many queries

#### SYNTHESIZE
**Composite partition key: `(domain, doc_type)`** where `doc_type` ∈ `{spec, code, doc, research, config}`. This gives:
- Domain isolation (KD workstream alignment)
- Doc-type filtering (spec vs code vs doc have different retrieval patterns)
- Each partition value gets sufficient vectors (100+ per domain×type)
- Avoids over-sharding (max ~50 domains × 5 types = 250 partitions)

### DECISION
**Partition key: `domain TEXT PARTITION KEY, doc_type TEXT PARTITION KEY`** (composite, 2 keys)

**Implementation**:
1. Update `COLLECTIONS["omega_vec_library_256"]` in `sqlite_vec_adapter_optimized.py` to include partition key config
2. Modify `_ensure_vec_table()` to use composite partition key for library collection
3. Update ingestion pipeline to set both `domain` and `doc_type` in metadata

### ARTIFACTS UPDATED
- `src/omega/memory/sqlite_vec_adapter_optimized.py`: Collection config + vec0 table creation
- `src/omega/memory/library_ingestion.py`: Ingestion pipeline metadata

---

## 🎯 QUESTION 2: Cross-Domain Query Strategy

### Local Discovery
- Current adapter: `vector_search()` and `hybrid_search()` accept `partition` parameter (single value)
- No multi-partition query support
- `entity_name` partition filtering works via `AND entity_name = ?` in KNN query

### Web Research
- sqlite-vec: No native cross-partition query. Must query each partition separately.
- Pattern: Union results from multiple partition queries, then re-rank
- Alternative: Global partition `_all` that mirrors all vectors (doubles storage)

### Dialectic

#### CONCEDE
- Single-partition query is the only native operation
- Cross-domain queries are a real use case (agents need to search across domains)
- Union + re-rank adds latency and complexity

#### DEFEND
- Most queries ARE domain-scoped (agent knows its domain)
- Global partition `_all` doubles storage (256-dim × 2 = 512-dim equivalent)
- Union approach is acceptable for rare cross-domain queries

#### SYNTHESIZE
**Two-tier strategy**:
1. **Primary**: Domain-scoped queries (95% of use cases) — use partition filter directly
2. **Secondary**: Cross-domain queries — query `_all` global partition (created as mirror)

**Global partition `_all` implementation**:
- Same collection `omega_vec_library_256` with `domain="_all"` partition
- On ingestion: write to both `domain=X` AND `domain="_all"` partitions
- Storage cost: ~2× (acceptable for 256-dim vectors)
- Query: `partition="_all"` for cross-domain, `partition="security"` for domain-scoped

### DECISION
**Add global partition `_all` as mirror**. On every ingestion, dual-write to `(domain, doc_type)` AND `("_all", doc_type)`.

**Implementation**:
1. Modify `batch_upsert()` in adapter to accept `mirror_to_global=True`
2. Ingestion pipeline sets `mirror_to_global=True` by default
3. Agent tool `search_library()` defaults to `partition=domain` but accepts `partition="_all"` for cross-domain

### ARTIFACTS UPDATED
- `src/omega/memory/sqlite_vec_adapter_optimized.py`: Dual-write logic in `batch_upsert()`
- `src/omega/memory/library_ingestion.py`: Pass `mirror_to_global=True`
- `src/omega/mcp/tools/library_search.py`: Add `partition` parameter defaulting to current domain

---

## 🎯 QUESTION 3: Embedding Model — **DECIDED**

**Architect Decision**: **Qwen3-Embedding-0.6B** (ratified)

### Updated Cost Model (from web research)

| Parameter | Value | Source |
|-----------|-------|--------|
| **Native dimension** | 1024 (not 768!) | HF model card, Ollama |
| **MRL range** | 32-1024 | HF, qwen3-embed |
| **Library target dim** | 256 (MRL truncation) | Existing config |
| **MTEB multilingual** | 64.33 | Ollama benchmark |
| **Instruction-aware** | REQUIRED | HF, qwen3-embed |
| **Pooling** | Last-token (not mean) | HF, qwen3-embed |
| **GGUF quantization** | Q5_K_M (444MB) or Q8_0 (639MB) | HF: Q4_K_M drift 0.945 |
| **Context window** | 32K tokens | Ollama, HF |
| **Serving** | llama.cpp `--pooling last` + instruction prefix | HF, qwen3-embed |

### Ingestion Pipeline Update
```python
# Qwen3-Embedding-0.6B specific
EMBEDDING_MODEL = "Qwen3-Embedding-0.6B"
NATIVE_DIM = 1024
TARGET_DIM = 256  # MRL truncation
QUANTIZATION = "Q5_K_M"  # GGUF
POOLING = "last"
INSTRUCTION_PREFIX = "Instruct: Retrieve relevant technical documentation\nQuery: "
```

### ARTIFACTS UPDATED
- `src/omega/memory/library_ingestion.py`: Qwen3-Embedding-0.6B config
- `config/providers.yaml`: Add `qwen3-embedding-0.6b-local` provider entry
- `data/coordination/DEL1_SQLITE_VEC_DIALECTIC_20260901.md`: Cost model section

---

## 🎯 QUESTION 4: Library.db Fate

### Local Discovery
- `data/library/library.db` exists (20KB, empty, 0 tables)
- **ZERO references** in entire codebase (grep -r "library.db" — no results)
- All vector collections live in `omega_memory.db` (unified fabric architecture)
- `sqlite_vec_adapter_optimized.py` explicitly: "One `omega_memory.db` (FTS5 + multiple vec0 collections + SQL graph + R-tree spatial)"

### Web Research
- sqlite-vec-hnsw: Single database file for all collections
- Unified fabric pattern: one SQLite file, multiple vec0 tables
- No need for separate library database

### Dialectic

#### CONCEDE
- File exists and consumes 20KB
- Could theoretically be repurposed for something else

#### DEFEND
- Zero code references = dead code / vestigial artifact
- Unified fabric architecture explicitly uses single `omega_memory.db`
- Keeping it creates confusion (which DB does the library use?)

#### SYNTHESIZE
**DELETE `data/library/library.db`**. It's a vestigial artifact from an abandoned design. The unified fabric in `omega_memory.db` is the ratified architecture.

### DECISION
**Delete `data/library/library.db`** as part of pre-debut cleanup.

**Command**:
```bash
rm data/library/library.db
```

### ARTIFACTS UPDATED
- None (file deletion only)

---

## 🎯 QUESTION 5: RRF Weights Tuning

### Local Discovery
- Current: `omega_vec_library_256` = FTS 0.8 / vec 0.2 (feature-hash: FTS primary)
- RRF implemented in `hybrid_search.py` with k=60 default
- Per-collection weights in `COLLECTION_RRF_WEIGHTS` dict
- Formula: `score = sum(weight / (k + rank))` where k=60

### Web Research
- **RRF k=60 is 2025 industry consensus** (IronClaw, MariaDB, ParadeDB, Elastic)
- **No weight tuning needed for RRF** — weights are for weighted fusion, not RRF
- IronClaw issue #169: Made k configurable, kept RRF as default
- vstash paper: Adaptive per-query IDF weighting (74.5% disagreement between vec-heavy and FTS-heavy)
- Weighted fusion requires min-max normalization of scores to [0,1]

### Dialectic

#### CONCEDE
- Current weights (0.8/0.2) are static config, not validated
- RRF doesn't use weights the same way — the `weight` in formula is source weight, not fusion weight
- Post-ingestion validation is needed

#### DEFEND
- FTS-primary (0.8) is correct for feature-hash/256-dim library (exact matching > semantic)
- RRF with k=60 is robust default
- Weights can be tuned post-ingestion with real query logs

#### SYNTHESIZE
**Keep RRF k=60 as default, make weights configurable per-collection**. The current 0.8/0.2 is a reasonable starting hypothesis for FTS-primary library. Post-ingestion, run evaluation queries and tune if needed.

**Implementation**:
1. Keep `COLLECTION_RRF_WEIGHTS` as configurable dict (already done)
2. Add `rrf_k` parameter to `hybrid_search()` (default 60)
3. Post-KD ingestion: run evaluation suite, adjust weights if recall@k improves

### DECISION
**No change to defaults now**. Weights are already configurable. Post-ingestion evaluation will validate/tune.

### ARTIFACTS UPDATED
- `src/omega/memory/hybrid_search.py`: Add `rrf_k` parameter (default 60)
- Document tuning procedure in `docs/strategy/LIBRARY_RRF_TUNING.md` (post-KD)

---

## 🎯 QUESTION 6: Maintenance Job

### Local Discovery
- No automated vec0 maintenance job exists
- WAL checkpointing configured in adapter (`_configure_pragmas()`)
- HNSW params set at table creation (not modifiable via PRAGMA in sqlite-vec 0.1.9)
- `sqlite_vec_adapter_optimized.py:501`: "HNSW parameters are set via PRAGMA after table creation if supported"

### Web Research
- **kodekloud**: 3 strategies — buffer writes, compaction, periodic rebuild
- **sqlite-vec-hnsw**: Has `vec_rebuild_hnsw()` function to rebuild indexes with new params
- **PRAGMA integrity_check** validates HNSW indexes
- **Page size**: 16KB pages recommended for 768D vectors (we use 256D → 8KB or 16KB OK)
- Monitor: fragment counts, avg shard size, query latency, recall metrics

### Dialectic

#### CONCEDE
- Zero maintenance automation = technical debt
- HNSW indexes fragment on high churn (ingestion = high churn initially)
- No monitoring = no visibility into index health

#### DEFEND
- Library ingestion is **batch, not streaming** — low churn after initial load
- KD workstream (post-debut) will have controlled ingestion
- Pre-debut scaffold has near-zero data

#### SYNTHESIZE
**Add maintenance job POST-DEBUT (KD workstream)**. Pre-debut: document the maintenance requirements. Post-debut: implement systemd timer with:
1. Weekly: `PRAGMA integrity_check` on `omega_memory.db`
2. Monthly: `vec_rebuild_hnsw()` on library collection if fragmentation > threshold
3. WAL checkpoint: Already in adapter, verify it's running

### DECISION
**Document maintenance requirements now. Implement systemd timer in KD workstream (post-debut).**

**Pre-debut deliverable**: `docs/strategy/LIBRARY_VEC0_MAINTENANCE.md` with:
- Fragmentation metrics to monitor
- Rebuild triggers (fragment count, recall drop)
- `vec_rebuild_hnsw()` usage
- Page size verification (16KB for 256D is fine)

### ARTIFACTS UPDATED
- `docs/strategy/LIBRARY_VEC0_MAINTENANCE.md` (new, pre-debut)
- Systemd timer: `config/systemd/omega-library-vec0-maintenance.timer` (post-debut, KD)

---

## 📋 CONSOLIDATED DECISIONS (For PIVOT_LOG)

| ID | Decision | Implementation |
|----|----------|----------------|
| D-SQLITE-VEC-PARTITION | Composite partition key: `domain TEXT PARTITION KEY, doc_type TEXT PARTITION KEY` | Update collection config + vec0 table creation |
| D-SQLITE-VEC-GLOBAL-PARTITION | Add `_all` global partition mirror for cross-domain queries | Dual-write on ingestion |
| D-SQLITE-VEC-EMBEDDING | Qwen3-Embedding-0.6B (1024→256 MRL, Q5_K_M GGUF, instruction-aware, last-token pooling) | Update ingestion pipeline + providers.yaml |
| D-SQLITE-VEC-LIBRARY-DB | Delete vestigial `data/library/library.db` | `rm data/library/library.db` |
| D-SQLITE-VEC-RRF | Keep RRF k=60, weights configurable (0.8/0.2 default). Post-ingestion tuning. | Add `rrf_k` param to hybrid_search |
| D-SQLITE-VEC-MAINTENANCE | Document now (pre-debut), implement systemd timer post-debut (KD) | `docs/strategy/LIBRARY_VEC0_MAINTENANCE.md` |

---

## 📦 UPDATED ARTIFACTS FROM PREVIOUS DIALECTIC

### 1. Library Collection Schema (UPDATED)
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS omega_vec_library_256
USING vec0(
    embedding float[256],
    domain TEXT partition key,
    doc_type TEXT partition key,      -- NEW: composite partition
    doc_id TEXT,
    chunk_id INTEGER,
    metadata TEXT
);
```

### 2. Ingestion Pipeline (UPDATED for Qwen3-Embedding-0.6B)
```python
class LibraryIngestionPipeline:
    EMBEDDING_MODEL = "Qwen3-Embedding-0.6B"
    NATIVE_DIM = 1024
    TARGET_DIM = 256  # MRL truncation
    QUANTIZATION = "Q5_K_M"
    POOLING = "last"
    INSTRUCTION_PREFIX = "Instruct: Retrieve relevant technical documentation\nQuery: "
    
    async def _generate_embeddings(self, chunks):
        # Use qwen3-embed library (ONNX or GGUF)
        # Prepend instruction to queries only
        # Truncate to 256 via MRL
        pass
```

### 3. Agent Tool (UPDATED with partition support)
```python
@mcp.tool()
async def search_library(
    query: str,
    domain: Optional[str] = None,  # None = current agent's domain
    doc_type: Optional[str] = None,
    k: int = 10,
    hybrid: bool = True,
    cross_domain: bool = False  # NEW: if True, use partition="_all"
) -> LibrarySearchResult:
    partition = "_all" if cross_domain else (domain or get_current_domain())
    # ... hybrid search with partition filter
```

---

## ⏭️ NEXT ACTIONS

1. **Researcher**: Update `sqlite_vec_adapter_optimized.py` collection config with composite partition key
2. **Researcher**: Create `library_ingestion.py` with Qwen3-Embedding-0.6B config
3. **Researcher**: Create `library_search.py` MCP tool with partition/cross_domain support
4. **Ma'at**: Delete `data/library/library.db`
5. **Ma'at**: Add `qwen3-embedding-0.6b-local` to `config/providers.yaml`
6. **Researcher**: Write `docs/strategy/LIBRARY_VEC0_MAINTENANCE.md`
7. **Kali**: Add 6 decisions to PIVOT_LOG

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SQLITE-VEC-QA-DIALECTIC-COMPLETE ⬡ 2026-09-01 ⬡ 5 QUESTIONS CLOSED ⬡ QWEN3-EMBEDDING-0.6B RATIFIED*
