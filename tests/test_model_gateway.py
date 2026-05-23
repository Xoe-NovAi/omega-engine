"""Tests for Omega Model Gateway."""

from omega.oracle.model_gateway import ModelGateway


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
