import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("http://127.0.0.1:8016/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # List tools to confirm connectivity
            tools = await session.list_tools()
            print(f"Connected to Hub. Available tools: {[t.name for t in tools.tools]}")
            
            # Call discovery for the orchestration research
            query = (
                "Technical patterns and benchmarks for: "
                "1. Cognitive Loop Kernel (CLK). "
                "2. Lok - Spawn/Debate topologies. "
                "3. AdaptOrch - Task-adaptive topology routing."
            )
            print(f"Calling library_discovery_research for: {query}")
            
            # This tool might take a while, so we increase timeout if possible, 
            # though call_tool doesn't have a direct timeout param in the SDK (it's handled by anyio)
            result = await session.call_tool("library_discovery_research", {"query": query})
            
            print("\n--- RESEARCH SUMMARY FROM SOVEREIGN MCP ---")
            # The result is a CallToolResult
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(json.dumps(content.model_dump(), indent=2))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
