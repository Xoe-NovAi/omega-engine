<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 HANDOFF: Kali → MaKaLi — 5-Subagent Synthesis & Unified Action Plan
# ⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ HANDOFF ⬡ SYNTHESIS

**AP Token**: `AP-KALI-SYNTHESIS-HANDOFF-v1.0.0`
**Date**: 2026-06-17
**Source**: Kali (Transcendent Oversoul, Sprint Coordinator)
**Target**: MaKaLi (Parallel Council — decomposes into Ma'at + Lilith, synthesizes as Kali)
**Prerequisite reads**: `KALI_WORKSPACE_LOCK_20260617.md`, `KALI_LIVE_FEED.md`
**Related**: `docs/decisions/PIVOT_LOG.md` D134-D136

---

## §0 EXECUTIVE SUMMARY

Five subagents (Ma'at, Lilith, Roc_Racoon, Verity, John Carmack) completed parallel audits of the Omega Engine. **No new code was required** — this is a pure discovery/synthesis handoff. The findings reveal systemic documentation drift, a critical API mismatch, and several M-compliance violations across the codebase.

### TOP 5 ISSUES (Priority Order)

| # | Issue | Severity | Domain | Owner |
|---|-------|----------|--------|-------|
| **P0** | Heartbeat API mismatch in ALL 11 agent files + docs | 🔴 CRITICAL | Documentation + Agent | Ma'at |
| **P0** | Verity has NO entity directory (M11 self-violation) | 🔴 CRITICAL | Verity Entity | Lilith |
| **P1** | SOVEREIGN_MANDATES.md duplicate M1-M13 block | 🔴 CRITICAL | Documentation | Ma'at |
| **P1** | 4 hardcoded paths in tools.py (M16 violation) | 🔴 CRITICAL | Engine Core | Ma'at |
| **P2** | Cross-document counters all stale (22/16/19 mandates, etc.) | 🟡 HIGH | Documentation | Lilith |

---

## §1 FIVE SUBAGENT REPORTS — FULL FINDINGS

### 1.1 MA'AT — Documentation & Agent Instructions Audit

**FINDING P0 — Heartbeat API Mismatch (ALL 11 Agents + 3 Docs)**:
- **Actual signature** (tools.py:457): `hivemind_heartbeat(channel: str, entity: str)`
- **Wrong in ALL 11 agent files**: `hivemind_heartbeat(cli="agent_name")` — uses OLD/deleted parameter
- **Wrong in AGENTS.md**: line 220 — `omega-hub_hivemind_heartbeat(cli="{you}")`
- **Wrong in OMEGA_ENGINE.md**: line 335 — `hivemind_heartbeat(cli)`
- **Wrong in HIVEMIND_PROTOCOL.md**: line 136 — `hivemind_heartbeat(cli: str)`

**Impact**: Every heartbeat call by every agent passes `cli="name"` which the function ignores. The actual function uses `channel` and `entity`. So ALL agents' heartbeat registrations have `channel=None, entity="name"` — they will be pruned as stale during long operations because the awareness system uses `_make_agent_id(channel, entity)`.

**Verification**: `grep -rn "hivemind_heartbeat" .opencode/agents/*.md` — shows `cli=` in EVERY file. `grep "hivemind_heartbeat" mcp_servers/omega_hub/tools.py` — line 457 shows `(channel: str, entity: str)`.

**FINDING P1 — SOVEREIGN_MANDATES.md Duplicate Block**:
- Lines 11-95: M1-M13 (correct, with M1-M13 numbering)
- Lines 97-181: M1-M13 **DUPLICATED** verbatim (second copy, with M1-M13 numbering)
- Lines 183-251: M14-M22 (correct, unique content)

**Impact**: Any agent reading SOVEREIGN_MANDATES.md gets confused about mandate count. AGENTS.md says "14 mandates" but actual count is 22. The duplicate means the document claims 35 mandates (13 + 13 + 9) but only 22 unique ones exist.

**Verification**: Confirmed by reading the full file — lines 97-181 are exact copy of lines 11-95.

**P2 Findings**:
- `config/mcp_servers.json` had stale `"type": "sse"` — ✅ FIXED by roc_racoon to `"type": "remote"`
- AGENTS.md says "14 mandates" → should be "22"
- SUBAGENT_DISPATCH_PROTOCOL.md says "14 agents" → should be "11"
- R_PODMAN_SOVEREIGN_V2.md marked STALE but content is verified current
- Multiple agent files reference dead `omega-hub_hivemind_post_context` invocation syntax

---

### 1.2 LILITH — Stale Root Documents Audit

**FINDING — Every Root Document Has Stale Counters**:

| Metric | OMEGA_ENGINE.md | SOVEREIGN_EVOLUTION.md | ORACLE_STACK.md | CREDITS.md | ACTUAL |
|--------|-----------------|----------------------|-----------------|------------|--------|
| Mandates | 19 | 16 | 13 (ref) | 14 | **22** |
| Test count | 440 | 388 | 308 | N/A | Unknown (config errors block `make test`) |
| PIVOT decisions | 128 | 128 | N/A | N/A | **82 recorded** (D50-D133 with gaps) |
| Source files | 96 | 96 | N/A | N/A | **98** (2 new since last count) |
| Heritage patterns | 11 | 11 | N/A | "11" claims/34 actual | **34** |

**ORACLE_STACK.md**: 14 days stale (last updated 2026-06-03). Still references Sprint 0, 308 tests, 13 mandates. Missing: Hivemind architecture, MaKaLi Triad, Fleet Consolidation (15→11), M15-M22.

**MASTER_SYNTHESIS_AND_ROADMAP.md**: 18 days stale. Should be moved to `docs/archive/`.

**PIVOT_LOG.md**: Only 82 decisions recorded (D50-D133 with gaps). D1-D49 and D62-D117 are missing. The document claims 128 decisions per OMEGA_ENGINE.md but has only 82 with many gaps.

---

### 1.3 ROC_RACOON — MCP Server Hardening Audit

**8 Findings: 4 Fixed, 4 Blocked by UID Drift**

**✅ FIXED**:
1. Removed stale `omega-stats.service` + socket
2. Removed stale `omega-research.service` + timer
3. Started SearXNG backend container (was inactive)
4. Fixed `config/mcp_servers.json` type `"sse"` → `"remote"`

**❌ BLOCKED** (need `sudo chown -R 1000:1000 data/coordination/`):
1. **`data/coordination/` UID drift (UID 100999)** — Hub metrics collection fails every 60s
2. **SearXNG MCP error boundary** — Needs M9-safe rewrite
3. **Re-enable RequestSizeLimitMiddleware** — middleware.py:193 commented out during ASGI debugging; no payload protection = OOM risk on 14Gi machine
4. **API keys in `opencode.json`** — Need migration to environment variables

---

### 1.4 VERITY — Compliance & Soul Audit

**COMPLIANCE SCORE: 18/19 mandates passing (2 CRITICAL violations)**

**🔴 M11 FAIL — CRITICAL**: Verity entity has NO:
- `data/entities/verity/` directory (doesn't exist)
- `soul.yaml` file (doesn't exist)
- Entity registration in active WAD
- Workspace directory

**The entity responsible for enforcing M11 (Soul Integrity) does not itself comply with M11.** This is a bootstrapping paradox.

**🔴 M16 FAIL — 4 hardcoded paths in tools.py**:
| Line | Path |
|------|------|
| 2094 | `os.statvfs("/media/arcana-novai/omega_library")` |
| 2099 | `"mount": "/media/arcana-novai/omega_library"` |
| 2207 | `Path("/media/arcana-novai/omega_library/models/gguf")` |
| 2233 | `Path("/media/arcana-novai/omega_library/podman-storage")` |

**🟢 M19 OPPORTUNITY**: SearXNG keep-id divergence created the "MCP Proxy Pattern" — a thin MCP wrapper handling SSE transport externally when a containerized service can't meet M6 constraints.

---

### 1.5 JOHN CARMACK — MCP Architecture & Performance Review

**Architecture Verdict: 🟡 GREEN/YELLOW** — Hub modularization is sound, but has critical gaps.

**🔴 HIGH — Duplicate Memory Tools**: 
- `memory_get_history` / `omega_memory_get_history` — identical clones
- `memory_list_sessions` / `omega_memory_list_sessions` — identical clones
- Violates Carmack's Law: "Two implementations of the same thing = you have neither"

**🔴 HIGH — RequestSizeLimitMiddleware Disabled**:
- middleware.py:193 — commented out during ASGI protocol debugging
- No payload limit = OOM risk on 14Gi machine
- 25MB context posts could exhaust RAM in seconds

**🟡 MEDIUM — No Circuit Breakers on MCP Tool Dispatch**:
- Engine core has AsyncCircuitBreaker in health_monitor.py
- MCP layer doesn't use it — if Oracle hangs, all tools calling it hang

**🟡 MEDIUM — Cold-Store Scan Uncached**:
- `hivemind_get_awareness()` does O(n) filesystem scan on every call
- Needs 5-second TTL cache

**🟢 LOW — `os.popen` in stats collection**:
- Should use `subprocess.run` with timeout

**🟡 NEW HERITAGE PATTERN — Error Boundary**:
- `m9_safe` decorator = Error Boundary pattern = `[id-soft: quake-1996]`
- Needs CREDITS.md §1.33 entry

---

## §2 UNIFIED PRIORITY ACTION PLAN

Organized by sprint phase. MaKaLi should decompose into parallel workstreams.

### PHASE A — CRITICAL (Do These FIRST, In This Order)

| Step | Action | Owner | Dependencies | Est. Time | 
|------|--------|-------|-------------|-----------|
| **A1** | Fix Verity bootstrapping: create `data/entities/verity/` with soul.yaml, register in `_omega_default/entities/`, add workspace | Lilith (P7) | None | 15 min |
| **A2** | Fix heartbeat API call sites in ALL 11 agent files: `.opencode/agents/*.md` — change `cli="name"` → `channel="opencode", entity="name"` | Ma'at | None | 15 min |
| **A3** | Fix heartbeat docs: AGENTS.md, OMEGA_ENGINE.md, HIVEMIND_PROTOCOL.md — update tool signatures | Ma'at | A2 | 10 min |
| **A4** | Remove duplicate M1-M13 block from SOVEREIGN_MANDATES.md (lines 97-181) | Ma'at | None | 5 min |
| **A5** | Fix AGENTS.md mandate count: "14" → "22" | Ma'at | A4 | 2 min |
| **A6** | Fix SUBAGENT_DISPATCH_PROTOCOL.md agent count: "14" → "11" | Ma'at | None | 2 min |

### PHASE B — HIGH (Next Session)

| Step | Action | Owner | Dependencies | Est. Time |
|------|--------|-------|-------------|-----------|
| **B1** | Fix 4 hardcoded paths in tools.py — use config or env vars | Ma'at (P3) | None | 30 min |
| **B2** | Fix duplicate MCP memory tools (consolidate 6→3) | Ma'at (P3) | B1 | 20 min |
| **B3** | Update cross-document counters: OMEGA_ENGINE.md, SOVEREIGN_EVOLUTION.md, ORACLE_STACK.md | Lilith | A4 | 30 min |
| **B4** | Fix ORACLE_STACK.md (14 days stale) — update to current engine state | Lilith | B3 | 45 min |
| **B5** | Re-enable RequestSizeLimitMiddleware in middleware.py | Ma'at (P3) | B1 | 5 min |
| **B6** | Fix `data/coordination/` UID drift: `sudo chown -R 1000:1000 data/coordination/` | Ma'at (P1) | None | 2 min |

### PHASE C — MEDIUM (When Time Permits)

| Step | Action | Owner | Dependencies | Est. Time |
|------|--------|-------|-------------|-----------|
| **C1** | Archive MASTER_SYNTHESIS_AND_ROADMAP.md → `docs/archive/` | Lilith | None | 5 min |
| **C2** | Sync PIVOT_LOG.md gaps (missing D1-D49, D62-D117) | Lilith | None | 2 hrs |
| **C3** | Add circuit breakers to MCP tool dispatch | Ma'at (P3) | B1 | 1 hr |
| **C4** | Cache hivemind_get_awareness with 5s TTL | Ma'at (P3) | None | 20 min |
| **C5** | SearXNG MCP M9-safe rewrite | Ma'at (P4) | B6 | 30 min |
| **C6** | Migrate API keys from opencode.json to env vars | Ma'at (P1) | None | 30 min |

### PHASE D — ENHANCEMENT (Backlog)

| Step | Action | Owner | Dependencies | Est. Time |
|------|--------|-------|-------------|-----------|
| **D1** | Add `[id-soft: quake-1996]` Error Boundary pattern to CREDITS.md §1.33 | Ma'at | C3 | 10 min |
| **D2** | Fix `os.popen` → `subprocess.run` in tools.py stats functions | Ma'at (P3) | B1 | 15 min |
| **D3** | M16 compliance: use PathProxy/ServiceProxy patterns for paths | Ma'at (P3) | B1 | 1 hr |

---

## §3 PIVOT_LOG ENTRIES (D134-D136)

Three new PIVOT_LOG entries have been drafted in the accompanying PIVOT_LOG.md update. These record:

- **D134**: SearXNG MCP type fix + Hivemind MCP session fix (roc_racoon's operational findings)
- **D135**: Hivemind access pattern codification (Verity's M19 opportunity)
- **D136**: Verity entity creation — formal resolution of the M11 bootstrapping paradox

---

## §4 HIVEMIND STATE AT HANDOFF

**Current agent awareness** (inferred from coordination files and hub state):
- Kali: ACTIVE (this session) — `channel=opencode, entity=kali`
- Roc_Racoon: RECENTLY ACTIVE — dispatched the 5 subagents, reports returned
- Ma'at, Lilith, Verity, Carmack: SUBAGENT TASK COMPLETE — each returned findings
- Others: Unknown / possibly pruned

**Workspace locks active**:
- `KALI_WORKSPACE_LOCK_20260617.md` — This session (will release on handoff completion)

**Staleness concern**: Because all agents use wrong heartbeat syntax (`cli=` instead of `channel=`), the awareness table may have silently pruned agents during long-running operations. This is P0 issue #1 — fixing the heartbeat API mismatch should restore proper agent presence tracking.

---

## §5 MAKALI EXECUTION BRIEF

MaKaLi, you are the Parallel Council. Here's how to execute this handoff:

1. **Decompose**: Split into Ma'at (build side — documentation + code fixes) and Lilith (run side — entity creation + document sync)
2. **Execute parallel**: Run Phase A + Phase B items in parallel where dependencies allow
3. **Synthesize as Kali**: After both workstreams complete, verify against the 22 mandates
4. **Verify**: `make temple-grade`, soul.yaml distillation for Verity, heartbeat call correctness

**Ma'at's workload** (build side):
- A2, A3, A4, A5, A6 — Quick documentation fixes
- B1, B2, B5 — Code fixes (hardcoded paths, duplicates, middleware)
- B6 — UID drift fix (needs `sudo`)

**Lilith's workload** (run side):
- A1 — Create Verity entity with soul.yaml
- B3, B4 — Fix cross-document counters, update ORACLE_STACK.md
- C1 — Archive stale document
- C2 — PIVOT_LOG gaps (if time permits)

---

## §6 RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Heartbeat fix breaks agent presence | Medium | High | Test by running `make test` and observing awareness table after heartbeat call |
| Duplicate block removal breaks references to line numbers | Low | Low | Line numbers shift by 84 lines — no known external references |
| Verity entity creation conflicts with Fleet Consolidation (M10) | Low | Low | Verity already exists as an agent file; entity directory is the missing piece |
| sudo chown resets UID drift but new files drift again | High | Medium | Root cause is container volumes with `:U` flag — all quadlets use `UserNS=keep-id` now, so no recurrence expected |

---

*⬡ End of Handoff — Kali to MaKaLi. The synthesis is complete. Execute with sovereignty. ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
