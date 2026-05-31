import os
import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import anyio

from omega.memory.providers import (
    RedisStorageProvider,
    FileStorageProvider,
    InMemoryStorageProvider,
    DiskSpaceError,
)
from omega.memory_store import MemoryStore

@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    yield tmp_path

class TestInMemoryStorageProvider:
    @pytest.mark.anyio
    async def test_basic_operations(self):
        provider = InMemoryStorageProvider()
        exchanges = [{"user": "hello", "assistant": "hi"}]
        
        await provider.save_history("Sophia", "ses_1", exchanges)
        history = await provider.get_history("Sophia", "ses_1", limit=10)
        assert history == exchanges
        
        archived = await provider.archive("Sophia", "ses_1")
        assert archived is True
        
        history_after = await provider.get_history("Sophia", "ses_1", limit=10)
        assert history_after == []

class TestFileStorageProvider:
    @pytest.mark.anyio
    async def test_basic_operations(self, temp_data_dir):
        provider = FileStorageProvider(data_dir=temp_data_dir)
        exchanges = [{"user": "hello", "assistant": "hi"}]
        
        await provider.save_history("Sophia", "ses_1", exchanges)
        history = await provider.get_history("Sophia", "ses_1", limit=10)
        assert history == exchanges
        
        # Verify file exists
        path = temp_data_dir / "entities" / "sophia" / "ses_1.json"
        assert path.exists()
        
        # Archive
        archived = await provider.archive("Sophia", "ses_1")
        assert archived is True
        assert not path.exists()
        
        archive_path = temp_data_dir / "archive" / "sophia" / "ses_1.json.gz"
        assert archive_path.exists()

    @pytest.mark.anyio
    async def test_disk_space_guard(self, temp_data_dir):
        provider = FileStorageProvider(data_dir=temp_data_dir)
        exchanges = [{"user": "hello", "assistant": "hi"}]
        
        # Mock shutil.disk_usage to return 5% free space
        mock_usage = MagicMock()
        mock_usage.total = 1000
        mock_usage.free = 50  # 5%
        
        with patch("shutil.disk_usage", return_value=mock_usage):
            with pytest.raises(DiskSpaceError):
                await provider.save_history("Sophia", "ses_1", exchanges)

    @pytest.mark.anyio
    async def test_concurrency_and_locking(self, temp_data_dir):
        provider = FileStorageProvider(data_dir=temp_data_dir)
        
        async def write_task(i):
            exchanges = [{"user": f"hello {i}", "assistant": f"hi {i}"}]
            await provider.save_history("Sophia", "ses_concurrent", exchanges)
            
        # Run multiple concurrent writes
        async with anyio.create_task_group() as tg:
            for i in range(10):
                tg.start_soon(write_task, i)
                
        # Verify we can read without corruption
        history = await provider.get_history("Sophia", "ses_concurrent", limit=1)
        assert len(history) == 1

class TestRedisStorageProvider:
    @pytest.mark.anyio
    async def test_health_check_failure(self):
        # Redis is not running or fails health check
        provider = RedisStorageProvider(host="nonexistent_host", port=1234)
        assert await provider.check_health() is False
        
        # Operations should fail gracefully and return empty/None
        assert await provider.get_history("Sophia", "ses_1", 10) == []
        await provider.save_history("Sophia", "ses_1", [{"user": "hi"}]) # Should not raise

    @pytest.mark.anyio
    async def test_mocked_success(self):
        provider = RedisStorageProvider()
        provider.client = AsyncMock()
        provider.client.ping = AsyncMock()
        provider.client.xrevrange = AsyncMock(return_value=[
            ("1-0", {"json": '{"user": "hello", "assistant": "hi"}'})
        ])
        provider.client.hset = AsyncMock()
        provider.client.expire = AsyncMock()
        provider.client.delete = AsyncMock()
        
        # Mock pipeline
        mock_pipeline = AsyncMock()
        provider.client.pipeline.return_value = mock_pipeline
        
        assert await provider.check_health() is True
        
        history = await provider.get_history("Sophia", "ses_1", 10)
        assert len(history) == 1
        assert history[0]["user"] == "hello"
        
        await provider.save_history("Sophia", "ses_1", [{"user": "hello", "assistant": "hi"}])
        provider.client.hset.assert_called_once()

class TestMemoryStoreFallbackChain:
    @pytest.mark.anyio
    async def test_fallback_flow(self, temp_data_dir):
        # Setup providers:
        # 1. Redis (fails health check)
        redis_provider = RedisStorageProvider(host="nonexistent_host")
        
        # 2. File (succeeds)
        file_provider = FileStorageProvider(data_dir=temp_data_dir)
        
        # 3. InMemory (succeeds)
        in_mem_provider = InMemoryStorageProvider()
        
        store = MemoryStore(providers=[redis_provider, file_provider, in_mem_provider])
        
        # Add exchange - should fall back to File and InMemory
        await store.add_exchange("Sophia", "ses_fallback", "Hello", "Hi")
        
        # Verify it was saved to File
        path = temp_data_dir / "entities" / "sophia" / "ses_fallback.json"
        assert path.exists()
        
        # Verify we can load it back
        history = await store.get_history("Sophia", "ses_fallback")
        assert len(history) == 1
        assert history[0]["user"] == "Hello"
