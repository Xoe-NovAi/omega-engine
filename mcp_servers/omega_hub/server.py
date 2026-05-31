"""Omega Core Hub MCP Server — Consolidated runtime services.

Consolidates Oracle, Hivemind, Library, Research, and Stats.
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

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
from omega.library.research import ResearchEngine
from omega.mcp_runtime import run_mcp

# Initialization
mcp = FastMCP("Omega Core Hub")
registry = EntityRegistry()
oracle = Oracle(registry=registry)
hierarchy = SovereignHierarchy()
inbox = InboxManager()
curator = CurationPipeline()
library = Library()
indexer = Indexer()
discovery = DiscoveryOrchestrator()
research_engine = ResearchEngine()

_awareness: Dict[str, Dict[str, Any]] = {}
_awareness_lock = anyio.Lock()
_current_entity: Optional[str] = None
_global_tg: Optional[anyio.abc.TaskGroup] = None

# --- BACKGROUND TASKS ---

async def _prune_awareness_background() -> None:
    while True:
        try:
            now = datetime.now(timezone.utc)
            async with _awareness_lock:
                stale_clis = [cli for cli, snap in _awareness.items() if (now - datetime.fromisoformat(snap["timestamp"])).total_seconds() > 300]
                for cli in stale_clis: del _awareness[cli]
        except Exception: pass
        await anyio.sleep(60)

# --- MINIMAL TOOLS (To be expanded) ---

@mcp.tool()
async def oracle_talk(query: str) -> str:
    """Route a query through the Omega Oracle."""
    global _current_entity
    response = await oracle.talk(query)
    _current_entity = response.entity
    return json.dumps(asdict(response), indent=2)

@mcp.tool()
async def hivemind_heartbeat(cli_name: str, status: str = "active") -> str:
    """Register agent presence."""
    async with _awareness_lock:
        _awareness[cli_name] = {"status": status, "timestamp": datetime.now(timezone.utc).isoformat()}
    return f"Heartbeat for {cli_name} acknowledged."

# --- HTTP ENDPOINTS ---

def _add_hub_endpoints(app):
    import logging
    logger = logging.getLogger("omega.hub")

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
                with open(path, "r") as f: data = yaml.safe_load(f)
                return JSONResponse(data)
            return JSONResponse({"providers": []})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _provider_list(request):
        try:
            path = PROJECT_ROOT / "config" / "providers.yaml"
            if path.exists():
                import yaml
                with open(path, "r") as f: data = yaml.safe_load(f)
                chain = data.get("inference", {}).get("fallback_chain", [])
                names = [p.get("provider") for p in chain if "provider" in p]
                return JSONResponse({"providers": names})
            return JSONResponse({"providers": []})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _app_agents(request):
        try:
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

    from contextlib import asynccontextmanager
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
