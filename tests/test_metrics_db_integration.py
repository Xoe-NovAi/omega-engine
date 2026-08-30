# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for MetricsDB wiring into ObservabilityEngine.
AP: AP-METRICS-DB-INTEGRATION-TESTS-v1.0.0

Tests verify that MetricsDB receives data from the main systems:
- ObservabilityEngine.log_event() → events table
- ObservabilityEngine.record_performance() → performance table
- ObservabilityEngine.record_metrics_error() → errors table
- ObservabilityEngine.record_breaker_transition() → breaker_transitions table
- ObservabilityEngine.stats() includes metrics_db section
"""

import tempfile
from pathlib import Path

import pytest

from omega.observability.metrics_db import MetricsDB
from omega.observability import ObservabilityEngine


@pytest.fixture
def temp_metrics_db():
    """Create a temporary MetricsDB instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_metrics.db"
        db = MetricsDB(db_path)
        db.initialize()
        yield db
        db.close()


@pytest.fixture
def obs_engine(temp_metrics_db: MetricsDB):
    """Create an ObservabilityEngine with injected MetricsDB."""
    engine = ObservabilityEngine(enable_dataset_collection=False, metrics_db=temp_metrics_db)
    yield engine


class TestObservabilityEngineMetricsDBWiring:
    """Verify ObservabilityEngine records to MetricsDB."""

    async def test_log_event_writes_to_metrics_db(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """log_event() should write to events table."""
        await obs_engine.log_event(
            event_type="test_event",
            trace_id="test-trace-001",
            data={"provider": "test-provider", "entity": "test-entity", "model": "test-model"},
        )
        cursor = temp_metrics_db._conn.execute(
            "SELECT COUNT(*) FROM events WHERE trace_id = ?", ("test-trace-001",)
        )
        count = cursor.fetchone()[0]
        assert count >= 1

    async def test_record_performance_writes_to_metrics_db(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """record_performance() should write to performance table."""
        await obs_engine.record_performance(
            latency_ms=123.45,
            provider="test-provider",
            model_used="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            is_cloud=False,
        )
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM performance")
        count = cursor.fetchone()[0]
        assert count >= 1

        # Verify data is correct
        cursor = temp_metrics_db._conn.execute(
            "SELECT latency_ms, provider, model_used, prompt_tokens, completion_tokens, is_cloud FROM performance ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        assert row[0] == 123.45
        assert row[1] == "test-provider"
        assert row[2] == "test-model"
        assert row[3] == 100
        assert row[4] == 50
        assert row[5] == 0

    async def test_record_metrics_error_writes_to_metrics_db(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """record_metrics_error() should write to errors table."""
        await obs_engine.record_metrics_error(
            error_type="test_error",
            error_message="Something went wrong",
            provider="test-provider",
            trace_id="test-trace-002",
            context={"detail": "test context"},
        )
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM errors")
        count = cursor.fetchone()[0]
        assert count >= 1

        # Verify data is correct
        cursor = temp_metrics_db._conn.execute(
            "SELECT error_type, error_message, provider, trace_id FROM errors ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        assert row[0] == "test_error"
        assert row[1] == "Something went wrong"
        assert row[2] == "test-provider"
        assert row[3] == "test-trace-002"

    async def test_record_breaker_transition_writes_to_metrics_db(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """record_breaker_transition() should write to breaker_transitions table."""
        await obs_engine.record_breaker_transition(
            provider="test-provider",
            from_state="CLOSED",
            to_state="OPEN",
            reason="Too many failures",
            trace_id="test-trace-003",
        )
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM breaker_transitions")
        count = cursor.fetchone()[0]
        assert count >= 1

        # Verify data is correct
        cursor = temp_metrics_db._conn.execute(
            "SELECT provider, from_state, to_state, reason FROM breaker_transitions ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        assert row[0] == "test-provider"
        assert row[1] == "CLOSED"
        assert row[2] == "OPEN"
        assert row[3] == "Too many failures"

    async def test_stats_includes_metrics_db_section(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """stats() should include metrics_db section."""
        # Add some data first
        await obs_engine.record_performance(latency_ms=100.0, provider="test")
        stats = await obs_engine.stats()
        assert "metrics_db" in stats
        assert "events_count" in stats["metrics_db"]
        assert "errors_count" in stats["metrics_db"]
        assert "performance_count" in stats["metrics_db"]

    async def test_record_performance_is_cloud_true(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """record_performance() with is_cloud=True."""
        await obs_engine.record_performance(latency_ms=50.0, is_cloud=True)
        cursor = temp_metrics_db._conn.execute("SELECT is_cloud FROM performance ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == 1  # True = 1

    async def test_record_performance_is_cloud_false(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """record_performance() with is_cloud=False."""
        await obs_engine.record_performance(latency_ms=60.0, is_cloud=False)
        cursor = temp_metrics_db._conn.execute("SELECT is_cloud FROM performance ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row[0] == 0  # False = 0


class TestMetricsDBGracefulDegradation:
    """Verify systems degrade gracefully when MetricsDB is unavailable."""

    async def test_obs_engine_without_metrics_db(self):
        """ObservabilityEngine should work without MetricsDB."""
        engine = ObservabilityEngine(enable_dataset_collection=False, metrics_db=None)
        # Should not raise
        engine.log_event(
            event_type="test",
            trace_id="test-trace-004",
            data={"test": True},
        )
        await engine.record_performance(latency_ms=100.0)
        await engine.record_metrics_error(error_type="test", error_message="test msg")

    def test_stats_without_metrics_db(self):
        """stats() should report metrics_db as not_initialized when None."""
        engine = ObservabilityEngine(enable_dataset_collection=False, metrics_db=None)
        stats = engine.stats_sync()
        assert stats["metrics_db"]["status"] == "not_initialized"


class TestMetricsDBMultipleEvents:
    """Verify multiple events can be recorded and queried."""

    async def test_multiple_performance_records(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """Multiple performance records should all be stored."""
        for i in range(5):
            await obs_engine.record_performance(latency_ms=float(i * 100), provider=f"provider-{i}")
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM performance")
        count = cursor.fetchone()[0]
        assert count >= 5

    async def test_multiple_error_records(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """Multiple error records should all be stored."""
        for i in range(3):
            await obs_engine.record_metrics_error(error_type=f"error_{i}", error_message=f"msg_{i}")
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM errors")
        count = cursor.fetchone()[0]
        assert count >= 3

    async def test_multiple_breaker_transitions(self, obs_engine: ObservabilityEngine, temp_metrics_db: MetricsDB):
        """Multiple breaker transitions should all be stored."""
        await obs_engine.record_breaker_transition(provider="p1", from_state="CLOSED", to_state="OPEN")
        await obs_engine.record_breaker_transition(provider="p1", from_state="OPEN", to_state="HALF_OPEN")
        await obs_engine.record_breaker_transition(provider="p1", from_state="HALF_OPEN", to_state="CLOSED")
        cursor = temp_metrics_db._conn.execute("SELECT COUNT(*) FROM breaker_transitions WHERE provider = 'p1'")
        count = cursor.fetchone()[0]
        assert count >= 3
