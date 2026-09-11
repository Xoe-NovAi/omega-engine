# ============================================================================
# Omega Engine Alpha — Local AI Harness
# ============================================================================
# Makefile for Ollama-powered local AI on ASUS Expertbook
# i7-13620H (16 cores) | 16GB DDR5 | 512GB NVMe | CPU-only
#
# Usage:  make help
# ============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ──────────────────────────────────────────────────────────────────────────────
# Hardware Profile
# ──────────────────────────────────────────────────────────────────────────────
HOSTNAME    := $(shell hostname)
CORES       := $(shell nproc 2>/dev/null || echo 8)
RAM_GB      := $(shell free -g | awk '/^Mem:/{print int($$2)}')
OLLAMA_HOST := http://localhost:11434
API_KEY     := ollama
# Open WebUI secret (persists login sessions across redeploys).
# Read from .env.ollama if present, else auto-generate a stable value.
WEBUI_TAG := v0.11.3
WEBUI_SECRET_KEY := $(shell grep -E '^WEBUI_SECRET_KEY=' .env.ollama 2>/dev/null | head -1 | cut -d= -f2)
ifeq ($(strip $(WEBUI_SECRET_KEY)),)
WEBUI_SECRET_KEY := $(shell openssl rand -hex 32 2>/dev/null || echo local-dev-key)
endif

# ──────────────────────────────────────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────────────────────────────────────
C_RESET  := \033[0m
C_BOLD   := \033[1m
C_DIM    := \033[2m
C_GREEN  := \033[32m
C_CYAN   := \033[36m
C_YELLOW := \033[33m
C_RED    := \033[31m
C_MAG    := \033[35m
C_BLUE   := \033[34m

# ──────────────────────────────────────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help
	@echo ""
	@echo "$(C_BOLD)$(C_CYAN)╔══════════════════════════════════════════════════════════════╗$(C_RESET)"
	@echo "$(C_BOLD)$(C_CYAN)║         Omega Engine Alpha — Local AI Harness               ║$(C_RESET)"
	@echo "$(C_BOLD)$(C_CYAN)╚══════════════════════════════════════════════════════════════╝$(C_RESET)"
	@echo ""
	@echo "$(C_DIM)Host: $(HOSTNAME) | $(CORES) cores | $(RAM_GB)GB RAM | CPU-only$(C_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(C_GREEN)%-24s$(C_RESET) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# § SERVICE MANAGEMENT
# ============================================================================
.PHONY: start stop restart status logs

start: ## Start Ollama service (systemd)
	@echo "$(C_BOLD)$(C_CYAN)▶ Starting Ollama...$(C_RESET)"
	@sudo systemctl start ollama 2>/dev/null || ollama serve &>/dev/null &
	@sleep 2
	@$(MAKE) --no-print-directory status

stop: ## Stop Ollama service (systemd)
	@echo "$(C_BOLD)$(C_YELLOW)■ Stopping Ollama...$(C_RESET)"
	@sudo systemctl stop ollama 2>/dev/null || pkill -f "ollama serve" 2>/dev/null
	@echo "$(C_GREEN)  Stopped$(C_RESET)"

restart: ## Restart Ollama service (systemd)
	@echo "$(C_BOLD)$(C_CYAN)↻ Restarting Ollama...$(C_RESET)"
	@sudo systemctl restart ollama 2>/dev/null || { $(MAKE) stop && $(MAKE) start; }
	@sleep 2
	@$(MAKE) --no-print-directory status

status: ## Show Ollama server status and loaded models
	@echo "$(C_BOLD)$(C_CYAN)── Ollama Status ──$(C_RESET)"
	@curl -s $(OLLAMA_HOST)/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); models=d.get('models',[]); [print(f'  $(C_GREEN)●$(C_RESET)  {m[\"name\"]:30s} {m[\"size\"]/1e9:.1f}GB') for m in models] if models else print('  $(C_YELLOW)○$(C_RESET)  No models installed')" 2>/dev/null || echo "  $(C_RED)✗$(C_RESET)  Ollama not responding at $(OLLAMA_HOST)"
	@echo ""
	@ollama ps 2>/dev/null || true

logs: ## Tail Ollama service logs
	@sudo journalctl -u ollama -f --no-pager -o cat

# ============================================================================
# § MODEL MANAGEMENT
# ============================================================================
.PHONY: pull list rm pull-core pull-coder pull-reason pull-embed clean-models

pull: ## Pull a model: make pull MODEL=phi4-mini
	@if [ -z "$(MODEL)" ]; then echo "$(C_RED)Usage: make pull MODEL=<name>$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)⬇ Pulling $(MODEL)...$(C_RESET)"
	@ollama pull $(MODEL)

list: ## List all installed models with sizes
	@echo "$(C_BOLD)$(C_CYAN)── Installed Models ──$(C_RESET)"
	@ollama list 2>/dev/null || echo "$(C_YELLOW)  No models installed yet$(C_RESET)"

rm: ## Remove a model: make rm MODEL=phi4-mini
	@if [ -z "$(MODEL)" ]; then echo "$(C_RED)Usage: make rm MODEL=<name>$(C_RESET)"; exit 1; fi
	@ollama rm $(MODEL)

pull-core: ## Pull essential models (phi4-mini + embedding)
	@echo "$(C_BOLD)$(C_CYAN)⬇ Pulling core models...$(C_RESET)"
	@ollama pull phi4-mini
	@ollama pull nomic-embed-text
	@echo "$(C_GREEN)  ✓ Core models ready$(C_RESET)"

pull-coder: ## Pull coding models (qwen2.5-coder)
	@echo "$(C_BOLD)$(C_CYAN)⬇ Pulling coder models...$(C_RESET)"
	@ollama pull qwen2.5-coder:7b
	@echo "$(C_GREEN)  ✓ Coder model ready$(C_RESET)"

pull-reason: ## Pull reasoning model (deepseek-r1)
	@echo "$(C_BOLD)$(C_CYAN)⬇ Pulling reasoning model...$(C_RESET)"
	@ollama pull deepseek-r1:8b
	@echo "$(C_GREEN)  ✓ Reasoning model ready$(C_RESET)"

pull-embed: ## Pull embedding model for RAG
	@echo "$(C_BOLD)$(C_CYAN)⬇ Pulling embedding model...$(C_RESET)"
	@ollama pull nomic-embed-text
	@echo "$(C_GREEN)  ✓ Embedding model ready$(C_RESET)"

clean-models: ## Remove all installed models
	@echo "$(C_RED)⚠ This removes ALL models. Press Ctrl+C to cancel, Enter to continue.$(C_RESET)"
	@read _confirm
	@ollama list 2>/dev/null | tail -n +2 | awk '{print $$1}' | xargs -r -I{} ollama rm {}
	@echo "$(C_GREEN)  ✓ All models removed$(C_RESET)"

# ============================================================================
# § QUICK CHAT
# ============================================================================
.PHONY: chat chat-fast chat-coder chat-reason

chat: ## Interactive chat: make chat MODEL=phi4-mini
	@ollama run $(or $(MODEL),phi4-mini)

chat-fast: ## Quick chat with fastest model (phi4-mini)
	@ollama run phi4-mini

chat-coder: ## Chat with coding model (qwen2.5-coder)
	@ollama run qwen2.5-coder:7b

chat-reason: ## Chat with reasoning model (deepseek-r1)
	@ollama run deepseek-r1:8b

# ============================================================================
# § API TESTING
# ============================================================================
.PHONY: api-test api-generate api-chat api-embed api-models api-stream

api-test: ## Quick API health check
	@echo "$(C_BOLD)$(C_CYAN)── API Health ──$(C_RESET)"
	@curl -s $(OLLAMA_HOST) | head -1
	@echo ""

api-generate: ## Test generate endpoint: make api-generate PROMPT="Hello"
	@curl -s $(OLLAMA_HOST)/api/generate \
		-d '{"model":"$(or $(MODEL),phi4-mini)","prompt":"$(or $(PROMPT),Say hello in one sentence.)","stream":false}' \
		| python3 -m json.tool 2>/dev/null || echo "$(C_YELLOW)  Ensure model is pulled first$(C_RESET)"

api-chat: ## Test chat endpoint: make api-chat PROMPT="Hello"
	@curl -s $(OLLAMA_HOST)/api/chat \
		-d '{"model":"$(or $(MODEL),phi4-mini)","messages":[{"role":"user","content":"$(or $(PROMPT),Hello, who are you?)"}],"stream":false}' \
		| python3 -m json.tool 2>/dev/null || echo "$(C_YELLOW)  Ensure model is pulled first$(C_RESET)"

api-embed: ## Test embeddings endpoint: make api-embed TEXT="Hello world"
	@curl -s $(OLLAMA_HOST)/api/embeddings \
		-d '{"model":"nomic-embed-text","prompt":"$(or $(TEXT),Hello world)"}' \
		| python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Vector dimension: {len(d[\"embedding\"])}')" 2>/dev/null || echo "$(C_YELLOW)  Ensure nomic-embed-text is pulled$(C_RESET)"

api-models: ## List models via API
	@curl -s $(OLLAMA_HOST)/api/tags | python3 -m json.tool 2>/dev/null

api-stream: ## Test streaming response: make api-stream PROMPT="Tell me a joke"
	@curl -s $(OLLAMA_HOST)/api/generate \
		-d '{"model":"$(or $(MODEL),phi4-mini)","prompt":"$(or $(PROMPT),Tell me a short joke.)","stream":true}' \
		| python3 -c "import sys,json; [print(json.loads(l).get('response',''),end='',flush=True) for l in sys.stdin if l.strip()]; print()"

# ============================================================================
# § CUSTOM MODELS (Modelfiles)
# ============================================================================
.PHONY: create-admin create-coder create-summarizer create-json create-modelfile list-modelfiles

create-admin: ## Create linux-admin custom model
	@if [ ! -f .modelfiles/Modelfile.linux-admin ]; then echo "$(C_RED)Missing .modelfiles/Modelfile.linux-admin$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)◆ Creating linux-admin...$(C_RESET)"
	@ollama create linux-admin -f .modelfiles/Modelfile.linux-admin
	@echo "$(C_GREEN)  ✓ linux-admin ready — run: make chat MODEL=linux-admin$(C_RESET)"

create-coder: ## Create code-reviewer custom model
	@if [ ! -f .modelfiles/Modelfile.code-reviewer ]; then echo "$(C_RED)Missing .modelfiles/Modelfile.code-reviewer$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)◆ Creating code-reviewer...$(C_RESET)"
	@ollama create code-reviewer -f .modelfiles/Modelfile.code-reviewer
	@echo "$(C_GREEN)  ✓ code-reviewer ready — run: make chat MODEL=code-reviewer$(C_RESET)"

create-summarizer: ## Create document summarizer custom model
	@if [ ! -f .modelfiles/Modelfile.summarizer ]; then echo "$(C_RED)Missing .modelfiles/Modelfile.summarizer$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)◆ Creating summarizer...$(C_RESET)"
	@ollama create summarizer -f .modelfiles/Modelfile.summarizer
	@echo "$(C_GREEN)  ✓ summarizer ready — run: make chat MODEL=summarizer$(C_RESET)"

create-json: ## Create JSON-only output model
	@if [ ! -f .modelfiles/Modelfile.json-extractor ]; then echo "$(C_RED)Missing .modelfiles/Modelfile.json-extractor$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)◆ Creating json-extractor...$(C_RESET)"
	@ollama create json-extractor -f .modelfiles/Modelfile.json-extractor
	@echo "$(C_GREEN)  ✓ json-extractor ready$(C_RESET)"

create-modelfile: ## Create model from .modelfiles/<name>: make create-modelfile NAME=my-model
	@if [ -z "$(NAME)" ]; then echo "$(C_RED)Usage: make create-modelfile NAME=<model-name>$(C_RESET)"; exit 1; fi
	@ollama create $(NAME) -f .modelfiles/Modelfile.$(NAME)
	@echo "$(C_GREEN)  ✓ $(NAME) created$(C_RESET)"

list-modelfiles: ## Show all custom Modelfiles
	@echo "$(C_BOLD)$(C_CYAN)── Custom Modelfiles ──$(C_RESET)"
	@ls -la .modelfiles/Modelfile.* 2>/dev/null || echo "  $(C_YELLOW)No custom Modelfiles yet$(C_RESET)"

# ============================================================================
# § ENVIRONMENT CONFIGURATION
# ============================================================================
.PHONY: env-setup env-show env-apply env-revert

# CPU/env profile lives in .env.ollama — single source of truth.
ENV_FILE ?= .env.ollama

env-setup: ## Apply tuned CPU profile from .env.ollama
	@$(MAKE) env-apply FILE=$(ENV_FILE)

env-show: ## Show current Ollama environment variables
	@echo "$(C_BOLD)$(C_CYAN)── Ollama Environment ──$(C_RESET)"
	@sudo systemctl show ollama --property=Environment 2>/dev/null | sed 's/^Environment=//' | tr ' ' '\n' | grep -E 'OLLAMA_|WEBUI_' | sort || \
		echo "  $(C_YELLOW)Could not read systemd env — Ollama may be running without systemd$(C_RESET)"

env-apply: ## Apply env from file: make env-apply FILE=.env.ollama
	@if [ ! -f "$(or $(FILE),$(ENV_FILE))" ]; then echo "$(C_RED)Missing $(or $(FILE),$(ENV_FILE)) — create it or run: make env-apply FILE=<path>$(C_RESET)"; exit 1; fi
	@echo "$(C_BOLD)$(C_CYAN)◆ Applying environment from $(or $(FILE),$(ENV_FILE))...$(C_RESET)"
	@sudo mkdir -p /etc/systemd/system/ollama.service.d
	@echo "[Service]" | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
	@grep -v '^#' $(or $(FILE),$(ENV_FILE)) | grep -v '^$$' | sed 's/^/Environment=/' | sudo tee -a /etc/systemd/system/ollama.service.d/override.conf > /dev/null
	@echo "AllowedCPUs=0-11" | sudo tee -a /etc/systemd/system/ollama.service.d/override.conf > /dev/null
	@sudo systemctl daemon-reload
	@sudo systemctl restart ollama
	@echo "$(C_GREEN)  ✓ Environment applied (P-cores 0-11, E-cores excluded)$(C_RESET)"

env-revert: ## Revert to default Ollama environment
	@sudo rm -f /etc/systemd/system/ollama.service.d/override.conf
	@sudo systemctl daemon-reload
	@sudo systemctl restart ollama
	@echo "$(C_GREEN)  ✓ Reverted to defaults$(C_RESET)"

# ============================================================================
# § MONITORING & DEBUGGING
# ============================================================================
.PHONY: monitor ram usage inspect debug

monitor: ## Watch RAM usage and loaded models in real-time
	@echo "$(C_BOLD)$(C_CYAN)── Live Monitor (Ctrl+C to stop) ──$(C_RESET)"
	@watch -n 2 'echo "── RAM ──"; free -h | head -2; echo ""; echo "── Ollama Models ──"; ollama ps 2>/dev/null || echo "not running"'

ram: ## Show RAM usage breakdown
	@echo "$(C_BOLD)$(C_CYAN)── Memory ──$(C_RESET)"
	@free -h
	@echo ""
	@echo "$(C_DIM)  Ollama default: auto-unloads after 5m idle$(C_RESET)"
	@echo "$(C_DIM)  To force unload: curl $(OLLAMA_HOST)/api/generate -d '"'"'{"model":"phi4-mini","keep_alive":0}'"'"'$(C_RESET)"

usage: ## Show disk usage of Ollama models
	@echo "$(C_BOLD)$(C_CYAN)── Model Disk Usage ──$(C_RESET)"
	@sudo du -sh /usr/share/ollama/.ollama/models 2>/dev/null || echo "  $(C_YELLOW)Could not determine model size$(C_RESET)"
	@echo ""
	@df -h / | tail -1 | awk '{print "  Disk: "$$4" free of "$$2" ("$$5" used)"}'

inspect: ## Inspect a model's config: make inspect MODEL=phi4-mini
	@echo "$(C_BOLD)$(C_CYAN)── Model: $(or $(MODEL),phi4-mini) ──$(C_RESET)"
	@ollama show $(or $(MODEL),phi4-mini) 2>/dev/null
	@echo ""
	@echo "$(C_DIM)── Modelfile ──$(C_RESET)"
	@ollama show $(or $(MODEL),phi4-mini) --modelfile 2>/dev/null

debug: ## Run Ollama with debug logging
	@echo "$(C_BOLD)$(C_YELLOW)⚠ Debug mode — run in separate terminal$(C_RESET)"
	@OLLAMA_DEBUG=1 ollama serve

# ============================================================================
# § OPEN WEBUI (Browser Interface)
# ============================================================================
.PHONY: webui webui-up webui-down webui-logs webui-status

webui-up: ## Start Open WebUI (ChatGPT-style browser interface)
	@echo "$(C_BOLD)$(C_CYAN)◆ Starting Open WebUI...$(C_RESET)"
	@docker run -d \
		-p 3000:8080 \
		--add-host=host.docker.internal:host-gateway \
		-e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
		-e WEBUI_SECRET_KEY=$(WEBUI_SECRET_KEY) \
		-v open-webui:/app/backend/data \
		--name open-webui \
		--restart unless-stopped \
		ghcr.io/open-webui/open-webui:$(WEBUI_TAG) 2>/dev/null || \
		docker start open-webui
	@sleep 5
	@echo "$(C_GREEN)  ✓ Open WebUI running at http://localhost:3000$(C_RESET)"
	@echo "  $(C_DIM)Connectivity: relies on OLLAMA_HOST=0.0.0.0 (see .env.ollama) + host-gateway$(C_RESET)"

webui-down: ## Stop Open WebUI
	@docker stop open-webui 2>/dev/null && echo "$(C_GREEN)  ✓ Stopped$(C_RESET)" || echo "$(C_YELLOW)  Not running$(C_RESET)"

webui-logs: ## Tail Open WebUI logs
	@docker logs -f open-webui

webui-status: ## Check Open WebUI status
	@docker ps --filter name=open-webui --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "$(C_YELLOW)  Docker not available$(C_RESET)"

webui: ## Start Open WebUI + ensure Ollama is running
	@$(MAKE) start
	@$(MAKE) webui-up

# ============================================================================
# § PYTHON INTEGRATION
# ============================================================================
.PHONY: python-setup python-test python-chatbot python-rag python-serve

python-setup: ## Install Ollama Python SDK
	@echo "$(C_BOLD)$(C_CYAN)◆ Setting up Python environment...$(C_RESET)"
	@python3 -m venv .venv 2>/dev/null || true
	@.venv/bin/pip install --quiet ollama
	@echo "$(C_GREEN)  ✓ ollama package installed in .venv$(C_RESET)"
	@echo "  $(C_DIM)Activate: source .venv/bin/activate$(C_RESET)"

python-test: ## Test Python Ollama connection
	@.venv/bin/python3 -c "import ollama; print(ollama.list())" 2>/dev/null || \
		echo "$(C_YELLOW)  Run 'make python-setup' first, then pull a model$(C_RESET)"

python-chatbot: ## Launch Python streaming chatbot (requires .venv)
	@.venv/bin/python3 scripts/chatbot.py --model $(or $(MODEL),phi4-mini)

python-rag: ## Quick RAG demo (requires .venv + langchain)
	@.venv/bin/pip install --quiet langchain langchain-ollama langchain-chroma chromadb pypdf 2>/dev/null
	@echo "$(C_BOLD)$(C_CYAN)◆ RAG stack installed. Use in your scripts:${C_RESET}"
	@echo "  $(C_DIM)from langchain_ollama import OllamaEmbeddings, ChatOllama$(C_RESET)"
	@echo "  $(C_DIM)from langchain_chroma import Chroma$(C_RESET)"

python-serve: ## Start a FastAPI server wrapping Ollama (port 8000)
	@.venv/bin/pip install --quiet fastapi uvicorn 2>/dev/null
	@.venv/bin/python3 scripts/serve.py --model $(or $(MODEL),phi4-mini) --port $(or $(PORT),8000)

# ============================================================================
# § BENCHMARKING
# ============================================================================
.PHONY: bench bench-all bench-compare

bench: ## Benchmark a model: make bench MODEL=phi4-mini PROMPTS=5 WARM=1
	@python3 scripts/bench.py --model $(or $(MODEL),phi4-mini) --prompts $(or $(PROMPTS),3) --host $(OLLAMA_HOST) $(if $(WARM),--warm)

bench-all: ## Benchmark all installed models
	@echo "$(C_BOLD)$(C_CYAN)── Benchmarking All Models ──$(C_RESET)"
	@ollama list 2>/dev/null | tail -n +2 | awk '{print $$1}' | while read m; do \
		echo ""; \
		echo "$(C_BOLD)  Model: $$m$(C_RESET)"; \
		$(MAKE) --no-print-directory bench MODEL=$$m PROMPTS=2; \
	done

bench-compare: ## Compare phi4-mini vs qwen2.5-coder vs deepseek-r1
	@echo "$(C_BOLD)$(C_CYAN)── Head-to-Head Benchmark ──$(C_RESET)"
	@for m in phi4-mini qwen2.5-coder:7b deepseek-r1:8b; do \
		echo ""; \
		echo "$(C_BOLD)  ┌─ $$m ─┐$(C_RESET)"; \
		$(MAKE) --no-print-directory bench MODEL=$$m PROMPTS=2; \
	done

# ============================================================================
# § GNOSIS LOCK PROTOCOL (context-compaction safety)
# ============================================================================
.PHONY: gnosis-lock gnosis-stats

GNOSIS_RITUAL    := scripts/compaction/pre_compaction_ritual.sh
GNOSIS_EVOLUTION := scripts/compaction/evolution_log.py

gnosis-lock: ## Run pre-compaction ritual: make gnosis-lock REASON="why" [ENTITY=... CHANNEL=... PHASE=...]
	@SESSION_ID="session-$$(date -u +%Y-%m-%dT%H-%M-%SZ)" ; \
	REASON="$${REASON:-Manual gnosis lock before compact}" ; \
	ENTITY="$${ENTITY:-build}" ; \
	CHANNEL="$${CHANNEL:-cli}" ; \
	PHASE="$${PHASE:-unset}" ; \
	echo "$(C_CYAN)🔱 Locking gnosis: $$REASON$(C_RESET)" ; \
	echo "$(C_DIM)   Session: $$SESSION_ID | Entity: $$ENTITY | Phase: $$PHASE$(C_RESET)" ; \
	echo "" ; \
	bash "$(GNOSIS_RITUAL)" "$$SESSION_ID" "$$REASON" ; \
	echo "" ; \
	echo "$(C_CYAN)✅ Gnosis locked. Complete the compact INSIDE OpenCode:$(C_RESET)" ; \
	echo "   Switch to your session and type:  /compact $$REASON"

gnosis-stats: ## Show evolution-log stats + recent timeline: make gnosis-stats LIMIT=5
	@python3 "$(GNOSIS_EVOLUTION)" stats
	@echo ""
	@python3 "$(GNOSIS_EVOLUTION)" timeline --limit $(or $(LIMIT),5)

gnosis-leash-status: ## Watchdog: is the automated gnosis-leash plugin alive + clean?
	@python3 scripts/compaction/leash_status.py

# ============================================================================
# § QUICK REFS
# ============================================================================
.PHONY: cheat env-all

cheat: ## Show Ollama quick reference
	@echo "$(C_BOLD)$(C_CYAN)╔══════════════════════════════════════════════════════════════╗$(C_RESET)"
	@echo "$(C_BOLD)$(C_CYAN)║                   Ollama Quick Reference                    ║$(C_RESET)"
	@echo "$(C_BOLD)$(C_CYAN)╚══════════════════════════════════════════════════════════════╝$(C_RESET)"
	@echo ""
	@echo "$(C_BOLD)$(C_GREEN)CLI Commands$(C_RESET)"
	@echo "  ollama run <model>           Pull + chat"
	@echo "  ollama pull <model>          Download model"
	@echo "  ollama list                  List installed models"
	@echo "  ollama ps                    Show loaded models"
	@echo "  ollama show <model> --modelfile   View config"
	@echo "  ollama create <name> -f Modelfile  Create custom model"
	@echo ""
	@echo "$(C_BOLD)$(C_GREEN)Key Parameters$(C_RESET)"
	@echo "  temperature    0.0=focused, 1.0+=creative"
	@echo "  num_ctx        Context window (more RAM = more tokens)"
	@echo "  num_predict    Max output tokens (-1 = unlimited)"
	@echo "  seed           Fixed=reproducible output"
	@echo ""
	@echo "$(C_BOLD)$(C_GREEN)API Endpoints$(C_RESET)"
	@echo "  GET  /                Health check"
	@echo "  POST /api/generate    Single-turn completion"
	@echo "  POST /api/chat        Multi-turn conversation"
	@echo "  POST /api/embeddings  Generate vectors"
	@echo "  GET  /api/tags        List models"
	@echo "  POST /v1/chat/completions  OpenAI-compatible"
	@echo ""
	@echo "$(C_BOLD)$(C_GREEN)Env Variables (systemd override)$(C_RESET)"
	@echo "  OLLAMA_HOST             Bind address (default 127.0.0.1)"
	@echo "  OLLAMA_MODELS           Storage path (default ~/.ollama/models)"
	@echo "  OLLAMA_KEEP_ALIVE       How long to keep model loaded (5m default)"
	@echo "  OLLAMA_NUM_PARALLEL     Concurrent requests (default 1-4)"
	@echo "  OLLAMA_MAX_LOADED_MODELS  Models in RAM at once"
	@echo "  OLLAMA_NUM_THREAD       CPU threads for inference"
	@echo ""
	@echo "$(C_BOLD)$(C_GREEN)Model Sizes (16GB RAM)$(C_RESET)"
	@echo "  3-4B models     2-3GB  → fast, responsive"
	@echo "  7-8B models     4-6GB  → balanced"
	@echo "  12-14B models   8-10GB → tight fit, slower"
	@echo "  16GB+ models    won't fit safely on this machine"
	@echo ""

env-all: ## Show all Ollama env variables with descriptions
	@echo "$(C_BOLD)$(C_CYAN)── All Ollama Environment Variables ──$(C_RESET)"
	@echo ""
	@echo "$(C_BOLD)Networking$(C_RESET)"
	@echo "  OLLAMA_HOST            Bind address (127.0.0.1 / 0.0.0.0)"
	@echo "  OLLAMA_ORIGINS         CORS origins (comma-separated)"
	@echo ""
	@echo "$(C_BOLD)Storage$(C_RESET)"
	@echo "  OLLAMA_MODELS          Model storage path"
	@echo "  OLLAMA_NOPRUNE         Disable automatic cleanup"
	@echo ""
	@echo "$(C_BOLD)Performance$(C_RESET)"
	@echo "  OLLAMA_NUM_PARALLEL    Concurrent request slots (1-N)"
	@echo "  OLLAMA_MAX_LOADED_MODELS  Models kept in memory"
	@echo "  OLLAMA_KEEP_ALIVE      Duration before model unload"
	@echo "  OLLAMA_NUM_THREAD      CPU thread count"
	@echo "  OLLAMA_FLASH_ATTENTION Enable flash attention (GPU)"
	@echo "  OLLAMA_GPU_OVERHEAD    GPU memory reservation (bytes)"
	@echo "  OLLAMA_KV_CACHE_TYPE   KV cache quantization (f16/q8/q4)"
	@echo "  OLLAMA_CONTEXT_LENGTH  Default context window"
	@echo ""
	@echo "$(C_BOLD)GPU$(C_RESET)"
	@echo "  CUDA_VISIBLE_DEVICES   NVIDIA GPU selection"
	@echo "  ROCR_VISIBLE_DEVICES   AMD GPU selection"
	@echo "  OLLAMA_SCHED_SPREAD    Spread layers across GPUs"
	@echo ""
	@echo "$(C_BOLD)Debug$(C_RESET)"
	@echo "  OLLAMA_DEBUG           Verbose debug logging"
	@echo "  OLLAMA_VERBOSE         Request logging"
	@echo "  OLLAMA_NO_CLOUD        Disable cloud features"

# ============================================================================
# § DOCS
# ============================================================================
.PHONY: docs lint lint-async

lint: ## ALL code-quality gates: anyio purity + bare-exception ban + torch ban
	@echo "$(C_BOLD)$(C_CYAN)── Code-quality gates ──$(C_RESET)"
	@python3 scripts/lint_checks.py

docs: ## Validate docs integrity: README links + CODE_QUALITY async gate
	@echo "$(C_BOLD)$(C_CYAN)── Docs integrity check ──$(C_RESET)"
	@echo "$(C_BOLD)README links:$(C_RESET)"
	@for f in README.md docs/GETTING_STARTED.md docs/ARCHITECTURE.md docs/DEVELOPER_GUIDE.md docs/PLUGIN_DEVELOPMENT.md docs/CODE_QUALITY.md docs/WANDERGROUND_SPEC.md docs/SYSTEM_GUIDE.md docs/HARDWARE.md LICENSE CONTRIBUTING.md; do \
		[ -f "$$f" ] && echo "  ✓ $$f" || { echo "  ✗ MISSING: $$f"; exit 1; }; \
	done
	@echo "$(C_BOLD)Markdown headers anchor sanity (README internal links):$(C_RESET)"
	@grep -oE '\]\(#[^)]+' README.md | tr -d '](#' | while read -r h; do \
		[ -n "$$h" ] && { grep -q "## .*$$h" README.md || echo "  ⚠ unverified anchor: #$$h"; }; \
	done || true
	@echo "  docs OK ✓"

lint-async: ## Reject bare asyncio/trio imports in first-party scripts
	@echo "$(C_BOLD)anyio-only gate (absolute anyio full async wiring):$(C_RESET)"
	@hits=$$(grep -rn "^\s*\(import\|from\) \(asyncio\|trio\)\b" scripts/ 2>/dev/null || true); \
	if [ -n "$$hits" ]; then echo "$$hits"; echo "  FAIL: bare asyncio/trio in first-party code — use anyio (CODE_QUALITY.md)"; exit 1; \
	else echo "  ✓ no bare asyncio/trio in scripts/"; fi
