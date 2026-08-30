# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Arcana-NovAi — Mnemosyne Memory Adapter
# ⬡ OMEGA ⬡ ARCA.NA-NOVAI ⬡ MNEMOSYNE ⬡ v1.1.0 ⬡ 2026-06-15
"""
13-sphere Kabbalistic memory adapter for the Arcana-NovAi WAD.

Per M2 (Engine-Stack Firewall), this entire module lives in the WAD layer.
The core engine knows nothing of spheres, qliphoth, or Kabbalah — it only
speaks IMemoryAdapter.

Mnemosyne (Μνημοσύνη) is the Titaness of Memory, mother of the Nine Muses.
In this system, she is the 13th sphere — the record-keeper that bridges
all other spheres by tracking entity session history, shadow state, and
failure taxonomy.

Architecture:
    MnemosyneAdapter
      ├── file_provider: FileStorageProvider  (exchange persistence)
      ├── vault_dir: Path                      (shadow state storage)
      ├── spheres: dict                        (loaded from spheres.yaml)
      └── qliphoth: dict                       (loaded from qliphoth.yaml)
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import yaml

from omega.memory.adapters import IMemoryAdapter, MemoryRecord, MemoryType, MemoryPriority

logger = logging.getLogger(__name__)

# P2: File size guard for YAML loading — 10MB max
MAX_YAML_SIZE = 10 * 1024 * 1024  # 10MB


def _get_wad_dir() -> Path:
    """Get the Arcana-NovAi WAD directory."""
    return Path(__file__).resolve().parent.parent


def _get_vault_dir() -> Path:
    """Get vault data directory (under engine data dir, not WAD)."""
    data_dir = Path(os.environ.get(
        "OMEGA_DATA_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent.parent / "data")
    ))
    return data_dir / "wads" / "arcana_novai" / "vaults"


async def _load_yaml_async(name: str) -> dict:
    """Load a YAML file from the WAD directory asynchronously.
    
    P2: Enforces 10MB file size guard to prevent OOM on malicious/large files.
    """
    path = _get_wad_dir() / name
    if not await anyio.Path(path).exists():
        logger.warning(f"WAD data file not found: {path}")
        return {}
    
    # P2: File size guard - reject files > 10MB
    try:
        stat = await anyio.Path(path).stat()
        if stat.st_size > MAX_YAML_SIZE:
            logger.error(f"WAD data file {path} exceeds {MAX_YAML_SIZE} bytes ({stat.st_size} bytes). Refusing to load.")
            return {}
    except OSError as e:
        logger.warning(f"Failed to stat WAD data file {path}: {e}")
        return {}
    
    try:
        async with await anyio.open_file(str(path), "r") as f:
            content = await f.read()
            return yaml.safe_load(content) or {}
    except Exception as e:
        logger.warning(f"Failed to load WAD data file {path}: {e}")
        return {}


class MnemosyneAdapter(IMemoryAdapter):
    """13-sphere Kabbalistic memory adapter for Arcana-NovAi entities.

    Wraps FileStorageProvider for exchange history, adds vault CRUD for
    shadow state (evolution_stage, shadow_xp, session tracking), and
    provides sphere/qliphoth queries from WAD data files.
    """

    def __init__(self):
        self._vault_dir: Optional[Path] = None
        self._spheres: dict = {}
        self._qliphoth: dict = {}
        self._entity_spheres: dict = {}
        self._closed = False
        self._initialized = False

    async def initialize(self) -> None:
        """Async initialization - load sphere/qliphoth data and create vault directory.
        
        MUST be called after construction before any other methods.
        This is an async method because it performs I/O (file reads, directory creation).
        """
        if self._initialized:
            return
        
        # Initialize vault directory asynchronously
        self._vault_dir = _get_vault_dir()
        await anyio.Path(self._vault_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            spheres_data = await _load_yaml_async("spheres.yaml")
            self._spheres = spheres_data.get("spheres", {})
            self._entity_spheres = spheres_data.get("entity_spheres", {})
            logger.info(f"Loaded {len(self._spheres)} spheres and {len(self._entity_spheres)} entity mappings")
        except Exception as e:
            logger.warning(f"Failed to load spheres.yaml: {e}")

        try:
            q_data = await _load_yaml_async("qliphoth.yaml")
            self._qliphoth = q_data.get("qliphoth", {})
            logger.info(f"Loaded {len(self._qliphoth)} Qliphothic shells")
        except Exception as e:
            logger.warning(f"Failed to load qliphoth.yaml: {e}")

        self._initialized = True

    # ── I/O Helpers (async) ──

    async def _vault_path(self, entity_name: str, vault_key: str) -> Path:
        """Get the filesystem path for a vault entry (async mkdir)."""
        if self._vault_dir is None:
            raise RuntimeError("Adapter not initialized - call initialize() first")
        entity_dir = self._vault_dir / entity_name
        await anyio.Path(entity_dir).mkdir(parents=True, exist_ok=True)
        return entity_dir / f"{vault_key}.json"

    async def _read_vault_json(self, path: Path) -> Optional[Dict[str, Any]]:
        """Read a JSON vault file asynchronously, returning None if missing or corrupt."""
        if not await anyio.Path(path).exists():
            return None
        try:
            async with await anyio.open_file(str(path), "r") as f:
                content = await f.read()
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Corrupt vault file {path}: {e}")
            return None

    async def _write_vault_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Write a JSON vault file atomically via .tmp rename (async)."""
        tmp_path = path.with_suffix(".tmp")
        # Use anyio for async file write with fsync
        async with await anyio.open_file(str(tmp_path), "w") as f:
            await f.write(json.dumps(data, indent=2))
            await f.flush()
            # fsync on the open file handle
            await anyio.to_thread.run_sync(os.fsync, f.fileno())
        await anyio.Path(tmp_path).rename(path)

    # ── Core IMemoryAdapter Methods ──

    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Retrieve exchange history (delegated to file vault storage)."""
        vault = await self.get_vault(entity_name, f"session_{session_id}")
        if vault is None:
            return []
        exchanges = vault.get("exchanges", [])
        return exchanges[-limit:]

    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        """Persist exchange history (delegated to file vault storage)."""
        path = await self._vault_path(entity_name, f"session_{session_id}")
        data = {
            "session_id": session_id,
            "entity_name": entity_name,
            "exchange_count": len(exchanges),
            "timestamp": time.time(),
            "exchanges": exchanges,
        }
        await self._write_vault_json(path, data)

    async def archive(self, entity_name: str, session_id: str) -> bool:
        """Archive a session by writing a summary and removing live data."""
        vault = await self.get_vault(entity_name, f"session_{session_id}")
        if vault is None:
            return False

        if self._vault_dir is None:
            raise RuntimeError("Adapter not initialized - call initialize() first")
        
        # Write an archive summary
        archive_path = self._vault_dir / entity_name / "archive"
        await anyio.Path(archive_path).mkdir(parents=True, exist_ok=True)
        archive_file = archive_path / f"{session_id}.json"
        await self._write_vault_json(archive_file, {
            "session_id": session_id,
            "entity_name": entity_name,
            "archived_at": time.time(),
            "summary": {
                "exchange_count": vault.get("exchange_count", 0),
                "timestamp": vault.get("timestamp", 0),
            },
        })

        # Remove live session file
        live_path = await self._vault_path(entity_name, f"session_{session_id}")
        if await anyio.Path(live_path).exists():
            await anyio.Path(live_path).unlink()
        return True

    async def close(self) -> None:
        """Release resources."""
        self._closed = True
        self._spheres.clear()
        self._qliphoth.clear()
        self._entity_spheres.clear()

    # ── Vault Operations ──

    async def get_vault(
        self, entity_name: str, vault_key: str
    ) -> Optional[Dict[str, Any]]:
        """Read a vault entry from the entity's JSON shadow state."""
        path = await self._vault_path(entity_name, vault_key)
        return await self._read_vault_json(path)

    async def put_vault(
        self, entity_name: str, vault_key: str, data: Dict[str, Any]
    ) -> None:
        """Write a vault entry to the entity's JSON shadow state."""
        path = await self._vault_path(entity_name, vault_key)
        await self._write_vault_json(path, data)

    # ── Lifecycle Hooks ──

    async def on_session_end(
        self, entity_name: str, session_transcript: str, trace_id: Optional[str] = None
    ) -> List[MemoryRecord]:
        """On session end, update shadow state and return a distilled record.
        
        Args:
            entity_name: Name of the entity
            session_transcript: Full session transcript for distillation
            trace_id: Optional trace ID for observability correlation
        """
        # Update shadow state
        shadow = await self.get_vault(entity_name, "shadow") or {}
        shadow["session_count"] = shadow.get("session_count", 0) + 1
        shadow["evolution_stage"] = self._calculate_evolution(shadow)
        if trace_id:
            shadow["last_trace_id"] = trace_id
        await self.put_vault(entity_name, "shadow", shadow)

        # Return a single memory record for the session
        return [
            MemoryRecord(
                memory_id=f"session_end_{entity_name}_{int(time.time())}",
                entity_name=entity_name,
                memory_type=MemoryType.EPISODIC,
                priority=MemoryPriority.NORMAL,
                content=f"Session ended for {entity_name}. Total sessions: {shadow.get('session_count', 0)}",
                metadata={
                    "event": "session_end",
                    "session_count": shadow.get("session_count", 0),
                    "evolution_stage": shadow.get("evolution_stage", "DORMANT"),
                    "trace_id": trace_id,
                },
                timestamp=time.time(),
                source_trace_id=trace_id,
            )
        ]

    async def on_pre_compact(
        self, entity_name: str, session_id: str
    ) -> Dict[str, Any]:
        """Before compacting, preserve vault state into a compacting checkpoint."""
        shadow = await self.get_vault(entity_name, "shadow") or {}
        return {
            "vault_snapshot": shadow,
            "sphere": self._entity_spheres.get(entity_name),
            "adapter": "mnemosyne",
        }

    # ── Sphere Operations ──

    async def get_sphere(
        self, entity_name: str, sphere_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sphere metadata for an entity."""
        if sphere_name:
            sphere = self._spheres.get(sphere_name)
            if sphere:
                return dict(sphere)
            return {}

        # Look up by entity name
        sphere_key = self._entity_spheres.get(entity_name)
        if not sphere_key:
            return {}
        sphere = self._spheres.get(sphere_key)
        if not sphere:
            return {}
        return dict(sphere)

    async def get_qliphoth(
        self, entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Qliphothic failure taxonomy (optionally filtered by entity)."""
        if entity_name:
            # Check if this entity has Qliphothic history
            history = await self.get_vault(entity_name, "qliphoth_history")
            if history:
                return {"shells": self._qliphoth, "history": history}
            return {"shells": self._qliphoth, "history": {"failures": []}}
        return {"shells": self._qliphoth}

    # ── Internal ──

    def _calculate_evolution(self, shadow: Dict[str, Any]) -> str:
        """Calculate evolution stage based on session metrics."""
        stages = ["DORMANT", "AWAKENING", "ACTIVE", "EVOLVING", "TRANSCENDENT"]
        session_count = shadow.get("session_count", 0)
        exchange_count = shadow.get("exchange_count", 0)
        last_audit = shadow.get("last_audit_score", 0)

        if session_count == 0:
            return "DORMANT"
        elif session_count < 3:
            return "AWAKENING"
        elif session_count < 10:
            return "ACTIVE"
        elif session_count >= 10 and last_audit and last_audit >= 0.8:
            return "TRANSCENDENT"
        elif session_count >= 10:
            return "EVOLVING"
        return "ACTIVE"

    def get_status(self) -> Dict[str, Any]:
        """Get adapter status for observability."""
        return {
            "adapter": "MnemosyneAdapter",
            "type": "13-sphere Kabbalistic",
            "vault_dir": str(self._vault_dir),
            "spheres_loaded": len(self._spheres),
            "qliphoth_loaded": len(self._qliphoth),
            "entity_mappings": len(self._entity_spheres),
            "closed": self._closed,
        }
