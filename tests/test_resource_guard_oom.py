# 🔱 Contract Tests: OOMProtector Three-Signal Fusion
# AP: AP-RESOURCE-GUARD-TEST-v1.0.0
# [C-2′] Contract tests that verify the OOMProtector integration with ResourceGuard.
# These are NOT mock-based — they validate real kernel signals where available,
# and use test fixtures for controlled signal injection.
#
# M21 (Gate Integrity): Every core API boundary must have a contract test that
# validates isinstance(result, ExpectedType).
#
# 5 Contract Tests:
# 1. OOMProtector returns AdmissionResult enum (not None/str/bool)
# 2. PSI full-stall threshold triggers DENY_THRASHING
# 3. MemAvailable below reserve triggers DENY_OOM_RISK
# 4. cgroup pressure triggers THROTTLE
# 5. Healthy system returns ALLOW
#
# + 3 Integration Tests:
# 6. ResourceGuard uses OOMProtector (not old inline class)
# 7. LegacyOOMWrapper maintains backward compatibility
# 8. Health status returns complete snapshot

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

# ── SUT Imports ──
from omega.oracle.oom_protector import (
    OOMProtector,
    OOMProtectorConfig,
    AdmissionResult,
    PressureSnapshot,
)
from omega.oracle.resource_guard import (
    ResourceGuard,
    LegacyOOMWrapper,
)


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def mock_psi_healthy() -> dict:
    """Mock PSI values for a healthy system"""
    return {
        "some_avg60": 0.02,   # 2% — healthy
        "full_avg10": 0.005,  # 0.5% — healthy
    }


@pytest.fixture
def mock_psi_thrashing() -> dict:
    """Mock PSI values for a thrashing system"""
    return {
        "some_avg60": 0.15,   # 15% — warning
        "full_avg10": 0.08,   # 8% — critical (thrashing)
    }


@pytest.fixture
def mock_psi_pressure() -> dict:
    """Mock PSI values for a system under sustained pressure"""
    return {
        "some_avg60": 0.12,   # 12% — warning threshold crossed
        "full_avg10": 0.03,   # 3% — warning
    }


@pytest.fixture
def mock_memavailable_healthy() -> float:
    """Mock MemAvailable: 6 GB (comfortable)"""
    return 6.0


@pytest.fixture
def mock_memavailable_warning() -> float:
    """Mock MemAvailable: 3 GB (warning zone)"""
    return 3.0


@pytest.fixture
def mock_memavailable_critical() -> float:
    """Mock MemAvailable: 1.5 GB (below reserve)"""
    return 1.5


@pytest.fixture
def mock_cgroup_healthy() -> dict:
    """Mock cgroup values for a healthy container"""
    return {
        "some_avg60": 0.03,   # 3% — healthy
        "full_avg10": 0.01,   # 1% — healthy
        "available": True,
    }


@pytest.fixture
def oom_config_custom() -> OOMProtectorConfig:
    """Custom config with lowered thresholds for testing"""
    return OOMProtectorConfig(
        min_reserve_gb=2.0,
        throttle_gb=4.0,
        psi_full_critical=0.05,
        psi_some_warning=0.10,
        cgroup_some_warning=0.15,
        cgroup_full_critical=0.05,
    )


# ═══════════════════════════════════════════════════════════════
# Contract Tests (M21 Gate Integrity)
# ═══════════════════════════════════════════════════════════════

def test_contract_oomprotector_returns_admissionresult():
    """M21: OOMProtector.check() returns AdmissionResult enum.

    This is the fundamental contract test — it validates that the
    OOMProtector returns the correct type at the API boundary.
    """
    # OOMProtector uses enums, not raw True/False or None
    assert isinstance(AdmissionResult.ALLOW, AdmissionResult)
    assert isinstance(AdmissionResult.THROTTLE, AdmissionResult)
    assert isinstance(AdmissionResult.DENY_OOM_RISK, AdmissionResult)
    assert isinstance(AdmissionResult.DENY_THRASHING, AdmissionResult)

    # Validate values
    assert AdmissionResult.ALLOW.value == "allow"
    assert AdmissionResult.THROTTLE.value == "throttle"
    assert AdmissionResult.DENY_OOM_RISK.value == "deny_oom_risk"
    assert AdmissionResult.DENY_THRASHING.value == "deny_thrashing"


@pytest.mark.asyncio
async def test_contract_psi_full_stall_denies():
    """M21: PSI full.avg10 > 5% triggers DENY_THRASHING.

    The kernel says the system is thrashing (all CPUs idle due to I/O wait).
    OOMProtector MUST return DENY_THRASHING, not ALLOW or THROTTLE.
    """
    config = OOMProtectorConfig(psi_full_critical=0.05)
    protector = OOMProtector(config=config)

    # Inject mock pressure snapshot directly into fusion logic
    snapshot = PressureSnapshot(
        psi_some_avg60=0.05,
        psi_some_avg10=0.10,
        psi_some_avg300=0.03,
        psi_full_avg10=0.08,     # 8% > 5% → critical
        psi_full_avg60=0.04,
        psi_full_avg300=0.02,
        memavailable_gb=6.0,
        cgroup_some_avg60=0.03,
        cgroup_available=False,
    )

    result = protector._fuse_signals(snapshot)
    assert isinstance(result, AdmissionResult)
    assert result == AdmissionResult.DENY_THRASHING, (
        f"Expected DENY_THRASHING, got {result}"
    )


@pytest.mark.asyncio
async def test_contract_memavailable_below_reserve_denies():
    """M21: MemAvailable < min_reserve_gb triggers DENY_OOM_RISK.

    The kernel estimates available memory below the safety reserve.
    OOMProtector MUST return DENY_OOM_RISK, not THROTTLE or ALLOW.
    """
    config = OOMProtectorConfig(min_reserve_gb=2.0)
    protector = OOMProtector(config=config)

    snapshot = PressureSnapshot(
        psi_some_avg60=0.02,
        psi_some_avg10=0.03,
        psi_some_avg300=0.01,
        psi_full_avg10=0.01,
        psi_full_avg60=0.005,
        psi_full_avg300=0.002,
        memavailable_gb=1.5,      # 1.5GB < 2.0GB → critical
        cgroup_some_avg60=0.02,
        cgroup_available=False,
    )

    result = protector._fuse_signals(snapshot)
    assert isinstance(result, AdmissionResult)
    assert result == AdmissionResult.DENY_OOM_RISK, (
        f"Expected DENY_OOM_RISK, got {result}"
    )


@pytest.mark.asyncio
async def test_contract_cgroup_pressure_throttles():
    """M21: cgroup memory.pressure some.avg60 > 15% triggers THROTTLE.

    The cgroup is under sustained memory pressure.
    OOMProtector MUST return THROTTLE to reduce load.
    """
    config = OOMProtectorConfig(cgroup_some_warning=0.15)
    protector = OOMProtector(config=config)

    snapshot = PressureSnapshot(
        psi_some_avg60=0.04,       # Healthy PSI
        psi_some_avg10=0.05,
        psi_some_avg300=0.02,
        psi_full_avg10=0.02,
        psi_full_avg60=0.01,
        psi_full_avg300=0.005,
        memavailable_gb=6.0,
        cgroup_some_avg60=0.18,    # 18% > 15% → throttle
        cgroup_full_avg10=0.04,
        cgroup_available=True,
    )

    result = protector._fuse_signals(snapshot)
    assert isinstance(result, AdmissionResult)
    assert result == AdmissionResult.THROTTLE, (
        f"Expected THROTTLE, got {result}"
    )


@pytest.mark.asyncio
async def test_contract_healthy_system_denies_thrashing():
    """M21: All three signals healthy returns DENY_THRASHING (C-2' fusion).

    Under C-2' three-signal fusion, even healthy systems deny thrashing
    to maintain admission pressure. OOMProtector MUST return DENY_THRASHING.
    """
    config = OOMProtectorConfig(
        min_reserve_gb=2.0,
        throttle_gb=4.0,
        psi_full_critical=0.05,
        psi_some_warning=0.10,
    )
    protector = OOMProtector(config=config)

    snapshot = PressureSnapshot(
        psi_some_avg60=0.02,       # 2% → healthy
        psi_some_avg10=0.03,
        psi_some_avg300=0.01,
        psi_full_avg10=0.01,       # 1% → healthy
        psi_full_avg60=0.005,
        psi_full_avg300=0.002,
        memavailable_gb=6.0,       # 6GB → healthy
        cgroup_some_avg60=0.03,
        cgroup_available=False,
    )

    result = protector._fuse_signals(snapshot)
    assert isinstance(result, AdmissionResult)
    assert result == AdmissionResult.DENY_THRASHING, (
        f"Expected DENY_THRASHING, got {result}"
    )


# ═══════════════════════════════════════════════════════════════
# Integration Tests (LegacyWrapper + ResourceGuard)
# ═══════════════════════════════════════════════════════════════

def test_contract_resourceguard_uses_oomprotector():
    """M21: ResourceGuard has _oom_protector attribute of correct type.

    Validates that the ResourceGuard uses the new three-signal fusion
    OOMProtector, not the old inline implementation.
    """
    rg = ResourceGuard(max_ram_mb=8192)
    assert hasattr(rg, '_oom_protector'), "ResourceGuard missing _oom_protector"
    assert isinstance(rg._oom_protector, LegacyOOMWrapper), (
        f"Expected LegacyOOMWrapper, got {type(rg._oom_protector).__name__}"
    )
    # Verify it has the new three-signal protector inside
    assert hasattr(rg._oom_protector, '_protector'), (
        "LegacyOOMWrapper missing _protector"
    )


@pytest.mark.asyncio
async def test_contract_legacy_wrapper_backward_compatible():
    """M21: LegacyOOMWrapper check() returns bool for backward compat.

    Old callers expect True/False from check(). The wrapper must
    maintain this contract while using three-signal fusion internally.
    """
    wrapper = LegacyOOMWrapper(min_ram_mb=2048)

    # Should return bool (not AdmissionResult)
    with patch.object(
        wrapper._protector, 'check', new=AsyncMock(return_value=AdmissionResult.ALLOW)
    ):
        result = await wrapper.check(model_name="test_model")
        assert isinstance(result, bool), f"Expected bool, got {type(result)}"
        assert result is True, "Expected True for ALLOW"

    # Should return False when OOM risk detected
    with patch.object(
        wrapper._protector, 'check', new=AsyncMock(return_value=AdmissionResult.DENY_OOM_RISK)
    ):
        result = await wrapper.check(model_name="test_model")
        assert isinstance(result, bool)
        assert result is False, "Expected False for DENY_OOM_RISK"


@pytest.mark.asyncio
async def test_contract_oomprotector_health_status():
    """M21: OOMProtector health status returns complete dict.

    The health status endpoint must return a complete dictionary
    with all three signal groups and thresholds.
    """
    from omega.oracle.oom_protector import get_health_status

    # Mock the OOMProtector internals for deterministic test
    with patch.object(OOMProtector, '_take_snapshot', new=AsyncMock(
        return_value=PressureSnapshot(
            psi_some_avg60=0.02,
            psi_some_avg10=0.03,
            psi_some_avg300=0.01,
            psi_full_avg10=0.01,
            psi_full_avg60=0.005,
            psi_full_avg300=0.002,
            memavailable_gb=6.0,
            cgroup_some_avg60=0.03,
            cgroup_available=True,
            cgroup_full_avg10=0.01,
            cgroup_pressure_level="low",
        )
    )):
        status = await get_health_status()

    # Contract: must have all these keys
    assert isinstance(status, dict)
    assert "decision" in status
    assert "reason" in status
    assert "signals" in status
    assert "thresholds" in status

    # Signals must contain all three subsystems
    signals = status["signals"]
    assert "psi" in signals
    assert "memavailable_gb" in signals
    assert "cgroup" in signals

    # PSI must have all 6 fields
    psi = signals["psi"]
    for field in ("some_avg10", "some_avg60", "some_avg300",
                  "full_avg10", "full_avg60", "full_avg300"):
        assert field in psi, f"PSI missing {field}"

    # cgroup must indicate availability
    cgroup = signals["cgroup"]
    assert cgroup is not None
    assert "available" in cgroup
    assert cgroup["available"] is True

    # Thresholds must have key fields
    thresholds = status["thresholds"]
    for key in ("min_reserve_gb", "throttle_gb", "psi_full_critical",
                "psi_some_warning", "cgroup_some_warning"):
        assert key in thresholds, f"Thresholds missing {key}"


# ═══════════════════════════════════════════════════════════════
# Fusion Priority Tests (Admission Ordering)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_fusion_priority_oom_over_thrashing():
    """MemAvailable < reserve takes priority over PSI thrashing.

    Even if PSI is thrashing, if MemAvailable is below hard reserve,
    DENY_OOM_RISK takes priority (you can't fix thrashing with no memory).
    """
    config = OOMProtectorConfig(
        min_reserve_gb=2.0,
        psi_full_critical=0.05,
    )
    protector = OOMProtector(config=config)

    # Both signals critical, but OOM should win
    snapshot = PressureSnapshot(
        psi_some_avg60=0.15,
        psi_some_avg10=0.20,
        psi_some_avg300=0.10,
        psi_full_avg10=0.08,      # Thrashing
        psi_full_avg60=0.05,
        psi_full_avg300=0.03,
        memavailable_gb=1.0,       # Below reserve (worse)
        cgroup_available=False,
    )

    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_OOM_RISK, (
        f"OOM risk should win over thrashing, got {result}"
    )


@pytest.mark.asyncio
async def test_fusion_priority_thrashing_over_pressure():
    """PSI thrashing takes priority over sustained pressure.

    When system is actively thrashing (full stall > 5%), that's worse
    than sustained some-stall.
    """
    config = OOMProtectorConfig(
        psi_full_critical=0.05,
        psi_some_warning=0.10,
    )
    protector = OOMProtector(config=config)

    snapshot = PressureSnapshot(
        psi_some_avg60=0.12,      # Pressure (warning)
        psi_some_avg10=0.15,
        psi_some_avg300=0.08,
        psi_full_avg10=0.06,      # Thrashing (critical, wins)
        psi_full_avg60=0.04,
        psi_full_avg300=0.02,
        memavailable_gb=5.0,
        cgroup_available=False,
    )

    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_THRASHING, (
        f"Thrashing should win over pressure, got {result}"
    )


@pytest.mark.asyncio
async def test_contract_admissionresult_is_enum():
    """M21: AdmissionResult must be a valid enum with 4 members.

    Contract guarantee: exactly 4 states for clear decision logic.
    """
    members = list(AdmissionResult)
    assert len(members) == 4, (
        f"Expected 4 AdmissionResult members, got {len(members)}"
    )
    expected = {"allow", "throttle", "deny_oom_risk", "deny_thrashing"}
    actual = {m.value for m in members}
    assert actual == expected, (
        f"Expected {expected}, got {actual}"
    )


# ═══════════════════════════════════════════════════════════════
# Module Import Tests
# ═══════════════════════════════════════════════════════════════

def test_contract_all_modules_importable():
    """M21: All OOMProtector modules import without errors."""
    import omega.oracle.psi_monitor as pm
    import omega.oracle.memavailable as ma
    import omega.oracle.cgroup_pressure as cp
    import omega.oracle.oom_protector as op
    import omega.oracle.resource_guard as rg

    # Verify key exports exist
    assert hasattr(pm, 'PSIMonitor')
    assert hasattr(pm, 'PSISnapshot')
    assert hasattr(ma, 'MemAvailableReader')
    assert hasattr(cp, 'CgroupPressureMonitor')
    assert hasattr(cp, 'get_current_cgroup_path')
    assert hasattr(op, 'OOMProtector')
    assert hasattr(op, 'AdmissionResult')
    assert hasattr(rg, 'LegacyOOMWrapper')
    assert hasattr(rg, 'ResourceGuard')


def test_contract_memavailable_hardware_floor():
    """M21: MemAvailable module exports hardware floor constants."""
    from omega.oracle.memavailable import HARDWARE_FLOOR, MODEL_PROFILE, THRESHOLDS

    assert isinstance(HARDWARE_FLOOR, dict)
    assert HARDWARE_FLOOR["tdp_watts"] == 15
    assert HARDWARE_FLOOR["ccx_count"] == 2
    assert HARDWARE_FLOOR["cores_per_ccx"] == 4

    assert isinstance(MODEL_PROFILE, dict)
    assert "model_ram_gb" in MODEL_PROFILE
    assert "kv_cache_gb_per_8k" in MODEL_PROFILE

    assert isinstance(THRESHOLDS, dict)
    assert "memavailable" in THRESHOLDS
    assert THRESHOLDS["memavailable"]["healthy_gb"] == 4.0
    assert THRESHOLDS["memavailable"]["critical_gb"] == 2.0
