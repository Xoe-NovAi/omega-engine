# 🔱 Omega Engine — Observability Reader
# AP: AP-OBS-READER-v1.0.0
# Status: ACTIVE
#
# Unified, read-only facade for Omega Engine observability data.
#
"""
Sovereign Observatory Reader (observability_reader.py)
Unified, read-only facade for Omega Engine observability data.

Mandate 1: AnyIO Absolute (No asyncio)
Mandate 8: Zero Telemetry (100% Local)
Mandate 9: Error Integrity (Typed, Traceable Errors)
"""
# DocRef: docs/explanation/metrics-pipeline.md

import json
import sqlite3
import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any

import anyio

# ─── Data Models ──────────────────────────────────────────────────────────────


@dataclass
class MetricSeries:
    timestamps: List[float]
    values: List[float]


@dataclass
class TraceEvent:
    timestamp: str
    level: str
    entity: str
    message: str
    trace_id: str
    raw: Dict[str, Any]


@dataclass
class TokenBurn:
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    provider_name: str


@dataclass
class CognitiveVelocity:
    tokens_per_second: float
    acceleration: float  # Rate of change (tokens/sec^2)


@dataclass
class FleetHealth:
    breaker_states: Dict[str, str]
    global_error_rate: float


# ─── Custom Errors ────────────────────────────────────────────────────────────


class ObservabilityError(Exception):
    """Base error for observability reader failures."""

    pass


class DatabaseLockedError(ObservabilityError):
    """Raised if the database is locked despite read-only mode."""

    pass


# ─── Main Reader Class ────────────────────────────────────────────────────────


class SovereignReader:
    def __init__(self, db_path: Path, trace_dir: Path, crash_dir: Path):
        self.db_path = db_path
        self.trace_dir = trace_dir
        self.crash_dir = crash_dir

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a read-only SQLite connection to prevent locking the WAL."""
        if not self.db_path.exists():
            # Return an in-memory DB if it doesn't exist yet to prevent crashes
            return sqlite3.connect(":memory:")

        try:
            # URI mode required for ?mode=ro
            conn = sqlite3.connect(f"file:{self.db_path.absolute()}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise ObservabilityError(f"Failed to connect to metrics DB: {e}")

    # ─── Metrics & TSDB Queries ───────────────────────────────────────────────

    def _sync_get_metric_series(
        self, metric_name: str, entity_id: Optional[str], window_mins: int
    ) -> MetricSeries:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_mins)).timestamp()

        query = "SELECT ts as timestamp, value FROM metrics WHERE metric_name = ? AND ts >= ?"
        params = [metric_name, cutoff]

        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)

        query += " ORDER BY ts ASC"

        try:
            with self._get_connection() as conn:
                # Check if table exists first (graceful degradation)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
                if not cur.fetchone():
                    return MetricSeries(timestamps=[], values=[])

                cur.execute(query, params)
                rows = cur.fetchall()
                return MetricSeries(
                    timestamps=[r["timestamp"] for r in rows], values=[r["value"] for r in rows]
                )
        except sqlite3.Error as e:
            raise ObservabilityError(f"Database query failed: {e}")

    async def get_metric_series(
        self, metric_name: str, entity_id: Optional[str] = None, window_mins: int = 60
    ) -> MetricSeries:
        return await anyio.to_thread.run_sync(
            self._sync_get_metric_series, metric_name, entity_id, window_mins
        )

    def _sync_get_fleet_health(self) -> FleetHealth:
        # In a full implementation, this would query a circuit_breakers table and error metrics.
        # For now, we scaffold the query structure.
        breaker_states = {}
        error_rate = 0.0

        try:
            with self._get_connection() as conn:
                cur = conn.cursor()

                # Scaffold: get latest breaker states
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='circuit_breakers'"
                )
                if cur.fetchone():
                    cur.execute("SELECT provider, state FROM circuit_breakers")
                    breaker_states = {r["provider"]: r["state"] for r in cur.fetchall()}

                # Scaffold: calculate error rate over last 5 mins using performance table
                cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
                )
                if cur.fetchone():
                    cur.execute(
                        "SELECT COUNT(*) as total, SUM(CASE WHEN is_cloud = 0 THEN 1 ELSE 0 END) as errors FROM performance WHERE ts >= ?",
                        (cutoff,),
                    )
                    row = cur.fetchone()
                    if row and row["total"] > 0:
                        error_rate = row["errors"] / row["total"]

        except sqlite3.Error as e:
            # Graceful degradation if tables don't exist yet
            pass

        return FleetHealth(breaker_states=breaker_states, global_error_rate=error_rate)

    async def get_fleet_health(self) -> FleetHealth:
        return await anyio.to_thread.run_sync(self._sync_get_fleet_health)

    # ─── Token & Cost Attribution ─────────────────────────────────────────────

    def _sync_get_entity_cost(self, entity_id: str, session_id: Optional[str]) -> TokenBurn:
        query = "SELECT SUM(prompt_tokens) as p, SUM(completion_tokens) as c, SUM(cost_usd) as cost, provider FROM performance WHERE entity_id = ?"
        params = [entity_id]

        if session_id:
            query += " AND trace_id = ?"
            params.append(session_id)

        query += " GROUP BY provider"

        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
                )
                if not cur.fetchone():
                    return TokenBurn(0, 0, 0.0, "unknown")

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return TokenBurn(0, 0, 0.0, "unknown")

                # Aggregate across providers if multiple
                p_tokens = sum(r["p"] for r in rows if r["p"])
                c_tokens = sum(r["c"] for r in rows if r["c"])
                total_cost = sum(r["cost"] for r in rows if r["cost"])
                # Just take the most recent/dominant provider for the summary
                provider = rows[0]["provider"]

                return TokenBurn(p_tokens, c_tokens, total_cost, provider)
        except sqlite3.Error as e:
            raise ObservabilityError(f"Performance query failed: {e}")

    async def get_entity_cost(self, entity_id: str, session_id: Optional[str] = None) -> TokenBurn:
        return await anyio.to_thread.run_sync(self._sync_get_entity_cost, entity_id, session_id)

    def _sync_get_sovereignty_ratio(self, entity_id: str, window_secs: int = 300) -> float:
        """Calculate local vs cloud inference ratio for an entity.

        [M22 SSOT / Decision 3] Queries the corrected view
        ``v_performance_corrected`` (config-derived classification) so the
        entity-level ratio always matches the global ratio in
        ``sovereignty.py``.
        """
        now = datetime.now(timezone.utc).timestamp()
        cutoff = now - window_secs

        # Preserve graceful degradation when the DB is absent (no side effects).
        if not self.db_path.exists():
            return 1.0

        # Ensure the corrected schema/view exists (idempotent), mirroring
        # sovereignty.py._ensure_corrected_schema so both paths share one view.
        try:
            from omega.observability.metrics_db import MetricsDB

            db = MetricsDB(self.db_path)
            try:
                db.initialize()
                db.create_corrected_performance_view()
            finally:
                db.close()
        except sqlite3.Error as e:
            raise ObservabilityError(f"Sovereignty schema ensure failed: {e}")

        query = """
            SELECT
                SUM(CASE WHEN is_cloud_corrected = 0 THEN 1 ELSE 0 END) as local_count,
                SUM(CASE WHEN is_cloud_corrected = 1 THEN 1 ELSE 0 END) as cloud_count
            FROM v_performance_corrected
            WHERE entity_id = ? AND ts >= ?
        """

        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
                )
                if not cur.fetchone():
                    return 1.0

                cur.execute(query, (entity_id, cutoff))
                row = cur.fetchone()

                local_count = row["local_count"] or 0
                cloud_count = row["cloud_count"] or 0
                total = local_count + cloud_count

                if total == 0:
                    return 1.0

                return local_count / total
        except sqlite3.Error as e:
            raise ObservabilityError(f"Sovereignty ratio calculation failed: {e}")

    async def get_sovereignty_ratio(self, entity_id: str, window_secs: int = 300) -> float:
        return await anyio.to_thread.run_sync(
            self._sync_get_sovereignty_ratio, entity_id, window_secs
        )

    def _sync_get_somatic_pressure(self, entity_id: str, window_secs: int = 60) -> Dict[str, Any]:
        """Get hardware pressure metrics for an entity."""
        now = datetime.now(timezone.utc).timestamp()
        cutoff = now - window_secs

        query = """
            SELECT
                AVG(latency_ms) as avg_latency,
                MAX(latency_ms) as max_latency,
                COUNT(*) as request_count
            FROM performance
            WHERE entity_id = ? AND ts >= ?
        """

        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
                )
                if not cur.fetchone():
                    return {"avg_latency_ms": 0.0, "max_latency_ms": 0.0, "request_count": 0}

                cur.execute(query, (entity_id, cutoff))
                row = cur.fetchone()

                return {
                    "avg_latency_ms": row["avg_latency"] or 0.0,
                    "max_latency_ms": row["max_latency"] or 0.0,
                    "request_count": row["request_count"] or 0,
                }
        except sqlite3.Error as e:
            raise ObservabilityError(f"Somatic pressure calculation failed: {e}")

    async def get_somatic_pressure(self, entity_id: str, window_secs: int = 60) -> Dict[str, Any]:
        return await anyio.to_thread.run_sync(
            self._sync_get_somatic_pressure, entity_id, window_secs
        )

    def _sync_get_cognitive_velocity(
        self, entity_id: str, window_secs: int = 30
    ) -> CognitiveVelocity:
        """Calculates tokens/sec and acceleration (change in tokens/sec) to detect loops."""
        now = datetime.now(timezone.utc).timestamp()
        t1 = now - window_secs
        t2 = now - (window_secs * 2)

        query = """
            SELECT
                SUM(CASE WHEN ts >= ? THEN prompt_tokens + completion_tokens ELSE 0 END) as window1_tokens,
                SUM(CASE WHEN ts >= ? AND ts < ? THEN prompt_tokens + completion_tokens ELSE 0 END) as window2_tokens
            FROM performance
            WHERE entity_id = ? AND ts >= ?
        """

        try:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
                )
                if not cur.fetchone():
                    return CognitiveVelocity(0.0, 0.0)

                cur.execute(query, (t1, t2, t1, entity_id, t2))
                row = cur.fetchone()

                w1_tokens = row["window1_tokens"] or 0
                w2_tokens = row["window2_tokens"] or 0

                v1 = w1_tokens / window_secs
                v2 = w2_tokens / window_secs

                acceleration = (v1 - v2) / window_secs

                return CognitiveVelocity(tokens_per_second=v1, acceleration=acceleration)
        except sqlite3.Error as e:
            raise ObservabilityError(f"Velocity calculation failed: {e}")

    async def get_cognitive_velocity(
        self, entity_id: str, window_secs: int = 30
    ) -> CognitiveVelocity:
        return await anyio.to_thread.run_sync(
            self._sync_get_cognitive_velocity, entity_id, window_secs
        )

    # ─── Forensic Trace Tailing (JSONL) ───────────────────────────────────────

    def _sync_tail_live_traces(self, max_lines: int) -> List[TraceEvent]:
        """O(1) reverse-binary scan of the active daily event file."""
        # Events are written to data/logs/events/YYYY-MM-DD.jsonl
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        trace_file = self.trace_dir.parent / "logs" / "events" / f"{today}.jsonl"

        if not trace_file.exists():
            return []

        events = []
        chunk_size = 8192

        try:
            with open(trace_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                position = file_size
                buffer = b""

                while position > 0 and len(events) < max_lines:
                    read_size = min(chunk_size, position)
                    position -= read_size
                    f.seek(position)
                    chunk = f.read(read_size)
                    buffer = chunk + buffer

                    lines = buffer.split(b"\n")
                    # The first element might be an incomplete line, save it for the next iteration
                    buffer = lines.pop(0)

                    # Process lines in reverse
                    for line in reversed(lines):
                        if not line.strip():
                            continue
                        if len(events) >= max_lines:
                            break
                        try:
                            data = json.loads(line.decode("utf-8"))
                            # Extract the actual event data from the wrapped format
                            event_data = data.get("data", data)
                            events.append(
                                TraceEvent(
                                    timestamp=data.get("timestamp", ""),
                                    level=event_data.get("level", "INFO"),
                                    entity=event_data.get("entity", "system"),
                                    message=event_data.get("message", str(event_data)[:200]),
                                    trace_id=data.get("trace_id", "unknown"),
                                    raw=data,
                                )
                            )
                        except json.JSONDecodeError:
                            continue

                # Handle the last remaining buffer if we haven't hit max_lines
                if buffer.strip() and len(events) < max_lines:
                    try:
                        data = json.loads(buffer.decode("utf-8"))
                        event_data = data.get("data", data)
                        events.append(
                            TraceEvent(
                                timestamp=data.get("timestamp", ""),
                                level=event_data.get("level", "INFO"),
                                entity=event_data.get("entity", "system"),
                                message=event_data.get("message", str(event_data)[:200]),
                                trace_id=data.get("trace_id", "unknown"),
                                raw=data,
                            )
                        )
                    except json.JSONDecodeError:
                        pass

        except IOError as e:
            raise ObservabilityError(f"Failed to tail traces: {e}")

        # Reverse again to return in chronological order (oldest to newest among the tail)
        return list(reversed(events))

    async def tail_live_traces(self, max_lines: int = 50) -> List[TraceEvent]:
        return await anyio.to_thread.run_sync(self._sync_tail_live_traces, max_lines)

    def _sync_get_crash_dump(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific crash dump from the bleg directory."""
        # Sanitize trace_id to prevent path traversal
        safe_trace_id = "".join(c for c in trace_id if c.isalnum() or c in "-_")
        dump_file = self.crash_dir / f"{safe_trace_id}.json"

        if not dump_file.exists():
            return None

        try:
            with open(dump_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise ObservabilityError(f"Failed to read crash dump {safe_trace_id}: {e}")

    async def get_crash_dump(self, trace_id: str) -> Optional[Dict[str, Any]]:
        return await anyio.to_thread.run_sync(self._sync_get_crash_dump, trace_id)
