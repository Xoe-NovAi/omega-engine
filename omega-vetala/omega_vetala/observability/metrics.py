# 🔱 omega-vetala — Metrics Collection
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ METRICS
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake-1996] cvar — counters as observable engine state
#
"""Thread-safe metrics collection for the moderation system.

All metrics are aggregate-only — no raw text, no user IDs, no PII.
Metrics are stored in an in-memory rolling window (last 10 000 events)
and periodically exported to disk as JSON snapshots.

Metric types:
    Counter:   Monotonically increasing count (requests, errors).
    Gauge:     Point-in-time value (request rate, flag percentage).
    Histogram: Distribution of values (latency per provider).
"""

from __future__ import annotations

import json
import math
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Rolling-window event store
# ---------------------------------------------------------------------------

_MAX_EVENTS = 10_000


@dataclass
class MetricEvent:
    """A single event in the rolling window."""

    timestamp: float
    kind: str  # "request" | "flag" | "appeal" | "error" | "latency"
    provider_name: str = ""
    value: float = 0.0
    action_type: str = ""


# ---------------------------------------------------------------------------
# Latency histogram helpers
# ---------------------------------------------------------------------------

_LATENCY_BUCKETS = [5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000, 5000, 10000]


def _bucket_index(ms: float) -> int:
    """Return the bucket index for a latency value.

    Args:
        ms: Latency in milliseconds.

    Returns:
        Index into ``_LATENCY_BUCKETS``.  Values larger than the last
        bucket go into an overflow bucket at the end.
    """
    for i, bound in enumerate(_LATENCY_BUCKETS):
        if ms <= bound:
            return i
    return len(_LATENCY_BUCKETS)


# ---------------------------------------------------------------------------
# Metrics reporter
# ---------------------------------------------------------------------------

class MetricsReporter:
    """Thread-safe metrics collection for moderation operations.

    All public methods are safe to call from multiple threads.
    Internally uses a ``threading.Lock`` for all mutations.

    Usage::

        metrics = MetricsReporter()
        metrics.record_request(provider_name="perspective")
        metrics.record_flag(provider_name="perspective")
        metrics.record_latency(provider_name="perspective", latency_ms=142.0)
        metrics.record_error(provider_name="perspective")

        snapshot = metrics.snapshot()
        metrics.export_to_disk("/tmp/metrics_snapshot.json")

    Args:
        export_path: Optional path for periodic disk exports.
            If provided, a background thread should call
            :meth:`export_to_disk` periodically.
    """

    def __init__(self, export_path: str = "") -> None:
        self._lock = threading.Lock()
        self._export_path = export_path

        # -- Counters
        self._requests_total: dict[str, int] = defaultdict(int)  # provider → count
        self._flags_total: dict[str, int] = defaultdict(int)     # provider → count
        self._appeals_total: dict[str, int] = defaultdict(int)   # provider → count
        self._errors_total: dict[str, int] = defaultdict(int)    # provider → count
        self._action_distribution: dict[str, int] = defaultdict(int)  # action → count

        # -- Latency histograms: provider → list of bucket counts
        self._latency_histograms: dict[str, list[int]] = defaultdict(
            lambda: [0] * (len(_LATENCY_BUCKETS) + 1)
        )

        # -- Rolling window
        self._events: list[MetricEvent] = []

        # -- Rate tracking
        self._request_timestamps: list[float] = []
        self._flag_timestamps: list[float] = []
        self._appeal_timestamps: list[float] = []

    # ------------------------------------------------------------------
    # Recording methods
    # ------------------------------------------------------------------

    def record_request(
        self,
        provider_name: str = "",
        *,
        action_type: str = "",
    ) -> None:
        """Record that a moderation request was processed.

        Args:
            provider_name: Which provider handled the request.
            action_type: The action taken (allow, block, warn, review).
        """
        now = time.time()
        with self._lock:
            self._requests_total[provider_name] += 1
            self._request_timestamps.append(now)
            if action_type:
                self._action_distribution[action_type] += 1
            self._events.append(MetricEvent(
                timestamp=now,
                kind="request",
                provider_name=provider_name,
                action_type=action_type,
            ))
            self._trim_events()

    def record_flag(
        self,
        provider_name: str = "",
    ) -> None:
        """Record that content was flagged.

        Args:
            provider_name: The provider that detected the violation.
        """
        now = time.time()
        with self._lock:
            self._flags_total[provider_name] += 1
            self._flag_timestamps.append(now)
            self._events.append(MetricEvent(
                timestamp=now,
                kind="flag",
                provider_name=provider_name,
                value=1.0,
            ))
            self._trim_events()

    def record_appeal(
        self,
        provider_name: str = "",
    ) -> None:
        """Record that a moderation decision was appealed.

        Args:
            provider_name: The provider whose decision was appealed.
        """
        now = time.time()
        with self._lock:
            self._appeals_total[provider_name] += 1
            self._appeal_timestamps.append(now)
            self._events.append(MetricEvent(
                timestamp=now,
                kind="appeal",
                provider_name=provider_name,
                value=1.0,
            ))
            self._trim_events()

    def record_latency(
        self,
        provider_name: str = "",
        *,
        latency_ms: float = 0.0,
    ) -> None:
        """Record a provider latency observation.

        Args:
            provider_name: The provider that produced this latency.
            latency_ms: Wall-clock time in milliseconds.
        """
        with self._lock:
            idx = _bucket_index(latency_ms)
            self._latency_histograms[provider_name][idx] += 1
            self._events.append(MetricEvent(
                timestamp=time.time(),
                kind="latency",
                provider_name=provider_name,
                value=latency_ms,
            ))
            self._trim_events()

    def record_error(
        self,
        provider_name: str = "",
    ) -> None:
        """Record a provider error.

        Args:
            provider_name: The provider that failed.
        """
        now = time.time()
        with self._lock:
            self._errors_total[provider_name] += 1
            self._events.append(MetricEvent(
                timestamp=now,
                kind="error",
                provider_name=provider_name,
                value=1.0,
            ))
            self._trim_events()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def requests_total(self) -> int:
        """Total number of moderation requests across all providers."""
        with self._lock:
            return sum(self._requests_total.values())

    def requests_per_minute(self, window_seconds: int = 60) -> float:
        """Requests per minute over the last *window_seconds*.

        Args:
            window_seconds: Lookback window.

        Returns:
            Requests per minute as a float.
        """
        now = time.time()
        with self._lock:
            cutoff = now - window_seconds
            count = sum(1 for t in self._request_timestamps if t >= cutoff)
        return count / (window_seconds / 60.0)

    def flag_rate(self, window_seconds: int = 300) -> float:
        """Percentage of requests that resulted in a flag.

        .. math::

            flag_rate = \\frac{flags}{requests} \\times 100

        Args:
            window_seconds: Lookback window (default 5 minutes).

        Returns:
            Percentage (0.0–100.0).
        """
        now = time.time()
        with self._lock:
            cutoff = now - window_seconds
            req_count = sum(1 for t in self._request_timestamps if t >= cutoff)
            flag_count = sum(1 for t in self._flag_timestamps if t >= cutoff)
        if req_count == 0:
            return 0.0
        return (flag_count / req_count) * 100.0

    def appeal_rate(self, window_seconds: int = 300) -> float:
        """Percentage of flags that were appealed.

        .. math::

            appeal_rate = \\frac{appeals}{flags} \\times 100

        Args:
            window_seconds: Lookback window.

        Returns:
            Percentage (0.0–100.0).
        """
        now = time.time()
        with self._lock:
            cutoff = now - window_seconds
            flag_count = sum(1 for t in self._flag_timestamps if t >= cutoff)
            appeal_count = sum(1 for t in self._appeal_timestamps if t >= cutoff)
        if flag_count == 0:
            return 0.0
        return (appeal_count / flag_count) * 100.0

    def provider_latency_percentiles(
        self,
        provider_name: str,
    ) -> dict[str, float]:
        """Estimate latency percentiles for *provider_name* from histogram data.

        Uses linear interpolation within each bucket.  Returns P50, P95, P99.

        Args:
            provider_name: The provider to query.

        Returns:
            Dict with keys ``p50``, ``p95``, ``p99`` and values in milliseconds.
        """
        with self._lock:
            buckets = list(self._latency_histograms.get(provider_name, []))
        total = sum(buckets)
        if total == 0:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        return {
            "p50": self._percentile_from_buckets(buckets, total, 50),
            "p95": self._percentile_from_buckets(buckets, total, 95),
            "p99": self._percentile_from_buckets(buckets, total, 99),
        }

    @staticmethod
    def _percentile_from_buckets(
        buckets: list[int],
        total: int,
        percentile: int,
    ) -> float:
        """Estimate a percentile from histogram buckets.

        Args:
            buckets: Bucket counts (last bucket is overflow).
            total: Sum of all bucket counts.
            percentile: Desired percentile (0–100).

        Returns:
            Estimated value in milliseconds.
        """
        target = total * percentile / 100.0
        cumulative = 0

        for i, count in enumerate(buckets):
            cumulative += count
            if cumulative >= target:
                if i < len(_LATENCY_BUCKETS):
                    return float(_LATENCY_BUCKETS[i])
                # Overflow bucket — estimate as 1.5× last bound
                return float(_LATENCY_BUCKETS[-1] * 1.5)

        return float(_LATENCY_BUCKETS[-1])

    def action_distribution(self) -> dict[str, int]:
        """Return a copy of the action distribution counters."""
        with self._lock:
            return dict(self._action_distribution)

    def provider_error_count(self, provider_name: str) -> int:
        """Return total errors for a specific provider."""
        with self._lock:
            return self._errors_total.get(provider_name, 0)

    # ------------------------------------------------------------------
    # Snapshot / export
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Capture a point-in-time snapshot of all metrics.

        Returns:
            A JSON-serialisable dict of current metrics.
        """
        with self._lock:
            total_req = sum(self._requests_total.values())
            total_flags = sum(self._flags_total.values())
            total_appeals = sum(self._appeals_total.values())
            total_errors = sum(self._errors_total.values())

        return {
            "requests_total": total_req,
            "flags_total": total_flags,
            "appeals_total": total_appeals,
            "errors_total": total_errors,
            "requests_per_minute": round(self.requests_per_minute(), 2),
            "flag_rate_pct": round(self.flag_rate(), 2),
            "appeal_rate_pct": round(self.appeal_rate(), 2),
            "action_distribution": self.action_distribution(),
            "per_provider": {
                p: {
                    "requests": self._requests_total.get(p, 0),
                    "flags": self._flags_total.get(p, 0),
                    "errors": self._errors_total.get(p, 0),
                    "latency_percentiles": self.provider_latency_percentiles(p),
                }
                for p in list(self._requests_total.keys())
            },
        }

    def export_to_disk(self, path: str = "") -> None:
        """Export the current metrics snapshot to a JSON file.

        Args:
            path: Filesystem path.  Falls back to the path provided at
                construction time.
        """
        dest = path or self._export_path
        if not dest:
            return
        snapshot = self.snapshot()
        Path(dest).write_text(json.dumps(snapshot, indent=2, default=str))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _trim_events(self) -> None:
        """Keep the rolling window within ``_MAX_EVENTS``."""
        while len(self._events) > _MAX_EVENTS:
            self._events.pop(0)
