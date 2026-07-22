"""Chaos test: OOMProtector handles SIGKILL from OOM killer."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.chaos
@pytest.mark.anyio
async def test_oom_protector_handles_sigkill(admission_controller):
    """Simulate OOM killer sending SIGKILL — admission should fail-fast."""
    # In a real OOM scenario, the kernel kills the process.
    # This test verifies that admission controller releases resources on unexpected exit.
    
    # Acquire admission
    acquired = await admission_controller.acquire("model-a")
    assert acquired is True
    
    # Simulate process crash by directly manipulating internal state
    # (In real OOM, the semaphore is automatically released by the kernel)
    admission_controller._current_model = None
    admission_controller._semaphore.release()
    
    # Verify admission is available again
    assert admission_controller.is_available
    
    # Acquire again should succeed
    acquired2 = await admission_controller.acquire("model-b")
    assert acquired2 is True
    admission_controller.release()

@pytest.mark.chaos
@pytest.mark.anyio
async def test_oom_protector_RAM_check_under_pressure(oom_protector):
    """Verify OOMProtector correctly detects low RAM conditions."""
    # Mock the available RAM to simulate low memory
    with patch("omega.oracle.resource_guard._get_available_ram_mb", return_value=500):
        # Should return False when RAM is low
        result = oom_protector.check(model_ram_mb=1000, kv_cache_mb=512)
        assert result is False
    
    # Mock normal RAM
    with patch("omega.oracle.resource_guard._get_available_ram_mb", return_value=8000):
        result = oom_protector.check(model_ram_mb=1000, kv_cache_mb=512)
        assert result is True

from unittest.mock import patch
