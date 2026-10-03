# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

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

# [DEL-1 4h] fleet_orchestrator default exports removed 2026-08-24 —
# zero importers verified (MaKaLi council S4). The file itself stays on
# disk until the Week-2 router collapse (its private RouteDecision would
# collide with the single-control-plane gate, S4(4h)->S5 edge).

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
]
