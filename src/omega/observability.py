# 🔱 Omega Observability — Deep Logging, Tracking & Dataset Collection
# AP: AP-OBSERVABILITY-v2.0.0
# ICS: [NODE: MAAT | ARCHETYPE: SOPHIA | CONTEXT: OBSERVABILITY]
#
# Logs every query-response cycle with full provenance for:
#   - Real-time monitoring (console + Redis streams)
#   - Debugging and audit (file rotation)
#   - Fine-tuning dataset generation (JSONL export)
#   - Forensic crash dump generation (Last Gasp protocol)
#
# Every interaction gets a trace_id that follows it through
# the entire Oracle → Entity → ModelGateway → Response pipeline.

import json
import logging
import os
import time
import traceback
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

logger = logging.getLogger(__name__)

# ── Structured JSON Logging Formatter ───────────────────────────────────

class JsonFormatter(logging.Formatter):
    """Structured JSON logging formatter.

    Outputs machine-parseable JSON log lines instead of text.
    Drop-in replacement for any logging.Formatter — zero code changes
    to existing logger calls.

    Example output:
    {"timestamp":"2026-06-01T12:00:00Z","level":"INFO","logger":"omega.hub","message":"server started","trace_id":"trc_abc123","extra":{"key":"val"}}
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            payload["exc_info"] = traceback.format_exception(*record.exc_info)
        for key in ("trace_id", "entity", "provider", "model"):
            val = getattr(record, key, None)
            if val:
                payload[key] = val
        return json.dumps(payload, default=str)


def setup_json_logging(logger_name: str = "omega") -> None:
    """Apply structured JSON logging to all loggers under the given name.

    Call once at engine startup. Existing logger calls continue to work.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    target = logging.getLogger(logger_name)
    target.handlers.clear()
    target.addHandler(handler)


# ── Storage paths ─────────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
LOG_DIR = DATA_DIR / "logs"
DATASET_DIR = DATA_DIR / "datasets"
TRACE_DIR = DATA_DIR / "traces"
CRASH_DIR = DATA_DIR / "crashes"

for d in [LOG_DIR, DATASET_DIR, TRACE_DIR, CRASH_DIR]:
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


# ── Forensics Manager (Last Gasp Protocol) ────────────────────────────

class ForensicsManager:
    """
    Last Gasp crash dump system. Implements the Crash Dump & Forensics
    Protocol defined in LOGGING_ERROR_HANDLING_ARCHITECTURE.md §6.

    On fatal error, captures a structured snapshot of engine state:
    - Error details (type, message, traceback)
    - Provider states (circuit breaker status)
    - Recent events (ring buffer of last 100)
    - System info (RSS, CPU, backend)
    """

    def __init__(
        self,
        crash_dir: Optional[Path] = None,
        max_recent_errors: int = 50,
        observability_engine: Optional["ObservabilityEngine"] = None,
    ):
        self._crash_dir = crash_dir or CRASH_DIR
        self._crash_dir.mkdir(parents=True, exist_ok=True)
        self._recent_errors: deque = deque(maxlen=max_recent_errors)
        self._has_crashed = False
        self._obs_engine = observability_engine
        self._lock = anyio.Lock()

    def record_error(
        self,
        error: Exception,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an error for potential crash dump.

        Thread-safe recording of error metadata into a ring buffer.
        """
        self._recent_errors.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error)[:500],
            "traceback": traceback.format_exc()[:2000],
            "trace_id": trace_id or "unknown",
            "context": context or {},
        })

    async def snapshot(
        self,
        reason: str = "manual",
        error: Optional[Exception] = None,
        trace_id: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate a forensic crash dump snapshot.

        Collects error details, engine state, recent events, and system
        info into a JSON file at data/crashes/crash_{timestamp}_{trace_id}.json.
        """
        self._has_crashed = True

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tid = trace_id or "unknown"
        filename = f"crash_{timestamp}_{tid}.json"
        path = self._crash_dir / filename

        dump = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": tid,
            "reason": reason,
            "error": None,
            "engine_state": await self._collect_engine_state(),
            "recent_errors": list(self._recent_errors),
            "system_info": self._collect_system_info(),
            "extra_context": extra_context or {},
        }

        if error:
            dump["error"] = {
                "type": type(error).__name__,
                "message": str(error)[:1000],
                "traceback": traceback.format_exc()[:5000],
            }

        atomic_path = path.with_suffix(".tmp")
        try:
            with open(str(atomic_path), "w", encoding="utf-8") as f:
                json.dump(dump, f, default=str, indent=2)
            atomic_path.rename(path)
            logger.critical(f"Crash dump written to {path}")
        except Exception as e:
            logger.error(f"Failed to write crash dump: {e}")

        return path

    async def _collect_engine_state(self) -> Dict[str, Any]:
        """Collect current engine state for crash dump.

        Safe to call even if engine components are not fully initialized.
        """
        state: Dict[str, Any] = {
            "providers_available": 0,
            "circuit_breakers_open": [],
            "memory_warm_count": 0,
            "memory_hot_count": 0,
            "has_crashed": self._has_crashed,
        }

        if self._obs_engine:
            state["total_events"] = len(self._obs_engine._event_log)
            state["dataset_size"] = len(self._obs_engine._dataset)

        try:
            from omega.oracle.model_gateway import ModelGateway
            gw = ModelGateway()
            providers = gw.providers if hasattr(gw, 'providers') else []
            state["providers_count"] = len(providers)
            state["providers_available"] = len([
                p for p in providers
                if hasattr(p, 'is_available') and p.is_available
            ])
        except Exception:
            pass

        try:
            import psutil
            proc = psutil.Process()
            state["rss_mb"] = proc.memory_info().rss / 1024 / 1024
        except ImportError:
            try:
                with open("/proc/self/status") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            parts = line.split()
                            if len(parts) >= 2:
                                state["rss_mb"] = int(parts[1]) / 1024
                            break
            except Exception:
                pass

        return state

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system-level info for crash dump.

        Lightweight, synchronous — safe to call from signal handlers.
        """
        info: Dict[str, Any] = {
            "anyio_backend": self._detect_anyio_backend(),
            "timestamp": time.time(),
        }
        try:
            import psutil
            info["rss_mb"] = psutil.Process().memory_info().rss / 1024 / 1024
            info["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        except ImportError:
            pass
        return info

    @staticmethod
    def _detect_anyio_backend() -> str:
        """Detect the running anyio backend in a portable way.

        Uses sniffio (anyio's internal backend detector) first,
        falls back gracefully.
        """
        try:
            import sniffio
            return sniffio.current_async_library()
        except Exception:
            pass
        return "unknown"

    def check_recovery(self) -> Optional[Dict[str, Any]]:
        """Check for crash dumps from previous runs.

        Called at engine startup. If a crash dump is found:
        1. Load the most recent dump
        2. Log recovery info
        3. Archive the dump to data/crashes/archived/
        4. Return the dump contents for further analysis

        Returns the most recent crash dump dict, or None if clean shutdown.
        """
        crash_files = sorted(self._crash_dir.glob("crash_*.json"))
        if not crash_files:
            return None

        latest = crash_files[-1]
        try:
            with open(str(latest), "r") as f:
                dump = json.load(f)

            error_info = dump.get("error", {})
            logger.info(
                f"Engine recovered from crash at {dump.get('timestamp', 'unknown')} — "
                f"{error_info.get('type', 'Unknown')}: {error_info.get('message', 'No message')}"
            )

            archive_dir = self._crash_dir / "archived"
            archive_dir.mkdir(parents=True, exist_ok=True)
            archived = archive_dir / latest.name
            latest.rename(archived)
            logger.info(f"Crash dump archived to {archived}")

            return dump
        except Exception as e:
            logger.warning(f"Failed to process crash dump {latest}: {e}")
            return None

    async def replay(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Reconstruct the sequence of events that led to a crash.

        Loads the crash dump with the given trace_id, then gathers all
        persisted log events with that trace_id to rebuild the timeline.
        """
        crash_files = sorted(self._crash_dir.glob(f"crash_*_{trace_id}.json"))
        if not crash_files:
            crash_files = sorted(self._crash_dir.glob("crash_*.json"))
        if not crash_files:
            return None

        latest = crash_files[-1]
        try:
            with open(str(latest), "r") as f:
                dump = json.load(f)
        except Exception as e:
            logger.warning("Failed to load crash dump for replay: %s", e)
            return None

        events_path = DATA_DIR / "logs" / "events"
        timeline = []
        if events_path.exists():
            for f in sorted(events_path.glob("*.jsonl")):
                try:
                    with open(str(f)) as fh:
                        for line in fh:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                event = json.loads(line)
                                if event.get("trace_id") == trace_id:
                                    timeline.append(event)
                            except json.JSONDecodeError:
                                continue
                except Exception:
                    continue

        return {
            "crash_dump": dump,
            "timeline": sorted(timeline, key=lambda e: e.get("timestamp", "")),
            "total_events_in_trace": len(timeline),
        }

    async def learn(self, trace_id: str, entity_name: str = "SOPHIA") -> Optional[str]:
        """Extract a lesson from a crash and append to the entity's soul.yaml.

        Returns the lesson string if written successfully.
        """
        dump = await self.replay(trace_id)
        if not dump:
            return None

        crash = dump["crash_dump"]
        error_info = crash.get("error", {})
        reason = crash.get("reason", "unknown")

        lesson = (
            f"Recovered from {error_info.get('type', 'error')}: "
            f"{error_info.get('message', 'unknown')[:200]} "
            f"(reason: {reason})"
        )

        soul_path = DATA_DIR / "entities" / entity_name / "soul.yaml"
        if soul_path.exists():
            try:
                import yaml
                with open(str(soul_path)) as f:
                    soul = yaml.safe_load(f) or {}
                lessons = soul.setdefault("lessons", [])
                if isinstance(lessons, list):
                    lessons.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "trace_id": trace_id,
                        "lesson": lesson,
                    })
                    if len(lessons) > 100:
                        lessons[:] = lessons[-100:]
                    with open(str(soul_path), "w") as f:
                        yaml.safe_dump(soul, f, default_flow_style=False)
                logger.info("Learned from crash %s: %s", trace_id, lesson)
                return lesson
            except Exception as e:
                logger.warning("Failed to write lesson to soul.yaml: %s", e)
        return lesson

    @property
    def recent_errors(self) -> List[Dict[str, Any]]:
        return list(self._recent_errors)

    @property
    def has_crashed(self) -> bool:
        return self._has_crashed


# ── Observability Engine ──────────────────────────────────────────────
class ObservabilityEngine:
    """Central observability, logging, dataset collection, and forensics."""

    def __init__(
        self,
        enable_dataset_collection: bool = False,
        forensics_manager: Optional[ForensicsManager] = None,
    ):
        self.enable_dataset_collection = enable_dataset_collection
        self._session_id = uuid.uuid4().hex[:8]
        self._event_log: deque = deque(maxlen=1000)
        self._dataset: List[Dict[str, Any]] = []
        self._event_persist_enabled = os.environ.get("OMEGA_PERSIST_EVENTS", "true").lower() == "true"
        self._load_persisted_events()

        # Forensics / Crash Dump support
        self._forensics = forensics_manager or ForensicsManager(
            observability_engine=self,
        )
        self._last_crash: Optional[Dict[str, Any]] = self._forensics.check_recovery()

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
    def clear_log(self) -> None:
        """Clear the in-memory event log. Useful for testing."""
        self._event_log = []

    def _load_persisted_events(self, max_days: int = 7) -> None:
        """Load events from disk on startup to restore continuity.
        Events are skipped in test mode to prevent cross-test contamination.
        """
        if os.environ.get("OMEGA_ENV") == "test":
            self._event_log = []
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
        total = len(self._event_log)
        start = max(0, total - limit)
        return [self._event_log[i] for i in range(start, total)]

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
            "forensics": {
                "has_crashed": self._forensics.has_crashed,
                "recent_errors": len(self._forensics.recent_errors),
                "last_crash": self._last_crash["timestamp"] if self._last_crash else None,
            },
        }

    # ── Forensics / Crash Dump ──────────────────────────────────────

    def record_error(
        self,
        error: Exception,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an error for forensic analysis."""
        self._forensics.record_error(error, trace_id=trace_id, context=context)
        self.log_event(
            EventType.ERROR,
            trace_id or "unknown",
            {
                "error_type": type(error).__name__,
                "error_message": str(error)[:300],
                "context": context or {},
            },
        )

    async def snapshot(
        self,
        reason: str = "manual",
        error: Optional[Exception] = None,
        trace_id: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate a forensic crash dump."""
        return await self._forensics.snapshot(
            reason=reason,
            error=error,
            trace_id=trace_id,
            extra_context=extra_context,
        )

    @property
    def last_crash(self) -> Optional[Dict[str, Any]]:
        """Most recent crash dump recovered at startup, or None."""
        return self._last_crash


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
