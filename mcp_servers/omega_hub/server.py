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
# To run with SSE transport (for MCP client connections from Cline/OpenCode):
#   OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 python mcp_servers/omega_hub/server.py
#

"""

import sys

# ── Fix: canonical module name registration ──
# When server.py runs as __main__ (python server.py), Python registers it under
# '__main__' but NOT under 'mcp_servers.omega_hub.server'. When tools.py does
# "from mcp_servers.omega_hub.server import mcp" at line 44, Python doesn't find
# the module in sys.modules and re-imports server.py as a fresh module,
# creating a SECOND FastMCP instance with 0 tools registered on it.
# This fix ensures both names point to the same module object.
if __name__ == "__main__":
    _canonical = "mcp_servers.omega_hub.server"
    if _canonical not in sys.modules:
        sys.modules[_canonical] = sys.modules[__name__]

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

# ── Bootstrapping: ensure mcp_servers is resolvable from any context ──
# This handles systemd (PYTHONPATH via service unit), direct CLI invocation, and IDE launches.
_server_file = Path(__file__).resolve()
_mcp_servers_root = str(_server_file.parents[1])  # omega-engine/mcp_servers/
_project_root = str(_server_file.parents[2])       # omega-engine/
for p in [_project_root, _mcp_servers_root]:
    if p not in sys.path:
        sys.path.insert(0, p)
# [P1b] contextvars and threading are no longer used directly in server.py
# (now in state.py and middleware.py respectively)


import anyio
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import CallToolResult, TextContent
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
# [P1b] Middleware (RateLimitMiddleware, RequestSizeLimitMiddleware, apply_security)
# now imported from mcp_servers.omega_hub.middleware


# ═══════════════════════════════════════════════════════════════════════════
# P1a-2: Import state from extracted module (replaces inline definitions)
# ═══════════════════════════════════════════════════════════════════════════
from mcp_servers.omega_hub import state
from mcp_servers.omega_hub.state import (
    PROJECT_ROOT,
    _init_complete, _init_error, _require_service, _init_services,
    registry, model_gateway, oracle, hierarchy,
    inbox, curator, library, indexer, discovery,
    research_engine, sovereign_search_service,
    _current_entity, HEARTBEAT_TTL, HALL_OF_RECORDS,
    _hot_store, _hot_store_lock, _awareness, _awareness_lock,
    _extended_sessions, _extended_sessions_lock, EXTENDED_SESSIONS_FILE,
    EXTENDED_SAFETY_TTL_DEFAULT,
    _background_tasks, _get_intent_matcher,
    HANDOFF_PENDING, HANDOFF_ACTIVE, HANDOFF_COMPLETED, HANDOFF_STALE, HANDOFF_ARCHIVE,
    LOCKS_BASE, METRICS_PATH,
    _make_agent_id, _cold_path, _latest_path, _find_packet_path,
    # P0-2: Sharded hot store
    hot_store_set, hot_store_get, hot_store_get_all,
    # P0-4: Cold-store cache
    get_cached_cold_awareness, invalidate_awareness_cache,
    # P1-6: Handoff index
    handoff_index_rebuild,
)

# [P1a-3] Background orchestration: pruning, reaping, metrics
from mcp_servers.omega_hub.background import (
    _prune_awareness_background,
    _run_discovery_background,
    _reap_stale_locks,
    _reap_stale_handoffs,
    _reaper_background,
    _write_metrics,
)

from omega.observability import new_trace_id, get_engine
from omega.oracle.security import tdp_wrap, determine_url_taint
from omega.ics import render as ics_render_logic
from omega.mcp_runtime import run_mcp
from omega.observability.observability_reader import SovereignReader
from pathlib import Path
import os

logger = logging.getLogger("omega.hub")

# [P1b] m9_safe decorator and apply_security imported from extracted middleware.py
from mcp_servers.omega_hub.middleware import m9_safe, apply_security


mcp = FastMCP("Omega Core Hub")

# [P1a-2] State, service singletons, hivemind state, background tasks,
# and helper functions are now in mcp_servers.omega_hub.state (extracted).
# Import block at top of file pulls them in by name.

# Initialize SovereignReader for observability streaming
data_dir = Path(os.environ.get("OMEGA_DATA_DIR", "data"))
_sovereign_reader = SovereignReader(
    db_path=data_dir / "observability" / "metrics.db",
    trace_dir=data_dir / "traces",
    crash_dir=data_dir / "crashes"
)


# [P1b] All MCP tool definitions moved to mcp_servers.omega_hub.tools
# They register with the mcp instance via side-effect import.
from mcp_servers.omega_hub import tools  # noqa: F401


def __getattr__(name: str):
    """Lazy-load tools to resolve circular imports while maintaining backward compatibility."""
    if name in [
        "oracle_talk", "oracle_summon", "oracle_summon_local", "oracle_list_entities",
        "oracle_list_pillar_keepers", "oracle_entity_info", "oracle_assess_intent",
        "oracle_discover_entity", "sovereign_search", "delegate_task",
        "hivemind_post_context", "hivemind_heartbeat", "hivemind_get_awareness",
        "hivemind_get_continuation", "hivemind_extended_checkin", "hivemind_extended_checkout",
        "hivemind_get_session", "hivemind_list_sessions", "hivemind_get_entity_context",
        "hivemind_workspace_lock_acquire", "hivemind_workspace_lock_release",
        "hivemind_workspace_lock_check", "hivemind_submit_handoff", "hivemind_accept_handoff",
        "hivemind_complete_handoff", "hivemind_reject_handoff", "hivemind_handoff_list",
        "hivemind_get_handoff", "hivemind_handoff_archive"
    ]:
        import mcp_servers.omega_hub.tools as _tools
        return getattr(_tools, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# === HTTP ENDPOINTS (OpenCode 1.15+ High-Fidelity Handshake) ===

async def _health(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.2.0"
    })

async def _debug_tools(request: Request) -> JSONResponse:
    """Diagnostic: count tools registered in the mcp instance."""
    tool_count = len(mcp._tool_manager._tools)
    tool_names = list(mcp._tool_manager._tools.keys())[:10]
    handler_count = len(mcp._mcp_server.request_handlers)
    return JSONResponse({
        "tool_manager_count": tool_count,
        "handler_count": handler_count,
        "sample_tools": tool_names,
        "mcp_id": id(mcp),
    })

async def _entity_current(request: Request) -> JSONResponse:
    entity_name = _current_entity.get() or "SOPHIA"
    if registry is None:
        return JSONResponse({"entity": entity_name, "note": "services initializing"})
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


# === OBSERVABILITY SSE STREAM ===

async def _observability_stream(request: Request) -> None:
    """Server-Sent Events stream for real-time observability data.
    
    Agents connect to this endpoint to receive live metrics, traces, and health updates.
    Uses the SovereignReader to fetch data without blocking the event loop.
    """
    from sse_starlette.sse import EventSourceResponse
    
    async def event_generator():
        import asyncio
        while True:
            try:
                # Fetch data using SovereignReader (offloads to threads)
                health = await _sovereign_reader.get_fleet_health()
                traces = await _sovereign_reader.tail_live_traces(max_lines=10)
                
                # Build payload
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "health": {
                        "breaker_states": health.breaker_states,
                        "global_error_rate": health.global_error_rate
                    },
                    "traces": [
                        {
                            "timestamp": t.timestamp,
                            "level": t.level,
                            "entity": t.entity,
                            "message": t.message,
                            "trace_id": t.trace_id
                        }
                        for t in traces
                    ]
                }
                
                yield {"event": "observability_update", "data": json.dumps(payload)}
                
            except Exception as e:
                logger.error(f"Observability stream error: {e}")
                yield {"event": "error", "data": json.dumps({"error": str(e)})}
            
            # Wait 2 seconds before next update
            await asyncio.sleep(2)
    
    return EventSourceResponse(event_generator())


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

# [P1b] SovereignGateway + _proxy_handler extracted to gateway.py
from mcp_servers.omega_hub.gateway import _proxy_handler

# hub_routes — includes the /proxy/ handler imported from gateway.py
hub_routes = [
    Route("/health", _health),
    Route("/debug/tools", _debug_tools),
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
    Route("/obs/stream", _observability_stream),
]


# ── Cleanup / Shutdown ─────────────────────────────────────────────

# [P1a-2] _background_tasks is now imported from mcp_servers.omega_hub.state


async def _cleanup_indexer() -> None:
    """Close the indexer on server shutdown.
    Background tasks are cancelled automatically by the lifespan TaskGroup.
    Order: batch writer flush FIRST, then indexer close, then gateway client.
    [id-soft: doom3-2004] idHeap — explicit shutdown sequence for all allocations."""
    from omega.memory_store import get_memory_store
    store = get_memory_store()
    try:
        await store.stop_batch_writer()
        logger.info("MemoryStore batch writer stopped cleanly")
    except Exception as e:
        logger.error("MemoryStore batch writer stop FAILED — pending writes may be lost: %s", e)

    if indexer is not None:
        try:
            await indexer.close()
            logger.info("Indexer closed")
        except Exception as e:
            logger.warning("Indexer close failed: %s", e)

    # Close SovereignGateway httpx client (P0-1)
    if state.gateway is not None:
        try:
            await state.gateway.client.aclose()
            logger.info("SovereignGateway HTTP client closed")
        except Exception as e:
            logger.warning("Gateway client close failed: %s", e)


async def _on_startup(tg: anyio.abc.TaskGroup = None) -> None:
    """Background startup callback — receives TaskGroup from lifespan for
    running background loops concurrently with the server."""
    await _init_services()

    # P1-6: Rebuild handoff packet index from filesystem
    try:
        count = await handoff_index_rebuild()
        logger.info("Handoff index rebuilt: %d packets", count)
    except Exception as e:
        logger.warning("Handoff index rebuild failed: %s", e)

    # Start background reaper and pruning loops (AnyIO TaskGroup pattern)
    if tg:
        tg.start_soon(_prune_awareness_background)
        tg.start_soon(_reaper_background)
        
        # Start MemoryStore batch writer
        from omega.memory_store import get_memory_store
        store = get_memory_store()
        tg.start_soon(store.start_batch_writer, tg)
    else:
        logger.warning("No TaskGroup provided — background loops not started")
    logger.info("Background tasks started: pruning, reaper")


if __name__ == "__main__":
    run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security,
            on_shutdown=_cleanup_indexer, on_startup=_on_startup)