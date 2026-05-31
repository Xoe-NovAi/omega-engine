"""Omega Oracle MCP Server — exposes Oracle as MCP tools for OpenCode agents.

AP Token: AP-OMEGA-ORACLE-MCP-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: ORACLE-MCP]

Usage:
    cd ~/omega && python mcp/omega-oracle/server.py
    # or via fastmcp:
    fastmcp run mcp/omega-oracle/server.py
"""

import sys
import os
from pathlib import Path

# Ensure omega module is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

import anyio
import json
from mcp.server.fastmcp import FastMCP

from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry

mcp = FastMCP("Omega Oracle")
registry = EntityRegistry()
oracle = Oracle(registry=registry)


@mcp.tool()
async def talk(query: str) -> str:
    """Route a query through the Omega Oracle.

    The Oracle uses speculative decoding:
    - Simple queries handled by Nova (functiongemma-270m)
    - Complex queries escalated to domain-matched Pillar Keeper
    - Explicit @summon or 'summon Name' routes directly to entity

    Args:
        query: The user's query text
    """
    from omega.observability import new_trace_id
    trace_id = new_trace_id()
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
async def summon(entity_name: str, query: str) -> str:
    """Directly summon a specific entity by name.

    Bypasses the speculative decoder and routes directly
    to the named entity's model.

    Args:
        entity_name: Name of the entity to summon
        query: The question or message for the entity
    """
    from omega.observability import new_trace_id
    trace_id = new_trace_id()
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
def list_entities() -> str:
    """List all entities in the Omega pantheon.

    Returns each entity's name, pillar, role, description,
    pantheon, element, and energy metadata.
    """
    entities = registry.list()
    result = []
    for e in entities:
        sigil_str = f" {e.sigil}" if e.sigil else ""
        result.append({
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
        })
    return json.dumps(result, indent=2)


@mcp.tool()
def list_pillar_keepers() -> str:
    """List only the 10 Pillar Keepers (core pantheon)."""
    entities = registry.list_pillar_keepers()
    result = []
    for e in entities:
        sigil_str = f" {e.sigil}" if e.sigil else ""
        result.append({
            "name": e.name,
            "pillars": e.pillars,
            "element": e.element,
            "chakra": e.chakra,
            "planet": e.planet,
            "sigil": e.sigil,
        })
    return json.dumps(result, indent=2)


@mcp.tool()
def entity_info(name: str) -> str:
    """Get detailed information about a specific entity.

    Args:
        name: Entity name (case-insensitive, partial match supported)
    """
    entity = registry.get(name)
    if not entity:
        entity = registry.find_by_name_fragment(name)
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
def assess_intent(query: str) -> str:
    """Test how the Oracle would classify a query without generating a response.

    Useful for debugging intent detection and domain routing.

    Args:
        query: The query to classify
    """
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


from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
