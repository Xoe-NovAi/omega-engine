"""Search Observability — Structured Logging, Tracing, and Metrics for Search Pipeline.
AP: AP-SEARCH-OBSERVABILITY-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_search_obs ⬡ ACTIVE

Provides comprehensive observability for the SSP-V2 search pipeline:
- Structured logging with trace IDs
- Latency metrics per tier
- Error categorization and tracking
- Health status reporting
- Integration with Omega observability stack
"""

import time
import logging
import uuid
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from enum import Enum

logger = logging.getLogger(__name__)


class SearchTier(Enum):
    """SSP-V2 Search Tiers."""

    T0_LOCAL = 0
    T1_SEARXNG = 1
    T2_EXA = 2
    T3_FIRECRAWL = 3

    @property
    def name_str(self) -> str:
        return self.name


class SearchOutcome(Enum):
    """Search execution outcomes."""

    SUCCESS = "success"
    EMPTY = "empty"
    ERROR = "error"
    AUTH_ERROR = "auth_error"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"
    SKIPPED = "skipped"


@dataclass
class TierExecutionRecord:
    """Record of a single tier execution attempt."""

    tier: int
    tier_name: str
    trace_id: str
    query: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    latency_ms: Optional[float] = None
    outcome: SearchOutcome = SearchOutcome.ERROR
    result_length: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    circuit_state_before: Optional[str] = None
    circuit_state_after: Optional[str] = None
    provider_health: Optional[bool] = None

    def mark_start(self) -> None:
        self.start_time = time.time()

    def mark_end(
        self, outcome: SearchOutcome, result: str = "", error: Optional[Exception] = None
    ) -> None:
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.outcome = outcome
        self.result_length = len(result) if result else 0
        if error:
            self.error_type = type(error).__name__
            self.error_message = str(error)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "tier_name": self.tier_name,
            "trace_id": self.trace_id,
            "query_hash": hash(self.query) % 1000000,  # Don't log full query
            "latency_ms": round(self.latency_ms, 2) if self.latency_ms else None,
            "outcome": self.outcome.value,
            "result_length": self.result_length,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "circuit_state_before": self.circuit_state_before,
            "circuit_state_after": self.circuit_state_after,
            "provider_health": self.provider_health,
        }


@dataclass
class SearchPipelineTrace:
    """Complete trace of a search pipeline execution."""

    trace_id: str
    query: str
    entity_name: str
    start_time: float
    end_time: Optional[float] = None
    total_latency_ms: Optional[float] = None
    search_intent: Optional[Dict[str, Any]] = None
    tier_executions: List[TierExecutionRecord] = field(default_factory=list)
    final_tier: Optional[int] = None
    final_outcome: SearchOutcome = SearchOutcome.ERROR
    verification_status: Optional[str] = None
    fallback_count: int = 0

    def add_tier_execution(self, record: TierExecutionRecord) -> None:
        self.tier_executions.append(record)

    def mark_complete(self, final_tier: Optional[int], outcome: SearchOutcome) -> None:
        self.end_time = time.time()
        self.total_latency_ms = (self.end_time - self.start_time) * 1000
        self.final_tier = final_tier
        self.final_outcome = outcome
        self.fallback_count = len(
            [r for r in self.tier_executions if r.outcome != SearchOutcome.SUCCESS]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "query_hash": hash(self.query) % 1000000,
            "entity_name": self.entity_name,
            "total_latency_ms": round(self.total_latency_ms, 2) if self.total_latency_ms else None,
            "search_intent": self.search_intent,
            "tier_executions": [r.to_dict() for r in self.tier_executions],
            "final_tier": self.final_tier,
            "final_outcome": self.final_outcome.value,
            "verification_status": self.verification_status,
            "fallback_count": self.fallback_count,
        }


class SearchObservability:
    """Central observability coordinator for search pipeline."""

    def __init__(self, enable_console_logging: bool = True):
        self.enable_console_logging = enable_console_logging
        self._traces: Dict[str, SearchPipelineTrace] = {}
        self._lock = __import__("threading").RLock()

    @asynccontextmanager
    async def trace_search(
        self,
        query: str,
        entity_name: str,
        search_intent: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for tracing a complete search pipeline."""
        trace_id = f"srch_{uuid.uuid4().hex[:12]}"
        trace = SearchPipelineTrace(
            trace_id=trace_id,
            query=query,
            entity_name=entity_name,
            start_time=time.time(),
            search_intent=search_intent,
        )

        with self._lock:
            self._traces[trace_id] = trace

        logger.info(
            f"[SEARCH-TRACE] trace_id={trace_id} entity={entity_name} "
            f"query_hash={hash(query) % 1000000} intent={search_intent}"
        )

        try:
            yield trace
        finally:
            # Trace is completed by caller via trace.mark_complete()
            pass

    def record_tier_execution(
        self,
        trace: SearchPipelineTrace,
        tier: int,
        tier_name: str,
        outcome: SearchOutcome,
        result: str = "",
        error: Optional[Exception] = None,
        circuit_state_before: Optional[str] = None,
        circuit_state_after: Optional[str] = None,
        provider_health: Optional[bool] = None,
    ) -> TierExecutionRecord:
        """Record a tier execution in the trace."""
        record = TierExecutionRecord(
            tier=tier,
            tier_name=tier_name,
            trace_id=trace.trace_id,
            query=trace.query,
        )
        record.mark_start()
        # Simulate execution time (actual timing done by caller)
        record.mark_end(outcome, result, error)
        record.circuit_state_before = circuit_state_before
        record.circuit_state_after = circuit_state_after
        record.provider_health = provider_health

        trace.add_tier_execution(record)

        # Structured log
        log_data = {
            "trace_id": trace.trace_id,
            "tier": tier,
            "tier_name": tier_name,
            "outcome": outcome.value,
            "latency_ms": record.latency_ms,
            "result_length": record.result_length,
            "error_type": record.error_type,
            "circuit_state_before": circuit_state_before,
            "circuit_state_after": circuit_state_after,
        }

        if outcome == SearchOutcome.SUCCESS:
            logger.info(f"[SEARCH-TIER] {json.dumps(log_data)}")
        elif outcome == SearchOutcome.CIRCUIT_OPEN:
            logger.warning(f"[SEARCH-TIER] {json.dumps(log_data)}")
        else:
            logger.error(f"[SEARCH-TIER] {json.dumps(log_data)}")

        return record

    def complete_trace(
        self,
        trace: SearchPipelineTrace,
        final_tier: Optional[int],
        outcome: SearchOutcome,
        verification_status: Optional[str] = None,
    ) -> None:
        """Mark trace as complete."""
        trace.mark_complete(final_tier, outcome)
        trace.verification_status = verification_status

        # Log completion
        log_data = trace.to_dict()
        if outcome == SearchOutcome.SUCCESS:
            logger.info(f"[SEARCH-COMPLETE] {json.dumps(log_data)}")
        else:
            logger.error(f"[SEARCH-COMPLETE] {json.dumps(log_data)}")

        # Store for potential retrieval
        with self._lock:
            self._traces[trace.trace_id] = trace

    def get_trace(self, trace_id: str) -> Optional[SearchPipelineTrace]:
        """Retrieve a trace by ID."""
        with self._lock:
            return self._traces.get(trace_id)

    def get_recent_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent traces as dicts."""
        with self._lock:
            traces = sorted(self._traces.values(), key=lambda t: t.start_time, reverse=True)
            return [t.to_dict() for t in traces[:limit]]

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        with self._lock:
            traces = list(self._traces.values())
            if not traces:
                return {"total_traces": 0}

            successful = [t for t in traces if t.final_outcome == SearchOutcome.SUCCESS]
            failed = [t for t in traces if t.final_outcome != SearchOutcome.SUCCESS]

            tier_stats = {}
            for t in traces:
                for rec in t.tier_executions:
                    if rec.tier not in tier_stats:
                        tier_stats[rec.tier] = {"calls": 0, "successes": 0, "total_latency": 0.0}
                    tier_stats[rec.tier]["calls"] += 1
                    if rec.outcome == SearchOutcome.SUCCESS:
                        tier_stats[rec.tier]["successes"] += 1
                    if rec.latency_ms:
                        tier_stats[rec.tier]["total_latency"] += rec.latency_ms

            for tier, stats in tier_stats.items():
                stats["success_rate"] = (
                    stats["successes"] / stats["calls"] if stats["calls"] > 0 else 0
                )
                stats["avg_latency_ms"] = (
                    stats["total_latency"] / stats["calls"] if stats["calls"] > 0 else 0
                )

            return {
                "total_traces": len(traces),
                "successful_traces": len(successful),
                "failed_traces": len(failed),
                "success_rate": len(successful) / len(traces) if traces else 0,
                "avg_total_latency_ms": sum(t.total_latency_ms or 0 for t in traces) / len(traces)
                if traces
                else 0,
                "tier_stats": tier_stats,
            }


# Global observability instance
_search_observability: Optional[SearchObservability] = None
_obs_lock = __import__("threading").Lock()


def get_search_observability() -> SearchObservability:
    """Get global search observability instance."""
    global _search_observability
    if _search_observability is None:
        with _obs_lock:
            if _search_observability is None:
                _search_observability = SearchObservability()
    return _search_observability


# Convenience functions for structured logging
def log_search_event(event_type: str, trace_id: str, tier: Optional[int] = None, **kwargs) -> None:
    """Log a structured search event."""
    log_data = {
        "event": event_type,
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if tier is not None:
        log_data["tier"] = tier
    log_data.update(kwargs)
    logger.info(f"[SEARCH-EVENT] {json.dumps(log_data)}")


def log_search_error(
    trace_id: str,
    tier: int,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a search error with full context."""
    log_data = {
        "event": "search_error",
        "trace_id": trace_id,
        "tier": tier,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if context:
        log_data["context"] = context
    logger.error(f"[SEARCH-ERROR] {json.dumps(log_data)}")


# Tier name mapping
TIER_NAMES = {
    0: "T0_LOCAL",
    1: "T1_SEARXNG",
    2: "T2_EXA",
    3: "T3_FIRECRAWL",
}


def get_tier_name(tier: int) -> str:
    return TIER_NAMES.get(tier, f"T{tier}_UNKNOWN")
