# 🔱 omega-vetala — Observability Pillar (P8 / WatchTower)
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ OBSERVABILITY-FABRIC
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: quake-1996] cvar — metrics as observable state variables
#
"""Observability fabric for the moderation system.

Provides structured logging, metrics collection, distributed tracing,
alert management, and dashboard queries — all designed with privacy
preservation as a first-class constraint. No raw content ever leaks
into logs, metrics, or traces.

Modules:
    structured_logger: JSON-structured decision logging with content hashing.
    metrics: Thread-safe metrics collection with rolling window.
    tracing: Context-var based trace propagation and timing decorator.
    alerts: Threshold-based alert rules with rate-limited firing.
    dashboard: Query interface for metrics and alert history.
    moderation_observer: Wraps provider chains with full observability.
"""

from __future__ import annotations

from omega_vetala.observability.structured_logger import (
    ModerationLogger,
)
from omega_vetala.observability.metrics import MetricsReporter
from omega_vetala.observability.tracing import TraceContext, traced
from omega_vetala.observability.alerts import AlertManager, AlertRule
from omega_vetala.observability.dashboard import DashboardQuery
from omega_vetala.observability.moderation_observer import ModerationObserver

__all__ = [
    "ModerationLogger",
    "MetricsReporter",
    "TraceContext",
    "traced",
    "AlertManager",
    "AlertRule",
    "DashboardQuery",
    "ModerationObserver",
]
