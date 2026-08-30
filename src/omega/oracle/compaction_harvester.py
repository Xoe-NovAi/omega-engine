# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-COMPACTION-HARVESTER-v1.0.0
"""
COMPACTION HARVESTER
Role: Automated background trigger for memory compaction.
Monitors all active entity sessions and triggers compaction for those
exceeding the sovereign history threshold.

Follows Mandate 18 (Token Efficiency) and Mandate 1 (AnyIO Absolute).
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

import anyio

logger = logging.getLogger("compaction_harvester")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default max exchanges before compaction is triggered
DEFAULT_MAX_EXCHANGES = 30
# Default warn threshold (percentage of max)
DEFAULT_WARN_THRESHOLD = 25
# Maximum events retained in memory for metrics
METRICS_WINDOW = 500

# ============================================================================
# MODELS
# ============================================================================


@dataclass
class CompactionEvent:
    """A recorded compaction event."""

    entity_name: str
    session_id: str
    before_count: int
    after_count: int
    triggered_by: str = "auto"
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None

    @property
    def exchanges_saved(self) -> int:
        return self.before_count - self.after_count


@dataclass
class SessionSizeReport:
    """Report on a session's size relative to compaction thresholds."""

    entity_name: str
    session_id: str
    exchange_count: int
    needs_compaction: bool
    near_threshold: bool


@dataclass
class CompactionMetrics:
    """Aggregated metrics for compaction activity."""

    total_events: int = 0
    total_exchanges_saved: int = 0
    average_exchanges_saved: float = 0.0
    entities_affected: int = 0
    latest_events: List[CompactionEvent] = field(default_factory=list)


# ============================================================================
# HARVESTER ENGINE
# ============================================================================


class CompactionHarvester:
    """
    Background agent that proactively harvests bloated sessions
    and triggers compaction to maintain token efficiency.
    """

    def __init__(
        self,
        max_exchanges: int = DEFAULT_MAX_EXCHANGES,
        warn_threshold: int = DEFAULT_WARN_THRESHOLD,
    ):
        self._max_exchanges = max_exchanges
        # Clamp warn_threshold to max_exchanges
        self._warn_threshold = min(warn_threshold, max_exchanges)
        self._events: List[CompactionEvent] = []
        self._running = False

    # ── Property setters with clamping ─────────────────────────────────

    @property
    def max_exchanges(self) -> int:
        return self._max_exchanges

    @max_exchanges.setter
    def max_exchanges(self, value: int) -> None:
        self._max_exchanges = value
        # Clamp warn_threshold if it exceeds new max
        if self._warn_threshold > value:
            self._warn_threshold = value

    @property
    def warn_threshold(self) -> int:
        return self._warn_threshold

    @warn_threshold.setter
    def warn_threshold(self, value: int) -> None:
        self._warn_threshold = min(value, self._max_exchanges)

    # ── Session Assessment ─────────────────────────────────────────────

    def assess_session(
        self, entity_name: str, session_id: str, exchange_count: int
    ) -> SessionSizeReport:
        """Assess whether a session needs compaction."""
        needs_compaction = exchange_count > self.max_exchanges
        near_threshold = exchange_count >= self.warn_threshold
        return SessionSizeReport(
            entity_name=entity_name,
            session_id=session_id,
            exchange_count=exchange_count,
            needs_compaction=needs_compaction,
            near_threshold=near_threshold,
        )

    # ── Event Recording ────────────────────────────────────────────────

    async def record_compaction(
        self,
        entity_name: str,
        session_id: str,
        before_count: int,
        after_count: int,
        triggered_by: str = "auto",
        duration_ms: Optional[float] = None,
    ) -> CompactionEvent:
        """Record a compaction event."""
        event = CompactionEvent(
            entity_name=entity_name,
            session_id=session_id,
            before_count=before_count,
            after_count=after_count,
            triggered_by=triggered_by,
            duration_ms=duration_ms,
        )
        self._events.append(event)

        # Trim to window size
        if len(self._events) > METRICS_WINDOW:
            self._events = self._events[-METRICS_WINDOW:]

        return event

    def get_recent_events(
        self,
        entity_name: Optional[str] = None,
        limit: int = 50,
    ) -> List[CompactionEvent]:
        """Get recent events, optionally filtered by entity."""
        events = self._events
        if entity_name:
            events = [e for e in events if e.entity_name == entity_name]
        # Return most recent first
        return list(reversed(events[-limit:]))

    # ── Metrics ────────────────────────────────────────────────────────

    def get_metrics(self, entity_name: Optional[str] = None) -> CompactionMetrics:
        """Get aggregated compaction metrics."""
        events = self._events
        if entity_name:
            events = [e for e in events if e.entity_name == entity_name]

        if not events:
            return CompactionMetrics()

        total_saved = sum(e.exchanges_saved for e in events)
        entities = set(e.entity_name for e in events)

        return CompactionMetrics(
            total_events=len(events),
            total_exchanges_saved=total_saved,
            average_exchanges_saved=total_saved / len(events) if events else 0.0,
            entities_affected=len(entities),
            latest_events=list(reversed(events[-10:])),
        )

    def get_entity_metrics(self, entity_name: str) -> CompactionMetrics:
        """Get metrics scoped to a specific entity."""
        return self.get_metrics(entity_name=entity_name)

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the harvester state to a dict."""
        metrics = self.get_metrics()
        return {
            "metrics_summary": {
                "total_compactions": metrics.total_events,
                "total_exchanges_saved": metrics.total_exchanges_saved,
                "average_exchanges_saved": metrics.average_exchanges_saved,
                "entities_affected": metrics.entities_affected,
            },
            "config": {
                "max_exchanges": self.max_exchanges,
                "warn_threshold": self.warn_threshold,
            },
            "recent_events": [
                {
                    "entity_name": e.entity_name,
                    "session_id": e.session_id,
                    "before_count": e.before_count,
                    "after_count": e.after_count,
                    "exchanges_saved": e.exchanges_saved,
                    "triggered_by": e.triggered_by,
                    "timestamp": e.timestamp,
                    "duration_ms": e.duration_ms,
                }
                for e in self.get_recent_events(limit=50)
            ],
        }

    # ── Background Loop (Optional) ─────────────────────────────────────

    async def start(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start the background harvest loop (optional, for proactive harvesting)."""
        self._running = True
        task_group.start_soon(self._harvest_loop)
        logger.info(
            "CompactionHarvester online — max=%d warn=%d",
            self.max_exchanges,
            self.warn_threshold,
        )

    async def stop(self) -> None:
        """Stop the harvester."""
        self._running = False

    async def _harvest_loop(self) -> None:
        """Periodic loop to scan and compact bloated sessions."""
        while self._running:
            try:
                # Proactive harvesting would go here
                # For now, the harvester is event-driven via record_compaction()
                pass
            except Exception as e:
                logger.error("Compaction harvest failed: %s", e, exc_info=True)

            await anyio.sleep(1800.0)  # 30 minutes


# ============================================================================
# SINGLETON
# ============================================================================

_harvester: Optional[CompactionHarvester] = None


def get_harvester() -> CompactionHarvester:
    """Get the singleton CompactionHarvester instance."""
    global _harvester
    if _harvester is None:
        _harvester = CompactionHarvester()
    return _harvester


def reset_harvester() -> None:
    """Reset the singleton (for testing)."""
    global _harvester
    _harvester = None


# ============================================================================
# INTEGRATION
# ============================================================================


async def start_compaction_harvester(task_group: anyio.abc.TaskGroup):
    """Helper to start the harvester within a TaskGroup."""
    harvester = get_harvester()
    await harvester.start(task_group)
    return harvester
