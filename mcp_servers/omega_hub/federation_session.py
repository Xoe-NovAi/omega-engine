# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""R5 — mandatory `session_id`, validated read-only, counted four ways.

WHY VALIDATION AND NOT JUST A REQUIRED FIELD
--------------------------------------------
12 malformed 16-character session ids exist in current gnoses. Every real
session id in `opencode.db` is exactly 30 characters. Those 12 are not pruned
sessions — they are truncated/legacy strings that never resolved to anything.
R5 without validation would *institutionalise* that class: make a field
mandatory that nobody checks, so the malformed population grows instead of
being caught.

GRANDFATHER, DON'T BREAK
------------------------
Legacy callers (`test_no_redis`, the fallback script) exist and are not going
away this cycle. So an unknown id is **stamped and flagged on the envelope**,
not rejected. Blocking a live agent over provenance metadata costs more than it
protects — the reader is the one M29 exists to protect, and the flag is what
tells THEM.

The flag lives ON THE ENVELOPE, visible to other agents, not only in a counter.
Metrics-only leaves the record looking clean to exactly the people who would
inspect it.

MALFORMED AND UNKNOWN ARE SEPARATE COUNTERS
------------------------------------------
Malformed is a typo class (wrong shape). Unknown is right-shaped but absent from
the DB, which may be a legitimately-pruned session. Merging them would make the
flip criterion unmeasurable.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from . import federation_envelope as fe

_DB = Path.home() / ".local/share/opencode/opencode.db"
_db_cache: dict[str, bool] = {}


def _lookup_readonly(session_id: str) -> bool | None:
    """Is this session in the DB? Opened READ-ONLY. None if unavailable.

    Read-only is not a nicety: the file is ~45GB and `mode=ro` is what makes an
    accidental write impossible rather than merely unlikely.
    """
    if session_id in _db_cache:
        return _db_cache[session_id]
    if not _DB.is_file():
        return None
    try:
        con = sqlite3.connect(f"file:{_DB}?mode=ro", uri=True, timeout=5)
        try:
            row = con.execute("SELECT 1 FROM session WHERE id=?", (session_id,)).fetchone()
            found = row is not None
        finally:
            con.close()
    except sqlite3.Error:
        return None
    _db_cache[session_id] = found
    return found


def resolve_session_id(supplied: str | None, *, bump, fallback_entity: str,
                       daemon_session_id: str | None = None) -> dict:
    """Validate, count, and decide. Returns the resolution record.

    `bump` is the store's counter incrementer, injected so this module has no
    import cycle with the store.

    The returned dict is echoed in the response so a caller can ALWAYS tell
    whether their id was the one recorded. Silent substitution is the same
    failure class as a silent post: the caller believes their provenance is
    recorded when it is not.
    """
    shape_ok, reason = fe.validate_session_id(supplied)

    if not shape_ok:
        if reason == "absent":
            bump("session_id_stamped_by_server_total")
        else:
            bump("session_id_malformed_total")
        resolved = daemon_session_id or f"ses_unstamped_{fe.utc_stamp()}"
        return {
            "session_id": resolved,
            "source": "server_stamped",
            "verified": False,
            "unverified_sender": True,
            "reason": reason,
            "note": "server-substituted id; YOUR id was not recorded",
        }

    found = _lookup_readonly(supplied)
    if found is False:
        bump("session_id_unknown_total")
        return {
            "session_id": supplied,
            "source": "caller",
            "verified": False,
            "unverified_sender": True,
            "reason": "unknown",
            "note": "well-formed but not found in opencode.db (may be pruned)",
        }

    bump("session_id_supplied_total")
    return {
        "session_id": supplied,
        "source": "caller",
        "verified": True,
        "unverified_sender": False,
        "reason": "ok" if found is not None else "db_unavailable_but_shape_valid",
    }


def flip_criterion(counters: dict, *, days_stable: int, distinct_caller_classes: int
                   ) -> dict:
    """Ma'at's Q3 flip criterion, evaluated. NOT auto-enforced.

    Requires ALL of:
      1. supplied ratio >= 0.99
      2. stable for 14 consecutive days (caller passes the observed window)
      3. malformed_total == 0
      4. >= 2 distinct caller classes observed

    Condition 4 is the one people skip. Right now the entire caller population
    for `post` is one agent through one script: a ratio of 1.0 measured from a
    single caller is not adoption, it is a sample of one.
    """
    supplied = int(counters.get("session_id_supplied_total", 0))
    stamped = int(counters.get("session_id_stamped_by_server_total", 0))
    malformed = int(counters.get("session_id_malformed_total", 0))
    unknown = int(counters.get("session_id_unknown_total", 0))
    total = supplied + stamped
    ratio = (supplied / total) if total else 0.0
    checks = {
        "ratio>=0.99": ratio >= 0.99,
        f"stable>={days_stable}d": days_stable >= 14,
        "malformed==0": malformed == 0,
        f"caller_classes>={distinct_caller_classes}": distinct_caller_classes >= 2,
    }
    return {
        "supplied_total": supplied,
        "stamped_by_server_total": stamped,
        "malformed_total": malformed,
        "unknown_total": unknown,
        "ratio": round(ratio, 4),
        "checks": checks,
        "flip_ready": all(checks.values()),
        "note": "flip is NOT automatic; it is a decision, and condition 4 exists "
                "so a sample of one cannot be mistaken for adoption",
    }
