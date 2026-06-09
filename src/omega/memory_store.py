"""Entity Memory Store — Hot/Warm/Cold persistent memory for entities.
AP: AP-MEMORY-STORE-v1.0.0
"""

import gzip
import json
import logging
import os
import re
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)

from .constants import DEFAULT_CONTEXT_LIMIT, MAX_HISTORY_EXCHANGES, ZONEID_MEMORY, validate_zoneid
from .errors import EntityTombstonedError
from .memory.providers import (
    StorageProvider,
    RedisStorageProvider,
    FileStorageProvider,
    InMemoryStorageProvider,
    DiskSpaceError,
)
from .memory.vector_adapters import IVectorStoreAdapter, QdrantAdapter, MemoryVectorAdapter
from .memory.fts_index import ConversationFTSIndex

logger = logging.getLogger(__name__)

def _get_data_dir() -> Path:
    """Get data directory, respecting OMEGA_DATA_DIR env var."""
    return Path(os.environ.get(
        "OMEGA_DATA_DIR",
        str(Path(__file__).resolve().parent.parent.parent / "data")
    ))

def _get_memory_dir() -> Path:
    return _get_data_dir() / "memory"

def _get_trace_dir() -> Path:
    return _get_memory_dir() / "trace"

def _get_entity_dir() -> Path:
    return _get_memory_dir() / "entities"

def _get_archive_dir() -> Path:
    return _get_memory_dir() / "archive"

MAX_HOT_SESSIONS = 50
MAX_HISTORY = MAX_HISTORY_EXCHANGES
MAX_CONTEXT_EXCHANGES = DEFAULT_CONTEXT_LIMIT
ARCHIVE_AFTER_DAYS = 7

# [id-soft: quake-1996] Grace Period — 0.5s delay before fully removing a
# tombstoned session from the hot cache. Prevents hot-slot reuse during
# in-flight add_exchange operations. Same value used by id Software's Quake
# server (15 packets at 30Hz ≈ 0.5s) to prevent client-side entity morphing.
TOMBSTONE_GRACE_SECONDS = 0.5


class MemoryStore:
    """Hot/Warm/Cold entity memory with LRU caching and 3-tier provider fallback.

    [id-soft: doom-1993] ZONEID Pattern — integrity marker embedded in every
    persisted exchange entry, verified on load to catch data corruption.
    [id-soft: doom-1993] Lazy Deletion — archive_session() tombstones a
    cache_key for TOMBSTONE_GRACE_SECONDS before fully removing the hot
    cache entry. In-flight add_exchange operations complete safely because
    they hold their own reference to the OrderedDict.
    [id-soft: quake-1996] Grace Period — 0.5s delay (TOMBSTONE_GRACE_SECONDS)
    before reap matches the original Quake server realloc grace.
    """

    ZONEID = ZONEID_MEMORY

    def __init__(self, providers: Optional[List[StorageProvider]] = None, vector_store: Optional[IVectorStoreAdapter] = None):
        self._hot: Dict[str, OrderedDict] = {}
        # [id-soft: doom-1993] Lazy Deletion — tombstone registry
        # Maps cache_key -> time.time() when tombstoned
        self._tombstoned: Dict[str, float] = {}
        # [id-soft: quake-1996] Temp Tier — transient scratchpad memory
        # Used for in-flight inference results that should not be persisted.
        self._temp: Dict[str, Any] = {}
        self._stats: Dict[str, int] = {"loads": 0, "saves": 0, "archives": 0, "fallbacks": 0}
        
        if providers is not None:
            self.providers = providers
        else:
            self.providers = []
            
            # Skip Redis in test environment to keep tests fast
            is_test = os.environ.get("OMEGA_ENV") == "test"
            
            if not is_test:
                # 1. Redis Provider (Hot)
                try:
                    redis_host = os.environ.get("OMEGA_REDIS_HOST", "localhost")
                    redis_port = int(os.environ.get("OMEGA_REDIS_PORT", "6379"))
                    redis_password = os.environ.get("OMEGA_REDIS_PASSWORD", "omega")
                    self.providers.append(RedisStorageProvider(host=redis_host, port=redis_port, password=redis_password))
                except OmegaError:
                    raise
                except Exception as e:
                    logger.error(f"Failed to initialize RedisStorageProvider: {e}", exc_info=True)
                    raise OmegaPersistenceError(f"Redis init failed: {e}", raw_error=e) from e
            
            # 2. File Provider (Warm)
            try:
                self.providers.append(FileStorageProvider(data_dir=_get_memory_dir()))
            except Exception as e:
                logger.warning(f"Failed to initialize FileStorageProvider: {e}")
                
            # 3. InMemory Provider (Cold/Volatile Fallback)
            self.providers.append(InMemoryStorageProvider())

        if vector_store is not None:
            self.vector_store = vector_store
        else:
            # Default to QdrantAdapter with sovereign fallback to MemoryVectorAdapter
            # Health check is performed lazily during first use
            self.vector_store = QdrantAdapter()

        # [Horizon 2: MiMo] FTS5 Search Index
        self.fts = ConversationFTSIndex(_get_memory_dir() / "fts_memory.db")
        self.fts.initialize()

    async def get_history(
        self,
        entity_name: str,
        session_id: str,
        limit: int = MAX_CONTEXT_EXCHANGES,
    ) -> List[Dict[str, str]]:
        """Get recent conversation history for context injection."""
        if not session_id:
            return []
        cache_key = f"{entity_name.lower()}:{session_id}"

        # [id-soft: doom-1993] Lazy Deletion — tombstoned sessions raise typed error
        # Mandate 9 enforcement: silent empty returns hide the fact that the
        # session was archived. Callers must catch EntityTombstonedError and
        # handle it explicitly (typically by loading from cold storage).
        if self._is_tombstoned(cache_key):
            raise EntityTombstonedError(
                cache_key=cache_key,
                message=f"Session '{session_id}' for entity '{entity_name}' is tombstoned (archived within grace period {TOMBSTONE_GRACE_SECONDS}s)",
                trace_id=None,
            )

        # 1. Check hot cache
        if cache_key in self._hot:
            self._stats["loads"] += 1
            history = list(self._hot[cache_key].values())
            return history[-limit:]

        # 2. Query providers in order
        for provider in self.providers:
            if hasattr(provider, "check_health"):
                if not await provider.check_health():
                    continue
                    
            try:
                exchanges = await provider.get_history(entity_name, session_id, limit=MAX_HISTORY)
                if exchanges:
                    # Validate first exchange has ZONEID marker
                    validated = []
                    for ex in exchanges:
                        if ex.get("_zoneid") != ZONEID_MEMORY:
                            logger.warning(
                                "Exchange missing/invalid zoneid in %s/%s (expected 0x%08x, got %s)",
                                entity_name, session_id, ZONEID_MEMORY, ex.get("_zoneid")
                            )
                            # Tag it with the marker so it passes next time
                            ex["_zoneid"] = ZONEID_MEMORY
                        validated.append(ex)
                    self._stats["loads"] += 1
                    self._cache_hot(cache_key, validated)
                    return validated[-limit:]
            except OmegaError:
                continue
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed to get_history: {e}", exc_info=True)
                self._stats["fallbacks"] += 1
                continue

        return []

    async def search_fts(
        self,
        query: str,
        entity_name: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search across conversation history using FTS5 (BM25 ranking).
        
        [C3: entity_name REQUIRED] for sovereign isolation.
        """
        if not query.strip():
            return []
        
        return await anyio.to_thread.run_sync(
            self.fts.search, query, entity_name, limit
        )

    async def search(
        self,
        query: str,
        entity_name: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Hybrid search: FTS5 + Vector, re-ranked via RRF.
        
        [C3: entity_name REQUIRED] for sovereign isolation.
        """
        if not query.strip():
            return []
            
        # 1. Fetch Keyword (FTS) and Vector results in parallel
        fts_results = []
        vec_results = []
        
        async with anyio.create_task_group() as tg:
            async def _fetch_fts():
                nonlocal fts_results
                fts_results = await self.search_fts(query, entity_name, limit * 2)
                
            async def _fetch_vec():
                nonlocal vec_results
                vector_adapter = await self._ensure_vector_store()
                if vector_adapter:
                    embedding = self._compute_simple_embedding(query)
                    vec_results = await vector_adapter.query(
                        entity_name=entity_name,
                        vector=embedding,
                        limit=limit * 2
                    )

            tg.start_soon(_fetch_fts)
            tg.start_soon(_fetch_vec)

        # 2. Apply Reciprocal Rank Fusion (RRF)
        # RRF formula: score = sum( 1 / (k + rank) )
        k = 60
        
        def get_doc_id(res):
            return f"{res.get('session_id')}:{res.get('timestamp')}"
            
        fts_ranks = {get_doc_id(r): i + 1 for i, r in enumerate(fts_results)}
        
        vec_ranks = {}
        for i, (score, payload) in enumerate(vec_results):
            doc_id = f"{payload.get('session_id')}:{payload.get('timestamp')}"
            vec_ranks[doc_id] = i + 1
            
        all_doc_ids = set(fts_ranks.keys()) | set(vec_ranks.keys())
        
        scored_docs = []
        for doc_id in all_doc_ids:
            score = 0.0
            if doc_id in fts_ranks:
                score += 1.0 / (k + fts_ranks[doc_id])
            if doc_id in vec_ranks:
                score += 1.0 / (k + vec_ranks[doc_id])
            scored_docs.append((doc_id, score))
            
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Final results construction
        final_results = []
        for doc_id, rrf_score in scored_docs[:limit]:
            # Prefer FTS metadata (it has content, role, etc.)
            doc = next((r for r in fts_results if get_doc_id(r) == doc_id), None)
            if not doc:
                # Fallback to vector payload
                _, payload = next(
                    ((s, p) for s, p in vec_results if f"{p.get('session_id')}:{p.get('timestamp')}" == doc_id), 
                    (None, None)
                )
                if payload:
                    doc = payload
            
            if doc:
                doc_copy = doc.copy()
                doc_copy["_rrf_score"] = round(rrf_score, 6)
                final_results.append(doc_copy)
                
        return final_results

    def _compute_simple_embedding(self, text: str) -> List[float]:
        """Lightweight bag-of-words embedding for sovereign fallback.
        
        Uses a stable MD5-based Feature Hashing (hashing trick) to map
        tokens deterministically to a fixed 256-dimensional space.
        """
        import hashlib
        import math
        
        vec = [0.0] * 256
        if not text:
            return vec
            
        tokens = re.findall(r"[a-zA-Z]\w+", text.lower())
        # Filter stopwords to keep the semantic signal clean
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "shall", "can", "need", "dare",
            "this", "that", "these", "those", "i", "me", "my", "we", "our", "you",
            "your", "he", "him", "his", "she", "her", "it", "its", "they", "them",
            "their", "what", "which", "who", "whom", "when", "where", "why", "how",
            "all", "each", "every", "both", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "because", "as", "until", "while", "about", "between",
            "through", "during", "before", "after", "above", "below", "up", "down",
        }
        tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
        if not tokens:
            return vec
            
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim = h % 256
            vec[dim] += 1.0
            
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
            
        return vec

    async def add_exchange(
        self,
        entity_name: str,
        session_id: str,
        user_message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a user-assistant exchange in entity memory."""
        if not session_id:
            logger.warning("add_exchange called with None/empty session_id for entity=%s, skipping", entity_name)
            return
        cache_key = f"{entity_name.lower()}:{session_id}"

        # [id-soft: doom-1993] Lazy Deletion — tombstoned sessions reject new exchanges
        # Mandate 9 enforcement: prevent data loss on archived sessions
        if self._is_tombstoned(cache_key):
            raise EntityTombstonedError(
                cache_key=cache_key,
                message=f"Cannot add exchange to tombstoned session '{session_id}' for entity '{entity_name}' — session was archived within grace period {TOMBSTONE_GRACE_SECONDS}s",
                trace_id=None,
            )
        exchange = {
            # [id-soft: doom-1993] ZONEID Pattern — integrity marker
            "_zoneid": ZONEID_MEMORY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user_message,
            "assistant": response,
            "metadata": metadata or {},
        }

        if cache_key not in self._hot:
            existing = await self.get_history(entity_name, session_id, limit=MAX_HISTORY)
            self._cache_hot(cache_key, existing)

        self._hot[cache_key][str(time.time())] = exchange
        exchanges = list(self._hot[cache_key].values())

        if len(exchanges) > MAX_HISTORY:
            exchanges = await self._compact(entity_name, session_id, exchanges)
            self._hot[cache_key] = OrderedDict()
            for i, ex in enumerate(exchanges):
                self._hot[cache_key][f"hist_{i}"] = ex

        # Save to providers
        saved_any = False
        for provider in self.providers:
            if hasattr(provider, "check_health"):
                if not await provider.check_health():
                    continue
                    
            try:
                await provider.save_history(entity_name, session_id, exchanges)
                saved_any = True
            except OmegaError:
                continue
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed to save_history: {e}", exc_info=True)
                self._stats["fallbacks"] += 1
                                
        if not saved_any:
            logger.error(f"All providers failed to save_history for {session_id}!")
        else:
            self._stats["saves"] += 1
        
        # [Horizon 2: MiMo] FTS5 Dual-Write
        try:
            self.fts.index_exchange(session_id, entity_name, "user", user_message)
            self.fts.index_exchange(session_id, entity_name, "assistant", response)
        except Exception as e:
            logger.warning("FTS dual-write failed for %s: %s", session_id, e)

        # Sovereign Vector Update
        vector_adapter = await self._ensure_vector_store()
        if vector_adapter:
            try:
                combined_text = f"{user_message} {response}"
                embedding = self._compute_simple_embedding(combined_text)
                await vector_adapter.upsert(
                    entity_name=entity_name,
                    vector=embedding,
                    metadata={"session_id": session_id, "timestamp": exchange["timestamp"]}
                )
            except Exception as e:
                logger.warning("Vector upsert failed for %s: %s", session_id, e)

    def _cache_hot(self, cache_key: str, exchanges: List[Dict]) -> None:
        # [id-soft: doom-1993] Lazy Deletion — reap tombstoned before slot reuse
        self._reap_tombstoned()
        if cache_key not in self._hot:
            self._hot[cache_key] = OrderedDict()
        for i, ex in enumerate(exchanges):
            self._hot[cache_key][f"hist_{i}"] = ex
        while len(self._hot) > MAX_HOT_SESSIONS:
            self._hot.popitem(last=False)

    def _reap_tombstoned(self) -> None:
        """Reap tombstoned hot cache entries past the grace period.

        [id-soft: doom-1993] Lazy Deletion — sweep tombstoned entries
        [id-soft: quake-1996] Grace Period — only reap after TOMBSTONE_GRACE_SECONDS
        In-flight add_exchange operations hold their own references to the
        OrderedDict, so they complete safely even after the slot is reaped
        from the registry. The actual data is in providers, so the reaped
        slot is recoverable on next get_history() call.
        """
        if not self._tombstoned:
            return
        now = time.time()
        expired = [k for k, ts in self._tombstoned.items() if now - ts >= TOMBSTONE_GRACE_SECONDS]
        for cache_key in expired:
            self._hot.pop(cache_key, None)
            del self._tombstoned[cache_key]

    def _is_tombstoned(self, cache_key: str) -> bool:
        """Check if a cache_key is currently tombstoned (within grace period)."""
        return cache_key in self._tombstoned

    async def _ensure_vector_store(self) -> IVectorStoreAdapter:
        """Ensure the vector store is healthy, falling back to MemoryVectorAdapter if not."""
        if not self.vector_store:
            self.vector_store = MemoryVectorAdapter()
            return self.vector_store
            
        if isinstance(self.vector_store, MemoryVectorAdapter):
            return self.vector_store
            
        try:
            status = await self.vector_store.get_status()
            if status.get("status") == "healthy":
                return self.vector_store
            logger.warning("Vector store unhealthy (%s), falling back to MemoryVectorAdapter", status.get("error"))
        except Exception as e:
            logger.error("Vector store health check failed: %s, falling back to MemoryVectorAdapter", e)
            
        self.vector_store = MemoryVectorAdapter()
        return self.vector_store

    def store_transient(self, key: str, value: Any) -> None:
        """Store data in the Temp tier (transient scratchpad).

        [id-soft: quake-1996] Temp Tier — transient memory that is not
        persisted to any provider. Used for intermediate inference steps.
        """
        self._temp[key] = value

    def get_transient(self, key: str) -> Optional[Any]:
        """Retrieve data from the Temp tier."""
        return self._temp.get(key)

    def clear_transient(self, key: Optional[str] = None) -> None:
        """Clear transient memory. If key is provided, clear only that key."""
        if key:
            self._temp.pop(key, None)
        else:
            self._temp.clear()

    async def _compact(
        self,
        entity_name: str,
        session_id: str,
        exchanges: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """Compact long conversation: keep first + last N exchanges, summarize middle."""
        logger.info(f"Compacting {entity_name}/{session_id}: {len(exchanges)} exchanges")
        self._stats["archives"] += 1

        if len(exchanges) <= MAX_HISTORY:
            return exchanges

        keep = MAX_HISTORY // 2
        kept = exchanges[:keep] + exchanges[-keep:]
        middle_count = len(exchanges) - (keep * 2)
        kept.insert(keep, {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": f"[{middle_count} exchanges compacted]",
            "user": "[summarized]",
            "assistant": f"[{middle_count} previous exchanges were compacted. Context preserved.]",
        })
        return kept

    async def get_summary(
        self,
        entity_name: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """Get a summary of the conversation for this entity/session."""
        exchanges = await self.get_history(entity_name, session_id, limit=MAX_HISTORY)
        return {
            "entity": entity_name,
            "session_id": session_id,
            "exchange_count": len(exchanges),
            "last_exchange": exchanges[-1] if exchanges else None,
            "first_exchange": exchanges[0] if exchanges else None,
        }

    async def archive_session(
        self,
        entity_name: str,
        session_id: str,
    ) -> bool:
        """Move a session to cold storage / archive across all providers.

        [id-soft: doom-1993] Lazy Deletion — instead of popping the hot cache
        entry immediately, tombstone it for TOMBSTONE_GRACE_SECONDS so any
        in-flight add_exchange operations complete safely. The slot is
        reaped by _reap_tombstoned() on the next access.
        """
        archived_any = False
        for provider in self.providers:
            try:
                if await provider.archive(entity_name, session_id):
                    archived_any = True
            except OmegaError:
                continue
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed to archive: {e}", exc_info=True)
                continue

        if archived_any:
            cache_key = f"{entity_name.lower()}:{session_id}"
            # [id-soft: doom-1993] Lazy Deletion — tombstone marker
            # [id-soft: quake-1996] Grace Period — wait TOMBSTONE_GRACE_SECONDS
            self._tombstoned[cache_key] = time.time()
            
            # Sovereign Vector Cleanup (C4 Fix)
            if self.vector_store:
                try:
                    await self.vector_store.delete_session(entity_name, session_id)
                    logger.info("Vector cleanup completed for session %s", session_id)
                except Exception as e:
                    logger.warning("Vector cleanup failed for %s: %s", session_id, e)
            
            self._stats["archives"] += 1
            
            # [Horizon 2: MiMo] FTS5 Cleanup (C1 fix)
            try:
                await anyio.to_thread.run_sync(self.fts.remove_session, session_id)
            except Exception as e:
                logger.warning("FTS cleanup failed for %s: %s", session_id, e)

            logger.info(f"Archived session {session_id} across providers (tombstoned, grace={TOMBSTONE_GRACE_SECONDS}s)")
            return True
        return False

    async def trace_exchange(
        self,
        trace_id: str,
        entity_name: str,
        session_id: str,
        user_message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a trace-oriented exchange (linked to observability trace)."""
        trace_data = {
            "trace_id": trace_id,
            "entity": entity_name,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": user_message,
            "response": response,
            "metadata": metadata or {},
        }
        trace_path = _get_trace_dir() / f"{trace_id}.json"
        await anyio.Path(trace_path.parent).mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(str(trace_path), "w") as f:
            await f.write(json.dumps(trace_data, indent=2, default=str))

    async def list_sessions(
        self,
        entity_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List recent sessions, optionally filtered by entity.

        [id-soft: doom-1993] Lazy Deletion — skips sessions whose hot-cache
        entry is tombstoned (within grace period). After grace expires, the
        tombstone is reaped and the file itself remains the source of truth.
        """
        sessions = []
        if entity_name:
            search_dir = _get_entity_dir() / entity_name.lower().replace(" ", "_")
            if await anyio.Path(search_dir).exists():
                async for path in anyio.Path(search_dir).glob("*.json"):
                    cache_key = f"{entity_name.lower()}:{path.stem}"
                    if self._is_tombstoned(cache_key):
                        continue
                    sessions.append({
                        "session_id": path.stem,
                        "entity": entity_name,
                        "path": str(path),
                    })
                sessions.sort(key=lambda s: s["session_id"], reverse=True)
                sessions = sessions[:limit]
        else:
            async for ent_dir in anyio.Path(_get_entity_dir()).iterdir():
                if await anyio.Path(ent_dir).is_dir():
                    async for path in anyio.Path(ent_dir).glob("*.json"):
                        cache_key = f"{ent_dir.name}:{path.stem}"
                        if self._is_tombstoned(cache_key):
                            continue
                        sessions.append({
                            "session_id": path.stem,
                            "entity": ent_dir.name,
                            "path": str(path),
                        })
            sessions.sort(key=lambda s: s["session_id"], reverse=True)
            sessions = sessions[:limit]
        return sessions

    def stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        return {
            "hot_sessions": sum(len(v) for v in self._hot.values()),
            "hot_cache_size": len(self._hot),
            "tombstoned": len(self._tombstoned),
            "loads": self._stats["loads"],
            "saves": self._stats["saves"],
            "archives": self._stats["archives"],
            "fallbacks": self._stats.get("fallbacks", 0),
        }

    async def close(self) -> None:
        """Flush hot cache to providers and close them.

        [id-soft: doom-1993] Lazy Deletion — skip tombstoned keys when flushing
        because their data has already been archived to providers.
        """
        for cache_key in list(self._hot.keys()):
            if self._is_tombstoned(cache_key):
                continue
            entity_name, session_id = cache_key.rsplit(":", 1)
            exchanges = list(self._hot[cache_key].values())
            if exchanges:
                for provider in self.providers:
                    try:
                        await provider.save_history(entity_name, session_id, exchanges)
                    except Exception as e:
                        logger.warning(f"Failed to flush to {provider.__class__.__name__} on close: {e}")

        for provider in self.providers:
            try:
                await provider.close()
            except OmegaError:
                pass
            except Exception as e:
                logger.error(f"Failed to close provider {provider.__class__.__name__}: {e}", exc_info=True)
                pass

        logger.info("Memory store flushed and closed")

    async def archive_old_sessions(self, older_than_days: int = ARCHIVE_AFTER_DAYS) -> int:
        """Auto-archive sessions older than N days."""
        count = 0
        now = time.time()
        async for ent_dir in anyio.Path(_get_entity_dir()).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue
            async for path in anyio.Path(ent_dir).glob("*.json"):
                stat = await anyio.Path(path).stat()
                age_days = (now - stat.st_mtime) / 86400
                if age_days > older_than_days:
                    entity_name = ent_dir.name
                    session_id = path.stem
                    if await self.archive_session(entity_name, session_id):
                        count += 1
        return count

_memory_store: Optional[MemoryStore] = None

def reset_memory_store() -> None:
    """Reset the singleton instance. Used for testing."""
    global _memory_store
    _memory_store = None

def get_memory_store() -> MemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
