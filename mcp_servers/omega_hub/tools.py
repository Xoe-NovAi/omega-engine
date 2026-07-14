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
    _extended_sessions, _extended_sessions_lock, EXTENDED_SESSIONS_FILE,
    EXTENDED_SAFETY_TTL_DEFAULT,
    _get_intent_matcher,
    HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE,
    LOCKS_BASE, METRICS_PATH,
    _make_agent_id, _cold_path, _latest_path, _find_packet_path,
    # P0-2: Sharded hot store API
    hot_store_set, hot_store_get, hot_store_get_all,
    # P0-4: Cold-store awareness cache
    get_cached_cold_awareness, invalidate_awareness_cache,
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


@m9_safe("oracle_list_pillar_keepers")
@mcp.tool()
async def oracle_list_pillar_keepers() -> str:
    _require_service()
    """List entities with slot assignments (backward-compat name).
    
    The concept of "Pillar Keepers" is Arcana-NovAi WAD content. The engine
    discovers slot-holding entities dynamically. WAD-specific display fields
    are in Entity.metadata and passed through for client use.
    
    Returns:
        JSON string containing entities with slot assignments.
    """
    entities = await anyio.to_thread.run_sync((await registry).list_pillar_keepers)
    result = [{
        "name": e.name,
        "slots": e.slots,
        "metadata": e.metadata,  # WAD content: element, chakra, planet, sigil, etc.
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


@m9_safe("oracle_assess_intent")
@mcp.tool()
async def oracle_assess_intent(query: str) -> str:
    _require_service()
    """Test how the Oracle would classify a query without generating a response.
    
    Args:
        query: The message to analyze for intent and confidence.
        
    Returns:
        JSON string containing the classification result and confidence metrics.
    """
    async def _assess():
        # P0-B: Use module-level singleton (not fresh IntentMatcher per call)
        matcher = _get_intent_matcher()
        classification = matcher.classify(query)
        domain_entity = (await registry).find_by_domain(query)
        # P0-B: Use public assess_confidence() alias, not private _assess_iris_confidence
        iris_confidence = (await oracle).assess_confidence(query)
        return classification, domain_entity, iris_confidence
    
    classification, domain_entity, iris_confidence = await _assess()
    return json.dumps({
        "query": query,
        "classification": classification,
        "iris_confidence": iris_confidence,
        "would_escalate": iris_confidence <= 0.4,
        "domain_entity": domain_entity.name if domain_entity else None,
        "detected_summon": (await oracle)._detect_summon(query),
    }, indent=2)


@m9_safe("oracle_discover_entity")
@mcp.tool()
async def oracle_discover_entity(query: str) -> str:
    _require_service()
    """Find the best entity in the pantheon to handle a specific task or domain.
    
    Args:
        query: A description of the task or a domain keyword.
    """
    entity = (await registry).find_by_domain(query)
    if not entity:
        return json.dumps({"error": "No matching entity found for this domain."})
    return json.dumps({
        "entity": entity.name,
        "slots": entity.slots,
        "role": entity.role,
        "domains": entity.domains,
        "reason": f"Matched domain via query: {query}"
    }, indent=2)

@m9_safe("sovereign_search")
@mcp.tool()
async def sovereign_search(query: str, entity_name: str = "SOPHIA", limit: int = 10, force_tier: Optional[int] = None) -> str:
    _require_service()
    """Execute the 4-Tier Sovereign Search Protocol (SSP-V2).
    
    T0 (Local) -> T1 (SearXNG) -> T2 (Exa) -> T3 (Firecrawl).
    T0 includes both MemoryStore and a local filesystem cache.
    
    Args:
        query: The search query.
        entity_name: The entity context for T0 cache and routing signals.
        limit: Maximum results per tier.
        force_tier: Optional tier to force execution (0-3).
    """
    result = await (await sovereign_search_service).search(query, entity_name, limit=limit, force_tier=force_tier)
    return json.dumps(result, indent=2)

@m9_safe("search_extract")
@mcp.tool()
async def search_extract(query: str, limit: int = 10) -> str:
    _require_service()
    """Force a T3 (Firecrawl) Deep Extraction for a specific query.
    
    Bypasses the tiered routing to ensure full-page content extraction
    and structured markdown results.
    
    Args:
        query: The query to extract content for.
        limit: Number of sources to scrape.
    """
    result = await (await sovereign_search_service).extract(query, limit=limit)
    return json.dumps({"result": result, "tier": 3, "provider": "firecrawl"}, indent=2)

@m9_safe("search_status")
@mcp.tool()
async def search_status() -> str:
    _require_service()
    """Get the current health and configuration status of the Sovereign Search pipeline.
    
    Returns:
        JSON string containing tier availability, credit status, and cache metrics.
    """
    # Gather health from the gateway's health monitor
    tier_map = {0: "local", 1: "searxng", 2: "exa", 3: "firecrawl"}
    gw = await gateway
    health_monitor = gw.model_gateway._health_monitor
    health = {name: health_monitor.is_available(name) for name in tier_map.values()}
    
    service = await sovereign_search_service
    status = {
        "pipeline_version": "SSP-V2",
        "tier_health": health,
        "firecrawl_credits": (await sovereign_search_service).budget.has_quota("firecrawl", 100),
        "cache_dir": str((await sovereign_search_service).cache.cache_dir),
        "config_version": (await sovereign_search_service).config.get("version", "unknown")
    }
    return json.dumps(status, indent=2)




@m9_safe("delegate_task")
@mcp.tool()
async def delegate_task(target_entity: str, query: str, context: str = "") -> str:
    _require_service()
    """Delegate a task to another entity and receive their response.

    This allows agents to collaborate by summoning specialized keepers for sub-tasks.

    Args:
        target_entity: The name of the entity to delegate to.
        query: The specific request or question for the target entity.
        context: Optional background context or findings to pass along.
    """
    full_query = f"CONTEXT: {context}\n\nREQUEST: {query}" if context else query
    response = await (await oracle).summon(target_entity, full_query)
    return json.dumps({
        "status": "delegated",
        "target": response.entity,
        "response": response.text,
        "trace_id": response.trace_id,
        "backend": response.backend,
        "model": response.model,
    }, indent=2)


# === HIVEMIND TOOLS (7) ===

@m9_safe("hivemind_post_context")
@mcp.tool()
async def hivemind_post_context(
    channel: str,
    entity: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[str],
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
        decisions: List of architectural or strategic decisions made (strings, not dicts).
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
    # 1. Get awareness (with lock, fast)
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

    # 2. Cold-store hydration (WITHOUT lock, cached — P0-4)
    cold_results = await get_cached_cold_awareness()
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
        except Exception as e:
            logger.debug(f"Cold fallback read failed for {json_files[0].name}: {e}")
            return None

    cold = await anyio.to_thread.run_sync(_read_cold_fallback)
    if cold:
        return cold.get("continuation", "No continuation note found in cold store.")
    return f"No awareness data for '{agent_id}' (checked hot + cold stores)."



# [P1a-2] Extended sessions state is now in mcp_servers.omega_hub.state


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
    _deprecated("hivemind_get_session", "hivemind_session(action='get')")
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
    _deprecated("hivemind_list_sessions", "hivemind_session(action='list')")
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
    try:
        _require_service()
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
                    except Exception as e:
                        logger.debug(f"Knowledge file parse failed for {f.name}: {e}")
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
                except Exception as e:
                    logger.debug(f"Session file parse failed for {f.name}: {e}")
                    continue
            return active

        # Gather all data
        entity_reg = _state.registry.get(entity_name) or _state.registry.find_by_name_fragment(entity_name)

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
            entity_identity["type"] = "pillar_keeper" if entity_reg.slots else "entity"
            entity_identity["role"] = entity_reg.role
            entity_identity["pantheon"] = entity_reg.metadata.get("pantheon")
            if entity_reg.slots:
                entity_identity["pillar"] = entity_reg.slots[0]

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
    except Exception as e:
        return json.dumps({"error": str(e), "status": "failed"})


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
    _deprecated("hivemind_workspace_lock_acquire", "hivemind_workspace_lock(action='acquire')")
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
    _deprecated("hivemind_workspace_lock_release", "hivemind_workspace_lock(action='release')")
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
    _deprecated("hivemind_workspace_lock_check", "hivemind_workspace_lock(action='check')")
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


# [P1b] _find_packet_path is now in state.py — imported above


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
    _deprecated("hivemind_submit_handoff", "hivemind_handoff(action='submit')")
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
    handoff_index_add(packet_id, "pending")
    return json.dumps({"status": "submitted", "packet_id": packet_id, "path": str(path)})


@m9_safe("hivemind_accept_handoff")
@mcp.tool()
async def hivemind_accept_handoff(packet_id: str, accepting_channel: str, accepting_entity: str) -> str:
    """Accept a handoff packet. [hardening-p9] Moves -> active/.

    Args:
        packet_id: The packet_id from hivemind_submit_handoff.
        accepting_channel: The channel of the accepting agent.
        accepting_entity: The entity of the accepting agent.
        
    Returns:
        JSON string confirming acceptance or stating an error.
    """
    _deprecated("hivemind_accept_handoff", "hivemind_handoff(action='accept')")
    acceptor_agent_id = _make_agent_id(accepting_channel, accepting_entity)
    src = _find_packet_path(packet_id)
    dst = HANDOFF_ACTIVE / f"{packet_id}.json"

    if not src:
        return json.dumps({"error": f"Packet '{packet_id}' not found in any queue"})

    def _move():
        with open(src) as f:
            packet = json.load(f)
        
        # If already active and accepted by the same entity, just return success
        if src.parent == HANDOFF_ACTIVE and packet.get("accepted_by_agent_id") == acceptor_agent_id:
            return True

        packet["status"] = "active"
        packet["accepted_at"] = datetime.now(timezone.utc).isoformat()
        packet["accepted_by_agent_id"] = acceptor_agent_id
        packet["accepted_by_channel"] = accepting_channel
        packet["accepted_by_entity"] = accepting_entity
        
        with open(dst, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(packet, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
            
        if src != dst:
            src.unlink()
        return True

    await anyio.to_thread.run_sync(_move)
    handoff_index_move(packet_id, "active")
    return json.dumps({"status": "accepted", "packet_id": packet_id, "accepted_by": acceptor_agent_id})


@m9_safe("hivemind_complete_handoff")
@mcp.tool()
async def hivemind_complete_handoff(packet_id: str, result: str = "") -> str:
    """Complete a handoff packet. [hardening-p9] Moves -> completed/.

    Args:
        packet_id: The packet_id from hivemind_accept_handoff.
        result: The outcome or result of the handoff.
        
    Returns:
        JSON string confirming completion or stating an error.
    """
    _deprecated("hivemind_complete_handoff", "hivemind_handoff(action='complete')")
    src = _find_packet_path(packet_id)
    dst = HANDOFF_COMPLETED / f"{packet_id}.json"

    if not src:
        return json.dumps({"error": f"Packet '{packet_id}' not found in any queue"})

    def _move():
        with open(src) as f:
            packet = json.load(f)
            
        # If already completed, just update the result and return
        if src.parent == HANDOFF_COMPLETED:
            packet["result"] = result
            with open(src, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(packet, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
            return True

        packet["status"] = "completed"
        packet["completed_at"] = datetime.now(timezone.utc).isoformat()
        packet["result"] = result
        with open(dst, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(packet, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
            
        if src != dst:
            src.unlink()
        return True

    await anyio.to_thread.run_sync(_move)
    handoff_index_move(packet_id, "completed")
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
    _deprecated("hivemind_reject_handoff", "hivemind_handoff(action='reject')")
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
    handoff_index_move(packet_id, "stale")
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
    _deprecated("hivemind_handoff_list", "hivemind_handoff(action='list')")
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


@m9_safe("hivemind_get_handoff")
@mcp.tool()
async def hivemind_get_handoff(packet_id: str) -> str:
    """Retrieve full details for a specific handoff packet.

    Args:
        packet_id: The unique identifier for the handoff packet.

    Returns:
        JSON string containing the full packet details or an error.
    """
    _deprecated("hivemind_get_handoff", "hivemind_handoff(action='get')")
    path = _find_packet_path(packet_id)
    if not path:
        return json.dumps({"error": f"Packet '{packet_id}' not found in any queue"})

    def _read():
        with open(path) as f:
            return json.load(f)

    packet = await anyio.to_thread.run_sync(_read)
    return json.dumps(packet, indent=2)


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
    _deprecated("hivemind_handoff_archive", "hivemind_handoff(action='archive')")
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
    # Update index for successfully archived packets
    for pid in packet_ids:
        if (HANDOFF_ARCHIVE / f"{pid}.json").exists():
            handoff_index_move(pid, "archive")
    return json.dumps({
        "status": "archived" if failed == 0 else "partial",
        "total": len(packet_ids),
        "succeeded": succeeded,
        "failed": failed,
        "failures": failures if failures else None,
    }, indent=2)


# === LIBRARY TOOLS (12) ===

@m9_safe("library_inbox_add_url")
@tdp_wrap(source="library_inbox_add_url", taint_level=determine_url_taint)
@mcp.tool()
async def library_inbox_add_url(url: str, tags: str = "", priority: int = 0) -> str:
    _require_service()
    """Add a URL to the intake inbox for later curation.
    
    Args:
        url: The web address to ingest.
        tags: Optional comma-separated list of tags.
        priority: Processing priority (0=normal, higher=sooner).
        
    Returns:
        JSON string containing the item_id and source metadata.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await (await inbox).add_url(url, tags=tag_list, priority=priority)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source, "source_type": item.source_type})


@m9_safe("library_inbox_add_note")
@tdp_wrap(source="library_inbox_add_note", taint_level=1)
@mcp.tool()
async def library_inbox_add_note(text: str, tags: str = "") -> str:
    _require_service()
    """Add a text note to the intake (await inbox).
    
    Args:
        text: The content of the note.
        tags: Optional comma-separated list of tags.
        
    Returns:
        JSON string containing the item_id and title.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await (await inbox).add_note(text, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "title": item.title})


@m9_safe("library_inbox_add_file")
@tdp_wrap(source="library_inbox_add_file", taint_level=1)
@mcp.tool()
async def library_inbox_add_file(path: str, tags: str = "") -> str:
    _require_service()
    """Add a local file path to the intake (await inbox).
    
    Args:
        path: The absolute path to the file on disk.
        tags: Optional comma-separated list of tags.
        
    Returns:
        JSON string containing the item_id and file source.
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    item = await (await inbox).add_file(path, tags=tag_list)
    return json.dumps({"status": "added", "item_id": item.item_id, "source": item.source})


@m9_safe("library_inbox_list")
@mcp.tool()
async def library_inbox_list(limit: int = 20) -> str:
    _require_service()
    """List pending items in the intake (await inbox).
    
    Args:
        limit: Maximum number of pending items to retrieve.
        
    Returns:
        JSON string containing the total counts and a list of pending items.
    """
    items = await (await inbox).list_pending(limit=limit)
    counts = await (await inbox).count()
    return json.dumps({
        "counts": counts,
        "items": [{"item_id": i.item_id, "source": i.source[:80], "source_type": i.source_type, "title": i.title, "priority": i.priority, "created_at": i.created_at} for i in items],
    }, indent=2)


@m9_safe("library_inbox_stats")
@mcp.tool()
async def library_inbox_stats() -> str:
    _require_service()
    """Get inbox statistics (pending, processing, failed counts).
    
    Returns:
        JSON string with counts for each inbox item status.
    """
    counts = await (await inbox).count()
    return json.dumps(counts)


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
    # P1-C: MCP-layer input guards (M-A4 compliance fix, defense-in-depth)
    if not query.strip():
        return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
    if len(query) > 500:
        return json.dumps({"error": "Query exceeds 500-char limit", "count": 0, "results": []})
    
    # Use module-level sovereign_search_service (not a fresh instance)
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
        limit: Maximum number of results to return (default 10).
        
    Returns:
        JSON string containing search results with doc_id, title, summary, score, domain.
    """
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


@m9_safe("library_index_flush")
@mcp.tool()
async def library_index_flush() -> str:
    _require_service()
    """Flush search indices to disk.
    
    Returns:
        JSON string confirming the flush status and providing current index stats.
    """
    await (await indexer).flush()
    stats = (await indexer).stats()
    return json.dumps({"status": "flushed", "stats": stats})


# === DISCOVERY TOOLS (3) ===

@m9_safe("library_discovery_research")
@mcp.tool()
async def library_discovery_research(query: str, depth: int = 2) -> str:
    _require_service()
    """Execute the tiered external discovery pipeline.

    This performs real-time web discovery and returns a consolidated report.
    Async — non-blocking (P2-A: M-A8 docstring fix).
    
    Args:
        query: The search or discovery query.
        depth: Discovery depth (1-3).
        
    Returns:
        JSON string containing the consolidated discovery report.
    """
    report = await (await discovery).discover(query, depth=depth)
    return json.dumps(report.to_dict(), indent=2)


@m9_safe("library_discovery_start")
@mcp.tool()
async def library_discovery_start(query: str) -> str:
    _require_service()
    """Start a background discovery job and return the job ID.

    Use library_discovery_status to poll for results.
    
    Args:
        query: The discovery query to run in the background.
        
    Returns:
        JSON string containing the job_id.
    """
    job_id = await (await discovery).start_discovery(query)
    async with anyio.create_task_group() as tg:
        tg.start_soon(_run_discovery_background, job_id)
    return json.dumps({"status": "started", "job_id": job_id})


@m9_safe("library_discovery_status")
@mcp.tool()
async def library_discovery_status(job_id: str) -> str:
    _require_service()
    """Get the current status and partial results of a background discovery job.
    
    Args:
        job_id: The job identifier returned by library_discovery_start.
        
    Returns:
        JSON string containing the job status and any results found so far.
    """
    _deprecated("library_discovery_status", "library_discovery(action='status')")
    result = (await discovery).get_job_status(job_id)
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
    depth = max(1, min(4, depth))
    domain_filter = domain if domain else None
    result = await (await research_engine).research(query, depth=depth, domain=domain_filter)
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


@m9_safe("research_list")
@mcp.tool()
async def research_list(limit: int = 20) -> str:
    _require_service()
    """List recent research results.

    Args:
        limit: Maximum results to return
        
    Returns:
        JSON string containing a list of recent research IDs and queries.
    """
    results = await (await research_engine).list_results(limit=limit)
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
    _require_service()
    """Get research engine statistics.
    
    Returns:
        JSON string containing the total count and depth distribution of research tasks.
    """
    results = await (await research_engine).list_results(limit=1000)
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
    
    Args:
        action: The operation to perform (submit|accept|complete|reject|list|get|archive)
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
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    # Validate action
    valid_actions = {"submit", "accept", "complete", "reject", "list", "get", "archive"}
    if action not in valid_actions:
        return json.dumps({"error": f"Invalid action '{action}'. Valid: {valid_actions}"})
    
    try:
        if action == "submit":
            if not all([target_channel, target_entity, source_channel, source_entity, task]):
                return json.dumps({"error": "submit requires target_channel, target_entity, source_channel, source_entity, task"})
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
                "context": context or "",
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
            handoff_index_add(packet_id, "pending")
            return json.dumps({"status": "submitted", "packet_id": packet_id, "path": str(path)})
        
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
            packet["status"] = "rejected"
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
        list_pillar_keepers: List entities with slot assignments (no args)
    
    Args:
        action: The operation to perform (assess_intent|discover_entity|list_pillar_keepers)
        query: Query to analyze (for assess_intent|discover_entity)
        
    Returns:
        JSON string with operation result.
    """
    _require_service()
    
    valid_actions = {"assess_intent", "discover_entity", "list_pillar_keepers"}
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
        
        elif action == "list_pillar_keepers":
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


# === OBSERVABILITY STREAM ===

@m9_safe("observability_stream")
@mcp.tool()
async def observability_stream() -> str:
    """Get the SSE endpoint URL for real-time observability streaming.
    
    Agents can connect to this endpoint via EventSource to receive live metrics,
    trace events, and system health updates without polling.
    
    Returns:
        JSON string with the SSE endpoint URL and connection instructions.
    """
    _require_service()
    
    # The SSE endpoint is served by the Hub's Starlette app
    # We return the relative path; the agent constructs the full URL
    return json.dumps({
        "endpoint": "/obs/stream",
        "transport": "SSE (Server-Sent Events)",
        "description": "Real-time observability stream. Connect via EventSource to receive live metrics, traces, and health updates.",
        "event_types": [
            "metric_update",      # Per-entity metric changes
            "trace_event",        # New trace events
            "health_change",      # Circuit breaker state changes
            "entity_focus"        # Entity selection changes
        ],
        "usage": "const es = new EventSource('http://localhost:8016/obs/stream'); es.onmessage = (e) => console.log(JSON.parse(e.data));"
    }, indent=2)

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
    _deprecated("library_search", "library_web_search (for web) or library_fts_search (for local)")
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



# ── Hivemind Redis Event Bus (P1-3) ───────────────────────────────────
# [heritage: redis-py 2010] Ephemeral Pub/Sub awareness layer. Durable
# coordination stays file-based (data/coordination/); Redis is ephemeral-only.
@m9_safe("hivemind_redis_publish")
@mcp.tool()
async def hivemind_redis_publish(channel: str, message: str, ttl: int = 20) -> str:
    """Publish an ephemeral Hivemind awareness message over Redis Pub/Sub.

    Used for heartbeats and live-feed deltas — high-frequency, low-stakes
    signals. Task-critical coordination remains file-based (Hivemind locks,
    handoffs). Degrades gracefully to a status="unavailable" JSON when Redis
    is not running; the file-based Hivemind is the fallback (M23).

    Args:
        channel: Channel name (e.g. "heartbeat", "live_feed").
        message: JSON or text payload to broadcast.
        ttl: Advisory TTL (seconds) echoed to subscribers for local expiry.

    Returns:
        JSON string with status, delivered count, and channel.
    """
    from mcp_servers.omega_hub.hivemind_redis import get_hivemind_redis

    bus = get_hivemind_redis()
    result = await bus.publish(channel, message, ttl=ttl)
    return json.dumps(result, indent=2)


@m9_safe("hivemind_redis_subscribe")
@mcp.tool()
async def hivemind_redis_subscribe(channel: str, timeout: float = 2.0, max_messages: int = 50) -> str:
    """Subscribe to an ephemeral Hivemind Redis Pub/Sub channel (bounded listen).

    Collects messages for up to ``timeout`` seconds (never blocks indefinitely,
    M23 Failure Integrity). Use for ephemeral awareness only; for task-critical
    work use the file-based Hivemind handoff/lock tools.

    Args:
        channel: Channel name to listen on.
        timeout: Max seconds to listen (default 2.0).
        max_messages: Max messages to collect before returning.

    Returns:
        JSON string with status, channel, and collected messages.
    """
    from mcp_servers.omega_hub.hivemind_redis import get_hivemind_redis

    bus = get_hivemind_redis()
    result = await bus.subscribe(channel, timeout=timeout, max_messages=max_messages)
    return json.dumps(result, indent=2)
