<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 N4 Node Review Report
## Researcher Handoff Integration Analysis — Dev Roadmap Alignment
**Session**: `ses_4331b4d6f6af` · **Date**: 2026-08-23 · **Entity**: N4 bridge (maat)
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N4)
**Mandates**: M1, M2, M7, M13, M22, M25 (SOVEREIGN_MANDATES.md v3.8.0)

---

## Executive Summary

**Verdict: PROCEED WITH CONDITIONS**

The Researcher Handoff Integration Analysis (DR-4, DR-5, DR-10) accurately identifies three protocol alignment gaps that must be resolved before Wave 2/3 Node genesis. All three drift register items are **confirmed valid** with file:line evidence. The integration requires protocol version updates, registry reconciliation, and a minimal layering map.

---

## 1. DR-4: HIVEMIND_PROTOCOL v1.3.0 vs Current Session Systems

### 1.1 Protocol Version & Date Verification
**Status**: ✅ **CONFIRMED** `last_verified:2026-08-23`

- `docs/strategy/HIVEMIND_PROTOCOL.md` header: **AP Token**: `AP-HIVEMIND-PROTOCOL-v1.3.0`, **Last Updated**: 2026-06-25 (lines 3-5)
- Changelog §12 confirms v1.3.0 = 2026-06-25 (line 543)

### 1.2 Missing Node Paging Support
**Status**: ✅ **CONFIRMED — NO NODE PAGING**

- HIVEMIND_PROTOCOL.md has **no reference** to Node expert sessions, Node paging, or `NODE_EXPERT_SESSIONS_PLAN.md`
- NODE_EXPERT_SESSIONS_PLAN.md §2 defines page format (lines 47-51):
  ```
  task(task_id=<session_id>, subagent_type=<overseer-agent>,
       prompt="[NODE PAGE — from <agent> (<session_id>)]\n[Charter header: You are N_X <keeper>, <department>. Charter: this file §4.\n<question/task ≤500 words>")
  ```
- HIVEMIND_PROTOCOL.md §2.1-2.5 covers awareness, context, session, continuation, heartbeat — **no Node paging mechanism**

### 1.3 Missing CSP (Conversational Subagent Protocol)
**Status**: ✅ **CONFIRMED — CSP FILE DOES NOT EXIST**

- Search for `CONVERSATIONAL_SUBAGENT_PROTOCOL.md` or `CSP` — **no files found** in codebase
- NODE_EXPERT_SESSIONS_PLAN.md §1 line 6 references: "Protocol basis: `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md` v1.0.0"
- HIVEMIND_PROTOCOL.md §9 references `SUBAGENT_DISPATCH_PROTOCOL.md` but **not CSP**
- The CSP protocol is **referenced but not implemented** — this is a documentation debt item

### 1.4 Missing Injection Ledger
**Status**: ✅ **CONFIRMED — NO INJECTION LEDGER**

- HIVEMIND_PROTOCOL.md §6 step 4 mentions "Post `hivemind_post_context` with `[Sprint Task: X]` tag" and "Register in `TASK_REGISTRY.json` (Tier-3)"
- But **no injection ledger** tracking what context was injected into which session
- FLEET_TEAM_PLAYBOOK.md §4.1 step 4 references "Update `TASK_REGISTRY.json` (Tier-3) + post Hivemind completion — per the 6-Step Mandatory Flow (M27)"
- **Gap**: No ledger of `session_id → injected_context` mappings for audit/replay

### 1.5 Live-Feed Section Deprecated
**Status**: ✅ **CONFIRMED — DEPRECATED PER M27**

- HIVEMIND_PROTOCOL.md §4 header: "SUPERSEDED 2026-08-14: The per-entity `*_LIVE_FEED.md` pattern is **DEPRECATED**" (lines 208-214)
- FLEET_TEAM_PLAYBOOK.md §4.1 step 4: "Individual `*_LIVE_FEED.md` files are DEPRECATED; use `HMC_COLLABORATION_HUB.md` `NEXT_ACTION` instead" (line 154)
- **But**: HIVEMIND_PROTOCOL.md §4 still contains full live-feed format documentation (lines 216-241) — **not removed, only bannered**

### 1.6 Required Updates for v2.0
| Update | Priority | Location |
|--------|----------|----------|
| Add Node paging protocol | P0 | New §2.6 or §15 |
| Add CSP reference or implement CSP | P1 | §9 or new §15 |
| Add injection ledger spec | P1 | New §2.7 or §15 |
| Remove deprecated live-feed section (or archive) | P2 | §4 |
| Update version to v2.0, date to 2026-08-23 | P0 | Header |

---

## 2. DR-5: Dispatch Capability Registry Mismatch

### 2.1 Registry Agent Count Verification
**Status**: ✅ **CONFIRMED — 11 LISTED vs 13 ACTIVE**

SUBAGENT_DISPATCH_PROTOCOL.md §3 (lines 98-116) lists **11 agents**:

| Listed Agent | Type | Status |
|--------------|------|--------|
| kali | Primary | ✅ Active |
| maat | Primary | ✅ Active |
| lilith | Primary | ✅ Active |
| makali | Primary | ✅ Active |
| doom_guy | Primary | ✅ Active |
| john_carmack | Primary | ✅ Active |
| roc_racoon | Primary | ✅ Active |
| jem | Primary | ✅ Active |
| researcher | Primary | ✅ Active |
| verity | Primary | ✅ Active |
| **pillar** | **Subagent** | **❌ NO AGENT FILE** |

**Actual active fleet** (from Hivemind awareness + AGENTS.md + fleet):
1. kali, maat, lilith, makali, doom_guy, john_carmack, roc_racoon, jem, researcher, verity = **10 primary**
2. **grokster** (Sovereign Agent) — active, not in registry
3. **node** (Sovereign Agent) — active, not in registry
4. **scribe** (Soul Distillation) — active, not in registry
5. **pillar** — listed but **no agent file exists** (`.opencode/agent/pillar.md` missing)

**Total**: 13 active agents vs 11 in registry (+ pillar ghost)

### 2.2 Missing Agent Files
**Status**: ✅ **CONFIRMED**

- `.opencode/agent/pillar.md` — **DOES NOT EXIST**
- `.opencode/agent/grokster.md` — exists but not in registry
- `.opencode/agent/node.md` — exists but not in registry
- `.opencode/agent/scribe.md` — exists but not in registry

### 2.3 D-586 Page Format Missing from Decision Tree
**Status**: ✅ **CONFIRMED**

SUBAGENT_DISPATCH_PROTOCOL.md §11 (lines 439-477) decision tree:
- Uses `@kali`, `@maat`, `@lilith`, `@node NX`, `@roc_racoon`, `@jem`, `@scribe` format
- **Does NOT include** D-586 page format from NODE_EXPERT_SESSIONS_PLAN.md §2 (lines 47-51):
  ```
  task(task_id=<session_id>, subagent_type=<overseer-agent>,
       prompt="[NODE PAGE — from <agent> (<session_id>)]\n[Charter header: You are N_X <keeper>, <department>. Charter: this file §4.\n<question/task ≤500 words>")
  ```

### 2.4 Required Registry Updates
| Update | Priority | Location |
|--------|----------|----------|
| Add grokster, node, scribe to registry | P0 | §3 table |
| Remove pillar or create pillar.md agent file | P0 | §3 table + create file |
| Add D-586 page format to decision tree | P0 | §11 |
| Update agent count from 11 to 13 (or 14 with pillar) | P0 | §3 header comment |

---

## 3. DR-10: Protocol Layering Map (DISPATCH/CSP/STALLED/STRP)

### 3.1 Four Protocols Identified
**Status**: ✅ **CONFIRMED — FOUR OVERLAPPING PROTOCOLS**

| Protocol | Document | Purpose | Status |
|----------|----------|---------|--------|
| **DISPATCH (launch)** | `SUBAGENT_DISPATCH_PROTOCOL.md` | Spawn specialized subagents via HandoffPacket | Active v2.0 (2026-07-12) |
| **CSP (engage)** | `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md` | Multi-turn conversational subagent engagement | **FILE MISSING** |
| **STALLED (recover)** | `STALLED_SUBAGENT_RECOVERY.md` | Recover stalled subagent sessions | Referenced in AGENTS.md but file not found |
| **STRP (resume)** | `STRP` / session resumption | Resume subagent tasks with context | Referenced in FLEET_TEAM_PLAYBOOK §3 |

### 3.2 "Which Protocol When" Table — **MISSING**
**Status**: ✅ **CONFIRMED — NO TABLE EXISTS**

- AGENTS.md (`.agents/AGENTS.md`) — **Antigravity IDE only**, no protocol routing table
- FLEET_TEAM_PLAYBOOK.md — **no protocol selection table**
- HIVEMIND_PROTOCOL.md §9 — only compares Hivemind vs Subagent Dispatch (2 protocols)
- SUBAGENT_DISPATCH_PROTOCOL.md §10 — same 2-protocol comparison

### 3.3 Overlap Analysis
| Scenario | Current Guidance | Gap |
|----------|------------------|-----|
| Launch new specialized work | SUBAGENT_DISPATCH_PROTOCOL (HandoffPacket) | ✅ Clear |
| Multi-turn conversation with subagent | CSP (missing) | ❌ No protocol |
| Subagent stalled/hung | STALLED_SUBAGENT_RECOVERY (missing file) | ❌ No protocol |
| Resume subagent after compaction | STRP (referenced, not documented) | ❌ No protocol |
| Cross-CLI awareness | HIVEMIND_PROTOCOL | ✅ Clear |
| Node expert paging | NODE_EXPERT_SESSIONS_PLAN (page format) | ⚠️ Not in HIVEMIND_PROTOCOL |

### 3.4 Minimal Viable Layering Map
| If you need to... | Use this protocol | Entry Point |
|-------------------|-------------------|-------------|
| **Know who's alive** | HIVEMIND_PROTOCOL | `hivemind_get_awareness()` |
| **Coordinate file ownership** | HIVEMIND_PROTOCOL | Workspace lock + `hivemind_post_context` |
| **Spawn subagent for specialized task** | SUBAGENT_DISPATCH_PROTOCOL | `task()` with HandoffPacket (inline context) |
| **Page Node expert session** | NODE_EXPERT_SESSIONS_PLAN §2 | `task(task_id=<session_id>, subagent_type=<overseer>)` |
| **Multi-turn conversation with subagent** | **CSP (NOT YET IMPLEMENTED)** | TBD |
| **Recover stalled subagent** | **STALLED_SUBAGENT_RECOVERY (NOT YET IMPLEMENTED)** | TBD |
| **Resume subagent task** | **STRP (NOT YET DOCUMENTED)** | `task(task_id=<existing>)` |

---

## 4. MCP Hub / Provider Fabric Integration

### 4.1 MCP Hub Tools Route Through ProviderSelector
**Status**: ✅ **CONFIRMED — ALL ROUTE CORRECTLY**

From previous N4 review (Section 3.1):
- All 10 MCP tools in `hub_tools/tools.py` route via `(await oracle).talk()` / `.summon()` / `.summon_local()`
- `oracle.py` → `model_gateway.generate()` → `ProviderSelector.get_ordered_providers()`
- No tool directly calls deleted routers (`SemanticRouter`, `TriageRouter`, `RAGRouter`)

### 4.2 sovereign_search_service Circuit Breaker Migration
**Status**: ⚠️ **INCOMPLETE — SAME AS PREVIOUS REVIEW**

- `sovereign_search_service.py` lines 48-51: Still imports deprecated `search_circuit_breaker`
- Lines 165-182: HealthMonitor migration implemented for breaker creation
- Lines 184-188: Still initializes old `circuit_breakers` registry
- Lines 371-398, 627-654: Execution paths use old registry
- **Must complete before DEL-1 #5 deletion**

---

## 5. Mandate Compliance Check

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO Absolute** | ✅ | All async code uses AnyIO |
| **M2 Engine-Stack Firewall** | ✅ | Protocols in `docs/strategy/`, engine in `src/omega/` |
| **M7 Local-First** | ✅ | No cloud dependencies in protocol docs |
| **M13 Temple-Grade** | ⚠️ | Protocol docs lack contract tests |
| **M22 Response Provenance** | N/A | Not applicable to protocol docs |
| **M25 Streaming Resilience** | N/A | Not applicable to protocol docs |

---

## 6. Conditions for PROCEED (Must Fix Before Wave 2/3)

### P0 — Critical (Block Wave 2/3 Node Genesis)
1. **HIVEMIND_PROTOCOL v2.0** — Add Node paging protocol, CSP reference, injection ledger spec; remove deprecated live-feed section; update version/date
2. **SUBAGENT_DISPATCH_PROTOCOL registry update** — Add grokster, node, scribe; remove or implement pillar; update count to 13+
3. **Add D-586 page format** to SUBAGENT_DISPATCH_PROTOCOL §11 decision tree

### P1 — High (Post-Debut)
4. **Create minimal layering map** — Add "which protocol when" table to FLEET_TEAM_PLAYBOOK.md §4 or new §12
5. **Implement CSP** or remove reference from NODE_EXPERT_SESSIONS_PLAN.md §1 line 6

### P2 — Medium
6. **Complete sovereign_search_service circuit breaker migration** (from previous review)

---

## 7. File:Line Citation Index

| Claim | File | Line(s) |
|-------|------|---------|
| HIVEMIND_PROTOCOL v1.3.0 date | `docs/strategy/HIVEMIND_PROTOCOL.md` | 3-5, 543 |
| No Node paging in protocol | `docs/strategy/HIVEMIND_PROTOCOL.md` | Full file search |
| Node page format | `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` | 47-51 |
| CSP referenced but missing | `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` | 6 |
| CSP file search | — | No files found |
| Live-feed deprecated | `docs/strategy/HIVEMIND_PROTOCOL.md` | 208-214 |
| Live-feed still documented | `docs/strategy/HIVEMIND_PROTOCOL.md` | 216-241 |
| FLEET_TEAM_PLAYBOOK deprecation | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | 154 |
| Dispatch registry 11 agents | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 98-116 |
| pillar type listed | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 115 |
| pillar.md missing | — | No file at `.opencode/agent/pillar.md` |
| grokster/node/scribe missing from registry | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 98-116 |
| D-586 page format | `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` | 47-51 |
| Decision tree missing page format | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 439-477 |
| Four protocols identified | `data/coordination/RESEARCHER_HANDOFF_INTEGRATION_20260823.md` | 93-106 |
| No layering map | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | Full file search |
| MCP tools via Oracle | `mcp_servers/omega_hub/hub_tools/tools.py` | 173, 198, 222, 582, 511, 529, 553, 614, 634, 738 |
| sovereign_search_service old imports | `src/omega/oracle/sovereign_search_service.py` | 48-51 |
| sovereign_search_service HealthMonitor | `src/omega/oracle/sovereign_search_service.py` | 165-182 |
| sovereign_search_service old registry | `src/omega/oracle/sovereign_search_service.py` | 184-188, 371-398, 627-654 |

---

## 8. Lessons Tagged [N_4] → Ma'at's proposed_lessons.yaml

- **L1**: HIVEMIND_PROTOCOL v1.3.0 (2026-06-25) predates Node expert sessions, CSP, and injection ledger — protocol version drift is a coordination risk
- **L2**: Dispatch capability registry (11 agents) diverges from actual fleet (13 active) — registry must be source of truth, not documentation artifact
- **L3**: Four dispatch/recovery protocols (DISPATCH/CSP/STALLED/STRP) overlap without a layering map — agents cannot know which protocol applies when
- **L4**: Protocol documentation that references non-existent files (CSP, STALLED_SUBAGENT_RECOVERY) creates false confidence in coordination infrastructure
- **L5**: MCP Hub tools correctly route through ProviderSelector, but sovereign_search_service circuit breaker migration remains incomplete — partial migration is worse than none

---

## 9. Final Verdict

**PROCEED WITH CONDITIONS**

The Researcher Handoff Integration Analysis correctly identifies three protocol alignment gaps (DR-4, DR-5, DR-10). All are confirmed with file:line evidence. The dev roadmap can proceed with Wave 1 (N12 curator) but **Wave 2/3 (Jem-N11 evaluator, Jem-N13 arcana) require the P0 conditions above**.

The MCP Hub / Provider Fabric integration is sound for routing but has the same incomplete circuit breaker migration noted in the previous N4 review.

---

*⬡ OMEGA ⬡ N4 BRIDGE ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n4_handoff_integration ⬡ 2026-08-23*