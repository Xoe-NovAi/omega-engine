# SPDX-FileCopyrightText: 2026 Arcana Novai
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
    hivemind_post_context,
    hivemind_heartbeat,
    hivemind_get_awareness,
    hivemind_get_continuation,
    hivemind_extended_checkin,
    hivemind_extended_checkout,
    hivemind_get_session,
    hivemind_list_sessions,
    hivemind_submit_handoff,
    hivemind_accept_handoff,
    hivemind_complete_handoff,
    hivemind_reject_handoff,
    hivemind_get_handoff,
    hivemind_handoff_archive,
)

# Tool registry is complete
__all__ = [
    "task_registry",
    "hivemind_post_context",
    "hivemind_heartbeat",
    "hivemind_get_awareness",
    "hivemind_get_continuation",
    "hivemind_extended_checkin",
    "hivemind_extended_checkout",
    "hivemind_get_session",
    "hivemind_list_sessions",
    "hivemind_submit_handoff",
    "hivemind_accept_handoff",
    "hivemind_complete_handoff",
    "hivemind_reject_handoff",
    "hivemind_get_handoff",
    "hivemind_handoff_archive",
]

# OMEGA HUB TOOLS 2026-07-21
