# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""P0 federation fixes — red/green guards for the 2026-10-02 N0 stack."""

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
def store(tmp_path):
    st = fst.FederationStore(tmp_path / "handoff")
    st.ensure_layout()
    return st


def _legacy_packet_no_seq(packet_id="ho_legacy_noseq01", target="maat"):
    """Legacy shape: no `seq` key at all — predates the cursor machinery."""
    return {
        "packet_id": packet_id,
        "target_entity": target,
        "source_entity": "kali",
        "task": "legacy task",
        "status": "pending",
        "read_by": {},
        "state_history": [],
        "created_at_utc": fe.utc_stamp(),
        "received_at_utc": fe.utc_stamp(),
        "body_sha256": "",
    }


def test_p0_1_inbox_returns_legacy_packet_without_seq(store):
    """P0-1: a packet with NO seq must survive the cursor filter.

    Cursor starts at max_seq_seen=0; legacy packets have no seq (treated as
    0) and were dropped by `seq <= cursor` BEFORE the unread/journal filter.
    """
    pkt = _legacy_packet_no_seq()
    (store.pending / f"{pkt['packet_id']}.json").write_text(json.dumps(pkt))
    out = store.inbox("maat")
    ids = [e.get("packet_id") or e.get("handoff_id") for e in out["entries"]]
    assert pkt["packet_id"] in ids, (
        f"legacy packet without seq was dropped by the cursor filter: {ids}"
    )


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


def test_p0_2_submit_writes_full_envelope(bound):
    """P0-2: the live submit path must persist a full envelope.

    New packets must carry handoff_id, seq, body_sha256, read_by — not the
    legacy packet_id-only shape.
    """
    store, call = bound
    out = call(action="submit", target_channel="opencode", target_entity="maat",
               source_channel="opencode", source_entity="kali", task="p0-2 probe")
    assert out["status"] == "submitted", out
    path = Path(out["path"])
    pkt = json.loads(path.read_text())
    for key in ("handoff_id", "seq", "body_sha256", "read_by"):
        assert key in pkt, f"stored packet missing {key!r}: keys={sorted(pkt)}"
    # and the envelope must actually verify
    ok, why = fe.verify_envelope(pkt)
    assert ok, f"stored envelope does not verify: {why}"


def test_p1_submit_persists_session_id_and_source_instance(bound):
    """P1: submit must persist session_id/source_instance when supplied."""
    store, call = bound
    out = call(action="submit", target_channel="opencode", target_entity="maat",
               source_channel="opencode", source_entity="kali", task="p1 probe",
               session_id=SESSION, source_instance="node0-primary")
    assert out["status"] == "submitted", out
    pkt = json.loads(Path(out["path"]).read_text())
    assert pkt.get("session_id") == SESSION, pkt.keys()
    assert pkt.get("source_instance") == "node0-primary", pkt.keys()


def test_p0_4_reaper_moves_receipt_journal(tmp_path, monkeypatch):
    """P0-4: when the reaper moves a packet, its .receipts.jsonl sibling
    must move alongside it — otherwise every journaled read becomes
    invisible the moment the packet reaps."""
    import anyio
    from mcp_servers.omega_hub import state
    from mcp_servers.omega_hub import background

    base = tmp_path / "handoff"
    for d in ("pending", "active", "completed", "stale", "archive"):
        (base / d).mkdir(parents=True)
    monkeypatch.setattr(state, "HANDOFF_BASE", base)
    monkeypatch.setattr(state, "HANDOFF_PENDING", base / "pending")
    monkeypatch.setattr(state, "HANDOFF_ACTIVE", base / "active")
    monkeypatch.setattr(state, "HANDOFF_COMPLETED", base / "completed")
    monkeypatch.setattr(state, "HANDOFF_STALE", base / "stale")
    monkeypatch.setattr(state, "HANDOFF_ARCHIVE", base / "archive")

    pkt = {"packet_id": "ho_reap01", "status": "pending",
           "created_at_utc": fe.utc_stamp()}
    pkt_path = base / "pending" / "ho_reap01.json"
    pkt_path.write_text(json.dumps(pkt))
    # age the file past the 24h threshold
    old = __import__("time").time() - 90000
    __import__("os").utime(pkt_path, (old, old))
    journal = base / "pending" / "ho_reap01.receipts.jsonl"
    journal.write_text('{"reader": "maat", "action": "read", "at": "2026-10-01T00:00:00+00:00"}\n')

    anyio.run(background._reap_stale_handoffs)

    assert (base / "stale" / "ho_reap01.json").is_file(), "packet not reaped"
    assert (base / "stale" / "ho_reap01.receipts.jsonl").is_file(), (
        "receipt journal was NOT carried alongside the packet"
    )
    assert not journal.exists(), "journal left behind in pending/"


def test_p0_5_code_stamp_detects_stale(tmp_path):
    """P0-5: touching a source file after the stamp must report STALE;
    a fresh stamp must report CURRENT."""
    from mcp_servers.omega_hub import code_stamp

    root = tmp_path
    hub = root / "mcp_servers" / "omega_hub"
    hub.mkdir(parents=True)
    f = hub / "mod.py"
    f.write_text("x = 1\n")
    stamp_path = root / "stamp.json"
    code_stamp.write_stamp(root, stamp_path=stamp_path)
    current, stale = code_stamp.check_stamp(root, stamp_path=stamp_path)
    assert current, f"fresh stamp reported stale: {stale}"
    # touch the file (change mtime)
    import os, time
    new = time.time() + 5
    os.utime(f, (new, new))
    current, stale = code_stamp.check_stamp(root, stamp_path=stamp_path)
    assert not current, "touched file not detected as stale"
    assert any("mod.py" in s for s in stale), stale


def test_p1_awareness_rehydrate_from_cold(tmp_path, monkeypatch):
    """P1: on boot, the hot awareness map must rehydrate from the cold store.

    Seed a cold-store session file with a recent mtime, rehydrate, and assert
    the agent is now in the hot `_awareness` map.
    """
    import anyio
    from mcp_servers.omega_hub import state

    hall = tmp_path / "HALL_OF_RECORDS"
    agent_dir = hall / "opencode_maat"
    agent_dir.mkdir(parents=True)
    snap = {
        "agent_id": "opencode/maat",
        "channel": "opencode",
        "entity": "maat",
        "model": "test-model",
        "task_current": "p1 probe",
        "timestamp": fe.utc_stamp(),
    }
    f = agent_dir / "ses_test1234567890ab.json"
    f.write_text(json.dumps(snap))
    monkeypatch.setattr(state, "HALL_OF_RECORDS", hall)
    monkeypatch.setattr(state, "_awareness", {})
    monkeypatch.setattr(state, "_awareness_cache", {})

    n = anyio.run(state.rehydrate_awareness_from_cold)
    assert n == 1, f"expected 1 rehydrated, got {n}"
    assert "opencode/maat" in state._awareness, state._awareness.keys()
    assert state._awareness["opencode/maat"]["task_current"] == "p1 probe"
