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
                
                # [seam-fix 2026-09-28 carmack] `hivemind_post_context` is not
                # in the registered MCP surface. The Hivemind consolidation
                # (NES→EIS) folded it into `hivemind_awareness(action="post")`.
                # Verified against the live surface: 54 registered tools, of
                # which the Hivemind set is exactly
                #   hivemind_awareness, hivemind_get_metrics,
                #   hivemind_handoff, hivemind_lock
                # — no `hivemind_post_context`. Calling it returned a
                # "Unknown tool" error from the server, caught by the blanket
                # `except` below and reported as "Error connecting to
                # Hivemind", which misattributed a dead tool name to a
                # connectivity problem.
                #
                # `tag` is not a field of the unified tool; it is carried in
                # `task_current` so the experiment label is not silently lost.
                tag = payload.pop("tag", None)
                if tag:
                    payload["task_current"] = f"{payload.get('task_current', '')} [tag={tag}]"

                result = await session.call_tool("hivemind_awareness", {
                    "action": "post",
                    **payload,
                })

                print("\n--- POST STATUS ---")
                for content in result.content:
                    if hasattr(content, "text"):
                        print(content.text)
                    else:
                        print(json.dumps(content.model_dump(), indent=2))
    except Exception as e:
        # M23: distinguish a dead tool name from a transport failure. The old
        # message claimed connectivity for every failure mode.
        print(f"Error posting to Hivemind: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())