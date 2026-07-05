# AP: AP-HEADROOM-PROTOCOL-v1.0.0
# 🔱 Headroom Protocol — Sovereign Prompt Compression
# ⚠️ DEPRECATED: This implementation uses binary zlib compression, which does NOT reduce LLM tokens.
# This file is kept for historical reference and rollback purposes.
#
# The Omega Engine has pivoted to the `headroom-ai` library for semantic/structural compression.
# See docs/research/R_HEADROOM_Sovereign_Analysis.md for the detailed audit.
#
# [id-soft: doom-1993] WAD System — Data-driven separation of engine and content
#   The Headroom store acts as a "prompt WAD", where compressed content is
#   stored externally and injected only when needed.
#
# Pattern: JSON Object -> json.dumps() -> zlib.compress() -> base64.b64encode()
# Envelope: [[zlib:base64_string]]

import zlib
import base64
import json
import logging
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("omega.headroom")

class HeadroomError(Exception):
    """Base exception for Headroom operations."""
    pass

class HeadroomStore:
    """Flat-file storage for compressed prompt blobs.
    
    Uses a 2-level directory structure (hash[:2]/hash.json) to avoid 
    directory overflow in large-scale deployments.
    """
    def __init__(self, base_dir: str = "data/headroom"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, content_hash: str) -> Path:
        return self.base_dir / content_hash[:2] / f"{content_hash}.json"

    async def store(self, content: str) -> str:
        """Compresses and stores content. Returns the content hash.
        
        Args:
            content: The raw text to compress.
        Returns:
            The SHA256 hash of the original content.
        """
        # 1. Generate hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        path = self._get_path(content_hash)
        
        if path.exists():
            return content_hash

        try:
            # 2. Compress: text -> zlib -> base64
            compressed = zlib.compress(content.encode())
            b64_encoded = base64.b64encode(compressed).decode('utf-8')
            
            # 3. Envelope as JSON
            envelope = {
                "hash": content_hash,
                "data": b64_encoded,
                "original_size": len(content),
                "compressed_size": len(b64_encoded)
            }
            
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(envelope))
            
            return content_hash
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to store headroom blob {content_hash}: {e}")
            raise HeadroomError(f"Compression failed: {e}")

    async def retrieve(self, content_hash: str) -> str:
        """Retrieves and decompresses content by hash."""
        path = self._get_path(content_hash)
        if not path.exists():
            raise HeadroomError(f"Blob {content_hash} not found in store")

        try:
            # 1. Load JSON
            envelope = json.loads(path.read_text())
            b64_data = envelope["data"]
            
            # 2. Decompress: base64 -> zlib -> text
            compressed = base64.b64decode(b64_data)
            raw_content = zlib.decompress(compressed).decode('utf-8')
            
            return raw_content
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to retrieve headroom blob {content_hash}: {e}")
            raise HeadroomError(f"Decompression failed: {e}")

class HeadroomMiddleware:
    """Sovereign Envelope middleware for prompt interception.
    
    Scans prompts for [[zlib:hash]] patterns and injects the raw content
    before the prompt reaches the provider.
    """
    def __init__(self, store: HeadroomStore):
        self.store = store

    async def compress_block(self, text: str) -> str:
        """Wraps text in a Sovereign Envelope.
        
        Returns: [[zlib:content_hash]]
        """
        content_hash = await self.store.store(text)
        return f"[[zlib:{content_hash}]]"

    async def expand_prompt(self, prompt: str) -> str:
        """Scans prompt for envelopes and expands them.
        
        Example: "Here is the context: [[zlib:a1b2c3]]" 
        -> "Here is the context: <raw content of a1b2c3>"
        """
        import re
        
        # Regex for [[zlib:hash]]
        pattern = r"\[\[zlib:([a-f0-9]{64})\]\]"
        
        async def replace_match(match):
            content_hash = match.group(1)
            try:
                return await self.store.retrieve(content_hash)
            except HeadroomError as e:
                logger.warning(f"Headroom expansion failed for {content_hash}: {e}")
                return f"[[ERROR: Blob {content_hash} missing]]"

        # Since re.sub doesn't support async, we find all matches and replace manually
        matches = list(re.finditer(pattern, prompt))
        if not matches:
            return prompt
            
        # Replace from back to front to maintain indices
        expanded_prompt = prompt
        for match in reversed(matches):
            replacement = await replace_match(match)
            expanded_prompt = (
                expanded_prompt[:match.start()] + 
                replacement + 
                expanded_prompt[match.end():]
            )
            
        return expanded_prompt

# ── Singleton Access ──────────────────────────────────────────────────────

_headroom_store: Optional[HeadroomStore] = None
_headroom_middleware: Optional[HeadroomMiddleware] = None

def get_headroom_store() -> HeadroomStore:
    global _headroom_store
    if _headroom_store is None:
        _headroom_store = HeadroomStore()
    return _headroom_store

def get_headroom_middleware() -> HeadroomMiddleware:
    global _headroom_middleware
    if _headroom_middleware is None:
        _headroom_middleware = HeadroomMiddleware(get_headroom_store())
    return _headroom_middleware
