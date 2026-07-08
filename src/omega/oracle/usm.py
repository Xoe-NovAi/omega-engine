# AP: AP-USM-v1.0.0
import os
import hashlib
import shutil
import anyio
from pathlib import Path
from typing import Optional, Union, Dict, Any
from dataclasses import dataclass, field
import ctypes

# --- Sovereign Mandates ---
# M1: AnyIO Absolute - All blocking I/O wrapped in to_thread.run_sync
# M2: Engine-Stack Firewall - USM is Core Engine logic
# M20: SomaticState - Binary LLM state serialization via ctypes

@dataclass
class SomaticState:
    \"\"\"
    Represents a serialized snapshot of a model's internal state (KV cache, etc.).
    [SomaticState: M20]
    \"\"\"
    blob_id: str
    size: int
    model_id: str
    context_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class UnifiedStateManager:
    \"\"\"
    Unified State Manager (USM) - The single source of truth for all engine state.
    Implements Content Addressable Storage (CAS) for binary blobs, sessions, and memory.
    [Sovereign Bedrock: Strike 2]
    \"\"\"
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.blob_dir = data_dir / \"blobs\"
        self.session_dir = data_dir / \"sessions\"
        self.memory_dir = data_dir / \"memory\"
        
        # Ensure directories exist
        self.blob_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    async def store_blob(self, data: bytes) -> str:
        \"\"\"
        Stores a binary blob in CAS and returns its SHA-256 hash.
        [CAS: Content Addressable Storage]
        \"\"\"
        blob_id = hashlib.sha256(data).hexdigest()
        
        # Sharding: blobs/ab/cd/hash
        shard_dir = self.blob_dir / blob_id[:2] / blob_id[2:4]
        shard_dir.mkdir(parents=True, exist_ok=True)
        
        blob_path = shard_dir / blob_id
        
        if not blob_path.exists():
            # Atomic write: .tmp -> final
            tmp_path = blob_path.with_suffix(\".tmp\")
            await anyio.to_thread.run_sync(tmp_path.write_bytes, data)
            await anyio.to_thread.run_sync(tmp_path.rename, blob_path)
            
        return blob_id

    async def retrieve_blob(self, blob_id: str) -> bytes:
        \"\"\"
        Retrieves a binary blob from CAS by its hash.
        \"\"\"
        shard_dir = self.blob_dir / blob_id[:2] / blob_id[2:4]
        blob_path = shard_dir / blob_id
        
        if not blob_path.exists():
            raise FileNotFoundError(f\"Blob {blob_id} not found in CAS\")
            
        return await anyio.to_thread.run_sync(blob_path.read_bytes)

    async def capture_somatic_state(self, llama_instance: Any) -> SomaticState:
        \"\"\"
        Captures the current internal state of a Llama model.
        [SomaticState: M20]
        \"\"\"
        # Use the high-level save_state() from llama-cpp-python
        # This returns a LlamaState object containing the binary buffer
        state = await anyio.to_thread.run_sync(llama_instance.save_state)
        
        # Extract the binary buffer (llama_state)
        # LlamaState.llama_state is a ctypes array
        binary_data = bytes(state.llama_state)
        
        blob_id = await self.store_blob(binary_data)
        
        return SomaticState(
            blob_id=blob_id,
            size=len(binary_data),
            model_id=getattr(llama_instance, \"model_id\", \"unknown\"),
            context_size=getattr(llama_instance, \"n_ctx\", 0)
        )

    async def restore_somatic_state(self, llama_instance: Any, somatic_state: SomaticState) -> None:
        \"\"\"
        Restores a model's internal state from a SomaticState snapshot.
        [SomaticState: M20]
        \"\"\"
        binary_data = await self.retrieve_blob(somatic_state.blob_id)
        
        if len(binary_data) != somatic_state.size:
            raise ValueError(f\"Blob size mismatch: expected {somatic_state.size}, got {len(binary_data)}\")
            
        # Convert bytes back to the expected ctypes array for load_state
        # Llama.load_state expects a LlamaState object or a compatible buffer
        # We can create a dummy LlamaState-like object or use the low-level API
        
        # Using the low-level API for maximum precision:
        # llama_cpp.llama_state_set_data(ctx, src, size)
        
        from llama_cpp import llama_cpp
        ctx = llama_instance._ctx.ctx
        
        # Create the ctypes array from the binary data
        state_array = (ctypes.c_uint8 * len(binary_data)).from_buffer_copy(binary_data)
        
        result = await anyio.to_thread.run_sync(
            llama_cpp.llama_state_set_data, 
            ctx, 
            state_array, 
            len(binary_data)
        )
        
        if result != len(binary_data):
            raise RuntimeError(f\"Failed to restore somatic state: expected {len(binary_data)} bytes, restored {result}\")
