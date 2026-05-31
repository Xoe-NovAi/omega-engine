"""Omega Core Hub MCP Server — Consolidated runtime services.

AP Token: AP-OMEGA-CORE-HUB-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: MiMo-2.5 | CONTEXT: CORE-HUB-MCP]

Consolidates the following services into a single FastMCP endpoint:
  - Oracle: Routing, Summoning, and Entity Intelligence
  - Hivemind: Cross-CLI awareness and session context
  - Library: RAG intake, curation, and offline indexing
  - Research: Multi-depth research engine (consolidated from omega-research MCP)
  - Stats: System monitoring and Omega metrics (consolidated from omega-stats MCP)

Usage:
    cd ~/Documents/Xoe-NovAi/omega-engine && python mcp_servers/omega_hub/server.py
"""

import sys
import os
import json
import logging
import uuid
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import anyio
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

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
from omega.library.research import ResearchEngine, RESEARCH_DEPTHS
from omega.mcp_runtime import run_mcp

logger = logging.getLogger("omega.hub")

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

# Research engine (consolidated from omega-research MCP)
research_engine = ResearchEngine()

# Background task tracking (prevents garbage collection of fire-and-forget tasks)
_background_tasks: set = set()
_global_tg: Optional[anyio.abc.TaskGroup] = None

# --- HIVEMIND STATE ---
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}
_hot_store_lock = anyio.Lock()
_awareness_lock = anyio.Lock()
HEARTBEAT_TTL = 300  # TTL for agent presence in seconds
_current_entity: Optional[str] = None  # Tracks the last entity used by oracle_talk/oracle_summon


def _cold_path(cli: str, session_id: str) -> Path:
    safe_cli = cli.replace(" ", "_").replace("/", "_")
    safe_sid = session_id.replace("/", "_").replace(":", "_")
    return HALL_OF_RECORDS / safe_cli / f"{safe_sid}.json"


def _latest_path() -> Path:
    return HALL_OF_RECORDS / "latest.yaml"


# --- BACKGROUND TASKS ---

async def _prune_awareness_background() -> None:
    """Background loop to prune stale agents from the hivemind."""
    while True:
        try:
            now = datetime.now(timezone.utc)
            async with _awareness_lock:
                stale_clis = [
                    cli for cli, snap in _awareness.items()
                    if snap.get("timestamp") and (now - datetime.fromisoformat(snap["timestamp"])).total_seconds() > HEARTBEAT_TTL
                ]
                for cli in stale_clis:
                    del _awareness[cli]
                if stale_clis:
                    logger.info(f"Pruned {len(stale_clis)} stale agents from awareness.")
        except Exception as e:
            logger.error(f"Awareness pruning failed: {e}")
        await anyio.sleep(60)


async def _run_discovery_background(job_id: str) -> None:
    """Run a discovery task in the background without blocking the tool response."""
    try:
        await discovery.run_discovery_task(job_id)
    except Exception as e:
        logger.error(f"Discovery background task {job_id} failed: {e}")


# === ORACLE TOOLS (8) ===

@mcp.tool()
async def oracle_talk(query: str) -> str:
    """Route a query through the Omega Oracle. Speculative decoding handled internally."""
    global _current_entity
    response = await oracle.talk(query)
    _current_entity = response.entity
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
    global _current_entity
    response = await oracle.summon(entity_name, query)
    _current_entity = response.entity
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


@mcp.tool()
async def oracle_discover_entity(query: str) -> str:
    """Find the best entity in the pantheon to handle a specific task or domain.

    Args:
        query: A description of the task or a domain keyword.
    """
    entity = registry.find_by_domain(query)
    if not entity:
        return json.dumps({"error": "No matching entity found for this domain."})
    return json.dumps({
        "entity": entity.name,
        "pillars": entity.pillars,
        "role": entity.role,
        "domains": entity.domains,
        "reason": f"Matched domain via query: {query}"
    }, indent=2)


@mcp.tool()
async def delegate_task(target_entity: str, query: str, context: str = "") -> str:
    """Delegate a task to another entity and receive their response.

    This allows agents to collaborate by summoning specialized keepers for sub-tasks.

    Args:
        target_entity: The name of the entity to delegate to.
        query: The specific request or question for the target entity.
        context: Optional background context or findings to pass along.
    """
    full_query = f"CONTEXT: {context}\n\nREQUEST: {query}" if context else query
    try:
        response = await oracle.summon(target_entity, full_query)
        return json.dumps({
            "status": "delegated",
            "target": response.entity,
            "response": response.text,
            "trace_id": response.trace_id,
            "backend": response.backend,
            "model": response.model,
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Delegation failed: {str(e)}"})


# === HIVEMIND TOOLS (6) ===

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

    async with _hot_store_lock:
        _hot_store[sid] = snapshot
    async with _awareness_lock:
        _awareness[cli] = snapshot

    cold = _cold_path(cli, sid)
    await anyio.to_thread.run_sync(lambda: cold.parent.mkdir(parents=True, exist_ok=True))
    async with await anyio.open_file(str(cold), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))

    latest = _latest_path()
    async with await anyio.open_file(str(latest), "w") as f:
        await f.write(f"latest_session: {sid}\nupdated: {snapshot['timestamp']}\n")

    return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})


@mcp.tool()
async def hivemind_heartbeat(cli: str) -> str:
    """Signal presence to the hivemind to avoid being pruned as stale."""
    async with _awareness_lock:
        now_str = datetime.now(timezone.utc).isoformat()
        if cli in _awareness:
            _awareness[cli]["timestamp"] = now_str
            return json.dumps({"status": "heartbeat_received", "cli": cli})
        _awareness[cli] = {
            "cli": cli,
            "timestamp": now_str,
            "model": "unknown",
            "task_current": "heartbeat-only"
        }
        return json.dumps({"status": "presence_registered", "cli": cli})


@mcp.tool()
async def hivemind_get_awareness() -> str:
    """Get real-time awareness of all active CLI agents."""
    now = datetime.now(timezone.utc)
    async with _awareness_lock:
        stale_clis = []
        awareness_list = []
        for cli, snap in _awareness.items():
            ts_str = snap.get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                if (now - ts).total_seconds() > HEARTBEAT_TTL:
                    stale_clis.append(cli)
                    continue
            awareness_list.append({
                "cli": cli,
                "model": snap.get("model"),
                "task_current": snap.get("task_current", ""),
                "last_seen": ts_str or ""
            })
        for cli in stale_clis:
            del _awareness[cli]
    return json.dumps(awareness_list, indent=2)


@mcp.tool()
async def hivemind_get_continuation(cli: str) -> str:
    """Get the latest continuation note for a specific CLI."""
    async with _awareness_lock:
        snap = _awareness.get(cli)
    if snap:
        return snap.get("continuation", "No continuation note found.")
    return f"No awareness data for CLI '{cli}'."


@mcp.tool()
async def hivemind_get_session(session_id: str) -> str:
    """Retrieve a session snapshot by ID."""
    async with _hot_store_lock:
        if session_id in _hot_store:
            return json.dumps(_hot_store[session_id], indent=2)

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


@mcp.tool()
async def hivemind_list_sessions(cli: Optional[str] = None, limit: int = 10) -> str:
    """List recent session snapshots."""
    def _list_sessions():
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
        return sessions

    sessions = await anyio.to_thread.run_sync(_list_sessions)
    return json.dumps(sessions, indent=2)


# === LIBRARY TOOLS (12) ===

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
async def library_index_flush() -> str:
    """Flush search indices to disk."""
    await indexer.flush()
    stats = indexer.stats()
    return json.dumps({"status": "flushed", "stats": stats})


# === DISCOVERY TOOLS (3) ===

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
    if _global_tg:
        _global_tg.start_soon(_run_discovery_background, job_id)
    else:
        async with anyio.create_task_group() as tg:
            tg.start_soon(_run_discovery_background, job_id)
    return json.dumps({"status": "started", "job_id": job_id})


@mcp.tool()
async def library_discovery_status(job_id: str) -> str:
    """Get the current status and partial results of a background discovery job."""
    result = discovery.get_job_status(job_id)
    return json.dumps(result, indent=2)


# === RESEARCH TOOLS (5) ===

@mcp.tool()
async def research(query: str, depth: int = 2, domain: str = "") -> str:
    """Execute multi-depth research on a query using the offline library.

    Depth levels: 1=Quick (1-2 sources), 2=Standard (3-5 sources),
    3=Deep (6-15 sources), 4=Scholarly (10-50 sources).

    Args:
        query: The research question or topic
        depth: Research depth (1-4)
        domain: Optional domain filter
    """
    depth = max(1, min(4, depth))
    domain_filter = domain if domain else None
    result = await research_engine.research(query, depth=depth, domain=domain_filter)
    return json.dumps(result.to_dict(), indent=2, default=str)


@mcp.tool()
async def research_get(research_id: str) -> str:
    """Retrieve a previous research result by ID.

    Args:
        research_id: Research ID (e.g. res_abc123)
    """
    result = await research_engine.get_result(research_id)
    if not result:
        return json.dumps({"error": f"Research '{research_id}' not found"})
    return json.dumps(result.to_dict(), indent=2, default=str)


@mcp.tool()
async def research_list(limit: int = 20) -> str:
    """List recent research results.

    Args:
        limit: Maximum results to return
    """
    results = await research_engine.list_results(limit=limit)
    return json.dumps(results, indent=2, default=str)


@mcp.tool()
async def research_depths() -> str:
    """List available research depth levels and their configurations."""
    return json.dumps(RESEARCH_DEPTHS, indent=2)


@mcp.tool()
async def research_stats() -> str:
    """Get research engine statistics."""
    results = await research_engine.list_results(limit=1000)
    depths = {}
    for r in results:
        d = str(r.get("depth", 2))
        depths[d] = depths.get(d, 0) + 1
    return json.dumps({
        "total_research": len(results),
        "by_depth": depths,
    }, indent=2)


# === STATS TOOLS (5) ===

@mcp.tool()
async def get_system_stats() -> str:
    """Get comprehensive system stats: zRAM, CPU, disk, GPU, memory, Podman."""
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
    except Exception:
        pass

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
    except Exception:
        pass

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
        except Exception:
            pass

    # Disk — omega_library partition
    try:
        statvfs = os.statvfs("/media/arcana-novai/omega_library")
        total = statvfs.f_frsize * statvfs.f_blocks // (1024**3)
        free = statvfs.f_frsize * statvfs.f_bfree // (1024**3)
        stats["disk"] = {
            "available": True,
            "mount": "/media/arcana-novai/omega_library",
            "total_gb": total,
            "free_gb": free,
            "used_gb": total - free,
            "used_pct": round((total - free) / total * 100, 1) if total > 0 else 0,
        }
    except Exception:
        pass

    # Vulkan iGPU
    gpu_path = Path("/sys/class/drm/card1/device/gpu_busy_percent")
    if gpu_path.exists():
        try:
            with open(gpu_path) as f:
                stats["gpu"] = {
                    "available": True,
                    "utilization_pct": int(f.read().strip()),
                }
        except Exception:
            pass

    # Podman
    try:
        def _podman_ps():
            return os.popen("podman ps --format json 2>/dev/null").read()
        result = await anyio.to_thread.run_sync(_podman_ps)
        if result:
            containers = json.loads(result)
            stats["podman"] = {
                "available": True,
                "running": sum(1 for c in containers if c.get("State") == "running"),
                "total": len(containers),
                "names": [c.get("Names", [""])[0] for c in containers],
            }
    except Exception:
        pass

    # Ryzen tuning check
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            governor = f.read().strip()
        stats["ryzen_tuning"] = {
            "available": True,
            "governor": governor,
        }
    except Exception:
        pass

    return json.dumps(stats, indent=2)


@mcp.tool()
async def get_omega_metrics() -> str:
    """Get aggregated Omega Engine metrics (Inference, Research, Memory, and Errors)."""
    metrics_path = PROJECT_ROOT / "data" / "logs" / "metrics.json"
    if not metrics_path.exists():
        return json.dumps({"error": "Metrics file not found. No metrics have been recorded yet."}, indent=2)
    try:
        def _read():
            with open(metrics_path, "r") as f:
                return json.load(f)
        metrics = await anyio.to_thread.run_sync(_read)
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read metrics: {str(e)}"}, indent=2)


@mcp.tool()
def check_models_directory() -> str:
    """Check available GGUF models on omega_library partition."""
    models_dir = Path("/media/arcana-novai/omega_library/models/gguf")
    if not models_dir.exists():
        return json.dumps({"error": "Models directory not found"})
    models = []
    for f in sorted(models_dir.glob("*.gguf")):
        size_gb = round(f.stat().st_size / (1024**3), 2)
        models.append({"name": f.name, "size_gb": size_gb})
    return json.dumps({
        "path": str(models_dir),
        "total_models": len(models),
        "models": models,
    }, indent=2)


@mcp.tool()
def check_podman_storage() -> str:
    """Check Podman storage usage on omega_library."""
    storage_dir = Path("/media/arcana-novai/omega_library/podman-storage")
    if not storage_dir.exists():
        return json.dumps({"error": "Podman storage directory not found"})
    try:
        total_size = sum(f.stat().st_size for f in storage_dir.rglob("*") if f.is_file())
        size_mb = round(total_size / (1024**2), 1)
        return json.dumps({
            "path": str(storage_dir),
            "size_mb": size_mb,
            "exists": True,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# === OBSERVABILITY TOOLS (2) ===

@mcp.tool()
async def observability_check_recursion(entity_name: str, current_depth: int) -> str:
    """Check if an entity is allowed to spawn a subagent at the given depth.

    Args:
        entity_name: The name of the entity attempting to spawn a subagent.
        current_depth: The current depth of the subagent chain (0-indexed).
    """
    if not hierarchy._hierarchy:
        await hierarchy.load()
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

    metrics_path = PROJECT_ROOT / "data" / "logs" / "metrics.json"
    await anyio.to_thread.run_sync(lambda: metrics_path.parent.mkdir(parents=True, exist_ok=True))

    metrics = {"violations": []}
    if metrics_path.exists():
        try:
            def _read():
                with open(metrics_path) as f:
                    return json.load(f)
            metrics = await anyio.to_thread.run_sync(_read)
        except Exception:
            logger.warning(f"Could not read metrics file: {metrics_path}, starting fresh")

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


# === HTTP ENDPOINT ROUTES (OpenCode Plugin / Health / Identity) ===

def _add_hub_endpoints(app):
    """Add HTTP endpoints for OpenCode handshake, health checks, and identity."""

    async def _health(request):
        return JSONResponse({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})

    async def _entity_current(request):
        entity_name = _current_entity or "SOPHIA"
        entity = registry.get(entity_name)
        return JSONResponse(asdict(entity) if entity else {"entity": entity_name})

    async def _soul_check_boundary(request):
        return JSONResponse({"result": "ALLOW"})

    async def _soul_filter_output(request):
        try:
            body = await request.json()
            return JSONResponse({"filtered": False, "output": body.get("output", "")})
        except Exception:
            return JSONResponse({"filtered": True, "output": ""})

    async def _config_providers(request):
        try:
            path = PROJECT_ROOT / "config" / "providers.yaml"
            if path.exists():
                import yaml
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                return JSONResponse(data)
            return JSONResponse({"providers": []})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _provider_list(request):
        try:
            path = PROJECT_ROOT / "config" / "providers.yaml"
            if path.exists():
                import yaml
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                chain = data.get("inference", {}).get("fallback_chain", [])
                names = [p.get("provider") for p in chain if "provider" in p]
                return JSONResponse({"providers": names})
            return JSONResponse({"providers": []})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _app_agents(request):
        try:
            from dataclasses import asdict
            return JSONResponse([asdict(a) for a in registry.list()])
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _config_get(request):
        return JSONResponse({"version": "1.0.0", "status": "healthy"})

    @asynccontextmanager
    async def lifespan(app):
        global _global_tg
        _global_tg = anyio.create_task_group()
        await _global_tg.__aenter__()
        _global_tg.start_soon(_prune_awareness_background)
        yield
        if _global_tg:
            await _global_tg.__aexit__(None, None, None)
            _global_tg = None

    app.router.lifespan_context = lifespan
    app.add_route("/health", _health)
    app.add_route("/entity/current", _entity_current)
    app.add_route("/soul/check-boundary", _soul_check_boundary, methods=["POST"])
    app.add_route("/soul/filter-output", _soul_filter_output, methods=["POST"])
    app.add_route("/config/providers", _config_providers)
    app.add_route("/provider/list", _provider_list)
    app.add_route("/app/agents", _app_agents)
    app.add_route("/config/get", _config_get)


if __name__ == "__main__":
    run_mcp(mcp, modify_app=_add_hub_endpoints)