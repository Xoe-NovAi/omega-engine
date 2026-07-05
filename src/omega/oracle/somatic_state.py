# AP: AP-SOMATIC-SSTATE-v1.0.0
# AP: AP-SOMATIC-SSTATE-v1.0.0
# 🔱 Somatic State Manager — Binary LLM State Serialization
# Mandate M20: Model session state MUST be serializable and resumable via low-level bindings.

import logging
import anyio
from typing import Optional
from pathlib import Path
import llama_cpp

logger = logging.getLogger(__name__)

class SomaticStateManager:
    """
    Handles the capture and restoration of the LLM's internal state (KV cache).
    
    This allows the Omega Engine to 'freeze' a model's cognitive state and 
    resume it later without re-processing the entire prompt.
    """
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    async def capture_state(self, context_ptr: int, state_id: str) -> bool:
        """
        Captures the current state of the LLM context and saves it to disk.
        
        Args:
            context_ptr: The raw pointer to the llama_context.
            state_id: Unique identifier for the state snapshot.
        """
        try:
            # Wrap blocking C-call in anyio thread
            state_bytes = await anyio.to_thread.run_sync(
                llama_cpp.llama_copy_state_data, context_ptr
            )
            
            if not state_bytes:
                logger.error(f"Somatic capture failed: No state data returned for {state_id}")
                return False
            
            file_path = self.state_dir / f"{state_id}.somatic"
            async with await anyio.to_thread.run_sync(open, file_path, "wb") as f:
                f.write(state_bytes)
                
            logger.info(f"Somatic state captured: {state_id} ({len(state_bytes)} bytes)")
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Somatic capture error for {state_id}: {e}", exc_info=True)
            return False

    async def restore_state(self, context_ptr: int, state_id: str) -> bool:
        """
        Restores a previously captured state into the LLM context.
        
        Args:
            context_ptr: The raw pointer to the llama_context.
            state_id: Unique identifier for the state snapshot.
        """
        try:
            file_path = self.state_dir / f"{state_id}.somatic"
            if not file_path.exists():
                logger.error(f"Somatic restore failed: State file {state_id} not found")
                return False
            
            state_bytes = await anyio.to_thread.run_sync(
                lambda: file_path.read_bytes()
            )
            
            # Wrap blocking C-call in anyio thread
            await anyio.to_thread.run_sync(
                llama_cpp.llama_set_state_data, context_ptr, state_bytes
            )
            
            logger.info(f"Somatic state restored: {state_id}")
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Somatic restore error for {state_id}: {e}", exc_info=True)
            return False

    async def purge_state(self, state_id: str):
        """Removes a state snapshot from disk."""
        file_path = self.state_dir / f"{state_id}.somatic"
        if file_path.exists():
            await anyio.to_thread.run_sync(os.remove, file_path)
