# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M21 Contract Tests: OOM detection works (5 tests)."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_check_returns_admission_result():
    """OOMProtector.check() returns AdmissionResult."""
    from omega.oracle.oom_protector import OOMProtector, AdmissionResult
    
    protector = OOMProtector.__new__(OOMProtector)
    # Mock the snapshot and fusion
    protector._take_snapshot = AsyncMock(return_value={})
    protector._fuse_signals = MagicMock(return_value=AdmissionResult.ALLOW)
    
    result = await protector.check()
    assert isinstance(result, AdmissionResult)

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_check_available_true():
    """OOMProtector.check_available() returns True when memory sufficient."""
    from omega.oracle.oom_protector import OOMProtector
    
    protector = OOMProtector.__new__(OOMProtector)
    # Mock MemAvailableReader.get_memavailable_gb (async)
    protector.memavailable = MagicMock()
    protector.memavailable.get_memavailable_gb = AsyncMock(return_value=8.0)  # 8GB available
    
    # Mock config with reserve
    protector.config = MagicMock()
    protector.config.reserve_gb = 1.0
    
    result = await protector.check_available(required_gb=2.0)
    assert result is True  # 8GB >= 2GB + 1GB reserve

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_check_available_false():
    """OOMProtector.check_available() returns False when memory insufficient."""
    from omega.oracle.oom_protector import OOMProtector
    
    protector = OOMProtector.__new__(OOMProtector)
    protector.memavailable = MagicMock()
    protector.memavailable.get_memavailable_gb = AsyncMock(return_value=2.0)  # 2GB available
    
    protector.config = MagicMock()
    protector.config.reserve_gb = 1.0
    
    result = await protector.check_available(required_gb=2.0)
    assert result is False  # 2GB < 2GB + 1GB reserve

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_deny_on_low_memory():
    """OOMProtector denies admission when MemAvailable < min_reserve_gb."""
    from omega.oracle.oom_protector import OOMProtector, AdmissionResult, PressureSnapshot
    
    protector = OOMProtector.__new__(OOMProtector)
    # Create a proper PressureSnapshot dataclass with low memory
    snapshot = PressureSnapshot(
        memavailable_gb=0.5,   # Very low — below 1GB reserve
        psi_some_avg60=0.0,
        psi_some_avg10=0.0,
        psi_some_avg300=0.0,
        psi_full_avg10=0.0,
        psi_full_avg60=0.0,
        psi_full_avg300=0.0,
    )
    protector._take_snapshot = AsyncMock(return_value=snapshot)
    
    # Mock config
    protector.config = MagicMock()
    protector.config.min_reserve_gb = 1.0  # 1GB minimum
    protector.config.psi_full_critical = 0.05
    protector.config.psi_some_warning = 0.10
    protector.config.cgroup_some_warning = 0.15
    protector.config.cgroup_full_critical = 0.05
    protector.config.throttle_gb = 4.0
    
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_OOM_RISK

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_allow_on_sufficient_memory():
    """OOMProtector allows admission when memory is sufficient."""
    from omega.oracle.oom_protector import OOMProtector, AdmissionResult, PressureSnapshot
    
    protector = OOMProtector.__new__(OOMProtector)
    # Create a proper PressureSnapshot dataclass with plenty of memory
    snapshot = PressureSnapshot(
        memavailable_gb=8.0,
        psi_some_avg60=0.01,
        psi_some_avg10=0.01,
        psi_some_avg300=0.01,
        psi_full_avg10=0.0,
        psi_full_avg60=0.0,
        psi_full_avg300=0.0,
    )
    protector._take_snapshot = AsyncMock(return_value=snapshot)
    
    protector.config = MagicMock()
    protector.config.min_reserve_gb = 1.0
    protector.config.psi_full_critical = 0.05
    protector.config.psi_some_warning = 0.10
    protector.config.cgroup_some_warning = 0.15
    protector.config.cgroup_full_critical = 0.05
    protector.config.throttle_gb = 4.0
    
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.ALLOW
