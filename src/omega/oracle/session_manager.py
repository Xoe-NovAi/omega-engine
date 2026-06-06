# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Session Manager — Entity-scoped rolling sessions with daily counter.

Implements the R50 session architecture. Each entity has one active session
per day, persisted to data/sessions/{entity}.active. Transient mode falls
back to trace_id with no persistence.

[id-soft: quake-1996] 4-Tier Memory — session persistence mirrors Cache tier
  Quake's Cache (PU_CACHE=101) is the transient-but-reusable memory tier.
  Sessions are the Cache tier: transient (lost on engine restart in transient
  mode) but persistent when actively maintained (saved to disk).
[id-soft: quake-1996] Grace Period — session archive follows 0.5s rule
  Session archival defers cleanup for TOMBSTONE_GRACE_SECONDS to prevent
  in-flight requests from writing to a closed session.
"""

import json
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import logging
import os
import time
import uuid
import anyio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SESSION_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")
)) / "sessions"


class SessionManager:
    """Manages entity-scoped rolling sessions."""

    def __init__(self, session_dir: Optional[Path] = None):
        self.session_dir = session_dir or SESSION_DIR
        if os.environ.get("OMEGA_ENV") != "test":
            self.session_dir.mkdir(parents=True, exist_ok=True)

    async def get_session_id(self, entity_name: str) -> str:
        """Get or create the active session ID for an entity.
        
        Returns existing session if same day, otherwise creates new one.
        Session ID format: ses_{YYYYMMDD}_{entity_slug}_{counter}
        """
        entity_slug = entity_name.lower().replace(" ", "_")
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        active_file = self.session_dir / f"{entity_slug}.active"

        # Use atomic file creation to prevent TOCTOU race (C-MEM-002)
        lock_file = self.session_dir / f"{entity_slug}.lock"
        
        try:
            # Attempt to create lock file atomically
            def _create_lock():
                try:
                    fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    os.close(fd)
                    return True
                except FileExistsError:
                    # Check for stale lock (older than 30 seconds)
                    try:
                        age = time.time() - lock_file.stat().st_mtime
                        if age > 30:
                            lock_file.unlink()
                            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                            os.close(fd)
                            return True
                    except (OSError, FileNotFoundError):
                        pass
                    return False

            while not await anyio.to_thread.run_sync(_create_lock):
                await anyio.sleep(0.01)

            counter = 1
            if await anyio.Path(active_file).exists():
                try:
                    async with await anyio.open_file(str(active_file), "r") as f:
                        content = await f.read()
                        data = json.loads(content)
                        stored_date = data.get("date", "")
                        if stored_date == today:
                            return data.get("session_id", "")
                        counter = data.get("counter", 0) + 1
                except (json.JSONDecodeError, KeyError, OSError) as e:
                    logger.warning(f"Failed to read session file {active_file}: {e}")

            session_id = f"ses_{today}_{entity_slug}_{counter:03d}"
            
            # Sovereign Atomic Write: Flush -> Sync -> Commit -> Anchor
            data = {
                "date": today,
                "session_id": session_id,
                "counter": counter,
                "entity": entity_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await anyio.to_thread.run_sync(self._write_session_atomic, active_file, data)
            
            return session_id
        finally:
            if await anyio.Path(lock_file).exists():
                await anyio.Path(lock_file).unlink()

    def _write_session_atomic(self, target_path: Path, data: dict) -> None:
        """Physically synchronize session data to disk. (Sovereign Pattern)"""
        temp_path = target_path.with_suffix(f".{os.getpid()}.tmp")
        try:
            # 1. Write and Sync File
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # 2. Atomic Replace
            os.replace(temp_path, target_path)
            
            # 3. Anchor: Sync Parent Directory
            parent_dir = target_path.parent
            dir_fd = os.open(str(parent_dir), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OmegaError:
            if temp_path.exists():
                temp_path.unlink()
            raise
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Sovereign atomic write failed for {target_path}: {e}", exc_info=True)
            raise OmegaPersistenceError(f"Session write failed: {e}", raw_error=e) from e

    def get_session_id_transient(self, trace_id: str) -> str:
        """Return trace_id as session_id for transient mode."""
        return trace_id
