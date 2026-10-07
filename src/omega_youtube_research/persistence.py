# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# 🔱 Omega Engine — YouTube Research Module (P0)
# AP: AP-YOUTUBE-RESEARCH-MODULE-v1.0.0
# ⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_youtube_research ⬡ P0-STRUCTURAL
#
# AtomicPersistence — crash-safe writes via WAL-mode SQLite + atomic file renames.
#
# Heritage:
#   [heritage: aiosqlite 2021] WAL-mode SQLite persistence (journal_mode=WAL)
#   [heritage: anyio 2024] Blocking fsync/rename wrapped in anyio.to_thread.run_sync
#   [heritage: sqlite-fts5 2015] (future) full-text indexing of stored transcripts

"""AtomicPersistence — crash-safe persistence for attestations and provenance chunks.

Two complementary guarantees (Mandate 12 / Temple-Grade T10):

1. **WAL-mode SQLite** — all DB writes use Write-Ahead Logging so a crash mid-commit
   leaves the database in a consistent state on the next open (no partial rows).
2. **Atomic JSON renames** — ``atomic_write_json`` writes to a ``.tmp`` sibling and
   renames it into place with ``os.replace`` (atomic on POSIX *and* Windows), so
   readers never observe a half-written file.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite
import anyio
from pydantic import BaseModel

from .errors import PersistenceError
from .signer import SourceChainAttestation


class ProvenanceChunkRecord(BaseModel):
    """A persisted provenance chunk row (mirrors ``provenance.ProvenanceChunk``)."""

    chunk_id: str
    source_id: str
    parent_chunk_id: Optional[str]
    sequence: int
    content_hash: str
    chain_hash: str
    source_url: Optional[str]
    created_at: str


class AtomicPersistence:
    """WAL SQLite store + atomic JSON file writer.

    Args:
        db_path: Path to the SQLite database file. Parent dirs are created.
        tmp_suffix: Suffix used for in-progress JSON writes.
    """

    def __init__(self, db_path: Path, tmp_suffix: str = ".tmp"):
        self._db_path = Path(db_path)
        self._tmp_suffix = tmp_suffix
        self._conn: Optional[aiosqlite.Connection] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────
    async def init(self) -> None:
        """Open the SQLite connection and enable WAL mode + schema.

        Raises:
            PersistenceError: If the database cannot be opened or initialised.
        """
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(str(self._db_path))
            # WAL: durable atomic commits, readers never block writers.
            await self._conn.execute("PRAGMA journal_mode=WAL;")
            await self._conn.execute("PRAGMA synchronous=NORMAL;")
            await self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attestations (
                    source_id TEXT PRIMARY KEY,
                    source_type TEXT,
                    source_url TEXT,
                    cleaned_text_hash TEXT,
                    provenance_hash TEXT,
                    sieve_metadata TEXT,
                    signed_at TEXT,
                    signer TEXT,
                    key_id TEXT,
                    attestation_json TEXT
                )
                """
            )
            await self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS provenance_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    source_id TEXT,
                    parent_chunk_id TEXT,
                    sequence INTEGER,
                    content_hash TEXT,
                    chain_hash TEXT,
                    source_url TEXT,
                    created_at TEXT
                )
                """
            )
            await self._conn.commit()
        except (OSError, aiosqlite.Error) as exc:
            raise PersistenceError(
                f"Failed to initialise persistence at {self._db_path}: {exc}"
            ) from exc

    async def close(self) -> None:
        """Close the SQLite connection if open."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    # ── Atomic JSON file writer ──────────────────────────────────────────────
    async def atomic_write_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Write ``data`` as JSON atomically via a ``.tmp`` sibling + ``os.replace``.

        Args:
            path: Destination ``.json`` path.
            data: JSON-serialisable payload.

        Raises:
            PersistenceError: If the temp write or rename fails.
        """
        path = Path(path)
        tmp = path.with_suffix(path.suffix + self._tmp_suffix)

        def _write() -> None:
            payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            with tmp.open("w", encoding="utf-8") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)  # atomic on POSIX + Windows

        try:
            await anyio.to_thread.run_sync(_write)
        except (OSError, ValueError) as exc:
            # Clean up a possibly-partial temp file; original is untouched.
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:  # pragma: no cover - defensive
                    pass
            raise PersistenceError(
                f"Atomic JSON write failed for {path}: {exc}"
            ) from exc

    # ── Attestation storage (WAL SQLite) ─────────────────────────────────────
    async def store_attestation(self, attestation: SourceChainAttestation) -> None:
        """Persist a signed attestation. Atomic via WAL transaction.

        Args:
            attestation: The ``SourceChainAttestation`` to store.

        Raises:
            PersistenceError: If the connection is not initialised or the write fails.
        """
        if self._conn is None:
            raise PersistenceError("AtomicPersistence.init() must be called first")
        try:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO attestations
                (source_id, source_type, source_url, cleaned_text_hash,
                 provenance_hash, sieve_metadata, signed_at, signer, key_id,
                 attestation_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attestation.source_id,
                    attestation.source_type,
                    attestation.source_url,
                    attestation.cleaned_text_hash,
                    attestation.provenance_hash,
                    json.dumps(attestation.sieve_metadata, ensure_ascii=False),
                    attestation.signed_at,
                    attestation.signer,
                    attestation.key_id,
                    attestation.model_dump_json(),
                ),
            )
            await self._conn.commit()
        except aiosqlite.Error as exc:
            raise PersistenceError(
                f"Failed to store attestation {attestation.source_id}: {exc}"
            ) from exc

    async def get_attestation(self, source_id: str) -> Optional[SourceChainAttestation]:
        """Retrieve a stored attestation by ``source_id``.

        Args:
            source_id: The source identifier.

        Returns:
            The ``SourceChainAttestation`` or ``None`` if not found.
        """
        if self._conn is None:
            raise PersistenceError("AtomicPersistence.init() must be called first")
        async with self._conn.execute(
            "SELECT attestation_json FROM attestations WHERE source_id = ?",
            (source_id,),
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            return None
        return SourceChainAttestation.model_validate_json(row[0])

    # ── Provenance chunk storage (WAL SQLite) ────────────────────────────────
    async def store_chunk(self, chunk: ProvenanceChunkRecord) -> None:
        """Persist a provenance chunk (parent linkage). Atomic via WAL transaction.

        Args:
            chunk: The ``ProvenanceChunkRecord`` to store.
        """
        if self._conn is None:
            raise PersistenceError("AtomicPersistence.init() must be called first")
        try:
            await self._conn.execute(
                """
                INSERT OR REPLACE INTO provenance_chunks
                (chunk_id, source_id, parent_chunk_id, sequence, content_hash,
                 chain_hash, source_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.source_id,
                    chunk.parent_chunk_id,
                    chunk.sequence,
                    chunk.content_hash,
                    chunk.chain_hash,
                    chunk.source_url,
                    chunk.created_at,
                ),
            )
            await self._conn.commit()
        except aiosqlite.Error as exc:
            raise PersistenceError(
                f"Failed to store chunk {chunk.chunk_id}: {exc}"
            ) from exc

    async def get_chunks(self, source_id: str) -> List[ProvenanceChunkRecord]:
        """Retrieve all provenance chunks for a source, ordered by sequence.

        Args:
            source_id: The source identifier.

        Returns:
            Ordered list of ``ProvenanceChunkRecord``.
        """
        if self._conn is None:
            raise PersistenceError("AtomicPersistence.init() must be called first")
        async with self._conn.execute(
            "SELECT chunk_id, source_id, parent_chunk_id, sequence, content_hash, "
            "chain_hash, source_url, created_at FROM provenance_chunks "
            "WHERE source_id = ? ORDER BY sequence ASC",
            (source_id,),
        ) as cur:
            rows = await cur.fetchall()
        return [
            ProvenanceChunkRecord(
                chunk_id=r[0],
                source_id=r[1],
                parent_chunk_id=r[2],
                sequence=r[3],
                content_hash=r[4],
                chain_hash=r[5],
                source_url=r[6],
                created_at=r[7],
            )
            for r in rows
        ]
