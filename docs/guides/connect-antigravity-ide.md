<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# 🔱 How-to: Connect Antigravity IDE to the Omega Hub
**AP Token**: `AP-GUIDE-ANTIGRAVITY-MCP-v1.0.0`
⬡ OMEGA ⬡ MAKALI ⬡ opencode ⬡ trc_post_debut ⬡ STANDARD

**Date**: 2026-10-12
**Purpose**: Connect Antigravity IDE (Seat #10, strategy-only) to the local Omega Hub MCP server.
**Tags**: how-to, antigravity, hub, mcp, seat-10
**Cross-references**: `mcp_servers/omega_hub/server.py`, `docs/guides/how-to-debug-hub.md`, `docs/architecture/omega-hub-exposure.md`, `.agents/rules/antigravity-seat.md`

---

## 1. Start the Hub

From the repo root, using the project venv:

```bash
cd ~/Documents/Xoe-NovAi/omega-engine
.venv/bin/python mcp_servers/omega_hub/server.py
```

SSE-transport variant (only if your MCP client cannot use Streamable HTTP):

```bash
OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 .venv/bin/python mcp_servers/omega_hub/server.py
```

Verify it is alive:

```bash
curl -s http://127.0.0.1:8016/health
# Expected: {"status":"healthy","version":"1.6.0-alpha"}
```

If this fails, see `docs/guides/how-to-debug-hub.md` before touching any IDE settings.

---

## 2. Connect Antigravity IDE

Add the Hub as an MCP server in Antigravity IDE:

- **Primary (Streamable HTTP):** `http://127.0.0.1:8016/mcp`
- **Legacy SSE fallback:** `http://127.0.0.1:8016/sse`

Example MCP server entry:

```json
{
  "omega-hub": {
    "type": "remote",
    "url": "http://127.0.0.1:8016/mcp"
  }
}
```

If Antigravity only speaks SSE, use the `/sse` URL and start the Hub with the SSE-transport variant above.

---

## 3. Verify the connection

Inside Antigravity, list MCP tools and confirm the Omega Hub tools appear (hivemind awareness/handoff, oracle, library, research, stats). If tools are missing:

1. Re-run the `/health` check above.
2. Confirm no second Hub is running on `:8016` (D-619: never spawn duplicate MCP servers on an active port).
3. See `docs/guides/how-to-debug-hub.md`.

---

## 4. Seat #10 boundary

Antigravity is a **strategy-only** seat: reviews, audits, stress-tests, and verifies gates. It does **not** author git commits or core runtime implementations. OpenCode remains the commit and implementation authority.

*⬡ OMEGA ⬡ MAKALI ⬡ GUIDE-ANTIGRAVITY-MCP ⬡ 2026-10-12 ⬡*