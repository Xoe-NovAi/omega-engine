# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Grokster — Hydration MCP Tool (Prototype)
# MCP tool registration for omega-hub_entity_hydrate
# Location: src/omega/infra/hydration/mcp_tool.py (when implemented)

"""
MCP Tool: omega-hub_entity_hydrate

Hydrates an entity by reading all soul files in parallel and returning
a structured HydrationContext. Replaces 5-8 sequential file reads with
one server-side batch operation.

Registration:
    In Omega Hub MCP server (src/omega/omega_hub/server.py or similar):
    
    from omega.infra.hydration.mcp_tool import register_hydration_tool
    
    register_hydration_tool(mcp)
"""

from typing import Optional
import logging

logger = logging.getLogger("omega.hydration.mcp")


async def entity_hydrate(
    entity_name: str,
    session_id: Optional[str] = None,
    include_full_gnosis: bool = False,
) -> str:
    """Hydrate an entity — reads all soul files, assembles context.
    
    Call this at session start to get full entity identity, history,
    and momentum in one shot. Replaces 5-8 sequential file reads.
    
    Args:
        entity_name: Entity to hydrate (e.g., "grokster", "kali", "roc_racoon")
        session_id: Optional current session ID for trace linkage
        include_full_gnosis: If true, include full session_gnosis.md text (default: false — summary only)
    
    Returns:
        Compact context string for model injection (~200 tokens)
    """
    from omega.infra.hydration.orchestrator import entity_hydrate as _hydrate
    
    try:
        context = await _hydrate(entity_name, session_id, include_full_gnosis)
        return context.to_context_string()
    except Exception as e:
        logger.error(f"Hydration failed for {entity_name}: {e}")
        return f"## Hydration Failed\nEntity: {entity_name}\nError: {e}\n\nProceeding with Soul Kernel only."


def register_hydration_tool(mcp) -> None:
    """Register the entity_hydrate tool with the MCP server."""
    
    @mcp.tool()
    async def entity_hydrate(
        entity_name: str,
        session_id: Optional[str] = None,
        include_full_gnosis: bool = False,
    ) -> str:
        """Hydrate an entity — reads all soul files, assembles context.
        
        Call this at session start to get full entity identity, history,
        and momentum in one shot. Replaces 5-8 sequential file reads.
        
        Args:
            entity_name: Entity to hydrate (e.g., "grokster", "kali", "roc_racoon")
            session_id: Optional current session ID for trace linkage
            include_full_gnosis: If true, include full session_gnosis.md text (default: false — summary only)
        
        Returns:
            Compact context string for model injection (~200 tokens)
        """
        from omega.infra.hydration.orchestrator import entity_hydrate as _hydrate
        
        try:
            context = await _hydrate(entity_name, session_id, include_full_gnosis)
            return context.to_context_string()
        except Exception as e:
            logger.error(f"Hydration failed for {entity_name}: {e}")
            return f"## Hydration Failed\nEntity: {entity_name}\nError: {e}\n\nProceeding with Soul Kernel only."