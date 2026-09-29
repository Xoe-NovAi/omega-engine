# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Federation store: the single primitive behind `inbox`, `receipts`, and `list`.

R4's structural requirement: "list and inbox must be TWO PROJECTIONS OF ONE
PRIMITIVE, not two code paths." They drifted apart once already — `list` ignored
`target_entity` while every caller re-implemented filtering client-side. So
there is exactly one query function here and the three actions are thin
projections over it.

CURSOR: a cache, NOT a record.
--------------------------------
`read_by` on the envelope is the source of truth for "have I seen this". The
cursor is a daemon-owned file that exists only to avoid scanning. Therefore:
  * losing the cursor has ZERO correctness impact — it is a performance event;
  * that is why the cursor carries an EPOCH, so a caller can tell "reset" from
    "first run" from "store absent" instead of silently re-reading a week.

STORE-UNREACHABLE IS A TYPE, NOT A SENTIMENT.
---------------------------------------------
`query` raises `StoreUnreachable`. The MCP layer turns that into an error
object with `error.code = "store_unreachable"`. An empty result and an error are
structurally different values, because the natural caller is `if not entries:
pass` — which passes on BOTH. Asserting non-emptiness would not catch a bug
that returns one error record.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from . import federation_envelope as fe

# ── counters (R5). Malformed and unknown are SEPARATE. ───────────────────────

COUNTER_NAMES = (
    "session_id_supplied_total",
    "session_id_stamped_by_server_total",
    "session_id_malformed_total",
    "session_id_unknown_total",
)


class StoreUnreachable(RuntimeError):
    """The envelope store could not be read. NOT an empty result."""


class FederationStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.hot = self.root / fe.HANDOFF_HOT
        self.envelopes = self.root / fe.HANDOFF_ENVELOPES
        self.cold = self.root / fe.HANDOFF_COLD
        self.retired = self.root / fe.HANDOFF_RETIRED
        self.seq_file = self.root / ".seq"
        self.cursor_file = self.root / ".cursors.json"
        self.counters_file = self.root / ".counters.json"

    # ── layout ───────────────────────────────────────────────────────────────

    def ensure_layout(self) -> None:
        for d in (self.hot, self.envelopes, self.cold, self.retired):
            d.mkdir(parents=True, exist_ok=True)

    def _readable(self) -> bool:
        return self.root.is_dir() and self.hot.is_dir() and self.envelopes.is_dir()

    # ── the ONE primitive ────────────────────────────────────────────────────

    def query(self, *, target_entity: str | None = None,
              source_entity: str | None = None,
              since_seq: int | None = None,
              unread_for: str | None = None) -> list[dict]:
        """The single read path. `inbox`, `receipts` and `list` all call this.

        Raises StoreUnreachable — never returns [] for "could not read".
        """
        if not self._readable():
            raise StoreUnreachable(
                f"handoff store not readable at {self.root} "
                "(envelopes/ or hot/ missing)"
            )
        out: list[dict] = []
        try:
            for p in sorted(self.envelopes.glob("*.json")):
                env = self._load(p)
                if env is None:
                    continue
                if target_entity and env.get("target_entity") != target_entity:
                    continue
                if source_entity and env.get("source_entity") != source_entity:
                    continue
                if since_seq is not None and int(env.get("seq") or 0) <= since_seq:
                    continue
                if unread_for and not fe.unread_for(env, unread_for):
                    continue
                out.append(env)
        except OSError as exc:
            raise StoreUnreachable(f"envelope read failed: {exc}") from exc
        out.sort(key=lambda e: int(e.get("seq") or 0))
        return out

    @staticmethod
    def _load(path: Path) -> dict | None:
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return None

    # ── R1: inbox ────────────────────────────────────────────────────────────

    def inbox(self, entity: str, limit: int | None = None) -> dict:
        """Unread submissions addressed to THIS caller only.

        Never returns {entries: [], cursor_reset: True} — a reset with no entries
        is indistinguishable from genuinely no news. If there is an error it is
        an error object; if there are entries they are populated.
        """
        store = self.read_cursor(entity)
        entries = self.query(target_entity=entity, since_seq=store["max_seq_seen"],
                             unread_for=entity)
        if limit is not None:
            entries = entries[:limit]
        now = time.time()
        ages = [_age_seconds(e) for e in entries if _age_seconds(e) is not None]
        payload = {
            "entries": entries,
            "unread_count": len(entries),
            "oldest_unread_age": int(max(ages)) if ages else 0,
            "newest_submitted_at": entries[-1]["created_at_utc"] if entries else None,
            "cursor": store,
        }
        if store.get("reset_reason"):
            payload["reset_reason"] = store["reset_reason"]
        return payload

    # ── R2: receipts ─────────────────────────────────────────────────────────

    def receipts(self, entity: str) -> dict:
        """Every packet I SENT, with full state_history. Closes the sender loop."""
        return {"entries": self.query(source_entity=entity)}

    # ── R4: list ─────────────────────────────────────────────────────────────

    def list_packets(self, caller_entity: str, target_entity: str | None,
                     scope: str = "default") -> dict:
        """Filtered by target BY DEFAULT. Bare listing is not possible.

        A list that returns everything is a tool that INVITES the
        confident-false-negative failure mode GE-N1 hit: the caller reads an
        unbounded dump, concludes there is nothing for them, and is wrong.
        """
        if target_entity is None and scope != "all":
            raise ValueError(
                "list requires target_entity (or an explicit scope=all). "
                "A bare listing is not a legal query."
            )
        if scope == "all":
            self.bump("scope_all_optin_total")
            return {"entries": self.query(target_entity=None), "scope": "all",
                    "deprecated": "scope=all is deprecated and logged"}
        return {"entries": self.query(target_entity=target_entity), "scope": "default"}

    # ── cursor (R1) ──────────────────────────────────────────────────────────

    def read_cursor(self, entity: str) -> dict:
        data = self._load_cursor_file()
        rec = data.get("entities", {}).get(entity)
        if rec is None:
            return {"epoch": data.get("epoch"), "max_seq_seen": 0,
                    "reset_at": None, "reset_reason": "never_seen"}
        return rec

    def advance_cursor(self, entity: str, max_seq_seen: int) -> dict:
        data = self._load_cursor_file()
        rec = {"epoch": data["epoch"], "max_seq_seen": int(max_seq_seen),
               "reset_at": data.get("epoch_created_at"), "reset_reason": None}
        data.setdefault("entities", {})[entity] = rec
        fe.write_atomic(self.cursor_file, json.dumps(data, indent=2, sort_keys=True))
        return rec

    def _load_cursor_file(self) -> dict:
        if not self.cursor_file.is_file():
            return {"epoch": fe.new_handoff_id().lstrip("H"), "entities": {},
                    "epoch_created_at": fe.utc_stamp(), "reset_reason": "store_rebuilt"}
        try:
            data = json.loads(self.cursor_file.read_text())
        except (OSError, ValueError):
            # A corrupt cursor store is a REBUILD, and must say so. Silently
            # resetting is how an agent re-reads a week without knowing why.
            return {"epoch": fe.new_handoff_id().lstrip("H"), "entities": {},
                    "epoch_created_at": fe.utc_stamp(), "reset_reason": "store_rebuilt"}
        return data

    def rebuild_cursor_store(self) -> str:
        """New epoch. Every agent's next read sees epoch_mismatch."""
        epoch = fe.new_handoff_id().lstrip("H")
        fe.write_atomic(self.cursor_file, json.dumps(
            {"epoch": epoch, "entities": {}, "epoch_created_at": fe.utc_stamp(),
             "reset_reason": "store_rebuilt"}, indent=2, sort_keys=True))
        return epoch

    # ── seq + counters ───────────────────────────────────────────────────────

    def next_seq(self) -> int:
        return fe.new_seq_file(self.seq_file)

    def bump(self, name: str, n: int = 1) -> None:
        data = {}
        if self.counters_file.is_file():
            try:
                data = json.loads(self.counters_file.read_text())
            except (OSError, ValueError):
                data = {}
        data[name] = int(data.get(name, 0)) + n
        fe.write_atomic(self.counters_file, json.dumps(data, indent=2, sort_keys=True))

    def counters(self) -> dict:
        data = {}
        if self.counters_file.is_file():
            try:
                data = json.loads(self.counters_file.read_text())
            except (OSError, ValueError):
                data = {}
        for name in COUNTER_NAMES:
            data.setdefault(name, 0)
        return data

    # ── write path ───────────────────────────────────────────────────────────

    def submit(self, envelope: dict) -> dict:
        """Copy the envelope into envelopes/ — written at birth, NEVER moved."""
        self.ensure_layout()
        ok, why = fe.verify_envelope(envelope)
        if not ok:
            raise ValueError(f"refusing to store an unverifiable envelope: {why}")
        fe.write_atomic(self.envelopes / f"{envelope['handoff_id']}.json",
                        json.dumps(envelope, indent=2, sort_keys=True))
        return envelope


def _age_seconds(envelope: dict) -> int | None:
    try:
        from datetime import datetime, timezone
        created = datetime.fromisoformat(envelope["created_at_utc"])
        if created.tzinfo is None:
            return None
        return int((datetime.now(timezone.utc) - created).total_seconds())
    except (KeyError, ValueError):
        return None
