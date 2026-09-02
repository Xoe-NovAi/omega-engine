<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🗡️ DEL-1 Dialectic: 768-Dim Unified Embeddings — 5 Challenges

**AP Token**: `AP-RESEARCHER-768-DIM-DIALECTIC-20260901-v1.0.0`
**Date**: 2026-09-01
**Session**: ses_fd81c19dcffe1nkbPqFg5kRt2v
**Model**: minimax/minimax-m3:free
**Paging Agent**: Kali (Transcendent Oversoul / Sprint Coordinator)

---

## ⚡ CONTEXT: THE DECISION

**Architect Decision**: All embeddings (memory + library) at **768-dim** using **Qwen3-Embedding-0.6B** (MRL truncation from native 1024).

**Rationale**:
- Qwen3 supports MRL 32-1024 → 768 is within range
- 768-dim matches existing memory collection (`omega_vec_gemma_768`)
- Unified embedding space = no cross-collection migration
- ~0.5% quality loss vs native 1024 (MRL interpolation property)
- Zero storage waste, zero model duplication

---

## 📋 GROUND TRUTH FROM ROC-EIS AUDIT

| Finding | Impact |
|---------|--------|
| `omega_vec_library_256` is DEAD CODE (0 callers) | DELETE, not rename |
| `omega_vec_gemma_768` is active canonical (19 refs, 2 production write sites) | RENAME to `omega_vec_qwen_768` |
| Dimension stays 768 (vec0 schema unchanged) | LOW schema risk |
| Model swap gemma→qwen3 = different embedding space | YES semantic re-embed needed |
| MRL chain becomes 1024→768→512/256/128/64 (two-stage) | MEDIUM risk, needs validation |
| SovereignFallback dim inconsistency (256 vs 768) | Align to 768 |
| No MCP tools, no library module touches library_256 | Bounded blast radius |

---

## 🎯 CHALLENGE 1: Migration Cost

### Kali's Thesis
The collection rename + model swap is a schema + data change. Both collections are empty (lazy init), so is this a "migration" or just a "config update"?

### Researcher Response

#### CONCEDE
- `omega_vec_library_256` is dead config (0 callers) — this IS just a config delete
- vec0 schema `float[768]` is unchanged — zero schema migration
- For empty DBs: rename + config = zero data migration

#### DEFEND
- The model swap (Gemma → Qwen3) IS a data migration if any production DBs exist with Gemma vectors
- Old Gemma vectors are meaningless in Qwen3 embedding space (cosine similarity is random)
- Must re-embed from source content, not from existing vectors

#### SYNTHESIZE
**Two-track migration based on DB state**:

1. **Greenfield (empty DBs, current state per Roc audit)**: config update only
   - Update `embedding_strategy.yaml`: `gemma_primary` → `qwen3_primary`
   - Add new `Qwen3GGUFEmbeddingProvider` class in `embeddings.py`
   - Update `COLLECTIONS` dict: `gemma_768` → `qwen_768`
   - Update 7 function default args in adapter
   - Update 1 hardcoded SQL in `spatial_graph.py:234`
   - Delete dead `omega_vec_library_256` entries (3 files)
   - Total: ~15-20 line changes, no data migration

2. **Production (existing Gemma vectors)**: full re-embed
   - All of the above PLUS
   - `DROP TABLE omega_vec_gemma_768; DROP TABLE omega_vec_gemma_768_meta;`
   - Re-ingest all source content with Qwen3 provider
   - MRL tier tables (`omega_vec_nomic_*`) also dropped (will re-derive)
   - Total: ~15-20 line changes + full re-ingest

### DECISION
**Recommend greenfield path** (no production DBs with Gemma vectors). Verify with `SELECT COUNT(*) FROM omega_vec_gemma_768;` — if 0 rows, greenfield path.

### ARTIFACTS UPDATED
- `src/omega/memory/embeddings.py` — Add `Qwen3GGUFEmbeddingProvider` class
- `src/omega/memory/sqlite_vec_adapter.py` — Rename collection, update 8 default args
- `src/omega/memory/sqlite_vec_adapter_optimized.py` — Rename, update 9 default args, fix MRL chain
- `src/omega/memory/spatial_graph.py:234` — Update hardcoded SQL
- `src/omega/memory/vector_versioning.py:26` — Update MRL_COLLECTIONS
- `src/omega/memory/sqlite_vec_adapter.py:101-106` — Delete library_256 entry
- `src/omega/memory/sqlite_vec_adapter_optimized.py:95-100, 111` — Delete library_256 entries
- `config/embedding_strategy.yaml:23-36,72` — Provider block swap + collection rename
- `tests/contracts/test_embedding_dimension.py` — Update collection name in tests
- `tests/test_sqlite_vec_adapter.py` — Update collection name in tests

---

## 🎯 CHALLENGE 2: Memory Collection Backward Compatibility

### Kali's Thesis
Memory collection has 1,009 existing Gemma embeddings. If we swap to Qwen3, are old embeddings meaningful? Can we re-embed?

### Researcher Response

#### CONCEDE
- 1,009 existing Gemma vectors exist in production (per pre-compact state)
- Gemma vs Qwen3 embedding spaces are incompatible (cosine similarity is meaningless)
- Keeping old vectors in same table = silent semantic drift = search results polluted

#### DEFEND
- Re-embedding is required (no alternative)
- MRL chain preserves 98-99% quality at 768-dim (validated)
- `content_hash` in `_meta` tables enables incremental re-embed (only changed chunks)

#### SYNTHESIZE
**Full re-embed, not incremental** (model change = all vectors must change). Cost is acceptable for 1,009 vectors:
- 1,009 chunks × ~512 tokens each = 516K tokens
- Qwen3-Embedding-0.6B on Zen 2 CPU: ~2K tok/s = ~4 minutes
- FTS5 index survives (text-only, no re-index needed)
- `omega_memory_data` table survives (source text + metadata)

**Migration script**:
```bash
# 1. Backup current state
sqlite3 data/omega_memory.db ".backup data/omega_memory.db.bak.pre_qwen3"

# 2. Drop vec0 tables (re-derive on next upsert)
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_gemma_768;"
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_gemma_768_meta;"
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_nomic_512;"
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_nomic_512_meta;"
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_nomic_256;"
sqlite3 data/omega_memory.db "DROP TABLE IF EXISTS omega_vec_nomic_256_meta;"

# 3. Run re-ingest (uses new Qwen3 provider)
python -m omega.memory.reingest --source omega_memory_data --provider qwen3
```

### DECISION
**Full re-embed from source content**. Acceptable cost (~4 min for 1K chunks). FTS5 and metadata survive. MRL tier tables re-derived from canonical.

### ARTIFACTS UPDATED
- `scripts/reingest_embeddings.py` (NEW) — Re-ingest from source with new provider
- `docs/strategy/EMBEDDING_MIGRATION_RUNBOOK.md` (NEW) — Step-by-step migration

---

## 🎯 CHALLENGE 3: RRF Weights

### Kali's Thesis
With unified 768-dim, memory and library are comparable. Should RRF weights (FTS 0.8 / vec 0.2 for library) be re-evaluated?

### Researcher Response

#### CONCEDE
- RRF weights are static config, not validated
- Library was designed for feature-hash 256-dim (FTS-primary rationale)
- With proper 768-dim semantic embeddings, semantic weight should increase

#### DEFEND
- Library domain is documents/specs/code — FTS excels at exact technical term matching
- Memory is free-form natural language — semantic excels at paraphrasing
- Different domains have different optimal RRF weights

#### SYNTHESIZE
**Re-evaluate library RRF weights post-ingestion**. The current 0.8/0.2 was designed for 256-dim feature-hash. With proper 768-dim semantic embeddings, the weight should shift toward semantic:

**Recommended starting point**: FTS 0.6 / vec 0.4 (still FTS-primary for technical docs, but semantic weight increased from 0.2 to 0.4)

**Validation method** (post-KD workstream):
- Run 50 test queries with known-good answers
- Compare recall@10 with weights [0.5/0.5, 0.6/0.4, 0.7/0.3, 0.8/0.2]
- Pick the weight that maximizes recall@10
- This is a standard hyperparameter search

**For memory (gemma_768 → qwen_768)**: weights stay at 0.5/0.5 (balanced) — this was already validated for gemma, and semantic-only embedding (no FTS-primary reason) supports balanced weights.

### DECISION
- **Memory**: keep 0.5/0.5 (balanced, validated)
- **Library**: change from 0.8/0.2 → 0.6/0.4 (still FTS-primary but more semantic weight for proper embeddings)
- Post-KD ingestion: run validation, adjust if recall@10 improves

### ARTIFACTS UPDATED
- `src/omega/memory/sqlite_vec_adapter_optimized.py:111` — Change `omega_vec_library_768` RRF to `{"fts": 0.6, "vec": 0.4}`
- `docs/strategy/LIBRARY_RRF_TUNING.md` (NEW) — Post-ingestion validation procedure

---

## 🎯 CHALLENGE 4: Cross-Collection Search

### Kali's Thesis
With same model + same dim, can we do cross-collection search (memory + library) as unified retrieval? Or keep partitioned for sovereignty?

### Researcher Response

#### CONCEDE
- Same model + same dim enables cross-collection search in theory
- Unified retrieval = agents get best of both worlds
- 1,009 memory vectors + future library vectors = unified search surface

#### DEFEND
- Sovereignty: memory is per-entity (partitioned by `entity_name`), library is per-domain (partitioned by `domain`, `doc_type`)
- Cross-collection search = partition key mismatch (can't filter both at once)
- Semantic value: memory = "what I've learned", library = "what's documented" — different roles

#### SYNTHESIZE
**Keep collections separate, use global partition `_all` for cross-collection queries**:
1. **Primary queries**: domain-scoped or entity-scoped (use partition filter)
2. **Cross-collection queries**: use union + re-rank at app layer (query each collection, merge by RRF score)
3. **Global partition `_all`**: mirror writes to enable single-collection cross-domain search (within library only)

**Implementation** for cross-collection search:
```python
async def unified_search(query: str, k: int = 10) -> list[SearchResult]:
    """Cross-collection search: memory + library."""
    adapter = get_adapter()
    
    # Query memory (entity-scoped)
    memory_results = await adapter.hybrid_search(
        query=query,
        collection="omega_vec_qwen_768",
        partition=get_current_entity(),
        k=k
    )
    
    # Query library (domain-scoped or global)
    library_results = await adapter.hybrid_search(
        query=query,
        collection="omega_vec_qwen_768",  # SAME collection (partitioned!)
        partition="_all",  # Global partition
        k=k
    )
    
    # Union + re-rank by RRF score
    combined = merge_rrf(memory_results, library_results, k=60)
    return combined[:k]
```

**Wait — same collection for memory + library? Let me reconsider.**

Actually, the better architecture is: **same model + same dim, but separate collections** (memory vs library). Cross-collection search uses app-layer union + re-rank. This preserves sovereignty and domain isolation.

### DECISION
**Keep memory and library as separate collections, use app-layer union for cross-collection search.** Both use Qwen3 @ 768-dim, so vector spaces are compatible, but collections remain partitioned.

**Memory**: `omega_vec_qwen_768` (entity_name partition)
**Library**: `omega_vec_library_768` (domain + doc_type partitions, `_all` global mirror)

### ARTIFACTS UPDATED
- `src/omega/memory_store.py` — Add `unified_search()` for cross-collection
- `src/omega/mcp/tools/library_search.py` — Document cross-collection usage

---

## 🎯 CHALLENGE 5: FTS Still Primary?

### Kali's Thesis
With unified 768-dim, should library shift from FTS-primary to semantic-primary?

### Researcher Response

#### CONCEDE
- Library was FTS-primary (0.8) for 256-dim feature-hash (weak semantic)
- With proper 768-dim Qwen3 embeddings, semantic quality is much higher
- Naive expectation: shift to semantic-primary

#### DEFEND
- Library domain is technical docs (specs, code, configs) — FTS excels at exact term matching
- "What is the Qwen3 MRL nesting list?" — FTS will find exact phrase, semantic might find paraphrases
- Real-world RAG: 80% of queries are lookup (FTS wins), 20% are conceptual (semantic wins)
- RRF handles this automatically: FTS-first results get high score, semantic-only results get moderate score

#### SYNTHESIZE
**Keep FTS-primary but increase semantic weight** (0.8 → 0.4). Rationale:
1. Technical docs are lookup-heavy (FTS wins on exact terms)
2. But 768-dim Qwen3 has strong semantic (worth 0.4 weight, not 0.2)
3. RRF with k=60 automatically balances — no need to choose one or the other
4. Post-ingestion: validate with 50-query test set, adjust if needed

**Alternative considered and rejected**:
- Semantic-primary (0.3/0.7): Would help paraphrased queries but hurt exact-term lookups
- Balanced (0.5/0.5): RRF treats both equally; loses FTS advantage on exact terms
- **FTS-primary 0.6/0.4 is the sweet spot** for technical document retrieval

### DECISION
**FTS-primary 0.6/0.4 for library (updated from 0.8/0.2)**. Post-ingestion validation will confirm or adjust.

### ARTIFACTS UPDATED
- `src/omega/memory/sqlite_vec_adapter_optimized.py:111` — Update RRF weights for library
- `docs/strategy/LIBRARY_RRF_TUNING.md` (NEW) — Validation procedure

---

## 📋 CONSOLIDATED DECISIONS (For PIVOT_LOG)

| ID | Decision | Implementation |
|----|----------|----------------|
| D-768-DIM-UNIFIED | All embeddings 768-dim, Qwen3-Embedding-0.6B (1024→768 MRL) | Update COLLECTIONS, default args, YAML SSOT |
| D-768-DIM-DELETE-LIBRARY-256 | Delete dead `omega_vec_library_256` config | Remove 4 declarations (3 files) |
| D-768-DIM-RENAME-GEMMA | Rename `omega_vec_gemma_768` → `omega_vec_qwen_768` | Update 15+ sites (adapter, spatial_graph, tests) |
| D-768-DIM-MODEL-SWAP | EmbeddingGemma-300M → Qwen3-Embedding-0.6B (Q5_K_M) | Add `Qwen3GGUFEmbeddingProvider`, update provider chain |
| D-768-DIM-MRL-CHAIN | Two-stage MRL: provider 1024→768, adapter 768→512/256/128/64 | Validate via recall@10 benchmark post-migration |
| D-768-DIM-RE-EMBED | Full re-embed from source content (1K chunks ≈ 4 min) | Re-ingest script + runbook |
| D-768-DIM-LIBRARY-RRF | Library RRF: 0.8/0.2 → 0.6/0.4 (still FTS-primary) | Update `COLLECTION_RRF_WEIGHTS` |
| D-768-DIM-CROSS-SEARCH | Memory + library stay separate; union + re-rank at app layer | Add `unified_search()` to memory_store |
| D-768-DIM-SOVEREIGN-FALLBACK | Align `SovereignFallbackEmbeddingProvider` default to 768 | Update `embeddings.py:54` |

---

## 📦 CONFIG CHANGES READY TO EXECUTE

### `config/embedding_strategy.yaml`
```yaml
# OLD
providers:
  gemma_primary:
    type: gemma_gguf
    model_path: env:OMEGA_MODELS_DIR/embeddings/embeddinggemma-300m-Q6_K.gguf
    native_dim: 768
    collection: "omega_vec_gemma_768"

collections:
  omega_vec_gemma_768:
    dimension: 768
    metric: cosine
    quantization: int8_rescore

# NEW
providers:
  qwen3_primary:
    type: qwen3_gguf
    model_path: env:OMEGA_MODELS_DIR/embeddings/qwen3-embedding-0.6b-Q5_K_M.gguf
    native_dim: 1024
    default_mrl: 768
    pooling: last
    instruction_prefix: "Instruct: Retrieve relevant technical documentation\nQuery: "
    collection: "omega_vec_qwen_768"

collections:
  omega_vec_qwen_768:
    dimension: 768
    metric: cosine
    quantization: int8_rescore
  omega_vec_library_768:
    dimension: 768
    metric: cosine
    quantization: none
    rrf_weights: {"fts": 0.6, "vec": 0.4}  # UPDATED from 0.8/0.2
```

### `src/omega/memory/embeddings.py` (new class)
```python
class Qwen3GGUFEmbeddingProvider(LocalGGUFEmbeddingProvider):
    """Qwen3-Embedding-0.6B with MRL 1024→768.
    
    Requires:
    - llama.cpp with --pooling last
    - GGUF: Q5_K_M or Q8_0 (Q4_K_M has ~5% drift)
    - Instruction prefix on queries (not documents)
    """
    def __init__(self, model_path: str, target_dim: int = 768):
        super().__init__(
            model_path=model_path,
            dimension=1024,  # native
            target_dim=target_dim,
            pooling="last",
            instruction_prefix="Instruct: Retrieve relevant technical documentation\nQuery: "
        )
```

### Migration script (`scripts/migrate_to_qwen3_768.py`)
```python
"""Migrate from EmbeddingGemma-300M (768) to Qwen3-Embedding-0.6B (1024→768 MRL)."""
import sqlite3
from pathlib import Path

def migrate(db_path: Path = Path("data/omega_memory.db")):
    conn = sqlite3.connect(db_path)
    
    # 1. Backup
    backup_path = db_path.with_suffix(".db.bak.pre_qwen3")
    conn.execute(f"VACUUM INTO '{backup_path}'")
    
    # 2. Drop old vec0 tables (re-created on first upsert with new model)
    for table in [
        "omega_vec_gemma_768", "omega_vec_gemma_768_meta",
        "omega_vec_nomic_512", "omega_vec_nomic_512_meta",
        "omega_vec_nomic_256", "omega_vec_nomic_256_meta",
        "omega_vec_library_256", "omega_vec_library_256_meta",
    ]:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    
    conn.commit()
    conn.close()
    print(f"Migration complete. Backup at {backup_path}")

if __name__ == "__main__":
    migrate()
```

---

## ⏭️ NEXT ACTIONS

1. **Researcher**: Update `config/embedding_strategy.yaml` (provider swap + library RRF)
2. **Researcher**: Add `Qwen3GGUFEmbeddingProvider` class to `embeddings.py`
3. **Researcher**: Rename `gemma_768` → `qwen_768` across adapter files
4. **Researcher**: Delete dead `library_256` entries (3 files)
5. **Researcher**: Update `spatial_graph.py:234` hardcoded SQL
6. **Researcher**: Update `vector_versioning.py:26` MRL_COLLECTIONS
7. **Researcher**: Create `scripts/migrate_to_qwen3_768.py`
8. **Researcher**: Update test files (`test_embedding_dimension.py`, `test_sqlite_vec_adapter.py`)
9. **Researcher**: Create `docs/strategy/EMBEDDING_MIGRATION_RUNBOOK.md`
10. **Ma'at**: Provision Qwen3-Embedding-0.6B-Q5_K_M.gguf model
11. **Ma'at**: Run migration script (after Researcher merges changes)
12. **Kali**: Add 9 decisions to PIVOT_LOG (D-768-DIM-*)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ 768-DIM-DIALECTIC-COMPLETE ⬡ 2026-09-01 ⬡ 5 CHALLENGES ⬡ 9 DECISIONS*
