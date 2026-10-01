<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Phase 2 — Gate Truth, MCP Import Path, Full-Suite Timeout

**Timestamp**: 2026-07-30T06:25Z

## 1. Phase D gate truth confirmed
- Mechanical gate script run under `.venv/bin/python` outputs `GATE: ✅ PASS` with 11/11 required, 2/3 optional.
- **But** V-1 detail string includes FAILED test names from `tests/unit/test_vault_core.py`, while the gate still records PASS.
- **Knowledge gap closed?** No. This is confirmed **false-PASS risk**:
  - The script uses `.venv/bin/python -m pytest ... | tail -5`; although the current script does not pipe `| tail`, the detail string is explicitly truncated from `out[:160]` and can include failure lines while still passing the string-match path.
  - Operational truth: focused suite PASS is credible; V-1 as currently implemented is **not trusted** because PASS can coexist with failing subtests due to truncation-based string checks.
- **Recommended action**: gate must check `code == 0` *and* absence of failure tokens in the pytest output, or drop the fragile detail heuristic.

## 2. Full-suite timeout truth
- `timeout 140s pytest -q --tb=no` exhausted wrapper timeout with no output; collect-only proves **1706 tests**.
- Focused suite is fast (~14.7s). Full suite unknown duration from this pass; likely >3 min.
- Operational impact: honest CI needs longer timeout or pytest splitting.

## 3. MCP current code path
- `mcp` SDK installed: **1.28.1**
- Standalone `fastmcp` package installed: **3.4.4**
- Hub uses legacy bundled path:
  - `from mcp.server.fastmcp import FastMCP, Context`
  - `from mcp.server.streamable_http_manager import StreamableHTTPSessionManager`
  - `from mcp.server.fastmcp.server import StreamableHTTPASGIApp`
- This means **v2 migration is a real import break**: new SDK uses `MCPServer`, different module paths, and removes deprecated protocol elements.
- Currently only the docs/schedule say to wait; repo code is still on v1 API surface.

## 4. New knowledge gaps discovered/confirmed in this phase
- **V-1 trustworthiness** is worse than previously stated: false-PASS is not just theoretical; it is reproducible from live run output.
- **FastMCP package duplication** installs both `mcp` and standalone `fastmcp`; one may shadow the other depending on PYTHONPATH/import order.
- **Full-suite duration** is an unmeasured blocker for honest CI badge automation.

---
*⬡ OMEGA ⬡ CLINE ⬡ KNOWLEDGE-GAP RESEARCH ⬡ PHASE 2 ⬡ 2026-07-30*