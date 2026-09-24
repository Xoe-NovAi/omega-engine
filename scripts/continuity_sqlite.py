"""Local SQLite adapter for the portable continuity kernel.

This module is an adapter, not part of the portable core. It gives one local
SQLite database authority for semantic events, state projections, checkpoints,
artifacts, and prepared intents. MemPalace can later consume the event/artifact
records as a projection without changing the core contract.

SQLite 3.51.3+ is required for production because earlier versions are within the
2026 WAL-reset defect range documented by SQLite. The private test sentinel is
available only to the repository's legacy-runtime tests; production callers
cannot opt out by passing a public boolean.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Iterator, Mapping

from scripts.continuity_kernel import (
    ArtifactRef,
    Checkpoint,
    CommitIntent,
    ContractError,
    RecoveryError,
    SemanticEvent,
    JsonObject,
)

MINIMUM_FIXED_SQLITE = (3, 51, 3)
_SQLITE_TEST_BYPASS = object()


class SqliteContinuityStore:
    """SQLite-backed state, event, artifact, checkpoint, and intent store."""

    def __init__(
        self,
        db_path: Path,
        *,
        _test_bypass: object | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if (
            sqlite3.sqlite_version_info < MINIMUM_FIXED_SQLITE
            and _test_bypass is not _SQLITE_TEST_BYPASS
        ):
            observed = ".".join(str(part) for part in sqlite3.sqlite_version_info)
            required = ".".join(str(part) for part in MINIMUM_FIXED_SQLITE)
            raise ContractError(
                f"SQLite {observed} is below the continuity production floor {required}"
            )
        self.timeout_seconds = timeout_seconds
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.db_path,
            timeout=self.timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    content_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    content BLOB NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL DEFAULT '',
                    event_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (entity_id, sequence)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS events_idempotency
                    ON events(entity_id, idempotency_key)
                    WHERE idempotency_key <> '';
                CREATE TABLE IF NOT EXISTS state (
                    entity_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS checkpoints (
                    entity_id TEXT PRIMARY KEY,
                    sequence INTEGER NOT NULL,
                    checkpoint_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS intents (
                    intent_id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    intent_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def lock(self, entity_id: str):
        """SQLite serializes writers; the context manager documents that fact."""
        return nullcontext()

    def put(
        self,
        content: bytes,
        content_type: str = "application/json",
        metadata: Mapping[str, object] | None = None,
    ) -> ArtifactRef:
        if not isinstance(content, bytes):
            raise TypeError("artifact content must be bytes")
        digest = hashlib.sha256(content).hexdigest()
        metadata_json = json.dumps(
            dict(metadata or {}), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT sha256, size_bytes, content FROM artifacts WHERE artifact_id = ?",
                    (digest,),
                ).fetchone()
                if row is not None:
                    if row["sha256"] != digest or row["size_bytes"] != len(content):
                        raise RecoveryError("artifact digest collision or size mismatch")
                    if bytes(row["content"]) != content:
                        raise RecoveryError("artifact digest collision or content mismatch")
                else:
                    connection.execute(
                        """
                        INSERT INTO artifacts
                            (artifact_id, sha256, size_bytes, content_type, metadata_json, content)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (digest, digest, len(content), content_type, metadata_json, content),
                    )
                connection.commit()
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise
        return ArtifactRef(
            artifact_id=digest,
            sha256=digest,
            size_bytes=len(content),
            content_type=content_type,
        )

    def get(self, artifact_id: str) -> bytes:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT content FROM artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
        if row is None:
            raise RecoveryError(f"missing artifact blob: {artifact_id}")
        content = bytes(row["content"])
        if hashlib.sha256(content).hexdigest() != artifact_id:
            raise RecoveryError(f"artifact hash mismatch: {artifact_id}")
        return content

    def append(self, event: SemanticEvent) -> None:
        event_json = _canonical_json(event.to_dict())
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                by_id = connection.execute(
                    "SELECT event_json FROM events WHERE event_id = ?",
                    (event.event_id,),
                ).fetchone()
                if by_id is not None:
                    if by_id["event_json"] != event_json:
                        raise RecoveryError("event id already exists with different content")
                    connection.commit()
                    return
                by_sequence = connection.execute(
                    "SELECT event_id FROM events WHERE entity_id = ? AND sequence = ?",
                    (event.entity_id, event.sequence),
                ).fetchone()
                if by_sequence is not None:
                    raise RecoveryError(
                        "event sequence already exists with different id: "
                        f"{event.entity_id}/{event.sequence}"
                    )
                connection.execute(
                    """
                    INSERT INTO events
                        (event_id, entity_id, sequence, idempotency_key, event_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        event.entity_id,
                        event.sequence,
                        event.idempotency_key,
                        event_json,
                        event.created_at,
                    ),
                )
                connection.commit()
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                raise RecoveryError(f"idempotency or sequence conflict: {exc}") from exc
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise

    def list(
        self, entity_id: str, upto_sequence: int | None = None
    ) -> list[SemanticEvent]:
        query = "SELECT event_json FROM events WHERE entity_id = ?"
        parameters: list[object] = [entity_id]
        if upto_sequence is not None:
            query += " AND sequence <= ?"
            parameters.append(upto_sequence)
        query += " ORDER BY sequence"
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [SemanticEvent.from_dict(json.loads(row["event_json"])) for row in rows]

    def write(self, state: JsonObject) -> None:
        entity_id = str(state.get("entity_id", ""))
        state_json = _canonical_json(state)
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO state(entity_id, state_json, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_id) DO UPDATE SET
                        state_json = excluded.state_json,
                        updated_at = excluded.updated_at
                    """,
                    (entity_id, state_json),
                )
                connection.commit()
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise

    def read(self, entity_id: str) -> JsonObject:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT state_json FROM state WHERE entity_id = ?",
                (entity_id,),
            ).fetchone()
        if row is None:
            raise RecoveryError(f"missing state pointer: {entity_id}")
        value = json.loads(row["state_json"])
        if not isinstance(value, dict):
            raise RecoveryError("state row must contain a JSON object")
        return value

    def save(self, checkpoint: Checkpoint) -> None:
        checkpoint_json = _canonical_json(checkpoint.to_dict())
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO checkpoints(entity_id, sequence, checkpoint_json, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_id) DO UPDATE SET
                        sequence = excluded.sequence,
                        checkpoint_json = excluded.checkpoint_json,
                        updated_at = excluded.updated_at
                    """,
                    (checkpoint.entity_id, checkpoint.sequence, checkpoint_json),
                )
                connection.commit()
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise

    def latest(self, entity_id: str) -> Checkpoint | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT checkpoint_json FROM checkpoints WHERE entity_id = ?",
                (entity_id,),
            ).fetchone()
        if row is None:
            return None
        return Checkpoint.from_dict(json.loads(row["checkpoint_json"]))

    def prepare(self, intent: CommitIntent) -> None:
        intent_json = _canonical_json(intent.to_dict())
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT intent_json FROM intents WHERE intent_id = ?",
                    (intent.intent_id,),
                ).fetchone()
                if row is not None and row["intent_json"] != intent_json:
                    raise RecoveryError("intent id already exists with different content")
                connection.execute(
                    """
                    INSERT OR IGNORE INTO intents(intent_id, entity_id, intent_json, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (intent.intent_id, intent.event.entity_id, intent_json, intent.created_at),
                )
                connection.commit()
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise

    def pending(self, entity_id: str) -> list[CommitIntent]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT intent_json FROM intents WHERE entity_id = ? ORDER BY created_at",
                (entity_id,),
            ).fetchall()
        return [CommitIntent.from_dict(json.loads(row["intent_json"])) for row in rows]

    def apply_intent(self, intent: CommitIntent) -> None:
        """Apply event, state, and checkpoint in one SQLite transaction."""
        event_json = _canonical_json(intent.event.to_dict())
        with self._connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                by_id = connection.execute(
                    "SELECT event_json FROM events WHERE event_id = ?",
                    (intent.event.event_id,),
                ).fetchone()
                if by_id is not None:
                    if by_id["event_json"] != event_json:
                        raise RecoveryError("intent event id conflicts with existing event")
                else:
                    by_sequence = connection.execute(
                        "SELECT event_id FROM events WHERE entity_id = ? AND sequence = ?",
                        (intent.event.entity_id, intent.event.sequence),
                    ).fetchone()
                    if by_sequence is not None:
                        raise RecoveryError("intent sequence conflicts with existing event")
                    connection.execute(
                        """
                        INSERT INTO events
                            (event_id, entity_id, sequence, idempotency_key, event_json, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            intent.event.event_id,
                            intent.event.entity_id,
                            intent.event.sequence,
                            intent.event.idempotency_key,
                            event_json,
                            intent.event.created_at,
                        ),
                    )
                state_row = connection.execute(
                    "SELECT state_json FROM state WHERE entity_id = ?",
                    (intent.event.entity_id,),
                ).fetchone()
                if state_row is None:
                    connection.execute(
                        "INSERT INTO state(entity_id, state_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                        (intent.event.entity_id, _canonical_json(intent.state)),
                    )
                else:
                    current_state = json.loads(state_row["state_json"])
                    if int(current_state.get("last_sequence", 0)) <= intent.event.sequence:
                        connection.execute(
                            "UPDATE state SET state_json = ?, updated_at = CURRENT_TIMESTAMP WHERE entity_id = ?",
                            (_canonical_json(intent.state), intent.event.entity_id),
                        )
                connection.execute(
                    """
                    INSERT INTO checkpoints(entity_id, sequence, checkpoint_json, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_id) DO UPDATE SET
                        sequence = excluded.sequence,
                        checkpoint_json = excluded.checkpoint_json,
                        updated_at = excluded.updated_at
                    WHERE checkpoints.sequence <= excluded.sequence
                    """,
                    (
                        intent.event.entity_id,
                        intent.checkpoint.sequence,
                        _canonical_json(intent.checkpoint.to_dict()),
                    ),
                )
                connection.execute(
                    "DELETE FROM intents WHERE intent_id = ?", (intent.intent_id,)
                )
                connection.commit()
            except (OSError, sqlite3.Error, TypeError, ValueError, RecoveryError):
                connection.rollback()
                raise

    def commit(self, intent_id: str, entity_id: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM intents WHERE intent_id = ?", (intent_id,))
            connection.commit()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
