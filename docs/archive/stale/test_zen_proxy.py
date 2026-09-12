# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import anyio
import httpx
from omega.proxy_pool import get_pool

async def main():
    pool = get_pool()
    print(f"Current port: {pool.current_port}")
    
    # Rotate to get a fresh IP
    print("Rotating proxy node...")
    success = await pool.rotate()
    print(f"Rotation success: {success}")
    
    proxy_url = await pool.get_proxy_url()
    print(f"New proxy URL: {proxy_url}")
    
    try:
        async with httpx.AsyncClient(proxy=proxy_url) as client:
            resp = await client.get("https://api.ipify.org", timeout=10.0)
            print(f"New Proxy IP: {resp.text}")
    except Exception as e:
        print(f"Verification failed: {e}")

anyio.run(main)
