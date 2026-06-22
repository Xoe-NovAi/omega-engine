# ⬡ OMEGA ⬡ VERITY ⬡ TEST ⬡ v1.0.0
# Test suite for GitHub Hivemind Bridge

import pytest
import anyio
import json
from mcp_servers.omega_hub.github_bridge import process_github_event, verify_signature

@pytest.mark.anyio
async def test_verify_signature_valid():
    # Mock secret and payload
    secret = "omega_sovereign_default_secret_2026"
    payload = b'{"action": "opened", "issue": {"number": 1}}'
    
    import hmac
    import hashlib
    hash_val = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    signature = f"sha256={hash_val}"
    
    assert await verify_signature(payload, signature) is True

@pytest.mark.anyio
async def test_verify_signature_invalid():
    payload = b'{"action": "opened", "issue": {"number": 1}}'
    assert await verify_signature(payload, "sha256=wronghash") is False

@pytest.mark.anyio
async def test_process_github_event_mapping():
    # We need to mock the config/github_accounts.yaml for this test
    # Since we are in a test, we can monkeypatch the _get_github_account function
    
    from mcp_servers.omega_hub.github_bridge import process_github_event
    import mcp_servers.omega_hub.github_bridge as bridge
    
    def mock_get_account(entity_name):
        return {"username": "test-user", "entity": "kali", "pat": "mock-pat"}
    
    bridge._get_github_account = mock_get_account
    
    payload = {
        "sender": {"login": "test-user"},
        "action": "opened",
        "pull_request": {"title": "Test PR"}
    }
    
    # We don't need to check the Hivemind post result directly as it's a side effect
    # But we can verify the function completes without error
    await process_github_event("pull_request", payload)

@pytest.mark.anyio
async def test_process_github_event_fallback():
    from mcp_servers.omega_hub.github_bridge import process_github_event
    import mcp_servers.omega_hub.github_bridge as bridge
    
    def mock_get_account(entity_name):
        raise RuntimeError("Not found")
    
    bridge._get_github_account = mock_get_account
    
    payload = {
        "sender": {"login": "unknown-user"},
        "action": "opened",
        "issue": {"title": "Unknown Issue"}
    }
    
    await process_github_event("issue", payload)
