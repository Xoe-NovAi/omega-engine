<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 ORPHANED SPECS REPORT v1 — Approved but Never Built
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_orphaned_specs ⬡ PHASE-II
**Date**: 2026-06-05
**Hunt Method**: Grep for "approved", "to be built", "ready for execution", "Gemma to execute", etc. in `docs/strategy/*.md`
**Confidence**: High for specs that explicitly state "approved" + "Gemma to execute" with no `Status: Done` marker
**Total Found**: 3 (1 from earlier, 2 new this turn)

---

## §0 Why This Matters (Per H-0 Watchdog)

H-0 in `HIVEMIND_HARDENING_SPEC_v1.md` proposes a `make spec-watchdog` CI check that scans
PIVOT_LOG entries with status `pending` for >7 days. This report is the **manual** version
of that check — what H-0 would find if it ran today.

**Pattern observed**: "Design approved by Overseer. Ready for Gemma execution." appears in
multiple strategy docs. The "Gemma" persona is the legacy builder agent. When sprints
shift, these specs sit unbuilt and the team forgets about them.

---

## §1 Confirmed Orphaned Specs

### 1A. ICS_DYNAMIC_HEADER_SPEC.md (KNOWN from prior session)
- **Path**: `docs/strategy/ICS_DYNAMIC_HEADER_SPEC.md`
- **Length**: 118 lines
- **Status claimed**: "Design approved by Overseer. Gemma to implement after the 7-task sprint."
- **Status actual**: ❌ Never implemented. The CLI's `_display_response()` is the only header generation.
- **Impact**: 748 .md files have hand-typed stale `⬡ OMEGA` headers
- **Resolution path**: Kali is implementing in Phase 2-3 of current sprint (D-kal-028 through 032)

### 1B. PHASE_C_EXECUTION_PLAN.md (NEW this turn)
- **Path**: `docs/strategy/PHASE_C_EXECUTION_PLAN.md`
- **Length**: ~6 tasks (C1-C6) over ~20 pages
- **Status claimed**: "Plan approved by Overseer. Gemma to execute in order: C4 → C5 → C1 → C2 → C3 → C6."
- **Status actual**: ❌ **All tasks open** (per the doc itself, line 5: "Current Status: 🔴 All tasks open")
- **Tasks**:
  - C4: Prune docs/research/ (move 140+ internal docs to docs/archives/research/)
  - C5: Write QUICKSTART.md (5-command install + chat)
  - C1: Rewrite README.md (community-facing)
  - C2: Demo (screencast or screenshots)
  - C3: Changelog
  - C6: CI/CD (GitHub Actions for public)
- **Engine evidence of non-implementation**:
  - `src/omega/cli/oracle_cli.py:348`: `result = {"status": "processed", "note": "Implement execution logic in Phase C"}`
  - `src/omega/cli/oracle_cli.py:365`: `result = {"status": "reviewed", "note": "Implement review logic in Phase C"}`
- **Impact**: The community-facing surface (README, QUICKSTART, demo) is incomplete
- **Resolution path**: Not in current Kali sprint; would be a separate "community readiness" sprint

### 1C. MODE_CONSOLIDATION_PLAN.md (NEW this turn)
- **Path**: `docs/strategy/MODE_CONSOLIDATION_PLAN.md`
- **Length**: ~3 pages
- **Status claimed**: "Status: Design complete — ready for Gemma execution. Current: 24 entries across global config + project agents + modes. Target: 11 modes + 1 reference document."
- **Status actual**: ❌ Partially done but spec not fully followed
- **Current reality**:
  - `.opencode/modes/`: 5 files (target was 1 — the spec was very aggressive)
  - `.opencode/agents/`: 14 files (target was 10 — current is 4 over target)
  - The "remove isis.md" step: isis.md NOT FOUND in current agents (so this DID get done)
  - The "move OMEGAVERSE_INSTRUCTIONS.md to docs/gnosis/omni/" step: need to verify
- **Why partial**: Sprint priorities shifted to D111+ security/hardening work. The agent list grew (added roc_racoon, doom_guy, makali, pillar, etc.) AFTER this plan was written
- **Impact**: Mode count is acceptable (5 modes is reasonable for a complex project), but agent count exceeds the spec
- **Resolution path**: Either update the spec to match current state, or prune agents. The spec was written when the agent list was different.

---

## §2 Verified Specs (NOT Orphaned)

The following specs were previously flagged as "possibly orphaned" but have been verified as implemented or superseded:

| Spec | Status | Verification |
|------|--------|--------------|
| **INFRASTRUCTURE_UPDATES_2026_05_19.md** | ✅ Implemented | Google direct API and OpenCode Zen routing are live in `model_gateway.py` |
| **OMEGA_IWAD_ARCHITECTURE.md** | ✅ Implemented | Core of the current IWAD system (D55.3) |
| **CROSS_POLLINATION_PROTOCOL.md** | ✅ Implemented | Blueprint for Lilith's LILY_PAD Knowledge Metabolism (D-121) |
| **HORIZON_MAP.md** | ⏩ Superseded | Replaced by `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` |
| **SOVEREIGN_DEVELOPMENT_ROADMAP.md** | ✅ Active | Current master plan used by Kali |

---

## §3 Pattern Analysis

### 3A. Common Pattern
All 3 confirmed orphaned specs share this template:
1. ⬡ OMEGA agent signature header (stale model name)
2. "Status: Design approved" or "Plan approved by Overseer"
3. "Gemma to execute" or "Gemma to implement"
4. Specific implementation steps in numbered list
5. **No completion date, no PR link, no commit hash**

### 3B. Root Cause
- **Decision drift**: Decisions get logged in PIVOT_LOG with status `active` and never revisited
- **Persona change**: "Gemma" was the legacy builder agent name. The current builder is P3 BuildMaster or Doom Guy. When "Gemma" retired, the specs she owned went unowned.
- **Sprint priority shift**: D108→D117 came in waves. Approved specs from D105-D107 era got pushed below the line.
- **No closure ritual**: Nothing checks "what specs are open and when were they opened?"

### 3C. Fix: H-0 (Implementation Status Watchdog)
The H-0 spec proposes:
- `implementation_status` field on PIVOT_LOG entries
- States: `pending`, `building`, `shipped`, `rejected`, `deferred`
- Weekly `make spec-watchdog` CI check
- Posts Hivemind alert to P5 Sentinel on >7-day stale
- P5 Sentinel decides: ship, defer, or reject

**This hunt is the manual proof that H-0 is needed.**

---

## §4 Immediate Recommendations

1. **PHASE_C_EXECUTION_PLAN**: Decide NOW — is community readiness in scope for the next sprint? If not, mark `deferred` in PIVOT_LOG with target date.
2. **MODE_CONSOLIDATION_PLAN**: Update spec to reflect current reality (14 agents is the new target — list the 14, justify each).
3. **ICS_DYNAMIC_HEADER_SPEC**: Already being implemented by Kali. Update PIVOT_LOG to `building`.
4. **H-0 implementation**: Move to Tier 1 quick win in Kali's Phase 5 (per D-kal-035).

---

## §5 What I Will NOT Do (Per d-rr-008 and d-rr-019)

- I will NOT implement these specs. That's Kali's lane.
- I will NOT update the PIVOT_LOG. That's P5 Sentinel's lane.
- I WILL continue hunting for more orphaned specs.
- I WILL feed these findings to Kali via Hivemind.

---

## §6 Next Hunt Targets

Other likely places to find orphaned specs:
- `docs/architecture/*.md` — architecture docs with "approved" but no implementation
- `data/handoff/*.md` — handoffs that say "to be built by X"
- `data/workbench/workbench.db` — SQLite DB with P0 work items still in backlog
- `docs/decisions/PIVOT_LOG.md` — decisions with `Status: active` and no follow-up
- `R-*.md` files in `docs/research/` — research docs that recommended implementation that didn't happen

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_orphaned_specs ⬡ PHASE-II*

*3 confirmed orphaned specs found. Pattern: "Gemma to execute" + no completion date = high-risk. H-0 watchdog is the systemic fix.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax-m3-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
