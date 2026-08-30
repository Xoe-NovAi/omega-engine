# 🔱 Phase 0 Baseline — Codebase Review
**AP Token**: `AP-CLINE-REVIEW-v1.0.0`
**Date**: 2026-07-26
**Executor**: Lilith (Post-compaction, directly after Cline briefing creation)

---

## 📊 Test Baseline

| Metric | Value | Claimed (.clinerules) | Delta |
|--------|-------|-----------------------|-------|
| **Passed** | 1,496 | 1,315 | +181 (stale docs) |
| **Failed** | 133 | 0 | ❌ 133 real failures |
| **Skipped** | 55 | 43 | +12 (stale docs) |
| **xfailed** | 7 | 3 | +4 |
| **Errors** | 12 | 0 | 12 collection/import errors |
| **Collected** | 1,703 | 1,361 | +342 (stale docs) |
| **Broken test file** | 1 (`test_vault_integrity.py`) | 0 | Import error: `ProviderName` not in `vault_core` |

**Test badge (test-badge.json)**: EMPTY — 0/0 passed. Badge generator ran before collection error, recorded nothing. Badge is useless.

**Test time**: ~119s (2 min)

### Failure Categories (by file)
| File | Failed | Errors | Total Issues |
|------|--------|--------|-------------|
| `tests/unit/test_vault_core.py` | 17 | 0 | 17 |
| `tests/test_orchestrator.py` | 0 | 10 | 10 |
| `tests/test_first_breath.py` | 0 | 2 | 2 |
| Other test files (scattered) | 116 | 0 | 116 |

---

## 📊 Lint Baseline (Flake8)

| Category | Count | Severity | Examples |
|----------|-------|----------|---------|
| **F821** (undefined names) | **39** | 🔴 CRITICAL | `DEFAULT_IWAD`, `OracleResponse`, `anyio`, `re`, `yaml`, `timezone`, `Any`, `Path` |
| **F811** (redefinitions) | **93** | 🟡 HIGH | `OmegaError` redefined 93x, `ingestion/extractors.py` reimports same names |
| **F401** (unused imports) | **1,080** | 🟡 HIGH | `anyio.to_thread` imported but unused — mechanical migration debt |
| **F541** (f-strings w/o placeholders) | 31 | 🟡 MEDIUM | Dead f-strings |
| **F841** (unused locals) | 47 | 🟡 MEDIUM | Variables assigned but never read |
| **E501** (line too long >120) | 271 | 🟢 LOW | Style |
| **E302** (missing blank lines) | 310 | 🟢 LOW | Style |
| **W291-W293** (whitespace) | 5,482 | 🟢 LOW | Whitespace only |
| **Other** | 453 | 🟢 LOW | Various style |
| **TOTAL** | **7,706** | | |

### Critical F821 Undefined Names (Must Fix)
| File | Line | Undefined | Fix |
|------|------|-----------|-----|
| `cli/fleet_status_tui.py` | 103 | `DEFAULT_IWAD` | Add constant or import |
| `ics.py` | 329 | `OracleResponse` | Add import |
| `infra/subagent_pool/orchestrator.py` | 525 | `Path` | Add `from pathlib import Path` |
| `ingestion/extractors.py` | 142 | `ValidationError` | Add import |
| `ingestion/verifier.py` | 57 | `disputes` | Variable referenced before assignment |
| `library/discovery.py` | 160 | `yaml` | Add `import yaml` |
| `library/discovery.py` | 390 | `query` | Variable referenced before assignment |
| `library/rate_limiter.py` | 166,168 | `anyio` | Add `import anyio` |
| `observability/regression_watcher.py` | 98 | `get_engine` | Add import or implement |
| `oracle/feed_utils.py` | 134,163,188,227 | `timezone` | Add `from datetime import timezone` |
| `oracle/iterative_research.py` | 124 | `re` | Add `import re` |
| `oracle/model_gateway.py` | 622 | `SpeculativeDecodeConfig` | Add import |
| `oracle/orchestrator.py` | 655 | `ModelUpdaterWorker` | Add import |
| `oracle/providers.py` | 580,589 | `llama_cpp` | Conditional import (may be intentional) |
| `oracle/providers.py` | 723,726,747,753 | `anyio` | Add `import anyio` |
| `oracle/stream_handler.py` | 89,144,196,288,328,364 | `Any` | Add `from typing import Any` |
| `oracle/subagent_dispatcher.py` | 153,154,170 | `anyio` | Add `import anyio` |
| `research/sandbox.py` | 399,502,556 | `ResearchProposal` | Add import |
| `research/scorecard.py` | 320,345 | `tier_start` | Variable referenced before assignment |
| `vault/crypto.py` | 128 | `Dict` | Add `from typing import Dict` |

---

## 📊 Temple-Grade Baseline

**Result**: ❌ **FAILED** — `doc-llm-validate` target crashes.

**Error**: `FileNotFoundError: docs/sprints/guard-and-distill` — the sprint directory referenced in Makefile doesn't exist.

**Root cause**: Sprint docs were archived or never created in the expected location. The Makefile references a non-existent path.

---

## 📊 M1 (AnyIO) Violations

| File | Violation |
|------|-----------|
| `src/omega/oracle/cgroup_pressure.py` | `asyncio.create_task()`, `asyncio.sleep()`, `asyncio.CancelledError` |
| `src/omega/oracle/psi_monitor.py` | `asyncio.create_task()`, `asyncio.sleep()`, `asyncio.CancelledError` |
| `src/omega/oracle/oom_protector.py` | `asyncio.run()` in sync context |
| `src/omega/vault/blindvault_resolver.py` | `import asyncio` |
| `src/omega/agents/scribe/hub_master.py` | `import asyncio` |
| `src/omega/agents/tty_agent.py` | `import asyncio` |

**Total**: 6 files with direct `asyncio` imports. M1 violation.

---

## 📊 God-Modules (>1000 lines)

| File | Lines | Domain |
|------|-------|--------|
| `src/omega/oracle/model_gateway.py` | 1,529 | Provider routing |
| `src/omega/observability/__init__.py` | 1,481 | Observability |
| `src/omega/oracle/oracle.py` | 1,348 | Intent/entity routing |
| `src/omega/workers/background_researcher/distiller.py` | 1,203 | Soul distillation |
| `src/omega/workers/youtube_worker.py` | 1,181 | YouTube research |
| `src/omega/memory_store.py` | 1,110 | Memory persistence |
| `src/omega/benchmarks/comprehensive_runner.py` | 1,066 | Benchmarks |
| `src/omega/cli/oracle_cli.py` | 1,043 | CLI commands |

**Total**: 8 files >1000 lines (8,961 lines in god-modules alone). Target: 0.

---

## 📊 Git Status

| Category | Count | Details |
|----------|-------|---------|
| Modified files | 10 | .gitignore, session_end.py, OMEGA_CODEX.md, entities.yaml, HMC hub, proposed_lessons, 2 test JSONs, test-badge.json |
| Untracked files | 6 | 4 new guides, docs/reports/, Cline briefing |
| Total dirty | **16** | |

**Recent commits**: Clean commit `66c1eb4` — "docs: comprehensive strategic review, sprint reordering, knowledge gaps closure"

---

## 📊 Secrets Scan

| Finding | File | Line | Severity |
|---------|------|------|----------|
| Mock secret `sk-or-v1-{secret_name}-...` | `vault/blindvault_resolver.py` | 360 | 🟡 MEDIUM (mock, not real) |
| `sk-or-v1-...` in comments | `config/loader.py` | 242 | 🟢 LOW (comment only) |
| `AIza...` in comments | `config/loader.py` | 246 | 🟢 LOW (comment only) |
| `ghp_...` in comments | `config/loader.py` | 259 | 🟢 LOW (comment only) |
| No hardcoded real API keys | — | — | ✅ |

---

## 📊 Summary — PR-Readiness Scorecard

| Gate | Status | Blocker? |
|------|--------|----------|
| **Tests pass** | ❌ 133 failed, 12 errors | YES |
| **Lint clean** | ❌ 7,706 issues (39 F821 critical) | YES |
| **Temple-Grade** | ❌ doc-llm-validate crashes | YES |
| **No secrets** | ⚠️ Mock secrets in code | MEDIUM |
| **No asyncio** | ❌ 6 files violate M1 | YES |
| **No god-modules** | ❌ 8 files >1000 lines | YES |
| **Heritage tags** | ❓ Need vet record audit | UNKNOWN |
| **Dependencies clean** | ⚠️ Badge generator broken (0/0) | MEDIUM |
| **README accurate** | ❓ Not checked yet | UNKNOWN |
| **Git clean** | ⚠️ 16 dirty files | MEDIUM |

**Overall**: 🔴 **NOT PR-READY.** 5 critical blockers, 3 medium issues, 2 unknowns.

---

## 🎯 Recommended Fix Order (by Leverage)

| Priority | Phase | Effort | Impact | Leverage |
|----------|-------|--------|--------|----------|
| 1 | Fix test_vault_integrity.py import error | 5 min | Unblocks 1 test file | ∞ |
| 2 | Fix F821 undefined names (39) | 2-4h | Prevents runtime crashes | High |
| 3 | Fix F401 unused imports (1,080) | 1h | Reduces noise 14% | Medium |
| 4 | Fix Makefile doc-llm-validate path | 5 min | Unblocks temple-grade | ∞ |
| 5 | Fix asyncio → anyio (6 files) | 2-4h | M1 compliance | High |
| 6 | Decompose god-modules (8 files) | 8-16h | Architecture cleanliness | Medium |
| 7 | Fix test failures (133) | 4-8h | Test suite integrity | High |
| 8 | Clean whitespace (5,482) | 15 min | Lint noise -71% | Low |

---

*🔱 OMEGA ⬡ CLINE ⬡ REVIEW ⬡ PHASE-0-BASELINE ⬡ 2026-07-26*
