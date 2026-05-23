# 🔱 Omega Observability — Deep Logging, Tracking & Dataset Collection
# AP: AP-OBSERVABILITY-v1.0.0
# ICS: [NODE: MAAT | ARCHETYPE: SOPHIA | CONTEXT: OBSERVABILITY]
#
# Logs every query-response cycle with full provenance for:
#   - Real-time monitoring (console + Redis streams)
#   - Debugging and audit (file rotation)
#   - Fine-tuning dataset generation (JSONL export)
#
# Every interaction gets a trace_id that follows it through
# the entire Oracle → Entity → ModelGateway → Response pipeline.

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

logger = logging.getLogger(__name__)

# ── Storage paths ─────────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
LOG_DIR = DATA_DIR / "logs"
DATASET_DIR = DATA_DIR / "datasets"
TRACE_DIR = DATA_DIR / "traces"

for d in [LOG_DIR, DATASET_DIR, TRACE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Trace ID ──────────────────────────────────────────────────────────
def new_trace_id(parent_id: Optional[str] = None) -> str:
    """Generate a unique trace ID for an interaction cycle."""
    return f"trc_{uuid.uuid4().hex[:12]}"


# ── Event types ───────────────────────────────────────────────────────
class EventType:
    QUERY_RECEIVED = "query.received"
    SUMMON_DETECTED = "summon.detected"
    DOMAIN_ROUTED = "domain.routed"
    ENTITY_MATCHED = "entity.matched"
    MODEL_INVOKED = "model.invoked"
    MODEL_COMPLETED = "model.completed"
    BACKEND_FALLBACK = "backend.fallback"
    RESPONSE_DELIVERED = "response.delivered"
    ESCALATION = "escalation"
    IRIS_SPECULATIVE = "iris.speculative"
    BOUNDARY_VIOLATION = "boundary.violation"
    GNOSIS_REDACTION = "gnosis.redaction"
    ERROR = "error"
    # Worker events
    WORKER_START = "worker.start"
    WORKER_COMPLETE = "worker.complete"
    WORKER_UPDATE = "worker.update"
    WORKER_REPORT = "worker.report"
    # Tiered Pipeline / Mode events (Phase E)
    TIER_INVOKED = "tier.invoked"
    MODE_SWITCHED = "mode.switched"
    AGENT_DISPATCHED = "agent.dispatched"
    RESEARCH_COMPLETE = "research.complete"


# ── Observability Engine ──────────────────────────────────────────────
class ObservabilityEngine:
    """Central observability, logging, and dataset collection."""

    def __init__(self, enable_dataset_collection: bool = False):
        self.enable_dataset_collection = enable_dataset_collection
        self._session_id = uuid.uuid4().hex[:8]
        self._event_log: List[Dict[str, Any]] = []
        self._dataset: List[Dict[str, Any]] = []
        self._event_persist_enabled = os.environ.get("OMEGA_PERSIST_EVENTS", "true").lower() == "true"
        self._load_persisted_events()

    # ── Trace an entire interaction cycle ────────────────────────────
    def trace(self, trace_id: Optional[str] = None, parent_trace_id: Optional[str] = None) -> "TraceSession":
        """Start a new trace session for an interaction."""
        return TraceSession(
            trace_id=trace_id or new_trace_id(),
            engine=self,
            parent_trace_id=parent_trace_id
        )

    # ── Persist a single event to disk ─────────────────────────────
    def _persist_event(self, event: Dict[str, Any]) -> None:
        """Append event to daily JSONL file for survival across restarts."""
        if not self._event_persist_enabled:
            return
        # Skip in test mode to avoid polluting filesystem
        if os.environ.get("OMEGA_ENV") == "test":
            return
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            path = LOG_DIR / "events" / f"{today}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(path), "a", encoding="utf-8") as f:
                f.write(json.dumps(event, default=str) + "\n")
        except Exception as e:
            logger.warning(f"Failed to persist event: {e}")

    # ── Load recent events from disk ───────────────────────────────
    def _load_persisted_events(self, max_days: int = 7) -> None:
        """Load events from disk on startup to restore continuity."""
        # Skip in test mode to avoid cross-test contamination
        if os.environ.get("OMEGA_ENV") == "test":
            return
        events_dir = LOG_DIR / "events"
        if not events_dir.exists():
            return
        try:
            import datetime as dt
            today = dt.date.today()
            for i in range(max_days):
                day = (today - dt.timedelta(days=i)).isoformat()
                path = events_dir / f"{day}.jsonl"
                if path.exists():
                    with open(str(path)) as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    event = json.loads(line)
                                    self._event_log.append(event)
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            logger.warning(f"Failed to load persisted events: {e}")

    # ── Log an event ─────────────────────────────────────────────────
    def log_event(
        self,
        event_type: str,
        trace_id: str,
        data: Dict[str, Any],
        parent_trace_id: Optional[str] = None,
    ) -> None:
        """Log a single observability event."""
        event = {
            "event": event_type,
            "trace_id": trace_id,
            "parent_trace_id": parent_trace_id,
            "session_id": self._session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._event_log.append(event)
        self._persist_event(event)

        # Also log to standard logger
        logger.debug(f"[{trace_id}] {event_type}: {json.dumps(data, default=str)[:200]}")


    # ── Record a training example for fine-tuning ────────────────────
    def record_training_example(
        self,
        trace_id: str,
        query: str,
        system_prompt: str,
        response: str,
        entity: str,
        model: str,
        backend: str,
        confidence: float,
        latency_ms: float,
        session_id: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> None:
        """Save a query-response pair as a fine-tuning dataset entry."""
        if not self.enable_dataset_collection:
            return
        
        example = {
            "trace_id": trace_id,
            "session_id": session_id or self._session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
                {"role": "assistant", "content": response},
            ],
            "metadata": {
                "entity": entity,
                "model": model,
                "backend": backend,
                "confidence": confidence,
                "latency_ms": latency_ms,
                "rating": rating,
            },
        }
        self._dataset.append(example)

    # ── Persist dataset to disk ──────────────────────────────────────
    async def flush_dataset(self) -> Optional[Path]:
        """Write collected training examples to disk as JSONL."""
        if not self._dataset:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = DATASET_DIR / f"finetune_{timestamp}.jsonl"

        async with await anyio.open_file(path, mode="a", encoding="utf-8") as f:
            for example in self._dataset:
                await f.write(json.dumps(example, default=str) + "\n")

        count = len(self._dataset)
        self._dataset = []
        logger.info(f"Flushed {count} training examples to {path}")
        return path

    # ── Get recent events for monitoring ─────────────────────────────
    def recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._event_log[-limit:]

    # ── Stats ────────────────────────────────────────────────────────
    def stats(self) -> Dict[str, Any]:
        event_counts: Dict[str, int] = {}
        for event in self._event_log:
            event_counts[event["event"]] = event_counts.get(event["event"], 0) + 1
        return {
            "total_events": len(self._event_log),
            "dataset_size": len(self._dataset),
            "event_counts": event_counts,
            "session_id": self._session_id,
        }


class TraceSession:
    """A single interaction trace. Context manager for easy lifecycle."""

    def __init__(self, trace_id: str, engine: ObservabilityEngine, parent_trace_id: Optional[str] = None):
        self.trace_id = trace_id
        self.engine = engine
        self.parent_trace_id = parent_trace_id
        self.start_time: float = 0.0
        self.data: Dict[str, Any] = {}

    async def __aenter__(self) -> "TraceSession":
        self.start_time = time.monotonic()
        return self

    async def __aexit__(self, *args) -> None:
        self.data["total_latency_ms"] = (time.monotonic() - self.start_time) * 1000
        # Auto-flush dataset periodically (every 100 interactions)
        if len(self.engine._dataset) >= 100:
            await self.engine.flush_dataset()

    def log(self, event_type: str, **data) -> None:
        """Log an event within this trace."""
        self.engine.log_event(
            event_type, 
            self.trace_id, 
            data, 
            parent_trace_id=self.parent_trace_id
        )

    def record(
        self,
        query: str,
        system_prompt: str,
        response: str,
        entity: str,
        model: str,
        backend: str,
        confidence: float,
        session_id: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> None:
        """Record a training example from this trace."""
        latency_ms = (time.monotonic() - self.start_time) * 1000
        self.engine.record_training_example(
            trace_id=self.trace_id,
            query=query,
            system_prompt=system_prompt,
            response=response,
            entity=entity,
            model=model,
            backend=backend,
            confidence=confidence,
            latency_ms=latency_ms,
            rating=rating,
            session_id=session_id,
        )


# ── Module-level singleton ────────────────────────────────────────────
_engine: Optional[ObservabilityEngine] = None


def get_engine() -> ObservabilityEngine:
    global _engine
    if _engine is None:
        _engine = ObservabilityEngine()
    return _engine
