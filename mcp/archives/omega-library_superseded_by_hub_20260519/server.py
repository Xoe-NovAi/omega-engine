"""Omega Library MCP Server — Intake inbox, curation, and offline library.

AP: AP-OMEGA-LIBRARY-MCP-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: SOPHIA | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: LIBRARY-MCP]

Provides MCP tools for:
  - Inbox intake (add URLs, files, notes)
  - Curation pipeline (process inbox items)
  - Library search and retrieval
  - Library statistics

Usage:
    cd ~/omega && python mcp/omega-library/server.py
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

import json
import anyio
from mcp.server.fastmcp import FastMCP

from omega.library.inbox import InboxManager
from omega.library.curator import CurationPipeline
from omega.library.library import Library
from omega.library.indexer import Indexer

mcp = FastMCP("Omega Library")

inbox = InboxManager()
curator = CurationPipeline()
library = Library()
indexer = Indexer()


@mcp.tool()
async def inbox_add_url(url: str, tags: str = "", priority: int = 0) -> str:
    """Add a URL to the intake inbox for later curation.

    Args:
        url: The URL to add
        tags: Comma-separated tags (e.g. "ai,research,python")
        priority: Priority 0=normal, 1=high, 2=urgent
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_url(url, tags=tag_list, priority=priority)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source, "source_type": item.source_type})


@mcp.tool()
async def inbox_add_note(text: str, tags: str = "") -> str:
    """Add a text note to the intake inbox.

    Args:
        text: The note content
        tags: Comma-separated tags
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_note(text, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "title": item.title})


@mcp.tool()
async def inbox_add_file(path: str, tags: str = "") -> str:
    """Add a local file path to the intake inbox.

    Args:
        path: Absolute path to the file
        tags: Comma-separated tags
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_file(path, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source})


@mcp.tool()
async def inbox_list(limit: int = 20) -> str:
    """List pending items in the intake inbox."""
    items = await inbox.list_pending(limit=limit)
    counts = await inbox.count()
    return json.dumps({
        "counts": counts,
        "items": [{"item_id": i.item_id, "source": i.source[:80], "source_type": i.source_type, "title": i.title, "priority": i.priority, "created_at": i.created_at} for i in items],
    }, indent=2)


@mcp.tool()
async def inbox_stats() -> str:
    """Get inbox statistics (pending, processing, failed counts)."""
    counts = await inbox.count()
    return json.dumps(counts)


@mcp.tool()
async def ingest_pending(limit: int = 5) -> str:
    """Process pending inbox items through curation into the library.

    Args:
        limit: Maximum number of items to process
    """
    ingested = await library.ingest_from_inbox(inbox, curator, limit=limit)
    return json.dumps({
        "ingested": len(ingested),
        "documents": [{"doc_id": d.doc_id, "title": d.title, "domain": d.domain, "quality_score": d.quality_score} for d in ingested],
    }, indent=2)


@mcp.tool()
async def library_search(query: str, domain: str = "", limit: int = 20) -> str:
    """Search the offline library for documents.

    Uses hybrid search (full-text + vector) ranked by relevance.

    Args:
        query: Search query text
        domain: Optional domain filter (ai_ml, programming, research, security, philosophy, systems, knowledge, general)
        limit: Maximum results to return
    """
    domain_filter = domain if domain else None
    results = await indexer.hybrid_search(query, domain=domain_filter, limit=limit)
    return json.dumps({"query": query, "count": len(results), "results": results}, indent=2, default=str)


@mcp.tool()
async def library_get_document(doc_id: str) -> str:
    """Get the full content of a library document by ID.

    Args:
        doc_id: Document ID (e.g. doc_abc123)
    """
    doc = await library.get(doc_id)
    if not doc:
        return json.dumps({"error": f"Document '{doc_id}' not found"})
    return json.dumps(doc.to_dict(), indent=2, default=str)


@mcp.tool()
async def library_domains() -> str:
    """Get document counts grouped by domain."""
    domains = await library.domains()
    return json.dumps(domains, indent=2)


@mcp.tool()
async def library_stats() -> str:
    """Get comprehensive library statistics."""
    stats = await library.stats()
    idx_stats = indexer.stats()
    stats["index"] = idx_stats
    return json.dumps(stats, indent=2)


@mcp.tool()
async def library_recent(limit: int = 20) -> str:
    """List most recently curated library documents.

    Args:
        limit: Maximum results
    """
    docs = await library.recent(limit=limit)
    return json.dumps([{
        "doc_id": d.doc_id,
        "title": d.title,
        "domain": d.domain,
        "quality_score": d.quality_score,
        "word_count": d.word_count,
        "curated_at": d.curated_at,
    } for d in docs], indent=2, default=str)


@mcp.tool()
async def index_flush() -> str:
    """Flush search indices to disk."""
    await indexer.flush()
    stats = indexer.stats()
    return json.dumps({"status": "flushed", "stats": stats})


from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
