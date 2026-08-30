# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# File: tests/property/test_oom_protector_fuse.py
# Purpose: Property-based tests for OOMProtector._fuse_signals() (sync logic)
# Dependencies: hypothesis, pytest, omega.oracle.oom_protector
#
# Strategy: Test _fuse_signals() directly with crafted PressureSnapshot objects.
# This avoids mocking kernel files — _fuse_signals() is pure logic, no I/O.
# Verified: OOMProtectorConfig thresholds are documented in oom_protector.py

import pytest
from hypothesis import given, settings, HealthCheck, strategies as st
from omega.oracle.oom_protector import (
    OOMProtector,
    OOMProtectorConfig,
    PressureSnapshot,
    AdmissionResult,
)


def _make_snapshot(
    memavailable_gb: float,
    psi_some_avg60: float,
    psi_full_avg10: float,
    cgroup_some_avg60: float | None = None,
    cgroup_full_avg10: float | None = None,
) -> PressureSnapshot:
    """Craft a PressureSnapshot for testing _fuse_signals()."""
    return PressureSnapshot(
        psi_some_avg10=psi_some_avg60 * 0.8,  # avg10 < avg60 usually
        psi_some_avg60=psi_some_avg60,
        psi_some_avg300=psi_some_avg60 * 0.9,
        psi_full_avg10=psi_full_avg10,
        psi_full_avg60=psi_full_avg10 * 0.5,
        psi_full_avg300=psi_full_avg10 * 0.3,
        memavailable_gb=memavailable_gb,
        cgroup_some_avg60=cgroup_some_avg60,
        cgroup_full_avg10=cgroup_full_avg10,
        cgroup_available=(cgroup_some_avg60 is not None),
    )


# ── Property 1: Fusion result is always a valid AdmissionResult ────────

@given(
    mem_gb=st.floats(min_value=0.0, max_value=16.0, allow_nan=False),
    psi_some=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    psi_full=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=500, derandomize=True, suppress_health_check=[HealthCheck.too_slow])
def test_fuse_result_always_valid(mem_gb, psi_some, psi_full):
    """_fuse_signals() must always return a valid AdmissionResult enum value."""
    config = OOMProtectorConfig(min_reserve_gb=2.0, throttle_gb=4.0)
    protector = OOMProtector(config=config)
    snapshot = _make_snapshot(memavailable_gb=mem_gb, psi_some_avg60=psi_some, psi_full_avg10=psi_full)
    result = protector._fuse_signals(snapshot)
    assert isinstance(result, AdmissionResult), f"Invalid result type: {type(result)}"
    assert result in AdmissionResult, f"Invalid AdmissionResult: {result}"


# ── Property 2: Low memory → DENY_OOM_RISK (hard floor) ───────────────

@given(
    mem_gb=st.floats(min_value=0.0, max_value=1.99, allow_nan=False),
)
@settings(max_examples=200, derandomize=True)
def test_low_memory_deny_oom(mem_gb):
    """MemAvailable < min_reserve_gb(2.0) → DENY_OOM_RISK regardless of PSI."""
    config = OOMProtectorConfig(min_reserve_gb=2.0)
    protector = OOMProtector(config=config)
    snapshot = _make_snapshot(memavailable_gb=mem_gb, psi_some_avg60=0.0, psi_full_avg10=0.0)
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_OOM_RISK, (
        f"mem={mem_gb}GB < 2.0GB should DENY_OOM_RISK, got {result}"
    )


# ── Property 3: High PSI full → DENY_THRASHING ─────────────────────────

@given(
    psi_full=st.floats(min_value=0.06, max_value=1.0, allow_nan=False),
)
@settings(max_examples=200, derandomize=True)
def test_high_psi_full_deny_thrashing(psi_full):
    """PSI full.avg10 > 5% → DENY_THRASHING when memory is adequate."""
    config = OOMProtectorConfig(min_reserve_gb=2.0)
    protector = OOMProtector(config=config)
    snapshot = _make_snapshot(memavailable_gb=8.0, psi_some_avg60=0.0, psi_full_avg10=psi_full)
    result = protector._fuse_signals(snapshot)
    assert result == AdmissionResult.DENY_THRASHING, (
        f"psi_full={psi_full} > 5% should DENY_THRASHING, got {result}"
    )


# ── Property 4: Low PSI + healthy memory → ALLOW or THROTTLE ──────────

@given(
    mem_gb=st.floats(min_value=4.0, max_value=16.0, allow_nan=False),
    psi_some=st.floats(min_value=0.0, max_value=0.09, allow_nan=False),
    psi_full=st.floats(min_value=0.0, max_value=0.04, allow_nan=False),
)
@settings(max_examples=200, derandomize=True)
def test_healthy_signals_allow_or_throttle(mem_gb, psi_some, psi_full):
    """Healthy signals with adequate memory → ALLOW (never DENY_*)"""
    config = OOMProtectorConfig(min_reserve_gb=2.0, throttle_gb=4.0)
    protector = OOMProtector(config=config)
    snapshot = _make_snapshot(memavailable_gb=mem_gb, psi_some_avg60=psi_some, psi_full_avg10=psi_full)
    result = protector._fuse_signals(snapshot)
    assert result in (AdmissionResult.ALLOW, AdmissionResult.THROTTLE), (
        f"Healthy signals should ALLOW or THROTTLE, got {result}"
    )
    assert result != AdmissionResult.DENY_OOM_RISK, "Healthy memory should not DENY_OOM_RISK"
    assert result != AdmissionResult.DENY_THRASHING, "Low PSI should not DENY_THRASHING"


# ── Property 5: Priority order — OOM risk > thrashing > throttle > allow ─

@given(
    mem_gb=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    psi_full=st.floats(min_value=0.10, max_value=1.0, allow_nan=False),
)
@settings(max_examples=100, derandomize=True)
def test_priority_oom_over_thrashing(mem_gb, psi_full):
    """When both OOM risk and thrashing present, DENY_OOM_RISK takes priority."""
    config = OOMProtectorConfig(min_reserve_gb=2.0)
    protector = OOMProtector(config=config)
    snapshot = _make_snapshot(memavailable_gb=mem_gb, psi_some_avg60=0.5, psi_full_avg10=psi_full)
    result = protector._fuse_signals(snapshot)
    # OOM risk (mem < 2.0) should beat thrashing (psi_full > 5%)
    assert result == AdmissionResult.DENY_OOM_RISK, (
        f"OOM risk should have priority: mem={mem_gb}, psi_full={psi_full}, got {result}"
    )