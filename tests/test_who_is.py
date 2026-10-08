# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ WHOIS ⬡ v1.0.0
"""Guard tests for `who_is` — the live peer-discovery primitive.

The tool's entire value is that it REFUSES. A version that silently picks a
session id is worse than no tool, because it produces a confident wrong answer
instead of an honest "ask the peer". So the headline test here is a refusal.

Every guard was observed RED with a deliberately-broken fixture before it was
trusted. A gate never observed failing is not a gate.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import who_is as W  # noqa: E402


@pytest.fixture
def db(tmp_path):
    """A tiny synthetic opencode.db with a KNOWN shape."""
    p = tmp_path / "opencode.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE session (id TEXT PRIMARY KEY, agent TEXT, "
                "parent_id TEXT, title TEXT, time_updated INTEGER)")
    con.commit()
    con.close()
    return p


def _add(db, sid, agent, parent, title, age_s=0, now_ms=1_700_000_000_000):
    con = sqlite3.connect(db)
    con.execute("INSERT INTO session VALUES (?,?,?,?,?)",
                (sid, agent, parent, title, now_ms - age_s * 1000))
    con.commit()
    con.close()


# ═══════════════════════════════════════════════════════════════════════════
# THE HEADLINE: the carmack two-EIS case must REFUSE
# ═══════════════════════════════════════════════════════════════════════════

def test_two_live_structural_eis_refuses_rather_than_picking(db):
    """Two live structural EIS 2.26h apart. A recency rule picks the WRONG one.

    This mirrors the real acceptance case: JC-EIS-kq5 (newer) and JC-EIS
    (2.26h older). Paging by recency would reach JC-EIS-kq5 and miss JC-EIS.
    The correct behaviour is to return BOTH and refuse.
    """
    now = 1_700_000_000_000
    _add(db, "ses_NEWER", "peer", None, "JC-EIS-kq5", age_s=78, now_ms=now)
    _add(db, "ses_OLDER", "peer", None, "JC-EIS", age_s=8357, now_ms=now)

    r = W.who_is("peer", db_path=db, entity="peer", now_ms=now)

    assert r["ambiguous"] is True, "two live structural EIS must be ambiguous"
    assert r["refused"] is True
    assert r["session_id"] is None, (
        "MUST NOT pick one. A chosen id here is a coin toss presented as a lookup."
    )
    assert r["error"] == "ambiguous_eis"
    ids = {c["id"] for c in r["candidates"]}
    assert ids == {"ses_NEWER", "ses_OLDER"}, "both candidates must be surfaced"
    assert "recency" in r["message"]


def test_unique_structural_eis_resolves(db):
    """The happy path still works — refusal is not the only requirement."""
    now = 1_700_000_000_000
    _add(db, "ses_ONLY", "peer", None, "the one", age_s=10, now_ms=now)
    r = W.who_is("peer", db_path=db, entity="peer", now_ms=now)
    assert r["ambiguous"] is False and r["refused"] is False
    assert r["session_id"] == "ses_ONLY"
    assert "ses_ONLY" in r["pager_echo"], "the pager MUST echo the resolved target"


def test_non_structural_sessions_are_ignored(db):
    """NES task sessions are not EIS. parent_id must be NULL."""
    now = 1_700_000_000_000
    _add(db, "ses_ROOT", "peer", None, "EIS", age_s=5, now_ms=now)
    _add(db, "ses_CHILD", "peer", "ses_ROOT", "task", age_s=1, now_ms=now)
    r = W.who_is("peer", db_path=db, entity="peer", now_ms=now)
    assert r["session_id"] == "ses_ROOT", "a task session must never be paged as EIS"


# ═══════════════════════════════════════════════════════════════════════════
# STALENESS
# ═══════════════════════════════════════════════════════════════════════════

def test_all_stale_refuses_and_lists_candidates(db, monkeypatch):
    """A peer's only match outside the window is stale: refuse, do not guess."""
    now = 1_700_000_000_000
    _add(db, "ses_OLD", "peer", None, "ancient", age_s=90 * 86400, now_ms=now)
    r = W.who_is("peer", db_path=db, entity="peer", now_ms=now)
    assert r["refused"] is True
    assert r["session_id"] is None
    assert r["error"] == "all_stale"
    assert r["candidates"], "a stale refusal must still SHOW what it saw"


def test_staleness_window_exceeds_the_real_2h26m_gap():
    """The window must exceed the acceptance case's gap, or it passes for the
    wrong reason (a recency pick that happens to look unambiguous)."""
    assert W.STALENESS_WINDOW_S > 8357, (
        f"window {W.STALENESS_WINDOW_S}s must exceed the 8357s acceptance gap"
    )


# ═══════════════════════════════════════════════════════════════════════════
# READ-ONLY — asserted, not assumed
# ═══════════════════════════════════════════════════════════════════════════

def test_connection_is_read_only(db):
    """A discovery tool that can WRITE to the session store is a new hazard."""
    _add(db, "ses_X", "peer", None, "t")
    con = W._connect_readonly(db)
    try:
        with pytest.raises(sqlite3.OperationalError):
            con.execute("INSERT INTO session VALUES ('ses_INJECTED','p',NULL,'t',0)")
    finally:
        con.close()
    # and it really is absent
    con = sqlite3.connect(db)
    n = con.execute("SELECT COUNT(*) FROM session WHERE id='ses_INJECTED'").fetchone()[0]
    con.close()
    assert n == 0, "the write must not have landed"


def test_readonly_probe_would_detect_a_writable_connection(db):
    """_is_readonly must actually reject a writable handle — otherwise the guard
    above proves nothing, since a mutable probe would always pass."""
    con = sqlite3.connect(db)          # deliberately WRITABLE
    try:
        assert W._is_readonly(con) is False, (
            "a writable connection must be detected as writable"
        )
    finally:
        con.close()


def test_uri_carries_mode_ro():
    """The guard must be structural, not only behavioural."""
    src = (REPO / "mcp_servers" / "omega_hub" / "who_is.py").read_text()
    assert "mode=ro" in src, "the connection URI must pin mode=ro"


# ═══════════════════════════════════════════════════════════════════════════
# AGENT -> ENTITY: derived by query, no hand-maintained table
# ═══════════════════════════════════════════════════════════════════════════

def test_resolution_needs_no_mapping_table():
    """The mapping must be DERIVED by scanning the live entity set.

    A table would be a registry — the exact thing being eliminated. So the
    module must contain no peer->entity mapping literal.
    """
    src = (REPO / "mcp_servers" / "omega_hub" / "who_is.py").read_text()
    for bad in ('"carmack":', "'carmack':", '"kali":', '"makali":'):
        assert bad not in src, f"hardcoded mapping {bad} — must be derived by query"
    assert "ENTITIES_DIR" in src, "resolution must scan the live entity set"


def test_two_entities_claiming_one_peer_is_ambiguous():
    """`carmack` and `john_carmack` are BOTH registered entities, and the DB
    keys Carmack's sessions as `john_carmack`. Preferring the exact match would
    hide a real ambiguity and dead-end the lookup."""
    ents = ["carmack", "john_carmack", "maat"]
    assert W._entity_candidates("carmack", ents) == ["carmack", "john_carmack"]
    r = W.resolve_agent("carmack")
    assert r["ambiguous"] is True and r["entity"] is None


def test_unambiguous_agent_resolves():
    ents = ["carmack", "john_carmack", "maat"]
    assert W._entity_candidates("maat", ents) == ["maat"]
    assert W.resolve_agent("maat")["entity"] == "maat"


# ═══════════════════════════════════════════════════════════════════════════
# THE GENERATED REGISTRY IS NOT AN ANSWER PATH
# ═══════════════════════════════════════════════════════════════════════════

def test_generated_registry_carries_a_loud_banner():
    """A stale answer that LOOKS authoritative is the defect. The artifact must
    say so at the top, not in a footnote."""
    f = REPO / "data" / "coordination" / "EXPERT_SESSION_REGISTRY.md"
    head = f.read_text()[:1400]
    assert "DO NOT PAGE PEER EIS IDs FROM THIS FILE" in head
    assert "who_is" in head, "the banner must point at the replacement"
    assert "STRUCTURALLY INCAPABLE" in head, "the banner must say why, not just that"
    # The banner must ALSO stay clean of the substrings check_sahs.py assertion 4
    # scans for, or a deprecation notice is itself read as a capability claim.
    for kw in ("live session", "current session", "active session", "resolves",
               "resolver", "lookup", "find session"):
        assert kw not in head.lower(), f"banner trips the SAHS detector on {kw!r}"


def test_makali_soul_does_not_appoint_the_registry_a_living_source():
    """An AGENT PROMPT is the most dangerous consumer: it is what made an agent
    trust the file in the first place."""
    import yaml
    soul = yaml.safe_load((REPO / "data" / "entities" / "makali" / "soul.yaml").read_text())
    blob = yaml.safe_dump(soul)
    line = next(l for l in blob.splitlines() if "Living Registries" in l)
    assert "EXPERT_SESSION_REGISTRY.md" not in line, (
        "the generated registry must not be listed as a living registry"
    )
    assert "who_is" in blob, "the prompt must point at the live query instead"
