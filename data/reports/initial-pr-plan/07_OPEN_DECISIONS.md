<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Initial PR Plan — Open Decisions
## 5 Decisions Requiring Grok CLI Review

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 07 of 09  
**Date**: 2026-08-14  

---

## 🎯 DECISION 1: HERITAGE TAGS ON STACKLOADER

### The Question
Should the `[id-soft: doom-1993]` heritage tags be preserved on `StackLoader` after the WAD→Stack rename?

### Context
- The `StackLoader` class intentionally knows about WAD-format files (Doom 1993 lump structure)
- The heritage tag `[id-soft: doom-1993]` on `StackLoader` is **correct** — it's the Doom 1993 WAD format
- M2 Firewall requires: Engine knows "Stack" interface; StackLoader knows "WAD" format
- The rename is: internal concept "WAD" → "Stack", but loader's domain knowledge remains

### Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Preserve** (Recommended) | Keep `[id-soft: doom-1993]` on StackLoader | Maintains Doom provenance; correct architectural boundary | None |
| **B) Remove** | Strip heritage tags from StackLoader | Simplifies rename | Loses Doom provenance; historically inaccurate |
| **C) Move** | Move tags to config/stacks/ directory or separate file | Separates concerns | Wrong level — loader IS the translation layer |

### Recommendation
**Option A — Preserve heritage tags on StackLoader.**

**Reasoning**: The heritage is about the FILE FORMAT (Doom 1993 WAD), not the internal concept. StackLoader IS the WAD-format loader. The M2 firewall boundary is exactly here: Engine knows "Stack"; StackLoader knows "WAD". The heritage tag correctly documents what StackLoader loads.

### Grok CLI Input Required
**Does Grok CLI agree the `[id-soft: doom-1993]` heritage tags should be preserved on StackLoader?**

- [ ] Yes, preserve (Option A)
- [ ] No, remove (Option B)
- [ ] Move to config/stacks/ (Option C)
- [ ] Other: _______________

---

## 🎯 DECISION 2: TEST COUNT BADGE IN README

### The Question
What should the test count badge show in the README after cleanup?

### Context
- Previous README lied: "1315 passing tests" when 1870 were collected
- After cleanup, actual test count will be whatever it is
- We must NOT lie again — honesty is the only correct answer

### Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Actual count** (Recommended) | e.g., "tests-1200_passing" | Honest, transparent | Might look low vs competitors |
| **B) "Green" without count** | e.g., "tests-passing" | Honest but vague | Less informative |
| **C) Omit badge** | No badge, link to results | Can't lie if no badge | Less visible |

### Recommendation
**Option A — Show actual count.**

**Reasoning**: The previous lie ("1315 passing" when 1870 collected) destroyed credibility. Honesty is the only way to rebuild trust. The actual count is what it is — if it's 900, it's 900. We don't inflate.

### Grok CLI Input Required
**What should the README test count badge show?**

- [ ] Actual count (Option A)
- [ ] "Green" without count (Option B)
- [ ] Omit badge (Option C)
- [ ] Other: _______________

---

## 🎯 DECISION 3: VISION_ANCHOR.MD FATE

### The Question
What to do with `data/coordination/VISION_ANCHOR.md`?

### Context
- This file has 1 code reference — in the deleted `realm_cli.py` theater CLI
- The content is good sovereign vision theory (7 realms, cognitive sovereign, etc.)
- The VOS implementation was theater — 0 code imports from `data/realms/`
- The vision theory itself is valuable but not wired to execution

### Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Delete entirely** (Recommended) | Remove completely | Clean; vision in code comments + 5 wired docs | Loses the consolidated vision doc |
| **B) Archive** | Move to `docs/archive/` | Preserves theory | Still exists but not mandatory |
| **C) Keep in coordination/** | Leave as-is | Available for reference | Clutters coordination dir |

### Recommendation
**Option A — Delete entirely.**

**Reasoning**: The vision is documented in:
1. Code comments throughout the codebase
2. The 5 wired strategy docs (especially SOVEREIGN_ARK_BLUEPRINT.md)
3. The CREDITS.md heritage registry
4. The README architecture section

The VISION_ANCHOR.md was part of the VOS theater. Deleting it cleans the coordination directory. The vision theory isn't lost — it's distributed where it's actually used.

### Grok CLI Input Required
**What should happen to VISION_ANCHOR.md?**

- [ ] Delete entirely (Option A)
- [ ] Archive to docs/archive/ (Option B)
- [ ] Keep in coordination/ (Option C)
- [ ] Other: _______________

---

## 🎯 DECISION 4: ORPHANED COORDINATION CLEANUP SCOPE

### The Question
How many orphaned coordination files should we delete?

### Context
We have these archived/superseded files in `data/coordination/`:

| File | Status | Size |
|------|--------|------|
| `KALI_DEV_ROADMAP_20260811.md` | Absorbed into ACTIVE_SPRINT.json | ~15KB |
| `KALI_OVERSIGHT_PORTFOLIO_20260811.md` | Superseded | ~11KB |
| `KNOWLEDGE_GAPS_RESEARCH_20260811.md` | 12-gap scan, superseded by v3.2.0 | ~15KB |
| `RESEARCH_JOB_BOARD.yaml` | Not in mandatory flow | ~57KB |
| `SONNET_4_6_REVIEW_20260814.md` | Review artifact | ~22KB |

### Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Delete all 5** (Recommended) | Cleanest, simplest | Minimal coordination dir | Loses historical artifacts |
| **B) Delete 3, keep 2** | Keep KALI_DEV_ROADMAP + KALI_OVERSIGHT | Preserves some history | Inconsistent cleanup |
| **C) Keep all** | Minimal change | No loss | Clutters coordination dir |

### Recommendation
**Option A — Delete all 5.**

**Reasoning**: 
- `KALI_DEV_ROADMAP` → absorbed into ACTIVE_SPRINT.json (Tier-0 SSOT)
- `KALI_OVERSIGHT_PORTFOLIO` → superseded by current oversight
- `KNOWLEDGE_GAPS_RESEARCH` → superseded by RESEARCH_PLAN_PHASE1_4_20260813.md v3.2.0
- `RESEARCH_JOB_BOARD.yaml` → not in mandatory flow
- `SONNET_4_6_REVIEW` → review artifact, not needed post-review

The coordination directory should only contain M27-mandatory files + DECISION_LEDGER.md.

### Grok CLI Input Required
**How many orphaned coordination files should we delete?**

- [ ] Delete all 5 (Option A)
- [ ] Delete 3, keep 2 (Option B)
- [ ] Keep all (Option C)
- [ ] Other: _______________

---

## 🎯 DECISION 5: TEAM NARRATIVE FRAME

### The Question
What narrative do we give the team about why files are being deleted?

### Context
The team has invested 8,000 hours. Deleting their work can feel like rejection. We need a frame that honors their contribution while explaining the cleanup.

### Options

| Option | Frame | Pros | Cons |
|--------|-------|------|------|
| **A) "Cleaning theater"** | We're deleting documentation never wired to execution | Honest about what's being removed | May feel dismissive |
| **B) "Fixing M2 firewall"** | This is a mandate compliance issue | Technical, objective | Doesn't explain root theater deletion |
| **C) Both A + B** (Recommended) | We're cleaning theater AND fixing a critical mandate violation | Complete, honest, technical | More complex message |

### Recommendation
**Option C — Both frames.**

**Reasoning**: Both statements are true:
1. We ARE cleaning theater — VOS realms, tracking architecture (5 of 6 files), most docs, root garbage, vault, 5 dead modules were never wired to execution
2. We ARE fixing a critical mandate violation — 344 WAD references in engine core violate M2

The team deserves the full truth: their documentation work was theater (not their fault — the architecture wasn't wired), and we're fixing a real mandate violation. This honors their code contributions while being honest about the documentation.

### Suggested Message to Team:
> "We're doing a nuclear cleanup for the initial PR. Two things:
> 1. **Cleaning theater**: ~2.5MB of documentation (VOS realms, 37+ strategy docs, root session dumps, tracking architecture) that was never wired to execution. The code works; the docs were theater.
> 2. **Fixing M2 firewall**: 344 internal 'WAD' references in src/omega/ violated the Engine-Stack Firewall. We're renaming the internal concept to 'Stack' while preserving Doom heritage on the loader.
> 
> Your CODE contributions are preserved and working. The DOCUMENTATION theater is being removed so the initial PR is honest and shippable."

### Grok CLI Input Required
**What narrative frame should we use for the team?**

- [ ] "Cleaning theater" (Option A)
- [ ] "Fixing M2 firewall" (Option B)
- [ ] Both A + B (Option C) — Recommended
- [ ] Other: _______________

---

## 📋 ADDITIONAL GROK CLI QUESTIONS

### Question 6: Grok CLI Integration Timeline
After the vault is deleted and the PR is out, should the Grok CLI 8-account fleet integration proceed (per the V-1 ticket sequence: vault MVP → smoke → pool)? Or wait for a later PR?

### Question 7: Mandate Compliance Review
Are there any mandate compliance issues I've missed? Review all 27 mandates against the proposed changes.

### Question 8: Grok-Specific Insights
The 8,000 hours of development across 14 months — any patterns, anti-patterns, or insights Grok CLI wants to add?

---

## 📋 DECISION SUMMARY FOR GROK CLI

| Decision | Recommended | Grok CLI Vote |
|----------|-------------|---------------|
| 1. Heritage on StackLoader | Preserve (A) | ☐ A ☐ B ☐ C |
| 2. Test count badge | Actual count (A) | ☐ A ☐ B ☐ C |
| 3. VISION_ANCHOR.md | Delete (A) | ☐ A ☐ B ☐ C |
| 4. Orphaned coordination | Delete all 5 (A) | ☐ A ☐ B ☐ C |
| 5. Team narrative | Both frames (C) | ☐ A ☐ B ☐ C |

**Please respond with your votes and any comments on each decision.**

---

**Next**: See `08_VERIFICATION_CHECKLIST.md` for complete verification steps.
