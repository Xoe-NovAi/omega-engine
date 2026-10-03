# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Omega Hub Tools — MCP Tool Registration
# AP Token: AP-OMEGA-HUB-TOOLS-v1.0.0

# This module registers all MCP tools with the FastMCP instance via side-effect import.
from mcp_servers.omega_hub.hub_tools.task_registry import (
    task_registry_register,
    task_registry_query,
    task_registry_update,
    task_registry_get,
)
from mcp_servers.omega_hub.hub_tools.tools import (
    hivemind_awareness,
    hivemind_handoff,
    hivemind_lock,
    library_inbox,
    oracle_debug,
    github,
    library_web_search,
    library_fts_search,
    library_get_document,
    library_domains,
    library_recent,
    library_stats,
    library_ingest_pending,
)
from mcp_servers.omega_hub.hub_tools.federation import (
    omega_federation_status,
    omega_federation_diagnose,
)

# Tool registry is complete
__all__ = [
    "task_registry",
    "hivemind_awareness",
    "hivemind_handoff",
    "hivemind_lock",
    "library_inbox",
    "oracle_debug",
    "github",
    "library_web_search",
    "library_fts_search",
    "library_get_document",
    "library_domains",
    "library_recent",
    "library_stats",
    "library_ingest_pending",
    "omega_federation_status",
    "omega_federation_diagnose",
]

# OMEGA HUB TOOLS 2026-07-21

