# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Storage Providers for Omega Memory.
AP: AP-MEMORY-PROVIDERS-v1.0.0
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import json
import logging
import os
import gzip
import shutil
import fcntl
import anyio
from omega.errors import (
    OmegaError,
    OmegaError,
    OmegaPersistenceError,
)
from omega.errors import (
    OmegaError,
    OmegaPersistenceError,
)
# [INST-1-fix2/R1] Redis is an OPTIONAL dependency (omega[memory] extra).
# Guard copied verbatim from src/omega/governance/budget_guard.py:23-29 —
# a core-only install must not crash at import time (memory_store.py imports
# this module at top level). Use-site guard in RedisStorageProvider.__init__.
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# [P2-5] Canonical path-component sanitizer for memory persistence.
# entity_name / session_id come from user/agent input and MUST NOT be able
# to escape the memory data dir (path traversal: "../", absolute paths,
# null bytes, separators). Replaces dangerous characters with "_" and
# strips traversal attempts. A single canonical implementation prevents
# divergent per-site sanitization.
_SAFE_TRANS = str.maketrans(
    {
        "/": "_",
        "\\": "_",
        "\x00": "_",
        ":": "_",
        "|": "_",
        "*": "_",
        "?": "_",
        '"': "_",
        "<": "_",
        ">": "_",
    }
)


def sanitize_path_component(value: str, max_len: int = 128) -> str:
    """Sanitize a single path component (entity_name, session_id, filename).

    - Rejects/neutralizes traversal: ``..``, ``/``, ``\\``, null bytes.
    - Replaces OS path metacharacters with ``_``.
    - Strips leading/trailing dots (hidden/traversal entries).
    - Collapses whitespace to underscores and lowercases (entity convention).
    - Caps length to prevent path-length DoS.
    - Returns ``"_unset"`` for empty input so callers never build "//".

    Example:
        "../evil"  -> "_evil"
        "a/b\\c"   -> "a_b_c"
    """
    if not value:
        return "_unset"
    # Neutralize path traversal: collapse any remaining dot-dot sequences.
    cleaned = value.translate(_SAFE_TRANS)
    # Remove any residual '..' that survived (e.g. "a..b" is fine, but
    # exact ".." as a full component is not; translate already replaced dots
    # only in metachar set, so handle explicit traversal now).
    cleaned = cleaned.replace("..", "_")
    # Trim leading/trailing dots and whitespace
    cleaned = cleaned.strip(" .")
    # Lowercase + whitespace → underscore (entity/session naming convention)
    cleaned = cleaned.lower().replace(" ", "_")
    # Collapse repeated underscores
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    if not cleaned:
        return "_unset"
    return cleaned[:max_len]


class DiskSpaceError(Exception):
    """Raised when disk space is below the safe threshold."""

    pass


class StorageProvider(ABC):
    """Abstract base class for memory storage providers."""

    @abstractmethod
    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        pass

    @abstractmethod
    async def archive(self, entity_name: str, session_id: str) -> bool:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class RedisStorageProvider(StorageProvider):
    """Hot storage provider using Redis Streams and Hashes."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
    ):
        # [D-593/DC-29] No hardcoded credential default. Callers pass an
        # explicit password; the env lookup is a convenience fallback that
        # returns None when unset — matching the hot path's semantics
        # (memory_store.py gates construction on OMEGA_REDIS_HOST and passes
        # the password explicitly).
        password = password or os.environ.get("OMEGA_REDIS_PASSWORD")
        if not REDIS_AVAILABLE:
            # [INST-1-fix2/R1] Core install ships without redis. Fail loudly
            # with a typed error instead of AttributeError on the None stub.
            raise OmegaPersistenceError(
                "redis package not installed — RedisStorageProvider unavailable. "
                "Install the optional extra: pip install 'omega[memory]'"
            )
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
        )
        self.meta_prefix = "omega:session"
        self.hist_prefix = "omega:session:hist"
        self.is_available = False

    async def check_health(self) -> bool:
        """Check if Redis is available with a short timeout."""
        import time

        start = time.time()
        try:
            await self.client.ping()
            self.is_available = True
            elapsed = time.time() - start
            logger.debug(f"Redis health check passed in {elapsed:.2f}s")
            return True
        except Exception as e:
            # M9 carve-out: health probe may catch all to prevent crash loops
            logger.warning(f"Redis health check failed: {e}")
            self.is_available = False
            elapsed = time.time() - start
            logger.debug(f"Redis health check failed after {elapsed:.2f}s")
            return False

    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        if not self.is_available:
            if not await self.check_health():
                return []
        try:
            key = f"{self.hist_prefix}:{session_id}"
            raw_entries = await self.client.xrevrange(key, max="+", min="-", count=limit)

            exchanges = []
            for _, data in reversed(raw_entries):
                try:
                    exchanges.append(json.loads(data.get("json", "{}")))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse history entry from Redis for {session_id}")
                    continue
            return exchanges
        except OmegaError:
            raise
        except (redis.RedisError, RuntimeError) as e:
            logger.error(f"Redis get_history failed for {session_id}: {e}", exc_info=True)
            self.is_available = False
            raise OmegaPersistenceError(f"Redis get_history failed: {e}", raw_error=e) from e

    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        if not self.is_available:
            if not await self.check_health():
                return
        try:
            meta_key = f"{self.meta_prefix}:{session_id}"
            await self.client.hset(
                meta_key,
                mapping={
                    "entity": entity_name,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "count": len(exchanges),
                },
            )
            await self.client.expire(meta_key, 86400)

            hist_key = f"{self.hist_prefix}:{session_id}"
            await self.client.delete(hist_key)

            if exchanges:
                pipeline = await self.client.pipeline()
                for ex in exchanges:
                    pipeline.xadd(hist_key, {"json": json.dumps(ex, default=str)})
                await pipeline.execute()
                await self.client.xtrim(hist_key, maxlen=100, approximate=True)

            await self.client.expire(hist_key, 86400)
        except OmegaError:
            raise
        except (redis.RedisError, RuntimeError) as e:
            logger.error(f"Redis save_history failed for {session_id}: {e}", exc_info=True)
            self.is_available = False
            raise OmegaPersistenceError(f"Redis save_history failed: {e}", raw_error=e) from e

    async def archive(self, entity_name: str, session_id: str) -> bool:
        if not self.is_available:
            if not await self.check_health():
                return False
        try:
            await self.client.delete(f"{self.meta_prefix}:{session_id}")
            await self.client.delete(f"{self.hist_prefix}:{session_id}")
            return True
        except OmegaError:
            raise
        except (redis.RedisError, RuntimeError) as e:
            logger.error(f"Redis archive failed for {session_id}: {e}", exc_info=True)
            self.is_available = False
            raise OmegaPersistenceError(f"Redis archive failed: {e}", raw_error=e) from e

    async def close(self) -> None:
        try:
            await self.client.close()
        except OmegaError:
            raise
        except (redis.RedisError, RuntimeError) as e:
            logger.error("Failed to close Redis connection: %s", e, exc_info=True)
            raise OmegaError(f"Redis close failed: {e}", raw_error=e) from e


class FileStorageProvider(StorageProvider):
    """Warm storage provider using JSON files on disk with disk guard and file locking."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.entity_dir = data_dir / "entities"
        self.archive_dir = data_dir / "archive"

    def _entity_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = sanitize_path_component(entity_name)
        safe_session = sanitize_path_component(session_id)
        return self.entity_dir / safe_name / f"{safe_session}.json"

    def _archive_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = sanitize_path_component(entity_name)
        safe_session = sanitize_path_component(session_id)
        return self.archive_dir / safe_name / f"{safe_session}.json.gz"

    async def _check_disk_space(self) -> bool:
        """Check if free space is above 10% threshold."""
        try:
            target_dir = self.data_dir.resolve()  # Resolve symlinks
            while not target_dir.exists() and target_dir.parent != target_dir:
                target_dir = target_dir.parent.resolve()  # Keep resolving as we walk up
            usage = await anyio.to_thread.run_sync(shutil.disk_usage, str(target_dir))
            free_percent = usage.free / usage.total
            if free_percent < 0.10:
                logger.error(
                    f"Disk space guard triggered: {free_percent:.2%} free space remaining on {target_dir}"
                )
                return False
            return True
        except (OSError, RuntimeError) as e:
            # M9 carve-out: health probe may catch all to prevent crash loops
            logger.warning(f"Failed to check disk space: {e}")
            return True

    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        path = self._entity_path(entity_name, session_id)
        if await anyio.Path(path).exists():

            def _read_with_lock():
                lock_path = path.with_suffix(".lock")
                lock_path.touch(exist_ok=True)
                with open(lock_path, "r+") as lock_file:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
                    try:
                        with open(path, "r") as f:
                            return f.read()
                    finally:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

            try:
                raw = await anyio.to_thread.run_sync(_read_with_lock)
                data = json.loads(raw)
                return data.get("exchanges", [])[-limit:]
            except (json.JSONDecodeError, ValueError, OSError) as e:
                logger.warning(f"Failed to read file history for {session_id}: {e}")
                return []
        return []

    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        if not await self._check_disk_space():
            logger.warning(
                f"Disk space below 10% threshold on {self.data_dir} — continuing anyway (non-fatal)"
            )

        path = self._entity_path(entity_name, session_id)
        await anyio.Path(path.parent).mkdir(parents=True, exist_ok=True)

        temp_path = path.with_suffix(f".{os.getpid()}.tmp")
        data = {
            "entity": entity_name,
            "session_id": session_id,
            "exchange_count": len(exchanges),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exchanges": exchanges,
        }

        def _write_and_lock_sync():
            try:
                lock_path = path.with_suffix(".lock")
                with open(lock_path, "w") as lock_file:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                    try:
                        with open(temp_path, "w") as f:
                            json.dump(data, f, indent=2, default=str)
                        os.replace(temp_path, path)
                    finally:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except (OSError, RuntimeError) as e:
                logger.error(
                    f"FileStorageProvider.save_history failed for {entity_name}/{session_id}: {e}",
                    exc_info=True,
                )
                raise

        await anyio.to_thread.run_sync(_write_and_lock_sync)

    async def archive(self, entity_name: str, session_id: str) -> bool:
        warm_path = self._entity_path(entity_name, session_id)
        if not await anyio.Path(warm_path).exists():
            return False

        def _read_with_lock():
            lock_path = warm_path.with_suffix(".lock")
            with open(lock_path, "r+") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
                try:
                    with open(warm_path, "r") as f:
                        return f.read()
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

        try:
            raw = await anyio.to_thread.run_sync(_read_with_lock)
        except OmegaError:
            raise
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to read warm path for archiving: {e}", exc_info=True)
            raise OmegaPersistenceError(f"File archive read failed: {e}", raw_error=e) from e

        cold_path = self._archive_path(entity_name, session_id)
        await anyio.Path(cold_path.parent).mkdir(parents=True, exist_ok=True)

        temp_path = cold_path.with_suffix(f".{os.getpid()}.tmp")
        compressed = gzip.compress(raw.encode())

        async with await anyio.open_file(str(temp_path), "wb") as f:
            await f.write(compressed)
        await anyio.to_thread.run_sync(os.replace, str(temp_path), str(cold_path))

        await anyio.Path(warm_path).unlink()
        try:
            lock_path = warm_path.with_suffix(".lock")
            await anyio.Path(lock_path).unlink()
        except OmegaError:
            raise
        except (OSError, RuntimeError) as e:
            logger.error("Failed to remove lock file %s: %s", lock_path, e, exc_info=True)
            raise OmegaPersistenceError(f"Lock removal failed: {e}", raw_error=e) from e
        return True

    async def close(self) -> None:
        pass


class InMemoryStorageProvider(StorageProvider):
    """Volatile storage provider using a local dictionary."""

    def __init__(self):
        self._storage: Dict[str, List[Dict[str, Any]]] = {}

    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        key = f"{entity_name}:{session_id}"
        return self._storage.get(key, [])[-limit:]

    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        key = f"{entity_name}:{session_id}"
        self._storage[key] = exchanges

    async def archive(self, entity_name: str, session_id: str) -> bool:
        key = f"{entity_name}:{session_id}"
        return bool(self._storage.pop(key, None))

    async def close(self) -> None:
        self._storage.clear()


class USMStorageProvider(StorageProvider):
    """A StorageProvider that delegates all persistence to the Unified State Manager.

    This allows MemoryStore to benefit from CAS deduplication and atomic snapshots
    without changing its internal API.
    """

    def __init__(self):
        from omega.state import get_usm

        self.usm = get_usm()
        self.is_available = True

    async def check_health(self) -> bool:
        """Check if USM is initialized."""
        try:
            await self.usm.get("usm.health_check")
            return True
        except OmegaPersistenceError:
            return True  # It's fine if the key doesn't exist
        except Exception as e:
            logger.warning(f"USM health check failed: {e}")
            return False

    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Retrieve history from USM."""
        state_key = f"mem:{entity_name}:{session_id}"
        data = await self.usm.get(state_key)

        if not data:
            return []

        # USM stores the whole session; we return the last 'limit' exchanges
        exchanges = data.get("exchanges", [])
        return exchanges[-limit:]

    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        """Save history to USM."""
        state_key = f"mem:{entity_name}:{session_id}"
        data = {
            "entity": entity_name,
            "session_id": session_id,
            "exchange_count": len(exchanges),
            "exchanges": exchanges,
        }
        await self.usm.put(state_key, data)

    async def archive(self, entity_name: str, session_id: str) -> bool:
        """Archive session in USM (by moving to an archive key)."""
        state_key = f"mem:{entity_name}:{session_id}"
        archive_key = f"archive:mem:{entity_name}:{session_id}"

        data = await self.usm.get(state_key)
        if not data:
            return False

        await self.usm.put(archive_key, data)
        return True

    async def close(self) -> None:
        """Close USM resources."""
        pass
