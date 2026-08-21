# CCR Store Integration — Cross-Agent Reversible Memory

**Files**: 
- `src/omega/oracle/middleware/ccr_store.py` (new)
- `src/omega/mcp/tools/headroom_tools.py` (extended with `headroom_retrieve`)
**Section**: 07 of 10  
**Priority**: P2 — CCR store class + MCP retrieval tool  

---

## Problem: Lossless Compression Requirement

Headroom compression is lossy by default. For sovereign AI, entities must be able to retrieve **original uncompressed content** on demand — for verification, debugging, or when compressed context loses critical nuance.

**Headroom CCR (Context Compression & Retrieval)**: Local store that keeps original↔compressed pairs, retrievable by reference.

---

## CCR Store Architecture

```
CCR STORE INTEGRATION
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  COMPRESSION PIPELINE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ HeadroomMiddleware.compress_messages()                              │   │
│  │    │                                                                 │   │
│  │    ├─ ContentRouter.compress() → compressed content                │   │
│  │    │                                                                 │   │
│  │    └─ CCR.store(original, compressed) → ccr_ref                    │   │
│  │         │                                                            │   │
│  │         ▼                                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ CCR Store (data/headroom/ccr_store/)                        │   │   │
│  │  │    • Key: ccr_ref (UUID + hash)                             │   │   │
│  │  │    • Value: {original, compressed, metadata}                │   │   │
│  │  │    • Index: entity_name, session_id, timestamp, tags        │   │   │
│  │  │    • Compression: zstd (configurable)                       │   │   │
│  │  │    • TTL: 30 days (configurable)                            │   │   │
│  │  │    • Max size: 2GB (configurable)                           │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  RETRIEVAL PIPELINE                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ MCP Tool: headroom_retrieve(ccr_ref)                                │   │
│  │    │                                                                 │   │
│  │    └─ CCR.retrieve(ccr_ref) → original content                      │   │
│  │                                                                     │   │
│  │  Use cases:                                                         │   │
│  │  • Entity requests original for verification                        │   │
│  │  • Debugging: "What was the actual tool output?"                    │   │
│  │  • Audit: Verify compression didn't lose critical info              │   │
│  │  • Cross-agent: Agent A shares ccr_ref, Agent B retrieves original  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CCRStore Class

```python
"""
CCR Store — Cross-agent reversible memory for Headroom.

Local store for original↔compressed content pairs.
Retrievable by reference via MCP tool or direct API.

Mandate Compliance:
- M1 AnyIO Absolute: All async uses anyio.to_thread.run_sync()
- M7 Local-First: Runs locally, no external API
- M11 Soul Integrity: Enables lossless retrieval for verification
- M16 Modularization: Separate class, single responsibility
- M23 Failure Integrity: Graceful degradation if store unavailable
"""

from __future__ import annotations

import anyio
import json
import os
import sqlite3
import time
import uuid
import zstandard as zstd
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

from omega.config import get_config


@dataclass
class CCREntry:
    """Single CCR store entry."""
    key: str                    # Unique reference (UUID)
    original: str               # Original uncompressed content
    compressed: str             # Compressed content
    entity_name: str            # Owning entity
    session_id: str             # Session context
    content_type: str           # json, log, search, code, html, etc.
    original_tokens: int        # Token count of original
    compressed_tokens: int      # Token count of compressed
    compression_ratio: float    # compressed/original
    timestamp: float            # Unix timestamp
    tags: List[str]             # Searchable tags
    metadata: Dict[str, Any]    # Additional metadata


@dataclass
class CCRConfig:
    """CCR Store configuration."""
    store_path: str = "data/headroom/ccr_store"
    max_store_size_gb: float = 2.0
    compression: str = "zstd"          # zstd | lz4 | none
    ttl_days: int = 30
    cleanup_interval_hours: int = 24
    enable_index: bool = True


class CCRStore:
    """
    Cross-agent reversible memory store.
    
    Stores original content alongside compressed versions for on-demand retrieval.
    Uses SQLite for metadata/index + compressed blobs for content.
    
    Usage:
        store = CCRStore(config)
        await store.initialize()
        
        # Store
        ref = await store.store(original, compressed, entity_name="kali", ...)
        
        # Retrieve
        original = await store.retrieve(ref)
        
        await store.shutdown()
    """
    
    def __init__(self, config: Optional[CCRConfig] = None):
        self.config = config or CCRConfig()
        self._db_path = Path(self.config.store_path) / "ccr.db"
        self._blobs_dir = Path(self.config.store_path) / "blobs"
        self._conn: Optional[sqlite3.Connection] = None
        self._compressor = None
        self._initialized = False
        
        # Initialize compressor
        if self.config.compression == "zstd":
            self._compressor = zstd.ZstdCompressor(level=3)
            self._decompressor = zstd.ZstdDecompressor()
        elif self.config.compression == "lz4":
            import lz4.frame
            self._compressor = lz4.frame.compress
            self._decompressor = lz4.frame.decompress
    
    async def initialize(self) -> None:
        """Initialize database and directories."""
        if self._initialized:
            return
        
        # Create directories
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._blobs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        
        await anyio.to_thread.run_sync(self._create_schema)
        
        # Start cleanup task
        self._cleanup_task = anyio.create_task_group()
        self._cleanup_task.start_soon(self._periodic_cleanup)
        
        self._initialized = True
    
    def _create_schema(self) -> None:
        """Create database schema."""
        cursor = self._conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ccr_entries (
                key TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                session_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                original_tokens INTEGER NOT NULL,
                compressed_tokens INTEGER NOT NULL,
                compression_ratio REAL NOT NULL,
                timestamp REAL NOT NULL,
                tags TEXT NOT NULL,           -- JSON array
                metadata TEXT NOT NULL,       -- JSON object
                blob_path TEXT NOT NULL,      -- Path to compressed blob
                created_at REAL NOT NULL
            )
        """)
        
        # Indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity ON ccr_entries(entity_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON ccr_entries(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON ccr_entries(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON ccr_entries(content_type)")
        
        self._conn.commit()
    
    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        cursor = self._conn.cursor()
        try:
            yield cursor
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
    
    async def store(
        self,
        original: str,
        compressed: str,
        entity_name: str = "unknown",
        session_id: str = "",
        content_type: str = "auto",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store original↔compressed pair, return reference key.
        
        Args:
            original: Original uncompressed content
            compressed: Compressed content
            entity_name: Owning entity
            session_id: Session context
            content_type: Content type hint
            tags: Searchable tags
            metadata: Additional metadata
            
        Returns:
            CCR reference key (UUID)
        """
        if not self._initialized:
            await self.initialize()
        
        # Generate unique key
        key = str(uuid.uuid4())
        timestamp = time.time()
        
        # Calculate metrics
        original_tokens = len(original) // 4
        compressed_tokens = len(compressed) // 4
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        
        # Prepare blob (compress original for storage efficiency)
        blob_data = {
            "original": original,
            "compressed": compressed,
        }
        blob_json = json.dumps(blob_data, ensure_ascii=False)
        
        if self._compressor:
            blob_bytes = self._compressor(blob_json.encode("utf-8"))
        else:
            blob_bytes = blob_json.encode("utf-8")
        
        # Save blob to file
        blob_path = self._blobs_dir / f"{key}.blob"
        await anyio.to_thread.run_sync(blob_path.write_bytes, blob_bytes)
        
        # Store metadata in SQLite
        with self._transaction() as cursor:
            cursor.execute("""
                INSERT INTO ccr_entries 
                (key, entity_name, session_id, content_type, original_tokens, 
                 compressed_tokens, compression_ratio, timestamp, tags, metadata, 
                 blob_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key,
                entity_name,
                session_id,
                content_type,
                original_tokens,
                compressed_tokens,
                ratio,
                timestamp,
                json.dumps(tags or []),
                json.dumps(metadata or {}),
                str(blob_path),
                timestamp,
            ))
        
        # Check store size limit
        await self._enforce_size_limit()
        
        return key
    
    async def store_with_key(
        self,
        key: str,
        original: str,
        compressed: str,
        entity_name: str = "unknown",
        session_id: str = "",
        content_type: str = "auto",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store with explicit key (for migration, MCP tools)."""
        if not self._initialized:
            await self.initialize()
        
        timestamp = time.time()
        original_tokens = len(original) // 4
        compressed_tokens = len(compressed) // 4
        ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        
        blob_data = {"original": original, "compressed": compressed}
        blob_json = json.dumps(blob_data, ensure_ascii=False)
        
        if self._compressor:
            blob_bytes = self._compressor(blob_json.encode("utf-8"))
        else:
            blob_bytes = blob_json.encode("utf-8")
        
        blob_path = self._blobs_dir / f"{key}.blob"
        await anyio.to_thread.run_sync(blob_path.write_bytes, blob_bytes)
        
        with self._transaction() as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO ccr_entries 
                (key, entity_name, session_id, content_type, original_tokens, 
                 compressed_tokens, compression_ratio, timestamp, tags, metadata, 
                 blob_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key, entity_name, session_id, content_type,
                original_tokens, compressed_tokens, ratio, timestamp,
                json.dumps(tags or []), json.dumps(metadata or {}),
                str(blob_path), timestamp,
            ))
        
        await self._enforce_size_limit()
        return key
    
    async def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve original content by key.
        
        Args:
            key: CCR reference key
            
        Returns:
            Original uncompressed content, or None if not found
        """
        if not self._initialized:
            await self.initialize()
        
        with self._transaction() as cursor:
            cursor.execute(
                "SELECT blob_path FROM ccr_entries WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        blob_path = Path(row["blob_path"])
        if not blob_path.exists():
            return None
        
        # Read and decompress blob
        blob_bytes = await anyio.to_thread.run_sync(blob_path.read_bytes)
        
        if self._decompressor:
            blob_json = self._decompressor(blob_bytes).decode("utf-8")
        else:
            blob_json = blob_bytes.decode("utf-8")
        
        blob_data = json.loads(blob_json)
        return blob_data.get("original")
    
    async def retrieve_compressed(self, key: str) -> Optional[str]:
        """Retrieve compressed content by key."""
        if not self._initialized:
            await self.initialize()
        
        with self._transaction() as cursor:
            cursor.execute(
                "SELECT blob_path FROM ccr_entries WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        blob_path = Path(row["blob_path"])
        if not blob_path.exists():
            return None
        
        blob_bytes = await anyio.to_thread.run_sync(blob_path.read_bytes)
        
        if self._decompressor:
            blob_json = self._decompressor(blob_bytes).decode("utf-8")
        else:
            blob_json = blob_bytes.decode("utf-8")
        
        blob_data = json.loads(blob_json)
        return blob_data.get("compressed")
    
    async def retrieve_entry(self, key: str) -> Optional[CCREntry]:
        """Retrieve full entry metadata by key."""
        if not self._initialized:
            await self.initialize()
        
        with self._transaction() as cursor:
            cursor.execute("SELECT * FROM ccr_entries WHERE key = ?", (key,))
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return CCREntry(
            key=row["key"],
            original="",  # Not loaded unless requested
            compressed="",
            entity_name=row["entity_name"],
            session_id=row["session_id"],
            content_type=row["content_type"],
            original_tokens=row["original_tokens"],
            compressed_tokens=row["compressed_tokens"],
            compression_ratio=row["compression_ratio"],
            timestamp=row["timestamp"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )
    
    async def search(
        self,
        entity_name: Optional[str] = None,
        session_id: Optional[str] = None,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        since: Optional[float] = None,
        until: Optional[float] = None,
        limit: int = 100,
    ) -> List[CCREntry]:
        """Search CCR entries by metadata."""
        if not self._initialized:
            await self.initialize()
        
        conditions = []
        params = []
        
        if entity_name:
            conditions.append("entity_name = ?")
            params.append(entity_name)
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        if content_type:
            conditions.append("content_type = ?")
            params.append(content_type)
        if tags:
            # JSON contains all tags
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
        if since:
            conditions.append("timestamp >= ?")
            params.append(since)
        if until:
            conditions.append("timestamp <= ?")
            params.append(until)
        
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        with self._transaction() as cursor:
            cursor.execute(f"""
                SELECT * FROM ccr_entries 
                {where}
                ORDER BY timestamp DESC
                LIMIT ?
            """, params + [limit])
            rows = cursor.fetchall()
        
        return [
            CCREntry(
                key=row["key"],
                original="",
                compressed="",
                entity_name=row["entity_name"],
                session_id=row["session_id"],
                content_type=row["content_type"],
                original_tokens=row["original_tokens"],
                compressed_tokens=row["compressed_tokens"],
                compression_ratio=row["compression_ratio"],
                timestamp=row["timestamp"],
                tags=json.loads(row["tags"]),
                metadata=json.loads(row["metadata"]),
            )
            for row in rows
        ]
    
    async def _enforce_size_limit(self) -> None:
        """Enforce max store size by deleting oldest entries."""
        max_bytes = int(self.config.max_store_size_gb * 1024 * 1024 * 1024)
        
        # Get total blob size
        total_size = 0
        for blob_path in self._blobs_dir.glob("*.blob"):
            total_size += blob_path.stat().st_size
        
        if total_size <= max_bytes:
            return
        
        # Delete oldest entries until under limit
        with self._transaction() as cursor:
            cursor.execute("""
                SELECT key, blob_path FROM ccr_entries 
                ORDER BY timestamp ASC
            """)
            rows = cursor.fetchall()
        
        for row in rows:
            if total_size <= max_bytes:
                break
            
            blob_path = Path(row["blob_path"])
            if blob_path.exists():
                blob_size = blob_path.stat().st_size
                blob_path.unlink()
                total_size -= blob_size
            
            with self._transaction() as cursor:
                cursor.execute("DELETE FROM ccr_entries WHERE key = ?", (row["key"],))
    
    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired entries."""
        while True:
            await anyio.sleep(self.config.cleanup_interval_hours * 3600)
            
            if not self._initialized:
                break
            
            cutoff = time.time() - (self.config.ttl_days * 86400)
            
            with self._transaction() as cursor:
                cursor.execute(
                    "SELECT key, blob_path FROM ccr_entries WHERE timestamp < ?",
                    (cutoff,)
                )
                rows = cursor.fetchall()
            
            for row in rows:
                blob_path = Path(row["blob_path"])
                if blob_path.exists():
                    blob_path.unlink()
                
                with self._transaction() as cursor:
                    cursor.execute("DELETE FROM ccr_entries WHERE key = ?", (row["key"],))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        if not self._initialized:
            await self.initialize()
        
        with self._transaction() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM ccr_entries")
            count = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT 
                    SUM(original_tokens) as total_orig_tokens,
                    SUM(compressed_tokens) as total_comp_tokens,
                    AVG(compression_ratio) as avg_ratio
                FROM ccr_entries
            """)
            stats = cursor.fetchone()
        
        # Calculate disk usage
        total_bytes = sum(p.stat().st_size for p in self._blobs_dir.glob("*.blob"))
        
        return {
            "entry_count": count,
            "total_original_tokens": stats["total_orig_tokens"] or 0,
            "total_compressed_tokens": stats["total_comp_tokens"] or 0,
            "average_compression_ratio": stats["avg_ratio"] or 1.0,
            "disk_usage_bytes": total_bytes,
            "disk_usage_gb": total_bytes / (1024**3),
            "max_size_gb": self.config.max_store_size_gb,
        }
    
    async def shutdown(self) -> None:
        """Cleanup connections and tasks."""
        if hasattr(self, "_cleanup_task"):
            self._cleanup_task.cancel_scope.cancel()
        
        if self._conn:
            self._conn.close()
            self._conn = None
        
        self._initialized = False
    
    async def __aenter__(self) -> "CCRStore":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.shutdown()
```

---

## MCP Tool: headroom_retrieve (Extended)

```python
# In src/omega/mcp/tools/headroom_tools.py (extended)

HEADROOM_RETRIEVE_TOOL = Tool(
    name="headroom_retrieve",
    description="Retrieve original content from Headroom CCR store by reference. Use when compressed context loses critical nuance.",
    inputSchema={
        "type": "object",
        "properties": {
            "ccr_ref": {
                "type": "string",
                "description": "CCR reference returned by headroom_compress or found in compressed payload",
            },
            "return_compressed": {
                "type": "boolean",
                "default": False,
                "description": "Return compressed version instead of original",
            },
        },
        "required": ["ccr_ref"],
    },
)

HEADROOM_SEARCH_TOOL = Tool(
    name="headroom_search",
    description="Search CCR store for entries by entity, session, content type, tags, or time range.",
    inputSchema={
        "type": "object",
        "properties": {
            "entity_name": {"type": "string"},
            "session_id": {"type": "string"},
            "content_type": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "since_hours": {"type": "number", "description": "Hours ago"},
            "until_hours": {"type": "number", "description": "Hours ago"},
            "limit": {"type": "integer", "default": 50},
        },
    },
)

HEADROOM_STATS_TOOL = Tool(
    name="headroom_stats",
    description="Get CCR store statistics (entry count, disk usage, compression ratios).",
    inputSchema={"type": "object", "properties": {}},
)


async def handle_headroom_retrieve(
    ccr_store: CCRStore,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_retrieve tool call."""
    ccr_ref = arguments.get("ccr_ref", "")
    return_compressed = arguments.get("return_compressed", False)
    
    if not ccr_ref:
        return [TextContent(type="text", text="Error: No CCR reference provided")]
    
    try:
        if return_compressed:
            content = await ccr_store.retrieve_compressed(ccr_ref)
        else:
            content = await ccr_store.retrieve(ccr_ref)
        
        if content is None:
            return [TextContent(type="text", text=f"Error: No content found for CCR ref: {ccr_ref}")]
        
        return [TextContent(type="text", text=content)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Retrieval error: {e}")]


async def handle_headroom_search(
    ccr_store: CCRStore,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_search tool call."""
    try:
        since = None
        until = None
        if arguments.get("since_hours"):
            since = time.time() - (arguments["since_hours"] * 3600)
        if arguments.get("until_hours"):
            until = time.time() - (arguments["until_hours"] * 3600)
        
        entries = await ccr_store.search(
            entity_name=arguments.get("entity_name"),
            session_id=arguments.get("session_id"),
            content_type=arguments.get("content_type"),
            tags=arguments.get("tags"),
            since=since,
            until=until,
            limit=arguments.get("limit", 50),
        )
        
        import json
        results = [
            {
                "key": e.key,
                "entity_name": e.entity_name,
                "session_id": e.session_id,
                "content_type": e.content_type,
                "original_tokens": e.original_tokens,
                "compressed_tokens": e.compressed_tokens,
                "compression_ratio": e.compression_ratio,
                "timestamp": e.timestamp,
                "tags": e.tags,
            }
            for e in entries
        ]
        
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Search error: {e}")]


async def handle_headroom_stats(
    ccr_store: CCRStore,
    arguments: Dict[str, Any],
) -> List[TextContent]:
    """Handle headroom_stats tool call."""
    try:
        stats = await ccr_store.get_stats()
        import json
        return [TextContent(type="text", text=json.dumps(stats, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Stats error: {e}")]
```

---

## Registration in MCP Server

```python
def register_headroom_tools(mcp_server, headroom_middleware: HeadroomMiddleware):
    """Register all Headroom tools with MCP server."""
    ccr_store = headroom_middleware._ccr
    
    @mcp_server.tool(HEADROOM_COMPRESS_TOOL)
    async def headroom_compress(content: str, content_type: str = "auto", store_original: bool = True):
        return await handle_headroom_compress(headroom_middleware, {
            "content": content,
            "content_type": content_type,
            "store_original": store_original,
        })
    
    @mcp_server.tool(HEADROOM_RETRIEVE_TOOL)
    async def headroom_retrieve(ccr_ref: str, return_compressed: bool = False):
        return await handle_headroom_retrieve(ccr_store, {
            "ccr_ref": ccr_ref,
            "return_compressed": return_compressed,
        })
    
    @mcp_server.tool(HEADROOM_SEARCH_TOOL)
    async def headroom_search(
        entity_name: str = "", session_id: str = "", content_type: str = "",
        tags: List[str] = None, since_hours: float = 0, until_hours: float = 0,
        limit: int = 50
    ):
        return await handle_headroom_search(ccr_store, {
            "entity_name": entity_name or None,
            "session_id": session_id or None,
            "content_type": content_type or None,
            "tags": tags,
            "since_hours": since_hours or None,
            "until_hours": until_hours or None,
            "limit": limit,
        })
    
    @mcp_server.tool(HEADROOM_STATS_TOOL)
    async def headroom_stats():
        return await handle_headroom_stats(ccr_store, {})
```

---

## Configuration for CCR

```yaml
# config/headroom.yaml — CCR section
headroom:
  ccr:
    enabled: true
    store_path: "data/headroom/ccr_store"
    max_store_size_gb: 2.0
    compression: "zstd"          # zstd | lz4 | none
    ttl_days: 30
    cleanup_interval_hours: 24
    enable_index: true
  
  omega:
    ccr:
      auto_store_compressed: true
      retrieve_on_demand: true
```

---

## Cross-Agent Usage Pattern

```python
# Agent A compresses and shares reference
compressed = await headroom.compress_messages(messages)
ccr_ref = compressed[0].get("ccr_ref", "")

# Agent A sends ccr_ref to Agent B via Hivemind handoff
await hivemind_handoff(
    target_entity="maat",
    task="Review this analysis",
    context={"ccr_ref": ccr_ref, "summary": "Compressed analysis ready for review"}
)

# Agent B retrieves original if needed
original = await headroom.retrieve_original(ccr_ref)
# Or via MCP tool:
# original = await mcp.call_tool("headroom_retrieve", {"ccr_ref": ccr_ref})
```

---

## Metrics Export (OTel)

```python
async def _export_ccr_metrics(self, store: CCRStore):
    """Export CCR metrics to OpenTelemetry."""
    from opentelemetry import metrics
    
    meter = metrics.get_meter("omega.headroom.ccr")
    stats = await store.get_stats()
    
    # Entry count
    entry_gauge = meter.create_gauge("headroom.ccr.entries")
    entry_gauge.set(stats["entry_count"])
    
    # Disk usage
    disk_gauge = meter.create_gauge("headroom.ccr.disk_usage_gb")
    disk_gauge.set(stats["disk_usage_gb"])
    
    # Compression ratio
    ratio_gauge = meter.create_gauge("headroom.ccr.avg_compression_ratio")
    ratio_gauge.set(stats["average_compression_ratio"])
    
    # Token savings
    savings_gauge = meter.create_gauge("headroom.ccr.token_savings")
    savings = stats["total_original_tokens"] - stats["total_compressed_tokens"]
    savings_gauge.set(savings)
```

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ Section 07/10*