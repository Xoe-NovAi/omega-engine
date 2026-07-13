"""M21 Contract tests for the Sovereignty Gate (P0-2).
**AP Token**: `AP-KALI-TEST-GATE-20260712`
[Gate Integrity] The gate's `check()` / `check_strict()` MUST return bool.
A missing/empty MetricsDB is not an error: `check()` passes (nothing to gate),
`check_strict()` fails (no inference was recorded — a sovereignty gap in prod CI).
"""
from omega.governance.sovereignty_gate import SovereigntyGate


def test_sovereignty_gate_instantiation():
    g = SovereigntyGate()
    assert g.min_local_ratio == 0.80


def test_sovereignty_gate_check_returns_bool():
    g = SovereigntyGate()
    result = g.check("data/observability/metrics_does_not_exist.db")
    assert isinstance(result, bool)
    # Missing DB => nothing to gate => passes.
    assert result is True


def test_sovereignty_gate_check_strict_returns_bool():
    g = SovereigntyGate()
    result = g.check_strict("data/observability/metrics_does_not_exist.db")
    assert isinstance(result, bool)
    # Strict mode fails when no inference was recorded.
    assert result is False


def test_sovereignty_gate_min_local_ratio_override():
    g = SovereigntyGate(min_local_ratio=0.50)
    assert g.min_local_ratio == 0.50
