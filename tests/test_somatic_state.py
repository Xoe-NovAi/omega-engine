"""Tests for Phase C — Somatic State (C.1.1–C.1.2)."""

import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock
import anyio

from omega.cvar_table import cvar_get
from omega.oracle.state_manager import UnifiedStateManager, CASBlobStore, SomaticStateSerializer

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.model = MagicMock()
    return model

@pytest.mark.anyio
async def test_usm_freeze_resume_cycle(mock_model):
    """Verify that USM can freeze and resume a state bundle."""
    test_dir = "data/test_somatic"
    usm = UnifiedStateManager(model=mock_model, base_dir=test_dir)
    
    usm.somatic._capture = MagicMock(return_value=b"binary-state-data")
    usm.somatic._apply = MagicMock()
    
    entity_id = "test-entity"
    mem_data = b"memory-data"
    sess_data = b"session-data"
    
    bundle_hash = await usm.freeze(entity_id, mem_data, sess_data)
    assert bundle_hash is not None
    assert len(bundle_hash) == 64
    
    restored = await usm.resume(bundle_hash)
    
    assert restored["entity_id"] == entity_id
    assert restored["memory"] == mem_data
    assert restored["session"] == sess_data
    usm.somatic._apply.assert_called_once_with(b"binary-state-data")
    
    shutil.rmtree(test_dir, ignore_errors=True)

@pytest.mark.anyio
async def test_cas_blob_store_atomicity():
    """Verify that CASBlobStore writes atomically."""
    test_dir = "data/test_cas"
    store = CASBlobStore(base_dir=test_dir)
    
    data = b"hello sovereign world"
    blob_hash = await store.put(data)
    
    assert (Path(test_dir) / f"{blob_hash}.bin").exists()
    assert await store.get(blob_hash) == data
    
    shutil.rmtree(test_dir, ignore_errors=True)

class TestSomaticStateKey:
    """SomaticStateKey parameter tuple validation."""

    def test_master_kill_switch_exists(self):
        assert cvar_get("config.somatic.enable") is False

    def test_somatic_cvars_registered(self):
        assert cvar_get("config.somatic.max_snapshots_per_entity") == 3
        assert cvar_get("config.somatic.memory_budget_mb") == 1024
        assert cvar_get("config.somatic.page_size_mb") == 2
        assert cvar_get("config.somatic.ctypes_safe_mode") is True

class TestDreamingCycleCvars:
    """Dreaming Cycle cvar configuration (C.2.x)."""

    def test_dreaming_cvars_registered(self):
        assert cvar_get("config.dreaming.enable") is False
        assert cvar_get("config.dreaming.model") == "qwen3-0.6b"
        assert cvar_get("config.dreaming.max_rss_mb") == 1500
        assert cvar_get("config.dreaming.max_hours_per_day") == 4
        assert cvar_get("config.dreaming.poll_interval_ms") == 100

class TestSymmetryCvars:
    """Symmetry-Break Audit cvar configuration (C.3.x)."""

    def test_symmetry_cvars_registered(self):
        assert cvar_get("config.symmetry.enable") is False
        assert cvar_get("config.symmetry.mode") == "fast"
        assert cvar_get("config.symmetry.max_attempts") == 2
        assert cvar_get("config.symmetry.semantic_delta_threshold") == 0.3
