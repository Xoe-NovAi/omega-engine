"""Omega Core Hub MCP Server — Consolidated runtime services.

AP Token: AP-OMEGA-CORE-HUB-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: MiMo-2.5 | CONTEXT: CORE-HUB-MCP]

Consolidates the following services into a single FastMCP endpoint:
  - Oracle: Routing, Summoning, and Entity Intelligence
  - Hivemind: Cross-CLI awareness and session context
  - Library: RAG intake, curation, and offline indexing
  - Research: Multi-depth research engine
  - Stats: System monitoring and Omega metrics

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
import anyio
import yaml
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

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

# Research engine
research_engine = ResearchEngine()

# Hivemind State
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)
_awareness: Dict[str, Dict[str, Any]] = {}
_awareness_lock = anyio.Lock()
_current_entity: Optional[str] = None
# --- TOOLS ---

@mcp.tool()
async def oracle_talk(query: str) -> str:
    """Route a query through the Omega Oracle."""
    global _current_entity
    response = await oracle.talk(query)
    _current_entity = response.entity
    return json.dumps(asdict(response), indent=2)

@mcp.tool()
async def oracle_summon(entity_name: str, query: str) -> str:
    """Directly summon a specific entity."""
    global _current_entity
    response = await oracle.summon(entity_name, query)
    _current_entity = response.entity
    return json.dumps(asdict(response), indent=2)

@mcp.tool()
async def hivemind_heartbeat(cli_name: str, status: str = "active") -> str:
    """Register agent presence."""
    async with _awareness_lock:
        _awareness[cli_name] = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    return f"Heartbeat for {cli_name} acknowledged."

# --- HTTP ENDPOINTS (OpenCode 1.15+ High-Fidelity Handshake) ---

async def _health(request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.2.0"
    })

async def _entity_current(request: Request) -> JSONResponse:
    try:
        entity_name = _current_entity or "SOPHIA"
        entity = registry.get(entity_name)
        if entity:
            return JSONResponse({
                "entity": entity.name,
                "pillars": getattr(entity, "pillars", []),
                "role": getattr(entity, "role", "")
            })
        return JSONResponse({"entity": entity_name, "pillars": [], "note": "entity not in registry"})
    except Exception as exc:
        return JSONResponse({"entity": "SOPHIA", "error": str(exc)}, status_code=500)

async def _config_providers(request: Request) -> JSONResponse:
    """GET /config/providers and /config.providers"""
    try:
        path = PROJECT_ROOT / "config" / "providers.yaml"
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            return JSONResponse(data)
        return JSONResponse({"inference": {"fallback_chain": []}})
    except Exception as e:
        logger.error(f"Error in /config/providers: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def _provider_list(request: Request) -> JSONResponse:
    """GET /provider and /provider.list"""
    try:
        path = PROJECT_ROOT / "config" / "providers.yaml"
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
        return JSONResponse(providers)
    except Exception as e:
        logger.error(f"Error in /provider: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def _agent_list(request: Request) -> JSONResponse:
    """GET /agent and /app.agents"""
    try:
        agents = []
        for e in registry.list():
            agents.append({
                "id": e.name.lower(),
                "name": e.name,
                "description": e.personality[:100] + "..." if len(e.personality) > 100 else e.personality,
                "mode": "subagent",
                "permission": [{"permission": "task", "pattern": "*", "action": "allow"}],
                "options": {},
                "prompt": e.personality,
                "model": {"modelID": e.model, "providerID": "native-gguf"}
            })
        return JSONResponse(agents)
    except Exception as e:
        logger.error(f"Error in /agent: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

async def _config_get(request: Request) -> JSONResponse:
    """GET /config, /config.get, /global/config"""
    try:
        path = PROJECT_ROOT / "opencode.json"
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            return JSONResponse(data)
        return JSONResponse({"error": "opencode.json not found"}, status_code=404)
    except Exception as e:
        logger.error(f"Error in /config: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# --- CUSTOM ROUTES (Starlette) ---
# These are registered at the TOP level of the app, BEFORE the MCP
# sub-app mount. This ensures OpenCode 1.15+ dot-separated paths
# (config.get, config.providers, provider.list, app.agents) are matched
# before the MCP framework's routing.

hub_routes = [
    Route("/health", _health),
    Route("/entity/current", _entity_current),
    # Slash-separated paths
    Route("/config/providers", _config_providers),
    Route("/provider", _provider_list),
    Route("/agent", _agent_list),
    Route("/config", _config_get),
    Route("/global/config", _config_get),
    # OpenCode 1.15+ dot-separated paths (startup handshake)
    Route("/config.get", _config_get),
    Route("/config.providers", _config_providers),
    Route("/provider.list", _provider_list),
    Route("/app.agents", _agent_list),
]

# --- MAIN ---

if __name__ == "__main__":
    run_mcp(mcp, custom_routes=hub_routes)