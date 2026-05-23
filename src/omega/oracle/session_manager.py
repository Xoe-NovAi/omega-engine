"""Session Manager — Entity-scoped rolling sessions with daily counter.

Implements the R50 session architecture. Each entity has one active session
per day, persisted to data/sessions/{entity}.active. Transient mode falls
back to trace_id with no persistence.
"""

import json
import logging
import os
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

        # Use a simple lock file to prevent concurrent RMW collisions
        lock_file = self.session_dir / f"{entity_slug}.lock"
        
        try:
            # Simple spin-lock for file access
            while await anyio.Path(lock_file).exists():
                await anyio.sleep(0.01)
            
            await anyio.Path(lock_file).touch()

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

            # Persist active session
            async with await anyio.open_file(str(active_file), "w") as f:
                await f.write(json.dumps({
                    "date": today,
                    "counter": counter,
                    "session_id": session_id,
                    "entity": entity_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }, indent=2))
            
            return session_id
        finally:
            if await anyio.Path(lock_file).exists():
                await anyio.Path(lock_file).unlink()

    def get_session_id_transient(self, trace_id: str) -> str:
        """Return trace_id as session_id for transient mode."""
        return trace_id
