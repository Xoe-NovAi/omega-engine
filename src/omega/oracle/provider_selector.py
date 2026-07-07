# AP: AP-PROV-SELECT-v1.0.0
# AP: AP-PROV-SELECT-v1.0.0
# 🔱 Provider Selector — Intelligent Backend Routing
# Ported from xna-omega-legacy/src/omega/core/provider_selector.py


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import anyio
from typing import Any, Dict, List, Optional, Tuple
from ..errors import ProviderUnavailableError, ProviderError

logger = logging.getLogger(__name__)

class ProviderSelector:
    """
    Intelligent provider routing that balances performance, cost, and sovereignty.
    
    Implements a penalty-based selection mechanism:
    - Local providers are always preferred (Sovereignty).
    - Cloud providers are penalized if PII is detected in the query.
    - Providers with high recent error rates are deprioritized.
    """
    
    def __init__(self, model_gateway):
        self.model_gateway = model_gateway
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
        
        Score = (BasePriority * 10) - PII_Penalty - Error_Penalty
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
        
        # Error Penalty: Penalize providers with high recent error rates
        # This would integrate with the HealthMonitor's EWMA score
        error_rate = getattr(provider, "recent_error_rate", 0.0)
        if isinstance(error_rate, (int, float)):
            score -= float(error_rate * 50.0)
        
        return float(score)
