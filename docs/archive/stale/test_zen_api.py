import anyio
import httpx
import os
from omega.proxy_pool import get_healthy_proxy_url

async def main():
    api_key = os.getenv("OPENCODE_ZEN_API_KEY")
    if not api_key:
        print("OPENCODE_ZEN_API_KEY not set")
        return
    
    proxy_url = await get_healthy_proxy_url()
    print(f"Using proxy: {proxy_url}")
    
    url = "https://api.opencode.ai/zen/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek/deepseek-v4-flash",
        "messages": [{"role": "user", "content": "Ping"}]
    }
    
    try:
        async with httpx.AsyncClient(proxy=proxy_url) as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

anyio.run(main)
