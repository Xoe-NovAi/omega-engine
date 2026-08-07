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
    
    assert result.text == "Success from P3"
    assert p1.generate.called
    assert p2.generate.called
    assert p3.generate.called


# ── T2.2 Tests: BSP-style pre-check uses provider.name, not model_name ──────


@pytest.mark.anyio
async def test_precheck_skips_open_circuit_by_provider_name(monkeypatch):
    """T2.2: _precheck_provider must check breaker by provider.name, not model_name.

    Before the fix, is_available(model_name) used _model_provider_map which often
    returned True (no mapping), so OPEN circuits were never culled. After the fix,
    the breaker is looked up directly by provider.name.
    """
    from unittest.mock import AsyncMock, MagicMock

    from omega.oracle.health_monitor import AsyncCircuitBreaker, HealthMonitor

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    # Create a health monitor with a breaker for "broken_provider"
    hm = HealthMonitor(providers={"broken_provider": {"type": "cloud"}})
    # Force the breaker OPEN by recording 5 failures (threshold default)
    for _ in range(5):
        await hm._breakers["broken_provider"]._on_failure()
    assert hm._breakers["broken_provider"].state.value == "open"

    gateway._health_monitor = hm
    gateway.providers = []

    p_open = MagicMock()
    p_open.name = "broken_provider"
    p_open.is_available = AsyncMock(return_value=True)
    p_open.generate = AsyncMock(return_value="should not reach here")

    result = await gateway._precheck_provider(p_open, "any-model-name")
    assert result is False, "OPEN circuit must be culled by precheck"
    assert not p_open.generate.called, "Provider.generate() must not be called when precheck fails"


@pytest.mark.anyio
async def test_precheck_allows_closed_circuit():
    """T2.2: CLOSED circuits must pass the precheck."""
    from unittest.mock import AsyncMock, MagicMock

    from omega.oracle.health_monitor import HealthMonitor

    gateway = ModelGateway()
    hm = HealthMonitor(providers={"healthy_provider": {"type": "cloud"}})
    gateway._health_monitor = hm

    p_healthy = MagicMock()
    p_healthy.name = "healthy_provider"
    p_healthy.is_available = AsyncMock(return_value=True)

    result = await gateway._precheck_provider(p_healthy, "any-model")
    assert result is True, "CLOSED circuit must pass precheck"


# ── T2.3 Tests: RemoteProvider None return must trip the breaker ────────────


@pytest.mark.anyio
async def test_none_response_trips_breaker(monkeypatch):
    """T2.3: When provider.generate() returns None, the breaker must be tripped.

    Before the fix, breaker.call() recorded a 'success' (no exception) for None
    returns, so the circuit never opened. After the fix, the else clause detects
    the None result and manually calls breaker._on_failure().
    """
    from unittest.mock import AsyncMock, MagicMock

    from omega.oracle.health_monitor import CircuitState, HealthMonitor

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    hm = HealthMonitor(providers={"silent_provider": {"type": "cloud"}})
    gateway._health_monitor = hm

    # Provider always returns None (e.g., RemoteProvider with exhausted retries)
    p_silent = MagicMock()
    p_silent.name = "silent_provider"
    p_silent.is_available = AsyncMock(return_value=True)
    p_silent.generate = AsyncMock(return_value=None)

    # Set the threshold to 2 for fast test
    hm._breakers["silent_provider"].failure_threshold = 2

    # First call: should record failure, breaker still CLOSED
    gateway.providers = [p_silent]
    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
    )
    # Provider returned nothing → fallback response
    assert result.is_cloud is False, "None response should return fallback (success=False)"
    breaker = hm._breakers["silent_provider"]
    assert breaker.failure_count == 1, f"First None response should record 1 failure, got {breaker.failure_count}"
    assert breaker.state == CircuitState.CLOSED, "One failure should not open the circuit yet"

    # Second call: threshold reached, breaker should trip
    result2 = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
    )
    breaker = hm._breakers["silent_provider"]
    assert breaker.failure_count >= 2, f"Second None response should reach threshold, got {breaker.failure_count}"
    assert breaker.state == CircuitState.OPEN, (
        f"After {breaker.failure_count} failures (threshold=2), breaker must be OPEN, "
        f"got {breaker.state.value}"
    )


@pytest.mark.anyio
async def test_successful_response_keeps_breaker_closed(monkeypatch):
    """T2.3: Real responses must NOT trip the breaker (regression check)."""
    from unittest.mock import AsyncMock, MagicMock

    from omega.oracle.health_monitor import CircuitState, HealthMonitor

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    hm = HealthMonitor(providers={"good_provider": {"type": "cloud"}})
    gateway._health_monitor = hm

    p_good = MagicMock()
    p_good.name = "good_provider"
    p_good.is_available = AsyncMock(return_value=True)
    p_good.generate = AsyncMock(return_value="Real response from provider")

    gateway.providers = [p_good]

    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
    )
    
    assert result.text == "Real response from provider"
    assert result.is_cloud is False  # not cloud
    breaker = hm._breakers["good_provider"]
    assert breaker.failure_count == 0, "Successful response must not count as failure"
    assert breaker.state == CircuitState.CLOSED, "Successful response must keep circuit CLOSED"


@pytest.mark.anyio
async def test_exception_still_trips_breaker(monkeypatch):
    """T2.3: Exceptions (not just None) must continue to trip the breaker.

    This is a regression check — the original code already handled exceptions
    via the except clause + breaker.call()'s internal _on_failure.
    """
    from unittest.mock import AsyncMock, MagicMock

    from omega.oracle.health_monitor import CircuitState, HealthMonitor

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    hm = HealthMonitor(providers={"flaky_provider": {"type": "cloud"}})
    gateway._health_monitor = hm
    hm._breakers["flaky_provider"].failure_threshold = 2

    p_flaky = MagicMock()
    p_flaky.name = "flaky_provider"
    p_flaky.is_available = AsyncMock(return_value=True)
    p_flaky.generate = AsyncMock(side_effect=ConnectionError("network down"))

    gateway.providers = [p_flaky]

    # First failure
    await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
    )
    breaker = hm._breakers["flaky_provider"]
    assert breaker.failure_count == 1

    # Second failure → circuit should open
    await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
    )
    breaker = hm._breakers["flaky_provider"]
    assert breaker.state == CircuitState.OPEN, (
        f"Circuit must be OPEN after 2 ConnectionError failures, got {breaker.state.value}"
    )

@pytest.mark.anyio
async def test_all_providers_fail_falls_to_mock(monkeypatch):
    """Verify that if all providers in the chain fail, the ModelGateway returns the fallback response."""
    from unittest.mock import AsyncMock, MagicMock
    
    gateway = ModelGateway()
    
    # Create mock providers that all fail
    p1 = MagicMock()
    p1.name = "provider1"
    p1.is_available = AsyncMock(return_value=True)
    p1.generate = AsyncMock(side_effect=Exception("P1 Failed"))
    
    p2 = MagicMock()
    p2.name = "provider2"
    p2.is_available = AsyncMock(return_value=True)
    p2.generate = AsyncMock(side_effect=Exception("P2 Failed"))
    
    gateway.providers = [p1, p2]
    
    # Set to production to avoid the automatic mock_backend in test mode
    import os
    monkeypatch.setenv("OMEGA_ENV", "production")
    
    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100
    )
    
    # Should return the fallback response
    assert "no inference backend is running" in result.text
    assert p1.generate.called
    assert p2.generate.called


# ── M21/M22 Contract Tests: GenerateResult ──────────────────────────────


@pytest.mark.anyio
async def test_generate_result_success_has_latency(monkeypatch):
    """M22: Success path GenerateResult must have real latency_ms > 0."""
    from unittest.mock import AsyncMock, MagicMock

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    mock_provider = MagicMock()
    mock_provider.name = "test_provider"
    mock_provider.is_available = AsyncMock(return_value=True)
    mock_provider.generate = AsyncMock(return_value="Success response")

    gateway.providers = [mock_provider]

    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
        trace_id="contract-test-trace-001",
    )

    assert isinstance(result.latency_ms, float), "latency_ms must be a float"
    assert result.latency_ms > 0, "Latency must be > 0 on success path"


@pytest.mark.anyio
async def test_generate_result_success_has_model_used(monkeypatch):
    """M22: Success path GenerateResult must have model_used populated."""
    from unittest.mock import AsyncMock, MagicMock

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    mock_provider = MagicMock()
    mock_provider.name = "test_provider"
    mock_provider.is_available = AsyncMock(return_value=True)
    mock_provider.generate = AsyncMock(return_value="Success response")

    gateway.providers = [mock_provider]

    result = await gateway.generate(
        model_name="test-model",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
        trace_id="contract-test-trace-002",
    )

    assert result.model_used == "test-model", "model_used must match the requested model"


@pytest.mark.anyio
async def test_generate_result_fallback_has_model_used(monkeypatch):
    """M22: Fallback path should still report the model name."""
    from unittest.mock import AsyncMock, MagicMock

    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")

    # All providers fail — triggers fallback path
    p = MagicMock()
    p.name = "failing_provider"
    p.is_available = AsyncMock(return_value=True)
    p.generate = AsyncMock(side_effect=Exception("Failure"))

    gateway.providers = [p]

    result = await gateway.generate(
        model_name="fallback-model-test",
        system_prompt="sys",
        user_query="query",
        temperature=0.7,
        max_tokens=100,
        trace_id="contract-test-trace-003",
    )

    # Fallback should still report the model that was requested
    assert result.model_used == "fallback-model-test"
    assert result.provider_name == "fallback"

@pytest.mark.anyio
async def test_sovereign_sampling_overrides(monkeypatch):
    """Verify that Gemma 4 31B triggers sampling overrides (logit_bias, repetition_penalty)."""
    from unittest.mock import AsyncMock, MagicMock
    
    gateway = ModelGateway()
    monkeypatch.setenv("OMEGA_ENV", "production")
    
    mock_provider = MagicMock()
    mock_provider.name = "test_provider"
    mock_provider.is_available = AsyncMock(return_value=True)
    mock_provider.generate = AsyncMock(return_value="Success response")
    
    gateway.providers = [mock_provider]
    
    # Use the target model name
    model_name = "gemma-4-31b-it"
    
    result = await gateway.generate(
        model_name=model_name,
        system_prompt="sys",
        user_query="query",
        temperature=0.1, # Should be overridden to 0.8
        max_tokens=100,
    )
    
    # Verify that the provider's generate was called with the overrides
    # (provider.generate is invoked with all-keyword args in generate())
    args, kwargs = mock_provider.generate.call_args

    # Check temperature override — code clamps to max(temperature, 0.85)
    assert kwargs["temperature"] == 0.85
    # Check repetition penalty override — code clamps to max(penalty, 1.2)
    assert kwargs["repetition_penalty"] == 1.2
    # Check logit_bias is present as keyword argument
    assert "logit_bias" in kwargs
    assert isinstance(kwargs["logit_bias"], dict)
    assert len(kwargs["logit_bias"]) > 0

