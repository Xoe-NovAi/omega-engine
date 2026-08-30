<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine Initial PR Plan — Dead Code Removal
## Complete Deletion Details with Exact Commands and Rationale

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 04 of 09  
**Date**: 2026-08-14  

---

## 🗑️ CATEGORY 1: ZERO-REFERENCE PYTHON MODULES (5 FILES)

These modules have **0 references** across `src/` and `tests/` — completely dead code.

### 1. `src/omega/state_manager.py`
- **References**: 0
- **Size**: ~200 lines
- **Rationale**: No imports anywhere. Dead code.
- **Command**: `rm -f src/omega/state_manager.py`

### 2. `src/omega/pool_tracker.py`
- **References**: 0
- **Size**: ~150 lines
- **Rationale**: No imports anywhere. Dead code.
- **Command**: `rm -f src/omega/pool_tracker.py`

### 3. `src/omega/mandate_enforcer.py`
- **References**: 0
- **Size**: ~180 lines
- **Rationale**: No imports anywhere. Mandate enforcement is handled elsewhere (mandate_auditor.py, firewall_checker.py).
- **Command**: `rm -f src/omega/mandate_enforcer.py`

### 4. `src/omega/oracle/link_p9_runtime.py`
- **References**: 0
- **Size**: ~300 lines
- **Rationale**: No imports anywhere. P9 runtime not wired.
- **Command**: `rm -f src/omega/oracle/link_p9_runtime.py`

### 5. `src/omega/oracle/lifecycle_harvester.py`
- **References**: 0
- **Size**: ~250 lines
- **Rationale**: No imports anywhere. Lifecycle harvesting not wired.
- **Command**: `rm -f src/omega/oracle/lifecycle_harvester.py`

---

## 🗑️ CATEGORY 2: VAULT MODULE (17 FAILING TESTS)

### `src/omega/vault/` — Entire Directory
- **References**: 0 (not used by core flow)
- **Test Failures**: 17 in `tests/unit/test_vault_core.py`
- **Failure Types**:
  - `AttributeError: 'VaultCore' object has no attribute 'store_credential'` (wrong API name)
  - `ImportError: cannot import name 'initialize_fleet_vault'` (module not found)
  - `ValidationError: encrypted_blob must be age-armored ciphertext` (wrong format)
- **Rationale**: Dead API, broken tests, not used by core inference flow. Can be re-added properly later if needed.
- **Commands**:
  ```bash
  rm -rf src/omega/vault/
  rm -f tests/unit/test_vault_core.py
  ```

---

## 🗑️ CATEGORY 3: ROOT DIRECTORY THEATER (21 FILES)

### Session Dumps & Artifacts:
| File | Size | Command |
|------|------|---------|
| `session-ses_07ee.md` | 627KB | `rm -f session-ses_07ee.md` |
| `P1.md` | 110KB | `rm -f P1.md` |
| `P2.md` | ~80KB | `rm -f P2.md` |
| `P3.md` | 70KB | `rm -f P3.md` |
| `P4.md` | 48KB | `rm -f P4.md` |
| `P5.md` | 82KB | `rm -f P5.md` |
| `P6.md` | 87KB | `rm -f P6.md` |
| `P7.md` | 87KB | `rm -f P7.md` |
| `P8.md` | 36KB | `rm -f P8.md` |
| `P9.md` | 275KB | `rm -f P9.md` |

### Copy-Paste Artifacts:
| File | Size | Command |
|------|------|---------|
| `failed-subagent-copy-paste.txt` | 181KB | `rm -f failed-subagent-copy-paste.txt` |

### Screenshots (5 files):
| File | Size | Command |
|------|------|---------|
| `Screenshot From 2026-07-30 10-03-21.png` | 89KB | `rm -f "Screenshot From 2026-07-30 10-03-21.png"` |
| `Screenshot From 2026-07-30 10-11-55.png` | 148KB | `rm -f "Screenshot From 2026-07-30 10-11-55.png"` |
| `Screenshot From 2026-07-30 10-03-21.png` (dup?) | — | `rm -f "Screenshot*.png"` |

### Research Theater:
| File | Size | Command |
|------|------|---------|
| `quantum_error_correction_2026_article.md` | 25KB | `rm -f quantum_error_correction_2026_article.md` |
| `youtube-links-for-ingestion.txt` | 22KB | `rm -f youtube-links-for-ingestion.txt` |
| `youtube-links-mind-science-esoteric.txt` | 13KB | `rm -f youtube-links-mind-science-esoteric.txt` |

### Legacy/Dead Scripts:
| File | Size | Command |
|------|------|---------|
| `old-claude-sys-prompt.md` | 17KB | `rm -f old-claude-sys-prompt.md` |
| `trim_scope.py` | 5KB | `rm -f trim_scope.py` |
| `debug_test.py` | 4KB | `rm -f debug_test.py` |
| `test.txt` | 0KB | `rm -f test.txt` |
| `file` | 0KB | `rm -f file` |
| `tui.json` | 1KB | `rm -f tui.json` |

### Batch Command for All Root Theater:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
rm -f session-ses_07ee.md P1.md P2.md P3.md P4.md P5.md P6.md P7.md P8.md P9.md
rm -f failed-subagent-copy-paste.txt
rm -f "Screenshot*.png"
rm -f quantum_error_correction_2026_article.md
rm -f youtube-links*.txt
rm -f old-claude-sys-prompt.md trim_scope.py debug_test.py test.txt file tui.json
```

---

## 🗑️ CATEGORY 4: VOS THEATER (0 CODE IMPORTS)

### `data/realms/` — 7 Realm State Files
| File | Size | Command |
|------|------|---------|
| `data/realms/engine_core/state.yaml` | ~2KB | `rm -rf data/realms/` |
| `data/realms/engine_core/workspace/PHASE_0_BRIEF.md` | ~1KB | (included) |
| `data/realms/stacks/state.yaml` | ~2KB | (included) |
| `data/realms/fleet/state.yaml` | ~2KB | (included) |
| `data/realms/fleet/workspace/PHASE_0_BRIEF.md` | ~1KB | (included) |
| `data/realms/heritage/state.yaml` | ~2KB | (included) |
| `data/realms/heritage/workspace/PHASE_0_BRIEF.md` | ~1KB | (included) |
| `data/realms/memory/state.yaml` | ~2KB | (included) |
| `data/realms/memory/workspace/PHASE_0_BRIEF.md` | ~1KB | (included) |
| `data/realms/omegaverse/state.yaml` | ~2KB | (included) |
| `data/realms/community/state.yaml` | ~2KB | (included) |

**Command**: `rm -rf data/realms/`

### `src/omega/cli/realm_cli.py` — Theater CLI
- **References**: 1 (reads VISION_ANCHOR.md)
- **Rationale**: Theater CLI that reads theater VISION_ANCHOR.md. Not wired to execution.
- **Command**: `rm -f src/omega/cli/realm_cli.py`

### `data/coordination/VISION_ANCHOR.md` — Theater Vision Doc
- **References**: 1 (in theater realm_cli.py)
- **Rationale**: Good vision theory but not wired to execution. The VOS was theater.
- **Command**: `rm -f data/coordination/VISION_ANCHOR.md`

---

## 🗑️ CATEGORY 5: ORPHANED COORDINATION FILES (12 FILES)

These are archived/superseded files with no current purpose in the mandatory flow.

### Archived Roadmaps (Absorbed into ACTIVE_SPRINT.json):
| File | Size | Command |
|------|------|---------|
| `data/coordination/KALI_DEV_ROADMAP_20260811.md` | ~15KB | `rm -f data/coordination/KALI_DEV_ROADMAP_20260811.md` |
| `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md` | ~11KB | `rm -f data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md` |

### Superseded Research (Replaced by v3.2.0):
| File | Size | Command |
|------|------|---------|
| `data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md` | ~15KB | `rm -f data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md` |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | ~57KB | `rm -f data/coordination/RESEARCH_JOB_BOARD.yaml` |

### Review Artifacts:
| File | Size | Command |
|------|------|---------|
| `data/coordination/SONNET_4_6_REVIEW_20260814.md` | ~22KB | `rm -f data/coordination/SONNET_4_6_REVIEW_20260814.md` |

### Handoff Artifacts:
| File | Size | Command |
|------|------|---------|
| `data/coordination/HANDOFF_TO_CLAUDE_SONNET_4_6_20260814.md` | ~10KB | `rm -f data/coordination/HANDOFF_TO_CLAUDE_SONNET_4_6_20260814.md` |

### Batch Command for All Orphaned Coordination:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
rm -f data/coordination/KALI_DEV_ROADMAP_20260811.md
rm -f data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md
rm -f data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md
rm -f data/coordination/RESEARCH_JOB_BOARD.yaml
rm -f data/coordination/SONNET_4_6_REVIEW_20260814.md
rm -f data/coordination/HANDOFF_TO_CLAUDE_SONNET_4_6_20260814.md
```

---

## 🗑️ CATEGORY 6: STRATEGY DOCS WITH 0 CODE REFERENCES (37+ FILES)

All files in `docs/strategy/` except the 5 wired docs. These are documentation theater.

### Files to DELETE (examples — delete all except the 5 wired):
```
docs/strategy/WEB_RECONCILIATION_MATRIX_20260807.md
docs/strategy/WEB_GROK_BEST_PRACTICES.md
docs/strategy/WEB_GEMINI_BEST_PRACTICES.md
docs/strategy/WEB_CLAUDE_BEST_PRACTICES.md
docs/strategy/WEB_CHATBOT_PLATFORM_PLAYBOOK.md
docs/strategy/UNOVERENGINEERING_PLAN.md
docs/strategy/UNIFIED_EXECUTION_PLAN_20260722.md
docs/strategy/TASK_REGISTRY_DESIGN.md
docs/strategy/SYSTEMD_NETWORK_NAMESPACES_GUIDE.md
docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md
docs/strategy/STRATEGY_INDEX.md
docs/strategy/STRATEGY_CORPUS_MAP.md
docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md
docs/strategy/SESSION_END_ORCHESTRATION_PIVOT_20260730.md
docs/strategy/SDP_MODEL_AWARE_GAUGE_SPEC.md
docs/strategy/SDP_IMPLEMENTATION_SPEC.md
... and all other docs/strategy/ files except:
  - SOVEREIGN_ARK_BLUEPRINT.md
  - CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md
  - IMPLEMENTATION_MANUAL_C0_C2.md
  - SUBAGENT_DISPATCH_PROTOCOL.md
  - DECISION_LEDGER.md (in data/coordination/)
```

**Note**: The 5 wired strategy docs MUST be kept. Delete the rest.

---

## 📋 COMPLETE DELETION SUMMARY

| Category | Files | Lines/Size | Rationale |
|----------|-------|------------|-----------|
| Zero-ref Python modules | 5 | ~1,000 lines | 0 references |
| Vault module | 1 dir + 1 test | ~2,000 lines | 17 failing tests, broken API |
| Root theater | 21 | ~1.8MB | Garbage not wired |
| VOS theater | 15 | ~30KB | 0 code imports |
| Orphaned coordination | 6 | ~130KB | Archived/superseded |
| Strategy theater | 37+ | ~500KB | 0 code references |
| **TOTAL** | **~85+** | **~2.5MB** | **All theater/dead code** |

---

## ✅ VERIFICATION AFTER DELETION

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Check git status
git status --short | grep -E "deleted|renamed" | wc -l
# Should show: ~85+ deletions

# 2. Verify core imports still work
.venv/bin/python -c "
from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.stack_loader import StackLoader
from omega.memory_store import get_memory_store
print('All core imports OK')
"

# 3. Run core tests
.venv/bin/python -m pytest tests/test_oracle.py tests/test_entity_registry.py tests/test_model_gateway.py tests/test_stack_loader.py tests/test_memory_store.py -q
# Should show: 92 passed, 2 failed (memory store FTS - fixable)

# 4. Verify no dead imports remain
grep -rn "state_manager\|pool_tracker\|mandate_enforcer\|link_p9_runtime\|lifecycle_harvester" src/ --include="*.py" | grep -v "__pycache__"
# Should show: 0 results

# 5. Verify vault is gone
ls src/omega/vault/ 2>/dev/null && echo "VAULT STILL EXISTS" || echo "VAULT DELETED"
```

---

**Next**: See `05_M2_FIREWALL_FIX.md` for the WAD→Stack rename details.
