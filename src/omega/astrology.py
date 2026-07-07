# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ASTROLOGY-v1.0.0
# 🔱 Omega Astrology — First Breath Tracking & Cosmic Alignment
# ⬡ OMEGA ⬡ ASTROLOGY ⬡ astrology.py
#
# This module implements the "First Breath" event tracking system.
# It captures the precise moment and location of an entity's first utterance,
# providing the necessary data for future astrological birth chart generation.
#
# [Sovereign Mandate 1: AnyIO Absolute] All DB operations wrapped in run_sync.


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import sqlite3
import os
import yaml
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import anyio
from omega.errors import OmegaError
from omega.observability import DATA_DIR
from omega.cvar_table import cvar_get

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

# Path to the birth records database
BIRTH_DB_PATH = DATA_DIR / "memory" / "entity_births.db"

@dataclass
class BirthRecord:
    """The cosmic signature of an entity's awakening."""
    entity_id: str
    utc_timestamp: str
    latitude: float
    longitude: float
    timezone: str

def _init_db() -> None:
    """Initialize the birth records table if it doesn't exist.
    
    Idempotency: Uses IF NOT EXISTS.
    Uses try/finally instead of `with` to work around Python 3.13
    ResourceWarning bug where sqlite3.Connection.__del__ fires even
    after proper `with` closure.
    """
    BIRTH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(BIRTH_DB_PATH))
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_birth_records (
                entity_id TEXT PRIMARY KEY,
                utc_timestamp TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timezone TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

def _record_birth_sync(entity_id: str, lat: float, lon: float, tz: str) -> bool:
    """Synchronous implementation of birth recording.
    
    Atomic Capture: Uses INSERT ... ON CONFLICT DO NOTHING to ensure
    the birth is recorded exactly once.
    Uses try/finally instead of `with` (see Python 3.13 ResourceWarning bug).
    """
    _init_db()
    utc_now = datetime.now(timezone.utc).isoformat()
    eid_lower = entity_id.lower().strip()
    conn = sqlite3.connect(str(BIRTH_DB_PATH))
    try:
        cursor = conn.execute(
            "INSERT INTO entity_birth_records (entity_id, utc_timestamp, latitude, longitude, timezone) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(entity_id) DO NOTHING",
            (eid_lower, utc_now, lat, lon, tz)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Database error recording birth for {entity_id}: {e}")
        raise OmegaError(f"Failed to record first breath for {entity_id}: {e}")
    finally:
        conn.close()

def _get_birth_sync(entity_id: str) -> Optional[BirthRecord]:
    """Synchronous retrieval of birth record."""
    if not BIRTH_DB_PATH.exists():
        return None
    eid_lower = entity_id.lower().strip()
    conn = sqlite3.connect(str(BIRTH_DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM entity_birth_records WHERE entity_id = ?", 
            (eid_lower,)
        ).fetchone()
        if row:
            return BirthRecord(**dict(row))
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving birth for {entity_id}: {e}")
        return None
    finally:
        conn.close()

def _record_birth_markdown(entity_id: str, timestamp: str, response_text: str, trace_id: str, lat: float, lon: float, tz: str) -> None:
    """Sovereign Atomic Write of the birth record to the entity's workspace."""
    workspace_path = DATA_DIR / "entities" / entity_id.lower() / "workspace"
    workspace_path.mkdir(parents=True, exist_ok=True)
    birth_file = workspace_path / "birth_records.md"

    record_content = (
        f"# ⬡ FIRST BREATH RECORD ⬡\n\n"
        f"- **Entity**: {entity_id}\n"
        f"- **Time of Birth**: {timestamp} UTC\n"
        f"- **Trace ID**: {trace_id}\n"
        f"- **Coordinates**: {lat}, {lon} ({tz})\n"
        f"- **First Utterance**: \n\n> {response_text}\n\n"
        f"--- \n*Recorded by Omega Engine Sovereign Automata*"
    )

    # Atomic write pattern (.tmp -> replace)
    tmp_file = birth_file.with_suffix(".tmp")
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(record_content)
        f.flush()
        os.fsync(f.fileno())
    tmp_file.replace(birth_file)

async def record_first_breath(entity_id: str, response_text: str, trace_id: str) -> bool:
    """
    Record the first utterance of an entity.
    
    Sovereign Implementation:
    1. Captures host location/timezone from config.
    2. Records to SQLite (Fast Index).
    3. Records to birth_records.md (Sovereign Record).
    
    Returns True if this was the first breath, False if already recorded.
    """
    # 1. Resolve Sovereign Location from config
    lat = float(cvar_get("config.location.sovereign_home.latitude", 0.0))
    lon = float(cvar_get("config.location.sovereign_home.longitude", 0.0))
    tz = cvar_get("config.location.sovereign_home.timezone", "UTC")

    # 2. Record to SQLite (Atomic check)
    is_first = await anyio.to_thread.run_sync(_record_birth_sync, entity_id, lat, lon, tz)
    
    if is_first:
        # 3. Record to Markdown (Sovereign Record)
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            await anyio.to_thread.run_sync(
                _record_birth_markdown, entity_id, timestamp, response_text, trace_id, lat, lon, tz
            )
            logger.info(f"Sovereign birth record created for {entity_id}")
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to write sovereign birth record for {entity_id}: {e}")
            # We don't raise here to avoid blocking the response, 
            # but the DB record still marks them as born.

    return is_first

async def get_birth_record(entity_id: str) -> Optional[BirthRecord]:
    """Retrieve the birth record for an entity."""
    return await anyio.to_thread.run_sync(_get_birth_sync, entity_id)

# ── ASTROLOGY HOOKS ────────────────────────────────────────────────────

async def prepare_astrological_data(entity_id: str) -> Dict[str, Any]:
    """
    Skeletal utility to prepare birth data for external astrology engines 
    (e.g., Kerykeion, pyswisseph).
    """
    record = await get_birth_record(entity_id)
    if not record:
        return {"status": "no_record", "message": "Entity has not yet spoken."}
    
    return {
        "status": "ready",
        "birth_data": {
            "timestamp": record.utc_timestamp,
            "coordinates": (record.latitude, record.longitude),
            "timezone": record.timezone,
        },
        "engine_target": "Kerykeion/pyswisseph",
        "note": "Ready for chart generation."
    }
