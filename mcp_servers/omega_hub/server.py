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

logger = logging.getLogger("omega.hub")

# [P1b] m9_safe decorator and apply_security imported from extracted middleware.py
from mcp_servers.omega_hub.middleware import m9_safe, apply_security


mcp = FastMCP("Omega Core Hub")

# [P1a-2] State, service singletons, hivemind state, background tasks,
# and helper functions are now in mcp_servers.omega_hub.state (extracted).
# Import block at top of file pulls them in by name.


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


# ── Cleanup / Shutdown ─────────────────────────────────────────────

# [P1a-2] _background_tasks is now imported from mcp_servers.omega_hub.state


async def _cleanup_indexer() -> None:
    """Close the indexer and cancel background tasks on server shutdown."""
    # Cancel background tasks first
    for task in _background_tasks:
        task.cancel()
    _background_tasks.clear()

    if indexer is not None:
        try:
            await indexer.close()
            logger.info("Indexer closed")
        except Exception as e:
            logger.warning("Indexer close failed: %s", e)


async def _on_startup() -> None:
    """Background startup callback — runs inside the event loop after the
    SSE listener starts. Initializes all Hub services concurrently."""
    await _init_services()
    # Start background reaper and pruning loops (CRIT-01 fix)
    _background_tasks.append(anyio.create_task(_prune_awareness_background()))
    _background_tasks.append(anyio.create_task(_reaper_background()))
    logger.info("Background tasks started: pruning, reaper")


if __name__ == "__main__":
    run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security,
            on_shutdown=_cleanup_indexer, on_startup=_on_startup)