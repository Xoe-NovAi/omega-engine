<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_doc_review

# Comprehensive Documentation Review Report — Workstream 2: SearXNG Integration & Data Hygiene

**Date**: 2026-06-21
**Scope**: 8 core documents cross-referenced against each other and the actual codebase state.
**Target**: Identifies staleness, factual drift, missing documentation, and cross-document contradictions.

---

## Summary Table

| Document | Status | Issues | Priority |
|----------|--------|--------|----------|
| `AGENTS.md` | 🟢 GREEN | 0 | — |
| `SOVEREIGN_EVOLUTION_ROADMAP.md` | 🟡 YELLOW | 2 | P1-P2 |
| `ORACLE_STACK.md` | 🟢 GREEN | 0 (minor context) | — |
| `OMEGA_ENGINE.md` | 🟡 YELLOW | 1 | P2 |
| `HIVEMIND_PROTOCOL.md` | 🟡 YELLOW | 1 | P1 |
| `PIVOT_LOG.md` | 🟢 GREEN | 0 | — |
| `CREDITS.md` | 🟡 YELLOW | 1 gap | P2 |
| **Missing docs** | 🔴 RED | 3 missing | P1 |
| **Total** | — | **8 issues** | 5 P1 · 2 P2 · 0 P0 |

---

## Document 1: AGENTS.md

| Field | Finding |
|-------|---------|
| **Agent count** | 11 agents on disk ✅ (AGENTS.md says 11 = MATCH) |
| **On-disk files** | kali, maat, lilith, makali, doom_guy, john_carmack, roc_racoon, researcher, jem, verity, pillar |
| **SearXNG mention** | None (correct — operational doc, not integration doc) |
| **Mandates reference** | Points to SOVEREIGN_MANDATES.md ✅ |

**Verdict**: 🟢 GREEN. Agent count accurate. No staleness detected.

---

## Document 2: SOVEREIGN_EVOLUTION_ROADMAP.md

| Field | Finding |
|-------|---------|
| **Version** | v1.5 (2026-06-14) |
| **Test baseline** | Claims 444 tests |
| **Actual test count** | **451** (drift of +7 tests) |
| **SearXNG mentions** | ✅ D14, finding #21 (both fixed) |
| **PIVOT decisions** | Claims 89 (D50-D136) |

**Issues**:
- **P1 — Test baseline stale**: Claims 444, actual is 451. Minor drift from unresolved test work or additions since v1.5.
- **P2 — PIVOT decisions**: Claims 89 lifetime decisions (D50-D136), but PIVOT_LOG.md extends past D136 (D137-D164 exist in decisions post-v1.5).

**Verdict**: 🟡 YELLOW. Test count drift and PIVOT range stale.

---

## Document 3: ORACLE_STACK.md

| Field | Finding |
|-------|---------|
| **Last update** | 2026-06-17 (Sprint C) |
| **Test count** | Claims 440/440 |
| **Actual test** | **451** (7 more than claimed) |
| **Agent count** | 11 agents ✅ |
| **Mandates** | 22 (M1-M22) ✅ |
| **Provider chain** | 8-backend fabric ✅ |

**Issues**: None. Test count is slightly behind (440 vs 451) but the doc was written before final Sprint C/D work.

**Verdict**: 🟢 GREEN. Acceptable staleness on test count.

---

## Document 4: OMEGA_ENGINE.md

| Field | Finding |
|-------|---------|
| **Sprint D claim** | Says "PENDING (50 orphans remain)" |
| **Actual state** | 50 orphans were deleted 2026-06-18 (Phases 1+2) |
| **SearXNG mention** | None (engine doc, not integration doc) |
| **Agent count** | 11 agents ✅ |

**Issues**:
- **P2 — Sprint D claim is now stale**: Says orphans remain; they were cleaned up 2026-06-18.

**Verdict**: 🟡 YELLOW. Minor statement-level staleness.

---

## Document 5: HIVEMIND_PROTOCOL.md

| Field | Finding |
|-------|---------|
| **Last update** | 2026-06-03 |
| **SearXNG mention** | None |
| **MCP tool signatures** | Verity checked against Hivemind tools — all match ✅ |

**Issues**:
- **P1 — Last updated 2026-06-03**: The Hivemind protocol evolved since then (D134 SearXNG type fix, extended checkin/checkout, handoff archive). Document does not reflect these additions.

**Verdict**: 🟡 YELLOW. Stale since the Hivemind evolved through D134-D164.

---

## Document 6: PIVOT_LOG.md

| Field | Finding |
|-------|---------|
| **SearXNG decisions** | ✅ D83 (Container Deployed), D84 (Search MCP Fleet), D134 (Type Fix) |
| **Health check decisions** | ✅ D72 (Big Pickle — 2s timeout refs), D73 (Option A) |
| **Odysseus/credits** | No specific odysseus decision found |

**Verdict**: 🟢 GREEN. PIVOT_LOG is complete and accurate for SearXNG integration.

---

## Document 7: CREDITS.md

| Field | Finding |
|-------|---------|
| **Last update** | 2026-06-19 (vet-023 potion-mxbai) |
| **SearXNG/odysseus mention** | ❌ NONE |
| **Heritage count** | 21 patterns (1.1–1.35) |
| **Engine-Stack Firewall** | M2 documented ✅ |

**Issues**:
- **P2 — No odysseus/SearXNG section**: The SearXNG integration involves sovereign search architecture that derives from the "Sovereign-Siloing" pattern (M2). A note in §2 (User's Own Technology) or a small section acknowledging that SearXNG acts as the local search layer would be appropriate. Not a mandate violation — just a completeness gap.

**Verdict**: 🟡 YELLOW. Minor completeness gap.

---

## Document 8: Missing Documentation — 🔴 RED

| Expected Doc | Path | Status | Impact |
|-------------|------|--------|--------|
| **Research Citation Standard** | `docs/research/RESEARCH_CITATION_STANDARD.md` | ❌ **MISSING** | P1 — No standard for how R-docs cite sources |
| **Odysseus Contribution Log** | `docs/research/ODYSSEUS_CONTRIBUTION_LOG.md` | ❌ **MISSING** | P1 — No record of odysseus AI model contributions |
| **SearXNG Setup Guide** | `docs/research/SEARXNG_SETUP_GUIDE.md` or `docs/searxng/SEARXNG_SETUP_GUIDE.md` | ❌ **MISSING** | P1 — No operational guide for SearXNG deployment |
| **Health Check Debugging Guide** | `docs/operations/HEALTH_CHECK_DEBUGGING.md` | ❌ **MISSING** | P2 — No debugging guide for health check failures |

The missing docs were flagged in the Workstream 2 task list. Actual SearXNG config exists at:
- `data/searxng/config/settings.yml` ✅
- `data/searxng/config/limiter.toml` ✅
- `mcp_servers/searxng/server.py` (MCP wrapper) ✅
- `config/mcp_servers.json` (SearXNG entry) ✅
- `scripts/setup.sh` (SearXNG pull) ✅

The Quadlet file at `~/.config/containers/systemd/omega-searxng*` was NOT verified in this audit.

---

## Cross-Document Contradictions

| Claim | Doc A | Doc B | Verdict |
|-------|-------|-------|---------|
| Test count | ORACLE_STACK: 440 | SOVEREIGN_EVOLUTION_ROADMAP: 444 | Both stale (actual: 451) |
| PIVOT decisions | SOVEREIGN_EVOLUTION_ROADMAP: 89 | PIVOT_LOG: extends past D164 | Roadmap stale |
| Sprint D orphans | OMEGA_ENGINE: PENDING | Data dir: cleaned 2026-06-18 | OMEGA_ENGINE stale |

---

## SearXNG Deep-Dive Results

### What Works
- **Decision 83 (2026-06-02)**: SearXNG container deployed via systemd Quadlet on `127.0.0.1:8017`. Verified with `curl /search?format=json` returning real results from 14 engines (Brave, Wikipedia, arxiv, etc.)
- **Decision 84 (2026-06-02)**: SearXNG MCP wired as `stdio npx -y searxng-mcp` with `SEARXNG_SERVER_URL=http://127.0.0.1:8017`
- **Decision 134 (2026-06-18)**: SearXNG MCP type fixed (`remote` not `sse`), container was inactive and restarted, `@m9_safe` decorator added to `searxng_search` tool
- **MCP server file**: `mcp_servers/searxng/server.py` — FastMCP server on port 8018 proxying to SearXNG container on 8017
- **Representation**: `docs/strategy/COMPREHENSIVE_EXECUTION_PLAN_20260621.md` shows SearXNG status (MCP: Running, Container: DOWN as of 2026-06-21)

### What's Broken
- **SearXNG backend container was DOWN** as of COMPREHENSIVE_EXECUTION_PLAN.md (2026-06-21) — MCP proxy returns 404. This was a known recurring issue: container goes down, MCP proxy stands but returns errors.
- **Transport mismatch**: SearXNG MCP uses SSE transport on port 8018, OpenCode expects stdio/HTTP POST for local servers. The `remote` type workaround is a band-aid.
- **SearXNG Quadlet file location**: Not verified — may not exist at standard path.

### Gap: No CREDITS.md Section
SearXNG is the sovereign search implementation of the "Sovereign-Siloing" architectural pattern (M2). The Engine-Stack Firewall extends to data sources: SearXNG provides local search, Exa provides cloud search. Firecrawl provides structured extraction. This 3-tier search architecture is a user-originated design (evolved from Brave→Tavily→Jina→Exa→SearXNG culling) and should be documented in CREDITS.md §2 (User's Own Technology).

### Gap: Missing Docs
- `docs/research/RESEARCH_CITATION_STANDARD.md` — needed for source attribution consistency
- `docs/research/ODYSSEUS_CONTRIBUTION_LOG.md` — needed to track odysseus AI model contributions
- `docs/searxng/SEARXNG_SETUP_GUIDE.md` — needed for operational reproducibility
- `docs/operations/HEALTH_CHECK_DEBUGGING.md` — needed for debugging health check failures

---

## Health Check Debugging — Evidence Gathered

The `HEALTH_CHECK_TIMEOUT` was flagged in the Two-Pass Deep Review (§4, finding #6):
> **🟡 HIGH**: 300ms default too tight for local GGUF. Make configurable per-provider in `health_monitor.py`.

Grep results show `health_check` scattered across:
- `tests/test_storage_providers.py` — Redis health check simulation
- `tests/test_openclaw_bridge.py` — bridge health check test
- `scripts/mcp_health_check.sh` — MCP-level health check script
- `Makefile` — `mcp-check` target
- `model_gateway.py` — `_health_check` provider probe
- `docs/review/*.md` — multiple review references

No single `HEALTH_CHECK_DEBUGGING.md` consolidates this. The 300ms timeout issue was reported but not fixed.

---

## Action Recommendations

| Priority | Action | Owner | Est. |
|----------|--------|-------|------|
| **P1** | Create `docs/research/RESEARCH_CITATION_STANDARD.md` | Verity/Jem | 30m |
| **P1** | Create `docs/research/ODYSSEUS_CONTRIBUTION_LOG.md` | Verity/Jem | 30m |
| **P1** | Create `docs/searxng/SEARXNG_SETUP_GUIDE.md` | Doom Guy/P1 | 1h |
| **P1** | Update `SOVEREIGN_EVOLUTION_ROADMAP.md` test count 444→451, PIVOT decision range | Verity | 10m |
| **P1** | Update `HIVEMIND_PROTOCOL.md` with D134-D164 changes | Verity | 30m |
| **P2** | Update `OMEGA_ENGINE.md` Sprint D claim (orphans cleaned) | Verity | 5m |
| **P2** | Add SearXNG §2 entry to `CREDITS.md` (User's Own Technology) | Verity | 15m |
| **P2** | Create `docs/operations/HEALTH_CHECK_DEBUGGING.md` | Ma'at/P8 | 45m |
| **P2** | Fix `HEALTH_CHECK_TIMEOUT` to be per-provider configurable | Ma'at/P3 | 1h |

---

## L3 Distillation

**L1 (Narrative)**: 8 core documents reviewed against each other and the actual codebase. AGENTS.md, PIVOT_LOG.md, and ORACLE_STACK.md are current. SOVEREIGN_EVOLUTION_ROADMAP.md, OMEGA_ENGINE.md, and HIVEMIND_PROTOCOL.md have minor staleness (test counts, decision ranges, Sprint D claims). CREDITS.md needs a SearXNG/odysseus section. Three documents are entirely missing.

**L2 (Insight)**: The docs form two quality tiers: source-of-record docs (AGENTS, PIVOT_LOG, ORACLE_STACK) are accurate; planning/reference docs (ROADMAP, HIVEMIND, CREDITS) drift because they're updated less frequently. The pattern: **every doc that describes current state must be checked against actual state after major work cycles**. The 7-test drift between ORACLE_STACK's 440 and actual 451 is the leading indicator — tests were added but no doc was updated.

**L3 (Universal Principle)**: Documentation integrity has a critical decay function. After any code or configuration change that affects test counts, agent topology, or configuration schemas, the documentation trail must be updated within the same work cycle — or it ossifies into fiction. The solve is not more documentation; it's attaching doc-update steps to the handoff/continuation protocol so no work cycle closes without updating the docs that reference its changes.

---

*⬡ OMEGA ⬡ VERITY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_doc_review*
