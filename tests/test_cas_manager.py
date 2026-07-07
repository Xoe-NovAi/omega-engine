"""Contract tests for CASManager.
M21: Gate Integrity — All core API boundaries must have contract tests.
"""

import pytest
import tempfile
from pathlib import Path
from omega.state import CASManager
from omega.errors import OmegaPersistenceError


class TestCASManager:
    @pytest.fixture
    async def cas(self):
        with tempfile.TemporaryDirectory() as tmp:
            cas = CASManager(Path(tmp))
            await cas.initialize()
            yield cas
    
    @pytest.mark.anyio
    async def test_put_get_roundtrip(self, cas):
        await cas.initialize()
        data = b"hello world"
        hash_ = await cas.put(data)
        assert await cas.get(hash_) == data
    
    @pytest.mark.anyio
    async def test_deduplication(self, cas):
        await cas.initialize()
        data = b"duplicate content"
        hash1 = await cas.put(data)
        hash2 = await cas.put(data)
        assert hash1 == hash2
    
    @pytest.mark.anyio
    async def test_exists(self, cas):
        await cas.initialize()
        data = b"test"
        hash_ = await cas.put(data)
        assert await cas.exists(hash_) is True
        assert await cas.exists("nonexistent") is False
    
    @pytest.mark.anyio
    async def test_delete(self, cas):
        await cas.initialize()
        data = b"test"
        hash_ = await cas.put(data)
        await cas.delete(hash_)
        assert await cas.exists(hash_) is False
    
    @pytest.mark.anyio
    async def test_sharding_structure(self, cas):
        await cas.initialize()
        data = b"shard test"
        hash_ = await cas.put(data)
        # Verify sharding: blobs/ab/cd/<hash>
        path = cas._get_blob_path(hash_)
        assert path.parent.name == hash_[2:4]
        assert path.parent.parent.name == hash_[:2]
    
    @pytest.mark.anyio
    async def test_empty_data_raises(self, cas):
        await cas.initialize()
        with pytest.raises(OmegaPersistenceError):
            await cas.put(b"")
    
    @pytest.mark.anyio
    async def test_integrity_verification(self, cas):
        await cas.initialize()
        data = b"integrity test"
        hash_ = await cas.put(data)
        # Corrupt the blob directly
        path = cas._get_blob_path(hash_)
        await anyio.Path(path).write_bytes(b"corrupted")
        with pytest.raises(OmegaPersistenceError):
            await cas.get(hash_)


# Need to import anyio for the test
import anyio