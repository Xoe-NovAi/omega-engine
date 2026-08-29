#!/bin/bash
# 🔱 Native GGUF Server Launcher
# AP Token: AP-NATIVE-GGUF-SERVER-v1.0.0
# Starts llama-cpp servers for native-gguf providers
# Ports: 1234 (extractor), 1235 (reasoner)

set -euo pipefail

MODELS_DIR="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}"
EXTRACTOR_MODEL="${MODELS_DIR}/Qwen3-1.7B-Q6_K.gguf"
REASONER_MODEL="${MODELS_DIR}/Qwen3-4B-Thinking-2507-Q4_K_M.gguf"

LOG_DIR="/tmp/native-gguf-logs"
mkdir -p "$LOG_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERR]${NC} $1"; }

# Check models exist
if [[ ! -f "$EXTRACTOR_MODEL" ]]; then
    err "Extractor model not found: $EXTRACTOR_MODEL"
    exit 1
fi
if [[ ! -f "$REASONER_MODEL" ]]; then
    err "Reasoner model not found: $REASONER_MODEL"
    exit 1
fi

info "Models found:"
info "  Extractor: $EXTRACTOR_MODEL"
info "  Reasoner: $REASONER_MODEL"

# Function to start a server
start_server() {
    local port=$1
    local model=$2
    local name=$3
    local log_file="$LOG_DIR/${name}.log"
    local pid_file="$LOG_DIR/${name}.pid"

    # Check if already running
    if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        info "$name already running on port $port (PID: $(cat "$pid_file"))"
        return 0
    fi

    info "Starting $name on port $port..."
    
    # Use the venv python
    source .venv/bin/activate
    
    # RAM-optimized settings per model
    local n_ctx=2048
    local n_batch=256
    local use_mlock="True"
    
    # Reasoner (4B Thinking) needs more context, disable mlock to save RAM
    if [[ "$name" == "reasoner" ]]; then
        n_ctx=4096
        use_mlock="False"
    fi
    
    nohup python3 -m llama_cpp.server \
        --model "$model" \
        --host 127.0.0.1 \
        --port "$port" \
        --n_ctx "$n_ctx" \
        --n_threads 4 \
        --n_batch "$n_batch" \
        --use_mlock "$use_mlock" \
        --verbose false \
        > "$log_file" 2>&1 &
    
    local pid=$!
    echo $pid > "$pid_file"
    
    # Wait for server to be ready
    local retries=30
    while [[ $retries -gt 0 ]]; do
        if curl -s --max-time 2 "http://127.0.0.1:$port/v1/models" >/dev/null 2>&1; then
            info "$name started on port $port (PID: $pid)"
            return 0
        fi
        sleep 1
        ((retries--))
    done
    
    err "$name failed to start on port $port"
    cat "$log_file"
    return 1
}

# Start both servers
start_server 1234 "$EXTRACTOR_MODEL" "extractor"
start_server 1235 "$REASONER_MODEL" "reasoner"

info "All servers started. Logs in $LOG_DIR"
info "Health checks:"
info "  curl http://127.0.0.1:1234/v1/models"
info "  curl http://127.0.0.1:1235/v1/models"