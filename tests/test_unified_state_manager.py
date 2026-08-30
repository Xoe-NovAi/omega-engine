# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for UnifiedStateManager.
M21: Gate Integrity — All core API boundaries must have contract tests.
"""

import pytest
import tempfile
from pathlib import Path
from omega.state import UnifiedStateManager


class TestUnifiedStateManager:
    @pytest.fixture
    async def usm(self):
        with tempfile.TemporaryDirectory() as tmp:
            usm = UnifiedStateManager(Path(tmp))
            await usm.initialize()
            yield usm
    
    @pytest.mark.anyio
    async def test_session_save_load(self, usm):
        yaml_data = "entity: test\nmessages:\n  - hello\n  - world"
        hash_ = await usm.save_session("ses_123", yaml_data)
        loaded = await usm.load_session("ses_123")
        assert loaded == yaml_data
        assert usm.has_session("ses_123")
    
    @pytest.mark.anyio
    async def test_session_release(self, usm):
        yaml_data = "test"
        await usm.save_session("ses_123", yaml_data)
        assert await usm.release_session("ses_123") is True
        assert not usm.has_session("ses_123")
    
    @pytest.mark.anyio
    async def test_memory_save_load(self, usm):
        json_data = '{"key": "value", "count": 42}'
        hash_ = await usm.save_memory("entity_1", json_data)
        loaded = await usm.load_memory("entity_1")
        assert loaded == json_data
        assert usm.has_memory("entity_1")
    
    @pytest.mark.anyio
    async def test_handoff_save_load(self, usm):
        payload = b"x" * 20000  # >10KB
        hash_ = await usm.save_handoff("pkt_123", payload)
        loaded = await usm.load_handoff("pkt_123")
        assert loaded == payload
        assert usm.has_handoff("pkt_123")
    
    @pytest.mark.anyio
    async def test_stats(self, usm):
        await usm.save_session("s1", "a")
        await usm.save_memory("e1", "b")
        await usm.save_handoff("p1", b"c")
        stats = await usm.stats()
        assert stats["tracked_sessions"] == 1
        assert stats["tracked_memories"] == 1
        assert stats["tracked_handoffs"] == 1
        assert "somatic_available" in stats
