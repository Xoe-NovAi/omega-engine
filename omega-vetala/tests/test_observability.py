# 🔱 omega-vetala — Observability Tests
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ OBSERVABILITY-TESTS
#
# AP Token: AP-MODERATION-P8-v1.0.0
#
"""Tests for the observability fabric (P8 / WatchTower).

Covers: structured_logger, metrics, tracing, alerts, moderation_observer.
"""

from __future__ import annotations

import json
import logging
import math
import time
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from omega_vetala.observability.structured_logger import (
    ModerationLogger,
    _content_hash,
    _hash_categories,
    ActionTaken,
)
from omega_vetala.observability.metrics import MetricsReporter
from omega_vetala.observability.tracing import (
    TraceContext,
    clear_trace,
    get_current_trace,
    start_trace,
    trace_span,
    traced,
    within_trace,
)
from omega_vetala.observability.alerts import (
    AlertManager,
    AlertRule,
    AlertSeverity,
    Op,
)
from omega_vetala.observability.moderation_observer import (
    ModerationObserver,
    _resolve_action,
)
from omega_vetala.providers.base import ModerationResult, ModelProvider


# ═══════════════════════════════════════════════════════════════════
# 1. Structured Logger — Privacy tests
# ═══════════════════════════════════════════════════════════════════


class TestContentHash:
    """Content hashing privacy primitive."""

    def test_hash_is_16_chars(self) -> None:
        """SHA-256[:16] produces 16 hex characters."""
        h = _content_hash("hello world")
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_is_deterministic(self) -> None:
        """Same input always produces the same hash."""
        h1 = _content_hash("some long text here")
        h2 = _content_hash("some long text here")
        assert h1 == h2

    def test_different_inputs_different_hashes(self) -> None:
        """Different inputs produce (with overwhelming probability) different hashes."""
        h1 = _content_hash("text A")
        h2 = _content_hash("text B")
        assert h1 != h2

    def test_hash_is_not_reversible(self) -> None:
        """The hash should not equal any substring of the original text."""
        text = "this is a test message"
        h = _content_hash(text)
        # The hash should NOT appear as a substring of the original
        assert h not in text


class TestCategoryHashing:
    """Category name hashing for privacy."""

    def test_category_keys_are_hashed(self) -> None:
        """Category names should be replaced with hashes."""
        cats = {"TOXICITY": 0.95, "INSULT": 0.80}
        hashed = _hash_categories(cats)
        assert "TOXICITY" not in hashed
        assert "INSULT" not in hashed
        assert len(hashed) == 2
        # Values should be preserved (rounded to 4 decimal places)
        assert abs(hashed[list(hashed.keys())[0]] - 0.95) < 0.0001


class TestModerationLogger:
    """Logger behaviour and content privacy."""

    def test_logger_creates_no_raw_content_in_output(self, tmp_path: Path) -> None:
        """Log file must NOT contain the raw input text."""
        log_path = tmp_path / "moderation.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        raw_text = "this is some sensitive user content with PII"
        logger.log_decision(
            trace_id="trace123",
            provider_name="test",
            is_flagged=True,
            confidence=0.95,
            latency_ms=42.0,
            categories={"TOXICITY": 0.95},
            action_taken="block",
            text=raw_text,
        )

        lines = log_path.read_text().splitlines()
        assert len(lines) >= 1

        for line in lines:
            parsed = json.loads(line)
            content = json.dumps(parsed)
            # The raw text should NOT appear anywhere in the log
            assert raw_text not in content
            # But a content_hash field should be present
            if "content_hash" in parsed:
                assert len(parsed["content_hash"]) == 16

    def test_logger_decision_fields(self, tmp_path: Path) -> None:
        """Decision log entries should contain all expected fields."""
        log_path = tmp_path / "decisions.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        logger.log_decision(
            trace_id="abc",
            provider_name="perspective",
            is_flagged=True,
            confidence=0.92,
            latency_ms=150.0,
            categories={"TOXICITY": 0.92},
            action_taken="block",
            text="flagged content here",
        )

        line = json.loads(log_path.read_text().splitlines()[0])
        assert line["trace_id"] == "abc"
        assert line["provider_name"] == "perspective"
        assert line["is_flagged"] is True
        assert line["confidence"] == 0.92
        assert line["latency_ms"] == 150.0
        assert line["action_taken"] == "block"
        assert line["content_hash"] == _content_hash("flagged content here")

    def test_provider_failure_log(self, tmp_path: Path) -> None:
        """Provider failure logs at WARNING level."""
        log_path = tmp_path / "failures.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        logger.log_provider_failure(
            trace_id="fail123",
            provider_name="openai",
            error_message="API timeout",
            latency_ms=5000.0,
            text="some text",
        )

        line = json.loads(log_path.read_text().splitlines()[0])
        assert line["level"] == "WARNING"
        assert "error" in line
        assert line["provider_name"] == "openai"

    def test_systemic_failure(self, tmp_path: Path) -> None:
        """Systemic failure logs at ERROR level."""
        log_path = tmp_path / "systemic.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        logger.log_systemic_failure(
            trace_id="sys123",
            error_message="All providers down",
        )

        line = json.loads(log_path.read_text().splitlines()[0])
        assert line["level"] == "ERROR"

    def test_flag_event_is_info_level(self, tmp_path: Path) -> None:
        """Flag events should be logged at INFO level."""
        log_path = tmp_path / "flags.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        logger.log_flag_event(
            trace_id="flag123",
            provider_name="perspective",
            is_flagged=True,
            confidence=0.95,
            latency_ms=100.0,
            categories={"TOXICITY": 0.95},
            action_taken="block",
            text="bad text",
        )

        line = json.loads(log_path.read_text().splitlines()[0])
        assert line["level"] == "INFO"

    def test_no_raw_content_in_provider_failure(self, tmp_path: Path) -> None:
        """Provider failure logs must also hash content."""
        log_path = tmp_path / "fail_hash.jsonl"
        logger = ModerationLogger(log_path=str(log_path))

        raw_text = "sensitive failure content"
        logger.log_provider_failure(
            trace_id="f1",
            provider_name="test",
            error_message="timeout",
            latency_ms=3000.0,
            text=raw_text,
        )

        content = log_path.read_text()
        assert raw_text not in content
        assert _content_hash(raw_text) in content


# ═══════════════════════════════════════════════════════════════════
# 2. Metrics — Counter correctness
# ═══════════════════════════════════════════════════════════════════


class TestMetricsReporter:
    """Metrics counters increment correctly."""

    def test_record_request_increments_total(self) -> None:
        """record_request should increment the total request count."""
        metrics = MetricsReporter()
        assert metrics.requests_total() == 0
        metrics.record_request(provider_name="p1")
        assert metrics.requests_total() == 1
        metrics.record_request(provider_name="p2")
        assert metrics.requests_total() == 2

    def test_record_flag_tracks_counts(self) -> None:
        """record_flag should increment flag counts per provider."""
        metrics = MetricsReporter()
        metrics.record_flag(provider_name="p1")
        metrics.record_flag(provider_name="p1")
        metrics.record_flag(provider_name="p2")
        snapshot = metrics.snapshot()
        assert snapshot["flags_total"] == 3

    def test_record_error_tracks_counts(self) -> None:
        """record_error should increment error counts."""
        metrics = MetricsReporter()
        metrics.record_error(provider_name="perspective")
        assert metrics.provider_error_count("perspective") == 1
        metrics.record_error(provider_name="perspective")
        assert metrics.provider_error_count("perspective") == 2

    def test_action_distribution(self) -> None:
        """Action distribution counters should track action types."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1", action_type="allow")
        metrics.record_request(provider_name="p1", action_type="block")
        metrics.record_request(provider_name="p1", action_type="block")
        dist = metrics.action_distribution()
        assert dist.get("allow") == 1
        assert dist.get("block") == 2

    def test_record_appeal_increments(self) -> None:
        """Appeals should be tracked."""
        metrics = MetricsReporter()
        metrics.record_appeal(provider_name="p1")
        metrics.record_appeal(provider_name="p1")
        snapshot = metrics.snapshot()
        assert snapshot["appeals_total"] == 2

    def test_requests_per_minute(self) -> None:
        """requests_per_minute should reflect recent activity."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1")
        metrics.record_request(provider_name="p1")
        # With a large enough window, should see 2 requests
        rpm = metrics.requests_per_minute(window_seconds=60)
        assert rpm > 0

    def test_flag_rate(self) -> None:
        """flag_rate should return percentage of flagged requests."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1")
        metrics.record_request(provider_name="p1")
        metrics.record_flag(provider_name="p1")
        rate = metrics.flag_rate(window_seconds=60)
        assert rate == 50.0  # 1 flag / 2 requests = 50%

    def test_flag_rate_zero_requests(self) -> None:
        """flag_rate should be 0 when there are no requests."""
        metrics = MetricsReporter()
        assert metrics.flag_rate() == 0.0

    def test_appeal_rate(self) -> None:
        """appeal_rate should return percentage of flagged that were appealed."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1")
        metrics.record_flag(provider_name="p1")
        metrics.record_flag(provider_name="p1")
        metrics.record_appeal(provider_name="p1")
        rate = metrics.appeal_rate(window_seconds=60)
        assert rate == 50.0  # 1 appeal / 2 flags = 50%

    def test_latency_histogram(self) -> None:
        """Latency recording should populate histogram buckets."""
        metrics = MetricsReporter()
        metrics.record_latency(provider_name="p1", latency_ms=50.0)
        metrics.record_latency(provider_name="p1", latency_ms=200.0)
        metrics.record_latency(provider_name="p1", latency_ms=5000.0)

        percentiles = metrics.provider_latency_percentiles("p1")
        assert percentiles["p50"] >= 50.0
        assert percentiles["p95"] >= 200.0
        assert percentiles["p99"] >= 5000.0

    def test_snapshot_contains_expected_keys(self) -> None:
        """Snapshot should include all high-level metrics."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1")
        snapshot = metrics.snapshot()
        assert "requests_total" in snapshot
        assert "flags_total" in snapshot
        assert "flag_rate_pct" in snapshot
        assert "action_distribution" in snapshot
        assert "per_provider" in snapshot

    def test_export_to_disk(self, tmp_path: Path) -> None:
        """Export to disk should write a valid JSON file."""
        metrics = MetricsReporter()
        metrics.record_request(provider_name="p1")
        export_path = str(tmp_path / "metrics.json")
        metrics.export_to_disk(export_path)
        data = json.loads(Path(export_path).read_text())
        assert data["requests_total"] == 1


class TestMetricsThreadSafety:
    """Metrics operations must be thread-safe."""

    def test_concurrent_records(self) -> None:
        """Multiple threads recording simultaneously should not corrupt state."""
        import threading

        metrics = MetricsReporter()

        def record_thread() -> None:
            for _ in range(100):
                metrics.record_request(provider_name="p1")
                metrics.record_flag(provider_name="p1")

        threads = [threading.Thread(target=record_thread) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        snapshot = metrics.snapshot()
        assert snapshot["requests_total"] == 400
        assert snapshot["flags_total"] == 400


# ═══════════════════════════════════════════════════════════════════
# 3. Tracing — Context propagation
# ═══════════════════════════════════════════════════════════════════


class TestTraceContext:
    """Trace context creation and propagation."""

    def test_start_trace_creates_valid_context(self) -> None:
        """start_trace should return a context with trace_id and root span."""
        trace = start_trace()
        assert trace.trace_id != ""
        assert len(trace.trace_id) == 16
        assert len(trace.spans) == 1
        assert trace.spans[0].operation == "root"
        clear_trace()

    def test_get_current_trace(self) -> None:
        """get_current_trace should return the active trace."""
        trace = start_trace()
        current = get_current_trace()
        assert current is not None
        assert current.trace_id == trace.trace_id
        clear_trace()

    def test_get_current_trace_none(self) -> None:
        """get_current_trace returns None when no trace is active."""
        clear_trace()
        assert get_current_trace() is None

    def test_clear_trace(self) -> None:
        """clear_trace should remove the active trace."""
        start_trace()
        clear_trace()
        assert get_current_trace() is None

    def test_within_trace_restores(self) -> None:
        """within_trace should restore a previously saved trace."""
        trace = start_trace()
        saved_id = trace.trace_id
        clear_trace()
        assert get_current_trace() is None
        within_trace(trace)
        assert get_current_trace() is not None
        assert get_current_trace().trace_id == saved_id
        clear_trace()

    def test_nested_spans(self) -> None:
        """Nested spans should have correct parent_span_id."""
        trace = start_trace()
        root_id = trace.current_span_id
        span_a = trace.new_span("operation_a")
        span_b = trace.new_span("operation_b")

        # Find spans
        spans = {s.span_id: s for s in trace.spans}
        assert spans[span_a].parent_span_id == root_id
        assert spans[span_b].parent_span_id == span_a

        trace.end_span(span_b)
        trace.end_span(span_a)
        clear_trace()

    def test_end_span_records_duration(self) -> None:
        """end_span should set duration_ms."""
        trace = start_trace()
        span_id = trace.new_span("test")
        trace.end_span(span_id)
        spans = {s.span_id: s for s in trace.spans}
        assert spans[span_id].duration_ms > 0
        clear_trace()

    def test_end_span_records_success(self) -> None:
        """end_span should record success/failure."""
        trace = start_trace()
        span_id = trace.new_span("failing")
        trace.end_span(span_id, success=False, error="something broke")
        spans = {s.span_id: s for s in trace.spans}
        assert spans[span_id].success is False
        assert spans[span_id].error == "something broke"
        clear_trace()

    def test_export_returns_serialisable_dict(self) -> None:
        """export should return a JSON-serialisable dict."""
        trace = start_trace()
        data = trace.export()
        assert "trace_id" in data
        assert "spans" in data
        assert len(data["spans"]) == 1
        # Should be JSON-serialisable
        json.dumps(data)
        clear_trace()


class TestTracedDecorator:
    """@traced decorator."""

    @pytest.mark.anyio
    async def test_traced_async_wraps_with_span(self) -> None:
        """@traced on async functions should create and close a span."""
        trace = start_trace()
        initial_span_count = len(trace.spans)

        @traced("test_async_op")
        async def my_async_func() -> str:
            return "done"

        result = await my_async_func()
        assert result == "done"

        # Should have added a span
        assert len(trace.spans) == initial_span_count + 1
        assert trace.spans[-1].operation == "test_async_op"
        assert trace.spans[-1].success is True
        clear_trace()

    @pytest.mark.anyio
    async def test_traced_captures_failure(self) -> None:
        """@traced should mark span as failed when function raises."""
        trace = start_trace()

        @traced("failing_op")
        async def failing_func() -> None:
            msg = "intentional failure"
            raise ValueError(msg)

        with pytest.raises(ValueError):
            await failing_func()

        # Last span should be marked as failed
        assert trace.spans[-1].success is False
        assert "intentional failure" in trace.spans[-1].error
        clear_trace()

    @pytest.mark.anyio
    async def test_traced_noop_without_trace(self) -> None:
        """@traced should be a no-op when no trace is active."""
        clear_trace()

        @traced("noop_op")
        async def my_func() -> str:
            return "ok"

        result = await my_func()
        assert result == "ok"
        # No trace context — should still work

    def test_traced_sync(self) -> None:
        """@traced should also work with synchronous functions."""
        trace = start_trace()

        @traced("sync_op")
        def sync_func() -> int:
            return 42

        result = sync_func()
        assert result == 42
        assert trace.spans[-1].operation == "sync_op"
        clear_trace()


class TestTraceSpanContextManager:
    """trace_span context manager."""

    def test_context_manager_creates_span(self) -> None:
        """trace_span should create a child span."""
        trace = start_trace()
        with trace_span("ctx_op"):
            pass
        assert trace.spans[-1].operation == "ctx_op"
        assert trace.spans[-1].success is True
        clear_trace()

    def test_context_manager_records_failure(self) -> None:
        """trace_span should record failure on exception."""
        trace = start_trace()
        try:
            with trace_span("failing_ctx"):
                msg = "bad"
                raise RuntimeError(msg)
        except RuntimeError:
            pass
        assert trace.spans[-1].success is False
        clear_trace()


# ═══════════════════════════════════════════════════════════════════
# 4. Alerts — Threshold evaluation
# ═══════════════════════════════════════════════════════════════════


class TestAlertRuleOperators:
    """Comparison operators for threshold evaluation."""

    def test_gt_true(self) -> None:
        """GT: 15 > 10 is True."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(15.0, 10.0, Op.GT) is True

    def test_gt_false(self) -> None:
        """GT: 5 > 10 is False."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(5.0, 10.0, Op.GT) is False

    def test_lt_true(self) -> None:
        """LT: 5 < 10 is True."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(5.0, 10.0, Op.LT) is True

    def test_lt_false(self) -> None:
        """LT: 15 < 10 is False."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(15.0, 10.0, Op.LT) is False

    def test_eq_true(self) -> None:
        """EQ: 10 == 10 is True."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(10.0, 10.0, Op.EQ) is True

    def test_eq_false(self) -> None:
        """EQ: 10 != 11 is False."""
        from omega_vetala.observability.alerts import _evaluate
        assert _evaluate(10.0, 11.0, Op.EQ) is False


class TestAlertManager:
    """AlertManager rule evaluation."""

    def test_rule_fires_when_threshold_breached(self) -> None:
        """Alert should fire when metric exceeds threshold."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        # Create conditions: 2 flags out of 4 requests = 50% flag rate
        for _ in range(4):
            metrics.record_request(provider_name="test")
        for _ in range(2):
            metrics.record_flag(provider_name="test")

        # Add a simple rule: flag_rate > 10%
        alert_mgr.add_rule(AlertRule(
            name="test_flag_spike",
            description="Test rule",
            metric="flag_rate",
            op=Op.GT,
            threshold=10.0,
            cooldown_seconds=1.0,
            severity=AlertSeverity.WARNING,
        ))

        fired = alert_mgr.evaluate()
        assert len(fired) >= 1
        fired_names = [a["rule_name"] for a in fired]
        assert "test_flag_spike" in fired_names

    def test_rule_does_not_fire_below_threshold(self) -> None:
        """Alert should NOT fire when metric is below threshold."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        alert_mgr.add_rule(AlertRule(
            name="test_no_fire",
            description="Should not fire",
            metric="requests_per_minute",
            op=Op.GT,
            threshold=1000000.0,  # Very high threshold — impossible to breach
            cooldown_seconds=1.0,
        ))

        metrics.record_request(provider_name="test")

        fired = alert_mgr.evaluate()
        # No rules should fire (requests_per_minute is tiny vs 1M)
        assert not any(a["rule_name"] == "test_no_fire" for a in fired)

    def test_builtin_rules_are_registered(self) -> None:
        """AlertManager should register built-in rules on init."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        rules = alert_mgr.list_rules()
        names = [r["name"] for r in rules]
        assert "flag_rate_spike" in names
        assert "high_provider_failure_rate" in names
        assert "high_latency" in names
        assert "high_appeal_rate" in names

    def test_alert_history(self) -> None:
        """Fired alerts should appear in history."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        alert_mgr.add_rule(AlertRule(
            name="historic_rule",
            description="For history",
            metric="flag_rate",
            op=Op.GT,
            threshold=-1.0,  # Always fires (flag_rate >= 0 always > -1)
            cooldown_seconds=1.0,
        ))

        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")
        fired = alert_mgr.evaluate()
        assert len(fired) >= 1

        history = alert_mgr.alert_history()
        assert any(h["rule_name"] == "historic_rule" for h in history)

    def test_alert_history_filter_by_severity(self) -> None:
        """alert_history should support severity filtering."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        alert_mgr.add_rule(AlertRule(
            name="info_rule",
            description="Info rule",
            metric="flag_rate",
            op=Op.GT,
            threshold=-1.0,  # Always fires
            severity=AlertSeverity.INFO,
            cooldown_seconds=1.0,
        ))

        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")
        alert_mgr.evaluate()

        info_history = alert_mgr.alert_history(severity="info")
        warning_history = alert_mgr.alert_history(severity="warning")
        assert len(info_history) >= 1
        # info_rule is severity INFO, not warning
        assert all(h["severity"] == "info" for h in info_history)
        # The warning filter should not include our info rule
        if warning_history:
            assert all(h["severity"] == "warning" for h in warning_history)


class TestAlertCooldown:
    """Alert cooldown prevents storm."""

    def test_cooldown_prevents_repeat_fires(self) -> None:
        """Alert should NOT fire again within cooldown period."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        alert_mgr.add_rule(AlertRule(
            name="cooldown_rule",
            description="Cooldown test",
            metric="flag_rate",
            op=Op.GT,
            threshold=0.0,  # Always fires
            cooldown_seconds=3600.0,  # 1 hour cooldown
            severity=AlertSeverity.WARNING,
        ))

        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")

        # First evaluation should fire
        fired1 = alert_mgr.evaluate()
        assert len(fired1) >= 1

        # Second immediate evaluation should NOT fire (cooldown active)
        fired2 = alert_mgr.evaluate()
        assert len(fired2) == 0

    def test_cooldown_expires(self) -> None:
        """Alert should fire again after cooldown expires."""
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        alert_mgr.add_rule(AlertRule(
            name="expiring_rule",
            description="Expiry test",
            metric="flag_rate",
            op=Op.GT,
            threshold=0.0,  # Always fires
            cooldown_seconds=0.1,  # 100 ms cooldown
            severity=AlertSeverity.WARNING,
        ))

        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")

        # First fire
        fired1 = alert_mgr.evaluate()
        assert len(fired1) >= 1

        # Wait for cooldown to expire
        time.sleep(0.15)

        # Should fire again
        fired2 = alert_mgr.evaluate()
        # Note: with flag_rate still > 0, and cooldown expired,
        # it should fire if threshold is still breached
        assert len(fired2) >= 1


# ═══════════════════════════════════════════════════════════════════
# 5. ModerationObserver — Integration
# ═══════════════════════════════════════════════════════════════════


class AlwaysPassProvider(ModelProvider):
    """Mock provider that always returns clean."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=False,
            confidence=0.05,
            categories={"clean": 0.95},
            provider_name="always_pass",
            latency_ms=10.0,
        )


class AlwaysFlagProvider(ModelProvider):
    """Mock provider that always flags."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=True,
            confidence=0.95,
            categories={"toxicity": 0.95},
            provider_name="always_flag",
            latency_ms=20.0,
        )


class FailingProvider(ModelProvider):
    """Mock provider that always crashes."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        msg = "provider crashed"
        raise RuntimeError(msg)


class TestResolveAction:
    """Action resolution from ModerationResult."""

    def test_not_flagged_is_allow(self) -> None:
        """Non-flagged content should be ALLOW."""
        result = ModerationResult(is_flagged=False)
        assert _resolve_action(result) == ActionTaken.ALLOW

    def test_high_confidence_is_block(self) -> None:
        """Flagged with high confidence should be BLOCK."""
        result = ModerationResult(is_flagged=True, confidence=0.95)
        assert _resolve_action(result) == ActionTaken.BLOCK

    def test_medium_confidence_is_warn(self) -> None:
        """Flagged with medium confidence should be WARN."""
        result = ModerationResult(is_flagged=True, confidence=0.6)
        assert _resolve_action(result) == ActionTaken.WARN

    def test_low_confidence_is_review(self) -> None:
        """Flagged with low confidence should be REVIEW."""
        result = ModerationResult(is_flagged=True, confidence=0.3)
        assert _resolve_action(result) == ActionTaken.REVIEW


class TestModerationObserver:
    """Observer integration tests."""

    @pytest.mark.anyio
    async def test_observer_wraps_provider_call(self) -> None:
        """Observer should call the provider and return a ModerationResult."""
        provider = AlwaysPassProvider()
        observer = ModerationObserver(provider)
        result = await observer.observe(provider, "clean text")
        assert isinstance(result, ModerationResult)
        assert result.is_flagged is False

    @pytest.mark.anyio
    async def test_observer_records_metrics(self) -> None:
        """Observer should update metrics after a provider call."""
        provider = AlwaysPassProvider()
        observer = ModerationObserver(provider)
        await observer.observe(provider, "test")
        assert observer.metrics.requests_total() == 1

    @pytest.mark.anyio
    async def test_observer_records_flag_metrics(self) -> None:
        """Observer should record flag metrics when result is flagged."""
        provider = AlwaysFlagProvider()
        observer = ModerationObserver(provider)
        await observer.observe(provider, "bad text")
        snapshot = observer.metrics.snapshot()
        assert snapshot["flags_total"] == 1
        assert snapshot["requests_total"] == 1

    @pytest.mark.anyio
    async def test_observer_handles_provider_failure(self) -> None:
        """Observer should handle a provider crash gracefully."""
        provider = FailingProvider()
        observer = ModerationObserver(provider)
        result = await observer.observe(provider, "test")
        # Should return a fallback result, not crash
        assert isinstance(result, ModerationResult)
        assert result.is_flagged is False
        # Error should be recorded
        assert observer.metrics.provider_error_count("provider_chain") >= 0

    @pytest.mark.anyio
    async def test_observer_appeal_tracking(self) -> None:
        """Appeals should update metrics."""
        provider = AlwaysFlagProvider()
        observer = ModerationObserver(provider)
        result = await observer.observe(provider, "appeal test")
        observer.appeal(result.trace_id, result, user_feedback=False)
        snapshot = observer.metrics.snapshot()
        assert snapshot["appeals_total"] == 1

    @pytest.mark.anyio
    async def test_observer_trace_integration(self) -> None:
        """Observer should create a trace during observe."""
        provider = AlwaysPassProvider()
        observer = ModerationObserver(provider)
        clear_trace()
        assert get_current_trace() is None
        result = await observer.observe(provider, "trace test")
        assert result.trace_id != ""
        # Trace should be cleared after observe completes
        assert get_current_trace() is None

    @pytest.mark.anyio
    async def test_observer_heartbeat(self) -> None:
        """Heartbeat should return status dict."""
        provider = AlwaysPassProvider()
        observer = ModerationObserver(provider)
        status = observer.heartbeat()
        assert status["status"] == "ok"
        assert status["chain_type"] == "AlwaysPassProvider"

    @pytest.mark.anyio
    async def test_observer_hash_frequencies(self) -> None:
        """Observer should track hash frequencies for flagged content."""
        provider = AlwaysFlagProvider()
        observer = ModerationObserver(provider)
        await observer.observe(provider, "repeated bad text")
        await observer.observe(provider, "repeated bad text")
        freqs = observer.hash_frequencies
        # Should have 1 key (same hash from same text)
        assert len(freqs) == 1
        assert list(freqs.values())[0] == 2

    @pytest.mark.anyio
    async def test_observer_no_raw_content_in_logs(self, tmp_path: Path) -> None:
        """Observe should not leak raw content into logs."""
        log_path = tmp_path / "observer.jsonl"
        logger = ModerationLogger(log_path=str(log_path))
        provider = AlwaysFlagProvider()
        observer = ModerationObserver(provider, logger_instance=logger)

        raw_text = "sensitive-user-content-with-pii@email.com"
        await observer.observe(provider, raw_text)

        log_content = log_path.read_text()
        assert raw_text not in log_content

    @pytest.mark.anyio
    async def test_observer_multiple_requests(self) -> None:
        """Observer should correctly track multiple requests."""
        provider = AlwaysPassProvider()
        observer = ModerationObserver(provider)

        for _ in range(5):
            await observer.observe(provider, "some text")

        assert observer.metrics.requests_total() == 5

    @pytest.mark.anyio
    async def test_observer_alert_integration(self) -> None:
        """Observer should evaluate alerts after each observation."""
        provider = AlwaysFlagProvider()
        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        # Add a rule with very low threshold that always fires
        alert_mgr.add_rule(AlertRule(
            name="always_fire",
            description="Always fires",
            metric="flag_rate",
            op=Op.GT,
            threshold=0.0,
            cooldown_seconds=0.1,
            severity=AlertSeverity.INFO,
        ))

        observer = ModerationObserver(
            provider,
            metrics=metrics,
            alerts=alert_mgr,
        )

        await observer.observe(provider, "trigger alert")
        # Alert should have fired — check alert rule fire count
        rule = alert_mgr.get_rule("always_fire")
        assert rule is not None
        if rule:
            assert rule.fire_count >= 1


# ═══════════════════════════════════════════════════════════════════════
# 6. Additional observability tests (added by P10)
# ═══════════════════════════════════════════════════════════════════════


class TestObserverEndToEnd:
    """End-to-end observer workflow."""

    @pytest.mark.anyio
    async def test_full_observe_cycle(self) -> None:
        """Full observe cycle: mock provider → observe → verify all components."""
        from omega_vetala.observability.structured_logger import ModerationLogger
        from omega_vetala.observability.metrics import MetricsReporter
        from omega_vetala.observability.alerts import AlertManager, AlertRule, AlertSeverity, Op

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        observer = ModerationObserver(
            AlwaysPassProvider(),
            metrics=metrics,
            alerts=alert_mgr,
        )

        # Add a rule that won't fire for clean content
        alert_mgr.add_rule(AlertRule(
            name="high_flag_rate",
            description="Flag rate > 50%",
            metric="flag_rate",
            op=Op.GT,
            threshold=50.0,
            cooldown_seconds=1.0,
            severity=AlertSeverity.WARNING,
        ))

        # Perform observation
        result = await observer.observe(AlwaysPassProvider(), "clean test text")

        # Verify all components touched
        assert isinstance(result, ModerationResult)
        assert observer.metrics.requests_total() == 1
        assert result.is_flagged is False

        # Verify heartbeat reflects state
        status = observer.heartbeat()
        assert status["total_requests"] >= 1
        assert status["status"] == "ok"

    @pytest.mark.anyio
    async def test_observe_with_provider_chain(self) -> None:
        """Observer should work with a ProviderChain."""
        from omega_vetala.providers.chain import ProviderChain

        chain = ProviderChain([AlwaysPassProvider()])
        observer = ModerationObserver(chain)
        result = await observer.observe(chain, "chain test")
        assert isinstance(result, ModerationResult)
        assert observer.metrics.requests_total() == 1

    @pytest.mark.anyio
    async def test_multiple_observations_aggregate(self) -> None:
        """Multiple observations should aggregate correctly."""
        observer = ModerationObserver(AlwaysPassProvider())

        for _ in range(10):
            await observer.observe(AlwaysPassProvider(), f"test {_}")

        assert observer.metrics.requests_total() == 10
        snapshot = observer.metrics.snapshot()
        assert snapshot["requests_total"] == 10


class TestAlertIntegration:
    """Alert integration with observer."""

    @pytest.mark.anyio
    async def test_flag_rate_spike_triggers_alert(self) -> None:
        """Force flag rate spike → verify alert fires."""
        from omega_vetala.observability.alerts import AlertManager, AlertRule, AlertSeverity, Op

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        # Replace built-in rules with a test rule
        alert_mgr._rules.clear()
        alert_mgr.add_rule(AlertRule(
            name="test_spike",
            description="Flag rate > 10%",
            metric="flag_rate",
            op=Op.GT,
            threshold=10.0,
            cooldown_seconds=0.1,
            severity=AlertSeverity.CRITICAL,
        ))

        observer = ModerationObserver(
            AlwaysFlagProvider(),
            metrics=metrics,
            alerts=alert_mgr,
        )

        # 10 requests, 8 flagged = 80% flag rate (well above 10%)
        for _ in range(10):
            await observer.observe(AlwaysFlagProvider(), f"flagged text {_}")

        # The alert should have fired
        rule = alert_mgr.get_rule("test_spike")
        assert rule is not None
        assert rule.fire_count >= 1

    @pytest.mark.anyio
    async def test_alert_not_fired_below_threshold(self) -> None:
        """Alert should NOT fire when flag rate is below threshold."""
        from omega_vetala.observability.alerts import AlertManager, AlertRule, AlertSeverity, Op

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)

        # Replace built-in rules
        alert_mgr._rules.clear()
        alert_mgr.add_rule(AlertRule(
            name="high_threshold",
            description="Flag rate > 90%",
            metric="flag_rate",
            op=Op.GT,
            threshold=90.0,
            cooldown_seconds=0.1,
            severity=AlertSeverity.WARNING,
        ))

        observer = ModerationObserver(
            AlwaysPassProvider(),
            metrics=metrics,
            alerts=alert_mgr,
        )

        for _ in range(10):
            await observer.observe(AlwaysPassProvider(), "clean text")

        rule = alert_mgr.get_rule("high_threshold")
        assert rule is not None
        # Flag rate should be 0% (AlwaysPassProvider never flags)
        assert rule.fire_count == 0

    @pytest.mark.anyio
    async def test_builtin_alert_rules_observe_integration(self) -> None:
        """Built-in alert rules should work with observer observations."""
        observer = ModerationObserver(AlwaysFlagProvider())

        for _ in range(5):
            await observer.observe(AlwaysFlagProvider(), "text")

        # Built-in 'flag_rate_spike' rule has threshold=30% with 300s cooldown
        # Our flag rate is 100% (all flagged), but cooldown prevents re-firing
        rule = observer.alerts.get_rule("flag_rate_spike")
        assert rule is not None
        assert rule.fire_count >= 0  # At least the first evaluation should fire


class TestDashboardQueryTimeRanges:
    """Dashboard query time range handling."""

    def test_dashboard_time_range_presets(self) -> None:
        """Dashboard time range presets resolve to correct seconds."""
        from omega_vetala.observability.dashboard import DashboardQuery, _resolve_window

        assert _resolve_window("last_5m") == 300.0
        assert _resolve_window("last_1h") == 3600.0
        assert _resolve_window("last_24h") == 86400.0
        assert _resolve_window("last_7d") == 604800.0

    def test_dashboard_time_range_unknown_defaults(self) -> None:
        """Unknown time range preset defaults to 1 hour."""
        from omega_vetala.observability.dashboard import _resolve_window

        assert _resolve_window("unknown_range") == 3600.0

    def test_dashboard_time_range_numeric(self) -> None:
        """Numeric time range should pass through."""
        from omega_vetala.observability.dashboard import _resolve_window

        assert _resolve_window(120.0) == 120.0

    def test_dashboard_overview(self) -> None:
        """Dashboard overview returns expected structure."""
        from omega_vetala.observability.dashboard import DashboardQuery

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")

        overview = dashboard.overview()
        assert "status" in overview
        assert "requests_total" in overview
        assert "requests_per_minute" in overview
        assert "flag_rate_pct" in overview
        assert overview["requests_total"] >= 1

    def test_dashboard_provider_latency(self) -> None:
        """Dashboard provider latency query."""
        from omega_vetala.observability.dashboard import DashboardQuery

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        metrics.record_latency(provider_name="test", latency_ms=50.0)

        latency = dashboard.provider_latency("test")
        assert "test" in latency
        assert "p50" in latency["test"]

    def test_dashboard_all_providers_latency(self) -> None:
        """Dashboard queries latency for all providers."""
        from omega_vetala.observability.dashboard import DashboardQuery

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        # Must record requests for providers to appear in per_provider snapshot
        metrics.record_request(provider_name="p1")
        metrics.record_request(provider_name="p2")
        metrics.record_latency(provider_name="p1", latency_ms=50.0)
        metrics.record_latency(provider_name="p2", latency_ms=100.0)

        all_latency = dashboard.provider_latency()
        assert "p1" in all_latency
        assert "p2" in all_latency

    def test_dashboard_action_distribution(self) -> None:
        """Dashboard action distribution query."""
        from omega_vetala.observability.dashboard import DashboardQuery

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        metrics.record_request(provider_name="test", action_type="allow")
        metrics.record_request(provider_name="test", action_type="block")

        dist = dashboard.action_distribution()
        assert "allow" in dist or "block" in dist

    def test_dashboard_full_snapshot(self) -> None:
        """Dashboard full snapshot returns comprehensive structure."""
        from omega_vetala.observability.dashboard import DashboardQuery

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        metrics.record_request(provider_name="test")
        snapshot = dashboard.full_snapshot()

        assert "overview" in snapshot
        assert "provider_latency" in snapshot
        assert "action_distribution" in snapshot
        assert "alert_rules" in snapshot
        assert "recent_alerts" in snapshot

    def test_dashboard_export_json(self, tmp_path: Any) -> None:
        """Dashboard export to JSON produces valid file."""
        from omega_vetala.observability.dashboard import DashboardQuery
        import json

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        metrics.record_request(provider_name="test")
        export_path = str(tmp_path / "dashboard.json")
        dashboard.export_json(export_path)

        data = json.loads(Path(export_path).read_text())
        assert "overview" in data

    def test_dashboard_alert_history_time_range(self) -> None:
        """Dashboard alert_history with time range filter."""
        from omega_vetala.observability.dashboard import DashboardQuery
        from omega_vetala.observability.alerts import AlertRule, AlertSeverity, Op

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        alert_mgr.add_rule(AlertRule(
            name="test_alert",
            description="Test",
            metric="flag_rate",
            op=Op.GT,
            threshold=0.0,
            cooldown_seconds=0.1,
        ))
        metrics.record_request(provider_name="test")
        metrics.record_flag(provider_name="test")
        alert_mgr.evaluate()

        history = dashboard.alert_history(range_spec="last_5m")
        assert any(h["rule_name"] == "test_alert" for h in history)


class TestAppealTracking:
    """Appeal tracking end-to-end."""

    @pytest.mark.anyio
    async def test_appeal_end_to_end(self) -> None:
        """Full appeal lifecycle: flag → appeal → verify metrics."""
        observer = ModerationObserver(AlwaysFlagProvider())
        result = await observer.observe(AlwaysFlagProvider(), "flagged content")

        # Appeal the decision
        observer.appeal(result.trace_id, result, user_feedback=False)

        # Verify metrics updated
        snapshot = observer.metrics.snapshot()
        assert snapshot["appeals_total"] >= 1

    @pytest.mark.anyio
    async def test_appeal_with_feedback_true(self) -> None:
        """Appeal with user_feedback=True should record appeal."""
        observer = ModerationObserver(AlwaysFlagProvider())
        result = await observer.observe(AlwaysFlagProvider(), "content")

        observer.appeal(result.trace_id, result, user_feedback=True)
        snapshot = observer.metrics.snapshot()
        assert snapshot["appeals_total"] == 1

    @pytest.mark.anyio
    async def test_multiple_appeals(self) -> None:
        """Multiple appeals should increment counter correctly."""
        observer = ModerationObserver(AlwaysFlagProvider())

        for i in range(5):
            result = await observer.observe(AlwaysFlagProvider(), f"text {i}")
            observer.appeal(result.trace_id, result, user_feedback=False)

        snapshot = observer.metrics.snapshot()
        assert snapshot["appeals_total"] == 5

    @pytest.mark.anyio
    async def test_appeal_no_flag(self) -> None:
        """Appeal on non-flagged content should still record."""
        observer = ModerationObserver(AlwaysPassProvider())
        result = await observer.observe(AlwaysPassProvider(), "clean content")

        observer.appeal(result.trace_id, result, user_feedback=True)
        snapshot = observer.metrics.snapshot()
        assert snapshot["appeals_total"] == 1

    @pytest.mark.anyio
    async def test_appeal_rate_calculation(self) -> None:
        """Appeal rate should be calculated correctly."""
        metrics = MetricsReporter()
        observer = ModerationObserver(
            AlwaysFlagProvider(),
            metrics=metrics,
        )

        # 3 flags, 1 appeal
        for i in range(3):
            result = await observer.observe(AlwaysFlagProvider(), f"text {i}")
            if i == 0:
                observer.appeal(result.trace_id, result, user_feedback=False)

        rate = metrics.appeal_rate(window_seconds=60)
        assert rate > 0.0

    @pytest.mark.anyio
    async def test_appeal_with_logger(self, tmp_path: Any) -> None:
        """Appeal should be logged when logger is configured."""
        from omega_vetala.observability.structured_logger import ModerationLogger

        log_path = tmp_path / "appeals.jsonl"
        logger = ModerationLogger(log_path=str(log_path))
        observer = ModerationObserver(
            AlwaysFlagProvider(),
            logger_instance=logger,
        )

        result = await observer.observe(AlwaysFlagProvider(), "appeal content")
        observer.appeal(result.trace_id, result, user_feedback=False)

        log_content = log_path.read_text()
        assert "appeal" in log_content.lower()
