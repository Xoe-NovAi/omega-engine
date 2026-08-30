# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M21 Contract Tests: Fallback chain works (3 tests) - Updated for CascadeRouter.
SKIPPED: CascadeRouter class was never implemented (vaporware).
The fallback chain logic exists in TriageRouter and ModelGateway but with different APIs.
Re-enable when CascadeRouter is implemented or rewrite tests for actual router.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.skip(
    reason="CascadeRouter not implemented - tests reference vaporware module omega.oracle.cascade_router"
)


class MockProvider:
    """Mock provider object with name attribute."""
    def __init__(self, name):
        self.name = name


@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_chain_order():
    """CascadeRouter selects providers in correct order with fallback chain."""
    from omega.oracle.cascade_router import CascadeRouter
    from omega.oracle.health_monitor import HealthMonitor
    from omega.oracle.quota_tracker import QuotaTracker
    from omega.oracle.token_estimator import TokenEstimator
    
    # Create a mock gateway
    gateway = MagicMock()
    gateway.get_available_providers = AsyncMock(return_value=[
        MockProvider("local"), 
        MockProvider("cloud1"), 
        MockProvider("cloud2")
    ])
    
    # Create cascade router with mocked dependencies
    health_monitor = HealthMonitor()
    quota_tracker = QuotaTracker()
    token_estimator = TokenEstimator()
    
    router = CascadeRouter(
        model_gateway=gateway,
        health_monitor=health_monitor,
        quota_tracker=quota_tracker,
        token_estimator=token_estimator,
    )
    
    # Mock the scoring to return predictable order
    # We'll patch _score_provider to return scores that ensure local > cloud1 > cloud2
    original_score = router._score_provider
    
    async def mock_score_provider(provider_name, model_name, prompt_tokens, completion_tokens, total_tokens):
        scores = {
            "local": 100.0,
            "cloud1": 80.0,
            "cloud2": 60.0,
        }
        from omega.oracle.cascade_router import ProviderScore
        return ProviderScore(
            provider=provider_name,
            total_score=scores.get(provider_name, 50.0),
            cost_score=scores.get(provider_name, 50.0),
            quality_score=scores.get(provider_name, 50.0),
            latency_score=scores.get(provider_name, 50.0),
            quota_score=100.0,
            health_score=100.0,
        )
    
    router._score_provider = mock_score_provider
    
    # Route a request
    decision = await router.route_request(
        model_name="test-model",
        system_prompt="System",
        user_prompt="User query",
        temperature=0.7,
        max_tokens=1024,
    )
    
    # Should select local as primary, with cloud1 and cloud2 as fallback
    assert decision.selected_provider == "local"
    assert decision.fallback_chain == ["cloud1", "cloud2"]


@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_on_timeout():
    """CascadeRouter handles quota-exhausted providers in fallback chain."""
    from omega.oracle.cascade_router import CascadeRouter
    from omega.oracle.health_monitor import HealthMonitor
    from omega.oracle.quota_tracker import QuotaTracker
    from omega.oracle.token_estimator import TokenEstimator
    
    # Create a mock gateway
    gateway = MagicMock()
    gateway.get_available_providers = AsyncMock(return_value=[
        MockProvider("timeout_provider"), 
        MockProvider("backup_provider")
    ])
    
    # Create cascade router with mocked dependencies
    health_monitor = HealthMonitor()
    quota_tracker = QuotaTracker()
    token_estimator = TokenEstimator()
    
    router = CascadeRouter(
        model_gateway=gateway,
        health_monitor=health_monitor,
        quota_tracker=quota_tracker,
        token_estimator=token_estimator,
    )
    
    # Mock scoring to prefer timeout_provider first, then backup_provider
    async def mock_score_provider(provider_name, model_name, prompt_tokens, completion_tokens, total_tokens):
        scores = {
            "timeout_provider": 100.0,
            "backup_provider": 80.0,
        }
        from omega.oracle.cascade_router import ProviderScore
        return ProviderScore(
            provider=provider_name,
            total_score=scores.get(provider_name, 50.0),
            cost_score=scores.get(provider_name, 50.0),
            quality_score=scores.get(provider_name, 50.0),
            latency_score=scores.get(provider_name, 50.0),
            quota_score=100.0,
            health_score=100.0,
        )
    
    router._score_provider = mock_score_provider
    
    # Mark timeout_provider as quota exhausted
    quota_tracker._quotas["timeout_provider"] = MagicMock()
    quota_tracker._quotas["timeout_provider"].is_exhausted = True
    
    # Route a request - should skip timeout_provider and select backup_provider
    decision = await router.route_request(
        model_name="test-model",
        system_prompt="System",
        user_prompt="User query",
        temperature=0.7,
        max_tokens=1024,
    )
    
    # Should select backup_provider since timeout_provider is quota exhausted
    assert decision.selected_provider == "backup_provider"


@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_all_fail():
    """CascadeRouter uses highest-scoring provider when all are quota exhausted."""
    from omega.oracle.cascade_router import CascadeRouter
    from omega.oracle.health_monitor import HealthMonitor
    from omega.oracle.quota_tracker import QuotaTracker
    from omega.oracle.token_estimator import TokenEstimator
    
    # Create a mock gateway
    gateway = MagicMock()
    gateway.get_available_providers = AsyncMock(return_value=[
        MockProvider("local"), 
        MockProvider("cloud1"), 
        MockProvider("cloud2")
    ])
    
    # Create cascade router with mocked dependencies
    health_monitor = HealthMonitor()
    quota_tracker = QuotaTracker()
    token_estimator = TokenEstimator()
    
    router = CascadeRouter(
        model_gateway=gateway,
        health_monitor=health_monitor,
        quota_tracker=quota_tracker,
        token_estimator=token_estimator,
    )
    
    # Mock scoring
    async def mock_score_provider(provider_name, model_name, prompt_tokens, completion_tokens, total_tokens):
        scores = {
            "local": 100.0,
            "cloud1": 80.0,
            "cloud2": 60.0,
        }
        from omega.oracle.cascade_router import ProviderScore
        return ProviderScore(
            provider=provider_name,
            total_score=scores.get(provider_name, 50.0),
            cost_score=scores.get(provider_name, 50.0),
            quality_score=scores.get(provider_name, 50.0),
            latency_score=scores.get(provider_name, 50.0),
            quota_score=100.0,
            health_score=100.0,
        )
    
    router._score_provider = mock_score_provider
    
    # Mark all providers as quota exhausted
    for provider in ["local", "cloud1", "cloud2"]:
        quota_tracker._quotas[provider] = MagicMock()
        quota_tracker._quotas[provider].is_exhausted = True
    
    # Route a request - should still return a provider (highest scoring) 
    # even when all are quota exhausted (with warning)
    decision = await router.route_request(
        model_name="test-model",
        system_prompt="System",
        user_prompt="User query",
        temperature=0.7,
        max_tokens=1024,
    )
    
    # Should still select the highest-scoring provider (local) despite quota exhaustion
    assert decision.selected_provider == "local"
    assert decision.fallback_chain == ["cloud1", "cloud2"]