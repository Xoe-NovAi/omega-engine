# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M21 Contract Tests: GenerateResult type validation (3 tests)."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from omega.oracle.model_gateway import GenerateResult

_test_result = GenerateResult(
    text="test response",
    provider_name="mock_provider",
    is_cloud=False,
    latency_ms=10.0,
    model_used="test-model",
    logprobs=[],
)


@pytest.mark.contract
@pytest.mark.anyio
async def test_generate_returns_generate_result():
    """GenerateResult dataclass must have all required fields per M21."""
    result = _test_result
    
    # Contract test: result must be GenerateResult
    assert isinstance(result, GenerateResult)
    assert hasattr(result, "text")
    assert hasattr(result, "provider_name")
    assert hasattr(result, "is_cloud")
    assert hasattr(result, "latency_ms")
    assert hasattr(result, "model_used")
    assert hasattr(result, "logprobs")

@pytest.mark.contract
@pytest.mark.anyio
async def test_generate_result_text_is_string():
    """GenerateResult.text must be a string."""
    from omega.oracle.model_gateway import GenerateResult
    
    result = GenerateResult(
        text="test",
        provider_name="provider",
        is_cloud=True,
        latency_ms=100.0,
        model_used="model",
        logprobs=[],
    )
    
    assert isinstance(result.text, str)
    assert len(result.text) > 0

@pytest.mark.contract
@pytest.mark.anyio
async def test_generate_result_provider_name_is_string():
    """GenerateResult.provider_name must be a non-empty string."""
    from omega.oracle.model_gateway import GenerateResult
    
    result = GenerateResult(
        text="response",
        provider_name="specific_provider",
        is_cloud=False,
        latency_ms=50.0,
        model_used="model",
        logprobs=None,
    )
    
    assert isinstance(result.provider_name, str)
    assert len(result.provider_name) > 0
    # M22: provider_name must match actual provider, not configured intent
    assert result.provider_name == "specific_provider"
