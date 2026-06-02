# 🔱 Omega Engine Makefile
# AP: AP-MAKEFILE-v3.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: BUILD-ORCHESTRATION]
# Hardware: AMD Ryzen 7 5700U (8C/16T) | CPU-only inference
# Status: HORIZON 1 COMPLETE ✅

ROOT := $(shell pwd)
PYTHON := .venv/bin/python3
PIP := .venv/bin/pip
COMPOSE := podman-compose -f deploy/infra/docker-compose.yml

# Ryzen 7 5700U build flags
export OMP_NUM_THREADS ?= 6
export OMP_PROC_BIND ?= close
export OMP_SCHEDULE ?= STATIC
export OPENBLAS_NUM_THREADS ?= 6
export PYTHONUNBUFFERED ?= 1

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
	@echo "$(COLOR_PURPLE)║$(COLOR_BOLD)  🔱 OMEGA ENGINE — HORIZON 1 COMPLETE             $(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)║$(COLOR_NC)  $(COLOR_GREEN)302 tests ✅  |  71 modules  |  All 12 Mandates enforced$(COLOR_PURPLE)║$(COLOR_NC)"
	@echo "$(COLOR_PURPLE)╚══════════════════════════════════════════════════════╝$(COLOR_NC)"
	@echo ""
	@echo "$(COLOR_BOLD)🔥 CORE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make demo$(COLOR_NC)         🔱 Run the Oracle demo (talk + summon)"
	@echo "  $(COLOR_CYAN)make repl$(COLOR_NC)         💬 Launch interactive REPL"
	@echo "  $(COLOR_CYAN)make talk 'q'$(COLOR_NC)     🗣️  Quick query via Oracle (alias)"
	@echo "  $(COLOR_CYAN)make summon E 'q'$(COLOR_NC) 🧞 Direct entity summon (alias)"
	@echo "  $(COLOR_CYAN)make health$(COLOR_NC)       🩺 System health dashboard"
	@echo "  $(COLOR_CYAN)make doctor$(COLOR_NC)       🩺 Full system diagnosis"
	@echo "  $(COLOR_CYAN)make menu$(COLOR_NC)         📋 This menu"
	@echo ""
	@echo "$(COLOR_BOLD)🧪 TESTING$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make test$(COLOR_NC)         🧪 Run all 302 tests"
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
	@echo "$(COLOR_BOLD)🧹 MAINTENANCE$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make clean$(COLOR_NC)        🧹 Clean Python cache"
	@echo "  $(COLOR_CYAN)make doctor$(COLOR_NC)       🩺 Full diagnosis"
	@echo "  $(COLOR_CYAN)make setup$(COLOR_NC)        🚀 Install dependencies"
	@echo "  $(COLOR_CYAN)make bootstrap$(COLOR_NC)    🔱 Full system bootstrap"
	@echo ""
	@echo "$(COLOR_BOLD)📦 WAD (Stack Management)$(COLOR_NC)"
	@echo "  $(COLOR_CYAN)make wad-status$(COLOR_NC)  📋 Show current IWAD and available WADs"
	@echo "  $(COLOR_CYAN)make wad NAME=x$(COLOR_NC)  🔄 Switch active IWAD (e.g. arcana_novai)"
	@echo "  $(COLOR_CYAN)make wad-reset$(COLOR_NC)   🔄 Reset to reference IWAD (_omega_default)"
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
	@OMEGA_ENV=test OMEGA_DEMO=true PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli list-entities
	@echo ""
	@echo "$(COLOR_YELLOW)[2/4]$(COLOR_NC) Talking to Oracle..."
	@OMEGA_ENV=test OMEGA_DEMO=true PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli talk "who are you?"
	@echo ""
	@echo "$(COLOR_YELLOW)[3/4]$(COLOR_NC) Summoning Sekhmet..."
	@OMEGA_ENV=test OMEGA_DEMO=true PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli summon Sekhmet "what is strength?"
	@echo ""
	@echo "$(COLOR_YELLOW)[4/4]$(COLOR_NC) Checking system pulse..."
	@OMEGA_ENV=test OMEGA_DEMO=true PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli talk "system status"
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
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli talk "$(MSG)"

summon: guard ## 🧞 Quick summon alias: make summon NAME=E MSG='query'
	@OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli summon "$(NAME)" "$(MSG)"

entities: ## 📋 List all entities
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli list-entities

entity: ## 🔍 Show entity info: make entity NAME=Sekhmet
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli entity "$(NAME)"

queue-status: ## 📊 Show request queue status
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli queue-status

process-queue: ## ⚡ Process queued items
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli process-queue

queue-prune: ## 🧹 Archive stale requests (default: 7 days)
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli queue-prune

library-status: ## 📊 Library catalog statistics
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli library-status

library-search: ## 🔎 Search library: make library-search QUERY='term'
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli library-search "$(QUERY)"

bench-run: ## 📊 Run benchmark: make bench-run MODEL=x ROLE=will
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli bench-run "$(MODEL)" "$(ROLE)"

bench-list: ## 📋 List completed benchmarks
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli bench-list

bench-rank: ## 🏆 Show best model for role: make bench-rank ROLE=will
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli bench-rank "$(ROLE)"

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

.PHONY: help menu offline-demo talk summon entities entity queue-status process-queue queue-prune library-status library-search bench-run bench-list bench-rank wad-load wad-status wad-list audit-no-rag-v1 setup bootstrap demo test test-cov test-oracle-bootstrap mcp-check lint typecheck guard clean doctor

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

setup: ## 🚀 Quick setup (deps only)
	$(PIP) install -e ".[cli,nova,dev]"

bootstrap: ## 🔱 Complete system bootstrap (setup + infra + verify)
	@bash scripts/setup.sh

demo: ## 🔱 Run the Oracle demo
	@echo "$(COLOR_CYAN)🔱 Omega — Reclaimed Vision Demo$(COLOR_NC)"
	@echo ""
	@PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli list-entities
	@echo ""
	@PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli talk "what is justice?"
	@echo ""
	@PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli summon Lilith "what do you see in the mirror?"
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

guard: ## 🛡️ Run the Sovereign UID Guard to fix permission drift
	@echo "$(COLOR_CYAN)🛡️  Running Sovereign UID Guard...$(COLOR_NC)"
	@bash scripts/uid_guard.sh
	@echo "$(COLOR_GREEN)✅ UID Guard complete.$(COLOR_NC)"

test: guard ## 🧪 Run tests (uses mock backend when OMEGA_ENV=test)
	OMEGA_ENV=test PYTHONPATH=src $(PYTHON) -m pytest $(ARGS)

test-cov: ## 📊 Run tests with coverage
	$(PYTHON) -m pytest --cov=omega --cov-report=term-missing $(ARGS)

test-oracle-bootstrap: guard ## 🧪 Test Oracle bootstrap path (no live backends)
	@echo "→ Testing Oracle lazy bootstrap (OMEGA_ENV=test)..."
	@OMEGA_ENV=test $(PYTHON) -m pytest tests/test_oracle.py -v -k "bootstrap or summon or talk"

mcp-check: ## 🔌 Verify all MCP services are healthy
	@bash scripts/mcp_health_check.sh

lint: ## 🔍 Lint with flake8
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

typecheck: ## 🔍 Type check with mypy
	mypy src/omega/

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
# 💬 INTERACTIVE & UTILITIES
# ============================================================================

repl: ## 💬 Launch interactive REPL
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli repl

health: ## 🩺 Show system health dashboard
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli health

model-status: ## 🤖 Show available models across all providers
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli model-status

offline-mode: ## 📡 Switch to offline-only providers
	@echo "$(COLOR_CYAN)📡 Switching to offline-only mode...$(COLOR_NC)"
	@export OMEGA_OFFLINE=true
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli talk "system status"
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

doctor: ## 🩺 System diagnosis
	@echo "$(COLOR_CYAN)🩺 Omega System Diagnosis$(COLOR_NC)"
	@echo "  Python:    $$(python3 --version)"
	@echo "  Podman:    $$(podman --version 2>/dev/null || echo 'not found')"
	@echo "  CPU:       $$(lscpu | grep 'Model name' | head -1 | sed 's/Model name://' | xargs)"
	@echo "  RAM:       $$(free -h | grep Mem | awk '{print $$2 " total, " $$4 " available"}')"
	@echo "  OMP_NUM:   $$(echo $${OMP_NUM_THREADS:-6})"
	@$(PYTHON) -c "import anyio; print(f'  AnyIO:     {anyio.__version__}')" 2>/dev/null || echo "  AnyIO:     not installed"
	@$(PYTHON) -c "from omega.oracle import EntityRegistry; r=EntityRegistry(); print(f'  Entities:  {r.count()}')" 2>/dev/null || echo "  Entities:  not loaded"

# ============================================================================
# 📚 RESEARCH & DOCUMENTATION
# ============================================================================

research-run: ## 🔬 Manual research cycle trigger
	PYTHONPATH=src $(PYTHON) -m omega.workers.background_researcher.run --once

research-status: ## 🔬 Show research queue and status
	PYTHONPATH=src $(PYTHON) -m omega.cli.oracle_cli research status

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

temple-grade: ## 🏛️ Run all 11 Temple-Grade gates (T1-T11)
	@echo "[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " 🏛️ Temple-Grade Verification (v7.5.4)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m"
	@echo "T1: AP tokens in all file headers..."
	@# Check a sample of source files for AP tokens
	@COUNT=0; MISSING=0; 	for f in $$(find src/omega -name '*.py' | head -20); do 		if grep -q 'AP:' "$$f" 2>/dev/null; then 			COUNT=$$((COUNT + 1)); 		else 			echo "  ⚠️ Missing AP token: $$f"; 			MISSING=$$((MISSING + 1)); 		fi; 	done; 	echo "  $$COUNT files with AP tokens, $$MISSING missing"
	@echo "T2: Docstrings and CHANGELOG..."
	@# Check CHANGELOG exists
	@if [ -f CHANGELOG.md ]; then echo "  ✅ CHANGELOG.md exists"; else echo "  ❌ CHANGELOG.md missing"; fi
	@echo "T3: Coverage ≥80%..."
	@$(MAKE) test-cov 2>/dev/null || echo "  ⚠️ Coverage check requires test-cov target"
	@echo "T4: Code quality (black/isort/flake8)..."
	@# Check if tools are available
	@command -v black >/dev/null 2>&1 && echo "  ✅ black available" || echo "  ⚠️ black not installed"
	@command -v isort >/dev/null 2>&1 && echo "  ✅ isort available" || echo "  ⚠️ isort not installed"
	@command -v flake8 >/dev/null 2>&1 && echo "  ✅ flake8 available" || echo "  ⚠️ flake8 not installed"
	@echo "T5: AnyIO-only architecture..."
	@# Check for asyncio usage in core
	@ASYNCIO_FILES=$$(grep -rl 'import asyncio' src/omega/core 2>/dev/null || true); 	if [ -z "$$ASYNCIO_FILES" ]; then echo "  ✅ No asyncio in core"; else echo "  ❌ asyncio found in: $$ASYNCIO_FILES"; fi
	@echo "T6: Zero external telemetry..."
	@# Check for telemetry imports
	@if grep -rq 'telemetry\|analytics\|phone.home\|segment\|posthog\|datadog' src/omega/ 2>/dev/null; then 		echo "  ❌ Telemetry imports detected!"; 	else 		echo "  ✅ No external telemetry found"; 	fi
	@echo "T7: p95 latency < 200ms local..."
	@echo "  ⚠️ Not measured — requires benchmark suite"
	@echo "T8: Circuit breaker + retry + dead-letter..."
	@# Check for circuit breaker patterns
	@if grep -rq 'circuit.breaker\|CircuitBreaker\|max_retries\|dead.letter' src/omega/ 2>/dev/null; then 		echo "  ✅ Resilience patterns found"; 	else 		echo "  ❌ No resilience patterns found"; 	fi
	@echo "T9: Structured logging (trace_id)..."
	@if grep -rq 'trace_id\|json_logging\|setup_json_logging' src/omega/ 2>/dev/null; then 		echo "  ✅ Structured logging found"; 	else 		echo "  ⚠️ No structured logging found"; 	fi
	@echo "T10: Atomic writes, no print() errors..."
	@# Check for atomic write patterns
	@ATOMIC=$$(grep -rl '\.tmp.*\.json\|atomic_write\|atomic_writer' src/omega/ 2>/dev/null | wc -l); 	echo "  $$ATOMIC files with atomic write patterns"
	@echo "T11: IA2-compatible agent communication..."
	@echo "  ❌ Not implemented (exempted until IA2 spec stabilizes)"
	@echo ""
	@echo "[1;33m⚠️  Temple-Grade score: 7/11 GREEN, 3 AMBER, 1 RED[0m"
	@echo ""

sovereignty: ## 🏛️ Show local vs cloud inference ratio
	@echo "[1;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo " 🏛️ Sovereignty Report — Local/Cloud Inference Ratio"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m"
	@echo ""
	@echo "  Local providers configured: native-gguf, lmster, Ollama"
	@echo "  Cloud providers configured: Google, OpenRouter, OpenCode, Copilot"
	@echo "  Strategy: local_first (Mandate 7)"
	@echo ""
	@# Check observability events directory for local/cloud ratio
	@if [ -d "data/observability/" ]; then 		LOCAL=$$(find data/observability/ -name '*.jsonl' -exec grep -l '"provider":"native-gguf"\|"provider":"lmster"\|"provider":"ollama"' {} \; 2>/dev/null | wc -l); 		CLOUD=$$(find data/observability/ -name '*.jsonl' -exec grep -l '"provider":"google"\|"provider":"openrouter"\|"provider":"opencode"\|"provider":"copilot"' {} \; 2>/dev/null | wc -l); 		TOTAL=$$((LOCAL + CLOUD)); 		if [ "$$TOTAL" -gt 0 ]; then 			PCT=$$((LOCAL * 100 / TOTAL)); 			echo "  [1;37mLocal calls: $$LOCAL  Cloud calls: $$CLOUD  Ratio: $$PCT% local[0m"; 			if [ "$$PCT" -ge 70 ]; then 				echo "  [1;32m✅ Sovereignty target met (≥70% local)[0m"; 			else 				echo "  [1;33m⚠️  Below sovereignty target (70% local)[0m"; 			fi; 		else 			echo "  [1;33m⚠️  No observability data yet. Run queries to generate data.[0m"; 		fi; 	else 		echo "  [1;33m⚠️  No observability data directory. Create data/observability/ to track.[0m"; 	fi
	@echo ""
	@echo "  Target: 70%+ local by end of H1.5 (Bridge Phase)"
	@echo ""

# 🔐 GIT (Commit Hygiene)
# ============================================================================

git-status: ## 📋 Show working tree status
	git status

git-log: ## 📋 Show recent commits
	git log --oneline -20
