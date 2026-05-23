"""Omega Research MCP Server — Multi-depth research engine.

AP: AP-OMEGA-RESEARCH-MCP-v1.0.0
ICS: [NODE: OSIRIS | ARCHETYPE: APOLLO | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: RESEARCH-MCP]

Provides MCP tools for:
  - Multi-depth research (Level 1-4)
  - Research result retrieval
  - Research history

Depth levels:
  1 (Quick) — 1-2 sources, < 30s
  2 (Standard) — 3-5 sources, < 2min
  3 (Deep) — 6-15 sources, < 10min
  4 (Scholarly) — 10-50 sources, < 30min

Usage:
    cd ~/omega && python mcp/omega-research/server.py
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

import json
from mcp.server.fastmcp import FastMCP

from omega.library.research import ResearchEngine, RESEARCH_DEPTHS

mcp = FastMCP("Omega Research")
engine = ResearchEngine()


@mcp.tool()
async def research(
    query: str,
    depth: int = 2,
    domain: str = "",
) -> str:
    """Execute multi-depth research on a query using the offline library.

    The deeper the level, the more sources are gathered and synthesized.

    Args:
        query: The research question or topic
        depth: Research depth 1=Quick, 2=Standard, 3=Deep, 4=Scholarly
        domain: Optional domain filter (ai_ml, programming, research, security, philosophy, systems, knowledge, general)
    """
    depth = max(1, min(4, depth))
    domain_filter = domain if domain else None
    result = await engine.research(query, depth=depth, domain=domain_filter)
    return json.dumps(result.to_dict(), indent=2, default=str)


@mcp.tool()
async def research_get(research_id: str) -> str:
    """Retrieve a previous research result by ID.

    Args:
        research_id: Research ID (e.g. res_abc123)
    """
    result = await engine.get_result(research_id)
    if not result:
        return json.dumps({"error": f"Research '{research_id}' not found"})
    return json.dumps(result.to_dict(), indent=2, default=str)


@mcp.tool()
async def research_list(limit: int = 20) -> str:
    """List recent research results.

    Args:
        limit: Maximum results to return
    """
    results = await engine.list_results(limit=limit)
    return json.dumps(results, indent=2, default=str)


@mcp.tool()
async def research_depths() -> str:
    """List available research depth levels and their configurations."""
    return json.dumps(RESEARCH_DEPTHS, indent=2)


@mcp.tool()
async def research_stats() -> str:
    """Get research engine statistics."""
    results = await engine.list_results(limit=1000)
    depths = {}
    for r in results:
        d = str(r.get("depth", 2))
        depths[d] = depths.get(d, 0) + 1
    return json.dumps({
        "total_research": len(results),
        "by_depth": depths,
    }, indent=2)


from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
