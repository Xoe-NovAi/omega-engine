# AP: AP-LATENCY-TRACKER-v1.0.0
"""
Sovereign Latency Tracker — Time-series monitoring for provider performance.
"""

# DocRef: docs/explanation/metrics-pipeline.md
import time
import logging
from typing import Any, Dict, Optional
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

from omega.observability import get_engine
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


class LatencyTracker:
    """
    Tracks provider latency over time to detect 'busy hours' and server degradation.
    Wired into the unified MetricsDB for high-speed, zero-wear logging.
    """

    def __init__(self):
        pass

    async def record(
        self,
        provider: str,
        model: str,
        latency_ms: float,
        status: str = "success",
        trace_id: Optional[str] = None,
        is_cloud: bool = False,
    ) -> None:
        """Records a single inference latency event via the ObservabilityEngine. [M1 AnyIO]"""
        try:
            await get_engine().record_performance(
                latency_ms=latency_ms,
                provider=provider,
                model_used=model,
                is_cloud=is_cloud,
                trace_id=trace_id,
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to record latency metric via engine: {e}")

    def get_recent_stats(
        self, provider: str, model: str, window_minutes: int = 15
    ) -> Dict[str, Any]:
        """Calculates P50, P95, and average latency for the given window using MetricsDB."""
        try:
            metrics_db = get_engine().metrics_db
            if not metrics_db:
                return {"status": "error", "message": "MetricsDB not initialized"}

            ts_threshold = int((time.time() - window_minutes * 60) * 1000)
            cursor = metrics_db._conn.execute(
                "SELECT latency_ms FROM performance WHERE ts > ? AND provider = ? AND model_used = ?",
                (ts_threshold, provider, model),
            )
            latencies = [row["latency_ms"] for row in cursor.fetchall()]

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
                "max": latencies[-1],
            }
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Error calculating latency stats from MetricsDB: {e}")
            return {"status": "error", "message": str(e)}


# Global singleton for the engine
tracker = LatencyTracker()
# Global singleton for the engine
tracker = LatencyTracker()
