# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# [id-soft: quake3-1999] Hub Tools — netchan-style typed message dispatch for Hivemind coordination tools

"""Omega Hub — MCP Tool Definitions (extracted from server.py Phase 1b).

AP: AP-OMEGA-HUB-TOOLS-v1.0.0

All MCP tool functions live here and register themselves with the ``mcp``
FastMCP instance via side-effect import. The ``mcp`` instance is created in
``server.py`` BEFORE this module is imported, so the circular import
(``tools.py`` → ``server.py`` for ``mcp``) resolves correctly.

Dependency bartprint (M16):
  - mcp_servers.omega_hub.server: ``mcp`` instance (circular, resolved)
  - mcp_servers.omega_hub.middleware: ``m9_safe`` decorator
  - mcp_servers.omega_hub.state: All service singletons + hivemind state
  - mcp_servers.omega_hub.background: ``_run_discovery_background``
  - omega.observability: ``new_trace_id``, ``get_engine``
  - omega.(await oracle).security: ``tdp_wrap``, ``determine_url_taint``
  - omega.ics: ``render as ics_render_logic``
  - omega.memory_store: ``get_memory_store``

Public API:
  Each ``@mcp.tool()`` decorated function is an MCP tool. None are
  re-exported — registration is via side-effect on import.
"""

import json
import logging
import os
import uuid
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
from dataclasses import asdict

from omega.library.research import RESEARCH_DEPTHS

import anyio
import yaml
from mcp.server.fastmcp import Context

# ── mcp instance (circular import — resolves because mcp is created before this import) ──
from mcp_servers.omega_hub.server import mcp

# ── Extracted middleware ──
from mcp_servers.omega_hub.middleware import m9_safe

# ── GitHub Integration Tools ──
import mcp_servers.omega_hub.github_tools as github_tools # noqa: F401

# ── State (service singletons + hivemind state) ──
from mcp_servers.omega_hub import state as _state
from mcp_servers.omega_hub.state import (
    _require_service,
    _current_entity, HEARTBEAT_TTL, HALL_OF_RECORDS,
    _hot_store, _hot_store_lock, _awareness, _awareness_lock,
    EXTENDED_SAFETY_TTL_DEFAULT,
    _get_intent_matcher,
    HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE,
    LOCKS_BASE, METRICS_PATH,
    _make_agent_id, _cold_path, _latest_path, _find_packet_path,
    # P0-2: Sharded hot store API
    hot_store_set, hot_store_get, hot_store_get_all,
    # P0-4: Cold-store awareness cache
    get_cached_cold_awareness, invalidate_awareness_cache,
    # Extended session TTL now stored in _awareness[agent_id]["extended_ttl"]
    EXTENDED_SAFETY_TTL_DEFAULT,
    # P1-6: Handoff packet index
    handoff_index_add, handoff_index_move, handoff_index_remove,
)

class PathProxy:
    """Dynamic proxy for PROJECT_ROOT to allow monkeypatching in tests."""
    def __getattr__(self, item):
        return getattr(_state.PROJECT_ROOT, item)
    def __truediv__(self, other):
        return _state.PROJECT_ROOT / other
    def __str__(self):
        return str(_state.PROJECT_ROOT)
    def __repr__(self):
        return repr(_state.PROJECT_ROOT)

PROJECT_ROOT = PathProxy()

class AsyncServiceProxy:
    """Async proxy for lazy-loaded service singletons from state."""
    def __init__(self, name: str):
        self._name = name
    def __await__(self):
        return _state.get_service(self._name).__await__()
    def __bool__(self):
        return getattr(_state, self._name) is not None

registry = AsyncServiceProxy("registry")
oracle = AsyncServiceProxy("oracle")
hierarchy = AsyncServiceProxy("hierarchy")
inbox = AsyncServiceProxy("inbox")
curator = AsyncServiceProxy("curator")
library = AsyncServiceProxy("library")
indexer = AsyncServiceProxy("indexer")
discovery = AsyncServiceProxy("discovery")
research_engine = AsyncServiceProxy("research_engine")
sovereign_search_service = AsyncServiceProxy("sovereign_search_service")
gateway = AsyncServiceProxy("gateway")

# ── M16-compliant path resolution ──────────────────────────────────────────────
# [M16: Modularization & Portability] Read omega_library paths from env var
# with canonical default. This avoids hardcoded paths in core engine code.
_OMEGA_LIBRARY_PATH = Path(os.environ.get(
    "OMEGA_LIBRARY_PATH",
    "/media/arcana-novai/omega_library"
))
_OMEGA_MODELS_PATH = Path(os.environ.get(
    "OMEGA_MODELS_PATH",
    str(_OMEGA_LIBRARY_PATH / "models" / "gguf")
))
_OMEGA_PODMAN_STORAGE = Path(os.environ.get(
    "OMEGA_PODMAN_STORAGE",
    str(_OMEGA_LIBRARY_PATH / "podman-storage")
))

# ── Library inbox directory constants ──
INBOX_DIR = PROJECT_ROOT / "data" / "library" / "inbox"
PROCESSING_DIR = PROJECT_ROOT / "data" / "library" / "processing"
FAILED_DIR = PROJECT_ROOT / "data" / "library" / "dead"


# ── Background tasks ──
from mcp_servers.omega_hub.background import (
    _run_discovery_background,
    _reap_stale_locks,
    _write_metrics,
)

# ── Deprecation helper ──
def _deprecated(tool_name: str, replacement: str) -> None:
    """Log a deprecation warning for an old tool name."""
    logger.warning(
        "DEPRECATED: '%s' is deprecated. Use '%s' instead. "
        "This tool will be removed in a future version.",
        tool_name, replacement
    )

# ── Omega engine internals ──
from omega.observability import new_trace_id, get_engine
from omega.observability.sovereignty import get_sovereignty_ratio
from omega.oracle.security import tdp_wrap, determine_url_taint
from omega.ics import render as ics_render_logic
from omega.memory_store import get_memory_store
from omega.search import SearchPersistence

logger = logging.getLogger("omega.hub")
@m9_safe("headroom_retrieve")
@mcp.tool()
async def headroom_retrieve(ref_id: str) -> str:
    _require_service()
    """Retrieve the original, uncompressed content for a given reference ID.
    
    This is used when semantic compression has been too aggressive and the 
    agent needs the high-fidelity original text to perform a precise task.
    
    Args:
        ref_id: The reference ID provided in the compressed context block.
        
    Returns:
        The original uncompressed text or an error message.
    """
    result = await (await oracle).retrieve_headroom_content(ref_id)
    return result

@m9_safe("oracle_talk")
@mcp.tool()
async def oracle_talk(query: str) -> str:
    _require_service()
    """Route a query through the Omega Oracle. Speculative decoding handled internally.
    
    Args:
        query: The natural language query or command to route.
        
    Returns:
        JSON string containing the response text, entity, slots, and metadata.
    """
    response = await (await oracle).talk(query)
    _current_entity.set(response.entity)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "slots": response.slots,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
        "backend": response.backend,
        "escalated": response.escalated,
    }, indent=2)


@m9_safe("oracle_summon")
@mcp.tool()
async def oracle_summon(entity_name: str, query: str) -> str:
    _require_service()
    """Directly summon a specific entity by name.
    
    Args:
        entity_name: The name of the entity to summon.
        query: The message or task for the summoned entity.
        
    Returns:
        JSON string containing the response text and entity metadata.
    """
    response = await (await oracle).summon(entity_name, query)
    _current_entity.set(response.entity)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "slots": response.slots,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
    }, indent=2)


@m9_safe("oracle_summon_local")
@mcp.tool()
async def oracle_summon_local(entity_name: str, query: str, model: str) -> str:
    _require_service()
    """Summon an entity with a specific model override.
    
    [D118 Dual-Inference Mandate] Bypasses TriageRouter and routes to the
    specified model directly. Use for opt-in local routing (MaKaLi council).
    
    Args:
        entity_name: Name of the entity to summon
        query: The user query
        model: Model name to use (e.g., 'qwen3-1.7b', 'rocracoon-3b-instruct')
        
    Returns:
        JSON string containing the local model response or an error hint.
    """
    response = await (await oracle).summon(entity_name, query, model_override=model)
    _current_entity.set(response.entity)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "slots": response.slots,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
        "model_override": model,
    }, indent=2)


@m9_safe("spawn_local_worker")
@mcp.tool()
async def spawn_local_worker(
    task: str,
    model: str = "qwen3-1.7b",
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    entity: str = "roc_racoon",
) -> str:
    """Fire-and-forget local inference using GGUF models. Returns task_id immediately.
    
    [Phase 2 Local Worker Pool] Offloads work to background local models.
    Use for: mining, distillation, pattern extraction, synthesis, pre-commit checks.
    
    Args:
        task: The prompt/task for local inference
        model: GGUF model to use (default: qwen3-1.7b)
        system_prompt: System prompt (default: "")
        max_tokens: Max tokens to generate (default: 1024)
        temperature: Sampling temperature (default: 0.7)
        entity: Entity name for tracking (default: roc_racoon)
        
    Returns:
        JSON string with task_id and status.
    """
    _require_service()
    from omega.oracle.local_worker_pool import queue_local_task
    task_id = await queue_local_task(
        prompt=task,
        model=model,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        entity=entity,
    )
    return json.dumps({
        "task_id": task_id,
        "status": "queued",
        "model": model,
        "entity": entity,
        "message": f"Task queued. Check status with local_queue_status or local_queue_cat.",
    }, indent=2)


@m9_safe("local_queue_status")
@mcp.tool()
async def local_queue_status(task_id: str) -> str:
    """Get status of a local worker task.
    
    Args:
        task_id: The task ID returned by spawn_local_worker.
        
    Returns:
        JSON string with task status.
    """
    _require_service()
    from omega.oracle.local_worker_pool import get_local_task_status
    status = await get_local_task_status(task_id)
    if status is None:
        return json.dumps({"error": f"Task '{task_id}' not found"})
    return json.dumps(status, indent=2)


@m9_safe("local_queue_cat")
@mcp.tool()
async def local_queue_cat(task_id: str) -> str:
    """Get result of a completed local worker task.
    
    Args:
        task_id: The task ID returned by spawn_local_worker.
        
    Returns:
        JSON string with task result.
    """
    _require_service()
    from omega.oracle.local_worker_pool import get_local_task_result
    result = await get_local_task_result(task_id)
    if result is None:
        return json.dumps({"error": f"Result for '{task_id}' not found. Task may not be completed yet."})
    return json.dumps({
        "task_id": result.task_id,
        "text": result.text,
        "model": result.model,
        "provider_name": result.provider_name,
        "tokens_generated": result.tokens_generated,
        "latency_ms": result.latency_ms,
        "entity": result.entity,
        "trace_id": result.trace_id,
        "completed_at": result.completed_at,
        "error": result.error,
    }, indent=2)


@m9_safe("local_queue_list")
@mcp.tool()
async def local_queue_list(
    status: str = "all",
    limit: int = 20,
    entity: str = "",
) -> str:
    """List local worker tasks with optional filters.
    
    Args:
        status: Filter by status (queued/completed/dead/all)
        limit: Max tasks to show (default: 20)
        entity: Filter by entity name
        
    Returns:
        JSON string with list of tasks.
    """
    _require_service()
    from omega.oracle.local_worker_pool import list_local_tasks, TaskStatus
    status_enum = None
    if status != "all":
        try:
            status_enum = TaskStatus(status.lower())
        except ValueError:
            return json.dumps({"error": f"Invalid status: {status}. Use: queued, completed, dead, all"})

    tasks = await list_local_tasks(status=status_enum, limit=limit, entity=entity if entity else None)
    return json.dumps(tasks, indent=2)


@m9_safe("oracle_list_entities")
@mcp.tool()
async def oracle_list_entities() -> str:
    _require_service()
    """List all entities in the Omega pantheon.
    
    Returns:
        JSON string containing a list of all entities and their primary attributes.
    """
    entities = await anyio.to_thread.run_sync((await registry).list)
    result = [{
        "name": e.name,
        "slots": e.slots,
        "role": e.role,
        "domains": e.domains,
        "model": e.model,
    } for e in entities]
    return json.dumps(result, indent=2)


@m9_safe("oracle_entity_info")
@mcp.tool()
async def oracle_entity_info(name: str) -> str:
    _require_service()
    """Get detailed information about a specific entity.
    
    Args:
        name: Name or fragment of the entity name to look up.
        
    Returns:
        JSON string containing the full entity profile or an error.
    """
    async def _get():
        return (await registry).get(name) or (await registry).find_by_name_fragment(name)
    entity = await anyio.to_thread.run_sync(_get)
    if not entity:
        return json.dumps({"error": f"Entity '{name}' not found"})
    return json.dumps({
        "name": entity.name,
        "slots": entity.slots,
        "role": entity.role,
        "personality": entity.personality,
        "metadata": entity.metadata,  # WAD content: pantheon, element, chakra, sigil, etc.
        "domains": entity.domains,
        "model": entity.model,
        "temperature": entity.temperature,
    }, indent=2)

@m9_safe("sovereign_search")
@mcp.tool()
async def sovereign_search(query: str, entity_name: str = "SOPHIA", limit: int = 10, force_tier: Optional[int] = None) -> str:
    _require_service()
    """Execute the 6-Tier Sovereign Search Protocol (SSP-V2).
    
    T0 (Local) -> T1 (websearch) -> T2 (webfetch) -> T3 (SearXNG) -> T4 (Parallel Search) -> T5 (Exa) -> T6 (Firecrawl).
    T0 includes both MemoryStore and a local filesystem cache.
    
    Args:
        query: The search query.
        entity_name: The entity context for T0 cache and routing signals.
        limit: Maximum results per tier.
        force_tier: Optional tier to force execution (0-6).
    """
    import time
    start = time.perf_counter()
    
    result = await (await sovereign_search_service).search(query, entity_name, limit=limit, force_tier=force_tier)
    
    # Persist search result
    latency_ms = int((time.perf_counter() - start) * 1000)
    try:
        persistence = SearchPersistence(entity_name=entity_name, channel="opencode")
        persistence.wrap_search(
            tool_name="sovereign_search",
            tier=result.get("final_tier", 0),
            query=query,
            results=result,
            latency_ms=latency_ms,
            status="success" if result.get("status") != "error" else "failed",
            error_code=result.get("error_code"),
            error_message=result.get("error"),
            provider_name=result.get("provider_name"),
        )
    except Exception as e:
        logger.warning(f"Search persistence failed: {e}")
    
    return json.dumps(result, indent=2)

@m9_safe("search_extract")
@mcp.tool()
async def search_extract(query: str, limit: int = 10) -> str:
    _require_service()
    """Force a T6 (Firecrawl) Deep Extraction for a specific query.
    
    Bypasses the tiered routing to ensure full-page content extraction
    and structured markdown results.
    
    Args:
        query: The query to extract content for.
        limit: Number of sources to scrape.
    """
    import time
    start = time.perf_counter()
    
    result = await (await sovereign_search_service).extract(query, limit=limit)
    
    # Persist search result
    latency_ms = int((time.perf_counter() - start) * 1000)
    try:
        persistence = SearchPersistence(entity_name="researcher", channel="opencode")
        persistence.wrap_search(
            tool_name="search_extract",
            tier=6,
            query=query,
            results=result,
            latency_ms=latency_ms,
            status="success",
            provider_name="firecrawl",
        )
    except Exception as e:
        logger.warning(f"Search persistence failed: {e}")

    return json.dumps({"result": result, "tier": 6, "provider": "firecrawl"}, indent=2)


# === HIVEMIND TOOLS (7) ===
# === LIBRARY TOOLS (12) ===

@m9_safe("library_ingest_pending")
@mcp.tool()
async def library_ingest_pending(limit: int = 5) -> str:
    _require_service()
    """Process pending inbox items through curation into the (await library).
    
    Args:
        limit: Maximum number of items to process in this batch.
        
    Returns:
        JSON string containing the number of ingested items and their summaries.
    """
    ingested = await (await library).ingest_from_inbox(inbox, curator, limit=limit)
    return json.dumps({
        "ingested": len(ingested),
        "documents": [{"doc_id": d.doc_id, "title": d.title, "domain": d.domain, "quality_score": d.quality_score} for d in ingested],
    }, indent=2)


@m9_safe("library_search")
@tdp_wrap(source="library_search", taint_level=1)
@mcp.tool()
async def library_search(query: str, domain: str = "", limit: int = 20) -> str:
    _require_service()
    """Search the offline library for documents. Uses hybrid search.
    
    Args:
        query: The search query (max 500 chars).
        domain: Optional domain filter (e.g., 'security', 'research').
        limit: Maximum number of results to return.
        
    Returns:
        JSON string containing the search results and hit count.
    """
    import time
    start = time.perf_counter()
    
    # P1-C: MCP-layer input guards (M-A4 compliance fix, defense-in-depth)
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})
    
    # Use module-level sovereign_search_service (not a fresh instance)
    report = await (await sovereign_search_service).search(
        query, entity_name=domain if domain else "general", limit=limit
    )
    
    # Persist search result
    latency_ms = int((time.perf_counter() - start) * 1000)
    try:
        persistence = SearchPersistence(entity_name=domain if domain else "general", channel="opencode")
        persistence.wrap_search(
            tool_name="library_search",
            tier=report.get("final_tier", 0),
            query=query,
            results=report,
            latency_ms=latency_ms,
            status="success" if report.get("status") != "error" else "failed",
            error_code=report.get("error_code"),
            error_message=report.get("error"),
            provider_name=report.get("provider_name"),
        )
    except Exception as e:
        logger.warning(f"Search persistence failed: {e}")
    
    return json.dumps({
        "query": query, 
        "status": report["status"],
        "final_tier": report["final_tier"],
        "primary_finding": report["primary_finding"],
        "evidence": report["evidence"],
        "fallback_log": report["fallback_log"],
        "results": report["primary_finding"] if isinstance(report["primary_finding"], list) else [report["primary_finding"]]
    }, indent=2, default=str)


@m9_safe("library_fts_search")
@tdp_wrap(source="library_fts_search", taint_level=1)
@mcp.tool()
async def library_fts_search(query: str, domain: str = "", limit: int = 10) -> str:
    _require_service()
    """Search the local Library knowledge base using FTS5 full-text search + vector hybrid.
    This searches curated documents (research specs, API references, guides) stored locally.
    For web search, use `sovereign_search` instead.
    
    Args:
        query: The search query (max 500 chars).
        domain: Optional domain filter (e.g., 'networking', 'testing', 'security').
        limit: Maximum number of results to retrieve (default 10).
        
    Returns:
        JSON string containing search results with doc_id, title, summary, score, domain.
    """
    import time
    start = time.perf_counter()
    
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})

    try:
        results = await (await library).search(query, domain=domain if domain else None, limit=limit)
        formatted = []
        for doc in results:
            formatted.append({
                "doc_id": doc.doc_id,
                "title": doc.title,
                "summary": doc.summary[:300] if doc.summary else "",
                "domain": doc.domain,
                "quality_score": doc.quality_score,
                "tags": doc.tags if doc.tags else [],
                "word_count": doc.word_count,
            })
        
        # Persist search result
        latency_ms = int((time.perf_counter() - start) * 1000)
        try:
            persistence = SearchPersistence(entity_name=domain if domain else "general", channel="opencode")
            persistence.wrap_search(
                tool_name="library_fts_search",
                tier=0,  # Local search = Tier 0
                query=query,
                results={"results": formatted, "count": len(formatted)},
                latency_ms=latency_ms,
                status="success",
                provider_name="local_fts5",
            )
        except Exception as e:
            logger.warning(f"Search persistence failed: {e}")
        
        return json.dumps({
            "query": query,
            "count": len(formatted),
            "results": formatted,
            "source": "library_fts5"
        }, indent=2)
    except Exception as e:
        logger.warning("library_fts_search failed: %s", e)
        return json.dumps({"error": str(e), "count": 0, "results": []})


@m9_safe("library_get_document")
@mcp.tool()
async def library_get_document(doc_id: str) -> str:
    _require_service()
    """Get the full content of a library document by ID.
    
    Args:
        doc_id: The unique identifier of the document.
        
    Returns:
        JSON string containing the complete document content and metadata.
    """
    doc = await (await library).get(doc_id)
    if not doc:
        return json.dumps({"error": f"Document '{doc_id}' not found"})
    return json.dumps(doc.to_dict(), indent=2, default=str)


@m9_safe("library_domains")
@mcp.tool()
async def library_domains() -> str:
    _require_service()
    """Get document counts grouped by domain.
    
    Returns:
        JSON string containing domain names and their document counts.
    """
    domains = await (await library).domains()
    return json.dumps(domains, indent=2)


@m9_safe("library_stats")
@mcp.tool()
async def library_stats() -> str:
    _require_service()
    """Get comprehensive library statistics.
    
    Returns:
        JSON string containing library and indexer usage metrics.
    """
    # P1-D: Guard (await indexer).stats() outside the library's error boundary (M-A6 fix)
    stats = await (await library).stats()
    try:
        idx_stats = (await indexer).stats()
        stats["index"] = idx_stats
    except Exception as e:
        logger.warning("library_stats: (await indexer).stats() failed: %s", e)
        stats["index"] = {"error": str(e)}
    return json.dumps(stats, indent=2)


@m9_safe("library_recent")
@mcp.tool()
async def library_recent(limit: int = 20) -> str:
    _require_service()
    """List most recently curated library documents.
    
    Args:
        limit: Maximum number of recent documents to retrieve.
        
    Returns:
        JSON string containing a list of recently ingested document summaries.
    """
    docs = await (await library).recent(limit=limit)
    return json.dumps([{
        "doc_id": d.doc_id,
        "title": d.title,
        "domain": d.domain,
        "quality_score": d.quality_score,
        "word_count": d.word_count,
        "curated_at": d.curated_at,
    } for d in docs], indent=2, default=str)


# === MEMORY TOOLS (6) ===
# Sterile-named tools (P2 DataStore — Wave 1.5 P1)
# These wrap MemoryStore methods with context params for MCP client compatibility.
# The `omega_memory_*` tools above remain for backward compatibility.

@m9_safe("omega_memory_search")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def omega_memory_search(query: str, entity_name: str, limit: int = 20) -> str:
    """Search across conversation history using Hybrid Search (RRF: FTS5 + Vector).
    
    Provides sovereign memory retrieval for specific entities by merging
    keyword results (BM25) and semantic results (Vector).
    
    Args:
        query: The search query (natural language or keywords).
        entity_name: The sovereign owner of the memory (REQUIRED).
        limit: Maximum number of results to return.
        
    Returns:
        JSON string containing the matched exchanges and RRF re-ranking.
    """
    import time
    start = time.perf_counter()
    
    memory_store = get_memory_store()
    results = await memory_store.search(query, entity_name, limit)
    
    # Persist search result
    latency_ms = int((time.perf_counter() - start) * 1000)
    try:
        persistence = SearchPersistence(entity_name=entity_name, channel="opencode")
        persistence.wrap_search(
            tool_name="omega_memory_search",
            tier=0,  # Local memory search = Tier 0
            query=query,
            results={"results": results, "count": len(results)},
            latency_ms=latency_ms,
            status="success",
            provider_name="local_memory_hybrid",
        )
    except Exception as e:
        logger.warning(f"Search persistence failed: {e}")
    
    return json.dumps({
        "query": query,
        "entity": entity_name,
        "count": len(results),
        "results": results
    }, indent=2)


@m9_safe("omega_memory_get_history")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def omega_memory_get_history(entity_name: str, session_id: str, limit: int = 20) -> str:
    """Retrieve conversation history for a specific entity and session.
    
    Args:
        entity_name: The sovereign owner of the memory (REQUIRED).
        session_id: The session identifier (REQUIRED).
        limit: Maximum number of exchanges to return.
        
    Returns:
        JSON string containing the conversation history.
    """
    memory_store = get_memory_store()
    results = await memory_store.get_history(entity_name, session_id, limit)
    return json.dumps({
        "entity": entity_name,
        "session_id": session_id,
        "count": len(results),
        "history": results
    }, indent=2)


@m9_safe("omega_memory_list_sessions")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def omega_memory_list_sessions(entity_name: Optional[str] = None, limit: int = 20) -> str:
    """List recent sessions, optionally filtered by entity.
    
    Args:
        entity_name: Optional entity name to filter by.
        limit: Maximum number of sessions to return.
        
    Returns:
        JSON string containing the list of sessions.
    """
    memory_store = get_memory_store()
    results = await memory_store.list_sessions(entity_name, limit)
    return json.dumps({
        "entity_filter": entity_name,
        "count": len(results),
        "sessions": results
    }, indent=2)


# === RESEARCH TOOLS (5) ===

@m9_safe("research")
@mcp.tool()
async def research(query: str, depth: int = 2, domain: str = "") -> str:
    _require_service()
    """Execute multi-depth research on a query using the offline (await library).

    Depth levels: 1=Quick (1-2 sources), 2=Standard (3-5 sources),
    3=Deep (6-15 sources), 4=Scholarly (10-50 sources).

    Args:
        query: The research question or topic
        depth: Research depth (1-4)
        domain: Optional domain filter
        
    Returns:
        JSON string containing the research result and citations.
    """
    import time
    start = time.perf_counter()
    
    depth = max(1, min(4, depth))
    domain_filter = domain if domain else None
    result = await (await research_engine).research(query, depth=depth, domain=domain_filter)
    
    # Persist search result
    latency_ms = int((time.perf_counter() - start) * 1000)
    try:
        persistence = SearchPersistence(entity_name=domain if domain else "researcher", channel="opencode")
        persistence.wrap_search(
            tool_name="research",
            tier=3,  # Research uses web search = Tier 3+
            query=query,
            results=result.to_dict(),
            latency_ms=latency_ms,
            status="success",
            provider_name="research_engine",
        )
    except Exception as e:
        logger.warning(f"Search persistence failed: {e}")
    
    return json.dumps(result.to_dict(), indent=2, default=str)


@m9_safe("research_get")
@mcp.tool()
async def research_get(research_id: str) -> str:
    _require_service()
    """Retrieve a previous research result by ID.

    Args:
        research_id: Research ID (e.g. res_abc123)
        
    Returns:
        JSON string containing the research result or an error.
    """
    result = await (await research_engine).get_result(research_id)
    if not result:
        return json.dumps({"error": f"Research '{research_id}' not found"})
    return json.dumps(result.to_dict(), indent=2, default=str)


# === STATS TOOLS (5) ===

@m9_safe("get_system_stats")
@mcp.tool()
async def get_system_stats() -> str:
    """Get comprehensive system stats: zRAM, CPU, disk, GPU, memory, Podman.
    
    Returns:
        JSON string containing real-time hardware and process metrics.
    """
    def _collect():
        stats = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {"available": False},
            "memory": {"available": False},
            "zram": {"available": False},
            "disk": {"available": False},
            "gpu": {"available": False},
            "podman": {"available": False},
            "ryzen_tuning": {"available": False},
        }

        # CPU
        try:
            with open("/proc/loadavg") as f:
                parts = f.read().strip().split()
                stats["cpu"] = {
                    "available": True,
                    "load_1min": float(parts[0]),
                    "load_5min": float(parts[1]),
                    "load_15min": float(parts[2]),
                    "running_processes": int(parts[3].split("/")[0]),
                    "total_processes": int(parts[3].split("/")[1]),
                }
        except Exception as exc:
            logger.debug("Failed to collect CPU stats: %s", exc)

        # Memory
        try:
            with open("/proc/meminfo") as f:
                mem = {}
                for line in f:
                    k, v = line.split(":", 1)
                    mem[k.strip()] = int(v.strip().split()[0]) // 1024
                stats["memory"] = {
                    "available": True,
                    "total_mb": mem.get("MemTotal", 0),
                    "free_mb": mem.get("MemFree", 0),
                    "available_mb": mem.get("MemAvailable", 0),
                    "used_mb": mem.get("MemTotal", 0) - mem.get("MemAvailable", 0),
                }
        except Exception as exc:
            logger.debug("Failed to collect memory stats: %s", exc)

        # zRAM
        zram_path = Path("/sys/block/zram0/mm_stat")
        if zram_path.exists():
            try:
                with open(zram_path) as f:
                    mm = f.read().strip().split()
                stats["zram"] = {
                    "available": True,
                    "orig_data_mb": round(int(mm[0]) / 1048576, 1),
                    "compressed_mb": round(int(mm[1]) / 1048576, 1),
                    "mem_used_mb": round(int(mm[2]) / 1048576, 1),
                    "ratio": round(int(mm[0]) / max(int(mm[1]), 1), 2),
                }
            except Exception as exc:
                logger.debug("Failed to collect zRAM stats: %s", exc)

        # Disk — omega_library partition (M16: path from env var)
        try:
            statvfs = os.statvfs(str(_OMEGA_LIBRARY_PATH))
            total = statvfs.f_frsize * statvfs.f_blocks // (1024**3)
            free = statvfs.f_frsize * statvfs.f_bfree // (1024**3)
            stats["disk"] = {
                "available": True,
                "mount": str(_OMEGA_LIBRARY_PATH),
                "total_gb": total,
                "free_gb": free,
                "used_gb": total - free,
                "used_pct": round((total - free) / total * 100, 1) if total > 0 else 0,
            }
        except Exception as exc:
            logger.debug("Failed to collect disk stats: %s", exc)

        # Vulkan iGPU
        gpu_path = Path("/sys/class/drm/card1/device/gpu_busy_percent")
        if gpu_path.exists():
            try:
                with open(gpu_path) as f:
                    stats["gpu"] = {
                        "available": True,
                        "utilization_pct": int(f.read().strip()),
                    }
            except Exception as exc:
                logger.debug("Failed to collect GPU stats: %s", exc)

        # Podman
        try:
            result = os.popen("podman ps --format json 2>/dev/null").read()
            if result:
                containers = json.loads(result)
                stats["podman"] = {
                    "available": True,
                    "running": sum(1 for c in containers if c.get("State") == "running"),
                    "total": len(containers),
                    "names": [c.get("Names", [""])[0] for c in containers],
                }
        except Exception as exc:
            logger.debug("Failed to collect Podman stats: %s", exc)

        # Ryzen tuning check
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
                governor = f.read().strip()
            stats["ryzen_tuning"] = {
                "available": True,
                "governor": governor,
            }
        except Exception as exc:
            logger.debug("Failed to collect Ryzen tuning stats: %s", exc)

        return stats

    stats = await anyio.to_thread.run_sync(_collect)
    return json.dumps(stats, indent=2)


@m9_safe("get_hardware_stats")
@mcp.tool()
async def get_hardware_stats(
    interval: float = 0.3,
    include_threads: bool = False,
) -> str:
    """Get detailed per-core hardware stats: CPU utilization, memory pressure, OOM risk, thread contention, thermal.

    More granular than get_system_stats — shows per-CPU-core utilization,
    memory pressure score, OOM risk analysis, and thread counts.

    Args:
        interval: Sampling interval in seconds for CPU utilization (default 0.3).
        include_threads: Include detailed per-process thread counts (default False).

    Returns:
        JSON string with per-core CPU %, memory status with OOM risk, thermal data, and thread info.
    """
    try:
        from omega.monitoring import HardwareMonitor
    except ImportError:
        return json.dumps({
            "available": False,
            "error": "HardwareMonitor module not available (import omega.monitoring failed)",
        })

    def _collect():
        hm = HardwareMonitor()
        stats = hm.collect_all()
        # Override CPU with fresh per-core at requested interval
        stats["cpu"]["per_core_percent"] = hm.get_per_core_utilization(interval=interval)
        stats["cpu"]["avg_percent"] = round(
            sum(stats["cpu"]["per_core_percent"].values())
            / max(len(stats["cpu"]["per_core_percent"]), 1), 1
        )

        if include_threads:
            stats["threads"] = hm.get_process_thread_count()
        else:
            stats.pop("threads", None)

        # Add topology info
        stats["topology"] = hm.get_cpu_topology()
        return stats

    try:
        stats = await anyio.to_thread.run_sync(_collect)
        return json.dumps(stats, indent=2, default=str)
    except Exception as exc:
        logger.exception("get_hardware_stats failed")
        return json.dumps({"available": False, "error": str(exc)})


@m9_safe("get_omega_metrics")
@mcp.tool()
async def get_omega_metrics() -> str:
    """Get aggregated Omega Engine metrics (Inference, Research, Memory, and Errors).
    
    Returns:
        JSON string containing high-level engine performance and error metrics.
    """
    metrics_path = PROJECT_ROOT / "data" / "logs" / "metrics.json"
    if not metrics_path.exists():
        return json.dumps({"error": "Metrics file not found. No metrics have been recorded yet."}, indent=2)
    try:
        async with await anyio.open_file(str(metrics_path), "r") as f:
            content = await f.read()
        metrics = json.loads(content)
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read metrics: {str(e)}"}, indent=2)


@m9_safe("hivemind_get_metrics")
@mcp.tool()
async def hivemind_get_metrics() -> str:
    """Get Hivemind coordination metrics (awareness, handoffs, locks, sessions).

    [hi-observability-1] Returns real-time Hivemind metrics from
    data/coordination/metrics.json. If the file does not exist (e.g.
    because the pruning loop hasn't run yet), generates it on the fly.

    Returns:
        JSON string containing active agents, handoff queue counts,
        workspace lock counts, extended sessions, and last pruning timestamp.
    """
    if not METRICS_PATH.exists():
        metrics = await _write_metrics()
        return json.dumps(metrics, indent=2)
    try:
        async with await anyio.open_file(str(METRICS_PATH), "r") as f:
            content = await f.read()
        metrics = json.loads(content)
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read metrics: {str(e)}"}, indent=2)


@m9_safe("check_models_directory")
@mcp.tool()
async def check_models_directory() -> str:
    """Check available GGUF models on omega_library partition.
    
    Returns:
        JSON string listing available local GGUF models and their sizes.
    """
    _deprecated("check_models_directory", "CLI: omega models list")
    def _collect():
        models_dir = _OMEGA_MODELS_PATH
        if not models_dir.exists():
            return {"error": "Models directory not found"}
        models = []
        for f in sorted(models_dir.glob("*.gguf")):
            size_gb = round(f.stat().st_size / (1024**3), 2)
            models.append({"name": f.name, "size_gb": size_gb})
        return {
            "path": str(models_dir),
            "total_models": len(models),
            "models": models,
        }
    
    result = await anyio.to_thread.run_sync(_collect)
    return json.dumps(result, indent=2)


@m9_safe("check_podman_storage")
@mcp.tool()
async def check_podman_storage() -> str:
    """Check Podman storage usage on omega_(await library).
    
    Returns:
        JSON string containing Podman storage path and size metrics.
    """
    _deprecated("check_podman_storage", "CLI: podman system df")
    def _collect():
        storage_dir = _OMEGA_PODMAN_STORAGE
        if not storage_dir.exists():
            return {"error": "Podman storage directory not found"}
        try:
            total_size = sum(f.stat().st_size for f in storage_dir.rglob("*") if f.is_file())
            size_mb = round(total_size / (1024**2), 1)
            return {
                "path": str(storage_dir),
                "size_mb": size_mb,
                "exists": True,
            }
        except Exception as e:
            return {"error": str(e)}
            
    result = await anyio.to_thread.run_sync(_collect)
    return json.dumps(result, indent=2)


# === OBSERVABILITY TOOLS (2) ===

@m9_safe("observability_check_recursion")
@mcp.tool()
async def observability_check_recursion(entity_name: str, current_depth: int) -> str:
    _require_service()
    """Check if an entity is allowed to spawn a subagent at the given depth.

    Args:
        entity_name: The name of the entity attempting to spawn a subagent.
        current_depth: The current depth of the subagent chain (0-indexed).
        
    Returns:
        JSON string containing the recursion check results (allowed/blocked).
    """
    if not (await hierarchy)._hierarchy:
        await (await hierarchy).load()
    result = (await hierarchy).check_recursion(entity_name, current_depth)
    return json.dumps(result, indent=2)


@m9_safe("observability_log_boundary_violation")
@mcp.tool()
async def observability_log_boundary_violation(tool_name: str, reason: str, entity: str) -> str:
    """Log a sovereign boundary violation from the OpenCode plugin.

    Args:
        tool_name: The tool that was blocked
        reason: Why the entity blocked it
        entity: The entity currently active
        
    Returns:
        JSON string confirming the violation was logged.
    """
    trace_id = new_trace_id()
    get_engine().log_event(
        "boundary.violation",
        trace_id,
        {"tool": tool_name, "reason": reason, "entity": entity}
    )

    metrics_path = PROJECT_ROOT / "data" / "logs" / "metrics.json"
    await anyio.Path(str(metrics_path)).parent.mkdir(parents=True, exist_ok=True)

    metrics = {"violations": []}
    if metrics_path.exists():
        try:
            def _read():
                with open(metrics_path) as f:
                    return json.load(f)
            metrics = await anyio.to_thread.run_sync(_read)
        except Exception as e:
            logger.warning(f"Could not read metrics file {metrics_path}: {e}; starting fresh")

    metrics["violations"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "reason": reason,
        "entity": entity
    })
    metrics["violations"] = metrics["violations"][-100:]

    def _write():
        with open(metrics_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(metrics, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
    await anyio.to_thread.run_sync(_write)

    return json.dumps({"status": "logged", "trace_id": trace_id})


# === ICS TOOLS (1) ===

@m9_safe("ics_render_header")
@mcp.tool()
async def ics_render_header(
    entity: str,
    model: Optional[str] = None,
    channel: str = "opencode",
    trace_id: Optional[str] = None,
    phase: Optional[str] = None,
    mode: str = "full",
) -> str:
    """Render an ICS-S session header string from the ICS module.

    Single source of truth for the ⬡ OMEGA agent signature. Use this instead
    of hand-typing session headers.

    Args:
        entity: The entity name (e.g., "KALI", "sophia")
        model: Optional model override (D118). Auto-detected if omitted.
        channel: Execution channel (default: "opencode")
        trace_id: Optional trace ID. Auto-generated if omitted.
        phase: Optional phase string. Auto-detected from ROADMAP if omitted.
        mode: "full" | "compact" | "off" (default: "full")
        
    Returns:
        JSON string containing the rendered ICS-S header.
    """
    header = ics_render_logic(
        entity=entity,
        model=model,
        channel=channel,
        trace_id=trace_id,
        phase=phase,
        mode=mode,
    )
    return json.dumps({"header": header, "entity": entity, "mode": mode})


# === CONSOLIDATED TOOLS (7) ===
# These replace the fragmented CRUD tools with single action-based interfaces.
# Old tools are deprecated but kept for backward compatibility.

# ═══════════════════════════════════════════════════════════════════════════
# R1-R5 MCP BINDING
# ═══════════════════════════════════════════════════════════════════════════
# The store already raises StoreUnreachable rather than returning []. THIS is
# where that guarantee could be lost, because MCP makes it easier to lose: a
# tool result is a success payload by default, so `{"entries": []}` on a dead
# store looks identical to a healthy "no news". The natural caller is
# `if not entries: pass`, which passes on both.
#
# So a failure is a DISCRIMINATOR, never an empty list.

def _resolve_target_entity(entity: str, channel: str):
    """Alias resolution, imported lazily to keep the module import graph flat."""
    from ..handoff_alias import resolve_target_entity
    return resolve_target_entity(entity, channel)


def _federation_store():
    # `tools.py` imports selected NAMES from state, not the module itself, so
    # `state` is not a module-level name here. Import it inside the function.
    from .. import state as _state
    from ..federation_store import FederationStore
    return FederationStore(_state.HANDOFF_BASE)


def _fe_mark_read(env: dict, entity: str) -> None:
    from .. import federation_envelope as fe
    fe.mark_read(env, entity, action="read")


def _federation_dispatch(action: str, *, source_channel, source_entity, packet_id,
                         target_entity, session_id, limit, scope,
                         source_instance=None) -> str:
    """Bind inbox / receipts / read to the store, without losing its guarantees."""
    from .. import federation_store as fstore
    from .. import federation_session as fsess

    if not source_channel or not source_entity:
        return json.dumps({"error": {"code": "missing_identity",
                                     "message": f"{action} requires source_channel and source_entity"}})
    store = _federation_store()

    # ── M15/ADR-001: read state is INSTANCE-scoped, not entity-scoped ──
    # `unread_scope: instance` (hivemind.yaml:190). `ge-n0` and `ge-n1` are
    # two chat sessions of ONE agent, so keying `read_by` by `source_entity`
    # cannot separate them — an agent that cannot tell its own mail from its
    # other instance's cannot know what it has reviewed. Falls back to the
    # entity name so pre-ADR callers keep their existing read state.
    read_key = source_instance or source_entity

    resolved = fsess.resolve_session_id(
        session_id, bump=store.bump, fallback_entity=source_entity,
        daemon_session_id=f"ses_stamped_{source_channel}_{source_entity}")
    session_block = {
        "session_id": resolved["session_id"],
        "session_id_source": resolved["source"],
        "session_verified": resolved["verified"],
        "unverified_sender": resolved["unverified_sender"],
    }
    if resolved["source"] == "server_stamped":
        # Never substitute silently: the caller must learn their id was NOT the
        # one recorded, or they will believe provenance that does not exist.
        session_block["session_id_substituted"] = True
        session_block["session_id_note"] = (
            f"your supplied session_id was {resolved['reason']!r}; the server stamped "
            "one instead and flagged the envelope unverified")

    try:
        if action == "inbox":
            payload = store.inbox(source_entity, limit=limit)
        elif action == "receipts":
            payload = store.receipts(source_entity)
        elif action == "read":
            if not packet_id:
                return json.dumps({"error": {"code": "missing_packet_id",
                                             "message": "read requires packet_id"}})
            # Dual-key lookup (handoff_id OR legacy packet_id) + append-only
            # journal write. NEVER store.submit() here: submit re-validates the
            # envelope, which rejects legacy packets (no body_sha256) and
            # KeyErrors on envelope['handoff_id'] — the hidden crash. The
            # envelope on disk is never mutated; read state is pure addition.
            envelope = store.record_read_receipt(packet_id, read_key, action="read")
            if envelope is None:
                return json.dumps({"error": {"code": "not_found",
                                             "message": f"no packet {packet_id}"}})
            read_by = store.read_receipts(packet_id)
            payload = {"entries": [envelope], "read_by": read_by}
        else:
            return json.dumps({"error": {"code": "bad_action", "message": action}})
    except fstore.StoreUnreachable as exc:
        # THE discriminator. An error, never an empty list.
        return json.dumps({
            "error": {"code": "store_unreachable", "message": str(exc),
                      "hint": "entries are ABSENT, not empty. Do not treat this as "
                              "'no new handoffs'."},
            **session_block})
    except ValueError as exc:
        return json.dumps({"error": {"code": "invalid_request", "message": str(exc)},
                           **session_block})

    out = {**payload, **session_block}
    out.pop("error", None)
    return json.dumps(out)


@m9_safe("hivemind_handoff")
@mcp.tool()
async def hivemind_handoff(
    action: str,
    packet_id: Optional[str] = None,
    target_channel: Optional[str] = None,
    target_entity: Optional[str] = None,
    source_channel: Optional[str] = None,
    source_entity: Optional[str] = None,
    task: Optional[str] = None,
    context: Optional[str] = None,
    priority: int = 0,
    accepting_channel: Optional[str] = None,
    accepting_entity: Optional[str] = None,
    result: Optional[str] = None,
    reason: Optional[str] = None,
    status: Optional[str] = None,
    packet_ids: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    scope: str = "default",
    limit: Optional[int] = None,
    source_instance: Optional[str] = None,
) -> str:
    """Unified handoff management — replaces 7 fragmented tools.
    
    Actions:
        submit: Create a new handoff packet (requires target_channel, target_entity, source_channel, source_entity, task)
        accept: Accept a pending handoff (requires packet_id, accepting_channel, accepting_entity)
        complete: Mark handoff as complete (requires packet_id, optional result)
        reject: Reject a pending handoff (requires packet_id, reason)
        list: List handoffs by status (requires status: pending|active|completed|stale)
        get: Get full handoff details (requires packet_id)
        archive: Archive completed handoffs (requires packet_ids list)
        inbox: NEW — unread submissions addressed to YOU, across all queues
        receipts: NEW — every packet YOU sent, with full state_history
        read: NEW — record that YOU read a packet. Explicit, and DISTINCT from
               accept: reading is not deciding, and collapsing the two loses the
               fact that someone looked and did not act.

    ERROR CONTRACT (load-bearing)
    -----------------------------
    A store failure is an ERROR PAYLOAD, never an empty list:

        {"error": {"code": "store_unreachable", "message": "..."}}

    Branch on `error.code` — NOT on emptiness. The natural caller is
    `if not entries: pass`, which passes on BOTH an empty inbox and a dead store,
    which is the confident-false-negative this contract exists to eliminate. An
    `entries` key and an `error` key are mutually exclusive: you will never
    receive `{"entries": [], "error": ...}`, nor `{"entries": [], "cursor_reset":
    true}` (a reset with no entries is indistinguishable from genuinely no news).

    SESSION PROVENANCE
    ------------------
    `session_id` is validated read-only against opencode.db; malformed and
    unknown are SEPARATE outcomes. Unknown ids are stamped and flagged
    `unverified_sender` on the ENVELOPE — visible to the RECEIVING agent, not
    merely counted — because a counter tells you the rate while the flag tells
    the reader, and the reader is who M29 exists to protect. Every response
    echoes the resolved `session_id` and states explicitly when the server
    substituted a stamped one. Silent substitution is the same failure class as
    a silent post.
    
    Args:
        action: submit|accept|complete|reject|list|get|archive|inbox|receipts|read
        packet_id: Handoff packet ID (for accept|complete|reject|get)
        target_channel: Target agent channel (for submit)
        target_entity: Target agent entity (for submit)
        source_channel: Source agent channel (for submit)
        source_entity: Source agent entity (for submit)
        task: Task description (for submit)
        context: Optional background context (for submit)
        priority: 0=normal, 1=high, 2=critical (for submit)
        accepting_channel: Channel accepting the handoff (for accept)
        accepting_entity: Entity accepting the handoff (for accept)
        result: Completion result text (for complete)
        reason: Rejection reason (for reject)
        status: Filter status for list (pending|active|completed|stale)
        packet_ids: List of packet IDs to archive (for archive)
        session_id: Calling session id. Validated; stamped+flagged if malformed/unknown.
        scope: list only. "default" filters by target_entity; "all" is a DEPRECATED,
               LOGGED opt-in with removal date 2026-12-31.
        limit: Optional cap on inbox entries
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    # Validate action
    # R1-R5 federation actions are ADDED, not substituted.
    valid_actions = {"submit", "accept", "complete", "reject", "list", "get", "archive",
                     "inbox", "receipts", "read"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {sorted(valid_actions)}"})

    # Federation actions (R1-R5) dispatch BEFORE the legacy queue logic, which is
    # untouched: submit/accept/complete/reject/get/list keep their behaviour.
    # This is an ADDITION, not a replacement.
    if action in ("inbox", "receipts", "read"):
        return _federation_dispatch(
            action, source_channel=source_channel, source_entity=source_entity,
            packet_id=packet_id, target_entity=target_entity,
            session_id=session_id, limit=limit, scope=scope,
            source_instance=source_instance)

    try:
        if action == "submit":
            if not all([target_channel, target_entity, source_channel, source_entity, task]):
                return json.dumps({"error": "submit requires target_channel, target_entity, source_channel, source_entity, task"})

            # M23/GE-N1: resolve the target through the DERIVED alias map
            # instead of literal concatenation, which forked `ge_n1` away from
            # `ge-n1`. Ambiguous input is REFUSED, never guessed.
            try:
                _alias = _resolve_target_entity(target_entity, target_channel)
            except Exception as _exc:
                return json.dumps({
                    "error": "ambiguous_target_entity",
                    "message": str(_exc),
                    "supplied": target_entity,
                    "hint": "a wrong target silently forks the packet; pass the "
                            "exact entity name or an explicit agent_id",
                })
            target_entity = _alias["entity"]
            target_agent_id = _alias["agent_id"]
            source_agent_id = _make_agent_id(source_channel, source_entity)
            packet_id = f"ho_{uuid.uuid4().hex[:12]}"
            packet = {
                "packet_id": packet_id,
                "target_agent_id": target_agent_id,
                "target_channel": target_channel,
                "target_entity": target_entity,
                "source_agent_id": source_agent_id,
                "source_channel": source_channel,
                "source_entity": source_entity,
                "task": task,
                "context": context or "",
                "priority": priority,
                "context_delivery": "inline",  # D216 default
                "resolver_strategy": "escalate",  # Decree 2 default
                "status": "pending",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            }
            path = HANDOFF_PENDING / f"{packet_id}.json"
            
            def _write():
                with open(path, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(packet, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
            await anyio.to_thread.run_sync(_write)
            handoff_index_add(packet_id, "pending")

            # M30/GE-N1: echo what was PERSISTED, not what was requested.
            # GE-N1 had to make a SECOND call to discover their target was
            # resolved differently than they sent it. Reading the packet back is
            # the cheapest possible defence: the difference between requested and
            # stored becomes visible in the response they already have.
            _stored = {}
            try:
                _stored = json.loads(path.read_text())
            except (OSError, ValueError) as _e:  # pragma: no cover — defensive
                logger.warning("submit echo could not read back %s: %s", path, _e)

            _resp = {
                "status": "submitted",
                "packet_id": _stored.get("packet_id", packet_id),
                "path": str(path),
                # what was ASKED for
                "requested": {
                    "target_entity": _alias.get("supplied", target_entity),
                    "target_agent_id": f"{target_channel}/{_alias.get('supplied', target_entity)}",
                },
                # what was STORED — the authoritative answer
                "stored": {
                    "packet_id": _stored.get("packet_id"),
                    "target_agent_id": _stored.get("target_agent_id"),
                    "target_entity": _stored.get("target_entity"),
                    "status": _stored.get("status"),
                },
                "target_resolution": {
                    "resolved": _alias.get("resolved"),
                    "rule": _alias.get("rule"),
                    "candidates": _alias.get("candidates", []),
                    "note": _alias.get("note"),
                },
            }
            if _alias.get("resolved") is False:
                _resp["warning"] = (
                    f"target {target_entity!r} matched no live entity; the agent_id "
                    "was left exactly as supplied and the packet may be undeliverable"
                )
            return json.dumps(_resp)
        
        elif action == "accept":
            if not all([packet_id, accepting_channel, accepting_entity]):
                return json.dumps({"error": "accept requires packet_id, accepting_channel, accepting_entity"})
            src = HANDOFF_PENDING / f"{packet_id}.json"
            if not src.exists():
                return json.dumps({"error": f"Packet {packet_id} not found in pending"})
            accepting_agent_id = _make_agent_id(accepting_channel, accepting_entity)
            packet = json.loads(src.read_text())
            if packet["target_agent_id"] != accepting_agent_id:
                return json.dumps({"error": "Agent mismatch: packet not addressed to this agent"})
            packet["status"] = "active"
            packet["accepted_at"] = datetime.now(timezone.utc).isoformat()
            packet["accepted_by"] = accepting_agent_id
            dst = HANDOFF_ACTIVE / f"{packet_id}.json"
            
            def _move():
                with open(dst, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(packet, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
                src.unlink()
            await anyio.to_thread.run_sync(_move)
            handoff_index_move(packet_id, "active")
            return json.dumps({"status": "accepted", "packet_id": packet_id})
        
        elif action == "complete":
            if not packet_id:
                return json.dumps({"error": "complete requires packet_id"})
            src = HANDOFF_ACTIVE / f"{packet_id}.json"
            if not src.exists():
                return json.dumps({"error": f"Packet {packet_id} not found in active"})
            packet = json.loads(src.read_text())
            packet["status"] = "completed"
            packet["completed_at"] = datetime.now(timezone.utc).isoformat()
            packet["result"] = result or ""
            dst = HANDOFF_COMPLETED / f"{packet_id}.json"
            
            def _move():
                with open(dst, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(packet, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
                src.unlink()
            await anyio.to_thread.run_sync(_move)
            handoff_index_move(packet_id, "completed")
            return json.dumps({"status": "completed", "packet_id": packet_id})
        
        elif action == "reject":
            if not all([packet_id, reason]):
                return json.dumps({"error": "reject requires packet_id and reason"})
            src = HANDOFF_PENDING / f"{packet_id}.json"
            if not src.exists():
                return json.dumps({"error": f"Packet {packet_id} not found in pending"})
            packet = json.loads(src.read_text())
            packet["status"] = "stale"
            packet["rejected"] = True
            packet["rejected_at"] = datetime.now(timezone.utc).isoformat()
            packet["rejection_reason"] = reason
            dst = HANDOFF_STALE / f"{packet_id}.json"
            
            def _move():
                with open(dst, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(packet, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
                src.unlink()
            await anyio.to_thread.run_sync(_move)
            handoff_index_move(packet_id, "stale")
            return json.dumps({"status": "rejected", "packet_id": packet_id})
        
        elif action == "list":
            if not status:
                return json.dumps({"error": "list requires status (pending|active|completed|stale)"})
            status_dir = {
                "pending": HANDOFF_PENDING,
                "active": HANDOFF_ACTIVE,
                "completed": HANDOFF_COMPLETED,
                "stale": HANDOFF_STALE,
            }.get(status)
            if not status_dir:
                return json.dumps({"error": f"Invalid status '{status}'"})
            packets = []
            for f in status_dir.glob("*.json"):
                try:
                    packets.append(json.loads(f.read_text()))
                except Exception:
                    pass
            return json.dumps({"status": status, "count": len(packets), "packets": packets})
        
        elif action == "get":
            if not packet_id:
                return json.dumps({"error": "get requires packet_id"})
            path = _find_packet_path(packet_id)
            if not path:
                return json.dumps({"error": f"Packet {packet_id} not found"})
            def _read():
                with open(path) as f:
                    return json.load(f)
            packet = await anyio.to_thread.run_sync(_read)
            return json.dumps(packet, indent=2)
        
        elif action == "archive":
            if not packet_ids:
                return json.dumps({"error": "archive requires packet_ids list"})
            archived = 0
            for pid in packet_ids:
                src = HANDOFF_COMPLETED / f"{pid}.json"
                if src.exists():
                    dst = HANDOFF_ARCHIVE / f"{pid}.json"
                    def _move():
                        with open(dst, "w") as f:
                            fcntl.flock(f, fcntl.LOCK_EX)
                            json.dump(json.loads(src.read_text()), f, indent=2)
                            fcntl.flock(f, fcntl.LOCK_UN)
                        src.unlink()
                    await anyio.to_thread.run_sync(_move)
                    handoff_index_move(pid, "archive")
                    archived += 1
            return json.dumps({"status": "archived", "count": archived})
    
    except Exception as e:
        logger.warning("hivemind_handoff %s failed: %s", action, e)
        return json.dumps({"error": str(e)})


@m9_safe("library_inbox")
@mcp.tool()
async def library_inbox(
    action: str,
    url: Optional[str] = None,
    text: Optional[str] = None,
    path: Optional[str] = None,
    tags: str = "",
    priority: int = 0,
    limit: int = 20,
) -> str:
    """Unified library inbox management — replaces 5 fragmented tools.
    
    Actions:
        add_url: Add a URL to the intake inbox (requires url)
        add_note: Add a text note to the intake inbox (requires text)
        add_file: Add a local file path to the intake inbox (requires path)
        list: List pending inbox items (optional limit)
        stats: Get inbox statistics (pending, processing, failed counts)
    
    Args:
        action: The operation to perform (add_url|add_note|add_file|list|stats)
        url: URL to add (for add_url)
        text: Note text (for add_note)
        path: Local file path (for add_file)
        tags: Comma-separated tags
        priority: 0=normal, 1=high, 2=critical
        limit: Max items to return (for list)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"add_url", "add_note", "add_file", "list", "stats"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "add_url":
            if not url:
                return json.dumps({"error": "add_url requires url"})
            item_id = f"in_{uuid.uuid4().hex[:12]}"
            item = {
                "item_id": item_id,
                "type": "url",
                "source": url,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "priority": priority,
                "status": "pending",
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
            path = INBOX_DIR / f"{item_id}.json"
            def _write():
                with open(path, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(item, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
            await anyio.to_thread.run_sync(_write)
            return json.dumps({"status": "added", "item_id": item_id, "type": "url"})
        
        elif action == "add_note":
            if not text:
                return json.dumps({"error": "add_note requires text"})
            item_id = f"in_{uuid.uuid4().hex[:12]}"
            item = {
                "item_id": item_id,
                "type": "note",
                "source": text,
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "priority": priority,
                "status": "pending",
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
            path = INBOX_DIR / f"{item_id}.json"
            def _write():
                with open(path, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(item, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
            await anyio.to_thread.run_sync(_write)
            return json.dumps({"status": "added", "item_id": item_id, "type": "note"})
        
        elif action == "add_file":
            if not path:
                return json.dumps({"error": "add_file requires path"})
            p = Path(path)
            if not p.exists():
                return json.dumps({"error": f"File not found: {path}"})
            item_id = f"in_{uuid.uuid4().hex[:12]}"
            item = {
                "item_id": item_id,
                "type": "file",
                "source": str(p),
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "priority": priority,
                "status": "pending",
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
            path = INBOX_DIR / f"{item_id}.json"
            def _write():
                with open(path, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(item, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
            await anyio.to_thread.run_sync(_write)
            return json.dumps({"status": "added", "item_id": item_id, "type": "file"})
        
        elif action == "list":
            items = []
            for f in sorted(INBOX_DIR.glob("*.json")):
                try:
                    items.append(json.loads(f.read_text()))
                except Exception:
                    pass
                if len(items) >= limit:
                    break
            return json.dumps({"count": len(items), "items": items})
        
        elif action == "stats":
            pending = len(list(INBOX_DIR.glob("*.json")))
            processing = len(list(PROCESSING_DIR.glob("*.json"))) if PROCESSING_DIR.exists() else 0
            failed = len(list(FAILED_DIR.glob("*.json"))) if FAILED_DIR.exists() else 0
            return json.dumps({
                "pending": pending,
                "processing": processing,
                "failed": failed,
                "total": pending + processing + failed,
            })
    
    except Exception as e:
        logger.warning("library_inbox %s failed: %s", action, e)
        return json.dumps({"error": str(e)})


@m9_safe("library_discovery")
@mcp.tool()
async def library_discovery(
    action: str,
    query: Optional[str] = None,
    depth: int = 2,
    job_id: Optional[str] = None,
) -> str:
    """Unified library discovery — replaces 3 fragmented tools.
    
    Actions:
        research: Execute tiered external discovery and return consolidated report (requires query, depth)
        start: Start a background discovery job (requires query)
        status: Get status and partial results of a background job (requires job_id)
    
    Args:
        action: The operation to perform (research|start|status)
        query: Search query (for research|start)
        depth: Research depth 1-4 (for research)
        job_id: Background job ID (for status)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"research", "start", "status"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "research":
            if not query:
                return json.dumps({"error": "research requires query"})
            report = await (await sovereign_search_service).search(
                query, entity_name="general", limit=20
            )
            return json.dumps({
                "query": query,
                "depth": depth,
                "status": report["status"],
                "final_tier": report["final_tier"],
                "primary_finding": report["primary_finding"],
                "evidence": report["evidence"],
                "fallback_log": report["fallback_log"],
            }, indent=2, default=str)
        elif action == "start":
            if not query:
                return json.dumps({"error": "start requires query"})
            report = await (await sovereign_search_service).search(
                query, entity_name="general", limit=20
            )
            return json.dumps({"status": "submitted", "query": query, "job_id": report.get("final_tier", "unknown")}, indent=2, default=str)
        elif action == "status":
            if not job_id:
                return json.dumps({"error": "status requires job_id"})
            return json.dumps({"status": "unknown", "job_id": job_id, "note": "Async job tracking not yet implemented; use 'research' for synchronous results."})
    except Exception as e:
        return json.dumps({"error": f"library_discovery failed: {e}"})


@mcp.tool()
async def sovereignty_ratio(since_days: int = 0) -> str:
    """Get the local vs cloud inference ratio from historical data (D203).

    Queries the MetricsDB performance table to calculate what percentage of
    inference requests were served by local vs cloud providers. This is the
    canonical Sovereignty Scorecard metric.

    Args:
        since_days: Optional — only count inferences from last N days.
                    0 (default) = all time.

    Returns:
        JSON string with local_count, cloud_count, total, ratio_local,
        ratio_cloud, and provider_breakdown.
    """
    since = since_days if since_days > 0 else None
    result = get_sovereignty_ratio(since_days=since)
    return json.dumps(result, indent=2, default=str)


@m9_safe("oracle_debug")
@mcp.tool()
async def oracle_debug(
    action: str,
    query: Optional[str] = None,
) -> str:
    """Unified Oracle debug tools — replaces 3 fragmented tools.
    
    Actions:
        assess_intent: Test how Oracle would classify a query (requires query)
        discover_entity: Find best entity for a task (requires query)
        list_slot_keepers: List entities with slot assignments (no args)
    
    Args:
        action: The operation to perform (assess_intent|discover_entity|list_slot_keepers)
        query: Query to analyze (for assess_intent|discover_entity)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"assess_intent", "discover_entity", "list_slot_keepers"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "assess_intent":
            if not query:
                return json.dumps({"error": "assess_intent requires query"})
            intent = _detect_intent(query)
            confidence = _compute_confidence(query, intent)
            entity_name = _route_by_domain(query)
            escalate = confidence < 0.7
            return json.dumps({
                "query": query,
                "intent": intent,
                "confidence": confidence,
                "entity": entity_name,
                "escalate": escalate,
            })
        
        elif action == "discover_entity":
            if not query:
                return json.dumps({"error": "discover_entity requires query"})
            entity_name = _route_by_domain(query)
            if entity_name and entity_name != "SOPHIA":
                entity = (await registry).get(entity_name)
                if entity:
                    return json.dumps({
                        "query": query,
                        "entity": entity_name,
                        "role": entity.role,
                        "domain": entity.domain,
                        "model": entity.model,
                    })
            return json.dumps({
                "query": query,
                "entity": "SOPHIA",
                "note": "No specific entity matched; defaulting to SOPHIA",
            })
        
        elif action == "list_slot_keepers":
            entities = (await registry).list_all()
            result = []
            for e in entities:
                if e.slot:
                    result.append({
                        "name": e.name,
                        "slot": e.slot,
                        "role": e.role,
                        "domain": e.domain,
                        "model": e.model,
                    })
            return json.dumps({"count": len(result), "entities": result})
    
    except Exception as e:
        logger.warning("oracle_debug %s failed: %s", action, e)
        return json.dumps({"error": str(e)})


# ── Internal Helper Functions for system_stats ──────────────────────────────────

async def _get_system_summary() -> dict:
    """Collect system summary stats (CPU, memory, zRAM, disk, GPU, Podman, Ryzen).

    Returns:
        Dict with system summary metrics.
    """
    def _collect():
        stats = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {"available": False},
            "memory": {"available": False},
            "zram": {"available": False},
            "disk": {"available": False},
            "gpu": {"available": False},
            "podman": {"available": False},
            "ryzen_tuning": {"available": False},
        }

        # CPU
        try:
            with open("/proc/loadavg") as f:
                parts = f.read().strip().split()
                stats["cpu"] = {
                    "available": True,
                    "load_1min": float(parts[0]),
                    "load_5min": float(parts[1]),
                    "load_15min": float(parts[2]),
                    "running_processes": int(parts[3].split("/")[0]),
                    "total_processes": int(parts[3].split("/")[1]),
                }
        except Exception as exc:
            logger.debug("Failed to collect CPU stats: %s", exc)

        # Memory
        try:
            with open("/proc/meminfo") as f:
                mem = {}
                for line in f:
                    k, v = line.split(":", 1)
                    mem[k.strip()] = int(v.strip().split()[0]) // 1024
                stats["memory"] = {
                    "available": True,
                    "total_mb": mem.get("MemTotal", 0),
                    "free_mb": mem.get("MemFree", 0),
                    "available_mb": mem.get("MemAvailable", 0),
                    "used_mb": mem.get("MemTotal", 0) - mem.get("MemAvailable", 0),
                }
        except Exception as exc:
            logger.debug("Failed to collect memory stats: %s", exc)

        # zRAM
        zram_path = Path("/sys/block/zram0/mm_stat")
        if zram_path.exists():
            try:
                with open(zram_path) as f:
                    mm = f.read().strip().split()
                stats["zram"] = {
                    "available": True,
                    "orig_data_mb": round(int(mm[0]) / 1048576, 1),
                    "compressed_mb": round(int(mm[1]) / 1048576, 1),
                    "mem_used_mb": round(int(mm[2]) / 1048576, 1),
                    "ratio": round(int(mm[0]) / max(int(mm[1]), 1), 2),
                }
            except Exception as exc:
                logger.debug("Failed to collect zRAM stats: %s", exc)

        # Disk — omega_library partition (M16: path from env var)
        try:
            statvfs = os.statvfs(str(_OMEGA_LIBRARY_PATH))
            total = statvfs.f_frsize * statvfs.f_blocks // (1024**3)
            free = statvfs.f_frsize * statvfs.f_bfree // (1024**3)
            stats["disk"] = {
                "available": True,
                "mount": str(_OMEGA_LIBRARY_PATH),
                "total_gb": total,
                "free_gb": free,
                "used_gb": total - free,
                "used_pct": round((total - free) / total * 100, 1) if total > 0 else 0,
            }
        except Exception as exc:
            logger.debug("Failed to collect disk stats: %s", exc)

        # Vulkan iGPU
        gpu_path = Path("/sys/class/drm/card1/device/gpu_busy_percent")
        if gpu_path.exists():
            try:
                with open(gpu_path) as f:
                    stats["gpu"] = {
                        "available": True,
                        "utilization_pct": int(f.read().strip()),
                    }
            except Exception as exc:
                logger.debug("Failed to collect GPU stats: %s", exc)

        # Podman
        try:
            result = os.popen("podman ps --format json 2>/dev/null").read()
            if result:
                containers = json.loads(result)
                stats["podman"] = {
                    "available": True,
                    "running": sum(1 for c in containers if c.get("State") == "running"),
                    "total": len(containers),
                    "names": [c.get("Names", [""])[0] for c in containers],
                }
        except Exception as exc:
            logger.debug("Failed to collect Podman stats: %s", exc)

        # Ryzen tuning check
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
                governor = f.read().strip()
            stats["ryzen_tuning"] = {
                "available": True,
                "governor": governor,
            }
        except Exception as exc:
            logger.debug("Failed to collect Ryzen tuning stats: %s", exc)

        return stats

    stats = await anyio.to_thread.run_sync(_collect)
    return stats


async def _get_hardware_detail() -> dict:
    """Collect detailed hardware stats (per-core CPU, memory pressure, OOM risk, threads, topology).

    Returns:
        Dict with detailed hardware metrics.
    """
    try:
        from omega.monitoring import HardwareMonitor
    except ImportError:
        return {
            "available": False,
            "error": "HardwareMonitor module not available (import omega.monitoring failed)",
        }

    def _collect():
        hm = HardwareMonitor()
        stats = hm.collect_all()
        # Per-core CPU utilization
        stats["cpu"]["per_core_percent"] = hm.get_per_core_utilization(interval=0.3)
        stats["cpu"]["avg_percent"] = round(
            sum(stats["cpu"]["per_core_percent"].values())
            / max(len(stats["cpu"]["per_core_percent"]), 1), 1
        )

        # Threads
        stats["threads"] = hm.get_process_thread_count()

        # Topology
        stats["topology"] = hm.get_cpu_topology()
        return stats

    try:
        stats = await anyio.to_thread.run_sync(_collect)
        return stats
    except Exception as exc:
        logger.exception("_get_hardware_detail failed")
        return {"available": False, "error": str(exc)}


# ── SYSTEM STATS TOOL ───────────────────────────────────────────────────────────

@m9_safe("system_stats")
@mcp.tool()
async def system_stats(
    detail: str = "summary",
) -> str:
    """Unified system stats — replaces get_system_stats + get_hardware_stats.
    
    Args:
        detail: "summary" for overview, "hardware" for per-core details, "full" for both
        
Returns:
        JSON string with per-core CPU %, memory status with OOM risk, thermal data, and thread info.
    """
    _deprecated("get_hardware_stats", "system_stats(detail='hardware')")
    _require_service()
    
    try:
        if detail in ("summary", "full"):
            summary = await _get_system_summary()
        if detail in ("hardware", "full"):
            hardware = await _get_hardware_detail()
        
        if detail == "summary":
            return json.dumps(summary, indent=2)
        elif detail == "hardware":
            return json.dumps(hardware, indent=2)
        else:  # full
            return json.dumps({"summary": summary, "hardware": hardware}, indent=2)
    
    except Exception as e:
        logger.warning("system_stats failed: %s", e)
        return json.dumps({"error": str(e)})


@m9_safe("github")
@mcp.tool()
async def github(
    action: str,
    repo: Optional[str] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
    base: Optional[str] = None,
    head: Optional[str] = None,
    pr_number: Optional[int] = None,
    entity: Optional[str] = None,
    issue_number: Optional[int] = None,
) -> str:
    """Unified GitHub operations — replaces 6 fragmented tools.
    
    Actions:
        create_pr: Create a PR with Temple-Grade template (requires repo, title, body, base, head)
        check_temple_grade: Check Temple-Grade CI status for a PR (requires repo, pr_number)
        add_entity_attribution: Inject entity attribution into a commit (requires repo, entity)
        list_heritage_issues: List open heritage-tagged issues (requires repo)
        create_vet_issue: Create a vet issue from a heritage record (requires repo, issue_number)
        get_repo_health: Get repo health metrics (requires repo)
    
    Args:
        action: The operation to perform
        repo: Repository in 'owner/name' format
        title: PR title (for create_pr)
        body: PR body (for create_pr)
        base: Base branch (for create_pr)
        head: Head branch (for create_pr)
        pr_number: PR number (for check_temple_grade)
        entity: Entity name (for add_entity_attribution)
        issue_number: Issue number (for create_vet_issue)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"create_pr", "check_temple_grade", "add_entity_attribution", 
                     "list_heritage_issues", "create_vet_issue", "get_repo_health"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "create_pr":
            if not all([repo, title, body, base, head]):
                return json.dumps({"error": "create_pr requires repo, title, body, base, head"})
            return await _github_create_pr(repo, title, body, base, head)
        
        elif action == "check_temple_grade":
            if not all([repo, pr_number]):
                return json.dumps({"error": "check_temple_grade requires repo, pr_number"})
            return await _github_check_temple_grade(repo, pr_number)
        
        elif action == "add_entity_attribution":
            if not all([repo, entity]):
                return json.dumps({"error": "add_entity_attribution requires repo, entity"})
            return await _github_add_entity_attribution(repo, entity)
        
        elif action == "list_heritage_issues":
            if not repo:
                return json.dumps({"error": "list_heritage_issues requires repo"})
            return await _github_list_heritage_issues(repo)
        
        elif action == "create_vet_issue":
            if not all([repo, issue_number]):
                return json.dumps({"error": "create_vet_issue requires repo, issue_number"})
            return await _github_create_vet_issue(repo, issue_number)
        
        elif action == "get_repo_health":
            if not repo:
                return json.dumps({"error": "get_repo_health requires repo"})
            return await _github_get_repo_health(repo)
    
    except Exception as e:
        logger.warning("github %s failed: %s", action, e)
        return json.dumps({"error": str(e)})


@m9_safe("library_web_search")
@tdp_wrap(source="library_web_search", taint_level=1)
@mcp.tool()
async def library_web_search(query: str, domain: str = "", limit: int = 20) -> str:
    """Search the web via Sovereign Search pipeline (SearXNG → Exa → Firecrawl).
    
    This is the RENAMED tool. The old 'library_search' name is DEPRECATED
    because it misleadingly suggested local library search. Use 'library_fts_search'
    for local FTS5 search, and 'library_web_search' for web search.
    
    Args:
        query: The search query (max 500 chars).
        domain: Optional domain filter (e.g., 'security', 'research').
        limit: Maximum number of results to return.
        
Returns:
        JSON string containing the search results and hit count.
    """
    _deprecated("library_web_search", "library_fts_search (for local) or sovereign_search (for web)")
    _require_service()
    
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})
    
    report = await (await sovereign_search_service).search(
        query, entity_name=domain if domain else "general", limit=limit
    )
    
    return json.dumps({
        "query": query, 
        "status": report["status"],
        "final_tier": report["final_tier"],
        "primary_finding": report["primary_finding"],
        "evidence": report["evidence"],
        "fallback_log": report["fallback_log"],
        "results": report["primary_finding"] if isinstance(report["primary_finding"], list) else [report["primary_finding"]],
        "note": "This is WEB search. For LOCAL library FTS5 search, use 'library_fts_search'."
    }, indent=2, default=str)



# HIVEMIND UNIFIED TOOLS (consolidated from 15 fragmented tools)
# ═══════════════════════════════════════════════════════════════════════════

@m9_safe("hivemind_awareness")
@mcp.tool()
async def hivemind_awareness(
    action: str,
    channel: Optional[str] = None,
    entity: Optional[str] = None,
    model: Optional[str] = None,
    task_current: Optional[str] = None,
    focus_chain: Optional[List[str]] = None,
    decisions: Optional[List[str]] = None,
    continuation: Optional[str] = None,
    session_id: Optional[str] = None,
    intent: Optional[str] = None,
    suggested_model: Optional[str] = None,
    reason: Optional[str] = None,
    ttl_seconds: int = 10800,
    limit: int = 10,
) -> str:
    """Unified Hivemind awareness tool — consolidates 9 fragmented tools.

    Actions (unified names with legacy aliases in parentheses):
        post (hivemind_post_context): Submit a context snapshot. See "THE post CONTRACT" below — it is
              stricter than a truthiness check and is easy to get wrong.
        heartbeat (hivemind_heartbeat): Signal presence (requires channel, entity)
        get (hivemind_get_awareness): Get real-time awareness of all active agents
        continuation (hivemind_get_continuation): Get latest continuation note (requires channel, entity)
        session (hivemind_get_session): Get session by ID (requires session_id)
        list (hivemind_list_sessions): List recent sessions (optional channel, entity, limit)
        entity_context (hivemind_get_entity_context): Get entity startup briefing (requires entity)
        extended_checkin (hivemind_extended_checkin): Register extended session TTL (requires channel, entity, optional reason, ttl_seconds)
        extended_checkout (hivemind_extended_checkout): Cancel extended session (requires channel, entity)

    ── THE `post` CONTRACT ──────────────────────────────────────────────────
    Seven fields are REQUIRED for action="post":

        channel, entity, model, task_current, focus_chain, decisions, continuation

    Required means NOT OMITTED. It does NOT mean non-empty.

      * `decisions=[]` is VALID and means "no decisions were made".
      * `focus_chain=[]` is VALID and means "no prior focus areas".
      * `continuation=""` is VALID and means "no continuation note".
      * Only an explicit `None`, or omitting the argument entirely, is rejected.

    This distinction is deliberate. `post` previously validated with
    `all([...])`, which treats an empty container and an empty string as
    MISSING and rejected perfectly legitimate "none recorded" posts. Worse, it
    signalled failure by returning a JSON error STRING rather than raising, so
    any caller that ignored the return value believed it had posted while
    nothing reached the Hivemind. Validation now tests for `None`, which
    separates "field omitted" from "field present but empty".

    A rejected `post` returns {"error": ..., "missing": [...]} and the field
    names. CALLERS MUST CHECK THE RETURN VALUE. Do not assume a post landed.

    Note: this tool requires initialized hub services (`_require_service()`).
    Posting into a Hivemind that is not yet serving is refused rather than
    silently accepted — a post that reports success into a dead Hivemind is
    the silent-degradation failure this fleet was blind to for 36+ hours.

    ── `entity_context` RESPONSE SCHEMA ─────────────────────────────────────
    Returns exactly five keys:

        {
          "entity":         <str>   the entity NAME, not a dict
          "soul":           <dict>  raw soul.yaml contents, or
                                   {"status": "missing", "error": ...} / {"status": "malformed", "error": ...}
          "knowledge":      {"file_count": int, "total_size_bytes": int, "files": [...]}
          "workspace":      {"file_count": int, "total_size_bytes": int, "files": [...]}
          "recent_sessions": [{"session_id", "timestamp", "task_current", "continuation"}]
        }

    There is no `readiness` key and no registry enrichment. Do not code against
    the pre-consolidation `hivemind_get_entity_context` shape (which exposed
    `entity` as a dict with slot/role, `soul_state` with distilled lessons, and
    a `readiness` block). That response no longer exists.

    Args:
        action: Operation to perform (post|heartbeat|get|continuation|session|list|entity_context|extended_checkin|extended_checkout)
        channel: Execution channel (e.g., 'opencode', 'cline')
        entity: Entity persona (e.g., 'kali', 'roc_racoon')
        model: Current model being used (for post)
        task_current: Active task description (for post)
        focus_chain: Previous sub-tasks/focus areas (for post). [] is valid.
        decisions: Architectural/strategic decisions (for post). [] is valid.
        continuation: Next steps/handoff notes (for post). "" is valid.
        session_id: Session UUID (for session action)
        intent: Semantic intent (question|decision|observation|command|status|handoff|blocker|meta) (for post)
        suggested_model: Model override hint for subagents (for post)
        reason: Human-readable reason (for extended_checkin)
        ttl_seconds: Extended session TTL seconds, max 86400 (for extended_checkin)
        limit: Max sessions to return (for list)

    Returns:
        JSON string with operation result. On `post` rejection the JSON carries
        an "error" key naming the missing fields — CHECK FOR IT.
    """
    _require_service()
    
    # Preserve docstring for legacy adapter validation
    hivemind_awareness.__doc__ = hivemind_awareness.__wrapped__.__doc__
    
    valid_actions = {"post", "heartbeat", "get", "continuation", "session", "list", "entity_context", "extended_checkin", "extended_checkout"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "post":
            # [seam-fix 2026-09-28 maat] Validation is by ABSENCE, not truthiness.
            #
            # The previous check was:
            #     if not all([channel, entity, model, task_current,
            #                  focus_chain, decisions, continuation]):
            # `all()` treats an EMPTY CONTAINER as missing. So `decisions=[]` and
            # `focus_chain=[]` — both legitimate values meaning "none recorded" —
            # were rejected. The pre-consolidation hivemind_post_context had NO
            # validation and accepted them, so this check silently narrowed the
            # contract at the moment the tool was unified.
            #
            # The failure mode is especially nasty: `post` returns a JSON error
            # STRING rather than raising, so callers that ignore the return value
            # believe they posted while nothing reached the Hivemind. Every caller
            # passing an empty list was silently a no-op.
            #
            # Fixed to test for None, which distinguishes "field omitted" from
            # "field present but empty" — the distinction the old tool honoured.
            _required = {
                "channel": channel,
                "entity": entity,
                "model": model,
                "task_current": task_current,
                "focus_chain": focus_chain,
                "decisions": decisions,
                "continuation": continuation,
            }
            _missing = [k for k, v in _required.items() if v is None]
            if _missing:
                return json.dumps({
                    "error": f"post requires: {', '.join(sorted(_missing))}",
                    "missing": sorted(_missing),
                })
            agent_id = _make_agent_id(channel, entity)
            sid = session_id or f"ses_{uuid.uuid4().hex[:12]}"
            snapshot = {
                "session_id": sid,
                "agent_id": agent_id,
                "channel": channel,
                "entity": entity,
                "model": model,
                "task_current": task_current,
                "focus_chain": focus_chain,
                "decisions": decisions,
                "continuation": continuation,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "intent": intent or "status",
                "suggested_model": suggested_model,
            }
            await hot_store_set(sid, snapshot)
            async with _awareness_lock:
                _awareness[agent_id] = snapshot
            await invalidate_awareness_cache()
            cold = _cold_path(agent_id, sid)
            await anyio.Path(str(cold)).parent.mkdir(parents=True, exist_ok=True)
            async with await anyio.open_file(str(cold), "w") as f:
                await f.write(json.dumps(snapshot, indent=2))
            latest = _latest_path()
            async with await anyio.open_file(str(latest), "w") as f:
                await f.write(f"latest_session: {sid}\nupdated: {snapshot['timestamp']}\n")
            return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})
        
        elif action == "heartbeat":
            if not all([channel, entity]):
                return json.dumps({"error": "heartbeat requires channel, entity"})
            agent_id = _make_agent_id(channel, entity)
            result_status = None
            async with _awareness_lock:
                now_str = datetime.now(timezone.utc).isoformat()
                if agent_id in _awareness:
                    _awareness[agent_id]["timestamp"] = now_str
                    result_status = "heartbeat_received"
                else:
                    _awareness[agent_id] = {
                        "agent_id": agent_id,
                        "channel": channel,
                        "entity": entity,
                        "timestamp": now_str,
                        "model": "unknown",
                        "task_current": "heartbeat-only"
                    }
                    result_status = "presence_registered"
            await invalidate_awareness_cache()
            return json.dumps({"status": result_status, "agent_id": agent_id})
        
        elif action == "get":
            now = datetime.now(timezone.utc)
            async with _awareness_lock:
                stale_ids = []
                awareness_list = []
                for agent_id, snap in _awareness.items():
                    ts_str = snap.get("timestamp")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str)
                        if (now - ts).total_seconds() > HEARTBEAT_TTL:
                            stale_ids.append(agent_id)
                            continue
                    awareness_list.append({
                        "agent_id": agent_id,
                        "channel": snap.get("channel", ""),
                        "entity": snap.get("entity", ""),
                        "model": snap.get("model"),
                        "task_current": snap.get("task_current", ""),
                        "last_seen": ts_str or ""
                    })
                for agent_id in stale_ids:
                    del _awareness[agent_id]
            cold_results = await get_cached_cold_awareness()
            hot_ids = {a["agent_id"] for a in awareness_list}
            for cold_agent in cold_results:
                if cold_agent["agent_id"] not in hot_ids:
                    awareness_list.append(cold_agent)
            return json.dumps(awareness_list, indent=2)
        
        elif action == "continuation":
            if not all([channel, entity]):
                return json.dumps({"error": "continuation requires channel, entity"})
            agent_id = _make_agent_id(channel, entity)
            async with _awareness_lock:
                snap = _awareness.get(agent_id)
            if snap:
                continuation = snap.get("continuation", "No continuation note found.")
                session_id = snap.get("session_id", "unknown")
                timestamp = snap.get("timestamp", "unknown")
                task_current = snap.get("task_current", "unknown")
                return f"[Agent: {agent_id} | Session: {session_id} | Time: {timestamp} | Task: {task_current}]\nContinuation: {continuation}"
            def _read_cold_fallback():
                safe_id = agent_id.replace(" ", "_").replace("/", "_")
                agent_dir = HALL_OF_RECORDS / safe_id
                if not agent_dir.exists():
                    return None
                json_files = sorted(agent_dir.glob("ses_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                if not json_files:
                    return None
                try:
                    with json_files[0].open() as f:
                        return json.load(f)
                except Exception as e:
                    logger.debug(f"Cold fallback read failed for {json_files[0].name}: {e}")
                    return None
            cold = await anyio.to_thread.run_sync(_read_cold_fallback)
            if cold:
                continuation = cold.get("continuation", "No continuation note found in cold store.")
                session_id = cold.get("session_id", "unknown")
                timestamp = cold.get("timestamp", "unknown")
                task_current = cold.get("task_current", "unknown")
                return f"[Cold Agent: {agent_id} | Session: {session_id} | Time: {timestamp} | Task: {task_current}]\nContinuation: {continuation}"
            return f"No awareness data for '{agent_id}' (checked hot + cold stores)."
        
        elif action == "session":
            if not session_id:
                return json.dumps({"error": "session requires session_id"})
            snapshot = await hot_store_get(session_id)
            if snapshot is not None:
                return json.dumps(snapshot, indent=2)
            def _find_session():
                for cli_dir in HALL_OF_RECORDS.iterdir():
                    if cli_dir.is_dir():
                        sess_file = cli_dir / f"{session_id}.json"
                        if sess_file.exists():
                            return sess_file
                return None
            sess_file = await anyio.to_thread.run_sync(_find_session)
            if sess_file:
                async with await anyio.open_file(str(sess_file)) as f:
                    content = await f.read()
                return content
            return json.dumps({"error": f"Session '{session_id}' not found"})
        
        elif action == "list":
            filter_id = _make_agent_id(channel, entity) if (channel and entity) else None
            def _list_sessions():
                sessions = []
                if filter_id:
                    safe_id = filter_id.replace(" ", "_").replace("/", "_")
                    agent_dir = HALL_OF_RECORDS / safe_id
                    if agent_dir.exists():
                        for f in sorted(agent_dir.glob("*.json"), reverse=True)[:limit]:
                            sessions.append(f.stem)
                else:
                    for agent_dir in HALL_OF_RECORDS.iterdir():
                        if agent_dir.is_dir():
                            for f in sorted(agent_dir.glob("*.json"), reverse=True)[:limit]:
                                sessions.append({"agent_id": agent_dir.name, "session_id": f.stem})
                return sessions
            sessions = await anyio.to_thread.run_sync(_list_sessions)
            return json.dumps(sessions, indent=2)
        
        elif action == "entity_context":
            if not entity:
                # [seam-fix 2026-09-28 maat] Message names the real parameter
                # (`entity`), not the retired `hivemind_get_entity_context`
                # parameter. The legacy name is still accepted via the adapter's
                # _LEGACY_KWARG_RENAMES map in server.py, so a caller using the
                # old spelling gets this error only if the value is genuinely empty.
                return json.dumps({"error": "entity_context requires entity"})
            _require_service()
            entity_name_lower = entity.lower()
            entity_base = PROJECT_ROOT / "data" / "entities" / entity_name_lower

            def _read_soul() -> dict:
                soul_path = entity_base / "soul.yaml"
                if not soul_path.exists():
                    return {"status": "missing", "error": "soul.yaml not found"}
                try:
                    with open(soul_path) as f:
                        return yaml.safe_load(f) or {}
                except Exception as e:
                    return {"status": "malformed", "error": str(e)}

            def _list_knowledge() -> dict:
                knowledge_dir = entity_base / "knowledge"
                if not knowledge_dir.exists():
                    return {"file_count": 0, "total_size_bytes": 0, "files": []}
                files = []
                total_size = 0
                for f in sorted(knowledge_dir.iterdir()):
                    if not f.is_file():
                        continue
                    total_size += f.stat().st_size
                    if f.suffix.lower() == ".md":
                        try:
                            with open(f) as fh:
                                content = fh.read()
                        except Exception:
                            content = ""
                        lines = content.strip().split("\n")
                        title = ""
                        summary = ""
                        for line in lines:
                            stripped = line.strip()
                            if stripped.startswith("# ") and not title:
                                title = stripped[2:]
                            elif stripped and not summary and not stripped.startswith("#"):
                                summary = stripped[:200]
                                break
                        files.append({"name": f.name, "size": f.stat().st_size, "title": title, "summary": summary})
                    else:
                        files.append({"name": f.name, "size": f.stat().st_size})
                return {"file_count": len(files), "total_size_bytes": total_size, "files": files}

            def _list_workspace() -> dict:
                workspace_dir = entity_base / "workspace"
                if not workspace_dir.exists():
                    return {"file_count": 0, "total_size_bytes": 0, "files": []}
                files = []
                total_size = 0
                for f in sorted(workspace_dir.iterdir()):
                    if not f.is_file():
                        continue
                    total_size += f.stat().st_size
                    files.append({"name": f.name, "size": f.stat().st_size})
                return {"file_count": len(files), "total_size_bytes": total_size, "files": files}

            def _list_sessions() -> list:
                sessions = []
                safe_id = entity.replace(" ", "_").replace("/", "_")
                agent_dir = HALL_OF_RECORDS / safe_id
                if agent_dir.exists():
                    for f in sorted(agent_dir.glob("ses_*.json"), reverse=True)[:10]:
                        try:
                            with open(f) as fh:
                                sess = json.load(fh)
                            sessions.append({
                                "session_id": f.stem,
                                "timestamp": sess.get("timestamp"),
                                "task_current": sess.get("task_current"),
                                "continuation": sess.get("continuation", "")[:200],
                            })
                        except Exception:
                            pass
                return sessions

            # [seam-fix 2026-09-28 maat] Restore the Temple-grade entity_context enrichment
            # that was lost during the Hivemind consolidation. The pre-consolidation
            # hivemind_get_entity_context provided registry enrichment (slot, role,
            # archetype), a readiness block (HYDRATED/DORMANT/UNINITIALIZED with flags),
            # and L3 lesson distillation (recent_lessons). The consolidation lost all
            # of this. This restores it while keeping the unified tool's contract.
            async def _enrich_entity_context(entity_name: str, entity_base: Path, soul: dict) -> dict:
                """Enrich the entity context with registry data, readiness, and L3 lessons."""
                enrichment = {}

                # 1. Registry enrichment: slot, role, archetype
                try:
                    reg = await registry
                    entity_obj = reg.get(entity)  # sync call, not await
                    if entity_obj:
                        # Convert slot format from 'p1' to 'S1' for external API
                        raw_slot = entity_obj.slots[0] if entity_obj.slots else None
                        if raw_slot and raw_slot.startswith('p'):
                            enrichment["slot"] = 'S' + raw_slot[1:]
                        else:
                            enrichment["slot"] = raw_slot
                        enrichment["role"] = "Build" if (entity_obj.slots and entity_obj.slots[0].startswith("S") and int(entity_obj.slots[0][1:]) <= 5) else "Run"
                        enrichment["archetype"] = soul.get("entity", {}).get("archetype") if isinstance(soul.get("entity"), dict) else None
                except Exception:
                    # Registry may not be available or entity not registered; enrichment is best-effort
                    pass

                # 2. Readiness block: HYDRATED / DORMANT / UNINITIALIZED
                # Determine soul validity from the already-parsed soul dict
                soul_status = soul.get("status") if isinstance(soul, dict) else "valid"
                has_valid_soul = soul_status == "valid" or (isinstance(soul, dict) and "status" not in soul)
                has_soul_file = (entity_base / "soul.yaml").exists()
                lessons_path = entity_base / "proposed_lessons.yaml"
                approved_lessons_path = entity_base / "approved_lessons.yaml"
                has_lessons = lessons_path.exists() or approved_lessons_path.exists()

                if has_valid_soul and has_lessons:
                    readiness_status = "HYDRATED"
                    readiness_flags = ["soul_present", "lessons_present"]
                elif has_soul_file:
                    # Soul file exists but may be missing or malformed
                    if soul_status == "missing":
                        readiness_status = "UNINITIALIZED"
                        readiness_flags = []
                    elif soul_status == "malformed":
                        readiness_status = "DORMANT"
                        readiness_flags = ["soul_present", "soul_malformed", "lessons_present"]
                    else:
                        readiness_status = "DORMANT"
                        readiness_flags = ["soul_present"]
                elif has_lessons:
                    # No soul file but lessons exist
                    readiness_status = "DORMANT"
                    readiness_flags = ["lessons_present"]
                else:
                    readiness_status = "UNINITIALIZED"
                    readiness_flags = []

                enrichment["readiness"] = {
                    "status": readiness_status,
                    "flags": readiness_flags,
                }

                # 3. L3 Lesson distillation: recent_lessons from proposed_lessons.yaml (or approved_lessons.yaml)
                lessons_path = entity_base / "proposed_lessons.yaml"
                approved_lessons_path = entity_base / "approved_lessons.yaml"
                lessons_file = lessons_path if lessons_path.exists() else (approved_lessons_path if approved_lessons_path.exists() else None)
                recent_lessons = []
                if lessons_file:
                    try:
                        with open(lessons_file) as f:
                            lessons_data = yaml.safe_load(f) or []
                        # Filter for L3 lessons (outcome starts with "l3_") and sort by timestamp desc
                        l3_lessons = [
                            {
                                "id": lesson.get("trace_id"),
                                "title": lesson.get("lesson", "")[:120],
                                "confidence": "high" if lesson.get("outcome", "").startswith("l3_") else "medium",
                                "distilled_at": lesson.get("timestamp"),
                                "source": lesson.get("source"),
                                "outcome": lesson.get("outcome"),
                            }
                            for lesson in lessons_data
                            if lesson.get("outcome", "").startswith("l3_")
                        ]
                        # Sort by distilled_at descending (most recent first)
                        l3_lessons.sort(key=lambda x: x.get("distilled_at", ""), reverse=True)
                        recent_lessons = l3_lessons[:5]  # Last 5 L3 lessons
                    except Exception:
                        pass

                enrichment["recent_lessons"] = recent_lessons

                return enrichment

            soul = _read_soul()
            knowledge = _list_knowledge()
            workspace = _list_workspace()
            sessions = _list_sessions()
            enrichment = await _enrich_entity_context(entity, entity_base, soul)

            return json.dumps({
                "entity": entity,
                "slot": enrichment.get("slot"),
                "role": enrichment.get("role"),
                "archetype": enrichment.get("archetype"),
                "readiness": enrichment.get("readiness"),
                "soul": soul,
                "knowledge": knowledge,
                "workspace": workspace,
                "recent_sessions": sessions,
                "recent_lessons": enrichment.get("recent_lessons", []),
            }, indent=2)
        
        elif action == "extended_checkin":
            if not all([channel, entity]):
                return json.dumps({"error": "extended_checkin requires channel, entity"})
            agent_id = _make_agent_id(channel, entity)
            ttl_seconds = min(ttl_seconds, 86400)
            async with _awareness_lock:
                if agent_id not in _awareness:
                    _awareness[agent_id] = {
                        "agent_id": agent_id,
                        "channel": channel,
                        "entity": entity,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "model": "unknown",
                        "task_current": "extended_checkin"
                    }
                _awareness[agent_id]["extended_ttl"] = ttl_seconds
                _awareness[agent_id]["extended_reason"] = reason or "Extended Hivemind session — user may forget to check out"
                _awareness[agent_id]["extended_registered_at"] = datetime.now(timezone.utc).isoformat()
            await invalidate_awareness_cache()
            return json.dumps({
                "status": "extended_checkin_registered",
                "agent_id": agent_id,
                "ttl_seconds": ttl_seconds,
                "expires_at": (
                    datetime.now(timezone.utc).timestamp() + ttl_seconds
                ),
            })
        
        elif action == "extended_checkout":
            if not all([channel, entity]):
                return json.dumps({"error": "extended_checkout requires channel, entity"})
            agent_id = _make_agent_id(channel, entity)
            async with _awareness_lock:
                if agent_id in _awareness and "extended_ttl" in _awareness[agent_id]:
                    del _awareness[agent_id]["extended_ttl"]
                    del _awareness[agent_id]["extended_reason"]
                    del _awareness[agent_id]["extended_registered_at"]
                    await invalidate_awareness_cache()
                    return json.dumps({"status": "extended_checkout_complete", "agent_id": agent_id})
                return json.dumps({"status": "no_extended_session", "agent_id": agent_id})
    
    except Exception as e:
        logger.warning("hivemind_awareness %s failed: %s", action, e)
        return json.dumps({"error": str(e)})


@m9_safe("hivemind_lock")
@mcp.tool()
async def hivemind_lock(
    action: str,
    channel: Optional[str] = None,
    entity: Optional[str] = None,
    domain: Optional[str] = None,
    ttl: int = 3600,
) -> str:
    """Unified workspace lock tool — consolidates 3 fragmented tools.
    
    Actions:
        acquire: Acquire an exclusive workspace lock (requires channel, entity, domain, optional ttl)
        release: Release a workspace lock (requires channel, entity, domain)
        check: Check lock status (requires domain)
    
    Args:
        action: Operation to perform (acquire|release|check)
        channel: Execution channel (e.g., 'opencode', 'cline')
        entity: Entity persona (e.g., 'kali', 'roc_racoon')
        domain: Domain/resource to lock
        ttl: Time-to-live in seconds (default 3600, max 86400)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"acquire", "release", "check"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "acquire":
            if not all([channel, entity, domain]):
                return json.dumps({"error": "acquire requires channel, entity, domain"})
            await _reap_stale_locks()
            agent_id = _make_agent_id(channel, entity)
            ttl = min(ttl, 86400)
            lock_path = LOCKS_BASE / f"{domain}.lock"

            def _acquire():
                fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o644)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    os.close(fd)
                    return {"conflict": True, "holder": "unknown (locked by another process)", "domain": domain}

                with os.fdopen(fd, 'r+') as f:
                    existing_data = f.read()
                    now = datetime.now(timezone.utc).timestamp()

                    if existing_data:
                        existing = json.loads(existing_data)
                        acquired_at = existing.get("acquired_at", 0)
                        lock_ttl = existing.get("ttl", 3600)
                        if now <= acquired_at + lock_ttl:
                            return {"conflict": True, "holder": existing.get("agent_id"), "domain": domain}
                        f.seek(0)
                        f.truncate()

                    lock_data = {
                        "agent_id": agent_id,
                        "channel": channel,
                        "entity": entity,
                        "domain": domain,
                        "acquired_at": now,
                        "ttl": ttl,
                    }
                    json.dump(lock_data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                    return lock_data

            result = await anyio.to_thread.run_sync(_acquire)
            if "conflict" in result:
                return json.dumps(result)
            return json.dumps({
                "status": "acquired",
                "agent_id": agent_id,
                "channel": channel,
                "entity": entity,
                "domain": domain,
                "acquired_at": result["acquired_at"],
                "ttl": ttl,
            })
        
        elif action == "release":
            if not all([channel, entity, domain]):
                return json.dumps({"error": "release requires channel, entity, domain"})
            agent_id = _make_agent_id(channel, entity)
            lock_path = LOCKS_BASE / f"{domain}.lock"

            def _release():
                if not lock_path.exists():
                    return {"error": "No lock exists for this domain"}
                with open(lock_path) as f:
                    existing = json.load(f)
                if existing.get("agent_id") != agent_id:
                    return {"error": f"Lock held by '{existing.get('agent_id')}', not '{agent_id}'"}
                lock_path.unlink()
                return {"status": "released", "agent_id": agent_id, "domain": domain}

            result = await anyio.to_thread.run_sync(_release)
            return json.dumps(result)
        
        elif action == "check":
            if not domain:
                return json.dumps({"error": "check requires domain"})
            lock_path = LOCKS_BASE / f"{domain}.lock"
            now = datetime.now(timezone.utc).timestamp()

            def _check():
                if not lock_path.exists():
                    return {"status": "no_lock", "domain": domain}
                with open(lock_path) as f:
                    lock_data = json.load(f)
                acquired_at = lock_data.get("acquired_at", 0)
                lock_ttl = lock_data.get("ttl", 3600)
                age = now - acquired_at
                remaining = max(0, lock_ttl - age)
                return {
                    "status": "locked",
                    "domain": domain,
                    "holder": lock_data.get("agent_id"),
                    "acquired_at": acquired_at,
                    "age_seconds": round(age, 1),
                    "ttl": lock_ttl,
                    "remaining_seconds": round(remaining, 1),
                    "expired": age > lock_ttl,
                }

            result = await anyio.to_thread.run_sync(_check)
            return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.warning("hivemind_lock %s failed: %s", action, e)
        return json.dumps({"error": str(e)})

