# 🔱 Omega Engine Makefile
# AP: AP-MAKEFILE-v2.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: BUILD-ORCHESTRATION]
# Hardware: AMD Ryzen 7 5700U (8C/16T) | 16GB RAM | CPU-only inference

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
COLOR_NC := \033[0m

# ============================================================================
# 🚀 CORE COMMANDS
# ============================================================================

.PHONY: help setup bootstrap demo test lint clean

help: ## 📚 Show this help
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  $(COLOR_CYAN)%-20s$(COLOR_NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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
# 🔐 GIT (Commit Hygiene)
# ============================================================================

git-status: ## 📋 Show working tree status
	git status

git-log: ## 📋 Show recent commits
	git log --oneline -20
