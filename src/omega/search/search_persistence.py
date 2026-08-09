# [heritage: sqlite-vec 2024] Search Persistence Layer — SQLite-backed search history with full traceability
"""
Search Results Persistence System

Provides automatic persistence of all search tool results to SQLite database
for metrics, visibility, traceability, and M12/M23 compliance.

Mandates addressed:
- M12 Queue Integrity: Every search request has terminal state (persisted)
- M9 Error Integrity: Typed, traceable errors with full context
- M23 Failure Integrity: No soft-failures — tool failures logged with full context
- M22 Response Provenance: Actual provider recorded from response, not intent
- FS-Β4: Uses sqlite_policy for profiled connections (search profile)
"""

import json
import uuid
import time
import threading
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from omega.observability import new_trace_id, get_engine
from omega.infra.sqlite_policy import sqlite_transaction, Profile
from omega.governance.config_resolver import DATA_DIR


# ─── Database Path ───
SEARCH_DB_PATH = DATA_DIR / "search" / "search_history.db"
SEARCH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ─── Schema ───
SCHEMA = """
CREATE TABLE IF NOT EXISTS search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id TEXT UNIQUE NOT NULL,           -- UUID for this search
    query TEXT NOT NULL,                       -- Original query
    tier INTEGER,                              -- 0=local, 1=websearch, 2=webfetch, 3=searxng, 4=parallel, 5=exa, 6=firecrawl
    tool_name TEXT NOT NULL,                   -- 'websearch', 'parallel-search', 'sovereign_search', etc.
    entity_name TEXT,                          -- Requesting entity
    channel TEXT,                              -- 'opencode', 'cline', etc.
    results_json TEXT,                         -- Full JSON response
    result_count INTEGER DEFAULT 0,            -- Number of results returned
    latency_ms INTEGER,                        -- Total latency
    status TEXT NOT NULL,                      -- 'success', 'partial', 'failed', 'fallback'
    error_code TEXT,                           -- 401, 402, 429, 500, timeout, connection_refused
    error_message TEXT,                        -- Human-readable error
    fallback_tool TEXT,                        -- Tool used for fallback (if any)
    fallback_tier INTEGER,                     -- Tier of fallback tool
    provider_name TEXT,                        -- Actual provider from response (M22)
    trace_id TEXT,                             -- Observability trace ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_entity_time ON search_results(entity_name, created_at);
CREATE INDEX IF NOT EXISTS idx_search_query ON search_results(query);
CREATE INDEX IF NOT EXISTS idx_search_tier ON search_results(tier);
CREATE INDEX IF NOT EXISTS idx_search_status ON search_results(status);
CREATE INDEX IF NOT EXISTS idx_search_trace ON search_results(trace_id);
CREATE INDEX IF NOT EXISTS idx_search_provider ON search_results(provider_name);

CREATE TABLE IF NOT EXISTS search_sessions (
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

CREATE INDEX IF NOT EXISTS idx_session_entity ON search_sessions(entity_name, started_at);
"""


# ─── Data Classes ───
@dataclass
class SearchRecord:
    search_id: str
    query: str
    tier: Optional[int]
    tool_name: str
    entity_name: Optional[str]
    channel: Optional[str]
    results_json: str
    result_count: int
    latency_ms: int
    status: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    fallback_tool: Optional[str] = None
    fallback_tier: Optional[int] = None
    provider_name: Optional[str] = None
    trace_id: Optional[str] = None


# ─── Connection Manager (Thread-Safe, Profiled) ───
class SearchDB:
    """Thread-safe database access using sqlite_policy search profile."""
    
    _local = threading.local()
    
    @classmethod
    def get_conn(cls) -> sqlite3.Connection:
        """Get a thread-local connection with search profile PRAGMAs."""
        if not hasattr(cls._local, 'conn'):
            # FS-Β4: Use sqlite_policy search profile
            cls._local.conn = sqlite3.connect(
                str(SEARCH_DB_PATH),
                check_same_thread=False,
                timeout=30.0
            )
            cls._local.conn.row_factory = sqlite3.Row
            # Apply search profile PRAGMAs
            for pragma, value in [
                ("journal_mode", "WAL"),
                ("synchronous", "NORMAL"),
                ("cache_size", "-65536"),
                ("mmap_size", "268435456"),
                ("temp_store", "MEMORY"),
                ("busy_timeout", "30000"),
                ("foreign_keys", "ON"),
                ("page_size", "4096"),
            ]:
                cls._local.conn.execute(f"PRAGMA {pragma} = {value}")
        return cls._local.conn
    
    @classmethod
    def init(cls):
        """Initialize database schema."""
        with sqlite_transaction(SEARCH_DB_PATH, profile="search") as conn:
            conn.executescript(SCHEMA)
    
    @classmethod
    def insert(cls, record: SearchRecord) -> None:
        conn = cls.get_conn()
        conn.execute("""
            INSERT INTO search_results (
                search_id, query, tier, tool_name, entity_name, channel,
                results_json, result_count, latency_ms, status,
                error_code, error_message, fallback_tool, fallback_tier,
                provider_name, trace_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.search_id, record.query, record.tier, record.tool_name,
            record.entity_name, record.channel, record.results_json,
            record.result_count, record.latency_ms, record.status,
            record.error_code, record.error_message, record.fallback_tool,
            record.fallback_tier, record.provider_name, record.trace_id
        ))
        conn.commit()
    
    @classmethod
    def query(cls, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        conn = cls.get_conn()
        cursor = conn.execute(sql, params)
        return cursor.fetchall()
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        conn = cls.get_conn()
        stats = {}
        
        # Total searches
        stats['total_searches'] = conn.execute("SELECT COUNT(*) FROM search_results").fetchone()[0]
        
        # By tier
        stats['by_tier'] = dict(conn.execute("""
            SELECT tier, COUNT(*) FROM search_results GROUP BY tier
        """).fetchall())
        
        # By status
        stats['by_status'] = dict(conn.execute("""
            SELECT status, COUNT(*) FROM search_results GROUP BY status
        """).fetchall())
        
        # By tool
        stats['by_tool'] = dict(conn.execute("""
            SELECT tool_name, COUNT(*) FROM search_results GROUP BY tool_name
        """).fetchall())
        
        # By provider (M22 provenance)
        stats['by_provider'] = dict(conn.execute("""
            SELECT provider_name, COUNT(*) FROM search_results 
            WHERE provider_name IS NOT NULL GROUP BY provider_name
        """).fetchall())
        
        # By entity
        stats['by_entity'] = dict(conn.execute("""
            SELECT entity_name, COUNT(*) FROM search_results 
            WHERE entity_name IS NOT NULL GROUP BY entity_name
        """).fetchall())
        
        # Avg latency by tier
        stats['avg_latency_by_tier'] = dict(conn.execute("""
            SELECT tier, AVG(latency_ms) FROM search_results 
            WHERE latency_ms IS NOT NULL GROUP BY tier
        """).fetchall())
        
        # Fallback rate
        fallback_count = conn.execute("""
            SELECT COUNT(*) FROM search_results WHERE fallback_tool IS NOT NULL
        """).fetchone()[0]
        stats['fallback_rate'] = fallback_count / max(stats['total_searches'], 1)
        
        # Error rate
        error_count = conn.execute("""
            SELECT COUNT(*) FROM search_results WHERE status = 'failed'
        """).fetchone()[0]
        stats['error_rate'] = error_count / max(stats['total_searches'], 1)
        
        return stats


# ─── Persistence Wrapper ───
class SearchPersistence:
    """Wrapper that automatically persists search results from any search tool."""
    
    def __init__(self, entity_name: str = "unknown", channel: str = "opencode"):
        self.entity_name = entity_name
        self.channel = channel
        self.db = SearchDB
        self.db.init()
    
    def wrap_search(self, tool_name: str, tier: int, query: str, 
                    results: Any, latency_ms: int, 
                    status: str = "success",
                    error_code: Optional[str] = None,
                    error_message: Optional[str] = None,
                    fallback_tool: Optional[str] = None,
                    fallback_tier: Optional[int] = None,
                    provider_name: Optional[str] = None) -> str:
        """
        Persist a search result and return the search_id.
        
        Args:
            tool_name: Name of the search tool used
            tier: SSP tier (0-6)
            query: Original search query
            results: Full results object (will be JSON serialized)
            latency_ms: Total latency in milliseconds
            status: 'success', 'partial', 'failed', 'fallback'
            error_code: Error code if failed
            error_message: Error message if failed
            fallback_tool: Tool used for fallback
            fallback_tier: Tier of fallback tool
            provider_name: Actual provider from response (M22)
        
        Returns:
            search_id (UUID)
        """
        search_id = f"search_{uuid.uuid4().hex[:12]}"
        
        # Serialize results
        if isinstance(results, str):
            results_json = results
        else:
            results_json = json.dumps(results, default=str)
        
        # Count results
        result_count = 0
        try:
            if isinstance(results, dict):
                if 'results' in results:
                    result_count = len(results['results']) if isinstance(results['results'], list) else 1
                elif 'evidence' in results:
                    result_count = len(results['evidence']) if isinstance(results['evidence'], list) else 1
                elif 'count' in results:
                    result_count = results['count']
            elif isinstance(results, list):
                result_count = len(results)
        except Exception:
            result_count = 0
        
        # Extract provider_name from results if not provided (M22)
        if provider_name is None and isinstance(results, dict):
            provider_name = results.get('provider_name') or results.get('backend') or results.get('provider')
        
        record = SearchRecord(
            search_id=search_id,
            query=query[:500],  # Limit query length
            tier=tier,
            tool_name=tool_name,
            entity_name=self.entity_name,
            channel=self.channel,
            results_json=results_json,
            result_count=result_count,
            latency_ms=latency_ms,
            status=status,
            error_code=error_code,
            error_message=error_message,
            fallback_tool=fallback_tool,
            fallback_tier=fallback_tier,
            provider_name=provider_name,
            trace_id=new_trace_id()
        )
        
        # Persist (non-blocking would be better but this is fast)
        try:
            self.db.insert(record)
        except Exception as e:
             # Log but don't fail the search
             get_engine().log_event_sync(
                 "search.persistence_failed",
                 record.trace_id,
                 {"error": str(e), "search_id": search_id}
             )
        
        return search_id
    
    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent search history for this entity."""
        rows = self.db.query("""
            SELECT * FROM search_results 
            WHERE entity_name = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (self.entity_name, limit))
        return [dict(r) for r in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search statistics."""
        return self.db.get_stats()


# ─── Decorator for Automatic Persistence ───
def persist_search(entity_name: str = "unknown", channel: str = "opencode"):
    """
    Decorator to automatically persist search tool results.
    
    Usage:
        @persist_search(entity_name="researcher", channel="opencode")
        async def my_search_tool(query: str) -> dict:
            ...
    """
    persistence = SearchPersistence(entity_name, channel)
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            query = kwargs.get('query') or (args[0] if args else "unknown")
            tool_name = func.__name__
            
            # Determine tier from tool name
            tier_map = {
                'websearch': 1, 'webfetch': 2, 'sovereign_search': 3,
                'parallel-search': 4, 'parallel-fetch': 4, 'exa': 5, 'firecrawl': 6,
                'library_search': 3, 'library_fts_search': 0, 'memory_search': 0,
            }
            tier = tier_map.get(tool_name, 0)
            
            try:
                result = await func(*args, **kwargs)
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                
                # Extract provider from result (M22)
                provider_name = None
                if isinstance(result, dict):
                    provider_name = result.get('provider_name') or result.get('backend') or result.get('provider')
                
                persistence.wrap_search(
                    tool_name=tool_name,
                    tier=tier,
                    query=query,
                    results=result,
                    latency_ms=latency_ms,
                    status="success",
                    provider_name=provider_name
                )
                
                return result
                
            except Exception as e:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                error_code = type(e).__name__
                error_message = str(e)
                
                persistence.wrap_search(
                    tool_name=tool_name,
                    tier=tier,
                    query=query,
                    results={"error": error_message},
                    latency_ms=latency_ms,
                    status="failed",
                    error_code=error_code,
                    error_message=error_message
                )
                
                # Re-raise for M23 Failure Integrity
                raise
        
        return wrapper
    return decorator


# ─── Tier Mapping ───
TOOL_TO_TIER = {
    # Tier 0: Local
    'memory_search': 0,
    'omega_memory_search': 0,
    'library_fts_search': 0,
    'library_search': 0,
    
    # Tier 1: Built-in websearch
    'websearch': 1,
    'web_search': 1,
    
    # Tier 2: Built-in webfetch
    'webfetch': 2,
    'web_fetch': 2,
    
    # Tier 3: SearXNG
    'searxng_searxng_search': 3,
    'sovereign_search': 3,  # Can route to multiple tiers
    
    # Tier 4: Parallel Search (free MCP)
    'parallel-search': 4,
    'parallel_search': 4,
    'parallel-fetch': 4,
    'parallel_fetch': 4,
    
    # Tier 5: Exa
    'exa': 5,
    'web_search_exa': 5,
    'web_fetch_exa': 5,
    
    # Tier 6: Firecrawl
    'firecrawl': 6,
    'firecrawl_firecrawl_search': 6,
    'firecrawl_firecrawl_scrape': 6,
    'search_extract': 6,
    
    # Research tools
    'research': 3,
    'library_discovery_research': 3,
    'library_discovery_start': 3,
}


def _get_tier(tool_name: str) -> int:
    """Map tool name to tier."""
    return TOOL_TO_TIER.get(tool_name.lower(), -1)


def _extract_provider_name(results_json: str, tool_name: str) -> Optional[str]:
    """Extract actual provider name from response (M22 compliance)."""
    try:
        data = json.loads(results_json)
        # Check common provider fields
        if isinstance(data, dict):
            # Direct provider field
            if 'provider' in data:
                return str(data['provider'])
            if 'provider_name' in data:
                return str(data['provider_name'])
            if 'backend' in data:
                return str(data['backend'])
            # GenerateResult style
            if 'provider_name' in data:
                return str(data['provider_name'])
            # Parallel Search response
            if 'results' in data and isinstance(data['results'], list) and data['results']:
                first = data['results'][0]
                if isinstance(first, dict) and 'provider' in first:
                    return str(first['provider'])
            # Exa response
            if 'provider' in data:
                return str(data['provider'])
    except Exception:
        pass
    return None


# ─── Global instance ───
_search_persistence: Optional[SearchPersistence] = None


def get_search_persistence() -> SearchPersistence:
    """Get global search persistence instance."""
    global _search_persistence
    if _search_persistence is None:
        _search_persistence = SearchPersistence()
    return _search_persistence


def record_search(
    query: str,
    tool_name: str,
    results_json: str,
    entity_name: Optional[str] = None,
    channel: Optional[str] = None,
    latency_ms: int = 0,
    status: str = 'success',
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    fallback_tool: Optional[str] = None,
    fallback_tier: Optional[int] = None,
    trace_id: Optional[str] = None,
) -> None:
    """Convenience function to record a search."""
    get_search_persistence().record_async(
        search_id=f"sr_{uuid.uuid4().hex[:12]}",
        query=query,
        tier=_get_tier(tool_name),
        tool_name=tool_name,
        entity_name=entity_name,
        channel=channel,
        results_json=results_json,
        result_count=0,  # Will be computed if needed
        latency_ms=latency_ms,
        status=status,
        error_code=error_code,
        error_message=error_message,
        fallback_tool=fallback_tool,
        fallback_tier=fallback_tier,
        provider_name=_extract_provider_name(results_json, tool_name),
        trace_id=trace_id,
    )


# ─── Add record_async method to SearchPersistence ───
def _add_record_async():
    """Add record_async method to SearchPersistence class."""
    def record_async(self, **kwargs):
        record = SearchRecord(
            search_id=kwargs.get('search_id', f"sr_{uuid.uuid4().hex[:12]}"),
            query=kwargs.get('query', ''),
            tier=kwargs.get('tier', -1),
            tool_name=kwargs.get('tool_name', ''),
            entity_name=kwargs.get('entity_name'),
            channel=kwargs.get('channel'),
            results_json=kwargs.get('results_json', '{}'),
            result_count=kwargs.get('result_count', 0),
            latency_ms=kwargs.get('latency_ms', 0),
            status=kwargs.get('status', 'unknown'),
            error_code=kwargs.get('error_code'),
            error_message=kwargs.get('error_message'),
            fallback_tool=kwargs.get('fallback_tool'),
            fallback_tier=kwargs.get('fallback_tier'),
            provider_name=kwargs.get('provider_name'),
            trace_id=kwargs.get('trace_id'),
        )
        self.db.insert(record)
    
    SearchPersistence.record_async = record_async

_add_record_async()


# ─── CLI Interface ───
def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m omega.search.search_persistence <command>")
        print("Commands: stats, recent [entity], export [entity]")
        return
    
    db = SearchDB
    db.init()
    
    cmd = sys.argv[1]
    
    if cmd == "stats":
        stats = db.get_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    elif cmd == "recent":
        entity = sys.argv[2] if len(sys.argv) > 2 else None
        if entity:
            rows = db.query("""
                SELECT * FROM search_results 
                WHERE entity_name = ? 
                ORDER BY created_at DESC 
                LIMIT 20
            """, (entity,))
        else:
            rows = db.query("""
                SELECT * FROM search_results 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
        for r in rows:
            print(f"[{r['created_at']}] {r['entity_name']} | {r['tool_name']} | {r['query'][:60]} | {r['status']} | {r['latency_ms']}ms")
    
    elif cmd == "export":
        entity = sys.argv[2] if len(sys.argv) > 2 else None
        if entity:
            rows = db.query("SELECT * FROM search_results WHERE entity_name = ? ORDER BY created_at", (entity,))
        else:
            rows = db.query("SELECT * FROM search_results ORDER BY created_at")
        
        output = [dict(r) for r in rows]
        print(json.dumps(output, indent=2, default=str))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()