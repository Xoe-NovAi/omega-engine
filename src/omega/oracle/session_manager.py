# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ORACLE-RESTORE-v2.3.0
"""Session Manager — Entity-scoped rolling sessions with daily counter.

Implements the R50 session architecture. Each entity has one active session
per day, persisted to data/sessions/{entity}.active. Transient mode falls
back to trace_id with no persistence.

[id-soft: vet-009] 4-Tier Memory — session persistence mirrors Cache tier
  Quake's Cache (PU_CACHE=101) is the transient-but-reusable memory tier.
  Sessions are the Cache tier: transient (lost on engine restart in transient
  mode) but persistent when actively maintained (saved to disk).
[id-soft: vet-008] Grace Period — session archive follows 0.5s rule
  Session archival defers cleanup for TOMBSTONE_GRACE_SECONDS to prevent
  in-flight requests from writing to a closed session.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import json
import logging
import os
import time
import anyio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from omega.state import get_usm

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

SESSION_DIR = (
    Path(
        os.environ.get(
            "OMEGA_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent.parent / "data")
        )
    )
    / "sessions"
)


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
        usm = get_usm()
        state_key = f"session:{entity_slug}:active"

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
            data = await usm.get(state_key)
            if data:
                try:
                    stored_date = data.get("date", "")
                    if stored_date == today:
                        return data.get("session_id", "")
                    counter = data.get("counter", 0) + 1
                except (json.JSONDecodeError, KeyError, OSError) as e:
                    logger.warning(f"Failed to process session state for {entity_slug}: {e}")

            session_id = f"ses_{today}_{entity_slug}_{counter:03d}"

            # Sovereign Atomic Write via USM
            data = {
                "date": today,
                "session_id": session_id,
                "counter": counter,
                "entity": entity_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await usm.put(state_key, data)

            # Create .active file for Hub visibility
            active_file = self.session_dir / f"{entity_slug}.active"

            def _write_active():
                with open(active_file, "w") as f:
                    json.dump(data, f)

            await anyio.to_thread.run_sync(_write_active)

            return session_id
        finally:
            if await anyio.Path(lock_file).exists():
                await anyio.Path(lock_file).unlink()

    def get_session_id_transient(self, trace_id: str) -> str:
        """Return trace_id as session_id for transient mode."""
        return trace_id
