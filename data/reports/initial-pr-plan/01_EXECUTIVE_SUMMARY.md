<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Initial PR Plan — Executive Summary
## Comprehensive Report: All Analysis, Decisions, and Proposed Changes

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Date**: 2026-08-14  
**Author**: `@john_carmack` (Sovereign Consultant)  
**Status**: Complete — Ready for Implementation  

---

## 📊 THE SITUATION

The Omega Engine has accumulated **~8,000 hours** of self-directed development across **14 months**, **4 legacy repositories**, and **3 partitions** (Root, omega_library, omega_vault). The Vision Operating System (VOS v1.0) instantiation attempted to "capture the full vision" but created **7 sovereign realm YAML files** and a **disconnected CLI** that are **NOT wired to the execution path**.

**The Core Problem**: Architectural bloat, simulated rigor, and a complete breakdown of the **Engine-Stack Firewall (M2)**. The system has **344 internal "WAD" references** in `src/omega/` that violate Mandate 2 (Engine-Stack Firewall). The README promises "1315 passing tests" but **1870 tests are collected** — a lie by vanity count. The VOS was **documentation theater**, not execution.

**The Goal**: Get to an initial PR that is **honest, working, and sovereign** — no more cargo-cult engineering, no more quarantined-test lies, no more architectural theater.

---

## 🎯 THE 4-COMMIT PLAN (HIGH-LEVEL)

| Commit | Focus | Time |
|--------|-------|------|
| **1** | Delete Root Theater + VOS Theater + Actual Dead Code + Vault | 10 min |
| **2** | Fix M2 Firewall (Rename WAD → Stack Internally) | 20 min |
| **3** | Honest README + Verification | 10 min |
| **4** | Clean Coordination Directory of Orphaned Files | 5 min |
| **Verification** | Full test suite + temple-grade gates | 20 min |
| **Total** | | **~1 hour 15 min** |

---

## ✅ WHAT IS KEPT (Actually Wired to Code)

### Strategy Docs with Code References (5 files):
1. `SOVEREIGN_ARK_BLUEPRINT.md` (3 refs) — Strategy SSOT, wired into `entity_workspace.py:295` and `ics.py:239-245`
2. `CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` (2 refs) — SSOT for `token_estimator.py:4` and `test_context_packer_v3.py:4`
3. `IMPLEMENTATION_MANUAL_C0_C2.md` (many inline refs) — Mandate mapping C-0 through C-11 throughout codebase
4. `SUBAGENT_DISPATCH_PROTOCOL.md` (2 refs) — Comments in `link_p9_runtime.py:14` and `subagent_dispatcher.py:10`
5. `DECISION_LEDGER.md` (6 refs) — Actually referenced in code

### M27-Mandatory Tracking Files (7 files):
- `ACTIVE_SPRINT.json` — Tier-0 SSOT for 6-step flow
- `HMC_COLLABORATION_HUB.md` — Team sync, NEXT_ACTION pointer
- `GAP_REGISTRY.json` — Tier-1a: authoritative gap-ID map
- `RESEARCH_PLAN_PHASE1_4_20260813.md` — Tier-1: research gap catalog R1-R38
- `TASK_REGISTRY.json` — Tier-3: subagent task sessions
- `SESSION_ANCHOR.md` — Tier-4: session continuity
- `DECISION_LEDGER.md` — Immutable decision history (6 code refs)

---

## 🗑️ WHAT IS DELETED (Theater/Dead Code)

### 5 Python Modules with 0 References:
- `state_manager.py`, `pool_tracker.py`, `mandate_enforcer.py`, `link_p9_runtime.py`, `lifecycle_harvester.py`

### Vault Code (17 Failing Tests):
- `src/omega/vault/` + `tests/unit/test_vault_core.py`

### Root Theater:
- 627KB session dump, 275KB P9.md, 181KB copy-paste, 5 Screenshot*.png, quantum_error_correction_2026_article.md, youtube-links*.txt, old-claude-sys-prompt.md, trim_scope.py, debug_test.py, test.txt, file, tui.json

### VOS Theater (0 code imports):
- `data/realms/` (7 realm state YAML files)
- `src/omega/cli/realm_cli.py` (theater CLI)
- `data/coordination/VISION_ANCHOR.md` (1 ref in theater CLI)

### Orphaned Coordination Files:
- `KALI_DEV_ROADMAP_20260811.md`, `KALI_OVERSIGHT_PORTFOLIO_20260811.md`, `KNOWLEDGE_GAPS_RESEARCH_20260811.md`, `RESEARCH_JOB_BOARD.yaml`, `SONNET_4_6_REVIEW_20260814.md`

### 37+ Strategy Docs with 0 Code References:
- All P1-P9.md in root, all session files, most docs/strategy/ docs

---

## 🔧 THE M2 FIREWALL FIX

**The Violation**: 344 internal "WAD" references in `src/omega/` violate Mandate 2 (Engine-Stack Firewall).

**The Fix**: Rename internal concept from "WAD" to "Stack" while **preserving** `[id-soft: doom-1993]` heritage tags on `StackLoader` (it loads WAD-format files — that's correct).

**The Principle**: Engine knows "Stack" interface; StackLoader knows "WAD" format. Heritage tags on the loader are intentionally correct.

---

## 📋 VERIFICATION CHECKLIST (Must Pass Before Push)

1. `make test` — XXX passed, 0 failed, 0 quarantined
2. `make temple-grade` — All 11 gates green (M2 must pass)
3. Core imports work: Oracle, ModelGateway, EntityRegistry, StackLoader, MemoryStore
4. CLI works: `omega talk "hello"` runs on CPU, zero cloud
3. No WAD refs in engine core: `grep -rn "WAD" src/omega/ | grep -v "\[id-soft:" | grep -v "doom-1993" | wc -l` → 0
4. Clean git status: Only modified README.md, config/omega.yaml, new/renamed source files

---

## 📁 REPORT STRUCTURE

This report is split into multiple parts:

| Part | File | Contents |
|------|------|----------|
| 01 | `01_EXECUTIVE_SUMMARY.md` | This file — high-level overview |
| 02 | `02_CURRENT_STATE_ANALYSIS.md` | Full codebase analysis with metrics |
| 03 | `03_WHAT_IS_WIRED_TO_CODE.md` | Complete list of actually-referenced files |
| 04 | `04_DEAD_CODE_REMOVAL.md` | All proposed deletions with rationale |
| 05 | `05_M2_FIREWALL_FIX.md` | WAD→Stack rename details |
| 06 | `06_COMMIT_PLAN.md` | 4 commits with exact bash commands |
| 07 | `07_OPEN_DECISIONS.md` | 5 decisions for Grok CLI review |
| 08 | `08_VERIFICATION_CHECKLIST.md` | Complete verification steps |
| 09 | `09_HANDOFF_TO_GROK_CLI.md` | Handoff packet details |

---

**Next**: See `02_CURRENT_STATE_ANALYSIS.md` for the full codebase analysis.
