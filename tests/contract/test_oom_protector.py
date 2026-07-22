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
    # Mock MemAvailableReader
    protector.memavailable = MagicMock()
    protector.memavailable.read_available_gb = MagicMock(return_value=8.0)  # 8GB available
    
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
    protector.memavailable.read_available_gb = MagicMock(return_value=2.0)  # 2GB available
    
    protector.config = MagicMock()
    protector.config.reserve_gb = 1.0
    
    result = await protector.check_available(required_gb=2.0)
    assert result is False  # 2GB < 2GB + 1GB reserve

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_deny_on_low_memory():
    """OOMProtector denies admission when MemAvailable < min_reserve_gb."""
    from omega.oracle.oom_protector import OOMProtector, AdmissionResult
    
    protector = OOMProtector.__new__(OOMProtector)
    # Mock snapshot with low memory
    snapshot = {
        "memavailable_gb": 0.5,  # Very low
        "psi_full_avg10": 0.0,
        "cgroup_full_avg10": 0.0,
        "psi_some_avg60": 0.0,
        "cgroup_some_avg60": 0.0,
    }
    protector._take_snapshot = AsyncMock(return_value=snapshot)
    
    # Mock config
    protector.config = MagicMock()
    protector.config.min_reserve_gb = 1.0  # 1GB minimum
    
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_OOM_RISK

@pytest.mark.contract
@pytest.mark.anyio
async def test_oom_protector_allow_on_sufficient_memory():
    """OOMProtector allows admission when memory is sufficient."""
    from omega.oracle.oom_protector import OOMProtector, AdmissionResult
    
    protector = OOMProtector.__new__(OOMProtector)
    # Mock snapshot with plenty of memory
    snapshot = {
        "memavailable_gb": 8.0,
        "psi_full_avg10": 0.0,
        "cgroup_full_avg10": 0.0,
        "psi_some_avg60": 0.0,
        "cgroup_some_avg60": 0.0,
    }
    protector._take_snapshot = AsyncMock(return_value=snapshot)
    
    protector.config = MagicMock()
    protector.config.min_reserve_gb = 1.0
    
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.ALLOW
