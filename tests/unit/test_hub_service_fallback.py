"""Regression test for omega-hub state.py get_service fallback resolution.

Validates that get_service correctly retrieves module-level eager services
(oracle, registry, hierarchy, inbox, curator) without failing due to __import__
returning top-level packages.

Mandate: M21 (Gate Integrity), M9 (Error Integrity)
Decision: D-592
"""
import pytest
import anyio
import mcp_servers.omega_hub.state as hub_state


@pytest.mark.anyio
async def test_get_service_eager_fallback(monkeypatch):
    """Verify that get_service retrieves eager service objects via fallback."""
    # Mock an eager service on state module
    class DummyOracle:
        pass

    dummy = DummyOracle()
    monkeypatch.setattr(hub_state, "oracle", dummy)

    resolved = await hub_state.get_service("oracle")
    assert resolved is dummy
    assert isinstance(resolved, DummyOracle)


@pytest.mark.anyio
async def test_get_service_unknown_raises():
    """Verify that get_service raises RuntimeError for non-existent service."""
    with pytest.raises(RuntimeError, match="is not a lazy-loadable service or is not initialized"):
        await hub_state.get_service("non_existent_service_xyz")
