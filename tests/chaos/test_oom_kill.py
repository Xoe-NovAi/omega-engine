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

# [CUT-20261007] Hermetic: check() fuses THREE live signals (MemAvailable +
# PSI stalls + cgroup pressure). The RAM mock freezes only one leg — on a host
# whose real PSI full-stall exceeds 5% (a busy dev box), check() honestly
# reports DENY_THRASHING. Freeze the pressure legs too so the test asserts the
# RAM arithmetic it was written for, on every host.
from omega.oracle.oom_protector import AdmissionResult  # noqa: E402


@pytest.fixture
def _calm_pressure(oom_protector):
    from omega.oracle.psi_monitor import PSISnapshot, Resource

    with patch.object(
        oom_protector.psi, "get_all_metrics", new_callable=AsyncMock
    ) as m_psi:
        m_psi.return_value = PSISnapshot(
            resource=Resource.MEMORY,
            some_avg10=0.0, some_avg60=0.0, some_avg300=0.0, some_total_us=0,
            full_avg10=0.0, full_avg60=0.0, full_avg300=0.0, full_total_us=0,
        )
        yield m_psi

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
# [maat 2026-09-29] RESIDUAL — I TRIED to mark this `isolated_oom_ram` and REVERTED IT.
#
# The brief said `test_oom_protector_RAM_check_under_pressure` was the failing
# one. Measured against both legs, it is not:
#     baseline origin/main : RAM_check_under_pressure PASSED, handles_sigkill PASSED
#     full-suite run       : RAM_check_under_pressure PASSED, handles_sigkill FAILED
# This test mocks `get_memavailable_gb` and asserts the decision arithmetic, so
# it is deterministic. It was never the problem.
#
# Marking it `isolated_oom_ram` made it WORSE: the conftest's isolation fixture
# patches `OOMProtector.check_available` to always return True, and this test
# asserts on exactly that method — so the isolation overrode the subject under
# test and turned a passing test red. Recorded because "the brief said X" is not
# evidence, and the fix that looked responsive would have shipped a new failure.
async def test_oom_protector_RAM_check_under_pressure(oom_protector, _calm_pressure):
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
