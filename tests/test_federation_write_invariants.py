# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ WRITE-INVARIANTS ⬡ v1.0.0
"""Concurrency + time-ordering invariants of the federation write path.

Four guards, each observed red before it was trusted:

  FIX 1  `new_seq_file` allocates a GLOBAL monotonic counter under contention.
         The defect is CROSS-PROCESS, so the test spawns real processes. Threads
         would pass against the broken implementation and prove nothing.
  FIX 2  `write_atomic` is hardened against two writers to the SAME target.
         This is DEFENSE IN DEPTH on the known read-path race, not a second
         distinct defect: the tmp name is per-target, so two DIFFERENT
         envelopes never collided. What this guards is that the tmp name is now
         per-WRITER, so those two writers no longer stomp a shared path.
  FIX 3  Ordering is by `seq`, never by wall-clock. On this host (AST, UTC-4)
         something writes naive `datetime.now().isoformat()` into `*_utc`
         fields, producing a 13-hour spread in the corpus. Seq-ordering makes
         that bug structurally irrelevant to correctness; these tests make the
         seq-ordering invariant impossible to quietly revert.
  FIX 4  The `O_EXCL` reclaim must not delete a LIVE writer's temp file. The
         temp name is `{name}.{pid}.{tid}` and BOTH are reused by the OS, so two
         logically distinct writers can provably derive ONE name. See the
         FIX 4 block for why the current implementation cannot honour this and
         what that means.

A gate never observed failing is not a gate. FIX 1 and FIX 2 are red against the
pre-fix implementation. FIX 3 guards behaviour that is already correct, so it is
verified by MUTATION: the `query()` seq-sort is temporarily mutated to a
timestamp-sort and the test is shown to catch it. FIX 4 is red against the
implementation as it stands — see the block below, which states the defect
rather than papering over it.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_servers.omega_hub import federation_envelope as fe  # noqa: E402
from mcp_servers.omega_hub import federation_store as fst  # noqa: E402

SESSION = "ses_fb6cf6856ffes3wd3wmvyrm2IG"

# 8 processes x 50 increments. 400 allocations. Chosen to be small enough to be
# fast and large enough that the read-modify-write window is hit repeatedly.
WORKERS = 8
PER_WORKER = 50


# ═══════════════════════════════════════════════════════════════════════════
# FIX 1 — the global seq counter under CROSS-PROCESS contention
# ═══════════════════════════════════════════════════════════════════════════
#
# The worker lives at module level so it is picklable under the fork start
# method. It catches EVERY exception and reports it rather than letting a child
# die silently: an exception that escapes a worker is itself a failure of the
# invariant, and a test that only counts returned values would miss it.

def _seq_worker(seq_path: str, n: int, barrier, results) -> None:
    """Allocate `n` sequence numbers, releasing the gate only when ALL workers
    are ready. The barrier is what makes this contention real: without it the
    first process to be scheduled finishes before the last one is even forked.
    """
    allocated: list[int] = []
    failure: str | None = None
    try:
        p = Path(seq_path)
        barrier.wait(timeout=60)  # every worker starts allocating at once
        for _ in range(n):
            allocated.append(fe.new_seq_file(p))
    except BaseException as exc:  # noqa: BLE001 — reported, never swallowed
        failure = f"{type(exc).__name__}: {exc}"
    results.put((os.getpid(), allocated, failure))


def test_seq_counter_is_unique_across_processes(tmp_path):
    """Every allocation is a DISTINCT seq. distinct == attempted, exactly.

    The single global counter backs the R1 single-cursor design: one cursor
    spanning queues only works if no two packets ever share a seq. A duplicate
    is not a gap, it is an invisible packet — the cursor advances past it and
    nobody is ever told it existed.
    """
    seq_file = tmp_path / ".seq"
    ctx = mp.get_context("fork")
    barrier = ctx.Barrier(WORKERS)
    results = ctx.Queue()
    procs = [
        ctx.Process(target=_seq_worker,
                    args=(str(seq_file), PER_WORKER, barrier, results))
        for _ in range(WORKERS)
    ]
    for p in procs:
        p.start()

    collected: list[list[int]] = []
    failures: list[str] = []
    for _ in range(WORKERS):
        pid, allocated, failure = results.get(timeout=120)
        collected.append(allocated)
        if failure:
            failures.append(f"pid={pid}: {failure}")
    for p in procs:
        p.join(timeout=60)
        assert p.exitcode == 0, f"worker exited with {p.exitcode} — an exception escaped"

    attempted = WORKERS * PER_WORKER
    flat = [seq for batch in collected for seq in batch]

    assert not failures, (
        "new_seq_file raised under cross-process contention. A shared tmp path "
        f"means one writer can os.replace() a file another writer already "
        f"moved, so FileNotFoundError is an expected symptom:\n  "
        + "\n  ".join(failures)
    )
    assert len(flat) == attempted, (
        f"expected {attempted} allocations, got {len(flat)} — a worker lost a value"
    )

    distinct = set(flat)
    assert len(distinct) == attempted, (
        f"DUPLICATE seq allocated: {len(attempted) - len(distinct)} of "
        f"{attempted} allocations collided. distinct={len(distinct)} "
        f"attempted={attempted}. Collisions (sample): "
        f"{sorted(v for v in distinct if flat.count(v) > 1)[:5]}"
    )

    # The value handed back must be the value that landed on disk. A shared tmp
    # path breaks this independently of uniqueness: os.replace() moves whatever
    # bytes are IN the tmp file, not the ones this writer put there.
    final = int(seq_file.read_text().strip())
    assert final == max(flat), (
        f"on-disk seq {final} != max allocated {max(flat)} — the counter "
        f"returned a value it did not persist"
    )


# ═══════════════════════════════════════════════════════════════════════════
# FIX 2 — write_atomic tmp naming
# ═══════════════════════════════════════════════════════════════════════════

def test_write_atomic_same_target_two_threads_never_blends(tmp_path):
    """Two threads, ONE target: the file is always exactly one payload, whole.

    A blend (A's bytes and B's bytes interleaved) would mean a reader observed
    a file that never existed as a unit — the precise corruption the temp-then-
    rename dance exists to prevent.
    """
    target = tmp_path / "envelope.json"
    # Distinct, long, and self-identifying so a blend is unambiguous.
    payload_a = ("A" * 250_000)
    payload_b = ("B" * 250_000)

    barrier = threading.Barrier(2)
    errors: list[str] = []

    def _write(payload: str) -> None:
        try:
            barrier.wait(timeout=30)
            for _ in range(25):
                fe.write_atomic(target, payload)
        except BaseException as exc:  # noqa: BLE001
            errors.append(f"{type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=_write, args=(p,)) for p in (payload_a, payload_b)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert not errors, "write_atomic raised under concurrent same-target writes: " + "; ".join(errors)

    final = target.read_text()
    assert final in (payload_a, payload_b), (
        "BLEND: the surviving file is not exactly one payload — a partial write "
        f"became visible at the final path (len={len(final)}, "
        f"starts_with_A={final.startswith('A')}, "
        f"starts_with_B={final.startswith('B')})"
    )

    leftovers = sorted(p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp"))
    assert not leftovers, f"temp debris left behind: {leftovers}"


def test_write_atomic_recovers_from_stale_tmp_and_leaves_no_debris(tmp_path):
    """PID+TID naming means a crashed predecessor's tmp can still be present.

    PIDs and TIDs are reused, so O_EXCL raises FileExistsError on a name that
    is already there. That must be handled by removing the stale file and
    retrying ONCE — and a second failure must be LOUD (M23), never a silent
    proceed onto a half-written envelope.
    """
    target = tmp_path / "cursor.json"
    # Same formula the implementation uses. If the naming ever changes this
    # seeds the wrong file, and the "stale file is gone" assertion below then
    # FAILS loudly — so the test cannot pass vacuously.
    stale = tmp_path / f".{target.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    stale.write_text('{"half-written-by-a-crashed-predecessor": ')

    fe.write_atomic(target, json.dumps({"cursor": "recovered"}))

    assert not stale.exists(), (
        f"stale tmp {stale.name} was not consumed — the EEXIST retry path did "
        "not run, so this test proved nothing"
    )
    assert json.loads(target.read_text()) == {"cursor": "recovered"}
    leftovers = sorted(p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp"))
    assert not leftovers, f"temp debris left behind: {leftovers}"


def test_write_atomic_unlinks_the_stale_tmp_at_most_once(tmp_path, monkeypatch):
    """The reclaim is ONCE. A second unlink deletes a stranger's file.

    The audited rule is "on EEXIST, unlink the stale tmp and retry ONCE, and if
    it fails again raise loudly". So exactly ONE unlink is sanctioned. Two is a
    bug: after the first reclaim, the name may have been re-created by a
    DIFFERENT writer, and a second unlink destroys a live writer's file — the
    precise failure the EEXIST-RAISE rule exists to prevent.

    This is a regression guard for a bug introduced and caught inside this same
    change: the first draft cleaned up the temp file on EVERY failure path,
    which made the count 2 (one in the reclaim helper, one in the caller).

    Counting unlinks is the assertion that actually distinguishes the two
    implementations. Asserting "the file still exists" cannot: the single
    sanctioned reclaim legitimately removes it.
    """
    target = tmp_path / "cursor.json"
    tmp_name = f".{target.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    tmp_path.joinpath(tmp_name).write_text("held")

    real_open = os.open
    unlinks: list[Path] = []
    real_unlink = Path.unlink

    def _counting_unlink(self, *a, **kw):
        unlinks.append(self)
        return real_unlink(self, *a, **kw)

    def _always_busy(path, *a, **kw):
        if str(path).endswith(".tmp"):
            raise FileExistsError(17, "File exists", str(path))
        return real_open(path, *a, **kw)

    monkeypatch.setattr(os, "open", _always_busy)
    monkeypatch.setattr(Path, "unlink", _counting_unlink)

    with pytest.raises(FileExistsError):
        fe.write_atomic(target, "{}")

    tmp_unlinks = [p for p in unlinks if p.name == tmp_name]
    assert len(tmp_unlinks) == 1, (
        f"expected exactly ONE reclaim unlink of the temp file, saw "
        f"{len(tmp_unlinks)}. A second unlink can delete a temp file that a "
        f"different live writer has since created under the same name."
    )
    assert not target.exists(), "the target must not be created on a failed open"


def test_write_atomic_tmp_is_hidden_from_a_glob_scan(tmp_path):
    """A partial write must never be observable as an envelope.

    The leading dot is load-bearing: `pending.glob("*.json")` does not match
    a dotfile, so an in-flight write is invisible to the query path.
    """
    target = tmp_path / "H0123456789.json"
    fe.write_atomic(target, '{"seq": 1}')
    # Simulate an in-flight write: the temp file that exists DURING the write.
    inflight = tmp_path / f".{target.name}.999.888.tmp"
    inflight.write_text('{"seq": 1, "partial')

    scanned = sorted(p.name for p in tmp_path.glob("*.json"))
    assert scanned == ["H0123456789.json"], (
        f"an in-flight temp file was visible to a *.json scan: {scanned}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# FIX 4 — the O_EXCL reclaim must never destroy a LIVE writer's temp file
# ═══════════════════════════════════════════════════════════════════════════
#
# WHY THESE TESTS CALL THE HELPER DIRECTLY INSTEAD OF WAITING FOR A REAL
# COLLISION. The temp name is `.{name}.{pid}.{tid}.tmp`. A genuine collision
# needs the OS to hand this process the SAME pid AND the SAME thread id as
# another live writer — unreproducible on demand, and a test that depends on it
# either passes vacuously or is flaky. Both are worse than no test. So the
# collision is INJECTED: the helper is handed a name that is, by construction,
# the name a second logical writer would derive. The invariant under test is
# about what the helper does with that name, and that is fully determined here.
#
# NOTE THE SHAPE: writer A holds an OPEN descriptor and has written its bytes.
# A is not "a file that happens to exist" — A is an in-flight write. Deleting
# the name out from under it is the defect.

# A (pid, tid) pair chosen to be obviously synthetic, so a reader can see the
# name is injected rather than observed.
_FAKE_PID = 424242
_FAKE_TID = 777777

# The payload A is mid-way through writing. Long enough that an empty file is
# unmistakably not it, and self-identifying so a swap is unambiguous.
_A_PAYLOAD = b'{"handoff_id":"WRITER-A","seq":41,"task":"payload that A owns"}'


def _tmp_name_for(target_name: str) -> str:
    """The exact temp name `write_atomic` derives for the injected pid/tid."""
    return f".{target_name}.{_FAKE_PID}.{_FAKE_TID}.tmp"


def _count_unlinks(monkeypatch) -> list[Path]:
    """Record every `Path.unlink` for the duration of a test.

    Counting is necessary because asserting on file EXISTENCE cannot separate
    the two implementations: the sanctioned reclaim legitimately removes the
    file, so "still there" and "still A's" are different questions and only the
    second one has teeth.
    """
    seen: list[Path] = []
    real_unlink = Path.unlink

    def _recording_unlink(self, *a, **kw):
        seen.append(self)
        return real_unlink(self, *a, **kw)

    monkeypatch.setattr(Path, "unlink", _recording_unlink)
    return seen


def test_reclaim_never_deletes_a_live_writers_tmp(tmp_path, monkeypatch):
    """A second writer on the SAME temp name must not delete A's live file.

    THE HAZARD, precisely: the temp name is scoped to (pid, tid) and the OS
    REUSES both. A writer that crashed in a previous run can therefore leave
    behind exactly the name the current process is about to claim. If the
    current process is instead a SECOND LIVE writer that derived the same name,
    the reclaim unlinks a file another writer owns and is actively writing, and
    that writer's envelope is lost.

    An earlier draft judged this window "tiny". That may well be true and it is
    irrelevant: the size of a window is not a defence against unlinking another
    process's live file, which is the same defect one level up that this change
    already fixed on the open-failure path.
    """
    target_name = "H01WRITERA.json"
    tmp = tmp_path / _tmp_name_for(target_name)
    unlinks = _count_unlinks(monkeypatch)

    # ── Writer A: claims the name with O_EXCL and HOLDS it. No close, no
    #    replace. A is mid-write and is entitled to this name.
    fd_a = fe._open_exclusive_tmp(tmp)
    written = 0
    while written < len(_A_PAYLOAD):
        written += os.write(fd_a, _A_PAYLOAD[written:])
    os.fsync(fd_a)
    assert tmp.exists(), (
        "writer A never created the temp file — there is nothing for this test "
        "to protect, so it would pass vacuously"
    )

    # ── Writer B, deriving the IDENTICAL name. Must take the EEXIST branch.
    fd_b = None
    b_raised: BaseException | None = None
    try:
        fd_b = fe._open_exclusive_tmp(tmp)
    except BaseException as exc:  # noqa: BLE001 — outcome (a), reported not hidden
        b_raised = exc
    finally:
        if fd_b is not None:
            os.close(fd_b)

    # ── (5) Only two outcomes are acceptable: a clear error, or a recovery that
    #    left A alone. "Returned a descriptor" is acceptable ONLY if A's bytes
    #    are still on disk, which is asserted next. A silent success that
    #    destroyed A's data is the forbidden third outcome.
    if b_raised is not None:
        assert tmp.name in str(b_raised) or str(tmp) in str(b_raised), (
            "writer B failed, but not LEGIBLY: the exception does not name the "
            "temp file an operator would have to clear by hand. A hard failure "
            "that does not say what to clear is a different soft-fail. Got "
            f"{type(b_raised).__name__}: {b_raised}"
        )

    # ── (6) The reclaim is at most ONE unlink, and never one against a file a
    #    live writer still holds.
    tmp_unlinks = [p for p in unlinks if p == tmp]
    assert len(tmp_unlinks) <= 1, (
        f"the reclaim path unlinked {tmp.name} {len(tmp_unlinks)} times. One "
        "unlink is the sanctioned reclaim; two is a bug, because after the "
        "first the name may belong to a DIFFERENT live writer and the second "
        "destroys its file."
    )

    # ── (4) THE assertion with teeth. Existence alone is not enough — after an
    #    unlink-and-recreate the NAME is present again, pointing at a new, empty
    #    inode, while A's descriptor still holds the now-unlinked original.
    #    Only the CONTENT tells the two apart.
    assert tmp.exists(), (
        f"writer B DELETED a live writer's temp file. {tmp.name} is gone while "
        f"writer A holds an open descriptor on it and has written "
        f"{len(_A_PAYLOAD)} bytes. A's subsequent os.replace() will either "
        "raise FileNotFoundError or, worse, promote nothing at all: the "
        "envelope is lost. The reclaim cannot tell a crashed predecessor's "
        "debris from a live same-pid-same-tid writer, and unlinking it is only "
        "safe in the first case."
    )
    on_disk = tmp.read_bytes()
    assert on_disk == _A_PAYLOAD, (
        f"writer A's temp file no longer holds A's bytes. Expected "
        f"{_A_PAYLOAD!r}, found {on_disk!r}. This is the silent-success case: "
        "the reclaim removed A's inode and created a fresh empty file at the "
        "same name, so A's open descriptor writes into a file nothing will "
        "ever read, and B's empty file is what gets renamed into place."
    )

    os.close(fd_a)


def test_reclaim_race_loses_the_envelope_at_the_final_path(tmp_path):
    """The consequence, at the path the query path actually reads.

    The test above proves A's temp file is destroyed. This proves WHY THAT
    MATTERS: A's promotion step is `os.replace(tmp, path)`. Against a rebuilt
    empty temp file that replace SUCCEEDS — it moves zero bytes to the final
    path. The failure is not an exception anyone would notice. It is an
    envelope that reads as valid JSON and contains nothing.
    """
    target = tmp_path / "H01WRITERA.json"
    tmp = tmp_path / _tmp_name_for(target.name)

    # Writer A: claims the name and writes its payload.
    fd_a = fe._open_exclusive_tmp(tmp)
    written = 0
    while written < len(_A_PAYLOAD):
        written += os.write(fd_a, _A_PAYLOAD[written:])
    os.fsync(fd_a)

    # Writer B arrives on the identical name.
    fd_b = None
    b_raised: BaseException | None = None
    try:
        fd_b = fe._open_exclusive_tmp(tmp)
    except BaseException as exc:  # noqa: BLE001
        b_raised = exc
    if fd_b is not None:
        os.close(fd_b)
    os.close(fd_a)

    # If B declined loudly, A's temp file is untouched and A completes normally.
    # If B returned a descriptor, A is about to promote the WRONG bytes.
    os.replace(tmp, target)

    assert target.read_bytes() == _A_PAYLOAD, (
        f"the file at the final path holds {target.read_bytes()!r}, not writer "
        f"A's envelope { _A_PAYLOAD !r}. A's os.replace() succeeded while "
        "promoting a file A never wrote, so the envelope is silently empty at "
        f"the path the query path reads. (B {'raised ' + type(b_raised).__name__ if b_raised else 'returned a descriptor'})"
    )
    leftovers = sorted(p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp"))
    assert not leftovers, f"temp debris left behind: {leftovers}"


def test_reclaim_is_a_no_op_when_the_name_was_never_taken(tmp_path, monkeypatch):
    """The happy path unlinks NOTHING — not even its own file.

    The counterpart to the round-one bug, which cleaned up on EVERY failure
    path and so deleted a temp file the caller had no claim to. `write_atomic`
    owns the temp file only once O_EXCL has SUCCEEDED, so before that point any
    unlink is by definition an unlink of somebody else's file.
    """
    target = tmp_path / "cursor.json"
    unlinks = _count_unlinks(monkeypatch)

    fe.write_atomic(target, '{"cursor": "fresh"}')

    assert unlinks == [], (
        f"a successful write_atomic unlinked {unlinks}. A write that never hit "
        "EEXIST has no claim to any temp file; cleanup before O_EXCL succeeds "
        "is the unlink-another-process's-live-file defect."
    )
    assert json.loads(target.read_text()) == {"cursor": "fresh"}


def test_stale_leftover_with_no_live_owner_is_still_reclaimed(tmp_path, monkeypatch):
    """The reclaim must keep WORKING for a genuine crashed-predecessor leftover.

    This is the deliberate counterpart to the live-writer test above. Identical
    shape, one difference: nobody holds the name. If a fix for the live-writer
    case is ever written, THIS is the test that stops it from "solving" the bug
    by deleting the reclaim entirely — the failure mode of every tempting
    one-line answer.
    """
    target_name = "H01WRITERA.json"
    tmp = tmp_path / _tmp_name_for(target_name)
    stale_body = b'{"handoff_id":"CRASHED-PREDECESSOR", partial'
    tmp.write_bytes(stale_body)  # NO live owner: nobody has it open
    unlinks = _count_unlinks(monkeypatch)

    fd = fe._open_exclusive_tmp(tmp)
    try:
        assert tmp.exists()
        # The name now belongs to the NEW writer, so the stale bytes must be
        # gone — reclaim that leaves the old content in place has not reclaimed
        # anything, it has just appended.
        assert tmp.read_bytes() == b"", (
            f"the stale body survived the reclaim: {tmp.read_bytes()!r}. The "
            "new writer would publish a half-written predecessor's envelope."
        )
    finally:
        os.close(fd)

    tmp_unlinks = [p for p in unlinks if p == tmp]
    assert len(tmp_unlinks) == 1, (
        f"expected the reclaim to unlink the stale temp file exactly once, saw "
        f"{len(tmp_unlinks)}. Zero means the EEXIST branch did not run and this "
        "test proved nothing; two is the double-unlink bug."
    )


# ═══════════════════════════════════════════════════════════════════════════
# FIX 5 — an unparseable seq counter RAISES, and the raise says what to do
# ═══════════════════════════════════════════════════════════════════════════
#
# A hard failure with no stated remedy is a DIFFERENT soft-fail. The operator,
# under pressure, learns that the fix is to `rm` the file — and removing the
# counter re-issues every seq it had handed out, manufacturing the exact
# duplicate the whole counter exists to prevent. So the remedy is part of the
# contract, and it is asserted below like any other contract.

def test_unparseable_seq_counter_raises_and_names_the_remedy(tmp_path):
    """The raise must be legible: what broke, and what the operator must do."""
    seq_file = tmp_path / ".seq"
    corrupt = "forty-one\n"
    seq_file.write_text(corrupt)

    with pytest.raises(ValueError) as ei:
        fe.new_seq_file(seq_file)

    msg = str(ei.value)

    # (a) the offending file path
    assert str(seq_file) in msg, (
        f"the error does not name the counter file ({seq_file}). An operator "
        f"cannot act on a path they were never told. Message: {msg}"
    )
    # (b) the unreadable content
    assert "forty-one" in msg, (
        "the error does not show WHAT it read. The operator has to re-derive "
        f"the corruption by hand. Message: {msg}"
    )
    # (c) a remedy that survives pressure: quarantine, not delete; and
    #     reconcile against the on-disk maximum before re-enabling writes.
    low = msg.lower()
    for token, why in (
        ("quarantine", "the file must be preserved as evidence, not deleted"),
        ("reconcile", "the store must be reconciled against what is on disk"),
        ("on-disk", "the reconciliation target is the on-disk maximum seq"),
        ("re-issue", "the operator must be told WHY deletion is dangerous"),
    ):
        assert token in low, (
            f"the error message dropped {token!r} — {why}. A hard failure with "
            f"no stated remedy teaches the operator to `rm` the file under "
            f"pressure, which re-issues live seqs. Message: {msg}"
        )

    # The raise must not have side-effected the counter into a reset state.
    assert seq_file.read_text() == corrupt, (
        "new_seq_file modified the counter while raising. The raise must leave "
        "the evidence exactly as found, or the operator loses the artifact they "
        "need to diagnose it."
    )


# ═══════════════════════════════════════════════════════════════════════════
# FIX 3 — ordering is by seq, NOT by wall clock
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def store(tmp_path):
    st = fst.FederationStore(tmp_path / "handoffs")
    st.ensure_layout()
    return st


def _env(seq, target="makali", source="maat", task="t", created=None):
    return fe.build_envelope(
        seq=seq, task=task, source_entity=source, source_channel="opencode",
        target_entity=target, target_channel="opencode", source_session_id=SESSION,
        source_hardware="node0", sender_verified=True, created_at_utc=created,
    )


def test_query_orders_by_seq_not_timestamp(store):
    """seq wins even when created_at_utc is inverted.

    This host is America/St_Thomas (UTC-4) and the corpus already carries a
    13-hour spread, because some writer stamps naive LOCAL time into a field
    named `*_utc`. If ordering ever falls back to a timestamp, that bug stops
    being cosmetic and starts reordering the inbox. This test is the thing that
    makes the fallback impossible to ship quietly.
    """
    # seq=2 carries a DELIBERATELY EARLIER created_at_utc than seq=1.
    store.submit(_env(1, target="maat", created="2026-09-30T23:00:00+00:00"))
    store.submit(_env(2, target="maat", created="2020-01-01T00:00:00+00:00"))

    results = store.query(target_entity="maat")
    assert len(results) == 2
    assert results[0]["seq"] == 1, "ordering regressed to timestamp — the TZ bug is now load-bearing"
    assert results[1]["seq"] == 2, "ordering regressed to timestamp — the TZ bug is now load-bearing"


def test_query_order_survives_inverted_timestamps_under_backdated_writes(store):
    """Ordering is not an accident of filename order or of mtime.

    The scan is `sorted(glob("*.json"))` and the ULID is timestamp-sortable, so
    a name-ordered scan agrees with seq-ordering right up until a backdated or
    clock-skewed write lands. Here the LATER seq carries the EARLIER clock, so
    any sort key other than `seq` inverts the result.

    NOTE: an earlier draft of this test put the older clock on the older seq.
    That ordering is ALSO what a timestamp-sort produces, so the test passed
    against a deliberately mutated `query()` — a guard that cannot fail is
    decoration. The inversion is now deliberate in both directions.
    """
    store.submit(_env(10, target="maat", created="2026-09-30T00:00:00+00:00"))
    store.submit(_env(11, target="maat", created="2019-06-01T00:00:00+00:00"))
    results = store.query(target_entity="maat")
    assert [e["seq"] for e in results] == [10, 11], (
        f"a backdated envelope sorted ahead of a newer one — ordering is "
        f"timestamp-dependent, got {[e['seq'] for e in results]}"
    )


def test_utc_stamp_is_tz_aware():
    """Our own stamp function, asserted directly.

    A real assertion about OUR code, not a guard that trips on someone else's
    defect. `utc_stamp()` is the single sanctioned way to write a `*_utc`
    field, so its output parsing to a NAIVE datetime would be a bug here.
    """
    parsed = datetime.fromisoformat(fe.utc_stamp())
    assert parsed.tzinfo is not None, (
        "utc_stamp() produced a naive datetime — a local-time-as-UTC write is "
        "exactly the defect this module exists to prevent"
    )
    assert parsed.utcoffset().total_seconds() == 0, "utc_stamp() is not at UTC+00:00"
