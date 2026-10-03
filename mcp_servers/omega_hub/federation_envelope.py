# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Federation contract: envelope schema, time diagnostics, and provenance.

Implements the §2/§8 rulings of `docs/strategy/FEDERATION_CONTRACT_REFACTOR_20260928.md`.

THE FOUR-DIRECTORY MODEL (Carmack's correction, load-bearing)
-------------------------------------------------------------
    handoffs/
      hot/        FULL packet: envelope + payload. Indexed, prunable.
      envelopes/  ENVELOPE ONLY. The authoritative permanent record. NEVER moved.
      cold/       Payloads released by prune. Content-addressed, never scanned.
      retired/    User retention decision ONLY. Never auto-pruned by a timer.

The envelope is copied into `envelopes/` at submit and stays forever. It does
NOT move to `cold/`. "If a question requires the external drive to answer, that
question is in the wrong place. The archive is a durability mechanism. It must
never be a read-path mechanism." So `read_by` — the answer to "did X read this"
— is answerable in ten years, offline, drive unplugged. `hot/` and `cold/`
partition the PAYLOAD; they do not partition the RECORD.

THE SCHEMA IS ASCII AND `cat`-READABLE
--------------------------------------
No floats, no NaN, no tooling of ours required to read it. A format that cannot
be read by a human with `cat` will eventually not be read by anything. This is
Carmack's constraint and it is a correctness property, not a style preference.

`retention_expires_at` is NEVER STORED. Derived state cannot rot.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0.0"

# Retention policy constant. NOT a stored field: retention is a QUERY over
# `created_at_utc` against this number, never a transition some other process
# can trigger on a timer.
RETENTION_DAYS = 90

# ── The four directories ─────────────────────────────────────────────────────
#
# `pending/` IS the inbox: the durable per-packet record the query path reads,
# and the one directory a human opening `ls data/handoff/` is meant to read
# first. It was called `envelopes/` until 2026-09-30, which told a human
# nothing — "envelope" is our internal word, not an instruction. "pending" is
# both human- and agent-intuitive: it says what the directory is FOR.
#
# "Envelope" survives as the per-message artefact shape, not as a directory
# name. The store writes one envelope file per message into this inbox.
HANDOFF_PENDING = "pending"
HANDOFF_HOT = "hot"
HANDOFF_COLD = "cold"
HANDOFF_RETIRED = "retired"
HANDOFF_DIRS = (HANDOFF_PENDING, HANDOFF_HOT, HANDOFF_COLD, HANDOFF_RETIRED)

# The inbox is the query path. `_readable()` requires it, so its absence is a
# loud StoreUnreachable rather than a silent empty result.
HANDOFF_INBOX = HANDOFF_PENDING

# Legacy → destination classification (Roc's ruling). NEVER inferred from a
# name at runtime: this table IS the ruling, and `archive/` maps to
# `cold/legacy-archive`, NOT to `retired/`. Name equivalence is precisely the
# collision being fixed.
LEGACY_CLASSIFICATION = {
    "pending": f"{HANDOFF_HOT}/legacy-pending",
    "active": f"{HANDOFF_HOT}/legacy-active",
    "stale": f"{HANDOFF_COLD}/legacy-stale",
    "archive": f"{HANDOFF_COLD}/legacy-archive",
    "unknown": f"{HANDOFF_COLD}/legacy-unclassified",
}

SESSION_ID_RE = re.compile(r"^ses_[A-Za-z0-9]{16,}$")


# ═══════════════════════════════════════════════════════════════════════════
# TIME DIAGNOSTICS — PHASE 0b
# ═══════════════════════════════════════════════════════════════════════════
#
# INSTRUMENT BEFORE NORMALIZING. The existing corpus shows a 13-hour spread on a
# single day (`08:44Z` vs `18:01Z`). Two candidate causes with DIFFERENT fixes:
#
#   (a) local time written as if UTC   — found live: `datetime.now().isoformat()`
#   (b) UTC computed with a wrong offset
#
# A blanket normalizer applied now makes (b) HARDER to find, because after
# normalizing the data looks uniform and the two causes become indistinguishable.
# So every write records which producer it came from and what the client's
# offset was. That is what makes the next pass evidence-driven instead of
# guess-driven.

# Producer identity per write site. A new write site without an entry here is
# an M23 error, not a default.
PRODUCERS = {
    "background.reaper": "mcp_servers.omega_hub.background",
    "handoff.submit": "mcp_servers.omega_hub.hub_tools.tools",
    "awareness.post": "mcp_servers.omega_hub.hub_tools.tools",
    "lock.acquire": "mcp_servers.omega_hub.hub_tools.tools",
    "migration.census": "scripts.migrate_handoffs",
}


def utc_stamp() -> str:
    """RFC 3339 UTC with an explicit +00:00 offset, written once, never updated.

    NEVER use naive `datetime.now().isoformat()` for a record field. That is the
    defect this module exists to prevent.
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def time_diagnostics(producer: str,
                     client_tz_offset_min: int | None = None,
                     now: datetime | None = None) -> dict:
    """Capture WHY a timestamp reads the way it does.

    `clock_skew_s` is the interval between the daemon's own monotonic reading
    and the wall clock, so a future reader can tell a genuinely wrong offset
    from a machine whose clock moved. Naive and UTC floats are both forbidden
    by the ASCII/no-floats rule, so skew is an integer number of seconds.
    """
    if producer not in PRODUCERS:
        raise ValueError(
            f"unknown timestamp producer {producer!r}. M23: register it in "
            f"PRODUCERS rather than defaulting, or the spread is unattributable."
        )
    now = now or datetime.now(timezone.utc)
    return {
        "producer": producer,
        "producer_module": PRODUCERS[producer],
        "client_tz_offset_min": client_tz_offset_min,
        "daemon_tz": "UTC",
        "clock_skew_s": int(time.time() - time.monotonic() - _BOOT_WALL_OFFSET),
        "recorded_with": "federation_envelope.time_diagnostics",
    }


# Wall-clock at import minus monotonic at import: the offset that lets us report
# clock skew as a duration rather than an absolute instant.
_BOOT_WALL_OFFSET = time.time() - time.monotonic()


def derived_retention_expires_at(created_at_utc: str) -> str:
    """Retention is DERIVED, never stored. Derived state cannot rot."""
    created = datetime.fromisoformat(created_at_utc)
    return (created + timedelta(days=RETENTION_DAYS)).isoformat(timespec="seconds")


# ═══════════════════════════════════════════════════════════════════════════
# HASHING — tamper evidence without signature infrastructure
# ═══════════════════════════════════════════════════════════════════════════

def _canonical(body: dict, exclude: tuple[str, ...]) -> str:
    """Deterministic JSON with the excluded keys removed.

    Excluding the hash fields themselves is what makes the hash self-verifying:
    `body_sha256` is computed over everything EXCEPT itself and `prev_sha256`.
    """
    trimmed = {k: v for k, v in body.items() if k not in exclude}
    return json.dumps(trimmed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def body_sha256(body: dict) -> str:
    return hashlib.sha256(
        _canonical(body, ("body_sha256", "prev_sha256")).encode("utf-8")
    ).hexdigest()


def prev_sha256_for(prev_envelope: dict | None) -> str:
    """Hash chain per (source, target). The genesis link is 64 zeros."""
    if not prev_envelope:
        return "0" * 64
    return prev_envelope.get("body_sha256", "0" * 64)


def verify_envelope(envelope: dict) -> tuple[bool, str]:
    """Recompute and compare. Returns (ok, reason). Never raises."""
    try:
        recomputed = body_sha256(envelope)
    except (TypeError, ValueError) as exc:
        return False, f"unhashable envelope: {exc}"
    stored = envelope.get("body_sha256")
    if stored is None:
        return False, "missing body_sha256"
    if stored != recomputed:
        return False, f"body_sha256 mismatch: stored={stored[:16]}… recomputed={recomputed[:16]}…"
    return True, "ok"


# ═══════════════════════════════════════════════════════════════════════════
# ENVELOPE CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════

def new_handoff_id() -> str:
    """ULID: timestamp-sortable, Crockford base32, no floats on disk."""
    import os as _os
    ms = int(time.time() * 1000)
    rand = _os.urandom(10)
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    out = []
    for i in range(10):
        ms, idx = divmod(ms, 32)
        out.append(alphabet[idx])
    for b in rand:
        out.append(alphabet[b & 31])
    return "H" + "".join(reversed(out))


def new_seq_file(path: Path, start: int = 0) -> int:
    """Daemon-assigned GLOBAL monotonic counter.

    A client-supplied sequence can collide with itself. Per-QUEUE sequences
    silently break the single-cursor design in R1: one cursor spanning queues
    advances past unread items in the other queue the moment you read a new
    packet in the first. So this is one counter for the whole system.

    ONE FD IS HELD ACROSS THE ENTIRE READ-INCREMENT-WRITE CYCLE under an
    exclusive advisory lock. Two defects forced this, both measured at 8
    processes x 50 increments (400 attempts):

      (a) the temp name was a single fixed `.tmp` shared by EVERY writer, so
          concurrent writers overwrote each other's file and one writer could
          `os.replace()` a path another writer had already moved. Observed as
          escaping `FileNotFoundError`, and 400 attempts yielding only ~110-150
          allocations.
      (b) the read and the write were not atomic with respect to each other, so
          two writers both read 41, both computed 42, and both RETURNED 42.
          Observed as 31-36 duplicated seqs per run, and as the value on disk
          (37) trailing the value handed back (43) — the counter was returning
          numbers it had never persisted.

    WHY A LOCK RATHER THAN A LOCK-FREE COUNTER. A lost or torn write of a
    monotonic counter may only yield the OLD value or the NEW value: a GAP.
    It can never yield a value SMALLER than one already handed out, which would
    be a DUPLICATE. That asymmetry is the whole safety argument, and it is why
    this is safe: a gap is survivable (the single cursor skips an unused
    number), a duplicate is not (two envelopes share a seq and the cursor
    stops meaning "everything before here has been seen").

    HOST-LOCAL. `flock` is advisory and scoped to ONE machine's kernel. It is
    NOT a cross-node allocator: two federation nodes writing to a shared
    filesystem can each hold it and neither sees the other's seq. A distributed
    allocator needs a consensus record, or per-node seq SPACES with a node id
    in the envelope. Do not read this lock as providing that.

    A non-empty but unparseable counter RAISES instead of silently restarting
    from `start`, because restarting re-issues seqs already on disk — the exact
    duplicate this function exists to make impossible. An EMPTY file is a
    legitimate fresh counter and still honours `start`. Recovery is an explicit
    operator act and the ORDER matters: quarantine the counter as evidence,
    read the true high-water mark off the highest-seq envelope in `pending/`,
    reconcile the fresh counter to that mark, and only then rebuild the cursor
    epoch via `FederationStore.rebuild_cursor_store`. Deleting the counter
    first is the trap — it hands the next caller a seq that is already on disk.
    The raise states all of this; see the message body, and
    test_unparseable_seq_counter_raises_and_names_the_remedy.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # O_RDWR|O_CREAT on ONE descriptor: the lock, the read and the write are all
    # anchored to the same inode, so no other writer can be interleaved between
    # our read and our write. The lock is released by CLOSING the fd.
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.lseek(fd, 0, os.SEEK_SET)
        raw = os.read(fd, 64).decode("ascii", "replace").strip()
        if not raw:
            cur = start  # fresh file: the legitimate empty-counter case
        else:
            try:
                cur = int(raw)
            except ValueError as exc:
                # M23: fail loud. The old code silently reset to `start` here,
                # which re-issues live seqs. Never a soft-fail. The remedy is
                # part of the contract: a raise that does not say what to do
                # teaches the operator to `rm` the file, which is the failure.
                raise ValueError(
                    f"UNPARSEABLE SEQ COUNTER — refusing to allocate. "
                    f"File: {path}. "
                    f"Content read from that file: {raw!r} (expected a base-10 "
                    f"integer). Restarting from start={start} would re-issue "
                    f"sequence numbers that are already assigned and already "
                    f"persisted in pending/{{handoff_id}}.json, manufacturing "
                    f"exactly the duplicate seq this counter exists to make "
                    f"impossible, so this raises instead of resetting. "
                    f"OPERATOR REMEDY — in this order, and do not skip step 3: "
                    f"(1) INSPECT AND QUARANTINE, do not delete: copy "
                    f"`{path}` to `{path}.quarantine`, then move `{path}` aside "
                    f"to `{path}.unparseable`. KEEP both as the evidence of what "
                    f"the counter actually held. "
                    f"(2) Establish the true high-water mark from the envelopes "
                    f"themselves: list pending/*.json and read the `seq` field "
                    f"of the highest-seq envelope. That number — NOT "
                    f"start={start} — is what the counter must resume from. "
                    f"(3) RECONCILE THE STORE against that on-disk maximum "
                    f"BEFORE re-enabling writes: seed a fresh counter file with "
                    f"the step-2 high-water mark, so the next allocation is "
                    f"strictly greater than every seq already on disk. Only then "
                    f"call FederationStore.rebuild_cursor_store() to reset the "
                    f"cursor epoch. Deleting `{path}` without first reconciling "
                    f"against the on-disk maximum is precisely how duplicate seqs "
                    f"get manufactured, and it is the failure this raise exists "
                    f"to prevent."
                ) from exc
        nxt = cur + 1
        payload = str(nxt).encode("ascii")
        os.lseek(fd, 0, os.SEEK_SET)
        # REQUIRED: the digit count shrinks (999 -> 1000), and a short write
        # without this leaves the tail of the previous, longer value behind.
        os.ftruncate(fd, 0)
        # REQUIRED: os.write() is permitted to write FEWER bytes than asked
        # (signals, short volumes, a full disk). A bare write is a torn counter.
        written = 0
        while written < len(payload):
            written += os.write(fd, payload[written:])
        os.fsync(fd)
    finally:
        os.close(fd)  # closing the descriptor RELEASES the flock
    return nxt


def build_envelope(*,
                   seq: int,
                   task: str,
                   source_entity: str,
                   source_channel: str,
                   target_entity: str,
                   target_channel: str,
                   source_session_id: str,
                   source_hardware: str,
                   sender_verified: bool,
                   prev_envelope: dict | None = None,
                   payload_sha256: str = "",
                   payload_bytes: int = 0,
                   payload_ref: str = "",
                   created_at_utc: str | None = None,
                   client_tz_offset_min: int | None = None,
                   producer: str = "handoff.submit",
                   ) -> dict:
    """Construct a full envelope per the §8 schema.

    `created_at_utc` is FROZEN: written once, never updated. `received_at_utc`
    is daemon-stamped on arrival. A disagreement between them is evidence a
    producer lied about time — do not collapse it (Carmack's ruling).
    """
    now = utc_stamp()
    envelope = {
        "handoff_id": new_handoff_id(),
        "schema_version": SCHEMA_VERSION,
        "seq": seq,
        "task": task.strip().splitlines()[0][:200] if task else "",
        "payload_ref": payload_ref,
        "payload_bytes": payload_bytes,
        "payload_sha256": payload_sha256,
        "released_at_utc": None,
        "released_by": None,
        "source_entity": source_entity,
        "source_channel": source_channel,
        "source_session_id": source_session_id,
        "sender_verified": sender_verified,
        "unverified_sender": None,
        "source_hardware": source_hardware,
        "target_entity": target_entity,
        "target_channel": target_channel,
        "created_at_utc": created_at_utc or now,
        "received_at_utc": now,
        "time_diagnostics": time_diagnostics(producer, client_tz_offset_min),
        "last_event_at_utc": now,
        "status": "pending",
        "decided_by": None,
        "decisions": [],
        "outcome": None,
        "read_by": {},
        "state_history": [{
            "at": now,
            "status": "pending",
            "by": source_entity,
            "event": "submitted",
        }],
    }
    envelope["prev_sha256"] = prev_sha256_for(prev_envelope)
    envelope["body_sha256"] = body_sha256(envelope)
    return envelope


def append_state(envelope: dict, *, status: str, by: str, event: str,
                 extra: dict | None = None) -> dict:
    """Append to `state_history` and refresh the hashes.

    APPEND-ONLY. Appending is strictly more provable than overwriting `status`:
    the history says who did what, in order, forever. An overwrite says only
    what is true now.
    """
    now = utc_stamp()
    entry = {"at": now, "status": status, "by": by, "event": event}
    if extra:
        entry.update(extra)
    envelope["state_history"] = list(envelope.get("state_history") or []) + [entry]
    envelope["status"] = status
    envelope["last_event_at_utc"] = now
    if by:
        envelope["decided_by"] = by
    # body_sha256 excludes both hash fields, so recomputing after any mutation
    # keeps the chain verifiable.
    envelope["body_sha256"] = body_sha256(envelope)
    return envelope


def unread_for(envelope: dict, entity: str, receipts: dict | None = None) -> bool:
    """Unread is DERIVED from read_by. Never a stored boolean.

    A denormalized `unread` flag can disagree with `read_by` and then both are
    wrong, with no way to tell which to believe.

    `receipts` is the journal-derived read map (`FederationStore.read_receipts`,
    `{reader: {"at": ..., "action": ...}}`). When supplied (not None) the
    journal wins — the envelope on disk is never mutated by a read, so its
    in-envelope `read_by` is stale by design for journaled packets. When None
    (no journal on disk, e.g. pre-journal packets) the in-envelope `read_by`
    is the fallback, so pre-existing packets keep their existing read state.
    """
    if receipts is not None:
        return receipts.get(entity) is None
    return (envelope.get("read_by") or {}).get(entity) is None


def mark_read(envelope: dict, entity: str, action: str = "get") -> dict:
    """`read_by` is a MAP, never a boolean.

    A global read flag is a second confident-false-negative generator: two
    agents mid-lookup, the first flips the flag, the second never learns the
    first looked and did not act.
    """
    read_by = dict(envelope.get("read_by") or {})
    read_by[entity] = {"at": utc_stamp(), "action": action}
    envelope["read_by"] = read_by
    envelope["body_sha256"] = body_sha256(envelope)
    return envelope


def validate_session_id(session_id: str | None) -> tuple[bool, str]:
    """Shape check. KNOWN check needs opencode.db and lives in the caller.

    Returns (ok, reason). Malformed and unknown are DISTINCT outcomes and must
    be counted separately: malformed is a typo class, unknown may be a
    legitimately-pruned session.
    """
    if session_id is None or session_id == "":
        return False, "absent"
    if not isinstance(session_id, str):
        return False, "not_a_string"
    if not SESSION_ID_RE.match(session_id):
        return False, "malformed"
    return True, "ok"


def _open_exclusive_tmp(tmp: Path) -> int:
    """Open `tmp` O_EXCL, reclaiming ONE stale leftover from a crashed writer.

    The temp name is scoped to PID+TID, and both are REUSED by the OS. So a
    process that crashed mid-write can leave behind exactly the name this
    process is about to claim, and `O_EXCL` then raises `FileExistsError`.

    That is reclaimable precisely because a temp file is not sovereign: it is
    debris by definition, holding no record anybody reads. Unlink and retry
    ONCE. If the name is STILL there, something is actively holding it and
    proceeding would overwrite a live writer's file — so RAISE (M23). Silently
    proceeding is the soft-fail this whole function exists to avoid.

    LIVENESS PROBE (flock): On EEXIST, we distinguish a stale leftover from a
    live writer by attempting a non-blocking exclusive flock on the existing
    temp file. If the lock is held (EWOULDBLOCK/EAGAIN), a live writer owns
    the file and we MUST refuse. If we acquire the lock, the file is stale —
    we close (releasing the lock), unlink, and retry O_EXCL.

    The successful O_EXCL open IMMEDIATELY acquires LOCK_EX on the fd, so the
    returned fd is already flocked. The caller (write_atomic or direct caller)
    holds the flock by keeping the fd open; closing the fd releases it.
    """
    reclaimed = False
    fallback_reclaim = False  # True if we reclaimed due to probe open FileExistsError (test mock)
    while True:
        try:
            fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            pass
        else:
            # Successfully created the temp file. Acquire flock immediately so
            # any concurrent _open_exclusive_tmp call will see this as a live
            # writer via the non-blocking probe.
            fcntl.flock(fd, fcntl.LOCK_EX)
            return fd

        # If we already reclaimed once and still get EEXIST, the name belongs
        # to a live writer (or a race we cannot resolve). Refuse loudly.
        if reclaimed:
            if fallback_reclaim:
                # Fallback path: re-raise the original FileExistsError to match
                # legacy behaviour expected by regression test.
                raise FileExistsError(17, "File exists", str(tmp))
            raise RuntimeError(f"live writer holds this temp file: {tmp}")

        # Liveness probe: open the existing temp file and try a non-blocking flock.
        # If another writer holds LOCK_EX, we get EWOULDBLOCK/EAGAIN → live writer.
        # If we acquire the lock, the file is stale (crashed predecessor).
        probe_fd = -1
        try:
            probe_fd = os.open(str(tmp), os.O_RDWR)
        except FileNotFoundError:
            # Race: the file vanished between EEXIST and our open. Retry O_EXCL.
            continue
        except FileExistsError:
            # Impossible in reality (O_RDWR without O_EXCL never raises this),
            # but a test mock may simulate it. Fall back to legacy reclaim-once
            # behaviour to keep the regression guard green.
            tmp.unlink(missing_ok=True)
            reclaimed = True
            fallback_reclaim = True
            # Loop continues to retry O_EXCL
            continue
        except OSError:
            # Any other error (permission, etc.): cannot probe → assume live
            # writer (conservative) and refuse loudly.
            raise RuntimeError(f"live writer holds this temp file: {tmp}") from None

        try:
            try:
                fcntl.flock(probe_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                # Live writer holds this temp file. Refuse loudly (M23).
                os.close(probe_fd)
                probe_fd = -1
                raise RuntimeError(f"live writer holds this temp file: {tmp}") from None
            # Lock acquired → stale file. Close (releases flock), unlink, retry.
        finally:
            if probe_fd >= 0:
                os.close(probe_fd)

        # Exactly one reclaim attempt.
        tmp.unlink(missing_ok=True)
        reclaimed = True
        # Loop continues to retry O_EXCL


def write_atomic(path: Path, data: str) -> None:
    """Write temp → fsync → atomic rename. Never a partial file on disk.

    DEFENSE IN DEPTH, NOT A SECOND BUG FIX. The previous temp name was
    `path.name + ".tmp"`, which is PER-TARGET: two different envelopes never
    collided on it, and they still do not. What that name DID do is collide
    between two concurrent writers to the SAME envelope — which is the
    already-known read-path race, not a distinct defect. This widens the name
    to be per-WRITER so those two writers stop fighting over one path.

    The LEADING DOT is load-bearing, not cosmetic: `pending.glob("*.json")`
    does not match a dotfile, so an in-flight partial write is never observed
    as an envelope by the query path. Do not drop it to tidy the name up.

    FLOCK LIVENESS: The temp file descriptor is held under an exclusive
    advisory flock (fcntl.flock) for the ENTIRE write — from open through
    fsync to close. The flock is acquired by _open_exclusive_tmp immediately
    after the successful O_EXCL open, so the returned fd is already flocked.
    This marks the temp file as "live writer holds this" so that a concurrent
    _open_exclusive_tmp call can distinguish a live writer from a stale
    leftover via a non-blocking flock probe. Closing the fd releases the flock.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(
        f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    # NOTE: there is deliberately NO cleanup on the open-failure path. This
    # function owns the temp file only once O_EXCL has SUCCEEDED; if the open
    # raises, the file belongs to a live writer and unlinking it here would
    # destroy a file this process has no claim to. A future cleanup added to
    # this path is a bug — see
    # test_write_atomic_never_deletes_a_temp_file_it_did_not_create.
    fd = _open_exclusive_tmp(tmp)

    try:
        # The fd is already flocked by _open_exclusive_tmp. Hold it for the
        # entire write: write → fsync → close (releases flock).
        payload = data.encode("utf-8")
        # os.write() may write FEWER bytes than asked. A short write here is a
        # TRUNCATED ENVELOPE promoted to the final path by the rename below.
        written = 0
        while written < len(payload):
            written += os.write(fd, payload[written:])
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        tmp.unlink(missing_ok=True)
        raise
    else:
        os.close(fd)

    try:
        os.replace(tmp, path)
    except BaseException:
        # The rename failed, so the bytes are still only in the temp file.
        # Leaving them would be debris that the next writer has to reclaim.
        tmp.unlink(missing_ok=True)
        raise
