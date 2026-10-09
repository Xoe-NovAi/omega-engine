# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Task Registry MCP Tools — Implementation
# AP Token: AP-TASK-REGISTRY-MCP-v1.0.0
# Location: mcp_servers/omega_hub/tools/task_registry.py

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal
import fcntl

from mcp.server.fastmcp import FastMCP

# Get the MCP instance from the server module
from mcp_servers.omega_hub.server import mcp

REGISTRY_PATH = Path(os.environ.get(
    "OMEGA_TASK_REGISTRY",
    str(Path(__file__).parents[3] / "data" / "coordination" / "TASK_REGISTRY.json")
))

def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"version": "1.0", "updated": datetime.now(timezone.utc).isoformat(), "tasks": []}
    with open(REGISTRY_PATH) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def _save_registry(registry: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry["updated"] = datetime.now(timezone.utc).isoformat()
    with open(REGISTRY_PATH, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(registry, f, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

@mcp.tool()
async def task_registry_register(
    task_id: str,
    subagent_type: str,
    launched_by: str,
    channel: str,
    entity: str,
    description: str,
    tags: list[str] = None
) -> dict:
    """
    Register a new subagent task session in the Task Registry.
    
    MUST be called IMMEDIATELY after every task() launch.
    
    Args:
        task_id: Unique task identifier (format: domain-action-date-seq)
        subagent_type: Type of subagent (roc_racoon, researcher, kali, etc.)
        launched_by: Entity that launched the task
        channel: Execution channel (opencode, cline, gemini-cli)
        entity: Launching entity persona
        description: One-line task description
        tags: Optional tags for categorization
    
    Returns:
        {"status": "registered", "task_id": "...", "created_at": "..."}
    """
    registry = _load_registry()
    
    # Check for duplicate
    if any(t["task_id"] == task_id for t in registry["tasks"]):
        return {"status": "exists", "task_id": task_id}
    
    task = {
        "task_id": task_id,
        "subagent_type": subagent_type,
        "launched_by": launched_by,
        "channel": channel,
        "entity": entity,
        "description": description,
        "status": "in_progress",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_checkpoint": datetime.now(timezone.utc).isoformat(),
        "resumption_count": 0,
        "context_verified": False,
        "tags": tags or []
    }
    
    registry["tasks"].append(task)
    _save_registry(registry)
    return {"status": "registered", "task_id": task_id, "created_at": task["created_at"]}

@mcp.tool()
async def task_registry_query(
    subagent_type: str = None,
    launched_by: str = None,
    channel: str = None,
    entity: str = None,
    status: Literal['backlog', 'ready', 'in_progress', 'blocked', 'completed', 'superseded', 'failed'] = None,
    tags: list[str] = None,
    limit: int = 50
) -> dict:
    """
    Discover existing subagent task sessions.
    
    Use BEFORE launching to check for resumable tasks.
    Use to find stalled tasks from other agents.
    
    Args:
        subagent_type: Filter by subagent type
        launched_by: Filter by launching entity
        channel: Filter by execution channel
        entity: Filter by launching entity persona
        status: Filter by status (backlog|ready|in_progress|blocked|completed|superseded|failed)
        tags: Filter by tags (AND logic)
        limit: Maximum results
    
    Returns:
        {"tasks": [...], "count": N, "filters_applied": {...}}
    """
    registry = _load_registry()
    tasks = registry["tasks"]
    
    # Apply filters
    if subagent_type:
        tasks = [t for t in tasks if t["subagent_type"] == subagent_type]
    if launched_by:
        tasks = [t for t in tasks if t["launched_by"] == launched_by]
    if channel:
        tasks = [t for t in tasks if t["channel"] == channel]
    if entity:
        tasks = [t for t in tasks if t["entity"] == entity]
    if status != "all":
        tasks = [t for t in tasks if t["status"] == status]
    if tags:
        tasks = [t for t in tasks if all(tag in t["tags"] for tag in tags)]
    
    # Sort by last_checkpoint descending
    tasks.sort(key=lambda t: t["last_checkpoint"], reverse=True)
    
    return {
        "tasks": tasks[:limit],
        "count": len(tasks),
        "filters_applied": {
            "subagent_type": subagent_type,
            "launched_by": launched_by,
            "channel": channel,
            "entity": entity,
            "status": status,
            "tags": tags
        }
    }

@mcp.tool()
async def task_registry_update(
    task_id: str,
    status: Literal['backlog', 'ready', 'in_progress', 'blocked', 'completed', 'superseded', 'failed'] = None,
    last_checkpoint: str = None,  # ISO timestamp
    resumption_count: int = None,
    context_verified: bool = None,
    tags: list[str] = None        # Add tags (not replace)
) -> dict:
    """
    Update task session state after resumption, checkpoint, or completion.
    
    MUST be called after:
    - Successful resumption (increment resumption_count, set context_verified)
    - Checkpoint during long-running task
    - Completion (status=completed)
    - Failure (status=blocked or superseded)
    
    Args:
        task_id: Task to update
        status: New status
        last_checkpoint: Current timestamp
        resumption_count: Increment on each resume
        context_verified: True after "Tell me what you know" verification
        tags: Additional tags to add
    
    Returns:
        {"status": "updated", "task_id": "...", "updated_fields": [...]}
    """
    registry = _load_registry()
    
    for i, task in enumerate(registry["tasks"]):
        if task["task_id"] == task_id:
            updated = []
            if status:
                task["status"] = status
                updated.append("status")
            if last_checkpoint:
                task["last_checkpoint"] = last_checkpoint
                updated.append("last_checkpoint")
            if resumption_count is not None:
                task["resumption_count"] = resumption_count
                updated.append("resumption_count")
            if context_verified is not None:
                task["context_verified"] = context_verified
                updated.append("context_verified")
            if tags:
                for tag in tags:
                    if tag not in task["tags"]:
                        task["tags"].append(tag)
                updated.append("tags")
            
            _save_registry(registry)
            return {"status": "updated", "task_id": task_id, "updated_fields": updated}
    
    return {"error": "not_found", "task_id": task_id}

@mcp.tool()
async def task_registry_get(
    task_id: str
) -> dict:
    """
    Get full details for a specific task_id.
    
    Use to inspect before resuming.
    
    Args:
        task_id: Task to retrieve
    
    Returns:
        Full task object or {"error": "not_found"}
    """
    registry = _load_registry()
    for task in registry["tasks"]:
        if task["task_id"] == task_id:
            return task
    return {"error": "not_found", "task_id": task_id}