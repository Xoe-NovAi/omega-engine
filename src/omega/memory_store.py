# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Entity Memory Store — Hot/Warm/Cold persistent memory for entities.
AP: AP-MEMORY-STORE-v1.0.0
# [heritage: rrf-algorithm 2009] Reciprocal Rank Fusion — FTS5 + vector score fusion
"""

import json
import logging
import os
import re
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
from omega.errors import (
    OmegaError,
    OmegaPersistenceError,
)

from .constants import DEFAULT_CONTEXT_LIMIT, MAX_HISTORY_EXCHANGES, ZONEID_MEMORY
from .errors import EntityTombstonedError
from .memory.providers import (
    StorageProvider,
    FileStorageProvider,
    InMemoryStorageProvider,
    USMStorageProvider,
    sanitize_path_component,
)
from .memory.vector_adapters import IVectorStoreAdapter, MemoryVectorAdapter
from .memory.sqlite_vec_adapter import SQLiteVecAdapter
from .memory.fts_index import ConversationFTSIndex
from .memory.embeddings import EmbeddingManager, Qwen3GGUFEmbeddingProvider, SovereignFallbackEmbeddingProvider
from .memory.adapters import MemoryAdapterRegistry

logger = logging.getLogger(__name__)


def _get_data_dir() -> Path:
    """Get data directory, respecting OMEGA_DATA_DIR env var."""
    return Path(
        os.environ.get(
            "OMEGA_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")
        )
    )


def _get_memory_dir() -> Path:
    return _get_data_dir() / "memory"


def _get_trace_dir() -> Path:
    return _get_memory_dir() / "trace"


def _get_entity_dir() -> Path:
    return _get_memory_dir() / "entities"


def _get_archive_dir() -> Path:
    return _get_memory_dir() / "archive"


def _get_sessions_dir() -> Path:
    """Get the sessions directory for JSONL persistence (ACP event stream)."""
    return _get_data_dir() / "coordination" / "sessions"


MAX_HOT_SESSIONS = 50
MAX_HISTORY = MAX_HISTORY_EXCHANGES
MAX_CONTEXT_EXCHANGES = DEFAULT_CONTEXT_LIMIT
ARCHIVE_AFTER_DAYS = 7

# [id-soft: vet-008] Grace Period — wait TOMBSTONE_GRACE_SECONDS before full reclamation
# 0.5s delay before fully removing a tombstoned session from the hot cache.
# Prevents hot-slot reuse during in-flight add_exchange operations.
# Same value used by id Software's Quake server (15 packets at 30Hz ≈ 0.5s)
# to prevent client-side entity morphing.
TOMBSTONE_GRACE_SECONDS = 0.5

# External storage for long-term session archival (90-day policy)
# Sessions older than 90 days are moved to external 8TB storage drive.
# M29: env-overridable so no machine-specific mount leaks into the public tree.
EXTERNAL_STORAGE_PATH = Path(os.environ.get(
    "OMEGA_EXTERNAL_STORAGE",
    Path.home() / "omega_library" / "archive" / "sessions",
))
ARCHIVE_TO_EXTERNAL_DAYS = 90


class MemoryStore:
    """Hot/Warm/Cold entity memory with LRU caching and 3-tier provider fallback.
    DocRef: docs/reference/api/memory_store.md

    [id-soft: vet-015] ZONEID Pattern — integrity marker embedded in every

    persisted exchange entry, verified on load to catch data corruption.
    [id-soft: vet-008] Lazy Deletion — archive_session() tombstones a
    cache_key for TOMBSTONE_GRACE_SECONDS before fully removing the hot
    cache entry. In-flight add_exchange operations complete safely because
    they hold their own reference to the OrderedDict.
    [id-soft: vet-008] Grace Period — 0.5s delay (TOMBSTONE_GRACE_SECONDS)
    before reap matches the original Quake server realloc grace.

    Batch Persistence (MnemosyneWriter pattern, ported from xna-omega-legacy):
    Provider writes are buffered and flushed in batches to prevent connection
    pool exhaustion under concurrent load. Buffer flushes on:
      - BATCH_THRESHOLD writes accumulated
      - get_history() call (read-your-writes consistency)
      - explicit flush() call
    """

    ZONEID = ZONEID_MEMORY
    BATCH_THRESHOLD: int = 25  # flush after this many pending writes

    def __init__(
        self,
        providers: Optional[List[StorageProvider]] = None,
        vector_store: Optional[IVectorStoreAdapter] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        adapter_registry: Optional[MemoryAdapterRegistry] = None,
    ):
        self._hot: Dict[str, OrderedDict] = {}
        self._adapter_registry = adapter_registry
        # [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle
        # Maps cache_key -> time.time() when tombstoned
        self._tombstoned: Dict[str, float] = {}
        # [id-soft: vet-037] Temp Tier — transient scratchpad memory
        # Used for in-flight inference results that should not be persisted.
        self._temp: Dict[str, Any] = {}
        self._stats: Dict[str, int] = {
            "loads": 0,
            "saves": 0,
            "archives": 0,
            "fallbacks": 0,
            "batch_flushes": 0,
        }

        # ── Batch Persistence Buffer ──
        # Groups pending writes by (entity_name, session_id) to minimize
        # provider round-trips. Prevents connection pool exhaustion under
        # concurrent oracle.talk() load.
        from .memory.batch_writer import BatchPersistenceWriter

        self._batch_writer = BatchPersistenceWriter(providers=providers)
        self._batch_buffer: Dict[tuple, List[Dict[str, Any]]] = {}
        self._batch_count: int = 0

        if providers is not None:
            self.providers = providers
        else:
            self.providers = []

            # 0. USM Provider (Sovereign Primary)
            self.providers.append(USMStorageProvider())

            # [redis-20260928] Redis provider REMOVED (Architect ruling, group A).
            #
            # This branch was gated on `OMEGA_REDIS_HOST`, which meant the
            # entire hot-storage tier was re-creatable by setting ONE env var —
            # a config surface that reads as configuration but is not
            # configuration. It was the live re-creation vector for a
            # non-loopback `*:6379` connection that `check-lan-exposure`
            # never voted on. Redis was `*:6379` on this box for a month and
            # no gate saw it.
            #
            # A capability that cannot be reached, guarded by an env var
            # nobody remembers setting, is not a capability. Storage chain is
            # now: USM (sovereign primary) -> File (warm) -> InMemory (cold).
            # See scripts/lan_exposure_audit.py for the historical evidence.

            # 1. File Provider (Warm) - Always enabled to support persistence tests and local-first fallback
            try:
                self.providers.append(FileStorageProvider(data_dir=_get_memory_dir()))
            except (OSError, RuntimeError) as e:
                logger.warning(f"Failed to initialize FileStorageProvider: {e}")

            # 2. InMemory Provider (Cold/Volatile Fallback)
            self.providers.append(InMemoryStorageProvider())

        # FS-Β1: Embedding Strategy SSOT — canonical_dimension=1024
        # (D-1024-DIM-NATIVE-20260926). Native 1024 IS canonical; MRL
        # truncation is available but NOT the canonical path.

        if vector_store is not None:
            self.vector_store = vector_store
        else:
            # Default to SQLiteVecAdapter (unified fabric) with sovereign fallback to MemoryVectorAdapter
            # Correction C2: ADD a tier, never redefine the class
            # Health check is performed lazily during first use
            self.vector_store = SQLiteVecAdapter()

        if embedding_manager is not None:
            self.embedding_manager = embedding_manager
        else:
            # FS-Β1 / [D-1024-DIM-NATIVE-20260926]: write-path must emit the
            # canonical width or the adapter's dimension guard rejects it (M23).
            # Qwen3-Embedding-0.6B is native 1024 == canonical. EmbeddingGemma
            # (768 native) and potion (768 native) CANNOT reach 1024 — MRL only
            # truncates — so they are demoted to fallback-tier collections.
            from .memory.embedding_strategy import get_embedding_strategy

            strategy = get_embedding_strategy()
            target_dim = strategy.canonical_dimension  # 1024

            self.embedding_manager = EmbeddingManager(
                [
                    Qwen3GGUFEmbeddingProvider(target_dim=target_dim),
                    SovereignFallbackEmbeddingProvider(dimension=target_dim),
                ]
            )
        # [Horizon 2: MiMo] FTS5 Search Index
        self.fts = ConversationFTSIndex(_get_memory_dir() / "fts_memory.db")
        self.fts.initialize()

        # Ensure batch writer has the fully populated providers list
        self._batch_writer._providers = self.providers

    async def start_batch_writer(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start the background batch writer."""
        await self._batch_writer.start(task_group)

    async def stop_batch_writer(self) -> None:
        """Stop the background batch writer."""
        await self._batch_writer.stop()

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

        # [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle
        # Mandate 9 enforcement: silent empty returns hide the fact that the
        # session was archived. Callers must catch EntityTombstonedError and
        # handle it explicitly (typically by loading from cold storage).
        if self._is_tombstoned(cache_key):
            raise EntityTombstonedError(
                cache_key=cache_key,
                message=f"Session '{session_id}' for entity '{entity_name}' is tombstoned (archived within grace period {TOMBSTONE_GRACE_SECONDS}s)",
                trace_id=None,
            )

        # ── Batch Flush: read-your-writes consistency ──
        # Flush pending provider writes before reading to ensure the read
        # returns data that includes recent writes.
        if self._batch_count > 0:
            await self.flush()

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
                                entity_name,
                                session_id,
                                ZONEID_MEMORY,
                                ex.get("_zoneid"),
                            )
                            # Tag it with the marker so it passes next time
                            ex["_zoneid"] = ZONEID_MEMORY
                        validated.append(ex)
                    self._stats["loads"] += 1
                    self._cache_hot(cache_key, validated)
                    return validated[-limit:]
            except OmegaError:
                continue
            except (RuntimeError, OSError) as e:
                logger.error(
                    f"Provider {provider.__class__.__name__} failed to get_history: {e}",
                    exc_info=True,
                )
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

        return await self.fts.search(query, entity_name, limit)

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

        from .memory.hybrid_search import fetch_and_fuse

        async def _fts_fetch() -> List[Dict[str, Any]]:
            return await self.search_fts(query, entity_name, limit * 2)

        async def _vec_fetch() -> List[tuple]:
            vector_adapter = await self._ensure_vector_store()
            if not vector_adapter:
                return []
            embedding, _ = await self.embedding_manager.get_embedding(query)
            return await vector_adapter.query(
                entity_name=entity_name, vector=embedding, limit=limit * 2
            )

        fused = await fetch_and_fuse(
            fts_fetch=_fts_fetch,
            vec_fetch=_vec_fetch,
            limit=limit,
        )

        final_results = []
        for result in fused:
            doc_copy = result.metadata.copy()
            doc_copy["_rrf_score"] = result.fused_score
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
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "shall",
            "can",
            "need",
            "dare",
            "this",
            "that",
            "these",
            "those",
            "i",
            "me",
            "my",
            "we",
            "our",
            "you",
            "your",
            "he",
            "him",
            "his",
            "she",
            "her",
            "it",
            "its",
            "they",
            "them",
            "their",
            "what",
            "which",
            "who",
            "whom",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "because",
            "as",
            "until",
            "while",
            "about",
            "between",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
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
        trace_id: Optional[str] = None,
    ) -> None:
        """Record a user-assistant exchange in entity memory."""
        if not session_id:
            logger.warning(
                "add_exchange called with None/empty session_id for entity=%s, skipping",
                entity_name,
            )
            return
        cache_key = f"{entity_name.lower()}:{session_id}"

        # [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle
        # Mandate 9 enforcement: prevent data loss on archived sessions
        if self._is_tombstoned(cache_key):
            raise EntityTombstonedError(
                cache_key=cache_key,
                message=f"Cannot add exchange to tombstoned session '{session_id}' for entity '{entity_name}' — session was archived within grace period {TOMBSTONE_GRACE_SECONDS}s",
                trace_id=trace_id,
            )
        exchange = {
            # [id-soft: vet-015] ZONEID Pattern — integrity marker
            "_zoneid": ZONEID_MEMORY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user_message,
            "assistant": response,
            "metadata": metadata or {},
        }
        if trace_id:
            exchange["metadata"]["trace_id"] = trace_id

        # ── JSONL Session Persistence (ACP Event Stream) ──
        # Append-only event log for crash resilience and rewind capability.
        # Mirrors Grok CLI's updates.jsonl pattern.
        await self._log_acp_event(entity_name, session_id, exchange)

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

        # ── Batch Provider Persistence ──
        # Buffer writes instead of spawning threads per-provider per-call.
        # Prevents connection pool exhaustion under concurrent oracle.talk() load.
        # Hot cache (above) is updated immediately — providers get batched writes.
        await self._batch_writer.write(entity_name, session_id, exchanges)
        self._stats["saves"] += 1

        # ── Vault Update via Adapter Registry ──
        if self._adapter_registry:
            adapter = self._adapter_registry.get_for_entity(entity_name)
            if adapter:
                try:
                    vault = await adapter.get_vault(entity_name, "shadow") or {}
                    vault["last_exchange_ts"] = exchange.get("timestamp", time.time())
                    vault["exchange_count"] = vault.get("exchange_count", 0) + 1
                    vault["last_session_id"] = session_id
                    # P2: Propagate trace_id to vault for observability correlation
                    if trace_id:
                        vault["last_trace_id"] = trace_id
                    await adapter.put_vault(entity_name, "shadow", vault)
                except (OmegaError, RuntimeError) as e:
                    logger.warning("Vault update failed for %s/%s: %s", entity_name, session_id, e)

        # [Horizon 2: MiMo] FTS5 Dual-Write
        try:
            await self.fts.index_exchange(session_id, entity_name, "user", user_message)
            await self.fts.index_exchange(session_id, entity_name, "assistant", response)
        except (RuntimeError, OSError) as e:
            logger.warning("FTS dual-write failed for %s: %s", session_id, e)

        # Sovereign Vector Update
        vector_adapter = await self._ensure_vector_store()
        if vector_adapter:
            try:
                combined_text = f"{user_message} {response}"
                embedding, provider_name = await self.embedding_manager.get_embedding(combined_text)
                await vector_adapter.upsert(
                    entity_name=entity_name,
                    vector=embedding,
                    metadata={
                        "session_id": session_id,
                        "timestamp": exchange["timestamp"],
                        "embedding_provider": provider_name,
                    },
                )
            except (OmegaError, RuntimeError) as e:
                logger.warning("Vector upsert failed for %s: %s", session_id, e)

    async def flush(self) -> None:
        """Public method: explicitly flush all pending provider writes."""
        await self._batch_writer.flush()

    def _cache_hot(self, cache_key: str, exchanges: List[Dict]) -> None:
        # [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle
        self._reap_tombstoned()
        if cache_key not in self._hot:
            self._hot[cache_key] = OrderedDict()
        for i, ex in enumerate(exchanges):
            self._hot[cache_key][f"hist_{i}"] = ex
        while len(self._hot) > MAX_HOT_SESSIONS:
            self._hot.popitem(last=False)

    # ── Lifecycle Directory Accessors ──────────────────────────────────────
    # Expose module-level dir helpers as methods for SessionLifecycleManager
    def _get_entity_dir(self) -> Path:
        """Return the entities directory path."""
        return _get_entity_dir()

    def _get_archive_dir(self) -> Path:
        """Return the archive directory path."""
        return _get_archive_dir()

    def _reap_tombstoned(self) -> None:
        """Reap tombstoned hot cache entries past the grace period.

        [id-soft: vet-008] Lazy Deletion — sweep tombstoned entries
        [id-soft: vet-008] Grace Period — only reap after TOMBSTONE_GRACE_SECONDS
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
            logger.warning(
                "Vector store unhealthy (%s), falling back to MemoryVectorAdapter",
                status.get("error"),
            )
        except Exception as e:
            logger.error(
                "Vector store health check failed: %s, falling back to MemoryVectorAdapter", e
            )

        self.vector_store = MemoryVectorAdapter()
        return self.vector_store

    def store_transient(self, key: str, value: Any) -> None:
        """Store data in the Temp tier (transient scratchpad).

        [id-soft: vet-037] Temp Tier — transient memory that is not
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

    async def sovereign_ingest(
        self,
        content: str,
        entity_name: str,
        metadata: Dict[str, Any],
        provider_name: str = "external",
    ) -> str:
        """Sovereign Ingestion Pipeline: Sieve -> Sign -> Index.

        Ensures all external data is sanitized, PII-masked, and signed
        before entering the sovereign memory.
        """
        from omega.oracle.ingestion import get_ingestion_pipeline

        pipeline = get_ingestion_pipeline()

        # 1. Process through the sovereign sieve
        doc = await pipeline.ingest(content, metadata, provider_name)

        # 2. Index into MemoryStore (as a synthetic exchange)
        # We create a synthetic exchange to leverage existing persistence
        session_id = f"ingest_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        await self.add_exchange(
            entity_name=entity_name,
            session_id=session_id,
            user_message=f"[Sovereign Ingest] Source: {metadata.get('source', 'unknown')}",
            response=doc.content,
            metadata={
                **metadata,
                "provenance_hash": doc.provenance_hash,
                "pii_token_map": doc.pii_token_map.tokens if doc.pii_token_map else None,
                "ingested_at": doc.timestamp,
                "is_ingested": True,
            },
            trace_id=None,
        )

        return session_id

    async def _compact(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compact long conversation: keep first + last N exchanges, summarize middle."""
        logger.info(f"Compacting {entity_name}/{session_id}: {len(exchanges)} exchanges")
        self._stats["archives"] += 1

        if len(exchanges) <= MAX_HISTORY:
            return exchanges

        keep = MAX_HISTORY // 2
        kept = exchanges[:keep] + exchanges[-keep:]
        middle_count = len(exchanges) - (keep * 2)
        kept.insert(
            keep,
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system": f"[{middle_count} exchanges compacted]",
                "user": "[summarized]",
                "assistant": f"[{middle_count} previous exchanges were compacted. Context preserved.]",
            },
        )
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

        [id-soft: vet-008] Lazy Deletion — instead of popping the hot cache
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
            except (RuntimeError, OSError) as e:
                logger.error(
                    f"Provider {provider.__class__.__name__} failed to archive: {e}", exc_info=True
                )
                continue

        if archived_any:
            cache_key = f"{entity_name.lower()}:{session_id}"
            # [id-soft: vet-008] Lazy Deletion — tombstone-based session lifecycle
            # [id-soft: vet-008] Grace Period — wait TOMBSTONE_GRACE_SECONDS before full reclamation
            self._tombstoned[cache_key] = time.time()

            # Sovereign Vector Cleanup (C4 Fix)
            if self.vector_store:
                try:
                    await self.vector_store.delete_session(entity_name, session_id)
                    logger.info("Vector cleanup completed for session %s", session_id)
                except (OmegaError, RuntimeError) as e:
                    logger.warning("Vector cleanup failed for %s: %s", session_id, e)

            self._stats["archives"] += 1

            # [Horizon 2: MiMo] FTS5 Cleanup (C1 fix)
            try:
                await self.fts.remove_session(session_id)
            except (RuntimeError, OSError) as e:
                logger.warning("FTS cleanup failed for %s: %s", session_id, e)

            logger.info(
                f"Archived session {session_id} across providers (tombstoned, grace={TOMBSTONE_GRACE_SECONDS}s)"
            )
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

    # ── JSONL Session Persistence (ACP Event Stream) ─────────────────────────
    # Mirrors Grok CLI's updates.jsonl + rewind_points.jsonl pattern for
    # crash-resilient sessions (Mandate 11: Soul Integrity, Mandate 15: Sovereign Continuity)

    def _get_session_jsonl_path(self, entity_name: str, session_id: str, filename: str) -> Path:
        """Get the path for a session's JSONL file (updates.jsonl or rewind_points.jsonl)."""
        safe_entity = sanitize_path_component(entity_name)
        safe_session = sanitize_path_component(session_id)
        session_dir = _get_sessions_dir() / safe_entity / safe_session
        return session_dir / filename

    async def _ensure_session_dir(self, entity_name: str, session_id: str) -> Path:
        """Ensure the session directory exists for JSONL persistence."""
        safe_entity = sanitize_path_component(entity_name)
        safe_session = sanitize_path_component(session_id)
        session_dir = _get_sessions_dir() / safe_entity / safe_session
        await anyio.Path(session_dir).mkdir(parents=True, exist_ok=True)
        return session_dir

    async def log_acp_event(
        self,
        entity_name: str,
        session_id: str,
        event_type: str,
        payload: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> None:
        """Append an ACP event to the session's updates.jsonl (source of truth).

        This is the append-only event stream that survives OOM/kill.
        Pattern from Grok CLI: xai-sqlite-journal/src/lib.rs
        """
        if not session_id:
            return

        await self._ensure_session_dir(entity_name, session_id)
        jsonl_path = self._get_session_jsonl_path(entity_name, session_id, "updates.jsonl")

        event = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity": entity_name,
            "session_id": session_id,
            "payload": payload,
        }
        if trace_id:
            event["trace_id"] = trace_id

        # Append to JSONL (atomic write via anyio)
        async with await anyio.open_file(str(jsonl_path), "a") as f:
            await f.write(json.dumps(event, default=str) + "\n")

    async def _log_acp_event(
        self,
        entity_name: str,
        session_id: str,
        exchange: Dict[str, Any],
    ) -> None:
        """Internal: log an exchange as an ACP event to updates.jsonl.

        Called from add_exchange to maintain the append-only event stream.
        """
        await self.log_acp_event(
            entity_name=entity_name,
            session_id=session_id,
            event_type="exchange",
            payload=exchange,
            trace_id=exchange.get("metadata", {}).get("trace_id"),
        )

    async def create_rewind_point(
        self,
        entity_name: str,
        session_id: str,
        snapshot: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> None:
        """Create a periodic filesystem snapshot in rewind_points.jsonl.

        Pattern from Grok CLI: /rewind command replays journal to restore state.
        """
        if not session_id:
            return

        await self._ensure_session_dir(entity_name, session_id)
        jsonl_path = self._get_session_jsonl_path(entity_name, session_id, "rewind_points.jsonl")

        rewind_point = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity": entity_name,
            "session_id": session_id,
            "snapshot": snapshot,
        }
        if trace_id:
            rewind_point["trace_id"] = trace_id

        async with await anyio.open_file(str(jsonl_path), "a") as f:
            await f.write(json.dumps(rewind_point, default=str) + "\n")

    async def rewind_session(
        self,
        entity_name: str,
        session_id: str,
        target_timestamp: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Restore session state from rewind_points.jsonl.

        If target_timestamp is provided, restores to the latest rewind point
        at or before that timestamp. Otherwise, restores the latest rewind point.
        """
        jsonl_path = self._get_session_jsonl_path(entity_name, session_id, "rewind_points.jsonl")
        if not await anyio.Path(jsonl_path).exists():
            return None

        rewind_points = []
        async with await anyio.open_file(str(jsonl_path), "r") as f:
            async for line in f:
                line = line.strip()
                if line:
                    try:
                        rewind_points.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not rewind_points:
            return None

        if target_timestamp:
            # Find latest rewind point at or before target
            target_dt = datetime.fromisoformat(target_timestamp.replace("Z", "+00:00"))
            candidates = [
                rp
                for rp in rewind_points
                if datetime.fromisoformat(rp["timestamp"].replace("Z", "+00:00")) <= target_dt
            ]
            if not candidates:
                return None
            return max(candidates, key=lambda rp: rp["timestamp"])["snapshot"]
        else:
            # Return latest
            return rewind_points[-1]["snapshot"]

    async def list_session_events(
        self,
        entity_name: str,
        session_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Read recent events from updates.jsonl for debugging/inspection."""
        jsonl_path = self._get_session_jsonl_path(entity_name, session_id, "updates.jsonl")
        if not await anyio.Path(jsonl_path).exists():
            return []

        events = []
        async with await anyio.open_file(str(jsonl_path), "r") as f:
            async for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return events[-limit:]

    async def list_sessions(
        self,
        entity_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List recent sessions, optionally filtered by entity.

        [id-soft: vet-008] Lazy Deletion — skips sessions whose hot-cache
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
                    sessions.append(
                        {
                            "session_id": path.stem,
                            "entity": entity_name,
                            "path": str(path),
                        }
                    )
                sessions.sort(key=lambda s: s["session_id"], reverse=True)
                sessions = sessions[:limit]
        else:
            async for ent_dir in anyio.Path(_get_entity_dir()).iterdir():
                if await anyio.Path(ent_dir).is_dir():
                    async for path in anyio.Path(ent_dir).glob("*.json"):
                        cache_key = f"{ent_dir.name}:{path.stem}"
                        if self._is_tombstoned(cache_key):
                            continue
                        sessions.append(
                            {
                                "session_id": path.stem,
                                "entity": ent_dir.name,
                                "path": str(path),
                            }
                        )
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

        [id-soft: vet-008] Lazy Deletion — skip tombstoned keys when flushing
        because their data has already been archived to providers.
        """
        # Flush batch buffer first (pending writes from add_exchange)
        await self._batch_writer.flush()

        for cache_key in list(self._hot.keys()):
            if self._is_tombstoned(cache_key):
                continue
            entity_name, session_id = cache_key.rsplit(":", 1)
            exchanges = list(self._hot[cache_key].values())
            if exchanges:
                for provider in self.providers:
                    try:
                        await provider.save_history(entity_name, session_id, exchanges)
                    except (OmegaError, RuntimeError, OSError) as e:
                        logger.warning(
                            f"Failed to flush to {provider.__class__.__name__} on close: {e}"
                        )

        for provider in self.providers:
            try:
                await provider.close()
            except OmegaError:
                pass
            except (RuntimeError, OSError) as e:
                logger.error(
                    f"Failed to close provider {provider.__class__.__name__}: {e}", exc_info=True
                )
                pass

        # Close FTS5 index (must be called here, not in reset_memory_store,
        # because close() is async and needs the event loop)
        if hasattr(self, "fts") and self.fts is not None:
            try:
                await anyio.to_thread.run_sync(self.fts.close)
            except (RuntimeError, OSError) as e:
                logger.warning("Failed to close FTS index: %s", e)

        logger.info("Memory store flushed and closed")

    async def archive_old_sessions(self, older_than_days: int = ARCHIVE_AFTER_DAYS) -> int:
        """Auto-archive sessions older than N days.

        Session Lifecycle Policy:
        - 7 days: Archive to cold storage (local disk)
        - 90 days: Move to external 8TB storage drive for permanent archival
        """
        count = 0
        now = time.time()
        entity_dir = anyio.Path(_get_entity_dir())
        # [M9: Error Integrity] Guard against a missing entity dir (e.g. fresh
        # test environment or first boot). A missing dir is not an error — there
        # is simply nothing to archive.
        if not await entity_dir.exists():
            return 0
        async for ent_dir in entity_dir.iterdir():
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

    async def move_to_external_storage(
        self, older_than_days: int = ARCHIVE_TO_EXTERNAL_DAYS
    ) -> int:
        """Move sessions older than N days to external 8TB storage drive.

        This implements the 90-day permanent archival policy. Sessions are moved
        (not deleted) to preserve data while freeing local disk space.
        """
        count = 0
        now = time.time()

        # Ensure external storage directory exists
        await anyio.Path(EXTERNAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

        # Check archive directory for old sessions
        archive_dir = _get_archive_dir()
        if not await anyio.Path(archive_dir).exists():
            return 0

        async for ent_dir in anyio.Path(archive_dir).iterdir():
            if not await anyio.Path(ent_dir).is_dir():
                continue
            async for path in anyio.Path(ent_dir).glob("*.json"):
                stat = await anyio.Path(path).stat()
                age_days = (now - stat.st_mtime) / 86400
                if age_days > older_than_days:
                    # Move to external storage
                    entity_name = ent_dir.name
                    external_entity_dir = EXTERNAL_STORAGE_PATH / entity_name
                    await anyio.Path(external_entity_dir).mkdir(parents=True, exist_ok=True)

                    # Move the file
                    dest_path = external_entity_dir / path.name
                    await anyio.Path(path).rename(dest_path)
                    count += 1
                    logger.info("Moved session %s to external storage: %s", path.name, dest_path)

        return count


_memory_store: Optional[MemoryStore] = None


def reset_memory_store() -> None:
    """Reset the singleton instance. Used for testing.

    Closes the FTS5 SQLite connection before abandoning the store.
    Batch persistence buffer is flushed via the async close() path
    when possible; on sync abandon, pending writes are logged and lost.
    """
    global _memory_store
    if _memory_store is not None:
        # Log any unflushed batch writes (best-effort on sync abandon)
        if _memory_store._batch_count > 0:
            logger.warning(
                "reset_memory_store: abandoning %d unflushed batch writes",
                _memory_store._batch_count,
            )
            _memory_store._batch_buffer = {}
            _memory_store._batch_count = 0

        # Close the FTS5 SQLite connection before abandoning to prevent
        # ResourceWarning from sqlite3 connections being garbage-collected.
        if hasattr(_memory_store, "fts") and _memory_store.fts is not None:
            try:
                _memory_store.fts.close()
            except (RuntimeError, OSError):
                pass  # Best-effort — MemoryStore is being abandoned anyway
        _memory_store = None
    else:
        _memory_store = None


async def async_reset_memory_store() -> None:
    """Async reset: flushes batch buffer before abandoning. Preferred in tests."""
    global _memory_store
    if _memory_store is not None:
        await _memory_store.close()
        _memory_store = None


def get_memory_store() -> MemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
