# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
import anyio
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DualWriteEntry:
    canonical_path: Path
    active_path: Path
    full_content: str
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_id: str = ""


class DualWriteError(Exception):
    """Base exception for dual-write operations."""

    pass


class JournalWriteError(DualWriteError):
    """Failed to write to journal."""

    pass


class TargetWriteError(DualWriteError):
    """Failed to write to canonical or active target."""

    pass


class RecoveryError(DualWriteError):
    """Failed to recover pending writes."""

    pass


async def write_dual(entry: DualWriteEntry) -> None:
    """
    Atomic dual-write: single call, zero mental overhead.

    Args:
        entry: DualWriteEntry with paths, content, summary, and trace_id

    Raises:
        JournalWriteError: If journal append fails
        TargetWriteError: If canonical/active write fails
    """
    journal_path = entry.canonical_path.parent / ".dual_write_journal.jsonl"

    journal_line = (
        json.dumps(
            {
                "canonical": str(entry.canonical_path),
                "active": str(entry.active_path),
                "full": entry.full_content,
                "summary": entry.summary,
                "ts": entry.timestamp,
                "trace": entry.trace_id,
                "status": "pending",
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    try:
        await anyio.to_thread.run_sync(_append_atomic, journal_path, journal_line)
        logger.debug(f"Journal appended for trace {entry.trace_id}")
    except Exception as e:
        logger.error(f"Failed to write journal for trace {entry.trace_id}: {e}")
        raise JournalWriteError(f"Journal write failed: {e}") from e

    try:
        await _split_journal_entry(journal_path, entry)
        logger.info(f"Dual-write completed for trace {entry.trace_id}")
    except Exception as e:
        logger.error(f"Dual-write split failed for trace {entry.trace_id}: {e}")
        raise TargetWriteError(f"Target write failed: {e}") from e


def _append_atomic(path: Path, line: str) -> None:
    """Append line to file atomically via tmp-rename."""
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(line, encoding="utf-8")
        if path.exists():
            with open(path, "ab") as f:
                f.write(line.encode("utf-8"))
        else:
            tmp.rename(path)
    except OSError as e:
        logger.error(f"Atomic append failed for {path}: {e}")
        raise JournalWriteError(f"Atomic append failed: {e}") from e


async def _split_journal_entry(journal_path: Path, entry: DualWriteEntry) -> None:
    """Write both targets atomically."""
    canon_tmp = entry.canonical_path.with_suffix(".tmp")
    try:
        await anyio.to_thread.run_sync(
            lambda: canon_tmp.write_text(entry.full_content, encoding="utf-8")
        )
        await anyio.to_thread.run_sync(canon_tmp.rename, entry.canonical_path)
        logger.debug(f"Canonical written: {entry.canonical_path}")
    except Exception as e:
        logger.error(f"Canonical write failed for {entry.canonical_path}: {e}")
        raise TargetWriteError(f"Canonical write failed: {e}") from e

    active_tmp = entry.active_path.with_suffix(".tmp")
    try:
        await anyio.to_thread.run_sync(
            lambda: active_tmp.write_text(entry.summary, encoding="utf-8")
        )
        await anyio.to_thread.run_sync(active_tmp.rename, entry.active_path)
        logger.debug(f"Active written: {entry.active_path}")
    except Exception as e:
        logger.error(f"Active write failed for {entry.active_path}: {e}")
        raise TargetWriteError(f"Active write failed: {e}") from e

    complete_line = (
        json.dumps({"ts": entry.timestamp, "trace": entry.trace_id, "status": "complete"}) + "\n"
    )
    try:
        await anyio.to_thread.run_sync(_append_atomic, journal_path, complete_line)
        logger.debug(f"Journal marked complete for trace {entry.trace_id}")
    except Exception as e:
        logger.error(f"Failed to mark journal complete for trace {entry.trace_id}: {e}")
        raise JournalWriteError(f"Journal completion failed: {e}") from e


async def recover_pending_writes(journal_dir: Path) -> None:
    """Run at engine startup. Replays incomplete journal entries."""
    journal_path = journal_dir / ".dual_write_journal.jsonl"
    if not journal_path.exists():
        logger.debug(f"No journal found at {journal_path}")
        return

    try:
        lines = await anyio.to_thread.run_sync(lambda: journal_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to read journal at {journal_path}: {e}")
        raise RecoveryError(f"Journal read failed: {e}") from e

    pending: dict[str, dict] = {}

    for line_num, line in enumerate(lines.strip().split("\n"), 1):
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            logger.warning(f"Skipping malformed journal line {line_num}: {e}")
            continue

        trace = entry.get("trace", f"unknown_line_{line_num}")
        if entry.get("status") == "pending":
            pending[trace] = entry
        elif entry.get("status") == "complete" and trace in pending:
            del pending[trace]

    if not pending:
        logger.info("No pending writes to recover")
        return

    logger.info(f"Recovering {len(pending)} pending writes")

    # Replay pending
    for trace, entry in pending.items():
        try:
            canon_tmp = Path(entry["canonical"]).with_suffix(".tmp")
            active_tmp = Path(entry["active"]).with_suffix(".tmp")
            await anyio.to_thread.run_sync(
                lambda: canon_tmp.write_text(entry["full"], encoding="utf-8")
            )
            await anyio.to_thread.run_sync(canon_tmp.rename, entry["canonical"])
            await anyio.to_thread.run_sync(
                lambda: active_tmp.write_text(entry["summary"], encoding="utf-8")
            )
            await anyio.to_thread.run_sync(active_tmp.rename, entry["active"])
            logger.info(f"Recovered pending write for trace {trace}")
        except Exception as e:
            logger.error(f"Failed to recover pending write for trace {trace}: {e}")
            raise RecoveryError(f"Recovery failed for trace {trace}: {e}") from e

    logger.info(f"Recovery complete: {len(pending)} writes restored")
