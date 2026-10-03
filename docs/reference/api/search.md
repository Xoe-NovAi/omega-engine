# 🔱 Search — Sovereign Search Persistence & Telemetry
**AP Token**: `AP-SEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Search package — persistence, metrics, and traceability for all search operations across the Sovereign Search Protocol (5 tiers).
**Tags**: search, persistence, telemetry, metrics, sovereign-search-protocol, sqlite
**Cross-references**: src/omega/search/search_persistence.py, src/omega/infra/sqlite_policy.py, docs/research/R_CG07_SOVEREIGN_SEARCH_5TIER.md, SOVEREIGN_MANDATES.md

---

## Overview

The `search` package provides **automatic persistence** of all search tool results to a SQLite database for metrics, visibility, traceability, and mandate compliance. It implements the data layer for the **Sovereign Search Protocol (SSP)** 5-tier fallback chain.

Every search tool invocation is recorded with full context: query, tier, tool, results, latency, status, errors, fallback chain, and **actual provider provenance (M22)**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Search Package                          │
├─────────────────────────────────────────────────────────────┤
│  search_persistence.py │  SearchDB, SearchRecord,          │
│                        │  SearchPersistence, decorators     │
│  __init__.py           │  Public exports                    │
└─────────────────────────────────────────────────────────────┘
```

**Database**: `data/search/search_history.db` (SQLite with WAL mode)

**Tables**:
- `search_results` — Every search invocation (immutable log)
- `search_sessions` — Session-level aggregates

---

## Sovereign Search Protocol (5 Tiers)

| Tier | Tools | Description |
|------|-------|-------------|
| **0** | `library_fts_search`, `omega_memory_search` | Local FTS5 / vector search |
| **1** | `websearch`, `web_search` | Built-in web search |
| **2** | `webfetch`, `web_fetch` | Built-in web fetch |
| **3** | `searxng_searxng_search`, `sovereign_search` | SearXNG / multi-tier router |
| **4** | `parallel-search`, `parallel-fetch` | Parallel Search (free MCP) |
| **5** | `exa`, `web_search_exa` | Exa AI search |
| **6** | `firecrawl`, `search_extract` | Firecrawl scrape/search |

The `TOOL_TO_TIER` mapping in `search_persistence.py` defines the authoritative tier for each tool.

---

## Core Classes

### SearchRecord

Immutable record of a single search invocation.

```python
@dataclass
class SearchRecord:
    search_id: str                    # UUID: "search_<12-char>"
    query: str                        # Original query (truncated to 500 chars)
    tier: Optional[int]               # SSP tier (0-6)
    tool_name: str                    # Tool identifier
    entity_name: Optional[str]        # Requesting entity
    channel: Optional[str]            # "opencode", "cline", etc.
    results_json: str                 # Full JSON response (serialized)
    result_count: int                 # Number of results returned
    latency_ms: int                   # Total latency
    status: str                       # "success" | "partial" | "failed" | "fallback"
    error_code: Optional[str] = None  # "401", "429", "500", "timeout", ...
    error_message: Optional[str] = None
    fallback_tool: Optional[str] = None
    fallback_tier: Optional[int] = None
    provider_name: Optional[str] = None  # M22: actual provider from response
    trace_id: Optional[str] = None
```

### SearchDB

Thread-safe database access using `sqlite_policy` **search profile**.

```python
class SearchDB:
    _local = threading.local()  # Thread-local connections
    
    @classmethod
    def get_conn(cls) -> sqlite3.Connection:
        """Get thread-local connection with search profile PRAGMAs."""
    
    @classmethod
    def init(cls):
        """Initialize database schema."""
    
    @classmethod
    def insert(cls, record: SearchRecord) -> None:
        """Persist a search record."""
    
    @classmethod
    def query(cls, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute arbitrary query."""
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get aggregated search statistics."""
```

**Search Profile PRAGMAs** (from `sqlite_policy.py`):
```python
[
    ("journal_mode", "WAL"),
    ("synchronous", "NORMAL"),
    ("cache_size", "-65536"),      # 64MB
    ("mmap_size", "268435456"),    # 256MB
    ("temp_store", "MEMORY"),
    ("busy_timeout", "30000"),     # 30s
    ("foreign_keys", "ON"),
    ("wal_autocheckpoint", "10000"),
    ("journal_size_limit", "67108864"),  # 64MB
    ("page_size", "4096"),
]
```

### SearchPersistence

High-level wrapper that automatically persists search results from any search tool.

#### Constructor

```python
SearchPersistence(entity_name: str = "unknown", channel: str = "opencode")
```

#### `wrap_search(...) -> str`

Persist a search result and return the `search_id`.

```python
persistence = SearchPersistence(entity_name="researcher", channel="opencode")

search_id = persistence.wrap_search(
    tool_name="websearch",
    tier=1,
    query="sovereign AI architecture",
    results={"results": [...], "count": 10},
    latency_ms=245,
    status="success",
    provider_name="parallel-search"
)
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Search tool identifier |
| `tier` | `int` | SSP tier (0-6) |
| `query` | `str` | Original search query |
| `results` | `Any` | Full results object (JSON serialized) |
| `latency_ms` | `int` | Total latency in milliseconds |
| `status` | `str` | `"success"`, `"partial"`, `"failed"`, `"fallback"` |
| `error_code` | `Optional[str]` | Error code if failed |
| `error_message` | `Optional[str]` | Human-readable error |
| `fallback_tool` | `Optional[str]` | Tool used for fallback |
| `fallback_tier` | `Optional[int]` | Tier of fallback tool |
| `provider_name` | `Optional[str]` | Actual provider (M22) |

**Auto-extraction**: If `provider_name` not provided, extracts from results dict (`provider_name`, `backend`, `provider` fields).

#### `get_recent(limit: int = 50) -> List[Dict]`

Get recent search history for this entity.

#### `get_stats() -> Dict[str, Any]`

Get search statistics (delegates to `SearchDB.get_stats()`).

---

## Decorator: `@persist_search`

Automatic persistence for async search tools.

```python
from omega.search import persist_search

@persist_search(entity_name="researcher", channel="opencode")
async def my_search_tool(query: str) -> dict:
    # Your search logic here
    return {"results": [...], "count": 5}
```

**Behavior**:
- Measures latency automatically
- Determines tier from tool name via `TOOL_TO_TIER` mapping
- Extracts `provider_name` from result (M22)
- On exception: records failure with error details, **re-raises** (M23)

---

## Statistics API

`SearchDB.get_stats()` returns:

```python
{
    "total_searches": 1247,
    "by_tier": {0: 400, 1: 350, 2: 120, 3: 200, 4: 100, 5: 50, 6: 27},
    "by_status": {"success": 1100, "partial": 80, "failed": 45, "fallback": 22},
    "by_tool": {"websearch": 350, "parallel-search": 100, ...},
    "by_provider": {"parallel-search": 150, "exa": 50, "native-gguf": 400, ...},
    "by_entity": {"researcher": 500, "jem": 300, "kali": 200, ...},
    "avg_latency_by_tier": {0: 12, 1: 850, 2: 1200, 3: 2100, 4: 1800, 5: 3200, 6: 4500},
    "fallback_rate": 0.018,
    "error_rate": 0.036
}
```

---

## CLI Interface

```bash
# Show global statistics
python -m omega.search.search_persistence stats

# Show recent searches for entity
python -m omega.search.search_persistence recent researcher

# Export all searches for entity as JSON
python -m omega.search.search_persistence export researcher
```

---

## Usage Example

```python
from omega.search import SearchPersistence, persist_search
from omega.observability import new_trace_id

# Manual persistence
persistence = SearchPersistence(entity_name="jem", channel="opencode")

async def search_with_persistence(query: str) -> dict:
    trace_id = new_trace_id()
    start = time.perf_counter()
    
    try:
        results = await websearch(query)  # Your search tool
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        persistence.wrap_search(
            tool_name="websearch",
            tier=1,
            query=query,
            results=results,
            latency_ms=latency_ms,
            status="success",
            provider_name=results.get("provider_name"),
            trace_id=trace_id
        )
        return results
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        persistence.wrap_search(
            tool_name="websearch",
            tier=1,
            query=query,
            results={"error": str(e)},
            latency_ms=latency_ms,
            status="failed",
            error_code=type(e).__name__,
            error_message=str(e),
            trace_id=trace_id
        )
        raise  # M23: re-raise

# Or use decorator
@persist_search(entity_name="researcher", channel="opencode")
async def sovereign_search(query: str) -> dict:
    return await sovereign_search_impl(query)
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Thread-local connections; blocking I/O in threads |
| **M9 Error Integrity** | Typed error codes; full context in `error_message` |
| **M12 Queue Integrity** | Every search has terminal state (persisted) |
| **M22 Response Provenance** | `provider_name` extracted from response, not intent |
| **M23 Failure Integrity** | Decorator re-raises after persistence; no soft-failures |
| **FS-Β4** | Uses `sqlite_policy` search profile for connections |

---

## Database Schema

```sql
CREATE TABLE search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id TEXT UNIQUE NOT NULL,
    query TEXT NOT NULL,
    tier INTEGER,
    tool_name TEXT NOT NULL,
    entity_name TEXT,
    channel TEXT,
    results_json TEXT,
    result_count INTEGER DEFAULT 0,
    latency_ms INTEGER,
    status TEXT NOT NULL,
    error_code TEXT,
    error_message TEXT,
    fallback_tool TEXT,
    fallback_tier INTEGER,
    provider_name TEXT,
    trace_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_entity_time ON search_results(entity_name, created_at);
CREATE INDEX idx_search_query ON search_results(query);
CREATE INDEX idx_search_tier ON search_results(tier);
CREATE INDEX idx_search_status ON search_results(status);
CREATE INDEX idx_search_trace ON search_results(trace_id);
CREATE INDEX idx_search_provider ON search_results(provider_name);

CREATE TABLE search_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    entity_name TEXT NOT NULL,
    channel TEXT NOT NULL,
    model TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    total_searches INTEGER DEFAULT 0,
    total_latency_ms INTEGER DEFAULT 0
);
```

---

## Testing

```bash
pytest tests/test_search_persistence.py -v
```

Key test scenarios:
- Record insertion and retrieval
- Statistics aggregation
- Decorator persistence on success/failure
- Provider name extraction (M22)
- Thread-safety of connections
- CLI commands

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SEARCH-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

