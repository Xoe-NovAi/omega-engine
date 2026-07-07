# AP: AP-HEADROOM-MIDDLEWARE-v1.0.0
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import anyio
from omega.errors import OmegaError
from omega.oracle.entity_registry import EntityRegistry

# [M1 AnyIO Absolute] headroom-ai is an optional dep; gracefully degrade
# if not installed (fallback behavior in each method)
try:
    import headroom
    HAS_HEADROOM = True
except ImportError:
    HAS_HEADROOM = False
    logger = logging.getLogger("omega.headroom")
    logger.info("headroom-ai not installed — compression disabled, pass-through mode active")
    headroom = None  # type: ignore[assignment]

logger = logging.getLogger("omega.headroom")

@dataclass
class HeadroomResult:
    compressed_text: str
    original_ref: Optional[str] = None
    tokens_saved: int = 0

class HeadroomMiddleware:
    """
    Sovereign Semantic Compression Middleware.
    Integrates the headroom-ai library to reduce token usage in the context window.
    """
    def __init__(self, entity_registry: Optional[EntityRegistry] = None):
        self.registry = entity_registry

    async def compress_context(self, entity_name: str, messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[HeadroomResult]]:
        """
        Compresses a list of messages using semantic/structural compression.
        
        Args:
            entity_name: The target entity (used for cache isolation).
            messages: The list of messages to compress.
            
        Returns:
            A tuple of (compressed_messages, results_metadata).
        """
        if not HAS_HEADROOM:
            return messages, []
        try:
            # [M1 AnyIO Absolute] Wrap blocking CPU-bound compression in run_sync
            result = await anyio.to_thread.run_sync(headroom.compress, messages)
            compressed_messages = result.messages
            
            # In a full implementation, we would track the tokens saved and the 
            # reference IDs for the CCR (Compress-Cache-Retrieve) store.
            # For now, we return the compressed messages and a generic result.
            
            results = [HeadroomResult(compressed_text=m.get("content", ""), tokens_saved=0) for m in compressed_messages]
            
            return compressed_messages, results
            
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Headroom compression failed for {entity_name}: {e}")
            # Fallback: return original messages to ensure the system doesn't crash
            return messages, []

    async def retrieve_original(self, ref_id: str) -> str:
        """
        Retrieves the original, uncompressed content from the CCR cache.
        """
        if not HAS_HEADROOM:
            return f"[[ERROR: headroom-ai not available, cannot retrieve {ref_id}]]"
        try:
            # [M1 AnyIO Absolute] Wrap blocking I/O retrieval in run_sync
            return await anyio.to_thread.run_sync(headroom.retrieve, ref_id)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Headroom retrieval failed for {ref_id}: {e}")
            return f"[[ERROR: Original content for {ref_id} could not be retrieved]]"

_headroom_instance: Optional[HeadroomMiddleware] = None

def get_headroom_middleware() -> HeadroomMiddleware:
    """Singleton provider for HeadroomMiddleware."""
    global _headroom_instance
    if _headroom_instance is None:
        _headroom_instance = HeadroomMiddleware()
    return _headroom_instance


