# AP: AP-LATENCY-TRACKER-v1.0.0
"""
Sovereign Latency Tracker — Time-series monitoring for provider performance.
"""
import time
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class LatencyTracker:
    """
    Tracks provider latency over time to detect 'busy hours' and server degradation.
    Uses a local SQLite WAL-mode database for high-speed, zero-wear logging.
    """
    def __init__(self, db_path: str = "data/observability/latency_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS latency_logs (
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    provider TEXT,
                    model TEXT,
                    latency_ms REAL,
                    status TEXT,
                    trace_id TEXT
                )
            """)
            conn.commit()

    def record(self, provider: str, model: str, latency_ms: float, status: str = "success", trace_id: Optional[str] = None):
        """Records a single inference latency event."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO latency_logs (provider, model, latency_ms, status, trace_id) VALUES (?, ?, ?, ?, ?)",
                    (provider, model, latency_ms, status, trace_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record latency metric: {e}")

    def get_recent_stats(self, provider: str, model: str, window_minutes: int = 15) -> Dict[str, Any]:
        """Calculates P50, P95, and average latency for the given window."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT latency_ms FROM latency_logs WHERE provider = ? AND model = ? AND timestamp > datetime('now', ?)",
                    (provider, model, f"-{window_minutes} minutes")
                )
                latencies = [row[0] for row in cursor.fetchall()]
                
                if not latencies:
                    return {"status": "no_data"}
                
                latencies.sort()
                n = len(latencies)
                return {
                    "count": n,
                    "avg": sum(latencies) / n,
                    "p50": latencies[int(n * 0.5)],
                    "p95": latencies[int(n * 0.95)],
                    "min": latencies[0],
                    "max": latencies[-1]
                }
        except Exception as e:
            logger.error(f"Error calculating latency stats: {e}")
            return {"status": "error", "message": str(e)}

# Global singleton for the engine
tracker = LatencyTracker()
