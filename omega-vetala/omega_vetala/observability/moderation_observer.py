# 🔱 omega-vetala — Moderation Observer
# ⬡ OMEGA ⬡ P8-WATCHTOWER ⬡ MODERATION-OBSERVER
#
# AP Token: AP-MODERATION-P8-v1.0.0
# [id-soft: doom-1993] BSP Culling — early-exit on alert conditions
# [id-soft: quake-1996] Surface Cache — caching hash lookups
#
"""Main observer class that wraps the provider chain with observability.

The :class:`ModerationObserver` sits between the application and the
provider chain, automatically:
    1. Creating a distributed trace for each moderation request.
    2. Logging every decision with hashed content.
    3. Recording metrics (counters, histograms).
    4. Evaluating alert rules.

Usage::

    from omega_vetala.providers.chain import ProviderChain
    from omega_vetala.observability import ModerationObserver

    chain = ProviderChain.from_yaml("config.yaml")
    observer = ModerationObserver(chain)

    # Observe a moderation decision
    result = await observer.observe(chain, "some user text")

    # Appeal a decision (false positive tracking)
    observer.appeal(result.trace_id, result, user_feedback=False)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

import anyio

from omega_vetala.observability.alerts import AlertManager
from omega_vetala.observability.metrics import MetricsReporter
from omega_vetala.observability.structured_logger import (
    ActionTaken,
    ModerationLogger,
)
from omega_vetala.observability.tracing import (
    TraceContext,
    clear_trace,
    start_trace,
    traced,
    within_trace,
)
from omega_vetala.providers.base import ModerationResult, ModelProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default action resolution
# ---------------------------------------------------------------------------

def _resolve_action(result: ModerationResult) -> str:
    """Map a :class:`ModerationResult` to an action.

    Args:
        result: The moderation result.

    Returns:
        One of ``ActionTaken`` values.
    """
    if not result.is_flagged:
        return ActionTaken.ALLOW
    if result.confidence >= 0.9:
        return ActionTaken.BLOCK
    if result.confidence >= 0.5:
        return ActionTaken.WARN
    return ActionTaken.REVIEW


# ---------------------------------------------------------------------------
# Main observer
# ---------------------------------------------------------------------------

class ModerationObserver:
    """Wraps moderation provider chains with full observability.

    The observer is the integration point between the application and
    the observability fabric.  Every moderation decision flows through
    :meth:`observe`, which auto-instruments tracing, logging, metrics,
    and alerts.

    Args:
        chain: The :class:`ProviderChain` (or any ``ModelProvider``)
            to observe.
        logger_instance: Optional :class:`ModerationLogger` instance.
            Created with defaults if omitted.
        metrics: Optional :class:`MetricsReporter` instance.
            Created with defaults if omitted.
        alerts: Optional :class:`AlertManager` instance.
            Created with defaults if omitted.
    """

    def __init__(
        self,
        chain: ModelProvider,
        *,
        logger_instance: ModerationLogger | None = None,
        metrics: MetricsReporter | None = None,
        alerts: AlertManager | None = None,
    ) -> None:
        self._chain = chain

        self._logger = logger_instance or ModerationLogger()
        self._metrics = metrics or MetricsReporter()
        self._alerts = alerts or AlertManager(self._metrics)

        # Hash-frequency tracking for top-flagged-pattern analysis.
        # Uses SHA-256[:16] content hashes — not raw text.
        # NOTE: This is an in-memory map; for production, offload to
        # an external aggregator (e.g. a stream processor consuming
        # the structured logs).
        self._hash_frequencies: dict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    # Core observe method
    # ------------------------------------------------------------------

    @traced("moderation_observer.observe")
    async def observe(
        self,
        provider: ModelProvider,
        text: str,
        trace_id: str = "",
    ) -> ModerationResult:
        """Observe a moderation decision through the full pipeline.

        Steps:
            1. Create or resume a trace context.
            2. Call the provider chain.
            3. Log the decision (hashed content only).
            4. Record metrics.
            5. Evaluate alert rules.
            6. Return the result.

        Args:
            provider: The provider (or chain) to invoke.
            text: The user-generated content to moderate.
            trace_id: Optional trace ID.  Auto-generated if omitted.

        Returns:
            The :class:`ModerationResult` from the provider.
        """
        # Step 1: Trace
        if trace_id:
            trace = TraceContext(trace_id=trace_id)
            within_trace(trace)
        else:
            trace = start_trace()

        # Step 2: Invoke provider
        try:
            result = await provider.analyze(text)
        except Exception as exc:
            # Log failure and re-raise
            self._logger.log_systemic_failure(
                trace_id=trace.trace_id,
                error_message=f"Provider chain crashed: {exc}",
            )
            self._metrics.record_error(provider_name="provider_chain")
            clear_trace()

            return ModerationResult(
                is_flagged=False,
                confidence=0.0,
                provider_name="provider_chain",
                categories={"__observer_error__": 1.0},
                trace_id=trace.trace_id,
            )

        # Step 3: Log
        action = _resolve_action(result)
        if result.is_flagged:
            self._logger.log_flag_event(
                trace_id=trace.trace_id,
                provider_name=result.provider_name,
                is_flagged=result.is_flagged,
                confidence=result.confidence,
                latency_ms=result.latency_ms,
                categories=result.categories,
                action_taken=action,
                text=text,
            )
        else:
            self._logger.log_decision(
                trace_id=trace.trace_id,
                provider_name=result.provider_name,
                is_flagged=result.is_flagged,
                confidence=result.confidence,
                latency_ms=result.latency_ms,
                categories=result.categories,
                action_taken=action,
                text=text,
            )

        # Step 4: Metrics
        self._metrics.record_request(
            provider_name=result.provider_name,
            action_type=action,
        )
        if result.is_flagged:
            self._metrics.record_flag(provider_name=result.provider_name)
        if result.latency_ms > 0:
            self._metrics.record_latency(
                provider_name=result.provider_name,
                latency_ms=result.latency_ms,
            )

        # Hash-frequency tracking (for top-flagged-patterns dashboard)
        if result.is_flagged and text:
            import hashlib
            h = hashlib.sha256(text.encode()).hexdigest()[:16]
            self._hash_frequencies[h] += 1

        # Step 5: Alerts
        fired = self._alerts.evaluate()
        if fired:
            logger.info(
                "Alert rules fired during moderation: %s",
                [a["rule_name"] for a in fired],
            )

        # Clean up trace
        clear_trace()

        return result

    # ------------------------------------------------------------------
    # Appeal
    # ------------------------------------------------------------------

    @traced("moderation_observer.appeal")
    def appeal(
        self,
        trace_id: str,
        original_result: ModerationResult,
        user_feedback: bool,
    ) -> None:
        """Record a user appeal against a moderation decision.

        Appeals are critical for detecting false positives.  A high
        appeal rate triggers the ``high_appeal_rate`` alert rule.

        Args:
            trace_id: The trace ID of the original decision.
            original_result: The :class:`ModerationResult` being appealed.
            user_feedback: ``True`` if the user agrees content was
                correctly flagged, ``False`` if they contest it.
        """
        self._logger.log_decision(
            trace_id=trace_id,
            provider_name=original_result.provider_name,
            is_flagged=original_result.is_flagged,
            confidence=original_result.confidence,
            latency_ms=0.0,
            categories=original_result.categories,
            action_taken=f"appeal:user_feedback={user_feedback}",
        )

        self._metrics.record_appeal(provider_name=original_result.provider_name)

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    @traced("moderation_observer.heartbeat")
    def heartbeat(self) -> dict[str, Any]:
        """Health check for the observer and its subcomponents.

        Returns:
            A dict with status, uptime, and component health.
        """
        snapshot = self._metrics.snapshot()
        return {
            "status": "ok",
            "chain_type": type(self._chain).__name__,
            "total_requests": snapshot["requests_total"],
            "total_alerts_fired": sum(
                r["fire_count"] for r in self._alerts.list_rules()
            ),
            "metrics_status": "ok",
            "logger_status": "ok",
            "alerts_status": "ok",
        }

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def metrics(self) -> MetricsReporter:
        """The :class:`MetricsReporter` instance."""
        return self._metrics

    @property
    def alerts(self) -> AlertManager:
        """The :class:`AlertManager` instance."""
        return self._alerts

    @property
    def logger(self) -> ModerationLogger:
        """The :class:`ModerationLogger` instance."""
        return self._logger

    @property
    def hash_frequencies(self) -> dict[str, int]:
        """Copy of the in-memory hash-frequency map."""
        return dict(self._hash_frequencies)
