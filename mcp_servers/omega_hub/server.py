# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

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
from mcp.server.transport_security import TransportSecuritySettings
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


# Transport security for LAN binding (0.0.0.0) — allows HP LAN IP + loopback + Tailscale mesh with all ports
# FED-HANDOFF-ANTIGRAVITY-20260920: Machine renamed omega-hub → n0; n0 entries added to unblock
# Node 1 MCP access (421 Misdirected Request). omega-hub entries retained for backward compat.
_transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[
        "192.168.10.168", "192.168.10.168:*",
        "127.0.0.1", "127.0.0.1:*",
        "localhost", "localhost:*",
        "[::1]", "[::1]:*",
        # Tailscale L2 federation (C6 v1.1 / L2_ACCEPTANCE.md FED-L2-001)
        "100.123.51.67", "100.123.51.67:*",
        # n0 — current hostname (renamed from omega-hub 2026-09-19)
        "n0", "n0:*",
        "n0.tail51f14a.ts.net", "n0.tail51f14a.ts.net:*",
        # omega-hub — legacy hostname (retained for backward compat with older clients)
        "omega-hub.tail51f14a.ts.net", "omega-hub.tail51f14a.ts.net:*",
        "*.tail51f14a.ts.net", "*.tail51f14a.ts.net:*",
    ],
    allowed_origins=[
        "http://192.168.10.168:*",
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://100.123.51.67:*",
        # n0 origins
        "http://n0:*",
        "http://n0.tail51f14a.ts.net:*",
        # omega-hub origins (legacy)
        "http://omega-hub.tail51f14a.ts.net:*",
        "http://*.tail51f14a.ts.net:*",
    ],
)

# SSOT for the version surfaced by /health and MCP serverInfo
# (pyproject.toml [project] version, resolved by omega.__version__).
from omega import __version__ as _ENGINE_VERSION

mcp = FastMCP(
    "Omega Core Hub",
    json_response=True,  # JSON-only responses for OpenCode/Cline compatibility
    transport_security=_transport_security,
)


# ═══════════════════════════════════════════════════════════════════════════
# M23 — REFUSE INPUT THE TOOL CANNOT HONOUR  (2026-09-29, GE-N1 finding)
# ═══════════════════════════════════════════════════════════════════════════
# THE DEFECT CLASS: THE INTERFACE ACCEPTS INPUT IT DOES NOT HONOUR.
#
# GE-N1 called `hivemind_handoff(action="submit", artifact_ids=[...])` over the
# wire, got `{"status": "submitted"}`, and the stored packet had no
# `artifact_ids` field at all. `artifact_ids` is in no signature and no schema.
# They were not misusing the tool — the server should have thrown. A rejection
# is safe: it fails loudly. A silent accept converts an error into a false
# belief that propagates to the next agent, the next node, the next week.
#
# ROOT CAUSE, and it is NOT in our code. FastMCP builds a pydantic `arg_model`
# from each tool's signature and validates with it at
#     mcp/server/fastmcp/utilities/func_metadata.py:107
#         arguments_parsed_model = self.arg_model.model_validate(...)
# Pydantic's default is `extra='ignore'`, so any key not in the signature is
# DISCARDED during validation and never reaches the function. Calling the tool
# directly raises TypeError; only the wire path loses it — which is why a
# schema-only test passes while the defect ships. See
# `tests/test_handoff_contract.py::test_artifact_ids_is_rejected_not_dropped`.
#
# The fix is to make the arg model STRICT for every registered tool, so an
# unknown parameter becomes a ValidationError -> `m9_safe` -> `isError=True`.
# Applied generally rather than to `artifact_ids` alone: the class is the
# defect, and a one-off fix for one parameter leaves the next one open.
def _enforce_strict_tool_arguments(_server) -> int:
    tools = getattr(getattr(_server, "_tool_manager", None), "_tools", {}) or {}
    hardened = 0
    for _name, _tool in tools.items():
        meta = getattr(_tool, "fn_metadata", None)
        model = getattr(meta, "arg_model", None)
        if model is None:
            continue
        try:
            if model.model_config.get("extra") == "forbid":
                continue
            model.model_config["extra"] = "forbid"
            model.model_rebuild(force=True)
            hardened += 1
        except Exception as exc:  # pragma: no cover — never block boot
            logger.warning("strict-args hardening skipped for %s: %s", _name, exc)
    return hardened


# FastMCP (mcp 1.30.0) accepts no `version` kwarg; when the underlying
# serverInfo version is unset the SDK reports its OWN library version, so
# clients saw "1.30.0" (the mcp package) instead of the engine version.
# Set it explicitly, guarded so an SDK change can never block boot.
try:
    mcp._mcp_server.version = _ENGINE_VERSION
except (AttributeError, ValueError) as exc:  # pragma: no cover - defensive
    import sys as _sys

    print(
        f"[TOOL-CHAIN-COLLAPSE] could not set MCP serverInfo version: {exc}",
        file=_sys.stderr,
    )

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
from mcp_servers.omega_hub import hub_tools as tools  # noqa: F401

# ── Tool Surface Curation (2026-09-22) ────────────────────────────────
# Remove deprecated/confusing tools so the exposed surface stays
# temple-grade. Removed tools are filtered from list_tools and cannot
# be called (mcp SDK FastMCP.remove_tool).
#
# library_search: legacy hybrid-search name, superseded by
#   library_fts_search (local FTS5) + library_web_search (web). Its name
#   misleadingly suggested local search while hitting the web pipeline.
try:
    mcp.remove_tool("library_search")
    logger.info("Tool surface curation: removed deprecated 'library_search'")
except Exception as e:  # pragma: no cover — defensive, must never block boot
    logger.warning("Tool surface curation failed (non-fatal): %s", e)


# Legacy tool names retired during tool-surface curation (92 → 66 tools),
# mapped to their unified replacements. Accessing any of these names returns a
# thin adapter so existing callers keep working instead of raising
# AttributeError. Each entry is (unified_tool_name, bound_kwargs).
_LEGACY_TOOL_ADAPTERS = {
    # Hivemind handoff: 7 fragmented tools → 1 action-based tool
    "hivemind_submit_handoff": ("hivemind_handoff", {"action": "submit"}),
    "hivemind_accept_handoff": ("hivemind_handoff", {"action": "accept"}),
    "hivemind_complete_handoff": ("hivemind_handoff", {"action": "complete"}),
    "hivemind_reject_handoff": ("hivemind_handoff", {"action": "reject"}),
    "hivemind_handoff_list": ("hivemind_handoff", {"action": "list"}),
    "hivemind_get_handoff": ("hivemind_handoff", {"action": "get"}),
    "hivemind_handoff_archive": ("hivemind_handoff", {"action": "archive"}),
    # [maat 2026-09-29] R1-R3 legacy names, so callers written against the
    # three-queue era keep working across the four-directory refactor.
    "hivemind_inbox": ("hivemind_handoff", {"action": "inbox"}),
    "hivemind_receipts": ("hivemind_handoff", {"action": "receipts"}),
    "hivemind_read_handoff": ("hivemind_handoff", {"action": "read"}),
    "hivemind_federation_list": ("hivemind_handoff", {"action": "list"}),
    # Oracle debug: 3 fragmented tools → 1 action-based tool
    "oracle_list_slot_keepers": ("oracle_debug", {"action": "list_slot_keepers"}),
    "oracle_assess_intent": ("oracle_debug", {"action": "assess_intent"}),
    "oracle_discover_entity": ("oracle_debug", {"action": "discover_entity"}),
    # Hivemind awareness: 9 fragmented tools → 1 action-based tool
    # [seam-fix 2026-09-28 maat] These 9 names were previously listed in
    # _PASSTHROUGH_TOOLS, which does `getattr(_tools, name)`. The consolidation
    # deleted all 9 from tools.py, so EVERY one of them raised
    #   AttributeError: module '...hub_tools.tools' has no attribute 'hivemind_post_context'
    # on first use — a deferred failure that only fired when a caller actually
    # invoked the name, which is why the hub booted clean and stayed broken.
    # They are adapters now, bound to the correct hivemind_awareness action.
    "hivemind_post_context": ("hivemind_awareness", {"action": "post"}),
    "hivemind_heartbeat": ("hivemind_awareness", {"action": "heartbeat"}),
    "hivemind_get_awareness": ("hivemind_awareness", {"action": "get"}),
    "hivemind_get_continuation": ("hivemind_awareness", {"action": "continuation"}),
    "hivemind_extended_checkin": ("hivemind_awareness", {"action": "extended_checkin"}),
    "hivemind_extended_checkout": ("hivemind_awareness", {"action": "extended_checkout"}),
    "hivemind_get_session": ("hivemind_awareness", {"action": "session"}),
    "hivemind_list_sessions": ("hivemind_awareness", {"action": "list"}),
    "hivemind_get_entity_context": ("hivemind_awareness", {"action": "entity_context"}),
    # Hivemind lock: 3 fragmented tools → 1 action-based tool (same defect, same fix)
    "hivemind_workspace_lock_acquire": ("hivemind_lock", {"action": "acquire"}),
    "hivemind_workspace_lock_release": ("hivemind_lock", {"action": "release"}),
    "hivemind_workspace_lock_check": ("hivemind_lock", {"action": "check"}),
}

# Legacy parameter names that differ from their unified replacement.
# [seam-fix 2026-09-28 maat] The adapter forwards **kwargs straight through, so a
# legacy name whose signature used a different parameter name raises TypeError on
# call. This was the only such mismatch across all 12 awareness/lock tools,
# established by comparing every pre-consolidation signature
# (tools.py.fixbak) against the unified ones:
#
#   OLD  hivemind_get_entity_context(entity_name: str)      tools.py.fixbak:854
#   NEW  hivemind_awareness(action, channel, entity, ...)   tools.py:2125
#
# The other 11 (post_context, heartbeat, get_awareness, get_continuation,
# extended_checkin/out, get_session, list_sessions, lock_acquire/release/check)
# share every parameter name and forward unchanged.
#
# Kept declarative and separate from _LEGACY_TOOL_ADAPTERS so the binding map
# stays a flat (target, kwargs) table that existing adapter-contract tests read
# without needing to know about renames.
_LEGACY_KWARG_RENAMES = {
    "hivemind_get_entity_context": {"entity_name": "entity"},
}

# Tools still resolvable by their original name — these MUST still exist as
# module-level functions in hub_tools/tools.py, because __getattr__ forwards
# them with a bare getattr(_tools, name) and no adapter.
#
# [seam-fix 2026-09-28 maat] The 9 Hivemind awareness names and 3 Hivemind lock
# names were REMOVED from this set and given real adapter bindings above. They
# were dead entries: naming a deleted symbol here produced a shim that resolved
# the name and then failed with AttributeError on invocation. Every name in this
# set is asserted to exist by tests/test_hub_import_smoke.py::test_passthrough_tools_exist,
# so a future consolidation cannot silently reintroduce a dead passthrough.
_PASSTHROUGH_TOOLS = frozenset({
    "oracle_talk", "oracle_summon", "oracle_summon_local", "oracle_list_entities",
    "oracle_entity_info", "sovereign_search",
})


def _raw_tool(tool: object) -> object:
    """Return the underlying coroutine of a FastMCP-decorated tool.

    @mcp.tool() wraps callables so direct invocation yields a CallToolResult
    instead of the tool's JSON string. Adapters must call the raw function.
    """
    return getattr(tool, "__wrapped__", tool)


def __getattr__(name: str):
    """Lazy-load tools to resolve circular imports while maintaining backward compatibility."""
    import mcp_servers.omega_hub.hub_tools.tools as _tools

    if name in _PASSTHROUGH_TOOLS:
        return getattr(_tools, name)

    if name in _LEGACY_TOOL_ADAPTERS:
        target_name, bound_kwargs = _LEGACY_TOOL_ADAPTERS[name]
        renames = _LEGACY_KWARG_RENAMES.get(name, {})
        _raw = _raw_tool(getattr(_tools, target_name))

        async def _legacy_adapter(**kwargs):
            """Backward-compatible adapter → unified action-based tool."""
            if renames:
                for old_param, new_param in renames.items():
                    if old_param in kwargs:
                        kwargs[new_param] = kwargs.pop(old_param)
            return await _raw(**{**bound_kwargs, **kwargs})

        _legacy_adapter.__name__ = name
        _legacy_adapter.__doc__ = (
            f"Backward-compatible adapter for {target_name} "
            f"(bound: {', '.join(f'{k}={v!r}' for k, v in bound_kwargs.items())})."
        )
        return _legacy_adapter

    if name == "delegate_task":
        # Retired in favour of oracle_summon; preserved because callers used it
        # as a context-prefixed summon.
        _raw_summon = _raw_tool(getattr(_tools, "oracle_summon"))

        async def _delegate_task(target_entity: str, query: str, context: str = "") -> str:
            full_query = f"CONTEXT: {context}\n\nREQUEST: {query}" if context else query
            return await _raw_summon(entity_name=target_entity, query=full_query)

        _delegate_task.__name__ = "delegate_task"
        _delegate_task.__doc__ = "Backward-compatible adapter for oracle_summon."
        return _delegate_task

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# === HTTP ENDPOINTS (OpenCode 1.15+ High-Fidelity Handshake) ===

async def _health(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": _ENGINE_VERSION
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
            await anyio.sleep(2)
    
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
                "slot": desc.get("slot"),
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

    # P0-5: stamp the code we loaded so a later probe can detect a stale
    # process running pre-fix code.
    try:
        from mcp_servers.omega_hub import code_stamp
        from pathlib import Path as _P
        code_stamp.write_stamp(_P(__file__).resolve().parents[2])
    except Exception as e:
        logger.warning("code stamp write failed: %s", e)

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


# ── M23 strict arguments: RUN AFTER the @mcp.tool() registrations ──
# MUST run BEFORE `run_mcp(...)` below, which BLOCKS for the process lifetime.
# The first two attempts sat AFTER it and therefore never executed at all —
# verified by the missing journal line, not assumed. Three placement bugs in
# one fix, each caught by executing rather than reading.
try:
    _strict_tools = _enforce_strict_tool_arguments(mcp)
    if _strict_tools:
        logger.info(
            "M23 strict-arguments: hardened %d tool schema(s) to reject unknown "
            "parameters instead of silently dropping them", _strict_tools)
except Exception as exc:  # pragma: no cover — defensive, must never block boot
    logger.warning("M23 strict-arguments hardening unavailable: %s", exc)


if __name__ == "__main__":
    run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security,
            on_shutdown=_cleanup_indexer, on_startup=_on_startup)
