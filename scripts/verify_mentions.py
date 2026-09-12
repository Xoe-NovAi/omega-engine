# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import anyio
from omega.oracle.oracle import Oracle

async def main():
    oracle = Oracle()
    await oracle.bootstrap()
    
    test_cases = [
        ("@sysAdmin how do I deploy a container?", "SysAdmin"),
        ("Hello @sysAdmin, can you help me with the server?", "SysAdmin"),
        ("@fakeAgent hello", "Iris"), # fallback to default
        ("Can you help me @SYSADMIN?", "SysAdmin"),
    ]
    
    for query, expected in test_cases:
        resp = await oracle.talk(query)
        print(f"Query: {query} -> Entity: {resp.entity} (Expected: {expected})")
        assert resp.entity == expected or (expected == "Iris" and resp.entity != "fakeAgent")

anyio.run(main)
