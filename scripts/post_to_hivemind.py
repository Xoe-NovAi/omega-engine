# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    try:
        async with sse_client("http://127.0.0.1:8016/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                print("Posting kq5-godot Day 0 announcement to Hivemind...")
                payload = {
                    "channel": "opencode",
                    "entity": "john_carmack",
                    "model": "minimax/minimax-m3:free",
                    "task_current": "kq5-godot integration Day 0 complete — experiment lab operational",
                    "focus_chain": [
                        "1. Symlink created: data/experiments/kq5-godot -> /media/arcana-novai/omega_library/games/kq5-godot",
                        "2. Godot 4.7.2 headless check passes (Graham debug loaded)",
                        "3. EXPERIMENT_STATUS.md created locally (28 mandates, tiered)",
                        "4. Cline-KQV entity registered locally (symlinks to gnosis)",
                        "5. data/experiments/ gitignored — local-only research lab"
                    ],
                    "decisions": [
                        "Symlink approach (not bind-mount) for local reproducibility",
                        "Tiered mandates: Tier 0 (safety always), Tier 1 (adapted), Tier 2 (waived)",
                        "Cline-KQV as research persona (not governance entity)",
                        "VNR as perception provider in experiment layer (not Core interface)"
                    ],
                    "continuation": "kq5-godot experiment lab operational. Day 1-2: Cline-KQV coordination, validation evidence, protocol design. Hub restored — Hivemind operational.",
                    "intent": "status",
                    "tag": "experiment:kq5-godot"
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