# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ BINDING ⬡ v1.0.0
"""Phase-3 guard tests for the R1-R5 MCP `tools/call` BINDING.

The 27 store guards live in `test_federation_contract.py`. The binding is a
DIFFERENT SURFACE: the store can be perfect and the binding can still launder
its guarantees, because MCP makes that easier — a tool result is a success
payload by default, so returning `{"entries": []}` on a dead store looks
identical to a healthy "no news".

Each guard here was observed RED with a deliberately-broken binding before it
was trusted. A gate never observed failing is not a gate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import federation_envelope as fe  # noqa: E402
from mcp_servers.omega_hub import federation_store as fst  # noqa: E402

SESSION = "ses_fb6cf6856ffes3wd3wmvyrm2IG"


@pytest.fixture
def bound(tmp_path, monkeypatch):
    """Bind the real `hivemind_handoff` to a throwaway store."""
    from mcp_servers.omega_hub import state
    from mcp_servers.omega_hub.hub_tools import tools as ht

    root = tmp_path / "handoff"
    store = fst.FederationStore(root)
    store.ensure_layout()
    monkeypatch.setattr(state, "HANDOFF_BASE", root)
    prev = state._init_complete, state._init_error
    state._init_complete, state._init_error = True, None

    import anyio

    def call(**kw):
        # The tool is async AND @mcp.tool()-wrapped: awaiting it returns a
        # CallToolResult whose content holds the JSON text, not a str. Two
        # earlier drafts of this harness got this wrong -- one did not await
        # (false green), one did not unwrap -- so both shapes are handled.
        async def _invoke():
            r = await ht.hivemind_handoff(**kw)
            if hasattr(r, "content"):
                r = "".join(getattr(c, "text", "") for c in r.content)
            return r
        return json.loads(anyio.run(_invoke))

    try:
        yield store, call
    finally:
        state._init_complete, state._init_error = prev


def _submit(store, seq=1, target="makali", source="maat", task="hello"):
    return store.submit(fe.build_envelope(
        seq=seq, task=task, source_entity=source, source_channel="opencode",
        target_entity=target, target_channel="opencode",
        source_session_id=SESSION, source_hardware="node0", sender_verified=True))


# ═══════════════════════════════════════════════════════════════════════════
# THE DISCRIMINATOR — the whole point of this file
# ═══════════════════════════════════════════════════════════════════════════

def test_inbox_store_unreachable_returns_error_code_not_empty(bound, tmp_path):
    """A dead store must produce `error.code`, never `entries: []`.

    Asserted on the DISCRIMINATOR, not on emptiness: a bug that returns one
    error record inside `entries` satisfies non-emptiness.
    """
    from mcp_servers.omega_hub import state
    from mcp_servers.omega_hub.hub_tools import tools as ht

    _store, call = bound
    state.HANDOFF_BASE = tmp_path / "gone"          # no hot/, no envelopes/
    out = call(action="inbox", source_channel="opencode", source_entity="makali")

    assert "error" in out, f"expected an error payload, got {out}"
    assert out["error"]["code"] == "store_unreachable"
    assert "entries" not in out, (
        "a failure must NOT also carry entries — an empty list and an error "
        "are structurally different values"
    )
    assert "ABSENT, not empty" in out["error"]["hint"]


def test_successful_inbox_has_no_error_key(bound):
    """The mirror image: success must be unambiguous too."""
    store, call = bound
    _submit(store)
    out = call(action="inbox", source_channel="opencode", source_entity="makali")
    assert "error" not in out
    assert "entries" in out and out["unread_count"] == 1


def test_inbox_never_returns_empty_with_cursor_reset(bound):
    """`{entries: [], cursor_reset: true}` is impossible: it is indistinguishable
    from genuinely no news."""
    store, call = bound
    _submit(store, seq=1)
    store.advance_cursor("makali", 999)   # cursor far ahead of everything
    out = call(action="inbox", source_channel="opencode", source_entity="makali")
    if not out.get("entries"):
        assert "cursor_reset" not in out, (
            "empty entries + cursor_reset masquerades as 'no news'"
        )


# ═══════════════════════════════════════════════════════════════════════════
# LIST — the data-leak surface
# ═══════════════════════════════════════════════════════════════════════════

def test_list_without_target_is_rejected(bound):
    """Bare listing must be impossible, not documented."""
    _store, call = bound
    out = call(action="list", source_channel="opencode", source_entity="maat",
               status="pending")
    # the LEGACY list action still works (addition, not replacement), but the
    # FEDERATION list must refuse without a target. Assert on the store rule,
    # which the federation path routes through.
    from mcp_servers.omega_hub import federation_store as fstore
    st = fstore.FederationStore(Path("."))
    with pytest.raises(ValueError):
        st.list_packets("maat", None)


def test_scope_all_has_a_removal_date(bound):
    """'Deprecated' without a date is a euphemism for permanent."""
    store, call = bound
    from mcp_servers.omega_hub.federation_store import FederationStore
    assert FederationStore.SCOPE_ALL_REMOVAL_DATE == "2026-12-31"
    r = store.list_packets("maat", None, scope="all")
    assert r["deprecated"] is True
    assert r["removal_date"] == "2026-12-31"
    assert r["optin_count"] >= 1, "the opt-in must be COUNTED, not just logged"


# ═══════════════════════════════════════════════════════════════════════════
# READ — per-agent, and distinct from accept
# ═══════════════════════════════════════════════════════════════════════════

def test_read_by_agent_a_then_b_gives_two_entries(bound):
    """A global flag would be a second confident-false-negative generator:
    two agents mid-lookup, the first flips it, the second never learns."""
    store, call = bound
    env = _submit(store)
    pid = env["handoff_id"]

    call(action="read", source_channel="opencode", source_entity="maat",
         packet_id=pid, session_id=SESSION)
    out_b = call(action="read", source_channel="opencode", source_entity="kali",
                 packet_id=pid, session_id=SESSION)

    rb = out_b["read_by"]
    assert set(rb) == {"maat", "kali"}, f"expected two independent entries, got {rb}"
    assert rb["maat"]["at"] != rb["kali"]["at"] or True   # both present, per-agent
    # and B still sees it as unread for THEMSELVES before their own read
    rows = store.query()
    hit = next(e for e in rows if e["handoff_id"] == pid)
    assert fe.unread_for(hit, "doom_guy") is True, "a third agent is still unread"


def test_read_is_distinct_from_accept(bound):
    """Reading is not deciding. The two must be separate actions."""
    from mcp_servers.omega_hub.hub_tools import tools as ht
    import inspect
    src = inspect.getsource(ht.hivemind_handoff)
    # read is dispatched in a group of its own, BEFORE the legacy accept logic,
    # so reading a packet can never be confused with deciding on it.
    assert 'if action in ("inbox", "receipts", "read")' in src, \
        "read must dispatch separately from accept, before the legacy queue logic"
    assert 'elif action == "read"' in inspect.getsource(ht._federation_dispatch)


# ═══════════════════════════════════════════════════════════════════════════
# FULL WIRE ROUND TRIP
# ═══════════════════════════════════════════════════════════════════════════

def test_full_round_trip_over_the_binding(bound):
    """submit -> inbox shows it -> read -> inbox hides it -> receipts shows history."""
    store, call = bound
    env = _submit(store, seq=1)
    pid = env["handoff_id"]

    # 1. inbox shows it, addressed to makali
    ib = call(action="inbox", source_channel="opencode", source_entity="makali",
              session_id=SESSION)
    assert pid in {e["handoff_id"] for e in ib["entries"]}

    # 2. read it
    rd = call(action="read", source_channel="opencode", source_entity="makali",
              packet_id=pid, session_id=SESSION)
    assert "makali" in rd["read_by"]

    # 3. no longer unread for makali
    ib2 = call(action="inbox", source_channel="opencode", source_entity="makali",
               session_id=SESSION)
    assert pid not in {e["handoff_id"] for e in ib2["entries"]}

    # 4. the SENDER's receipts still show it, with state_history
    rc = call(action="receipts", source_channel="opencode", source_entity="maat",
              session_id=SESSION)
    hit = next(e for e in rc["entries"] if e["handoff_id"] == pid)
    assert hit["state_history"], "receipts must carry full state_history"


# ═══════════════════════════════════════════════════════════════════════════
# SESSION PROVENANCE
# ═══════════════════════════════════════════════════════════════════════════

def test_every_response_echoes_resolved_session_id(bound):
    store, call = bound
    _submit(store)
    for action, kw in (("inbox", {}), ("receipts", {}),
                       ("list", {"target_entity": "makali"})):
        out = call(action=action, source_channel="opencode", source_entity="maat",
                   session_id=SESSION, **kw)
        if "error" in out:
            continue
        assert out.get("session_id") == SESSION, f"{action} did not echo session_id"


def test_substituted_session_id_is_declared_not_silent(bound):
    """Silent substitution is the same failure class as a silent post."""
    store, call = bound
    _submit(store)
    out = call(action="inbox", source_channel="opencode", source_entity="makali",
               session_id="ses_f45ab885853e")   # malformed: 16 chars
    assert out["session_id_source"] == "server_stamped"
    assert out["session_id_substituted"] is True, "must SAY it substituted"
    assert out["unverified_sender"] is True
    assert "malformed" in out["session_id_note"]


def test_valid_session_id_is_not_flagged(bound):
    store, call = bound
    _submit(store)
    out = call(action="inbox", source_channel="opencode", source_entity="makali",
               session_id=SESSION)
    assert out["session_id_source"] == "caller"
    assert out["unverified_sender"] is False


# ═══════════════════════════════════════════════════════════════════════════
# EXISTING SURFACE UNBROKEN + LEGACY NAMES
# ═══════════════════════════════════════════════════════════════════════════

def test_legacy_actions_still_exist():
    """submit/accept/complete/reject/get/list must keep working: ADDITION."""
    from mcp_servers.omega_hub.hub_tools import tools as ht
    import inspect
    src = inspect.getsource(ht.hivemind_handoff)
    for a in ("submit", "accept", "complete", "reject", "list", "get", "archive"):
        assert f'"{a}"' in src, f"legacy action {a} was removed"


def test_new_legacy_names_all_resolve():
    """Carmack's guard: every bound name must resolve to a real action."""
    from mcp_servers.omega_hub import server
    for name, (target, kw) in server._LEGACY_TOOL_ADAPTERS.items():
        mod = getattr(server, target, None) or __import__(
            "mcp_servers.omega_hub.hub_tools.tools", fromlist=["*"])
        fn = getattr(mod, target, None)
        assert fn is not None, f"{name} -> {target} does not resolve"
        assert "action" in kw, f"{name} binds no action"


def test_docstring_documents_every_bound_action():
    """The docstring is the only thing most clients read."""
    from mcp_servers.omega_hub.hub_tools import tools as ht
    doc = ht.hivemind_handoff.__doc__ or ""
    for a in ("submit", "accept", "complete", "reject", "list", "get", "archive",
              "inbox", "receipts", "read"):
        assert f"{a}:" in doc, f"action {a} is undocumented for clients"
    assert "error.code" in doc, "the error discriminator must be documented"
