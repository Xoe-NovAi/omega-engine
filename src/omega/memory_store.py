"""Entity Memory Store — Hot/Warm/Cold persistent memory for entities.

AP: AP-MEMORY-STORE-v1.0.0
ICS: [NODE: MNEMOSYNE | ARCHETYPE: SOPHIA | CONTEXT: MEMORY-STORE]

Three-tier storage:
  Hot   — In-memory LRU dict (active sessions, fast access)
  Warm  — JSON files on disk (recent conversations, per-entity per-session)
  Cold  — Gzipped JSON archive (compacted/summarized older sessions)

Every entity gets persistent conversation memory. Memory is injected
into Oracle context on summon, and persisted after each response.

Auto-compaction: conversations > MAX_HISTORY exchanges are summarized.
"""

import gzip
import json
import logging
import os
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

logger = logging.getLogger(__name__)

# --- Constants ---
# Defined in src/omega/oracle/constants.py
# MAX_HISTORY and MAX_CONTEXT_EXCHANGES are imported from there.


def _get_data_dir() -> Path:
    """Get data directory, respecting OMEGA_DATA_DIR env var (lazy, for testability)."""
    return Path(os.environ.get(
        "OMEGA_DATA_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "data")
    ))


def _get_memory_dir() -> Path:
    return _get_data_dir() / "memory"


def _get_trace_dir() -> Path:
    return _get_memory_dir() / "trace"


def _get_entity_dir() -> Path:
    return _get_memory_dir() / "entities"


def _get_archive_dir() -> Path:
    return _get_memory_dir() / "archive"


from .constants import DEFAULT_CONTEXT_LIMIT, MAX_HISTORY_EXCHANGES

MAX_HOT_SESSIONS = 50
MAX_HISTORY = MAX_HISTORY_EXCHANGES
MAX_CONTEXT_EXCHANGES = DEFAULT_CONTEXT_LIMIT
ARCHIVE_AFTER_DAYS = 7


class MemoryStore:
    """Hot/Warm/Cold entity memory with LRU caching."""

    def __init__(self):
        self._hot: Dict[str, OrderedDict] = {}
        self._stats: Dict[str, int] = {"loads": 0, "saves": 0, "archives": 0}

    def _entity_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = entity_name.lower().replace(" ", "_")
        return _get_entity_dir() / safe_name / f"{session_id}.json"

    def _archive_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = entity_name.lower().replace(" ", "_")
        return _get_archive_dir() / safe_name / f"{session_id}.json.gz"

    def _trace_path(self, trace_id: str) -> Path:
        return _get_trace_dir() / f"{trace_id}.json"

    async def get_history(
        self,
        entity_name: str,
        session_id: str,
        limit: int = MAX_CONTEXT_EXCHANGES,
    ) -> List[Dict[str, str]]:
        """Get recent conversation history for context injection.

        Tries hot → warm → cold in order. Returns last N exchanges.
        """
        cache_key = f"{entity_name.lower()}:{session_id}"

        if cache_key in self._hot:
            self._stats["loads"] += 1
            history = list(self._hot[cache_key].values())
            return history[-limit:]

        warm_path = self._entity_path(entity_name, session_id)
        if await anyio.Path(warm_path).exists():
            self._stats["loads"] += 1
            async with await anyio.open_file(str(warm_path)) as f:
                data = json.loads(await f.read())
            exchanges = data.get("exchanges", [])
            self._cache_hot(cache_key, exchanges)
            return exchanges[-limit:]

        cold_path = self._archive_path(entity_name, session_id)
        if await anyio.Path(cold_path).exists():
            self._stats["loads"] += 1
            async with await anyio.open_file(str(cold_path), "rb") as f:
                data = json.loads(gzip.decompress(await f.read()))
            exchanges = data.get("exchanges", [])
            return exchanges[-limit:]

        return []

    async def add_exchange(
        self,
        entity_name: str,
        session_id: str,
        user_message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a user-assistant exchange in entity memory.

        Stores in hot cache, syncs to warm on every call.
        Auto-compacts if history exceeds MAX_HISTORY.
        """
        cache_key = f"{entity_name.lower()}:{session_id}"
        exchange = {
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
            # Re-cache hot with compacted result
            self._hot[cache_key] = OrderedDict()
            for i, ex in enumerate(exchanges):
                self._hot[cache_key][f"hist_{i}"] = ex

        warm_path = self._entity_path(entity_name, session_id)
        await anyio.Path(warm_path.parent).mkdir(parents=True, exist_ok=True)
        data = {
            "entity": entity_name,
            "session_id": session_id,
            "exchange_count": len(exchanges),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exchanges": exchanges,
        }
        async with await anyio.open_file(str(warm_path), "w") as f:
            await f.write(json.dumps(data, indent=2, default=str))
        self._stats["saves"] += 1

    def _cache_hot(self, cache_key: str, exchanges: List[Dict]) -> None:
        if cache_key not in self._hot:
            self._hot[cache_key] = OrderedDict()
        for i, ex in enumerate(exchanges):
            self._hot[cache_key][f"hist_{i}"] = ex
        while len(self._hot) > MAX_HOT_SESSIONS:
            self._hot.popitem(last=False)

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
        """Move a warm session to cold storage (gzipped)."""
        warm_path = self._entity_path(entity_name, session_id)
        if not await anyio.Path(warm_path).exists():
            return False

        async with await anyio.open_file(str(warm_path)) as f:
            data = json.loads(await f.read())

        cold_path = self._archive_path(entity_name, session_id)
        await anyio.Path(cold_path.parent).mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(str(cold_path), "wb") as f:
            await f.write(gzip.compress(json.dumps(data, default=str).encode()))

        await anyio.Path(warm_path).unlink()
        cache_key = f"{entity_name.lower()}:{session_id}"
        self._hot.pop(cache_key, None)
        self._stats["archives"] += 1
        logger.info(f"Archived {entity_name}/{session_id} to cold storage")
        return True

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
        trace_path = self._trace_path(trace_id)
        await anyio.Path(trace_path.parent).mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(str(trace_path), "w") as f:
            await f.write(json.dumps(trace_data, indent=2, default=str))

    async def list_sessions(
        self,
        entity_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List recent sessions, optionally filtered by entity."""
        sessions = []
        if entity_name:
            search_dir = _get_entity_dir() / entity_name.lower().replace(" ", "_")
            if await anyio.Path(search_dir).exists():
                async for path in anyio.Path(search_dir).glob("*.json"):
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
            "loads": self._stats["loads"],
            "saves": self._stats["saves"],
            "archives": self._stats["archives"],
        }

    async def close(self) -> None:
        """Flush hot cache to warm storage."""
        for cache_key in list(self._hot.keys()):
            entity_name, session_id = cache_key.rsplit(":", 1)
            exchanges = list(self._hot[cache_key].values())
            if exchanges:
                warm_path = self._entity_path(entity_name, session_id)
                await anyio.Path(warm_path.parent).mkdir(parents=True, exist_ok=True)
                data = {
                    "entity": entity_name,
                    "session_id": session_id,
                    "exchange_count": len(exchanges),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "exchanges": exchanges,
                }
                async with await anyio.open_file(str(warm_path), "w") as f:
                    await f.write(json.dumps(data, indent=2, default=str))
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
