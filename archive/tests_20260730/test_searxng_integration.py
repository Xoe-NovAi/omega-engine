# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from omega.workers.background_researcher.searxng_client import SearXNGClient
from mcp_servers.searxng.server import searxng_search

# --- Client Tests ---

@pytest.mark.asyncio
async def test_client_search_success():
    client = SearXNGClient()
    mock_response = {
        "results": [
            {"title": "Result 1", "url": "http://1.com", "content": "Content 1", "engine": "google", "score": 1.0},
            {"title": "Result 2", "url": "http://2.com", "content": "Content 2", "engine": "google", "score": 0.9},
        ]
    }
    
    with patch("httpx2.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response
        mock_post.return_value = mock_resp
    
        results = await client.search(query="test", max_results=1)
    
        assert len(results) == 1
        assert results[0]["title"] == "Result 1"
        assert mock_post.called

@pytest.mark.asyncio
async def test_client_search_empty():
    client = SearXNGClient()
    mock_response = {"results": []}
    
    with patch("httpx2.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response
        mock_post.return_value = mock_resp
    
        results = await client.search(query="test")
        assert results == []

@pytest.mark.asyncio
async def test_client_search_text():
    client = SearXNGClient()
    mock_response = {
        "results": [{"url": "http://1.com"}, {"url": "http://2.com"}]
    }
    
    with patch("httpx2.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response
        mock_post.return_value = mock_resp
    
        urls = await client.search_text(query="test")
        assert urls == ["http://1.com", "http://2.com"]

@pytest.mark.asyncio
async def test_client_health():
    client = SearXNGClient()
    with patch("httpx2.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        assert await client.health() is True
        
        mock_resp.status_code = 500
        assert await client.health() is False

# --- MCP Server Tests ---

@pytest.mark.asyncio
async def test_mcp_search_success():
    # Mocking the environment and the httpx client
    with patch("mcp_servers.searxng.server.SEARXNG_URL", "http://mock-searxng"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [{"title": "M1", "url": "u1", "content": "c1", "engine": "e1", "score": 1.0}]
        }
        mock_post.return_value = mock_resp

        result = await searxng_search(query="test", limit=5)

        assert "Search: test" in result
        assert "[1] M1" in result
        assert "URL: u1" in result

@pytest.mark.asyncio
async def test_mcp_search_error():
    with patch("mcp_servers.searxng.server.SEARXNG_URL", "http://mock-searxng"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:

        from httpx import HTTPStatusError, Response
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = HTTPStatusError("Error", request=AsyncMock(), response=Response(500))
        mock_post.return_value = mock_resp

        result = await searxng_search(query="test")
        assert "Error" in result

