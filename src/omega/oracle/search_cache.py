"""Sovereign Search Cache — Local filesystem persistence for deep search results.
AP: AP-SOVEREIGN-SEARCH-CACHE-v1.0.0
ICS: [NODE: PERSISTENCE | ARCHETYPE: MNEMOSYNE | CONTEXT: SEARCH-HARDENING]
"""
from __future__ import annotations

import logging
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """A single cached search result."""
    content: str
    timestamp: str
    query: str
    entity: str
    metadata: Dict[str, Any]

class SovereignCache:
    """
    Implements a local filesystem cache for SSP-V2 search results.
    
    Focuses on T3 (Firecrawl) results which are expensive to produce but
    highly valuable to persist.
    """
    def __init__(self, cache_dir: str = ".firecrawl", ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, query: str, entity: str) -> str:
        """Generate a deterministic filename based on query and entity."""
        raw_key = f"{entity}:{query}".lower().strip()
        hash_val = hashlib.sha256(raw_key.encode()).hexdigest()
        return f"cache_{hash_val}.json"

    def get(self, query: str, entity: str) -> Optional[str]:
        """Retrieve a cached result if it exists and is not expired."""
        key = self._generate_key(query, entity)
        cache_file = self.cache_dir / key

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                entry = CacheEntry(**data)

            # Check TTL
            created_at = datetime.fromisoformat(entry.timestamp)
            delta = (datetime.now(timezone.utc) - created_at).total_seconds()
            
            if delta > self.ttl_seconds:
                logger.info(f"Cache expired for {query} (delta={delta:.0f}s > TTL={self.ttl_seconds}s)")
                cache_file.unlink()
                return None

            logger.info(f"SovereignCache HIT for {query} (entity={entity})")
            return entry.content

        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None

    def set(self, query: str, entity: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Persist a search result to the local cache."""
        key = self._generate_key(query, entity)
        cache_file = self.cache_dir / key

        try:
            entry = CacheEntry(
                content=content,
                timestamp=datetime.now(timezone.utc).isoformat(),
                query=query,
                entity=entity,
                metadata=metadata or {}
            )
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(asdict(entry), f, indent=2)
            return True
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Cache write error for {key}: {e}")
            return False

    def clear(self) -> int:
        """Clear all cached entries. Returns number of files deleted."""
        count = 0
        for f in self.cache_dir.glob("cache_*.json"):
            f.unlink()
            count += 1
        return count
