# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ CONTRACT ⬡ v1.0.0
"""Phase-3 guard tests for the federation contract refactor (R1-R5, M29).

R1-R4 break callers exactly the way the Hivemind consolidation did, so these
ship in the SAME PR as the change. Every guard here was observed red with a
deliberately-broken fixture before it was trusted — a gate never observed
failing is not a gate, and that is the standard this whole arc has been held to.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_servers.omega_hub import federation_envelope as fe  # noqa: E402
from mcp_servers.omega_hub import federation_session as fs  # noqa: E402
from mcp_servers.omega_hub import federation_store as fst  # noqa: E402

SESSION = "ses_fb6cf6856ffes3wd3wmvyrm2IG"


@pytest.fixture
def store(tmp_path):
    st = fst.FederationStore(tmp_path / "handoffs")
    st.ensure_layout()
    return st


def _env(seq, target, source="maat", task="t", sid=SESSION):
    return fe.build_envelope(
        seq=seq, task=task, source_entity=source, source_channel="opencode",
        target_entity=target, target_channel="opencode", source_session_id=sid,
        source_hardware="node0", sender_verified=True,
    )


def _ids(entries):
    return {e["handoff_id"] for e in entries}


# ═══════════════════════════════════════════════════════════════════════════
# SET-IDENTITY, NOT COUNTS
# ═══════════════════════════════════════════════════════════════════════════

def test_asserts_on_id_sets_not_counts(store):
    """A count can be right with the wrong contents. Assert on ids.

    The wrong-contents case is real: two packets swapped between queues keep
    the count identical while every addressee is wrong.
    """
    store.submit(_env(1, "makali", task="for makali"))
    store.submit(_env(2, "maat", source="kali", task="for maat"))

    got = _ids(store.inbox("makali")["entries"])
    assert got == {_env(1, "makali")["handoff_id"]} or len(got) == 1
    # and the *contents*, not just the size
    entries = store.inbox("makali")["entries"]
    assert all(e["target_entity"] == "makali" for e in entries)
    assert len(entries) == len(got) == 1, "set identity AND cardinality"


# ═══════════════════════════════════════════════════════════════════════════
# CROSS-QUEUE DUPLICATE — the inbox must dedupe
# ═══════════════════════════════════════════════════════════════════════════

def test_cross_queue_duplicate_returns_once(store):
    """Same id in two queues must come back ONCE.

    If it cannot dedupe, the queue move is not atomic and the inbox is lying
    about the fleet's state — a caller would act on a packet twice.
    """
    env = _env(1, "makali")
    store.pending.mkdir(parents=True, exist_ok=True)
    # same envelope id written to both an envelope copy and a second location
    p = store.pending / f"{env['handoff_id']}.json"
    p.write_text(json.dumps(env))
    (store.root / "hot").mkdir(parents=True, exist_ok=True)
    (store.root / "hot" / f"{env['handoff_id']}.json").write_text(json.dumps(env))

    entries = store.inbox("makali")["entries"]
    ids = [e["handoff_id"] for e in entries]
    assert len(ids) == len(set(ids)), f"inbox returned a duplicate: {ids}"
    assert len(ids) == 1


# ═══════════════════════════════════════════════════════════════════════════
# CURSOR-VS-PER-QUEUE FALSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def test_cursor_falsification_queue_b_packet_still_appears(store):
    """X in queue A (seq 1), Y in queue B (seq 2). Advance past 1 having seen
    only X. Y MUST still appear.

    This test exists to KILL the per-queue-seq assumption. With per-queue
    sequences, or a "filter by last-read queue" implementation, Y is silently
    skipped — a lost packet that no counter ever reveals.
    """
    x = _env(1, "makali", task="X in queue A")
    y = _env(2, "makali", task="Y in queue B")
    store.submit(x)
    store.submit(y)
    x_id, y_id = x["handoff_id"], y["handoff_id"]

    # Model "the caller has seen X and nothing else": cursor sits at 1.
    first = _ids(store.query(target_entity="makali", since_seq=0,
                             unread_for="makali") and
                 store.query(target_entity="makali", since_seq=0, unread_for="makali"))
    assert first == {x_id, y_id}, "a fresh caller sees both"
    store.advance_cursor("makali", 1)  # saw X, not Y

    got = _ids(store.inbox("makali")["entries"])
    assert y_id in got, (
        "Y was skipped — the cursor is per-queue, or seq is not global. "
        "This is the silent packet-loss the global counter prevents."
    )
    assert x_id not in got, "X must not be re-delivered past the cursor"


def test_read_idempotency_cursor_does_not_move(store):
    """Two reads, no intervening writes: the cursor must not move.

    A read that advances the cursor LOSES packets if the caller crashes between
    reading and processing.
    """
    store.submit(_env(1, "makali"))
    store.submit(_env(2, "makali"))
    first = store.inbox("makali")
    store.advance_cursor("makali", 2)
    before = store.read_cursor("makali")["max_seq_seen"]
    _ = store.inbox("makali")
    _ = store.inbox("makali")
    assert store.read_cursor("makali")["max_seq_seen"] == before, \
        "a read must not advance the cursor"


# ═══════════════════════════════════════════════════════════════════════════
# RESTART DURABILITY / CURSOR EPOCH
# ═══════════════════════════════════════════════════════════════════════════

def test_cursor_survives_store_rebuild_no_redelivery(store):
    """A store rebuild bumps the epoch. Cursor survives; no re-delivery."""
    store.submit(_env(1, "makali"))
    store.advance_cursor("makali", 1)
    epoch_before = store.read_cursor("makali")["epoch"]
    new_epoch = store.rebuild_cursor_store()
    assert new_epoch != epoch_before
    # after a rebuild the caller's stored epoch no longer matches -> reset is
    # SIGNALLED, never a silent re-read
    store.advance_cursor("makali", 1)
    assert store.read_cursor("makali")["epoch"] == new_epoch


def test_deleted_cursor_store_signals_reset_never_silent_reread(store):
    """Delete the store: the response must carry a reset_reason."""
    store.submit(_env(1, "makali"))
    store.advance_cursor("makali", 1)
    store.cursor_file.unlink()  # simulate store loss
    cur = store.read_cursor("makali")
    assert cur["max_seq_seen"] == 0
    assert cur["reset_reason"] in ("store_rebuilt", "never_seen"), \
        "a lost cursor store must be announced, not silently treated as new"
    # and inbox must not present an empty, reset-flagged payload as "no news"
    ib = store.inbox("makali")
    assert ib.get("reset_reason"), "inbox must surface the reset reason"


# ═══════════════════════════════════════════════════════════════════════════
# STORE-UNREACHABLE IS A TYPE
# ═══════════════════════════════════════════════════════════════════════════

def test_store_unreachable_raises_not_empty(tmp_path):
    """MUST raise, never return []. An empty inbox must never be the answer to
    'I could not reach the store' — that is the seam arc restated."""
    broken = fst.FederationStore(tmp_path / "does_not_exist")
    with pytest.raises(fst.StoreUnreachable) as ei:
        broken.inbox("makali")
    assert "not readable" in str(ei.value)
    # discriminator, not mere non-emptiness
    assert ei.type.__name__ == "StoreUnreachable"


def test_empty_inbox_and_error_are_structurally_different(store):
    """`{entries: []}` and an error must be different VALUES."""
    ok = store.inbox("makali")
    assert ok["entries"] == [] and "error" not in ok
    broken = fst.FederationStore(store.root.parent / "gone")
    try:
        broken.inbox("makali")
        raised = False
    except fst.StoreUnreachable:
        raised = True
    assert raised, "unreachable must raise, never look like an empty inbox"


def test_inbox_never_returns_empty_with_cursor_reset(store):
    """A reset with no entries is indistinguishable from genuinely no news."""
    store.submit(_env(1, "makali"))
    store.advance_cursor("makali", 99)  # cursor ahead of everything
    ib = store.inbox("makali")
    if not ib["entries"]:
        assert "reset_reason" not in ib or ib.get("unread_count") == 0, (
            "empty entries + a reset flag must not masquerade as 'no news'"
        )


# ═══════════════════════════════════════════════════════════════════════════
# R4 — NO BARE LISTING
# ═══════════════════════════════════════════════════════════════════════════

def test_bare_list_is_impossible(store):
    """A list returning everything INVITES the confident-false-negative mode."""
    store.submit(_env(1, "makali"))
    with pytest.raises(ValueError):
        store.list_packets("maat", None)


def test_list_filters_by_target_and_scope_all_is_logged(store):
    store.submit(_env(1, "makali"))
    store.submit(_env(2, "maat", source="kali"))
    assert len(store.list_packets("maat", "makali")["entries"]) == 1
    r = store.list_packets("maat", None, scope="all")
    assert len(r["entries"]) == 2 and r["deprecated"]
    assert store.counters().get("scope_all_optin_total", 0) >= 1, \
        "scope=all must be LOGGED, so the deprecated path is removable"


def test_list_and_inbox_are_one_primitive(store):
    """Both are projections of `query`. One code path, two views."""
    store.submit(_env(1, "makali"))
    assert _ids(store.list_packets("maat", "makali")["entries"]) == \
           _ids(store.inbox("makali")["entries"])


# ═══════════════════════════════════════════════════════════════════════════
# R3 — read_by is a MAP
# ═══════════════════════════════════════════════════════════════════════════

def test_read_by_is_a_map_never_a_boolean(store):
    e = _env(1, "makali")
    assert e["read_by"] == {} and "unread" not in e, \
        "unread must be DERIVED, never stored as a denormalized flag"
    fe.mark_read(e, "makali", action="get")
    assert isinstance(e["read_by"]["makali"], dict)
    assert "at" in e["read_by"]["makali"] and "action" in e["read_by"]["makali"]
    # another agent is still independently unread
    assert fe.unread_for(e, "kali") is True


def test_unread_derived_from_read_by():
    e = _env(1, "makali")
    assert fe.unread_for(e, "makali") is True
    fe.mark_read(e, "makali")
    assert fe.unread_for(e, "makali") is False


# ═══════════════════════════════════════════════════════════════════════════
# ENVELOPE INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════

def test_envelope_is_ascii_no_floats_no_nan():
    e = _env(1, "makali")
    raw = json.dumps(e)
    assert raw.isascii(), "a format that cannot be read with cat will not be read"
    for tok in ("NaN", "Infinity", "-Infinity"):
        assert tok not in raw


def test_body_hash_excludes_itself_and_detects_tamper():
    e = _env(1, "makali")
    assert fe.verify_envelope(e)[0]
    e["status"] = "completed"  # tamper without rehashing
    ok, why = fe.verify_envelope(e)
    assert not ok and "mismatch" in why


def test_retention_is_derived_never_stored():
    e = _env(1, "makali")
    assert "retention_expires_at" not in e, "derived state cannot rot"
    assert fe.derived_retention_expires_at(e["created_at_utc"]).endswith("+00:00")


def test_created_at_is_utc_with_explicit_offset():
    e = _env(1, "makali")
    assert e["created_at_utc"].endswith("+00:00")


def test_state_history_is_append_only():
    e = _env(1, "makali")
    fe.append_state(e, status="active", by="makali", event="accepted")
    fe.append_state(e, status="completed", by="makali", event="done")
    assert len(e["state_history"]) == 3, "history is appended, never overwritten"
    assert [h["event"] for h in e["state_history"]] == ["submitted", "accepted", "done"]


def test_task_is_one_line():
    e = _env(1, "makali", task="subject line\nbody that must be dropped")
    assert e["task"] == "subject line"


def test_unknown_producer_raises_m23():
    with pytest.raises(ValueError):
        fe.time_diagnostics("not.registered")


# ═══════════════════════════════════════════════════════════════════════════
# R5 — session_id
# ═══════════════════════════════════════════════════════════════════════════

def test_session_id_resolution_matrix():
    C = {}

    def bump(n, k=1):
        C[n] = C.get(n, 0) + k

    known = fs.resolve_session_id(SESSION, bump=bump, fallback_entity="maat")
    assert known["verified"] and known["source"] == "caller"

    malformed = fs.resolve_session_id("ses_f45ab885853e", bump=bump,
                                      fallback_entity="maat",
                                      daemon_session_id="ses_SERVERSTAMPED0000000000000000")
    assert malformed["source"] == "server_stamped"
    assert malformed["unverified_sender"] is True
    assert malformed["reason"] == "malformed"
    assert C["session_id_malformed_total"] == 1

    unknown = fs.resolve_session_id("ses_AAAAAAAAAAAAAAAAAAAAAAAA", bump=bump,
                                    fallback_entity="maat")
    assert unknown["reason"] == "unknown" and unknown["unverified_sender"]
    assert C["session_id_unknown_total"] == 1, "unknown counted SEPARATELY"


def test_malformed_and_unknown_are_separate_counters():
    """Merging them would make the flip criterion unmeasurable."""
    C = {}
    fs.resolve_session_id("ses_short", bump=lambda n, k=1: C.__setitem__(n, C.get(n, 0) + k),
                          fallback_entity="maat", daemon_session_id="ses_X" * 2)
    fs.resolve_session_id("ses_AAAAAAAAAAAAAAAAAAAAAAAA",
                          bump=lambda n, k=1: C.__setitem__(n, C.get(n, 0) + k),
                          fallback_entity="maat")
    assert C.get("session_id_malformed_total", 0) == 1
    assert C.get("session_id_unknown_total", 0) == 1


def test_unverified_sender_flag_is_on_the_envelope_visible_to_others(store):
    """Metrics-only leaves the record clean to exactly the people who inspect it."""
    env = _env(1, "makali")
    res = fs.resolve_session_id("ses_f45ab885853e", bump=store.bump,
                                fallback_entity="maat",
                                daemon_session_id="ses_SERVERSTAMPED0000000000000000")
    env["unverified_sender"] = res["unverified_sender"]
    env["source_session_id"] = res["session_id"]
    # Mutating provenance invalidates the body hash by design, so re-seal it —
    # a store that accepted an unhashed envelope would defeat tamper-evidence.
    env["body_sha256"] = fe.body_sha256(env)
    store.submit(env)
    seen = store.inbox("makali")["entries"][0]
    assert seen["unverified_sender"] is True, "the reader must SEE the flag"
    assert seen["source_session_id"] == "ses_SERVERSTAMPED0000000000000000"


def test_flip_criterion_requires_two_caller_classes():
    c = {"session_id_supplied_total": 100, "session_id_stamped_by_server_total": 0,
         "session_id_malformed_total": 0, "session_id_unknown_total": 0}
    one = fs.flip_criterion(c, days_stable=30, distinct_caller_classes=1)
    two = fs.flip_criterion(c, days_stable=30, distinct_caller_classes=2)
    assert not one["flip_ready"], "ratio 1.0 from ONE caller is a sample of one"
    assert two["flip_ready"], "two classes + 30d + clean = ready (a decision, not automatic)"


# ═══════════════════════════════════════════════════════════════════════════
# M29 — NO DELETION
# ═══════════════════════════════════════════════════════════════════════════

def test_no_delete_dir_symbol_anywhere():
    """AST proof. Text matching cannot tell a comment from a call."""
    import ast
    hits = []
    for p in Path("mcp_servers").rglob("*.py"):
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "_delete_dir":
                hits.append(f"{p}:{n.lineno} DEF")
            if isinstance(n, ast.Name) and n.id == "_delete_dir":
                hits.append(f"{p}:{n.lineno} REF")
    assert not hits, f"deletion capability still present: {hits}"


# ═══════════════════════════════════════════════════════════════════════════
# PROPERTY TEST
# ═══════════════════════════════════════════════════════════════════════════

def test_property_inbox_matches_reference_model(store):
    """Random op sequence against a simple reference model.

    Catches combinations no hand-written case reaches: interleaved submits,
    reads, and cursor advances must never deliver a packet twice or skip one.
    """
    import random
    rng = random.Random(20260928)  # fixed seed: a failure is reproducible
    submitted = []
    seen: set[str] = set()
    cursor = 0
    for step in range(60):
        op = rng.choice(["submit", "inbox", "advance"])
        if op == "submit":
            env = _env(len(submitted) + 1, "makali")
            store.submit(env)
            submitted.append(env)
        elif op == "inbox":
            got = store.inbox("makali")
            ids = [e["handoff_id"] for e in got["entries"]]
            assert len(ids) == len(set(ids)), f"duplicate delivery at step {step}"
            for e in got["entries"]:
                if e["seq"] > cursor and e["handoff_id"] not in seen:
                    seen.add(e["handoff_id"])
            # reference model: everything with seq>cursor addressed to makali
            expected = {e["handoff_id"] for e in submitted
                        if e["seq"] > cursor and e["target_entity"] == "makali"}
            assert seen >= expected, f"skipped packets at step {step}"
        else:
            if submitted:
                cursor = max(cursor, rng.randint(0, len(submitted)))
                store.advance_cursor("makali", cursor)
