"""
Integrations module for Omega Engine

Provides integrations with external API providers and services.
"""

from .grok_cli import (
    GrokCLIClient,
    GrokQuickPrompt,
    GrokFleetManager,
    GrokAccountConfig,
    QuotaInfo,
    GrokCLIError,
    GrokCLITimeoutError,
    GrokCLIQuotaExhaustedError,
    GrokProcessError,
    grok_prompt,
)

from .quota_pollers import (
    QuotaStatusLevel,
    QuotaSnapshot,
    QuotaPoller,
    GrokQuotaPoller,
    OpenRouterQuotaPoller,
    GCPQuotaPoller,
    ExaQuotaPoller,
    FirecrawlQuotaPoller,
    create_quota_poller,
)

from .fleet_orchestrator import (
    ProviderType,
    RouteDecision,
    ProviderFleet,
    RouteRequest,
    RouteResponse,
    FleetOrchestrator,
    create_default_orchestrator,
)

__all__ = [
    # Grok CLI
    "GrokCLIClient",
    "GrokQuickPrompt",
    "GrokFleetManager",
    "GrokAccountConfig",
    "QuotaInfo",
    "GrokCLIError",
    "GrokCLITimeoutError",
    "GrokCLIQuotaExhaustedError",
    "GrokProcessError",
    "grok_prompt",
    
    # Quota Pollers
    "QuotaStatusLevel",
    "QuotaSnapshot",
    "QuotaPoller",
    "GrokQuotaPoller",
    "OpenRouterQuotaPoller",
    "GCPQuotaPoller",
    "ExaQuotaPoller",
    "FirecrawlQuotaPoller",
    "create_quota_poller",
    
    # Fleet Orchestrator
    "ProviderType",
    "RouteDecision",
    "ProviderFleet",
    "RouteRequest",
    "RouteResponse",
    "FleetOrchestrator",
    "create_default_orchestrator",
]