"""Tests for Omega Model Gateway."""

import pytest
from omega.oracle.model_gateway import ModelGateway
import os

@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to handle OMEGA_ENV pollution."""
    original_env = os.environ.get("OMEGA_ENV")
    yield monkeypatch
    if original_env:
        os.environ["OMEGA_ENV"] = original_env
    else:
        os.environ.pop("OMEGA_ENV", None)


def test_model_gateway_init():
    gateway = ModelGateway()
    assert gateway.models is not None


def test_get_model_path():
    gateway = ModelGateway()
    path = gateway.get_model_path("qwen3-1.7b")
    # May not exist on test machine, but should return the configured path
    assert path is not None
    assert path.endswith(".gguf")


def test_get_model_spec():
    gateway = ModelGateway()
    spec = gateway.get_model_spec("qwen3-1.7b-q6_k")
    assert spec is not None
    assert "size_gb" in spec
    assert spec["size_gb"] == 1.6


def test_unknown_model():
    gateway = ModelGateway()
    assert gateway.get_model_path("nonexistent-model") is None


def test_fallback_response():
    gateway = ModelGateway()
    response = gateway._fallback_response(
        "qwen3-1.7b-q6_k",
        "You are a test entity.",
        "Hello",
    )
    assert "no inference backend is running" in response


@pytest.mark.anyio
async def test_model_gateway_fallback_chain(monkeypatch):
    """Verify that ModelGateway falls back through the provider chain when others fail."""
    from unittest.mock import AsyncMock, MagicMock
    
    gateway = ModelGateway()
    
    # Create mock providers
    p1 = MagicMock()
    p1.name = "provider1"
    p1.is_available = AsyncMock(return_value=True)
    p1.generate = AsyncMock(side_effect=Exception("P1 Failed"))
    
    p2 = MagicMock()
    p2.name = "provider2"
    p2.is_available = AsyncMock(return_value=True)
    p2.generate = AsyncMock(side_effect=Exception("P2 Failed"))
    
    p3 = MagicMock()
    p3.name = "provider3"
    p3.is_available = AsyncMock(return_value=True)
    p3.generate = AsyncMock(return_value="Success from P3")
    
    gateway.providers = [p1, p2, p3]
    
    # We must mock the environment to avoid the mock_backend in test mode
    import os
    monkeypatch.setenv("OMEGA_ENV", "production") 
    
    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100
    )
    
    assert result[0] == "Success from P3"
    assert p1.generate.called
    assert p2.generate.called
    assert p3.generate.called
