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
import os
import sqlite3
import time
from pathlib import Path

from . import federation_envelope as fe

# ── receipt journal (P0 FIX 2) ────────────────────────────────────────────
#
# Read state lives in an APPEND-ONLY sidecar, not in the envelope. Each
# packet `X.json` gets a sibling `X.receipts.jsonl`: one JSON object per
# line per read event. The envelope is NEVER mutated by a read — pure
# addition, which is why this needs no mandate change (M28-clean).
#
# A single receipt line is ~120 bytes: atomic on local ext4 well under
# PIPE_BUF, so no lock is needed for the append itself. Every write is
# fsynced (a receipt that vanishes on crash is a lost acknowledgement), and
# a write failure RAISES loudly (M23) — never swallowed.

#: Sibling suffix: packet `pending/X.json` -> journal `pending/X.receipts.jsonl`.
#: `pending.glob("*.json")` never matches it, so the query scan is unaffected.
RECEIPT_SUFFIX = ".receipts.jsonl"

#: Debug key carrying the count of skipped corrupt journal lines. Present
#: ONLY when at least one line was skipped, so a clean journal reads back as
#: exactly the reader map (no phantom entry beside real readers).
RECEIPT_SKIPPED_DEBUG_KEY = "_skipped_corrupt_lines"

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
        # `pending` is the inbox AND the query path: one directory, one truth.
        # Renaming it here means `tools.py`'s by-value `HANDOFF_PENDING` and
        # this store's read path can no longer disagree.
        self.pending = self.root / fe.HANDOFF_PENDING
        self.hot = self.root / fe.HANDOFF_HOT
        self.cold = self.root / fe.HANDOFF_COLD
        self.retired = self.root / fe.HANDOFF_RETIRED
        self.seq_file = self.root / ".seq"
        self.cursor_file = self.root / ".cursors.json"
        self.counters_file = self.root / ".counters.json"

    # ── layout ───────────────────────────────────────────────────────────────

    def ensure_layout(self) -> None:
        for d in (self.pending, self.hot, self.cold, self.retired):
            d.mkdir(parents=True, exist_ok=True)

    def _readable(self) -> bool:
        return self.root.is_dir() and self.pending.is_dir() and self.hot.is_dir()

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
                f"handoff inbox not readable at {self.root} "
                "(pending/ or hot/ missing)"
            )
        out: list[dict] = []
        try:
            for p in sorted(self.pending.glob("*.json")):
                env = self._load(p)
                if env is None:
                    continue
                if target_entity and env.get("target_entity") != target_entity:
                    continue
                if source_entity and env.get("source_entity") != source_entity:
                    continue
                if since_seq is not None and int(env.get("seq") or 0) <= since_seq:
                    continue
                if unread_for:
                    receipts = None
                    journal = self._receipt_path_for(p)
                    try:
                        if journal.is_file():
                            receipts = self._parse_receipt_journal(journal)
                    except OSError as exc:
                        raise StoreUnreachable(
                            f"envelope read failed: {exc}") from exc
                    # receipts=None -> no journal on disk -> in-envelope fallback.
                    # receipts=dict  -> journal wins, even when empty.
                    if not fe.unread_for(env, unread_for, receipts=receipts):
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

    # `scope=all` is deprecated, NOT removed. "Deprecated" without a date is a
    # euphemism for permanent: nobody ever revisits a deprecation with no
    # deadline, and the opt-in counter keeps ticking. Carmack's review note.
    SCOPE_ALL_REMOVAL_DATE = "2026-12-31"

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
            return {
                "entries": self.query(target_entity=None),
                "scope": "all",
                "deprecated": True,
                "removal_date": self.SCOPE_ALL_REMOVAL_DATE,
                "optin_count": self.counters().get("scope_all_optin_total", 0),
                "note": (
                    f"scope=all is deprecated and will be REMOVED on "
                    f"{self.SCOPE_ALL_REMOVAL_DATE}. It is logged so the "
                    "deprecation decision is evidence-based: when the removal "
                    "date arrives, the opt-in count says whether anyone is "
                    "still relying on it. Pass target_entity instead."
                ),
            }
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
        fe.write_atomic(self.pending / f"{envelope['handoff_id']}.json",
                        json.dumps(envelope, indent=2, sort_keys=True))
        return envelope

    # ── receipt journal (P0 FIX 2): read state without mutating envelopes ──

    @staticmethod
    def _receipt_path_for(packet_path: Path) -> Path:
        """Sibling journal: `pending/X.json` -> `pending/X.receipts.jsonl`."""
        return packet_path.with_name(packet_path.stem + RECEIPT_SUFFIX)

    def _find_by_any_id_path(self, packet_id: str) -> Path | None:
        """Dual-key lookup: match EITHER `handoff_id` OR `packet_id`.

        Direct path first (`pending/{id}.json`), then a SINGLE linear scan.
        Returns the Path — callers derive the journal from it, so there is NO
        re-lookup and NO second scan inside the critical section.

        Raises StoreUnreachable when the store itself is unreadable (never a
        silent empty answer). Returns None when no packet matches.
        """
        if not self._readable():
            raise StoreUnreachable(
                f"handoff inbox not readable at {self.root} "
                "(pending/ or hot/ missing)"
            )
        # A caller-supplied id must never escape the store: the scan below
        # only ever matches files already under pending/.
        if "/" not in packet_id and "\\" not in packet_id and ".." not in packet_id:
            try:
                direct = self.pending / f"{packet_id}.json"
                if direct.is_file():
                    return direct
            except OSError as exc:
                raise StoreUnreachable(f"envelope read failed: {exc}") from exc
        try:
            files = sorted(self.pending.glob("*.json"))
        except OSError as exc:
            raise StoreUnreachable(f"envelope read failed: {exc}") from exc
        for p in files:
            env = self._load(p)
            if env is None:
                continue
            if env.get("handoff_id") == packet_id or env.get("packet_id") == packet_id:
                return p
        return None

    def record_read_receipt(self, packet_id: str, reader_key: str,
                            action: str = "read") -> dict | None:
        """Append one read receipt to the packet's sidecar journal.

        Returns the envelope (loaded from disk, NEVER mutated) so the caller
        can echo what was read. Returns None when no packet matches
        `packet_id` — the caller turns that into `not_found`, never into a
        delivery to some other packet (M23).

        Write path: O_APPEND single-line write (~120 bytes, atomic on local
        ext4 under PIPE_BUF — no lock on the append path) + fsync on the fd.
        A write failure RAISES (RuntimeError) — never swallowed, never a soft
        `invalid_request`. Works on legacy packets (packet_id only, no
        handoff_id, no body_sha256) that `submit()` would refuse.
        """
        found = self._find_by_any_id_path(packet_id)
        if found is None:
            return None
        journal = self._receipt_path_for(found)
        record = {"reader": reader_key, "action": action,
                  "at": fe.utc_stamp(), "handoff_id": packet_id}
        line = (json.dumps(record, sort_keys=True, separators=(",", ":"))
                + "\n").encode("utf-8")
        try:
            fd = os.open(str(journal), os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                         0o644)
        except OSError as exc:
            raise RuntimeError(
                f"receipt journal open failed for {packet_id}: {exc}") from exc
        try:
            written = 0
            while written < len(line):
                n = os.write(fd, line[written:])
                if n == 0:  # pragma: no cover — defensive
                    raise RuntimeError(
                        f"receipt journal short write for {packet_id}: "
                        "os.write returned 0")
                written += n
            # NOT optional: a receipt that vanishes on crash is a lost
            # acknowledgement. The cost of one fsync per receipt is
            # proportionate to the value of the record.
            os.fsync(fd)
        except OSError as exc:
            raise RuntimeError(
                f"receipt journal append failed for {packet_id}: {exc}") from exc
        finally:
            os.close(fd)
        return self._load(found)

    @staticmethod
    def _parse_receipt_journal(journal: Path) -> dict:
        """Reconstruct `{reader: {"at": ..., "action": ...}}`, last-writer-wins.

        A corrupt line skips THAT LINE, never the whole read; skipped lines
        are counted under the debug key (present only when nonzero).
        """
        readers: dict = {}
        skipped = 0
        try:
            text = journal.read_text()
        except FileNotFoundError:
            return {}
        except OSError as exc:
            raise StoreUnreachable(f"envelope read failed: {exc}") from exc
        for raw in text.splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
            except ValueError:
                skipped += 1
                continue
            reader = obj.get("reader") if isinstance(obj, dict) else None
            if not isinstance(reader, str) or not reader:
                skipped += 1
                continue
            readers[reader] = {"at": obj.get("at"),
                               "action": obj.get("action", "read")}
        if skipped:
            readers[RECEIPT_SKIPPED_DEBUG_KEY] = skipped
        return readers

    def read_receipts(self, packet_id: str) -> dict:
        """Read state for one packet, journal-derived. `{}` when none recorded.

        Never raises for a missing packet or a missing journal — "nobody has
        read this" is a legitimate empty state, not an error. A corrupt line
        is skipped and counted, never fatal (see `_parse_receipt_journal`).
        """
        found = self._find_by_any_id_path(packet_id)
        if found is None:
            return {}
        return self._parse_receipt_journal(self._receipt_path_for(found))


def _age_seconds(envelope: dict) -> int | None:
    try:
        from datetime import datetime, timezone
        created = datetime.fromisoformat(envelope["created_at_utc"])
        if created.tzinfo is None:
            return None
        return int((datetime.now(timezone.utc) - created).total_seconds())
    except (KeyError, ValueError):
        return None
