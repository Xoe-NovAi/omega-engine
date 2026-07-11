# 🔱 omega-vetala — Alert Management
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ ALERTS
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake-1996] cvar — alert thresholds as observable state
#
"""Threshold-based alert rules with rate-limited firing.

Alert rules evaluate current metrics against configured thresholds.
When a threshold is breached, the alert fires (runs callbacks) but
will not re-fire during the cooldown period to prevent alert storms.

Built-in alert rules:
    * CRITICAL: Hate speech / toxicity spike — flag_rate > 3× baseline
    * WARNING:  Provider failure rate > 10%
    * WARNING:  P95 latency > 3000 ms
    * INFO:     Appeal rate > 20% (potential false-positive issue)
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from omega_vetala.observability.metrics import MetricsReporter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Severity levels
# ---------------------------------------------------------------------------

class AlertSeverity(Enum):
    """Severity of an alert rule."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Comparison operators
# ---------------------------------------------------------------------------

class Op(Enum):
    """Comparison operator for threshold evaluation."""

    GT = "gt"   # greater than
    LT = "lt"   # less than
    EQ = "eq"   # equal to


def _evaluate(value: float, threshold: float, op: Op) -> bool:
    """Evaluate *value* against *threshold* using *op*.

    Args:
        value: The current metric value.
        threshold: The configured threshold.
        op: Comparison operator.

    Returns:
        ``True`` if the condition is met.
    """
    if op == Op.GT:
        return value > threshold
    if op == Op.LT:
        return value < threshold
    if op == Op.EQ:
        return abs(value - threshold) < 1e-9
    return False


# ---------------------------------------------------------------------------
# Alert callback types
# ---------------------------------------------------------------------------

AlertCallback = Callable[["AlertRule", dict[str, Any]], None]


def _log_callback(rule: "AlertRule", context: dict[str, Any]) -> None:
    """Default callback: log the alert at the appropriate level.

    Args:
        rule: The alert rule that fired.
        context: Metric context at the time of firing.
    """
    msg = f"ALERT [{rule.severity.value.upper()}] {rule.name}: {rule.description}"
    if rule.severity == AlertSeverity.CRITICAL:
        logger.critical(msg, extra={"alert_rule": rule.name, "context": context})
    elif rule.severity == AlertSeverity.WARNING:
        logger.warning(msg, extra={"alert_rule": rule.name, "context": context})
    else:
        logger.info(msg, extra={"alert_rule": rule.name, "context": context})


# ---------------------------------------------------------------------------
# Alert rule
# ---------------------------------------------------------------------------

@dataclass
class AlertRule:
    """A single alert threshold rule.

    Attributes:
        name: Unique identifier for this rule.
        description: Human-readable explanation.
        metric: The metric to evaluate (dotted path understood by
            the evaluator, e.g. ``flag_rate``, ``provider_errors``).
        op: Comparison operator.
        threshold: Value to compare against.
        cooldown_seconds: Minimum seconds between consecutive fires.
        severity: Severity level.
        callback: Function to call when the alert fires.
            Defaults to ``_log_callback``.
        last_fired: Timestamp of the most recent fire (managed internally).
        fire_count: Total number of times this rule has fired.
    """

    name: str = ""
    description: str = ""
    metric: str = ""
    op: Op = Op.GT
    threshold: float = 0.0
    cooldown_seconds: float = 300.0
    severity: AlertSeverity = AlertSeverity.WARNING
    callback: AlertCallback = _log_callback
    last_fired: float = 0.0
    fire_count: int = 0


# ---------------------------------------------------------------------------
# Alert manager
# ---------------------------------------------------------------------------

class AlertManager:
    """Evaluate alert rules against current metrics and fire on breach.

    Usage::

        metrics = MetricsReporter()
        alert_mgr = AlertManager(metrics)
        alert_mgr.add_rule(AlertRule(
            name="high_flag_rate",
            description="Flag rate exceeds 3× baseline",
            metric="flag_rate",
            op=Op.GT,
            threshold=30.0,
            severity=AlertSeverity.CRITICAL,
        ))
        alert_mgr.evaluate()

    Args:
        metrics: The :class:`MetricsReporter` to poll for current values.
        history_path: Optional path to persist alert history.
    """

    def __init__(
        self,
        metrics: MetricsReporter,
        *,
        history_path: str = "",
    ) -> None:
        self._metrics = metrics
        self._rules: list[AlertRule] = []
        self._history_path = history_path

        # Alert history
        self._history: list[dict[str, Any]] = []

        # Register built-in rules
        self._register_builtins()

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, rule: AlertRule) -> str:
        """Register an alert rule.

        Args:
            rule: The :class:`AlertRule` to add.

        Returns:
            The rule name.
        """
        self._rules.append(rule)
        return rule.name

    def remove_rule(self, name: str) -> bool:
        """Remove an alert rule by name.

        Args:
            name: Rule name to remove.

        Returns:
            ``True`` if the rule was found and removed.
        """
        for i, r in enumerate(self._rules):
            if r.name == name:
                self._rules.pop(i)
                return True
        return False

    def get_rule(self, name: str) -> AlertRule | None:
        """Look up a rule by name.

        Args:
            name: Rule name.

        Returns:
            The :class:`AlertRule` or ``None``.
        """
        for r in self._rules:
            if r.name == name:
                return r
        return None

    def list_rules(self) -> list[dict[str, Any]]:
        """Return all registered rules as serialisable dicts."""
        return [
            {
                "name": r.name,
                "description": r.description,
                "metric": r.metric,
                "op": r.op.value,
                "threshold": r.threshold,
                "cooldown_seconds": r.cooldown_seconds,
                "severity": r.severity.value,
                "last_fired": r.last_fired,
                "fire_count": r.fire_count,
            }
            for r in self._rules
        ]

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(self) -> list[dict[str, Any]]:
        """Evaluate all rules against current metrics.

        Rules whose threshold is breached and whose cooldown has
        elapsed will fire, invoking their callback.

        Returns:
            A list of fired alert dicts for this evaluation round.
        """
        fired: list[dict[str, Any]] = []
        now = time.time()

        for rule in self._rules:
            value = self._resolve_metric(rule.metric)
            if value is None:
                continue

            if not _evaluate(value, rule.threshold, rule.op):
                continue

            # Check cooldown
            if now - rule.last_fired < rule.cooldown_seconds:
                continue

            # Fire!
            rule.last_fired = now
            rule.fire_count += 1

            context = {
                "metric": rule.metric,
                "value": value,
                "threshold": rule.threshold,
                "op": rule.op.value,
                "timestamp": now,
            }

            alert_record = {
                "rule_name": rule.name,
                "description": rule.description,
                "severity": rule.severity.value,
                "timestamp": now,
                "context": context,
            }

            try:
                rule.callback(rule, context)
            except Exception as exc:
                logger.error("Alert callback failed for %s: %s", rule.name, exc)

            self._history.append(alert_record)
            fired.append(alert_record)

        # Persist history if configured
        if fired and self._history_path:
            self._export_history()

        return fired

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def alert_history(
        self,
        *,
        since: float = 0.0,
        severity: str = "",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query alert history.

        Args:
            since: Unix timestamp — only return alerts after this time.
            severity: Filter by severity ("info", "warning", "critical").
            limit: Maximum number of entries to return.

        Returns:
            Filtered alert history entries.
        """
        results = [
            entry
            for entry in self._history
            if (not since or entry["timestamp"] >= since)
            and (not severity or entry["severity"] == severity)
        ]
        return results[-limit:]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _export_history(self) -> None:
        """Append recent history to the JSON lines file."""
        if not self._history_path:
            return
        path = Path(self._history_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as fh:
            for entry in self._history[-10:]:
                fh.write(json.dumps(entry, default=str) + "\n")

    # ------------------------------------------------------------------
    # Metric resolution
    # ------------------------------------------------------------------

    def _resolve_metric(self, metric_path: str) -> float | None:
        """Resolve a dotted metric path to a numeric value.

        Supports:
            * ``flag_rate`` — current flag rate percentage
            * ``appeal_rate`` — current appeal rate percentage
            * ``requests_per_minute`` — requests per minute
            * ``provider_errors.{name}`` — total errors for provider
            * ``requests_total`` — total request count
            * ``latency_p95.{name}`` — P95 latency for a provider
            * Any metric name directly supported by MetricsReporter

        Args:
            metric_path: Dotted metric identifier.

        Returns:
            The current value or ``None`` if unresolvable.
        """
        # Direct metrics reporter calls
        direct = {
            "flag_rate": self._metrics.flag_rate,
            "appeal_rate": self._metrics.appeal_rate,
            "requests_per_minute": self._metrics.requests_per_minute,
            "requests_total": self._metrics.requests_total,
        }

        if metric_path in direct:
            return direct[metric_path]()

        # Provider-specific metrics: "provider_errors.perspective"
        if metric_path.startswith("provider_errors."):
            provider = metric_path.split(".", 1)[1]
            return float(self._metrics.provider_error_count(provider))

        # Latency percentiles: "latency_p95.perspective"
        if metric_path.startswith("latency_p"):
            parts = metric_path.split(".", 1)
            percentile_str = parts[0].replace("latency_p", "p")
            provider = parts[1] if len(parts) > 1 else ""
            percentiles = self._metrics.provider_latency_percentiles(provider)
            return percentiles.get(percentile_str, 0.0)

        return None

    # ------------------------------------------------------------------
    # Built-in rules
    # ------------------------------------------------------------------

    def _register_builtins(self) -> None:
        """Register the four built-in alert rules."""
        baseline_flag_rate = 10.0  # Assumed baseline 10%

        self._rules = [
            AlertRule(
                name="flag_rate_spike",
                description=(
                    "Flag rate exceeds 3× the assumed baseline of 10% — "
                    "indicates a possible coordinated hate-speech attack"
                ),
                metric="flag_rate",
                op=Op.GT,
                threshold=baseline_flag_rate * 3,
                cooldown_seconds=300.0,
                severity=AlertSeverity.CRITICAL,
            ),
            AlertRule(
                name="high_provider_failure_rate",
                description=(
                    "Provider failure rate exceeds 10% — check API keys, "
                    "network, or provider availability"
                ),
                metric="provider_errors",
                op=Op.GT,
                threshold=10.0,
                cooldown_seconds=300.0,
                severity=AlertSeverity.WARNING,
            ),
            AlertRule(
                name="high_latency",
                description=(
                    "P95 latency exceeds 3000 ms — provider is degrading "
                    "or network congestion"
                ),
                metric="latency_p95",
                op=Op.GT,
                threshold=3000.0,
                cooldown_seconds=300.0,
                severity=AlertSeverity.WARNING,
            ),
            AlertRule(
                name="high_appeal_rate",
                description=(
                    "Appeal rate exceeds 20% — potential false-positive "
                    "issue, review thresholds"
                ),
                metric="appeal_rate",
                op=Op.GT,
                threshold=20.0,
                cooldown_seconds=600.0,
                severity=AlertSeverity.INFO,
            ),
        ]
