# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Omega Engine Test Suite Makefile — Carmack Mode v2
# First public release — this IS the legacy.

# Configuration — M24: Always use project venv Python
PYTHON := .venv/bin/python
PYTEST := .venv/bin/python -m pytest

# Use bash so targets can rely on [[ ]] / bash-isms (e.g. local inference lifecycle)
SHELL := /bin/bash

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: help test test-all test-prepush test-clarity test-json test-summary test-watch test-watch-all test-pick test-pick-skim notify-test test-random test-flake-hunt test-cov test-debug test-clean clean codex check-codex-stale check-codex-fix check-codex-force ark-optimize ark-optimize-report lint doc-llm-validate sprint-plan-llm sprint-plan-llms-txt doc-token-check doc-chunk-sprint temple-grade check-tracking-state check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates heritage-vet heritage-map sote-index sote-digest sote-validate sote-week sote-pipeline sote-full help-sote check-broken-imports check-hub-health

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
	@echo "Provider Benchmark & Diurnal Dashboard:"
	@echo "  dashboard             Live terminal dashboard (refresh 2s, Ctrl+C to exit)"
	@echo "  dashboard-once        Single snapshot of provider benchmark"
	@echo "  dashboard-self-test   Run 53 adversarial in-process tests (--self-test)"
	@echo "  dashboard-test        Run 128 pytest unit tests (test_benchmark_dashboard.py)"
	@echo "  dashboard-ci          Run --once + --self-test + pytest (for CI gate)"
	@echo "  probe-models          Probe free model availability/latency"
	@echo "  probe-network         Probe network latency (gateway, DNS, OpenRouter)"
	@echo "  probe-antigravity     Probe Antigravity account quotas"
	@echo ""
	@echo "Local Inference (native-gguf / llama-cpp):"
	@echo "  infer-start       Start native-gguf servers (extractor:1234, reasoner:1235)"
	@echo "  infer-stop        Stop native-gguf servers and unload models from RAM"
	@echo "  infer-restart     Stop then start native-gguf servers"
	@echo "  infer-status      Show native-gguf server state, PIDs, health, memory"
	@echo "  infer-memory      Report RAM/swap footprint of loaded models"
	@echo "  infer-stop-all    Full unload: native-gguf + ollama + lingering llama procs"
	@echo "  infer-models      List available GGUF models in the models directory"
	@echo "  infer-talk        Smoke-test the running native-gguf server (MSG=...)"
	@echo "  infer-logs        Tail live server logs (LOG=extractor|reasoner)"
	@echo "  infer-events      Show lifecycle events from events.jsonl (N=last N)"
	@echo "  infer-health      Detailed health: status + memory + log tail"
	@echo "  infer-debug       Full debug dump: status + memory + events + logs"
	@echo ""
	@echo "Codex Targets (D-277 Hydration):"
	@echo "  codex             Regenerate OMEGA_CODEX.md from groups.json"
	@echo "  check-codex-stale Check if Codex >24h old; exit 1 if stale"
	@echo "  check-codex-fix   Check and auto-regenerate if stale"
	@echo ""
	@echo "SOTE Targets:"
	@echo "  sote-index       Regenerate SOTE master index"
	@echo "  sote-digest      Generate public digest (SOTE_WEEK=YYYY-WNN)"
	@echo "  sote-validate    Validate sote.yaml against JSON Schema"
	@echo "  sote-pipeline    Full mechanical pipeline (index + digest + validate + temple-grade)"
	@echo "  sote-week        Weekly pipeline (alias for sote-pipeline)"
	@echo "  sote-full        Full SOTE including human steps reminder"

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
# SOTE Targets (Week 37+)
# =============================================================================

# Regenerate SOTE master index
sote-index:
	@echo "$(YELLOW)Regenerating SOTE Master Index...$(NC)"
	@$(PYTHON) scripts/regenerate_sote_index.py
	@echo "$(GREEN)SOTE index regenerated$(NC)"

# Generate public digest for current week
SOTE_WEEK ?= $(shell date -u +%Y-W%V)
sote-digest:
	@echo "$(YELLOW)Generating public digest for week $(SOTE_WEEK)...$(NC)"
	@$(PYTHON) scripts/generate_public_digest.py docs/strategy/sote/$(SOTE_WEEK)
	@echo "$(GREEN)Public digest generated$(NC)"

# Validate sote.yaml against JSON Schema
sote-validate:
	@echo "$(YELLOW)Validating sote.yaml against JSON Schema...$(NC)"
	@$(PYTHON) scripts/validate_sote_schema.py
	@echo "$(GREEN)sote.yaml schema validation passed$(NC)"

# Full SOTE mechanical pipeline (index + digest + validate + temple-grade)
sote-pipeline: sote-index sote-digest sote-validate
	@echo "$(YELLOW)Running temple-grade gate...$(NC)"
	@$(MAKE) temple-grade
	@echo "$(GREEN)SOTE mechanical pipeline complete — all gates passed$(NC)"

# Weekly SOTE target (run Monday 06:00 UTC via cron)
sote-week: sote-pipeline
	@echo "$(GREEN)SOTE mechanical pipeline complete for week $(SOTE_WEEK)$(NC)"

# Full SOTE including human steps (topic selection, voice paging, etc.)
sote-full: sote-week
	@echo "SOTE mechanical pipeline complete. Human steps remaining:"
	@echo "  1. Select topic for next week"
	@echo "  2. Page 8 voices for dialectic"
	@echo "  3. Conduct dialectic rounds"
	@echo "  4. Synthesize report"
	@echo "  5. Publish SOTE report"

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
# Provider Benchmark & Diurnal Dashboard
# =============================================================================
# Live terminal dashboard for the diurnal provider benchmark suite.
# Reads: data/metrics/free_model_probes.jsonl
#        data/metrics/network_probes.jsonl
#        data/metrics/antigravity_quotas.jsonl
#        data/metrics/antigravity_{stress,burst,long_duration}_test_*.jsonl
# Refresh: every 2s. Press Ctrl+C to exit.

.PHONY: dashboard dashboard-once dashboard-self-test dashboard-test dashboard-ci probe-models probe-network probe-antigravity

dashboard:
	@echo "$(YELLOW)Launching provider benchmark dashboard (Ctrl+C to exit)...$(NC)"
	@$(PYTHON) scripts/benchmark_dashboard.py

dashboard-once:
	@echo "$(YELLOW)Rendering single snapshot of provider benchmark...$(NC)"
	@timeout 3 $(PYTHON) scripts/benchmark_dashboard.py 2>&1 | head -80 || true

# R4 (maat): Run the in-process adversarial suite (jem R3's 53 tests).
# Used by CI gate; also useful as a local sanity check before publishing.
dashboard-self-test:
	@echo "$(YELLOW)Running benchmark_dashboard adversarial tests (53 cases)...$(NC)"
	@$(PYTHON) scripts/benchmark_dashboard.py --self-test

# R4 (maat): Run the pytest unit test suite (128 tests in <5s).
# Style mirrors tests/unit/test_circuit_breaker.py — pytest, no extra deps.
dashboard-test:
	@echo "$(YELLOW)Running benchmark_dashboard pytest suite (128 tests)...$(NC)"
	@cd "$(CURDIR)" && $(PYTEST) tests/unit/test_benchmark_dashboard.py -v --tb=short -p no:cacheprovider --confcutdir=tests/unit

# R4 (maat): Aggregate CI target. Runs --once (smoke), --self-test (53 tests),
# and pytest (129 tests) in sequence. Wired into the dashboard-test GitHub
# Actions workflow. Exit non-zero if any step fails.
dashboard-ci: dashboard-self-test dashboard-test
	@echo "$(YELLOW)Rendering dashboard-once for smoke test...$(NC)"
	@$(PYTHON) scripts/benchmark_dashboard.py --once --no-clear 2>&1 | head -10
	@echo "$(GREEN)dashboard-ci: all checks passed$(NC)"

# Run a single probe sweep across all configured free models
probe-models:
	@echo "$(YELLOW)Probing free model availability/latency...$(NC)"
	@bash scripts/probe_free_models.sh

# Run network probes (gateway, DNS, OpenRouter connectivity)
probe-network:
	@echo "$(YELLOW)Probing network latency...$(NC)"
	@bash scripts/network_metrics.sh

# Run Antigravity account quota probe (per-account model availability)
probe-antigravity:
	@echo "$(YELLOW)Probing Antigravity account quotas...$(NC)"
	@$(PYTHON) scripts/antigravity_quota_probe.py

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

# Temple-grade includes Codex freshness, LLM doc validation, mandate
# compliance meter, and tracking state validation. (P0-1 fix 2026-08-28:
# meter was decoupled — now gates the chain.)
# R4 (maat): dashboard-self-test is now part of the chain — the dashboard
# is M13 shippable only when its 53 adversarial tests pass.
temple-grade: check-codex-stale doc-llm-validate check-mandates check-mandate-compliance check-tracking-state dashboard-self-test
	@echo "$(YELLOW)Running temple-grade checks...$(NC)"
	@echo "$(GREEN)Temple-grade complete (Codex + LLM doc validation + Mandates + Compliance + Tracking State + Dashboard)$(NC)"

# M37 Heritage — REUSE v3.3 SPDX compliance gate
# Verifies every file has SPDX-FileCopyrightText and SPDX-License-Identifier
# per the REUSE specification v3.3. Wired into CI (.github/workflows/reuse-compliance.yml)
# and pre-commit (.pre-commit-config.yaml: reuse-lint-file on pre-commit, reuse on pre-push).
# Per RESEARCHER_GAP_FILL_PHASE_2_20260830.md MED-3.
REUSE := .venv/bin/reuse

check-reuse:
	@echo "$(YELLOW)Checking REUSE v3.3 compliance (M37 Heritage)...$(NC)"
	@$(REUSE) --version
	@$(REUSE) lint
	@echo "$(GREEN)M37 passed: REUSE v3.3 compliant (all files have SPDX headers)$(NC)"

# Check kq5-godot experiment (VNR vision system integration)
# Runs the experiment's make check (22 checks) and validates VNR integration
check-kq5:
	@echo "$(YELLOW)Checking kq5-godot experiment (VNR vision system)...$(NC)"
	@if [ ! -L data/experiments/kq5-godot ]; then \
		echo "$(RED)FAIL: kq5-godot symlink not found at data/experiments/kq5-godot$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d /media/arcana-novai/omega_library/games/kq5-godot ]; then \
		echo "$(RED)FAIL: kq5-godot source not found at /media/arcana-novai/omega_library/games/kq5-godot$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running kq5-godot make check (22 checks)...$(NC)"
	@cd data/experiments/kq5-godot && $(MAKE) check
	@echo "$(YELLOW)Verifying VNR script...$(NC)"
	@cd /media/arcana-novai/omega_library/games/kq5-godot && python3 scripts/vnr_render.py --help >/dev/null
	@echo "$(YELLOW)Verifying VNR backend import...$(NC)"
	@cd /media/arcana-novai/omega_library/games/kq5-godot && python3 -c "import sys; sys.path.insert(0, '.'); from vnr import VisionBackendVNR; print('VNR backend import OK')"
	@echo "$(GREEN)kq5-godot check passed: experiment operational, VNR integrated$(NC)"

# Download license texts to LICENSES/ directory (run once after clone)
reuse-download:
	@echo "$(YELLOW)Downloading license texts...$(NC)"
	@$(REUSE) download --all
	@echo "$(GREEN)License texts downloaded to LICENSES/$(NC)"

# Cognitive State Validator (M27 Tracking Integrity)
# Wired into temple-grade + pre-commit (omega-tracking-state). Includes the
# M1 staleness rule (in_progress > 7d = error) and M3 warn-only schema checks.
check-tracking-state:
	@echo "$(YELLOW)Validating tracking state (M27)...$(NC)"
	@$(PYTHON) scripts/validate_tracking_state.py

# Tier-3 zombie sweep (M27, G5-1 amendment) — MANUAL ONLY.
# NEVER wire into pre-commit/temple-grade: --apply mutates TASK_REGISTRY.json
# and ambiguous cases route to a review list (exit 3), which would brick CI.
# Dry-run by default; pass APPLY=1 to execute.
sweep-tasks:
	@echo "$(YELLOW)Sweeping TASK_REGISTRY zombies (dry-run)...$(NC)"
	@$(PYTHON) scripts/sweep_task_registry.py $(if $(APPLY),--apply,)

# Self-test for the sweep (fail-closed proof, M13/M21)
sweep-self-test:
	@$(PYTHON) scripts/sweep_task_registry.py --self-test

# Regenerate EXPERT_SESSION_REGISTRY.md from TASK_REGISTRY.json +
# session_annotations.yaml (M4). Output is GENERATED — never hand-edit.
session-registry:
	@$(PYTHON) scripts/generate_session_registry.py

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

# P0 CI Gates — Broken imports detection
check-broken-imports:
	@echo "$(YELLOW)Checking for broken imports in src/omega/...$(NC)"
	@failed=0; \
	for f in $$(find src/omega -name "*.py" -not -path "*/__pycache__/*" -not -path "*/test*" 2>/dev/null); do \
		if ! $(PYTHON) -m py_compile "$$f" 2>/dev/null; then \
			echo "$(RED)FAIL: Syntax error in $$f$(NC)"; \
			$(PYTHON) -m py_compile "$$f" 2>&1 | sed 's/^/  /'; \
			failed=1; \
		fi; \
	done; \
	if [ $$failed -eq 1 ]; then \
		echo "$(RED)Broken imports detected$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)No broken imports in src/omega/$(NC)"

# P0 CI Gates — Omega Hub health check
check-hub-health:
	@echo "$(YELLOW)Checking Omega Hub health...$(NC)"
	@if ! systemctl --user is-active omega-hub.service >/dev/null 2>&1; then \
		echo "$(RED)FAIL: omega-hub.service is not active$(NC)"; \
		systemctl --user status omega-hub.service --no-pager; \
		exit 1; \
	fi
	@echo "$(GREEN)omega-hub.service is active$(NC)"
	@if ! curl -sf -o /dev/null --max-time 5 http://localhost:8080/sse 2>/dev/null; then \
		echo "$(RED)FAIL: SSE endpoint not responding on localhost:8080/sse$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)SSE endpoint responding$(NC)"
	@if ! curl -sf -o /dev/null --max-time 5 -X POST http://localhost:8080/mcp \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' 2>/dev/null; then \
		echo "$(RED)FAIL: Streamable HTTP endpoint not responding$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Streamable HTTP endpoint responding$(NC)"
	@echo "$(GREEN)Omega Hub health check passed$(NC)"

# Regenerate the M23 baseline (run after intentionally fixing violations)
m23-baseline:
	@echo "$(YELLOW)Regenerating M23 baseline...$(NC)"
	@$(PYTHON) -m ruff check src/omega --select S110,S112,BLE001,E722 --output-format concise 2>&1 | sed 's/:.*//' | sort | uniq -c | sort -rn > config/m23_baseline.txt
	@echo "$(GREEN)Baseline regenerated: config/m23_baseline.txt$(NC)"

# Run all mandate checks (CI gate). P0-1 fix 2026-08-28: compliance meter
# is now part of the chain — a red meter can no longer hide behind green gates.
check-mandates: check-m1-anyio check-asyncio-import check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity verify-mandate-claims check-mandate-compliance
	@echo "$(GREEN)All mandate checks passed$(NC)"

# Claims harness (Team-Study #1 ruling S7, P0): claims-vs-disk gate +
# sanitation / FP-11 / T0 detectors over changed files. WARN-ONLY phase
# (ruling S5) — always EXIT 0; findings are structured warnings.
verify-mandate-claims:
	@echo "$(YELLOW)Running verify-mandate-claims (warn-only)...$(NC)"
	@$(PYTHON) scripts/verify_mandate_claims.py
	@echo "$(GREEN)verify-mandate-claims passed (warn-only mode)$(NC)"

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

.PHONY: check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates check-mandate-compliance check-mandate-compliance-json verify-mandate-claims check-kq5

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

# =============================================================================
# Local Inference Lifecycle (native-gguf / llama-cpp)
# =============================================================================
# Lifecycle + observability for the local GGUF inference servers
# (extractor:1234, reasoner:1235) managed by scripts/serve_native_gguf.sh.
# These commands let you start, stop, inspect, and DEBUG the local inference
# engines, and — critically — UNLOAD the models from RAM when not needed.
#
# All lifecycle logic lives in scripts/serve_native_gguf.sh (single source of
# truth). Logs + pid files + lifecycle events live in data/logs/native-gguf/
# (persistent, M8-compliant local observability — never external telemetry).
#
# Observability targets:
#   infer-logs    — tail live server logs (LOG=extractor|reasoner, default both)
#   infer-events  — show recent lifecycle events from events.jsonl
#   infer-health  — detailed health: status + memory + recent log tail
#   infer-debug   — full debug dump: status + memory + events + log tail
#
# See SOVEREIGN_MANDATES.md §M8 (zero telemetry: local observability in data/
# is acceptable; external telemetry is not).

INFER_LOG_DIR := data/logs/native-gguf
INFER_MODELS_DIR := $(or $(OMEGA_MODELS_DIR),/media/arcana-novai/omega_library/models/gguf)

.PHONY: infer-start infer-stop infer-restart infer-status infer-memory infer-stop-all infer-models infer-talk infer-logs infer-events infer-health infer-debug

# Start both native-gguf servers (extractor:1234, reasoner:1235)
infer-start:
	@bash scripts/serve_native_gguf.sh start

# Stop native-gguf servers and unload models from RAM (graceful then force).
infer-stop:
	@bash scripts/serve_native_gguf.sh stop

# Stop then start native-gguf servers
infer-restart:
	@bash scripts/serve_native_gguf.sh restart

# Show native-gguf server state: PIDs, health, and memory footprint
infer-status:
	@bash scripts/serve_native_gguf.sh status

# Report RAM/swap footprint of loaded models (per running llama server)
infer-memory:
	@echo "$(YELLOW)Loaded model memory footprint:$(NC)"
	@found=0; \
	for pid in $$(pgrep -f "python3 -m llama_cpp.server" || true); do \
		[[ -r "/proc/$$pid/status" ]] || continue; \
		model=$$(tr '\0' ' ' < /proc/$$pid/cmdline 2>/dev/null | sed -n 's/.*--model \([^ ]*\.gguf\).*/\1/p'); \
		[[ -n "$$model" ]] || continue; \
		found=1; \
		rss_kb=$$(awk '/VmRSS/{print $$2}' /proc/$$pid/status 2>/dev/null); \
		swap_kb=$$(awk '/VmSwap/{print $$2}' /proc/$$pid/status 2>/dev/null); \
		rss_mb=$$(( $${rss_kb:-0} / 1024 )); \
		swap_mb=$$(( $${swap_kb:-0} / 1024 )); \
		printf "  PID %-8s RSS %6s MB  Swap %7s MB  %s\n" "$$pid" "$$rss_mb" "$$swap_mb" "$${model:-?}"; \
	done; \
	if [[ $$found -eq 0 ]]; then echo "  (no llama_cpp.server processes running)"; fi

# Full unload: stop native-gguf servers + ollama + any lingering llama processes
infer-stop-all:
	@echo "$(YELLOW)Full local-inference shutdown...$(NC)"
	@$(MAKE) --no-print-directory infer-stop
	@if pgrep -x ollama >/dev/null 2>&1; then \
		echo "  stopping ollama (PID $$(pgrep -x ollama))"; \
		kill $$(pgrep -x ollama) 2>/dev/null || true; sleep 1; \
		kill -9 $$(pgrep -x ollama) 2>/dev/null || true; \
	else echo "  ollama not running"; fi
	@ling=""; \
	for port in 1234 1235; do \
		pids=$$(ss -ltnp 2>/dev/null | awk -v p=":$$port " '$$0 ~ p {match($$0, /pid=[0-9]+/); if (RSTART) print substr($$0, RSTART+4, RLENGTH-4)}' | sort -u); \
		for pid in $$pids; do ling="$$ling $$pid"; done; \
	done; \
	if [[ -n "$$ling" ]]; then \
		echo "  killing lingering llama_cpp.server on ports 1234/1235:$$ling"; \
		kill $$ling 2>/dev/null || true; sleep 1; kill -9 $$ling 2>/dev/null || true; \
	else echo "  no lingering llama_cpp.server processes"; fi
	@echo "$(GREEN)All local inference engines stopped; models unloaded from RAM.$(NC)"

# List available GGUF models in the models directory
infer-models:
	@echo "$(YELLOW)Available GGUF models in $(INFER_MODELS_DIR):$(NC)"
	@if [[ -d "$(INFER_MODELS_DIR)" ]]; then \
		ls -1 "$(INFER_MODELS_DIR)"/*.gguf 2>/dev/null | sed 's#.*/##' || echo "  (no .gguf files found)"; \
	else \
		echo "  (models dir not found: $(INFER_MODELS_DIR))"; \
	fi

# Smoke-test the running native-gguf server. Usage: make infer-talk MSG="hello"
infer-talk:
	@if [[ -z "$(MSG)" ]]; then echo "usage: make infer-talk MSG='your question'"; exit 1; fi
	@echo "$(YELLOW)Querying native-gguf (reasoner:1235)...$(NC)"
	@curl -s --max-time 120 http://127.0.0.1:1235/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d "{\"messages\":[{\"role\":\"user\",\"content\":\"$(MSG)\"}],\"max_tokens\":64}" \
		| .venv/bin/python -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])" 2>/dev/null \
		|| echo "$(RED)infer-talk failed — is the reasoner server running? (make infer-status)$(NC)"

# ── Observability ───────────────────────────────────────────────────────────
# Tail live server logs. Usage: make infer-logs LOG=extractor (default: both)
infer-logs:
	@if [[ -n "$(LOG)" ]]; then \
		echo "$(YELLOW)Tailing $(LOG).log (Ctrl+C to exit)...$(NC)"; \
		tail -f "$(INFER_LOG_DIR)/$(LOG).log"; \
	else \
		echo "$(YELLOW)Tailing extractor.log + reasoner.log (Ctrl+C to exit)...$(NC)"; \
		tail -f "$(INFER_LOG_DIR)/extractor.log" "$(INFER_LOG_DIR)/reasoner.log"; \
	fi

# Show recent lifecycle events from events.jsonl (N=last N, default 20)
infer-events:
	@echo "$(YELLOW)Recent native-gguf lifecycle events:$(NC)"
	@if [[ -f "$(INFER_LOG_DIR)/events.jsonl" ]]; then \
		tail -n $(or $(N),20) "$(INFER_LOG_DIR)/events.jsonl" | \
		.venv/bin/python -c "import sys,json;[print(f\"  {json.loads(l)['ts']}  {json.loads(l)['event']:<16} {json.loads(l)['server']:<10} {json.loads(l).get('detail','')}\") for l in sys.stdin if l.strip()]" 2>/dev/null \
		|| tail -n $(or $(N),20) "$(INFER_LOG_DIR)/events.jsonl"; \
	else echo "  (no events yet — run make infer-start)"; fi

# Detailed health: status + memory + recent log tail
infer-health:
	@echo "$(YELLOW)════════ Native-GGUF Health ════════$(NC)"
	@bash scripts/serve_native_gguf.sh status
	@echo ""
	@$(MAKE) --no-print-directory infer-memory
	@echo ""
	@echo "$(YELLOW)Recent log activity:$(NC)"
	@for name in extractor reasoner; do \
		if [[ -f "$(INFER_LOG_DIR)/$$name.log" ]]; then \
			echo "  --- $$name.log (last 5 lines) ---"; \
			tail -n 5 "$(INFER_LOG_DIR)/$$name.log" | sed 's/^/    /'; \
		fi; \
	done

# Full debug dump: status + memory + events + log tail
infer-debug:
	@echo "$(YELLOW)════════ Native-GGUF Debug Dump ════════$(NC)"
	@$(MAKE) --no-print-directory infer-health
	@echo ""
	@echo "$(YELLOW)Lifecycle events:$(NC)"
	@$(MAKE) --no-print-directory infer-events N=30
	@echo ""
	@echo "$(YELLOW)Log directory contents:$(NC)"
	@ls -la "$(INFER_LOG_DIR)" 2>/dev/null | sed 's/^/  /' || echo "  (no log dir yet)"
	@echo ""
	@echo "$(YELLOW)System memory:$(NC)"
	@free -m | sed 's/^/  /'

# === SECRET GATES (D-K6, kali ruling 2026-08-22) ===
# gitleaks scan runs when the binary is on PATH, against DURABLE refs only
# (--branches --tags) per Kali ratification ho_409d1ada5e0a: IDE checkpoint
# shadow-refs (refs/cline/*) can resurrect purged secret-bearing objects as
# dangling commits and must neither fail gates nor hide durable-ref leaks.
# Gate passes ONLY at zero findings on durable refs (31 baselined FPs in
# .gitleaksignore, WHY-documented line-above each fingerprint).
.PHONY: gate-secrets
gate-secrets:
	@echo '=== gate-secrets: format-regex PRIMARY gates (durable refs) ==='
	@FAIL=0; \
	for R in 'GOCSPX-[A-Za-z0-9_-]{10,}' 'fc-[A-Za-z0-9_-]{16,}' 'AIzaSy[A-Za-z0-9_-]{20,}' 'tvly-[A-Za-z0-9]{10,}' 'eyJhbGci[A-Za-z0-9_.-]{30,}'; do \
		N=$$(git log -G "$$R" --branches --tags --oneline | wc -l); \
		echo "  git log -G '$$R' -> $$N commits"; \
		[ "$$N" -eq 0 ] || FAIL=1; \
	done; \
	PEM_R='-----BEGIN[ A-Z]*PRIVATE KEY-----'; \
	PEM_FILES=$$(git log -G "$$PEM_R" --branches --tags --name-only --format= | sort -u); \
	PEM_BAD=$$(echo "$$PEM_FILES" | grep -v -e '^docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md$$' -e '^docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md$$' -e '^docs/research/R_VAULT_SCHEMA_V2.md$$' -e '^$$' | wc -l); \
	PEM_N=$$(echo "$$PEM_FILES" | grep -c .); \
	if [ "$$PEM_BAD" -eq 0 ]; then \
		echo "  git log -G PEM -> $$PEM_N file(s), all baselined template FPs (P0-5 fix 2026-08-28: docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md + docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md + docs/research/R_VAULT_SCHEMA_V2.md; regex self-avoiding so gate source never self-matches)"; \
	else \
		echo "  git log -G PEM -> OFFENDING FILES:"; echo "$$PEM_FILES" | grep -v -e '^docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md$$' -e '^docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md$$' -e '^docs/research/R_VAULT_SCHEMA_V2.md$$'; FAIL=1; \
	fi; \
	if command -v gitleaks >/dev/null 2>&1; then \
		echo '=== gitleaks durable refs (--branches --tags) ==='; \
		IGN=$$(grep -c '^# WHY:' .gitleaksignore 2>/dev/null || echo 0); \
		gitleaks detect --source . --redact --no-banner --log-opts='--branches --tags' >/dev/null 2>&1 \
			&& echo "  gitleaks: 0 findings (baseline ignored: $$IGN - see .gitleaksignore)" \
			|| { echo '  gitleaks: FINDINGS PRESENT'; FAIL=1; }; \
	else \
		echo '  (gitleaks not on PATH - regex gates only)'; \
	fi; \
	if [ "$$FAIL" -eq 0 ]; then echo 'gate-secrets PASSED'; else echo 'gate-secrets FAILED'; exit 1; fi
