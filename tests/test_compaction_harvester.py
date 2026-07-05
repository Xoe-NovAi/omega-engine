# AP: AP-TEST-COMPACTION-HARVESTER-v1.0.0
# 🔱 Tests for CompactionHarvester — Automated Compaction Monitoring
# ⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ TEST-COMPACTION-HARVESTER
#
# Tests session size monitoring, event recording, and metrics reporting.
#
# M21: Gate Integrity — contract tests verify return types with isinstance
# M9: Error Integrity — tests for error paths

from typing import Any, Dict, List

import pytest

from omega.oracle.compaction_harvester import (
    CompactionHarvester,
    CompactionEvent,
    CompactionMetrics,
    SessionSizeReport,
    get_harvester,
    reset_harvester,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def harvester() -> CompactionHarvester:
    """Create a fresh CompactionHarvester for each test."""
    return CompactionHarvester(max_exchanges=30, warn_threshold=25)


# ── Dataclass Contract Tests ──────────────────────────────────────────

class TestCompactionEvent:
    """Contract tests for CompactionEvent dataclass."""

    def test_event_is_dataclass(self) -> None:
        """M21: Contract test — CompactionEvent is a dataclass."""
        event = CompactionEvent(
            entity_name="test", session_id="ses_001",
            before_count=40, after_count=20,
        )
        assert isinstance(event, CompactionEvent)
        assert isinstance(event.entity_name, str)
        assert isinstance(event.session_id, str)
        assert isinstance(event.before_count, int)
        assert isinstance(event.after_count, int)
        assert isinstance(event.triggered_by, str)
        assert event.exchanges_saved == 20

    def test_event_auto_timestamp(self) -> None:
        """Event without explicit timestamp gets one auto-assigned."""
        import time
        event = CompactionEvent(
            entity_name="test", session_id="ses_001",
            before_count=40, after_count=20,
        )
        assert event.timestamp > 0
        assert abs(time.time() - event.timestamp) < 2.0

    def test_event_zero_saved(self) -> None:
        """Event where no exchanges were saved."""
        event = CompactionEvent(
            entity_name="test", session_id="ses_001",
            before_count=20, after_count=20,
        )
        assert event.exchanges_saved == 0


class TestSessionSizeReport:
    """Contract tests for SessionSizeReport dataclass."""

    def test_report_is_dataclass(self) -> None:
        """M21: Contract test — SessionSizeReport is a dataclass."""
        report = SessionSizeReport(
            entity_name="test", session_id="ses_001",
            exchange_count=35, needs_compaction=True,
            near_threshold=True,
        )
        assert isinstance(report, SessionSizeReport)
        assert isinstance(report.entity_name, str)
        assert isinstance(report.exchange_count, int)
        assert isinstance(report.needs_compaction, bool)

    def test_report_no_compaction_needed(self) -> None:
        """Report correctly indicates no compaction needed."""
        report = SessionSizeReport(
            entity_name="test", session_id="ses_001",
            exchange_count=10, needs_compaction=False,
            near_threshold=False,
        )
        assert not report.needs_compaction
        assert not report.near_threshold

    def test_report_near_threshold(self) -> None:
        """Report correctly indicates near-threshold state."""
        report = SessionSizeReport(
            entity_name="test", session_id="ses_001",
            exchange_count=28, needs_compaction=False,
            near_threshold=True,
        )
        assert not report.needs_compaction
        assert report.near_threshold


class TestCompactionMetrics:
    """Contract tests for CompactionMetrics dataclass."""

    def test_metrics_is_dataclass(self) -> None:
        """M21: Contract test — CompactionMetrics is a dataclass."""
        metrics = CompactionMetrics()
        assert isinstance(metrics, CompactionMetrics)
        assert isinstance(metrics.total_events, int)
        assert isinstance(metrics.total_exchanges_saved, int)
        assert isinstance(metrics.average_exchanges_saved, float)
        assert isinstance(metrics.entities_affected, int)
        assert isinstance(metrics.latest_events, list)


# ── CompactionHarvester Tests ────────────────────────────────────────

class TestCompactionHarvester:
    """Tests for the CompactionHarvester class."""

    def test_default_config(self) -> None:
        """Default thresholds match expected values."""
        h = CompactionHarvester()
        assert h.max_exchanges == 30
        assert h.warn_threshold == 25

    def test_custom_config(self) -> None:
        """Custom thresholds are correctly applied."""
        h = CompactionHarvester(max_exchanges=50, warn_threshold=40)
        assert h.max_exchanges == 50
        assert h.warn_threshold == 40

    def test_warn_threshold_clamped(self) -> None:
        """Warn threshold is clamped to max_exchanges if it exceeds it."""
        h = CompactionHarvester(max_exchanges=20, warn_threshold=30)
        assert h.warn_threshold == 20

    def test_setter_max_exchanges_adjusts_warn(self) -> None:
        """Setting max_exchanges below warn_threshold adjusts warn_threshold."""
        h = CompactionHarvester(max_exchanges=50, warn_threshold=40)
        h.max_exchanges = 30
        assert h.max_exchanges == 30
        assert h.warn_threshold == 30  # Clamped

    def test_assess_session_below_threshold(self, harvester: CompactionHarvester) -> None:
        """Sessions below max_exchanges are not flagged for compaction."""
        report = harvester.assess_session("test", "ses_001", 10)
        assert isinstance(report, SessionSizeReport)
        assert not report.needs_compaction
        assert not report.near_threshold
        assert report.exchange_count == 10

    def test_assess_session_near_threshold(self, harvester: CompactionHarvester) -> None:
        """Sessions near warn_threshold are flagged as near-threshold."""
        report = harvester.assess_session("test", "ses_001", 25)
        assert not report.needs_compaction
        assert report.near_threshold

    def test_assess_session_at_threshold(self, harvester: CompactionHarvester) -> None:
        """Sessions at exactly max_exchanges are not flagged."""
        report = harvester.assess_session("test", "ses_001", 30)
        assert not report.needs_compaction

    def test_assess_session_above_threshold(self, harvester: CompactionHarvester) -> None:
        """Sessions above max_exchanges are flagged for compaction."""
        report = harvester.assess_session("test", "ses_001", 35)
        assert report.needs_compaction
        assert report.near_threshold

    async def test_record_compaction(self, harvester: CompactionHarvester) -> None:
        """Recording a compaction event adds it to the log."""
        assert len(harvester.get_recent_events()) == 0
        
        await harvester.record_compaction(
            entity_name="test", session_id="ses_001",
            before_count=45, after_count=20,
        )
        
        events = harvester.get_recent_events()
        assert len(events) == 1
        assert events[0].entity_name == "test"
        assert events[0].before_count == 45
        assert events[0].after_count == 20
        assert events[0].exchanges_saved == 25

    async def test_record_multiple_compactions(self, harvester: CompactionHarvester) -> None:
        """Multiple compaction events are all recorded."""
        for i in range(5):
            await harvester.record_compaction(
                entity_name=f"entity_{i}",
                session_id=f"ses_{i:03d}",
                before_count=40 + i,
                after_count=20,
                triggered_by="test",
            )
        
        events = harvester.get_recent_events(limit=10)
        assert len(events) == 5
        # Most recent first
        assert events[0].entity_name == "entity_4"

    async def test_record_filter_by_entity(self, harvester: CompactionHarvester) -> None:
        """Events can be filtered by entity name."""
        await harvester.record_compaction(
            entity_name="alpha", session_id="ses_001",
            before_count=40, after_count=20,
            triggered_by="test",
        )
        await harvester.record_compaction(
            entity_name="beta", session_id="ses_002",
            before_count=50, after_count=25,
            triggered_by="test",
        )
        await harvester.record_compaction(
            entity_name="alpha", session_id="ses_003",
            before_count=35, after_count=15,
            triggered_by="test",
        )
        
        alpha_events = harvester.get_recent_events(entity_name="alpha")
        assert len(alpha_events) == 2
        assert all(e.entity_name == "alpha" for e in alpha_events)

    async def test_metrics_empty(self, harvester: CompactionHarvester) -> None:
        """Empty harvester returns zeroed metrics."""
        metrics = harvester.get_metrics()
        assert isinstance(metrics, CompactionMetrics)
        assert metrics.total_events == 0
        assert metrics.total_exchanges_saved == 0
        assert metrics.average_exchanges_saved == 0.0
        assert metrics.entities_affected == 0
        assert metrics.latest_events == []

    async def test_metrics_after_events(self, harvester: CompactionHarvester) -> None:
        """Metrics correctly aggregate after recording events."""
        await harvester.record_compaction(
            entity_name="alpha", session_id="ses_001",
            before_count=50, after_count=20, triggered_by="test",
        )
        await harvester.record_compaction(
            entity_name="alpha", session_id="ses_002",
            before_count=40, after_count=15, triggered_by="test",
        )
        
        metrics = harvester.get_metrics()
        assert metrics.total_events == 2
        assert metrics.total_exchanges_saved == 55  # 30 + 25
        assert metrics.average_exchanges_saved == 27.5
        assert metrics.entities_affected == 1

    async def test_entity_metrics(self, harvester: CompactionHarvester) -> None:
        """Entity-scoped metrics return correct values."""
        await harvester.record_compaction(
            entity_name="alpha", session_id="ses_001",
            before_count=50, after_count=20, triggered_by="test",
        )
        await harvester.record_compaction(
            entity_name="beta", session_id="ses_002",
            before_count=100, after_count=30, triggered_by="test",
        )
        
        alpha_metrics = harvester.get_entity_metrics("alpha")
        assert alpha_metrics.total_events == 1
        assert alpha_metrics.total_exchanges_saved == 30
        
        beta_metrics = harvester.get_entity_metrics("beta")
        assert beta_metrics.total_events == 1
        assert beta_metrics.total_exchanges_saved == 70

    def test_entity_metrics_unknown(self, harvester: CompactionHarvester) -> None:
        """Unknown entity returns zeroed metrics."""
        metrics = harvester.get_entity_metrics("nonexistent")
        assert metrics.total_events == 0

    async def test_metrics_window(self, harvester: CompactionHarvester) -> None:
        """Metrics window limits the number of retained events."""
        from omega.oracle.compaction_harvester import METRICS_WINDOW
        
        # Record more than window size
        for i in range(METRICS_WINDOW + 10):
            await harvester.record_compaction(
                entity_name="alpha", session_id=f"ses_{i:03d}",
                before_count=40, after_count=20, triggered_by="test",
            )
        
        events = harvester.get_recent_events(limit=200)
        assert len(events) <= METRICS_WINDOW

    async def test_to_dict(self, harvester: CompactionHarvester) -> None:
        """Serialization to dict produces expected structure."""
        await harvester.record_compaction(
            entity_name="test", session_id="ses_001",
            before_count=45, after_count=20, triggered_by="test",
        )
        
        data = harvester.to_dict()
        assert isinstance(data, dict)
        assert "metrics_summary" in data
        assert "config" in data
        assert "recent_events" in data
        assert data["metrics_summary"]["total_compactions"] == 1
        assert data["config"]["max_exchanges"] == 30
        assert len(data["recent_events"]) == 1

    def test_to_dict_empty(self, harvester: CompactionHarvester) -> None:
        """Empty harvester serializes without error."""
        data = harvester.to_dict()
        assert data["metrics_summary"]["total_compactions"] == 0
        assert data["recent_events"] == []

    def test_get_metrics_returns_compactionmetrics(self, harvester: CompactionHarvester) -> None:
        """M21: Contract test — get_metrics always returns a CompactionMetrics."""
        metrics = harvester.get_metrics()
        assert isinstance(metrics, CompactionMetrics)
        assert isinstance(metrics.total_events, int)

    def test_assess_session_returns_session_sizereport(self, harvester: CompactionHarvester) -> None:
        """M21: Contract test — assess_session returns SessionSizeReport."""
        report = harvester.assess_session("test", "ses_001", 10)
        assert isinstance(report, SessionSizeReport)

    def test_get_recent_events_returns_list(self, harvester: CompactionHarvester) -> None:
        """M21: Contract test — get_recent_events always returns a list."""
        events = harvester.get_recent_events()
        assert isinstance(events, list)

    async def test_duration_ms_preserved(self, harvester: CompactionHarvester) -> None:
        """Duration measurement is preserved in the event."""
        await harvester.record_compaction(
            entity_name="test", session_id="ses_001",
            before_count=50, after_count=20,
            triggered_by="test", duration_ms=150.5,
        )
        
        events = harvester.get_recent_events()
        assert events[0].duration_ms == 150.5


# ── Singleton Tests ──────────────────────────────────────────────────

class TestSingleton:

    def teardown_method(self) -> None:
        reset_harvester()

    def test_get_harvester_singleton(self) -> None:
        """get_harvester always returns the same instance."""
        h1 = get_harvester()
        h2 = get_harvester()
        assert h1 is h2

    def test_reset_harvester(self) -> None:
        """reset_harvester creates a new instance on next access."""
        h1 = get_harvester()
        reset_harvester()
        h2 = get_harvester()
        assert h1 is not h2
