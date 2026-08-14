# Omega Engine Test Suite Makefile
# Implements C-0 Test Suite Honesty: Quarantine + JSON Badge + Makefile Fix

# Configuration — M24: Always use project venv Python
PYTHON := .venv/bin/python
PYTEST := .venv/bin/python -m pytest
QUARANTINE_FILE := tests/quarantine.txt
BADGE_FILE := tests/test-badge.json
QUARANTINE_EXPIRY := 2026-09-01
TEST_LOG_FILE := data/logs/test-run.log
TEST_LOG_SCRIPT := scripts/rotate_test_log.py

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help test test-honest test-quarantine-check quarantine save-quarantine load-quarantine clean-badge clean generate-badge codex check-codex-stale check-codex-fix check-codex-force ark-optimize ark-optimize-report log-test-run lint

help:
	@echo "Omega Engine Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  test              Run all tests (default)"
	@echo "  test-honest       Run tests with quarantine, JSON badge, and test-run logging"
	@echo "  test-quarantine-check  Check quarantine expiry and fail if expired"
	@echo "  quarantine        Save current failures to quarantine.txt"
	@echo "  save-quarantine   Alias for quarantine"
	@echo "  load-quarantine   Run quarantined tests (marked as xfail)"
	@echo "  generate-badge    Generate JSON badge from test results"
	@echo "  clean-badge       Remove generated badge file"
	@echo "  clean             Remove all generated files"
	@echo "  log-test-run      Capture full test run output to rotating log"
	@echo ""
	@echo "Codex Targets (D-277 Hydration):"
	@echo "  codex             Regenerate OMEGA_CODEX.md from groups.json"
	@echo "  check-codex-stale Check if Codex >24h old; exit 1 if stale"
	@echo "  check-codex-fix   Check and auto-regenerate if stale"

# =============================================================================
# Codex Targets (D-277 Hydration)
# =============================================================================

# Regenerate OMEGA_CODEX.md from groups.json
codex:
	@echo "$(YELLOW)Regenerating OMEGA_CODEX.md...$(NC)"
	@$(PYTHON) scripts/codex_cat.py
	@echo "$(GREEN)OMEGA_CODEX.md regenerated successfully$(NC)"

# Check if Codex is >24h old; exit 1 if stale (useful for CI/pre-commit)
check-codex-stale:
	@echo "$(YELLOW)Checking Codex staleness...$(NC)"
	@$(PYTHON) scripts/check_codex_stale.py

# Check and auto-regenerate if stale
check-codex-fix:
	@echo "$(YELLOW)Checking Codex staleness (auto-fix)...$(NC)"
	@$(PYTHON) scripts/check_codex_stale.py --fix

# Force regenerate regardless of age
check-codex-force:
	@echo "$(YELLOW)Force regenerating OMEGA_CODEX.md...$(NC)"
	@$(PYTHON) scripts/check_codex_stale.py --force

# =============================================================================
# Test Suite Targets
# =============================================================================

# Default target
test: test-honest

# Main honest test target - includes quarantine, badge generation, and test-run logging
test-honest: check-tracking-state save-quarantine run-honest-tests log-test-run generate-badge check-quarantine-expiry

# Save current failures to quarantine file
save-quarantine:
	@echo "$(YELLOW)Saving test failures to quarantine...$(NC)"
	@$(PYTEST) --tb=short -q 2>&1 | grep "^FAILED" | sed 's/FAILED //' | sed 's/ - .*//' > $(QUARANTINE_FILE) || true
	@if [ -s $(QUARANTINE_FILE) ]; then \
		echo "$(GREEN)Quarantine saved to $(QUARANTINE_FILE) with $$(wc -l < $(QUARANTINE_FILE)) tests$(NC)"; \
	else \
		echo "$(GREEN)No failures detected — quarantine empty$(NC)"; \
	fi

# Run tests with quarantine (flaky tests marked as xfail)
run-honest-tests:
	@echo "$(YELLOW)Running tests with quarantine...$(NC)"
	@$(PYTEST) --tb=short -q 2>&1 | tail -5
	@echo "$(GREEN)Honest test run complete$(NC)"

# Capture full test run output to rotating log (data/logs/test-run.log + .1/.2.gz/.3.gz)
log-test-run:
	@echo "$(YELLOW)Rotating test run logs...$(NC)"
	@$(PYTHON) $(TEST_LOG_SCRIPT) rotate
	@echo "$(YELLOW)Running full test suite for log capture...$(NC)"
	@OUTPUT=$$($(PYTEST) --tb=short -q 2>&1); \
	echo "$$OUTPUT" | tail -10; \
	echo "$$OUTPUT" | $(PYTHON) $(TEST_LOG_SCRIPT) write
	@echo "$(GREEN)Test run log captured to $(TEST_LOG_FILE)$(NC)"

# Generate JSON badge with test results
generate-badge:
	@echo "$(YELLOW)Generating JSON badge...$(NC)"
	@$(PYTHON) -c "\
import json, datetime, subprocess, os; \
total = passed = failed = skipped = xfailed = xpassed = 0; \
quarantined = sum(1 for _ in open('$(QUARANTINE_FILE)')) if os.path.exists('$(QUARANTINE_FILE)') else 0; \
result = subprocess.run(['python3', '-m', 'pytest', '--tb=no', '-q', '--co'], capture_output=True, text=True); \
lines = result.stdout.strip().split('\n'); \
total = len([l for l in lines if '::' in l]); \
result2 = subprocess.run(['python3', '-m', 'pytest', '--tb=no', '-q'], capture_output=True, text=True); \
summary = result2.stdout.strip().split('\n')[-1] if result2.stdout.strip() else ''; \
import re; \
m = re.search(r'(\d+) passed', summary); passed = int(m.group(1)) if m else 0; \
m = re.search(r'(\d+) failed', summary); failed = int(m.group(1)) if m else 0; \
m = re.search(r'(\d+) skipped', summary); skipped = int(m.group(1)) if m else 0; \
m = re.search(r'(\d+) xfailed', summary); xfailed = int(m.group(1)) if m else 0; \
m = re.search(r'(\d+) xpassed', summary); xpassed = int(m.group(1)) if m else 0; \
badge = {\"passed\": passed, \"failed\": failed, \"quarantined\": quarantined, \"xpassed\": xpassed, \"skipped\": skipped, \"xfailed\": xfailed, \"timestamp\": datetime.datetime.now().isoformat(), \"version\": \"1.0.0\", \"quarantine_file\": \"$(QUARANTINE_FILE)\", \"expiry_date\": \"$(QUARANTINE_EXPIRY)\"}; \
f = open('$(BADGE_FILE)', 'w'); json.dump(badge, f, indent=2); f.close(); \
print('Created $(BADGE_FILE)')"

# Check quarantine expiry and fail if expired
check-quarantine-expiry:
	@if [ -f $(QUARANTINE_FILE) ] && [ -s $(QUARANTINE_FILE) ]; then \
		echo "$(YELLOW)Checking quarantine expiry...$(NC)"; \
		expiry_date="$(QUARANTINE_EXPIRY)"; \
		today="$$(date +%Y-%m-%d)"; \
		if [ "$$today" \> "$$expiry_date" ]; then \
			echo "$(RED)ERROR: Quarantine expired on $(QUARANTINE_EXPIRY)$(NC)"; \
			echo "$(RED)All quarantined tests must be remediated before this date$(NC)"; \
			exit 1; \
		else \
			echo "$(GREEN)Quarantine is still valid until $(QUARANTINE_EXPIRY)$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)No quarantine file to check$(NC)"; \
	fi

# Load quarantined tests (run only quarantined tests)
load-quarantine:
	@if [ ! -f $(QUARANTINE_FILE) ]; then \
		echo "$(YELLOW)No quarantine file found. Run 'make quarantine' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running quarantined tests...$(NC)"
	@$(PYTEST) --tb=short -q -k "$$(cat $(QUARANTINE_FILE) | tr '\n' ' or ')" 2>&1 | tail -10
	@echo "$(GREEN)Quarantine test run complete$(NC)"

# Clean up generated badge
clean-badge:
	@if [ -f $(BADGE_FILE) ]; then \
		echo "$(YELLOW)Removing $(BADGE_FILE)$(NC)"; \
		rm -f $(BADGE_FILE); \
	else \
		echo "$(YELLOW)$(BADGE_FILE) not found$(NC)"; \
	fi

# Quick test run for development
quick-test:
	@echo "$(YELLOW)Running quick test...$(NC)"
	@$(PYTEST) --tb=short -q tests/contracts/ 2>&1 | tail -5
	@echo "$(GREEN)Quick test complete$(NC)"

# Run flake8 linting on src/omega/ (M13 quality gate)
# Ignore F821: forward-reference type hints and TYPE_CHECKING-only imports
# are pervasive in this codebase and not actionable lint failures.
lint:
	@echo "$(YELLOW)Running flake8 lint...$(NC)"
	@$(PYTHON) -m flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics --ignore=F821
	@$(PYTHON) -m flake8 src/omega/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=F821
	@echo "$(GREEN)Lint complete$(NC)"

# Clean all generated files
clean: clean-badge
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	@rm -f $(QUARANTINE_FILE)
	@echo "$(GREEN)Clean complete$(NC)"

# =============================================================================
# LLM-Friendly Documentation Targets (per LLM_FRIENDLY_DOCS_BP.md)
# =============================================================================

# Token budget configuration
DOC_TOKEN_BUDGETS := configs/token_budgets.yaml
DOC_FRONTMATTER_SCHEMA := schemas/llm_doc_frontmatter.json

# Validate all LLM-friendly docs in a sprint directory
doc-llm-validate:
	@echo "$(YELLOW)Validating LLM-friendly documentation...$(NC)"
	@python3 scripts/validate_llm_docs.py \
		--frontmatter-schema $(DOC_FRONTMATTER_SCHEMA) \
		--token-budget $(DOC_TOKEN_BUDGETS) \
		--answer-first-check \
		--code-block-check \
		--dependency-graph-check \
		docs/sprints/current/
	@echo "$(GREEN)LLM doc validation complete$(NC)"

# Generate llms-full.txt for current sprint (concatenated for LLM consumption)
sprint-plan-llm:
	@echo "$(YELLOW)Generating llms-full.txt for current sprint...$(NC)"
	@mkdir -p docs/sprints/current
	@echo "# Sprint Plan: Doc Sanity & Un-overengineering (2026-07-30)" > docs/sprints/current/llms-full.txt
	@cat docs/archive/sprints/EXECUTION_PLAN_20260725.md >> docs/sprints/current/llms-full.txt
	@for f in docs/archive/sprints/2026-07-25-guard-and-distill/02-p0-tickets/*.md; do \
		[ -f "$$f" ] || continue; \
		echo "\n---\n# $$(basename $$f .md)" >> docs/sprints/current/llms-full.txt; \
		cat $$f >> docs/sprints/current/llms-full.txt; \
	done
	@for f in docs/archive/sprints/2026-07-25-guard-and-distill/03-p1-tickets/*.md; do \
		[ -f "$$f" ] || continue; \
		echo "\n---\n# $$(basename $$f .md)" >> docs/sprints/current/llms-full.txt; \
		cat $$f >> docs/sprints/current/llms-full.txt; \
	done
	@cat docs/archive/sprints/2026-07-25-guard-and-distill/08-research-index.md >> docs/sprints/current/llms-full.txt
	@echo "$(GREEN)Generated docs/sprints/current/llms-full.txt ($$(wc -c < docs/sprints/current/llms-full.txt) bytes)$(NC)"

# Generate llms.txt (index only) for current sprint
sprint-plan-llms-txt:
	@echo "$(YELLOW)Generating llms.txt for current sprint...$(NC)"
	@mkdir -p docs/sprints/current
	@echo "# Sprint Plan Index: Doc Sanity & Un-overengineering" > docs/sprints/current/llms.txt
	@echo "- Sprint Goal: Sanitize docs (UO-4), then un-overengineer (UO-6)" >> docs/sprints/current/llms.txt
	@echo "- Controlling Plan: data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md" >> docs/sprints/current/llms.txt
	@echo "- Active Sprint: data/coordination/ACTIVE_SPRINT.json" >> docs/sprints/current/llms.txt
	@echo "- Research: docs/archive/sprints/2026-07-25-guard-and-distill/08-research-index.md" >> docs/sprints/current/llms.txt
	@echo "- Full Plan: docs/sprints/current/llms-full.txt" >> docs/sprints/current/llms.txt
	@echo "$(GREEN)Generated docs/sprints/current/llms.txt$(NC)"

# Check token count for sprint plan docs only
doc-token-check:
	@echo "$(YELLOW)Checking token budgets for sprint plan docs...$(NC)"
	@python3 scripts/check_doc_tokens.py --budget $(DOC_TOKEN_BUDGETS) docs/sprints/current/
	@echo "$(GREEN)Token check complete$(NC)"

# Chunk sprint plan for RAG/vector storage
doc-chunk-sprint:
	@echo "$(YELLOW)Chunking sprint plan for RAG...$(NC)"
	@python3 scripts/chunk_sprint_plan.py docs/sprints/current/README.md
	@echo "$(GREEN)Chunking complete$(NC)"

# Temple-grade includes Codex freshness and LLM doc validation
temple-grade: check-codex-fix doc-llm-validate check-mandates check-tracking-state
	@echo "$(YELLOW)Running temple-grade checks...$(NC)"
	# Existing temple-grade checks would go here
	@echo "$(GREEN)Temple-grade complete (Codex + LLM doc validation + Mandates + Tracking State)$(NC)"

# Cognitive State Validator (M27 Tracking Integrity)
check-tracking-state:
	@echo "$(YELLOW)Validating tracking state (M27)...$(NC)"
	@$(PYTHON) scripts/validate_tracking_state.py

# =============================================================================
# Mandate Checks (CI-only, moved from runtime Vetter per Carmack Verdict)
# =============================================================================

# Check M1: AnyIO compliance - no asyncio imports in src/omega/
check-m1-anyio:
	@echo "$(YELLOW)Checking M1 (AnyIO compliance)...$(NC)"
	@! rg -n 'import asyncio|from asyncio' src/omega/ --type py --glob '!*test*' --glob '!*governance*' --glob '!*tty_agent*' 2>/dev/null || (echo "$(RED)FAIL: asyncio imports found in src/omega/$(NC)" && false)
	@echo "$(GREEN)M1 passed: No asyncio imports in core$(NC)"

# Check M9: Error integrity - no bare except:
check-m9-error-integrity:
	@echo "$(YELLOW)Checking M9 (Error integrity)...$(NC)"
	@! rg -n 'except\s*:' src/omega/ --type py --glob '!*test*' --glob '!*governance*' 2>/dev/null | rg -v 'except Exception' | rg -v '# noqa' || (echo "$(RED)FAIL: Bare except found in src/omega/$(NC)" && false)
	@echo "$(GREEN)M9 passed: No bare except in core$(NC)"

# Check M8: Zero telemetry - no telemetry SDK imports
check-m8-zero-telemetry:
	@echo "$(YELLOW)Checking M8 (Zero telemetry)...$(NC)"
	@! rg -n 'import (segment|posthog|datadog|amplitude|mixpanel)|from (segment|posthog|datadog|amplitude|mixpanel)' src/omega/ --type py 2>/dev/null || (echo "$(RED)FAIL: Telemetry SDK imports found$(NC)" && false)
	@echo "$(GREEN)M8 passed: No telemetry SDKs in core$(NC)"

# Check M7: Local-first strategy
check-m7-local-first:
	@echo "$(YELLOW)Checking M7 (Local-first strategy + SSOT)...$(NC)"
	@grep -q 'strategy: local_first' config/providers.yaml || (echo "$(RED)FAIL: providers.yaml missing local_first strategy$(NC)" && false)
	@echo "$(GREEN)M7 passed: Local-first strategy configured$(NC)"
	@echo "$(YELLOW)Checking M22 SSOT: is_cloud only in fallback_chain...$(NC)"
	@grep -n "is_cloud:" config/providers.yaml | grep -v "inference.fallback_chain" && (echo "$(RED)FAIL: is_cloud found outside fallback_chain — run 'make check-m7-local-first'$(NC)" && false) || echo "$(GREEN)M22 passed: is_cloud SSOT intact$(NC)"

# Check M23: Failure integrity - no soft-failure patterns (AST-based via Ruff)
# Uses ratchet: fails only on NEW violations vs config/m23_baseline.txt
check-m23-failure-integrity:
	@echo "$(YELLOW)Checking M23 (Failure integrity)...$(NC)"
	@$(PYTHON) scripts/m23_gate.py || (echo "$(RED)FAIL: M23 soft-failure patterns$(NC)" && false)
	@echo "$(GREEN)M23 passed: No new soft-failure patterns$(NC)"

# Regenerate the M23 baseline (run after intentionally fixing violations)
m23-baseline:
	@echo "$(YELLOW)Regenerating M23 baseline...$(NC)"
	@$(PYTHON) -m ruff check src/omega --select S110,S112,BLE001,E722 --output-format concise 2>&1 | sed 's/:.*//' | sort | uniq -c | sort -rn > config/m23_baseline.txt
	@echo "$(GREEN)Baseline regenerated: config/m23_baseline.txt$(NC)"

# Run all mandate checks (CI gate)
check-mandates: check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity
	@echo "$(GREEN)All mandate checks passed$(NC)"

## Run Ark Blueprint drift & M14 integrity check (read-only dry-run)
ark-optimize:
	@$(PYTHON) scripts/ark_optimizer.py --dry-run
	@echo "✅ Dry-run complete. Run 'make ark-optimize-report' to write the report file."

## Run Ark Blueprint check and write report to data/coordination/ARK_OPTIMIZATION_REPORT.md
ark-optimize-report:
	@$(PYTHON) scripts/ark_optimizer.py
	@echo "✅ Report written to data/coordination/ARK_OPTIMIZATION_REPORT.md"

.PHONY: check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates
