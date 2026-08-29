# 🔱 Omega Engine — Test Experience Specification
**AP Token**: `AP-TEST-UX-SPEC-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ N3 ⬡ TEST-UX ⬡ ACTIVE

---

## The Problem (What We Just Lived)

| Pain Point | Impact |
|------------|--------|
| **Blind execution** — No visibility into what's running, progress, or ETA | User waits 4+ minutes with zero feedback |
| **Sequential re-runs** — Agent ran tests one-by-one after each failure | Wasted 10+ minutes of compute + user time |
| **No smart selection** — Full suite runs every time | 1800+ tests when only 10 changed |
| **Poor failure UX** — Raw tracebacks, no actionable guidance | User can't distinguish "my bug" from "infra flake" |
| **No watch mode** — Manual re-run after every edit | Breaks flow state |
| **CI/CD disconnect** — Local ≠ CI behavior | "Works on my machine" syndrome |

---

## The Vision: Industry-Standard Test Experience

> **Goal**: A developer runs `make test` and gets **instant feedback**, **clear progress**, **actionable failures**, and **confidence** — every time.

### Core Principles

1. **Fast by Default** — Unit tests < 5s, Integration < 30s, Full suite < 2min
2. **Visible Always** — Real-time progress, not silent execution
3. **Smart Selection** — Run what matters, skip what doesn't
4. **Actionable Failures** — Every error tells you *what*, *where*, *why*, *how to fix*
5. **Local = CI** — Identical behavior, zero surprises
6. **Sovereign** — No external dependencies, fully offline-capable

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    omega-test (CLI Entry Point)                 │
├─────────────────────────────────────────────────────────────────┤
│  Tier 1: Fast Unit Tests      (< 5s, parallel, always run)     │
│  Tier 2: Contract Tests       (< 30s, parallel, smart select)  │
│  Tier 3: Integration Tests    (< 60s, sequential, opt-in)      │
│  Tier 4: Property/Chaos Tests (< 120s, scheduled, opt-in)      │
│  Tier 5: Full Suite           (CI only, all tiers)             │
├─────────────────────────────────────────────────────────────────┤
│  Smart Selector: changed-files → affected-tests mapping        │
│  Progress Reporter: Rich TUI with live progress bars           │
│  Failure Analyzer: Classifies flakes, infra, real bugs         │
│  Cache Layer: pytest-cache + custom content-hash invalidation  │
│  Watch Mode: anyio-based file watcher → incremental re-run     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tier Definitions

### Tier 1: Fast Unit Tests (`make test-unit` / `make test`)
- **Target**: < 5 seconds wall time
- **Parallelism**: Max (CPU cores)
- **Scope**: Pure logic, no I/O, no external deps
- **Markers**: `@pytest.mark.unit`
- **Always runs**: Yes (default `make test`)
- **Examples**: `tests/contracts/`, `tests/property/` (fast ones), `tests/unit/`

### Tier 2: Contract Tests (`make test-contract`)
- **Target**: < 30 seconds
- **Parallelism**: High (8-16 workers)
- **Scope**: API contracts, mandate gates, schema validation
- **Markers**: `@pytest.mark.contract`
- **Smart select**: Runs if public API changed
- **Examples**: `tests/contract/test_mandate_gates.py`, `tests/contract/test_model_gateway_fallback.py`

### Tier 3: Integration Tests (`make test-integration`)
- **Target**: < 60 seconds
- **Parallelism**: Low (2-4 workers, resource-heavy)
- **Scope**: Real providers, databases, MCP servers
- **Markers**: `@pytest.mark.integration`
- **Opt-in**: Explicit flag required
- **Examples**: `tests/test_antigravity_provider.py`, `tests/test_qdrant_index.py`

### Tier 4: Property/Chaos Tests (`make test-property`)
- **Target**: < 120 seconds
- **Parallelism**: Medium
- **Scope**: Hypothesis-based, chaos engineering, stress tests
- **Markers**: `@pytest.mark.property`, `@pytest.mark.chaos`
- **Scheduled**: Nightly/weekly, not on every commit
- **Examples**: `tests/property/test_soul_store_atomic.py`, `tests/property/test_oom_protector_fuse.py`

### Tier 5: Full Suite (`make test-all` / CI only)
- **Target**: < 120 seconds (parallelized)
- **Scope**: Everything
- **CI-only**: Not recommended for local development
- **Artifacts**: JUnit XML, coverage, JSON summary, HTML report

---

## Smart Test Selection

### Changed-Files → Affected-Tests Mapping

```python
# .github/test-selector.yml (generated from code analysis)
mappings:
  "src/omega/oracle/model_gateway.py":
    - "tests/contract/test_model_gateway_fallback.py"
    - "tests/contract/test_provider_classification.py"
    - "tests/test_contract_m21.py::test_talk_returns_oracleresponse"
  
  "src/omega/oracle/health_monitor.py":
    - "tests/contract/test_breaker_fsm.py"
    - "tests/property/test_breaker_fsm.py"
  
  "src/omega/observability/regression_watcher.py":
    - "tests/unit/test_regression_watcher.py"  # new
```

### Selection Algorithm

```bash
# 1. Get changed files since main
CHANGED=$(git diff --name-only main...HEAD -- "src/**/*.py")

# 2. Map to affected tests (cached mapping)
AFFECTED=$(python scripts/test_selector.py --changed "$CHANGED")

# 3. Run only affected + always-run (unit)
pytest $AFFECTED tests/contracts/ -x --tb=short
```

### Fallback Tiers

| Scenario | Command |
|----------|---------|
| **Default** (fast feedback) | `make test` → Tier 1 only |
| **Pre-push** (confidence) | `make test-prepush` → Tier 1 + affected Tier 2 |
| **Full confidence** | `make test-all` → All tiers (CI) |
| **Specific area** | `make test-area ORACLE` → Oracle-related tests |

---

## Progress Reporting (Rich TUI)

### Live Dashboard Layout

```
╭────────────────────────────────────────────────────────────────╮
│  Ω TEST RUNNER  │  Tier 1: Unit Tests  │  3.2s / 5s  │  ████░░  │
├────────────────────────────────────────────────────────────────┤
│  ████████████████████████████████  247/312  79%  12.3 tests/s  │
├────────────────────────────────────────────────────────────────┤
│  ✅ tests/contracts/test_firewall_checker.py     (0.23s)       │
│  ✅ tests/contracts/test_mandate_auditor.py      (0.41s)       │
│  🔄 tests/contract/test_model_gateway_fallback.py (running)    │
│  ⏳ tests/contract/test_provider_classification.py (pending)   │
├────────────────────────────────────────────────────────────────┤
│  Failures: 0  │  Skipped: 12  │  XFailed: 3  │  ETA: 1.8s     │
╰────────────────────────────────────────────────────────────────╯
```

### Key Features

- **Real-time updates** — Every test completion updates the dashboard
- **Progress bars** — Per-file and overall
- **Throughput metric** — Tests/second for pacing awareness
- **Failure preview** — Failed tests show inline with error summary
- **Keyboard shortcuts** — `f` = focus failures, `s` = skip slow, `q` = quit gracefully

---

## Failure Analysis & UX

### Failure Classification

Every failure gets auto-classified:

| Class | Icon | Meaning | Action |
|-------|------|---------|--------|
| **REAL_BUG** | 🔴 | Your code broke a contract | Fix the code |
| **INFRA_FLAKE** | 🟡 | Network, timing, resource contention | Re-run, investigate if persistent |
| **TEST_BUG** | 🟠 | Test itself is broken | Fix the test |
| **ENV_MISMATCH** | 🔵 | Local env differs from CI | Check `.env`, versions, services |
| **KNOWN_FLAKE** | ⚪ | Documented flaky test (in registry) | Ignore, tracked separately |

### Failure Output Format

```
╭─ FAILURE: tests/test_contract_m21.py::test_generateresult_has_required_fields ─╮
│ CLASS: REAL_BUG (confidence: 0.94)                                            │
│                                                                                 │
│ ASSERTION: Expected provider_name='mock', got 'fallback'                      │
│                                                                                 │
│ ROOT CAUSE: MockProvider.generate() signature mismatch — missing top_p param  │
│                                                                                 │
│ FILE: src/omega/oracle/backends/mock.py:42                                    │
│                                                                                 │
│ FIX: Add `top_p: Optional[float] = None` to MockProvider.generate()          │
│                                                                                 │
│ REPRO: pytest tests/test_contract_m21.py::test_generateresult_has_required_fields -v
╰────────────────────────────────────────────────────────────────────────────────╯
```

### Flaky Test Registry

```yaml
# config/flaky-tests.yml
flaky_tests:
  - test: "tests/test_contract_m21.py::test_resourceguard_lock_is_context_manager"
    reason: "Thread pool contention in ResourceGuard under load"
    frequency: "~5% on CI, ~1% local"
    mitigation: "Increase timeout, reduce parallelism for this test"
    owner: "N3 Engineering"
    since: "2026-07-15"
    tracker: "GH-1247"
```

---

## Watch Mode (`make test-watch`)

### Behavior

```bash
$ make test-watch
🔍 Watching src/omega/**/*.py, tests/**/*.py
📦 Initial run: Tier 1 (unit tests)...
✅ 312 passed in 3.2s

👀 Waiting for changes...
📝 Changed: src/omega/oracle/model_gateway.py
🎯 Affected tests: 7 (model_gateway_fallback, provider_classification, m21)
🔄 Re-running affected...
✅ 7 passed in 1.1s

👀 Waiting for changes...
```

### Implementation

- **anyio-based file watcher** (cross-platform, no external deps)
- **Content hashing** — Only re-run if actual logic changed (not whitespace)
- **Incremental** — Reuses pytest cache, only re-executes affected nodes
- **Debounced** — 500ms debounce to batch rapid saves

---

## Cache Strategy

### Layers

| Layer | Tool | Invalidation | Scope |
|-------|------|--------------|-------|
| **pytest cache** | `pytest-cache` | File mtime + content hash | Test results, collected items |
| **Content hash** | Custom (`.omega/test-cache/`) | AST semantic hash | Smart selection mapping |
| **Dependency graph** | Custom | Import analysis | Changed-files → affected-tests |
| **CI artifact cache** | GitHub Actions cache | `requirements.txt` + `pyproject.toml` | Virtual env, installed packages |

### Cache Commands

```bash
make test-cache-stats    # Show cache hit/miss rates
make test-cache-clear    # Full cache invalidation
make test-cache-warm     # Pre-populate cache (CI)
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
jobs:
  test-unit:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-omega  # Custom action
      - run: make test-unit
      - uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: test-results/unit/*.xml

  test-contract:
    needs: test-unit
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        shard: [1, 2, 3, 4]  # Parallel shards
    steps:
      - run: make test-contract --shard=${{ matrix.shard }}/4

  test-integration:
    needs: test-contract
    runs-on: [self-hosted, omega-integration]  # Has GPU, providers
    timeout-minutes: 30
    steps:
      - run: make test-integration

  test-report:
    needs: [test-unit, test-contract, test-integration]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      - run: python scripts/merge_test_reports.py
      - uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: test-report.html
      - run: python scripts/post_pr_comment.py  # PR summary
```

### PR Comment Summary

```
## 🧪 Test Results Summary

| Tier | Tests | Passed | Failed | Skipped | Time |
|------|-------|--------|--------|---------|------|
| Unit | 312 | 312 | 0 | 0 | 3.2s |
| Contract | 187 | 185 | 2 | 0 | 24.1s |
| Integration | 43 | 41 | 2 | 0 | 58.3s |
| **Total** | **542** | **538** | **4** | **0** | **85.6s** |

### ❌ Failures (4)

| Test | Class | Likely Cause |
|------|-------|--------------|
| `test_qdrant_index.py::test_hybrid_search_rrf_merging` | INFRA_FLAKE | Qdrant not ready |
| `test_sovereign_ingestion.py::test_sovereign_ingestion_flow` | ENV_MISMATCH | Missing API keys |
| `test_vault_core.py::test_store_and_retrieve_credential` | REAL_BUG | VaultCore init order |
| `test_provider_fallback.py::test_provider_fallback_chain_order` | TEST_BUG | Missing cascade_router |

[View Full Report](https://github.com/.../actions/runs/.../test-report.html)
```

---

## Makefile Targets (User-Facing)

```makefile
# Fast feedback (default)
test: test-unit

# Pre-push confidence
test-prepush: test-unit test-contract-affected

# Full local (opt-in, slow)
test-all: test-unit test-contract test-integration test-property

# Specific areas
test-area-oracle: test-unit tests/contract/test_model_gateway* tests/contract/test_provider*
test-area-memory: test-unit tests/property/test_soul_store* tests/property/test_oom*
test-area-mcp: test-unit tests/mcp_matrix/

# Watch mode
test-watch:  # Continuous testing on file changes

# Cache management
test-cache-stats:
test-cache-clear:
test-cache-warm:

# Debugging
test-debug:  # Single test with full output, no capture
test-profile:  # With profiling (snakeviz compatible)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] `scripts/omega_test.py` — Main entry point with Rich TUI
- [ ] Tier markers in pytest.ini (`unit`, `contract`, `integration`, `property`, `chaos`)
- [ ] Parallel execution with `pytest-xdist` (configured for local CPU)
- [ ] Basic progress reporting (spinner + counters)

### Phase 2: Smart Selection (Week 2)
- [ ] `scripts/test_selector.py` — Changed-files → affected-tests
- [ ] Mapping generation from import analysis
- [ ] `make test-prepush` target
- [ ] Cache layer for selection results

### Phase 3: Failure UX (Week 3)
- [ ] Failure classifier (heuristics + flaky registry)
- [ ] Rich failure output with root cause hints
- [ ] Flaky test registry (`config/flaky-tests.yml`)
- [ ] Auto-link to GitHub issues for known flakes

### Phase 4: Watch Mode (Week 4)
- [ ] `make test-watch` with anyio file watcher
- [ ] Content-hash based change detection
- [ ] Incremental re-run with pytest cache reuse
- [ ] Keyboard shortcuts (focus, skip, quit)

### Phase 5: CI/CD Polish (Week 5)
- [ ] GitHub Actions workflow with sharding
- [ ] PR comment bot with summary
- [ ] HTML test report artifact
- [ ] Badge generation (passing, coverage, flake rate)

### Phase 6: Documentation (Week 6)
- [ ] `docs/reference/testing.md` — User guide
- [ ] `docs/reference/test-authoring.md` — How to write good tests
- [ ] `docs/strategy/TEST_ARCHITECTURE.md` — Architecture decisions
- [ ] Video demo for README

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time to first feedback** | < 3s | `make test` → first progress update |
| **Time to full unit suite** | < 5s | `make test` completion |
| **Pre-push confidence time** | < 30s | `make test-prepush` |
| **Failure diagnosis time** | < 30s | Time from failure to "root cause" hint |
| **Flake rate** | < 1% | Tracked in flaky registry |
| **Cache hit rate** | > 90% | `make test-cache-stats` |
| **Watch mode latency** | < 1s | File save → test start |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Alternative |
|--------------|--------------|-------------|
| `pytest tests/` with no selection | Runs 1800 tests every time | Tiered + smart selection |
| `--tb=long` by default | Noise drowns signal | `--tb=short` default, `--tb=long` on demand |
| No parallel execution | Wastes multi-core CPU | `pytest-xdist` with CPU-aware workers |
| Silent execution | User thinks it hung | Rich TUI with live progress |
| Raw tracebacks | No actionable info | Classified failures with fix hints |
| CI-only test config | Local ≠ CI | Identical config, local-first |

---

## Appendix: Test Authoring Standards

### Required Markers

```python
# Every test MUST have exactly one tier marker:
@pytest.mark.unit          # Fast, no I/O, always runs
@pytest.mark.contract      # API contracts, mandate gates
@pytest.mark.integration   # Real providers, databases
@pytest.mark.property      # Hypothesis-based
@pytest.mark.chaos         # Stress, fault injection

# Optional modifiers:
@pytest.mark.slow          # > 10s, excluded from fast tiers
@pytest.mark.flaky         # Registered in flaky-tests.yml
@pytest.mark.skip_ci       # Local only (e.g., needs GPU)
```

### Test Structure Template

```python
"""
Test: <What is being tested>
Tier: <unit|contract|integration|property|chaos>
Mandates: <M1, M7, M13, etc.>
"""

import pytest
from omega.xxx import Xxx

class TestXxxContracts:
    """Contract tests for Xxx — verifies public API guarantees."""
    
    @pytest.mark.contract
    def test_xxx_returns_expected_type(self):
        """M21: Xxx() must return XxxResult with required fields."""
        result = Xxx()
        assert isinstance(result, XxxResult)
        assert hasattr(result, "required_field")
    
    @pytest.mark.unit
    def test_xxx_internal_logic(self):
        """Pure logic test — no I/O, no mocks needed."""
        assert Xxx._internal_helper("input") == "expected"
```

---

*This specification is the contract for the Omega Engine test experience. Every tool, script, and workflow must conform to these standards.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: N3 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
