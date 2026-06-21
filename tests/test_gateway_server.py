import pytest
from fastapi.testclient import TestClient
from src.omega.gateway.server import app, OmegaGateway
from unittest.mock import AsyncMock, patch
from omega.oracle.model_gateway import GenerateResult

client = TestClient(app)

def test_gateway_health():
    # The server doesn't have a /health endpoint, but we can test if it's alive
    response = client.post("/v1/chat/completions", json={
        "model": "test-model",
        "messages": [{"role": "user", "content": "hello"}]
    })
    # It should return 503 or 500 if providers aren't mocked, but not 404
    assert response.status_code != 404

@pytest.mark.asyncio
async def test_chat_completions_success():
    with patch("src.omega.gateway.server.ModelGateway.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = GenerateResult(text="Hello from Omega!", provider_name="mock", is_cloud=False)
        
        response = client.post("/v1/chat/completions", json={
            "model": "gemma-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["choices"][0]["message"]["content"] == "Hello from Omega!"
        assert data["model"] == "gemma-4"
        assert "usage" in data

@pytest.mark.asyncio
async def test_chat_completions_no_provider():
    with patch("src.omega.gateway.server.ModelGateway.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = GenerateResult(text="", provider_name="mock", is_cloud=False)
        
        response = client.post("/v1/chat/completions", json={
            "model": "nonexistent",
            "messages": [{"role": "user", "content": "hello"}]
        })
        
        assert response.status_code == 503
        assert "No available providers" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_completions_rate_limit():
    with patch("src.omega.gateway.server.ModelGateway.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("Rate limit exceeded (429)")
        
        response = client.post("/v1/chat/completions", json={
            "model": "rate-limited-model",
            "messages": [{"role": "user", "content": "hello"}]
        })
        
        assert response.status_code == 429
        assert "Rate limit reached" in response.json()["detail"]

def test_backoff_state():
    from src.omega.gateway.server import BackoffState
    import time
    
    state = BackoffState()
    assert not state.is_in_backoff()
    
    state.record_failure()
    assert state.fail_count == 1
    assert state.is_in_backoff()
    assert state.current_backoff == 120
    
    state.record_success()
    assert state.fail_count == 0
    assert not state.is_in_backoff()
    assert state.current_backoff == 60
