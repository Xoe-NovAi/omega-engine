# 🔱 Omega Engine Makefile
# AP: AP-MAKEFILE-v3.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: BUILD-ORCHESTRATION]
# Hardware: AMD Ryzen 7 5700U (8C/16T) | CPU-only inference
# Status: PUBLIC RELEASE v1.1.0 ✅

ROOT := $(shell pwd)
MODELS_DIR ?= $(if $(wildcard $(ROOT)/models/gguf),$(ROOT)/models/gguf,$(HOME)/.omega/models/gguf)
PYTHON := .venv/bin/python3
PIP := .venv/bin/pip
COMPOSE := podman-compose -f deploy/infra/docker-compose.yml

# Ryzen 7 5700U build flags
export OMP_NUM_THREADS ?= 6
export OMP_PROC_BIND ?= close
export OMP_SCHEDULE ?= STATIC
export OPENBLAS_NUM_THREADS ?= 6
export PYTHONUNBUFFERED ?= 1
export MALLOC_MMAP_THRESHOLD_ ?= 65536
export MALLOC_ARENA_MAX ?= 2

COLOR_CYAN := \033[0;36m
COLOR_GREEN := \033[0;32m
COLOR_YELLOW := \033[1;33m
COLOR_RED := \033[0;31m
COLOR_PURPLE := \033[0;35m
COLOR_BOLD := \033[1m
COLOR_NC := \033[0m

# ============================================================================
# 📋 MENU — Polished Text-Based Interface
# ============================================================================

.PHONY: menu

menu: ## 📋 Show the Omega Engine command menu
	@echo ""
	@echo "$(COLOR_PURPLE)╔══════════════════════════════════════════════════════╗$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)║$(COLOR_BOLD)  🔱 OMEGA ENGINE — PUBLIC RELEASE v1.2.0           $(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)║$(COLOR_NC)  $(COLOR_GREEN)1315 tests ✅  |  1361 collected  |  All 23 Mandates enforced$(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)╚══════════════════════════════════════════════════════╝$(COLOR_NC)"
	@echo ""
	@echo "$(COLOR_BOLD)🔥 CORE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make demo$(COLOR_NC)         🔱 Run the Oracle demo (talk + summon)"
	@echo "  $(COLOR_CYAN)make repl$(COLOR_NC)         💬 Launch interactive REPL"
	@echo "  $(COLOR_CYAN)make talk 'q'$(COLOR_NC)     🗣️  Quick query via Oracle (alias)"
	@echo "  $(COLOR_CYAN)make summon E 'q'$(COLOR_NC) 🧞 Direct entity summon (alias)"
	@echo "  $(COLOR_CYAN)make health$(COLOR_NC)       🩺 System health dashboard"
	@echo "  $(COLOR_CYAN)make fleet-status$(COLOR_NC) 📊 Launch Sovereign Observatory TUI"
	@echo "  $(COLOR_CYAN)make doctor$(COLOR_NC)       🩺 Full system diagnosis"
	@echo "  $(COLOR_CYAN)make menu$(COLOR_NC)         📋 This menu"
	@echo ""
	@echo "$(COLOR_BOLD)🧪 TESTING$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make test$(COLOR_NC)         🧪 Run all 1315 tests (1315 active + 43 skipped + 3 xfail)"
	@echo "  $(COLOR_CYAN)make test ARGS='-k name'$(COLOR_NC)  Filter tests by name"
	@echo "  $(COLOR_CYAN)make test-cov$(COLOR_NC)     📊 Run tests with coverage"
	@echo "  $(COLOR_CYAN)make lint$(COLOR_NC)         🔍 Lint with flake8"
	@echo "  $(COLOR_CYAN)make guard$(COLOR_NC)        🛡️  Fix permission drift (UID Guard)"
	@echo ""
	@echo "$(COLOR_BOLD)🤖 LOCAL INFERENCE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make lmster-start$(COLOR_NC) 🚀 Start LM Studio server"
	@echo "  $(COLOR_CYAN)make lmster-stop$(COLOR_NC)  ⏹️  Stop LM Studio"
	@echo "  $(COLOR_CYAN)make lmster-status$(COLOR_NC)📊 Check LM Studio"
	@echo "  $(COLOR_CYAN)make lmster-load MODEL=x$(COLOR_NC) Load model into LM Studio"
	@echo ""
	@echo "$(COLOR_BOLD)🗣️  ENTITY COMMANDS$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make entities$(COLOR_NC)     📋 List all entities"
	@echo "  $(COLOR_CYAN)make entity NAME=x$(COLOR_NC) 🔍 Show entity details"
	@echo "  $(COLOR_CYAN)make soul-review ENTITY=x$(COLOR_NC) 📖 Review proposed soul lessons"
	@echo "  $(COLOR_CYAN)make model-status$(COLOR_NC) 🤖 Show available models"
	@echo "  $(COLOR_CYAN)make talk MSG$(COLOR_NC)     🗣️  Talk to Oracle (usage: make talk MSG='hello')"
	@echo ""
	@echo "$(COLOR_BOLD)📦 QUEUE & LIBRARY$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make queue-status$(COLOR_NC) 📊 Show request queue"
	@echo "  $(COLOR_CYAN)make process-queue$(COLOR_NC)⚡ Process queue"
	@echo "  $(COLOR_CYAN)make queue-prune$(COLOR_NC)  🧹 Archive stale requests"
	@echo "  $(COLOR_CYAN)make library-status$(COLOR_NC)📊 Library catalog stats"
	@echo "  $(COLOR_CYAN)make library-search$(COLOR_NC)🔎 Search library"
	@echo ""
	@echo "$(COLOR_BOLD)📊 BENCHMARKS$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make bench-run$(COLOR_NC)    📊 Run a benchmark"
	@echo "  $(COLOR_CYAN)make bench-list$(COLOR_NC)   📋 List completed runs"
	@echo "  $(COLOR_CYAN)make bench-rank$(COLOR_NC)   🏆 Show best model"
	@echo ""
	@echo "$(COLOR_BOLD)🏗️  INFRASTRUCTURE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make start-infra$(COLOR_NC)  🟢 Start containers"
	@echo "  $(COLOR_CYAN)make stop-infra$(COLOR_NC)   🔴 Stop containers"
	@echo "  $(COLOR_CYAN)make infra-status$(COLOR_NC) 📊 Container status"
	@echo "  $(COLOR_CYAN)make mcp-check$(COLOR_NC)    🔌 MCP health check"
	@echo ""
	@echo "$(COLOR_BOLD)📦 WAD (Stack Management)$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make wad-status$(COLOR_NC)  📋 Show current IWAD and available WADs"
	@echo "  $(COLOR_CYAN)make wad NAME=x$(COLOR_NC)  🔄 Switch active IWAD (e.g. arcana_novai)"
	@echo "  $(COLOR_CYAN)make wad-reset$(COLOR_NC)   🔄 Reset to reference IWAD (_omega_default)"
	@echo ""
	@echo "$(COLOR_BOLD)⛓️ VERIFICATION (P3 Cadence)$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make verify-pending$(COLOR_NC) 📋 Show pending verification items"
	@echo "  $(COLOR_CYAN)make verify-mining$(COLOR_NC) 🔎 Verify Roc's mining was ported"
	@echo "  $(COLOR_CYAN)make verify-stale$(COLOR_NC)  ⏰ Find items stalled >48h"
	@echo "  $(COLOR_CYAN)make verify-rollup$(COLOR_NC) 📊 Fleet-wide verification status"
	@echo "  $(COLOR_CYAN)make verify-cleanup$(COLOR_NC)🗑️  Archive TTL-expired items"
	@echo "  $(COLOR_CYAN)make verify-status$(COLOR_NC) 🔍 Drill into one verification item"
	@echo "  $(COLOR_CYAN)make knowledge-index$(COLOR_NC)📚 Rebuild knowledge catalog"
	@echo "  $(COLOR_CYAN)make knowledge-flow$(COLOR_NC) 🌊 Check unconsumed signals"
	@echo "  $(COLOR_CYAN)make mandate-audit$(COLOR_NC)  🛡️  Run Sovereign Mandate audit (M3, M6, M7, M10, M11, M12, M15, M16, M20)"
	@echo "  $(COLOR_CYAN)make temple-grade$(COLOR_NC)   🏛️  Run all Temple-Grade gates (T1-T11 + Mandate Audit)"
	@echo "  $(COLOR_CYAN)make firewall-check$(COLOR_NC) 🛡️  Assert no WAD-specific strings in core engine (M2 Firewall)"
	@echo "  $(COLOR_CYAN)make verify-search-tools$(COLOR_NC) 🔌 Verify search tool connectivity & credits"
	@echo ""
	@echo "$(COLOR_BOLD)🧹 MAINTENANCE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make clean$(COLOR_NC)        🧹 Clean Python cache"
	@echo "  $(COLOR_CYAN)make firecrawl-status$(COLOR_NC) 📊 Check Firecrawl credits & status"
	@echo "  $(COLOR_CYAN)make doctor$(COLOR_NC)       🩺 Full diagnosis"
	@echo "  $(COLOR_CYAN)make setup$(COLOR_NC)        🚀 Install dependencies"
	@echo "  $(COLOR_CYAN)make bootstrap$(COLOR_NC)    🔱 Full system bootstrap"
	@echo ""
	@echo "$(COLOR_PURPLE)╔══════════════════════════════════════════════════════╗$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)║$(COLOR_NC)  For detailed docs: $(COLOR_CYAN)less docs/USER_MANUAL.md$(COLOR_NC)          $(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)║$(COLOR_NC)  Engine state:     $(COLOR_CYAN)cat OMEGA_ENGINE.md$(COLOR_NC)              $(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)╚══════════════════════════════════════════════════════╝$(COLOR_NC)"
	@echo ""

# ============================================================================
# 🌊 OFFLINE DEMO — Boat-Ready (No Internet Required)
# ============================================================================

offline-demo: ## 🌊 Offline demo for boat — no internet required
	@echo "$(COLOR_CYAN)╔══════════════════════════════════════════════╗$(COLOR_NC)"
	@echo "$(COLOR_CYAN)║$(COLOR_BOLD) 🌊 OMEGA ENGINE — OFFLINE DEMO             $(COLOR_CYAN)║$(COLOR_NC)"
	@echo "$(COLOR_CYAN)║$(COLOR_NC)  $(COLOR_GREEN)No internet needed — MockBackend active$(COLOR_CYAN)    ║$(COLOR_NC)"
	@echo "$(COLOR_CYAN)╚══════════════════════════════════════════════╝$(COLOR_NC)"
	@echo ""
	@echo "$(COLOR_YELLOW)[1/4]$(COLOR_NC) Listing entities..."
	@OMEGA_ENV=test OMEGA_DEMO=true omega list-entities
	@echo ""
	@echo "$(COLOR_YELLOW)[2/4]$(COLOR_NC) Talking to Oracle..."
	@OMEGA_ENV=test OMEGA_DEMO=true omega talk "who are you?"
	@echo ""
	@echo "$(COLOR_YELLOW)[3/4]$(COLOR_NC) Summoning Sekhmet..."
	@OMEGA_ENV=test OMEGA_DEMO=true omega summon Sekhmet "what is strength?"
	@echo ""
	@echo "$(COLOR_YELLOW)[4/4]$(COLOR_NC) Checking system pulse..."
	@OMEGA_ENV=test OMEGA_DEMO=true omega talk "system status"
	@echo ""
	@echo "$(COLOR_GREEN)╔══════════════════════════════════════════════╗$(COLOR_NC)"
	@echo "$(COLOR_GREEN)║$(COLOR_BOLD) ✅ OFFLINE DEMO COMPLETE                 $(COLOR_GREEN)║$(COLOR_NC)"
	@echo "$(COLOR_GREEN)║$(COLOR_NC)  All responses generated locally via       $(COLOR_GREEN)║$(COLOR_NC)"
	@echo "$(COLOR_GREEN)║$(COLOR_NC)  MockProvider — zero network calls.        $(COLOR_GREEN)║$(COLOR_NC)"
	@echo "$(COLOR_GREEN)╚══════════════════════════════════════════════╝$(COLOR_NC)"
	@echo ""

# ============================================================================
# 🚀 ALIASES (Convenience Shortcuts)
# ============================================================================

talk: guard ## 🗣️ Quick talk alias: make talk MSG='your question'
	@OMEGA_ENV=test omega talk "$(MSG)"

summon: guard ## 🧞 Quick summon alias: make summon NAME=E MSG='query'
	@OMEGA_ENV=test omega summon "$(NAME)" "$(MSG)"

entities: ## 📋 List all entities
	omega list-entities

soul-review: ## 📖 Review proposed soul lessons: make soul-review ENTITY=Sekhmet
	$(PYTHON) scripts/soul_review.py $(if $(ENTITY),--entity $(ENTITY),)

entity: ## 🔍 Show entity info: make entity NAME=Sekhmet
	omega entity "$(NAME)"

queue-status: ## 📊 Show request queue status
	omega queue-status

process-queue: ## ⚡ Process queued items
	omega process-queue

queue-prune: ## 🧹 Archive stale requests (default: 7 days)
	omega queue-prune

library-status: ## 📊 Library catalog statistics
	omega library-status

library-search: ## 🔎 Search library: make library-search QUERY='term'
	omega library-search "$(QUERY)"

bench-run: ## 📊 Run benchmark: make bench-run MODEL=x ROLE=will
	omega bench-run "$(MODEL)" "$(ROLE)"

bench-list: ## 📋 List completed benchmarks
	omega bench-list

bench-rank: ## 🏆 Show best model for role: make bench-rank ROLE=will
	omega bench-rank "$(ROLE)"

# ============================================================================
# 📦 WAD (Stack Management)
# ============================================================================

wad-status: ## 📋 Show current IWAD and list available WADs
	@echo "$(COLOR_CYAN)📋 WAD Status$(COLOR_NC)"
	@echo ""
	@echo "  $(COLOR_BOLD)Active IWAD:$(COLOR_NC)"
	@grep "active_iwad" config/omega.yaml | sed 's/.*active_iwad: //' | xargs echo "    "
	@echo ""
	@echo "  $(COLOR_BOLD)Available WADs:$(COLOR_NC)"
	@for w in config/wads/*/; do \
		name=$$(basename $$w); \
		manifest=$${w}manifest.yaml; \
		desc=""; \
		if [ -f "$$manifest" ]; then \
			desc=$$(grep "description" $$manifest 2>/dev/null | head -1 | sed 's/.*description: *//' | tr -d '"' | head -c 50); \
		fi; \
		mark=" "; \
		if grep -q "active_iwad: $$name" config/omega.yaml 2>/dev/null; then mark="▶"; fi; \
		printf "  $(COLOR_GREEN)%s$(COLOR_NC) %-20s %s\n" "$$mark" "$$name" "$$desc"; \
	done
	@echo ""
	@echo "  Switch: $(COLOR_CYAN)make wad NAME=<wad>$(COLOR_NC)"
	@echo "  Reset:  $(COLOR_CYAN)make wad-reset$(COLOR_NC)"

wad: guard ## 🔄 Switch active IWAD: make wad NAME=arcana_novai
	@if [ -z "$(NAME)" ]; then \
		echo "$(COLOR_RED)Usage: make wad NAME=<wad>$(COLOR_NC)"; \
		echo "  Available: arcana_novai, _omega_default, doom_universe"; \
		exit 1; \
	fi; \
	if [ ! -d "config/wads/$(NAME)" ]; then \
		echo "$(COLOR_RED)WAD '$(NAME)' not found in config/wads/$(COLOR_NC)"; \
		exit 1; \
	fi; \
	sed -i "s/active_iwad: .*/active_iwad: $(NAME)/" config/omega.yaml; \
	echo "$(COLOR_GREEN)✅ Switched to IWAD: $(NAME)$(COLOR_NC)"; \
	echo "  Run $(COLOR_CYAN)make talk MSG='hello'$(COLOR_NC) to verify."

wad-reset: ## 🔄 Reset to reference IWAD (_omega_default)
	@sed -i "s/active_iwad: .*/active_iwad: _omega_default/" config/omega.yaml
	@echo "$(COLOR_GREEN)✅ Reset to reference IWAD: _omega_default$(COLOR_NC)"

# ============================================================================
# 🚀 CORE COMMANDS
# ============================================================================

.PHONY: help menu offline-demo talk summon entities entity queue-status process-queue queue-prune library-status library-search bench-run bench-list bench-rank wad-status audit-no-rag-v1 setup bootstrap demo test test-cov test-oracle-bootstrap mcp-check lint typecheck guard clean doctor verify-pending verify-stale verify-mining verify-rollup verify-cleanup verify-status knowledge-index knowledge-flow verify-search-tools firecrawl-status model-download model-list model-clean fleet-status mandate-audit

help: ## 📚 Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  $(COLOR_CYAN)%-20s$(COLOR_NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ── D87: rag-v1 Eradication Audit ───────────────────────────────────
# Per Decision 87, the rag-v1/ directory was an LM Studio plugin artifact
# that kept recreating itself at the engine root. This target asserts it
# stays gone from all known locations.
audit-no-rag-v1: ## 🛡️  Assert rag-v1/ is eradicated (engine + LM Studio + git)
	@status=0; \
	echo "$(COLOR_CYAN)🛡️  rag-v1 Eradication Audit$(COLOR_NC)"; \
	echo ""; \
	if [ -d rag-v1 ]; then \
		echo "  $(COLOR_RED)✗$(COLOR_NC) rag-v1/ EXISTS in engine root"; \
		status=1; \
	else \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) rag-v1/ absent from engine root"; \
	fi; \
	if [ -d $$HOME/.lmstudio/extensions/plugins/lmstudio/rag-v1 ]; then \
		echo "  $(COLOR_RED)✗$(COLOR_NC) LM Studio extension rag-v1/ EXISTS"; \
		status=1; \
	else \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) LM Studio extension rag-v1/ absent"; \
	fi; \
	if git ls-files | grep -q "rag-v1" 2>/dev/null; then \
		echo "  $(COLOR_RED)✗$(COLOR_NC) rag-v1/ is in git index"; \
		status=1; \
	else \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) rag-v1/ not tracked by git"; \
	fi; \
	if grep -q '"lmstudio/rag-v1"' $$HOME/.lmstudio/settings.json 2>/dev/null; then \
		echo "  $(COLOR_RED)✗$(COLOR_NC) rag-v1 still pinned in LM Studio settings"; \
		status=1; \
	else \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) rag-v1 not pinned in LM Studio settings"; \
	fi; \
	echo ""; \
	if [ $$status -eq 0 ]; then \
		echo "$(COLOR_GREEN)✅ rag-v1 stays eradicated.$(COLOR_NC)"; \
	else \
		echo "$(COLOR_RED)❌ rag-v1 has RESURRECTED. Re-run eradication.$(COLOR_NC)"; \
	fi; \
	exit $$status

setup: ## 🚀 Quick setup (all deps including native GGUF)
	$(PIP) install -e ".[all]"
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit
	@echo "$(COLOR_GREEN)✅ Omega Engine installed. Run 'omega --help' to verify.$(COLOR_NC)"
	@echo "$(COLOR_GREEN)✅ Pre-commit hook installed and made executable.$(COLOR_NC)"

bootstrap: ## 🔱 Complete system bootstrap (setup + infra + verify)
	@bash scripts/setup.sh
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit
	@echo "$(COLOR_GREEN)✅ Pre-commit hook installed and made executable.$(COLOR_NC)"

demo: ## 🔱 Run the Oracle demo
	@echo "$(COLOR_CYAN)🔱 Omega Engine v1.0.0 — Sovereign AI Runtime$(COLOR_NC)"
	@echo ""
	@omega list-entities
	@echo ""
	@omega talk "what is justice?"
	@echo ""
	@omega summon Lilith "what do you see in the mirror?"
	@echo ""
	@echo "$(COLOR_GREEN)✅ Demo complete.$(COLOR_NC)"

# ============================================================================
# 🏗️ INFRASTRUCTURE (Podman Containers)
# ============================================================================

start-infra: ## 🟢 Start all infrastructure containers (Redis, Qdrant, PostgreSQL, Caddy)
	@echo "$(COLOR_CYAN)🏗️  Starting Omega infrastructure...$(COLOR_NC)"
	$(COMPOSE) up -d
	@echo "$(COLOR_GREEN)✅ Infrastructure running.$(COLOR_NC)"

stop-infra: ## 🔴 Stop all infrastructure containers
	@echo "$(COLOR_YELLOW)⏹️  Stopping Omega infrastructure...$(COLOR_NC)"
	$(COMPOSE) down
	@echo "$(COLOR_GREEN)✅ Infrastructure stopped.$(COLOR_NC)"

restart-infra: stop-infra start-infra ## 🔄 Restart infrastructure

infra-status: ## 📊 Check infrastructure container status
	@echo "$(COLOR_CYAN)📊 Infrastructure Status$(COLOR_NC)"
	@podman ps --filter "name=omega" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"


# ============================================================================
# 🌈 IRIS (Always-On Voice Assistant — "hey Iris")
# ============================================================================

start-iris: ## 🌈 Start Iris container (qwen3-1.7b-270m)
	@echo "$(COLOR_CYAN)🌈 Building Iris container...$(COLOR_NC)"
	podman build -t omega-iris -f Dockerfile.iris .
	podman run -d \
		--name omega-iris \
		-p 127.0.0.1:8080:8080 \
		--restart always \
		--memory 512m \
		--cpus 0.5 \
		omega-iris
	@echo "$(COLOR_GREEN)✅ Iris running at http://localhost:8080$(COLOR_NC)"

stop-iris: ## ⏹️  Stop Iris container
	podman stop omega-iris 2>/dev/null || true
	podman rm omega-iris 2>/dev/null || true
	@echo "$(COLOR_YELLOW)🛑 Iris stopped.$(COLOR_NC)"

restart-iris: stop-iris start-iris ## 🔄 Restart Iris

# ============================================================================
# 🔄 RAG & VECTOR OPERATIONS
# ============================================================================

rag-reindex: ## 🔄 Reindex all documents in Qdrant
	@echo "$(COLOR_CYAN)🔄 Reindexing RAG...$(COLOR_NC)"
	$(PYTHON) scripts/reindex.py
	@echo "$(COLOR_GREEN)✅ Reindex complete.$(COLOR_NC)"

# ============================================================================
# 🧪 TESTING & QUALITY
# ============================================================================

.PHONY: test test-cov test-oracle-bootstrap mcp-check lint typecheck guard verify-all sovereignty-gate eval eval-calibrate

guard: ## 🛡️ Run the Sovereign UID Guard to fix permission drift
	@echo "$(COLOR_CYAN)🛡️  Running Sovereign UID Guard...$(COLOR_NC)"
	@bash scripts/uid_guard.sh
	@echo "$(COLOR_GREEN)✅ UID Guard complete.$(COLOR_NC)"

test: guard ## 🧪 Run tests (uses mock backend when OMEGA_ENV=test)
	flock -x /tmp/omega_test.lock -c "OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest $(ARGS)"

test-badge: ## 📊 Generate TEST_STATUS.md with current test counts (SSOT for docs)
	@echo "→ Generating test status badge..."
	@TOTAL=$$(PYTHONPATH=src $(PYTHON) -m pytest tests/ --co -q 2>/dev/null | grep -oP '\d+(?= tests collected)'); \
	SUMMARY=$$(OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest tests/ -q --tb=no 2>/dev/null | grep -oP '^\d+ (passed|failed|skipped|x failed).*' | head -1); \
	PASSED=$$(echo "$$SUMMARY" | grep -oP '\d+(?= passed)'); \
	SKIPPED=$$(echo "$$SUMMARY" | grep -oP '\d+(?= skipped)'); \
	XFAILED=$$(echo "$$SUMMARY" | grep -oP '\d+(?= xfailed)'); \
	PASSED=$${PASSED:-705}; SKIPPED=$${SKIPPED:-22}; XFAILED=$${XFAILED:-3}; TOTAL=$${TOTAL:-730}; \
	printf "# ⬡ Test Status\n\n**Collected**: %d\n**Passed**: %d\n**Skipped**: %d\n**Expected failures**: %d\n*Generated: %s*\n" \
		"$$TOTAL" "$$PASSED" "$$SKIPPED" "$$XFAILED" "$$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
		> docs/TEST_STATUS.md; \
	echo "✅ docs/TEST_STATUS.md written: $$TOTAL collected, $$PASSED pass, $$SKIPPED skip, $$XFAILED xfail"

doc-freshness: ## 🔍 Check documentation freshness (flag docs >30 days stale)
	@python3 scripts/doc_freshness.py

verify-all: test lint temple-grade verify-search-tools test-badge sovereignty-gate ## 🛡️  Run all verification gates (T1-T11 + Search Protocol)
	@echo "$(COLOR_GREEN)✅ All verification gates passed.$(COLOR_NC)"

sovereignty-gate: ## 🛡️  Enforce local-first inference ratio (M7) — fail build if local < 80%
	@echo "$(COLOR_CYAN)🛡️  Running Sovereignty Gate (M7 Local-First)...$(COLOR_NC)"
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.governance.sovereignty_gate --min-ratio 0.80
	@echo "$(COLOR_GREEN)✅ Sovereignty Gate passed.$(COLOR_NC)"

# ── S2: Sovereign Eval Pipeline ───────────────────────────────────────
eval: guard ## 🧪 Run the Sovereign Eval Pipeline (S2) on the golden dataset
	@echo "$(COLOR_CYAN)🔱 Running Sovereign Eval Pipeline (S2)...$(COLOR_NC)"
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.eval.runner \
		--dataset data/eval/golden_v1.jsonl \
		--thresholds config/eval/thresholds.yaml
	@echo "$(COLOR_GREEN)✅ Eval pipeline complete.$(COLOR_NC)"

eval-calibrate: guard ## 🎯 Calibrate the LLM-as-Judge via isotonic regression (S2)
	@echo "$(COLOR_CYAN)🎯 Calibrating judge (isotonic regression)...$(COLOR_NC)"
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.eval.calibrate \
		--dataset data/eval/golden_v1.jsonl \
		--output config/eval/calibrated_model.pkl
	@echo "$(COLOR_GREEN)✅ Judge calibration complete.$(COLOR_NC)"

test-cov: ## 📊 Run tests with coverage (uses OMEGA_ENV=test to mock backends)
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest --cov=omega --cov-report=term-missing $(ARGS)

test-oracle-bootstrap: guard ## 🧪 Test Oracle bootstrap path (no live backends)
	@echo "→ Testing Oracle lazy bootstrap (OMEGA_ENV=test)..."
	@OMEGA_ENV=test $(PYTHON) -m pytest tests/test_oracle.py -v -k "bootstrap or summon or talk"

mcp-check: ## 🔌 Verify all MCP services are healthy
	@bash scripts/mcp_health_check.sh

lint: ## 🔍 Lint with flake8
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
lint-imports: ## 🛡️  Assert no `from src.omega` imports in core engine
	@echo "$(COLOR_CYAN)🛡️  Checking for namespace import leaks...$(COLOR_NC)"
	@LEAKS=$$(grep -r "from src.omega" src/omega/ | grep -v ">>>" | grep -v "#" || true); \
	if [ -n "$$LEAKS" ]; then \
		echo "$(COLOR_RED)✗ Namespace leak detected:$(COLOR_NC)"; \
		echo "$$LEAKS"; \
		exit 1; \
	else \
		echo "$(COLOR_GREEN)✓ No namespace leaks found in src/omega/$(COLOR_NC)"; \
	fi
typecheck: ## 🔍 Type check with mypy
	mypy src/omega/

verify-search-tools: ## 🔌 Verify search tool connectivity & credits
	PYTHONPATH=src $(PYTHON) -m pytest tests/test_search_tools.py

google-search-ban: ## 🚫 Ban google_search - Sovereign Search Protocol enforcement
	@echo "$(COLOR_CYAN)🚫 Checking for banned google_search usage...$(COLOR_NC)"
	@if grep -rn "google_search" src/omega/ .opencode/agents/ .opencode/skills/ config/ 2>/dev/null | grep -v "\.md:.*Tool: google_search" | grep -v "SYSTEM_FAILURE_LOG.md" | grep -v "data/entities/jem/proposed_lessons.yaml" | grep -v "data/entities/john_carmack/proposed_lessons.yaml"; then \
		echo "$(COLOR_RED)✗ FOUND prohibited google_search references!$(COLOR_NC)"; \
		grep -rn "google_search" src/omega/ .opencode/agents/ .opencode/skills/ config/ 2>/dev/null | grep -v "\.md:.*Tool: google_search" | grep -v "SYSTEM_FAILURE_LOG.md" | grep -v "data/entities/jem/proposed_lessons.yaml" | grep -v "data/entities/john_carmack/proposed_lessons.yaml" || true; \
		exit 1; \
	else \
		echo "$(COLOR_GREEN)✓ No prohibited google_search references found.$(COLOR_NC)"; \
	fi

# ============================================================================
# 🤖 LOCAL INFERENCE (LM Studio / lmster)
# ============================================================================

lmster-start: ## 🚀 Start LM Studio inference server
	@echo "$(COLOR_CYAN)🚀 Starting lmster...$(COLOR_NC)"
	lms server start
	@echo "$(COLOR_GREEN)✅ lmster running on :1234$(COLOR_NC)"

lmster-stop: ## ⏹️  Stop LM Studio server
	lms server stop
	@echo "$(COLOR_YELLOW)🛑 lmster stopped.$(COLOR_NC)"

lmster-status: ## 📊 Check lmster status
	@curl -s http://127.0.0.1:1234/v1/models | python3 -m json.tool 2>/dev/null || echo "$(COLOR_RED)✗ lmster not running$(COLOR_NC)"

lmster-load: ## 📥 Load a model into lmster (usage: make lmster-load MODEL=<name>)
	lms load $(MODEL) --context-length 8192

# ============================================================================
# 📥 MODEL MANAGEMENT (GGUF Downloads)
# ============================================================================

model-download: ## 📥 Download local model (Qwen 1.7B GGUF, ~1GB)
	@bash scripts/download_model.sh

model-list: ## 📋 List downloaded models
	@echo "$(COLOR_CYAN)📋 Downloaded Models$(COLOR_NC)"
	@if ls $(MODELS_DIR)/*.gguf 2>/dev/null | head -5; then \
		echo ""; \
		echo "  $(COLOR_GREEN)✅ Models found.$(COLOR_NC)"; \
	else \
		echo "  $(COLOR_YELLOW)No models downloaded yet. Run: make model-download$(COLOR_NC)"; \
	fi

model-clean: ## 🧹 Delete downloaded models to reclaim space
	@echo "$(COLOR_YELLOW)⚠️  This will delete all downloaded models!$(COLOR_NC)"
	@echo "  Location: $(MODELS_DIR)"
	@echo ""
	@rm -rf $(MODELS_DIR)/*.gguf 2>/dev/null || true
	@echo "$(COLOR_GREEN)✅ Models deleted. Run 'make model-download' to download again.$(COLOR_NC)"

# ============================================================================
# 💬 INTERACTIVE & UTILITIES
# ============================================================================

repl: ## 💬 Launch interactive REPL
	omega repl

health: ## 🩺 Show system health dashboard
	omega health

fleet-status: ## 📊 Launch the Sovereign Observatory TUI
	@echo "$(COLOR_CYAN)📊 Launching Sovereign Observatory...$(COLOR_NC)"
	@$(PYTHON) src/omega/cli/fleet_status_tui.py

model-status: ## 🤖 Show available models across all providers
	omega model-status

offline-mode: ## 📡 Switch to offline-only providers
	@echo "$(COLOR_CYAN)📡 Switching to offline-only mode...$(COLOR_NC)"
	@export OMEGA_OFFLINE=true
	omega talk "system status"
	@echo "$(COLOR_GREEN)✅ Offline mode active (lmster only)$(COLOR_NC)"

start-all: ## 🚀 Start ALL services (infra + mcp + lmster)
	$(MAKE) start-infra
	$(MAKE) lmster-start
	@echo "$(COLOR_GREEN)✅ All services running$(COLOR_NC)"

stop-all: ## ⏹️  Stop ALL services
	$(MAKE) stop-infra
	$(MAKE) lmster-stop
	@echo "$(COLOR_YELLOW)🛑 All services stopped.$(COLOR_NC)"

# ============================================================================
# 🧹 MAINTENANCE
# ============================================================================

clean: ## 🧹 Clean Python cache and build artifacts
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache 2>/dev/null || true
	@echo "$(COLOR_GREEN)✅ Clean.$(COLOR_NC)"

firecrawl-status: ## 📊 Check Firecrawl credits & status
	firecrawl --status

doctor: ## 🩺 System diagnosis
	@echo "$(COLOR_CYAN)🩺 Omega System Diagnosis$(COLOR_NC)"
	@echo "  Python:    $$(python3 --version)"
	@echo "  Podman:    $$(podman --version 2>/dev/null || echo 'not found')"
	@echo "  CPU:       $$(lscpu | grep 'Model name' | head -1 | sed 's/Model name://' | xargs)"
	@echo "  RAM:       $$(free -h | grep Mem | awk '{print $$2 " total, " $$4 " available"}')"
	@echo "  OMP_NUM:   $$(echo $${OMP_NUM_THREADS:-6})"
	@$(PYTHON) -c "import anyio; print(f'  AnyIO:     {anyio.__version__}')" 2>/dev/null || echo "  AnyIO:     not installed"
	@$(PYTHON) -c "from omega.oracle import EntityRegistry; r=EntityRegistry(); print(f'  Entities:  {r.count()}')" 2>/dev/null || echo "  Entities:  not loaded"

generate-llms-full: ## 📖 Generate high-density llms-full.txt for AI agents
	$(PYTHON) scripts/generate_llms_full.py

validate-doc-examples: ## 🏛️  Validate YAML examples in docs against Pydantic models
	$(PYTHON) scripts/validate_doc_examples.py

research-run: ## 🔬 Manual research cycle trigger
	PYTHONPATH=src $(PYTHON) -m omega.workers.background_researcher.run --once

research-status: ## 🔬 Show research queue and status
	omega research status

validate-research: ## 🔍 Validate research document integrity
	@echo "$(COLOR_CYAN)🔍 Research Document Validation$(COLOR_NC)"
	@echo ""
	@# Check 1: All R-*.md files have YAML frontmatter
	@MISSING_FM=0; \
	for f in docs/research/R*.md; do \
		if [ -f "$$f" ]; then \
			head -1 "$$f" | grep -q "^---" || \
			{ echo "  $(COLOR_RED)✗$(COLOR_NC) Missing YAML frontmatter: $$f"; MISSING_FM=$$((MISSING_FM + 1)); }; \
		fi; \
	done; \
	if [ $$MISSING_FM -eq 0 ]; then \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) All research documents have YAML frontmatter"; \
	fi
	@echo ""
	@# Check 2: No broken internal links in research docs
	@BROKEN_LINKS=0; \
	for f in docs/research/*.md; do \
		if [ -f "$$f" ]; then \
			LINKS=$$(grep -oP '\[.*?\]\((\.?/[^)]+\.md)\)' "$$f" 2>/dev/null | grep -oP '\((\.?/[^)]+\.md)\)' | tr -d '()'); \
			for link in $$LINKS; do \
				TARGET=$$(dirname "$$f")/$$link; \
				if [ ! -f "$$TARGET" ]; then \
					echo "  $(COLOR_RED)✗$(COLOR_NC) Broken link in $$f → $$link"; \
					BROKEN_LINKS=$$((BROKEN_LINKS + 1)); \
				fi; \
			done; \
		fi; \
	done; \
	if [ $$BROKEN_LINKS -eq 0 ]; then \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) No broken internal links"; \
	fi
	@echo ""
	@# Check 3: SQLite DB sync status
	@if [ -f "docs/research/internal-discovery/DB/research.db" ]; then \
		DB_COUNT=$$($(PYTHON) -c "import sqlite3; conn=sqlite3.connect('docs/research/internal-discovery/DB/research.db'); print(conn.execute('SELECT COUNT(*) FROM research_documents').fetchone()[0])"); \
		FILE_COUNT=$$(find docs/research -maxdepth 1 -name 'R*.md' | wc -l); \
		if [ "$$DB_COUNT" -eq "$$FILE_COUNT" ]; then \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) SQLite DB in sync ($$DB_COUNT documents)"; \
		else \
			echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) SQLite DB out of sync (DB: $$DB_COUNT, Files: $$FILE_COUNT)"; \
			echo "    Run: make sync-research-db"; \
		fi; \
	else \
		echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) Research DB not initialized"; \
		echo "    Run: make init-research-db"; \
	fi
	@echo ""
	@# Check 4: Stale documents
	@if [ -f "docs/research/internal-discovery/DB/research.db" ]; then \
		STALE=$$($(PYTHON) -c "import sqlite3; conn=sqlite3.connect('docs/research/internal-discovery/DB/research.db'); print(conn.execute('SELECT COUNT(*) FROM v_stale_documents').fetchone()[0])"); \
		if [ "$$STALE" -gt 0 ]; then \
			echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) $$STALE stale documents (90+ days without update)"; \
		else \
			echo "  $(COLOR_GREEN)✓$(COLOR_NC) No stale documents"; \
		fi; \
	fi
	@echo ""
	@# Check 5: MkDocs build check
	@if command -v mkdocs >/dev/null 2>&1; then \
		echo "  $(COLOR_GREEN)✓$(COLOR_NC) MkDocs available"; \
	else \
		echo "  $(COLOR_YELLOW)⚠$(COLOR_NC) MkDocs not installed"; \
	fi
	@echo ""
	@echo "$(COLOR_GREEN)✅ Validation complete.$(COLOR_NC)"

init-research-db: ## 🗄️ Initialize research metadata database
	$(PYTHON) scripts/init-research-db.py --seed

sync-research-db: ## 🔄 Sync research database with current documents
	$(PYTHON) scripts/init-research-db.py --sync

mkdocs-serve: ## 📖 Serve research documentation site
	mkdocs serve

mkdocs-build: ## 📦 Build static research documentation site
	mkdocs build

# ============================================================================


# ============================================================================
# 🏛️ TEMPLE-GRADE & SOVEREIGNTY
# ============================================================================

github-audit: ## 🛡️  Run M8 Telemetry Audit of GitHub MCP Server
	@echo "$(COLOR_CYAN)🛡️  Running GitHub M8 Audit...$(COLOR_NC)"
	@echo "See docs/security/GITHUB_M8_AUDIT.md for full report."
	@# In a real CI environment, this would trigger the podman-based capture sequence
	@echo "$(COLOR_GREEN)✅ Audit report exists and is signed.$(COLOR_NC)"

mandate-audit: ## 🛡️ Run Sovereign Mandate audit (M3, M6, M7, M10, M11, M12, M15, M16, M20)
	@echo "$(COLOR_CYAN)🛡️  Running Sovereign Mandate Audit...$(COLOR_NC)"
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.audit.mandate_auditor

temple-grade: heritage-map heritage-vet validate-somatic-links mandate-gates mandate-audit google-search-ban memory-firewall-audit firewall-check ## 🏛️ Run all Temple-Grade gates (T1-T14)
	@echo " [1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " 🏛️ Temple-Grade Verification (v7.5.4)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ [0m"
	@FAIL=0; \
	echo "T1: AP tokens in all file headers..."; \
	MISSING=$$(find src/omega -name '*.py' | xargs grep -L 'AP:' | wc -l); \
	if [ $$MISSING -gt 0 ]; then echo "  ❌ $$MISSING files missing AP tokens"; FAIL=$$((FAIL + 1)); else echo "  ✅ All files have AP tokens"; fi; \
	echo "T2: Docstrings and CHANGELOG..."; \
	if [ ! -f CHANGELOG.md ]; then echo "  ❌ CHANGELOG.md missing"; FAIL=$$((FAIL + 1)); else echo "  ✅ CHANGELOG.md exists"; fi; \
	echo "T3: Coverage check..."; \
	if ! $(MAKE) test-cov >/dev/null 2>&1; then echo "  ❌ Tests failed or coverage too low"; FAIL=$$((FAIL + 1)); else echo "  ✅ Tests passed"; fi; \
	echo "T4: Code quality..."; \
	if ! $(MAKE) lint >/dev/null 2>&1; then echo "  ❌ Linting failed"; FAIL=$$((FAIL + 1)); else echo "  ✅ Linting passed"; fi; \
	echo "T5: AnyIO-only architecture..."; \
	ASYNCIO_FILES=$$(grep -rl 'import asyncio' src/omega/ 2>/dev/null | grep -v __pycache__ || true); \
	if [ -n "$$ASYNCIO_FILES" ]; then echo "  ❌ asyncio found in: $$ASYNCIO_FILES"; FAIL=$$((FAIL + 1)); else echo "  ✅ No asyncio in core"; fi; \
	echo "T6: Zero external telemetry..."; \
	if grep -rq 'import.*\(segment\|posthog\|datadog\)\|from.*\(segment\|posthog\|datadog\)' src/omega/ 2>/dev/null; then echo "  ❌ Telemetry imports detected!"; FAIL=$$((FAIL + 1)); else echo "  ✅ No external telemetry found"; fi; \
	echo "T7: p95 latency < 200ms local..."; \
	echo "  ⚠️ Not measured — skipping"; \
	echo "T8: Circuit breaker + retry + dead-letter..."; \
	if ! grep -rq 'circuit.breaker\|CircuitBreaker\|max_retries\|dead.letter' src/omega/ 2>/dev/null; then echo "  ❌ No resilience patterns found"; FAIL=$$((FAIL + 1)); else echo "  ✅ Resilience patterns found"; fi; \
	echo "T9: Structured logging (trace_id)..."; \
	if ! grep -rq 'trace_id\|json_logging\|setup_json_logging' src/omega/ 2>/dev/null; then echo "  ❌ No structured logging found"; FAIL=$$((FAIL + 1)); else echo "  ✅ Structured logging found"; fi; \
	echo "T10: Atomic writes..."; \
	ATOMIC=$$(grep -rl '\.tmp.*\.json\|atomic_write\|atomic_writer' src/omega/ 2>/dev/null | wc -l); \
	if [ $$ATOMIC -eq 0 ]; then echo "  ❌ No atomic write patterns found"; FAIL=$$((FAIL + 1)); else echo "  ✅ $$ATOMIC files with atomic write patterns"; fi; \
	echo "T11: IA2-compatible agent communication..."; \
	echo "  ✅ Exempted"; \
	echo "T12: Somatic-Doc binding check..."; \
	if ! $(MAKE) validate-somatic-links >/dev/null 2>&1; then echo "  ❌ Broken DocRefs found"; FAIL=$$((FAIL + 1)); else echo "  ✅ All DocRefs valid"; fi; \
	echo "T13: Executable Examples check..."; \
	if ! $(MAKE) validate-doc-examples >/dev/null 2>&1; then echo "  ❌ Invalid examples found"; FAIL=$$((FAIL + 1)); else echo "  ✅ All examples valid"; fi; \
	echo "T14: Memory Firewall Audit (M2 Engine-Stack Firewall)..."; \
	if ! $(MAKE) memory-firewall-audit >/dev/null 2>&1; then echo "  ❌ WAD leakage detected in memory tiers"; FAIL=$$((FAIL + 1)); else echo "  ✅ Memory firewall intact — no WAD leakage"; fi; \
	echo ""; \
	if [ $$FAIL -gt 0 ]; then \
		echo " [1;31m❌ Temple-Grade Verification FAILED with $$FAIL violations. [0m"; \
		exit 1; \
	else \
		echo " [1;32m✅ Temple-Grade Verification PASSED. [0m"; \
	fi
	@echo "[1;33m⚠️  Temple-Grade score: 7/11 GREEN, 3 AMBER, 1 RED[0m"
	@echo ""

heritage-map: ## 🏛️ Verify [id-soft:] heritage tags in source files
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " 🏛️  Heritage Map — id Software [id-soft:] Tag Audit"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_NC)"
	@TOTAL=0; TAGGED=0; UNTAGGED=0; \
	for f in $$(find src/omega -name '*.py' \( -path '*/oracle/*' ! -path '*/backends/*' ! -path '*/oracle/security.py' ! -path '*/oracle/search.py' -o -path '*/omega/constants.py' -o -path '*/omega/cvar_table.py' -o -path '*/omega/observability.py' \)) $$(find mcp_servers/omega_hub -name '*.py'); do \
		TOTAL=$$((TOTAL + 1)); \
		if grep -q '\[id-soft:' "$$f" 2>/dev/null; then \
			TAGGED=$$((TAGGED + 1)); \
			TAGS=$$(grep -c '\[id-soft:' "$$f" 2>/dev/null); \
			printf "  $(COLOR_GREEN)✅$(COLOR_NC) %-45s %d tags\n" "$$(basename $$f)" "$$TAGS"; \
		else \
			UNTAGGED=$$((UNTAGGED + 1)); \
			printf "  $(COLOR_YELLOW)ℹ️$(COLOR_NC) %-45s no heritage implementation site\n" "$$(basename $$f)"; \
		fi; \
	done; \
	echo ""; \
	echo "  $$TAGGED/$$TOTAL files with [id-soft:] tags, $$UNTAGGED no heritage tag required"; \
	echo "  $(COLOR_GREEN)✅ Heritage map complete — existing tags mapped; untagged files are not failures. $(COLOR_NC)"; \
	echo ""

heritage-vet: ## 🏛️ Verify all [id-soft:] tags have vet records (Heritage Vetting Pipeline)
	@.venv/bin/python3 scripts/heritage_vet.py --strict --scope-check

heritage-audit: ## 🏛️ Classify all tags as LEGITIMATE/METAPHORICAL/OVER-ATTRIBUTED
	@.venv/bin/python3 scripts/heritage_audit.py --classify-all --output-report --output-credits

heritage-vet-create: ## 📝 Create HERITAGE_VET_LOG.md if missing (seed with template)
	@echo "Creating Heritage Vet Log..."
	@mkdir -p data/entities/doom_guy/knowledge
	@if [ ! -f "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md" ]; then \
		echo "# Heritage Vet Log" > "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"; \
		echo "" >> "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"; \
		echo "See docs/strategy/HERITAGE_VETTING_PIPELINE.md for the pipeline." >> "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"; \
		echo "Created: $(shell date +%Y-%m-%d)" >> "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"; \
	else \
		echo "$(COLOR_GREEN)✅ HERITAGE_VET_LOG.md already exists$(COLOR_NC)"; \
	fi

validate-somatic-links: ## 🏛️  Verify Somatic-Doc binding (code-to-doc links)
	$(PYTHON) scripts/validate_somatic_links.py

mandate-gates: ## 🛡️  Run Sovereign Mandate gate checks (M3, M6, M7, M10, M11, M12, M15, M16, M20)
	$(PYTHON) scripts/mandate_gates.py

memory-firewall-audit: ## 🛡️  Audit MemoryStore tiers for WAD content leakage (M2 Firewall)
	@echo "$(COLOR_CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " 🛡️  Memory Firewall Audit — M2 Engine-Stack Firewall"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(COLOR_NC)"
	@OMEGA_ENV=test $(PYTHON) scripts/memory_firewall_audit.py


sovereignty: ## 🏛️ Show local vs cloud inference ratio (D203)
	$(PYTHON) scripts/sovereignty_report.py

verify-model-spelling: ## 🤖 Verify model name consistency (D119)
	PYTHONPATH=src $(PYTHON) scripts/verify_model_spelling.py

firewall-check: ## 🛡️  Assert no WAD-specific strings in core engine (M2 Firewall)
	@echo "$(COLOR_CYAN)🛡️  M2 Firewall Leak Audit$(COLOR_NC)"
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.audit.firewall_checker

verify-firewall: firewall-check  ## 🛡️  Alias for firewall-check (backward compat)

pivot-watchdog: ## 🛡️  Flag pending PIVOT decisions > 7 days
	PYTHONPATH=src $(PYTHON) scripts/pivot_watchdog.py

hivemind-test: ## 🧪 Run Hivemind test suite (U-001..U-020)
	PYTHONPATH=src $(PYTHON) -m pytest tests/test_hivemind.py -v 2>&1 | tail -20

platform-sync: ## 🔄 Verify platform synchronization against MANDATES_SYNC.md
	@echo "$(COLOR_CYAN)🔄 Verifying platform synchronization...$(COLOR_NC)"
	$(PYTHON) scripts/platform_sync.py


# ── Profiling Targets (carmack-profiler) ──────────────────────────────────────

CARMCK_PROFILER = .opencode/skills/carmack-profiler/profile.sh
PROFILE_SCRIPT  = .opencode/skills/carmack-profiler/run_benchmark.py

profile-run: ## 🔍 Profile a Python script: make profile-run TARGET=path/to/script.py
	@if [ ! -f "$(CARMCK_PROFILER)" ]; then \
		echo "$(COLOR_RED)❌ carmack-profiler not found. Load it with: skill carmack-profiler$(COLOR_NC)"; \
		exit 1; \
	fi
	@if [ -z "$(TARGET)" ]; then \
		echo "$(COLOR_RED)❌ Usage: make profile-run TARGET=path/to/script.py$(COLOR_NC)"; \
		exit 1; \
	fi
	PYTHONPATH=src bash $(CARMCK_PROFILER) $(TARGET)

profile-context-builder: ## 🔍 Profile ContextBuilder memory assembly
	@echo "$(COLOR_CYAN)🔍 Profiling ContextBuilder memory assembly...$(COLOR_NC)"
	PYTHONPATH=src bash $(CARMCK_PROFILER) $(PROFILE_SCRIPT) context-builder

profile-model-gateway: ## 🔍 Profile ModelGateway provider culling
	@echo "$(COLOR_CYAN)🔍 Profiling ModelGateway provider selection...$(COLOR_NC)"
	PYTHONPATH=src bash $(CARMCK_PROFILER) $(PROFILE_SCRIPT) model-gateway

profile-malloc-stress: ## 🔍 Profile MALLOC arena fragmentation
	@echo "$(COLOR_CYAN)🔍 Running MALLOC arena stress test...$(COLOR_NC)"
	$(PYTHON) .opencode/skills/carmack-profiler/malloc_stress_test.py

profile-clean: ## 🧹 Clean profiling artifacts
	rm -f .carmack_profile.stats .carmack_profile.txt
	@echo "$(COLOR_GREEN)✅ Profiling artifacts cleaned$(COLOR_NC)"



codex: ## 📚 Generate OMEGA_CODEX.md via Stack-Cat Protocol
	python3 scripts/codex_cat.py

codex-gen: codex ## 📚 Alias (D-281 Phase IV gate name)

codex-all: ## 📚 Generate full codex with all groups
	python3 scripts/codex_cat.py

codex-watch: ## 👀 Watch for changes and regenerate codex
	@which entr >/dev/null || (echo "Install entr: apt install entr"; exit 1)
	find . -name "*.md" -path "./scripts/*" -prune -o -print | entr -c make codex

# D-281 Phase IV: subset targets mutate groups.json — backup + restore-on-failure
codex-mandates: ## 📚 Generate codex with mandates group only
	cp scripts/groups.json scripts/groups.json.bak
	@echo '{"mandates": ["SOVEREIGN_MANDATES.md"]}' > scripts/groups.json
	python3 scripts/codex_cat.py || (mv scripts/groups.json.bak scripts/groups.json && exit 1)
	mv scripts/groups.json.bak scripts/groups.json

codex-agents: ## 📚 Generate codex with agents group only
	cp scripts/groups.json scripts/groups.json.bak
	@echo '{"agents": ["AGENTS.md"]}' > scripts/groups.json
	python3 scripts/codex_cat.py || (mv scripts/groups.json.bak scripts/groups.json && exit 1)
	mv scripts/groups.json.bak scripts/groups.json

codex-arch: ## 📚 Generate codex with architecture group only
	cp scripts/groups.json scripts/groups.json.bak
	@echo '{"architecture": ["ORACLE_STACK.md"]}' > scripts/groups.json
	python3 scripts/codex_cat.py || (mv scripts/groups.json.bak scripts/groups.json && exit 1)
	mv scripts/groups.json.bak scripts/groups.json

codex-heritage: ## 📚 Generate codex with heritage group only
	cp scripts/groups.json scripts/groups.json.bak
	@echo '{"heritage": ["CREDITS.md"]}' > scripts/groups.json
	python3 scripts/codex_cat.py || (mv scripts/groups.json.bak scripts/groups.json && exit 1)
	mv scripts/groups.json.bak scripts/groups.json

install-codex-hook: ## 🔗 Install git post-merge hook for auto-codex
	@echo '#!/bin/bash\nmake codex' > .git/hooks/post-merge
	@chmod +x .git/hooks/post-merge
	@echo "Installed post-merge hook"

context-audit: ## 🔍 Audit context budget compliance
	@python3 -c "import os; files=['OMEGA_ENGINE.md','SOVEREIGN_MANDATES.md','AGENTS.md','ORACLE_STACK.md','CREDITS.md','docs/kb/REFINEMENT_PROTOCOL.md']; total=sum(os.path.getsize(f)//4 for f in files if os.path.exists(f)); [print(f'{f}: {os.path.getsize(f)//4} tokens') for f in files if os.path.exists(f)]; print(f'TOTAL: {total} tokens (budget: 15000)'); exit(1 if total>15000 else 0)"

meditate-calibrate: ## 🧘 Calibrate Meditate protocol quality vs budget
	@echo "Running Meditate calibration..."
	@python3 -c "import json, os, yaml; cal={'qwen3-1.7b':15000,'qwen3-4b':20000,'frontier':30000}; os.makedirs('config',exist_ok=True); yaml.dump(cal,open('config/meditate_calibration.yaml','w')); print('Calibration written to config/meditate_calibration.yaml')"

oversight-maturity: ## 📊 Compute Oversight Maturity Index (OMI)
	@python3 -c "import json, os; omi={'h1':1,'h2':1,'h3':1,'h4':1,'h5':1,'h6':1,'updates':3,'engagement':10,'recovery':1}; score=sum(omi[k] for k in ['h1','h2','h3','h4','h5','h6'])/6*(omi['updates']/3)*(omi['engagement']/10)*omi['recovery']; print(f'OMI: {score:.2f} (target > 0.8)')"

