# 🔱 Unified Forensic Ledger (UFL)
# AP: AP-UFL-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ ufl ⬡ OBSERVABILITY
#
# JSONL-based forensic ledger for persistent error/event recording.
# Captures all "Silent 200" events, circuit breaker state transitions,
# and other forensic-worthy events to a daily-rotated JSONL file.
#
# [M9 Error Integrity] — Every error is typed, traceable, and persisted.
# [M22 Response Provenance] — Every event records the actual provider.
#
# [id-soft: vet-008] Zone Memory — memory tagging pattern: each ledger
# entry carries a zoneid for integrity validation on replay.


# DocRef: docs/explanation/metrics-pipeline.md
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from omega.constants import ZONEID_TRACE

logger = logging.getLogger(__name__)


class UFLWriter:
    """Unified Forensic Ledger — append-only JSONL event store.

    Writes structured JSONL entries to daily-rotated files at
    ``DATA_DIR / observability / forensic / {date}.jsonl``.

    Each entry carries:
      - zoneid (integrity marker)
      - timestamp (ISO 8601 UTC)
      - trace_id (correlation token)
      - provider (actual provider name per M22)
      - event_type (typed event classifier)
      - payload (arbitrary structured data)

    Usage::

        ledger = UFLWriter()
        ledger.write("silent_200", provider="firecrawl", payload={
            "status_code": 200,
            "body_sample": "...",
            "error_signature": "quota_exceeded",
        })
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        rotate_daily: bool = True,
    ):
        self._data_dir = (data_dir or Path(
            os.environ.get(
                "OMEGA_DATA_DIR",
                str(Path(__file__).resolve().parent.parent.parent.parent / "data")
            )
        )) / "observability" / "forensic"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._rotate_daily = rotate_daily
        self._current_date: Optional[str] = None
        self._file_handle = None

    # ── Public API ─────────────────────────────────────────────────

    def write(
        self,
        event_type: str,
        trace_id: str,
        provider: str = "unknown",
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Write a single entry to the forensic ledger.

        Args:
            event_type: Typed event classifier (e.g. "silent_200",
                "breaker_open", "rate_limit").
            trace_id: Correlation token across the interaction chain.
            provider: Actual provider name that generated the event.
            payload: Arbitrary structured data describing the event.
        """
        entry = {
            "_zoneid": ZONEID_TRACE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "provider": provider,
            "event_type": event_type,
            "payload": payload or {},
        }
        self._append_entry(entry)

    def write_error(
        self,
        error: Exception,
        trace_id: str,
        provider: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Write an error entry to the forensic ledger.

        Shorthand for ``write("error", ...)`` with structured error info.
        """
        self.write(
            event_type="error",
            trace_id=trace_id,
            provider=provider,
            payload={
                "error_type": type(error).__name__,
                "error_message": str(error)[:500],
                "context": context or {},
            },
        )

    def write_breaker_event(
        self,
        provider: str,
        trace_id: str,
        from_state: str,
        to_state: str,
        reason: str = "",
    ) -> None:
        """Write a circuit breaker state transition to the ledger."""
        self.write(
            event_type="breaker_transition",
            trace_id=trace_id,
            provider=provider,
            payload={
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason[:200],
            },
        )

    def flush(self) -> None:
        """Flush the current file handle."""
        if self._file_handle is not None:
            self._file_handle.flush()
            os.fsync(self._file_handle.fileno())

    def close(self) -> None:
        """Close the current file handle."""
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None

    def read_recent(
        self,
        max_entries: int = 100,
        event_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Read the most recent entries from today's ledger.

        Args:
            max_entries: Maximum entries to return.
            event_type: Optional filter by event type.

        Returns:
            List of parsed JSON entries, most recent first.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        path = self._data_dir / f"{today}.jsonl"
        if not path.exists():
            return []

        entries: List[Dict[str, Any]] = []
        try:
            with open(str(path), "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if event_type is None or entry.get("event_type") == event_type:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except OSError as e:
            logger.error(f"Failed to read forensic ledger {path}: {e}")
            return []

        # Most recent first
        entries.reverse()
        return entries[:max_entries]

    # ── Internal ───────────────────────────────────────────────────

    def _get_current_path(self) -> Path:
        """Get the daily-rotated file path."""
        if self._rotate_daily:
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            date_str = "forensic"
        return self._data_dir / f"{date_str}.jsonl"

    def _append_entry(self, entry: Dict[str, Any]) -> None:
        """Append a JSON line to the daily forensic file."""
        path = self._get_current_path()
        try:
            with open(str(path), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except OSError as e:
            logger.error(f"Failed to write forensic ledger entry: {e}")


# ── Module-level singleton ───────────────────────────────────────────
_writer: Optional[UFLWriter] = None


def get_ufl_writer() -> UFLWriter:
    """Get or create the module-level UFL writer singleton."""
    global _writer
    if _writer is None:
        _writer = UFLWriter()
    return _writer
