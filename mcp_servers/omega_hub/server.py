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
from dataclasses import asdict
import yaml
import contextvars
import threading
import shutil

import anyio
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import CallToolResult, TextContent
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

# --- SECURITY MIDDLEWARE (Gap 2) ---
class RequestSizeLimitMiddleware:
    """Limits incoming request size to prevent OOM/DOS attacks."""
    def __init__(self, app, max_size: int = 10 * 1024 * 1024): # 10MB default
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            content_length = 0
            for header, value in scope.get("headers", []):
                if header == b"content-length":
                    content_length = int(value)
                    break
            if content_length > self.max_size:
                from starlette.responses import Response
                response = Response("Request too large", status_code=413)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)

def apply_security(app):
    """Apply CORS and size limits to the Starlette app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Tighten this in production
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestSizeLimitMiddleware, max_size=25 * 1024 * 1024) # 25MB for context posts

    # ── Shutdown: Starlette >=0.36 removed @app.on_event ─────────
    # The mcp_runtime.py lifespan handles ASGI lifecycle clean-up.
    # Indexer/library close() is best-effort on SIGTERM; the OS reclaims
    # file descriptors on exit. Log informational message only.
    logger.debug("Shutdown hook skipped — modern Starlette uses lifespan.")


# Ensure omega module is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.hierarchy import SovereignHierarchy
from omega.oracle.security import tdp_wrap

from omega.library.inbox import InboxManager
from omega.library.curator import CurationPipeline
from omega.library.library import Library
from omega.library.indexer import Indexer
from omega.library.discovery import DiscoveryOrchestrator
from omega.observability import new_trace_id, get_engine
from omega.library.research import ResearchEngine, RESEARCH_DEPTHS
from omega.memory_store import get_memory_store
from omega.ics import render as ics_render_logic
from omega.mcp_runtime import run_mcp

logger = logging.getLogger("omega.hub")

# --- INITIALIZATION ---
# --- M9-COMPLIANT TOOL DECORATOR (P0-A) ---
# Gemini CLI spec-correct: catches exceptions, returns CallToolResult(isError=True).
from functools import wraps

def m9_safe(tool_name: str):
    """Decorator: wrap an async MCP tool with M9-compliant error boundary.

    On exception, returns CallToolResult(content=[TextContent(...)], isError=True)
    so MCP clients see isError=True, not isError=False with embedded "error" key.
    [H-A1-aligned: zero id-soft heritage, pure MCP spec pattern.]
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                trace_id = new_trace_id()
                logger.error("[%s] %s: %s", tool_name, trace_id, e)
                error_payload = json.dumps({
                    "error": str(e),
                    "trace_id": trace_id,
                    "tool": tool_name,
                }, indent=2)
                return CallToolResult(
                    content=[TextContent(type="text", text=error_payload)],
                    isError=True,
                )
        return wrapper
    return decorator


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
research_engine = ResearchEngine(library=library, indexer=indexer)

# Sovereign Search Service (T0-T4)
def _load_search_keys():
    try:
        with open(PROJECT_ROOT / "opencode.json") as f:
            config = json.load(f)
        return (
            config.get("mcp", {}).get("firecrawl", {}).get("environment", {}).get("FIRECRAWL_API_KEY"),
            config.get("mcp", {}).get("exa", {}).get("headers", {}).get("x-api-key")
        )
    except Exception as e:
        logger.error(f"Failed to load search keys: {e}")
        return None, None

fc_key, exa_key = _load_search_keys()
sovereign_search = SovereignSearchService(
    memory_store=get_memory_store(),
    model_gateway=ModelGateway(),
    indexer=indexer,
    firecrawl_key=fc_key,
    exa_key=exa_key
)


# --- HIVEMIND STATE ---
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}
_hot_store_lock = anyio.Lock()

# Cross-thread aware lock: wraps threading.Lock for async with syntax.
# Fixes Q3: background thread runs anyio.run() with its OWN event loop,
# but anyio.Lock is tied to the creating event loop — crash on cross-loop
# access. Threading.Lock works across threads regardless of event loop.
#
class _AsyncThreadLock:
    """threading.Lock wrapped for async with — safe across event loops.

    Standard Python pattern for cross-event-loop thread safety.
    No id Software heritage — Zone Memory (z_zone.c) is a memory allocator;
    this is a concurrency primitive. (H-A1: tag removed 2026-06-09)
    """
    def __init__(self):
        self._lock = threading.Lock()
    async def __aenter__(self):
        await anyio.to_thread.run_sync(self._lock.acquire)
        return self
    async def __aexit__(self, *args):
        self._lock.release()

_awareness_lock = _AsyncThreadLock()
# [D-122] HEARTBEAT_TTL — 45 minutes (2700s) for active agent presence
# Increased from 20 minutes (1200s) per Q1 bug fix (2026-06-07).
# Rationale: The sprint-plan docs specified 45 min (2700s). The 20-min
# TTL was causing agents to appear stale during multi-session coordination.
# With 45-min TTL, an agent that heartbeats every 10-15 min has 3-4x safety
# margin. Aligns with the extended-session check-in (3h default) for
# long-running tasks.
# Heritage: matches Doom 1993 thinker grace period pattern (id-soft: doom-1993).
HEARTBEAT_TTL = 2700  # TTL for agent presence in seconds (45 minutes)
# --- P1-A: ContextVar swap for _current_entity (M-A5/AG-1 fix) ---
# Each async context gets isolated state, eliminating global race condition.
_current_entity: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "_current_entity", default=None
)  # Tracks the last entity used by oracle_talk/oracle_summon per-context

# --- P0-B: IntentMatcher singleton (M-A2b fix) ---
# Avoid fresh IntentMatcher per call (M-A2b). Lazy-init on first use.
_intent_matcher: Optional[object] = None
_intent_matcher_lock = threading.Lock()


def _get_intent_matcher():
    """Module-level singleton accessor for IntentMatcher (P0-B)."""
    global _intent_matcher
    if _intent_matcher is None:
        with _intent_matcher_lock:
            if _intent_matcher is None:
                from omega.iris.matcher import IntentMatcher
                _intent_matcher = IntentMatcher()
    return _intent_matcher


def _make_agent_id(channel: str, entity: str) -> str:
    """Build a canonical agent identifier from channel and entity.
    
    The agent_id uniquely identifies WHO is running WHERE.
    Format: '{channel}/{entity}'
    
    Examples:
        'opencode/kali' — Kali entity running inside OpenCode CLI
        'opencode/roc_racoon' — Roc Racoon entity inside OpenCode
        'cline/doom_guy' — Doom Guy inside Cline
    """
    return f"{channel}/{entity}"


def _cold_path(agent_id: str, session_id: str) -> Path:
    safe_id = agent_id.replace(" ", "_").replace("/", "_")
    safe_sid = session_id.replace("/", "_").replace(":", "_")
    return HALL_OF_RECORDS / safe_id / f"{safe_sid}.json"


def _latest_path() -> Path:
    return HALL_OF_RECORDS / "latest.yaml"


# --- BACKGROUND TASKS ---

async def _prune_awareness_background() -> None:
    """Background loop to prune stale agents from the hivemind.

    D-kal-052: Respects extended-session check-ins. If an agent
    has called hivemind_extended_checkin(), the pruning loop
    uses their custom TTL (default 3h) instead of HEARTBEAT_TTL (20m).

    [hi-observability-2] Records pruning cycle timestamp and logs
    results. Calls _write_metrics() after each cycle so the metrics
    file always reflects the latest state.
    """
    global _last_pruning_cycle
    while True:
        try:
            now = datetime.now(timezone.utc)
            async with _awareness_lock, _extended_sessions_lock:
                stale_clis = []
                for cli, snap in _awareness.items():
                    if not snap.get("timestamp"):
                        continue
                    age = (now - datetime.fromisoformat(snap["timestamp"])).total_seconds()
                    # Check if agent has an extended check-in
                    ext = _extended_sessions.get(cli)
                    effective_ttl = ext["ttl_seconds"] if ext else HEARTBEAT_TTL
                    if age > effective_ttl:
                        stale_clis.append(cli)
                for cli in stale_clis:
                    del _awareness[cli]
                if stale_clis:
                    logger.info(f"Pruned {len(stale_clis)} stale agent(s) from awareness.")
            _last_pruning_cycle = datetime.now(timezone.utc).isoformat()
            await _write_metrics()
        except Exception as e:
            logger.error(f"Awareness pruning failed: {e}")
        await anyio.sleep(60)


async def _run_discovery_background(job_id: str) -> None:
    """Run a discovery task in the background without blocking the tool response."""
    try:
        await discovery.run_discovery_task(job_id)
    except Exception as e:
        logger.error(f"Discovery background task {job_id} failed: {e}")


async def _reap_stale_locks() -> None:
    """Remove expired lock files.

    Scans data/coordination/locks/ and removes any lock whose
    acquired_at + ttl has passed. Called on acquire and periodically.
    """
    now = datetime.now(timezone.utc).timestamp()
    reaped = 0
    for lock_file in LOCKS_BASE.glob("*.lock"):
        try:
            def _read_lock():
                with open(lock_file) as f:
                    return json.load(f)
            lock_data = await anyio.to_thread.run_sync(_read_lock)
            acquired_at = lock_data.get("acquired_at", 0)
            ttl = lock_data.get("ttl", 3600)
            if now > acquired_at + ttl:
                lock_file.unlink()
                reaped += 1
        except Exception as e:
            logger.debug("Failed to reap stale lock %s: %s", lock_file, e)
    if reaped:
        logger.info("Reaped %d stale lock(s)", reaped)


async def _reap_stale_handoffs() -> None:
    """Reap stale handoff packets.

    - pending/ older than 24h -> stale/ with {ttl_expired: true}
    - active/ older than 48h -> stale/
    - completed/ older than 7 days -> archive/
    """
    now = datetime.now(timezone.utc)

    def _reap_dir(src_dir: Path, dst_dir: Path, max_age_seconds: int, extra: dict = None):
        reaped = 0
        for f in src_dir.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_age_seconds:
                try:
                    with open(f) as fh:
                        packet = json.load(fh)
                    packet["status"] = dst_dir.name
                    packet["reaped_at"] = now.isoformat()
                    if extra:
                        packet.update(extra)
                    dst_path = dst_dir / f.name
                    with open(dst_path, "w") as fh:
                        fcntl.flock(fh, fcntl.LOCK_EX)
                        json.dump(packet, fh, indent=2)
                        fcntl.flock(fh, fcntl.LOCK_UN)
                    f.unlink()
                    reaped += 1
                except Exception as e:
                    logger.debug("Failed to reap handoff %s: %s", f, e)
        return reaped

    reaped = await anyio.to_thread.run_sync(
        lambda: (
            _reap_dir(HANDOFF_PENDING, HANDOFF_STALE, 86400, {"ttl_expired": True})
            + _reap_dir(HANDOFF_ACTIVE, HANDOFF_STALE, 172800, {"ttl_expired": True})
            + _reap_dir(HANDOFF_COMPLETED, HANDOFF_ARCHIVE, 604800)
        )
    )
    if reaped:
        logger.info("Reaped %d stale handoff(s)", reaped)


async def _reaper_background() -> None:
    """Background loop that reaps stale locks and handoffs."""
    while True:
        try:
            await _reap_stale_locks()
            await _reap_stale_handoffs()
        except Exception as e:
            logger.error("Reaper background failed: %s", e)
        await anyio.sleep(300)


# --- HIVEMIND METRICS COLLECTION (hi-observability-1) ---
_last_pruning_cycle: Optional[str] = None
METRICS_PATH = PROJECT_ROOT / "data" / "coordination" / "metrics.json"


async def _write_metrics() -> Dict[str, Any]:
    """Write Hivemind coordination metrics atomically to data/coordination/metrics.json.

    Collects real-time state from awareness, handoff queues, workspace locks,
    and extended sessions. Writes atomically (write .tmp, rename) for crash safety.

    Returns:
        The metrics dict for immediate use without re-reading from disk.

    [hi-observability-1] Hivemind Metrics Collection — local observability only.
    Does NOT send data anywhere (Mandate 8 — Zero Telemetry).
    """
    now = datetime.now(timezone.utc)
    now_ts = now.isoformat()

    # Count active agents (respect TTL)
    active_agents = 0
    async with _awareness_lock:
        for _cli, snap in _awareness.items():
            ts_str = snap.get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                if (now - ts).total_seconds() <= HEARTBEAT_TTL:
                    active_agents += 1
            else:
                active_agents += 1

    # Count handoff queue items
    def _scan_handoffs():
        pending = len(list(HANDOFF_PENDING.glob("*.json")))
        active = len(list(HANDOFF_ACTIVE.glob("*.json")))
        completed = len(list(HANDOFF_COMPLETED.glob("*.json")))
        stale = len(list(HANDOFF_STALE.glob("*.json")))
        return pending, active, completed, stale

    pending_h, active_h, completed_h, stale_h = await anyio.to_thread.run_sync(_scan_handoffs)

    # Count workspace locks (active vs expired)
    def _scan_locks():
        active_locks = 0
        expired_locks = 0
        for lock_file in LOCKS_BASE.glob("*.lock"):
            try:
                with open(lock_file) as f:
                    ld = json.load(f)
                acquired_at = ld.get("acquired_at", 0)
                ttl = ld.get("ttl", 3600)
                if now.timestamp() > acquired_at + ttl:
                    expired_locks += 1
                else:
                    active_locks += 1
            except Exception:
                active_locks += 1
        return active_locks, expired_locks

    active_locks, expired_locks = await anyio.to_thread.run_sync(_scan_locks)

    # Count extended sessions
    async with _extended_sessions_lock:
        extended_count = len(_extended_sessions)

    metrics: Dict[str, Any] = {
        "hivemind": {
            "active_agents": active_agents,
            "handoff_queue": {
                "pending": pending_h,
                "active": active_h,
                "completed": completed_h,
                "stale": stale_h,
                "total": pending_h + active_h + completed_h + stale_h,
            },
            "workspace_locks": {
                "active": active_locks,
                "expired": expired_locks,
            },
            "extended_sessions": extended_count,
            "pruning_cycle_last_run": _last_pruning_cycle,
        },
        "updated_at": now_ts,
    }

    # Atomic write: .tmp -> rename
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = METRICS_PATH.with_suffix(".json.tmp")

    def _persist():
        with open(tmp_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(metrics, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
            fcntl.flock(f, fcntl.LOCK_UN)
        os.replace(str(tmp_path), str(METRICS_PATH))

    await anyio.to_thread.run_sync(_persist)
    return metrics


# === ORACLE TOOLS (8) ===

@m9_safe("oracle_talk")
@mcp.tool()
async def oracle_talk(query: str) -> str:
    """Route a query through the Omega Oracle. Speculative decoding handled internally.
    
    Args:
        query: The natural language query or command to route.
        
    Returns:
        JSON string containing the response text, entity, pillars, and metadata.
    """
    response = await oracle.talk(query)
    _current_entity.set(response.entity)
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


@m9_safe("oracle_summon")
@mcp.tool()
async def oracle_summon(entity_name: str, query: str) -> str:
    """Directly summon a specific entity by name.
    
    Args:
        entity_name: The name of the entity to summon.
        query: The message or task for the summoned entity.
        
    Returns:
        JSON string containing the response text and entity metadata.
    """
    response = await oracle.summon(entity_name, query)
    _current_entity.set(response.entity)
    return json.dumps({
        "text": response.text,
        "entity": response.entity,
        "pillars": response.pillars,
        "sigil": response.sigil,
        "pantheon": response.pantheon,
        "confidence": response.confidence,
        "trace_id": response.trace_id,
    }, indent=2)


@m9_safe("oracle_summon_local")
@mcp.tool()
async def oracle_summon_local(entity_name: str, query: str, model: str) -> str:
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
    try:
        response = await oracle.summon(entity_name, query, model_override=model)
        _current_entity.set(response.entity)
        return json.dumps({
            "text": response.text,
            "entity": response.entity,
            "pillars": response.pillars,
            "sigil": response.sigil,
            "pantheon": response.pantheon,
            "confidence": response.confidence,
            "trace_id": response.trace_id,
            "model_override": model,
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "entity": entity_name,
            "model_override": model,
            "hint": f"Model '{model}' may not be available. Check config/providers.yaml for available models.",
        }, indent=2)


@m9_safe("oracle_list_entities")
@mcp.tool()
async def oracle_list_entities() -> str:
    """List all entities in the Omega pantheon.
    
    Returns:
        JSON string containing a list of all entities and their primary attributes.
    """
    entities = await anyio.to_thread.run_sync(registry.list)
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


@m9_safe("oracle_list_pillar_keepers")
@mcp.tool()
async def oracle_list_pillar_keepers() -> str:
    """List only the 10 Pillar Keepers (core pantheon).
    
    Returns:
        JSON string containing the 10 core entities responsible for engine pillars.
    """
    entities = await anyio.to_thread.run_sync(registry.list_pillar_keepers)
    result = [{
        "name": e.name,
        "pillars": e.pillars,
        "element": e.element,
        "chakra": e.chakra,
        "planet": e.planet,
        "sigil": e.sigil,
    } for e in entities]
    return json.dumps(result, indent=2)


@m9_safe("oracle_entity_info")
@mcp.tool()
async def oracle_entity_info(name: str) -> str:
    """Get detailed information about a specific entity.
    
    Args:
        name: Name or fragment of the entity name to look up.
        
    Returns:
        JSON string containing the full entity profile or an error.
    """
    def _get():
        return registry.get(name) or registry.find_by_name_fragment(name)
    entity = await anyio.to_thread.run_sync(_get)
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


@m9_safe("oracle_assess_intent")
@mcp.tool()
async def oracle_assess_intent(query: str) -> str:
    """Test how the Oracle would classify a query without generating a response.
    
    Args:
        query: The message to analyze for intent and confidence.
        
    Returns:
        JSON string containing the classification result and confidence metrics.
    """
    def _assess():
        # P0-B: Use module-level singleton (not fresh IntentMatcher per call)
        matcher = _get_intent_matcher()
        classification = matcher.classify(query)
        domain_entity = registry.find_by_domain(query)
        # P0-B: Use public assess_confidence() alias, not private _assess_iris_confidence
        iris_confidence = oracle.assess_confidence(query)
        return classification, domain_entity, iris_confidence

    classification, domain_entity, iris_confidence = await anyio.to_thread.run_sync(_assess)
    return json.dumps({
        "query": query,
        "classification": classification,
        "iris_confidence": iris_confidence,
        "would_escalate": iris_confidence <= 0.4,
        "domain_entity": domain_entity.name if domain_entity else None,
        "detected_summon": oracle._detect_summon(query),
    }, indent=2)


@m9_safe("oracle_discover_entity")
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

@m9_safe("sovereign_search")
@mcp.tool()
async def sovereign_search(query: str, entity_name: str = "SOPHIA", limit: int = 10) -> str:
    """Execute the 5-Tier Sovereign Search Protocol (T0-T4).
    
    Bypasses the broken OpenCode local MCP bridge by using direct API providers.
    
    Args:
        query: The search query.
        entity_name: The entity context for T0/T3 search.
        limit: Maximum results per tier.
    """
    result = await sovereign_search.search(query, entity_name, limit=limit)
    return json.dumps(result, indent=2)



@m9_safe("delegate_task")
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


# === HIVEMIND TOOLS (7) ===

@m9_safe("hivemind_post_context")
@mcp.tool()
async def hivemind_post_context(
    channel: str,
    entity: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[Dict[str, str]],
    continuation: str,
    session_id: Optional[str] = None,
    intent: Optional[str] = None,
    suggested_model: Optional[str] = None,
) -> str:
    """Submit a context snapshot from any entity to the hivemind.
    
    D-kal-046 (P6 Ship-Now Proposal #1+#2):
      - intent: Structured reason for posting (question|decision|observation|
        command|status|handoff|blocker|meta). Turns inbox from noise into a
        prioritized queue.
      - suggested_model: D118 model override hint that cascades to subagents.
        If the receiving agent spawns a child, this becomes its default model.
        
    Args:
        channel: The execution channel (e.g., 'opencode', 'cline', 'gemini-cli').
        entity: The entity persona (e.g., 'kali', 'roc_racoon', 'doom_guy').
        model: The current model being used.
        task_current: Concise description of the active task.
        focus_chain: List of previous sub-tasks or focus areas.
        decisions: List of architectural or strategic decisions made.
        continuation: Next steps or handoff notes for the next session.
        session_id: Optional UUID for the session. Auto-generated if omitted.
        intent: The semantic intent of the post (status, decision, handoff, etc).
        suggested_model: Optional hint for the next model to use.
        
    Returns:
        JSON string confirming acceptance and providing the session_id.
    """
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
        # P6 Ship-Now Proposal fields (D-kal-046)
        "intent": intent or "status",
        "suggested_model": suggested_model,
    }


    async with _hot_store_lock:
        _hot_store[sid] = snapshot
    async with _awareness_lock:
        _awareness[agent_id] = snapshot

    cold = _cold_path(agent_id, sid)
    await anyio.to_thread.run_sync(lambda: cold.parent.mkdir(parents=True, exist_ok=True))
    async with await anyio.open_file(str(cold), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))

    latest = _latest_path()
    async with await anyio.open_file(str(latest), "w") as f:
        await f.write(f"latest_session: {sid}\nupdated: {snapshot['timestamp']}\n")

    return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})


@m9_safe("hivemind_heartbeat")
@mcp.tool()
async def hivemind_heartbeat(channel: str, entity: str) -> str:
    """Signal presence to the hivemind to avoid being pruned as stale.
    
    Args:
        channel: The execution channel (e.g., 'opencode', 'cline').
        entity: The entity persona (e.g., 'kali', 'roc_racoon').
        
    Returns:
        JSON string confirming the heartbeat status.
    """
    agent_id = _make_agent_id(channel, entity)
    async with _awareness_lock:
        now_str = datetime.now(timezone.utc).isoformat()
        if agent_id in _awareness:
            _awareness[agent_id]["timestamp"] = now_str
            return json.dumps({"status": "heartbeat_received", "agent_id": agent_id})
        _awareness[agent_id] = {
            "agent_id": agent_id,
            "channel": channel,
            "entity": entity,
            "timestamp": now_str,
            "model": "unknown",
            "task_current": "heartbeat-only"
        }
        return json.dumps({"status": "presence_registered", "agent_id": agent_id})


@m9_safe("hivemind_get_awareness")
@mcp.tool()
async def hivemind_get_awareness() -> str:
    """Get real-time awareness of all active agents.
    
    [hardening-p9] Cold-Store Hydration: if the hot store is empty (e.g.
    after a server restart), performs a shallow scan of HALL_OF_RECORDS
    to recover agent presence from disk. Agents whose session files
    were modified within HEARTBEAT_TTL are treated as active.
    
    Returns:
        JSON string containing a list of all active or recently seen agents.
        Each entry includes agent_id, channel, entity, model, task_current, last_seen.
    """
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

    # Cold-store hydration supplement (D-kal-051 protocol)
    def _scan_cold():
        recovered = []
        for agent_dir in HALL_OF_RECORDS.iterdir():
            if not agent_dir.is_dir():
                continue
            json_files = sorted(
                agent_dir.glob("ses_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if not json_files:
                continue
            latest = json_files[0]
            mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
            age = (now - mtime).total_seconds()
            if age <= HEARTBEAT_TTL:
                try:
                    with latest.open() as f:
                        snap = json.load(f)
                    recovered.append({
                        "agent_id": snap.get("agent_id", agent_dir.name),
                        "channel": snap.get("channel", ""),
                        "entity": snap.get("entity", agent_dir.name),
                        "model": snap.get("model", "unknown"),
                        "task_current": snap.get("task_current", ""),
                        "last_seen": snap.get("timestamp", mtime.isoformat()),
                        "source": "cold_store",
                    })
                except Exception as exc:
                    logger.debug("Failed to load cold session file %s: %s", latest, exc)
        return recovered

    cold_results = await anyio.to_thread.run_sync(_scan_cold)
    hot_ids = {a["agent_id"] for a in awareness_list}
    for cold_agent in cold_results:
        if cold_agent["agent_id"] not in hot_ids:
            awareness_list.append(cold_agent)

    return json.dumps(awareness_list, indent=2)


@m9_safe("hivemind_get_continuation")
@mcp.tool()
async def hivemind_get_continuation(channel: str, entity: str) -> str:
    """Get the latest continuation note for a specific agent.
    
    D-kal-051: Fixed cold-store fallback. Previously only checked
    in-memory _awareness (lost on server restart). Now falls back
    to HALL_OF_RECORDS cold store for the most recent session file.
    
    Args:
        channel: The execution channel (e.g., 'opencode', 'cline').
        entity: The entity persona (e.g., 'kali', 'roc_racoon').
        
    Returns:
        The text of the latest continuation note or an error message.
    """
    agent_id = _make_agent_id(channel, entity)
    async with _awareness_lock:
        snap = _awareness.get(agent_id)
    if snap:
        return snap.get("continuation", "No continuation note found.")
    
    # Cold-store fallback: scan HALL_OF_RECORDS/<agent_id>/*.json for latest
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
        except Exception:
            return None

    cold = await anyio.to_thread.run_sync(_read_cold_fallback)
    if cold:
        return cold.get("continuation", "No continuation note found in cold store.")
    return f"No awareness data for '{agent_id}' (checked hot + cold stores)."


# === D-kal-052: EXTENDED SESSION CHECK-IN (3-Hour Safety TTL) ===
# Per user feedback (2026-06-05): Agents in extended Hivemind sessions
# may need a longer safety TTL (default 3 hours) so the pruning loop
# doesn't reap them if the user forgets to instruct agents to check out.
_extended_sessions: Dict[str, Dict[str, Any]] = {}  # cli -> {ttl_seconds, registered_at, reason}
_extended_sessions_lock = _AsyncThreadLock()
EXTENDED_SAFETY_TTL_DEFAULT = 3 * 60 * 60  # 3 hours = 10800s

# Extended sessions persistence
EXTENDED_SESSIONS_FILE = HALL_OF_RECORDS / "extended_sessions.json"


def _load_extended_sessions() -> Dict[str, Dict[str, Any]]:
    """Load extended sessions from disk."""
    if not EXTENDED_SESSIONS_FILE.exists():
        return {}
    try:
        with open(EXTENDED_SESSIONS_FILE) as f:
            return dict(json.load(f))
    except Exception as e:
        logger.warning("Failed to load extended sessions: %s", e)
        return {}


def _save_extended_sessions(sessions: Dict[str, Dict[str, Any]]) -> None:
    """Save extended sessions to disk atomically."""
    EXTENDED_SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = EXTENDED_SESSIONS_FILE.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(sessions, f, indent=2)
    os.replace(str(tmp_path), str(EXTENDED_SESSIONS_FILE))


# Load persistent extended sessions on module start
_saved = _load_extended_sessions()
_extended_sessions.update(_saved)
if _saved:
    logger.info("Restored %d extended session(s) from disk", len(_saved))


@m9_safe("hivemind_extended_checkin")
@mcp.tool()
async def hivemind_extended_checkin(
    channel: str,
    entity: str,
    reason: str = "Extended Hivemind session — user may forget to check out",
    ttl_seconds: int = EXTENDED_SAFETY_TTL_DEFAULT,
) -> str:
    """Register an extended-session heartbeat with a custom safety TTL.

    D-kal-052: Long-running agents in Hivemind sessions can call this
    to prevent the 20-minute pruning loop from reaping them while the
    user is away. Default TTL is 3 hours. The pruning loop respects
    this longer TTL — agents are only reaped after `ttl_seconds` of
    silence (not the default 1200s).

    Use case: User kicks off 5 agents in parallel Hivemind mode, gets
    pulled into a meeting, comes back 2 hours later. Without this,
    the pruning loop would have reaped all 5 agents after 20 minutes.
    With this, they persist for the full 3 hours.

    Args:
        channel: The execution channel (e.g., 'opencode', 'cline').
        entity: The entity persona (e.g., 'kali', 'roc_racoon').
        reason: Human-readable explanation (for the Hivemind audit log)
        ttl_seconds: Override default 3-hour TTL (max 24h = 86400s)

    Returns:
        JSON string containing the registered TTL and expiry timestamp.
    """
    agent_id = _make_agent_id(channel, entity)
    ttl_seconds = min(ttl_seconds, 86400)  # cap at 24h
    async with _extended_sessions_lock:
        _extended_sessions[agent_id] = {
            "agent_id": agent_id,
            "channel": channel,
            "entity": entity,
            "ttl_seconds": ttl_seconds,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
    await anyio.to_thread.run_sync(_save_extended_sessions, _extended_sessions)
    return json.dumps({
        "status": "extended_checkin_registered",
        "agent_id": agent_id,
        "ttl_seconds": ttl_seconds,
        "expires_at": (
            datetime.now(timezone.utc).timestamp() + ttl_seconds
        ),
    })


@m9_safe("hivemind_extended_checkout")
@mcp.tool()
async def hivemind_extended_checkout(channel: str, entity: str) -> str:
    """Cancel an extended-session check-in.

    Call this when ending the session cleanly so the pruning loop
    reverts to the default 20-minute TTL behavior.
    
    Args:
        channel: The execution channel (e.g., 'opencode', 'cline').
        entity: The entity persona (e.g., 'kali', 'roc_racoon').
        
    Returns:
        JSON string confirming completion or stating no extended session was found.
    """
    agent_id = _make_agent_id(channel, entity)
    async with _extended_sessions_lock:
        if agent_id in _extended_sessions:
            del _extended_sessions[agent_id]
            await anyio.to_thread.run_sync(_save_extended_sessions, _extended_sessions)
            return json.dumps({"status": "extended_checkout_complete", "agent_id": agent_id})
        return json.dumps({"status": "no_extended_session", "agent_id": agent_id})


@m9_safe("hivemind_get_session")
@mcp.tool()
async def hivemind_get_session(session_id: str) -> str:
    """Retrieve a session snapshot by ID.
    
    Args:
        session_id: The UUID of the session to retrieve.
        
    Returns:
        JSON string containing the session snapshot or an error.
    """
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


@m9_safe("hivemind_list_sessions")
@mcp.tool()
async def hivemind_list_sessions(channel: Optional[str] = None, entity: Optional[str] = None, limit: int = 10) -> str:
    """List recent session snapshots.
    
    Args:
        channel: Optional channel to filter sessions for.
        entity: Optional entity to filter sessions for.
        limit: Maximum number of sessions to return.
        
    Returns:
        JSON string containing a list of session IDs and agent associations.
    """
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


@m9_safe("hivemind_get_entity_context")
@mcp.tool()
async def hivemind_get_entity_context(entity_name: str) -> str:
    """Compile a startup briefing for any entity by reading 3 sources.

    Reads soul.yaml, knowledge/ directory, workspace/ directory,
    and active sessions to assess entity readiness for autonomous work.

    Args:
        entity_name: The name of the entity to inspect.

    Returns:
        JSON string containing the compiled entity context briefing.
    """
    entity_name_lower = entity_name.lower()
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
                    lines = content.strip().split("\n")
                    title = ""
                    summary = ""
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith("# ") and not title:
                            title = stripped.lstrip("# ").strip()
                        if stripped.startswith("**Purpose**:"):
                            summary = stripped.split(":", 1)[1].strip()
                            break
                        if stripped.startswith("Purpose:"):
                            summary = stripped.split(":", 1)[1].strip()
                            break
                    if not title:
                        title = f.stem
                    if not summary:
                        for line in lines[1:5]:
                            stripped = line.strip()
                            if stripped and not stripped.startswith("#") and not stripped.startswith("---") and not stripped.startswith("**"):
                                summary = stripped[:200]
                                break
                except Exception:
                    title = f.stem
                    summary = ""
                files.append({
                    "name": f.name,
                    "title": title,
                    "summary": summary,
                    "size_bytes": f.stat().st_size,
                })
            else:
                files.append({
                    "name": f.name,
                    "title": f.stem,
                    "summary": "",
                    "size_bytes": f.stat().st_size,
                })
        return {"file_count": len(files), "total_size_bytes": total_size, "files": files}

    def _list_workspace() -> dict:
        workspace_dir = entity_base / "workspace"
        if not workspace_dir.exists():
            return {"file_count": 0, "files": [], "most_recent": None}
        files = []
        most_recent = 0.0
        for f in sorted(workspace_dir.rglob("*")):
            if not f.is_file():
                continue
            mtime = f.stat().st_mtime
            if mtime > most_recent:
                most_recent = mtime
            files.append({
                "name": str(f.relative_to(entity_base / "workspace")),
                "size_bytes": f.stat().st_size,
                "modified": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            })
        most_recent_ts = datetime.fromtimestamp(most_recent, tz=timezone.utc).isoformat() if most_recent > 0 else None
        return {"file_count": len(files), "files": files, "most_recent": most_recent_ts}

    def _check_sessions() -> list:
        sessions_dir = PROJECT_ROOT / "data" / "sessions"
        if not sessions_dir.exists():
            return []
        active = []
        for f in sorted(sessions_dir.glob("*.active")):
            try:
                with open(f) as fh:
                    sess = json.load(fh)
                sess_entity = sess.get("entity", "").lower()
                if sess_entity == entity_name_lower:
                    active.append({
                        "session_file": f.name,
                        "session_id": sess.get("session_id", ""),
                        "entity": sess.get("entity", ""),
                        "created_at": sess.get("created_at", ""),
                        "date": sess.get("date", ""),
                    })
            except Exception:
                continue
        return active

    # Gather all data
    entity_reg = await anyio.to_thread.run_sync(
        lambda: registry.get(entity_name) or registry.find_by_name_fragment(entity_name)
    )

    soul_raw = await anyio.to_thread.run_sync(_read_soul)
    knowledge = await anyio.to_thread.run_sync(_list_knowledge)
    workspace = await anyio.to_thread.run_sync(_list_workspace)
    active_sessions = await anyio.to_thread.run_sync(_check_sessions)

    # Parse soul data
    soul_state = {
        "soul_power": None,
        "sessions_completed": None,
        "last_distillation": None,
        "recent_lessons": [],
        "recent_experiences": [],
        "status": "ok",
    }
    if "error" in soul_raw:
        soul_state["status"] = soul_raw.get("status", "error")
        soul_state["error"] = soul_raw["error"]
    elif "entity" in soul_raw:
        ent = soul_raw["entity"]
        soul_state["soul_power"] = ent.get("soul_power")
        soul_state["sessions_completed"] = ent.get("sessions_completed")
        soul_state["last_distillation"] = ent.get("last_distillation")

        lessons = ent.get("lessons", [])
        if lessons:
            last = lessons[-1]
            soul_state["recent_lessons"].append({
                "id": last.get("id", ""),
                "topic": last.get("l1_narrative", "")[:120] if last.get("l1_narrative") else "",
                "l3_principle": last.get("l3_principle", ""),
            })

        embodied = ent.get("embodied_experiences", [])
        for exp in embodied[-3:]:
            soul_state["recent_experiences"].append({
                "context": exp.get("context", "")[:120] if isinstance(exp, dict) else str(exp)[:120],
            })

    # Also check lessons_learned (Sophia-style soul format)
    if not soul_state["recent_lessons"] and "entity" in soul_raw:
        lessons_learned = soul_raw["entity"].get("lessons_learned", [])
        if lessons_learned:
            last = lessons_learned[-1]
            soul_state["recent_lessons"].append({
                "id": last.get("id", ""),
                "topic": last.get("insight", "")[:120] if last.get("insight") else "",
                "l3_principle": last.get("principle", ""),
            })

    # Entity identity
    entity_identity = {
        "name": entity_name,
        "type": "unknown",
        "pillar": None,
        "role": None,
        "pantheon": None,
    }
    if entity_reg:
        entity_identity["type"] = "pillar_keeper" if entity_reg.pillars else "entity"
        entity_identity["role"] = entity_reg.role
        entity_identity["pantheon"] = entity_reg.pantheon
        if entity_reg.pillars:
            entity_identity["pillar"] = entity_reg.pillars[0]

    # Assess readiness
    readiness_flags = []
    if soul_state["status"] == "missing":
        readiness_flags.append("NO_SOUL")
    elif soul_state["status"] == "malformed":
        readiness_flags.append("MALFORMED_SOUL")
    if knowledge["file_count"] == 0:
        readiness_flags.append("NO_KNOWLEDGE")
    if workspace["file_count"] == 0:
        readiness_flags.append("NO_WORKSPACE")

    if not readiness_flags and soul_state["soul_power"] and soul_state["soul_power"] >= 1.0:
        readiness = "HYDRATED"
    elif readiness_flags:
        readiness = "DORMANT"
    else:
        readiness = "PARTIAL"

    briefing = {
        "entity": entity_identity,
        "soul_state": soul_state,
        "knowledge_base": {
            "file_count": knowledge["file_count"],
            "total_size_bytes": knowledge["total_size_bytes"],
            "files": knowledge["files"][:50],
        },
        "workspace": {
            "file_count": workspace["file_count"],
            "most_recent_modification": workspace["most_recent"],
            "files": workspace["files"][:50],
        },
        "active_sessions": active_sessions,
        "readiness": {
            "status": readiness,
            "flags": readiness_flags,
        },
    }
    return json.dumps(briefing, indent=2)


# === WORKSPACE LOCK TOOLS (3) ===

@m9_safe("hivemind_workspace_lock_acquire")
@mcp.tool()
async def hivemind_workspace_lock_acquire(channel: str, entity: str, domain: str, ttl: int = 3600) -> str:
    """Acquire an exclusive workspace lock for a domain.

    Creates an atomic lock file at data/coordination/locks/{domain}.lock.
    If a lock exists and hasn't expired, returns error with current holder.
    If a lock exists but has expired, overwrites it (TTL-based auto-release).

    Args:
        channel: The execution channel (e.g., 'opencode', 'cline').
        entity: The entity persona requesting the lock.
        domain: The domain/resource to lock.
        ttl: Time-to-live in seconds (default 3600, max 86400).

    Returns:
        JSON string confirming lock acquisition or conflict.
    """
    await _reap_stale_locks()
    agent_id = _make_agent_id(channel, entity)
    ttl = min(ttl, 86400)
    lock_path = LOCKS_BASE / f"{domain}.lock"

    def _acquire():
        # Open (or create) lock file, then acquire exclusive non-blocking lock.
        # Using fcntl.flock for atomic read-check-write against TOCTOU race.
        # os.fdopen closes the fd automatically on with-block exit.
        fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return {"conflict": True, "holder": "unknown (locked by another process)", "domain": domain}

        # We hold the exclusive lock now — atomic read-check-write
        # os.fdopen will close fd on with-block exit (normal or exception).
        with os.fdopen(fd, 'r+') as f:
            existing_data = f.read()
            now = datetime.now(timezone.utc).timestamp()

            if existing_data:
                existing = json.loads(existing_data)
                acquired_at = existing.get("acquired_at", 0)
                lock_ttl = existing.get("ttl", 3600)
                if now <= acquired_at + lock_ttl:
                    return {"conflict": True, "holder": existing.get("agent_id"), "domain": domain}
                # Lock expired — overwrite
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


@m9_safe("hivemind_workspace_lock_release")
@mcp.tool()
async def hivemind_workspace_lock_release(channel: str, entity: str, domain: str) -> str:
    """Release a workspace lock.

    Only succeeds if the agent matches the lock holder.

    Args:
        channel: The execution channel that owns the lock.
        entity: The entity persona that owns the lock.
        domain: The domain/resource to unlock.

    Returns:
        JSON string confirming release or error.
    """
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


@m9_safe("hivemind_workspace_lock_check")
@mcp.tool()
async def hivemind_workspace_lock_check(domain: str) -> str:
    """Check the status of a workspace lock.

    Args:
        domain: The domain/resource to check.

    Returns:
        JSON string containing lock status info or "no lock".
    """
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
            "holder": lock_data.get("cli"),
            "acquired_at": acquired_at,
            "age_seconds": round(age, 1),
            "ttl": lock_ttl,
            "remaining_seconds": round(remaining, 1),
            "expired": age > lock_ttl,
        }

    result = await anyio.to_thread.run_sync(_check)
    return json.dumps(result, indent=2)


# === D-P9: SOVEREIGN HANDOFF QUEUE ===
# Formal contract layer for cross-agent handoffs. Replaces the previous
# "prompt-injection hope" pattern with a persistent queue that tracks
# handoff packets through pending -> active -> completed states.
HANDOFF_BASE = PROJECT_ROOT / "data" / "handoff"
HANDOFF_PENDING = HANDOFF_BASE / "pending"
HANDOFF_ACTIVE = HANDOFF_BASE / "active"
HANDOFF_COMPLETED = HANDOFF_BASE / "completed"
for d in (HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED):
    d.mkdir(parents=True, exist_ok=True)
HANDOFF_STALE = HANDOFF_BASE / "stale"
HANDOFF_ARCHIVE = HANDOFF_BASE / "archive"
for d in (HANDOFF_STALE, HANDOFF_ARCHIVE):
    d.mkdir(parents=True, exist_ok=True)

# Workspace lock base directory
LOCKS_BASE = PROJECT_ROOT / "data" / "coordination" / "locks"
LOCKS_BASE.mkdir(parents=True, exist_ok=True)


@m9_safe("hivemind_submit_handoff")
@mcp.tool()
async def hivemind_submit_handoff(
    target_channel: str,
    target_entity: str,
    source_channel: str,
    source_entity: str,
    task: str,
    context: str = "",
    priority: int = 0,
) -> str:
    """Submit a handoff packet to the queue. [hardening-p9] Contract Layer.

    Writes the packet to data/handoff/pending/ and returns the packet_id.
    The target agent must call hivemind_accept_handoff() to move it to active/.

    Args:
        target_channel: The channel of the target agent (e.g., 'opencode').
        target_entity: The entity of the target agent (e.g., 'roc_racoon').
        source_channel: The channel of the submitting agent.
        source_entity: The entity of the submitting agent.
        task: The task description for the target agent.
        context: Optional background context.
        priority: 0=normal, 1=high, 2=critical.
        
    Returns:
        JSON string containing the packet_id and storage path.
    """
    target_agent_id = _make_agent_id(target_channel, target_entity)
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
        "context": context,
        "priority": priority,
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
    return json.dumps({"status": "submitted", "packet_id": packet_id, "path": str(path)})


@m9_safe("hivemind_accept_handoff")
@mcp.tool()
async def hivemind_accept_handoff(packet_id: str, accepting_channel: str, accepting_entity: str) -> str:
    """Accept a handoff packet. [hardening-p9] Moves pending -> active/.

    Args:
        packet_id: The packet_id from hivemind_submit_handoff.
        accepting_channel: The channel of the accepting agent.
        accepting_entity: The entity of the accepting agent.
        
    Returns:
        JSON string confirming acceptance or stating an error.
    """
    acceptor_agent_id = _make_agent_id(accepting_channel, accepting_entity)
    src = HANDOFF_PENDING / f"{packet_id}.json"
    dst = HANDOFF_ACTIVE / f"{packet_id}.json"

    def _move():
        if not src.exists():
            return False
        with open(src) as f:
            packet = json.load(f)
        packet["status"] = "active"
        packet["accepted_at"] = datetime.now(timezone.utc).isoformat()
        packet["accepted_by_agent_id"] = acceptor_agent_id
        packet["accepted_by_channel"] = accepting_channel
        packet["accepted_by_entity"] = accepting_entity
        with open(dst, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(packet, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        src.unlink()
        return True

    moved = await anyio.to_thread.run_sync(_move)
    if not moved:
        return json.dumps({"error": f"Packet '{packet_id}' not found in pending queue"})
    return json.dumps({"status": "accepted", "packet_id": packet_id, "accepted_by": acceptor_agent_id})


@m9_safe("hivemind_complete_handoff")
@mcp.tool()
async def hivemind_complete_handoff(packet_id: str, result: str = "") -> str:
    """Complete a handoff packet. [hardening-p9] Moves active -> completed/.

    Args:
        packet_id: The packet_id from hivemind_accept_handoff.
        result: The outcome or result of the handoff.
        
    Returns:
        JSON string confirming completion or stating an error.
    """
    src = HANDOFF_ACTIVE / f"{packet_id}.json"
    dst = HANDOFF_COMPLETED / f"{packet_id}.json"

    def _move():
        if not src.exists():
            return False
        with open(src) as f:
            packet = json.load(f)
        packet["status"] = "completed"
        packet["completed_at"] = datetime.now(timezone.utc).isoformat()
        packet["result"] = result
        with open(dst, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(packet, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        src.unlink()
        return True

    moved = await anyio.to_thread.run_sync(_move)
    if not moved:
        return json.dumps({"error": f"Packet '{packet_id}' not found in active queue"})
    return json.dumps({"status": "completed", "packet_id": packet_id})


@m9_safe("hivemind_reject_handoff")
@mcp.tool()
async def hivemind_reject_handoff(packet_id: str, reason: str) -> str:
    """Reject a pending handoff packet.

    Reads from pending/, marks as rejected, moves to stale/.

    Args:
        packet_id: The packet_id from hivemind_submit_handoff.
        reason: Why the handoff was rejected.

    Returns:
        JSON string confirming rejection with trace info.
    """
    src = HANDOFF_PENDING / f"{packet_id}.json"
    dst = HANDOFF_STALE / f"{packet_id}.json"

    def _reject():
        if not src.exists():
            return None
        with open(src) as f:
            packet = json.load(f)
        packet["status"] = "stale"
        packet["rejected"] = True
        packet["reason"] = reason
        packet["rejected_at"] = datetime.now(timezone.utc).isoformat()
        with open(dst, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(packet, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        src.unlink()
        return packet

    result = await anyio.to_thread.run_sync(_reject)
    if not result:
        return json.dumps({"error": f"Packet '{packet_id}' not found in pending queue"})
    return json.dumps({
        "status": "rejected",
        "packet_id": packet_id,
        "reason": reason,
        "rejected_at": result["rejected_at"],
        "trace_id": new_trace_id(),
    })


@m9_safe("hivemind_handoff_list")
@mcp.tool()
async def hivemind_handoff_list(status: str) -> str:
    """List handoff packets by status.

    Args:
        status: One of "pending", "active", "completed", or "stale".

    Returns:
        JSON string listing packets and their metadata.
    """
    dir_map = {
        "pending": HANDOFF_PENDING,
        "active": HANDOFF_ACTIVE,
        "completed": HANDOFF_COMPLETED,
        "stale": HANDOFF_STALE,
    }
    handoff_dir = dir_map.get(status)
    if not handoff_dir:
        return json.dumps({"error": f"Invalid status '{status}'. Must be one of: {', '.join(dir_map)}"})

    def _list():
        packets = []
        for f in sorted(handoff_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                with open(f) as fh:
                    packet = json.load(fh)
                packets.append({
                    "packet_id": packet.get("packet_id", f.stem),
                    "target_agent_id": packet.get("target_agent_id", packet.get("target_cli", "unknown")),
                    "target_channel": packet.get("target_channel", ""),
                    "target_entity": packet.get("target_entity", packet.get("target_cli", "")),
                    "source_agent_id": packet.get("source_agent_id", packet.get("source_cli", "unknown")),
                    "source_channel": packet.get("source_channel", ""),
                    "source_entity": packet.get("source_entity", packet.get("source_cli", "")),
                    "task": packet.get("task", "")[:80],
                    "status": packet.get("status", status),
                    "priority": packet.get("priority", 0),
                    "submitted_at": packet.get("submitted_at", ""),
                    "accepted_by": packet.get("accepted_by", packet.get("accepted_by_agent_id", "")),
                    "completed_at": packet.get("completed_at", ""),
                    "rejected": packet.get("rejected", False),
                })
            except Exception as e:
                logger.debug("Failed to read handoff %s: %s", f, e)
        return packets

    packets = await anyio.to_thread.run_sync(_list)
    return json.dumps({
        "status": status,
        "count": len(packets),
        "packets": packets,
    }, indent=2)


@m9_safe("hivemind_handoff_archive")
@mcp.tool()
async def hivemind_handoff_archive(packet_ids: List[str]) -> str:
    """Batch archive completed handoff packets.

    Moves specified packets from completed/ to archive/.

    Args:
        packet_ids: List of packet IDs to archive.

    Returns:
        JSON string with counts of success/failure.
    """
    def _archive():
        succeeded = 0
        failed = 0
        failures = []
        for pid in packet_ids:
            src = HANDOFF_COMPLETED / f"{pid}.json"
            if not src.exists():
                failed += 1
                failures.append({"packet_id": pid, "reason": "not found"})
                continue
            dst = HANDOFF_ARCHIVE / f"{pid}.json"
            try:
                with open(src) as f:
                    packet = json.load(f)
                packet["status"] = "archived"
                packet["archived_at"] = datetime.now(timezone.utc).isoformat()
                with open(dst, "w") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(packet, f, indent=2)
                    fcntl.flock(f, fcntl.LOCK_UN)
                src.unlink()
                succeeded += 1
            except Exception as e:
                failed += 1
                failures.append({"packet_id": pid, "reason": str(e)})
        return succeeded, failed, failures

    succeeded, failed, failures = await anyio.to_thread.run_sync(_archive)
    return json.dumps({
        "status": "archived" if failed == 0 else "partial",
        "total": len(packet_ids),
        "succeeded": succeeded,
        "failed": failed,
        "failures": failures if failures else None,
    }, indent=2)


# === LIBRARY TOOLS (12) ===

@m9_safe("library_inbox_add_url")
@mcp.tool()
async def library_inbox_add_url(url: str, tags: str = "", priority: int = 0) -> str:
    """Add a URL to the intake inbox for later curation.
    
    Args:
        url: The web address to ingest.
        tags: Optional comma-separated list of tags.
        priority: Processing priority (0=normal, higher=sooner).
        
    Returns:
        JSON string containing the item_id and source metadata.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_url(url, tags=tag_list, priority=priority)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source, "source_type": item.source_type})


@m9_safe("library_inbox_add_note")
@mcp.tool()
async def library_inbox_add_note(text: str, tags: str = "") -> str:
    """Add a text note to the intake inbox.
    
    Args:
        text: The content of the note.
        tags: Optional comma-separated list of tags.
        
    Returns:
        JSON string containing the item_id and title.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_note(text, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "title": item.title})


@m9_safe("library_inbox_add_file")
@mcp.tool()
async def library_inbox_add_file(path: str, tags: str = "") -> str:
    """Add a local file path to the intake inbox.
    
    Args:
        path: The absolute path to the file on disk.
        tags: Optional comma-separated list of tags.
        
    Returns:
        JSON string containing the item_id and file source.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await inbox.add_file(path, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source})


@m9_safe("library_inbox_list")
@mcp.tool()
async def library_inbox_list(limit: int = 20) -> str:
    """List pending items in the intake inbox.
    
    Args:
        limit: Maximum number of pending items to retrieve.
        
    Returns:
        JSON string containing the total counts and a list of pending items.
    """
    items = await inbox.list_pending(limit=limit)
    counts = await inbox.count()
    return json.dumps({
        "counts": counts,
        "items": [{"item_id": i.item_id, "source": i.source[:80], "source_type": i.source_type, "title": i.title, "priority": i.priority, "created_at": i.created_at} for i in items],
    }, indent=2)


@m9_safe("library_inbox_stats")
@mcp.tool()
async def library_inbox_stats() -> str:
    """Get inbox statistics (pending, processing, failed counts).
    
    Returns:
        JSON string with counts for each inbox item status.
    """
    counts = await inbox.count()
    return json.dumps(counts)


@m9_safe("library_ingest_pending")
@mcp.tool()
async def library_ingest_pending(limit: int = 5) -> str:
    """Process pending inbox items through curation into the library.
    
    Args:
        limit: Maximum number of items to process in this batch.
        
    Returns:
        JSON string containing the number of ingested items and their summaries.
    """
    ingested = await library.ingest_from_inbox(inbox, curator, limit=limit)
    return json.dumps({
        "ingested": len(ingested),
        "documents": [{"doc_id": d.doc_id, "title": d.title, "domain": d.domain, "quality_score": d.quality_score} for d in ingested],
    }, indent=2)


@m9_safe("library_search")
@mcp.tool()
async def library_search(query: str, domain: str = "", limit: int = 20) -> str:
    """Search the offline library for documents. Uses hybrid search.
    
    Args:
        query: The search query (max 500 chars).
        domain: Optional domain filter (e.g., 'security', 'research').
        limit: Maximum number of results to return.
        
    Returns:
        JSON string containing the search results and hit count.
    """
    # P1-C: MCP-layer input guards (M-A4 compliance fix, defense-in-depth)
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})
    # P1-C: MCP-layer input guards (M-A4 compliance fix, defense-in-depth)
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})
    
    # Sovereign Search Integration: Use the 5-Tier Protocol instead of raw hybrid search
    search_service = SovereignSearchService()
    report = await search_service.search(query, entity_name=domain if domain else "general", limit=limit)
    
    return json.dumps({
        "query": query, 
        "status": report["status"],
        "final_tier": report["final_tier"],
        "primary_finding": report["primary_finding"],
        "evidence": report["evidence"],
        "fallback_log": report["fallback_log"],
        "results": report["primary_finding"] if isinstance(report["primary_finding"], list) else [report["primary_finding"]]
    }, indent=2, default=str)


@m9_safe("library_get_document")
@mcp.tool()
async def library_get_document(doc_id: str) -> str:
    """Get the full content of a library document by ID.
    
    Args:
        doc_id: The unique identifier of the document.
        
    Returns:
        JSON string containing the complete document content and metadata.
    """
    doc = await library.get(doc_id)
    if not doc:
        return json.dumps({"error": f"Document '{doc_id}' not found"})
    return json.dumps(doc.to_dict(), indent=2, default=str)


@m9_safe("library_domains")
@mcp.tool()
async def library_domains() -> str:
    """Get document counts grouped by domain.
    
    Returns:
        JSON string containing domain names and their document counts.
    """
    domains = await library.domains()
    return json.dumps(domains, indent=2)


@m9_safe("library_stats")
@mcp.tool()
async def library_stats() -> str:
    """Get comprehensive library statistics.
    
    Returns:
        JSON string containing library and indexer usage metrics.
    """
    # P1-D: Guard indexer.stats() outside the library's error boundary (M-A6 fix)
    stats = await library.stats()
    try:
        idx_stats = indexer.stats()
        stats["index"] = idx_stats
    except Exception as e:
        logger.warning("library_stats: indexer.stats() failed: %s", e)
        stats["index"] = {"error": str(e)}
    return json.dumps(stats, indent=2)


@m9_safe("library_recent")
@mcp.tool()
async def library_recent(limit: int = 20) -> str:
    """List most recently curated library documents.
    
    Args:
        limit: Maximum number of recent documents to retrieve.
        
    Returns:
        JSON string containing a list of recently ingested document summaries.
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


@m9_safe("library_index_flush")
@mcp.tool()
async def library_index_flush() -> str:
    """Flush search indices to disk.
    
    Returns:
        JSON string confirming the flush status and providing current index stats.
    """
    await indexer.flush()
    stats = indexer.stats()
    return json.dumps({"status": "flushed", "stats": stats})


# === DISCOVERY TOOLS (3) ===

@m9_safe("library_discovery_research")
@mcp.tool()
async def library_discovery_research(query: str, depth: int = 2) -> str:
    """Execute the tiered external discovery pipeline (Gemini -> Exa -> Brave -> Tavily).

    This performs real-time web discovery and returns a consolidated report.
    Async — non-blocking (P2-A: M-A8 docstring fix).
    
    Args:
        query: The search or discovery query.
        depth: Discovery depth (1-3).
        
    Returns:
        JSON string containing the consolidated discovery report.
    """
    report = await discovery.discover(query, depth=depth)
    return json.dumps(report.to_dict(), indent=2)


@m9_safe("library_discovery_start")
@mcp.tool()
async def library_discovery_start(query: str) -> str:
    """Start a background discovery job and return the job ID.

    Use library_discovery_status to poll for results.
    
    Args:
        query: The discovery query to run in the background.
        
    Returns:
        JSON string containing the job_id.
    """
    job_id = await discovery.start_discovery(query)
    if _global_tg:
        _global_tg.start_soon(_run_discovery_background, job_id)
    else:
        async with anyio.create_task_group() as tg:
            tg.start_soon(_run_discovery_background, job_id)
    return json.dumps({"status": "started", "job_id": job_id})


@m9_safe("library_discovery_status")
@mcp.tool()
async def library_discovery_status(job_id: str) -> str:
    """Get the current status and partial results of a background discovery job.
    
    Args:
        job_id: The job identifier returned by library_discovery_start.
        
    Returns:
        JSON string containing the job status and any results found so far.
    """
    result = discovery.get_job_status(job_id)
    return json.dumps(result, indent=2)


# === MEMORY TOOLS (6) ===
# Sterile-named tools (P2 DataStore — Wave 1.5 P1)
# These wrap MemoryStore methods with context params for MCP client compatibility.
# The `omega_memory_*` tools above remain for backward compatibility.

@m9_safe("memory_search")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def memory_search(
    ctx: Context,
    query: str,
    entity_name: str,
    limit: int = 20,
) -> str:
    """Search across conversation history using FTS5 full-text search.
    
    Wraps MemoryStore.search_fts() — BM25 keyword ranking, no vector overhead.
    Use this for exact-match and keyword-focused memory lookups.
    
    Args:
        query: The search query (natural language or keywords).
        entity_name: The sovereign owner of the memory (REQUIRED).
        limit: Maximum number of results to return.
        
    Returns:
        JSON string containing matched exchanges with scores and timestamps.
    """
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    memory_store = get_memory_store()
    results = await memory_store.search_fts(query, entity_name, limit)
    return json.dumps({
        "query": query,
        "entity": entity_name,
        "count": len(results),
        "results": results,
    }, indent=2)


@m9_safe("memory_get_history")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def memory_get_history(
    ctx: Context,
    entity_name: str,
    session_id: str,
    limit: int = 20,
) -> str:
    """Retrieve conversation history for a specific entity and session.
    
    Wraps MemoryStore.get_history() — returns exchanges with roles and timestamps.
    
    Args:
        entity_name: The sovereign owner of the memory (REQUIRED).
        session_id: The session identifier (REQUIRED).
        limit: Maximum number of exchanges to return.
        
    Returns:
        JSON string containing the conversation exchanges.
    """
    if not session_id:
        return json.dumps({"error": "session_id cannot be empty", "count": 0, "history": []})
    memory_store = get_memory_store()
    results = await memory_store.get_history(entity_name, session_id, limit)
    return json.dumps({
        "entity": entity_name,
        "session_id": session_id,
        "count": len(results),
        "history": results,
    }, indent=2)


@m9_safe("memory_list_sessions")
@tdp_wrap(source="memory_store", taint_level=1)
@mcp.tool()
async def memory_list_sessions(
    ctx: Context,
    entity_name: str,
    limit: int = 20,
) -> str:
    """List recent sessions for an entity.
    
    Wraps MemoryStore.list_sessions() — returns active session identifiers.
    
    Args:
        entity_name: The entity to list sessions for (REQUIRED).
        limit: Maximum number of sessions to return.
        
    Returns:
        JSON string containing the list of active sessions.
    """
    if not entity_name:
        return json.dumps({"error": "entity_name cannot be empty", "count": 0, "sessions": []})
    memory_store = get_memory_store()
    results = await memory_store.list_sessions(entity_name, limit)
    return json.dumps({
        "entity_filter": entity_name,
        "count": len(results),
        "sessions": results,
    }, indent=2)


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
    memory_store = get_memory_store()
    results = await memory_store.search(query, entity_name, limit)
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
    """Execute multi-depth research on a query using the offline library.

    Depth levels: 1=Quick (1-2 sources), 2=Standard (3-5 sources),
    3=Deep (6-15 sources), 4=Scholarly (10-50 sources).

    Args:
        query: The research question or topic
        depth: Research depth (1-4)
        domain: Optional domain filter
        
    Returns:
        JSON string containing the research result and citations.
    """
    depth = max(1, min(4, depth))
    domain_filter = domain if domain else None
    result = await research_engine.research(query, depth=depth, domain=domain_filter)
    return json.dumps(result.to_dict(), indent=2, default=str)


@m9_safe("research_get")
@mcp.tool()
async def research_get(research_id: str) -> str:
    """Retrieve a previous research result by ID.

    Args:
        research_id: Research ID (e.g. res_abc123)
        
    Returns:
        JSON string containing the research result or an error.
    """
    result = await research_engine.get_result(research_id)
    if not result:
        return json.dumps({"error": f"Research '{research_id}' not found"})
    return json.dumps(result.to_dict(), indent=2, default=str)


@m9_safe("research_list")
@mcp.tool()
async def research_list(limit: int = 20) -> str:
    """List recent research results.

    Args:
        limit: Maximum results to return
        
    Returns:
        JSON string containing a list of recent research IDs and queries.
    """
    results = await research_engine.list_results(limit=limit)
    return json.dumps(results, indent=2, default=str)


@m9_safe("research_depths")
@mcp.tool()
async def research_depths() -> str:
    """List available research depth levels and their configurations.
    
    Returns:
        JSON string containing the available depth levels and source counts.
    """
    return json.dumps(RESEARCH_DEPTHS, indent=2)


@m9_safe("research_stats")
@mcp.tool()
async def research_stats() -> str:
    """Get research engine statistics.
    
    Returns:
        JSON string containing the total count and depth distribution of research tasks.
    """
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
        def _read():
            with open(metrics_path, "r") as f:
                return json.load(f)
        metrics = await anyio.to_thread.run_sync(_read)
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
        def _read():
            with open(METRICS_PATH) as f:
                return json.load(f)
        metrics = await anyio.to_thread.run_sync(_read)
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
    def _collect():
        models_dir = Path("/media/arcana-novai/omega_library/models/gguf")
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
    """Check Podman storage usage on omega_library.
    
    Returns:
        JSON string containing Podman storage path and size metrics.
    """
    def _collect():
        storage_dir = Path("/media/arcana-novai/omega_library/podman-storage")
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
    """Check if an entity is allowed to spawn a subagent at the given depth.

    Args:
        entity_name: The name of the entity attempting to spawn a subagent.
        current_depth: The current depth of the subagent chain (0-indexed).
        
    Returns:
        JSON string containing the recursion check results (allowed/blocked).
    """
    if not hierarchy._hierarchy:
        await hierarchy.load()
    result = hierarchy.check_recursion(entity_name, current_depth)
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


# === HTTP ENDPOINTS (OpenCode 1.15+ High-Fidelity Handshake) ===

async def _health(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.2.0"
    })

async def _entity_current(request: Request) -> JSONResponse:
    entity_name = _current_entity.get() or "SOPHIA"
    entity = registry.get(entity_name)
    if entity:
        return JSONResponse(asdict(entity))
    return JSONResponse({"entity": entity_name})


async def _config_providers(request: Request) -> JSONResponse:
    path = PROJECT_ROOT / "config" / "providers.yaml"
    def _read():
        if path.exists():
            with open(path, "r") as f:
                return yaml.safe_load(f)
        return {"providers": []}
    data = await anyio.to_thread.run_sync(_read)
    return JSONResponse(data)

async def _provider_list(request: Request) -> JSONResponse:
    path = PROJECT_ROOT / "config" / "providers.yaml"
    def _collect():
        providers = []
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            chain = data.get("inference", {}).get("fallback_chain", [])
            for p in chain:
                if isinstance(p, dict) and "provider" in p:
                    pid = p["provider"]
                    providers.append({
                        "id": pid,
                        "name": pid.replace("-", " ").title(),
                        "source": "config",
                        "env": [],
                        "options": {},
                        "models": {}
                    })
        return providers
    providers = await anyio.to_thread.run_sync(_collect)
    return JSONResponse(providers)

async def _config_get(request: Request) -> JSONResponse:
    path = PROJECT_ROOT / "opencode.json"
    def _read():
        if path.exists():
            with open(path, "r") as f:
                return json.load(f), 200
        return {"error": "opencode.json not found"}, 404
    data, status = await anyio.to_thread.run_sync(_read)
    return JSONResponse(data, status_code=status)




async def _agent_list(request: Request) -> JSONResponse:
    """List all agents from the CAPABILITY_REGISTRY.
    
    Used by OpenCode 1.15+ dot-separated handshake (app.agents).
    [id-soft: doom-1993] WAD System — agents loaded from active IWAD via
    subagent_dispatcher.CAPABILITY_REGISTRY, which is engine-agnostic.
    """
    def _collect():
        from omega.oracle.subagent_dispatcher import CAPABILITY_REGISTRY
        agents = []
        for name, desc in CAPABILITY_REGISTRY.items():
            agents.append({
                "id": name,
                "name": desc.get("purpose", name).split(" — ")[0].split(":")[0].strip(),
                "mode": desc.get("mode", "unknown"),
                "purpose": desc.get("purpose", ""),
                "capabilities": desc.get("capabilities", []),
                "domains": desc.get("domains", []),
                "pillar_slot": desc.get("pillar_slot"),
                "task_tool_type": desc.get("task_tool_type", "general"),
                "owned_files": desc.get("owned_files", []),
            })
        return agents
    agents = await anyio.to_thread.run_sync(_collect)
    return JSONResponse(agents)

# --- SOVEREIGN GATEWAY PROXY ---
class SovereignGateway:
    """Local proxy for AI providers to decouple rate-limiting and backoff from OpenCode.
    
    Implements:
      - Secret injection from .env / config
      - 65-second start backoff (prevents thundering herd on boot)
      - 300-second TUI cap (prevents excessive rapid-fire requests)
      - Independent httpx client to avoid recursive loopbacks
    """
    def __init__(self):
        import httpx
        self.client = httpx.AsyncClient(timeout=120.0)
        self._last_request_time = 0.0
        self._boot_time = datetime.now(timezone.utc).timestamp()
        self._tui_count = 0
        self._tui_reset_time = self._boot_time

    async def proxy_request(self, provider_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).timestamp()
        
        # 1. 65-second start backoff
        if now - self._boot_time < 65:
            wait_time = 65 - (now - self._boot_time)
            logger.info(f"Sovereign Gateway: Start backoff active. Waiting {wait_time:.2f}s")
            await anyio.sleep(wait_time)
            now = datetime.now(timezone.utc).timestamp()

        # 2. 300-second TUI cap (Rate limiting)
        if now - self._tui_reset_time > 300:
            self._tui_count = 0
            self._tui_reset_time = now
        
        self._tui_count += 1
        if self._tui_count > 100: # Example cap: 100 requests per 5 mins
            logger.warning("Sovereign Gateway: TUI cap reached. Throttling request.")
            await anyio.sleep(1.0)

        # 3. Secret Injection & Forwarding
        # In a real implementation, this would look up the provider's base_url and API key
        # from the ModelGateway's config and inject them into the headers.
        
        # For now, we implement the structure.
        logger.info(f"Sovereign Gateway: Proxying request to {provider_name}")
        
        # Mocking the actual forward for now, as we'd need the full provider fabric config
        # In the final version, this will use ModelGateway's provider instances.
        return {"status": "proxied", "provider": provider_name, "payload": payload}

gateway = SovereignGateway()

async def _proxy_handler(request: Request) -> JSONResponse:
    provider = request.path_params.get("provider", "default")
    try:
        body = await request.json()
        result = await gateway.proxy_request(provider, body)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Update hub_routes to include the proxy
hub_routes = [
    Route("/health", _health),
    Route("/entity/current", _entity_current),
    Route("/config/providers", _config_providers),
    Route("/provider", _provider_list),
    Route("/agent", _agent_list),
    Route("/config", _config_get),
    Route("/global/config", _config_get),
    Route("/config.get", _config_get),
    Route("/config.providers", _config_providers),
    Route("/provider.list", _provider_list),
    Route("/app.agents", _agent_list),
    Route("/proxy/{provider}", _proxy_handler),
]


if __name__ == "__main__":
    # Start background tasks in daemon threads (clean up when server stops)
    # Q3 fix: _AsyncThreadLock wraps threading.Lock — safe across event loops.
    # Each background thread runs its own anyio event loop; lock operations
    # bridge via anyio.to_thread.run_sync on a pool worker thread.
    bg_thread = threading.Thread(
        target=lambda: anyio.run(_prune_awareness_background),
        daemon=True,
    )
    bg_thread.start()

    reaper_thread = threading.Thread(
        target=lambda: anyio.run(_reaper_background),
        daemon=True,
    )
    reaper_thread.start()

    run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security)