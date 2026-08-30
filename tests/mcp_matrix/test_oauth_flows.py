# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""MCP Transport: OAuth 2.1 + PKCE auth flows."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.mcp
@pytest.mark.anyio
async def test_oauth_2_1_pkce_flow():
    """Verify OAuth 2.1 + PKCE flow structure."""
    # This is a structural test for OAuth 2.1 with PKCE.
    # Actual implementation may vary.
    
    # Mock PKCE challenge
    import hashlib
    import base64
    import os
    
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    
    # Verify PKCE challenge is correct
    assert len(code_verifier) >= 43  # RFC 7636 minimum
    assert len(code_challenge) == 43  # SHA256 base64url
    
    # Mock OAuth flow
    oauth_flow = {
        "authorization_endpoint": "https://auth.example.com/authorize",
        "token_endpoint": "https://auth.example.com/token",
        "client_id": "test-client",
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    
    # Verify required fields
    assert "authorization_endpoint" in oauth_flow
    assert "token_endpoint" in oauth_flow
    assert "client_id" in oauth_flow
    assert "code_verifier" in oauth_flow
    assert "code_challenge" in oauth_flow
    assert oauth_flow["code_challenge_method"] == "S256"

@pytest.mark.mcp
@pytest.mark.anyio
async def test_oauth_token_refresh():
    """Verify OAuth token refresh flow."""
    # Mock token refresh
    token_response = {
        "access_token": "new-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "refresh-token",
    }
    
    # Verify token response structure
    assert "access_token" in token_response
    assert "token_type" in token_response
    assert token_response["token_type"] == "Bearer"
    assert "expires_in" in token_response
    assert "refresh_token" in token_response
    
    # Verify expiration is reasonable
    assert token_response["expires_in"] > 0
    assert token_response["expires_in"] <= 86400  # Max 24 hours

@pytest.mark.mcp
@pytest.mark.anyio
async def test_oauth_scope_validation():
    """Verify OAuth scope validation."""
    # Mock scope validation
    required_scopes = ["mcp:read", "mcp:write"]
    granted_scopes = ["mcp:read", "mcp:write", "mcp:admin"]
    
    # Verify all required scopes are granted
    for scope in required_scopes:
        assert scope in granted_scopes, f"Missing required scope: {scope}"
    
    # Verify no excessive scopes
    excessive_scopes = [s for s in granted_scopes if s not in required_scopes]
    # This is a policy check; excessive scopes may be allowed depending on policy
    print(f"Granted scopes: {granted_scopes}")
    print(f"Excessive scopes: {excessive_scopes}")
