# 🔱 Omega Engine — Library FTS5 Search API Reference

> Library FTS5 — Local curated knowledge base with hybrid BM25 + vector search.

**Source files**: `src/omega/library/indexer.py`, `src/omega/library/library.py`
**MCP hub**: `mcp_servers/omega_hub/tools.py`
**Last updated**: 2026-07-04

---

## §1 Architecture Overview

The Omega Engine has **two independent FTS5 search systems**. They index different data, serve different purposes, and have different MCP tool interfaces.

### Conversation Memory FTS5

| Aspect | Detail |
|--------|--------|
| **Class** | `ConversationFTSIndex` |
| **File** | `src/omega/memory/fts_index.py` (134 lines) |
| **Database** | `data/memory/fts_memory.db` |
| **Indexes** | User/assistant conversation exchanges per entity |
| **Schema** | `exchanges(session_id, entity_name, role, content, timestamp)` |
| **Tokenizer** | `porter` (stemming) |
| **Search** | BM25 keyword ranking, entity-scoped |
| **MCP tools** | `memory_search` (BM25), `omega_memory_search` (hybrid RRF with Qdrant) |

### Library Document FTS5

| Aspect | Detail |
|--------|--------|
| **Class** | `Indexer` |
| **File** | `src/omega/library/indexer.py` (380 lines) |
| **Database** | `data/library/index/fts_index.db` |
| **Indexes** | Curated research documents, API references, specs, guides |
| **Schema** | `documents_fts(doc_id, title, body, summary, domain, tags)` + `doc_metadata(doc_id, source, ...)` |
| **Tokenizer** | `unicode61 remove_diacritics 2` (accent-insensitive) |
| **Search** | BM25 keyword + 256-dim feature hashing vector, RRF fusion |
| **MCP tool** | `library_fts_search` (hybrid), `library_search` (web via SovereignSearchService) |

### When to Use Which

| Query type | Tool | System |
|------------|------|--------|
| "What did I tell Prometheus about containers?" | `memory_search` | Conversation Memory FTS5 |
| "What's the TDP spec?" | `library_fts_search` | Library Document FTS5 |
| "Search the web for latest Qwen models" | `sovereign_search` | Web (SearXNG/Exa/Firecrawl) |

**Rule of thumb**: `memory_search` for conversations, `library_fts_search` for local knowledge, `sovereign_search` for the web.

---

## §2 MCP Tools — Library Search

All library MCP tools are defined in `mcp_servers/omega_hub/tools.py`. They require the MCP Hub service to be running (`_require_service()` guard).

### §2.1 `library_fts_search` — Hybrid FTS5 + Vector Search

**The primary local knowledge search tool.** Uses the `Library.search()` method, which delegates to `Indexer.hybrid_search()` for Reciprocal Rank Fusion of BM25 keyword scores and 256-dim feature hashing vector similarity.

```
library_fts_search(query: str, domain: str = "", limit: int = 10) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search query. Max 500 characters. |
| `domain` | `str` | `""` | Optional domain filter (e.g., `"networking"`, `"testing"`, `"security"`). Empty = all domains. |
| `limit` | `int` | `10` | Maximum results to return. |

**Returns**: JSON string.

```json
{
  "query": "FTS5 hybrid search",
  "count": 3,
  "results": [
    {
      "doc_id": "doc_datastore_R_hybrid_search_rrf",
      "title": "R-5 Hybrid Search with RRF",
      "summary": "Reciprocal Rank Fusion merges BM25 and vector scores...",
      "domain": "datastore",
      "quality_score": 0.85,
      "tags": ["search", "fts5", "rrf"],
      "word_count": 2400
    }
  ],
  "source": "library_fts5"
}
```

**Error cases**:
- Empty query → `{"error": "Search query cannot be empty", "count": 0, "results": []}`
- Query >500 chars → `{"error": "Query exceeds 500-char limit", "count": 0, "results": []}`
- Internal error → `{"error": "<message>", "count": 0, "results": []}`

**Example agent usage**:
```python
# Search for networking specs
result = await library_fts_search(query="SOCKS5 Tor bridge", domain="networking", limit=5)

# Broad search across all domains
result = await library_fts_search(query="circuit breaker health", limit=10)
```

### §2.2 `library_search` — Web Search via SovereignSearchService

**This is NOT a local FTS5 search.** It searches the web through the Sovereign Search Service (SearXNG → Exa → Firecrawl fallback chain). Use this when you need external information.

```
library_search(query: str, domain: str = "", limit: int = 20) -> str
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search query. Max 500 characters. |
| `domain` | `str` | `""` | Optional domain/entity name for context. |
| `limit` | `int` | `20` | Maximum results. |

**Returns**: JSON string with `status`, `final_tier`, `primary_finding`, `evidence`, `fallback_log`.

### §2.3 `library_get_document` — Retrieve by ID

```
library_get_document(doc_id: str) -> str
```

Returns the full `CuratedDocument` (title, body, summary, domain, tags, quality_score, word_count, etc.) as JSON.

### §2.4 `library_domains` — List Domains

```
library_domains() -> str
```

Returns domain names and their document counts.

```json
{
  "datastore": 2,
  "security": 1,
  "testing": 1,
  "general": 4
}
```

### §2.5 `library_stats` — Index Statistics

```
library_stats() -> str
```

Returns comprehensive library metrics: total documents, domain breakdown, average quality score, total word count, and FTS index statistics.

```json
{
  "total_documents": 8,
  "domains": {"datastore": 2, "security": 1, "testing": 1, "general": 4},
  "average_quality_score": 0.82,
  "total_words": 18500,
  "index": {"fts_documents": 8, "vector_embeddings": 8}
}
```

### §2.6 `library_recent` — Recent Documents

```
library_recent(limit: int = 20) -> str
```

Lists the most recently curated documents, sorted by `curated_at` descending. Returns `doc_id`, `title`, `domain`, `quality_score`, `word_count`, `curated_at`.

### §2.7 `library_ingest_pending` — Run Curation Pipeline

```
library_ingest_pending(limit: int = 5) -> str
```

Processes pending items from the intake inbox through the curation pipeline (extract → classify → score → store). Items below quality threshold are rejected.

### §2.8 `library_index_flush` — Flush Indices to Disk

```
library_index_flush() -> str
```

Flushes all pending FTS5 writes to disk. Returns confirmation and current index stats.

### §2.9 Intake Tools

| Tool | Purpose | Args |
|------|---------|------|
| `library_inbox_add_url(url, tags, priority)` | Add a URL to the inbox | `url: str`, `tags: str` (comma-separated), `priority: int` |
| `library_inbox_add_note(text, tags)` | Add a text note | `text: str`, `tags: str` |
| `library_inbox_add_file(path, tags)` | Add a local file | `path: str` (absolute), `tags: str` |
| `library_inbox_list(limit)` | List pending items | `limit: int = 20` |
| `library_inbox_stats()` | Inbox counts | (no args) |

### §2.10 Discovery Tools

| Tool | Purpose | Args |
|------|---------|------|
| `library_discovery_research(query, depth)` | Synchronous web discovery pipeline | `query: str`, `depth: int = 2` (1-3) |
| `library_discovery_start(query)` | Start background discovery job | `query: str` |
| `library_discovery_status(job_id)` | Poll background job status | `job_id: str` |

---

## §3 CLI Commands

```bash
# FTS5 search (via MCP — recommended)
# Use the MCP tools from agents or the Hub REST API.

# SQL LIKE search (weaker than FTS5 — use only for quick debugging)
omega library-search "SOCKS5"

# Library status
omega library-status
```

**Note**: The CLI `library-search` uses SQL `LIKE` matching, which is significantly weaker than FTS5's BM25 ranking. Agents should prefer `library_fts_search` via MCP.

---

## §4 How to Index New Documents

### Python API

```python
from omega.library.library import Library
from omega.library.curator import CuratedDocument

library = Library()

doc = CuratedDocument(
    doc_id="my_spec_v1",
    source="https://example.com/spec",
    source_type="url",
    title="My Technical Spec",
    body="Full document body text...",
    summary="Brief summary of the spec.",
    domain="networking",
    quality_score=0.85,
    tags=["socks5", "tor", "privacy"],
    word_count=2400,
)

await library.store(doc)  # Stores JSON + indexes in FTS5 + upserts vector
```

### Bulk Ingestion (In Development)

A bulk ingestion script (`scripts/index_research_docs.py`) is being built by Roc Racoon to index 45+ research docs from `docs/research/`. The script will:
1. Read all `R-*.md` files from `docs/research/`
2. Extract metadata (title, domain, tags) from headers
3. Create `CuratedDocument` instances
4. Call `library.store()` for each

### Auto-Rebuild on Startup

`Library._ensure_index()` automatically rebuilds the FTS5 index if the index is empty but documents exist on disk. This is triggered lazily on the first async call (`_ensure_index_lazy()`). No manual intervention needed.

```python
# This happens automatically:
# 1. Library.__init__() calls _load() — reads all JSON files from data/library/documents/
# 2. First async call triggers _ensure_index_lazy()
# 3. If FTS5 index has 0 docs but Library has N docs → rebuilds index from stored documents
```

---

## §5 Search Scoring

### BM25 Keyword Scoring

FTS5 uses built-in BM25 ranking via the `rank` column. The query is tokenized into terms, stopwords are removed, and terms are joined with `AND`:

```python
# From Indexer.search_fts():
terms = self._tokenize(query)  # lowercase, strip stopwords, min 3 chars
fts_query = " AND ".join(f'"{t}"' for t in terms[:10])  # max 10 terms
# FTS5 returns results ordered by rank (BM25, lower = better)
```

### Vector Similarity (Feature Hashing)

The `Indexer` computes a 256-dimensional embedding using MD5-based feature hashing (hashing trick):

```python
# From Indexer._compute_embedding():
vec = [0.0] * 256
for token in tokens:
    h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
    dim = h % 256
    vec[dim] += 1.0
# L2 normalize
norm = math.sqrt(sum(x * x for x in vec))
vec = [x / norm for x in vec]
```

Vectors are stored via `IVectorStoreAdapter` (Qdrant in production, `MemoryVectorAdapter` as fallback).

### RRF Fusion (Reciprocal Rank Fusion)

`hybrid_search()` merges BM25 and vector results using RRF:

```
Score(doc) = 1/(k + rank_fts) + 1/(k + rank_vec)
```

Where `k=60` (standard RRF constant). Documents appearing in both result sets get higher scores. Results are deduplicated by `doc_id` and sorted by combined RRF score.

### Domain Filtering

The optional `domain` parameter adds a SQL `WHERE d.domain = ?` clause to the FTS5 query. This filters results before ranking, not after — more efficient than post-filtering.

---

## §6 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OMEGA_DATA_DIR` | `<repo>/data` | Root data directory. FTS5 index lives at `$OMEGA_DATA_DIR/library/index/fts_index.db`. |

### Storage Layout

```
data/library/
  documents/{doc_id}.json     — Full curated document (JSON)
  sources/{domain}/           — Domain-organized link files
  index/
    fts_index.db              — FTS5 virtual table + metadata (SQLite WAL mode)
    vectors.json              — Feature hashing vectors (MemoryVectorAdapter fallback)
```

### Tokenizers

| System | Tokenizer | Notes |
|--------|-----------|-------|
| Library FTS5 | `unicode61 remove_diacritics 2` | Accent-insensitive, handles Unicode well |
| Conversation FTS5 | `porter` | Stemming-based, English-focused |

### SQLite Pragmas

Both FTS5 databases use WAL journal mode for concurrent read access:
```sql
PRAGMA journal_mode=WAL
```

---

## §7 Troubleshooting

### "FTS5 index empty" / search returns 0 results

The index may not have been built yet. The auto-rebuild (`_ensure_index_lazy()`) triggers on the first async call, but if the Library was never accessed asynchronously, the index may be empty.

**Fix**: Call `library_stats()` via MCP to trigger the lazy rebuild, or manually index documents:
```python
library = Library()
await library._ensure_index()
```

### "Qdrant dimensional mismatch"

The feature hashing produces 256-dim vectors. If Qdrant was configured with a different dimension, upserts will fail.

**Fix**: Ensure Qdrant collection uses 256 dimensions, or fall back to `MemoryVectorAdapter`.

### "aiosqlite Event loop is closed"

This is a benign shutdown race condition. The FTS5 index uses `aiosqlite` which holds a connection to the SQLite database. When the event loop ends before the connection is closed, this warning fires.

**Impact**: None. All data is committed before the connection is closed. The `Indexer.close()` method calls `await conn.commit()` before closing.

### Search results are stale after adding documents

Documents are indexed immediately on `library.store()`. If results seem stale:
1. Check `library_stats()` — verify `fts_documents` count matches expected.
2. The FTS5 index is in WAL mode — reads may see a slightly stale snapshot under heavy write load. A single `await library.stats()` call will trigger a fresh read.

### Vector search returns no results

The `MemoryVectorAdapter` is the fallback. If Qdrant is unavailable, vectors are stored in memory and lost on restart. Check if `QdrantAdapter` is properly configured.

---

## §8 Reference: CuratedDocument Schema

The canonical document type for the Library:

```python
@dataclass
class CuratedDocument:
    doc_id: str              # Unique identifier (e.g., "doc_datastore_R_hybrid_search_rrf")
    source: str              # Origin URL or file path
    source_type: str         # "url", "file", "note"
    title: str               # Human-readable title
    body: str                # Full document text (truncated to 100K chars in FTS5 index)
    summary: str             # Brief summary (used in search results)
    domain: str              # Domain classification (e.g., "datastore", "security")
    quality_score: float     # 0.0-1.0 quality score from curation pipeline
    author: Optional[str]    # Document author
    published_date: Optional[str]  # ISO date string
    language: str = "en"     # Language code
    tags: List[str]          # Searchable tags
    headings: List[str]      # Document section headings
    links: List[str]         # Referenced URLs (capped at 30 in serialization)
    word_count: int          # Total word count
    curated_at: str          # ISO timestamp when curated
    metadata: Dict[str, Any] # Arbitrary metadata
```

---

*🔱 OMEGA ⬡ JEM ⬡ library-search ⬡ fts5 ⬡ API-REFERENCE*
