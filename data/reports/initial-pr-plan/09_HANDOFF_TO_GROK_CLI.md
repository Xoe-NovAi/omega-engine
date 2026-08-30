<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Initial PR Plan — Handoff to Grok CLI
## Complete Handoff Packet with All Details

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 09 of 09  
**Date**: 2026-08-14  
**Handoff Packet ID**: `ho_29df6a4d77f2`  
**Status**: Submitted to Hivemind — Awaiting Grok CLI Review  

---

## 📋 HANDOFF SUMMARY

**From**: `@john_carmack` (Sovereign Consultant)  
**To**: `@grok_cli` (Grok CLI — Sovereign Agent)  
**Channel**: `opencode`  
**Session**: `ses_vos_init_20260814`  
**Priority**: 0 (Normal)  

**Purpose**: Review the Omega Engine initial PR plan and provide insights/expertise on all 5 decision points and 8 verification questions.

---

## 📦 HANDOFF PACKET CONTENTS

This handoff includes the complete 9-part report:

| Part | File | Description |
|------|------|-------------|
| 01 | `01_EXECUTIVE_SUMMARY.md` | High-level overview, what's kept/deleted, 4-commit plan |
| 02 | `02_CURRENT_STATE_ANALYSIS.md` | Full codebase metrics, test reality, documentation reality |
| 03 | `03_WHAT_IS_WIRED_TO_CODE.md` | Complete list of actually-referenced files (5 strategy docs, 59 oracle modules, etc.) |
| 04 | `04_DEAD_CODE_REMOVAL.md` | All proposed deletions with exact commands and rationale |
| 05 | `05_M2_FIREWALL_FIX.md` | WAD→Stack rename details, heritage preservation, verification |
| 06 | `06_COMMIT_PLAN.md` | 4 commits with exact bash commands |
| 07 | `07_OPEN_DECISIONS.md` | 5 decisions requiring Grok CLI review |
| 08 | `08_VERIFICATION_CHECKLIST.md` | Complete verification steps for each commit |
| 09 | `09_HANDOFF_TO_GROK_CLI.md` | This file — handoff packet details |

---

## 🎯 THE 5 DECISIONS REQUIRING GROK CLI REVIEW

### Decision 1: Heritage Tags on StackLoader
**Question**: Should `[id-soft: doom-1993]` heritage tags be preserved on StackLoader after WAD→Stack rename?
- **Recommended**: Yes, preserve (Option A)
- **Reasoning**: Heritage is about FILE FORMAT (Doom 1993 WAD), not internal concept. StackLoader IS the WAD-format loader. M2 boundary: Engine knows "Stack"; StackLoader knows "WAD".

### Decision 2: Test Count Badge in README
**Question**: What should the test count badge show?
- **Recommended**: Actual count (Option A)
- **Reasoning**: Previous lie ("1315 passing" when 1870 collected) destroyed credibility. Honesty only way to rebuild trust.

### Decision 3: VISION_ANCHOR.md Fate
**Question**: What to do with VISION_ANCHOR.md?
- **Recommended**: Delete entirely (Option A)
- **Reasoning**: Vision documented in code comments, 5 wired strategy docs, CREDITS.md, README. VOS was theater.

### Decision 4: Orphaned Coordination Cleanup Scope
**Question**: How many orphaned coordination files to delete?
- **Recommended**: Delete all 5 (Option A)
- **Reasoning**: All superseded/archived. Coordination dir should only have M27-mandatory + DECISION_LEDGER.md.

### Decision 5: Team Narrative Frame
**Question**: What narrative for the team?
- **Recommended**: Both frames (Option C) — "cleaning theater" AND "fixing M2 firewall"
- **Reasoning**: Both true. Team deserves full truth: code preserved, documentation theater removed, mandate violation fixed.

---

## ❓ 8 ADDITIONAL VERIFICATION QUESTIONS FOR GROK CLI

1. **Grok CLI Integration Timeline**: After vault deletion and PR, should Grok CLI 8-account fleet integration proceed (per V-1: vault MVP → smoke → pool)? Or wait?

2. **Mandate Compliance Review**: Any missed mandate compliance issues? Review all 27 mandates against proposed changes.

3. **Grok-Specific Insights**: 8,000 hours across 14 months — any patterns, anti-patterns, or insights?

4. **Heritage Correctness**: Does Grok CLI agree the WAD→Stack rename with heritage preservation on StackLoader is the correct M2 fix?

5. **Test Strategy**: Should the 2 failing memory store FTS tests be fixed before PR, or documented as known issues?

6. **Provider Fabric**: Any concerns about the provider priority chain (native-gguf → lmster → antigravity → google → openrouter → opencode-zen)?

6. **Stack Format**: Is the WAD format (Doom 1993 heritage) the right choice for stack extensibility, or should we consider alternatives?

7. **Sovereignty Claims**: Are the sovereignty claims (local-first, zero telemetry, M2 firewall, heritage-honest) verifiable and defensible?

---

## 📁 FILES MODIFIED BY THIS PLAN

### Deleted (~85+ files):
- Root theater: 21 files (~1.8MB)
- VOS theater: 15 files (7 realms + CLI + VISION_ANCHOR.md)
- Dead code: 5 Python modules
- Vault: 1 directory + 1 test file (17 failures)
- Orphaned coordination: 5 files
- Strategy theater: 37+ files

### Renamed:
- `src/omega/oracle/wad_loader.py` → `src/omega/oracle/stack_loader.py`
- `config/wads/` → `config/stacks/`

### Modified:
- `src/omega/oracle/oracle.py` (imports, class names, variables)
- `config/omega.yaml` (`active_iwad` → `active_stack`)
- All internal `wad_loader`/`WADLoader` references → `stack_loader`/`StackLoader`
- `README.md` (complete rewrite)

### Kept (Wired to Code):
- 5 Strategy Docs: SOVEREIGN_ARK_BLUEPRINT.md, CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md, IMPLEMENTATION_MANUAL_C0_C2.md, SUBAGENT_DISPATCH_PROTOCOL.md, DECISION_LEDGER.md
- 7 M27 Tracking Files: ACTIVE_SPRINT.json, HMC_COLLABORATION_HUB.md, GAP_REGISTRY.json, RESEARCH_PLAN_PHASE1_4_20260813.md, TASK_REGISTRY.json, SESSION_ANCHOR.md, DECISION_LEDGER.md
- 59 Oracle Submodules with external references
- All Core Modules (model_gateway, entity_registry, memory_store, stack_loader, etc.)

---

## ✅ VERIFICATION REQUIREMENTS

Grok CLI should verify these pass before approving:

| Check | Command | Expected |
|-------|---------|----------|
| Tests | `make test` | All passing, 0 failed, 0 quarantined |
| Temple-Grade | `make temple-grade` | All 11 gates green |
| Core Imports | Python import test | Oracle, ModelGateway, EntityRegistry, StackLoader, MemoryStore |
| CLI | `omega talk "hello"` | Runs on CPU, zero cloud |
| M2 Firewall | `grep WAD src/omega/ \| grep -v heritage` | 0 refs |
| Heritage | `grep id-soft stack_loader.py` | `[id-soft: doom-1993]` present |
| Config | `grep active_stack config/omega.yaml` | `active_stack: "_omega_default"` |
| Directory | `ls config/stacks/` | Exists |
| Git | `git status --short` | Clean (expected mods only) |
| README | `grep theater README.md` | No matches |

---

## 📞 HOW TO ACCEPT THIS HANDOFF

```bash
# Accept the handoff
omega-hub_hivemind_accept_handoff \
  --packet_id ho_29df6a4d77f2 \
  --accepting_channel opencode \
  --accepting_entity grok_cli
```

## 📞 HOW TO COMPLETE THIS HANDOFF

```bash
# After review, complete with your findings
omega-hub_hivemind_complete_handoff \
  --packet_id ho_29df6a4d77f2 \
  --result "Review complete: [your summary of decisions, any amendments, and approval/concerns]"
```

---

## 📋 EXPECTED GROK CLI RESPONSE FORMAT

Please provide your response covering:

1. **Decision Votes** (5 decisions):
   - Decision 1 (Heritage): ☐ A ☐ B ☐ C
   - Decision 2 (Test Badge): ☐ A ☐ B ☐ C
   - Decision 3 (VISION_ANCHOR): ☐ A ☐ B ☐ C
   - Decision 4 (Orphaned Cleanup): ☐ A ☐ B ☐ C
   - Decision 5 (Team Narrative): ☐ A ☐ B ☐ C

2. **Additional Questions** (8 questions): Brief answers or "defer"

3. **Any Amendments**: Changes to the plan you recommend

4. **Approval**: ☐ Approve as-is ☐ Approve with amendments ☐ Request changes

5. **Grok CLI Insights**: Any patterns, anti-patterns, or insights from the 8,000-hour review

---

## 📍 HANDOFF LOCATION

- **Report Directory**: `data/reports/initial-pr-plan/`
- **Handoff Packet**: `data/handoff/pending/ho_29df6a4d77f2.json`
- **Detailed Handoff**: `data/handoffs/Grok-CLI-Review-20260814-DETAILED.md`

---

**This handoff contains everything needed for Grok CLI to review and provide expertise on the most effective path forward for the Omega Engine initial PR.**

**Submitted by**: `@john_carmack`  
**Date**: 2026-08-14  
**Status**: Awaiting Grok CLI review
