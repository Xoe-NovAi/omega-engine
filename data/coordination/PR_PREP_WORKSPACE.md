# 🔱 Omega Engine — PR Prep Workspace
# ⬡ OMEGA ⬡ PREP ⬡ opencode ⬡ trc_pr_prep ⬡ EVOLVING
**AP Token**: `AP-PR-PREP-v1.0.0`
**Created**: 2026-07-13
**Last Revised**: 2026-07-14
**Status**: 🟡 EVOLVING (checklist, not a plan — items can be reordered, split, or dropped)
**Anchor**: D231 (7 Pre-PR Quick Wins — base layer)

---

## Operating Model: Solo Dev, Zero Cash, Free & Open Source

**This workspace tracks PR hardening for a solo developer using only free tools and open-source dependencies.**

The $6.1M agency-build figure and the $139K design-studio-hardening figure in the parent conversation are **reference valuations** — they establish the replacement cost and quality ceiling. The execution path is:

| Dimension | Approach |
|-----------|----------|
| **Budget** | $0 cash outlay. 8,000 hours already invested. Time is the only currency. |
| **Tools** | ruff (free), mypy (free), pre-commit (free), pytest (free), mkdocs (free), GitHub Actions (free), pyright (free) |
| **Design** | Free icon sets (Font Awesome, Material Icons), open-source MkDocs themes, ASCII/Unicode art. No designer. |
| **Security** | pip-audit (free), bandit (free), OpenSSF Scorecard (free), Dependabot (free) |
| **CI** | GitHub Actions free tier. Self-hosted runner on the Ryzen 5700U for heavier tests. |
| **Release** | PyPI (free), GitHub Releases (free), Homebrew (free for open source) |
| **Community** | GitHub Discussions (free), Discord free tier, OpenSSF Best Practices badge (free) |
| **Rate** | Time valued at opportunity cost, not billable rate. The 8,000-hour investment is sunk — this is iterative improvement. |

**What this changes from the cost-analysis framing:**
- Tiers 2 and 3 shift from "hire a designer/security firm" to "use free templates, automate what you can, accept the quality ceiling."
- The ~700h estimate is real solo-dev time, not billable hours. There's no acceleration through parallel team members.
- Prioritization tilts toward items only you can do (architecture, patterns) over items a team would parallelize (lint fixes, doc cleanup).

**What this doesn't change:**
- T0 bugs (F821, bare excepts) must still be fixed — they're real crashes.
- CI must still gate on quality. Free tools are the enforcers.
- Documentation must still be clear. MkDocs + your typing is the tool.

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

## §4 Tier 2 — Visual & Interaction (Solo Dev, Free Tools)

**Vibe**: Make it feel intentional using free design assets and AI tooling. No designer = no custom illustration, but clean typography, consistent iconography, and a well-organized MkDocs theme are fully achievable.

### 4.1 — Design System (Free Tier)

| Item | What | Effort | Status | Tool |
|------|------|--------|--------|------|
| DS01 | Document existing palette (deep purple/amber from mkdocs.yml) as style guide | 2h | 🔵 | MkDocs + markdown |
| DS02 | Standardize CLI output templates in Rich: `OmegaConsole` wrapper class | 6h | 🔵 | Rich library (free, open source) |
| DS03 | Create `omega status` terminal dashboard using Rich Layout | 10h | 🔵 | Rich Layout + Panel |
| DS04 | Standardize error display: `OmegaError` → Rich `Panel` with trace_id, suggestion | 4h | 🔵 | Rich Panel |

### 4.2 — Voice & Tone (Solo-Dev Scope)

| Item | What | Effort | Status | Method |
|------|------|--------|--------|--------|
| VT01 | Draft tone notes per entity — 2-3 sentences each, distilled from existing system prompts | 6h | 🔵 | Extract from entity YAML prompt fields |
| VT02 | Standardize error message format: `[Emoji] [Entity]: [Message] — [Suggestion]` | 3h | 🔵 | Template in `OmegaError.__str__` |
| VT03 | Script "first 5 minutes" walkthrough in README — exact commands, expected output | 4h | 🔵 | Markdown with embedded terminal blocks |

### 4.3 — Visual Identity (Free Assets)

| Item | What | Effort | Status | Method |
|------|------|--------|--------|--------|
| VI01 | Logo: `⬡` symbol + "OMEGA" in monospace ASCII. Clean, recognizable, zero cost. | 2h | 🔵 | Unicode + monospace font |
| VI02 | GitHub social preview: generate via `pillow` script in repo | 3h | 🔵 | Python + PIL (free) |
| VI03 | Refine MkDocs theme: Material deep-purple is already configured. Tweak nav structure, add logo. | 4h | 🔵 | MkDocs Material config |
| VI04 | Favicon: Unicode ⬡ (U+2B21) or generate SVG via script | 1h | 🔵 | Inline SVG |

---

## §5 Tier 3 — Production Gloss (Solo Dev, Free Infrastructure)

**Vibe**: Free-tier CI/CD, open-source security tooling, community platforms with no cost. Accept that some items (pen test, dedicated designer) are deferred indefinitely.

### 5.1 — Release Engineering (Free Tier)

| Item | What | Effort | Status | Tool |
|------|------|--------|--------|------|
| R01 | Set up `python-semantic-release` for automated version bumps | 8h | 🔵 | python-semantic-release (free) |
| R02 | Create PyPI publishing workflow (GitHub Action) | 4h | 🔵 | GitHub Actions free tier + PyPI trusted publishing |
| R03 | Create `curl -fsSL https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/scripts/install.sh \| bash` one-liner | 6h | 🔵 | Raw GitHub URL + bash |
| R04 | Build + publish Docker images to GHCR (GitHub Container Registry) | 8h | 🔵 | GHCR free for public images |
| R05 | Add SBOM generation (CycloneDX) per release | 4h | 🔵 | `pip-licenses` + `cyclonedx-bom` (free) |

### 5.2 — Testing Maturity (Free Tools)

| Item | What | Effort | Status | Tool |
|------|------|--------|--------|------|
| T01 | Add property-based tests with Hypothesis | 20h | 🔵 | Hypothesis (free) |
| T02 | Add fuzz testing for YAML config parser | 8h | 🔵 | python-afl / atheris (free) |
| T03 | Add performance regression benchmarks (`pytest-benchmark`) | 12h | 🔵 | pytest-benchmark (free) |
| T04 | Add load test: 50 concurrent `omega talk` calls via locust | 16h | 🔵 | locust (free) |
| T05 | Add mutation testing (`mutmut`) for test quality validation | 12h | 🔵 | mutmut (free) |

### 5.3 — Security Posture (Free Tools Only)

| Item | What | Effort | Status | Tool |
|------|------|--------|--------|------|
| S01 | Add `pip-audit` + `bandit` to CI pipeline | 4h | 🔵 | pip-audit, bandit (free) |
| S02 | Enable Dependabot for automated dependency updates | 1h | 🔵 | GitHub native (free) |
| S03 | Apply for OpenSSF Best Practices badge | 4h | 🔵 | OpenSSF (free) |
| S04 | Supply chain: OpenSSF Scorecard action in CI | 2h | 🔵 | scorecard-action (free) |
| S05 | Add `grype` or `trivy` for container image scanning | 3h | 🔵 | grype/trivy (free, open source) |
| ~~ | ~~Third-party penetration test~~ | ~~$15-25K~~ | 🔴 DEFERRED | Not in scope for zero-cash project |
| ~~ | ~~GPG-signed commits as CI requirement~~ | ~~2h~~ | 🔴 DEFERRED | Overhead exceeds threat model for solo dev |

### 5.4 — Community Infrastructure (Free Platforms)

| Item | What | Effort | Status | Platform |
|------|------|--------|--------|----------|
| C01 | Set up GitHub Discussions for community Q&A | 1h | 🔵 | GitHub native (free) |
| C02 | Create public roadmap (GitHub Projects) | 3h | 🔵 | GitHub Projects (free) |
| C03 | Write contributor ladder: first-timer → regular → maintainer | 2h | 🔵 | CONTRIBUTING.md update |
| C04 | Set up monthly release cadence with release notes template | 2h | 🔵 | GitHub Releases (free) |
| ~~ | ~~Discord/Discourse server~~ | ~~8h~~ | 🔴 DEFERRED | Until there's a community to serve |

### 5.5 — Hardware Certification (Solo Scope)

| Item | What | Effort | Status | Method |
|------|------|--------|--------|--------|
| H01 | Test + document on your Ryzen 7 5700U (the primary target) | 2h | 🔵 | Already running — document existing benchmarks |
| H02 | Test + document on a clean Ubuntu 24.04 VM | 6h | 🔵 | Free VM via VirtualBox or cloud free tier |
| H03 | Publish RAM/CPU benchmarks per model size (Qwen 1.7B, Qwen 4B, DeepSeek-R1-8B) | 6h | 🔵 | `hyperfine` + markdown tables |
| ~~ | ~~macOS testing~~ | ~~8h~~ | 🔴 DEFERRED | No Mac hardware available |
| ~~ | ~~Raspberry Pi testing~~ | ~~8h~~ | 🔴 DEFERRED | Not in scope for solo dev |

---

## §6 Progress Dashboard

```
Overall: 0/76 tasks complete • ⏱ 0h / ~550h estimated
Breakdown:
  §1 D231 Quick Wins:    0/7 • ⏱ 0h / 52min
  §2 Tier 0 (Ship-It):   0/40 • ⏱ 0h / 80h
  §3 Tier 1 (DX):        0/23 • ⏱ 0h / 120h
  §4 Tier 2 (Design):    0/11 • ⏱ 0h / 41h (solo scope)
  §5 Tier 3 (Production): 0/18 • ⏱ 0h / ~126h (free-tools scope)
  Deferred (cash items):   —-  • ~145h (deferred indefinitely)
```

### Deferred Indefinitely (Cash Items)

| Item | Original Est. | Reason |
|------|--------------|--------|
| Third-party penetration test | $15-25K | Free tools (pip-audit, bandit, scorecard) cover 80% |
| Professional designer (logo, theme) | ~$10K | Unicode logo + MkDocs Material default. Good enough. |
| macOS testing | 8h | No Mac hardware. Accept the gap. |
| Raspberry Pi testing | 8h | Out of scope for solo dev. |
| GPU support | N/A | CPU-only architecture. Validated choice. |
| Discourse community server | 8h set-up | GitHub Discussions until needed. |

### Current Blockers

| Blocker | Tied To | Notes |
|---------|---------|-------|
| None yet | — | First: execute D231 Quick Wins (52min) |

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
