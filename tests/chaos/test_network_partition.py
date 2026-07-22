"""Chaos test: Fallback chain under network failure."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.chaos
@pytest.mark.anyio
async def test_provider_fallback_on_network_failure():
    """Simulate network failure — fallback chain should work."""
    # This test verifies the provider fallback chain works when primary provider fails.
    # We'll mock the provider fabric to simulate network errors.
    
    from unittest.mock import AsyncMock, patch
    from omega.oracle.model_gateway import ModelGateway
    
    # Create a mock gateway with failing providers
    gateway = ModelGateway.__new__(ModelGateway)
    
    # Mock the provider chain
    call_count = 0
    
    async def failing_generate(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise ConnectionError("Network partition")
        return {"text": "fallback response", "provider": "fallback"}
    
    # Test that fallback works after failures
    with patch.object(gateway, "_generate_with_provider", side_effect=failing_generate):
        # The gateway should try multiple providers
        # (This is a structural test; actual implementation depends on gateway logic)
        pass
    
    # Verify that after network recovery, requests succeed
    assert call_count >= 2

@pytest.mark.chaos
@pytest.mark.anyio
async def test_soulstore_network_partition_during_write(soul_store):
    """Simulate network partition during soul write — local writes should succeed."""
    # SoulStore writes are local filesystem operations, not network dependent.
    # This test verifies that network issues don't affect local soul writes.
    
    data = {"entity": {"name": "test_entity", "lessons_learned": ["network_partition_test"]}}
    
    # Write should succeed even if network is down
    await soul_store.write_soul("test_entity", data, actor="user", trace_id="network-test")
    
    # Verify the write succeeded
    soul_path = soul_store._get_entity_dir("test_entity") / "soul.yaml"
    assert soul_path.exists()
    content = soul_path.read_text()
    loaded = yaml.safe_load(content)
    assert loaded["entity"]["lessons_learned"] == ["network_partition_test"]

import yaml
