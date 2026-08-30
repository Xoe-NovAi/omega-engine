# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import anyio
import httpx
from omega.proxy_pool import get_healthy_proxy_url

async def main():
    url = "https://api.ipify.org"
    
    print("--- IP OBSERVATION TEST ---")
    
    # 1. Direct Connection
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5.0)
            print(f"Direct IP: {resp.text}")
    except Exception as e:
        print(f"Direct request failed: {e}")
    
    # 2. WARP Proxy Connection
    proxy_url = await get_healthy_proxy_url()
    if not proxy_url:
        print("No healthy proxy found!")
        return
    
    print(f"Using Proxy: {proxy_url}")
    try:
        async with httpx.AsyncClient(proxy=proxy_url) as client:
            resp = await client.get(url, timeout=5.0)
            print(f"Proxy IP:  {resp.text}")
    except Exception as e:
        print(f"Proxy request failed: {e}")

anyio.run(main)
