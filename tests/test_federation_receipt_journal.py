# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ P0-FIX-2 ⬡ RECEIPT-JOURNAL
"""P0 FIX 2 guards: append-only receipt journal (read state).

MEASURED STATE: 0 of 10 packets in data/handoff/pending/ carry `read_by`.
Read and unread are indistinguishable. `unread_for` returns identical rows for
every name. This is why messages are missed.

DESIGN (audited, M28-clean): each packet `X.json` gets a sibling
`X.receipts.jsonl`. One JSON object per line per read event. The envelope is
NEVER mutated — pure addition. O_APPEND single-line writes (~120 bytes, well
under PIPE_BUF) need no lock; every write is fsynced (a receipt that vanishes
on crash is a lost acknowledgement); write failure raises loudly (M23).
"""

from __future__ import annotations

import json
import sys
import threading
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


@pytest.fixture
def bound(store, monkeypatch):
    """Bind the real `hivemind_handoff` read path to the throwaway store."""
    from mcp_servers.omega_hub import state
    from mcp_servers.omega_hub.hub_tools import tools as ht

    monkeypatch.setattr(state, "HANDOFF_BASE", store.root)
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


def _submit(store, seq=1, target="maat", source="kali", task="journal-task"):
    return store.submit(fe.build_envelope(
        seq=seq, task=task, source_entity=source, source_channel="opencode",
        target_entity=target, target_channel="opencode",
        source_session_id=SESSION, source_hardware="node0", sender_verified=True))


def _legacy_packet(packet_id="ho_legacy_read01"):
    """Legacy shape: packet_id only — no handoff_id, no body_sha256."""
    return {
        "packet_id": packet_id,
        "target_entity": "maat",
        "source_entity": "kali",
        "task": "legacy task",
        "status": "pending",
        "seq": 0,
        "read_by": {},
        "state_history": [],
        "created_at_utc": fe.utc_stamp(),
        "received_at_utc": fe.utc_stamp(),
        "body_sha256": "",
    }


def test_read_round_trip_records_receipt(bound):
    """THE CANARY: read through the tool records a journal receipt, fsynced."""
    store, call = bound
    env = _submit(store)
    hid = env["handoff_id"]

    fsync_calls = []
    import os as _os
    real_fsync = _os.fsync
    monkey_fsync = lambda fd: (fsync_calls.append(fd), real_fsync(fd))  # noqa: E731

    import unittest.mock as _mock
    with _mock.patch.object(_os, "fsync", monkey_fsync):
        out = call(action="read", source_channel="opencode", source_entity="kali",
                   packet_id=hid, session_id=SESSION)

    assert "entries" in out, f"read did not return the packet: {out}"
    assert out["entries"][0]["handoff_id"] == hid
    assert "kali" in out["read_by"], f"reader key missing from response: {out}"

    sibling = store.pending / f"{hid}.receipts.jsonl"
    assert sibling.is_file(), "no .receipts.jsonl sibling — read left no record"
    lines = sibling.read_text().splitlines()
    assert len(lines) == 1, f"expected exactly one receipt line, got {lines}"
    rec = json.loads(lines[0])
    assert rec == {"action": "read", "at": rec["at"], "handoff_id": hid,
                   "reader": "kali"}, f"receipt shape wrong: {rec}"
    assert rec["at"].endswith("+00:00"), "receipt timestamp is not UTC-explicit"

    # The envelope itself must be byte-identical: pure addition, M28-clean.
    on_disk = fst.FederationStore._load(store.pending / f"{hid}.json")
    assert on_disk.get("read_by") == {}, "envelope was mutated — journal must be pure addition"

    assert fsync_calls, "fsync was NOT called: a receipt that vanishes on crash is lost"


def test_read_legacy_packet_no_crash(bound):
    """Legacy packet (packet_id only) reads cleanly — the hidden crash test."""
    store, call = bound
    legacy = _legacy_packet()
    (store.pending / f"{legacy['packet_id']}.json").write_text(json.dumps(legacy))

    out = call(action="read", source_channel="opencode", source_entity="kali",
               packet_id=legacy["packet_id"], session_id=SESSION)

    assert "entries" in out, f"legacy read failed (was: not_found/crash): {out}"
    assert out["entries"][0]["packet_id"] == legacy["packet_id"]
    assert "kali" in out["read_by"]
    # journal sibling keyed off the legacy file stem
    sibling = store.pending / f"{legacy['packet_id']}.receipts.jsonl"
    assert sibling.is_file(), "legacy read recorded no receipt"


def test_concurrent_readers_both_recorded(store):
    """Two readers, same packet, threads, no lock on the append path."""
    env = _submit(store)
    hid = env["handoff_id"]
    readers = [f"reader-{i}" for i in range(8)]
    errors: dict = {}

    def _read(key):
        try:
            store.record_read_receipt(hid, key, action="read")
        except Exception as exc:  # noqa: BLE001 — collected, then asserted
            errors[key] = repr(exc)

    threads = [threading.Thread(target=_read, args=(k,)) for k in readers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"concurrent receipt writes raised: {errors}"
    got = store.read_receipts(hid)
    missing = [k for k in readers if k not in got]
    assert not missing, f"lost receipts under concurrency: missing={missing} got={got}"


def test_unread_for_uses_journal(store):
    """Fresh packet unread for X; after X reads, X False and Y still True."""
    env = _submit(store)
    hid = env["handoff_id"]

    assert fe.unread_for(env, "x") is True
    store.record_read_receipt(hid, "x", action="read")

    receipts = store.read_receipts(hid)
    assert fe.unread_for(env, "x", receipts=receipts) is False, (
        "journal says x read, but unread_for still reports unread"
    )
    assert fe.unread_for(env, "y", receipts=receipts) is True
    # and the in-envelope fallback still works when no journal is passed
    assert fe.unread_for(env, "y") is True


def test_corrupt_receipt_line_skipped(store):
    """A garbage line never crashes the read; good entries + skip count survive."""
    env = _submit(store)
    hid = env["handoff_id"]
    store.record_read_receipt(hid, "good", action="read")

    sibling = store.pending / f"{hid}.receipts.jsonl"
    with open(sibling, "a") as f:
        f.write("THIS IS NOT JSON {{{{\n")
        f.write('{"no_reader_key": true}\n')

    got = store.read_receipts(hid)
    assert "good" in got, f"good receipt lost to one corrupt line: {got}"
    skips = [v for k, v in got.items() if k.startswith("_")]
    assert skips, f"corrupt lines were not counted in a debug key: {got}"
    assert sum(v for v in skips if isinstance(v, int)) == 2, (
        f"expected 2 skipped lines counted, got {got}"
    )
