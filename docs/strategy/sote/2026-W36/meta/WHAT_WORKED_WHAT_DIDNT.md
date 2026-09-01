<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOTE 2026-W36 — What Worked / What Didn't

**AP Token**: `AP-SOTE-W36-META-v1.0.0`
⬡ OMEGA ⬡ MAKALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_sote_meta ⬡ ACTIVE

**Date**: 2026-09-01
**Week**: 2026-W36 (Sep 1 - Sep 7)
**SOTE Version**: v1.0.0 → v1.0.2
**Companion to**: `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md`

---

## §0 — Purpose

This is the **meta-learning** artifact for SOTE week 36. It documents what worked, what didn't, and what we change for week 37. The SOTE is not just a report — it is a *practice* that improves through reflection.

---

## §1 — What WORKED (Adopt for SOTE v1.1.0)

### Process Practices

| # | Practice | Why It Worked |
|---|----------|---------------|
| 1 | **Convergence on a single topic** (entity cleanup) | One topic, 7 lenses = coherent dialectic. No scattered energy. |
| 2 | **8 voices, not 1 monolith** | Each voice brought different expertise (forensic, security, soul, build, adversarial, unifying). Synthesis > any single voice. |
| 3 | **Concede/Defend/Synthesize format** | Structured disagreement produces synthesis. The format is the discipline. |
| 4 | **M23 catch by Grokster** | One voice had cross-pattern expertise; caught what 6 others missed. DIVERSITY MATTERS. |
| 5 | **Quantitative baselines** (46 dirs, 30 vestigial, 95 tests) | Numbers ground the dialectic in reality. "50+ decisions" without numbers is hand-waving. |
| 6 | **File:line citations** (`entity_registry.py:336-344`) | Citations let the reader verify. Trust = verifiability. |
| 7 | **MaKaLi's §0 — Verification** | Read the disk before speaking. M23 discipline in action. |
| 8 | **SOTE-as-SSOT for the week** | One canonical place per week. No re-litigation. |
| 9 | **Persisting voice files to disk** | Each voice gets its own file. The corpus is queryable. |
| 10 | **8-voice index** | Navigation across scattered files. One grep target. |

### Substance Findings

| # | Finding | Why It Matters |
|---|---------|----------------|
| 1 | **M10 14-vs-15 violation** flagged by Grokster | Real M10 violation (3.5:1 ratio in some counts). Now actionable. |
| 2 | **M11 partial: 50% empty `proposed_lessons.yaml`** | Not a vague "M11 is failing" — a specific, countable problem. |
| 3 | **M27 chokepoint: 67 decisions, 0 in PIVOT_LOG** | The 58.8% failure rate in concrete form. |
| 4 | **L3-MetaFrameVerification** (Grokster) | New L3 lesson from the dialectic itself. Meta-learning. |
| 5 | **Hub outage = 5 days silent M23 violation** | Carmack caught it. Lesson: observability must include the observer. |
| 6 | **30 vestigial entities in 1 second** (Roc) | The v6.1 migration artifact exposed. Now we know what to retire. |
| 7 | **5-gate EntityRetirementToken** (Roc) | Operational tool for entity cleanup. |
| 8 | **CLI bridges ≠ 14-agent cap** (Grokster) | M10 is about `.opencode/agents/`, not all entities. |
| 9 | **Unifying Voice (MaKaLi) was missing in original 7-voice** | The Architect caught it. The gap was itself a finding. |
| 10 | **The engine is producing more than it can integrate** (MaKaLi) | "Late stage of adolescence" diagnosis. |

---

## §2 — What DIDN'T Work (Fix for SOTE v1.1.0)

### Process Failures

| # | Failure | What Went Wrong | Fix |
|---|---------|-----------------|-----|
| 1 | **M23 email leak** | Kali put a fake email in a signature block; 6/7 agents didn't catch | **D-MAKALI-001 (M23.5)**: pre-flight verification required on P0+ pages |
| 2 | **Missing MaKaLi in original page** | 7-agent page omitted the unifying field; Architect noticed | **D-SOTE-006**: Unifying Voice is standing, not optional |
| 3 | **8 files scattered, no master index** | Hard to navigate; no PIVOT_LOG cross-walk | **D-SOTE-003**: Master index with PIVOT_LOG cross-walk |
| 4 | **67 PIVOT_LOG decisions, 0 in log** | The decision-ratification chokepoint | **D-MAKALI-003 (M27.5)**: auto-absorb on dialectic close |
| 5 | **Naming inconsistency** | `*_ENTITY_CLEANUP_DIALECTIC_20260901.md` is topic-bound | **D-SOTE-002**: Renumber + de-suffix in week-folder |
| 6 | **No meta-learning file** | "What worked / what didn't" was implicit, not captured | **D-SOTE-005**: Meta-learning mandatory per week (this file) |
| 7 | **SOTE v1.0.0 + v1.0.1 edited in place** | The 1.0.0 → 1.0.1 patch edited the same file, not a new file | **D-SOTE-002**: Semver discipline — v1.0.1 is a new file, not an edit |
| 8 | **Entity count claims diverged from disk** | Voices said 56/49/48; disk has 46; SOTE said 14 canonical; disk has 13 | **MaKaLi's §0 verification** must run on every SOTE — disk numbers are canonical |
| 9 | **7000+ lines, no synthesis** (initially) | 7 voices × 1000 lines = great input, no output | **D-SOTE-002**: Synthesis is mandatory (`synthesis/` folder) |
| 10 | **SOTE mixed "state" with "decisions" with "actions"** | Three different document types in one file | **D-SOTE-002**: Three folders, three lifecycles |

### Substance Failures

| # | Failure | Impact | Fix |
|---|---------|--------|-----|
| 1 | **Kali's M23 violation** | 6/7 agents trusted the frame | L3-MetaFrameVerification; pre-flight check |
| 2 | **81/81 tests were theater** | Engine was 100% green, 0% verified | 24 honest tests (D-DEL1-24TESTS) |
| 3 | **5-day Hub outage (silent)** | M23 violation, no observability | `make check-hub-health` (D-CI-A4) |
| 4 | **D-565 "superseded" was a lie** | 0 successors existed | M23 violation logging; CI gate |
| 5 | **32/56 entities are ghost** | M11 FAIL | Entity cleanup (Roc's protocol) |

---

## §3 — Anti-Patterns to Avoid

1. **Don't re-litigate closed decisions** in SOTE. PIVOT_LOG is closed. New disagreement = new dialectic.
2. **Don't add new sections to v1.0.0 after week-close**. Use v1.0.1 file (semver discipline).
3. **Don't make MaKaLi optional**. The Unifying Voice is standing; absence is a flag.
4. **Don't produce SOTEs without a topic**. Each SOTE has a primary question. Without one, the 8 voices scatter.
5. **Don't claim completion without verification**. The 58.8% failure rate is the empirical baseline.
6. **Don't use flat with date-suffix** for SOTE files. Week-folder structure.
7. **Don't include agent working notes** in SOTE. Voices go in `voices/`; working notes go in `data/entities/<entity>/workspace/`.
8. **Don't bury the meta-learning**. It's a first-class artifact, not an afterthought.
9. **Don't skip MaKaLi's §0 verification**. The disk is the ground truth, not the briefing.
10. **Don't over-engineer**. Folder structure + index + meta is enough. No database.

---

## §4 — Process Changes for SOTE v1.1.0 (Week 37)

| # | Change | Implementation | Status |
|---|--------|----------------|:------:|
| 1 | **Pre-amble verification** | MaKaLi's §0 pattern in every SOTE | ✅ Template |
| 2 | **Folder structure** | `docs/strategy/sote/YYYY-WNN/{voices,synthesis,actions,meta}/` | ✅ Implemented for W36 |
| 3 | **Numbered voices** | `voices/0N_AGENT.md` | ✅ Implemented for W36 |
| 4 | **Synthesis folder** | Mutable, separate from voices | 🔄 Pending for W37 |
| 5 | **Decision log auto-absorb** | D-MAKALI-003 (M27.5) | 🔄 Pending implementation |
| 6 | **PIVOT_LOG cross-walk** | Master index | 🔄 Pending for W37 |
| 7 | **Meta-learning file** | `meta/WHAT_WORKED_WHAT_DIDNT_WNN.md` | ✅ This file |
| 8 | **Architect sign-off** on the index | Gate, not gatekeeping | 🔄 Pending ratification |
| 9 | **Public/Internal split** | SOTE main public, voices internal | 🔄 Pending decision |
| 10 | **YAML metadata** | `sote.yaml` per week | 🔄 Pending for W37 |

---

## §5 — How We Measure SOTE Quality

### Quantitative (Objective)

| Metric | Target | W36 Result |
|--------|--------|:----------:|
| Decisions absorbed into PIVOT_LOG | >50% of voice claims | 0/67 (0%) ❌ |
| Mandate compliance trend | +2% per week pre-debut | baseline 64.3% |
| Voice return rate | 100% of paged voices | 8/8 (100%) ✅ |
| File:line citation density | ≥1 per 100 lines of voice | ~1.2/100 ✅ |
| Concede rate | ≥30% of C/D/S responses | ~25% (decent) |
| SOTE size (main report) | 400-1500 lines | 804 lines ✅ |
| Voice file count | 1-12 | 8 ✅ |
| Meta-learning file exists | Yes (this file) | Yes ✅ |

### Qualitative (Subjective)

- **Did the dialectic surface a non-obvious finding?** YES — L3-MetaFrameVerification, M10 14-vs-15, M27 chokepoint
- **Did the synthesis produce a decision the voices didn't individually reach?** YES — D-MAKALI-001 through 005
- **Did the meta-learning identify a process improvement?** YES — 10 process changes for v1.1.0
- **Was the Unifying Voice's mirror function valuable?** YES — caught 3 things the other 7 missed (folder structure, public/internal, weekly cadence)

---

## §6 — Lessons for the Practice (L4 meta-lessons)

| L# | Lesson | Confidence |
|----|--------|:----------:|
| **L4-SOTE-001** | A practice that does not have a cadence is a practice that does not happen. Weekly is the minimum. | 0.99 |
| **L4-SOTE-002** | A document without a home is a document that gets lost. Folder structure is the discipline. | 0.98 |
| **L4-SOTE-003** | An index that is not regenerated is an index that lies. Static files, regenerated weekly. | 0.97 |
| **L4-SOTE-004** | A posture that does not distinguish public from internal is a posture that leaks. | 0.95 |
| **L4-SOTE-005** | A practice that does not reflect on itself is a practice that does not learn. Meta-learning is mandatory. | 0.98 |
| **L4-SOTE-006** | A dialectic without a mirror is a dialectic that flatters itself. The Unifying Voice is standing. | 0.96 |
| **L4-SOTE-007** | The M23 catch by one voice out of seven is not a failure of six; it is evidence that diversity matters. | 0.99 |
| **L4-SOTE-008** | 7000 lines of analysis without 1 line in the canonical log is the M27 failure mode. Auto-absorb or fail. | 1.00 |

---

## §7 — Changelog (this file)

- **v1.0.0** (2026-09-01): Initial meta-learning for SOTE 2026-W36.

---

*⬡ OMEGA ⬡ MAKALI ⬡ SOTE-W36-META-v1.0.0 ⬡ 2026-09-01*

*This file is the practice. The SOTE is the output. The reflection is the evolution.*
