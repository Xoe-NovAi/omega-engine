# AP: AP-STATE-MANAGER-v1.0.0
import os
import hashlib
import shutil
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import anyio
from anyio.to_thread import run_sync

logger = logging.getLogger("omega.state_manager")

@dataclass
class SomaticStateKey:
    """Unique identifier for a binary model state."""
    model_hash: str
    session_id: str
    kv_size: int
    version: str = "1.0.0"

class CASBlobStore:
    """
    Content Addressable Storage for engine state.
    Implements M12 (Queue Integrity) via atomic renames.
    """
    def __init__(self, base_dir: str = "data/somatic/blobs"):
        self.base_dir = Path(base_dir)
        self._ensure_dir()

    def _ensure_dir(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def put(self, data: bytes) -> str:
        """Writes data to a blob and returns its SHA256 hash."""
        blob_hash = hashlib.sha256(data).hexdigest()
        blob_path = self.base_dir / f"{blob_hash}.bin"
        
        if blob_path.exists():
            return blob_hash

        tmp_path = blob_path.with_suffix(".tmp")
        try:
            await run_sync(self._write_atomic, tmp_path, blob_path, data)
        except Exception as e:
            logger.error(f"Failed to write blob {blob_hash}: {e}")
            raise
        
        return blob_hash

    def _write_atomic(self, tmp_path: Path, final_path: Path, data: bytes):
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp_path, final_path)

    async def get(self, blob_hash: str) -> bytes:
        """Reads a blob by its hash."""
        blob_path = self.base_dir / f"{blob_hash}.bin"
        if not blob_path.exists():
            raise FileNotFoundError(f"Blob {blob_hash} not found in CAS")
        
        return await run_sync(self._read_blob, blob_path)

    def _read_blob(self, path: Path) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    async def exists(self, blob_hash: str) -> bool:
        return await run_sync(lambda: (self.base_dir / f"{blob_hash}.bin").exists())

class SomaticStateSerializer:
    """
    High-fidelity binary state serialization for llama-cpp-python.
    Implements M20 (SomaticState).
    """
    def __init__(self, model: any):
        self.model = model

    async def capture_state(self) -> bytes:
        """Captures the current KV cache state using the C-API."""
        return await run_sync(self._capture)

    def _capture(self) -> bytes:
        # Use the low-level C-API bindings for maximum fidelity
        # llama_get_state_size -> llama_copy_state_data
        import llama_cpp
        try:
            size = llama_cpp.llama_cpp.llama_get_state_size(self.model.model)
            buffer = bytearray(size)
            llama_cpp.llama_cpp.llama_copy_state_data(self.model.model, buffer)
            return bytes(buffer)
        except Exception as e:
            logger.error(f"Somatic capture failed: {e}")
            raise

    async def apply_state(self, state_data: bytes):
        """Restores the KV cache state using the C-API."""
        await run_sync(self._apply, state_data)

    def _apply(self, data: bytes):
        import llama_cpp
        try:
            # Verify size before applying to prevent segfaults
            expected_size = llama_cpp.llama_cpp.llama_get_state_size(self.model.model)
            if len(data) != expected_size:
                raise ValueError(f"Somatic state size mismatch: expected {expected_size}, got {len(data)}")
            
            llama_cpp.llama_cpp.llama_set_state_data(self.model.model, data)
        except Exception as e:
            logger.error(f"Somatic apply failed: {e}")
            raise

class UnifiedStateManager:
    """
    The facade for managing all engine state.
    Coordinates between CAS, SomaticState, and Entity Memory.
    """
    def __init__(self, model: any, base_dir: str = "data/somatic"):
        self.blob_store = CASBlobStore()
        self.somatic = SomaticStateSerializer(model)
        self.base_dir = Path(base_dir)
        self._ensure_dir()

    def _ensure_dir(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def freeze(self, entity_id: str, memory_data: bytes, session_data: bytes) -> str:
        """
        Captures a full cognitive snapshot.
        Returns a master hash of the state bundle.
        """
        # 1. Capture binary model state
        somatic_blob = await self.somatic.capture_state()
        somatic_hash = await self.blob_store.put(somatic_blob)
        
        # 2. Store memory and session as blobs
        mem_hash = await self.blob_store.put(memory_data)
        sess_hash = await self.blob_store.put(session_data)
        
        # 3. Create a state bundle manifest
        bundle = {
            "entity_id": entity_id,
            "somatic_hash": somatic_hash,
            "memory_hash": mem_hash,
            "session_hash": sess_hash,
            "timestamp": anyio.current_time() if hasattr(anyio, 'current_time') else None,
        }
        
        import json
        bundle_data = json.dumps(bundle, sort_keys=True).encode()
        return await self.blob_store.put(bundle_data)

    async def resume(self, bundle_hash: str):
        """
        Restores a full cognitive snapshot.
        """
        # 1. Load bundle manifest
        bundle_data = await self.blob_store.get(bundle_hash)
        import json
        bundle = json.loads(bundle_data)
        
        # 2. Restore binary state first
        somatic_blob = await self.blob_store.get(bundle['somatic_hash'])
        await self.somatic.apply_state(somatic_blob)
        
        # 3. Return memory and session data for the engine to load
        return {
            "memory": await self.blob_store.get(bundle['memory_hash']),
            "session": await self.blob_store.get(bundle['session_hash']),
            "entity_id": bundle['entity_id']
        }
