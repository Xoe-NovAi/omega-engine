# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M34 Active Subagents — MCP Tools
# ⬡ OMEGA ⬡ LILITH ⬡ M34 ⬡ MCP-TOOLS
# AP: AP-M34-MCP-TOOLS-v1.0.0
#
# 4 MCP tools for the M34 (Multi-Agent Co-Interruption & Resumption Accounting) mandate.
# Integrates with omega-hub FastMCP server.
#
# Per Meta-Review §5.3 corrections:
# - 4 tools (not 3) — added m34_update_subagent_status
# - Uses real MCP tool name pattern (omega-hub_hivemind_post_context)
# - Single-writer watchdog via m34_update_subagent_status
#
# Pattern source: mcp_servers/omega_hub/hub_tools/task_registry.py

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional, List

from mcp.server.fastmcp import FastMCP

# Get the MCP instance from the server module
from mcp_servers.omega_hub.server import mcp

# Add src to path so we can import the registry
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Direct file-based import to avoid omega.__init__ chain
import importlib.util
_REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "src" / "omega" / "oracle" / "m34_registry.py"
spec = importlib.util.spec_from_file_location("omega.oracle.m34_registry", str(_REGISTRY_PATH))
assert spec is not None and spec.loader is not None, "Failed to load m34_registry spec"
_m34 = importlib.util.module_from_spec(spec)
sys.modules["omega.oracle.m34_registry"] = _m34
spec.loader.exec_module(_m34)

M34Registry = _m34.M34Registry
ActiveSubagent = _m34.ActiveSubagent
SessionStatus = _m34.SessionStatus
Checkpoint = _m34.Checkpoint

REGISTRY_PATH = Path(os.environ.get(
    "OMEGA_M34_REGISTRY",
    str(Path(__file__).parents[3] / "data" / "coordination" / "ACTIVE_SUBAGENTS.json")
))


def _get_registry() -> M34Registry:
    """Get a registry instance with the default path."""
    return M34Registry(registry_path=REGISTRY_PATH)


@mcp.tool()
async def m34_register_subagent(
    session_id: str,
    parent_session_id: Optional[str],
    parent_task_id: Optional[str],
    subagent_type: Literal["EIS", "NES", "SPT"],
    agent: str,
    model: str,
    channel: str,
    entity: str,
    task_brief: str,
    dispatch_packet_id: Optional[str] = None,
    task_type: Optional[str] = None,
    expected_deliverable: Optional[str] = None,
    write_tool_required: bool = False,
    cross_validator_agent: Optional[str] = None,
    plugin_load_path: Optional[Literal["file://", "npm", "pip", "unknown"]] = None,
    git_worktree_root: Optional[str] = None,
) -> dict:
    """Register a newly-spawned subagent in ACTIVE_SUBAGENTS.json.

    Called by subagent_dispatcher.py:dispatch() after task() returns the session_id.
    This is the ONLY way new subagent sessions enter the registry (M27).

    Per Meta-Review corrections, this tool accepts 7 additional fields that were
    missing from the original M34 spec:
    - expected_deliverable (Jem §1.2.1)
    - write_tool_required (M33 enforcement)
    - cross_validator_agent (M33 defense — separate verifier agent)
    - plugin_load_path (Researcher dual-load detection)
    - git_worktree_root (Jem self-correction)
    - dispatch_packet_id (for traceability)
    - task_type (for cohort grouping)

    Returns:
        {"status": "registered", "session_id": "...", "created_at": "..."}
    """
    registry = _get_registry()
    entry = ActiveSubagent(
        session_id=session_id,
        parent_session_id=parent_session_id,
        parent_task_id=parent_task_id,
        subagent_type=subagent_type,
        agent=agent,
        model=model,
        channel=channel,
        entity=entity,
        task_brief=task_brief,
        dispatch_packet_id=dispatch_packet_id,
        task_type=task_type,
        expected_deliverable=expected_deliverable,
        write_tool_required=write_tool_required,
        cross_validator_agent=cross_validator_agent,
        plugin_load_path=plugin_load_path,
        git_worktree_root=git_worktree_root,
    )
    stored = registry.register(entry)
    return {
        "status": "registered",
        "session_id": session_id,
        "created_at": stored.spawn_time,
        "registry_path": str(REGISTRY_PATH),
    }


@mcp.tool()
async def m34_list_active_subagents(
    status_filter: Optional[List[str]] = None,
    parent_session_id: Optional[str] = None,
    agent: Optional[str] = None,
    entity: Optional[str] = None,
    include_orphans: bool = True,
    only_interrupted: bool = False,
) -> dict:
    """List active subagents with optional filters.

    Used by orchestrator_session_start() to detect interrupted/orphaned sessions.

    If only_interrupted=True, returns only sessions in interruptable states:
    INTERRUPTED_EXTERNALLY, INTERRUPTED_MODEL_SWITCH, INTERRUPTED_CRASH, ORPHANED.
    This is the canonical query for resumption prompts.

    Returns:
        {"sessions": [...], "count": N, "filters_applied": {...}}
    """
    registry = _get_registry()
    if only_interrupted:
        results = registry.list_interrupted(parent_session_id=parent_session_id)
    else:
        results = registry.list_sessions(
            status_filter=status_filter,
            parent_session_id=parent_session_id,
            agent=agent,
            entity=entity,
            include_orphans=include_orphans,
        )
    return {
        "sessions": results,
        "count": len(results),
        "filters_applied": {
            "status_filter": status_filter,
            "parent_session_id": parent_session_id,
            "agent": agent,
            "entity": entity,
            "include_orphans": include_orphans,
            "only_interrupted": only_interrupted,
        },
    }


@mcp.tool()
async def m34_apply_user_decision(
    session_id: str,
    decision: Literal["RESUME", "ABANDON", "DEFER"],
    decided_by: str,
    note: Optional[str] = None,
) -> dict:
    """Apply user's resume/abandon/defer decision to a session entry.

    Called by orchestrator_session_start() after presenting interrupted sessions
    to the user and receiving their decision.

    RESUME: status=ALIVE, increment resumption_count, update last_resumed_at
    ABANDON: status=DEAD_LETTER, mark terminal (reaped after retention_days)
    DEFER: leave status unchanged, add note to checkpoint.last_action

    Returns:
        {"status": "applied", "session_id": "...", "new_status": "..."}
    """
    registry = _get_registry()
    result = registry.apply_user_decision(
        session_id=session_id,
        decision=decision,
        decided_by=decided_by,
        note=note,
    )
    if result is None:
        return {"error": "not_found", "session_id": session_id}
    return {
        "status": "applied",
        "session_id": session_id,
        "decision": decision,
        "new_status": result["status"],
        "resumption_count": result.get("resumption_count", 0),
    }


@mcp.tool()
async def m34_update_subagent_status(
    session_id: str,
    new_status: Literal["ALIVE", "INTERRUPTED_EXTERNALLY", "INTERRUPTED_MODEL_SWITCH",
                        "INTERRUPTED_CRASH", "COMPLETED", "FAILED", "DEAD_LETTER", "ORPHANED"],
    interruption_reason: Optional[Literal["esc_x2", "model_switch", "timeout",
                                           "architect_cancel", "crash", "unknown"]] = None,
    last_action: Optional[str] = None,
    tokens_used: Optional[int] = None,
    progress_pct: Optional[int] = None,
    resumption_count_increment: bool = False,
) -> dict:
    """Update an existing subagent's status.

    This is the SINGLE-WRITER MCP tool for status changes (per Meta-Review §1.4
    watchdog race fix). Called by:
    - Interruption watcher on SIGINT (status=INTERRUPTED_EXTERNALLY)
    - Heartbeat loop (status=ALIVE, updated last_heartbeat)
    - Subagent completion reports (status=COMPLETED/FAILED)
    - Pruning loop (status=ORPHANED for stale heartbeats)
    - User decisions (handled by m34_apply_user_decision)

    If new_status is an INTERRUPTED_* state, interruption_reason MUST be provided.

    Returns:
        {"status": "updated", "session_id": "...", "old_status": "...", "new_status": "..."}
    """
    registry = _get_registry()
    # Build checkpoint if any checkpoint fields provided
    checkpoint = None
    if last_action is not None or tokens_used is not None or progress_pct is not None:
        checkpoint = Checkpoint(
            ts=datetime.now(timezone.utc).isoformat(),
            tokens_used=tokens_used or 0,
            last_action=last_action or "",
            progress_pct=progress_pct,
        )

    result = registry.update_status(
        session_id=session_id,
        new_status=SessionStatus(new_status),
        interruption_reason=interruption_reason,
        checkpoint=checkpoint,
        resumption_count_increment=resumption_count_increment,
    )
    if result is None:
        return {"error": "not_found", "session_id": session_id}
    return {
        "status": "updated",
        "session_id": session_id,
        "new_status": result["status"],
        "interruption_reason": result.get("interruption_reason"),
        "resumption_count": result.get("resumption_count", 0),
        "last_heartbeat": result.get("last_heartbeat"),
    }


@mcp.tool()
async def m34_get_subagent(session_id: str) -> dict:
    """Get full details for a specific subagent session.

    Returns the full ActiveSubagent object, or error if not found.
    """
    registry = _get_registry()
    result = registry.get(session_id)
    if result is None:
        return {"error": "not_found", "session_id": session_id}
    return result


@mcp.tool()
async def m34_heartbeat(
    session_id: str,
    last_action: Optional[str] = None,
) -> dict:
    """Update last_heartbeat for an active session.

    Called by:
    - Pruning loop (every 60s) to confirm session is still alive
    - Subagent self-reporting via Hivemind

    Returns:
        {"status": "heartbeat", "session_id": "...", "last_heartbeat": "..."}
    """
    registry = _get_registry()
    result = registry.heartbeat(session_id, last_action or "")
    if result is None:
        return {"error": "not_found", "session_id": session_id}
    return {
        "status": "heartbeat",
        "session_id": session_id,
        "last_heartbeat": result.get("last_heartbeat"),
    }


@mcp.tool()
async def m34_prune_orphans(alive_ttl_seconds: int = 1200) -> dict:
    """Mark ALIVE sessions with stale heartbeats (>2× alive_ttl) as ORPHANED.

    Per the pruning policy. Called by scripts/m34_prune.py (cron @ 60s).

    Returns:
        {"status": "pruned", "orphans_marked": N, "alive_ttl_seconds": ...}
    """
    registry = _get_registry()
    marked = registry.prune(alive_ttl_seconds=alive_ttl_seconds)
    return {
        "status": "pruned",
        "orphans_marked": marked,
        "alive_ttl_seconds": alive_ttl_seconds,
    }


@mcp.tool()
async def m34_reap_dead_letters(retention_days: int = 30) -> dict:
    """Remove DEAD_LETTER sessions older than retention_days.

    Called by scripts/m34_prune.py (cron @ 24h). Default 30-day retention.

    Returns:
        {"status": "reaped", "entries_removed": N, "retention_days": ...}
    """
    registry = _get_registry()
    removed = registry.reap_dead_letters(retention_days=retention_days)
    return {
        "status": "reaped",
        "entries_removed": removed,
        "retention_days": retention_days,
    }
