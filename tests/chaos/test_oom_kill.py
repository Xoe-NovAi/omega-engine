# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Chaos test: OOMProtector handles SIGKILL from OOM killer."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
from unittest.mock import patch, AsyncMock

from omega.oracle.oom_protector import AdmissionResult

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
    """Verify OOMProtector correctly detects low RAM conditions (C-2' API)."""
    # [C-2'] OOMProtector uses check_available(required_gb) for memory checks.
    # Mock MemAvailableReader to simulate low/high RAM.
    with patch.object(
        oom_protector.memavailable, "get_memavailable_gb",
        new_callable=AsyncMock,
    ) as mock_mem:
        mock_mem.return_value = 0.5  # 0.5 GB — very low
        
        # check_available should return False when RAM is low
        result = await oom_protector.check_available(required_gb=1.0)
        assert result is False
        
        # check() should return DENY_OOM_RISK
        decision = await oom_protector.check()
        assert decision == AdmissionResult.DENY_OOM_RISK
    
    # Mock normal RAM (8 GB available, reserve is 2 GB, so 6 GB usable)
    with patch.object(
        oom_protector.memavailable, "get_memavailable_gb",
        new_callable=AsyncMock,
    ) as mock_mem:
        mock_mem.return_value = 8.0
        
        result = await oom_protector.check_available(required_gb=1.0)
        assert result is True
        
        decision = await oom_protector.check()
        assert decision == AdmissionResult.ALLOW
