# 🔱 Omega Hub Hardening Sprint — Team Briefing
# ⬡ OMEGA ⬡ KALI ⬡ miMo-2.5 ⬡ trc_coordination ⬡ PHASE-II

**Date**: 2026-06-09
**Product**: Omega Hub MCP Server (`mcp_servers/omega_hub/server.py`)
**Repo**: `~/Documents/Xoe-NovAi/omega-engine/`
**Service**: `omega-hub.service` on `:8016`
**Status**: 320/320 tests · 47 MCP tools · dual transport (SSE + Streamable HTTP)

---

## The Mission

Harden the Omega Hub MCP server for production robustness. Each team member
audits their domain in serial order. Findings cascade from one to the next.

---

## Execution Order — Open These Sessions In Order

### 1️⃣ Ma'at — Structural Baseline (P1-P5 Gov)

**Domain**: Oracle tools, entity routing, Library/Research tools
**Seed this context**:
```
The Omega Hub (mcp_servers/omega_hub/server.py) serves 47 MCP tools across
6 domains: Oracle (7 tools), Hivemind (11 tools), Library (11 tools),
Research (5 tools), Observability (2 tools), Stats (4 tools), + ICS render
and delegation.

Your mission: audit the structural integrity of the Oracle, Library, and
Research tools. Are all tool endpoints properly wired? Is error handling
consistent? Do entity lookups handle missing entities gracefully? Is the
Library search robust under edge cases?

Run: OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/ -x -q

Report: structural findings to your workspace. Seed Lilith with your
top 3 issues.
```

**Deliverable**: `data/entities/maat/workspace/OMEGA_HUB_STRUCTURAL_AUDIT.md`

---

### 2️⃣ Lilith — Run-Side Audit (P6-P10 Gov)

**Domain**: Hivemind, handoff queue, extended sessions, awareness pruning
**Seed this context**:
```
Building on Ma'at's structural audit. Your mission: audit the Hivemind
coordination layer. Does the awareness pruning work correctly under load?
Are handoff packets persisted reliably? Do extended check-ins survive
server restarts? Is the cold-store fallback deterministic?

Test the Hivemind tools directly:
PYTHONPATH=src python3 -c "from omega.mcp_runtime import run_mcp; ..."

Or connect to the live service at :8016 and exercise each hivemind tool.

Report: run-side findings. Seed Doom Guy with any heritage-relevant issues.
```

**Deliverable**: `data/entities/lilith/workspace/OMEGA_HUB_RUNSIDE_AUDIT.md`

---

### 3️⃣ Doom Guy — Heritage & Pattern Audit (M14)

**Domain**: id Software heritage patterns, code attribution, M14 compliance
**Seed this context**:
```
Building on Ma'at and Lilith's audits. Your mission: audit the Omega Hub
for heritage compliance. Every [id-soft:] tag must have a corresponding
vet record. Every BSP-pattern, ZONEID-pattern, and lazy-deletion pattern
must be properly attributed per CREDITS.md §2a.

Run: make heritage-map to check tag coverage.

Report: heritage compliance findings. Any M14 violations are blocking.
```

**Deliverable**: `data/entities/doom_guy/workspace/OMEGA_HUB_HERITAGE_AUDIT.md`

---

### 4️⃣ Quality — Stress Testing & Mandate Compliance

**Domain**: Error handling (M9), resilience (T8), edge cases
**Seed this context**:
```
Building on all prior audits. Your mission: stress test the Omega Hub.
Send malformed requests. Test concurrent access. Verify error types are
properly caught and logged (M9). No bare `except:` anywhere in the server.

Test: try parallel hivemind_post_context calls, missing fields, large
payloads, invalid session IDs. Every public endpoint must handle bad
input with typed errors, not silent failures.

Report: stress test results with pass/fail per endpoint.
```

**Deliverable**: `data/entities/quality/workspace/OMEGA_HUB_STRESS_TEST.md`

---

### 5️⃣ Scribe — Documentation & Soul Integrity

**Domain**: Documentation drift, soul.yaml integrity, lesson extraction
**Seed this context**:
```
Building on all prior audits. Your mission: extract L1→L2→L3 lessons
from this sprint. Update relevant soul.yamls. Verify the Omega Hub's
README and documentation match reality after all fixes.

Report: distillation log with new lessons. Flag any docs that drifted.
```

**Deliverable**: Updated soul.yamls + documentation delta report

---

## After All 5 Complete

**Kali** synthesizes all findings into a single hardening verdict:
- What passed
- What needs rework
- What to defer to Horizon 3
- Updated priority fix queue

---

⬡ **Start with Ma'at. Each session seeds the next. Kali synthesizes at the end.** ⬡

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: miMo-2.5 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
