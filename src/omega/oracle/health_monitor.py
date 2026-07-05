# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Health Monitor — Provider Health & Circuit Breaking
# AP: AP-HEALTH-MONITOR-v1.0.0
#
# Tracks per-provider circuit breakers, per-model latency percentiles,
# daily quota usage, and success/failure rates.
# AnyIO-native, zero external dependencies.
#
# Interface expected by TriageRouter:
#   - is_available(model_name) -> bool
#   - get_latency_p99(model_name) -> int
#   - get_quota_usage(provider) -> float (0.0-1.0)
#   - get_success_rate(model_name) -> float (0.0-1.0)

from __future__ import annotations

import anyio
import inspect
import time
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Deque, Dict, Optional
# Module-level singleton
_health_monitor: Optional[HealthMonitor] = None

def get_health_monitor() -> HealthMonitor:
    """Get or create the singleton HealthMonitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor



from omega.constants import ZONEID_BREAKER, validate_zoneid


logger = logging.getLogger("omega.health_monitor")


# ── Enums ──────────────────────────────────────────────────────────────

class CircuitState(Enum):
    CLOSED = "closed"         # Normal operation (HEALTHY)
    DEGRADED = "degraded"     # High latency or minor error spikes
    OPEN = "open"             # Failing fast, no requests (CRITICAL)
    HALF_OPEN = "half_open"   # Probe allowed (PROBATION)
    UNKNOWN = "unknown"       # Initial state / Cold start


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


# ── Data Classes ───────────────────────────────────────────────────────

@dataclass
class LatencySnapshot:
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    count: int = 0
    min_ms: float = float("inf")
    max_ms: float = 0.0


@dataclass
class QuotaStatus:
    daily_limit: int = 0           # 0 = unlimited
    used_today: int = 0
    reset_date: str = ""           # YYYY-MM-DD


# ── Circuit Breaker ────────────────────────────────────────────────────

class CircuitOpenError(Exception):
    """Raised when circuit breaker is open and requests are blocked."""
    pass


class AsyncCircuitBreaker:
    """Lightweight circuit breaker — AnyIO compliant, no dependencies."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_requests: int = 1,
    ):
        self.name = name
        # [id-soft: doom-1993] ZONEID Pattern — circuit breaker state marker
        self.magic = ZONEID_BREAKER
        self.state = CircuitState.CLOSED
        
        # --- Stochastic Metrics ---
        self.ema_latency = 0.0
        self.ema_quality = 1.0
        self.cusum_g = 0.0
        self.failure_count = 0
        
        # Constants from R_SOVEREIGN_INFRA_HARDENING
        self.alpha_lat = 0.2
        self.alpha_qual = 0.3
        self.cusum_drift = 0.5
        self.cusum_threshold = 4.0
        
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_requests = half_open_max_requests
        self.half_open_requests = 0
        self.last_failure_time: Optional[float] = None
        self._lock = anyio.Lock()

    async def call(self, func, *args, trace_id: Optional[str] = None, **kwargs):
        """Execute function through circuit breaker."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_transition_to_half_open():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                else:
                    raise CircuitOpenError(
                        f"Circuit '{self.name}' is OPEN. "
                        f"Retry in {self._recovery_remaining():.0f}s"
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.half_open_max_requests:
                    raise CircuitOpenError(
                        f"Circuit '{self.name}' is HALF_OPEN "
                        f"(probe limit reached)"
                    )
                self.half_open_requests += 1

        try:
            start = time.monotonic()
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            latency = (time.monotonic() - start) * 1000
            
            # We assume success if no exception. Quality is 1.0 for basic success.
            await self._on_success(latency=latency, quality=1.0, trace_id=trace_id)
            return result
        except Exception as e:
            if self._is_circuit_breaking_error(e):
                await self._on_failure(trace_id=trace_id)
            raise

    async def _on_success(self, latency: float, quality: float = 1.0, trace_id: Optional[str] = None):
        # [id-soft: doom-1993] ZONEID Pattern — pre-transition integrity check
        validate_zoneid(self.magic, ZONEID_BREAKER, f"AsyncCircuitBreaker._on_success({self.name})")
        async with self._lock:
            old_state = self.state
            
            # 1. Update EMA Latency
            if self.ema_latency == 0:
                self.ema_latency = latency
            else:
                self.ema_latency = (self.alpha_lat * latency) + ((1 - self.alpha_lat) * self.ema_latency)
            
            # 2. Update EMA Quality
            self.ema_quality = (self.alpha_qual * quality) + ((1 - self.alpha_qual) * self.ema_quality)
            
            # 3. Update CUSUM (success = 0 error)
            # Z_t = (0 - mu_0) / sigma_0. Using simplified Z_t = -0.5 for success
            self.cusum_g = max(0.0, self.cusum_g - 0.5)
            
            # 4. Determine State based on Health Score
            # Health = (0.4 * LatScore) + (0.35 * ErrScore) + (0.25 * QualScore)
            # Simplified: If CUSUM is low and EMA latency is reasonable, we are CLOSED.
            if self.cusum_g < 1.0 and self.ema_latency < 2000:
                self.state = CircuitState.CLOSED
            elif self.cusum_g < self.cusum_threshold:
                self.state = CircuitState.DEGRADED
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                
            self.failure_count = 0
            self.half_open_requests = 0
            
            if trace_id and old_state != self.state:
                try:
                    from omega.observability import get_engine, EventType
                    engine = get_engine()
                    engine.log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {"provider": self.name, "event": "circuit_closed",
                         "from": old_state.value, "to": self.state.value}
                    )
                    # Also record to MetricsDB
                    engine.record_breaker_transition(
                        provider=self.name,
                        from_state=old_state.value,
                        to_state=self.state.value,
                        trace_id=trace_id,
                        reason="success_recovery",
                    )
                except Exception as e:
                    logger.warning(f"Circuit closed event failed — observability unavailable: {e}")
                    pass

    async def _on_failure(self, trace_id: Optional[str] = None):
        # [id-soft: doom-1993] ZONEID Pattern — pre-transition integrity check
        validate_zoneid(self.magic, ZONEID_BREAKER, f"AsyncCircuitBreaker._on_failure({self.name})")
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            old_state = self.state
            
            # 1. Update CUSUM (failure = 1 error)
            # Z_t = (1 - mu_0) / sigma_0. Using simplified Z_t = 1.0 for failure
            self.cusum_g = max(0.0, self.cusum_g + 1.0 - self.cusum_drift)
            
            # 2. State Transition
            if self.cusum_g > self.cusum_threshold:
                self.state = CircuitState.OPEN
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            elif self.failure_count > (self.failure_threshold // 2):
                self.state = CircuitState.DEGRADED
            else:
                self.state = CircuitState.CLOSED

            if trace_id and old_state != self.state:
                try:
                    from omega.observability import get_engine, EventType
                    engine = get_engine()
                    engine.log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {"provider": self.name, "event": "circuit_opened",
                         "from": old_state.value, "to": self.state.value,
                         "failure_count": self.failure_count, "cusum": self.cusum_g}
                    )
                    # Also record to MetricsDB
                    engine.record_breaker_transition(
                        provider=self.name,
                        from_state=old_state.value,
                        to_state=self.state.value,
                        trace_id=trace_id,
                        reason=f"failures={self.failure_count},cusum={self.cusum_g:.2f}",
                    )
                except Exception as e:
                    logger.warning(f"Circuit opened event failed — observability unavailable: {e}")
                    pass


    def _should_transition_to_half_open(self) -> bool:
        if self.last_failure_time is None:
            return False
        elapsed = time.monotonic() - self.last_failure_time
        return elapsed >= self.recovery_timeout

    def _recovery_remaining(self) -> float:
        if self.last_failure_time is None:
            return 0.0
        elapsed = time.monotonic() - self.last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    @staticmethod
    def _is_circuit_breaking_error(exc: Exception) -> bool:
        """Determine if error should trip the circuit.

        Any network-level exception class or message matching is
        considered circuit-breaking.
        """
        # These exception types are always circuit-breaking
        if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
            return True

        error_str = str(exc).lower()
        circuit_breaking_keywords = [
            "connection", "timeout", "500", "502", "503", "504",
            "unavailable", "refused", "rate limit", "too many requests",
        ]
        return any(kw in error_str for kw in circuit_breaking_keywords)

    @property
    def is_available(self) -> bool:
        return self.state != CircuitState.OPEN


# ── Health Monitor ─────────────────────────────────────────────────────

class HealthMonitor:
    """
    Provider Health Monitor — AnyIO-native, zero external dependencies.

    Tracks per-provider circuit breakers, per-model latency percentiles,
    daily quota usage, and success/failure rates.
    """

    def __init__(
        self,
        providers: Optional[Dict[str, dict]] = None,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        probe_interval: float = 300.0,
        latency_window_size: int = 100,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._probe_interval = probe_interval
        self._latency_window_size = latency_window_size

        # Circuit breakers: one per provider
        self._breakers: Dict[str, AsyncCircuitBreaker] = {}
        if providers:
            for name in providers:
                self._breakers[name] = AsyncCircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                )

        # Latency tracking: sliding window per model
        self._latency_windows: Dict[str, Deque[float]] = {}

        # Quota tracking: per provider
        self._quotas: Dict[str, QuotaStatus] = {}

        # Success/failure counters: per model
        self._success_counts: Dict[str, int] = {}
        self._failure_counts: Dict[str, int] = {}

        # Provider status cache
        self._status: Dict[str, ProviderStatus] = {
            name: ProviderStatus.HEALTHY for name in self._breakers
        }

        # Lock for thread-safe updates
        self._lock = anyio.Lock()

        # Background task control
        self._running = False
        self._task_group: Optional[anyio.abc.TaskGroup] = None

        # Provider ping functions (set externally)
        self._ping_funcs: Dict[str, Callable] = {}

        # Model-to-provider mapping (set externally)
        self._model_provider_map: Dict[str, str] = {}

    # ── TriageRouter Interface ─────────────────────────────────────────

    def is_available(self, model_name: str) -> bool:
        """Check if a model's provider circuit is not open."""
        provider = self._model_provider_map.get(model_name)
        if provider and provider in self._breakers:
            return self._breakers[provider].is_available
        # If no provider mapping, assume available
        return True

    def get_latency_p99(self, model_name: str) -> int:
        """Get p99 latency for a model. Returns 1000ms if no data."""
        window = self._latency_windows.get(model_name)
        if not window or len(window) < 3:
            return 1000
        sorted_vals = sorted(window)
        idx = int(len(sorted_vals) * 0.99)
        return int(sorted_vals[min(idx, len(sorted_vals) - 1)])

    def get_latency_p50(self, model_name: str) -> int:
        """Get median latency for a model."""
        window = self._latency_windows.get(model_name)
        if not window or len(window) < 3:
            return 1000
        sorted_vals = sorted(window)
        return int(sorted_vals[len(sorted_vals) // 2])

    def get_latency_snapshot(self, model_name: str) -> LatencySnapshot:
        """Get full latency statistics for a model."""
        window = self._latency_windows.get(model_name)
        if not window:
            return LatencySnapshot()
        sorted_vals = sorted(window)
        n = len(sorted_vals)
        return LatencySnapshot(
            p50_ms=sorted_vals[n // 2],
            p95_ms=sorted_vals[int(n * 0.95)],
            p99_ms=sorted_vals[min(int(n * 0.99), n - 1)],
            count=n,
            min_ms=sorted_vals[0],
            max_ms=sorted_vals[-1],
        )

    def get_quota_usage(self, provider: str) -> float:
        """Get quota usage as 0.0-1.0. Returns 0.0 if no limit set."""
        quota = self._quotas.get(provider)
        if not quota or quota.daily_limit == 0:
            return 0.0
        return min(quota.used_today / quota.daily_limit, 1.0)

    def get_success_rate(self, model_name: str) -> float:
        """Get success rate as 0.0-1.0. Returns 1.0 if no data."""
        successes = self._success_counts.get(model_name, 0)
        failures = self._failure_counts.get(model_name, 0)
        total = successes + failures
        if total == 0:
            return 1.0
        return successes / total

    def get_provider_status(self, provider: str) -> ProviderStatus:
        """Get current status of a provider."""
        breaker = self._breakers.get(provider)
        if not breaker:
            return ProviderStatus.OFFLINE
        if breaker.state == CircuitState.OPEN:
            return ProviderStatus.OFFLINE
        if breaker.state == CircuitState.HALF_OPEN:
            return ProviderStatus.DEGRADED
        if self.get_quota_usage(provider) >= 1.0:
            return ProviderStatus.DEGRADED
        return ProviderStatus.HEALTHY

    # ── Recording Methods ──────────────────────────────────────────────

    def record_latency(self, model_name: str, latency_ms: float):
        """Record a latency observation for a model."""
        if model_name not in self._latency_windows:
            self._latency_windows[model_name] = deque(
                maxlen=self._latency_window_size
            )
        self._latency_windows[model_name].append(latency_ms)

    def record_success(self, model_name: str):
        """Record a successful request."""
        self._success_counts[model_name] = (
            self._success_counts.get(model_name, 0) + 1
        )

    def record_failure(self, model_name: str):
        """Record a failed request."""
        self._failure_counts[model_name] = (
            self._failure_counts.get(model_name, 0) + 1
        )

    def record_token_usage(self, provider: str, tokens: int):
        """Track token usage against daily quota."""
        if provider not in self._quotas:
            self._quotas[provider] = QuotaStatus()
        self._quotas[provider].used_today += tokens

    def set_model_provider(self, model_name: str, provider_name: str):
        """Map a model to its provider."""
        self._model_provider_map[model_name] = provider_name

    # ── Background Probe Loop ──────────────────────────────────────────

    async def start(self, ping_funcs: Optional[Dict[str, Callable]] = None):
        """Start the background health monitoring loop."""
        if ping_funcs:
            self._ping_funcs = ping_funcs
        self._running = True
        # Note: Task group is managed by the caller's lifecycle

    async def stop(self):
        """Stop the background health monitoring loop."""
        self._running = False

    async def probe_once(self, provider_name: str, ping_func: Callable):
        """Run a single health probe for a provider."""
        try:
            start = time.monotonic()
            if inspect.iscoroutinefunction(ping_func):
                await ping_func()
            else:
                ping_func()
            latency_ms = (time.monotonic() - start) * 1000

            async with self._lock:
                self._status[provider_name] = ProviderStatus.HEALTHY
                if provider_name in self._breakers:
                    self._breakers[provider_name].failure_count = 0

            logger.debug(
                "Provider %s healthy: %.0fms", provider_name, latency_ms
            )
            return True

        except Exception as e:
            logger.warning("Provider %s probe failed: %s", provider_name, e)
            async with self._lock:
                self._status[provider_name] = ProviderStatus.OFFLINE
                if provider_name in self._breakers:
                    await self._breakers[provider_name]._on_failure()
            return False

    # ── Status Report ──────────────────────────────────────────────────

    def get_status_report(self) -> Dict[str, Any]:
        """Get a full status report for all providers and models."""
        report: Dict[str, Any] = {
            "providers": {},
            "models": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for name, breaker in self._breakers.items():
            report["providers"][name] = {
                "status": self.get_provider_status(name).value,
                "circuit_state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "quota_usage": self.get_quota_usage(name),
            }

        for model_name in set(
            list(self._latency_windows.keys())
            + list(self._success_counts.keys())
        ):
            snap = self.get_latency_snapshot(model_name)
            report["models"][model_name] = {
                "latency_p50_ms": snap.p50_ms,
                "latency_p99_ms": snap.p99_ms,
                "success_rate": self.get_success_rate(model_name),
                "samples": snap.count,
            }

        return report
