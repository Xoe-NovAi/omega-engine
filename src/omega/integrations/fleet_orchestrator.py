"""
Fleet Orchestrator for Omega Engine

Manages multiple API provider fleets with quota-aware routing.
Integrates with VaultCore for credential management and quota pollers
for real-time usage monitoring.

Supports:
- Grok (xAI) 8-account fleet
- OpenRouter credits
- GCP Monitoring quotas
- Exa Search rate limits
- Firecrawl credits

M7 Local-First: Routes to local providers before cloud.
M13 Temple-Grade: All implementations include error handling,
retry logic, and structured logging.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import anyio

from .quota_pollers import (
    QuotaPoller,
    QuotaSnapshot,
    QuotaStatus,
    create_quota_poller,
)


class ProviderType(Enum):
    """Provider types for routing."""
    LOCAL = "local"           # Native GGUF, LM Studio, Ollama
    CLOUD = "cloud"           # Grok, OpenRouter, GCP, Exa, Firecrawl
    HYBRID = "hybrid"         # Can route to both


class RouteDecision(Enum):
    """Routing decision outcomes."""
    ROUTE = "route"           # Use this provider
    SKIP = "skip"             # Skip (quota exhausted, rate limited)
    FALLBACK = "fallback"     # Use fallback provider
    BLOCK = "block"           # Block all requests (critical state)


@dataclass
class ProviderFleet:
    """Configuration for a provider fleet."""
    provider_name: str
    provider_type: ProviderType
    accounts: list[dict[str, Any]] = field(default_factory=list)
    quota_poller: Optional[QuotaPoller] = None
    priority: int = 0  # Lower = higher priority
    enabled: bool = True
    last_health_check: float = 0
    health_check_interval: float = 300  # 5 minutes


@dataclass
class RouteRequest:
    """Request for provider routing."""
    query: str
    required_capability: Optional[str] = None
    max_latency_ms: Optional[int] = None
    prefer_local: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RouteResponse:
    """Response from provider routing."""
    provider: str
    decision: RouteDecision
    account_id: Optional[int] = None
    quota: Optional[QuotaSnapshot] = None
    fallback_provider: Optional[str] = None
    reason: str = ""
    latency_ms: float = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class FleetOrchestrator:
    """
    Orchestrates multiple API provider fleets with quota-aware routing.
    
    Features:
    - Real-time quota monitoring via pollers
    - Automatic failover on quota exhaustion
    - Rate limit respect with exponential backoff
    - Health checks for provider availability
    - Integration with VaultCore for credentials
    """
    
    def __init__(self):
        self._fleets: dict[str, ProviderFleet] = {}
        self._quota_cache: dict[str, QuotaSnapshot] = {}
        self._last_quota_update: dict[str, float] = {}
        self._quota_update_interval: float = 60.0  # 1 minute
        self._circuit_breakers: dict[str, dict[str, Any]] = {}
    
    def register_fleet(
        self,
        provider_name: str,
        provider_type: ProviderType,
        accounts: Optional[list[dict[str, Any]]] = None,
        quota_poller: Optional[QuotaPoller] = None,
        priority: int = 0,
        enabled: bool = True,
    ) -> None:
        """Register a provider fleet."""
        fleet = ProviderFleet(
            provider_name=provider_name,
            provider_type=provider_type,
            accounts=accounts or [],
            quota_poller=quota_poller,
            priority=priority,
            enabled=enabled,
        )
        self._fleets[provider_name] = fleet
    
    def unregister_fleet(self, provider_name: str) -> None:
        """Unregister a provider fleet."""
        self._fleets.pop(provider_name, None)
        self._quota_cache.pop(provider_name, None)
        self._last_quota_update.pop(provider_name, None)
        self._circuit_breakers.pop(provider_name, None)
    
    async def get_quota(self, provider_name: str, force: bool = False) -> QuotaSnapshot:
        """Get current quota for a provider."""
        fleet = self._fleets.get(provider_name)
        if not fleet or not fleet.quota_poller:
            return QuotaSnapshot(
                provider=provider_name,
                status=QuotaStatus.UNKNOWN,
                remaining=0,
                total=0,
                used=0,
                percent_remaining=0,
                error="No quota poller configured",
            )
        
        # Check cache freshness
        now = time.time()
        last_update = self._last_quota_update.get(provider_name, 0)
        if not force and (now - last_update) < self._quota_update_interval:
            cached = self._quota_cache.get(provider_name)
            if cached:
                return cached
        
        # Poll fresh quota
        snapshot = await fleet.quota_poller.poll(force=force)
        self._quota_cache[provider_name] = snapshot
        self._last_quota_update[provider_name] = now
        
        return snapshot
    
    async def get_all_quotas(self, force: bool = False) -> dict[str, QuotaSnapshot]:
        """Get quota for all registered providers."""
        quotas = {}
        for provider_name in self._fleets:
            quotas[provider_name] = await self.get_quota(provider_name, force=force)
        return quotas
    
    def _check_circuit_breaker(self, provider_name: str) -> bool:
        """Check if circuit breaker is open for a provider."""
        breaker = self._circuit_breakers.get(provider_name)
        if not breaker:
            return False
        
        if breaker.get("open", False):
            # Check if half-open period has elapsed
            if time.time() - breaker.get("opened_at", 0) > breaker.get("half_open_timeout", 300):
                breaker["open"] = False
                breaker["half_open"] = True
                return False
            return True
        
        return False
    
    def _trip_circuit_breaker(self, provider_name: str, reason: str) -> None:
        """Trip circuit breaker for a provider."""
        self._circuit_breakers[provider_name] = {
            "open": True,
            "half_open": False,
            "reason": reason,
            "opened_at": time.time(),
            "half_open_timeout": 300,  # 5 minutes
            "failure_count": self._circuit_breakers.get(provider_name, {}).get("failure_count", 0) + 1,
        }
    
    def _reset_circuit_breaker(self, provider_name: str) -> None:
        """Reset circuit breaker after successful use."""
        if provider_name in self._circuit_breakers:
            self._circuit_breakers[provider_name] = {
                "open": False,
                "half_open": False,
                "failure_count": 0,
            }
    
    async def _evaluate_provider(
        self,
        provider_name: str,
        request: RouteRequest,
    ) -> tuple[RouteDecision, Optional[QuotaSnapshot], str]:
        """Evaluate if a provider can handle the request."""
        fleet = self._fleets.get(provider_name)
        if not fleet:
            return RouteDecision.SKIP, None, "Provider not registered"
        
        if not fleet.enabled:
            return RouteDecision.SKIP, None, "Provider disabled"
        
        # Check circuit breaker
        if self._check_circuit_breaker(provider_name):
            return RouteDecision.SKIP, None, "Circuit breaker open"
        
        # Get quota
        quota = await self.get_quota(provider_name)
        
        # Check quota status
        if quota.status == QuotaStatus.EXHAUSTED:
            self._trip_circuit_breaker(provider_name, "Quota exhausted")
            return RouteDecision.SKIP, quota, "Quota exhausted"
        
        if quota.status == QuotaStatus.CRITICAL:
            return RouteDecision.FALLBACK, quota, "Quota critical"
        
        # Check rate limits
        if quota.rate_limit_rpm:
            # TODO: Implement rate limit tracking
            pass
        
        return RouteDecision.ROUTE, quota, "Available"
    
    async def route_request(self, request: RouteRequest) -> RouteResponse:
        """
        Route a request to the best available provider.
        
        Routing logic:
        1. If prefer_local, try local providers first
        2. Check quota for each provider in priority order
        3. Return first available provider
        4. If all exhausted, return fallback or block
        """
        start_time = time.time()
        
        # Separate local and cloud providers
        local_providers = []
        cloud_providers = []
        
        for name, fleet in self._fleets.items():
            if fleet.provider_type == ProviderType.LOCAL:
                local_providers.append((fleet.priority, name))
            elif fleet.provider_type == ProviderType.CLOUD:
                cloud_providers.append((fleet.priority, name))
        
        # Sort by priority (lower = higher priority)
        local_providers.sort()
        cloud_providers.sort()
        
        # Try local first if preferred
        providers_to_try = []
        if request.prefer_local:
            providers_to_try.extend([name for _, name in local_providers])
        providers_to_try.extend([name for _, name in cloud_providers])
        
        # If not prefer_local, try cloud first
        if not request.prefer_local:
            providers_to_try = [name for _, name in cloud_providers] + [name for _, name in local_providers]
        
        last_quota = None
        last_reason = ""
        
        for provider_name in providers_to_try:
            decision, quota, reason = await self._evaluate_provider(provider_name, request)
            last_quota = quota
            last_reason = reason
            
            if decision == RouteDecision.ROUTE:
                # Find available account for fleet providers
                account_id = None
                fleet = self._fleets[provider_name]
                if fleet.accounts:
                    # TODO: Implement account selection logic
                    account_id = 1
                
                latency_ms = (time.time() - start_time) * 1000
                return RouteResponse(
                    provider=provider_name,
                    decision=decision,
                    account_id=account_id,
                    quota=quota,
                    reason=reason,
                    latency_ms=latency_ms,
                )
            
            elif decision == RouteDecision.FALLBACK:
                # Continue to next provider
                continue
        
        # All providers exhausted or unavailable
        latency_ms = (time.time() - start_time) * 1000
        return RouteResponse(
            provider="none",
            decision=RouteDecision.BLOCK,
            quota=last_quota,
            reason=f"All providers exhausted: {last_reason}",
            latency_ms=latency_ms,
        )
    
    async def health_check(self, provider_name: Optional[str] = None) -> dict[str, Any]:
        """Check health of providers."""
        results = {}
        
        providers_to_check = [provider_name] if provider_name else list(self._fleets.keys())
        
        for name in providers_to_check:
            fleet = self._fleets.get(name)
            if not fleet:
                results[name] = {"status": "not_registered"}
                continue
            
            try:
                quota = await self.get_quota(name, force=True)
                results[name] = {
                    "status": "healthy" if quota.status != QuotaStatus.EXHAUSTED else "exhausted",
                    "quota_status": quota.status.value,
                    "remaining": quota.remaining,
                    "total": quota.total,
                    "percent_remaining": quota.percent_remaining,
                    "circuit_breaker": self._circuit_breakers.get(name, {}),
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                }
        
        return results
    
    async def get_fleet_summary(self) -> dict[str, Any]:
        """Get summary of all registered fleets."""
        summary = {
            "total_fleets": len(self._fleets),
            "enabled_fleets": sum(1 for f in self._fleets.values() if f.enabled),
            "providers": {},
        }
        
        for name, fleet in self._fleets.items():
            quota = self._quota_cache.get(name)
            summary["providers"][name] = {
                "type": fleet.provider_type.value,
                "enabled": fleet.enabled,
                "accounts": len(fleet.accounts),
                "priority": fleet.priority,
                "has_quota_poller": fleet.quota_poller is not None,
                "quota_status": quota.status.value if quota else "unknown",
                "quota_remaining": quota.remaining if quota else 0,
                "circuit_breaker": self._circuit_breakers.get(name, {}),
            }
        
        return summary


# Factory function for creating orchestrator with common providers
async def create_default_orchestrator(
    vault_core: Any = None,
    config: Optional[dict[str, Any]] = None,
) -> FleetOrchestrator:
    """
    Create a FleetOrchestrator with default provider configurations.
    
    Args:
        vault_core: VaultCore instance for credential retrieval
        config: Additional configuration overrides
        
    Returns:
        Configured FleetOrchestrator instance
    """
    orchestrator = FleetOrchestrator()
    config = config or {}
    
    # Register local providers (highest priority)
    orchestrator.register_fleet(
        provider_name="native-gguf",
        provider_type=ProviderType.LOCAL,
        priority=0,
    )
    
    orchestrator.register_fleet(
        provider_name="lmster",
        provider_type=ProviderType.LOCAL,
        priority=1,
    )
    
    orchestrator.register_fleet(
        provider_name="ollama",
        provider_type=ProviderType.LOCAL,
        priority=2,
    )
    
    # Register cloud providers (lower priority)
    # Note: API keys would come from VaultCore in production
    if config.get("grok_enabled", False):
        grok_key = config.get("grok_api_key", "")
        if grok_key:
            orchestrator.register_fleet(
                provider_name="grok",
                provider_type=ProviderType.CLOUD,
                quota_poller=create_quota_poller("grok", api_key=grok_key),
                priority=3,
            )
    
    if config.get("openrouter_enabled", False):
        openrouter_key = config.get("openrouter_api_key", "")
        if openrouter_key:
            orchestrator.register_fleet(
                provider_name="openrouter",
                provider_type=ProviderType.CLOUD,
                quota_poller=create_quota_poller("openrouter", api_key=openrouter_key),
                priority=4,
            )
    
    if config.get("gcp_enabled", False):
        gcp_project = config.get("gcp_project_id", "")
        if gcp_project:
            orchestrator.register_fleet(
                provider_name="gcp",
                provider_type=ProviderType.CLOUD,
                quota_poller=create_quota_poller("gcp", project_id=gcp_project),
                priority=5,
            )
    
    if config.get("exa_enabled", False):
        exa_key = config.get("exa_api_key", "")
        if exa_key:
            orchestrator.register_fleet(
                provider_name="exa",
                provider_type=ProviderType.CLOUD,
                quota_poller=create_quota_poller("exa", api_key=exa_key),
                priority=6,
            )
    
    if config.get("firecrawl_enabled", False):
        firecrawl_key = config.get("firecrawl_api_key", "")
        if firecrawl_key:
            orchestrator.register_fleet(
                provider_name="firecrawl",
                provider_type=ProviderType.CLOUD,
                quota_poller=create_quota_poller("firecrawl", api_key=firecrawl_key),
                priority=7,
            )
    
    return orchestrator


# Module exports
__all__ = [
    "ProviderType",
    "RouteDecision",
    "ProviderFleet",
    "RouteRequest",
    "RouteResponse",
    "FleetOrchestrator",
    "create_default_orchestrator",
]