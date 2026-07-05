"""Unified State Manager (USM) — Coordinates CAS and state indexing.
AP: AP-USM-MANAGER-v1.0.0
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import anyio
from omega.errors import OmegaPersistenceError, StateIntegrityError
from .cas import CASManager

logger = logging.getLogger(__name__)

class USMManager:
    """The Unified State Manager.
    
    Provides a high-level interface for saving and loading engine state
    using a Content Addressable Storage (CAS) backend and a SQLite index.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(os.environ.get(
            "OMEGA_DATA_DIR", 
            str(Path(__file__).resolve().parent.parent.parent.parent / "data")
        )) / "state"
        
        self.cas = CASManager(base_dir=self.base_dir / "blobs")
        self.index_path = self.base_dir / "index.db"
        self._db_conn: Optional[sqlite3.Connection] = None

    async def initialize(self) -> None:
        """Initialize CAS and the SQLite index."""
        await self.cas.initialize()
        await anyio.Path(self.base_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite index
        await anyio.to_thread.run_sync(self._init_db)

    def _init_db(self) -> None:
        """Create the state index table if it doesn't exist."""
        with sqlite3.connect(self.index_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state_refs (
                    key TEXT PRIMARY KEY,
                    hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            conn.commit()

    async def save_state(self, key: str, data: Any) -> str:
        """Serialize data, store in CAS, and update the index.
        
        Args:
            key: Human-readable identifier (e.g., 'session:test_entity:active').
            data: Data to store (must be JSON serializable or bytes).
            
        Returns:
            The CAS hash of the stored state.
        """
        # 1. Serialize
        if isinstance(data, bytes):
            blob = data
        else:
            blob = json.dumps(data, indent=2, default=str).encode("utf-8")
        
        # 2. Store in CAS
        blob_hash = await self.cas.put(blob)
        
        # 3. Update Index
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            await anyio.to_thread.run_sync(
                self._update_index, key, blob_hash, timestamp
            )
        except (sqlite3.Error, OSError) as e:
            logger.error(f"USM index update failed for {key}: {e}", exc_info=True)
            raise OmegaPersistenceError(f"Failed to index state {key}: {e}", raw_error=e) from e
            
        return blob_hash

    def _update_index(self, key: str, blob_hash: str, timestamp: str) -> None:
        with sqlite3.connect(self.index_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO state_refs (key, hash, timestamp) VALUES (?, ?, ?)",
                (key, blob_hash, timestamp)
            )
            conn.commit()

    async def load_state(self, key: str) -> Any:
        """Retrieve and deserialize state for a given key.
        
        Returns:
            The original data (bytes or JSON-decoded object).
        """
        # 1. Look up hash in index
        blob_hash = await anyio.to_thread.run_sync(self._get_hash, key)
        if not blob_hash:
            return None
            
        # 2. Retrieve from CAS
        blob = await self.cas.get(blob_hash)
        
        # 3. Deserialize (try JSON first, then return bytes)
        try:
            return json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return blob

    def _get_hash(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("SELECT hash FROM state_refs WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    async def snapshot(self, keys: List[str]) -> str:
        """Create a snapshot of multiple state keys.
        
        Returns a manifest hash that can be used to restore the entire set.
        """
        manifest = {}
        for key in keys:
            blob_hash = await anyio.to_thread.run_sync(self._get_hash, key)
            if blob_hash:
                manifest[key] = blob_hash
        
        # Store the manifest itself in CAS
        manifest_blob = json.dumps(manifest, indent=2).encode("utf-8")
        return await self.cas.put(manifest_blob)

    async def restore_snapshot(self, manifest_hash: str) -> Dict[str, str]:
        """Restore a snapshot and return the mapping of keys to hashes.
        
        Note: This updates the index to point to the snapshot's hashes.
        """
        manifest_blob = await self.cas.get(manifest_hash)
        manifest = json.loads(manifest_blob.decode("utf-8"))
        
        for key, blob_hash in manifest.items():
            timestamp = datetime.now(timezone.utc).isoformat()
            await anyio.to_thread.run_sync(
                self._update_index, key, blob_hash, timestamp
            )
            
        return manifest

    async def close(self) -> None:
        """Close resources."""
        # SQLite connections are handled via context managers in this impl.
        pass
