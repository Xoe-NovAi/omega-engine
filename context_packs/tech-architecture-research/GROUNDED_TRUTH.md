# Grounded Truth — Verified 2026-08-08

## Python Environment
- Python 3.13.7 (requires >=3.12)
- Platform: Linux (Ubuntu)
- Package manager: pip in .venv/

## Installed Packages

| Package | Version | Status | Used In |
|---------|---------|--------|---------|
| anyio | 4.14.2 | ✅ Installed | Core async runtime |
| httpx | 0.28.1 | ✅ Installed | Upstream (stalled since 2024) |
| httpx2 | 2.5.0 | ✅ Installed | 6 files (4 aliased as httpx, 2 direct) |
| mcp | 1.28.1 | ✅ Installed | MCP SDK v1.x |
| fastmcp | 3.4.4 | ✅ Installed | Separate package (searxng server) |
| pydantic | 2.13.4 | ✅ Installed | Core validation |
| PyYAML | 6.0.3 | ✅ Installed | YAML parsing |
| sqlite-vec | 0.1.9 | ✅ Installed | Vector search extension |
| tenacity | 9.1.4 | ✅ Installed | 3 files (retry_policy.py, extractors.py, model_gateway.py) |
| pybreaker | 1.4.1 | ✅ Installed | Legacy breaker lib (not used by HealthMonitor) |
| structlog | — | ❌ Not installed | Candidate |
| prometheus_client | — | ❌ Not installed | Candidate |
| interlock-cb | — | ❌ Not installed | Candidate |
| stamina | — | ❌ Not installed | Candidate |
| honker | — | ❌ Not installed | Candidate |

## Circuit Breaker Inventory

| File | Class | Lines | Status |
|------|-------|-------|--------|
| src/omega/oracle/health_monitor.py | AsyncCircuitBreaker, CircuitState | 944 | CANONICAL |
| src/omega/oracle/search_circuit_breaker.py | SearchCircuitBreaker | 299 | DEPRECATED |
| src/omega/research/sandbox.py | ExperimentCircuitBreaker | ~50 | CLONE |
| src/omega/ingestion/ingestion_types.py | CircuitBreakerState | — | Duplicate enum |
| src/omega/council/models.py | CircuitBreakerState | — | Duplicate enum |

## MCP Import Sites (8 total)

| File | Import |
|------|--------|
| mcp_servers/omega_hub/server.py | from mcp.server.fastmcp import FastMCP, Context |
| mcp_servers/omega_hub/hub_tools/tools.py | from mcp.server.fastmcp import Context |
| mcp_servers/omega_hub/hub_tools/task_registry.py | from mcp.server.fastmcp import FastMCP |
| mcp_servers/omega_hub/github_tools.py | from mcp.server.fastmcp import Context |
| mcp_servers/firecrawl/server.py | from mcp.server.fastmcp import FastMCP |
| mcp_servers/searxng/server.py | from fastmcp.server.server import FastMCP |
| mcp_servers/omega_hub/mcp_client.py | from mcp import ClientSession + streamablehttp_client |
| mcp_servers/omega_hub/middleware.py | from mcp.types import CallToolResult, TextContent |

## Dead Code (Zero Imports)
- src/omega/coordination/miap.py (~631 lines)
- src/omega/memory/recall.py (786 lines)

## NOT Dead Code
- mcp_servers/omega_hub/hivemind_redis.py (113 lines) — imported in tools.py:3621,3645

## Redis Inventory (Verified 2026-08-08)

| File | `redis` refs | Notes |
|------|-------------|-------|
| src/omega/governance/budget_guard.py | 24 | Rate limiting (INCR/EXPIRE) |
| src/omega/workers/youtube_worker.py | 19 | Queue (LPUSH/BRPOP) |
| src/omega/ingestion/worker.py | 11 | Ingestion queue |
| mcp_servers/omega_hub/hivemind_redis.py | 9 | Pub/sub (NOTIFY/LISTEN) — exposed as MCP tools |
| src/omega/memory/providers.py | 6 | Memory cache |
| src/omega/memory_store.py | 4 | Memory cache |

**Total**: 6 files, ~73 Redis references. Paths moved since earlier drafts —
youtube_worker.py → `src/omega/workers/`, budget_guard.py → `src/omega/governance/`,
ingestion worker → `src/omega/ingestion/worker.py`.
