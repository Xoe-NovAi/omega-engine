"""Sovereign Storage Providers for Omega Memory.
AP: AP-MEMORY-PROVIDERS-v1.0.0
"""

import json
import logging
import os
import gzip
import shutil
import fcntl
import anyio
import redis.asyncio as redis
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class DiskSpaceError(Exception):
    """Raised when disk space is below the safe threshold."""
    pass

class StorageProvider(ABC):
    """Abstract base class for memory storage providers."""
    
    @abstractmethod
    async def get_history(self, entity_name: str, session_id: str, limit: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def save_history(self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def archive(self, entity_name: str, session_id: str) -> bool:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

class RedisStorageProvider(StorageProvider):
    """Hot storage provider using Redis Streams and Hashes."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, password: str = "omega"):
        self.client = redis.Redis(
            host=host, 
            port=port, 
            password=password, 
            decode_responses=True,
            socket_timeout=1.0,
            socket_connect_timeout=1.0
        )
        self.meta_prefix = "omega:session"
        self.hist_prefix = "omega:session:hist"
        self.is_available = False

    async def check_health(self) -> bool:
        """Check if Redis is available with a short timeout."""
        try:
            await self.client.ping()
            self.is_available = True
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            self.is_available = False
            return False

    async def get_history(self, entity_name: str, session_id: str, limit: int) -> List[Dict[str, Any]]:
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
        except Exception as e:
            logger.error(f"Redis get_history failed for {session_id}: {e}")
            self.is_available = False
            return []

    async def save_history(self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]) -> None:
        if not self.is_available:
            if not await self.check_health():
                return
        try:
            meta_key = f"{self.meta_prefix}:{session_id}"
            await self.client.hset(meta_key, mapping={
                "entity": entity_name,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(exchanges)
            })
            await self.client.expire(meta_key, 86400)

            hist_key = f"{self.hist_prefix}:{session_id}"
            await self.client.delete(hist_key)
            
            if exchanges:
                pipeline = self.client.pipeline()
                for ex in exchanges:
                    pipeline.xadd(hist_key, {"json": json.dumps(ex, default=str)})
                await pipeline.execute()
                await self.client.xtrim(hist_key, maxlen=100, approximate=True)
            
            await self.client.expire(hist_key, 86400)
        except Exception as e:
            logger.error(f"Redis save_history failed for {session_id}: {e}")
            self.is_available = False

    async def archive(self, entity_name: str, session_id: str) -> bool:
        if not self.is_available:
            if not await self.check_health():
                return False
        try:
            await self.client.delete(f"{self.meta_prefix}:{session_id}")
            await self.client.delete(f"{self.hist_prefix}:{session_id}")
            return True
        except Exception as e:
            logger.error(f"Redis archive failed for {session_id}: {e}")
            self.is_available = False
            return False

    async def close(self) -> None:
        try:
            await self.client.close()
        except Exception:
            pass

class FileStorageProvider(StorageProvider):
    """Warm storage provider using JSON files on disk with disk guard and file locking."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.entity_dir = data_dir / "entities"
        self.archive_dir = data_dir / "archive"

    def _entity_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = entity_name.lower().replace(" ", "_")
        return self.entity_dir / safe_name / f"{session_id}.json"

    def _archive_path(self, entity_name: str, session_id: str) -> Path:
        safe_name = entity_name.lower().replace(" ", "_")
        return self.archive_dir / safe_name / f"{session_id}.json.gz"

    async def _check_disk_space(self) -> bool:
        """Check if free space is above 10% threshold."""
        try:
            target_dir = self.data_dir
            while not target_dir.exists() and target_dir.parent != target_dir:
                target_dir = target_dir.parent
            usage = await anyio.to_thread.run_sync(shutil.disk_usage, str(target_dir))
            free_percent = usage.free / usage.total
            if free_percent < 0.10:
                logger.error(f"Disk space guard triggered: {free_percent:.2%} free space remaining on {target_dir}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Failed to check disk space: {e}")
            return True

    async def get_history(self, entity_name: str, session_id: str, limit: int) -> List[Dict[str, Any]]:
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

    async def save_history(self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]) -> None:
        if not await self._check_disk_space():
            raise DiskSpaceError(f"Disk space below 10% threshold on {self.data_dir}")
            
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
            lock_path = path.with_suffix(".lock")
            with open(lock_path, "w") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    with open(temp_path, "w") as f:
                        json.dump(data, f, indent=2, default=str)
                    os.replace(temp_path, path)
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
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
        except Exception as e:
            logger.error(f"Failed to read warm path for archiving: {e}")
            return False
        
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
        except Exception:
            pass
        return True

    async def close(self) -> None:
        pass

class InMemoryStorageProvider(StorageProvider):
    """Volatile storage provider using a local dictionary."""
    
    def __init__(self):
        self._storage: Dict[str, List[Dict[str, Any]]] = {}
    
    async def get_history(self, entity_name: str, session_id: str, limit: int) -> List[Dict[str, Any]]:
        key = f"{entity_name}:{session_id}"
        return self._storage.get(key, [])[-limit:]
    
    async def save_history(self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]) -> None:
        key = f"{entity_name}:{session_id}"
        self._storage[key] = exchanges
    
    async def archive(self, entity_name: str, session_id: str) -> bool:
        key = f"{entity_name}:{session_id}"
        return bool(self._storage.pop(key, None))
    
    async def close(self) -> None:
        self._storage.clear()
