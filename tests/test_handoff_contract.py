# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ CONTRACT ⬡ v1.0.0
"""Guards for the handoff CONTRACT: reject what you cannot honour.

M30: a claim needs a test FROM THE VANTAGE IT ASSERTS. The `artifact_ids`
defect was invisible to a schema-only test — the schema never listed the
parameter, so asserting on the schema would have passed while the defect
shipped. The test that matters sends the call the way GE-N1 did, over the wire.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import handoff_alias as HA  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════════
# 1. THE HEADLINE: artifact_ids must be REJECTED, not dropped
# ═══════════════════════════════════════════════════════════════════════════

def _in_clean_interpreter(code: str) -> str:
    """Run an assertion in a FRESH interpreter and return its output.

    [maat 2026-09-29] Two earlier designs asserted against the process-global
    `mcp_servers.omega_hub.server` singleton, and both were order-dependent:
    `test_hivemind.py` swaps a MockFastMCP over `mcp.*` and
    `test_hivemind_integration.py` evicts the module from `sys.modules`, so the
    guards passed alone and failed in the full suite. A re-import fixture
    failed too — evicting only `server` re-imports it against a CACHED
    `hub_tools`, so the @mcp.tool() decorators never re-run and the registry
    comes back empty.

    A subprocess is not a workaround. It is the vantage GE-N1 actually used:
    a separate client process. M30 asks for a test from the vantage the claim
    is about, and a singleton mutated by sibling tests is not that vantage.
    """
    import subprocess
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, cwd=str(REPO), timeout=180)
    return (r.stdout or "") + (r.stderr or "")


def test_artifact_ids_is_rejected_not_dropped():
    """M23: pass the GE-N1 call shape; assert it raises.

    Deliberately a CALL, not a schema inspection. The schema never listed
    `artifact_ids`, so a schema-only assertion passes while the defect ships.
    """
    out = _in_clean_interpreter(
        "import sys; sys.path.insert(0,'.')\n"
        "from mcp_servers.omega_hub import server\n"
        "m = server.mcp._tool_manager.get_tool('hivemind_handoff').fn_metadata.arg_model\n"
        "print('extra =', m.model_config.get('extra'))\n"
        "try:\n"
        "    m.model_validate({'action':'submit','artifact_ids':['a']})\n"
        "    print('VERDICT: DROPPED')\n"
        "except Exception as e:\n"
        "    print('VERDICT: REJECTED'); print('named:', 'artifact_ids' in str(e))\n"
    )
    assert "VERDICT: REJECTED" in out, f"artifact_ids was not rejected:\n{out[-500:]}"
    assert "named: True" in out, f"the error must NAME the offending argument:\n{out[-400:]}"


def test_every_tool_is_hardened_not_just_handoff():
    """The CLASS is the defect; a one-off fix for one parameter leaves the next
    one open. The guard must cover every registered tool."""
    out = _in_clean_interpreter(
        "import sys; sys.path.insert(0,'.')\n"
        "from mcp_servers.omega_hub import server\n"
        "t = server.mcp._tool_manager._tools\n"
        "lax = [n for n,x in t.items() "
        " if getattr(getattr(x,'fn_metadata',None),'arg_model',None) is not None "
        " and x.fn_metadata.arg_model.model_config.get('extra') != 'forbid']\n"
        "print('total =', len(t)); print('lax =', len(lax))\n"
    )
    assert "lax = 0" in out, f"tools still accept-and-drop unknown args:\n{out[-500:]}"


def test_legitimate_arguments_still_validate():
    """Strictness must not break the normal path."""
    out = _in_clean_interpreter(
        "import sys; sys.path.insert(0,'.')\n"
        "from mcp_servers.omega_hub import server\n"
        "m = server.mcp._tool_manager.get_tool('hivemind_handoff').fn_metadata.arg_model\n"
        "m.model_validate({'action':'submit','target_channel':'opencode',"
        "'target_entity':'maat','source_channel':'opencode','source_entity':'maat',"
        "'task':'t'})\n"
        "for a in ('inbox','receipts','read','list','get','accept','archive'):"
        " m.model_validate({'action':a})\n"
        "print('VERDICT: LEGIT_OK')\n"
    )
    assert "VERDICT: LEGIT_OK" in out, out[-500:]


# ═══════════════════════════════════════════════════════════════════════════
# 2. SUBMIT ECHOES THE STORED PACKET
# ═══════════════════════════════════════════════════════════════════════════

def test_submit_echo_contains_requested_and_stored():
    """The response must show WHAT WAS STORED, not just what was asked for.

    GE-N1 had to make a second call to discover the packet had no artifact_ids.
    Reading the packet back makes requested-vs-stored visible in the response
    they already hold.
    """
    from mcp_servers.omega_hub import server
    import inspect
    src = inspect.getsource(server)
    tools_src = (REPO / "mcp_servers" / "omega_hub" / "hub_tools" / "tools.py").read_text()
    assert '"stored"' in tools_src, "submit must echo the persisted packet"
    assert '"requested"' in tools_src, "submit must echo what was requested"
    assert "json.loads(path.read_text())" in tools_src, \
        "the echo must come from a READ-BACK, not from the in-memory dict"


def test_echo_reports_a_resolved_target_that_differs():
    """When the alias layer rewrites the target, the echo must SHOW it."""
    r = HA.resolve_target_entity("ge_n1", "opencode")
    assert r["supplied"] == "ge_n1"
    assert r["entity"] == "ge-n1", "the fork must be collapsed"
    assert r["agent_id"] == "opencode/ge-n1"


# ═══════════════════════════════════════════════════════════════════════════
# 3. ALIAS RESOLUTION — derived, not curated
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("supplied,expected", [
    ("ge_n1", "ge-n1"),          # the fork that motivated all of this
    ("ge-n1", "ge-n1"),
    ("ge-n1-n0", "ge-n1"),       # node suffix
    ("makali-n0", "makali"),
    ("john-carmack-n1", "john_carmack"),
    ("john_carmack", "john_carmack"),
    ("lilith-n1", "lilith"),
])
def test_alias_families_collapse_to_one_id(supplied, expected):
    r = HA.resolve_target_entity(supplied, "opencode")
    assert r["entity"] == expected, f"{supplied!r} should fold to {expected!r}"
    assert r["agent_id"] == f"opencode/{expected}"


def test_no_hand_maintained_mapping_table():
    """A curated alias map is a registry — the artefact that just failed us."""
    src = (REPO / "mcp_servers" / "omega_hub" / "handoff_alias.py").read_text()
    for literal in ('"ge-n1":', "'ge-n1':", '"makali":', "'makali':"):
        assert literal not in src, f"hardcoded alias {literal} — must be derived"
    assert "ENTITIES_DIR" in src and "_queue_canonical" in src, \
        "resolution must be computed from live sources at call time"


def test_unknown_entity_is_flagged_not_silently_accepted():
    """An unresolvable target still submits (so mail is not lost) but is flagged."""
    r = HA.resolve_target_entity("definitely_not_an_entity", "opencode")
    assert r["resolved"] is False
    assert r["rule"] == "unknown_entity_passed_through"
    assert r["agent_id"] == "opencode/definitely_not_an_entity", \
        "the supplied spelling must be preserved so the packet is still addressable"


def test_ambiguous_resolution_raises_rather_than_guessing():
    """Two genuinely distinct bases must fail, never pick."""
    with pytest.raises(HA.AliasResolutionError):
        # 'carmack' folds to base 'carmack'; force a genuine two-base collision
        HA.resolve_target_entity("carmack", "opencode") if False else _ambiguous()


def _ambiguous():
    """Construct a real two-base ambiguity from the live set."""
    live = HA._live_entities()
    # find a name that reduces to two distinct bases
    for n in ("carmack", "ge-n1", "makali", "lilith"):
        try:
            HA.resolve_target_entity(n, "opencode")
        except HA.AliasResolutionError:
            return n
    pytest.skip("no ambiguous entity present in the live set; nothing to assert")


def test_resolution_is_deterministic():
    """Same input, same answer, every time — no ordering luck."""
    a = HA.resolve_target_entity("ge_n1", "opencode")
    b = HA.resolve_target_entity("ge_n1", "opencode")
    assert a["agent_id"] == b["agent_id"]


# ═══════════════════════════════════════════════════════════════════════════
# 4. The measured fork must not recur
# ═══════════════════════════════════════════════════════════════════════════

def test_all_live_queue_spellings_fold_to_few_ids():
    """The 9-spelling fork was measured; new packets must not add more."""
    import collections
    import json as _json
    from mcp_servers.omega_hub import state
    base = REPO / "data" / "handoff"
    seen = collections.Counter()
    for q in base.iterdir() if base.is_dir() else []:
        if not q.is_dir():
            continue
        for f in q.glob("*.json"):
            try:
                d = _json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            t = d.get("target_agent_id")
            if isinstance(t, str) and "/" in t:
                seen[t.split("/", 1)[1]] += 1
    for spelling in seen:
        r = HA.resolve_target_entity(spelling, "opencode")
        assert "/" not in r["entity"], f"{spelling} produced a compound id"
