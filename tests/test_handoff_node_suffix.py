# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ P0-FIX-1 ⬡ NODE-SUFFIX-IS-LOAD-BEARING
"""P0 FIX 1 guards: a trailing node qualifier is ROUTING, never spelling.

LIVE EVIDENCE (the defect): a packet addressed to `lilith-n1` was stored as
target `lilith` with `"rule": "spelling_or_suffix_folded",
"candidates": ["lilith", "lilith-n1"]` and `"resolved": true`. Node 0 Lilith
and Node 1 Lilith became the same address. A reply can be delivered to the
wrong machine while the sender is told it resolved.

RULE: a trailing node qualifier (`-n` + digits) is a DISTINGUISHING token,
never a spelling variant. Fellegi-Sunter: that is the clerical zone, not a
match. Folding it is the bug.

These tests are HERMETIC: they monkeypatch `_live_entities` and
`_queue_canonical` so the live queue on disk cannot leak into the verdict.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import handoff_alias as HA  # noqa: E402


@pytest.fixture
def two_liliths(monkeypatch):
    """Two registered entities: `lilith` and `lilith-n1`. No queue leakage."""
    monkeypatch.setattr(HA, "_live_entities", lambda: ["lilith", "lilith-n1"])
    monkeypatch.setattr(HA, "_queue_canonical", lambda: {})
    return ["lilith", "lilith-n1"]


def test_node_suffix_exact_delivers(two_liliths):
    """`lilith-n1` with a registered `lilith-n1` delivers EXACTLY, no fold."""
    r = HA.resolve_target_entity("lilith-n1", "opencode")
    assert r["entity"] == "lilith-n1", f"folded to the wrong node: {r}"
    assert r["agent_id"] == "opencode/lilith-n1"
    assert r["rule"] == "exact", f"expected rule 'exact', got {r['rule']!r}: {r}"
    assert r["resolved"] is True


def test_node_suffix_unmatched_does_not_fold(two_liliths):
    """`lilith-n9` (no such entity) must NOT silently fold to `lilith`."""
    r = HA.resolve_target_entity("lilith-n9", "opencode")
    assert r["resolved"] is False, f"claimed a resolution that does not exist: {r}"
    assert r["rule"] == "node_suffix_unmatched", (
        f"expected rule 'node_suffix_unmatched', got {r['rule']!r}: {r}"
    )
    assert r["entity"] != "lilith", (
        f"SILENT MISDELIVERY: lilith-n9 folded to lilith: {r}"
    )
    assert r.get("delivered") is False, "base candidate must be marked NOT delivered"


def test_bare_name_ambiguity_flag(two_liliths):
    """Bare `lilith` with two node candidates must NOT claim resolved:true."""
    r = HA.resolve_target_entity("lilith", "opencode")
    cands = r.get("candidates", [])
    assert len(cands) > 1, f"expected both node candidates listed, got {cands}"
    assert r["resolved"] is not True, (
        f"THE LIE: resolved:true with {len(cands)} candidates: {r}"
    )
