# 🔱 omega-vetala — Dashboard Query Interface
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ DASHBOARD
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake-1996] cvar — dashboard as observable state viewer
#
"""Query interface for moderation system metrics and alert history.

This is a **data access layer** — it provides structured query methods
that can be consumed by any dashboard UI (CLI, Web, Grafana, etc.).
No rendering or presentation logic is included.

Time-range filters:
    * ``last_5m``  — 300 seconds
    * ``last_1h``  — 3600 seconds
    * ``last_24h`` — 86400 seconds
    * ``last_7d``  — 604800 seconds
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from omega_vetala.observability.alerts import AlertManager
from omega_vetala.observability.metrics import MetricsReporter


# ---------------------------------------------------------------------------
# Time-range presets
# ---------------------------------------------------------------------------

_TIME_RANGES: dict[str, float] = {
    "last_5m": 300.0,
    "last_1h": 3600.0,
    "last_24h": 86400.0,
    "last_7d": 604800.0,
}


def _resolve_window(range_spec: str | float) -> float:
    """Convert a time-range specification to seconds.

    Args:
        range_spec: Either a preset name (``last_5m``, ``last_1h``,
            ``last_24h``, ``last_7d``) or a raw number of seconds.

    Returns:
        Number of seconds for the lookback window.
    """
    if isinstance(range_spec, str):
        return _TIME_RANGES.get(range_spec, 3600.0)
    return float(range_spec)


# ---------------------------------------------------------------------------
# Dashboard query
# ---------------------------------------------------------------------------

class DashboardQuery:
    """Query interface for moderation observability data.

    Usage::

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        dashboard = DashboardQuery(metrics, alert_mgr)

        # Get a full dashboard snapshot
        snapshot = dashboard.full_snapshot()

        # Query top flagged patterns (by hash frequency)
        patterns = dashboard.top_flagged_patterns()

        # Export to JSON for rendering
        import json
        print(json.dumps(snapshot, indent=2))

    Args:
        metrics: The :class:`MetricsReporter` instance.
        alerts: The :class:`AlertManager` instance.
    """

    def __init__(
        self,
        metrics: MetricsReporter,
        alerts: AlertManager,
    ) -> None:
        self._metrics = metrics
        self._alerts = alerts

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    def overview(self) -> dict[str, Any]:
        """High-level system health overview.

        Returns:
            Dict with request counts, flag rate, error counts, and
            current alert status.
        """
        snapshot = self._metrics.snapshot()
        fired_alerts = self._alerts.evaluate()

        return {
            "status": "degraded" if any(
                a["severity"] == "critical" for a in fired_alerts
            ) else "healthy",
            "requests_total": snapshot["requests_total"],
            "requests_per_minute": snapshot["requests_per_minute"],
            "flag_rate_pct": snapshot["flag_rate_pct"],
            "appeal_rate_pct": snapshot["appeal_rate_pct"],
            "errors_total": snapshot["errors_total"],
            "active_alerts": len(fired_alerts),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Provider latency percentiles
    # ------------------------------------------------------------------

    def provider_latency(
        self,
        provider_name: str = "",
        *,
        range_spec: str | float = "last_1h",
    ) -> dict[str, Any]:
        """Latency percentiles for a specific provider.

        Args:
            provider_name: Provider to query.  Empty string returns all.
            range_spec: Time range preset or seconds.

        Returns:
            Dict of provider → percentiles.
        """
        _ = range_spec  # Histograms are cumulative; kept for API consistency

        if provider_name:
            percentiles = self._metrics.provider_latency_percentiles(provider_name)
            return {provider_name: percentiles}

        # Aggregate all providers from the snapshot
        snapshot = self._metrics.snapshot()
        result: dict[str, Any] = {}
        for prov in snapshot.get("per_provider", {}):
            result[prov] = snapshot["per_provider"][prov]["latency_percentiles"]
        return result

    # ------------------------------------------------------------------
    # Action distribution
    # ------------------------------------------------------------------

    def action_distribution(
        self,
        *,
        range_spec: str | float = "last_24h",
    ) -> dict[str, int]:
        """Distribution of moderation actions taken.

        Args:
            range_spec: Time range preset or seconds.

        Returns:
            Dict mapping action type to count (e.g. ``{"block": 42,
            "allow": 150, "warn": 12}``).
        """
        _ = range_spec  # Counters are cumulative
        return self._metrics.action_distribution()

    # ------------------------------------------------------------------
    # Alert history
    # ------------------------------------------------------------------

    def alert_history(
        self,
        *,
        range_spec: str | float = "last_24h",
        severity: str = "",
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Recent alert history.

        Args:
            range_spec: Time range preset or seconds.
            severity: Filter by severity.
            limit: Maximum entries.

        Returns:
            List of alert records.
        """
        window = _resolve_window(range_spec)
        since = time.time() - window
        return self._alerts.alert_history(
            since=since,
            severity=severity,
            limit=limit,
        )

    # ------------------------------------------------------------------
    # Top flagged patterns (by hash frequency)
    # ------------------------------------------------------------------

    def top_flagged_patterns(
        self,
        *,
        range_spec: str | float = "last_24h",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Most frequently flagged content hashes.

        .. note::

            This method requires the ``ModerationObserver`` to have
            recorded hash frequencies via ``record_flag``.  The hashes
            are SHA-256[:16] — they cannot be reversed to recover the
            original text.

        Args:
            range_spec: Time range preset or seconds.
            limit: Maximum number of entries to return.

        Returns:
            List of ``{"content_hash": str, "count": int}`` dicts,
            sorted descending by count.
        """
        _ = range_spec
        _ = limit

        # Note: hash frequency tracking is delegated to the
        # ModerationObserver, which maintains its own hash → count map.
        # This method queries that map via a shared store or direct
        # integration.
        #
        # In the current architecture, the observer pushes flag events
        # to MetricsReporter which does not store content hashes (by
        # design — privacy).  For hash-frequency analysis an external
        # aggregator (e.g., a stream processor) would consume the
        # structured logs.
        #
        # For now, return a placeholder indicating where to find this
        # data.
        return [
            {
                "note": (
                    "Hash-frequency tracking is an external aggregation "
                    "concern.  Structured log files contain hashed content "
                    "and can be consumed by a stream processor (e.g., "
                    "fluentd + Elasticsearch) for this analysis."
                ),
            }
        ]

    # ------------------------------------------------------------------
    # Full snapshot
    # ------------------------------------------------------------------

    def full_snapshot(self) -> dict[str, Any]:
        """Return a comprehensive snapshot of all observability data.

        Returns:
            A JSON-serialisable dict with overview, latency, actions,
            alert rules, and recent alerts.
        """
        return {
            "overview": self.overview(),
            "provider_latency": self.provider_latency(),
            "action_distribution": self.action_distribution(),
            "alert_rules": self._alerts.list_rules(),
            "recent_alerts": self.alert_history(limit=20),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # JSON export
    # ------------------------------------------------------------------

    def export_json(self, path: str) -> None:
        """Export the full snapshot to a JSON file.

        Args:
            path: Filesystem path to write.
        """
        import json
        from pathlib import Path

        snapshot = self.full_snapshot()
        Path(path).write_text(json.dumps(snapshot, indent=2, default=str))
