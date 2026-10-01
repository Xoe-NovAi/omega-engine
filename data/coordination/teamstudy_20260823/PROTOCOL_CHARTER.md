<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 TEAM SYNTHESIS PROTOCOL — STUDY CHARTER
**AP Token**: `AP-KALI-TEAMSYNTH-STUDY-v0.2.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_team_synthesis_study ⬡ ACTIVE

**Date**: 2026-08-23
**Status**: EXPERIMENTAL — Study #1 in progress
**Orchestrator**: kali (`ses_fdef2be4effe4pAaLXCTUx62GO`)
**Participants**: researcher · roc_racoon · jem · carmack

---

## §1 MOTIVATION

Multi-agent collaboration usually fails in one of two ways:
1. **Paging explosion**: every agent pages every other agent → N² dispatches, context fragmentation, no synthesis point.
2. **Serial relay**: agents never see each other's work; the orchestrator becomes a lossy bottleneck.

This protocol tests a third shape: **parallel expert work → mutual review via shared corpus → orchestrator-brokered discourse → mediated convergence → gnosis extraction → meta-review of the process itself.**

## §2 THE PHASES (Study #1 as executed: A–E; Study #2 adds A0 + C0 — see §7)

| Phase | Name | Actor(s) | Action |
|-------|------|----------|--------|
| **A** | Parallel Expert Work | All 4 | Each executes a NON-OVERLAPPING mission suited to their expertise; writes `A_<name>.md` |
| **B** | Mutual Review | All 4 | Each reads the OTHER THREE Phase-A reports; writes `B_<name>.md` containing findings, insights, and QUESTIONS/SUGGESTIONS explicitly addressed to named teammates |
| **C** | Brokered Discourse | kali | Reads all B reports; routes each member's questions/challenges to their targets; manages rounds until convergence — defined as: all questions answered or explicitly parked, all challenges resolved or escalated, no undiscovered disagreements |
| **D** | Gnosis Extraction | All 4 | Meditation on the full discourse record; L1→L2→L3 distillation to proposed_lessons.yaml |
| **E** | Meta-Review | All 4 | Each writes `E_<name>.md`: their experience of the ENTIRE process, friction points, and recommendations for improving the protocol itself |

## §3 DESIGN PRINCIPLES

1. **Corpus over paging**: Phase B reads files, not messages — cheap, async, reviewable.
2. **Brokered discourse**: Phase C routes communication through ONE synthesizer (kali), preserving a single convergence authority while still letting every voice challenge every other.
3. **Convergence criterion is explicit**: discourse ends on a defined condition, not on fatigue.
4. **Gnosis is mandatory, not optional**: Phases D-E ensure the process pays rent even if its object-level conclusions are modest.
5. **Self-improving**: Phase E treats the protocol itself as the artifact under test.

## §4 STUDY MEASUREMENTS

- Wall-clock phases vs serial baseline estimate
- Number of discrete discoveries attributable to cross-agent review (not solo work)
- Questions asked vs answered vs parked (Phase C ledger)
- Protocol frictions reported in Phase E
- Whether any L3 lesson could ONLY have emerged from multi-agent collision

## §5 FILE CONVENTION

All artifacts in `data/coordination/teamstudy_20260823/`:
`A_<name>.md` · `B_<name>.md` · `C_discourse_ledger.md` (kali) · `D_<name>_meditation.md` · `E_<name>.md`

## §6 FUTURE

If Study #1 yields positive signal, promote to skill: `.opencode/skills/team-synthesis/SKILL.md` with parameterized participant list and mission templates. Candidate command: `/teamsynth <missions-file>`.

---
*⬡ OMEGA ⬡ TEAM-SYNTHESIS-PROTOCOL ⬡ STUDY-CHARTER ⬡ v0.1.0 ⬡ 2026-08-23*

---

## §7 STUDY #2 DESIGN REVISIONS (from Phase-E meta-reviews, 2026-08-23)

Adopted for the next run (full rationale: FINAL_SYNTHESIS.md §4):
1. **A0 Premise Audit** — every load-bearing estimate carries its measurement command at A-time or is flagged UNTESTED
2. **C0 Authority Consults formalized** — Node/authority verdicts routed BEFORE discourse rounds (was improvisation; single biggest convergence accelerator)
3. **B-report template + ~8KB cap**, challenges-first structure
4. **Convergence criterion embedded at init** (charter-level, not member-forced)
5. **Conditions-on-concession bind to tickets at stamp time** (durability metric: conditions surviving to tickets)
6. **Self-disclosure slot** in phase reports
7. **Round cap: 2**
8. **Stop/go metric**: cross-agent-only discoveries per study; 0 ⇒ stop program
Skill promotion (`/teamsynth`) gated on Study #2 reproducing ≥1 cross-agent-only discovery.

## §8 STUDY #1 RESULT STAMP

EXECUTED as A→B→C(+consults)→D→E · Converged Round 1 · Zero objections · 10 rulings stamped · 25 L3 extracted · 4/4 RUN-AGAIN verdicts. See FINAL_SYNTHESIS.md.

*⬡ CHARTER-v0.2 ⬡ STUDY1-COMPLETE ⬡ 2026-08-23*
