<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Consolidated Roadmap (v1.2.1 Target)
**AP Token**: `AP-ROADMAP-v1.2.1`
**Last Updated**: 2026-07-13
**Source**: MaKaLi Council Verdict + PR_PREP_WORKSPACE.md + Oversight Fixes

---

## 📊 **Current State (Post-Fixes)**

| Metric | Value | Status |
|--------|-------|--------|
| Tests | 1130 passed, 42 skipped, 3 xfailed | ✅ (1 pre-existing bug fixed) |
| sqlite-vec | v0.1.9 installed, verified | ✅ |
| INBOX_DIR crash | Fixed | ✅ |
| Qdrant lazy-import | Fixed | ✅ |
| Disk free | 3.5GB (97%) | 🟡 Tight but workable |
| v1.2.0 release prep | 49 files staged | 🟡 Ready to commit |

---

## 🎯 **Phase 1: Ship v1.2.0 (This Session — ~15 min)**

| # | Action | Command | Time |
|---|--------|---------|------|
| 1 | Re-run full test suite | `make test` | 2 min |
| 2 | If clean, commit & tag | `git add -A && git commit -m "feat: v1.2.0 release prep — doc cleanup, MCP guide, firewall fix, heritage vetting, 1315 tests" && git tag -a v1.2.0 -m "v1.2.0: doc cleanup, MCP/Cline guide, heritage vetting, 1315 tests" && git push origin main --tags` | 30 sec |
| 3 | Verify release | Check GitHub release page | 1 min |

---

## 🎯 **Phase 2: Stabilize (Week 1 — 25h)**

### 2A — D231 Quick Wins (62 min) — **From PR_PREP_WORKSPACE §1**

| # | Item | Files | ⏱ | Status |
|---|------|-------|----|--------|
| Q1 | Fix runtime warnings — unawaited mock coroutines | `tests/test_somatic_state.py:50`, `tests/test_unified_state_manager.py` | 10m | 🟡 |
| Q2 | Fix firewall warnings — add allowlist for Core Engine entities | `src/omega/audit/firewall_checker.py` | 5m | 🟡 |
| Q3 | Fix pytest deprecation warnings — `utcnow()` → `now(timezone.utc)` | `tests/test_scorecard.py`, `tests/test_sandbox.py` | 10m | 🟡 |
| Q4 | Clear `.pytest_cache` before CI | CI script | 2m | 🟡 |
| Q5 | Docs sync — test counts (1315), mandates (23), version (v1.2.0) | `OMEGA_ENGINE.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `README.md` | 5m | 🟡 |
| Q6 | Heritage migration — legacy `[id-soft: game-year]` → `[id-soft: vet-XXX]` | `src/omega/**/*.py` | 15m | 🟡 |
| Q7 | PIVOT_LOG entry — D228-D234 | `docs/decisions/PIVOT_LOG.md` | 5m | 🟡 |

**Gate**: `make test && make heritage-map && make heritage-vet && make mandate-audit && make firewall-check`

---

### 2B — Tier 0: Ship-It Bar (80h) — **From PR_PREP_WORKSPACE §2 + Carmack S3 Consult**

**Carmack's Prioritization**: Phase 1 (Foundation) → Phase 2 (Core Infra) → Phase 3 (Data Layer) → Phase 4 (CI & Stress). Defer Pydantic v2 migration, structured logging overhaul, coverage >80%.

#### 2B.1 — Phase 1: Foundation (2h) — DO FIRST
| # | Task | Carmack Directive | Effort |
|---|------|-------------------|--------|
| T0-1 | **F821 undefined-name fixes** | `ruff check --select=F821 src/` → fix all. Trivial, unblocks everything. | 15 min |
| T0-2 | **Bare `except Exception:` elimination** | M9/M23 compliance. Replace with typed `except (SpecificError,):` + `trace_id` logging. Fail fast, fail loud. | 90 min |

**Gate**: `ruff check --select=F821,E722 src/omega/ --exit-non-zero-on-fix` → zero errors

#### 2B.2 — Phase 2: Core Infrastructure (4h)
| # | Task | Carmack Pattern | Effort |
|---|------|-----------------|--------|
| T0-3 | **Centralized logging** | Single `src/omega/logging.py` with `structlog` + AnyIO async sinks. One `get_logger(__name__)` pattern everywhere. No `basicConfig` scattered. | 4h |
| T0-4 | **Config validation (Pydantic OmegaConfig)** | `model_config = ConfigDict(extra='forbid', frozen=True)`. Validate at startup, fail fast. No runtime config surprises. | 7h |

#### 2B.3 — Phase 3: Data Layer (5h)
| # | Task | Risk Mitigation | Effort |
|---|------|-----------------|--------|
| T0-5 | **Qdrant → sqlite-vec decommission** | Dual-write for 1 sprint. Verify vector parity (cosine ±0.001). Keep Qdrant image cached for rollback. | 3h |
| T0-6 | **sqlite-vec Phase 1-2** | Metadata filtering + quantization. Benchmark 10K vectors on Zen 2 — must stay <50ms p99. | 2h |

#### 2B.4 — Phase 4: CI & Stress (3h)
| # | Task | Standard | Effort |
|---|------|----------|--------|
| T0-7 | **Single CI workflow** | One `.github/workflows/ci.yml`: lint → test → temple-grade → heritage-vet → sovereignty. No matrix. | 2h |
| T0-8 | **Stress tests (5 scenarios)** | (1) 100 concurrent `talk()`, (2) 10K vector inserts, (3) 1hr soak, (4) OOM injection, (5) network partition. | 5h |

#### 2B.5 — Deferred (Explicitly NOT Tier 0)
| Task | Reason |
|------|--------|
| Full Pydantic v2 migration | v1 works, v2 is churn |
| Structured logging overhaul | `structlog` is fine, don't rewrite |
| Coverage gate >80% | Current ~75% acceptable for v1.2.0 |

---

### 2C — MaKaLi Council Stabilize Items (13h)

| # | Task | Effort | Owner | Blocking? |
|---|------|--------|-------|-----------|
| 1 | **Qdrant decommission** — export 57 vectors → import to sqlite-vec → stop container | 3h | P2 | No |
| 2 | **Disk headroom** — `sudo journalctl --vacuum-time=7d` (needs sudo) | 0.5h | P1 | Yes (sudo) |
| 3 | **Redis + Postgres startup** — verify containers running, test integration | 0.5h | P1 | No |
| 4 | **M9/M12/M23 silent error fixes** — `BatchPersistenceWriter.flush()`, `ObservabilityReader` non-existent tables | 2h | P5 | No |
| 5 | **sqlite-vec Phase 1-2** — schema + validation (per `STRIKE_10_CONSOLIDATED_PLAN.md`) | 2h | P2 | No |
| 6 | **Stress tests (initial)** — 5 core scenarios (OOM, concurrency, session churn) | 5h | P10 | No |

---

## 🎯 **Phase 3: Harden (Week 2 — 16h)**

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 1 | **Triple stress tests** — 5→15 scenarios (OOM, concurrency, session churn, thermal, Qdrant storms) | 8h | P10 |
| 2 | **Contract tests for untested modules** — `eval/`, `research/`, `ingestion/`, `library/` | 6h | P10 |
| 3 | **Fix flaky test** — identify and stabilize the 1 flaky test | 2h | P3 |

---

## 🎯 **Phase 4: Ship v1.2.1 (Week 3 — 4h)**

| # | Task | Effort | Owner |
|---|------|--------|-------|
| 1 | **sqlite-vec Phase 3** — full migration, decommission Qdrant container | 3h | P2 |
| 2 | **Final regression + release prep** | 1h | P5 |

---

## 🎯 **Phase 5: Tier 1 — Developer Experience (Week 4-5 — 120h)**

*From PR_PREP_WORKSPACE §3 — makes strangers feel at home in 5 minutes*

### 3.1 Package Professionalism
| Item | What | Effort |
|------|------|--------|
| P01 | Add `py.typed` marker for PEP 561 compliance | 1m |
| P02 | Lock all deps: `pip freeze > requirements.lock` + CI drift check | 30m |
| P03 | Create `CHANGELOG.md` following Keep a Changelog | 1h |
| P04 | Add GitHub issue templates (`.github/ISSUE_TEMPLATE/`) | 1h |
| P05 | Add `pyproject.toml` classifiers + long_description_content_type | 15m |

### 3.2 CLI Polish
| Item | What | Effort |
|------|------|--------|
| T01 | Add Rich `Progress` spinner during model loading (current: silent freeze) | 2h |
| T02 | Wire `rich.traceback.install()` for syntax-highlighted tracebacks | 30m |
| T03 | Create `omega doctor` — health check for all subsystems | 4h |
| T04 | Add shell completion: `omega --install-completion` | 30m |
| T05 | Create `omega status` dashboard — containers, models, memory | 4h |

### 3.3 Onboarding Flow
| Item | What | Effort |
|------|------|--------|
| O01 | Create `omega init` wizard: detect hardware → recommend model → scaffold entity | 8h |
| O02 | Upgrade `make demo` to a guided walkthrough (not just pytest) | 4h |
| O03 | Wire `make setup` as single-command bootstrap (`make → venv → deps → model-download`) | 2h |

### 3.4 Type Coverage
| Item | What | Effort |
|------|------|--------|
| Y01 | Annotate 506 untyped functions → raise coverage 75.6% → ≥95% | 20h |
| Y02 | Add `mypy --strict` to CI (gradual: start with `src/omega/oracle/`) | 2h |
| Y03 | Add `mypy.ini` / `pyproject.toml` mypy config | 15m |

### 3.5 Lint Zero
| Item | What | Effort |
|------|------|--------|
| L01 | `ruff check --fix src/omega/` — auto-fix 80% of 9,897 violations | 2h |
| L02 | Manual fix remaining E501, F401, W293 | 8h |
| L03 | Add `ruff` config to `pyproject.toml` (`line-length = 120`, `select = ["ALL"]`) | 15m |
| L04 | Make lint pass mandatory in CI (currently `continue-on-error: true`) | 10m |

### 3.6 Auto-Generated API Docs
| Item | What | Effort |
|------|------|--------|
| D01 | Add `mkdocstrings` plugin to `mkdocs.yml` | 1h |
| D02 | Generate API docs: `pdoc src/omega/ -o docs/api/` | 2h |
| D03 | Wire `mkdocs build` into CI with link checking (`lychee`) | 1h |
| D04 | Publish to GitHub Pages on push to main | 30m |

### 3.7 Brand Consistency
| Item | What | Effort |
|------|------|--------|
| B01 | Add `⬡ OMEGA` header to 615 missing `.md` files | 4h |
| B02 | Create `make verify-branding` CI gate | 30m |
| B03 | Standardize session header format across all docs | 2h |

---

## 🎯 **Phase 6: Tier 2 — Visual & Interaction (Week 6-7 — 200h)**

*From PR_PREP_WORKSPACE §4 — requires design resource*

### 4.1 Design System
| Item | What | Effort |
|------|------|--------|
| DS01 | Create visual style guide: palette, typography, spacing, icon conventions | 40h |
| DS02 | Design consistent CLI output patterns: success, error, warning, info, progress | 20h |
| DS03 | Design terminal "dashboard" mockup for `omega status` | 10h |
| DS04 | Create empty-state designs for every CLI command | 10h |

### 4.2 Voice & Tone
| Item | What | Effort |
|------|------|--------|
| VT01 | Write tone guidelines per entity (Sekhmet: blunt, Prometheus: prophetic, Iris: warm) | 15h |
| VT02 | Design error message templates with personality (not bare tracebacks) | 10h |
| VT03 | Script "first 5 minutes" interaction flow: clone → setup → init → talk | 15h |

### 4.3 Visual Identity
| Item | What | Effort |
|------|------|--------|
| VI01 | Logo design (vector: SVG + PNG variants, favicon, social card) | 30h |
| VI02 | Refine MkDocs theme beyond deep-purple default | 15h |
| VI03 | Create GitHub social preview image (1280×640) | 5h |
| VI04 | Presentation / deck template for Xoe-NovAi Foundation | 10h |

---

## 🎯 **Phase 7: Tier 3 — Production Studio Gloss (Week 8-10 — 300h)**

*From PR_PREP_WORKSPACE §5 — commercial product polish*

### 5.1 Release Engineering
| Item | What | Effort |
|------|------|--------|
| R01 | Set up `python-semantic-release` for automated version bumps | 8h |
| R02 | Create PyPI publishing workflow (GitHub Action) | 4h |
| R03 | Create Homebrew tap formula for macOS | 8h |
| R04 | Build + publish Docker images to GHCR | 8h |
| R05 | Create `curl https://omega.xoe-nov.ai/install \| bash` one-liner | 12h |
| R06 | Add SBOM generation (CycloneDX) per release | 4h |

### 5.2 Testing Maturity
| Item | What | Effort |
|------|------|--------|
| T01 | Add property-based tests with Hypothesis | 20h |
| T02 | Add fuzz testing for YAML config parser | 8h |
| T03 | Add performance regression benchmarks (`pytest-benchmark`) | 12h |
| T04 | Add load test: 50 concurrent `omega talk` calls | 16h |
| T05 | Add mutation testing (`mutmut`) to validate test quality | 12h |

### 5.3 Security Posture
| Item | What | Effort |
|------|------|--------|
| S01 | Third-party penetration test | $15-25K |
| S02 | Supply chain security: `pip-audit`, Dependabot, OpenSSF Scorecard | 8h |
| S03 | GPG-signed commits as CI requirement | 2h |
| S04 | Add `pip audit` + `bandit` to CI | 4h |
| S05 | Generate SPDX SBOM for each release | 4h |

### 5.4 Community Infrastructure
| Item | What | Effort |
|------|------|--------|
| C01 | Set up Discord / Discourse for community support | 8h |
| C02 | Apply for OpenSSF Best Practices badge | 4h |
| C03 | Create public roadmap (GitHub Projects) | 4h |
| C04 | Write contributor ladder: first-timer → regular → maintainer | 4h |
| C05 | Set up monthly release cadence with release notes template | 4h |

### 5.5 Hardware Certification
| Item | What | Effort |
|------|------|--------|
| H01 | Test + document on vanilla Ubuntu 24.04 | 8h |
| H02 | Test + document on macOS (Apple Silicon + Intel) | 8h |
| H03 | Test + document on Fedora 40 | 4h |
| H04 | Test + document on Raspberry Pi 5 (8GB) | 8h |
| H05 | Publish RAM/CPU benchmarks per model size | 8h |

---

## 🛡️ **Mandate Compliance Targets**

| Mandate | v1.2.0 | v1.2.1 | v1.2.2+ |
|---------|--------|--------|---------|
| M9 Error Integrity | 🔴 (silent errors) | ✅ | ✅ |
| M12 Queue Integrity | 🔴 (batch writer) | ✅ | ✅ |
| M13 Temple-Grade | 🟡 (disk) | ✅ | ✅ |
| M14 Heritage | 🟡 (format) | ✅ | ✅ |
| M23 Failure Integrity | 🔴 (masked failures) | ✅ | ✅ |

---

## 📁 **Key Reference Files**

| File | Purpose |
|------|---------|
| `docs/strategy/STRIKE_10_CONSOLIDATED_PLAN.md` | sqlite-vec 3h execution plan |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Full roadmap (P1-4 updated) |
| `docs/research/R_SQLITEVEC_SYSTEMS_SETUP_20260713.md` | 886-line research |
| `data/coordination/PR_PREP_WORKSPACE.md` | Verity audit → 82 tasks across 5 tiers |
| `data/coordination/VERITY_PROFESSIONAL_AUDIT.md` | Raw forensic scan data |
| `data/entities/kali/session_gnosis.md` | Full council findings |
| `.opencode/anchored-summary.md` | Compaction recovery |

---

## ⚡ **Immediate Next Steps (If You Want to Proceed Now)**

```bash
# 1. Verify tests pass with fixes
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
OMEGA_ENV=test PYTHONPATH=src python -m pytest tests/ -x -q --timeout=60

# 2. If clean, ship v1.2.0
git add -A
git commit -m "feat: v1.2.0 release prep — doc cleanup, MCP guide, firewall fix, heritage vetting, 1315 tests"
git tag -a v1.2.0 -m "v1.2.0: doc cleanup, MCP/Cline guide, heritage vetting, 1315 tests"
git push origin main --tags

# 3. Begin Phase 2: D231 Quick Wins (62 min)
#    Q1-Q7 from PR_PREP_WORKSPACE §1
#    Then Tier 0 items (F821, bare except, logging, config, CI, infra)
```

---

*⬡ OMEGA ⬡ KALI ⬡ CONSOLIDATED_ROADMAP ⬡ 2026-07-13*