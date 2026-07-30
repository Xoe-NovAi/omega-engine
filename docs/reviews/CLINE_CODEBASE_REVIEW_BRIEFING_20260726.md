# 🔱 Cline CLI — Full Codebase Review Briefing (ENHANCED v2.0)
**AP Token**: `AP-CLINE-REVIEW-v2.0.0`
⬡ OMEGA ⬡ CLINE ⬡ CODEBASE-REVIEW ⬡ PR-READINESS

**Date**: 2026-07-26
**Purpose**: Phased codebase review to prepare the Omega Engine repo for public PR
**Context Engine**: DeepSeek V4 Flash (1M tokens) — you have full repo context
**Working Directory**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`
**Baseline Source**: `data/coordination/CLINE_REVIEW_PHASE0_BASELINE.md` (verified 2026-07-26)

---

## 🎯 Mission

The Omega Engine needs to be PR-ready. This means: no secrets in source, no M1 (AnyIO) violations, no god-modules, clean lint, honest tests, consistent dependencies, and a working `make temple-grade`. You are the execution arm — read, assess, fix, verify.

**You are NOT the architect.** You are a Cognitive Extension of the Omega Engine. Follow `.clinerules` and `SOVEREIGN_MANDATES.md`. Fix forward, never revert without understanding root cause.

---

## 📊 Current State (VERIFIED 2026-07-26 — Phase 0 Complete)

| Metric | Value | PR-Ready? |
|--------|-------|-----------|
| **Python files (src/omega/)** | 285 files, ~83,796 lines | — |
| **Test files** | 161 files, ~30,499 lines | — |
| **God-modules (>1000 lines)** | **8 files** (8,961 lines) | ❌ |
| **M1 (AnyIO) violations** | **6 files** import `asyncio` directly | ❌ |
| **Secrets in source** | Mock secret in `blindvault_resolver.py:360`; example keys in `config/loader.py` comments | ⚠️ |
| **Lint (flake8)** | **7,706 issues** — **39 F821 critical** (undefined names), 93 F811 (redefinitions), 1,080 F401 (unused imports) | ❌ |
| **Test pass rate** | **1,496 passed / 133 failed / 55 skipped / 7 xfailed / 12 errors** — badge generator broken (0/0) | ❌ |
| **Temple-Grade** | ❌ `doc-llm-validate` crashes on missing `docs/sprints/guard-and-distill` | ❌ |
| **Dependencies** | Both pyproject.toml + requirements.txt exist | ⚠️ |
| **Git status** | 10 modified, 6 untracked = 16 dirty files | ⚠️ |

**Overall**: 🔴 **NOT PR-READY** — 5 critical blockers, 3 medium issues.

---

## 📋 Phase 0: Baseline (COMPLETE — See `CLINE_REVIEW_PHASE0_BASELINE.md`)

**Goal**: Establish the real numbers. No vanity metrics.

### 0.1 — Test Baseline ✅ DONE
```bash
source .venv/bin/activate && make test
```
**Result**: 1,496 passed / 133 failed / 55 skipped / 7 xfailed / 12 errors (1,691 collected excluding broken test_vault_integrity.py). Badge generator recorded 0/0 (useless).

### 0.2 — Lint Baseline ✅ DONE
```bash
source .venv/bin/activate && flake8 src/omega/ --count --statistics --max-line-length=120
```
**Result**: 7,706 total — **39 F821 (undefined names — will crash at runtime)**, 93 F811 (redefinitions), 1,080 F401 (unused imports), 5,482 whitespace.

### 0.3 — Temple-Grade Baseline ✅ DONE
```bash
source .venv/bin/activate && make temple-grade
```
**Result**: FAILED — `doc-llm-validate` crashes: `FileNotFoundError: docs/sprints/guard-and-distill`

### 0.4 — Git Status ✅ DONE
```bash
git status --short && git log --oneline -5
```
**Result**: 16 dirty files (10 modified, 6 untracked). Last clean commit: `66c1eb4` — "docs: comprehensive strategic review..."

### 0.5 — Dependency Audit ✅ DONE
```bash
diff <(grep -E "^[a-z]" requirements.txt | sort) <(grep -E "^[a-z]" pyproject.toml | sort)
```
**Result**: Both files exist. Need manual comparison for conflicts.

---

## 📋 Phase 0.5: IMMEDIATE UNBLOCKERS (5 min each — Do First)

These unblock the entire pipeline. Do them before Phase 1.

### 0.5.1 — Fix Broken Test Collection
**File**: `tests/test_vault_integrity.py:7`
**Error**: `ImportError: cannot import name 'ProviderName' from 'src.omega.vault.vault_core'`
**Fix**: Remove the import or fix to import what actually exists in vault_core.py
```bash
grep -n "ProviderName" src/omega/vault/vault_core.py  # Verify it doesn't exist
# Then edit test_vault_integrity.py to remove the bad import
```

### 0.5.2 — Fix Makefile Temple-Grade Path
**File**: `Makefile` — find `doc-llm-validate` target
**Error**: References `docs/sprints/guard-and-distill` which doesn't exist
**Fix**: Update path to actual sprint docs location or remove the check if sprint structure changed
```bash
grep -n "guard-and-distill" Makefile
# Fix the path or comment out if obsolete
```

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE05_UNBLOCKERS.md`

---

## 📋 Phase 1: Secrets & Security (PR Blocker)

**Goal**: Zero hardcoded secrets, zero credential leaks in version control.

### 1.1 — Hardcoded Secrets Scan
```bash
grep -rn "sk-\|ghp_\|AIza\|Bearer \|api_key.*=\|password.*=" src/omega/ --include="*.py" | grep -v "test\|mock\|example\|comment\|TODO\|FIXME"
```

**Known issues to fix:**
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `src/omega/vault/blindvault_resolver.py` | 360 | `f"sk-or-v1-{secret_name}-{datetime.utcnow().timestamp()}"` — mock secret in code | Replace with `"REDACTED"` or remove entirely |
| `src/omega/config/loader.py` | 242-259 | `sk-or-v1-...`, `AIza...`, `ghp_...` in comments | Sanitize to `"YOUR_API_KEY_HERE"` |
| `src/omega/rag/router.py` | 60 | `Redis Pub/Sub` in string (false positive) | Skip |

### 1.2 — Environment Variable Leaks
```bash
grep -rn "os.environ\[" src/omega/ --include="*.py" | grep -iv "test\|mock\|example"
```
Verify each reads from config, not hardcoding.

### 1.3 — .env and Config Files
```bash
find . -name ".env" -not -path "./.venv/*" -not -path "./.git/*"
find . -name "*.env" -not -path "./.venv/*" -not -path "./.git/*"
git log --all --full-history -- "*.env" ".env"
```
Check: are .env files tracked? They should be in .gitignore.

### 1.4 — Pre-commit Hook Verification
```bash
cat .pre-commit-config.yaml 2>/dev/null | head -30
```
Verify: detect-secrets, detect-api-keys, enforce-vaultcore hooks exist and are active.

**Deliverable**: Fix all findings. Write to `data/coordination/CLINE_REVIEW_PHASE1_SECRETS.md`

---

## 📋 Phase 2: M1 AnyIO Compliance (Mandate Violation)

**Goal**: Zero `asyncio` imports in `src/omega/`. All async code uses `anyio`.

### 2.1 — Find All M1 Violations
```bash
grep -rn "import asyncio\|from asyncio" src/omega/ --include="*.py"
```

**Verified violations (6 files):**
| File | Violation | Fix Pattern |
|------|-----------|-------------|
| `src/omega/oracle/cgroup_pressure.py` | `asyncio.create_task()`, `asyncio.sleep()`, `asyncio.CancelledError` | `anyio.create_task_group()`, `anyio.sleep()`, `anyio.get_cancelled_exc_class()` |
| `src/omega/oracle/psi_monitor.py` | Same as above | Same fix |
| `src/omega/oracle/oom_protector.py` | `asyncio.run()` in sync context | Wrap in `anyio.to_thread.run_sync()` |
| `src/omega/vault/blindvault_resolver.py` | `import asyncio` | Replace with `anyio` equivalents |
| `src/omega/agents/scribe/hub_master.py` | `import asyncio` | Replace with `anyio` equivalents |
| `src/omega/agents/tty_agent.py` | `import asyncio` | Replace with `anyio` equivalents |

### 2.2 — Fix Pattern
```python
# WRONG (M1 violation)
import asyncio
await asyncio.sleep(1)
task = asyncio.create_task(coro)
try:
    await task
except asyncio.CancelledError:
    pass

# CORRECT (M1 compliant)
import anyio
await anyio.sleep(1)
async with anyio.create_task_group() as tg:
    tg.start_soon(coro)
# CancelledError → anyio.get_cancelled_exc_class()
```

### 2.3 — Verify No Regressions
After each file fix, run specific tests:
```bash
source .venv/bin/activate && python -m pytest tests/ -k "test_name" -x
```

**Deliverable**: All asyncio → anyio. Write to `data/coordination/CLINE_REVIEW_PHASE2_M1.md`

---

## 📋 Phase 3: God-Module Decomposition (Architecture)

**Goal**: No file >1000 lines. Split god-modules into focused submodules.

### 3.1 — Identify God-Modules
```bash
find src/omega -name "*.py" -exec wc -l {} + | sort -rn | head -20
```

**Verified god-modules (8 files >1000 lines):**
| File | Lines | Domain | Split Strategy |
|------|-------|--------|----------------|
| `src/omega/oracle/model_gateway.py` | 1,529 | Provider routing | → `model_gateway.py` (core), `provider_adapters/` (per-provider), `quota_tracker.py` (quota logic) |
| `src/omega/observability/__init__.py` | 1,481 | Observability | → Split into `traces.py`, `metrics.py`, `events.py`, `dashboard.py` |
| `src/omega/oracle/oracle.py` | 1,348 | Intent/entity routing | → `oracle.py` (core talk), `intent_router.py`, `entity_matcher.py` |
| `src/omega/workers/background_researcher/distiller.py` | 1,203 | Soul distillation | → `distiller.py` (pipeline), `classifiers.py`, `scorers.py` |
| `src/omega/workers/youtube_worker.py` | 1,181 | YouTube research | → `youtube_worker.py` (core), `transcriber.py`, `chunker.py`, `cas_archiver.py`, `gnosis_bridge.py`, `faithfulness.py`, `freshness.py`, `steering.py` |
| `src/omega/memory_store.py` | 1,110 | Memory persistence | → `memory_store.py` (core), `hot_tier.py`, `warm_tier.py`, `cold_tier.py` |
| `src/omega/benchmarks/comprehensive_runner.py` | 1,066 | Benchmarks | → `comprehensive_runner.py` (core), `metrics_collector.py`, `report_generator.py` |
| `src/omega/cli/oracle_cli.py` | 1,043 | CLI commands | → Split into `cli/talk.py`, `cli/summon.py`, `cli/entities.py`, `cli/admin.py` |

### 3.2 — Decomposition Rules
1. **Preserve public API** — existing imports must still work. Add backward-compat re-exports in `__init__.py`.
2. **M2 Firewall** — no stack-specific logic (`config/wads/`) leaks into core (`src/omega/`).
3. **Each submodule < 500 lines** — the 1000-line ceiling is a warning; 500 is the target.
4. **Run tests after every split** — `make test` must pass before moving to next file.
5. **Commit each split separately** — `refactor: split model_gateway into core + provider_adapters`

### 3.3 — Decomposition Order (by Impact)
1. **model_gateway.py** — Most critical, most complex, most likely to have hidden deps
2. **oracle.py** — Core entry point, must be clean
3. **observability/__init__.py** — Shouldn't be a god-module; split into proper subpackage
4. **memory_store.py** — Clean tier split is straightforward
5. **oracle_cli.py** — CLI decomposition is mechanical
6. **distiller.py** — Clean pipeline/classifier/scorer split
7. **youtube_worker.py** — Already has natural submodule boundaries (9-layer TKO)
8. **comprehensive_runner.py** — Benchmarks can be split cleanly

**Deliverable**: All files <1000 lines. Write to `data/coordination/CLINE_REVIEW_PHASE3_GODMODULES.md`

---

## 📋 Phase 4: Dependency Hygiene

**Goal**: Single source of truth for dependencies, no version conflicts.

### 4.1 — pyproject.toml vs requirements.txt
```bash
cat pyproject.toml | head -80
cat requirements.txt | head -40
```
Check:
- Are the same packages in both? Any version conflicts?
- Is pyproject.toml the SSOT? (It should be.)
- Is requirements.txt a generated output or manually maintained?

### 4.2 — Unused Dependencies
```bash
grep -rh "^import \|^from " src/omega/ --include="*.py" | sed 's/from \([a-z_]*\).*/\1/;s/import \([a-z_]*\).*/\1/' | sort -u > /tmp/imports.txt
grep -E "^[a-z]" requirements.txt | sed 's/[>=<].*//' | sort -u > /tmp/deps.txt
comm -23 /tmp/imports.txt /tmp/deps.txt
```

### 4.3 — Pinned Versions
Verify: are dependencies pinned? (`==` not `>=`)
```bash
grep -c ">=" requirements.txt
grep -c "==" requirements.txt
```
PR-ready = pinned versions for reproducibility.

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE4_DEPS.md`

---

## 📋 Phase 5: Test Suite Integrity

**Goal**: Honest test counts, no quarantine debt, no mock-only tests.

### 5.1 — Real Test Run (Excluding Broken File)
```bash
source .venv/bin/activate && python -m pytest tests/ --ignore=tests/test_vault_integrity.py -v --tb=short 2>&1 | tail -30
```
**Expected**: Record exact: `X passed, Y failed, Z skipped, W xfailed, N errors`

**Verified failure categories (from Phase 0):**
| Test File | Result | Category |
|-----------|--------|----------|
| `tests/unit/test_vault_core.py` | 17 failed, 1 passed | VaultCore persistence/edge cases |
| `tests/test_orchestrator.py` | 10 errors | Collection/import errors (MCP watchdog, dispatch agent) |
| `tests/test_first_breath.py` | 2 errors | AttributeError on test setup |
| Other files | 133 total failed | Various |

### 5.2 — Quarantine Audit
```bash
cat tests/quarantine.txt 2>/dev/null
```
Check:
- How many tests are quarantined?
- When does quarantine expire? (Should be soon.)
- Are quarantined tests real failures or false positives?

### 5.3 — Mock-Only Test Detection
```bash
grep -rl "mock.patch\|@patch\|MagicMock\|AsyncMock" tests/ --include="*.py" | xargs -I{} sh -c 'echo "=== {} ===" && grep -c "mock" {}'
```
Files with high mock-to-assertion ratios are suspect. Flag them.

### 5.4 — Coverage Baseline
```bash
source .venv/bin/activate && python -m pytest tests/ --ignore=tests/test_vault_integrity.py --cov=src/omega --cov-report=term-missing 2>&1 | tail -20
```
Record: overall coverage %, uncovered modules.

### 5.5 — Fix Badge Generator
The `make test` badge recorded 0/0 because test collection failed before any tests ran. After fixing test_vault_integrity.py, re-run `make test` to generate a real badge.

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE5_TESTS.md`

---

## 📋 Phase 6: Code Quality (Lint + Types)

**Goal**: Clean lint, consistent type hints, no dead code.

### 6.1 — Flake8 Critical Fixes (Priority Order)
```bash
source .venv/bin/activate && flake8 src/omega/ --select=F821,F811,F401,F541,F841,F402 --max-line-length=120
```

**Critical F821 (39 undefined names — will crash at runtime):**
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

**F811 (93 redefinitions — `OmegaError` imported then redefined):**
- Pattern: `from src.omega.errors import OmegaError` then later `class OmegaError(Exception):` — remove the import or the redefinition.

**F401 (1,080 unused imports — mostly `anyio.to_thread`):**
- Likely mechanical migration artifact. Remove unused imports.

### 6.2 — Dead Code Detection
```bash
find src/omega -name "*.py" -not -name "__init__.py" | while read f; do
    mod=$(basename "$f" .py)
    count=$(grep -r "from.*$mod\|import.*$mod" src/omega/ --include="*.py" | wc -l)
    if [ "$count" -lt 2 ]; then
        echo "POSSIBLY DEAD: $f (referenced $count times)"
    fi
done
```

### 6.3 — Type Hint Audit
```bash
grep -rn "def [a-z_]*(" src/omega/ --include="*.py" | grep -v "->" | head -20
```
Public functions should have return type hints (Python 3.12+ style).

### 6.4 — Docstring Coverage
```bash
grep -rn "^class " src/omega/ --include="*.py" | grep -v '"""' | head -20
```

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE6_QUALITY.md`

---

## 📋 Phase 7: Documentation & Structure

**Goal**: README accurate, CONTRIBUTING.md present, no orphan docs.

### 7.1 — README Audit
```bash
cat README.md | head -50
```
Check:
- Does it describe what the engine IS?
- Are install instructions current? (`source .venv/bin/activate && pip install -e .`)
- Are key commands listed?
- Does it link to the right docs?

### 7.2 — CONTRIBUTING.md
```bash
cat CONTRIBUTING.md 2>/dev/null | head -30
```
Does it exist? Is it accurate? Does it cover:
- Development setup
- Testing requirements (`make test` before PR)
- Code standards (AnyIO, YAML config, venv)
- Commit conventions (`feat:`, `fix:`, `docs:`, etc.)

### 7.3 — Orphan Documentation
```bash
find docs/ -name "*.md" -not -path "docs/archive/*" | wc -l
find docs/archive/ -name "*.md" | wc -l
```
How many docs in archive vs active? Are any active docs stale?

### 7.4 — .gitignore Audit
```bash
cat .gitignore | head -40
```
Check: .env, __pycache__, .venv, *.pyc, data/entities/*/soul.yaml (if soul files should be gitignored), etc.

### 7.5 — Fix Makefile doc-llm-validate Path
The `doc-llm-validate` target in Makefile references `docs/sprints/guard-and-distill` which doesn't exist. Fix the path or remove the check.

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE7_DOCS.md`

---

## 📋 Phase 8: Heritage & Mandate Compliance

**Goal**: All [id-soft:] tags have vet records, M14 compliance, M2 Firewall clean.

### 8.1 — Heritage Tag Audit
```bash
grep -rn "\[id-soft:" src/omega/ --include="*.py" | wc -l
grep -rn "\[heritage:" src/omega/ --include="*.py" | wc -l
cat data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md 2>/dev/null | wc -l
```
Every [id-soft:] tag MUST have a corresponding vet record.

### 8.2 — M2 Firewall Check
```bash
grep -rn "config/wads" src/omega/ --include="*.py" | head -10
```
No stack-specific logic in core. If found, it's a M2 violation.

### 8.3 — M8 Zero Telemetry
```bash
grep -rn "requests.post\|urllib\|httpx\|aiohttp" src/omega/ --include="*.py" | grep -iv "test\|mock\|localhost\|127.0.0.1" | head -10
```
Any outbound HTTP that isn't to localhost or a configured provider = potential telemetry.

### 8.4 — M10 Fleet Count
```bash
ls .opencode/agents/*.md 2>/dev/null | wc -l
```
Must be ≤14 agents.

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE8_MANDATES.md`

---

## 📋 Phase 9: PR Preparation

**Goal**: Clean commit history, proper message format, no secrets in diff.

### 9.1 — Commit Message Audit
```bash
git log --oneline -20
```
Check: do commits use conventional format? (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`)

### 9.2 — Uncommitted Changes
```bash
git status --short
```
Fix: stage and commit all intended changes. Don't leave dirty tree.

### 9.3 — Large Files
```bash
find . -not -path "./.git/*" -not -path "./.venv/*" -not -path "./models/*" -size +1M -type f
```
Large files (>1MB) in version control are PR blockers unless intentional (models, etc.)

### 9.4 — Final Verification
```bash
source .venv/bin/activate && make test && make lint && make temple-grade
```
All three must pass (or have documented exceptions) before PR.

### 9.5 — Branch & Push
```bash
git checkout -b refactor/pr-readiness-review
git add -A
git commit -m "refactor: PR readiness review — secrets, M1, god-modules, tests, lint"
git push origin refactor/pr-readiness-review
```

**Deliverable**: Write to `data/coordination/CLINE_REVIEW_PHASE9_PR.md`

---

## 🚨 Rules of Engagement

1. **Run `make test` after EVERY change.** If tests regress, revert the change and understand why.
2. **Never commit secrets.** If you find one, redact it and document the finding.
3. **One fix per commit.** Don't batch unrelated changes. `fix: sanitize mock secret in blindvault_resolver` not `fix: various fixes`.
4. **Preserve public API.** When splitting god-modules, add backward-compat re-exports.
5. **Ask before destroying.** If a fix requires deleting a file or major rewrite, document the plan first.
6. **Use `source .venv/bin/activate`** before every Python command. NEVER `--break-system-packages`.
7. **M23 Hard-Stop**: If a mandatory tool is broken (make test, make lint), STOP and report `[TOOL-CHAIN-COLLAPSE]`. Don't work around it.
8. **Heartbeat every 5-10 min**: `hivemind_heartbeat(channel="cline", entity="omega-engine")` via MCP.

---

## 📁 Deliverable Structure

After each phase, write a report to `data/coordination/`:
```
data/coordination/
├── CLINE_REVIEW_PHASE0_BASELINE.md       ← COMPLETE (verified numbers)
├── CLINE_REVIEW_PHASE05_UNBLOCKERS.md    ← NEW: 5-min fixes first
├── CLINE_REVIEW_PHASE1_SECRETS.md        ← Secrets found + fixed
├── CLINE_REVIEW_PHASE2_M1.md             ← asyncio → anyio fixes
├── CLINE_REVIEW_PHASE3_GODMODULES.md     ← File splits performed
├── CLINE_REVIEW_PHASE4_DEPS.md           ← Dependency audit
├── CLINE_REVIEW_PHASE5_TESTS.md          ← Test integrity report
├── CLINE_REVIEW_PHASE6_QUALITY.md        ← Lint/type/docstring fixes
├── CLINE_REVIEW_PHASE7_DOCS.md           ← Documentation audit
├── CLINE_REVIEW_PHASE8_MANDATES.md       ← Mandate compliance check
└── CLINE_REVIEW_PHASE9_PR.md             ← PR preparation + branch
```

---

## 🎯 Success Criteria (Specific Numbers)

The repo is PR-ready when:
- [ ] `make test` passes: **≥1,496 passed, 0 failed, 0 errors** (no regression from baseline)
- [ ] `make lint` passes: **0 errors, <10 warnings** (from 7,706)
- [ ] `make temple-grade` passes T1-T11 (or documented exceptions)
- [ ] Zero hardcoded secrets in `src/omega/`
- [ ] Zero `import asyncio` in `src/omega/`
- [ ] Zero files >1000 lines in `src/omega/`
- [ ] All [id-soft:] tags have vet records
- [ ] pyproject.toml is dependency SSOT
- [ ] README.md is accurate and current
- [ ] CONTRIBUTING.md exists with development setup instructions
- [ ] Clean git history with conventional commit messages
- [ ] Branch pushed with PR-ready commit

---

## 📊 Leverage-Ordered Fix Priority (From Phase 0 Data)

| Priority | Phase | Task | Effort | Impact | Leverage |
|----------|-------|------|--------|--------|----------|
| 1 | 0.5.1 | Fix test_vault_integrity.py import | 5 min | Unblocks test collection | ∞ |
| 2 | 0.5.2 | Fix Makefile doc-llm-validate path | 5 min | Unblocks temple-grade | ∞ |
| 3 | 1 | Sanitize mock secrets (3 locations) | 15 min | PR blocker removed | High |
| 4 | 6 | Fix 39 F821 undefined names | 2-4h | Prevents runtime crashes | High |
| 5 | 2 | Fix 6 M1 asyncio violations | 2-4h | Mandate compliance | High |
| 6 | 6 | Remove 1,080 F401 unused imports | 1h | Reduces lint noise 14% | Medium |
| 7 | 6 | Fix 93 F811 redefinitions | 1h | Clean imports | Medium |
| 8 | 3 | Decompose 8 god-modules | 8-16h | Architecture cleanliness | Medium |
| 9 | 5 | Fix 133 test failures | 4-8h | Test suite integrity | High |
| 10 | 6 | Clean 5,482 whitespace issues | 15 min | Lint noise -71% | Low |

---

*🔱 OMEGA ⬡ CLINE ⬡ CODEBASE-REVIEW ⬡ v2.0.0 ⬡ 2026-07-26*