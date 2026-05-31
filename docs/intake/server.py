"""Omega Core Hub MCP Server — Consolidated runtime services.

AP Token: AP-OMEGA-CORE-HUB-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: CORE-HUB-MCP]

Consolidates the following services into a single FastMCP endpoint:
  - Oracle: Routing, Summoning, and Entity Intelligence
  - Hivemind: Cross-CLI awareness and session context
  - Library: RAG intake, curation, and offline indexing

Usage:
    cd ~/omega && python mcp/omega_hub/server.py
"""

import sys
import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
from mcp.server.fastmcp import FastMCP

# Ensure omega module is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.hierarchy import SovereignHierarchy
from omega.library.inbox import InboxManager
from omega.library.curator import CurationPipeline
from omega.library.library import Library
from omega.library.indexer import Indexer
from omega.library.discovery import DiscoveryOrchestrator
from omega.observability import new_trace_id, get_engine

# --- INITIALIZATION ---
mcp = FastMCP("Omega Core Hub")

# Oracle / Registry
registry = EntityRegistry()
oracle = Oracle(registry=registry)
hierarchy = SovereignHierarchy()

# Library / Indexing / Discovery
inbox = InboxManager()
curator = CurationPipeline()
library = Library()
indexer = Indexer()
discovery = DiscoveryOrchestrator()

# --- ORACLE TOOLS ---

# Hivemind State (Internal to Hub)
HALL_OF_RECORDS = PROJECT_ROOT / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}

def _cold_path(cli: str, session_id: str) -> Path:
    safe_cli = cli.replace(" ", "_").replace("/", "_")
    safe_sid = session_id.replace("/", "_").replace(":", "_")
    return HALL_OF_RECORDS / safe_cli / f"{safe_sid}.json"

def _latest_path() -> Path:
    return HALL_OF_RECORDS / "latest.yaml"

# --- ORACLE TOOLS ---

@mcp.tool()
async def oracle_talk(query: str) -> str:
    """Route a query through the Omega Oracle. Speculative decoding handled internally."""
    response = await oracle.talk(query)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "pillars": response.pillars,
        "sigil": response.sigil,
        "glyph": response.glyph,
        "pantheon": response.pantheon,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
        "backend": response.backend,
        "escalated": response.escalated,
    }, indent=2)

@mcp.tool()
async def oracle_summon(entity_name: str, query: str) -> str:
    """Directly summon a specific entity by name."""
    response = await oracle.summon(entity_name, query)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "pillars": response.pillars,
        "sigil": response.sigil,
        "pantheon": response.pantheon,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
    }, indent=2)

@mcp.tool()
def oracle_list_entities() -> str:
    """List all entities in the Omega pantheon."""
    entities = registry.list()
    result = [{
        "name": e.name,
        "pillars": e.pillars,
        "role": e.role,
        "pantheon": e.pantheon,
        "element": e.element,
        "chakra": e.chakra,
        "planet": e.planet,
        "glyph": e.glyph,
        "sigil": e.sigil,
        "domains": e.domains,
        "model": e.model,
    } for e in entities]
    return json.dumps(result, indent=2)

@mcp.tool()
def oracle_list_pillar_keepers() -> str:
    """List only the 10 Pillar Keepers (core pantheon)."""
    entities = registry.list_pillar_keepers()
    result = [{
        "name": e.name,
        "pillars": e.pillars,
        "element": e.element,
        "chakra": e.chakra,
        "planet": e.planet,
        "sigil": e.sigil,
    } for e in entities]
    return json.dumps(result, indent=2)

@mcp.tool()
def oracle_entity_info(name: str) -> str:
    """Get detailed information about a specific entity."""
    entity = registry.get(name) or registry.find_by_name_fragment(name)
    if not entity:
        return json.dumps({"error": f"Entity '{name}' not found"})
    return json.dumps({
        "name": entity.name,
        "pillars": entity.pillars,
        "role": entity.role,
        "personality": entity.personality,
        "pantheon": entity.pantheon,
        "element": entity.element,
        "chakra": entity.chakra,
        "planet": entity.planet,
        "glyph": entity.glyph,
        "sigil": entity.sigil,
        "invocation": entity.invocation,
        "domains": entity.domains,
        "model": entity.model,
        "temperature": entity.temperature,
    }, indent=2)

@mcp.tool()
def oracle_assess_intent(query: str) -> str:
    """Test how the Oracle would classify a query without generating a response."""
    from omega.iris.matcher import IntentMatcher
    classification = IntentMatcher().classify(query)
    domain_entity = registry.find_by_domain(query)
    iris_confidence = oracle._assess_iris_confidence(query)
    return json.dumps({
        "query": query,
        "classification": classification,
        "iris_confidence": iris_confidence,
        "would_escalate": iris_confidence <= 0.4,
        "domain_entity": domain_entity.name if domain_entity else None,
        "detected_summon": oracle._detect_summon(query),
    }, indent=2)

# --- HIVEMIND TOOLS ---

@mcp.tool()
async def hivemind_post_context(
    cli: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[Dict[str, str]],
    continuation: str,
    session_id: Optional[str] = None,
) -> str:
    """Submit a context snapshot from any CLI to the hivemind."""
    sid = session_id or f"ses_{uuid.uuid4().hex[:12]}"
    snapshot = {
        "session_id": sid,
        "cli": cli,
        "model": model,
        "task_current": task_current,
        "focus_chain": focus_chain,
        "decisions": decisions,
        "continuation": continuation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    _hot_store[sid] = snapshot
    _awareness[cli] = snapshot

    cold = _cold_path(cli, sid)
    cold.parent.mkdir(parents=True, exist_ok=True)
    async with await anyio.open_file(str(cold), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))

    latest = _latest_path()
    async with await anyio.open_file(str(latest), "w") as f:
        await f.write(f"latest_session: {sid}\nupdated: {snapshot['timestamp']}\n")

    return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})

@mcp.tool()
async def hivemind_get_awareness() -> str:
    """Get real-time awareness of all active CLI agents."""
    awareness_list = [
        {"cli": cli, "model": snap.get("model"), "task_current": snap.get("task_current", ""), "last_seen": snap.get("timestamp", "")}
        for cli, snap in _awareness.items()
    ]
    return json.dumps(awareness_list, indent=2)

@mcp.tool()
async def hivemind_get_continuation(cli: str) -> str:
    """Get the latest continuation note for a specific CLI."""
    snap = _awareness.get(cli)
    if snap:
        return snap.get("continuation", "No continuation note found.")
    return f"No awareness data for CLI '{cli}'."

@mcp.tool()
async def hivemind_get_session(session_id: str) -> str:
    """Retrieve a session snapshot by ID."""
    if session_id in _hot_store:
        return json.dumps(_hot_store[session_id], indent=2)
    for cli_dir in HALL_OF_RECORDS.iterdir():
        if cli_dir.is_dir():
            sess_file = cli_dir / f"{session_id}.json"
            if sess_file.exists():
                async with await anyio.open_file(str(sess_file)) as f:
                    content = await f.read()
                return content
    return json.dumps({"error": f"Session '{session_id}' not found"})

@mcp.tool()
async def hivemind_list_sessions(cli: Optional[str] = None, limit: int = 10) -> str:
    """List recent session snapshots."""
    sessions = []
    if cli:
        cli_dir = HALL_OF_RECORDS / cli
        if cli_dir.exists():
            for f in sorted(cli_dir.glob("*.json"), reverse=True)[:limit]:
                sessions.append(f.stem)
    else:
        for cli_dir in HALL_OF_RECORDS.iterdir():
            if cli_dir.is_dir():
                for f in sorted(cli_dir.glob("*.json"), reverse=True)[:limit]:
                    sessions.append({"cli": cli_dir.name, "session_id": f.stem})
    return json.dumps(sessions, indent=2)

# --- LIBRARY TOOLS ---

@mcp.tool()
async def library_inbox_add_url(url: str, tags: str = "", priority: int = 0) -> str:
    """Add a URL to the intake inbox for later curation."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_url(url, tags=tag_list, priority=priority)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source, "source_type": item.source_type})

@mcp.tool()
async def library_inbox_add_note(text: str, tags: str = "") -> str:
    """Add a text note to the intake inbox."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_note(text, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "title": item.title})

@mcp.tool()
async def library_inbox_add_file(path: str, tags: str = "") -> str:
    """Add a local file path to the intake inbox."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_file(path, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source})

@mcp.tool()
async def library_inbox_list(limit: int = 20) -> str:
    """List pending items in the intake inbox."""
    items = await inbox.list_pending(limit=limit)
    counts = await inbox.count()
    return json.dumps({
        "counts": counts,
        "items": [{"item_id": i.item_id, "source": i.source[:80], "source_type": i.source_type, "title": i.title, "priority": i.priority, "created_at": i.created_at} for i in items],
    }, indent=2)

@mcp.tool()
async def library_inbox_stats() -> str:
    """Get inbox statistics (pending, processing, failed counts)."""
    counts = await inbox.count()
    return json.dumps(counts)

@mcp.tool()
async def library_ingest_pending(limit: int = 5) -> str:
    """Process pending inbox items through curation into the library."""
    ingested = await library.ingest_from_inbox(inbox, curator, limit=limit)
    return json.dumps({
        "ingested": len(ingested),
        "documents": [{"doc_id": d.doc_id, "title": d.title, "domain": d.domain, "quality_score": d.quality_score} for d in ingested],
    }, indent=2)

@mcp.tool()
async def library_search(query: str, domain: str = "", limit: int = 20) -> str:
    """Search the offline library for documents. Uses hybrid search."""
    domain_filter = domain if domain else None
    results = await indexer.hybrid_search(query, domain=domain_filter, limit=limit)
    return json.dumps({"query": query, "count": len(results), "results": results}, indent=2, default=str)

@mcp.tool()
async def library_get_document(doc_id: str) -> str:
    """Get the full content of a library document by ID."""
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
    """List most recently curated library documents."""
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
async def library_discovery_research(query: str, depth: int = 2) -> str:
    """Execute the tiered external discovery pipeline (Gemini -> Exa -> Brave -> Tavily).
    
    Returns a consolidated discovery report. Note: This is synchronous/blocking.
    """
    report = await discovery.discover(query, depth=depth)
    return json.dumps(report.to_dict(), indent=2)

@mcp.tool()
async def library_discovery_start(query: str) -> str:
    """Start a background discovery job and return the job ID.
    
    Use library_discovery_status to poll for results.
    """
    job_id = await discovery.start_discovery(query)
    
    # Spawn background task
    anyio.to_thread.run_sync(
        lambda: anyio.run(discovery.run_discovery_task, job_id)
    )
    
    return json.dumps({"status": "started", "job_id": job_id})

@mcp.tool()
async def library_discovery_status(job_id: str) -> str:
    """Get the current status and partial results of a background discovery job."""
    result = discovery.get_job_status(job_id)
    return json.dumps(result, indent=2)

@mcp.tool()
async def observability_check_recursion(entity_name: str, current_depth: int) -> str:
    """Check if an entity is allowed to spawn a subagent at the given depth.
    
    Args:
        entity_name: The name of the entity attempting to spawn a subagent.
        current_depth: The current depth of the subagent chain (0-indexed).
    """
    result = hierarchy.check_recursion(entity_name, current_depth)
    return json.dumps(result, indent=2)

@mcp.tool()
async def observability_log_boundary_violation(tool_name: str, reason: str, entity: str) -> str:
    """Log a sovereign boundary violation from the OpenCode plugin.
    
    Args:
        tool_name: The tool that was blocked
        reason: Why the entity blocked it
        entity: The entity currently active
    """
    trace_id = new_trace_id()
    get_engine().log_event(
        "boundary.violation",
        trace_id,
        {"tool": tool_name, "reason": reason, "entity": entity}
    )
    
    # Update shared metrics for omega-stats
    metrics_path = Path("data/logs/metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    
    metrics = {"violations": []}
    if metrics_path.exists():
        try:
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
        except: pass
    
    metrics["violations"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "reason": reason,
        "entity": entity
    })
    
    # Keep last 100 violations
    metrics["violations"] = metrics["violations"][-100:]
    
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    return json.dumps({"status": "logged", "trace_id": trace_id})

@mcp.tool()
async def library_index_flush() -> str:
    """Flush search indices to disk."""
    await indexer.flush()
    stats = indexer.stats()
    return json.dumps({"status": "flushed", "stats": stats})

from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
