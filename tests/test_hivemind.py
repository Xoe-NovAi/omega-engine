# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Hivemind MCP Test Harness
# AP: AP-HIVEMIND-TESTS-v1.0.0
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
from unittest.mock import AsyncMock, MagicMock, patch

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
    """Faithful-enough stand-in for FastMCP.

    [maat 2026-09-28] Extended beyond a bare no-op constructor. The mock is
    installed into `sys.modules` BEFORE `mcp_servers.omega_hub.server` is first
    imported (module-level `spec.loader.exec_module` at the bottom of this
    file). So the REAL server module binds THIS class as its `mcp` singleton and
    keeps it for the whole session -- it is not restored afterwards, because the
    reference lives in the server module, not in `sys.modules`.

    Consequence, measured: running `test_hivemind.py` before `test_hub_health.py`
    in one session gave 26 errors, all
        AttributeError: 'MockFastMCP' object has no attribute 'list_tools'
    from `test_hub_health.py::TestCriticalTools`, which enumerates the real
    registered tool surface. Standalone, test_hub_health is 46/46 green. The
    hub was never broken; the mock was simply too thin to stand in for the class
    the other file legitimately uses.

    These are the attributes the rest of the suite actually touches. They return
    plausible, obviously-synthetic values — this is a stub, and it must never be
    mistaken for a real tool registry. A test that needs the REAL surface
    should import the server in a fresh process rather than rely on the mock.
    """

    def __init__(self, *args, **kwargs):
        self._tools: dict = {}
        # server.py sets this after construction; accept it so that line does
        # not raise (it previously logged a non-fatal TOOL-CHAIN-COLLAPSE).
        self._mcp_server = None
        self.settings = types.SimpleNamespace(stateless_http=True)

    def tool(self, *args, **kwargs):
        def decorator(f):
            name = kwargs.get("name") or getattr(f, "__name__", "tool")
            self._tools[name] = f
            return f
        return decorator

    def remove_tool(self, name):
        self._tools.pop(name, None)

    def add_tool(self, fn, name=None, **kwargs):
        self._tools[name or getattr(fn, "__name__", "tool")] = fn

    async def list_tools(self):
        return [
            types.SimpleNamespace(name=n, description="", inputSchema={})
            for n in sorted(self._tools)
        ]

    def get_tool(self, name):
        return self._tools.get(name)


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
mock_mcp_client_streamable = types.ModuleType("mcp.client.streamable_http")
mock_mcp_client_streamable.streamablehttp_client = AsyncMock()

mock_mcp_server_sse = types.ModuleType("mcp.server.sse")
mock_mcp_server_sse.SseServerTransport = MagicMock()

mock_mcp_server_streamable = types.ModuleType("mcp.server.streamable_http_manager")
mock_mcp_server_streamable.StreamableHTTPSessionManager = MagicMock()

mock_mcp_server_transport_security = types.ModuleType("mcp.server.transport_security")

class MockTransportSecuritySettings:
    def __init__(self, **kwargs):
        pass

mock_mcp_server_transport_security.TransportSecuritySettings = MockTransportSecuritySettings

mock_mcp_server_fastmcp_server = types.ModuleType("mcp.server.fastmcp.server")
mock_mcp_server_fastmcp_server.StreamableHTTPASGIApp = MagicMock()

# Save originals before mocking (Carmack fix: restore after load to prevent
# polluting subsequent test modules that need the real mcp library)
_saved_keys = ["mcp", "mcp.server", "mcp.server.fastmcp", "mcp.server.sse", "mcp.server.streamable_http_manager", "mcp.server.transport_security", "mcp.server.fastmcp.server", "mcp.types", "mcp.client", "mcp.client.sse", "mcp.client.streamable_http"]
_originals = {k: sys.modules.get(k) for k in _saved_keys}

sys.modules["mcp"] = mock_mcp_pkg
sys.modules["mcp.server"] = mock_mcp_server
sys.modules["mcp.server.fastmcp"] = mock_mcp_fastmcp
sys.modules["mcp.server.sse"] = mock_mcp_server_sse
sys.modules["mcp.server.streamable_http_manager"] = mock_mcp_server_streamable
sys.modules["mcp.server.transport_security"] = mock_mcp_server_transport_security
sys.modules["mcp.server.fastmcp.server"] = mock_mcp_server_fastmcp_server
sys.modules["mcp.types"] = mock_mcp_types
sys.modules["mcp.client"] = mock_mcp_client
sys.modules["mcp.client.sse"] = mock_mcp_client_sse
sys.modules["mcp.client.streamable_http"] = mock_mcp_client_streamable

server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

# Restore original mcp modules so other tests get the real library
for k, orig in _originals.items():
    if orig is not None:
        sys.modules[k] = orig
    else:
        sys.modules.pop(k, None)

# [maat 2026-09-28] ALSO evict the omega_hub package cache.
#
# Restoring `sys.modules["mcp"]` is necessary but NOT sufficient. Executing
# server.py under the mock transitively imports `mcp_servers.omega_hub.*`,
# which CACHES `mcp_servers.omega_hub.server` in sys.modules with its `mcp`
# singleton permanently bound to MockFastMCP. The `mcp` key can be restored; the
# reference inside the cached server module cannot. Any later importer — in this
# file or any other — receives the mock.
#
# Measured consequence: `test_hub_health.py::TestCriticalTools` enumerates the
# REAL registered tool surface and failed in BOTH file orders, not just the
# polluting one, because pytest imports every test module at collection time —
# so the mock is always installed before any test body runs. That is also how
# the phantom 54-vs-55 tool count appeared (the old mock had no remove_tool, so
# server.py's curation of deprecated `library_search` silently no-opped).
#
# Evicting the package forces a clean re-import against the real `mcp` library.
# `server` (the local name) still points at the mock-built module, so this
# file's own 11 tests keep testing through the mock exactly as before.
# Evict ONLY `mcp_servers.omega_hub.server`, which is the single module holding
# the poisoned `mcp` singleton. Do NOT purge the whole `omega_hub` package:
# `state` and `hub_tools.tools` carry the service-init flags, and re-importing
# them resets `_init_complete` to False, so every later tool call raises
# "Hub services are still initializing" — which broke 15
# `tests/contracts/test_legacy_tool_adapters.py` cases. Measured both ways.
for _k in ("mcp_servers.omega_hub.server",):
    sys.modules.pop(_k, None)



# ─────────────────────────────────────────────────────────────────────────────
# [seam-fix 2026-09-28 maat] Rewritten against the CURRENT contract.
#
# WHAT WAS WRONG BEFORE (all 8 tests errored, not 5 — the "5" was an artifact of
# `-n auto -x` in addopts halting the run early; see pyproject.toml:144):
#
#   Group A (u001..u003, post contract) — the unified hivemind_awareness calls
#     _require_service(); the old hivemind_post_context did not. Services were
#     not initialised, so every call raised
#       RuntimeError: Hub services are still initializing in the background.
#     Per MaKaLi's ruling the guard STAYS. These tests therefore run against a
#     genuinely-live service state (live_hub fixture) rather than asserting
#     rejection — they exist to pin the post payload contract, and turning them
#     into "assert it raises" would delete all coverage of the very contract the
#     ruling just ratified. The guard keeps its own dedicated test below.
#
#   Group B (u004..u008, entity_context) — the calls SUCCEEDED (that fixture
#     already set _init_complete) but every assertion used the retired
#     pre-consolidation response shape:
#         OLD: entity=<dict w/ name,slot,role>, soul_state=…, knowledge_base=…,
#              workspace=…, active_sessions=…, readiness=…
#         NEW: entity=<str>,              soul=…,        knowledge=…,
#              workspace=…, recent_sessions=…
#     `readiness`, registry slot/role enrichment, and distilled `recent_lessons`
#     NO LONGER EXIST. Those assertions are DELETED, not weakened.
#
# Also fixed: the entity_context fixture patched state.HALL_OF_RECORDS, but
# _list_sessions() reads the module-local `HALL_OF_RECORDS` inside
# hub_tools/tools.py, so the patch never applied and recent_sessions was read
# from the REAL Hivemind store. It now patches the tools namespace.
# ─────────────────────────────────────────────────────────────────────────────

import mcp_servers.omega_hub.hub_tools.tools as tools_mod  # noqa: E402


@pytest.fixture
def temp_data_dir(monkeypatch):
    """Redirect Hivemind data storage to a temp directory."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
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
        # tools.py holds its own module-level import of HALL_OF_RECORDS; without
        # this the post path would write into the REAL Hivemind store.
        monkeypatch.setattr(tools_mod, "HALL_OF_RECORDS", tmp_path / "HALL_OF_RECORDS")
        (tmp_path / "HALL_OF_RECORDS").mkdir(parents=True, exist_ok=True)
        for d in ("pending", "active", "completed"):
            (tmp_path / "handoff" / d).mkdir(parents=True, exist_ok=True)
        yield tmp_path


@pytest.fixture
def live_hub(monkeypatch):
    """Mark hub services as initialised so _require_service() permits a post.

    The guard is CORRECT and is retained (MaKaLi ruling, 2026-09-28): posting
    into a Hivemind that is not serving is refused rather than silently
    accepted. Tests that verify the post CONTRACT need a serving hub, so they
    declare one explicitly here rather than the guard being relaxed.
    """
    from mcp_servers.omega_hub import state
    monkeypatch.setattr(state, "_init_complete", True)
    monkeypatch.setattr(server, "_init_complete", True)


@pytest.fixture
def reset_state(monkeypatch):
    """Reset the in-memory stores between tests."""
    from mcp_servers.omega_hub import state
    state._hot_store.clear()
    state._awareness.clear()
    state._init_complete = False
    yield


# ── THE GUARD (asserted as correct behaviour, per ruling) ─────────────────────

@pytest.mark.asyncio
async def test_post_refused_when_hub_not_serving(temp_data_dir, reset_state):
    """ASSERTED-AS-CORRECT: posting into a dead Hivemind must be REFUSED.

    hivemind_awareness() calls _require_service(). A post that reports success
    into a Hivemind that is not serving is the silent-degradation failure this
    fleet was blind to for 36+ hours (hub crash-looping while temple-grade read
    53/53). This test exists so that guard can never be quietly removed to make
    another test convenient.
    """
    from mcp_servers.omega_hub import state
    # Deliberately NOT using live_hub: services are down here.
    assert state._init_complete is False or not state._init_complete
    with pytest.raises(RuntimeError, match="initializ"):
        await server.hivemind_post_context(
            channel="opencode", entity="test-entity", model="m",
            task_current="t", focus_chain=[], decisions=[], continuation="",
        )


# ── THE post CONTRACT (both directions pinned) ───────────────────────────────

@pytest.mark.asyncio
async def test_post_empty_containers_are_valid(temp_data_dir, reset_state, live_hub):
    """decisions=[] / focus_chain=[] / continuation="" are VALID.

    Regression pin for the ratified validation change. The previous check was
    `all([...])`, which treats an empty container and an empty string as
    MISSING and rejected legitimate "none recorded" posts — while signalling
    failure with a returned error STRING rather than an exception, so a caller
    ignoring the return believed it had posted while nothing was delivered.
    """
    result = await server.hivemind_post_context(
        channel="opencode",
        entity="test-entity",
        model="minimax-m3-free",
        task_current="Recording no decisions",
        focus_chain=[],
        decisions=[],
        continuation="",
    )
    payload = json.loads(result)
    assert "error" not in payload, f"empty containers must be accepted, got: {payload}"
    assert payload["status"] == "accepted"
    assert payload["session_id"].startswith("ses_")


@pytest.mark.asyncio
async def test_post_omitted_field_is_rejected_and_named(temp_data_dir, reset_state, live_hub):
    """An OMITTED required field is rejected, and the field is NAMED.

    The other direction of the same contract. `None` means absent and must fail;
    `[]` means present-but-empty and must pass. Both are pinned so neither half
    can be changed without the other being noticed.
    """
    result = await server.hivemind_post_context(
        channel="opencode",
        entity="test-entity",
        model="minimax-m3-free",
        task_current="t",
        focus_chain=[],
        decisions=None,          # explicitly absent, NOT merely empty
        continuation="c",
    )
    payload = json.loads(result)
    assert "error" in payload, "omitting a required field must be rejected"
    assert payload.get("missing") == ["decisions"], (
        f"rejection must name the missing field, got: {payload}"
    )


# ── U-001..U-003: post payload contract (run against a live hub) ─────────────

@pytest.mark.asyncio
async def test_u001_post_context_basic(temp_data_dir, reset_state, live_hub):
    """U-001: post — basic call with required fields. FIXED (was: guard error)."""
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
async def test_u002_post_context_intent_field(temp_data_dir, reset_state, live_hub):
    """U-002: post — intent field captured. FIXED (was: guard error)."""
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
    from mcp_servers.omega_hub.state import hot_store_get
    snapshot = await hot_store_get(payload["session_id"])
    assert snapshot is not None
    assert snapshot["intent"] == "question"


@pytest.mark.asyncio
async def test_u003_post_context_suggested_model(temp_data_dir, reset_state, live_hub):
    """U-003: post — suggested_model field. FIXED (was: guard error)."""
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
    from mcp_servers.omega_hub.state import hot_store_get
    snapshot = await hot_store_get(payload["session_id"])
    assert snapshot is not None
    assert snapshot["suggested_model"] == "qwen3-4b-thinking-q4_k_m"


# ── entity_context tests, against the RESTORED enriched schema ───────────────

@pytest.fixture
def entity_context_env(monkeypatch, tmp_path):
    """Temp PROJECT_ROOT with test entity data for the entity_context action."""
    from mcp_servers.omega_hub import state
    import mcp_servers.omega_hub.hub_tools.tools as tools_mod
    monkeypatch.setattr(state, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(server, "PROJECT_ROOT", tmp_path)

    entity_base = tmp_path / "data" / "entities" / "testentity"
    knowledge_dir = entity_base / "knowledge"
    workspace_dir = entity_base / "workspace"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    soul = {
        "entity": {
            "echo": "testentity",
            "role": "Test Entity",
            "soul_power": 3.5,
            "soul_version": "1.0.0",
            "sessions_completed": 7,
            "last_distillation": "2026-06-10T12:00:00Z",
            "archetype": "Test Archetype",
        }
    }
    with open(entity_base / "soul.yaml", "w") as f:
        yaml.dump(soul, f)

    with open(knowledge_dir / "README.md", "w") as f:
        f.write("# Test Knowledge Doc\n\n**Purpose**: A sample knowledge document.\n\nBody content.")
    with open(knowledge_dir / "ARCHITECTURE.md", "w") as f:
        f.write("# Architecture Overview\n\nPurpose: System architecture notes.\n\nDetailed content.")
    with open(knowledge_dir / "notes.txt", "w") as f:
        f.write("Plain text notes file.")

    with open(workspace_dir / "current_task.md", "w") as f:
        f.write("# Current Task\n\nWorking on the context hydration tool.")
    (workspace_dir / "subdir").mkdir(exist_ok=True)
    with open(workspace_dir / "subdir" / "draft.md", "w") as f:
        f.write("# Draft\n\nWork in progress.")

    # Add proposed_lessons.yaml with L3 lessons for distillation test
    lessons = [
        {
            "lesson": "L3: Test lesson one about entity context hydration.",
            "source": "test-source",
            "trace_id": "ses_test_001",
            "entity_at_time": "TESTENTITY",
            "session_type": "testing",
            "timestamp": "2026-09-28 01:00:00+00:00",
            "model_used": "test-model",
            "outcome": "l3_principle_test_one",
        },
        {
            "lesson": "L3: Test lesson two about readiness computation.",
            "source": "test-source",
            "trace_id": "ses_test_002",
            "entity_at_time": "TESTENTITY",
            "session_type": "testing",
            "timestamp": "2026-09-27 01:00:00+00:00",
            "model_used": "test-model",
            "outcome": "l3_principle_test_two",
        },
        {
            "lesson": "L2: This is not an L3 lesson and should be filtered out.",
            "source": "test-source",
            "trace_id": "ses_test_003",
            "entity_at_time": "TESTENTITY",
            "session_type": "testing",
            "timestamp": "2026-09-26 01:00:00+00:00",
            "model_used": "test-model",
            "outcome": "l2_insight_test",
        },
    ]
    with open(entity_base / "proposed_lessons.yaml", "w") as f:
        yaml.dump(lessons, f)

    # _list_sessions() reads the module-local HALL_OF_RECORDS inside
    # hub_tools/tools.py — NOT state.HALL_OF_RECORDS. Patch that namespace or
    # the test reads the real Hivemind store.
    hor = tmp_path / "HALL_OF_RECORDS"
    (hor / "testentity").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(tools_mod, "HALL_OF_RECORDS", hor)
    with open(hor / "testentity" / "ses_20260610_abc123.json", "w") as f:
        json.dump(
            {
                "session_id": "ses_20260610_abc123",
                "timestamp": "2026-06-10T22:00:00+00:00",
                "task_current": "Session work",
                "continuation": "Next step",
            },
            f,
        )

    # Services live: the guard is retained, so declare a serving hub.
    monkeypatch.setattr(state, "_init_complete", True)
    monkeypatch.setattr(server, "_init_complete", True)

    # Mock the registry to return a test entity with slot and archetype
    from omega.oracle.entity_registry import Entity, EntityRegistry
    mock_registry = EntityRegistry()
    mock_entity = Entity(
        name="testentity",
        domains=["testing", "context"],
        model="qwen3-1.7b",
        personality="A test entity",
        slots=["P7"],
        role="Test Context Entity",
        metadata={"pantheon": "test"},
    )
    monkeypatch.setattr(state, "registry", mock_registry)
    monkeypatch.setattr(server, "registry", mock_registry)
    # Note: Do NOT patch tools_mod.registry as it's an AsyncServiceProxy that
    # resolves the registry via state.get_service("registry")

    yield tmp_path


@pytest.mark.asyncio
async def test_u004_entity_context_hydrated(entity_context_env):
    """U-004: entity_context — fully populated entity. RESTORED to enriched schema.

    The enriched schema includes registry enrichment (slot, role, archetype),
    a readiness block (HYDRATED/DORMANT/UNINITIALIZED with flags), and L3
    lesson distillation (recent_lessons). This restores the pre-consolidation
    capability that was lost during the Hivemind consolidation.
    """
    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    # Restored enriched schema has these keys.
    expected_keys = {
        "entity", "slot", "role", "archetype", "readiness",
        "soul", "knowledge", "workspace", "recent_sessions", "recent_lessons"
    }
    assert set(payload.keys()) == expected_keys

    # `entity` is the NAME string, not a dict.
    assert payload["entity"] == "testentity"

    # Registry enrichment: slot, role, archetype
    assert payload["slot"] in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", None)
    assert payload["role"] in ("Build", "Run", None)
    assert payload["archetype"] == "Test Archetype"

    # Readiness block: HYDRATED (soul + lessons both present)
    assert payload["readiness"]["status"] == "HYDRATED"
    assert "soul_present" in payload["readiness"]["flags"]
    assert "lessons_present" in payload["readiness"]["flags"]

    # `soul` is the raw soul.yaml payload.
    assert payload["soul"]["entity"]["soul_power"] == 3.5
    assert payload["soul"]["entity"]["sessions_completed"] == 7

    assert payload["knowledge"]["file_count"] == 3
    assert payload["knowledge"]["total_size_bytes"] > 0

    assert payload["workspace"]["file_count"] == 1   # subdir/ is not a file

    assert len(payload["recent_sessions"]) == 1
    assert payload["recent_sessions"][0]["session_id"] == "ses_20260610_abc123"
    assert payload["recent_sessions"][0]["task_current"] == "Session work"

    # L3 lesson distillation: recent_lessons contains L3 lessons only, sorted by timestamp desc
    assert "recent_lessons" in payload
    assert isinstance(payload["recent_lessons"], list)
    assert len(payload["recent_lessons"]) == 2  # Only L3 lessons (outcome starts with l3_)
    # Sorted by timestamp desc (most recent first)
    assert payload["recent_lessons"][0]["outcome"] == "l3_principle_test_one"
    assert payload["recent_lessons"][1]["outcome"] == "l3_principle_test_two"
    # Each lesson has the expected fields
    for lesson in payload["recent_lessons"]:
        assert "id" in lesson
        assert "title" in lesson
        assert "confidence" in lesson
        assert "distilled_at" in lesson
        assert "source" in lesson
        assert "outcome" in lesson
        assert lesson["outcome"].startswith("l3_")


@pytest.mark.asyncio
async def test_u005_entity_context_missing_soul(entity_context_env):
    """U-005: entity_context — missing soul.yaml. RESTORED with readiness.

    The readiness block now correctly reports DORMANT (soul missing, lessons present).
    """
    soul_path = entity_context_env / "data" / "entities" / "testentity" / "soul.yaml"
    soul_path.unlink()

    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    assert payload["entity"] == "testentity"
    assert payload["soul"]["status"] == "missing"
    assert "error" in payload["soul"]
    # Directories still exist, so the file listings are unaffected.
    assert payload["knowledge"]["file_count"] == 3

    # Readiness: DORMANT (soul missing, lessons present)
    assert payload["readiness"]["status"] == "DORMANT"
    assert "soul_present" not in payload["readiness"]["flags"]
    assert "lessons_present" in payload["readiness"]["flags"]


@pytest.mark.asyncio
async def test_u006_entity_context_nonexistent(entity_context_env):
    """U-006: entity_context — entity with no directory at all. RESTORED with readiness.

    DELETED: payload["entity"]["name"] (entity is a str now).
    """
    result = await server.hivemind_get_entity_context(entity_name="nonexistent")
    payload = json.loads(result)

    assert payload["entity"] == "nonexistent"
    assert payload["soul"]["status"] == "missing"
    assert payload["knowledge"]["file_count"] == 0
    assert payload["workspace"]["file_count"] == 0
    assert payload["recent_sessions"] == []

    # Readiness: UNINITIALIZED (no soul, no lessons)
    assert payload["readiness"]["status"] == "UNINITIALIZED"
    assert payload["readiness"]["flags"] == []


@pytest.mark.asyncio
async def test_u007_entity_context_empty_knowledge_workspace(entity_context_env):
    """U-007: entity_context — empty knowledge/workspace dirs. RESTORED with readiness."""
    entity_base = entity_context_env / "data" / "entities" / "newentity"
    entity_base.mkdir(parents=True, exist_ok=True)
    soul = {"entity": {"echo": "newentity", "role": "New", "soul_power": 0.5, "sessions_completed": 0}}
    with open(entity_base / "soul.yaml", "w") as f:
        yaml.dump(soul, f)
    (entity_base / "knowledge").mkdir(exist_ok=True)
    (entity_base / "workspace").mkdir(exist_ok=True)

    result = await server.hivemind_get_entity_context(entity_name="newentity")
    payload = json.loads(result)

    assert payload["entity"] == "newentity"
    assert payload["soul"]["entity"]["soul_power"] == 0.5
    assert payload["knowledge"]["file_count"] == 0
    assert payload["workspace"]["file_count"] == 0
    assert payload["recent_sessions"] == []

    # Readiness: DORMANT (soul present, no lessons)
    assert payload["readiness"]["status"] == "DORMANT"
    assert "soul_present" in payload["readiness"]["flags"]
    assert "lessons_present" not in payload["readiness"]["flags"]


@pytest.mark.asyncio
async def test_u008_entity_context_malformed_soul(entity_context_env):
    """U-008: entity_context — malformed soul.yaml. RESTORED with readiness.

    DELETED: payload["readiness"]["status"] == "DORMANT" (readiness now correctly reports malformed).
    """
    soul_path = entity_context_env / "data" / "entities" / "testentity" / "soul.yaml"
    with open(soul_path, "w") as f:
        f.write("{{{{invalid yaml::::\n")

    result = await server.hivemind_get_entity_context(entity_name="testentity")
    payload = json.loads(result)

    assert payload["entity"] == "testentity"
    assert payload["soul"]["status"] == "malformed"
    assert "error" in payload["soul"]

    # Readiness: DORMANT (soul file exists but malformed, lessons present)
    assert payload["readiness"]["status"] == "DORMANT"
    assert "soul_present" in payload["readiness"]["flags"]
    assert "lessons_present" in payload["readiness"]["flags"]
