"""Tests for MetricsDB — WAL-mode SQLite metrics store."""

import tempfile
from pathlib import Path

import pytest

from omega.observability.metrics_db import MetricsDB


@pytest.fixture
def metrics_db():
    """Create a temporary MetricsDB instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_metrics.db"
        db = MetricsDB(db_path)
        db.initialize()
        yield db
        db.close()


class TestMetricsDBInitialization:
    """Test database initialization and WAL mode."""

    def test_initialize_creates_database(self, metrics_db: MetricsDB):
        assert metrics_db.db_path.exists()

    def test_initialize_sets_wal_mode(self, metrics_db: MetricsDB):
        cursor = metrics_db._conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode == "wal"

    def test_initialize_creates_schema_version(self, metrics_db: MetricsDB):
        cursor = metrics_db._conn.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 1

    def test_initialize_creates_all_tables(self, metrics_db: MetricsDB):
        cursor = metrics_db._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        assert "events" in tables
        assert "errors" in tables
        assert "breaker_transitions" in tables
        assert "performance" in tables
        assert "baselines" in tables
        assert "schema_version" in tables


class TestEventRecording:
    """Test event recording."""

    def test_record_event(self, metrics_db: MetricsDB):
        metrics_db.record_event(
            event_type="inference_start",
            trace_id="trace-001",
            provider="native-gguf",
            payload={"model": "qwen3-1.7b"},
        )
        cursor = metrics_db._conn.execute("SELECT COUNT(*) FROM events")
        assert cursor.fetchone()[0] == 1

    def test_record_event_minimal(self, metrics_db: MetricsDB):
        metrics_db.record_event(event_type="test_event")
        cursor = metrics_db._conn.execute("SELECT event_type FROM events")
        assert cursor.fetchone()[0] == "test_event"


class TestErrorRecording:
    """Test error recording."""

    def test_record_error(self, metrics_db: MetricsDB):
        metrics_db.record_error(
            error_type="ProviderTimeout",
            error_message="Request timed out after 30s",
            trace_id="trace-002",
            provider="google",
            context={"timeout": 30},
        )
        cursor = metrics_db._conn.execute("SELECT COUNT(*) FROM errors")
        assert cursor.fetchone()[0] == 1

    def test_record_error_minimal(self, metrics_db: MetricsDB):
        metrics_db.record_error(
            error_type="TestError",
            error_message="test message",
        )
        cursor = metrics_db._conn.execute("SELECT error_type FROM errors")
        assert cursor.fetchone()[0] == "TestError"


class TestBreakerTransitions:
    """Test circuit breaker transition recording."""

    def test_record_breaker_transition(self, metrics_db: MetricsDB):
        metrics_db.record_breaker_transition(
            provider="ollama",
            from_state="CLOSED",
            to_state="OPEN",
            trace_id="trace-003",
            reason="3 consecutive failures",
        )
        cursor = metrics_db._conn.execute("SELECT COUNT(*) FROM breaker_transitions")
        assert cursor.fetchone()[0] == 1

    def test_breaker_transition_states(self, metrics_db: MetricsDB):
        metrics_db.record_breaker_transition(
            provider="ollama",
            from_state="CLOSED",
            to_state="OPEN",
        )
        metrics_db.record_breaker_transition(
            provider="ollama",
            from_state="OPEN",
            to_state="CLOSED",
            reason="recovery timeout",
        )
        cursor = metrics_db._conn.execute(
            "SELECT from_state, to_state FROM breaker_transitions ORDER BY ts"
        )
        rows = cursor.fetchall()
        assert len(rows) == 2
        assert rows[0][0] == "CLOSED"
        assert rows[0][1] == "OPEN"
        assert rows[1][0] == "OPEN"
        assert rows[1][1] == "CLOSED"


class TestPerformanceRecording:
    """Test performance measurement recording."""

    def test_record_performance(self, metrics_db: MetricsDB):
        metrics_db.record_performance(
            latency_ms=150.5,
            provider="native-gguf",
            model_used="qwen3-1.7b",
            prompt_tokens=100,
            completion_tokens=50,
            is_cloud=False,
            trace_id="trace-004",
        )
        cursor = metrics_db._conn.execute("SELECT COUNT(*) FROM performance")
        assert cursor.fetchone()[0] == 1

    def test_performance_total_tokens(self, metrics_db: MetricsDB):
        metrics_db.record_performance(
            latency_ms=200.0,
            prompt_tokens=100,
            completion_tokens=50,
        )
        cursor = metrics_db._conn.execute("SELECT total_tokens FROM performance")
        assert cursor.fetchone()[0] == 150

    def test_performance_is_cloud_integer(self, metrics_db: MetricsDB):
        metrics_db.record_performance(latency_ms=100.0, is_cloud=True)
        cursor = metrics_db._conn.execute("SELECT is_cloud FROM performance")
        assert cursor.fetchone()[0] == 1


class TestBaselineManagement:
    """Test baseline metric management."""

    def test_set_baseline(self, metrics_db: MetricsDB):
        metrics_db.set_baseline(
            metric_name="cold_start_latency",
            value=3500.0,
            sample_count=100,
            std_deviation=250.0,
            source="profiler",
        )
        baseline = metrics_db.get_baseline("cold_start_latency")
        assert baseline is not None
        assert baseline["metric_value"] == 3500.0
        assert baseline["sample_count"] == 100
        assert baseline["std_deviation"] == 250.0

    def test_set_baseline_update(self, metrics_db: MetricsDB):
        metrics_db.set_baseline("test_metric", 1.0, 10)
        metrics_db.set_baseline("test_metric", 2.0, 20)
        baseline = metrics_db.get_baseline("test_metric")
        assert baseline["metric_value"] == 2.0
        assert baseline["sample_count"] == 20

    def test_get_baseline_nonexistent(self, metrics_db: MetricsDB):
        baseline = metrics_db.get_baseline("nonexistent")
        assert baseline is None


class TestRegressionDetection:
    """Test regression detection logic."""

    def test_detect_regression_with_stddev(self, metrics_db: MetricsDB):
        metrics_db.set_baseline("latency", 100.0, 50, std_deviation=10.0)
        # Within 3 sigma (30.0) — no regression
        assert not metrics_db.detect_regression("latency", 120.0)
        # Outside 3 sigma — regression
        assert metrics_db.detect_regression("latency", 150.0)

    def test_detect_regression_percentage(self, metrics_db: MetricsDB):
        metrics_db.set_baseline("memory", 1000.0, 50, std_deviation=None)
        # Within 10% threshold
        assert not metrics_db.detect_regression("memory", 1050.0)
        # Outside 10% threshold
        assert metrics_db.detect_regression("memory", 1200.0)

    def test_detect_regression_no_baseline(self, metrics_db: MetricsDB):
        # No baseline — no regression detected
        assert not metrics_db.detect_regression("nonexistent", 100.0)

    def test_detect_regression_zero_baseline(self, metrics_db: MetricsDB):
        metrics_db.set_baseline("zero_metric", 0.0, 10)
        # Any positive value is a regression from zero
        assert metrics_db.detect_regression("zero_metric", 1.0)
        # Zero is not a regression
        assert not metrics_db.detect_regression("zero_metric", 0.0)


class TestQueryMethods:
    """Test query and reporting methods."""

    def test_get_performance_trend(self, metrics_db: MetricsDB):
        metrics_db.record_performance(latency_ms=100.0, provider="test")
        metrics_db.record_performance(latency_ms=200.0, provider="test")
        trend = metrics_db.get_performance_trend(provider="test", hours=1)
        assert len(trend) == 2

    def test_get_performance_trend_all_providers(self, metrics_db: MetricsDB):
        metrics_db.record_performance(latency_ms=100.0, provider="a")
        metrics_db.record_performance(latency_ms=200.0, provider="b")
        trend = metrics_db.get_performance_trend(hours=1)
        assert len(trend) == 2

    def test_get_error_summary(self, metrics_db: MetricsDB):
        metrics_db.record_error(error_type="Timeout", error_message="t1")
        metrics_db.record_error(error_type="Timeout", error_message="t2")
        metrics_db.record_error(error_type="Auth", error_message="a1")
        summary = metrics_db.get_error_summary(hours=1)
        assert summary["Timeout"] == 2
        assert summary["Auth"] == 1

    def test_get_breaker_history(self, metrics_db: MetricsDB):
        metrics_db.record_breaker_transition("p1", "CLOSED", "OPEN")
        metrics_db.record_breaker_transition("p1", "OPEN", "CLOSED")
        history = metrics_db.get_breaker_history(provider="p1")
        assert len(history) == 2

    def test_get_breaker_history_limit(self, metrics_db: MetricsDB):
        for i in range(10):
            metrics_db.record_breaker_transition("p1", "CLOSED", "OPEN")
        history = metrics_db.get_breaker_history(limit=5)
        assert len(history) == 5

    def test_get_stats(self, metrics_db: MetricsDB):
        metrics_db.record_event(event_type="test")
        metrics_db.record_error(error_type="test", error_message="test")
        stats = metrics_db.get_stats()
        assert stats["events_count"] == 1
        assert stats["errors_count"] == 1
        assert stats["db_size_bytes"] > 0


class TestCloseAndReopen:
    """Test database close and reopen."""

    def test_close_and_reopen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_reopen.db"
            
            # Create and write
            db1 = MetricsDB(db_path)
            db1.initialize()
            db1.record_event(event_type="test_event")
            db1.close()
            
            # Reopen and verify
            db2 = MetricsDB(db_path)
            db2.initialize()
            cursor = db2._conn.execute("SELECT COUNT(*) FROM events")
            assert cursor.fetchone()[0] == 1
            db2.close()
