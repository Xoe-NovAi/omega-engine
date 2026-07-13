"""M21 Contract tests for the Sovereign Vetter (P0-3).
**AP Token**: `AP-KALI-TEST-VETTER-20260712`
[Gate Integrity] Every public API boundary must have a contract test that
validates the return type via isinstance(). The vetter's `vet()` MUST return a
VettingResult, and any mandate in `failed_mandates` MUST be a CRITICAL mandate
(D221: advisory mandates are logged, never block).
"""
import anyio
from dataclasses import is_dataclass

from omega.governance.sovereign_vetter import SovereignVetter, VettingResult


def test_vetting_result_is_dataclass():
    assert is_dataclass(VettingResult)
    r = VettingResult(passed=True)
    assert r.passed is True
    assert isinstance(r.details, dict)


def test_sovereign_vetter_critical_mandates_whitelist():
    assert isinstance(SovereignVetter.CRITICAL_MANDATES, frozenset)
    assert {"M1", "M7", "M8", "M9", "M23"}.issubset(SovereignVetter.CRITICAL_MANDATES)


def test_vet_returns_vetting_result():
    async def run():
        return await SovereignVetter().vet(force=True)
    r = anyio.run(run)
    assert isinstance(r, VettingResult)
    assert "failed_mandates" in r.details
    assert "advisory_failed" in r.details
    assert "per_mandate" in r.details


def test_vet_does_not_self_flag():
    """D221: the vetter must never flag its own source (M9 docstring, M16 regex)."""
    async def run():
        return await SovereignVetter().vet(force=True)
    r = anyio.run(run)
    assert "M9" not in r.details["failed_mandates"], (
        f"M9 self-flag: {r.details['per_mandate'].get('M9')}"
    )
    assert "M16" not in r.details["failed_mandates"], (
        f"M16 self-flag: {r.details['per_mandate'].get('M16')}"
    )


def test_vet_failed_mandates_are_critical_only():
    """Any mandate in failed_mandates must be in CRITICAL_MANDATES (D221)."""
    async def run():
        return await SovereignVetter().vet(force=True)
    r = anyio.run(run)
    for m in r.details["failed_mandates"]:
        assert m in SovereignVetter.CRITICAL_MANDATES, (
            f"Advisory mandate {m} must not hard-block (use advisory_failed)"
        )


def test_vet_advisory_failure_does_not_block():
    """Advisory failures are recorded but do not set passed=False (D221)."""
    async def run():
        return await SovereignVetter().vet(force=True)
    r = anyio.run(run)
    # If only advisory mandates failed, passed must remain True.
    if not r.details["failed_mandates"] and r.details["advisory_failed"]:
        assert r.passed is True
