# 🔱 OMEGA ENGINE — Comprehensive Execution Plan & Strategy
# ⬡ OMEGA ⬡ CLINE ⬡ deepseek-v4-flash ⬡ trc_comprehensive_strategy ⬡ STRATEGY
**AP Token**: AP-COMPREHENSIVE-STRATEGY-v1.0.0
**Date**: 2026-06-21
**Author**: Cline CLI (DeepSeek V4 Flash, 1M context)
**Status**: ACTIVE - Ready for Execution
**Baseline**: 451 tests (493 functions) - 63 MCP tools - 22 Sovereign Mandates - 11-agent fleet

---

## §0 Executive Summary

This document is the single source of truth for the **Omega Engine restoration, documentation refresh, and strategic handoff** campaign. It integrates findings from a full-context deep hydration: codebase scanning, MCP server forensics, Hivemind awareness checks, and cross-referencing all strategic documents against actual filesystem state.

**Critical Discovery**: The documentation does not match reality in **11 verified dimensions** (test counts, service states, MCP configurations, resolved gaps). This plan closes every delta.

## §1 Current State — Ground Truth (Verified 2026-06-21)

### 1.1 Engine Metrics

| Metric | Documented | Actual | Delta |
|--------|-----------|--------|-------|
| Test count | 440/444 | **451** (493 functions) | +11 |
| Source files | 96 | ~104 | +8 |
| Sovereign Mandates | 22 (M1-M22) | 22 (M1-M22) | Match |
| Agent fleet | 11 | 11 | Match |
| Omega Hub tools | 40 | **63** | +23 |
| Hivemind tools listed | 6 | **13+** | +7 |

### 1.2 Running Services (Actual Infrastructure State)

| Service | Status | Port | Notes |
|---------|--------|------|-------|
| Omega Hub | Running 47h | :8016 | 63 tools, 140MB RAM, healthy |
| SearXNG MCP | Running | :8018 | Systemd service active |
| SearXNG container | DOWN | :8017 | Backend not running - 404 proxy |
| Omega Qdrant | Running 45h | :6333 | Vector store active |
| Omega Redis | Healthy | :6379 | Warm tier ready |
| Omega Postgres | Healthy | :5432 | Catalog |
| Omega Caddy | Unhealthy | :8088 | Needs investigation |
| GitHub MCP | Not deployed | N/A | Binary exists, container not running |
| Firecrawl | Not in Cline | N/A | In OpenCode configs only |
| Omega Bridge | Running | ElevenLabs | Voice bridge active |
| MCP Watchdog | Running | - | Health monitoring |

### 1.3 Resolved Gaps (Previously Flagged as Open)

| Gap | Status | Evidence |
|-----|--------|----------|
| D113 Engine-Stack Firewall | RESOLVED | PILLAR_SLOTS frozenset, IWAD-agnostic loading |
| S1.5a Firewall Restoration | RESOLVED | No hardcoded meanings in engine core |
| S1.5b Nomenclature | RESOLVED | Intuitive names, pillar_slot wired |
| M21 Gate Integrity | RESOLVED | 4 contract tests (test_contract_m21.py) |
| Dataset Collection | ENABLED | config/omega.yaml:39 |
| GitHub M8 Audit | PASSED | All 4 audit layers clean |
| GitHub Phase 2 Code | WRITTEN | All 5 files exist, needs deployment |

## §2 Phased Execution Plan

### Phase 0: IMMEDIATE FIREFIGHTING (30 min)

**Goal**: Restore core infrastructure connectivity.

| # | Task | Owner | Target | Verification |
|---|------|-------|--------|-------------|
| 0.1 | Start SearXNG container | Cline | SearXNG at :8017 | curl :8017/healthz -> 200 |
| 0.2 | Restore Cline MCP config | Cline | All MCPs in Cline settings | make mcp-check passes |
| 0.3 | Deploy GitHub MCP container | Cline | Docker container running | test_github_bridge.py passes |
| 0.4 | Diagnose Caddy unhealthy | Cline | Caddy healthy | podman logs omega-caddy |
| 0.5 | Sync global OpenCode config | Cline | Add searxng to config | Config complete |

### Phase 1: MCP RESTORATION & WIRING (1.5 hr)

| # | Task | Files | Verification |
|---|------|-------|-------------|
| 1.1 | Cline MCP config - all servers | cline_mcp_settings.json | make mcp-check passes |
| 1.2 | Project MCP config - add firecrawl | config/mcp_servers.json | Listed in config |
| 1.3 | Wire MCP Client into Hub | state.py, mcp_client.py | Hub connects to searxng |
| 1.4 | Add quota visibility tools | tools.py | 2 new MCP tools registered |
| 1.5 | Verify end-to-end | - | Every MCP server GREEN |

### Phase 2: .clinerules v5.0.0 (1 hr)

Key updates from v4.0.0:
- Test baseline: 315/315 -> 451/451
- Mandate count: 14 (M1-M14) -> 22 (M1-M22) v3.5.0
- Agent fleet: 14 agents -> 11 agents
- Models: minimax/m3 -> gemini-3.7-flash / deepseek-v4-flash (1M ctx)
- D113/S1.5: PENDING -> RESOLVED
- MCP servers: firecrawl/exa 401-broken -> ALL RESTORED
- Hivemind tools: 6 tools -> 13+ tools
- Sprint refs: Jun 2-4 -> Jun 21
- L3: Add Dataset Collection, Structural Invisibility, Self-Healing
- New: SovereignMCPClient, GitHub Integration, Quota Tools

### Phase 3: OMEGA_ENGINE.md v2.4.0 (1 hr)

Key updates:
- S5.1: Tests 440->451, D113->RESOLVED, Qdrant/Redis->Running
- S7: Remove D113/S1.5 blocker sections entirely
- S8: Move S1.5 items to completed
- S9: M21->RESOLVED, M10 cap: 14->11
- S11: Hivemind tools: 6->13+
- S10: Scorecard souls: 2/14->2/11
- S13: entity_registry D113 flag->Remove
- S6: Add PR Hardening, GitHub Integ, Sovereign Sight to sprint index

### Phase 4: Antigravity IDE Custom Instructions v3.1.0 (30 min)

Key updates:
- S3 M21: zero contract tests -> RESOLVED (4 exist)
- S5 PoolState: 3 phases -> 4 (add Quota Checker)
- NEW: Roc's SovereignGraphAdapter, GitHub Integ Ph3-4, Dataset Collection, MCP Client, Quota tools
- S6 Hydration: Add stale handoff review step

### Phase 5: SEARXNG RESTORATION (30 min)

1. Check Quadlet: ls ~/.config/containers/systemd/omega-searxng*
2. Start container: systemctl --user start or podman run
3. Verify: curl :8017/healthz -> 200
4. Verify MCP proxy: SearXNG MCP at :8018 routes through
5. Add to make mcp-check

### Phase 6: GITHUB MCP DEPLOYMENT (1 hr)

1. M8 audit DONE (docs/security/GITHUB_M8_AUDIT.md)
2. Create config/github_accounts.yaml with PATs
3. Start official server Docker container
4. Register in all MCP configs
5. Wire Hub wrapper routes in server.py
6. Finalize HMAC + retry queue
7. Run test_github_bridge.py

### Phase 7: KNOWLEDGE GAP DEEP DIVE (2 hr)

| Gap | Source | Investigation |
|-----|--------|---------------|
| Caddy unhealthy | podman ps | Check logs |
| Firecrawl binary | Command timed out | Verify installation |
| SearXNG Quadlet | Not in config/systemd/ | Check ~/.config/containers/systemd/ |
| Jem pipeline active? | Agent files exist | Test with research query |
| embeddinggemma-300m | Found by Roc, unregistered | Register in models.yaml |
| PoolState fully wired? | Code exists | Trace model_gateway.py calls |
| Entity count | Stale in docs | Audit data/entities/ |
| MCP Watchdog effective? | Service running | Test auto-restart |
| Firecrawl API key valid? | Hardcoded in wrapper | Test with firecrawl --status |

### Phase 8: COMPREHENSIVE ANTIGRAVITY HANDOFF (2 hr)

Replaces 4 stale packets: ho_4618926079f9, ho_09e936d70f8e, ho_a4e38a8d584c, ho_19131bab8b1f

Structure:
- Part A: Current State Briefing (~30%)
- Part B: Roc's Memory Architecture Integration (~20%)
- Part C: Strategic Priorities (~30%)
- Part D: Hydration & Logistics (~10%)
- Part E: Sovereign Debt Refresh (~10%)

### Phase 9: STALE HANDOFF ARCHIVAL (15 min)

Archive all 30 stale handoff packets from data/handoff/

## §3 Success Criteria

| Metric | Current | Target | Phase |
|--------|---------|--------|-------|
| MCP servers running | 3/6 | 6/6 | P0-P1 |
| Cline MCP tools available | 1/5 | 5/5 | P0 |
| All strategic docs current | 30% | 100% | P2-P4 |
| Stale handoffs archived | 30 stale | 0 stale | P9 |
| SearXNG search working | Broken | Working | P5 |
| GitHub MCP deployed | Not deployed | Deployed | P6 |
| Antigravity handoff live | 4 stale | 1 fresh | P8 |
| Quota visibility tools | Not built | Online | P1 |
| Knowledge gaps investigated | 0/10 | 10/10 | P7 |

## §4 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SearXNG container fails to start | Medium | High | Fall back to websearch built-in |
| GitHub PAT not configured | High | High | Document in Phase 0 |
| Caddy unhealthy is deeper issue | Medium | Medium | Isolate, not blocking MCP |
| Firecrawl API key expired | Medium | Medium | Check credits, rotate key |

---
*Omega Engine - Cline CLI - deepseek-v4-flash - Comprehensive Execution Plan v1.0.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
