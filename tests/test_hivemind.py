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

import yaml
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
mock_mcp_pkg.ClientSession = object  # Needed by mcp_client.py:11
mock_mcp_pkg.ServerSession = object
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
mock_mcp_fastmcp.Context = object  # FastMCP Context type — mock as plain object
mock_mcp_server.fastmcp = mock_mcp_fastmcp

# Mock mcp.types (used by m9_safe decorator for CallToolResult/TextContent)
mock_mcp_types = types.ModuleType("mcp.types")

class MockCallToolResult:
    def __init__(self, content=None, isError=False, **kwargs):
        self.content = content or []
        self.isError = isError

class MockTextContent:
    def __init__(self, type="text", text=""):
        self.type = type
        self.text = text

mock_mcp_types.CallToolResult = MockCallToolResult
mock_mcp_types.TextContent = MockTextContent

# Mock mcp.client and mcp.client.sse (needed by mcp_client.py)
mock_mcp_client = types.ModuleType("mcp.client")
mock_mcp_client_sse = types.ModuleType("mcp.client.sse")
mock_mcp_client_sse.sse_client = AsyncMock()

# Save originals before mocking (Carmack fix: restore after load to prevent
# polluting subsequent test modules that need the real mcp library)
_saved_keys = ["mcp", "mcp.server", "mcp.server.fastmcp", "mcp.types", "mcp.client", "mcp.client.sse"]
_originals = {k: sys.modules.get(k) for k in _saved_keys}

sys.modules["mcp"] = mock_mcp_pkg
sys.modules["mcp.server"] = mock_mcp_server
sys.modules["mcp.server.fastmcp"] = mock_mcp_fastmcp
sys.modules["mcp.types"] = mock_mcp_types
sys.modules["mcp.client"] = mock_mcp_client
sys.modules["mcp.client.sse"] = mock_mcp_client_sse

server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

# Restore original mcp modules so other tests get the real library
for k, orig in _originals.items():
    if orig is not None:
        sys.modules[k] = orig
    else:
        sys.modules.pop(k, None)


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Redirect Hivemind data storage to a temp directory."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Patch all data directory constants used by the server and state.
        from mcp_servers.omega_hub import state
        monkeypatch.setattr(state, "HALL_OF_RECORDS", tmp_path / "HALL_OF_RECORDS")
        monkeypatch.setattr(state, "HANDOFF_BASE", tmp_path / "handoff")
        monkeypatch.setattr(state, "HANDOFF_PENDING", tmp_path / "handoff" / "pending")
        monkeypatch.setattr(state, "HANDOFF_ACTIVE", tmp_path / "handoff" / "active")
        monkeypatch.setattr(state, "HANDOFF_COMPLETED", tmp_path / "handoff" / "completed")
        monkeypatch.setattr(server, "HALL_OF_RECORDS", tmp_path / "HALL_OF_RECORDS")
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
    from mcp_servers.omega_hub import state
    state._hot_store.clear()
    state._awareness.clear()
    yield


@pytest.mark.asyncio
async def test_u001_post_context_basic(temp_data_dir, reset_state):
    """U-001: hivemind_post_context — basic call with required fields."""
    result = await server.hivemind_post_context(
        channel="opencode",
        entity="test-entity",
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
        channel="opencode",
        entity="test-entity",
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
    from mcp_servers.omega_hub import state
    snapshot = state._hot_store.get(sid)
    assert snapshot is not None
    assert snapshot["intent"] == "question"


@pytest.mark.asyncio
async def test_u003_post_context_suggested_model(temp_data_dir, reset_state):
    """U-003: hivemind_post_context — suggested_model field (P6 ship-now #2)."""
    result = await server.hivemind_post_context(
        channel="opencode",
        entity="test-entity",
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
    from mcp_servers.omega_hub import state
    snapshot = state._hot_store.get(sid)
    assert snapshot is not None
    assert snapshot["suggested_model"] == "qwen3-4b-thinking-q4_k_m"


# ── hivemind_get_entity_context tests ──

@pytest.fixture
def entity_context_env(monkeypatch, tmp_path):
    """Set up a temp PROJECT_ROOT with test entity data for entity context tool."""
    from mcp_servers.omega_hub import state
    monkeypatch.setattr(state, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)

    # Create entity base directory
    entity_base = tmp_path / "data" / "entities" / "testentity"
    knowledge_dir = entity_base / "knowledge"
    workspace_dir = entity_base / "workspace"
    sessions_dir = tmp_path / "data" / "sessions"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Create soul.yaml
    soul = {
        "entity": {
            "echo": "testentity",
            "role": "Test Entity",
            "soul_power": 3.5,
            "soul_version": "1.0.0",
            "sessions_completed": 7,
            "last_distillation": "2026-06-10T12:00:00Z",
            "lessons": [
                {
                    "id": "ls-te-001",
                    "date": "2026-06-10",
                    "l1_narrative": "Test lesson about entity context hydration.",
                    "l2_insight": "Context hydration requires multi-source fusion.",
                    "l3_principle": "Knowledge without context is noise.",
                }
            ],
            "embodied_experiences": [
                {"context": "Built the hivemind protocol", "date": "2026-06-09"},
                {"context": "Designed workspace lock tools", "date": "2026-06-08"},
            ],
        }
    }
    with open(entity_base / "soul.yaml", "w") as f:
        yaml.dump(soul, f)

    # Create knowledge files
    with open(knowledge_dir / "README.md", "w") as f:
        f.write("# Test Knowledge Doc\n\n**Purpose**: A sample knowledge document for testing.\n\nThis is the body content.")
    with open(knowledge_dir / "ARCHITECTURE.md", "w") as f:
        f.write("# Architecture Overview\n\nPurpose: System architecture notes.\n\nDetailed architecture content here.")
    with open(knowledge_dir / "notes.txt", "w") as f:
        f.write("Plain text notes file.\n")

    # Create workspace files
    with open(workspace_dir / "current_task.md", "w") as f:
        f.write("# Current Task\n\nWorking on the context hydration tool.")
    (workspace_dir / "subdir").mkdir(exist_ok=True)
    with open(workspace_dir / "subdir" / "draft.md", "w") as f:
        f.write("# Draft\n\nWork in progress.")

    # Create active session file
    session = {
        "date": "20260610",
        "session_id": "ses_20260610_testentity_001",
        "counter": 1,
        "entity": "TESTENTITY",
        "created_at": "2026-06-10T22:00:00+00:00",
    }
    with open(sessions_dir / "testentity.active", "w") as f:
        json.dump(session, f)

    # Mark services as initialized to bypass _require_service() check
    from mcp_servers.omega_hub import state
    monkeypatch.setattr(state, "_init_complete", True)
    monkeypatch.setattr(server, "_init_complete", True)
    
    # Mock registry.get to return a mock entity
    from omega.oracle.entity_registry import Entity, EntityRegistry
    mock_registry = EntityRegistry()
    monkeypatch.setattr(state, "registry", mock_registry)
    monkeypatch.setattr(server, "registry", mock_registry)
    
    mock_entity = Entity(
        name="testentity",
        domains=["testing", "context"],
        model="qwen3-1.7b",
        personality="A test entity",
        slots=["P7"],
        role="Test Context Entity",
        metadata={"pantheon": "test"},
    )
    monkeypatch.setattr(mock_registry, "get", lambda name, _orig=mock_entity: mock_entity if name.lower() == "testentity" else None)
    monkeypatch.setattr(mock_registry, "find_by_name_fragment", lambda name: mock_entity if "test" in name.lower() else None)

    yield tmp_path


@pytest.mark.asyncio
async def test_u004_entity_context_hydrated(entity_context_env):
    """U-004: hivemind_get_entity_context — fully hydrated entity."""
    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    assert payload["entity"]["name"] == "testentity"
    assert payload["entity"]["pillar"] == "P7"
    assert payload["entity"]["role"] == "Test Context Entity"

    assert payload["soul_state"]["soul_power"] == 3.5
    assert payload["soul_state"]["sessions_completed"] == 7
    assert len(payload["soul_state"]["recent_lessons"]) >= 1
    assert payload["soul_state"]["recent_lessons"][0]["l3_principle"] == "Knowledge without context is noise."

    assert payload["knowledge_base"]["file_count"] == 3
    assert payload["knowledge_base"]["total_size_bytes"] > 0

    assert payload["workspace"]["file_count"] == 2

    assert len(payload["active_sessions"]) == 1
    assert "testentity" in payload["active_sessions"][0]["session_id"]

    assert payload["readiness"]["status"] == "HYDRATED"


@pytest.mark.asyncio
async def test_u005_entity_context_missing_soul(entity_context_env):
    """U-005: hivemind_get_entity_context — entity with missing soul.yaml."""
    # Remove the soul.yaml
    soul_path = entity_context_env / "data" / "entities" / "testentity" / "soul.yaml"
    soul_path.unlink()

    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    assert payload["soul_state"]["status"] in ("missing", "error")
    assert payload["readiness"]["status"] == "DORMANT"
    assert "NO_SOUL" in payload["readiness"]["flags"]


@pytest.mark.asyncio
async def test_u006_entity_context_nonexistent(entity_context_env):
    """U-006: hivemind_get_entity_context — nonexistent entity."""
    result = await server.hivemind_get_entity_context(entity_name="nonexistent")
    payload = json.loads(result)

    assert payload["entity"]["name"] == "nonexistent"
    assert payload["knowledge_base"]["file_count"] == 0
    assert payload["workspace"]["file_count"] == 0
    assert payload["active_sessions"] == []


@pytest.mark.asyncio
async def test_u007_entity_context_empty_knowledge_workspace(entity_context_env, monkeypatch):
    """U-007: hivemind_get_entity_context — entity with empty knowledge/workspace dirs."""
    from omega.oracle.entity_registry import Entity
    low_power = Entity(
        name="newentity",
        domains=["new"],
        model="qwen3-0.6b",
        personality="A new entity",
        role="New Entity",
    )
    # Use server.registry if it's already set by fixture, otherwise mock it
    reg = server.registry if server.registry else EntityRegistry()
    if not server.registry:
        monkeypatch.setattr(server, "registry", reg)
    monkeypatch.setattr(reg, "get", lambda name: low_power if name.lower() == "newentity" else None)
    monkeypatch.setattr(reg, "find_by_name_fragment", lambda name: low_power if "new" in name.lower() else None)

    entity_base = entity_context_env / "data" / "entities" / "newentity"
    entity_base.mkdir(parents=True, exist_ok=True)

    soul = {"entity": {"echo": "newentity", "role": "New", "soul_power": 0.5, "sessions_completed": 0}}
    with open(entity_base / "soul.yaml", "w") as f:
        yaml.dump(soul, f)

    (entity_base / "knowledge").mkdir(exist_ok=True)
    (entity_base / "workspace").mkdir(exist_ok=True)

    result = await server.hivemind_get_entity_context(entity_name="newentity")
    payload = json.loads(result)

    assert payload["soul_state"]["soul_power"] == 0.5
    assert payload["knowledge_base"]["file_count"] == 0
    assert payload["workspace"]["file_count"] == 0
    assert payload["active_sessions"] == []


@pytest.mark.asyncio
async def test_u008_entity_context_malformed_soul(entity_context_env):
    """U-008: hivemind_get_entity_context — malformed soul.yaml."""
    soul_path = entity_context_env / "data" / "entities" / "testentity" / "soul.yaml"
    with open(soul_path, "w") as f:
        f.write("{{{{invalid yaml::::\n")

    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    assert payload["soul_state"]["status"] == "malformed"
    assert payload["readiness"]["status"] == "DORMANT"
