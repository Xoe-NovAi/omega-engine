"""SQLite WAL-Mode Metrics Store for profiling baselines and regression detection.
AP: AP-METRICS-DB-v1.0.0
"""

import json
import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# Carmack's schema — 4-table WAL-mode design
# Source: data/entities/john_carmack/workspace/carmack_studies/technical/metrics_db_schema.sql
_SCHEMA_SQL = """
-- General Events Ledger
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    trace_id TEXT,
    provider TEXT,
    payload TEXT
);

-- Error Ledger (fast anomaly querying)
CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    trace_id TEXT,
    provider TEXT,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    context TEXT
);

-- Circuit Breaker State Transitions
CREATE TABLE IF NOT EXISTS breaker_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    provider TEXT NOT NULL,
    trace_id TEXT,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    reason TEXT
);

-- Token & Latency Ledger (cost/performance analytics)
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    trace_id TEXT,
    provider TEXT,
    model_used TEXT,
    latency_ms REAL NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    is_cloud INTEGER DEFAULT 0
);

-- Baseline metrics for regression detection
CREATE TABLE IF NOT EXISTS baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    sample_count INTEGER NOT NULL,
    std_deviation REAL,
    created_at INTEGER NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(metric_name, source)
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at INTEGER NOT NULL
);

-- Indices for fast forensic lookups
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_trace ON events(trace_id);
CREATE INDEX IF NOT EXISTS idx_events_provider ON events(provider);
CREATE INDEX IF NOT EXISTS idx_errors_ts ON errors(ts);
CREATE INDEX IF NOT EXISTS idx_errors_trace ON errors(trace_id);
CREATE INDEX IF NOT EXISTS idx_errors_provider ON errors(provider);
CREATE INDEX IF NOT EXISTS idx_breaker_provider ON breaker_transitions(provider);
CREATE INDEX IF NOT EXISTS idx_perf_ts ON performance(ts);
CREATE INDEX IF NOT EXISTS idx_perf_provider ON performance(provider);
CREATE INDEX IF NOT EXISTS idx_perf_latency ON performance(latency_ms);
CREATE INDEX IF NOT EXISTS idx_baselines_metric ON baselines(metric_name);
"""


class MetricsDB:
    """SQLite WAL-mode metrics store for profiling baselines and regression detection.
    
    [id-soft: doom3-2004] Event System — structured event logging for observability.
    [id-soft: quake-1996] cvar pattern — named constant registry for metric names.
    
    Uses WAL-mode for high-concurrency, non-blocking reads/writes.
    Designed for Carmack's profiler baselines and UFL (Unified Forensic Ledger).
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        """Initialize database with WAL mode and schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        # WAL-mode configuration (Carmack's battle-tested pattern)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        self._conn.execute("PRAGMA temp_store=MEMORY")

        # Create schema
        self._conn.executescript(_SCHEMA_SQL)

        # Record schema version
        now = int(time.time() * 1000)
        self._conn.execute(
            "INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (?, ?)",
            (SCHEMA_VERSION, now),
        )
        self._conn.commit()
        logger.info("MetricsDB initialized at %s (WAL-mode, schema v%d)", self.db_path, SCHEMA_VERSION)

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Event Recording ──────────────────────────────────────────────────

    def record_event(
        self,
        event_type: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a general event."""
        ts = int(time.time() * 1000)
        self._conn.execute(
            "INSERT INTO events (ts, event_type, trace_id, provider, payload) VALUES (?, ?, ?, ?, ?)",
            (ts, event_type, trace_id, provider, json.dumps(payload) if payload else None),
        )
        self._conn.commit()

    def record_error(
        self,
        error_type: str,
        error_message: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record an error event."""
        ts = int(time.time() * 1000)
        self._conn.execute(
            "INSERT INTO errors (ts, trace_id, provider, error_type, error_message, context) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ts, trace_id, provider, error_type, error_message, json.dumps(context) if context else None),
        )
        self._conn.commit()

    def record_breaker_transition(
        self,
        provider: str,
        from_state: str,
        to_state: str,
        trace_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Record a circuit breaker state transition."""
        ts = int(time.time() * 1000)
        self._conn.execute(
            "INSERT INTO breaker_transitions (ts, provider, trace_id, from_state, to_state, reason) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ts, provider, trace_id, from_state, to_state, reason),
        )
        self._conn.commit()

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
        """Record a performance measurement (latency, tokens, cost)."""
        ts = int(time.time() * 1000)
        total_tokens = prompt_tokens + completion_tokens
        self._conn.execute(
            "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, "
            "prompt_tokens, completion_tokens, total_tokens, is_cloud) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ts, trace_id, provider, model_used, latency_ms,
             prompt_tokens, completion_tokens, total_tokens, int(is_cloud)),
        )
        self._conn.commit()

    # ── Baseline Management ──────────────────────────────────────────────

    def set_baseline(
        self,
        metric_name: str,
        value: float,
        sample_count: int,
        std_deviation: Optional[float] = None,
        source: str = "profiler",
    ) -> None:
        """Set or update a baseline metric for regression detection."""
        now = int(time.time() * 1000)
        self._conn.execute(
            "INSERT OR REPLACE INTO baselines (metric_name, metric_value, sample_count, std_deviation, created_at, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (metric_name, value, sample_count, std_deviation, now, source),
        )
        self._conn.commit()

    def get_baseline(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get a baseline metric by name."""
        row = self._conn.execute(
            "SELECT metric_name, metric_value, sample_count, std_deviation, created_at, source "
            "FROM baselines WHERE metric_name = ?",
            (metric_name,),
        ).fetchone()
        if row:
            return dict(row)
        return None

    # ── Regression Detection ─────────────────────────────────────────────

    def detect_regression(
        self,
        metric_name: str,
        current_value: float,
        threshold: float = 0.1,
    ) -> bool:
        """Detect if current value regresses from baseline.
        
        Uses 3-sigma rule if std_deviation is available,
        otherwise falls back to percentage threshold.
        """
        baseline = self.get_baseline(metric_name)
        if not baseline:
            return False

        baseline_value = baseline["metric_value"]
        std_dev = baseline["std_deviation"]

        if std_dev and std_dev > 0:
            # 3-sigma rule
            z_score = abs(current_value - baseline_value) / std_dev
            return z_score > 3.0
        else:
            # Percentage threshold
            if baseline_value == 0:
                return current_value > 0
            return abs(current_value - baseline_value) / baseline_value > threshold

    # ── Query Methods ────────────────────────────────────────────────────

    def get_performance_trend(
        self,
        provider: Optional[str] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Get performance trend over time."""
        ts_threshold = int((time.time() - hours * 3600) * 1000)
        if provider:
            cursor = self._conn.execute(
                "SELECT ts, latency_ms, provider, model_used, prompt_tokens, completion_tokens "
                "FROM performance WHERE ts > ? AND provider = ? ORDER BY ts",
                (ts_threshold, provider),
            )
        else:
            cursor = self._conn.execute(
                "SELECT ts, latency_ms, provider, model_used, prompt_tokens, completion_tokens "
                "FROM performance WHERE ts > ? ORDER BY ts",
                (ts_threshold,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        ts_threshold = int((time.time() - hours * 3600) * 1000)
        cursor = self._conn.execute(
            "SELECT error_type, COUNT(*) as count FROM errors WHERE ts > ? GROUP BY error_type ORDER BY count DESC",
            (ts_threshold,),
        )
        return {row["error_type"]: row["count"] for row in cursor.fetchall()}

    def get_breaker_history(self, provider: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get circuit breaker transition history."""
        if provider:
            cursor = self._conn.execute(
                "SELECT ts, provider, from_state, to_state, reason FROM breaker_transitions "
                "WHERE provider = ? ORDER BY ts DESC LIMIT ?",
                (provider, limit),
            )
        else:
            cursor = self._conn.execute(
                "SELECT ts, provider, from_state, to_state, reason FROM breaker_transitions "
                "ORDER BY ts DESC LIMIT ?",
                (limit,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        for table in ["events", "errors", "breaker_transitions", "performance", "baselines"]:
            cursor = self._conn.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()["count"]
        stats["db_size_bytes"] = self.db_path.stat().st_size if self.db_path.exists() else 0
        return stats
