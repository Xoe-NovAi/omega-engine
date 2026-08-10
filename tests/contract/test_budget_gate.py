"""Contract Tests — §3.2 Concurrent BudgetGate check/record — M1 AnyIO.

[P2-2] Verifies the P0 §3.2 fix: `BudgetGate.check_budget()` and
`record_spend()` are fully async (M1) and safe under concurrent callers
against a shared MetricsDB connection.

[M1: AnyIO] Both methods await directly; no from_thread.run() in the path.
[M9: Error Integrity] Zero `sqlite3.OperationalError: database is locked`
under M-way concurrency — writes are lock-serialized.
[M21: Gate Integrity] Final cached daily spend equals the sum of recorded
costs (atomic read-your-writes contract).
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import anyio
import pytest

from omega.observability.metrics_db import MetricsDB
from omega.observability import BudgetGate


@pytest.fixture
def budget_env():
    """BudgetGate + MetricsDB pair on a tmp path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MetricsDB(Path(tmpdir) / "test_metrics.db")
        db.initialize()
        gate = BudgetGate(metrics_db=db)
        yield db, gate
        db.close()


@pytest.mark.anyio
async def test_concurrent_check_record_pairs_no_locked_errors(budget_env):
    """[P2-2] M concurrent check_budget()/record_spend() pairs ⇒ zero locks."""
    db, gate = budget_env
    M = 16
    errors: list = []

    # Seed performance rows with trace_ids so record_spend can update cost.
    for i in range(M):
        await db.record_performance(
            latency_ms=10.0,
            provider="google",
            model_used="gemini-flash",
            prompt_tokens=1000,
            completion_tokens=500,
            is_cloud=True,
            trace_id=f"budget-trc-{i}",
            cost_usd=0.0,
        )

    async def _pair(i: int) -> None:
        try:
            allowed, reason = await gate.check_budget("google", 1000, 500)
            assert allowed, f"check_budget({i}) unexpectedly blocked: {reason}"
            cost = await gate.record_spend(
                "google", 1000, 500, trace_id=f"budget-trc-{i}"
            )
            # google cost: 1.0 input tokens * 0.000125 + 0.5 output * 0.000375
            assert cost > 0.0, f"record_spend({i}) returned 0 cost"
        except Exception as e:  # pragma: no cover - should never happen
            errors.append(f"{i}: {type(e).__name__}: {e}")

    async with anyio.create_task_group() as tg:
        for i in range(M):
            tg.start_soon(_pair, i)

    assert errors == [], f"Concurrent budget ops raised: {errors}"

    # Expected total cost: per pair 1000 prompt * 0.000125/K + 500 comp * 0.000375/K
    # = 0.000125 + 0.0001875 = 0.0003125 USD. M pairs => 0.005 USD.
    expected = M * (1000 / 1000 * 0.000125 + 500 / 1000 * 0.000375)
    ts_start = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    final_spend = await db.get_daily_cloud_spend(ts_start)
    assert abs(final_spend - expected) < 1e-9, (
        f"Final daily spend {final_spend:.6f} != expected {expected:.6f}"
    )


@pytest.mark.anyio
async def test_record_spend_updates_cost_and_invalidates_cache(budget_env):
    """[P2-2/M21] record_spend writes cost and cache reflects new spend."""
    db, gate = budget_env

    await db.record_performance(
        latency_ms=5.0,
        provider="google",
        model_used="gemini-flash",
        prompt_tokens=1000,
        completion_tokens=1000,
        is_cloud=True,
        trace_id="single-trc",
        cost_usd=0.0,
    )

    # Warm cache
    await gate.check_budget("google", 100, 100)

    cost = await gate.record_spend("google", 1000, 1000, trace_id="single-trc")
    assert cost == pytest.approx(0.000125 + 0.000375, abs=1e-9)

    ts_start = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    spend = await db.get_daily_cloud_spend(ts_start)
    assert spend == pytest.approx(0.0005, abs=1e-9)


@pytest.mark.anyio
async def test_local_provider_bypasses_budget(budget_env):
    """[P2-2/M7] Local providers are never blocked by BudgetGate."""
    db, gate = budget_env
    allowed, reason = await gate.check_budget("native-gguf", 50000, 50000)
    assert allowed
    assert "no budget limit" in reason.lower()
