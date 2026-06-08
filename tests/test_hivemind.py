# 🔱 Omega Engine — Hivemind MCP Test Harness
# AP: AP-HIVEMIND-TESTS-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: CI-GATE]
"""
Unit tests for the Hivemind MCP tools.

Per Lilith's Dark Council Synthesis §5 (P10 Validation):
- 20 unit tests — each MCP tool in isolation
- 10 integration tests — 2 simulated agents
- 5 stress tests — 10+ agents, rapid posting

This file implements the first 3 unit tests (U-001..U-003) covering
hivemind_post_context, the foundational tool.
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Ensure MCP server is importable
MCP_SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp_servers" / "omega_hub"
sys.path.insert(0, str(MCP_SERVER_PATH.parent))

# Import the server module — but skip its mcp.tool() decorator side effects
# by mocking the mcp module before import.
import importlib.util
spec = importlib.util.spec_from_file_location("server_under_test", MCP_SERVER_PATH / "server.py")

# Mock the mcp module so the @mcp.tool() decorator is a no-op
# We need to mock mcp.server.fastmcp specifically since that's what's imported
import types
mock_mcp_pkg = types.ModuleType("mcp")
mock_mcp_server = types.ModuleType("mcp.server")
mock_mcp_fastmcp = types.ModuleType("mcp.server.fastmcp")


class MockFastMCP:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator


mock_mcp_fastmcp.FastMCP = MockFastMCP
mock_mcp_server.fastmcp = mock_mcp_fastmcp
sys.modules["mcp"] = mock_mcp_pkg
sys.modules["mcp.server"] = mock_mcp_server
sys.modules["mcp.server.fastmcp"] = mock_mcp_fastmcp

server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Redirect Hivemind data storage to a temp directory."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Patch all data directory constants used by the server.
        monkeypatch.setattr(server, "HALL_OF_RECORDS", tmp_path / "HALL_OF_RECORDS")
        monkeypatch.setattr(server, "HANDOFF_BASE", tmp_path / "handoff")
        monkeypatch.setattr(server, "HANDOFF_PENDING", tmp_path / "handoff" / "pending")
        monkeypatch.setattr(server, "HANDOFF_ACTIVE", tmp_path / "handoff" / "active")
        monkeypatch.setattr(server, "HANDOFF_COMPLETED", tmp_path / "handoff" / "completed")
        # Recreate subdirs
        (tmp_path / "HALL_OF_RECORDS").mkdir(parents=True, exist_ok=True)
        for d in ("pending", "active", "completed"):
            (tmp_path / "handoff" / d).mkdir(parents=True, exist_ok=True)
        yield tmp_path


@pytest.fixture
def reset_state(monkeypatch):
    """Reset the in-memory stores between tests."""
    monkeypatch.setattr(server, "_hot_store", {})
    monkeypatch.setattr(server, "_awareness", {})
    yield


@pytest.mark.asyncio
async def test_u001_post_context_basic(temp_data_dir, reset_state):
    """U-001: hivemind_post_context — basic call with required fields."""
    result = await server.hivemind_post_context(
        cli="test-cli",
        model="minimax-m3-free",
        task_current="Testing post context",
        focus_chain=["step1", "step2"],
        decisions=[{"id": "d-test", "text": "A decision"}],
        continuation="Working on tests",
    )
    payload = json.loads(result)
    assert payload["status"] == "accepted"
    assert "session_id" in payload
    assert payload["session_id"].startswith("ses_")


@pytest.mark.asyncio
async def test_u002_post_context_intent_field(temp_data_dir, reset_state):
    """U-002: hivemind_post_context — intent field captured (P6 ship-now #1)."""
    result = await server.hivemind_post_context(
        cli="test-cli",
        model="minimax-m3-free",
        task_current="Asking a question",
        focus_chain=[],
        decisions=[],
        continuation="",
        intent="question",
    )
    payload = json.loads(result)
    assert payload["status"] == "accepted"
    sid = payload["session_id"]
    # The snapshot should be stored in _hot_store
    snapshot = server._hot_store.get(sid)
    assert snapshot is not None
    assert snapshot["intent"] == "question"


@pytest.mark.asyncio
async def test_u003_post_context_suggested_model(temp_data_dir, reset_state):
    """U-003: hivemind_post_context — suggested_model field (P6 ship-now #2)."""
    result = await server.hivemind_post_context(
        cli="test-cli",
        model="minimax-m3-free",
        task_current="Suggesting a model",
        focus_chain=[],
        decisions=[],
        continuation="",
        suggested_model="qwen3-4b-thinking-q4_k_m",
    )
    payload = json.loads(result)
    assert payload["status"] == "accepted"
    sid = payload["session_id"]
    snapshot = server._hot_store.get(sid)
    assert snapshot is not None
    assert snapshot["suggested_model"] == "qwen3-4b-thinking-q4_k_m"
