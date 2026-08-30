# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import anyio
import httpx
from omega.proxy_pool import get_healthy_proxy_url

async def main():
    print("Fetching healthy proxy URL...")
    proxy_url = await get_healthy_proxy_url()
    if not proxy_url:
        print("No healthy proxy found!")
        return
    
    print(f"Using proxy: {proxy_url}")
    try:
        async with httpx.AsyncClient(proxy=proxy_url) as client:
            resp = await client.get("https://api.ipify.org", timeout=10.0)
            print(f"Proxy IP: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

anyio.run(main)
