# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""OpenCode MCP Client Adapter — Uses SovereignMCPClient to call local omega-hub tools"""

from typing import Optional
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient, MCPToolResult


class OpenCodeMCPClient:
    """Calls local MCP Hub tools through the MCP protocol using SovereignMCPClient."""

    def __init__(self, mcp_endpoint: str = "http://127.0.0.1:8016/mcp"):
        self.endpoint = mcp_endpoint
        self._client: Optional[SovereignMCPClient] = None

    async def _get_client(self) -> SovereignMCPClient:
        if self._client is None:
            self._client = SovereignMCPClient(self.endpoint)
            await self._client.__aenter__()
        return self._client

    async def close(self):
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None

    async def oracle_talk(self, query: str) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("oracle_talk", {"query": query})
        return result.content[0] if result.content else "{}"

    async def library_web_search(self, query: str, limit: int = 5) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool(
            "library_web_search", {"query": query, "limit": limit}
        )
        return result.content[0] if result.content else "{}"

    async def webfetch(self, url: str) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("webfetch", {"url": url})
        return result.content[0] if result.content else ""

    async def searxng_search(self, query: str, limit: int = 5) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool(
            "searxng_search", {"query": query, "limit": limit}
        )
        return result.content[0] if result.content else "{}"


class OpenCodePlatformClients:
    """PlatformClients implementation using OpenCodeMCPClient."""

    def __init__(self, mcp_endpoint: str = "http://127.0.0.1:8016/mcp"):
        self.mcp_client = OpenCodeMCPClient(mcp_endpoint)

    class Oracle:
        def __init__(self, mcp_client: OpenCodeMCPClient):
            self.mcp_client = mcp_client

        async def talk(self, prompt: str) -> str:
            return await self.mcp_client.oracle_talk(prompt)

    class Search:
        def __init__(self, mcp_client: OpenCodeMCPClient):
            self.mcp_client = mcp_client

        async def search(self, query: str, limit: int = 5) -> str:
            return await self.mcp_client.library_web_search(query, limit)

        async def fetch(self, url: str) -> str:
            return await self.mcp_client.webfetch(url)

        async def searxng(self, query: str, limit: int = 5) -> str:
            return await self.mcp_client.searxng_search(query, limit)

    def get_oracle(self) -> Oracle:
        return self.Oracle(self.mcp_client)

    def get_search(self) -> Search:
        return self.Search(self.mcp_client)

    async def close(self):
        await self.mcp_client.close()
