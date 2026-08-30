# 🔱 Omega Engine Initial PR Plan — Current State Analysis
## Full Codebase Metrics and Reality Check

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 02 of 09  
**Date**: 2026-08-14  

---

## 📊 CODEBASE SIZE & STRUCTURE

| Metric | Value | Reality Assessment |
|--------|-------|-------------------|
| Python source files (`src/omega/`) | **291 files** | 81,620 lines of code |
| Oracle directory (`src/omega/oracle/`) | **74 files** | 26,876 lines — god module |
| Test files (`tests/`) | **174 files** | 1,870 tests collected |
| Quarantine file (`tests/quarantine.txt`) | **0 lines** | Empty — previous "97 quarantined" claim was FALSE |
| Documentation (`docs/`) | **1,419 markdown files** | Only **5** have code references |
| Data coordination (`data/coordination/`) | **7,182 files** | Only **1** wired to code |
| Root directory theater | **627KB session dump**, **275KB P9.md**, **181KB copy-paste**, **5 Screenshot*.png** | Garbage |

---

## 📁 SRC/OMEGA/ DIRECTORY BREAKDOWN

| Subdirectory | Files | Lines | % of Total |
|--------------|-------|-------|------------|
| `oracle/` | 74 | 26,876 | 32.9% |
| `memory/` | 18 | 7,046 | 8.6% |
| `library/` | 15 | 4,481 | 5.5% |
| `observability/` | 12 | 4,074 | 5.0% |
| `cli/` | 8 | 3,625 | 4.4% |
| `research/` | 11 | 3,493 | 4.3% |
| `infra/` | 9 | 3,090 | 3.8% |
| `workers/` | 8 | 2,367 | 2.9% |
| `vault/` | 6 | 2,039 | 2.5% |
| `integrations/` | 7 | 1,678 | 2.1% |
| `ingestion/` | 6 | 1,570 | 1.9% |
| `benchmarks/` | 4 | 1,246 | 1.5% |
| `model_registry/` | 5 | 1,180 | 1.4% |
| `coordination/` | 6 | 1,070 | 1.3% |
| `tools/` | 5 | 1,020 | 1.2% |
| `privacy/` | 4 | 992 | 1.2% |
| `training/` | 4 | 940 | 1.2% |
| `audit/` | 4 | 907 | 1.1% |
| `mcp_core/` | 4 | 861 | 1.1% |
| `monitoring/` | 4 | 844 | 1.0% |
| **Other (20 dirs)** | ~70 | ~12,000 | ~15% |

---

## 🧪 TEST SUITE REALITY

### Test Collection Results:
```
1870 tests collected in 6.98s
```

### Core Module Test Results (94 tests):
| Test File | Passed | Failed | Notes |
|-----------|--------|--------|-------|
| `test_oracle.py` | 24 | 0 | Core routing works |
| `test_entity_registry.py` | 18 | 0 | Entity system works |
| `test_model_gateway.py` | 17 | 0 | Provider fabric works |
| `test_stack_loader.py` | 15 | 0 | WAD/Stack loading works |
| `test_memory_store.py` | 18 | 2 | 2 FTS failures (fixable) |
| **Total** | **92** | **2** | **97.9% pass rate** |

### Vault Tests (17 FAILURES):
| Test | Failure Type |
|------|-------------|
| `test_store_and_retrieve_credential` | ValidationError: encrypted_blob must be age-armored |
| `test_store_multiple_credentials` | AttributeError: no 'store_credential' method |
| `test_credential_status_lifecycle` | AttributeError: no 'store_credential' method |
| `test_list_credentials` | AttributeError: no 'store_credential' method |
| `test_lease_protocol` | ValidationError: encrypted_blob format |
| `test_lease_conflict` | ValidationError: encrypted_blob format |
| `test_lease_expiry` | ValidationError: encrypted_blob format |
| `test_audit_log_integrity` | ValidationError: encrypted_blob format |
| `test_vault_integrity_verification` | ValidationError: encrypted_blob format |
| `test_daily_counter_reset` | ValidationError: encrypted_blob format |
| `test_reconcile_quotas` | ValidationError: encrypted_blob format |
| `test_initialize_fleet_vault` | ImportError: cannot import 'initialize_fleet_vault' |
| `test_vault_persistence` | ValidationError: encrypted_blob format |
| `test_wrong_passphrase_fails` | ValidationError: encrypted_blob format |
| `test_empty_vault` | AttributeError: no 'verify_integrity' method |
| `test_duplicate_credential_rejected` | ValidationError: encrypted_blob format |
| `test_lease_release_wrong_agent_fails` | ValidationError: encrypted_blob format |

**Verdict**: Vault is dead code with broken API. Not used by core flow. Delete.

---

## 📚 DOCUMENTATION REALITY

### Strategy Docs with Code References (ONLY 5 of 45):

| Doc | Code Refs | Usage |
|-----|-----------|-------|
| `SOVEREIGN_ARK_BLUEPRINT.md` | **3** | `entity_workspace.py:295`, `ics.py:239-245` |
| `CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` | **2** | `token_estimator.py:4`, `test_context_packer_v3.py:4` |
| `IMPLEMENTATION_MANUAL_C0_C2.md` | **Many inline** | C-0 through C-11 throughout codebase |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | **2** | Comments in `link_p9_runtime.py:14`, `subagent_dispatcher.py:10` |
| `DECISION_LEDGER.md` | **6** | Actually referenced in code |

**All other 40 strategy docs have 0 code references** — documentation theater.

### Coordination Files with Code References (ONLY 1 of 7):

| File | Code Refs | Usage |
|------|-----------|-------|
| `DECISION_LEDGER.md` | **6** | Actually wired in code |

### M27-Mandatory Tracking Files (0 code refs but MANDATORY):

| File | M27 Tier | Purpose |
|------|----------|---------|
| `ACTIVE_SPRINT.json` | Tier-0 | SSOT for "what we build" |
| `HMC_COLLABORATION_HUB.md` | Tier-2 | Team sync, NEXT_ACTION pointer |
| `GAP_REGISTRY.json` | Tier-1a | Authoritative gap-ID map |
| `RESEARCH_PLAN_PHASE1_4_20260813.md` | Tier-1 | Research gap catalog R1-R38 |
| `TASK_REGISTRY.json` | Tier-3 | Subagent task sessions |
| `SESSION_ANCHOR.md` | Tier-4 | Session continuity for @kali |

---

## 🏗️ ORACLE MODULE DEPENDENCY GRAPH

### Core Imports (oracle.py imports these 25 modules):
```
session_manager, orchestrator, model_gateway, health_monitor, stack_loader,
entity_registry, security (TDPGate, TaintedData), pii_masker, context_builder,
iris.matcher, observability, errors, cvar_table, memory_store, astrology,
orchestration.triage_router, state, governance.config_resolver,
governance.dispatch_registry
```

### Oracle Submodules with External References (74 total, 59 have 1+ refs):

| Module | External Refs | Status |
|--------|--------------|--------|
| `search` | 12 | Core runtime |
| `somatic_state` | 10 | State management |
| `session_lifecycle` | 10 | Session management |
| `audience_calibrator` | 8 | Evaluation runner |
| `admission_controller` | 8 | Model gateway integration |
| `token_estimator` | 6 | Context packing |
| `sovereign_search_service` | 5 | Search orchestration |
| `search_router` | 5 | Search tier routing |
| `memavailable` | 5 | Memory monitoring |
| `world_state` | 4 | World state tracking |
| `skeptical_verifier` | 4 | Verification pipeline |
| `failure_registry` | 4 | Failure tracking |
| ... 30 more with 1-3 refs | | Active code |

### Zero-Reference Oracle Modules (DELETE):
| Module | Refs | Action |
|--------|------|--------|
| `state_manager` | 0 | DELETE |
| `pool_tracker` | 0 | DELETE |
| `mandate_enforcer` | 0 | DELETE |
| `link_p9_runtime` | 0 | DELETE |
| `lifecycle_harvester` | 0 | DELETE |

---

## 🔥 THE M2 FIREWALL VIOLATION

### The Numbers:
```
grep -rn "WAD" src/omega/ --include="*.py" | grep -v "__pycache__" | wc -l
→ 344 references
```

### Breakdown:
- **344** internal "WAD" references in `src/omega/`
- **0** heritage `[id-soft: doom-1993]` tags on these references (they're internal concept, not heritage)
- **Heritage tags** exist on `StackLoader` class — **correctly placed**

### The Violation:
Mandate 2 (Engine-Stack Firewall): "Maintain absolute separation between the Omega Engine Core and Expansion Stacks (WADs). Core: `src/omega/`, `config/omega.yaml`, `opencode.json`. Stacks: `config/wads/<stack_name>/`. Never add stack-specific logic to the Core Engine."

**The engine core knows about "WAD" as its internal runtime concept** — this IS the violation. The fix is renaming the internal concept from "WAD" to "Stack" while preserving heritage tags on the loader.

---

## 💾 ROOT DIRECTORY THEATER

| File | Size | Type |
|------|------|------|
| `session-ses_07ee.md` | 627KB | Session dump |
| `P9.md` | 275KB | Session theater |
| `failed-subagent-copy-paste.txt` | 181KB | Copy-paste artifact |
| `Screenshot From 2026-07-30 10-11-55.png` | 148KB | Image |
| `P1.md` | 110KB | Session theater |
| `Screenshot From 2026-07-30 10-03-21.png` | 89KB | Image |
| `P6.md` | 87KB | Session theater |
| `P7.md` | 87KB | Session theater |
| `P5.md` | 82KB | Session theater |
| `P3.md` | 70KB | Session theater |
| `P4.md` | 48KB | Session theater |
| `P8.md` | 36KB | Session theater |
| `quantum_error_correction_2026_article.md` | 25KB | Research theater |
| `youtube-links-for-ingestion.txt` | 22KB | Research artifact |
| `youtube-links-mind-science-esoteric.txt` | 13KB | Research artifact |
| `old-claude-sys-prompt.md` | 17KB | Legacy |
| `trim_scope.py` | 5KB | Dead script |
| `debug_test.py` | 4KB | Dead script |
| `test.txt` | 0KB | Empty |
| `file` | 0KB | Empty |
| `tui.json` | 1KB | Dead config |

**Total root theater**: ~1.8MB of garbage not wired to execution.

---

## 🎭 VOS THEATER (0 CODE IMPORTS)

| Item | Files | Code Imports |
|------|-------|--------------|
| `data/realms/` | 7 realm state YAMLs | **0** |
| `src/omega/cli/realm_cli.py` | 1 CLI | **0** (theater) |
| `data/coordination/VISION_ANCHOR.md` | 1 MD | **1** (in theater CLI) |

**The VOS was documentation theater** — created to "capture the vision" but never wired to execution.

---

## 📋 SUMMARY: WHAT'S REAL vs THEATER

| Category | Real (Wired) | Theater (Not Wired) |
|----------|--------------|---------------------|
| Strategy Docs | 5 | 40 |
| Coordination Files | 1 + 7 M27 | 12 orphaned |
| Python Modules | 286 | 5 dead |
| Tests | 92 passing core | 17 failing vault |
| Root Files | 0 | 21 garbage files |
| VOS | 0 | 7 realms + CLI |

**The engine that works**: Core inference flow, entity routing, provider fabric, memory store, stack loading — all functional.

**The theater**: VOS realms, tracking architecture (5 of 6 files), most docs, root garbage, vault, 5 dead modules.

---

**Next**: See `03_WHAT_IS_WIRED_TO_CODE.md` for complete list of actually-referenced files.
