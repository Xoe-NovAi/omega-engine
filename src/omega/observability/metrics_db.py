"""SQLite WAL-Mode Metrics Store for profiling baselines and regression detection.
AP: AP-METRICS-DB-v1.0.0
"""
# DocRef: docs/explanation/metrics-pipeline.md

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 3

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
    context TEXT,
    entity_id TEXT,
    FOREIGN KEY (entity_id) REFERENCES entities(name)
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
-- Schema v3: Added cache_read_tokens, provider_prompt_tokens, provider_completion_tokens
-- for QW-3 CI guard against token counting bugs (G-3, G-4).
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
    cache_read_tokens INTEGER DEFAULT 0,
    provider_prompt_tokens INTEGER DEFAULT 0,
    provider_completion_tokens INTEGER DEFAULT 0,
    is_cloud INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    entity_id TEXT,
    FOREIGN KEY (entity_id) REFERENCES entities(name)
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

-- Vault Audit Ledger (M11 Soul Integrity + M25 Streaming Resilience)
CREATE TABLE IF NOT EXISTS vault_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    trace_id TEXT,
    action TEXT NOT NULL,
    credential_ref TEXT NOT NULL,
    success INTEGER NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_vault_audit_ts ON vault_audit(ts);
CREATE INDEX IF NOT EXISTS idx_vault_audit_trace ON vault_audit(trace_id);
CREATE INDEX IF NOT EXISTS idx_vault_audit_cred ON vault_audit(credential_ref);
CREATE INDEX IF NOT EXISTS idx_vault_audit_action ON vault_audit(action);
"""


class MetricsDB:
    """SQLite WAL-mode metrics store for profiling baselines and regression detection.

    [id-soft: vet-040] Event System — structured event logging for observability.
    [id-soft: vet-016] cvar pattern — named constant registry for metric names.

    Uses WAL-mode for high-concurrency, non-blocking reads/writes.
    Designed for Carmack's profiler baselines and UFL (Unified Forensic Ledger).
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        # [M1 AnyIO] Serializes writes across anyio.to_thread.run_sync
        # worker threads. check_same_thread=False (set in initialize())
        # only disables Python's thread-identity check — it does not make
        # concurrent execute() calls from different threads safe. Mirrors
        # the pattern in sqlite_vec_adapter.py's _write_lock.
        self._write_lock: Optional[anyio.Lock] = None

    def _get_write_lock(self) -> anyio.Lock:
        if self._write_lock is None:
            self._write_lock = anyio.Lock()
        return self._write_lock

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

        # Migration: add cost_usd + v3 token columns if missing (schema v1/v2 -> v3).
        # The live DB may predate schema v3 (cache_read_tokens, provider_prompt_tokens,
        # provider_completion_tokens). Without this, record_performance() raises
        # sqlite3.OperationalError and crashes the entire oracle response (CP-1 blocker).
        try:
            cursor = self._conn.execute("PRAGMA table_info(performance)")
            columns = [row["name"] for row in cursor.fetchall()]
            _migration_cols = {
                "cost_usd": "REAL DEFAULT 0.0",
                "cache_read_tokens": "INTEGER DEFAULT 0",
                "provider_prompt_tokens": "INTEGER DEFAULT 0",
                "provider_completion_tokens": "INTEGER DEFAULT 0",
            }
            added = []
            for col, col_type in _migration_cols.items():
                if col not in columns:
                    self._conn.execute(f"ALTER TABLE performance ADD COLUMN {col} {col_type}")
                    added.append(col)
            if added:
                self._conn.commit()
                logger.info("MetricsDB migration: added columns %s to performance table", added)
        except Exception as e:
            logger.warning("MetricsDB migration check failed: %s", e)

        # Record schema version
        now = int(time.time() * 1000)
        self._conn.execute(
            "INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (?, ?)",
            (SCHEMA_VERSION, now),
        )
        self._conn.commit()
        logger.info(
            "MetricsDB initialized at %s (WAL-mode, schema v%d)", self.db_path, SCHEMA_VERSION
        )

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Sovereignty Classification Schema (M22 SSOT) ─────────────────────
    # The corrected sovereignty ratio delegates cloud/local classification
    # to config/providers.yaml (via ProviderRegistry) instead of the
    # per-response `is_cloud` bit written by the ModelGateway.

    def build_provider_classification_table(self) -> None:
        """Create/populate provider_classification from ProviderRegistry (sync).

        Idempotent — safe to call on every ratio query. Matches the sync
        DDL style of initialize(). Populates is_synthetic from the registry
        so the corrected view uses authoritative classification instead of
        the fragile string match it previously relied on.
        """
        from omega.oracle.provider_registry import get_provider_registry

        registry = get_provider_registry()

        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_classification (
                provider_name TEXT PRIMARY KEY,
                is_cloud BOOLEAN NOT NULL,
                is_synthetic BOOLEAN NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'providers.yaml',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Migrate pre-existing tables created before the is_synthetic column.
        cols = [
            row["name"] for row in self._conn.execute("PRAGMA table_info(provider_classification)")
        ]
        if "is_synthetic" not in cols:
            self._conn.execute(
                "ALTER TABLE provider_classification "
                "ADD COLUMN is_synthetic BOOLEAN NOT NULL DEFAULT 0"
            )
        for name, is_cloud in registry.all_providers().items():
            self._conn.execute(
                "INSERT OR REPLACE INTO provider_classification "
                "(provider_name, is_cloud, is_synthetic, source) "
                "VALUES (?, ?, ?, 'providers.yaml')",
                (name, int(is_cloud), int(registry.is_synthetic(name))),
            )
        # Flag synthetic (test/probe) providers even when absent from the
        # fallback_chain (e.g. "fallback") so they are always excluded from
        # sovereignty statistics (Decision 1).
        for name in registry.synthetic_providers():
            self._conn.execute(
                "INSERT OR REPLACE INTO provider_classification "
                "(provider_name, is_cloud, is_synthetic, source) "
                "VALUES (?, ?, 1, 'registry-synthetic')",
                (name, int(registry.is_cloud(name))),
            )
        self._conn.commit()

    def create_corrected_performance_view(self) -> None:
        """Create v_performance_corrected exposing config-derived classification.

        Joins performance with provider_classification. For providers present
        in providers.yaml the SSOT ``is_cloud`` wins; for providers absent
        from config we fall back to the per-response recorded ``is_cloud``
        bit (so historical cloud rows aren't mislabeled local). Synthetic
        probe rows are excluded via the registry's ``is_synthetic`` flag.
        """
        self.build_provider_classification_table()
        self._conn.execute("DROP VIEW IF EXISTS v_performance_corrected")
        self._conn.execute(
            """
            CREATE VIEW v_performance_corrected AS
            SELECT
                p.*,
                COALESCE(c.is_cloud, p.is_cloud) AS is_cloud_corrected,
                CASE WHEN c.provider_name IS NULL THEN 'recorded' ELSE 'providers.yaml' END
                    AS classification_source
            FROM performance p
            LEFT JOIN provider_classification c ON p.provider = c.provider_name
            WHERE (c.is_synthetic = 0 OR c.is_synthetic IS NULL)
            """
        )
        self._conn.commit()

    # ── Event Recording ──────────────────────────────────────────────────

    async def record_event(
        self,
        event_type: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a general event.

        [M1 AnyIO] Blocking SQLite write offloaded via to_thread.run_sync;
        [M9 Error Integrity] lock-serialized to prevent concurrent-thread
        interleaving on the shared connection.
        """
        ts = int(time.time() * 1000)
        payload_json = json.dumps(payload) if payload else None

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO events (ts, event_type, trace_id, provider, payload) VALUES (?, ?, ?, ?, ?)",
                (ts, event_type, trace_id, provider, payload_json),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)

    async def record_error(
        self,
        error_type: str,
        error_message: str,
        trace_id: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        """Record an error event. [M1 AnyIO] See record_event for pattern rationale."""
        ts = int(time.time() * 1000)
        context_json = json.dumps(context) if context else None

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO errors (ts, trace_id, provider, error_type, error_message, context, entity_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, trace_id, provider, error_type, error_message, context_json, entity_id),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)

    async def record_breaker_transition(
        self,
        provider: str,
        from_state: str,
        to_state: str,
        trace_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Record a circuit breaker state transition. [M1 AnyIO]"""
        ts = int(time.time() * 1000)

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO breaker_transitions (ts, provider, trace_id, from_state, to_state, reason) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, provider, trace_id, from_state, to_state, reason),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)

    async def record_performance(
        self,
        latency_ms: float,
        provider: Optional[str] = None,
        model_used: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_cloud: bool = False,
        trace_id: Optional[str] = None,
        cost_usd: float = 0.0,
        entity_id: Optional[str] = None,
        cache_read_tokens: int = 0,
        provider_prompt_tokens: Optional[int] = None,
        provider_completion_tokens: Optional[int] = None,
    ) -> None:
        """Record a performance measurement (latency, tokens, cost).

        [M1 AnyIO] All arguments are captured by closure into `_sync_insert`
        BEFORE the thread hop — the sync inner function touches no async
        state, only the sqlite3 connection and locals, which is what makes
        `anyio.to_thread.run_sync` safe here.

        [M9 Error Integrity] Lock-serialized: this is the highest-frequency
        write path in the engine (called once per successful inference from
        ModelGateway.generate() -> LatencyTracker.record()). Without the
        lock, concurrent inferences racing on the same connection object
        risk `sqlite3.OperationalError: database is locked` even with
        PRAGMA busy_timeout=5000 set, because busy_timeout governs
        cross-process contention, not same-process cross-thread races on
        one connection object.

        [QW-3 CI Guard] cache_read_tokens and provider_*_tokens fields enable
        divergence auditing between local estimate and provider returned usage.
        This prevents G-3/G-4 token counting bugs.
        """
        ts = int(time.time() * 1000)
        total_tokens = prompt_tokens + completion_tokens + cache_read_tokens

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, "
                "prompt_tokens, completion_tokens, total_tokens, cache_read_tokens, "
                "provider_prompt_tokens, provider_completion_tokens, "
                "is_cloud, cost_usd, entity_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ts,
                    trace_id,
                    provider,
                    model_used,
                    latency_ms,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    cache_read_tokens,
                    provider_prompt_tokens if provider_prompt_tokens is not None else prompt_tokens,
                    provider_completion_tokens
                    if provider_completion_tokens is not None
                    else completion_tokens,
                    int(is_cloud),
                    cost_usd,
                    entity_id,
                ),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)

    async def get_daily_cloud_spend(self, since_ts_ms: int) -> float:
        """Sum cost_usd for cloud rows since a ms timestamp. [M1 AnyIO]"""

        def _sync_get() -> float:
            row = self._conn.execute(
                "SELECT SUM(cost_usd) as total FROM performance WHERE ts >= ? AND is_cloud = 1",
                (since_ts_ms,),
            ).fetchone()
            return float(row["total"]) if row and row["total"] else 0.0

        return await anyio.to_thread.run_sync(_sync_get)

    async def get_token_divergence(
        self,
        hours: int = 24,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate token counting divergence (QW-3 CI Guard).

        Compares local prompt_tokens estimate against provider returned usage
        to detect tokenizer drift. Returns divergence statistics and drift flag.

        Args:
            hours: Time window in hours to analyze.
            provider: Optional provider filter.

        Returns:
            Dict with mean_ratio, max_ratio, sample_count, drift_detected.
        """
        since_ts = int((time.time() - hours * 3600) * 1000)
        query = (
            "SELECT prompt_tokens, provider_prompt_tokens, "
            "completion_tokens, provider_completion_tokens "
            "FROM performance WHERE ts >= ? AND provider_prompt_tokens > 0"
        )
        params: list = [since_ts]
        if provider:
            query += " AND provider = ?"
            params.append(provider)

        def _sync_query() -> Dict[str, Any]:
            cursor = self._conn.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                return {
                    "mean_ratio": 1.0,
                    "max_ratio": 1.0,
                    "sample_count": 0,
                    "drift_detected": False,
                }
            ratios = []
            for row in rows:
                local_prompt = row[0] if row[0] else 1
                provider_prompt = row[1] if row[1] else 1
                ratios.append(provider_prompt / local_prompt)
            mean_ratio = sum(ratios) / len(ratios)
            max_ratio = max(ratios)
            return {
                "mean_ratio": round(mean_ratio, 4),
                "max_ratio": round(max_ratio, 4),
                "sample_count": len(ratios),
                "drift_detected": max_ratio > 1.15,
            }

        return await anyio.to_thread.run_sync(_sync_query)

    async def update_cost(self, trace_id: str, cost_usd: float) -> None:
        """Set cost_usd on the performance row for trace_id. [M1 AnyIO] Lock-serialized —
        this is a write and must not race concurrent record_performance() writes."""

        def _sync_update() -> None:
            self._conn.execute(
                "UPDATE performance SET cost_usd = ? WHERE trace_id = ? AND is_cloud = 1",
                (cost_usd, trace_id),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_update)

    async def set_baseline(
        self,
        metric_name: str,
        value: float,
        sample_count: int,
        std_deviation: Optional[float] = None,
        source: str = "profiler",
    ) -> None:
        """Set or update a baseline metric for regression detection."""
        now = int(time.time() * 1000)

        def _sync_insert() -> None:
            self._conn.execute(
                "INSERT OR REPLACE INTO baselines (metric_name, metric_value, sample_count, std_deviation, created_at, source) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (metric_name, value, sample_count, std_deviation, now, source),
            )
            self._conn.commit()

        async with self._get_write_lock():
            await anyio.to_thread.run_sync(_sync_insert)

    # ── Query Methods ────────────────────────────────────────────────────
    # [M1 AnyIO] Reads offloaded via to_thread.run_sync (no write lock needed;
    # reads racing reads is safe, reads racing writes handled by busy_timeout).

    async def get_baseline(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Get a baseline metric by name."""

        def _sync_get():
            row = self._conn.execute(
                "SELECT metric_name, metric_value, sample_count, std_deviation, created_at, source "
                "FROM baselines WHERE metric_name = ?",
                (metric_name,),
            ).fetchone()
            return dict(row) if row else None

        return await anyio.to_thread.run_sync(_sync_get)

    # ── Regression Detection ─────────────────────────────────────────────

    async def detect_regression(
        self,
        metric_name: str,
        current_value: float,
        threshold: float = 0.1,
    ) -> bool:
        """Detect if current value regresses from baseline.

        Uses 3-sigma rule if std_deviation is available,
        otherwise falls back to percentage threshold.
        """
        baseline = await self.get_baseline(metric_name)
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

    async def get_performance_trend(
        self,
        provider: Optional[str] = None,
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """Get performance trend over time."""
        ts_threshold = int((time.time() - hours * 3600) * 1000)

        def _sync_get():
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

        return await anyio.to_thread.run_sync(_sync_get)

    async def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        ts_threshold = int((time.time() - hours * 3600) * 1000)

        def _sync_get():
            cursor = self._conn.execute(
                "SELECT error_type, COUNT(*) as count FROM errors WHERE ts > ? GROUP BY error_type ORDER BY count DESC",
                (ts_threshold,),
            )
            return {row["error_type"]: row["count"] for row in cursor.fetchall()}

        return await anyio.to_thread.run_sync(_sync_get)

    async def get_breaker_history(
        self, provider: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get circuit breaker transition history."""

        def _sync_get():
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

        return await anyio.to_thread.run_sync(_sync_get)

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""

        def _sync_get():
            stats = {}
            for table in ["events", "errors", "breaker_transitions", "performance", "baselines"]:
                cursor = self._conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()["count"]
            stats["db_size_bytes"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            return stats

        return await anyio.to_thread.run_sync(_sync_get)
