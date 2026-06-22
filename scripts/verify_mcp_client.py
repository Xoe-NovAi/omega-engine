import anyio
import json
import logging
import sys
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')

async def test_searxng_mcp():
    print("Testing Sovereign MCP Client connection to SearXNG...")
    url = "http://127.0.0.1:8018/sse"
    
    try:
        async with SovereignMCPClient(url) as client:
            # 1. List tools
            tools = await client.list_tools()
            print(f"Connected! Available tools: {tools}")
            
            if "searxng_search" in tools:
                print("Calling searxng_search with simple query...")
                result = await client.call_tool("searxng_search", {"query": "test"})
                if result.is_error:
                    print(f"Tool call failed: {result.content}")
                else:
                    print("Success! Result content length:", len(result.content))
                    print("First result snippet:", result.content[0][:200] if result.content else "Empty")
            else:
                print("searxng_search tool not found!")
                
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    anyio.run(test_searxng_mcp)
