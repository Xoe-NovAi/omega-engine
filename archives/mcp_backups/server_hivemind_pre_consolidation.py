"""Omega Hivemind MCP Server — Cross-CLI awareness for the Omega Engine.

AP Token: AP-OMEGA-HIVEMIND-MCP-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: HIVEMIND-MCP]

Provides shared state, session context, and continuation protocol
across Cline, OpenCode, Gemini, and Copilot CLIs.

Storage: ~/omega/knowledge/HALL_OF_RECORDS/<cli>/<session_id>.json

Usage:
    cd ~/omega && python mcp/omega-hivemind/server.py
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent.parent.parent
HALL_OF_RECORDS = BASE_DIR / "knowledge" / "HALL_OF_RECORDS"
HALL_OF_RECORDS.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("Omega Hivemind")

_hot_store: Dict[str, Dict[str, Any]] = {}
_awareness: Dict[str, Dict[str, Any]] = {}


def _cold_path(cli: str, session_id: str) -> Path:
    safe_cli = cli.replace(" ", "_").replace("/", "_")
    safe_sid = session_id.replace("/", "_").replace(":", "_")
    return HALL_OF_RECORDS / safe_cli / f"{safe_sid}.json"


def _latest_path() -> Path:
    return HALL_OF_RECORDS / "latest.yaml"


@mcp.tool()
async def post_context(
    cli: str,
    model: str,
    task_current: str,
    focus_chain: List[str],
    decisions: List[Dict[str, str]],
    continuation: str,
    session_id: Optional[str] = None,
) -> str:
    """Submit a context snapshot from any CLI to the hivemind.

    Args:
        cli: CLI name (cline, opencode, gemini, copilot)
        model: Model name
        task_current: Description of the current task
        focus_chain: Ordered list of focus/task items
        decisions: List of {'what': ..., 'why': ..., 'by': cli} dicts
        continuation: Instructions for the next agent/CLI
        session_id: Optional session identifier
    """
    sid = session_id or f"ses_{uuid.uuid4().hex[:12]}"
    snapshot = {
        "session_id": sid,
        "cli": cli,
        "model": model,
        "task_current": task_current,
        "focus_chain": focus_chain,
        "decisions": decisions,
        "continuation": continuation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    _hot_store[sid] = snapshot
    _awareness[cli] = snapshot

    cold = _cold_path(cli, sid)
    cold.parent.mkdir(parents=True, exist_ok=True)
    async with await anyio.open_file(str(cold), "w") as f:
        await f.write(json.dumps(snapshot, indent=2))

    latest = _latest_path()
    async with await anyio.open_file(str(latest), "w") as f:
        await f.write(f"latest_session: {sid}\nupdated: {snapshot['timestamp']}\n")

    return json.dumps({"status": "accepted", "session_id": sid, "timestamp": snapshot["timestamp"]})


@mcp.tool()
async def get_awareness() -> str:
    """Get real-time awareness of all active CLI agents."""
    awareness_list = []
    for cli, snap in _awareness.items():
        awareness_list.append({
            "cli": cli,
            "model": snap.get("model"),
            "task_current": snap.get("task_current", ""),
            "last_seen": snap.get("timestamp", ""),
        })
    return json.dumps(awareness_list, indent=2)


@mcp.tool()
async def get_continuation(cli: str) -> str:
    """Get the latest continuation note for a specific CLI.

    Args:
        cli: CLI name (cline, opencode, gemini, copilot)
    """
    snap = _awareness.get(cli)
    if snap:
        return snap.get("continuation", "No continuation note found.")
    return f"No awareness data for CLI '{cli}'."


@mcp.tool()
async def get_session(session_id: str) -> str:
    """Retrieve a session snapshot by ID.

    Args:
        session_id: The session identifier to retrieve
    """
    if session_id in _hot_store:
        return json.dumps(_hot_store[session_id], indent=2)
    for cli_dir in HALL_OF_RECORDS.iterdir():
        if cli_dir.is_dir():
            sess_file = cli_dir / f"{session_id}.json"
            if sess_file.exists():
                async with await anyio.open_file(str(sess_file)) as f:
                    content = await f.read()
                return content
    return json.dumps({"error": f"Session '{session_id}' not found"})


@mcp.tool()
async def list_sessions(cli: Optional[str] = None, limit: int = 10) -> str:
    """List recent session snapshots.

    Args:
        cli: Optional filter by CLI name
        limit: Maximum number of sessions to return
    """
    sessions = []
    if cli:
        cli_dir = HALL_OF_RECORDS / cli
        if cli_dir.exists():
            for f in sorted(cli_dir.glob("*.json"), reverse=True)[:limit]:
                sessions.append(f.stem)
    else:
        for cli_dir in HALL_OF_RECORDS.iterdir():
            if cli_dir.is_dir():
                for f in sorted(cli_dir.glob("*.json"), reverse=True)[:limit]:
                    sessions.append({"cli": cli_dir.name, "session_id": f.stem})
    return json.dumps(sessions, indent=2)


from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
