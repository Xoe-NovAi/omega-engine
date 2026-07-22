# AP: AP-ORACLE-CASCADE-ROUTER-v1.0.0
# 🔱 Oracle Cascade Router — Cost-Weighted Provider Fallback
# Implements intelligent provider cascading based on cost, quality, latency, and quota
# Uses weighted scoring to select optimal provider and fallback chain

"""
Cascade Router for Oracle Provider Fabric

Implements intelligent provider selection and fallback based on:
- Cost efficiency (lower cost = higher score)
- Quality score (higher quality = higher score) 
- Latency performance (lower latency = higher score)
- Quota availability (available quota = higher score)
- Provider health (healthy = higher score)

Uses a weighted scoring algorithm to rank providers and create
an optimal fallback chain that minimizes cost while maximizing
quality and reliability.

Configuration is driven from config/providers.yaml with cost/quality/latency scores.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from omega.errors import OmegaError
from omega.oracle.health_monitor import HealthMonitor
from omega.oracle.quota_tracker import QuotaTracker, QuotaSnapshot
from omega.oracle.token_estimator import TokenEstimator

logger = __import__("logging").getLogger("omega.cascade_router")


@dataclass
class ProviderScore:
    """Score breakdown for a provider."""
    provider: str
    total_score: float
    cost_score: float = 0.0
    quality_score: float = 0.0
    latency_score: float = 0.0
    quota_score: float = 0.0
    health_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure score is float."""
        self.total_score = float(self.total_score)


@dataclass
class RoutingDecision:
    """Result of a routing decision."""
    selected_provider: str
    fallback_chain: List[str]
    reasoning: str
    scores: List[ProviderScore]
    estimated_cost: float = 0.0
    estimated_quality: float = 0.0
    timestamp: float = field(default_factory=time.time)


class CascadeRouter:
    """
    Routes LLM requests to optimal providers using weighted scoring.
    
    Implements a cascade (waterfall) routing strategy where:
    1. All providers are scored based on cost, quality, latency, quota, and health
    2. The highest-scoring provider is selected as primary
    3. Remaining providers form the fallback chain in score order
    4. Quota-exhausted providers are filtered out unless no alternatives exist
    
    Weights are configurable via provider metadata in config/providers.yaml:
    - cost_weight: Default 0.4 (lower cost = higher score)
    - quality_weight: Default 0.4 (higher quality = higher score)
    - latency_weight: Default 0.2 (lower latency = higher score)
    """

    def __init__(
        self,
        model_gateway: Any,
        health_monitor: Optional[HealthMonitor] = None,
        quota_tracker: Optional[QuotaTracker] = None,
        token_estimator: Optional[TokenEstimator] = None,
    ):
        """
        Initialize the cascade router.
        
        Args:
            model_gateway: The model gateway instance
            health_monitor: Optional health monitor for provider health
            quota_tracker: Optional quota tracker for quota awareness
            token_estimator: Optional token estimator for cost calculation
        """
        self._gateway = model_gateway
        self._health_monitor = health_monitor
        self._quota_tracker = quota_tracker or QuotaTracker()
        self._token_estimator = token_estimator or TokenEstimator()
        self._logger = logger

        # Default weights (can be overridden per-provider in config)
        self._default_weights = {
            "cost": 0.4,
            "quality": 0.4,
            "latency": 0.2,
        }

    async def route_request(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        exclude_providers: Optional[List[str]] = None,
    ) -> RoutingDecision:
        """
        Route a request to the optimal provider with fallback chain.
        
        Args:
            model_name: The model to use for generation
            system_prompt: System prompt for the request
            user_prompt: User prompt for the request
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            exclude_providers: Providers to exclude from consideration
            
        Returns:
            RoutingDecision with selected provider and fallback chain
        """
        start_time = time.time()
        
        # Get available providers for this model
        available_provider_objects = await self._gateway.get_available_providers(model_name)
        if not available_provider_objects:
            raise OmegaError(f"No providers available for model {model_name}")
        
        # Extract provider names from objects
        available_providers = [p.name for p in available_provider_objects]
        
        # Filter out excluded providers
        if exclude_providers:
            available_providers = [
                p for p in available_providers 
                if p not in exclude_providers
            ]
        
        # Estimate token usage for cost calculation
        try:
            prompt_tokens = self._token_estimator.estimate_prompt_tokens(
                system_prompt, user_prompt, model_name
            )
            completion_tokens = self._token_estimator.estimate_completion_tokens(
                prompt_tokens, model_name, max_tokens
            )
            total_estimated_tokens = prompt_tokens + completion_tokens
        except Exception as e:
            self._logger.warning(f"Failed to estimate tokens: {e}")
            prompt_tokens = 0
            completion_tokens = max_tokens
            total_estimated_tokens = max_tokens
        
        # Score all available providers
        scored_providers: List[ProviderScore] = []
        for provider_name in available_providers:
            try:
                score = await self._score_provider(
                    provider_name, 
                    model_name,
                    prompt_tokens,
                    completion_tokens,
                    total_estimated_tokens
                )
                scored_providers.append(score)
            except Exception as e:
                self._logger.warning(f"Failed to score provider {provider_name}: {e}")
                # Still include it with a poor score so it's last resort
                scored_providers.append(ProviderScore(
                    provider=provider_name,
                    total_score=-1000.0,  # Very low score
                    details={"error": str(e)}
                ))
        
        # Sort by score (descending - higher is better)
        scored_providers.sort(key=lambda p: p.total_score, reverse=True)
        
        # Filter out quota-exhausted providers unless we have no choice
        non_exhausted = [p for p in scored_providers if not self._is_quota_exhausted(p.provider)]
        if non_exhausted:
            scored_providers = non_exhausted
        elif scored_providers:
            self._logger.warning("All providers are quota-exhausted, using highest-scoring anyway")
        
        if not scored_providers:
            raise OmegaError("No providers available for routing")
        
        # Select primary provider (highest score)
        primary = scored_providers[0]
        
        # Build fallback chain (remaining providers in score order)
        fallback_chain = [p.provider for p in scored_providers[1:]]
        
        # Calculate estimated cost and quality
        estimated_cost = self._estimate_cost(primary.provider, total_estimated_tokens)
        estimated_quality = primary.quality_score
        
        # Build reasoning
        reasoning = self._build_reasoning(primary, scored_providers[1:3] if len(scored_providers) > 1 else [])
        
        decision = RoutingDecision(
            selected_provider=primary.provider,
            fallback_chain=fallback_chain,
            reasoning=reasoning,
            scores=scored_providers,
            estimated_cost=estimated_cost,
            estimated_quality=estimated_quality,
            timestamp=start_time,
        )
        
        self._logger.info(
            f"Routed {model_name} to {primary.provider} "
            f"(score: {primary.total_score:.1f}, "
            f"cost: {estimated_cost:.4f}, "
            f"quality: {estimated_quality:.1f})"
            f"{' -> ' + ' -> '.join(fallback_chain[:2]) if fallback_chain else ''}"
        )
        
        return decision

    async def _score_provider(
        self,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ) -> ProviderScore:
        """
        Score a provider based on cost, quality, latency, quota, and health.
        
        Returns a ProviderScore with individual component scores and total.
        """
        # Get provider config
        provider_config = self._get_provider_config(provider_name)
        
        # Get weights (provider-specific or default)
        weights = provider_config.get("routing_weights", self._default_weights)
        
        # Initialize score components
        cost_score = self._calculate_cost_score(provider_name, model_name, total_tokens, provider_config)
        quality_score = self._get_quality_score(provider_name, provider_config)
        latency_score = self._get_latency_score(provider_name)
        quota_score = self._get_quota_score(provider_name)
        health_score = self._get_health_score(provider_name)
        
        # Calculate weighted total
        total_score = (
            weights.get("cost", 0.4) * cost_score +
            weights.get("quality", 0.4) * quality_score +
            weights.get("latency", 0.2) * latency_score +
            0.0 * quota_score +  # Quota is handled by filtering, not scoring
            0.0 * health_score   # Health is handled by filtering, not scoring
        )
        
        # Apply quota penalty if exhausted (but don't filter out yet)
        if self._is_quota_exhausted(provider_name):
            total_score *= 0.1  # Heavy penalty but still allow as last resort
        
        return ProviderScore(
            provider=provider_name,
            total_score=max(0.0, total_score),  # Ensure non-negative
            cost_score=cost_score,
            quality_score=quality_score,
            latency_score=latency_score,
            quota_score=quota_score,
            health_score=health_score,
            details={
                "model": model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "weights": weights,
                "quota_exhausted": self._is_quota_exhausted(provider_name),
            }
        )

    def _get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get provider configuration from the model gateway."""
        try:
            # Try to get from gateway's provider config
            if hasattr(self._gateway, 'providers'):
                for provider in self._gateway.providers:
                    if getattr(provider, 'name', None) == provider_name:
                        config = getattr(provider, 'config', {})
                        if isinstance(config, dict):
                            return config
                        elif hasattr(config, '__dict__'):
                            return vars(config)
            return {}
        except Exception:
            return {}

    def _calculate_cost_score(
        self,
        provider_name: str,
        model_name: str,
        total_tokens: int,
        provider_config: Dict[str, Any]
    ) -> float:
        """
        Calculate cost score (higher = lower cost).
        
        Returns 0-100 score where 100 = free, 0 = very expensive.
        """
        # Get cost per 1K tokens from config
        cost_per_1k = provider_config.get("cost_per_1k_tokens", 0.0)
        if cost_per_1k == 0.0:
            # Try to infer from provider name
            cost_per_1k = self._estimate_cost_per_1k(provider_name)
        
        # Calculate cost for this request
        cost = (total_tokens / 1000) * cost_per_1k
        
        # Convert to score (inverse - lower cost = higher score)
        # Using exponential decay: score = 100 * e^(-cost/max_cost)
        # where max_cost is $0.10 per 1K tokens (expensive but not extreme)
        max_cost = 0.10
        if cost <= 0:
            return 100.0
        score = 100.0 * (2.71828 ** (-cost / max_cost))
        return max(0.0, min(100.0, score))

    def _estimate_cost_per_1k(self, provider_name: str) -> float:
        """Estimate cost per 1K tokens based on provider name."""
        provider_lower = provider_name.lower()
        
        # Free/local providers
        if any(x in provider_lower for x in ["native-gguf", "lmster", "ollama", "mock"]):
            return 0.0
        
        # Known free tiers
        if "openrouter" in provider_lower:
            return 0.001  # Very low cost for free tier
        if "google-compat" in provider_lower:
            return 0.0005  # Gemini free tier is very cheap
        
        # Known paid providers
        if "anthropic" in provider_lower:
            return 0.008  # ~$8/M input, ~$24/M output -> avg ~$0.008/1K
        if "openai" in provider_lower:
            return 0.003  # GPT-3.5 turbo pricing
        if "google" in provider_lower and "compat" not in provider_lower:
            return 0.0005  # Gemini Pro pricing
        if "xai" in provider_lower:
            return 0.002  # Estimated Grok pricing
        
        # Default moderate cost
        return 0.005

    def _get_quality_score(self, provider_name: str, provider_config: Dict[str, Any]) -> float:
        """
        Get quality score for a provider.
        
        Returns 0-100 score where 100 = highest quality.
        """
        # Check for explicit quality score in config
        quality = provider_config.get("quality_score")
        if quality is not None:
            return max(0.0, min(100.0, float(quality)))
        
        # Infer quality from provider/model characteristics
        provider_lower = provider_name.lower()
        
        # High quality providers
        if any(x in provider_lower for x in ["anthropic", "opencode-zen"]):
            return 90.0
        if "google" in provider_lower:
            return 85.0
        if "openrouter" in provider_lower:
            return 80.0  # Varies by model
        if "xai" in provider_lower:
            return 75.0
        
        # Medium quality
        if any(x in provider_lower for x in ["sambanova", "cerebras"]):
            return 70.0
        
        # Lower quality but fast/cheap
        if any(x in provider_lower for x in ["native-gguf", "lmster", "ollama"]):
            return 60.0  # Local models vary widely
        
        # Default
        return 50.0

    def _get_latency_score(self, provider_name: str) -> float:
        """
        Get latency score based on recent performance.
        
        Returns 0-100 score where 100 = lowest latency.
        """
        if not self._health_monitor:
            return 50.0  # Neutral if no health data
        
        try:
            breaker = self._health_monitor._breakers.get(provider_name)
            if not breaker:
                return 50.0
            
            # Convert EMA latency to score (lower latency = higher score)
            # Target: <500ms = 100pts, >2000ms = 0pts
            latency_ms = getattr(breaker, 'ema_latency', 1000.0)
            if latency_ms <= 500:
                return 100.0
            elif latency_ms >= 2000:
                return 0.0
            else:
                # Linear interpolation between 500-2000ms
                return 100.0 * (2000 - latency_ms) / 1500
        except Exception:
            return 50.0

    def _get_quota_score(self, provider_name: str) -> float:
        """
        Get quota score based on remaining quota.
        
        Returns 0-100 score where 100 = full quota, 0 = exhausted.
        """
        quota = self._quota_tracker.get_quota(provider_name)
        if not quota:
            return 100.0  # Unknown = assume available
        
        # Score based on the more limited resource (requests or tokens)
        req_pct = (quota.requests_remaining / quota.request_limit * 100) if quota.request_limit > 0 else 100.0
        tok_pct = (quota.tokens_remaining / quota.token_limit * 100) if quota.token_limit > 0 else 100.0
        
        # Use the minimum - the bottleneck resource
        return max(0.0, min(100.0, min(req_pct, tok_pct)))

    def _get_health_score(self, provider_name: str) -> float:
        """
        Get health score based on circuit breaker state.
        
        Returns 0-100 score where 100 = healthy, 0 = tripped/open.
        """
        if not self._health_monitor:
            return 100.0  # Assume healthy if no monitoring
        
        try:
            breaker = self._health_monitor._breakers.get(provider_name)
            if not breaker:
                return 100.0
            
            # Map circuit state to score
            state_scores = {
                "closed": 100.0,    # Healthy
                "half_open": 75.0,  # Recovering
                "open": 0.0,        # Tripped
                "degraded": 50.0,   # Elevated errors
                "unknown": 50.0,    # No data
            }
            
            state_str = getattr(breaker, 'state', 'unknown')
            if hasattr(state_str, 'value'):  # Enum
                state_str = state_str.value
            
            return state_scores.get(str(state_str).lower(), 50.0)
        except Exception:
            return 50.0

    def _is_quota_exhausted(self, provider_name: str) -> bool:
        """Check if a provider's quota is exhausted."""
        return self._quota_tracker.is_quota_exhausted(provider_name)

    def _estimate_cost(self, provider_name: str, total_tokens: int) -> float:
        """Estimate the cost for a request in USD."""
        cost_per_1k = self._estimate_cost_per_1k(provider_name)
        return (total_tokens / 1000) * cost_per_1k

    def _build_reasoning(
        self,
        primary: ProviderScore,
        alternatives: List[ProviderScore]
    ) -> str:
        """Build a human-readable reasoning string for the routing decision."""
        reasons = []
        
        # Primary selection reason
        if primary.cost_score >= 90:
            reasons.append("free/local")
        elif primary.cost_score >= 70:
            reasons.append("low-cost")
        else:
            reasons.append(f"cost-{int(100-primary.cost_score)}")
        
        if primary.quality_score >= 80:
            reasons.append("high-quality")
        elif primary.quality_score >= 60:
            reasons.append("medium-quality")
        
        if primary.latency_score >= 80:
            reasons.append("low-latency")
        elif primary.latency_score >= 50:
            reasons.append("medium-latency")
        
        # Check if quota was a concern
        if primary.details.get("quota_exhausted"):
            reasons.append("quota-limited")
        
        # Add alternatives if close in score
        if alternatives and len(alternatives) > 0:
            second = alternatives[0]
            if abs(primary.total_score - second.total_score) < 10:
                reasons.append(f"close-call-vs-{second.provider}")
        
        return ", ".join(reasons) if reasons else "balanced"


# Global cascade router instance
_cascade_router: Optional[CascadeRouter] = None


def get_cascade_router(
    model_gateway: Any,
    health_monitor: Optional[HealthMonitor] = None,
    quota_tracker: Optional[QuotaTracker] = None,
    token_estimator: Optional[TokenEstimator] = None,
) -> CascadeRouter:
    """Get or create the global cascade router instance."""
    global _cascade_router
    if _cascade_router is None:
        _cascade_router = CascadeRouter(
            model_gateway, 
            health_monitor, 
            quota_tracker, 
            token_estimator
        )
    return _cascade_router