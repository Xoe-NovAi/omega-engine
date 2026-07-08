"""Unified State Manager (USM) — Coordinates CAS and state indexing.
AP: AP-USM-MANAGER-v1.0.0
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

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

    async def put(self, key: str, data: Any) -> str:
        """Serialize data, store in CAS, and update the index."""
        return await self.save_state(key, data)

    def _update_index(self, key: str, blob_hash: str, timestamp: str) -> None:
        with sqlite3.connect(self.index_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO state_refs (key, hash, timestamp) VALUES (?, ?, ?)",
                (key, blob_hash, timestamp)
            )
            conn.commit()

    async def get(self, key: str) -> Any:
        """Retrieve and deserialize state for a given key."""
        return await self.load_state(key)

    async def save_state(self, key: str, data: Any) -> str:
        """Internal implementation of state saving."""
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

    async def load_state(self, key: str) -> Any:
        """Internal implementation of state loading."""
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

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the state index."""
        blob_hash = await anyio.to_thread.run_sync(self._get_hash, key)
        return blob_hash is not None

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

    # ===== Convenience methods for common state types =====
    
    async def save_session(self, session_id: str, yaml_data: str) -> str:
        """Save session YAML to CAS. Returns content hash."""
        if not yaml_data:
            raise ValueError("Cannot save empty session")
        hash_ = await self.save_state(f"session:{session_id}", yaml_data)
        return hash_
    
    async def load_session(self, session_id: str) -> str:
        """Load session YAML from CAS. Returns YAML string."""
        data = await self.load_state(f"session:{session_id}")
        if data is None:
            raise KeyError(f"Session not tracked: {session_id}")
        return data
    
    def has_session(self, session_id: str) -> bool:
        """Check if session exists in index."""
        # This is a sync check - we'd need async for full check
        # For now, just check if key exists in index
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("SELECT 1 FROM state_refs WHERE key = ?", (f"session:{session_id}",))
            return cursor.fetchone() is not None
    
    async def release_session(self, session_id: str) -> bool:
        """Release session reference. Delete from CAS if unreferenced."""
        # Note: Full refcounting would require CAS-level refcounts
        # For now, just remove from index
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("DELETE FROM state_refs WHERE key = ?", (f"session:{session_id}",))
            conn.commit()
            return cursor.rowcount > 0
    
    async def save_memory(self, entity_id: str, json_data: str) -> str:
        """Save entity memory JSON to CAS. Returns content hash."""
        if not json_data:
            raise ValueError("Cannot save empty memory")
        hash_ = await self.save_state(f"mem:{entity_id}", json_data)
        return hash_
    
    async def load_memory(self, entity_id: str) -> str:
        """Load entity memory JSON from CAS. Returns JSON string."""
        data = await self.load_state(f"mem:{entity_id}")
        if data is None:
            raise KeyError(f"Memory not tracked: {entity_id}")
        return data
    
    def has_memory(self, entity_id: str) -> bool:
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("SELECT 1 FROM state_refs WHERE key = ?", (f"mem:{entity_id}",))
            return cursor.fetchone() is not None
    
    async def release_memory(self, entity_id: str) -> bool:
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("DELETE FROM state_refs WHERE key = ?", (f"mem:{entity_id}",))
            conn.commit()
            return cursor.rowcount > 0
    
    async def save_handoff(self, packet_id: str, payload: bytes) -> str:
        """Save handoff payload to CAS. Returns content hash."""
        if not payload:
            raise ValueError("Cannot save empty handoff")
        hash_ = await self.save_state(f"handoff:{packet_id}", payload)
        return hash_
    
    async def load_handoff(self, packet_id: str) -> bytes:
        """Load handoff payload from CAS."""
        data = await self.load_state(f"handoff:{packet_id}")
        if data is None:
            raise KeyError(f"Handoff not tracked: {packet_id}")
        if isinstance(data, str):
            return data.encode('utf-8')
        return data
    
    def has_handoff(self, packet_id: str) -> bool:
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("SELECT 1 FROM state_refs WHERE key = ?", (f"handoff:{packet_id}",))
            return cursor.fetchone() is not None
    
    async def release_handoff(self, packet_id: str) -> bool:
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            cursor = conn.execute("DELETE FROM state_refs WHERE key = ?", (f"handoff:{packet_id}",))
            conn.commit()
            return cursor.rowcount > 0
    
    def stats(self) -> dict:
        """Return combined statistics."""
        cas_stats = self.cas.stats()
        
        # Count entries in index
        import sqlite3
        with sqlite3.connect(self.index_path) as conn:
            sessions = conn.execute("SELECT COUNT(*) FROM state_refs WHERE key LIKE 'session:%'").fetchone()[0]
            memories = conn.execute("SELECT COUNT(*) FROM state_refs WHERE key LIKE 'mem:%'").fetchone()[0]
            handoffs = conn.execute("SELECT COUNT(*) FROM state_refs WHERE key LIKE 'handoff:%'").fetchone()[0]
            
        return {
            "cas": cas_stats,
            "tracked_sessions": sessions,
            "tracked_memories": memories,
            "tracked_handoffs": handoffs,
            "somatic_available": False,  # SomaticStateManager not integrated here
        }
