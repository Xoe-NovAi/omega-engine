# 🔱 Omega Observability — Deep Logging, Tracking & Dataset Collection
# AP: AP-OBSERVABILITY-v2.0.0
# [heritage: opentelemetry 2021] OpenTelemetry — GenAI semantic conventions for observability tracing
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
import sqlite3
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import logging
import os
import threading
import time
import traceback
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from omega.constants import ZONEID_TRACE
from omega.observability.bleg import BLEGMiddleware
from omega.observability.ufl import UFLWriter, get_ufl_writer
from omega.observability.metrics_db import MetricsDB
from omega.observability.otel_exporter import OTelSQLiteExporter, setup_otel_exporter
from omega.observability.regression_watcher import (
    RegressionWatcher, 
    start_regression_watcher, 
    stop_regression_watcher,
    get_regression_watcher,
)

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
# Resolve DATA_DIR relative to project root if OMEGA_DATA_DIR is not set
_root = Path(__file__).resolve().parent.parent.parent.parent

def _get_data_dir() -> Path:
    """Get the current data directory, respecting OMEGA_DATA_DIR env var."""
    return Path(os.environ.get("OMEGA_DATA_DIR", str(_root / "data")))

def get_metrics_db_path() -> Path:
    """Get the MetricsDB path at runtime, respecting current OMEGA_DATA_DIR."""
    return _get_data_dir() / "observability" / "metrics.db"

# Backward compatibility - compute once at import for non-test usage
DATA_DIR = _get_data_dir()
LOG_DIR = DATA_DIR / "logs"
DATASET_DIR = DATA_DIR / "datasets"
TRACE_DIR = DATA_DIR / "traces"
CRASH_DIR = DATA_DIR / "crashes"
METRICS_DB_PATH = DATA_DIR / "observability" / "metrics.db"

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
    TOKEN_CONSUMPTION = "token.consumption"
    ENTITY_INTERACTION = "entity.interaction"


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
        # [hardening-p8] Install signal handlers for last-gasp death marker.
        # These are only installed in the main thread and only if not in test mode.
        if os.environ.get("OMEGA_ENV") != "test":
            try:
                import signal
                if threading.current_thread() is threading.main_thread():
                    for sig in (signal.SIGSEGV, signal.SIGABRT, signal.SIGILL,
                                signal.SIGFPE, signal.SIGTERM):
                        try:
                            signal.signal(sig, self._sync_signal_handler)
                        except (ValueError, OSError):
                            pass
            except OmegaError:
                logger.debug("OmegaError installing signal handler")
            except (OSError, RuntimeError) as e:
                logger.error("Unexpected error installing signal handler: %s", e, exc_info=True)

    def _sync_signal_handler(self, signum, frame):
        """Synchronous signal handler. Writes a death marker then re-raises.

        [hardening-p8] Signal handlers must be async-signal-safe, so we
        only perform minimal synchronous I/O here.
        """
        import signal
        try:
            sig_name = signal.Signals(signum).name
        except (ValueError, AttributeError):
            sig_name = str(signum)
        self.write_death_marker(reason=f"signal_{sig_name}")
        # Re-raise to the default handler (which will terminate the process).
        import signal as _sig
        _sig.signal(signum, _sig.SIG_DFL)
        _sig.raise_signal(signum)

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
        [hardening-p8] Adds os.fsync() and deep state capture.
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
                # [hardening-p8] Force physical write — os.fsync() ensures
                # the crash dump survives a system freeze or hard kill.
                f.flush()
                os.fsync(f.fileno())
            atomic_path.rename(path)
            logger.critical(f"Crash dump written to {path}")
        except OmegaError:
            logger.error("Failed to write crash dump (OmegaError)")
        except (OSError, RuntimeError) as e:
            logger.error(f"Unexpected failure writing crash dump: {e}", exc_info=True)

        return path

    def write_death_marker(self, reason: str = "signal") -> None:
        """Synchronous last-gasp death marker.

        Called from signal handlers (which cannot run async code).
        Writes a minimal marker to disk so check_recovery() can detect
        an abnormal termination even if the async snapshot() never ran.
        [hardening-p8] Signal-safe fallback.
        """
        try:
            marker_path = self._crash_dir / "death_marker.txt"
            self._crash_dir.mkdir(parents=True, exist_ok=True)
            with open(str(marker_path), "w") as f:
                f.write(f"{datetime.now(timezone.utc).isoformat()}\t{reason}\n")
                f.flush()
                os.fsync(f.fileno())
        except OmegaError:
            pass
        except (IOError, OSError, TypeError) as e:
            logger.error("Failed to write death marker (signal handler): %s", e, exc_info=True)
            pass

    async def _collect_engine_state(self) -> Dict[str, Any]:
        """Collect current engine state for crash dump.

        Safe to call even if engine components are not fully initialized.
        [hardening-p8] Deep state capture: thread dumps, memory maps, fd audit.
        """
        import threading
        state: Dict[str, Any] = {
            "providers_available": 0,
            "circuit_breakers_open": [],
            "memory_warm_count": 0,
            "memory_hot_count": 0,
            "has_crashed": self._has_crashed,
            "thread_dump": self._collect_thread_dump(),
            "memory_map_sample": self._collect_memory_map(),
            "open_file_descriptors": self._collect_fd_audit(),
        }

        if self._obs_engine:
            state["total_events"] = len(self._obs_engine._event_log)
            state["dataset_size"] = len(self._obs_engine._dataset)

        try:
            from omega.oracle.health_monitor import get_health_monitor
            from omega.oracle.model_gateway import ModelGateway
            gw = ModelGateway(health_monitor=get_health_monitor())
            providers = gw.providers if hasattr(gw, 'providers') else []
            state["providers_count"] = len(providers)
            state["providers_available"] = len([
                p for p in providers
                if hasattr(p, 'is_available') and p.is_available
            ])
        except OmegaError:
            pass
        except (RuntimeError, OSError) as e:
            logger.error("Failed to collect provider state for crash dump: %s", e, exc_info=True)
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
            except (OSError, ValueError) as e:
                logger.error("Failed to read /proc/self/status for RSS: %s", e, exc_info=True)
                pass

        return state

    @staticmethod
    def _collect_thread_dump() -> List[Dict[str, str]]:
        """Capture stack traces of all live threads. [hardening-p8]"""
        import sys
        import threading
        try:
            frames = sys._current_frames()
            result = []
            for tid, frame in frames.items():
                thread = next((t for t in threading.enumerate() if t.ident == tid), None)
                name = thread.name if thread else f"Unknown-{tid}"
                # Format the stack trace
                import traceback
                stack = traceback.format_stack(frame, limit=8)
                result.append({
                    "thread_id": str(tid),
                    "thread_name": name,
                    "stack": "".join(stack)[:2000],
                })
            return result
        except (OSError, RuntimeError) as e:
            return [{"error": str(e)}]

    @staticmethod
    def _collect_memory_map(limit: int = 20) -> List[str]:
        """Sample the process memory map from /proc/self/maps. [hardening-p8]"""
        try:
            with open("/proc/self/maps", "r") as f:
                lines = f.readlines()
            # Return first N and last N lines to keep size manageable
            if len(lines) <= limit * 2:
                return [l.strip() for l in lines]
            return [l.strip() for l in lines[:limit] + lines[-limit:]]
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to collect memory map: {e}", exc_info=True)
            return []

    @staticmethod
    def _collect_fd_audit() -> Dict[str, int]:
        """Audit open file descriptors. [hardening-p8]"""
        try:
            with open("/proc/self/fd", "r") as f:
                fds = f.readlines()
            return {"total_open": len(fds)}
        except (OSError, RuntimeError) as e:
            logger.error(f"Failed to collect FD audit: {e}", exc_info=True)
            return {"total_open": -1}

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
        except (OSError, RuntimeError) as e:
            logger.error("Unexpected error detecting anyio backend: %s", e, exc_info=True)
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
        except OmegaError:
            return None
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Unexpected failure processing crash dump {latest}: {e}", exc_info=True)
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
        except OmegaError:
            return None
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Unexpected failure loading crash dump for replay: %s", e, exc_info=True)
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
                except OmegaError:
                    continue
                except (OSError, json.JSONDecodeError) as e:
                    logger.error("Unexpected failure reading event log for crash dump: %s", e, exc_info=True)
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
            except OmegaError:
                pass
            except (OSError, yaml.YAMLError) as e:
                logger.error("Unexpected failure writing lesson to soul.yaml: %s", e, exc_info=True)
                pass
        return lesson

    @property
    def recent_errors(self) -> List[Dict[str, Any]]:
        return list(self._recent_errors)

    @property
    def has_crashed(self) -> bool:
        return self._has_crashed


# ── Budget Gate (M7 Local-First Enforcement) ────────────────────────────
# [id-soft: quake-1996] Zone Memory — resource guard with budget enforcement.

class BudgetGate:
    """
    Enforces cloud inference budget limits per Mandate 7 (Local-First).
    
    Tracks daily cloud token spend and blocks cloud requests when budget exceeded.
    Local inference is always allowed (budget-free).
    """
    
    # Default daily budget in USD (configurable via env)
    DEFAULT_DAILY_BUDGET_USD = float(os.environ.get("OMEGA_DAILY_CLOUD_BUDGET_USD", "1.00"))
    
    # Cost per 1K tokens for known cloud providers (approximate)
    PROVIDER_COSTS = {
        "google": {"input": 0.000125, "output": 0.000375},  # Gemini 1.5 Flash
        "openrouter": {"input": 0.0005, "output": 0.0015},  # Varies by model
        "openai": {"input": 0.005, "output": 0.015},  # GPT-4o-mini
        "anthropic": {"input": 0.003, "output": 0.015},  # Claude Haiku
        "azure": {"input": 0.005, "output": 0.015},
        "aws": {"input": 0.005, "output": 0.015},
        "copilot": {"input": 0.0, "output": 0.0},  # Included in subscription
        "opencode": {"input": 0.0, "output": 0.0},  # Included in subscription
    }
    
    def __init__(self, metrics_db: Optional["MetricsDB"] = None):
        self._metrics_db = metrics_db
        self._daily_budget = self.DEFAULT_DAILY_BUDGET_USD
        self._daily_spend_cache: Dict[str, float] = {}  # date -> spend
        self._cache_date: Optional[str] = None
    
    def _get_provider_costs(self, provider: str) -> Dict[str, float]:
        """Get cost per 1K tokens for a provider."""
        provider_lower = provider.lower()
        for key, costs in self.PROVIDER_COSTS.items():
            if key in provider_lower:
                return costs
        # Default conservative estimate for unknown cloud providers
        return {"input": 0.001, "output": 0.003}
    
    def _get_today_spend(self) -> float:
        """Get today's cloud spend from MetricsDB."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        if self._cache_date == today and today in self._daily_spend_cache:
            return self._daily_spend_cache[today]
        
        if not self._metrics_db:
            return 0.0
        
        try:
            ts_start = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
            cursor = self._metrics_db._conn.execute(
                "SELECT SUM(cost_usd) as total FROM performance WHERE ts >= ? AND is_cloud = 1",
                (ts_start,)
            )
            row = cursor.fetchone()
            spend = row["total"] if row and row["total"] else 0.0
            self._daily_spend_cache[today] = spend
            self._cache_date = today
            return spend
        except Exception as e:
            logger.debug("BudgetGate daily spend query failed (returning 0.0): %s", e)
            return 0.0
    
    def estimate_cost(self, provider: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD for a cloud inference request."""
        costs = self._get_provider_costs(provider)
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]
        return input_cost + output_cost
    
    def check_budget(self, provider: str, prompt_tokens: int, completion_tokens: int) -> tuple[bool, str]:
        """
        Check if a cloud request would exceed the daily budget.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Local providers always allowed
        if not self._is_cloud_provider(provider):
            return True, "Local provider — no budget limit"
        
        estimated_cost = self.estimate_cost(provider, prompt_tokens, completion_tokens)
        current_spend = self._get_today_spend()
        projected_spend = current_spend + estimated_cost
        
        if projected_spend > self._daily_budget:
            return False, (
                f"Daily cloud budget exceeded: ${current_spend:.4f} spent, "
                f"${estimated_cost:.4f} estimated, ${self._daily_budget:.2f} limit"
            )
        
        return True, f"Budget OK: ${current_spend:.4f}/${self._daily_budget:.2f} used"
    
    def _is_cloud_provider(self, provider: str) -> bool:
        """Check if provider is cloud-based (same logic as OTel exporter)."""
        local_indicators = ["ollama", "lmstudio", "lm_studio", "native", "gguf", "llama.cpp", "local", "mock"]
        provider_lower = provider.lower()
        for indicator in local_indicators:
            if indicator in provider_lower:
                return False
        return True
    
    def record_spend(self, provider: str, prompt_tokens: int, completion_tokens: int, trace_id: Optional[str] = None) -> float:
        """Record actual spend after a cloud inference. Returns cost in USD."""
        if not self._is_cloud_provider(provider):
            return 0.0
        
        cost = self.estimate_cost(provider, prompt_tokens, completion_tokens)
        
        if self._metrics_db:
            try:
                ts = int(time.time() * 1000)
                self._metrics_db._conn.execute(
                    "UPDATE performance SET cost_usd = ? WHERE trace_id = ? AND is_cloud = 1",
                    (cost, trace_id)
                )
                self._metrics_db._conn.commit()
            except Exception as e:
                logger.debug("BudgetGate cost recording failed: %s", e)
        
        # Invalidate cache
        self._daily_spend_cache.clear()
        return cost
    
    def get_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        spend = self._get_today_spend()
        return {
            "daily_budget_usd": self._daily_budget,
            "current_spend_usd": spend,
            "remaining_usd": max(0, self._daily_budget - spend),
            "utilization_pct": (spend / self._daily_budget * 100) if self._daily_budget > 0 else 0,
        }


# Add cost_usd column to performance table if not exists (migration)
def _ensure_cost_column(metrics_db: "MetricsDB") -> None:
    """Ensure cost_usd column exists in performance table."""
    try:
        cursor = metrics_db._conn.execute("PRAGMA table_info(performance)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "cost_usd" not in columns:
            metrics_db._conn.execute("ALTER TABLE performance ADD COLUMN cost_usd REAL DEFAULT 0.0")
            metrics_db._conn.commit()
    except Exception as e:
        logger.debug("Schema migration (cost_usd column) failed (may already exist): %s", e)


# ── Observability Engine ──────────────────────────────────────────────
class ObservabilityEngine:
    """Central observability, logging, dataset collection, and forensics."""

    def __init__(
        self,
        enable_dataset_collection: bool = False,
        forensics_manager: Optional[ForensicsManager] = None,
        metrics_db: Optional[MetricsDB] = None,
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
        self._bleg = BLEGMiddleware(enabled=True)
        self._ufl = get_ufl_writer()

        # MetricsDB — WAL-mode SQLite for profiling baselines & regression detection
        # [id-soft: doom3-2004] Event System — structured event logging for observability.
        self._metrics_db = metrics_db
        self._metrics_db_initialized = False
        
        # OTel GenAI Exporter — exports spans to MetricsDB
        self._otel_exporter: Optional[OTelSQLiteExporter] = None
        self._otel_initialized = False
        
        # Regression Watcher — automated baseline regression detection
        self._regression_watcher: Optional[RegressionWatcher] = None
        self._regression_watcher_started = False
        
        # Budget Gate — M7 Local-First enforcement
        self._budget_gate: Optional[BudgetGate] = None
        self._budget_gate_initialized = False

    def _ensure_metrics_db(self) -> Optional[MetricsDB]:
        """Lazy-initialize MetricsDB if not already provided.

        Creates the DB at data/observability/metrics.db on first access.
        Returns None in test mode to avoid filesystem side effects.
        Respects an injected metrics_db even in test mode.
        """
        if self._metrics_db_initialized:
            return self._metrics_db
        self._metrics_db_initialized = True
        if self._metrics_db is not None:
            # Already injected — respect it even in test mode
            return self._metrics_db
        if os.environ.get("OMEGA_ENV") == "test":
            return None
        try:
            db = MetricsDB(get_metrics_db_path())
            db.initialize()
            self._metrics_db = db
        except (OSError, RuntimeError) as e:
            logger.warning("Failed to initialize MetricsDB: %s", e)
        return self._metrics_db

    def _ensure_otel_exporter(self) -> Optional[OTelSQLiteExporter]:
        """Lazy-initialize OTel GenAI exporter."""
        if self._otel_initialized:
            return self._otel_exporter
        self._otel_initialized = True
        
        metrics_db = self.metrics_db
        if not metrics_db:
            return None
            
        if os.environ.get("OMEGA_ENV") == "test":
            return None
            
        try:
            self._otel_exporter = setup_otel_exporter(metrics_db)
            logger.info("OTel GenAI SQLite exporter initialized")
        except (OSError, RuntimeError, ImportError) as e:
            logger.warning("Failed to initialize OTel exporter: %s", e)
        return self._otel_exporter

    @property
    def otel_exporter(self) -> Optional[OTelSQLiteExporter]:
        """Access the OTel GenAI exporter (lazy-initialized)."""
        return self._ensure_otel_exporter()

    @property
    def metrics_db(self) -> Optional[MetricsDB]:
        """Access the MetricsDB instance (lazy-initialized)."""
        return self._ensure_metrics_db()

    async def start_regression_watcher(
        self, 
        interval_seconds: int = 300, 
        threshold: float = 0.1
    ) -> Optional[RegressionWatcher]:
        """Start the regression watcher background task.
        
        Args:
            interval_seconds: Check interval in seconds (default 300 = 5 min)
            threshold: Regression threshold as percentage (default 0.1 = 10%)
            
        Returns:
            The RegressionWatcher instance, or None if MetricsDB not available
        """
        if self._regression_watcher_started:
            return self._regression_watcher
        
        metrics_db = self.metrics_db
        if not metrics_db:
            logger.warning("Cannot start RegressionWatcher: MetricsDB not available")
            return None
        
        if os.environ.get("OMEGA_ENV") == "test":
            return None
        
        try:
            self._regression_watcher = RegressionWatcher(
                metrics_db, 
                interval_seconds, 
                threshold
            )
            await self._regression_watcher.start()
            self._regression_watcher_started = True
            logger.info("RegressionWatcher started")
            return self._regression_watcher
        except Exception as e:
            logger.error(f"Failed to start RegressionWatcher: {e}")
            return None

    async def stop_regression_watcher(self) -> None:
        """Stop the regression watcher background task."""
        if self._regression_watcher and self._regression_watcher_started:
            await self._regression_watcher.stop()
            self._regression_watcher_started = False
            logger.info("RegressionWatcher stopped")

    def _ensure_budget_gate(self) -> Optional[BudgetGate]:
        """Lazy-initialize BudgetGate."""
        if self._budget_gate_initialized:
            return self._budget_gate
        self._budget_gate_initialized = True
        
        metrics_db = self.metrics_db
        if not metrics_db:
            return None
        
        if os.environ.get("OMEGA_ENV") == "test":
            return None
        
        try:
            self._budget_gate = BudgetGate(metrics_db)
            # Ensure cost_usd column exists
            _ensure_cost_column(metrics_db)
            logger.info("BudgetGate initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize BudgetGate: {e}")
        return self._budget_gate

    @property
    def budget_gate(self) -> Optional[BudgetGate]:
        """Access the BudgetGate (lazy-initialized)."""
        return self._ensure_budget_gate()

    def check_cloud_budget(self, provider: str, prompt_tokens: int, completion_tokens: int) -> tuple[bool, str]:
        """Check if a cloud request would exceed the daily budget.
        
        Returns:
            (allowed: bool, reason: str)
        """
        gate = self.budget_gate
        if not gate:
            return True, "BudgetGate not available — allowing"
        return gate.check_budget(provider, prompt_tokens, completion_tokens)

    def record_cloud_spend(self, provider: str, prompt_tokens: int, completion_tokens: int, trace_id: Optional[str] = None) -> float:
        """Record actual spend after a cloud inference. Returns cost in USD."""
        gate = self.budget_gate
        if not gate:
            return 0.0
        return gate.record_spend(provider, prompt_tokens, completion_tokens, trace_id)

    @property
    def budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        gate = self.budget_gate
        if not gate:
            return {"error": "BudgetGate not available"}
        return gate.get_status()

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
        except OmegaError:
            pass
        except (OSError, RuntimeError) as e:
            logger.error(f"Unexpected failure persisting event: {e}", exc_info=True)
            pass

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
        except OmegaError:
            pass
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Unexpected failure loading persisted events: {e}", exc_info=True)
            pass

    # ── Log an event ─────────────────────────────────────────────────
    def log_event(
        self,
        event_type: str,
        trace_id: str,
        data: Dict[str, Any],
        parent_trace_id: Optional[str] = None,
    ) -> None:
        """Log a single observability event.

        [id-soft: doom-1993] ZONEID Pattern — integrity marker on every event
        """
        event = {
            "_zoneid": ZONEID_TRACE,  # Heritage marker for event lineage validation
            "event": event_type,
            "trace_id": trace_id,
            "parent_trace_id": parent_trace_id,
            "session_id": self._session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._event_log.append(event)
        self._persist_event(event)

        # Also record to MetricsDB if available
        metrics_db = self.metrics_db
        if metrics_db:
            try:
                metrics_db.record_event(
                    event_type=event_type,
                    trace_id=trace_id,
                    provider=data.get("provider"),
                    payload=data,
                )
            except (OSError, RuntimeError) as e:
                logger.debug("MetricsDB event recording failed: %s", e)

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

    # ── Record performance to MetricsDB ──────────────────────────────
    def record_performance(
        self,
        latency_ms: float,
        provider: Optional[str] = None,
        model_used: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_cloud: bool = False,
        trace_id: Optional[str] = None,
    ) -> None:
        """Record a performance measurement to MetricsDB.

        Called after each inference to track latency, token usage, and cost.
        [id-soft: doom3-2004] Event System — structured performance logging.
        """
        metrics_db = self.metrics_db
        if not metrics_db:
            return
        try:
            metrics_db.record_performance(
                latency_ms=latency_ms,
                provider=provider,
                model_used=model_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                is_cloud=is_cloud,
                trace_id=trace_id,
            )
        except (OSError, RuntimeError) as e:
            logger.debug("MetricsDB performance recording failed: %s", e)

    # ── Record error to MetricsDB ────────────────────────────────────
    def record_metrics_error(
        self,
        error_type: str,
        error_message: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an error to MetricsDB (separate from forensics recording).

        [id-soft: doom3-2004] Event System — structured error logging.
        """
        metrics_db = self.metrics_db
        if not metrics_db:
            return
        try:
            metrics_db.record_error(
                error_type=error_type,
                error_message=error_message,
                trace_id=trace_id,
                provider=provider,
                context=context,
            )
        except (OSError, RuntimeError) as e:
            logger.debug("MetricsDB error recording failed: %s", e)

    # ── Record breaker transition to MetricsDB ────────────────────────
    def record_breaker_transition(
        self,
        provider: str,
        from_state: str,
        to_state: str,
        trace_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Record a circuit breaker state transition to MetricsDB.

        [id-soft: doom3-2004] Event System — breaker transition logging.
        """
        metrics_db = self.metrics_db
        if not metrics_db:
            return
        try:
            metrics_db.record_breaker_transition(
                provider=provider,
                from_state=from_state,
                to_state=to_state,
                trace_id=trace_id,
                reason=reason,
            )
        except (OSError, RuntimeError) as e:
            logger.debug("MetricsDB breaker recording failed: %s", e)

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
        result = {
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
        # Add MetricsDB stats if available
        metrics_db = self.metrics_db
        if metrics_db:
                try:
                    result["metrics_db"] = metrics_db.get_stats()
                except (RuntimeError, OSError):
                    result["metrics_db"] = {"error": "unavailable"}
        else:
            result["metrics_db"] = {"status": "not_initialized"}
        return result

    # ── Forensics / Crash Dump ──────────────────────────────────────

    def record_error(
        self,
        error: Exception,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an error for forensic analysis.
        
        Uses contextvars safety net if trace_id is not explicitly provided,
        ensuring errors never carry trace_id="unknown".
        """
        # [M22] Use contextvars safety net if trace_id not provided
        if trace_id is None:
            from .context import get_current_trace_id
            trace_id = get_current_trace_id()
        
        self._forensics.record_error(error, trace_id=trace_id, context=context)
        self.log_event(
            EventType.ERROR,
            trace_id,  # No more "unknown" — guaranteed by safety net
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
    def bleg(self) -> BLEGMiddleware:
        """Body-Level Error Guard — inspects 200 OK bodies for error signatures."""
        return self._bleg

    @property
    def ufl(self) -> UFLWriter:
        """Unified Forensic Ledger — append-only JSONL event store."""
        return self._ufl

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


def reset_observability() -> None:
    """Reset the ObservabilityEngine singleton. Used for testing.
    
    Closes the MetricsDB SQLite connection (WAL-mode) before abandoning
    the engine to prevent ResourceWarning and database corruption when
    OMEGA_DATA_DIR changes between tests. Without this, a stale MetricsDB
    connection from a previous test's tmp_path leaks into subsequent tests,
    causing 'database disk image is malformed' errors.
    """
    global _engine
    if _engine is not None:
        # Close MetricsDB connection if it was initialized (non-test mode)
        metrics_db = _engine._metrics_db
        if metrics_db is not None and hasattr(metrics_db, 'close'):
            try:
                metrics_db.close()
            except (RuntimeError, OSError, sqlite3.Error):
                pass  # Best-effort — engine is being abandoned anyway
        _engine = None


# Add cost_usd column to performance table if not exists (migration)
def _ensure_cost_column(metrics_db: "MetricsDB") -> None:
    """Ensure cost_usd column exists in performance table."""
    try:
        cursor = metrics_db._conn.execute("PRAGMA table_info(performance)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "cost_usd" not in columns:
            metrics_db._conn.execute("ALTER TABLE performance ADD COLUMN cost_usd REAL DEFAULT 0.0")
            metrics_db._conn.commit()
    except Exception as e:
        logger.debug("Schema migration (cost_usd column) failed (may already exist): %s", e)
