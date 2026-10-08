# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the Hub's legacy tool-name compatibility adapters.

Tool-surface curation retired 7 fragmented handoff tools, 3 Oracle debug
tools and `delegate_task` in favour of unified action-based tools
(92 → 66 tools). The server module still advertises the old names so
existing callers keep working. That compatibility layer silently rotted
once already: every legacy name raised AttributeError because the shim
forwarded to tool attributes that no longer existed.

These tests pin the contract so the layer cannot rot again:
- every advertised legacy name resolves to a coroutine function
- each adapter binds the correct action on its unified replacement
- `delegate_task` keeps its context-prefixing summon semantics
- adapters call the raw coroutine, not the FastMCP wrapper
"""

import inspect

import anyio
import pytest

import mcp_servers.omega_hub.hub_tools.tools as hub_tools
import mcp_servers.omega_hub.server as hub_server


LEGACY_HANDOFF_NAMES = [
    "hivemind_submit_handoff",
    "hivemind_accept_handoff",
    "hivemind_complete_handoff",
    "hivemind_reject_handoff",
    "hivemind_handoff_list",
    "hivemind_get_handoff",
    "hivemind_handoff_archive",
]

LEGACY_ORACLE_DEBUG_NAMES = [
    "oracle_list_slot_keepers",
    "oracle_assess_intent",
    "oracle_discover_entity",
]

ALL_LEGACY_NAMES = LEGACY_HANDOFF_NAMES + LEGACY_ORACLE_DEBUG_NAMES + ["delegate_task"]


def test_compatibility_layer_declares_supported_names():
    """The module must not advertise names it has no adapter for."""
    declared = set(hub_server._LEGACY_TOOL_ADAPTERS) | set(hub_server._PASSTHROUGH_TOOLS)
    assert declared, "compatibility layer must declare its supported names"
    # delegate_task has a bespoke adapter (different signature).
    assert "delegate_task" not in declared
    for name in ALL_LEGACY_NAMES:
        assert name in declared or name == "delegate_task"


@pytest.mark.parametrize("name", ALL_LEGACY_NAMES)
def test_legacy_name_resolves_to_coroutine_function(name):
    adapter = getattr(hub_server, name)
    assert inspect.iscoroutinefunction(adapter), f"{name} must be awaitable"
    assert adapter.__name__ == name


@pytest.mark.parametrize(
    ("name", "action"),
    [
        ("hivemind_submit_handoff", "submit"),
        ("hivemind_accept_handoff", "accept"),
        ("hivemind_complete_handoff", "complete"),
        ("hivemind_reject_handoff", "reject"),
        ("hivemind_handoff_list", "list"),
        ("hivemind_get_handoff", "get"),
        ("hivemind_handoff_archive", "archive"),
    ],
)
def test_handoff_adapter_binds_action(name, action, monkeypatch):
    """Each handoff adapter must bind its action on the unified tool."""
    captured = {}

    async def fake_unified(**kwargs):
        captured.update(kwargs)
        return '{"status": "submitted", "packet_id": "ho_0123456789ab"}'

    monkeypatch.setattr(hub_tools, "hivemind_handoff", fake_unified, raising=False)
    adapter = getattr(hub_server, name)

    payload = anyio.run(lambda: adapter(packet_id="ho_0123456789ab"))

    assert captured["action"] == action
    assert "ho_0123456789ab" in payload


@pytest.mark.parametrize(
    ("name", "action"),
    [
        ("oracle_list_slot_keepers", "list_slot_keepers"),
        ("oracle_assess_intent", "assess_intent"),
        ("oracle_discover_entity", "discover_entity"),
    ],
)
def test_oracle_debug_adapter_binds_action(name, action, monkeypatch):
    captured = {}

    async def fake_unified(**kwargs):
        captured.update(kwargs)
        return '{"result": "ok"}'

    monkeypatch.setattr(hub_tools, "oracle_debug", fake_unified, raising=False)
    adapter = getattr(hub_server, name)

    anyio.run(lambda: adapter(query="which entity validates?"))

    assert captured["action"] == action
    assert captured["query"] == "which entity validates?"


def test_delegate_task_prefixes_context_into_summon(monkeypatch):
    """delegate_task was a context-prefixed oracle_summon; preserve that."""
    captured = {}

    async def fake_summon(**kwargs):
        captured.update(kwargs)
        return '{"status": "delegated"}'

    monkeypatch.setattr(hub_tools, "oracle_summon", fake_summon, raising=False)
    adapter = getattr(hub_server, "delegate_task")

    anyio.run(
        lambda: adapter(
            target_entity="jem", query="verify this", context="P0 deliverable"
        )
    )

    assert captured["entity_name"] == "jem"
    assert captured["query"] == "CONTEXT: P0 deliverable\n\nREQUEST: verify this"


def test_delegate_task_without_context_passes_query_verbatim(monkeypatch):
    captured = {}

    async def fake_summon(**kwargs):
        captured.update(kwargs)
        return '{"status": "delegated"}'

    monkeypatch.setattr(hub_tools, "oracle_summon", fake_summon, raising=False)
    adapter = getattr(hub_server, "delegate_task")

    anyio.run(lambda: adapter(target_entity="jem", query="verify this"))

    assert captured["query"] == "verify this"


def test_unknown_name_still_raises_attribute_error():
    with pytest.raises(AttributeError):
        getattr(hub_server, "hivemind_definitely_not_a_tool")


def test_adapter_calls_raw_coroutine_not_mcp_wrapper(monkeypatch):
    """FastMCP wraps @mcp.tool(); adapters must return the JSON string.

    Calling the decorated object returns CallToolResult, which silently
    breaks every caller that json.loads() the result.
    """

    async def raw(**kwargs):
        return '{"status": "submitted", "packet_id": "ho_feedface0000"}'

    # Emulate the FastMCP wrapper: a function returning a sentinel object
    # instead of the tool's JSON string.
    def wrapped(**kwargs):
        return "<<CallToolResult sentinel>>"

    wrapped.__wrapped__ = raw
    monkeypatch.setattr(hub_tools, "hivemind_handoff", wrapped, raising=False)

    adapter = getattr(hub_server, "hivemind_submit_handoff")

    payload = anyio.run(
        lambda: adapter(
            target_channel="opencode",
            target_entity="jem",
            source_channel="opencode",
            source_entity="researcher",
            task="t",
        )
    )

    assert payload == '{"status": "submitted", "packet_id": "ho_feedface0000"}'

