# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import os
import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import anyio

from omega.memory.providers import (
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
            # Should not raise — only logs a warning and continues
            await provider.save_history("Sophia", "ses_1", exchanges)
            
            # Verify the data was still saved despite low disk space
            history = await provider.get_history("Sophia", "ses_1", limit=10)
            assert len(history) == 1

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
        # The ten concurrent writers used `f"hello {i}"`, so whichever survived
        # the limit=1 read must be one of those — a "Hello" here (and a torn or
        # empty history) is exactly the corruption this test exists to catch.
        assert history[0]["user"].startswith("hello "), (
            f"concurrent write corrupted the record: {history[0]!r}"
        )
        assert history[0]["assistant"].startswith("hi ")


# [redis-20260928] TestRedisStorageProvider REMOVED (Architect ruling, group B).
# RedisStorageProvider no longer exists — it is not a deprecated shim.
#
# TestMemoryStoreFallbackChain was also removed: it constructed a
# RedisStorageProvider as the first, deliberately-unhealthy tier to prove the
# fallback walk. With that tier gone the test would be asserting a chain
# (USM -> File -> InMemory) that is already covered by
# test_memory_store_fallback elsewhere, and keeping a redis-shaped version of
# it would re-introduce the very import the ruling removed.
#
# NOTE [maat 2026-09-28]: this block was previously spliced INTO the middle of
# test_concurrency_and_locking, orphaning its final assertion below the comment
# at module-body indentation. That left the test asserting a literal "Hello"
# against a writer that emits f"hello {i}" — a guaranteed failure, and a
# corrupted test body rather than a genuine engine defect. Fixed by restoring
# the assertion to the writer's real contract and moving this note to
# module scope where it belongs.

