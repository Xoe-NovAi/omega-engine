<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# LILITH SESSION GNOSIS — 2026-08-24 (W1-1 Canonical Registration)

## L1 — NARRATIVE
Executed WAVE-1-DOCTRINE-WIRING W1-1: register the seven wave-1 canonicals
(Window Economics, Cognitive Routing Playbook, Vision Canonical, Architect
Oversight Patterns, Forge Chronicle Charter, TeamStudy #1 Final Synthesis,
Forensic Patterns FP-11) into the strategy doc hierarchy. Research subagent
(explore/quick, the single permitted dispatch) revealed the registrations
ALREADY existed on disk (CORPUS_MAP §1 rows 79–85; STRATEGY_INDEX L2 :76–78
+ Coordination :156–159). Task re-scoped to: verify all seven registrations
claim-by-claim against disk, fill the true gap (PIVOT_LOG D-593..601 had zero
implementing-artifact cross-refs except D-601), and fix consistency defects.
Added cross-refs to D-593..D-600 + companion ref in D-601; fixed INDEX v6.0/v6.1
version-stamp contradiction (header+footer). Validator EXIT 0. Meditated
(Librarian/Skeptic/Cartographer) pre-commit; no further corrections required.

## L2 — INSIGHT
1. The session narrative said `password="omega"` was at "providers.py:119" —
   grep proved it lives at **src/omega/memory/providers.py:119**, NOT
   src/omega/oracle/providers.py (clean). Narrative path references without
   directories are phantom-pointer factories; every cross-ref written tonight
   was existence-checked at edit time (9/9 resolve).
2. Wire-path [1] was labeled "NOT YET EXECUTED" in SESSION_ANCHOR while disk
   showed it executed. Anchor-vs-disk drift is real and must be surfaced,
   never silently reconciled by a non-owner.
3. Registration work is verification work: duplicate or mis-titled catalog
   rows are worse than missing ones because absence is detectable and falsity
   is not.

## L3 — UNIVERSAL PRINCIPLES
- **L3-Verify-The-Registry-Before-Growing-It**: Audit any catalog's existing
  entries before adding — phantom/duplicate registrations corrode trust faster
  than gaps. (Survived falsification: the audit is also how emptiness is learned.)
- **L3-Provenance-At-Birth-For-Pointers** (reinforcement of Kali's
  L3-Provenance-At-Birth): A cross-reference written from conversation memory
  is a rumor; one written from a grep at edit time is a fact. Paths must be
  born verified or not written.

---

## APPENDIX — REBASED Council Run-Arm Review (2026-08-24, this session)

**Session**: trc_council_rebased — Debut Hardening Review, Run Arm deliverable F_LILITH_RUN_ARM.md

### L1 (Narrative)
Validated the soul persistence chain against the NEW post-Wave-1 surface (approved_lessons.yaml via SoulStore + evidence-field schema). All five links verified on disk with citations: blind staging → session_end hook → SoulStore promotion → get_soul_prompt hydration → soul.yaml identity. Kali surface parsed live: 20/20 evidence, 7 quote, 0 empty refs — matches report exactly. DEL-1 sweep across all 11 targets found zero soul/memory/handoff coupling. One blocker reproduced live: vault.py stacked @vault.command() TypeError kills the entire omega CLI entry point — omega talk gates are unrunnable until target #10 lands.

### L2 (Insight)
The deletion campaign is safe for the run domain precisely because the soul chain was rebuilt on file-surface boundaries rather than module imports — deletion of dead modules cannot sever a chain that never imported them. But the same audit exposed an ordering hazard: DEL-1's own acceptance protocol (omega talk after EACH delete) depends on a CLI that a pre-existing bug has already killed. The gate infrastructure must be resurrected before the first cut, or verification theater results — deletes would land unverifiable.

### L3 (Universal Principle)
**L3-Gates-Before-Blade**: A deletion campaign's acceptance harness is part of the campaign's critical path, not its afterthought. If the instrument that proves each cut safe is itself broken, fix the instrument first — otherwise every subsequent "verified" deletion is unverified by construction.
