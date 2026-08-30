# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PROV-SELECT-v1.0.0
# AP: AP-PROV-SELECT-v1.0.0
# 🔱 Provider Selector — Intelligent Backend Routing
# Ported from xna-omega-legacy/src/omega/core/provider_selector.py


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
from typing import Any, List
from ..errors import ProviderUnavailableError

logger = logging.getLogger(__name__)


class ProviderSelector:
    """
    Intelligent provider routing that balances performance, cost, and sovereignty.

    Implements a penalty-based selection mechanism:
    - Local providers are always preferred (Sovereignty).
    - Cloud providers are penalized if PII is detected in the query.
    - Providers with high recent error rates are deprioritized.
    """

    def __init__(self, model_gateway, health_monitor=None):
        self.model_gateway = model_gateway
        self.health_monitor = health_monitor
        self.pii_masker = model_gateway.pii_masker if hasattr(model_gateway, "pii_masker") else None

    async def select_best_provider(self, model_name: str, query: str) -> str:
        """
        Selects the optimal provider for a given model and query.

        Returns:
            The name of the selected provider.
        """
        providers = await self.get_ordered_providers(model_name, query)
        if not providers:
            raise ProviderUnavailableError(message=f"No providers available for model {model_name}")

        return providers[0].name

    async def get_ordered_providers(self, model_name: str, query: str) -> List[Any]:
        """Returns all available providers for a model, sorted by suitability score.

        Score = (BasePriority * 10) - PII_Penalty - Error_Penalty
        """
        providers = await self.model_gateway.get_available_providers(model_name)
        if not providers:
            return []

        scored_providers = []
        for provider in providers:
            score = self._calculate_score(provider, query)
            scored_providers.append((provider, score))

        # Sort by score (descending)
        scored_providers.sort(key=lambda x: x[1], reverse=True)

        return [p for p, score in scored_providers]

    def _calculate_score(self, provider: Any, query: str) -> float:
        """Calculates a suitability score for a provider.

        Score = (BasePriority * 10) - PII_Penalty - Latency_Penalty - Stability_Penalty
        """
        # Base priority from config (0 = highest)
        priority = getattr(provider, "priority", 10)
        if not isinstance(priority, (int, float)):
            priority = 10
        score = float((10 - priority) * 10.0)

        # PII Penalty: Heavily penalize cloud providers if PII is detected
        if self.pii_masker and self.pii_masker.detect_pii(query):
            is_cloud = getattr(provider, "is_cloud", False)
            if is_cloud:
                score -= 100.0  # Strong deterrent for cloud PII

        # Stability and Latency Penalties from HealthMonitor
        if self.health_monitor:
            breaker = self.health_monitor._breakers.get(provider.name)
            if breaker:
                # 1. Latency Penalty: Penalize providers with high EMA latency
                # Baseline: 1000ms. Penalty = (ema_latency - 1000) / 100
                latency_penalty = max(0.0, (breaker.ema_latency - 1000.0) / 100.0)
                score -= latency_penalty

                # 2. Stability Penalty: Penalize based on CUSUM drift (instability)
                # CUSUM_G > 0 indicates a trend toward failure.
                stability_penalty = breaker.cusum_g * 5.0
                score -= stability_penalty

        return float(score)
