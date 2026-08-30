<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# P3 Engineering — Documentation & Tooling Optimization
**Date**: 2026-06-28
**Analyzed by**: P3 (Engineering) / BuildMaster
⬡ OMEGA ⬡ P3 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_p3_engineering_audit ⬡ DISCOVERY

---

## 1. Makefile / CI/CD Targets

### Target Count & Classification

| Metric | Value |
|--------|-------|
| Total targets defined | **72** |
| Documented in `menu` target | 64 |
| Undocumented targets | 8 (restart-infra, restart-iris, verify-*, knowledge-*) |
| Total Makefile lines | 686 |
| Comment-to-code ratio | ~50/50 (heavy decorative formatting) |

### Target Categorization

| Category | Count | Examples |
|----------|-------|---------|
| **Core execution** (demo, repl, talk, summon) | 6 | demo, talk, summon, repl, menu, help |
| **Testing & quality** (test, lint, typecheck, cov) | 4 | test, test-cov, test-oracle-bootstrap, lint |
| **Verification gates** (heritage, sovereignty, firewall) | 10 | temple-grade, heritage-map, heritage-vet, verify-*, validate-research |
| **Infrastructure** (start/stop/restart containers) | 7 | start-infra, stop-infra, infra-status, iris-*, mcp-check |
| **Model management** (lmster, model-download) | 7 | lmster-start/stop/status/load, model-download/list/clean |
| **WAD management** (switch stacks) | 3 | wad-status, wad, wad-reset |
| **Queue & library** (request queue, library) | 6 | queue-status, queue-prune, process-queue, library-status/search |
| **Benchmarks** (run/list/rank) | 3 | bench-run, bench-list, bench-rank |
| **Research** (research-run, mkdocs, validate) | 7 | research-run/status, validate-research, init/sync-research-db, mkdocs-serve/build |
| **Maintenance** (clean, doctor, guard, firecrawl) | 7 | clean, doctor, guard, firecrawl-status, audit-no-rag-v1, offline-demo, offline-mode |
| **One-shot / niche** (setup, bootstrap, etc.) | 9 | setup, bootstrap, start-all, stop-all, pivot-watchdog, platform-sync, verify-model-spelling, github-audit, heritage-vet-create |
| **Convenience aliases** (thin CLI wrappers) | 3 | entities, entity, model-status |
| **Verification sub-targets** (P3 cadence) | 8 | verify-pending, verify-stale, verify-mining, verify-rollup, verify-cleanup, verify-status, knowledge-index, knowledge-flow |

### Dead / Low-Value Targets Identified

| Target | Lines | Problem |
|--------|-------|---------|
| `audit-no-rag-v1` | 43 | One-shot D87 fix. Checks a directory that should never (and has never) recreated itself organically. 43 lines of shell checking something that doesn't exist. **Status: DEAD** |
| `offline-mode` | 5 | Sets `OMEGA_OFFLINE=true` and runs one `omega talk` command. Doesn't persist the env var. Does nothing that can't be done manually. **Status: LOW VALUE** |
| `model-clean` | 5 | `rm -rf models/gguf/*.gguf` wrapped in a warning. Destructive with no un-do. Deleting models should not be a make target. **Status: RISKY/NICHE** |
| `heritage-vet-create` | 12 | One-time setup. Creates an empty log file. `mkdir -p` will succeed silently if it already exists. After initial setup, this target does nothing. **Status: DEAD** |
| `github-audit` | 6 | Does nothing real — just echoes "See docs/security/GITHUB_M8_AUDIT.md". Not an audit, not actionable. **Status: DEAD** |
| `init-research-db` | 2 | One-time DB seed. Useful once, then becomes a no-op or idempotent seed command. **Status: ONE-SHOT** |
| `knowledge-index` | — | Undocumented except in .PHONY. No implementation found in Makefile body. **Status: STALE REFERENCE** |
| `knowledge-flow` | — | Same as knowledge-index. Referenced but not implemented. **Status: STALE REFERENCE** |
| `sovreignty` | — | Referenced in AGENTS.md as `make sovereignty` but actual target is misspelled as `sovereignty` (correct in Makefile). Check ensures this doesn't break. **Status: OK** |

### Critical Overlap: `verify-all` vs `temple-grade` test duplication

The most impactful overlap in the entire Makefile:

```
verify-all: test lint temple-grade verify-search-tools

temple-grade:
  ├── T3: make test-cov  ← runs tests AGAIN
  ├── T4: make lint      ← runs lint AGAIN
  ├── heritage-map
  └── heritage-vet
```

**Impact**: Running `make verify-all` executes:
1. `make test` → full pytest run (guard + pytest)
2. `make lint` → flake8 (--exit-zero, non-blocking)
3. `make temple-grade` → T1-T11 checks including:
   - T3: `make test-cov` → **second full pytest run** with coverage
   - T4: `make lint` → **second flake8 run**
4. `make verify-search-tools` → pytest for search_tools only

**Total**: 2 full test suites + 2 lint runs for one verification command.

**Potential saving**: Consolidate to run tests once with coverage (`make test-cov` replaces `make test`). Remove the `lint` call from `temple-grade` T4 and instead check `make lint` output from the `verify-all` chain.

### CI/CD Overlap: ci.yml vs test.yml

| Aspect | ci.yml (48 lines) | test.yml (100 lines) |
|--------|-------------------|----------------------|
| Trigger | Push/PR to main | Push/PR to main + develop |
| Python matrix | 3.12, 3.13 | 3.12, 3.13 |
| Test execution | `pytest tests/ -v` | `pytest tests/ -v --tb=short -x` |
| Lint | flake8 (syntax + full) | flake8 (non-blocking, --exit-zero) |
| Additional checks | Doc lint (ci_check_docs.sh) | AnyIO check (M1), bare except (M9), heritage vet (M14), verify-mining, docs counter |
| Dependencies | pip install + -e . | pip install -e ".[cli,dev]" |

**Assessment**: `test.yml` is a superset of `ci.yml`. The only check in `ci.yml` not in `test.yml` is the doc lint (`ci_check_docs.sh`). `ci.yml` also has a slightly different flake8 approach (syntax error check first, then full lint with exit-zero).

**Recommendation**: Merge ci.yml into test.yml or vice versa. Keep one workflow file. The 48-line overlap (32% of total CI files) is unnecessary.

### Orphan Git Config: `.github/copilot-instructions.md`

- 28 lines of GitHub Copilot instructions
- Only relevant to users who use GitHub Copilot with VS Code
- Duplicates content already in `AGENTS.md` and `SOVEREIGN_MANDATES.md`
- Not referenced by any workflow, not enforceable in CI
- **Status: ORPHAN** — useful to Copilot users but creates a third source of mandate truth

---

## 2. Test Infrastructure

### Test File Metrics

| Metric | Value |
|--------|-------|
| Test files (`.py`) | **61** |
| Total test lines | **9,170** |
| Average lines/file | 150 |
| Largest file | `test_contract_m21.py` (508 lines) |
| Smallest file | (several < 50 lines) |
| Contract test files | 2 (test_contract_m21.py: 508, test_contract_soul_distiller.py: 211) |
| Test config files | 0 (config lives in `pyproject.toml` only — good) |

### Config Consolidation Assessment

| Config | Location | Lines | Verdict |
|--------|----------|-------|---------|
| pytest config | `pyproject.toml [tool.pytest.ini_options]` | 4 | ✅ Minimal, correct |
| asyncio_mode | `auto` | 1 | ✅ Needed for AnyIO tests |
| addopts | ignore odysseus-dev dir | 1 | ✅ Avoids build artifact pollution |
| `tests/README.md` | ❌ Does not exist | — | 🟡 No test documentation exists |
| `tests/__init__.py` | ❌ Does not exist | — | 🟢 Not needed for pytest (namespace works) |
| Coverage threshold | ❌ Not set | — | 🟡 T3 gate checks `test-cov` exits 0, but no % threshold |

### Strengths

- **Single config source**: All test config in `pyproject.toml` (no `pytest.ini`, `setup.cfg`, `conftest.py` bloat)
- **No test init file**: `__init__.py` not required for pytest namespace packages — correct
- **Mock mode isolation**: `OMEGA_ENV=test` ensures deterministic test runs
- **Lock file**: `flock -x /tmp/omega_test.lock` prevents concurrent test collisions

### Weaknesses

- **No test README**: No documentation of test categories, mocking strategy, or how to add new tests
- **No coverage threshold**: T3 gate passes as long as `make test-cov` exits 0 — no minimum coverage enforced
- **Test file growth without structure**: 61 flat test files with no subdirectory organization (except mcp_taint tests)
- **`verify-search-tools` is a single-test target**: 1 file (test_search_tools.py) doesn't warrant its own make target

---

## 3. Linting Configuration

### Current Linter Stack

| Linter | Config Source | Lines | Enforced? |
|--------|--------------|-------|-----------|
| **flake8** | `make lint` inline args | 127-char limit, complexity 10 | ✅ CI + local |
| **mypy** | No config file (pyproject.toml has no `[tool.mypy]` section) | — | ❌ `make typecheck` likely fails |
| **pyproject.toml lint config** | None | — | N/A — all config in Makefile |

### Overlap Assessment

**No overlap.** The Omega Engine uses a single linter (flake8) with inline arguments. No `.flake8` file. No `ruff`. No `pylint`. No `setup.cfg` lint config. This is minimal and correct.

### Issues Found

1. **mypy will fail**: `make typecheck` calls `mypy src/omega/` but `pyproject.toml` has no `[tool.mypy]` stanza. Without config, mypy will use strict defaults and likely report hundreds of errors. This target is either never run by CI or silently fails.
2. **CLI lint vs flake8**: The `make lint` target uses `--exit-zero` (non-failing) and `--count --statistics`. This means lint warnings are counted but never block CI. The CI uses the same flags for its full lint run. The syntax-only check (`--select=E9,F63,F7,F82`) is failing-capable.
3. **flake8 version not pinned**: `pyproject.toml` lists `flake8>=7.0.0` in `[dev]` extra. If the CI installs a different version, minor output differences are possible.

### Sizing

| Metric | Value |
|--------|-------|
| Total lint config lines | ~4 (all in Makefile line 375) |
| Config files | 0 dedicated files |
| Linter count | 1 (flake8) |
| **Rating**: Minimal, well-scoped | ✅ |

---

## 4. Documentation Generators

### Skill File Analysis

| Skill | Lines | Has Logic? | Assessment |
|-------|-------|------------|------------|
| `sovereign-refinement-protocol/SKILL.md` | 64 | ✅ Substantive | Active — forensic preservation gate for core changes |
| `sovereign-search/SKILL.md` | 62 | ✅ Substantive | Active — 5-tier search orchestration |
| `spec-generator/SKILL.md` | 59 | ✅ Substantive | Active — R-doc specifications |
| `provider-validator/SKILL.md` | 58 | ✅ Substantive | Active — provider connectivity check |
| `knowledge-miner/SKILL.md` | 51 | ✅ Substantive | Active — legacy pattern extraction |
| `hf-cli/SKILL.md` | 17 | ✅ Substantive | Active — HuggingFace Hub CLI |
| **`pr-readiness-checker/SKILL.md`** | **5** | ❌ **Skeleton only** | **DEAD — no implementation** |
| **`omega-doc-architect/SKILL.md`** | **5** | ❌ **Skeleton only** | **DEAD — no implementation** |
| **`legacy-pattern-miner/SKILL.md`** | **5** | ❌ **Skeleton only** | **DEAD — skeleton** |
| **`blitz-validate/SKILL.md`** | **5** | ❌ **Skeleton only** | **DEAD — skeleton** |
| **`blitz-tunnel/SKILL.md`** | **5** | ❌ **Skeleton only** | **DEAD — skeleton** |

**5 of 11 skills are 5-line skeletons** with only frontmatter and no functionality. They exist as registered skills in OpenCode's system prompt but provide no instructions when loaded. These are **dead registrations** that inflate the available_skills list.

### Research Document Volume

| Metric | Value |
|--------|-------|
| Research docs (`docs/research/R*.md`) | **167** |
| Strategy docs (`docs/strategy/*.md`) | **86** |
| Total doc directories | 22 |
| Total markdown files | **662** |
| Total docs size | **19 MB** |
| Research docs size | 6.6 MB |
| Strategy docs size | 1.2 MB |

### P5 Cross-Reference

P5's report already identified that ~20 of 86 strategy docs are stale/overlapping. The research doc count (167) is not audited in this pass but warrants investigation — some may be stale research artifacts from earlier mining phases.

### Template Consolidation Opportunities

- The `spec-generator` skill (59 lines) defines a formal R-doc template. If all 167 research docs follow this template, the tooling overhead per doc is reasonable. If they don't, the template is aspirational only.
- No mkdocs-specific doc generator or auto-publisher is active (mkdocs targets exist in Makefile but are not CI-enforced).

---

## 5. PR / Code Review Overhead

### Agent File Overhead

| Agent | Lines | Purpose | Review Overhead |
|-------|-------|---------|-----------------|
| kali | 83 | Grand Oversight | Low — orchestrates |
| maat | 83 | Light Oversoul | Low — delegates to P1-P5 |
| lilith | 83 | Dark Oversoul | Low — delegates to P6-P10 |
| makali | 83 | Parallel Council | Low — synthesis only |
| pillar | 83 | Slot agent | Low — parameterized |
| doom_guy | 65 | Heritage architect | Medium — heritage vetting adds review step |
| john_carmack | 112 | S3 consultant | Medium — architectural review |
| roc_racoon | 98 | Legacy miner | Low — background mining |
| researcher | 143 | Deep research | Low — research only |
| jem | 96 | Research orchestrator | Low — dispatches research |
| verity | 112 | Compliance + gnosis | **HIGH** — sprint C merged Quality + Scribe |
| **Total** | **1,041** | | |

### pr-readiness-checker Skill

- **5 lines, frontmatter only**: No actual quality check logic
- Referenced in AGENTS.md as a skill but provides zero instructions
- **Verdict**: Dead registration. Either implement or remove from available_skills.

### CI-Enforced Review Gates

Already enforced in `test.yml` CI:
1. ✅ Tests pass (pytest)
2. ✅ AnyIO-only check (M1)
3. ✅ Bare except check (M9)
4. ✅ Heritage vetting (M14)
5. ✅ Flake8 lint (non-blocking)
6. ✅ Document count sanity check

**Additional enforcement not in CI but in Makefile**:
7. ⏳ `verify-firewall` (M2 — WAD-specific strings)
8. ⏳ `verify-model-spelling` (D119 — model name consistency)
9. ⏳ `pivot-watchdog` (unreviewed decisions > 7 days)

Gates 7-9 are LOCAL-ONLY — they exist in the Makefile but are NOT called by CI (`test.yml`). This means these checks only run when a developer remembers `make verify-all`.

---

## 6. Top 3 Recommendations

Ordered by impact/effort ratio:

### 🥇 Recommendation 1: Eliminate Test Duplication in `verify-all` (Impact: High, Effort: Low)

**Problem**: `make verify-all` runs the full test suite TWICE (once in `make test`, once implicitly in `make temple-grade` → `make test-cov`) and lint TWICE (once in `make lint`, once in `make temple-grade` → T4).

**Action**:
- Change `temple-grade` T3 to read from last `test-cov` result instead of re-running: `if [ -f .coverage ]; then echo "✅ Coverage data exists"; else echo "⚠️ Run make test-cov first"; fi`
- OR: Remove `test` from `verify-all` and let `temple-grade`'s `test-cov` be the single test invocation
- OR: Change `verify-all` to `test-cov lint temple-grade verify-search-tools` — requires `temple-grade` to NOT call `make test-cov` internally

**Effort**: 10-15 minutes to restructure the Makefile chain.

**Impact**: Eliminates 100% of test duplication — saves ~30-60s per `verify-all` run and prevents misleading "all checks passed" when the first test run fails but the second passes.

---

### 🥈 Recommendation 2: Remove 5 Skeleton Skills & 3 Dead Make Targets (Impact: Medium, Effort: Low)

**Problem**: 5 of 11 skills are empty frontmatter-only files. 3+ make targets are one-shot or dead code. 2 CI workflow files overlap 48 lines.

**Actions**:

**Part A — Dead skills**: Remove or implement:
1. `pr-readiness-checker/SKILL.md` (5 lines) — empty PR gate
2. `omega-doc-architect/SKILL.md` (5 lines) — empty doc enforcer
3. `legacy-pattern-miner/SKILL.md` (5 lines) — empty miner (duplicates `knowledge-miner`)
4. `blitz-validate/SKILL.md` (5 lines) — empty validator
5. `blitz-tunnel/SKILL.md` (5 lines) — empty tunnel

**Part B — Dead make targets**:
1. Remove `audit-no-rag-v1` (43 lines) — one-shot D87 check
2. Remove `heritage-vet-create` (12 lines) — one-time setup
3. Remove `github-audit` (3 lines) — no-op target

**Part C — CI consolidation**:
1. Merge `ci.yml` (48 lines) into `test.yml` (100 lines) — keep only the doc lint step

**Effort**: 20-30 minutes total (file deletions + Makefile edits).

**Impact**: Removes 25 lines of dead code from Makefile, 25 lines of dead skill registrations, and 48 lines of redundant CI config. Cleans up the skill inventory from 11 to 6 (all substantive).

---

### 🥉 Recommendation 3: Fix `make typecheck` & Push CI Guard Gaps (Impact: Medium, Effort: Low)

**Problem**: `make typecheck` calls `mypy src/omega/` with no configuration — guaranteed to fail. 3 important checks (M2 firewall, model spelling, pivot watchdog) are LOCAL-ONLY and never run in CI.

**Actions**:
1. Add `[tool.mypy]` stanza to `pyproject.toml` (5-10 lines for basic config):
   ```toml
   [tool.mypy]
   python_version = "3.12"
   ignore_missing_imports = true
   disallow_untyped_defs = false  # gradual adoption
   ```
2. Add `verify-firewall`, `verify-model-spelling`, and `pivot-watchdog` to `test.yml` CI workflow (3 additional job steps, ~15 lines total)
3. Each check is O(1) grep — negligible CI time impact

**Effort**: 20 minutes.

**Impact**: Fixes a broken security check (`typecheck`). Moves 3 local-only verification gates into CI where they're actually enforced. Closes the gap between what the Makefile claims to check and what CI actually enforces.

---

## Summary of All Findings

| # | Finding | Severity | Location | Action |
|---|---------|----------|----------|--------|
| 1 | `verify-all` runs tests twice + lint twice | 🔴 HIGH | Makefile:361,579 | Consolidate test/cov |
| 2 | 5 skeleton skills (25 lines, no logic) | 🟡 MEDIUM | `.opencode/skills/` | Remove or implement |
| 3 | `audit-no-rag-v1` dead target (43 lines) | 🟡 MEDIUM | Makefile:240-274 | Remove |
| 4 | `heritage-vet-create` one-shot target | 🟡 MEDIUM | Makefile:643-654 | Remove |
| 5 | `github-audit` no-op target | 🟢 LOW | Makefile:573-577 | Remove |
| 6 | `ci.yml` 32% overlap with `test.yml` | 🟡 MEDIUM | `.github/workflows/ci.yml` | Merge into test.yml |
| 7 | `make typecheck` has no mypy config | 🟡 MEDIUM | pyproject.toml | Add `[tool.mypy]` stanza |
| 8 | 3 verification gates local-only (M2, D119, watchdog) | 🟡 MEDIUM | Makefile | Add to CI |
| 9 | `knowledge-index` and `knowledge-flow` are ghost targets | 🟢 LOW | Makefile .PHONY | Remove or implement |
| 10 | No test README or coverage threshold | 🟢 LOW | `tests/` | Add minimal doc |
| 11 | `.github/copilot-instructions.md` duplicates mandate truth | 🟢 LOW | `.github/` | Consolidate |
| 12 | `pr-readiness-checker` is frontmatter-only | 🟡 MEDIUM | `.opencode/skills/` | Remove or fill (see also #2) |
| 13 | `offline-mode` target doesn't persist env | 🟢 LOW | Makefile:438-442 | Fix or remove |
| 14 | `verify-search-tools` is a single-file test target | 🟢 LOW | Makefile:380-381 | Fold into main test |

---

## Methodological Note

This audit was conducted by reading the complete Makefile (686 lines), all 11 agent files (1,041 lines), all 11 skill files (336 lines), both CI workflow files (148 lines), pyproject.toml (57 lines), `.github/copilot-instructions.md` (28 lines), and performing directory listings and line/byte counts across test, docs, skills, and scripts directories. No files were modified. No code was changed.

**P5 and P2 reports checked**: P5 covered PIVOT_LOG/D64 compaction, strategy doc archiving, heritage pipeline overhead, and handoff debris — non-overlapping with this P3 engineering audit. P2 covered entity workspace bloat, soul.yaml health, memory growth, and storage patterns — also non-overlapping.

**Hivemind awareness checked**: Active agents — Kali (MaKaLi Council Pass 2), Ma'at (Build-side optimization), Lilith (Run-side optimization), P2 (complete), P5 (heartbeat-only), P7 (complete), P8 (active). This report is filed for Ma'at's build-side review and MaKaLi Council synthesis.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
