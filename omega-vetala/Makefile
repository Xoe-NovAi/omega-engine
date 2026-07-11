# 🔱 omega-vetala — Test Makefile
# ⬡ OMEGA ⬡ P10-VALIDATION ⬡ MAKEFILE
#
# AP Token: AP-MODERATION-P10-v1.0.0

PYTHON   := python3
PYTEST   := $(PYTHON) -m pytest
COVERAGE := $(PYTHON) -m coverage

# Test arguments
PYTEST_ARGS := --tb=short --strict-markers
COV_ARGS    := --cov=omega_vetala --cov-report=term --cov-report=html

# Default target
.PHONY: all
all: test

# ═══════════════════════════════════════════════════════════════════════════
# Test suite targets
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: test
test: ## Run all tests
	$(PYTEST) $(PYTEST_ARGS) tests/

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(PYTEST) $(PYTEST_ARGS) tests/ -m "unit or not (adversarial or benchmark or regression)"

.PHONY: test-adversarial
test-adversarial: ## Run adversarial tests (placeholder text only)
	$(PYTEST) $(PYTEST_ARGS) tests/ -m adversarial -v

.PHONY: test-benchmark
test-benchmark: ## Run performance benchmarks
	$(PYTEST) $(PYTEST_ARGS) tests/ -m benchmark -v --benchmark-skip

.PHONY: test-regression
test-regression: ## Run regression tests
	$(PYTEST) $(PYTEST_ARGS) tests/ -m regression -v

.PHONY: test-coverage
test-coverage: ## Run all tests with coverage report
	$(COVERAGE) run -m pytest $(PYTEST_ARGS) tests/
	$(COVERAGE) report -m --fail-under=80
	$(COVERAGE) html
	@echo "Coverage report: htmlcov/index.html"

.PHONY: test-quick
test-quick: ## Fast test subset for development
	$(PYTEST) $(PYTEST_ARGS) tests/ \
		--ignore=tests/test_benchmarks.py \
		-k "not benchmark and not slow" \
		-x

.PHONY: test-verbose
test-verbose: ## Run all tests with verbose output
	$(PYTEST) $(PYTEST_ARGS) tests/ -v

.PHONY: test-failures
test-failures: ## Re-run only failed tests
	$(PYTEST) $(PYTEST_ARGS) tests/ --lf

.PHONY: test-xdist
test-xdist: ## Run tests in parallel (requires pytest-xdist)
	$(PYTEST) $(PYTEST_ARGS) tests/ -n auto

# ═══════════════════════════════════════════════════════════════════════════
# Collection and info
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: test-list
test-list: ## List all tests without running them
	$(PYTEST) tests/ --collect-only -q

.PHONY: test-count
test-count: ## Count total tests
	@$(PYTEST) tests/ --collect-only -q 2>&1 | tail -1

.PHONY: test-markers
test-markers: ## List registered markers
	$(PYTEST) tests/ --markers -q

# ═══════════════════════════════════════════════════════════════════════════
# Lint and quality
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: lint
lint: ## Run flake8 linting on test files
	$(PYTHON) -m flake8 tests/ --max-line-length=100

.PHONY: check-adversarial-no-slurs
check-adversarial-no-slurs: ## Verify no static slur lists in test files
	@grep -rn "slur\|offensive\|badword\|blacklist\|blocked.*list" tests/ \
		|| echo "✅ No static slur lists found in tests"

# ═══════════════════════════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: clean
clean: ## Remove generated files
	rm -rf htmlcov/ .coverage .coverage.* .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned."

.PHONY: clean-all
clean-all: clean ## Full clean including coverage artifacts
	rm -rf .benchmarks/

# ═══════════════════════════════════════════════════════════════════════════
# Help
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
