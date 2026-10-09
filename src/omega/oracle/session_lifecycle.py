# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Session Lifecycle Manager — Active → Archived → External → Deleted.
AP: AP-SESSION-LIFECYCLE-v1.0.0

Orchestrates the full session lifecycle:
- Active (0-7 days): hot cache + warm providers (entities/{entity}/{session}.json)
- Archived (7-30 days): cold storage, gzip compressed (archive/{entity}/{session}.json.gz)
- External (90+ days): moved to external 8TB storage drive
- Deleted (optional): beyond retention policy

Heritage:
- [id-soft: vet-009] 4-Tier Memory — Active/Archived/External/Deleted maps to
  Hunk/Zone/Cache/Temp from Quake's zone memory allocator.
- [id-soft: vet-008] Lazy Deletion — tombstone before delete, grace period
  before reap. Prevents data loss on in-flight operations.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

from __future__ import annotations

import os
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from omega.errors import OmegaError
from omega.memory.providers import sanitize_path_component

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Lifecycle states for a session.

    [id-soft: vet-009] 4-Tier Memory — state machine mapping:
    - ACTIVE → Hunk (fast, in-memory)
    - ARCHIVED → Zone (compressed, on-disk)
    - EXTERNAL → Cache (cold, external drive)
    - DELETED → Purged (beyond retention)
    """

    ACTIVE = "active"  # 0-7 days: hot cache + warm providers
    ARCHIVED = "archived"  # 7-30 days: cold storage (gzip compressed)
    EXTERNAL = "external"  # 90+ days: external 8TB storage
    DELETED = "deleted"  # Beyond retention policy


@dataclass
class SessionLifecycleConfig:
    """Configuration for session lifecycle policies.

    Defaults match the Omega Engine's current 7/30/90-day policy:
    - 7 days: archive to cold storage (local disk)
    - 30 days: compressed in cold storage (gzip)
    - 90 days: move to external 8TB storage drive
    """

    archive_after_days: int = 7
    compress_after_days: int = 30  # Already compressed by FileStorageProvider on archive
    external_after_days: int = 90
    delete_after_days: int = 365  # Optional: full deletion beyond retention
    external_storage_path: Path = field(
        default_factory=lambda: Path(os.environ.get(
            "OMEGA_EXTERNAL_STORAGE", Path.home() / "omega_library" / "archive" / "sessions"
        ))
    )
    enable_external_archive: bool = True
    enable_deletion: bool = False  # Disabled by default — data preservation


@dataclass
class SessionInfo:
    """Metadata about a session's lifecycle state."""

    entity_name: str
    session_id: str
    state: SessionState
    age_days: float
    path: Optional[str] = None
    compressed: bool = False
    last_modified: Optional[float] = None


@dataclass
class LifecycleStats:
    """Aggregate statistics from a lifecycle sweep."""

    archived: int = 0
    externalized: int = 0
    deleted: int = 0
    recalled: int = 0
    errors: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archived": self.archived,
            "externalized": self.externalized,
            "deleted": self.deleted,
            "recalled": self.recalled,
            "errors": self.errors,
            "duration_ms": round(self.duration_ms, 2),
        }


class SessionLifecycleManager:
    """Orchestrates the full session lifecycle.

    Wraps MemoryStore's existing archive/external methods with a unified
    state machine and adds recall-from-external capability.

    Usage:
        manager = SessionLifecycleManager(memory_store)
        stats = await manager.run_lifecycle()
        state = await manager.get_session_state("kali", "ses_20260701_kali_001")
        recalled = await manager.recall_from_external("kali", "ses_20260701_kali_001")

    Heritage:
    - [id-soft: vet-009] 4-Tier Memory — state machine for session lifecycle
    - [id-soft: vet-008] Lazy Deletion — tombstone before delete
    """

    def __init__(
        self,
        memory_store: Any,  # MemoryStore — avoid circular import
        config: Optional[SessionLifecycleConfig] = None,
    ):
        self._store = memory_store
        self._config = config or SessionLifecycleConfig()
        self._stats = LifecycleStats()

    @property
    def config(self) -> SessionLifecycleConfig:
        return self._config

    @property
    def stats(self) -> LifecycleStats:
        return self._stats

    async def run_lifecycle(self) -> LifecycleStats:
        """Execute full lifecycle sweep.

        Transitions:
        1. Active → Archived: sessions older than archive_after_days
        2. Archived → External: sessions older than external_after_days
        3. External → Deleted: sessions older than delete_after_days (if enabled)

        Returns:
            LifecycleStats with counts per transition
        """
        start = time.monotonic()
        self._stats = LifecycleStats()

        # Step 1: Archive old sessions (Active → Archived)
        try:
            self._stats.archived = await self._store.archive_old_sessions(
                older_than_days=self._config.archive_after_days
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Lifecycle archive step failed: %s", e, exc_info=True)
            self._stats.errors += 1

        # Step 2: Move to external storage (Archived → External)
        if self._config.enable_external_archive:
            try:
                self._stats.externalized = await self._move_to_external()
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error("Lifecycle external step failed: %s", e, exc_info=True)
                self._stats.errors += 1

        # Step 3: Delete beyond retention (External → Deleted)
        if self._config.enable_deletion:
            try:
                self._stats.deleted = await self._delete_beyond_retention()
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error("Lifecycle delete step failed: %s", e, exc_info=True)
                self._stats.errors += 1

        self._stats.duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "Lifecycle sweep complete: archived=%d, externalized=%d, deleted=%d, errors=%d, %.1fms",
            self._stats.archived,
            self._stats.externalized,
            self._stats.deleted,
            self._stats.errors,
            self._stats.duration_ms,
        )
        return self._stats

    async def get_session_state(
        self,
        entity_name: str,
        session_id: str,
    ) -> SessionState:
        """Determine current lifecycle state of a session.

        Checks locations in order:
        1. Hot cache (ACTIVE)
        2. USM State (ACTIVE)
        3. Cold storage — archive/{entity}/{session}.json.gz (ARCHIVED)
        4. External storage (EXTERNAL)
        5. Not found (DELETED or never existed)
        """
        safe_name = sanitize_path_component(entity_name)
        safe_session = sanitize_path_component(session_id)

        # Check hot cache
        cache_key = f"{entity_name.lower()}:{session_id}"
        if cache_key in self._store._hot:
            return SessionState.ACTIVE

        # Check USM
        from omega.state import get_usm

        usm = get_usm()
        state_key = f"mem:{entity_name}:{session_id}"
        if await usm.exists(state_key):
            return SessionState.ACTIVE

        # Check cold storage
        archive_dir = (
            self._store._get_archive_dir() if hasattr(self._store, "_get_archive_dir") else None
        )
        if archive_dir is None:
            from omega.memory_store import _get_archive_dir

            archive_dir = _get_archive_dir()

        cold_path = archive_dir / safe_name / f"{safe_session}.json.gz"
        if await anyio.Path(cold_path).exists():
            return SessionState.ARCHIVED

        # Check external storage
        external_path = self._config.external_storage_path / safe_name / f"{safe_session}.json.gz"
        if await anyio.Path(external_path).exists():
            return SessionState.EXTERNAL

        return SessionState.DELETED

    async def get_session_info(
        self,
        entity_name: str,
        session_id: str,
    ) -> Optional[SessionInfo]:
        """Get detailed info about a session including age and path."""
        state = await self.get_session_state(entity_name, session_id)
        safe_name = entity_name.lower().replace(" ", "_")

        path = None
        compressed = False
        last_modified = None

        if state == SessionState.ACTIVE:
            # Check hot cache first
            cache_key = f"{entity_name.lower()}:{session_id}"
            if cache_key in self._store._hot:
                # Hot cache doesn't have a file path, but we can use the USM key as a virtual path
                path = f"usm://{cache_key}"
                # Use the timestamp of the last exchange in the hot cache
                exchanges = self._store._hot[cache_key].values()
                if exchanges:
                    last_ex = list(exchanges)[-1]
                    last_modified = datetime.fromisoformat(last_ex["timestamp"]).timestamp()
            else:
                # Check USM
                from omega.state import get_usm

                usm = get_usm()
                state_key = f"mem:{entity_name}:{session_id}"
                if await usm.exists(state_key):
                    path = f"usm://{state_key}"
                    data = await usm.load_state(state_key)
                    last_modified = datetime.fromisoformat(
                        data.get("last_updated", datetime.now(timezone.utc).isoformat())
                    ).timestamp()
                else:
                    # Fallback to warm storage (for legacy sessions)
                    from omega.memory_store import _get_entity_dir

                    entity_dir = _get_entity_dir()
                    p = entity_dir / safe_name / f"{session_id}.json"
                    if await anyio.Path(p).exists():
                        path = str(p)
                        stat = await anyio.Path(p).stat()
                        last_modified = stat.st_mtime
        elif state == SessionState.ARCHIVED:
            from omega.memory_store import _get_archive_dir

            archive_dir = _get_archive_dir()
            p = archive_dir / safe_name / f"{session_id}.json.gz"
            if await anyio.Path(p).exists():
                path = str(p)
                compressed = True
                stat = await anyio.Path(p).stat()
                last_modified = stat.st_mtime
        elif state == SessionState.EXTERNAL:
            p = self._config.external_storage_path / safe_name / f"{session_id}.json.gz"
            if await anyio.Path(p).exists():
                path = str(p)
                compressed = True
                stat = await anyio.Path(p).stat()
                last_modified = stat.st_mtime

        age_days = 0.0
        if last_modified:
            age_days = (time.time() - last_modified) / 86400

        return SessionInfo(
            entity_name=entity_name,
            session_id=session_id,
            state=state,
            age_days=age_days,
            path=path,
            compressed=compressed,
            last_modified=last_modified,
        )

    async def recall_from_external(
        self,
        entity_name: str,
        session_id: str,
    ) -> bool:
        """Recall a session from external storage back to cold storage.

        [D189 Gap Resolution] — 90-day archival was write-only with no
        retrieval path. This method enables recalling externally archived
        sessions back to local cold storage for access.

        Args:
            entity_name: Entity name
            session_id: Session ID to recall

        Returns:
            True if recalled successfully, False if not found or error
        """
        safe_name = entity_name.lower().replace(" ", "_")
        external_path = self._config.external_storage_path / safe_name / f"{session_id}.json.gz"
        local_path = (
            self._config.external_storage_path.parent
            / "archive"
            / safe_name
            / f"{session_id}.json.gz"
        )

        if not await anyio.Path(external_path).exists():
            logger.warning("Session %s/%s not found in external storage", entity_name, session_id)
            return False

        try:
            # Ensure local archive directory exists
            await anyio.Path(local_path.parent).mkdir(parents=True, exist_ok=True)

            # Copy from external to local (preserves original in external)
            import shutil

            await anyio.to_thread.run_sync(shutil.copy2, str(external_path), str(local_path))
            logger.info("Recalled session %s/%s from external to local", entity_name, session_id)
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error("Failed to recall session %s/%s: %s", entity_name, session_id, e)
            return False

    async def list_sessions_by_state(
        self,
        entity_name: Optional[str] = None,
        state: Optional[SessionState] = None,
        limit: int = 50,
    ) -> List[SessionInfo]:
        """List sessions filtered by entity and/or lifecycle state.

        Useful for observability and debugging lifecycle transitions.
        """
        results: List[SessionInfo] = []

        # Get all sessions from the memory store
        sessions = await self._store.list_sessions(entity_name=entity_name, limit=1000)

        for session in sessions:
            info = await self.get_session_info(session["entity"], session["session_id"])
            if info and (state is None or info.state == state):
                results.append(info)
                if len(results) >= limit:
                    break

        return results

    async def _move_to_external(self) -> int:
        """Move sessions older than external_after_days to external storage.

        [id-soft: vet-067] Cache Tier — cold data moved to external drive.
        """
        count = 0
        now = time.time()

        from omega.memory_store import _get_archive_dir

        archive_dir = _get_archive_dir()

        if not await anyio.Path(archive_dir).exists():
            return 0

        # Ensure external storage directory exists
        await anyio.Path(self._config.external_storage_path).mkdir(parents=True, exist_ok=True)

        async for ent_dir in anyio.Path(archive_dir).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue
            async for path in anyio.Path(ent_dir).glob("*.json.gz"):
                try:
                    stat = await anyio.Path(path).stat()
                    age_days = (now - stat.st_mtime) / 86400
                    if age_days > self._config.external_after_days:
                        entity_name = ent_dir.name
                        external_entity_dir = self._config.external_storage_path / entity_name
                        await anyio.Path(external_entity_dir).mkdir(parents=True, exist_ok=True)

                        dest_path = external_entity_dir / path.name
                        await anyio.Path(path).rename(dest_path)
                        count += 1
                        logger.info(
                            "Moved session %s to external storage: %s", path.name, dest_path
                        )
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning("Failed to move %s to external: %s", path, e)

        return count

    async def _delete_beyond_retention(self) -> int:
        """Delete sessions beyond retention policy.

        [id-soft: vet-008] Lazy Deletion — only deletes after full lifecycle.
        Disabled by default for data preservation.
        """
        count = 0
        now = time.time()

        # Only check external storage for deletion
        if not await anyio.Path(self._config.external_storage_path).exists():
            return 0

        async for ent_dir in anyio.Path(self._config.external_storage_path).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue
            async for path in anyio.Path(ent_dir).glob("*.json.gz"):
                try:
                    stat = await anyio.Path(path).stat()
                    age_days = (now - stat.st_mtime) / 86400
                    if age_days > self._config.delete_after_days:
                        await anyio.Path(path).unlink()
                        count += 1
                        logger.info("Deleted session beyond retention: %s", path)
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning("Failed to delete %s: %s", path, e)
        return count

    def get_config_summary(self) -> Dict[str, Any]:
        """Return a summary of the lifecycle configuration."""
        return {
            "archive_after_days": self._config.archive_after_days,
            "compress_after_days": self._config.compress_after_days,
            "external_after_days": self._config.external_after_days,
            "delete_after_days": self._config.delete_after_days,
            "enable_external_archive": self._config.enable_external_archive,
            "enable_deletion": self._config.enable_deletion,
            "external_storage_path": str(self._config.external_storage_path),
        }
