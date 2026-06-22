import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_simple():
    url = "http://127.0.0.1:8018/sse"
    print(f"Connecting to {url}...")
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session initialized.")
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")
            
            if "searxng_search" in [t.name for t in tools.tools]:
                print("Calling searxng_search...")
                res = await session.call_tool("searxng_search", {"query": "test"})
                print(f"Result: {res.content}")

if __name__ == "__main__":
    asyncio.run(test_simple())
