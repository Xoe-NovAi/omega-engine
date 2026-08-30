# MCP v2 / FastMCP Migration Schedule — 2026-07-30

**AP Token**: `AP-MCP-V2-MIGRATE-SCHED-20260730-v1.0.0`  
**Owner**: grok_cli (schedule) · **Executor later**: cline or dedicated spike  
**Status**: **SCHEDULED** — containment pin applied; full migrate **not** started

---

## Containment (DONE 2026-07-30)

| Item | State |
|------|-------|
| pyproject pin | `mcp>=1.28.1,<2` |
| venv | **1.28.1** |
| Rule | Do **not** `pip install mcp` unpinned (pulls v2.x since 2026-07-28) |
| Gate CG-01 | Mechanical pass while major &lt; 2 |

---

## Why migrate

- MCP Python SDK **v2.0.0** stable 2026-07-28: FastMCP→MCPServer, stateless protocol, import path breaks
- Omega Hub: `from mcp.server.fastmcp import FastMCP` (`mcp_servers/omega_hub/server.py`)
- Firecrawl: same SDK path
- `src/omega/mcp_runtime.py` imports `mcp.server.fastmcp.server.StreamableHTTPASGIApp`
- SearXNG **already** uses external `from fastmcp.server.server import FastMCP` — in-repo precedent

---

## Recommended path

**Migrate Hub (+ Firecrawl) to external FastMCP library** (gofastmcp / `fastmcp` package), not a raw mid-flight SDK v2 rewrite.

### Phases (effort ~4–8h total)

| Phase | Work | Effort | Owner hint |
|-------|------|--------|------------|
| **M0** | Pin + document (this file) | ✅ done | grok |
| **M1** | Spike: inventory Hub FastMCP/Context/transport APIs vs SearXNG | 1–2h | Cline 1M |
| **M2** | CI/gate: fail if `mcp` major ≥ 2 until `MIGRATE_MCP_V2=1` | 30m | Grok/Cline |
| **M3** | Hub cutover on `:8016` (SSE + Streamable HTTP smoke) | 2–3h | Cline |
| **M4** | Firecrawl `:8015` same pattern | 1h | Cline |
| **M5** | Clients (`mcp_client.py`, OpenCode/Cline MCP config) | 1h | Cline |
| **M6** | OMEGA_ENGINE row + drop temporary pin notes; optional allow mcp≥2 | 30m | Grok |

**Do not start M3 until** doc sanity (UO-4) is stable enough that agents are not thrashing — pin holds the fort.

---

## Non-goals now

- Full un-overengineering Phase 1 in the same PR as Hub migrate
- Implementing `make sovereignty`
- Breaking live `:8016` without smoke rollback plan

---

## Rollback

Keep `mcp>=1.28.1,<2` until M3 green. If Hub fails smoke, revert import path + redeploy prior Hub process.

*OMEGA · MCP · schedule only · 2026-07-30*
