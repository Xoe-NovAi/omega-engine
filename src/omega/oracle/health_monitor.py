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


# DocRef: docs/architecture/PROVIDER_FABRIC_DEEP_DIVE.md
from __future__ import annotations

import anyio
from omega.errors import OmegaError
import inspect
import re
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
    CLOSED = "closed"  # Normal operation (HEALTHY)
    DEGRADED = "degraded"  # High latency or minor error spikes
    OPEN = "open"  # Failing fast, no requests (CRITICAL)
    HALF_OPEN = "half_open"  # Probe allowed (PROBATION)
    UNKNOWN = "unknown"  # Initial state / Cold start


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


# Quota tracking for C-10.5
@dataclass
class QuotaStatus:
    """Tracks quota usage for a provider."""

    requests_remaining: int = 0
    tokens_remaining: int = 0
    requests_limit: int = 0
    tokens_limit: int = 0
    requests_reset: float = 0.0  # Unix timestamp
    tokens_reset: float = 0.0  # Unix timestamp
    exhausted: bool = False

    @property
    def requests_reset_in(self) -> float:
        """Seconds until request quota resets."""
        return max(0, self.requests_reset - time.time())

    @property
    def tokens_reset_in(self) -> float:
        """Seconds until token quota resets."""
        return max(0, self.tokens_reset - time.time())


# ── Data Classes ───────────────────────────────────────────────────────


@dataclass
class LatencySnapshot:
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    count: int = 0
    min_ms: float = float("inf")
    max_ms: float = 0.0


# ── Circuit Breaker (Canonical implementation — C-6') ──────────────────
#
# [C-6'] This is the SINGLE canonical circuit breaker implementation.
# All other breaker implementations in the codebase are DEPRECATED:
#   - search_circuit_breaker.py          → use HealthMonitor.get_breaker()
#   - IngestionCircuitBreaker            → use HealthMonitor.get_breaker()
#   - ExperimentCircuitBreaker           → use HealthMonitor.get_breaker()
#   - JemCircuitBreaker                  → use HealthMonitor.get_breaker()
#   - SearchCircuitBreaker (search_fleet)→ use HealthMonitor.get_breaker()
#
# The AsyncCircuitBreaker uses CUSUM + EMA anomaly detection (rate-based,
# not naive consecutive-counter) and supports a sliding-window mode for
# responsive failure-rate tracking.
#


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open and requests are blocked."""

    pass


class AsyncCircuitBreaker:
    """Lightweight circuit breaker — AnyIO compliant, zero external deps.

    [C-6'] Canonical breaker. All clones must migrate here.

    Two failure detection modes:
    - 'cusum': CUSUM drift detection (default) — detects sustained
      changes in failure rate. Better for detecting gradual degradation.
    - 'sliding_window': Rate-based sliding window — counts failures
      within a time window. Better for burst detection.

    Key features:
    - 5-state FSM: CLOSED → DEGRADED → OPEN → HALF_OPEN → CLOSED
    - CUSUM anomaly detection for gradual degradation
    - Sliding-window rate detection for burst failures
    - EMA latency smoothing
    - Half-open probe pattern
    - AnyIO-native async lock
    - Observability integration (breaker transitions logged)
    - ZONEID pattern for state integrity
    - [HARDENING-2026-07-22] 429 classification: separates rate-limit
      (transient, seconds) from quota-exhausted (period-based, hours/days)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_requests: int = 1,
        mode: str = "cusum",
        # Sliding window mode params
        window_seconds: float = 60.0,
        max_failures_per_window: int = 10,
    ):
        self.name = name
        # [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity
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

        # Sliding window mode (C-6')
        self.mode = mode
        self.window_seconds = window_seconds
        self.max_failures_per_window = max_failures_per_window
        self._window_failures: list = []  # [(timestamp, ...), ...]

        # 429 Classification (hardening P0 — from sprint research 2026-07-22)
        # Prevents the bug class: circuit breakers conflating rate-limit 429s
        # with quota-exhausted 429s (resilient-llm-router pattern)
        self.rate_limit_until: Optional[float] = None  # timestamp when rate limit expires
        self.quota_until: Optional[float] = None  # timestamp when quota resets
        self.quota_keywords = re.compile(
            r"monthly.quota|daily.limit|out.of.credits|quota.exceeded|"
            r"insufficient.credit|billing|payment|plan.limit",
            re.IGNORECASE,
        )

    async def call(self, func, *args, trace_id: Optional[str] = None, **kwargs):
        """Execute function through circuit breaker."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_transition_to_half_open():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                else:
                    raise CircuitOpenError(
                        f"Circuit '{self.name}' is OPEN. Retry in {self._recovery_remaining():.0f}s"
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.half_open_max_requests:
                    raise CircuitOpenError(
                        f"Circuit '{self.name}' is HALF_OPEN (probe limit reached)"
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
            # [A6] Catch broadly, then let _is_circuit_breaking_error() filter.
            # Previously only (OmegaError, RuntimeError, OSError) were caught, so
            # e.g. httpx/network exceptions escaped without tripping the breaker.
            if self._is_circuit_breaking_error(e):
                await self._on_failure(trace_id=trace_id)
            raise

    async def _on_success(
        self, latency: float, quality: float = 1.0, trace_id: Optional[str] = None
    ):
        # [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity
        validate_zoneid(self.magic, ZONEID_BREAKER, f"AsyncCircuitBreaker._on_success({self.name})")
        async with self._lock:
            old_state = self.state

            # 1. Update EMA Latency (SOTA: EWMA for smooth health tracking)
            if self.ema_latency == 0:
                self.ema_latency = latency
            else:
                self.ema_latency = (self.alpha_lat * latency) + (
                    (1 - self.alpha_lat) * self.ema_latency
                )

            # 2. Update EMA Quality
            self.ema_quality = (self.alpha_qual * quality) + (
                (1 - self.alpha_qual) * self.ema_quality
            )

            # 3. Update detection metric based on mode
            if self.mode == "sliding_window":
                # [C-6'] Sliding window: on success, just decay the window count
                # Keep the window failures but let them age out naturally
                now = time.monotonic()
                cutoff = now - self.window_seconds
                self._window_failures = [t for t in self._window_failures if t > cutoff]
                recent_failures = len(self._window_failures)

                if recent_failures < self.max_failures_per_window // 4:
                    self.state = CircuitState.CLOSED
                elif recent_failures < self.max_failures_per_window // 2:
                    self.state = CircuitState.DEGRADED

                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
            else:
                # 3. Update CUSUM (success = 0 error)
                # Z_t = max(0, g_{t-1} + (y_t - mu_0) / sigma_0)
                # For success, y_t = 0. mu_0 is the baseline failure rate.
                self.cusum_g = max(0.0, self.cusum_g - 0.5)

                # 4. State Transition (SOTA: 5-State FSM)
                # Optimal (CLOSED) -> Stressed (DEGRADED) -> Critical (OPEN)
                if self.cusum_g < 1.0 and self.ema_latency < 1500:
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
                    await engine.log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {
                            "provider": self.name,
                            "event": "circuit_closed",
                            "from": old_state.value,
                            "to": self.state.value,
                        },
                    )
                    await engine.record_breaker_transition(
                        provider=self.name,
                        from_state=old_state.value,
                        to_state=self.state.value,
                        trace_id=trace_id,
                        reason="success_recovery",
                    )
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning(f"Circuit closed event failed — observability unavailable: {e}")
                    pass

    async def _on_failure(self, trace_id: Optional[str] = None):
        # [id-soft: vet-015] ZONEID Pattern — magic constant for circuit breaker state integrity
        validate_zoneid(self.magic, ZONEID_BREAKER, f"AsyncCircuitBreaker._on_failure({self.name})")
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            old_state = self.state

            if self.mode == "sliding_window":
                # [C-6'] Rate-based sliding-window failure detection
                # Count failures within a time window — trip if rate exceeds threshold.
                now = time.monotonic()
                self._window_failures.append(now)
                # Prune failures outside window
                cutoff = now - self.window_seconds
                self._window_failures = [t for t in self._window_failures if t > cutoff]
                recent_failures = len(self._window_failures)

                if recent_failures >= self.max_failures_per_window:
                    self.state = CircuitState.OPEN
                elif self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                elif recent_failures >= self.max_failures_per_window // 2:
                    self.state = CircuitState.DEGRADED
                else:
                    self.state = CircuitState.CLOSED
            else:
                # Default: CUSUM drift detection
                # 1. Update CUSUM (failure = 1 error)
                # Z_t = max(0, g_{t-1} + (y_t - mu_0) / sigma_0)
                # For failure, y_t = 1. mu_0 is baseline failure rate.
                self.cusum_g = max(0.0, self.cusum_g + 1.0 - self.cusum_drift)

                # 2. State Transition (SOTA: 5-State FSM)
                # Optimal (CLOSED) -> Stressed (DEGRADED) -> Critical (OPEN)
                if self.cusum_g > self.cusum_threshold:
                    self.state = CircuitState.OPEN
                elif self.state == CircuitState.HALF_OPEN:
                    # Any failure in HALF_OPEN immediately trips the circuit back to OPEN
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
                    await engine.log_event(
                        EventType.BACKEND_FALLBACK,
                        trace_id,
                        {
                            "provider": self.name,
                            "event": "circuit_opened",
                            "from": old_state.value,
                            "to": self.state.value,
                            "failure_count": self.failure_count,
                            "cusum": self.cusum_g,
                        },
                    )
                    # Also record to MetricsDB
                    await engine.record_breaker_transition(
                        provider=self.name,
                        from_state=old_state.value,
                        to_state=self.state.value,
                        trace_id=trace_id,
                        reason=f"failures={self.failure_count},cusum={self.cusum_g:.2f}",
                    )
                except (OmegaError, RuntimeError, OSError) as e:
                    logger.warning(f"Circuit opened event failed — observability unavailable: {e}")
                    pass

    def record_429(
        self,
        retry_after: Optional[float] = None,
        response_body: str = "",
        is_quota: Optional[bool] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Classify a 429 response as rate-limit or quota-exhausted.

        [HARDENING-2026-07-22] Prevents the bug class where circuit breakers
        conflate transient rate limits with quota exhaustion (resilient-llm-router
        pattern). Rate limits use Retry-After (seconds); quotas use period-based
        cooldown (hours/days).

        Args:
            retry_after: Retry-After header value in seconds, if present.
            response_body: Response body text for quota keyword detection.
            is_quota: Explicit classification override. If None, auto-detect.
            trace_id: Optional trace ID for observability.
        """
        now = time.monotonic()

        if is_quota is None:
            # Auto-detect: check body for quota keywords, then headers
            has_quota_keywords = bool(self.quota_keywords.search(response_body))
            has_rate_limit_headers = retry_after is not None and retry_after < 3600
            # If retry_after is > 1 hour, treat as quota (not a per-minute rate limit)
            is_long_cooldown = retry_after is not None and retry_after >= 3600

            is_quota = has_quota_keywords or is_long_cooldown

        if is_quota:
            # Quota exhausted — cooldown until period rolls over
            cooldown = retry_after or 86400.0  # default 24h if no Retry-After
            self.quota_until = now + cooldown
            logger.info(
                f"[{self.name}] 429 QUOTA — cooldown {cooldown:.0f}s "
                f"(until {datetime.now(timezone.utc).isoformat()})"
            )
        else:
            # Rate limit — short cooldown
            cooldown = retry_after or 60.0  # default 60s if no Retry-After
            self.rate_limit_until = now + cooldown
            logger.info(
                f"[{self.name}] 429 RATE-LIMIT — cooldown {cooldown:.0f}s "
                f"(until {datetime.now(timezone.utc).isoformat()})"
            )

        if trace_id:
            try:
                from omega.observability import get_engine, EventType

                engine = get_engine()
                engine.log_event_sync(
                    EventType.BACKEND_FALLBACK,
                    trace_id,
                    {
                        "provider": self.name,
                        "event": "429_classified",
                        "classification": "quota" if is_quota else "rate_limit",
                        "cooldown_seconds": cooldown,
                    },
                )
            except (OmegaError, RuntimeError, OSError):
                pass

    def is_429_blocked(self) -> bool:
        """Check if this breaker is blocked by a 429 (rate-limit or quota).

        [HARDENING-2026-07-22] Check BEFORE calling provider. The guard()
        method handles circuit state; this handles 429 cooldowns.

        Returns:
            True if blocked by rate-limit or quota, False otherwise.
        """
        now = time.monotonic()

        if self.quota_until and now < self.quota_until:
            remaining = self.quota_until - now
            logger.debug(f"[{self.name}] BLOCKED by quota — {remaining:.0f}s remaining")
            return True

        if self.rate_limit_until and now < self.rate_limit_until:
            remaining = self.rate_limit_until - now
            logger.debug(f"[{self.name}] BLOCKED by rate-limit — {remaining:.0f}s remaining")
            return True

        return False

    def can_proceed(self) -> bool:
        """Check if a request may proceed through this breaker (non-raising).

        Mirrors the admission logic in ``call()`` but returns a boolean
        instead of raising ``CircuitOpenError``. Used by callers that want
        to skip work gracefully (e.g., ingestion pre-flight checks) rather
        than catch an exception.

        Returns:
            True if the breaker is CLOSED/DEGRADED, OPEN-but-ready-for-HALF_OPEN
            probe, or HALF_OPEN within its probe budget. False if the breaker
            is OPEN and not yet eligible for a probe.
        """
        if self.state in (CircuitState.CLOSED, CircuitState.DEGRADED):
            return True
        if self.state == CircuitState.OPEN:
            return self._should_transition_to_half_open()
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_requests < self.half_open_max_requests
        return False

    def get_429_status(self) -> Dict[str, Any]:
        """Get current 429 classification status for observability.

        Returns:
            Dict with rate_limit_until, quota_until, and remaining times.
        """
        now = time.monotonic()
        return {
            "rate_limit_until": self.rate_limit_until,
            "quota_until": self.quota_until,
            "rate_limit_remaining": max(0, (self.rate_limit_until or 0) - now),
            "quota_remaining": max(0, (self.quota_until or 0) - now),
            "is_blocked": self.is_429_blocked(),
        }

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
            "connection",
            "timeout",
            "500",
            "502",
            "503",
            "504",
            "unavailable",
            "refused",
            "rate limit",
            "too many requests",
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

        # Search provider specific tracking (SSP-V2)
        self._search_providers: Dict[str, Dict[str, Any]] = {}
        self._search_ping_funcs: Dict[str, Callable] = {}

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
        if not quota or quota.tokens_limit == 0:
            return 0.0
        # tokens_remaining counts DOWN from tokens_limit, so usage =
        # (limit - remaining) / limit.
        used = quota.tokens_limit - quota.tokens_remaining
        return min(max(used / quota.tokens_limit, 0.0), 1.0)

    def has_quota(self, provider_name: str) -> bool:
        """
        Check if provider has remaining quota for today.

        Returns True if either requests or tokens have remaining quota.
        """
        quota = self._quotas.get(provider_name)
        if not quota:
            # No quota tracking = assume available
            return True

        # Check if either resource has remaining quota
        return (quota.requests_remaining > 0 or quota.requests_limit == 0) and (
            quota.tokens_remaining > 0 or quota.tokens_limit == 0
        )

    def record_quota_usage(self, provider_name: str, tokens_used: int, requests_used: int = 1):
        """
        Record quota consumption from response headers.

        Updates the quota tracking based on response headers from providers.
        """
        if provider_name not in self._quotas:
            self._quotas[provider_name] = QuotaStatus()

        quota = self._quotas[provider_name]

        # Decrement remaining tokens (assumes tokens_limit was set by a prior
        # record that knows the provider's cap). If limit is unknown (0),
        # we only track cumulative usage via tokens_remaining going negative —
        # has_quota() treats limit==0 as "unlimited", so this is safe.
        quota.tokens_remaining -= tokens_used
        quota.requests_remaining -= requests_used
        if quota.tokens_remaining <= 0 or quota.requests_remaining <= 0:
            quota.exhausted = True

    def get_success_rate(self, model_name: str) -> float:
        """Get success rate as 0.0-1.0. Returns 1.0 if no data."""
        successes = self._success_counts.get(model_name, 0)
        failures = self._failure_counts.get(model_name, 0)
        total = successes + failures
        if total == 0:
            return 1.0
        return successes / total

    def get_provider_status(self, provider: str) -> ProviderStatus:
        """Get current status of a provider (LLM or Search)."""
        # Check LLM providers
        breaker = self._breakers.get(provider)
        if breaker:
            if breaker.state == CircuitState.OPEN:
                return ProviderStatus.OFFLINE
            if breaker.state == CircuitState.HALF_OPEN:
                return ProviderStatus.DEGRADED
            if self.get_quota_usage(provider) >= 1.0:
                return ProviderStatus.DEGRADED
            return ProviderStatus.HEALTHY

        # Check search providers
        if provider in self._search_providers:
            search_info = self._search_providers[provider]
            return search_info.get("status", ProviderStatus.OFFLINE)

        return ProviderStatus.OFFLINE

    # ── Circuit Breaker Factory (C-6') ──────────────────────────────────

    def get_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        mode: str = "cusum",
        window_seconds: float = 60.0,
        max_failures_per_window: int = 10,
    ) -> AsyncCircuitBreaker:
        """Get or create a circuit breaker for a named provider.

        [C-6'] This is the SINGLE factory for all circuit breakers in the engine.
        All callers MUST use this instead of instantiating their own breaker.

        Args:
            name: Provider/service name (e.g., 'google', 'searxng_t1', 'exa_t2')
            failure_threshold: Consecutive failures before opening (CUSUM mode)
            recovery_timeout: Seconds before transitioning to HALF_OPEN
            mode: 'cusum' (default) or 'sliding_window'
            window_seconds: Time window in seconds (sliding_window mode)
            max_failures_per_window: Max failures in window before tripping

        Returns:
            AsyncCircuitBreaker instance (shared singleton per name)
        """
        if name not in self._breakers:
            self._breakers[name] = AsyncCircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                mode=mode,
                window_seconds=window_seconds,
                max_failures_per_window=max_failures_per_window,
            )
        return self._breakers[name]

    async def record_breaker_success(self, name: str, trace_id: Optional[str] = None):
        """Record a success on a named breaker.

        [A4] Implements the previously no-op stub. Fire-and-forget: dispatches
        ``_on_success`` on the breaker's event loop with latency=0 and quality=1.0
        (the caller has no timing info — use ``breaker.call()`` when latency
        matters). Mirrors ``record_breaker_failure``.
        [M1 AnyIO] Async — safe to await directly from async context.
        """
        if name in self._breakers:
            breaker = self._breakers[name]
            try:
                await breaker._on_success(latency=0.0, quality=1.0, trace_id=trace_id)
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"record_breaker_success failed for {name}: {e}")

    async def record_breaker_failure(self, name: str, trace_id: Optional[str] = None):
        """Record a failure on a named breaker.
        [M1 AnyIO] Async — safe to await directly from async context.
        """
        if name in self._breakers:
            breaker = self._breakers[name]
            try:
                await breaker._on_failure(trace_id)
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"record_breaker_failure failed for {name}: {e}")

    # ── Search Provider Interface (SSP-V2) ──────────────────────────────

    def register_search_provider(
        self,
        name: str,
        ping_func: Callable,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
    ) -> None:
        """Register a search provider for health monitoring."""
        self._search_ping_funcs[name] = ping_func
        self._search_providers[name] = {
            "status": ProviderStatus.HEALTHY,
            "failure_count": 0,
            "last_check": 0.0,
            "failure_threshold": failure_threshold,
            "recovery_timeout": recovery_timeout,
        }
        # Also create a circuit breaker for it
        if name not in self._breakers:
            self._breakers[name] = AsyncCircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        self._status[name] = ProviderStatus.HEALTHY
        logger.info(f"Registered search provider for health monitoring: {name}")

    def get_search_provider_status(self, name: str) -> ProviderStatus:
        """Get health status of a search provider."""
        return self.get_provider_status(name)

    # ── Recording Methods ──────────────────────────────────────────────

    def record_latency(self, model_name: str, latency_ms: float):
        """Record a latency observation for a model."""
        if model_name not in self._latency_windows:
            self._latency_windows[model_name] = deque(maxlen=self._latency_window_size)
        self._latency_windows[model_name].append(latency_ms)

    def record_success(self, model_name: str):
        """Record a successful request."""
        self._success_counts[model_name] = self._success_counts.get(model_name, 0) + 1

    def record_failure(self, model_name: str):
        """Record a failed request."""
        self._failure_counts[model_name] = self._failure_counts.get(model_name, 0) + 1

    def record_token_usage(self, provider: str, tokens: int):
        """Track token usage against quota."""
        if provider not in self._quotas:
            self._quotas[provider] = QuotaStatus()
        quota = self._quotas[provider]
        quota.tokens_remaining -= tokens
        if quota.tokens_remaining <= 0:
            quota.exhausted = True

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

            logger.debug("Provider %s healthy: %.0fms", provider_name, latency_ms)
            return True

        except Exception as e:
            logger.warning("Provider %s probe failed: %s", provider_name, e)
            async with self._lock:
                self._status[provider_name] = ProviderStatus.OFFLINE
                if provider_name in self._breakers:
                    await self._breakers[provider_name]._on_failure()
            return False

    async def probe_search_providers(self) -> Dict[str, bool]:
        """Probe all registered search providers."""
        results = {}
        for name, ping_func in self._search_ping_funcs.items():
            try:
                start = time.monotonic()
                if inspect.iscoroutinefunction(ping_func):
                    await ping_func()
                else:
                    ping_func()
                latency_ms = (time.monotonic() - start) * 1000

                async with self._lock:
                    self._search_providers[name]["status"] = ProviderStatus.HEALTHY
                    self._search_providers[name]["failure_count"] = 0
                    self._search_providers[name]["last_check"] = time.time()
                    if name in self._breakers:
                        self._breakers[name].failure_count = 0
                    self._status[name] = ProviderStatus.HEALTHY

                logger.debug("Search provider %s healthy: %.0fms", name, latency_ms)
                results[name] = True

            except Exception as e:
                logger.warning("Search provider %s probe failed: %s", name, e)
                async with self._lock:
                    self._search_providers[name]["status"] = ProviderStatus.OFFLINE
                    self._search_providers[name]["failure_count"] += 1
                    self._search_providers[name]["last_check"] = time.time()
                    if name in self._breakers:
                        await self._breakers[name]._on_failure()
                    self._status[name] = ProviderStatus.OFFLINE
                results[name] = False
        return results

    # ── Status Report ──────────────────────────────────────────────────

    def get_status_report(self) -> Dict[str, Any]:
        """Get a full status report for all providers and models."""
        report: Dict[str, Any] = {
            "providers": {},
            "models": {},
            "search_providers": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for name, breaker in self._breakers.items():
            report["providers"][name] = {
                "status": self.get_provider_status(name).value,
                "circuit_state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "quota_usage": self.get_quota_usage(name),
            }

        for name, info in self._search_providers.items():
            report["search_providers"][name] = {
                "status": info.get("status", ProviderStatus.OFFLINE).value,
                "failure_count": info.get("failure_count", 0),
                "last_check": info.get("last_check", 0),
                "circuit_state": self._breakers.get(name, {}).state.value
                if name in self._breakers
                else "none",
            }

        for model_name in set(
            list(self._latency_windows.keys()) + list(self._success_counts.keys())
        ):
            snap = self.get_latency_snapshot(model_name)
            report["models"][model_name] = {
                "latency_p50_ms": snap.p50_ms,
                "latency_p99_ms": snap.p99_ms,
                "success_rate": self.get_success_rate(model_name),
                "samples": snap.count,
            }

        return report
