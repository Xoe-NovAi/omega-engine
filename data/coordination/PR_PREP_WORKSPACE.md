# 🔱 Omega Engine — PR Prep Workspace
# ⬡ OMEGA ⬡ PREP ⬡ opencode ⬡ trc_pr_prep ⬡ EVOLVING
**AP Token**: `AP-PR-PREP-v1.0.0`
**Created**: 2026-07-13
**Status**: 🟡 EVOLVING (checklist, not a plan — items can be reordered, split, or dropped)
**Anchor**: D231 (7 Pre-PR Quick Wins — base layer)

---

## Navigation

| Section | Description |
|---------|-------------|
| [§1 Sprint Zero — D231 Quick Wins](#s1-sprint-zero--d231-quick-wins) | Already in motion, ~62min total |
| [§2 Tier 0 — Ship-It Bar](#s2-tier-0--ship-it-bar) | Bugs + hygiene. 80h. Non-negotiables. |
| [§3 Tier 1 — Developer Experience](#s3-tier-1--developer-experience) | DX polish. 120h. Makes strangers feel at home. |
| [§4 Tier 2 — Visual & Interaction](#s4-tier-2--visual--interaction) | Design system + UX. 200h. Requires design resource. |
| [§5 Tier 3 — Production Gloss](#s5-tier-3--production-gloss) | Release engineering + security. 300h. |
| [§6 Progress Dashboard](#s6-progress-dashboard) | Roll-up status, velocity, blockers |
| [§7 Decision Log](#s7-decision-log) | PR-prep decisions as they're made |
| [§8 Done Pile](#s8-done-pile) | Completed items moved here |
| [§9 Reference — Verity Full Audit](#s9-reference--verity-full-audit) | Raw findings from forensic scan |

---

## §1 Sprint Zero — D231 Quick Wins

**Source**: `docs/decisions/PIVOT_LOG.md` D231
**Target**: Clean Temple-Grade pass, zero errors, minimal warnings.

| # | Item | Files | ⏱ | Status | Verified |
|---|------|-------|----|--------|----------|
| Q1 | **Fix runtime warnings** — unawaited mock coroutines | `tests/test_somatic_state.py:50`, `tests/test_unified_state_manager.py` | 10m | 🟡 | ❌ |
| Q2 | **Fix firewall warnings** — add allowlist for Core Engine entities | `src/omega/audit/firewall_checker.py` | 5m | 🟡 | ❌ |
| Q3 | **Fix pytest deprecation warnings** — `utcnow()` → `now(timezone.utc)` | `tests/test_scorecard.py`, `tests/test_sandbox.py` | 10m | 🟡 | ❌ |
| Q4 | **Clear .pytest_cache** before CI | CI script | 2m | 🟡 | ❌ |
| Q5 | **Docs sync** — test counts (1315), mandates (23), version (v1.2.0) | `OMEGA_ENGINE.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `README.md` | 5m | 🟡 | ❌ |
| Q6 | **Heritage migration** — legacy `[id-soft: game-year]` → `[id-soft: vet-XXX]` | `src/omega/**/*.py` | 15m | 🟡 | ❌ |
| Q7 | **PIVOT_LOG entry** — D228-D234 | `docs/decisions/PIVOT_LOG.md` | 5m | 🟡 | ❌ |

**Gate**: `make test && make heritage-map && make heritage-vet && make mandate-audit && make firewall-check`

---

## §2 Tier 0 — Ship-It Bar

**Vibe**: Things a professional studio fixes before showing code to a client. Bugs first.

### 2.1 — 30 Scope: Fix 30 Undefined-Name Bugs (F821)

| Item | File:Line | Symbol | Fix | Effort | Status |
|------|-----------|--------|-----|--------|--------|
| B01 | `src/omega/oracle/subagent_dispatcher.py:160` | `anyio` | Add `import anyio` | 1m | 🟡 |
| B02 | `src/omega/research/sandbox.py:399` | `ResearchProposal` | Add import | 1m | 🟡 |
| B03 | `src/omega/research/sandbox.py:502` | `ResearchProposal` | Same missing import | 1m | 🟡 |
| B04 | `src/omega/research/sandbox.py:556` | `ResearchProposal` | Same missing import | 1m | 🟡 |
| B05 | `src/omega/research/scorecard.py:320` | `tier_start` | Define or import variable | 2m | 🟡 |
| B06 | `src/omega/research/scorecard.py:345` | `tier_start` | Same undefined variable | 2m | 🟡 |
| B07-30 | (remaining F821 errors) | various | Run `ruff check --select F821` for full list | 10m | 🔵 |

**Gate**: `ruff check --select F821 src/omega/ --exit-non-zero-on-fix` → zero errors

### 2.2 — 30 Scope: Replace 19 Bare `except Exception:`

| Item | File:Line | Current | Fix | Effort | Status |
|------|-----------|---------|-----|--------|--------|
| E01 | `src/omega/research/hivemind_bridge.py:164` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E02 | `src/omega/research/hivemind_bridge.py:198` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E03-02 | `src/omega/research/sandbox.py:520,551` | `except Exception:` | Type-specific catch | 10m | 🟡 |
| E05-08 | `src/omega/audit/mandate_auditor.py:95,130,225,285` | `except Exception:` | Type-specific catch | 20m | 🟡 |
| E09 | `src/omega/rag/iterative_rag.py:63` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E10 | `src/omega/rag/simple_rag.py:39` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E11 | `src/omega/workers/youtube_worker.py:1016` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E12-14 | `src/omega/governance/budget_guard.py:196,309,365` | `except Exception:` | Type-specific catch | 15m | 🟡 |
| E15 | `src/omega/workers/background_researcher/run.py:74` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E16 | `src/omega/oracle/providers.py:44` | `except Exception:` | Type-specific catch | 5m | 🟡 |
| E17 | `src/omega/research/scorecard.py:133` | `except Exception:` | Type-specific catch | 5m | 🟡 |

**Gate**: `grep -rn "except Exception:" src/omega/ --include="*.py" | grep -v "# noqa"` → zero

### 2.3 — 30 Scope: Centralize Logging

| Item | What | Effort | Status |
|------|------|--------|--------|
| L01 | Create `src/omega/logging.py` with `setup_logging(level, json_format, trace_id)` | 2h | 🟡 |
| L02 | Replace 3 scattered `logging.basicConfig()` calls (iris/server.py, workers/.../run.py, hmc_watcher.py) | 1h | 🟡 |
| L03 | Wire `setup_logging()` into CLI entry point (`oracle_cli.py:main`) | 30m | 🟡 |
| L04 | Add log-level override via `--log-level` / `OMEGA_LOG_LEVEL` env var | 30m | 🟡 |

**Gate**: One function configures all logging. Zero `basicConfig` calls outside `src/omega/logging.py`.

### 2.4 — 30 Scope: Config Validation

| Item | What | Effort | Status |
|------|------|--------|--------|
| C01 | Create `src/omega/config.py` with Pydantic `OmegaConfig(BaseSettings)` | 4h | 🟡 |
| C02 | Fix duplicated `sovereignty_gate` block in `config/omega.yaml` (lines 51-55 and 73-77) | 5m | 🟡 |
| C03 | Route all `yaml.safe_load()` calls through single cached loader | 2h | 🟡 |
| C04 | Add schema validation at boot — reject unknown keys | 1h | 🟡 |

**Gate**: `omega talk "hello"` validates entire config tree at startup. Unknown YAML keys raise `ConfigError`.

### 2.5 — 30 Scope: CI Surgery

| Item | What | Effort | Status |
|------|------|--------|--------|
| CI01 | Merge `ci.yml` + `test.yml` into single `.github/workflows/omega-ci.yml` | 1h | 🟡 |
| CI02 | Add coverage gate: `pytest-cov` → ≥80% or fail | 30m | 🟡 |
| CI03 | Add `make temple-grade` to CI pipeline | 10m | 🟡 |
| CI04 | Add M2 Firewall check: `make firewall-check` in CI | 10m | 🟡 |
| CI05 | Add `pre-commit` config (`.pre-commit-config.yaml`): ruff, mypy, trailing-whitespace, end-of-file-fixer | 30m | 🟡 |

**Gate**: Single CI workflow. Coverage gate blocks <80%. Temple-grade runs every push.

### 2.6 — 30 Scope: Infrastructure Quick Fixes

| Item | What | Effort | Status |
|------|------|--------|--------|
| I01 | Create `CODE_OF_CONDUCT.md` (referenced in CONTRIBUTING.md but missing) | 5m | 🟡 |
| I02 | Create `scripts/uninstall.sh` | 1h | 🟡 |
| I03 | Fix `mkdocs.yml` repo URL (`arcana-novai` → `Xoe-NovAi`) | 1m | 🟡 |
| I04 | Add `SECURITY.md` with vulnerability reporting policy | 15m | 🟡 |

**Gate**: All community-standard files present. Uninstall works. MkDocs links resolve.

---

## §3 Tier 1 — Developer Experience

**Vibe**: A stranger clones the repo and feels at home in 5 minutes.

### 3.1 — DX Scope: Package Professionalism

| Item | What | Effort | Status |
|------|------|--------|--------|
| P01 | Add `py.typed` marker for PEP 561 compliance | 1m | 🔵 |
| P02 | Lock all deps: `pip freeze > requirements.lock` + CI drift check | 30m | 🔵 |
| P03 | Create `CHANGELOG.md` following Keep a Changelog | 1h | 🔵 |
| P04 | Add GitHub issue templates (`.github/ISSUE_TEMPLATE/`) | 1h | 🔵 |
| P05 | Add `pyproject.toml` classifiers + long_description_content_type | 15m | 🔵 |

### 3.2 — DX Scope: CLI Polish

| Item | What | Effort | Status |
|------|------|--------|--------|
| T01 | Add Rich `Progress` spinner during model loading (current: silent freeze) | 2h | 🔵 |
| T02 | Wire `rich.traceback.install()` for syntax-highlighted tracebacks | 30m | 🔵 |
| T03 | Create `omega doctor` — health check for all subsystems | 4h | 🔵 |
| T04 | Add shell completion: `omega --install-completion` | 30m | 🔵 |
| T05 | Create `omega status` dashboard — containers, models, memory | 4h | 🔵 |

### 3.3 — DX Scope: Onboarding Flow

| Item | What | Effort | Status |
|------|------|--------|--------|
| O01 | Create `omega init` wizard: detect hardware → recommend model → scaffold entity | 8h | 🔵 |
| O02 | Upgrade `make demo` to a guided walkthrough (not just pytest) | 4h | 🔵 |
| O03 | Wire `make setup` as a single-command bootstrap (`make → venv → deps → model-download`) | 2h | 🔵 |

### 3.4 — DX Scope: Type Coverage

| Item | What | Effort | Status |
|------|------|--------|--------|
| Y01 | Annotate 506 untyped functions → raise coverage 75.6% → ≥95% | 20h | 🔵 |
| Y02 | Add `mypy --strict` to CI (gradual: start with `src/omega/oracle/`) | 2h | 🔵 |
| Y03 | Add `mypy.ini` / `pyproject.toml` mypy config | 15m | 🔵 |

### 3.5 — DX Scope: Lint Zero

| Item | What | Effort | Status |
|------|------|--------|--------|
| L01 | `ruff check --fix src/omega/` — auto-fix 80% of 9,897 violations | 2h | 🔵 |
| L02 | Manual fix remaining E501 (line length), F401 (unused imports), W293 (blank line whitespace) | 8h | 🔵 |
| L03 | Add `ruff` config to `pyproject.toml` (`line-length = 120`, `select = ["ALL"]`) | 15m | 🔵 |
| L04 | Make lint pass mandatory in CI (currently `continue-on-error: true`) | 10m | 🔵 |

### 3.6 — DX Scope: Auto-Generated API Docs

| Item | What | Effort | Status |
|------|------|--------|--------|
| D01 | Add `mkdocstrings` plugin to `mkdocs.yml` | 1h | 🔵 |
| D02 | Generate API docs: `pdoc src/omega/ -o docs/api/` | 2h | 🔵 |
| D03 | Wire `mkdocs build` into CI with link checking (`lychee`) | 1h | 🔵 |
| D04 | Publish to GitHub Pages on push to main | 30m | 🔵 |

### 3.7 — DX Scope: Brand Consistency

| Item | What | Effort | Status |
|------|------|--------|--------|
| B01 | Add `⬡ OMEGA` header to 615 missing `.md` files | 4h | 🔵 |
| B02 | Create `make verify-branding` CI gate | 30m | 🔵 |
| B03 | Standardize session header format across all docs | 2h | 🔵 |

---

## §4 Tier 2 — Visual & Interaction

**Vibe**: A product designer spends 2 weeks making it feel intentional.

### 4.1 — Design System

| Item | What | Effort | Status |
|------|------|--------|--------|
| DS01 | Create visual style guide: palette, typography, spacing, icon conventions | 40h | 🔵 |
| DS02 | Design consistent CLI output patterns: success, error, warning, info, progress | 20h | 🔵 |
| DS03 | Design terminal "dashboard" mockup for `omega status` | 10h | 🔵 |
| DS04 | Create empty-state designs for every CLI command | 10h | 🔵 |

### 4.2 — Voice & Tone

| Item | What | Effort | Status |
|------|------|--------|--------|
| VT01 | Write tone guidelines per entity (Sekhmet: blunt, Prometheus: prophetic, Iris: warm) | 15h | 🔵 |
| VT02 | Design error message templates with personality (not bare tracebacks) | 10h | 🔵 |
| VT03 | Script "first 5 minutes" interaction flow: clone → setup → init → talk | 15h | 🔵 |

### 4.3 — Visual Identity

| Item | What | Effort | Status |
|------|------|--------|--------|
| VI01 | Logo design (vector: SVG + PNG variants, favicon, social card) | 30h | 🔵 |
| VI02 | Refine MkDocs theme beyond deep-purple default | 15h | 🔵 |
| VI03 | Create GitHub social preview image (1280×640) | 5h | 🔵 |
| VI04 | Presentation / deck template for Xoe-NovAi Foundation | 10h | 🔵 |

---

## §5 Tier 3 — Production Studio Gloss

**Vibe**: Commercial product polish. 300h+ of release engineering, security, and community infra.

### 5.1 — Release Engineering

| Item | What | Effort | Status |
|------|------|--------|--------|
| R01 | Set up `python-semantic-release` for automated version bumps | 8h | 🔵 |
| R02 | Create PyPI publishing workflow (GitHub Action) | 4h | 🔵 |
| R03 | Create Homebrew tap formula for macOS | 8h | 🔵 |
| R04 | Build + publish Docker images to GHCR | 8h | 🔵 |
| R05 | Create `curl https://omega.xoe-nov.ai/install \| bash` one-liner | 12h | 🔵 |
| R06 | Add SBOM generation (CycloneDX) per release | 4h | 🔵 |

### 5.2 — Testing Maturity

| Item | What | Effort | Status |
|------|------|--------|--------|
| T01 | Add property-based tests with Hypothesis | 20h | 🔵 |
| T02 | Add fuzz testing for YAML config parser | 8h | 🔵 |
| T03 | Add performance regression benchmarks (`pytest-benchmark`) | 12h | 🔵 |
| T04 | Add load test: 50 concurrent `omega talk` calls | 16h | 🔵 |
| T05 | Add mutation testing (`mutmut`) to validate test quality | 12h | 🔵 |

### 5.3 — Security Posture

| Item | What | Effort | Status |
|------|------|--------|--------|
| S01 | Third-party penetration test | $15-25K | 🔵 |
| S02 | Supply chain security: `pip-audit`, Dependabot, OpenSSF Scorecard | 8h | 🔵 |
| S03 | GPG-signed commits as CI requirement | 2h | 🔵 |
| S04 | Add `pip audit` + `bandit` to CI | 4h | 🔵 |
| S05 | Generate SPDX SBOM for each release | 4h | 🔵 |

### 5.4 — Community Infrastructure

| Item | What | Effort | Status |
|------|------|--------|--------|
| C01 | Set up Discord / Discourse for community support | 8h | 🔵 |
| C02 | Apply for OpenSSF Best Practices badge | 4h | 🔵 |
| C03 | Create public roadmap (GitHub Projects) | 4h | 🔵 |
| C04 | Write contributor ladder: first-timer → regular → maintainer | 4h | 🔵 |
| C05 | Set up monthly release cadence with release notes template | 4h | 🔵 |

### 5.5 — Hardware Certification

| Item | What | Effort | Status |
|------|------|--------|--------|
| H01 | Test + document on vanilla Ubuntu 24.04 | 8h | 🔵 |
| H02 | Test + document on macOS (Apple Silicon + Intel) | 8h | 🔵 |
| H03 | Test + document on Fedora 40 | 4h | 🔵 |
| H04 | Test + document on Raspberry Pi 5 (8GB) | 8h | 🔵 |
| H05 | Publish RAM/CPU benchmarks per model size | 8h | 🔵 |

---

## §6 Progress Dashboard

```
Overall: 0/82 tasks complete • ⏱ 0h / 700h estimated
Breakdown:
  §1 D231 Quick Wins:    0/7 • ⏱ 0h / 52min
  §2 Tier 0 (Ship-It):   0/40 • ⏱ 0h / 80h
  §3 Tier 1 (DX):        0/23 • ⏱ 0h / 120h
  §4 Tier 2 (Design):    0/10 • ⏱ 0h / 200h
  §5 Tier 3 (Production): 0/19 • ⏱ 0h / 300h
```

### Current Blockers

| Blocker | Tied To | Notes |
|---------|---------|-------|
| None yet | — | First: execute D231 Quick Wins (62min) |

### Current Velocity

| Metric | Value |
|--------|-------|
| Tasks completed this session | 0 |
| Hours logged this session | 0 |
| Items in progress | 0 |

---

## §7 Decision Log

| # | Date | Decision | Rationale |
|---|------|----------|-----------|
| P01 | 2026-07-13 | **Workspace created** | Consolidate all PR-prep work into single tracked workspace |

---

## §8 Done Pile

| # | Item | Completed | Verified By | Notes |
|---|------|-----------|-------------|-------|
| — | — | — | — | — |

---

## §9 Reference — Verity Full Audit

**Source**: Verity audit 2026-07-13. See `data/coordination/VERITY_PROFESSIONAL_AUDIT.md` for raw data.

### 9.1 Type Coverage
```
def declarations:     2,078
with -> ReturnType:   1,572  (75.6%)
missing:               506
target:              ≥95%
```

### 9.2 Lint Violations
```
E501  Line too long        3,569  🔴
W293  Blank line whitespace 2,501  🔴
F401  Unused import          914  🔴
W291  Trailing whitespace    277
E302  Expected 2 blank lines 262
F821  Undefined name          30  🔴 BUGS
F811  Redefinition            82
F841  Unused variable         26
E402  Import not at top       57
...others...
TOTAL                      ~9,897
```

### 9.3 Error Handling
```
Custom exception classes:  65  (OmegaError hierarchy)
Bare `except:`:             0  ✅
Bare `except Exception:`:  19  🔴 needs triage
```

### 9.4 Config
```
YAML files:                10
Central loader:             ❌ (ad-hoc yaml.safe_load at 20+ call sites)
Schema validation:          ❌
Duplicated blocks:          1  (sovereignty_gate at lines 51-55 and 73-77)
```

### 9.5 Community Standards
```
README:            ✅ (7/7 criteria)
CONTRIBUTING.md:   ✅ (236 lines, thorough)
CODE_OF_CONDUCT:   ❌ MISSING (referenced but absent)
LICENSE:           ✅ (Apache 2.0)
SECURITY.md:       ❌ MISSING
CHANGELOG.md:      ❌ MISSING
Issue templates:   ❌ MISSING
```

### 9.6 CI
```
ci.yml:                        present (largely redundant with test.yml)
test.yml:                      present
Coverage gate (≥80%):          ❌
make temple-grade in CI:       ❌
M2 Firewall check in CI:       ❌
pre-commit hooks:              ❌
```

---
*Last updated: 2026-07-13 • Items marked 🟡 (pending), 🔵 (backlog), ✅ (done), ❌ (failed)*
