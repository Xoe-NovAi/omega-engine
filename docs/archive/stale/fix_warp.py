# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import anyio
from omega.proxy_pool import get_pool

async def main():
    pool = get_pool()
    for port in pool.ports:
        print(f"Recycling node on port {port}...")
        # We need to find the node_id (index + 1)
        node_id = pool.ports.index(port) + 1
        # We call the rotate logic or just trigger the script
        import subprocess
        subprocess.run(["/usr/local/bin/spawn_warp_node.sh", str(node_id), "recycle"])
    print("All nodes triggered for recycle. Waiting 10s for tunnels to stabilize...")
    await anyio.sleep(10)

anyio.run(main)
