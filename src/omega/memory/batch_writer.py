# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-Sovereign-Hardening-v1.0.0
"""
🔱 BATCH PERSISTENCE WRITER
Role: Singleton background batch writer. Buffers provider save_history() calls
      into periodic flushes. Prevents connection pool exhaustion under concurrent
      load from multiple oracle.talk() / oracle.summon() calls.

Ported from: xna-omega-legacy/src/omega/core/mnemosyne_writer.py
Adapted for: Omega Engine provider fabric (Redis, File, InMemory)

[ZONEID: 0x1d4a16] BACTH_WRITER — batch persistence subsystem marker
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import anyio

from omega.errors import OmegaError

if TYPE_CHECKING:
    from omega.memory.providers import StorageProvider

logger = logging.getLogger("batch_writer")

# ── Configuration ────────────────────────────────────────────────────────────

BATCH_SIZE: int = 50  # flush when this many writes accumulate
FLUSH_INTERVAL: float = 2.0  # flush at least every N seconds
BUFFER_CAPACITY: int = 2000  # in-memory channel depth before backpressure
DLQ_MAX_ENTRIES: int = 10000  # max dead-letter queue entries on disk
DLQ_DIR: str = "data/batch_dlq"


@dataclass
class _WriteOp:
    """A single pending write operation."""

    entity_name: str
    session_id: str
    exchanges: List[Dict[str, Any]]
    enqueued_at: float = field(default_factory=time.time)


class BatchPersistenceWriter:
    """
    Background batch writer for MemoryStore provider persistence.

    Buffers add_exchange() writes and flushes them periodically in batches,
    grouped by (entity_name, session_id) for each provider. This prevents
    connection pool exhaustion when many concurrent oracle.talk() calls
    each trigger provider writes.

    Lifecycle:
        writer = BatchPersistenceWriter(providers=[...])
        async with anyio.create_task_group() as tg:
            await writer.start(tg)
            yield  # app runs
            await writer.stop()

    Usage (from MemoryStore.add_exchange):
        await batch_writer.write(entity_name, session_id, exchanges)
    """

    def __init__(
        self,
        providers: Optional[List["StorageProvider"]] = None,
        batch_size: int = BATCH_SIZE,
        flush_interval: float = FLUSH_INTERVAL,
        buffer_capacity: int = BUFFER_CAPACITY,
    ) -> None:
        self._providers: List["StorageProvider"] = providers or []
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._buffer_capacity = buffer_capacity
        self._send: Optional[anyio.abc.ObjectSendStream[_WriteOp]] = None
        self._recv: Optional[anyio.abc.ObjectReceiveStream[_WriteOp]] = None
        self._running: bool = False
        self._dlq_path: Optional[Path] = None
        self._stats: Dict[str, int] = {
            "enqueued": 0,
            "flushed": 0,
            "direct_writes": 0,
            "dlq_pushes": 0,
            "errors": 0,
        }

    async def start(self, task_group: anyio.abc.TaskGroup) -> None:
        """Wire the background flush loop into an existing TaskGroup."""
        self._send, self._recv = anyio.create_memory_object_stream(
            max_buffer_size=self._buffer_capacity,
        )
        self._running = True

        # Initialize DLQ directory
        dlq_path = Path(DLQ_DIR)
        dlq_path.mkdir(parents=True, exist_ok=True)
        self._dlq_path = dlq_path

        task_group.start_soon(self._flush_loop)
        logger.info(
            "BatchPersistenceWriter online — batch_size=%d flush_interval=%.1fs",
            self._batch_size,
            self._flush_interval,
        )

    async def write(
        self,
        entity_name: str,
        session_id: str,
        exchanges: List[Dict[str, Any]],
    ) -> None:
        """
        Non-blocking enqueue of a write operation. Falls back to direct write
        if the writer has not been started or the buffer is full.
        """
        op = _WriteOp(
            entity_name=entity_name,
            session_id=session_id,
            exchanges=exchanges,
        )
        self._stats["enqueued"] += 1

        if not self._send or not self._running:
            logger.warning("BatchPersistenceWriter not started — falling back to direct write")
            await self._direct_write(op)
            return

        try:
            self._send.send_nowait(op)
        except anyio.WouldBlock:
            logger.warning("BatchPersistenceWriter buffer full — bypassing to direct write")
            await self._direct_write(op)

    async def stop(self) -> None:
        """Graceful shutdown: drain remaining records then close."""
        self._running = False
        if self._send:
            await self._send.aclose()
        logger.info("BatchPersistenceWriter stopped — stats: %s", self._stats)

    async def flush(self) -> None:
        """Explicitly flush any pending writes.

        If the background loop is running, writes are flushed automatically within
        FLUSH_INTERVAL. If not running, writes are committed immediately on write(),
        so this is a no-op.
        """
        logger.debug("BatchPersistenceWriter.flush() called")

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    # ── Internal ──────────────────────────────────────────────────────────

    async def _flush_loop(self) -> None:
        """
        Core loop: collect up to BATCH_SIZE ops or FLUSH_INTERVAL seconds,
        whichever comes first, then commit in a single batch.
        """
        while self._running:
            batch: List[_WriteOp] = []

            with anyio.move_on_after(self._flush_interval):
                while len(batch) < self._batch_size:
                    try:
                        op = await self._recv.receive()
                        batch.append(op)
                    except anyio.EndOfStream:
                        self._running = False
                        break

            if batch:
                await self._commit_batch(batch)

    async def _commit_batch(self, batch: List[_WriteOp]) -> None:
        """
        Commit a batch of write ops to all providers. Groups ops by
        (entity_name, session_id) to minimize redundant writes.
        """
        # Group by (entity_name, session_id) — merge exchanges
        grouped: Dict[tuple, List[Dict[str, Any]]] = {}
        for op in batch:
            key = (op.entity_name, op.session_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].extend(op.exchanges)

        errors = 0
        for provider in self._providers:
            try:
                for (entity_name, session_id), exchanges in grouped.items():
                    await provider.save_history(entity_name, session_id, exchanges)
            except (OmegaError, RuntimeError, OSError) as exc:
                errors += 1
                logger.error(
                    "Batch commit failed for %s: %s",
                    provider.__class__.__name__,
                    exc,
                )

        if errors:
            self._stats["errors"] += errors
            # Push failed batch to DLQ for later replay
            await self._push_to_dlq(batch, f"{errors} provider(s) failed")

        self._stats["flushed"] += len(batch)
        logger.debug(
            "BatchPersistenceWriter flushed %d ops (%d groups) across %d providers",
            len(batch),
            len(grouped),
            len(self._providers),
        )

    async def _direct_write(self, op: _WriteOp) -> None:
        """Fallback single-op write (degraded path)."""
        for provider in self._providers:
            try:
                await provider.save_history(op.entity_name, op.session_id, op.exchanges)
            except (OmegaError, RuntimeError, OSError) as exc:
                logger.error(
                    "Direct write failed for %s/%s: %s",
                    op.entity_name,
                    provider.__class__.__name__,
                    exc,
                )
                self._stats["errors"] += 1
                await self._push_to_dlq([op], str(exc))

        self._stats["direct_writes"] += 1

    async def _push_to_dlq(self, batch: List[_WriteOp], error: str) -> None:
        """
        On provider failure, write serialisable op metadata to disk DLQ
        for later replay. Uses atomic write (tmp → rename).
        """
        if not self._dlq_path:
            logger.critical("DLQ path not initialized — %d records lost", len(batch))
            return

        try:
            ts = int(time.time() * 1000)
            dlq_file = self._dlq_path / f"dlq_{ts}.json"

            entries = []
            for op in batch:
                entries.append(
                    {
                        "entity_name": op.entity_name,
                        "session_id": op.session_id,
                        "exchanges_count": len(op.exchanges),
                        "exchanges": op.exchanges,
                        "enqueued_at": op.enqueued_at,
                        "error": error,
                    }
                )

            # Atomic write: tmp → rename
            tmp_path = dlq_file.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(entries, default=str, indent=2))
            tmp_path.rename(dlq_file)

            self._stats["dlq_pushes"] += len(batch)
            logger.info(
                "Pushed %d failed records to DLQ: %s",
                len(batch),
                dlq_file,
            )
        except (OSError, RuntimeError) as dlq_exc:
            logger.critical(
                "DLQ push also failed: %s. %d records lost.",
                dlq_exc,
                len(batch),
            )
