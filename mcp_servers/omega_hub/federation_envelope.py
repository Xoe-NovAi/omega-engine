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

import hashlib
import json
import os
import re
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
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        cur = int(path.read_text().strip() or start)
    except (OSError, ValueError):
        cur = start
    nxt = cur + 1
    tmp = path.with_suffix(".tmp")
    tmp.write_text(str(nxt))
    os.replace(tmp, path)  # atomic
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


def unread_for(envelope: dict, entity: str) -> bool:
    """Unread is DERIVED from read_by. Never a stored boolean.

    A denormalized `unread` flag can disagree with `read_by` and then both are
    wrong, with no way to tell which to believe.
    """
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


def write_atomic(path: Path, data: str) -> None:
    """Write temp → fsync → atomic rename. Never a partial file on disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
