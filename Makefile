# Omega Engine Test Suite Makefile — Carmack Mode v2
# First public release — this IS the legacy.

# Configuration — M24: Always use project venv Python
PYTHON := .venv/bin/python
PYTEST := .venv/bin/python -m pytest

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help test test-all test-prepush test-clarity test-json test-summary test-watch test-watch-all test-pick test-pick-skim notify-test test-random test-flake-hunt test-cov test-debug test-clean clean codex check-codex-stale check-codex-fix check-codex-force ark-optimize ark-optimize-report lint doc-llm-validate sprint-plan-llm sprint-plan-llms-txt doc-token-check doc-chunk-sprint temple-grade check-tracking-state check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates heritage-vet heritage-map

help:
	@echo "Omega Engine Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  test              Fast offline unit tests (parallel), stop on first failure"
	@echo "  test-all          Full suite, parallel, short tracebacks"
	@echo "  test-prepush      Fast + only affected tests (testmon incrementality)"
	@echo "  test-clarity      Enhanced output: instafail + tldr + json-report + clarity"
	@echo "  test-json         JSON report only (for tooling/CI)"
	@echo "  test-summary      Ultra-short summary (tldr)"
	@echo "  test-watch        Auto-re-run on file change (entr)"
	@echo "  test-watch-all    Watch full suite"
	@echo "  test-pick         Interactive test selection (fzf/skim)"
	@echo "  test-pick-skim    Interactive test selection (skim)"
	@echo "  notify-test       Desktop notification via OSC 9"
	@echo "  test-random       Randomized order to expose flakes"
	@echo "  test-flake-hunt   Randomized flake hunt"
	@echo "  test-cov          Coverage report"
	@echo "  test-debug        Run single test with full output (TEST=pattern)"
	@echo "  test-clean        Clean testmon cache"
	@echo "  clean             Remove all generated files"
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
# Test Suite Targets — Carmack Mode v2
# =============================================================================

# Default: fast unit tests only (<10s), parallel, stop on first failure
.PHONY: test
test:
	$(PYTEST) -x --tb=short -m "not integration" tests/

# Full suite: everything, parallel, short tracebacks
.PHONY: test-all
test-all:
	$(PYTEST) --tb=short tests/

# Pre-push: fast + only affected tests (testmon incrementality)
.PHONY: test-prepush
test-prepush:
	$(PYTEST) --tb=short --testmon -m "not integration" tests/

# Enhanced output: instafail + json-report + clarity (auto)
.PHONY: test-clarity
test-clarity:
	$(PYTEST) -x --tb=short --instafail --json-report --json-report-file=test-report.json -m "not integration" tests/

# JSON report only (for tooling/CI)
.PHONY: test-json
test-json:
	$(PYTEST) --tb=short --json-report --json-report-file=test-report.json --json-report-summary tests/

# Summary only (ultra-short)
.PHONY: test-summary
test-summary:
	$(PYTEST) --tldr tests/

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
	$(PYTEST) --collect-only -q -p no:tldr | fzf --multi | xargs -r $(PYTEST) -v

.PHONY: test-pick-skim
test-pick-skim:
	@command -v sk >/dev/null 2>&1 || { echo "skim not installed"; exit 1; }
	$(PYTEST) --collect-only -q -p no:tldr | sk --multi | xargs -r $(PYTEST) -v

# Desktop notification via OSC 9 (terminal standard: iTerm2, WezTerm, Kitty)
# Fallback to notify-send for terminals without OSC 9 support
.PHONY: notify-test
notify-test:
	@$(MAKE) test && (printf '\e]9;✅ Tests passed\a'; command -v notify-send >/dev/null && notify-send "Omega" "Tests passed") || printf '\e]9;❌ Tests failed\a'

# Flake detection: expose via randomization (don't mask with --reruns)
.PHONY: test-random
test-random:
	$(PYTEST) --randomly-seed=$$(shuf -i 1-1000000 -n 1) -x --tb=short tests/

.PHONY: test-flake-hunt
test-flake-hunt:
	$(PYTEST) --randomly-seed=$$(shuf -i 1-1000000 -n 1) -x --tb=short tests/

# Coverage report
.PHONY: test-cov
test-cov:
	$(PYTEST) -n auto --tb=short --cov=src/omega --cov-report=term-missing --cov-report=html tests/

# Debug: run single test with full output
.PHONY: test-debug
test-debug:
	$(PYTEST) -v --tb=long -k "$(TEST)" tests/

# Clean testmon cache
.PHONY: test-clean
test-clean:
	@rm -rf .testmondata .pytest_cache htmlcov test-report.json

# Run flake8 linting on src/omega/ (M13 quality gate)
# F821 is now enforced — all forward references use TYPE_CHECKING blocks
lint:
	@echo "$(YELLOW)Running flake8 lint...$(NC)"
	@$(PYTHON) -m flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@$(PYTHON) -m flake8 src/omega/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)Lint complete$(NC)"

# Clean all generated files
clean: test-clean
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
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
temple-grade: check-codex-stale doc-llm-validate check-mandates check-tracking-state
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

# Check M1 companion (audit r2 §1): any module driven by anyio.run() must NOT
# import asyncio. Catches the P0-1 bug class (asyncio.sleep under anyio.run)
# without banning standalone asyncio utilities (scripts that call asyncio.run
# directly are fine — they are not part of the anyio fabric).
check-asyncio-import:
	@echo "$(YELLOW)Checking M1 companion (no asyncio in anyio.run modules)...$(NC)"
	@failed=0; \
	for f in $$(rg -l 'anyio\.run\(' src/ scripts/ --type py --glob '!*test*' 2>/dev/null); do \
		if rg -q '^\s*import asyncio|^\s*from asyncio' "$$f" 2>/dev/null; then \
			echo "$(RED)FAIL: $$f uses anyio.run() but imports asyncio$(NC)"; failed=1; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then exit 1; fi
	@echo "$(GREEN)M1 companion passed: No asyncio in anyio.run() modules$(NC)"

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
	@$(PYTHON) scripts/check_m22_ssot.py

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
check-mandates: check-m1-anyio check-asyncio-import check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity
	@echo "$(GREEN)All mandate checks passed$(NC)"

# Mandate Compliance Meter (D-532 / T06) — mechanical compliance measurement.
# Parses SOVEREIGN_MANDATES.md for denominator (27, v3.8.0), runs per-mandate
# mechanical checks, emits JSON {"total": 27, "passed": N, ...}.
# Exit 0 = no failures (untested mandates are not counted, not failed).
check-mandate-compliance:
	@$(PYTHON) scripts/check_mandate_compliance.py
	@echo "$(GREEN)Mandate compliance meter passed$(NC)"

check-mandate-compliance-json:
	@$(PYTHON) scripts/check_mandate_compliance.py --json

## Run Ark Blueprint drift & M14 integrity check (read-only dry-run)
ark-optimize:
	@$(PYTHON) scripts/ark_optimizer.py --dry-run
	@echo "✅ Dry-run complete. Run 'make ark-optimize-report' to write the report file."

## Run Ark Blueprint check and write report to data/coordination/ARK_OPTIMIZATION_REPORT.md
ark-optimize-report:
	@$(PYTHON) scripts/ark_optimizer.py
	@echo "✅ Report written to data/coordination/ARK_OPTIMIZATION_REPORT.md"

## M14 Heritage Vet Gate — every [id-soft:] tag must have a vet record (HERITAGE_VET_LOG.md)
heritage-vet:
	@bash scripts/heritage_vet.sh

## M14 Heritage Map — audit + classification of all [id-soft:] tags, writes HERITAGE_AUDIT_REPORT.md
heritage-map:
	@$(PYTHON) scripts/heritage_audit.py --output-report
	@echo "✅ Heritage map written to data/coordination/HERITAGE_AUDIT_REPORT.md"

.PHONY: check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates check-mandate-compliance check-mandate-compliance-json

# === BUILD OBSERVABILITY (P8, AP-BUILD-OBS-v1.0.0) ===
# Wrap ANY long/native build with telemetry + auto-postmortem.
#   make observe CMD='bash scripts/install.sh'
# Artifacts -> /tmp/opencode/obs/<run-name>/ ; policy: docs/guides/BUILD_OBSERVABILITY.md
.PHONY: observe
observe:
	@if [ -z "$(CMD)" ]; then echo "usage: make observe CMD='<command>'"; exit 1; fi;
	@STAMP=$$(date +%Y%m%d-%H%M%S); bash scripts/observe-build.sh run-$$STAMP $(CMD)

# RAM-guarded install through the observer (llama-cpp builds etc.)
.PHONY: install-guarded
install-guarded:
	@STAMP=$$(date +%Y%m%d-%H%M%S); bash scripts/observe-build.sh install-$$STAMP bash scripts/install.sh

# === SECRET GATES (D-K6, kali ruling 2026-08-22) ===
# Format-regex -G scans are PRIMARY; bare-prefix -S is advisory only.
# gitleaks full-history scan runs when the binary is on PATH.
# Gate passes ONLY at zero findings across ALL refs.
.PHONY: gate-secrets
gate-secrets:
	@echo '=== gate-secrets: format-regex PRIMARY gates ==='
	@FAIL=0; \
	for R in 'GOCSPX-[A-Za-z0-9_-]{10,}' 'fc-[A-Za-z0-9_-]{16,}' 'AIzaSy[A-Za-z0-9_-]{20,}' 'tvly-[A-Za-z0-9]{10,}' 'eyJhbGci[A-Za-z0-9_.-]{30,}' '-----BEGIN [A-Z ]*PRIVATE KEY-----'; do \
		N=$$(git log -G "$$R" --all --oneline | wc -l); \
		echo "  git log -G '$$R' -> $$N commits"; \
		[ "$$N" -eq 0 ] || FAIL=1; \
	done; \
	if command -v gitleaks >/dev/null 2>&1; then \
		echo '=== gitleaks full-history ==='; \
		gitleaks detect --source . --redact --no-banner >/dev/null 2>&1 \
			&& echo '  gitleaks: 0 findings' \
			|| { echo '  gitleaks: FINDINGS PRESENT'; FAIL=1; }; \
	else \
		echo '  (gitleaks not on PATH — regex gates only)'; \
	fi; \
	if [ "$$FAIL" -eq 0 ]; then echo '✅ gate-secrets PASSED'; else echo '❌ gate-secrets FAILED'; exit 1; fi
