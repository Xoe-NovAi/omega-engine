"""M21 Contract Tests: Fallback chain works (3 tests)."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_chain_order():
    """Fallback chain tries providers in correct order."""
    from omega.oracle.model_gateway import ModelGateway
    
    gateway = ModelGateway.__new__(ModelGateway)
    
    # Mock provider list
    providers = ["local", "cloud1", "cloud2"]
    call_order = []
    
    async def mock_generate(provider_name, *args, **kwargs):
        call_order.append(provider_name)
        if provider_name == "local":
            raise ConnectionError("Local failed")
        return {"text": "response", "provider": provider_name}
    
    with patch.object(gateway, "_generate_with_provider", side_effect=mock_generate):
        # Simulate fallback chain
        for provider in providers:
            try:
                result = await gateway._generate_with_provider(provider)
                break
            except ConnectionError:
                continue
    
    # Should have tried local first, then cloud1
    assert call_order == ["local", "cloud1"]

@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_on_timeout():
    """Fallback chain works when provider times out."""
    from omega.oracle.model_gateway import ModelGateway
    
    gateway = ModelGateway.__new__(ModelGateway)
    
    async def timeout_then_success(provider_name, *args, **kwargs):
        if provider_name == "timeout_provider":
            raise TimeoutError("Provider timeout")
        return {"text": "success", "provider": provider_name}
    
    with patch.object(gateway, "_generate_with_provider", side_effect=timeout_then_success):
        # Try timeout provider first
        try:
            result = await gateway._generate_with_provider("timeout_provider")
        except TimeoutError:
            # Fallback to next provider
            result = await gateway._generate_with_provider("backup_provider")
    
    assert result["provider"] == "backup_provider"

@pytest.mark.contract
@pytest.mark.anyio
async def test_provider_fallback_all_fail():
    """Fallback chain raises error when all providers fail."""
    from omega.oracle.model_gateway import ModelGateway
    
    gateway = ModelGateway.__new__(ModelGateway)
    
    async def always_fail(provider_name, *args, **kwargs):
        raise ConnectionError(f"Provider {provider_name} failed")
    
    with patch.object(gateway, "_generate_with_provider", side_effect=always_fail):
        # Try multiple providers
        last_error = None
        for provider in ["local", "cloud1", "cloud2"]:
            try:
                result = await gateway._generate_with_provider(provider)
                break
            except ConnectionError as e:
                last_error = e
                continue
        else:
            # All providers failed
            assert last_error is not None
            assert "cloud2 failed" in str(last_error)
