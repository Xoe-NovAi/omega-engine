# AP: AP-CAS-BLOB-STORE-v1.0.0

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import hashlib
import anyio
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger("omega.archive.cas")

class CASArchiver:
    """
    Content-Addressable Storage (CAS) for the Omega Engine.
    Implements the 'Golden Copy' pattern: store once, reference many.
    
    Sovereignty: 100% local, zero telemetry, immutable provenance.
    """
    def __init__(self, base_dir: str = "data/archive/cas"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def store(self, content: bytes) -> str:
        """
        Stores content by its SHA-256 hash.
        Returns the content hash (CID).
        """
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Use a 2-level directory structure to prevent filesystem slowdowns
        # e.g., data/archive/cas/ab/cdef...
        prefix = content_hash[:2]
        folder = self.base_dir / prefix
        
        # Fix: anyio.to_thread.run_sync doesn't accept keyword args
        def mkdir_safe():
            folder.mkdir(parents=True, exist_ok=True)
        
        await anyio.to_thread.run_sync(mkdir_safe)
        
        file_path = folder / content_hash
        
        if not await anyio.Path(file_path).exists():
            async with await anyio.open_file(file_path, "wb") as f:
                await f.write(content)
            logger.debug(f"Stored new CAS blob: {content_hash}")
        
        return content_hash

    async def retrieve(self, content_hash: str) -> Optional[bytes]:
        """
        Retrieves content by its SHA-256 hash.
        """
        prefix = content_hash[:2]
        file_path = self.base_dir / prefix / content_hash
        
        if not await anyio.Path(file_path).exists():
            logger.warning(f"CAS blob not found: {content_hash}")
            return None
            
        async with await anyio.open_file(file_path, "rb") as f:
            return await f.read()

    async def exists(self, content_hash: str) -> bool:
        """Checks if a blob exists in the archive."""
        prefix = content_hash[:2]
        return await anyio.Path(self.base_dir / prefix / content_hash).exists()

    async def delete(self, content_hash: str) -> bool:
        """Deletes a blob from the archive."""
        prefix = content_hash[:2]
        file_path = self.base_dir / prefix / content_hash
        try:
            await anyio.Path(file_path).unlink()
            return True
        except FileNotFoundError:
            return False
