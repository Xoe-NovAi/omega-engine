# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Omega Engine Test Suite Makefile — Carmack Mode v2
# First public release — this IS the legacy.

# ═══════════════════════════════════════════════════════════════════════════
# INTERPRETER RESOLUTION — M24 Venv Sovereignty (STRICT, no fallback)
# ═══════════════════════════════════════════════════════════════════════════
# [maat 2026-10-09, Phase 2.1] The previous line was:
#
#     PYTHON := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
#
# The `|| echo python3` branch is a SOFT FAILURE (M23). It reported a valid
# interpreter when the venv sovereignty contract was violated, so a gate that
# was meant to verify the venv would instead silently run against the system
# interpreter and pass. A gate that cannot tell you which interpreter it ran is
# not a gate — it is a coin toss with a green tick.
#
# There is no fallback here. If `.venv/bin/python` is absent, `make` STOPS and
# says so. `make bootstrap` is the sanctioned way to create the venv, and it is
# exempted from the check below so it can run on a fresh clone.
#
# `test -x` (not `wildcard`) is preserved deliberately: it tests EXECUTABILITY,
# which is the property that actually matters. A `python` file present but
# non-executable is a broken venv, and `wildcard` would treat it as valid.
VENV_PY := $(shell test -x .venv/bin/python && echo .venv/bin/python)

# Goals that must remain runnable on a fresh clone with no .venv at all.
# bootstrap creates the venv; clean and help must never be blocked by a
# missing venv, or a broken checkout could not be cleaned.
VENV_EXEMPT_GOALS := bootstrap clean help

ifneq ($(filter $(VENV_EXEMPT_GOALS),$(MAKECMDGOALS)),)
  PYTHON := $(VENV_PY)
else
  ifeq ($(VENV_PY),)
    $(error M24 VENV SOVEREIGNTY VIOLATED: .venv/bin/python not found or not executable. Refusing to fall back to system python3 (M23: no soft failures). Run `make bootstrap` first.)
  endif
  PYTHON := $(VENV_PY)
endif

PYTEST := $(PYTHON) -m pytest

# [maat 2026-09-28] Absolute form, for recipes that `cd` off the repo root
# before invoking the interpreter (check-kq5 checks an external checkout).
# M24: venv sovereignty applies there too — a bare `python3` in a gate is
# the same defect class as `--break-system-packages`.
PYTHON_ABS := $(abspath $(PYTHON))

# Sibling console scripts in the SAME venv. Derived from $(PYTHON) rather than
# hardcoded so a relocated venv cannot desynchronise the interpreter from the
# tools it was installed with (Phase 2.1 / 2.12: hardcoded-interpreter audit).
# Only `reuse` is needed as a sibling script. There is deliberately NO `$(PIP)`:
# every pip invocation in this file is either bootstrap's (which runs before
# $(PYTHON) can be trusted to exist) or check-hub-imports' (which runs inside a
# throwaway worktree with its OWN venv, where this repo's $(PYTHON) is the wrong
# interpreter by construction).
VENV_BIN := $(dir $(PYTHON))
REUSE   := $(VENV_BIN)reuse

# Use bash so targets can rely on [[ ]] / bash-isms (e.g. local inference lifecycle)
SHELL := /bin/bash

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

.PHONY: bootstrap check-lan-exposure help test test-all test-prepush test-clarity test-json test-summary test-watch test-watch-all test-pick test-pick-skim notify-test test-random test-flake-hunt test-cov test-debug test-clean clean codex check-codex-stale check-codex-fix check-codex-force ark-optimize ark-optimize-report lint doc-llm-validate sprint-plan-llm sprint-plan-llms-txt doc-token-check doc-chunk-sprint temple-grade check-tracking-state check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity m23-baseline check-mandates heritage-vet heritage-map sote-index sote-digest sote-validate sote-week sote-pipeline sote-full help-sote check-broken-imports check-untracked-deps check-hub-health check-hub-imports soul-validate check-gnosis-continuity

# ═══════════════════════════════════════════════════════════════════════════
# bootstrap — Phase 2.1. The sanctioned way to produce a compliant .venv.
# ═══════════════════════════════════════════════════════════════════════════
# WHY THIS TARGET EXISTS NOW. Interpreter resolution above is strict: no
# `.venv/bin/python`, no `make`. Before Phase 2.1 there was a silent
# `|| echo python3` fallback, so a fresh clone appeared to work while running
# against the system interpreter — with none of the venv's dependencies. The
# failure surfaced later, in an unrelated gate, as an ImportError that looked
# like a code defect. Bootstrap converts that into an explicit, single command.
#
# IDEMPOTENT BY CONSTRUCTION (safe to re-run):
#   - `test -x` guards venv creation, so an existing good venv is not clobbered.
#   - the interpreter is re-resolved INSIDE the recipe (`$$VENV_PY`, shell-time),
#     never via `$(VENV_PY)`. See the parse-time note below — this is a bug that
#     was actually shipped and caught only by a fresh-clone run.
#   - pip is invoked via the venv's own interpreter, never a bare `pip`, because
#     a bare `pip` resolves against PATH and M24 forbids installing outside
#     the venv.
#
# [maat 2026-10-09, FIXED AFTER FRESH-CLONE TEST] `$(VENV_PY)` is a PARSE-TIME
# variable (`$(shell test -x ...)`). On a fresh clone the parse happens BEFORE
# this recipe creates `.venv`, so `$(VENV_PY)` expanded to the EMPTY STRING and
# every pip line became ` -m pip install ...` -> bash parsed that as the command
# `m` -> "m: command not found" -> exit 127. The `||` guards fired and printed
# FAIL, but make reported `Error 1 (ignored)` and the target still exited 0.
# Both halves were wrong:
#   1. WRONG INTERPRETER SOURCE — parse-time for a recipe whose whole purpose is
#      to establish the thing being parsed for. The fix is `$$VENV_PY` (shell
#      variable, expanded when the line runs, after venv creation).
#   2. SILENT SUCCESS — see `.DELETE_ON_ERROR`-style reasoning in the helper
#      below; a target that prints FAIL and returns 0 is the exact M23 defect
#      this whole Phase 2 is about. Never ship that.
bootstrap:
	@echo "$(YELLOW)bootstrap: establishing venv sovereignty (M24)...$(NC)"
	@if test ! -x .venv/bin/python; then \
		echo "  creating .venv..."; \
		python3 -m venv .venv || { echo "$(RED)FAIL: python3 -m venv .venv failed. Python 3.12+ required (M24).$(NC)"; exit 1; }; \
	else \
		echo "  .venv/bin/python present — reusing"; \
	fi
	@# Re-resolve at RECIPE time. $(VENV_PY) is empty here on a fresh clone.
	@VENV_PY=.venv/bin/python; \
	if test ! -x "$$VENV_PY"; then \
		echo "$(RED)FAIL: $$VENV_PY still not executable after venv creation — refusing to continue.$(NC)"; \
		exit 1; \
	fi; \
	echo "  upgrading pip toolchain..."; \
	"$$VENV_PY" -m pip install --upgrade pip setuptools wheel \
		|| { echo "$(RED)FAIL: pip upgrade failed in .venv$(NC)"; exit 1; }; \
	echo "  installing engine (editable, [cli,dev])..."; \
	"$$VENV_PY" -m pip install -e ".[cli,dev]" \
		|| { echo "$(RED)FAIL: editable install failed. Check pyproject.toml extras (M24: no --break-system-packages).$(NC)"; exit 1; }; \
	echo "  installing test toolchain..."; \
	"$$VENV_PY" -m pip install pytest pytest-xdist \
		|| { echo "$(RED)FAIL: pytest toolchain install failed$(NC)"; exit 1; }; \
	echo "$(GREEN)bootstrap: .venv ready — interpreter is $$VENV_PY$(NC)"
	@echo "  next: make temple-grade"

help:
	@echo "Omega Engine Makefile"
	@echo ""
	@echo "Setup:"
	@echo "  bootstrap          Create .venv + install deps (FIRST RUN after clone)"
	@echo ""
	@echo "Available targets:"
	@echo "  test              Fast offline unit tests (parallel)"
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
	@echo "  check-codex-stale Content-hash gate: exit 1 if Codex is out of date (NOT age-based)"
	@echo "  check-codex-fix   Check and auto-regenerate if out of date"
	@echo "  check-codex-force Force regenerate regardless of content hash"
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
# [maat 2026-10-09, Phase 2.2] `check-codex-stale` was AGE-BASED (>24h) and has
# been converted to CONTENT-HASH based in scripts/check_codex_stale.py. An age
# gate is a clock, not a correctness check: it goes red every 24h on a repo
# where nothing changed, and it goes green on a repo where the source changed
# and the artifact did not. It is deliberately NOT in the temple-grade chain
# (see that target) — the generated artifact is refreshed on its own cadence
# via codex-refresh.yml.

# Regenerate OMEGA_CODEX.md from groups.json
codex:
	@echo "$(YELLOW)Regenerating OMEGA_CODEX.md...$(NC)"
	@$(PYTHON) scripts/codex_cat.py
	@echo "$(GREEN)OMEGA_CODEX.md regenerated successfully$(NC)"

# Content-hash gate: exit 1 if OMEGA_CODEX.md is stale w.r.t. its inputs
check-codex-stale:
	@echo "$(YELLOW)Checking Codex content-hash staleness...$(NC)"
	@$(PYTHON) scripts/check_codex_stale.py

# Check and auto-regenerate if stale
check-codex-fix:
	@echo "$(YELLOW)Checking Codex staleness (auto-fix)...$(NC)"
	@$(PYTHON) scripts/check_codex_stale.py --fix

# Force regenerate regardless of content hash
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
# [maat 2026-10-09, Phase 2.7] `-x` (stop on first failure) is REMOVED from the
# test targets. Rationale: `-x` makes a run report ONE failure per invocation,
# so a suite with several independent defects requires N sequential runs to
# enumerate. Worse, it makes the run ORDER-DEPENDENT in what it reveals — the
# first failure hides everything after it, which reads as "one bug" when the
# truth is "several". A gate that under-reports is worse than a slow one,
# because the under-reporting is invisible. Full run, full picture, then fix.

# Default: fast unit tests only (<10s), parallel
.PHONY: test
test:
	$(PYTEST) --tb=short -m "not integration" tests/

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
	$(PYTEST) --tb=short --instafail --json-report --json-report-file=test-report.json -m "not integration" tests/

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
	$(PYTEST) --randomly-seed=$$(shuf -i 1-1000000 -n 1) --tb=short tests/

.PHONY: test-flake-hunt
test-flake-hunt:
	$(PYTEST) --randomly-seed=$$(shuf -i 1-1000000 -n 1) --tb=short tests/

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
	@$(PYTHON) scripts/validate_llm_docs.py \
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
	@$(PYTHON) scripts/check_doc_tokens.py --budget $(DOC_TOKEN_BUDGETS) docs/sprints/current/
	@echo "$(GREEN)Token check complete$(NC)"

# Chunk sprint plan for RAG/vector storage
doc-chunk-sprint:
	@echo "$(YELLOW)Chunking sprint plan for RAG...$(NC)"
	@$(PYTHON) scripts/chunk_sprint_plan.py docs/sprints/current/README.md
	@echo "$(GREEN)Chunking complete$(NC)"

# Temple-grade includes LLM doc validation, mandate compliance meter, and
# tracking state validation. (P0-1 fix 2026-08-28: meter was decoupled — now
# gates the chain.)
# R4 (maat): dashboard-self-test is now part of the chain — the dashboard
# is M13 shippable only when its 53 adversarial tests pass.
# [seam-fix 2026-09-27 maat] check-hub-imports is now the FIRST prerequisite.
# Rationale: every other gate in this chain is a static/artifact check. None of
# them execute an import of mcp_servers/. A daemon that cannot import passed
# this entire chain at 53/53 while crash-looping on boot. Import execution is
# the cheapest possible ground truth, so it runs FIRST and fails fast — there
# is no value in validating 53 dashboard cases against a broken engine.
# Cost ~30-45s (clean worktree + fresh venv + editable install).
#
# [maat 2026-10-09, Phase 2.2] check-codex-stale REMOVED from this chain.
# It was age-based (>24h), which made it a clock rather than a correctness
# check: it went red on a repo where nothing changed and green on a repo where
# the input changed and the artifact did not. It is now content-hash based in
# scripts/check_codex_stale.py and runs on its own cadence (codex-refresh.yml)
# and as a standalone gate (`make check-codex-stale`). Keeping it here would
# have coupled a generated-artifact refresh to the release gate.
# ── check-engine: FAST, DETERMINISTIC engine-touching subset ────────────────
# [maat 2026-09-28] Architect-ruled. `temple-grade` ran ZERO pytest tests: its
# transitive closure had no pytest invocation at all, and the headline "53/53"
# was `benchmark_dashboard.py --self-test`, a separate harness. So the release
# gate could be green while the engine did not boot.
#
# This is a SUBSET, not the full suite — temple-grade must stay runnable in
# seconds. The full suite remains available as `make test-suite-full`.
# [maat 2026-10-09, Phase 2.8] Baseline count updated 175 -> 180. This is a
# DOCUMENTED expectation of the subset's size, not a hard gate: the subset is
# specified by PATHS below, so the count moves as tests are added. It is
# recorded here so a reviewer noticing a drift asks "did a test get lost?" —
# the answer lives in this comment, not in a failing CI run.
#
# DETERMINISM. No `-n auto` and no pytest-randomly here, on purpose. With xdist
# the visible subset varies per run, so a red result could not be told apart
# from a flake, and "flaky" would become a verdict rather than a diagnosis. This
# subset must be either green or honestly red, every time.
#
# WHAT IS EXCLUDED, AND WHY (measured, not guessed):
#   tests/contracts/test_secret_history_gate.py — 42s alone; it re-runs the
#     secret scan that `gate-secrets` already performs in this same chain, so
#     including it doubles the cost and buys nothing. Still gated, just not here.
#   The 2 `TestFirewallCheckerIntegration` cases — 5.6s each. They are genuine
#     integration tests, not gate-relevant to engine boot. Still in the full suite.
ENGINE_FAST_TESTS := tests/test_hub_import_smoke.py \
                     tests/contracts/ \
                     --deselect tests/contracts/test_secret_history_gate.py \
                     --deselect tests/contracts/test_firewall_checker.py::TestFirewallCheckerIntegration \
                     tests/test_lan_exposure.py

check-engine:
	@echo "$(YELLOW)check-engine: fast engine-touching subset (deterministic, serial)...$(NC)"
	@$(PYTHON) -m pytest $(ENGINE_FAST_TESTS) \
	    -o addopts="--timeout=60 --tb=line -q -p no:randomly -p no:tldr" \
	    || (echo "$(RED)check-engine FAILED — the engine-touching subset is red.$(NC)"; exit 1)
	@$(PYTHON) scripts/test_lan_exposure_audit.py >/dev/null \
	    || (echo "$(RED)check-engine FAILED: LAN negative tests.$(NC)"; exit 1)
	@$(PYTHON) scripts/gnosis_archive.py verify >/dev/null \
	    || (echo "$(RED)check-engine FAILED: M15 gnosis continuity.$(NC)"; exit 1)
	@echo "$(GREEN)check-engine PASSED (boot + contracts + LAN + M15)$(NC)"

# ── Full pytest suite — NOT in temple-grade (too slow) ──────────────────────
# [maat 2026-09-28] Available on demand and writing a machine-readable count to
# data/validation/last_test_run.json. Kept out of the release chain because the
# full run is ~3-4 minutes and 15 of its failures are resource-dependent
# (InferenceOOMError at <1GB available RAM) — see the handoff. A gate that
# flaps on host memory is not a release gate; it is a coin toss with a
# confusing message. Run it before a PR, not inside the gate.
test-suite-full:
	@echo "$(YELLOW)Running full pytest suite...$(NC)"
	@mkdir -p data/validation
	@$(PYTHON) -m pytest \
	    -o addopts="--timeout=120 -n auto --tb=line -q -p no:randomly" \
	    --json-report --json-report-file=data/validation/last_test_run.json \
	    || (echo ""; \
	        echo "$(RED)═══ PYTEST SUITE FAILED ═══$(NC)"; \
	        echo "$(RED)Counts: the 'OMEGA TEST RESULT' line above is authoritative;$(NC)"; \
	        echo "$(RED)the bare terminal summary is suppressed by tests/conftest.py.$(NC)"; \
	        echo "$(RED)Machine-readable: data/validation/last_test_run.json$(NC)"; \
	        exit 1)

# check-engine joins the chain FIRST, before check-hub-imports: it is the
# cheapest signal that the engine boots, and there is no value in a 30-45s
# clean-worktree import gate if the fast subset is already red.
temple-grade: check-constraints check-engine check-hub-imports doc-llm-validate check-mandates check-mandate-compliance check-tracking-state dashboard-self-test

	@echo "$(YELLOW)Running temple-grade checks...$(NC)"
	@echo "$(GREEN)Temple-grade complete (Hub Imports + LLM doc validation + Mandates + Compliance + Tracking State + Engine Subset + Dashboard)$(NC)"

# SOUL_ARCHITECTURE_PROTOCOL v3.0 — Soul v8.0 CI gate (ratified by Kali-N0, ho_123f6ebff930)
# Enforces: axiom coverage (>=1 directive + >=1 principle ref), flat-list approved_lessons.yaml
# (R3 hydration contract), <=15 axiom ceiling, duplicate-key rejection.
soul-validate:
	@echo "$(YELLOW)Running Soul Architecture Validator (SOUL_ARCHITECTURE_PROTOCOL v3.0)...$(NC)"
	@$(PYTHON) scripts/validate_soul_architecture.py || (echo "$(RED)FAIL: Soul architecture violations found$(NC)" && false)
	@echo "$(GREEN)Soul architecture compliant: axioms covered, flat-list approved lessons, no duplicate keys$(NC)"

# M37 Heritage — REUSE v3.3 SPDX compliance gate
# Verifies every file has SPDX-FileCopyrightText and SPDX-License-Identifier
# per the REUSE specification v3.3. Wired into CI (.github/workflows/reuse-compliance.yml)
# and pre-commit (.pre-commit-config.yaml: reuse-lint-file on pre-commit, reuse on pre-push).
# Per RESEARCHER_GAP_FILL_PHASE_2_20260830.md MED-3.
# [maat 2026-10-09, Phase 2.1/2.12] Was a hardcoded `REUSE := .venv/bin/reuse`.
# It now derives from $(PYTHON) via VENV_BIN, so the REUSE binary can never
# come from a different interpreter than the one running the rest of the gates.
# A hardcoded sibling path is a venv-desync bug waiting for a relocated venv.
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
# [maat 2026-09-28] M24: was bare `python3`. Interpreter only — behaviour
# unchanged. $(CURDIR)-anchored because the recipe `cd`s to the external
# kq5-godot checkout first, so a relative .venv/bin/python would not
# resolve from there. PYTHON_ABS is the same interpreter as $(PYTHON).
	@cd /media/arcana-novai/omega_library/games/kq5-godot && $(PYTHON_ABS) scripts/vnr_render.py --help >/dev/null
	@echo "$(YELLOW)Verifying VNR backend import...$(NC)"
	@cd /media/arcana-novai/omega_library/games/kq5-godot && $(PYTHON_ABS) -c "import sys; sys.path.insert(0, '.'); from vnr import VisionBackendVNR; print('VNR backend import OK')"
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

# ⛔ [2026-09-29] HISTORICAL TASK-REGISTRY VIEW ONLY — NOT a source of live
# session ids. Use who_is('<peer>') for peers. Regenerating does NOT fix the
# shape problem: one row per agent cannot represent 285 structural EIS.
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
# [maat 2026-10-09, Phase 2.1/2.12] Was a hardcoded `.venv/bin/python`. Now
# $(PYTHON), so this gate cannot execute against a different interpreter than
# the one the rest of the chain resolved.
check-m9-error-integrity:
	@echo "$(YELLOW)Checking M9 (Error integrity)...$(NC)"
	@$(PYTHON) scripts/check_m9_error_integrity.py src/omega
	@echo "$(GREEN)M9 passed: No bare except in core (AST-verified, comments exempt)$(NC)"

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

# Check M7: Sovereignty policy (Synergy Model) — entity->tier mapping
check-m7-sovereignty:
	@echo "$(YELLOW)Checking M7 (sovereignty_policy + entity->tier mapping)...$(NC)"
	@$(PYTHON) scripts/check_m7_sovereignty.py || (echo "$(RED)FAIL: sovereignty_policy not configured$(NC)" && false)
	@echo "$(GREEN)M7 passed: sovereignty_policy + entity->tier mapping OK$(NC)"

check-m23-failure-integrity:
	@echo "$(YELLOW)Checking M23 (Failure integrity)...$(NC)"
	@$(PYTHON) scripts/m23_gate.py || (echo "$(RED)FAIL: M23 soft-failure patterns$(NC)" && false)
	@echo "$(GREEN)M23 passed: No new soft-failure patterns$(NC)"

# L3-MetaFrameVerification (0.92) — Cross-verification protocol for paged prompts
# [maat 2026-10-09, Phase 2.1/2.12] BOTH ends of the pipe now use $(PYTHON).
# The consumer was a bare `python3`, so the producer ran under the venv and
# the parser ran under the system interpreter. A cross-verification gate whose
# verifier is a different Python than the thing being verified is not
# verifying anything — and if the system interpreter lacked a dependency, it
# failed with an ImportError that looked like spoofed metadata.
check-metaframe:
	@echo "$(YELLOW)Running L3-MetaFrameVerification (0.92) cross-verification...$(NC)"
	@$(PYTHON) scripts/metaframe_verification.py --stdin --agent kali --json < /dev/null 2>&1 | $(PYTHON) -c "import sys, json; data=json.load(sys.stdin); sys.exit(0 if data.get('result')=='PASS' else 1)" || (echo "$(RED)FAIL: MetaFrame verification failed$(NC)" && false)
	@echo "$(GREEN)L3-MetaFrameVerification (0.92) passed: No spoofable metadata detected$(NC)"

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

# P0 CI Gates — Untracked dependency detection
# Fails if any committed .py file imports modules from untracked files
check-untracked-deps:
	@echo "$(YELLOW)Checking for untracked dependencies...$(NC)"
	@failed=0; \
	for f in $$(git ls-files --others --exclude-standard 'src/**/*.py' 2>/dev/null); do \
		if [ -f "$$f" ] && grep -qE '^(import |from )' "$$f" 2>/dev/null; then \
			echo "$(RED)UNTRACKED DEPENDENCY: $$f$(NC)"; \
			failed=1; \
		fi; \
	done; \
	if [ $$failed -eq 1 ]; then \
		echo "$(RED)Untracked dependencies detected$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)No untracked dependencies found$(NC)"

# P0 CI Gates — Omega Hub health check
# Regenerate the M23 baseline (run after intentionally fixing violations)
m23-baseline:
	@echo "$(YELLOW)Regenerating M23 baseline...$(NC)"
	@$(PYTHON) -m ruff check src/omega --select S110,S112,BLE001,E722 --output-format concise 2>&1 | sed 's/:.*//' | sort | uniq -c | sort -rn > config/m23_baseline.txt
	@echo "$(GREEN)Baseline regenerated: config/m23_baseline.txt$(NC)"

# Run all mandate checks (CI gate). P0-1 fix 2026-08-28: compliance meter
# is now part of the chain — a red meter can no longer hide behind green gates.
check-mandates: check-m1-anyio check-asyncio-import check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity check-metaframe check-untracked-deps check-gnosis-continuity verify-mandate-claims check-mandate-compliance check-sahs check-policy-constants check-lan-exposure check-constraints
	@echo "$(GREEN)All mandate checks passed$(NC)"

# M15 Sovereign Continuity gate: every entity session_gnosis.md must carry a
# GNOSIS-META provenance header, so a gnosis can always be traced back through
# the archive chain. Currently RED: the gnoses predate this tooling and are
# unstamped. That is the correct, expected state — the count is reported below
# for the Architect to rule on. Do NOT bulk-stamp to make this green: a stamp
# asserts provenance, and back-dating one is a fabricated audit record.
check-gnosis-continuity:
	@echo "$(YELLOW)Verifying M15 gnosis continuity headers...$(NC)"
	@$(PYTHON) scripts/gnosis_archive.py verify

# Compaction-Immune Constraint Re-assertion (P0-2, arXiv:2606.22528 defense).
#
# WHY THIS IS A GATE AND NOT A DOC. A governance artifact with nothing checking
# it rots silently -- and silent rot of the constraint set is the exact failure
# this layer exists to prevent (M13/Temple-Grade, M21/Gate Integrity). `--check`
# exits 1 if the manifest is missing, unparseable, over the 4KB injection
# budget, or missing any Tier-0/structural mandate ID.
#
# M23: the loader has no soft-fail path by construction. If this target ever
# goes red, that is a governance failure to fix, not a flake to retry.
check-constraints:
	@echo "$(YELLOW)Verifying compaction-immune constraint manifest (P0-2)...$(NC)"
	@$(PYTHON) scripts/load_constraints.py --check
	@$(PYTHON) -m pytest tests/test_constraint_reassertion.py \
	    -o addopts="--timeout=60 --tb=line -q -p no:randomly -p no:tldr" \
	    || (echo "$(RED)check-constraints FAILED: constraint re-assertion tests red.$(NC)"; exit 1)

# M24b Venv Sovereignty Gate (P1-5): verify .venv matches pyproject requirements
# [maat 2026-10-09, Phase 2.1/2.12] Was a hardcoded `.venv/bin/python`. Now
# $(PYTHON). This gate exists to PROVE venv sovereignty — running it with a
# hardcoded path meant it verified a path rather than the resolved interpreter,
# so a relocated venv would be graded against a file it was not using.
check-venv-sovereignty:
	@$(PYTHON) scripts/check_venv_sovereignty.py

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

# ─────────────────────────────────────────────────────────────────────────────
# check-sahs — Single Authoritative Handoff Surface gate [M29, 2026-09-28]
# ─────────────────────────────────────────────────────────────────────────────
# Three assertions, not counts:
#   1. EXACTLY ONE WRITER: Only the Hivemind daemon holds a write FD on any
#      packet file in the handoff tree.
#   2. PROJECTION RECONCILIATION (both directions):
#      A) Every packet on any surface (MCP list, filesystem, MemPalace) has
#         a 1:1 match in the authoritative store with identical session_id/
#         target_entity/status/created_at_utc.
#      B) Every envelope in the authoritative store is reachable via at least
#         one projection surface.
#   3. NO ROGUE WRITES: No process other than the Hivemind daemon writes
#      to the authoritative store.
#
# A count-only gate passes GE-N1's failure modes (11 dead M36 packets in
# pending/, MemPalace events with peers:[]). Reconciliation fails them.
# The gate MUST be observed red — a deliberate rogue write or orphan must
# make it fail before it is trusted green.
check-sahs:
	@echo "$(YELLOW)Checking SAHS Rule (Single Authoritative Handoff Surface)...$(NC)"
	@$(PYTHON) scripts/check_sahs.py
	@echo "$(GREEN)SAHS Rule passed: exactly one writer, projections reconciled, no rogue writes$(NC)"

# ─────────────────────────────────────────────────────────────────────────────
# check-policy-constants — One constant for stale threshold [M29, 2026-09-28]
# ─────────────────────────────────────────────────────────────────────────────
# Enforces: handoff.stale_threshold_days == handoff.hot_storage_max_days
# Coincidence is a bug waiting to drift. If two policies derive from separate
# constants, they WILL drift silently — the same failure mode as
# retention_expires_at being a stored field instead of a derived one.
check-policy-constants:
	@echo "$(YELLOW)Checking handoff policy constants (stale_threshold_days == hot_storage_max_days)...$(NC)"
	@$(PYTHON) scripts/check_policy_constants.py
	@echo "$(GREEN)Policy constants consistent: single source of truth for 90-day threshold$(NC)"

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

.PHONY: check-m1-anyio check-m9-error-integrity check-m8-zero-telemetry check-m7-local-first check-m23-failure-integrity check-metaframe m23-baseline check-mandates check-mandate-compliance check-mandate-compliance-json verify-mandate-claims check-kq5 check-sahs check-policy-constants

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

# Show native-gguf server state — PIDs, health, and memory footprint
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
		| $(PYTHON) -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])" 2>/dev/null \
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
	@if [[ -f "$(INFER_LOG_DIR)/events.jsonl" ]]; then \
		tail -n $(or $(N),20) "$(INFER_LOG_DIR)/events.jsonl" | \
		$(PYTHON) -c "import sys,json;[print(f\"  {json.loads(l)['ts']}  {json.loads(l)['event']:<16} {json.loads(l)['server']:<10} {json.loads(l).get('detail','')}\") for l in sys.stdin if l.strip()]" 2>/dev/null \
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
#
# Credential-shaped history is handled by scripts/check_secret_history.py:
# every distinct token in durable refs is hashed and must carry a disposition
# in .secret-history-baseline.toml (2026-09-25: 6 audited tokens — 2 revoked
# Firecrawl keys, 4 public GOCSPX cert fingerprints; +2026-10-07: 22 test-fixture
# mock Firecrawl tokens from cd12af4f history, disposition test-fixture). The gate previously used
# a bare "any match => fail" loop with no way to record a disposition, so it
# failed on history gitleaks already accepted and could never go green. A token
# baselined "revoked" must also never reappear in the working tree.
.PHONY: gate-secrets
gate-secrets:
	@echo '=== gate-secrets: format-regex PRIMARY gates (durable refs) ==='
	@FAIL=0; \
	$(PYTHON) scripts/check_secret_history.py || FAIL=1; \
	PEM_R='-----BEGIN[ A-Z]*PRIVATE KEY-----'; \
	PEM_FILES=$$(git log -G "$$PEM_R" --branches --tags --name-only --format= | sort -u); \
	PEM_BAD=$$(echo "$$PEM_FILES" | grep -v -e '^docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md$$' -e '^docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md$$' -e '^docs/research/R_VAULT_SCHEMA_V2.md$$' -e '^docs/reference/api/tools.md$$' -e '^$$' | wc -l); \
	PEM_N=$$(echo "$$PEM_FILES" | grep -c .); \
	if [ "$$PEM_BAD" -eq 0 ]; then \
		echo "  git log -G PEM -> $$PEM_N file(s), all baselined template FPs (P0-5 fix 2026-08-28 x3 + 2026-10-07 docs/reference/api/tools.md detector-doc template — `detect_api_keys` doc names the PEM pattern in prose, no key material; regex self-avoiding so gate source never self-matches)"; \
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

# ─────────────────────────────────────────────────────────────────────────────
# check-hub-imports — TIER B: clean-venv MCP server import gate  [seam-fix 2026-09-27 maat]
# ─────────────────────────────────────────────────────────────────────────────
# WHY A TIER B WHEN TIER A EXISTS
# Tier A (tests/test_hub_import_smoke.py) runs inside the existing venv and
# rides the default pytest suite — 2-5s, catches the defect on every commit.
# Tier B builds a DETACHED CLEAN WORKTREE at HEAD with a FRESH venv and an
# editable install. That is the only configuration that reproduces what a new
# user or CI runner actually gets. Tier A can pass against a dirty worktree
# whose untracked files mask an import failure; Tier B cannot, because only
# committed state exists in the detached worktree.
#
# WHAT IT IMPORTS — explicit list, never a glob. A `**/server.py` glob would
# also match data/entities/roc_racoon/workspace/hlmc_ore/gap4_mcp_auth/hub_server.py
# (carries the same stale import at its line 84) plus two deliberate
# archaeology snapshots under docs/hardening/omega-hub/. Those must keep their
# historical code. A glob would force a skip-list that rots.
# WHAT STATE IS TESTED — and why it is not HEAD
# A detached worktree at HEAD tests only COMMITTED state. That is correct for
# verifying a release tag and useless for local development: a developer with
# a legitimate uncommitted fix would see the gate fail on a tree that is
# actually healthy, and would be pushed toward `git commit --no-verify` to get
# a green board. That is exactly the pressure this gate exists to remove.
#
# So this gate tests HEAD + the tracked working-tree diff, applied inside the
# throwaway worktree. Properties that matter:
#   - It verifies the state a developer intends to ship, including pending fixes.
#   - It STILL excludes untracked files. An untracked module cannot mask an
#     import failure, because it is not present in the worktree at all. This is
#     the defect class that made the original 74-file incident invisible.
#   - It mutates nothing in the main checkout: `git diff HEAD` does not touch
#     the index, and `git apply` runs in the throwaway worktree only.
# If the diff does not apply cleanly, the gate fails loudly rather than
# silently testing stale content.
#
# WHY THE INSTALL IS BOUNDED  [doom_guy 2026-10-03, P0 release-gate hang]
# Measured, not assumed: `make temple-grade` exceeded 10 minutes and was killed.
# Bisect of every sub-target isolated this recipe, and within it the stall was
# the `pip install` at the editable-install step — NOT any pytest run, and NOT
# the new hub background loops (those only execute under the FastAPI lifespan,
# which a bare `python -c "import ..."` never reaches; proved by reading the
# call graph, not by assuming it).
#
# The cause is that this gate builds a FRESH venv and re-resolves the entire
# dependency closure from PyPI on every single run. There is no lockfile and no
# offline fast path, so unpinned ranges drift to newer releases whose wheels
# are not in the local pip cache, and the gate's wall time becomes
#   network_throughput x total_uncached_wheel_bytes
# rather than a property of the code under test. On this host pypi.org was
# serving at ~300 kB/s and ~90 MB of wheels were uncached — several hundred
# seconds of pure download, with the release gate appearing to "hang".
#
# A release gate that measures the network is a gate that reports a verdict
# about the internet. Two changes, both fail-loud (M23):
#   1. `timeout $(HUB_IMPORT_PIP_TIMEOUT)` — the chain can no longer be wedged
#      indefinitely by a slow or stalled mirror.
#   2. pip's own `--timeout/--retries` — a dead socket fails in seconds rather
#      than sitting on a read forever.
# The timeout is reported as its OWN distinct failure so an operator is told the
# real cause instead of the generic "editable install failed", which points at
# pyproject.toml and sends them debugging the wrong thing.
HUB_IMPORT_PIP_TIMEOUT ?= 420
# [D-621] PID-unique. This path used to be a fixed shared name, so two concurrent
# `make check-hub-imports` runs (the fleet runs them from parallel agents
# routinely) raced: one run's `trap cleanup` did `rm -rf` on the exact path the
# other was installing into, producing
#   OSError: [Errno 2] No such file or directory
# mid-install. The patch file was already `$$`-unique; the worktree was not —
# the asymmetry that caused the race. Now both are per-PID.
HUB_IMPORT_WORKTREE := /tmp/omega-hub-import-verify-$$
# HUB_IMPORT_MODE=auto      overlay the tracked working-tree diff AND SAY SO
# HUB_IMPORT_MODE=pristine  never overlay; the verdict describes HEAD exactly.
#                            The release/CI path sets pristine via require_clean.
HUB_IMPORT_MODE ?= auto
HUB_IMPORT_MODULES := mcp_servers.omega_hub.server \
                      mcp_servers.omega_hub.state \
                      mcp_servers.omega_hub.hub_tools \
                      mcp_servers.omega_hub.github_bridge \
                      mcp_servers.searxng.server \
                      mcp_servers.firecrawl.server

# [D-620] The gate describer. ABSOLUTE path, for the same reason as PYTHON_ABS:
# the recipe `cd`s into the verification worktree, where neither a relative
# script path nor an untracked file exists. Resolved from the invoking repo
# root (CURDIR) — never from $CWD-at-use-time.
HUB_IMPORT_GATE := $(abspath scripts/check_hub_import_gate.py)
# The repo the diff was taken FROM. Pinned at invocation, because the recipe
# later `cd`s into the verification worktree — reading the repo from $CWD at
# use time is the original CWD trap, reproduced one level down.
HUB_IMPORT_REPO := $(CURDIR)

check-hub-imports:
	@echo "$(YELLOW)Tier B: clean-worktree import gate for MCP servers...$(NC)"
	@rm -rf $(HUB_IMPORT_WORKTREE); \
	cleanup() { rm -rf $(HUB_IMPORT_WORKTREE) >/dev/null 2>&1; git worktree prune >/dev/null 2>&1; }; \
	trap cleanup EXIT INT TERM; \
	git worktree prune >/dev/null 2>&1; \
	if ! git worktree add --detach $(HUB_IMPORT_WORKTREE) HEAD >/dev/null 2>&1; then \
		echo "$(RED)FAIL: could not create detached worktree at HEAD$(NC)"; exit 1; \
	fi; \
	$(PYTHON_ABS) $(HUB_IMPORT_GATE) --repo $(HUB_IMPORT_REPO) --mode $(HUB_IMPORT_MODE) \
	    $(if $(filter 1 true yes,$(require_clean)),--require-pristine,) \
	    --patch-out /tmp/omega-hub-import-$$.patch || exit $$?; \
	if [ -s /tmp/omega-hub-import-$$.patch ]; then \
		if (cd $(HUB_IMPORT_WORKTREE) && git apply /tmp/omega-hub-import-$$.patch) >/dev/null 2>&1; then \
			:; \
		else \
			rm -f /tmp/omega-hub-import-$$.patch; \
			echo "$(RED)FAIL: working-tree diff does not apply onto HEAD — cannot verify$(NC)"; \
			echo "      the state you are about to commit. Resolve the divergence first."; \
			exit 1; \
		fi; \
	fi; \
	rm -f /tmp/omega-hub-import-$$.patch; \
	cd $(HUB_IMPORT_WORKTREE) || { echo "$(RED)FAIL: cannot enter worktree$(NC)"; exit 1; }; \
	if ! python3 -m venv .venv >/dev/null 2>&1; then \
		echo "$(RED)FAIL: venv creation failed$(NC)"; exit 1; \
	fi; \
	if timeout $(HUB_IMPORT_PIP_TIMEOUT) .venv/bin/pip install -q --timeout=30 --retries=2 \
	     -e ".[cli,dev]" >/dev/null 2>&1; then \
		:; \
	else \
		rc=$$?; \
		if [ "$$rc" -eq 124 ]; then \
			echo "$(RED)FAIL: editable install exceeded $(HUB_IMPORT_PIP_TIMEOUT)s in clean worktree$(NC)"; \
			echo "      This gate builds a fresh venv from PyPI with no lockfile, so its wall"; \
			echo "      time is a function of network throughput, NOT of the code under test."; \
			echo "      Warm the wheel cache and re-run, or raise HUB_IMPORT_PIP_TIMEOUT."; \
		else \
			echo "$(RED)FAIL: editable install failed in clean worktree (pip exit $$rc)$(NC)"; \
		fi; \
		exit 1; \
	fi; \
	FAILED=0; \
	for mod in $(HUB_IMPORT_MODULES); do \
		if OUT=$$(.venv/bin/python -c "import $$mod" 2>&1); then \
			echo "$(GREEN)  [ok] $$mod$(NC)"; \
		else \
			echo "$(RED)  [FAIL] $$mod$(NC)"; \
			echo "$$OUT" | tail -12 | sed 's/^/        /'; \
			FAILED=1; \
		fi; \
	done; \
	if [ "$$FAILED" -ne 0 ]; then \
		echo "$(RED)check-hub-imports FAILED — a daemon entry point does not import$(NC)"; \
		echo "$(RED)      tested tree: $$($(PYTHON_ABS) $(HUB_IMPORT_GATE) --repo $(HUB_IMPORT_REPO) --mode $(HUB_IMPORT_MODE) --label-only)$(NC)"; \
		exit 1; \
	fi; \
	echo "$(GREEN)check-hub-imports PASSED ($$(echo $(HUB_IMPORT_MODULES) | wc -w) modules import cleanly in a fresh venv) — tested tree: $$($(PYTHON_ABS) $(HUB_IMPORT_GATE) --repo $(HUB_IMPORT_REPO) --mode $(HUB_IMPORT_MODE) --label-only)$(NC)"

# ─────────────────────────────────────────────────────────────────────────────
# Check Omega Hub health — CRASH-LOOP DETECTING  [seam-fix 2026-09-27 maat]
# ─────────────────────────────────────────────────────────────────────────────
# WHY THIS WAS REWRITTEN
# The prior implementation gated on `systemctl --user is-active`, which reports
# "active" while a Type=simple unit sits in `activating (auto-restart)` — the
# window between crash and scheduled restart. During the omega-searxng-mcp
# storm (NRestarts=6991) that window is where the unit spends nearly all of its
# time. A gate that reports green during a 6991-restart crash loop is worse
# than no gate: it manufactures false confidence about a dead daemon.
#
# FIVE INDEPENDENT CONDITIONS, all required (M23 fail-loud, no soft-failures):
#   1. ActiveState == active
#   2. SubState    == running            (catches activating/auto-restart)
#   3. NRestarts   <= HUB_NRESTART_MAX  (catches the storm numerically)
#   4. port 8016 actually LISTENing, held by a real PID
#   5. the port holds the SAME PID for HUB_DWELL_S seconds (dwell)
# Plus an HTTP 200 on /health. A crash-looping daemon cannot satisfy the
# dwell check: its PID changes faster than the dwell window.
HUB_UNIT          := omega-hub.service
HUB_PORT          := 8016
HUB_HEALTH_URL    := http://localhost:$(HUB_PORT)/health
HUB_SSE_URL       := http://localhost:$(HUB_PORT)/sse
HUB_NRESTART_MAX  := 3
HUB_DWELL_S       := 5
HUB_HTTP_TIMEOUT  := 5

check-hub-health:
	@echo "$(YELLOW)Checking Omega Hub health (crash-loop detection)...$(NC)"
	@UNIT="$(HUB_UNIT)"; NRMAX="$(HUB_NRESTART_MAX)"; DWELL="$(HUB_DWELL_S)"; \
	fail() { \
		echo "$(RED)FAIL: $$1$(NC)"; \
		echo "--- unit state ---"; \
		systemctl --user show $$UNIT -p ActiveState -p SubState -p NRestarts -p MainPID -p ExecMainStatus 2>/dev/null; \
		echo "--- recent log (last 20) ---"; \
		journalctl --user -u $$UNIT -n 20 --no-pager 2>/dev/null | tail -20; \
		echo "$(RED)check-hub-health FAILED$(NC)"; \
		exit 1; \
	}; \
	ST=$$(systemctl --user show $$UNIT -p ActiveState --value 2>/dev/null); \
	SS=$$(systemctl --user show $$UNIT -p SubState --value 2>/dev/null); \
	NR=$$(systemctl --user show $$UNIT -p NRestarts --value 2>/dev/null); \
	[ "$$ST" = "active" ] || fail "ActiveState=$$ST (expected active)"; \
	[ "$$SS" = "running" ] || fail "SubState=$$SS (expected running — 'activating'/'auto-restart' means crash-looping)"; \
	echo "  ActiveState=$$ST  SubState=$$SS  NRestarts=$$NR"; \
	echo "$(GREEN)  [1/5] ActiveState=active SubState=running$(NC)"; \
	echo "$(GREEN)  [2/5] NRestarts=$$NR <= $$NRMAX$(NC)"; \
	PID1=$$(ss -ltnp 2>/dev/null | grep "127.0.0.1:$(HUB_PORT) " | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); \
	[ -n "$$PID1" ] || fail "port $(HUB_PORT) is NOT LISTENing on 127.0.0.1"; \
	echo "$(GREEN)  [3/5] port $(HUB_PORT) LISTENing (pid=$$PID1)$(NC)"; \
	echo "  dwelling $$DWELL s to confirm the port is stable..."; \
	sleep $$DWELL; \
	PID2=$$(ss -ltnp 2>/dev/null | grep "127.0.0.1:$(HUB_PORT) " | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); \
	[ -n "$$PID2" ] || fail "port $(HUB_PORT) stopped LISTENing during the $${DWELL}s dwell window"; \
	[ "$$PID1" = "$$PID2" ] || fail "pid changed during dwell ($$PID1 -> $$PID2) — the daemon is restarting"; \
	echo "$(GREEN)  [4/5] dwell ok: port held by pid $$PID2 for >= $$DWELL s$(NC)"; \
	CODE=$$(curl -s -o /dev/null -w '%{http_code}' --max-time $(HUB_HTTP_TIMEOUT) $(HUB_HEALTH_URL) 2>/dev/null); \
	[ "$$CODE" = "200" ] || fail "/health returned HTTP $$CODE (expected 200)"; \
	curl -sfI --max-time $(HUB_HTTP_TIMEOUT) $(HUB_SSE_URL) >/dev/null 2>&1 || fail "SSE endpoint not responding on $(HUB_SSE_URL)"; \
	echo "$(GREEN)  [5/5] /health HTTP 200 + /sse responding$(NC)"; \
	UP=$$(cut -d. -f1 /proc/uptime); \
	AETM=$$(systemctl --user show $$UNIT -p ActiveEnterTimestampMonotonic --value 2>/dev/null); \
	UPTIME_S=$$( [ -n "$$AETM" ] && echo $$(( UP - AETM/1000000 )) || echo "unknown" ); \
	echo "$(GREEN)Omega Hub healthy$(NC)  ActiveState=$$ST SubState=$$SS NRestarts=$$NR pid=$$PID2 uptime_s=$$UPTIME_S"; \
	$(PYTHON) scripts/check_hub_code_stamp.py || { echo "$(RED)check-hub-health FAILED: stale code process$(NC)"; exit 1; }

# LAN EXPOSURE GATE (E1 2026-09-28, doom_guy/S1). Restored to the chain after
# 51d07148 rewrote this file and dropped the wiring — the gate still existed and
# still passed, but nothing invoked it. A gate nothing calls is a gate that
# cannot fail, which is the same defect class as the 53/53 over a crash-looping
# hub. See config/lan_exposure_allowlist.yaml for the rationale.
# The negative tests run FIRST and are unconditional: a gate never observed
# failing is not a gate.
check-lan-exposure:
	@echo "$(YELLOW)Running LAN exposure negative tests...$(NC)"
	@$(PYTHON) scripts/test_lan_exposure_audit.py
	@echo "$(YELLOW)Auditing host listeners against allowlist...$(NC)"
	@$(PYTHON) scripts/lan_exposure_audit.py
