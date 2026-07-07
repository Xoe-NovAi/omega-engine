# 🔱 Regression Watcher — Automated Baseline Monitoring
# AP: AP-REGRESSION-WATCHER-v1.0.0
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ trc_regression_watcher ⬡ OBSERVABILITY
#
# Background task that polls MetricsDB baselines and detects regressions.
# Emits alerts via Hivemind and ObservabilityEngine events.
#
# [id-soft: quake-1996] Thinker Chain — periodic background task for health monitoring.
# [id-soft: doom3-2004] Event System — structured event logging for observability.

import anyio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from omega.observability.metrics_db import MetricsDB
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


def _get_obs_engine():
    """Lazy import to avoid circular dependency."""
    from omega.observability import get_engine
    return get_engine()


def _get_event_type():
    """Lazy import to avoid circular dependency."""
    from omega.observability import EventType
    return EventType


class RegressionWatcher:
    """
    Background task that monitors MetricsDB baselines for regressions.
    
    Runs periodically (default 5 min) and checks all registered baselines
    against current performance metrics. Emits alerts via Hivemind and
    ObservabilityEngine events.
    """
    
    def __init__(
        self,
        metrics_db: MetricsDB,
        check_interval_seconds: int = 300,  # 5 minutes
        regression_threshold: float = 0.1,  # 10% default
    ):
        self._metrics_db = metrics_db
        self._check_interval = check_interval_seconds
        self._threshold = regression_threshold
        self._running = False
        self._task_group: Optional[anyio.abc.TaskGroup] = None
    
    async def start(self) -> None:
        """Start the regression watcher background task."""
        if self._running:
            logger.warning("RegressionWatcher already running")
            return
        
        self._running = True
        logger.info(f"RegressionWatcher started (interval={self._check_interval}s)")
        
        # Run in background task group
        async with anyio.create_task_group() as tg:
            self._task_group = tg
            tg.start_soon(self._run_loop)
    
    async def stop(self) -> None:
        """Stop the regression watcher."""
        self._running = False
        if self._task_group:
            self._task_group.cancel_scope.cancel()
        logger.info("RegressionWatcher stopped")
    
    async def _run_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_regressions()
            except Exception as e:
                logger.error(f"RegressionWatcher check failed: {e}")
            
            # Wait for next interval
            try:
                await anyio.sleep(self._check_interval)
            except anyio.get_cancelled_exc_class():
                break
    
    async def _check_regressions(self) -> None:
        """Check all baselines for regressions."""
        # Get all baselines
        baselines = self._get_all_baselines()
        if not baselines:
            return
        
        obs = get_engine()
        
        for baseline in baselines:
            metric_name = baseline["metric_name"]
            baseline_value = baseline["metric_value"]
            std_dev = baseline.get("std_deviation")
            
            # Get recent performance data for this metric
            recent = self._get_recent_performance(metric_name, hours=1)
            if not recent:
                continue
            
            # Calculate current average
            current_values = [r["latency_ms"] for r in recent if "latency_ms" in r]
            if not current_values:
                continue
            
            current_avg = sum(current_values) / len(current_values)
            
            # Check for regression
            is_regression = self._detect_regression(
                baseline_value, current_avg, std_dev
            )
            
            if is_regression:
                await self._emit_regression_alert(
                    metric_name=metric_name,
                    baseline_value=baseline_value,
                    current_value=current_avg,
                    std_dev=std_dev,
                    sample_count=len(current_values),
                )
    
    def _get_all_baselines(self) -> List[Dict[str, Any]]:
        """Get all registered baselines from MetricsDB."""
        try:
            cursor = self._metrics_db._conn.execute(
                "SELECT metric_name, metric_value, sample_count, std_deviation, created_at, source "
                "FROM baselines"
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch baselines: {e}")
            return []
    
    def _get_recent_performance(
        self, 
        metric_name: str, 
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Get recent performance data for a metric."""
        try:
            ts_threshold = int((time.time() - hours * 3600) * 1000)
            cursor = self._metrics_db._conn.execute(
                "SELECT latency_ms, provider, model_used, ts FROM performance "
                "WHERE ts > ? ORDER BY ts DESC LIMIT 100",
                (ts_threshold,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch recent performance: {e}")
            return []
    
    def _detect_regression(
        self, 
        baseline: float, 
        current: float, 
        std_dev: Optional[float]
    ) -> bool:
        """Detect if current value represents a regression from baseline."""
        if baseline == 0:
            return current > 0
        
        if std_dev and std_dev > 0:
            # 3-sigma rule
            z_score = abs(current - baseline) / std_dev
            return z_score > 3.0
        else:
            # Percentage threshold
            return abs(current - baseline) / baseline > self._threshold
    
    async def _emit_regression_alert(
        self,
        metric_name: str,
        baseline_value: float,
        current_value: float,
        std_dev: Optional[float],
        sample_count: int,
    ) -> None:
        """Emit regression alert via ObservabilityEngine and Hivemind."""
        trace_id = f"trc_regression_{int(time.time() * 1000)}"
        
        # Log to ObservabilityEngine
        obs = _get_obs_engine()
        obs.log_event(
            _get_event_type().ERROR,
            trace_id,
            {
                "error_type": "REGRESSION_DETECTED",
                "error_message": f"Performance regression detected for {metric_name}",
                "context": {
                    "metric_name": metric_name,
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "deviation_pct": round(
                        abs(current_value - baseline_value) / baseline_value * 100, 2
                    ) if baseline_value else 0,
                    "std_deviation": std_dev,
                    "sample_count": sample_count,
                    "threshold": self._threshold,
                },
            },
        )
        
        # Also record in MetricsDB errors table
        obs.record_metrics_error(
            error_type="REGRESSION_DETECTED",
            error_message=f"Performance regression: {metric_name} deviated from baseline",
            trace_id=trace_id,
            context={
                "metric_name": metric_name,
                "baseline_value": baseline_value,
                "current_value": current_value,
            },
        )
        
        logger.warning(
            f"REGRESSION DETECTED: {metric_name} — "
            f"baseline={baseline_value:.2f}ms, current={current_value:.2f}ms "
            f"({abs(current_value-baseline_value)/baseline_value*100:.1f}% deviation)"
        )


async def run_regression_watcher(
    metrics_db: MetricsDB,
    interval_seconds: int = 300,
    threshold: float = 0.1,
) -> None:
    """Convenience function to run the regression watcher."""
    watcher = RegressionWatcher(metrics_db, interval_seconds, threshold)
    await watcher.start()


# ── Singleton Management ──────────────────────────────────────────────────

_watcher: Optional[RegressionWatcher] = None


async def get_regression_watcher(
    metrics_db: Optional[MetricsDB] = None,
    interval_seconds: int = 300,
    threshold: float = 0.1,
) -> RegressionWatcher:
    """Get or create the singleton RegressionWatcher."""
    global _watcher
    if _watcher is None:
        if metrics_db is None:
            from omega.observability import get_engine
            obs = get_engine()
            metrics_db = obs.metrics_db
        _watcher = RegressionWatcher(metrics_db, interval_seconds, threshold)
    return _watcher


async def start_regression_watcher() -> None:
    """Start the singleton regression watcher."""
    watcher = await get_regression_watcher()
    await watcher.start()


async def stop_regression_watcher() -> None:
    """Stop the singleton regression watcher."""
    global _watcher
    if _watcher:
        await _watcher.stop()
        _watcher = None