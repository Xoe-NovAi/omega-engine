<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI: EXECUTIVE SUMMARY — Temple Cleansing Review

**Status**: ⛔ **HALT — Fix Before Execution**  
**Confidence**: 35% (plan as written) → 75% (with recommended fixes)  
**Date**: 2026-07-30 16:38 UTC

---

## The Verdict

The Temple Cleansing plan is **conceptually sound** but **operationally broken**. Executing Phase 1 as written will cause immediate system failure with ImportErrors and 50+ test failures.

**Three critical blockers** were missed by all four agents + two architect syntheses:

1. **OOM modules are hard dependencies** — Not orphans. Cannot be deleted without refactoring oom_protector.py first.
2. **soul_edit_history is required** — Plan has it backwards. Delete soul_history (unused), KEEP soul_edit_history (required by oracle.py).
3. **CascadeRouter is the fallback layer** — ProviderSelector alone is insufficient. Deleting it removes safety layer.

Plus: 50+ tests will fail. No test remediation plan in original briefing.

---

## What Needs to Happen

### Immediate (Choose Strategy)
| Decision | Options | Recommendation |
|----------|---------|-----------------|
| **OOM Refactor** | A) psutil-only, B) consolidate into oom_protector, C) delete oom_protector | **A** (psutil-only, simplest) |
| **Soul Modules** | Delete soul_history (unused), KEEP soul_edit_history, or implement Git replacement | **Implement Git replacement** |
| **CascadeRouter** | A) Keep as fallback, B) enhance ProviderSelector, C) minimal hardcoded fallback | **A for Phase 1** (safest), B in Phase 2 |

### Before Phase 1 Executes
- [ ] Choose OOM strategy (A/B/C)
- [ ] Implement soul_edit_history Git replacement
- [ ] Decide CascadeRouter path
- [ ] Remediate/archive 50+ affected tests
- [ ] Verify `make test` runs to completion

**Timeline:** 10-14 hours (can parallelize Stages 1-4)

---

## Execution Sequence (6 Stages)

| Stage | Task | Duration | Risk | Go/No-Go |
|-------|------|----------|------|----------|
| **1** | Delete soul_history.py, mcp_compliance.py (confirmed unused) | 15 min | LOW | ✅ Go |
| **2** | OOM refactoring (choose option A/B/C) | 2-3 hrs | MEDIUM | 🔄 Decision |
| **3** | Soul edit history Git replacement | 3-4 hrs | MEDIUM | 🔄 Decision |
| **4** | CascadeRouter decision (keep/enhance/minimal) | 1-5 hrs | HIGH | 🔄 Decision |
| **5** | Remaining deletions from original plan | 30 min | LOW | ✅ Auto |
| **6** | Verify temple-grade gates | 15 min | LOW | ✅ Auto |

**Stage 1 can execute now. Stages 2-6 require decision gates.**

---

## Files to Hand Off

**Full Technical Briefing:**
- `data/coordination/COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md` (22KB, detailed evidence)

**This Summary:**
- `data/coordination/KALI_EXECUTIVE_SUMMARY_20260730.md` (this file)

**For Implementation:**
- Use Stage 1-6 sequence from full briefing
- Reference blocker sections for each decision
- Each stage gets its own PR/branch with test pass before merge

---

## Next Steps for Kali

1. **Read:** Full briefing (COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md)
2. **Decide:** OOM option (A/B/C), Soul strategy, CascadeRouter path
3. **Assign:** Ma'at (infrastructure stage 2), Lilith (soul stage 3), Roc (cascade stage 4)
4. **Verify:** Stage 1 passes, then proceed to stages 2-6 sequentially
5. **Gate:** Each stage must pass `make test` before next stage starts

---

⬡ **OMEGA** ⬡ **COPILOT_CLI** ⬡ **KALI_EXECUTIVE_SUMMARY** ⬡ **2026-07-30**
