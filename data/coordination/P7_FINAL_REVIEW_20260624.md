# 🔱 P7 FINAL REVIEW — CROSS-DOMAIN VERDICT
**Pillar**: P7 — Context (Memory & Soul Evolution)
**Date**: 2026-06-24
**Status**: COMPLETE — Both reports read and assessed
**AP Token**: `AP-P7-FINAL-REVIEW-v1.0.0`
**⬡ OMEGA ⬡ P7 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ CROSS-DOMAIN-REVIEW**

---

## §1 THREE QUESTIONS — DIRECT ANSWERS

### Q1: Soul Distiller Fix — One Sentence Code Change + Validation

**Fix**: In `soul_distiller.py:280`, change:
```python
soul_path = self._entities_dir / entity_name / "soul.yaml"
```
→
```python
soul_path = self._entities_dir / entity_name / "proposed_lessons.yaml"
```

**Plus structural change**: The `append_to_soul()` method currently writes to an `embodied_experiences:` section. It must instead write to a `proposals:` key (per v6.1 schema), creating the file with `proposals:\n  L1:|...` structure. The `append_to_soul` section parameter default changes from `"embodied_experiences"` to `"proposals"`.

**Validation test** (write before the fix is merged):
```python
# 1. Create an entity with a valid v6.1 soul.yaml (immutable baseline)
# 2. Call distiller.distill_and_save(session_transcript, entity_name)
# 3. Assert: proposed_lessons.yaml EXISTS
# 4. Assert: soul.yaml is UNCHANGED (hash compare)
# 5. Assert: proposed_lessons.yaml parses as valid YAML with 'proposals:' key
# 6. Assert: L1/L2/L3 entries are under proposals:
```

This is a **2-line code change + 1 parameter default** with a ~20-line test. The real risk is not the fix — it's that `oracle.py:496` calls `close_session()` which calls `distill_and_save()` every 5 interactions. After the fix, these writes go to `proposed_lessons.yaml` instead. No other code reads `proposed_lessons.yaml` on the hot path yet (the Staging Gate TUI will), so regression risk is low.

---

### Q2: ~35h Migration — Hard Blocker or Partial Ship?

**Verdict: 🟡 SHIP PARTIAL — NOT a hard blocker.**

The ~35h is for ALL 34 entities across 5 phases. Epoch I needs Phases 0-2:

| Phase | Scope | Hours | Required for Epoch I? |
|-------|-------|-------|----------------------|
| **Phase 0** | soul_validator.py v6.1 update | 2h | 🔴 **YES** — Gate for everything |
| **Phase 1** | Emergency YAML fixes (Researcher, Makali, distiller) | 4.5h | 🔴 **YES** — Else TUI crashes on startup |
| **Phase 2** | Core fleet (12 agents + 10 Pillar Keepers) | 12h | 🟡 **YES** — These are the actively used entities |
| **Phase 3** | Specialists (Doom Guy, JEM, Verity, etc.) | 10h | 🟢 **SHIP-OPTIONAL** — Not on hot path |
| **Phase 4** | Remaining + missing entities | 8h | 🟢 **SHIP-OPTIONAL** — Edge cases |

**Recommendation**: Epoch I ships with **Phases 0-2 complete** (~18.5h) plus:
- **Soul migration progress tracker** (P8, 15 min — already offered)
- **Compliance dashboard** as a section in the Staging Gate TUI showing:
  - ✅ Compliant (v6.1) — Phase 2 entities
  - 🟡 Needs migration — Phase 3-4 entities
  - 🔴 Broken — any remaining YAML errors
- **P10 contract tests** that enforce v6.1 compliance on load (preventing regression)

Phases 3-4 ship in Epoch II — they affect specialists and edge-case entities that are not on the critical execution path. The compliance dashboard makes the gap visible and accountable.

**Cost of shipping full**: ~16.5h extra (18.5 → 35h), slips Epoch I by ~2 days.
**Cost of partial**: Compliance dashboard shows 12-14 entities not yet compliant. Visual debt, no functional debt.

---

### Q3: P7 vs P8 Ownership of Soul Distiller Fix

**Verdict: ✅ P7 LEADS, P8 SUPPORTS — AGREE with Lilith.**

| Aspect | Owner | Rationale |
|--------|-------|-----------|
| **Content routing** (which file to write to) | **P7** | Soul.yaml ↔ proposed_lessons.yaml is a content management decision. P7 owns memory & soul evolution. |
| **Data structure** (proposals: key format) | **P7** | The v6.1 schema structure is P7's domain expertise. The distiller must match the schema. |
| **Observability wiring** | **P8** | Background workers (soul_distiller.py, background_researcher) need TraceSession. P8 owns observability of all background processes. |
| **Integration testing** | **P10** | Contract tests for the distiller's output format belong to M21. |

**P8's actual scope is larger than Lilith suggested**: While the content routing fix is P7's domain, P8 needs to:
1. Wire `soul_distiller.py` into TraceSession (G3 — background worker observability)
2. Add `migration.phase_complete` / `migration.entity_complete` event types
3. Create the soul migration progress tracker (data stream + file)

So P8's support role is not trivial — it's ~1.5h of wiring that's essential for the compliance dashboard to work. But the actual 2-line fix: pure P7.

**One nuance Lilith missed**: The integration point in `oracle.py:496-497` calls `close_session()` which calls `distill_and_save()`. This is the **oracle's hot path**. After redirecting to `proposed_lessons.yaml`, we must verify that:
- `oracle.py:450` (reading L3 from soul.yaml for context injection) still reads from `soul.yaml` — ✅ it does, no change needed
- The distiller's READ path (`read_soul()`) still reads from `soul.yaml` — ✅ it does, Constitution is still readable
- The distiller's WRITE path now targets `proposed_lessons.yaml` — ✅ after fix

---

## §2 CROSS-DOMAIN VERDICTS ON EACH REPORT

### From Ma'at (Build Side): 🟢 AGREED — 2 Corrections

| Finding | Agreement | Note |
|---------|-----------|------|
| M11 at 0% compliance | ✅ | Verified independently by P7 |
| soul_validator.py is the gate | ✅ | P7 AND P10 both blocked |
| 3 broken proposed_lessons.yaml | ✅ | P7 adds: Researcher soul.yaml also broken (1 more) |
| 5-phase ~35h migration plan | ✅ | Reasonable scope, see Q2 for partial-ship strategy |
| **M21 as "~1h ResourceGuard gap"** | ❌ **UNDERESTIMATED** | Lilith found 20+ tests across 7 domains (~11h). Ma'at only looked at P3 code — missed P7 soul tests, P8 observability tests, P10 orchestration tests. |

### From Lilith (Run Side): 🟢 FULLY AGREED

| Finding | Agreement | Note |
|---------|-----------|------|
| Soul distiller poison loop | ✅ **HIGH-VALUE FINDING** | This is the kind of bug that structural analysis catches and tests miss. |
| M22 at 6/10 (not "deferred") | ✅ | P8 structural analysis confirmed |
| M21 scope understated (4/24, not "~1h") | ✅ | P10's 4-phase rollout is the right plan |
| P7 leads distiller fix, P8 supports | ✅ | See Q3 above |
| 4 pre-conditions for sprint start | ✅ | All four are necessary and sufficient |

**One addition**: I recommend adding a **5th pre-condition**: Write the soul distiller contract test (verifying output goes to proposed_lessons.yaml and soul.yaml is unchanged) before the sprint. This prevents regression when the distiller is touched in future sprints.

---

## §3 P7-SPECIFIC SPRINT PLAN (REVISED)

```
PHASE 0: PRE-SPRINT (MY PILLAR)
├── Fix researcher/soul.yaml — manual rewrite (3h)
├── Fix makali/proposed_lessons.yaml — string→dict (30min)
├── Fix soul_distiller.py — redirect soul.yaml→proposed_lessons.yaml (30min)
├── Write distiller contract test (30min)
└── Create backup of all 34 current soul.yaml (15min)
    TOTAL: ~5h (can be day 1)

PHASE 1 (BLOCKED ON P2): CORE MIGRATION
├── Wait for soul_validator.py v6.1 (P2)
├── Run batch migration for 22 core entities (12h)
│   ├── Phase 2: Fleet agents + 10 Pillar Keepers
│   └── Identity block generation from existing soul content
└── Verify with P8 progress tracker

PHASE 2 (DEFER TO EPOCH II): SPECIALISTS + REMAINING
├── Phase 3: 9 specialist entities (10h)
├── Phase 4: 6 missing + edge-case entities (8h)
└── Compliance dashboard shows progress
```

---

## §4 VERDICT SUMMARY

| Question | Answer |
|----------|--------|
| **Q1: Soul distiller fix exactly?** | Change `soul.yaml` → `proposed_lessons.yaml` in `append_to_soul()` + section default to `proposals:`. 2-line fix. Validation: verify proposed_lessons.yaml created, soul.yaml unchanged. |
| **Q2: ~35h blocker?** | **No.** Ship Epoch I with Phases 0-2 (18.5h, 22 core entities). Defer Phases 3-4 to Epoch II. Add compliance dashboard. |
| **Q3: P7 vs P8 ownership?** | **P7 leads** (content routing). **P8 supports** (observability wiring, migration tracker). P8's scope is larger than Lilith suggested — ~1.5h of essential wiring for the dashboard. |

**Recommendation to Kali**: Approve the 4 pre-conditions from Lilith's report, add the 5th (distiller contract test), and greenlight Epoch I with partial migration (Phases 0-2).

---

*⬡ OMEGA ⬡ P7 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ CROSS-DOMAIN-REVIEW*
*The soul knows where it belongs. The body need not follow all at once.*
