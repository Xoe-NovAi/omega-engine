# 🔱 Omega Engine — Cline Status Tracker
# ⬡ OMEGA ⬡ ARTISAN ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_status ⬡ PHASE-I
#
# AP-OMEGA-STATUS-v1.0.0
# Last Updated: 2026-05-27

## §1 Current Session: MCP Hydration

**Entity**: HERMES (Code Integration — The Artisan)
**Channel**: Cline (VSCodium, Claude Sonnet 4.6)
**Model**: deepseek-v4-flash → Claude Sonnet
**Phase**: Phase 1 — MCP Infrastructure Hardening

## §2 What Was Accomplished

| # | Task | Status |
|---|------|--------|
| 1 | Cleaned Cline MCP config — removed `omega-research` (oneshot worker, not SSE) | ✅ |
| 2 | Removed `omega-stats` from config (tools consolidated in omega-hub) | ✅ |
| 3 | Removed `firecrawl` command MCP (VSCodium doesn't support `type: command`) | ✅ |
| 4 | Env-varized EXA API key in Cline config (was hardcoded plaintext) | ✅ |
| 5 | Fixed Exa MCP type back to `http` (was incorrectly changed to `sse`) | ✅ |
| 6 | Synced `config/mcp_servers.json` with Cline config (single source of truth) | ✅ |
| 7 | Stopped 5 problematic services (stats, belial, iris, postgres, qdrant) | ✅ |
| 8 | Verified omega-hub healthy on :8016 — returns `{"status":"healthy"}` | ✅ |
| 9 | Verified VSCodium schema error resolved (no `type: command` entries) | ✅ |

## §3 MCP Connection Status

| MCP Server | Type | Port | Status | Notes |
|------------|------|------|--------|-------|
| **omega-hub** | SSE | :8016 | ✅ Healthy | 28 tools across 6 domains |
| **exa** | HTTP | external | ✅ Fixed (was sse→restored to http) | Web search + fetch |

## §4 Running Services (7 essential)

| Service | Type | Status |
|---------|------|--------|
| omega-hub.service | SSE MCP server | ✅ active |
| omega-caddy.service | Reverse proxy | ✅ active |
| omega-infra-pod.service | Pod orchestrator | ✅ active |
| omega-redis.service | Cache | ✅ active |
| omega-bridge-elevenlabs.service | Voice bridge | ✅ active |
| omega-mcp-watchdog.service | Health monitor | ✅ active |
| omega-hub.socket | Socket activation | ✅ active |

## §5 Stopped Services

| Service | Reason | Can Restart? |
|---------|--------|--------------|
| omega-stats | Redundant (tools in hub) | ❌ No — archived |
| omega-belial | OCI container error (FUSE filesystem) | 🔧 Needs podman storage fix |
| omega-iris | Container crash (missing image) | 🔧 Needs image rebuild |
| omega-postgres | Failing to start | 🔧 Needs config fix |
| omega-qdrant | Failing to start | 🔧 Needs config fix |

## §6 Current Issues

| # | Issue | Priority | Status |
|---|-------|----------|--------|
| 1 | Qdrant/Postgres offline — needed for vector store + soul persistence | P0 | 🔧 Investigation done — OCI permission errors on FUSE mount |
| 2 | Redis not exposed outside pod — needed for cross-agent pub/sub | P1 | ⏳ Needs pod port addition |
| 3 | No SearXNG in infra compose — needed for sovereign web search | P2 | 📝 Client code exists, just needs compose entry |
| 4 | No Firecrawl in Cline (VSCodium doesn't support `type: command`) | P2 | ⏳ Needs SSE wrapper |
| 5 | lmster (:1234) not running — primary local inference | P3 | 📝 Separate service task |
| 6 | .env has 6 hardcoded API keys | P3 | 📝 Needs env-var standardisation |

## §7 Key References

- `.clinerules` — Project rules and IWAD architecture
- `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` — Architecture reference
- `docs/team/COMMUNICATION_HUB.md` — Fleet communication protocol
- `config/mcp_servers.json` — MCP config (single source of truth)
- `data/handoff/handoff_cline_to_opencode_overseer.md` — Previous handoff