# AP: AP-COMPACTION-HARVESTER-v1.0.0
# 🔱 Omega Engine — Compaction Harvester
# ⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ COMPACTION-HARVESTER
#
# [id-soft: doom-1993] Thinker Chain Sweep — automated reaping of stale state
#     Doom's P_Ticker() sweeps all thinkers and removes sentinel entries
#     every frame. The CompactionHarvester similarly sweeps all sessions
#     and marks oversize ones for compaction — not every "frame" (query),
#     but every N interactions or on explicit trigger.
#
# Automated compaction monitoring and metrics reporting.
# Tracks session sizes and triggers pre-emptive compaction when
# sessions exceed configurable thresholds.
#
# Integration:
#   - Hooked into Oracle._somatic_flush() and MemoryStore._compact()
#   - Reports metrics via observability engine
#   - Maintains a rolling window of compaction activity
#
# M1: AnyIO compliance — no asyncio, all I/O via anyio.to_thread.run_sync
# M9: Error Integrity — typed errors, no bare except
# M12: Queue Integrity — every compaction event is logged

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

# Default max exchanges before compaction is flagged
DEFAULT_MAX_EXCHANGES: int = 30

# Default max exchanges before pre-emptive warning is issued
DEFAULT_WARN_THRESHOLD: int = 25

# Rolling window for metrics (number of compaction events to retain)
METRICS_WINDOW: int = 100

# Sources for the metrics report
SOURCE_ROUTINE = "routine_check"
SOURCE_TRIGGERED = "triggered_compaction"
SOURCE_MEMORYSTORE = "memory_store_compact"


@dataclass
class CompactionEvent:
    """A single compaction event recorded by the harvester.
    
    Attributes:
        entity_name: The entity whose session was compacted.
        session_id: The session that was compacted.
        before_count: Number of exchanges before compaction.
        after_count: Number of exchanges after compaction.
        triggered_by: What triggered the compaction.
        timestamp: Unix timestamp of the event.
        duration_ms: How long the compaction took (if measured).
    """
    entity_name: str
    session_id: str
    before_count: int
    after_count: int
    triggered_by: str = SOURCE_TRIGGERED
    timestamp: float = 0.0
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def exchanges_saved(self) -> int:
        """Number of exchanges removed during compaction."""
        return self.before_count - self.after_count


@dataclass
class SessionSizeReport:
    """Report on the size of a single session."""
    entity_name: str
    session_id: str
    exchange_count: int
    needs_compaction: bool
    near_threshold: bool


@dataclass
class CompactionMetrics:
    """Aggregate compaction metrics for a given scope.
    
    Attributes:
        total_events: Total compaction events recorded.
        total_exchanges_saved: Sum of exchanges removed across all events.
        average_exchanges_saved: Average exchanges saved per event.
        entities_affected: Number of unique entities affected.
        latest_events: Most recent compaction events (ordered by time).
    """
    total_events: int = 0
    total_exchanges_saved: int = 0
    average_exchanges_saved: float = 0.0
    entities_affected: int = 0
    latest_events: List[CompactionEvent] = field(default_factory=list)


class CompactionHarvester:
    """Monitors session sizes and reports compaction metrics.
    
    Not directly responsible for performing compaction (that's handled by
    MemoryStore._compact()). Instead, this harvester:
    
    1. Analyzes session sizes across entities to identify compaction candidates.
    2. Records compaction events that happen elsewhere (MemoryStore, Oracle).
    3. Reports aggregate metrics for observability and decision-making.
    
    Usage:
        harvester = CompactionHarvester(max_exchanges=30)
        
        # Record a compaction event that happened
        await harvester.record_compaction(
            entity_name="jem",
            session_id="ses_20260704_jem_001",
            before_count=45,
            after_count=20,
        )
        
        # Check if a session needs compaction
        report = harvester.assess_session("jem", "ses_001", 55)
        if report.needs_compaction:
            logger.warning("Session %s needs compaction (%d exchanges)",
                           report.session_id, report.exchange_count)
        
        # Get aggregate metrics
        metrics = harvester.get_metrics()
    """

    def __init__(
        self,
        max_exchanges: int = DEFAULT_MAX_EXCHANGES,
        warn_threshold: int = DEFAULT_WARN_THRESHOLD,
    ) -> None:
        """Initialize the CompactionHarvester.
        
        Args:
            max_exchanges: Max exchanges before compaction is flagged.
                Defaults to 30.
            warn_threshold: Exchange count at which a warning is issued.
                Must be <= max_exchanges. Defaults to 25.
        """
        self._max_exchanges = max_exchanges
        self._warn_threshold = min(warn_threshold, max_exchanges)
        self._events: List[CompactionEvent] = []

    @property
    def max_exchanges(self) -> int:
        """Maximum exchanges before a session is flagged for compaction."""
        return self._max_exchanges

    @max_exchanges.setter
    def max_exchanges(self, value: int) -> None:
        """Set the maximum exchanges threshold.
        
        Also adjusts warn_threshold if it exceeds the new max.
        """
        self._max_exchanges = value
        if self._warn_threshold > value:
            self._warn_threshold = value

    @property
    def warn_threshold(self) -> int:
        """Exchange count at which a warning is issued."""
        return self._warn_threshold

    def assess_session(
        self,
        entity_name: str,
        session_id: str,
        exchange_count: int,
    ) -> SessionSizeReport:
        """Assess whether a session needs compaction.
        
        Args:
            entity_name: The entity name.
            session_id: The session ID.
            exchange_count: The current number of exchanges.
            
        Returns:
            SessionSizeReport with compaction flags.
        """
        return SessionSizeReport(
            entity_name=entity_name,
            session_id=session_id,
            exchange_count=exchange_count,
            needs_compaction=exchange_count > self._max_exchanges,
            near_threshold=exchange_count >= self._warn_threshold,
        )

    async def record_compaction(
        self,
        entity_name: str,
        session_id: str,
        before_count: int,
        after_count: int,
        triggered_by: str = SOURCE_TRIGGERED,
        duration_ms: float = 0.0,
    ) -> None:
        """Record a compaction event.
        
        Args:
            entity_name: The entity whose session was compacted.
            session_id: The session that was compacted.
            before_count: Number of exchanges before compaction.
            after_count: Number of exchanges after compaction.
            triggered_by: Source of the trigger.
            duration_ms: How long the compaction took.
        """
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
        
        logger.info(
            "Compaction recorded: %s/%s %d→%d (-%d) [%s]",
            entity_name, session_id, before_count, after_count,
            event.exchanges_saved, triggered_by,
        )

    def get_metrics(self) -> CompactionMetrics:
        """Get aggregate compaction metrics.
        
        Returns:
            CompactionMetrics with total events, exchanges saved, etc.
        """
        if not self._events:
            return CompactionMetrics()
        
        total_saved = sum(e.exchanges_saved for e in self._events)
        unique_entities = len(set(e.entity_name for e in self._events))
        
        # Most recent events first
        sorted_events = sorted(
            self._events, key=lambda e: e.timestamp, reverse=True
        )
        
        return CompactionMetrics(
            total_events=len(self._events),
            total_exchanges_saved=total_saved,
            average_exchanges_saved=round(total_saved / len(self._events), 1),
            entities_affected=unique_entities,
            latest_events=sorted_events[:10],
        )

    def get_recent_events(
        self,
        entity_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[CompactionEvent]:
        """Get recent compaction events, optionally filtered by entity.
        
        Args:
            entity_name: Optional filter — only return events for this entity.
            limit: Maximum number of events to return. Defaults to 20.
            
        Returns:
            List of CompactionEvent, most recent first.
        """
        filtered = self._events
        if entity_name:
            filtered = [e for e in filtered if e.entity_name == entity_name]
        
        sorted_filtered = sorted(
            filtered, key=lambda e: e.timestamp, reverse=True
        )
        return sorted_filtered[:limit]

    def get_entity_metrics(self, entity_name: str) -> CompactionMetrics:
        """Get compaction metrics for a specific entity.
        
        Args:
            entity_name: The entity to get metrics for.
            
        Returns:
            CompactionMetrics scoped to this entity.
        """
        entity_events = [e for e in self._events if e.entity_name == entity_name]
        
        if not entity_events:
            return CompactionMetrics()
        
        total_saved = sum(e.exchanges_saved for e in entity_events)
        sorted_events = sorted(
            entity_events, key=lambda e: e.timestamp, reverse=True
        )
        
        return CompactionMetrics(
            total_events=len(entity_events),
            total_exchanges_saved=total_saved,
            average_exchanges_saved=round(total_saved / len(entity_events), 1),
            entities_affected=1,
            latest_events=sorted_events[:10],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the harvester state to a dict for observability.
        
        Returns:
            Dict with metrics_summary and recent_events.
        """
        metrics = self.get_metrics()
        return {
            "metrics_summary": {
                "total_compactions": metrics.total_events,
                "total_exchanges_saved": metrics.total_exchanges_saved,
                "avg_exchanges_saved": metrics.average_exchanges_saved,
                "entities_affected": metrics.entities_affected,
            },
            "config": {
                "max_exchanges": self._max_exchanges,
                "warn_threshold": self._warn_threshold,
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
                }
                for e in metrics.latest_events
            ],
        }


# ── Singleton Convenience ───────────────────────────────────────────────

_harvester: Optional[CompactionHarvester] = None


def get_harvester() -> CompactionHarvester:
    """Get or create the singleton CompactionHarvester instance."""
    global _harvester
    if _harvester is None:
        _harvester = CompactionHarvester()
    return _harvester


def reset_harvester() -> None:
    """Reset the singleton harvester (for testing)."""
    global _harvester
    _harvester = None
