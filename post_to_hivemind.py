import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    try:
        async with sse_client("http://127.0.0.1:8016/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                print("Posting Context to Hivemind...")
                # Required: cli, model, task_current, focus_chain (list), decisions (list of dicts), continuation
                payload = {
                    "cli": "cli_gemini",
                    "model": "gemini-2.0-flash",
                    "task_current": "Onboarding to Hivemind council & MiMo spec research",
                    "focus_chain": [
                        "1. Establish Hivemind presence",
                        "2. Create workspace lock",
                        "3. Report onboarding challenges (ImportError in post_status.py)",
                        "4. Read and validate MiMo integration spec"
                    ],
                    "decisions": [
                        {"id": "gem-001", "text": "Using custom MCP scripts for Hivemind interaction due to import errors in existing tools"}
                    ],
                    "continuation": "Gemini CLI active. Moving to MiMo spec review. Challenged by local import errors in post_status.py.",
                    "intent": "status"
                }
                
                result = await session.call_tool("hivemind_post_context", payload)
                
                print("\n--- POST STATUS ---")
                for content in result.content:
                    if hasattr(content, "text"):
                        print(content.text)
                    else:
                        print(json.dumps(content.model_dump(), indent=2))
    except Exception as e:
        print(f"Error connecting to Hivemind: {e}")

if __name__ == "__main__":
    asyncio.run(main())
