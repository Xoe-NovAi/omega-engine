# 🔱 Test UX — Carmack Mode Implementation Plan
**AP Token**: `AP-TEST-UX-CARMACK-20260816-v1`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_test_ux_carmack ⬡ RATIFIED

**Date**: 2026-08-16
**Status**: CARMACK MODE RATIFIED — Ready for implementation
**Source**: John Carmack (S3 Consultant) architectural review of `TEST_UX_SPEC.md`

---

## 📋 Executive Summary

**Original Spec**: 6-phase, ~6 weeks, 5-tier system, Rich TUI, custom smart selection, anyio watcher, failure classification, custom cache, CI sharding, PR bot — **REJECTED**

**Carmack Alternative**: 50-line Makefile, 2 tiers, `pytest-xdist` + `pytest-testmon` + `entr` — **RATIFIED**

> *"Test infra that wastes user time is a sovereignty violation. This spec wastes user time building it, maintaining it, and running it. The 50-line alternative respects sovereignty."* — John Carmack

---

## 🎯 Carmack Verdict

```
CARMACK MODE: REJECTED (original spec) → RATIFIED (50-line alternative)

CUT LIST (delete all):
- 5-tier test system
- Smart selection via import analysis
- Rich TUI dashboard
- Failure classification taxonomy
- anyio file watcher + content hashing
- Custom cache layers
- Flaky test registry YAML
- CI sharding matrix
- PR comment bot, HTML reports, badges

KEEP LIST:
- Tier markers (@pytest.mark.unit, @pytest.mark.integration) — 2 tiers max
- pytest-xdist parallel execution (-n auto)
- make test / test-prepush / test-all targets
- --tb=short default
- Watch mode concept — use entr, not anyio
```

---

## 📦 Dependencies

### Python (add to `pyproject.toml`)
```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-xdist>=3.5",      # parallel execution (-n auto)
    "pytest-testmon>=1.4",    # automatic changed-test detection
    "pytest-cov>=5.0",        # coverage
]
```

### System Package
```bash
# Ubuntu/Debian
sudo apt install entr

# macOS
brew install entr

# Arch
sudo pacman -S entr
```

**Install**:
```bash
source .venv/bin/activate && pip install pytest-testmon
```

---

## ⚙️ pytest Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
# Tier markers (2 tiers max - Carmack)
markers = [
    "unit: fast tests (<10s total), run by default",
    "integration: slow tests (DB, network, full stack), opt-in",
]

# Default: fast tier only, parallel, stop on first failure, short traceback
addopts = "-n auto -x --tb=short -m \"not integration\""

# testmon config (incremental re-runs)
testmon = true
testmon_store = ".testmondata"

# Coverage
pythonpath = ["src"]
```

---

## 📝 Makefile Targets (Replace Existing Test Targets)

```makefile
# =============================================================================
# TEST TARGETS — Carmack Mode: 50 lines, maximum leverage
# =============================================================================

# Default: fast unit tests only (<10s), parallel, stop on first failure
.PHONY: test
test:
	@pytest -n auto -x --tb=short -m "not integration" tests/

# Full suite: everything, parallel, short tracebacks
.PHONY: test-all
test-all:
	@pytest -n auto --tb=short tests/

# Pre-push: fast + only affected tests (testmon incrementality)
.PHONY: test-prepush
test-prepush:
	@pytest -n auto --tb=short --testmon -m "not integration" tests/

# Watch mode: entr watches src/ + tests/, re-runs 'make test' on change
.PHONY: test-watch
test-watch:
	@command -v entr >/dev/null 2>&1 || { echo "entr not installed. Ubuntu: apt install entr | macOS: brew install entr"; exit 1; }
	@find src tests -name "*.py" | entr -c make test

# Watch full suite (opt-in)
.PHONY: test-watch-all
test-watch-all:
	@command -v entr >/dev/null 2>&1 || { echo "entr not installed"; exit 1; }
	@find src tests -name "*.py" | entr -c make test-all

# Coverage report
.PHONY: test-cov
test-cov:
	@pytest -n auto --tb=short --cov=src/omega --cov-report=term-missing --cov-report=html tests/

# Debug: run single test with full output
.PHONY: test-debug
test-debug:
	@pytest -v --tb=long -k "$(TEST)" tests/

# Clean testmon cache
.PHONY: test-clean
test-clean:
	@rm -rf .testmondata .pytest_cache htmlcov
```

---

## 🏷️ Tier Marker Migration

### Current State
Tests likely unmarked or using custom markers.

### Action Required
Add `@pytest.mark.unit` or `@pytest.mark.integration` to each test file.

```bash
# Audit existing markers
grep -r "@pytest.mark" tests/ | sort | uniq -c

# Bulk add unit marker (safe default)
# Then selectively mark integration tests
```

### Integration Test Criteria (mark `@pytest.mark.integration`)
- Uses real DB (Qdrant, Redis, SQLite file)
- Makes network calls (HTTP, MCP, provider APIs)
- Spawns subprocesses/containers
- Takes >5s individually
- Requires specific env vars/secrets

---

## ✅ Verification Gates (All Must Pass)

```bash
# 1. Unit tier <10s on Ryzen 5700U (16 cores, 14GiB)
make test
# Target: <10s wall time

# 2. Full suite <60s
make test-all
# Target: <60s wall time

# 3. test-prepush only runs changed tests
# Edit one test file → run test-prepush → only that test runs
make test-prepush

# 4. Watch mode works
make test-watch
# Edit a file → auto re-runs test → shows results

# 5. No regressions: all existing tests still pass
make test-all  # 77/77 contract tests + all others
```

---

## 🔄 CI/CD (GitHub Actions) — Minimal

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[test]"
      - run: sudo apt-get update && sudo apt-get install -y entr
      - run: make test-all
```

**No sharding, no matrix, no PR bot, no HTML artifacts** — just `make test-all`.

---

## 📚 Documentation Update

Replace the 6-phase roadmap in `docs/strategy/TEST_UX_SPEC.md` with a **"Carmack Mode" appendix**:

```markdown
## Appendix: Carmack Mode (Ratified Implementation)

The 50-line Makefile above is the ratified test infrastructure. 
All speculative features (5-tier, smart selection, Rich TUI, custom cache, 
failure classification, anyio watcher, CI sharding, PR bot) are **rejected**.

### Commands
| Command | Purpose | Time |
|---------|---------|------|
| `make test` | Fast unit tier (default) | <10s |
| `make test-all` | Full suite | <60s |
| `make test-prepush` | Incremental (changed only) | <5s |
| `make test-watch` | Auto-re-run on file change | ∞ |
| `make test-cov` | Coverage report | ~2min |

### Dependencies
- `pytest-xdist` — parallel execution
- `pytest-testmon` — automatic incrementality
- `entr` — file watcher (system package)

### Philosophy
> "Test infra that wastes user time is a sovereignty violation. 
> This implementation respects sovereignty." — Carmack
```

---

## 🚀 Implementation Order (30 min total)

| Step | Action | Time | Owner |
|------|--------|------|-------|
| 1 | Add `pytest-testmon` to `pyproject.toml` + install | 2 min | roc_racoon |
| 2 | Install `entr` (system package) | 1 min | roc_racoon |
| 3 | Add tier markers to `pyproject.toml` | 2 min | roc_racoon |
| 4 | Replace Makefile test targets with Carmack version | 5 min | roc_racoon |
| 5 | Mark existing integration tests with `@pytest.mark.integration` | 10 min | roc_racoon |
| 6 | Verify gates: `make test`, `make test-all`, `make test-prepush`, `make test-watch` | 10 min | roc_racoon |

---

## ❌ Explicitly NOT Building

| Rejected Feature | Replacement |
|------------------|-------------|
| 5-tier system | 2 tiers (unit/integration) |
| Import analysis smart selection | `pytest-testmon` (runtime dependency tracking) |
| Rich TUI dashboard | `pytest -v --tb=short` + terminal |
| Failure classification taxonomy | Traceback IS the classification |
| anyio watcher + content hashing | `entr` (kernel inotify, 50KB C binary) |
| Custom cache layers | `pytest-cache` + `testmon` |
| Flaky test registry YAML | `@pytest.mark.flaky` or fix the test |
| CI sharding matrix | Single `make test-all` job |
| PR comment bot / HTML reports | Green/red status only |

---

## 🏁 Success Criteria

```bash
# All must pass:
✅ make test          # <10s, parallel, stops on first failure
✅ make test-all      # <60s, full suite
✅ make test-prepush  # Only changed tests run
✅ make test-watch    # Auto-re-runs on file save
✅ make test-cov      # Coverage works
✅ 77/77 contract tests still pass
✅ No new Python dependencies beyond pytest-testmon
✅ entr is system package only
```

---

## 🔗 Cross-References

| Document | Purpose |
|----------|---------|
| `docs/strategy/TEST_UX_SPEC.md` | Original spec (rejected) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT |
| `SOVEREIGN_MANDATES.md` | M1, M7, M13, M18, M23, M27 |
| `pyproject.toml` | pytest config + deps |
| `Makefile` | Test targets |

---

## 📦 Handoff Context

**Entity**: roc_racoon
**Channel**: opencode
**Model**: nemotron-3-ultra-free
**Task**: Implement Carmack Mode test infrastructure
**Next**: Steps 1-4 (pyproject.toml + Makefile), then marker migration + verification

**Key Commands**:
```bash
# Start implementation
cat pyproject.toml | grep -A 30 "\[tool.pytest"
cat Makefile | grep -A 50 "TEST TARGETS"

# Verify
make test
make test-all
make test-prepush
make test-watch
```

---

## 🔬 Carmack Deep Research — Test UX Enhancements (2026)

**Date**: 2026-08-16
**Source**: John Carmack (S3 Consultant) deep web research across 7 domains, 20+ tools evaluated

### Research Summary

| Category | Tools Evaluated | Adopted | Evaluated | Rejected |
|----------|-----------------|---------|-----------|----------|
| pytest ecosystem | 8 | 2 | 2 | 4 |
| File watchers | 6 | 1 | 1 | 4 |
| Reporting/DX | 9 | 5 | 1 | 3 |
| Flaky detection | 5 | 0 | 2 | 3 |
| Test selection | 3 | 1 | 1 | 1 |
| Parallel execution | 2 | 1 | 0 | 1 |
| DX innovations | 6 | 2 | 1 | 3 |

---

### Top 3 Recommendations (Max Leverage, Min Effort)

| # | Tool/Technique | Why | Cost |
|---|----------------|-----|------|
| **1** | `pytest-clarity` + `pytest-json-report` + `pytest-instafail` + `pytest-tldr` | Readable diffs + machine JSON + instant failures + one-line summary | 4 lines in requirements, 4 flags in Makefile |
| **2** | `pytest --collect-only -q \| fzf/skim \| xargs pytest -v` | Interactive test selection via Unix composition, zero plugins | 1 shell alias |
| **3** | OSC 9 desktop notifications | `pytest && printf '\e]9;✅\a' \|\| printf '\e]9;❌\a'` — terminal standard, zero deps | 1 Makefile wrapper |

---

### Key Research Insights

| Finding | Carmack Take |
|---------|--------------|
| **pytest-testmon** | Proven at scale (Instawork: 35K tests, 20min → halved). Keep as primary. |
| **pytest-difftest/impacted** | Alpha/beta (2026). Watch, don't adopt. testmon works *now*. |
| **watchexec vs entr** | watchexec has debounce, but entr + `find` is sufficient. Don't swap unless double-runs on save. |
| **pytest-randomly** | Exposes flakes via randomization — **adopt**. `--reruns` masks flakes — **reject**. |
| **cargo-nextest patterns** | Steal principles: per-test isolation (xdist does this), machine output (json-report), live progress (add later). |
| **OSC 9 notifications** | Terminal standard (iTerm2, WezTerm, Kitty). Zero deps. Better than D-Bus plugins. |
| **pytest-clarity** | 80% of Rich TUI diff readability for 10% weight. Auto-activates. |

---

### Updated Dependencies

#### Python (add to `pyproject.toml`)
```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-xdist>=3.5",      # parallel execution (-n auto)
    "pytest-testmon>=1.4",    # automatic changed-test detection
    "pytest-cov>=5.0",        # coverage
    "pytest-clarity",         # readable assertion diffs
    "pytest-json-report",     # machine-readable JSON output
    "pytest-instafail",       # show failures immediately
    "pytest-tldr",            # ultra-short summary
    "pytest-randomly",        # randomize test order to expose flakes
]
```

#### System Package (unchanged)
```bash
# Ubuntu/Debian
sudo apt install entr

# macOS
brew install entr

# Arch
sudo pacman -S entr
```

---

### Updated Makefile Targets (Carmack Mode v2 — ~70 lines)

```makefile
# =============================================================================
# TEST TARGETS — Carmack Mode v2: ~70 lines, maximum leverage
# =============================================================================

# Default: fast unit tests only (<10s), parallel, stop on first failure
.PHONY: test
test:
	@pytest -n auto -x --tb=short -m "not integration" tests/

# Full suite: everything, parallel, short tracebacks
.PHONY: test-all
test-all:
	@pytest -n auto --tb=short tests/

# Pre-push: fast + only affected tests (testmon incrementality)
.PHONY: test-prepush
test-prepush:
	@pytest -n auto --tb=short --testmon -m "not integration" tests/

# Enhanced output: instafail + tldr + json-report + clarity (auto)
.PHONY: test-clarity
test-clarity:
	@pytest -n auto -x --tb=short --instafail --tldr --json-report --json-report-file=test-report.json -m "not integration" tests/

# JSON report only (for tooling/CI)
.PHONY: test-json
test-json:
	@pytest -n auto --tb=short --json-report --json-report-file=test-report.json --json-report-summary tests/

# Summary only (ultra-short)
.PHONY: test-summary
test-summary:
	@pytest --tldr tests/

# Watch mode: entr watches src/ + tests/, re-runs 'make test' on change
.PHONY: test-watch
test-watch:
	@command -v entr >/dev/null 2>&1 || { echo "entr not installed. Ubuntu: apt install entr | macOS: brew install entr"; exit 1; }
	@find src tests -name "*.py" -o -name "*.toml" -o -name "*.yaml" | entr -c $(MAKE) test

# Watch full suite (opt-in)
.PHONY: test-watch-all
test-watch-all:
	@command -v entr >/dev/null 2>&1 || { echo "entr not installed"; exit 1; }
	@find src tests -name "*.py" -o -name "*.toml" -o -name "*.yaml" | entr -c $(MAKE) test-all

# Interactive test selection via fzf/skim (Unix philosophy, zero plugins)
.PHONY: test-pick
test-pick:
	@command -v fzf >/dev/null 2>&1 || command -v sk >/dev/null 2>&1 || { echo "fzf or skim not installed"; exit 1; }
	@pytest --collect-only -q | fzf --multi | xargs -r pytest -v

.PHONY: test-pick-skim
test-pick-skim:
	@command -v sk >/dev/null 2>&1 || { echo "skim not installed"; exit 1; }
	@pytest --collect-only -q | sk --multi | xargs -r pytest -v

# Desktop notification via OSC 9 (terminal standard: iTerm2, WezTerm, Kitty)
.PHONY: notify-test
notify-test:
	@$(MAKE) test && printf '\e]9;✅ Tests passed\a' || printf '\e]9;❌ Tests failed\a'

# Flake detection: expose via randomization (don't mask with --reruns)
.PHONY: test-random
test-random:
	@pytest --randomly-seed=$$RANDOM -x --tb=short tests/

.PHONY: test-flake-hunt
test-flake-hunt:
	@pytest --randomly-seed=$$RANDOM -x --tb=short tests/

# Coverage report
.PHONY: test-cov
test-cov:
	@pytest -n auto --tb=short --cov=src/omega --cov-report=term-missing --cov-report=html tests/

# Debug: run single test with full output
.PHONY: test-debug
test-debug:
	@pytest -v --tb=long -k "$(TEST)" tests/

# Clean testmon cache
.PHONY: test-clean
test-clean:
	@rm -rf .testmondata .pytest_cache htmlcov test-report.json
```

---

### Updated Verification Gates

```bash
# 1. Unit tier <10s on Ryzen 5700U (16 cores, 14GiB)
make test
# Target: <10s wall time

# 2. Full suite <60s
make test-all
# Target: <60s wall time

# 3. test-prepush only runs changed tests
# Edit one test file → run test-prepush → only that test runs
make test-prepush

# 4. Enhanced output works
make test-clarity
# Shows: instant failures, readable diffs, JSON report, one-line summary

# 5. Watch mode works
make test-watch
# Edit a file → auto re-runs test → shows results

# 6. Interactive selection works
make test-pick
# Fuzzy find tests → run selected

# 7. Flake detection works
make test-random
# Randomized order exposes state leakage

# 8. Desktop notification works
make notify-test
# OSC 9 notification in terminal

# 9. No regressions: all existing tests still pass
make test-all  # 77/77 contract tests + all others
```

---

### Updated Success Criteria

```bash
# All must pass:
✅ make test          # <10s, parallel, stops on first failure
✅ make test-all      # <60s, full suite
✅ make test-prepush  # Only changed tests run
✅ make test-clarity  # Enhanced output (instafail, tldr, json, clarity)
✅ make test-watch    # Auto-re-runs on file save
✅ make test-pick     # Interactive selection via fzf/skim
✅ make test-random   # Randomized order exposes flakes
✅ make notify-test   # OSC 9 desktop notification
✅ make test-cov      # Coverage works
✅ 77/77 contract tests still pass
✅ No new Python dependencies beyond the 5 plugins
✅ entr is system package only
```

---

### Implementation Order (Updated — 45 min total)

| Step | Action | Time | Owner |
|------|--------|------|-------|
| 1 | Add 5 plugins to `pyproject.toml` + install | 3 min | roc_racoon |
| 2 | Install `entr` (system package) | 1 min | roc_racoon |
| 3 | Add tier markers to `pyproject.toml` | 2 min | roc_racoon |
| 4 | Replace Makefile test targets with Carmack v2 version | 5 min | roc_racoon |
| 5 | Mark existing integration tests with `@pytest.mark.integration` | 15 min | roc_racoon |
| 6 | Verify all gates (9 checks) | 15 min | roc_racoon |
| 7 | Run `make temple-grade` to verify T1-T11 | 5 min | roc_racoon |

---

### Explicitly NOT Building (Unchanged)

| Rejected Feature | Replacement |
|------------------|-------------|
| 5-tier system | 2 tiers (unit/integration) |
| Import analysis smart selection | `pytest-testmon` (runtime dependency tracking) |
| Rich TUI dashboard | `pytest-clarity` + `pytest-tldr` + terminal |
| Failure classification taxonomy | Traceback IS the classification |
| anyio watcher + content hashing | `entr` (kernel inotify, 50KB C binary) |
| Custom cache layers | `pytest-cache` + `testmon` |
| Flaky test registry YAML | `@pytest.mark.flaky` or fix the test |
| CI sharding matrix | Single `make test-all` job |
| PR comment bot / HTML reports | Green/red status only |

---

---

*Carmack Mode v2 ratified. ~70 lines. Maximum leverage. Minimum ego. Research-backed.*