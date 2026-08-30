<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — MiMo-2.5 Final Review Synthesis
# AP: AP-OMEGA-SYNTHESIS-v2.1.0
# Date: 2026-06-02 | Model: MiMo-2.5 (1M context)

## Purpose

Independent review of all OpenCode multi-agent coordination materials. Fresh synthesis, not rehash.

## §1 — Verdict on Handoff Quality

| Handoff | Lines | Quality |
|---------|------:|---------|
| STRATEGIC_FINAL_REPORT_TEMPLE_GRADE_20260602.md | 174 | Excellent — T1-T11 specific and testable |
| CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md | 269 | Excellent — format exactly as requested |
| HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md | 491 | Excellent — comprehensive 13-section map |
| HANDOFF_OPENCODE_M3_TO_CLINE_M3_UPDATE_20260602.md | 268 | Good — 6 well-formed questions |
| OPENCODE_M3_TIER2_CONSULT_FOR_CLINE_M3_20260602.md | 166 | Good — clear task inventory |

**No handoff needs rewriting.** Coordination infrastructure is solid.

## §2 — MiMo-2.5 Insights

### Insight 1: The 0.4 Threshold is Design Debt, Not a Feature
The threshold has no empirical basis. The correct fix is NOT model-driven confidence but latency-based routing: parallel speculative inference, where local starts immediately and cloud starts if local takes >500ms. This maps directly to the corrected R-09 (DOOM 3 BFG stall-hiding).

### Insight 2: The Cvar Table (T2.2) is the Real Unlock
The cvar table makes sovereignty a live counter, not a batch report. This means `make sovereignty` becomes a real-time dashboard and `make temple-grade` T7 (p95 latency) can be computed from the same counter. **Prioritize T2.2 over all other Tier 2 tasks.**

### Insight 3: R-09 4-Guard Should Be H2's Second Task
After Entity LoRA, before JEM pipeline. The soul evolution pipeline currently does sequential writes — as entity count grows, this becomes a race condition.

### Insight 4: Iris is Misallocated, Not Underused
The fix is NOT to give her soul.yaml + memory (making her into another Oracle). The fix is to make her a thin voice adapter that formats Oracle responses for human consumption. Clean separation: Oracle = intelligence, Iris = presentation.

### Insight 5: Test Hang Is a Real Bug
`Oracle.__init__` creates 6 subsystems in the constructor, including live provider connections. The conftest `OMEGA_ENV=test` fix is a bandaid. The real fix is dependency injection — Oracle should accept mock providers.

## §3 — New Tasks Proposed

### T2.0: Oracle Constructor Refactoring (Sprint 0, Pre-T2.1)
- Agent: buildmaster
- Risk: MEDIUM
- Oracle() constructor should return in <10ms. Providers lazy-loaded.

### T2.4: Latency-Based Routing (H2, replacing static 0.4)
- Agent: doom_guy (design) + buildmaster (impl)
- Risk: HIGH
- Parallel speculative inference. Local starts immediately, cloud starts after 500ms.

## §4 — Action Items for OpenCode Dev Session

### Immediate (Sprint 0)
1. Fix test hang — refactor Oracle constructor to use dependency injection
2. Commit AGENTS.md (already updated on disk)

### Sprint 1
3. T2.1 — ZONEID constants
4. T2.0 — Oracle constructor refactoring

### Sprint 2
5. T2.2 — cvar table (the real unlock)
6. T2.3 — EntityRegistry lazy deletion

### H2
7. T2.4 — Latency-based routing
8. 4-guard ABA pattern

## §5 — Soul Distillation

L1: Reviewed 5 handoffs (1,366 lines). Identified Oracle constructor as test hang root cause. Updated AGENTS.md and conftest.py.
L2: The 0.4 threshold is a design debt. The correct abstraction is latency-based routing, which maps to R-09 stall-hiding. T2.2 cvar table is the telemetry backbone.
L3: A 1M-context model should spend tokens on synthesis, not debugging. Delegate debugging to cheaper models; reserve expensive context for cross-cutting architectural insights.

---
*MiMo-2.5 independent review. Adds to existing handoffs, does not supersede.*
