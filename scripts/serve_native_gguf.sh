#!/bin/bash
# 🔱 Native GGUF Server Launcher & Lifecycle Manager
# AP Token: AP-NATIVE-GGUF-SERVER-v1.1.0
# Starts/stops llama-cpp servers for native-gguf providers.
# Ports: 1234 (extractor), 1235 (reasoner)
#
# Subcommands: start (default) | stop | status | restart
#   start    — launch both servers (idempotent; skips already-running)
#   stop     — graceful shutdown of both servers + remove pid files
#   status   — report running state, health, and memory footprint
#   restart  — stop then start
#
# Observability: logs live in data/logs/native-gguf/ (persistent, M8-compliant
# local observability — never external). Lifecycle events appended to
# events.jsonl for traceability. See SOVEREIGN_MANDATES.md §M8 (zero telemetry:
# local observability in data/ is acceptable; external telemetry is not).

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────
MODELS_DIR="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}"
EXTRACTOR_MODEL="${MODELS_DIR}/Qwen3-1.7B-Q6_K.gguf"
REASONER_MODEL="${MODELS_DIR}/Qwen3-4B-Thinking-2507-Q4_K_M.gguf"

# Persistent log location (data/logs/ is the canonical M8 local-observability dir)
LOG_DIR="${OMEGA_LOG_DIR:-data/logs/native-gguf}"
mkdir -p "$LOG_DIR"

EVENTS_FILE="$LOG_DIR/events.jsonl"
READY_RETRIES=90          # 90 x 1s — reasoner (4B Thinking) can take ~45s+ to load
READY_INTERVAL=1

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERR]${NC} $1"; }

# ── Lifecycle event logging (JSONL) ─────────────────────────────────────────
# Append a structured event to events.jsonl. M8-compliant: local only.
log_event() {
    local event="$1"
    local name="$2"
    local detail="${3:-}"
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
    printf '{"ts":"%s","event":"%s","server":"%s","detail":"%s"}\n' \
        "$ts" "$event" "$name" "$detail" >> "$EVENTS_FILE" 2>/dev/null || true
}

# ── Model existence check ───────────────────────────────────────────────────
check_models() {
    local missing=0
    [[ -f "$EXTRACTOR_MODEL" ]] || { err "Extractor model not found: $EXTRACTOR_MODEL"; missing=1; }
    [[ -f "$REASONER_MODEL" ]] || { err "Reasoner model not found: $REASONER_MODEL"; missing=1; }
    if [[ $missing -eq 1 ]]; then
        log_event "error" "all" "model file(s) missing"
        exit 1
    fi
    info "Models found:"
    info "  Extractor: $EXTRACTOR_MODEL"
    info "  Reasoner: $REASONER_MODEL"
}

# ── Start one server ────────────────────────────────────────────────────────
start_server() {
    local port=$1
    local model=$2
    local name=$3
    local log_file="$LOG_DIR/${name}.log"
    local pid_file="$LOG_DIR/${name}.pid"

    # Check if already running (via pid file)
    if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        info "$name already running on port $port (PID: $(cat "$pid_file"))"
        log_event "already_running" "$name" "port=$port pid=$(cat "$pid_file")"
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

    log_event "starting" "$name" "port=$port model=$(basename "$model")"

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

    # Wait for server to be ready (READY_RETRIES x READY_INTERVAL seconds)
    local retries=$READY_RETRIES
    while [[ $retries -gt 0 ]]; do
        if curl -s --max-time 2 "http://127.0.0.1:$port/v1/models" >/dev/null 2>&1; then
            info "$name started on port $port (PID: $pid)"
            log_event "ready" "$name" "port=$port pid=$pid"
            return 0
        fi
        # Early-exit if the process died during load (crash detection)
        if ! kill -0 "$pid" 2>/dev/null; then
            err "$name process died during load (port $port)"
            log_event "crash_on_load" "$name" "port=$port pid=$pid"
            cat "$log_file"
            return 1
        fi
        sleep "$READY_INTERVAL"
        ((retries--))
    done

    err "$name failed to become ready on port $port after ${READY_RETRIES}s"
    log_event "timeout" "$name" "port=$port pid=$pid"
    cat "$log_file"
    return 1
}

# ── Stop one server (graceful then force) ───────────────────────────────────
stop_server() {
    local name=$1
    local port=$2
    local pid_file="$LOG_DIR/${name}.pid"
    local pid=""

    if [[ -f "$pid_file" ]]; then
        pid="$(cat "$pid_file")"
    fi

    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        info "Stopping $name (PID $pid)..."
        log_event "stopping" "$name" "pid=$pid"
        # Graceful SIGTERM first, allow up to 5s, then SIGKILL
        kill "$pid" 2>/dev/null || true
        for _ in 1 2 3 4 5; do
            kill -0 "$pid" 2>/dev/null || break
            sleep 1
        done
        if kill -0 "$pid" 2>/dev/null; then
            warn "$name did not exit gracefully — forcing SIGKILL"
            kill -9 "$pid" 2>/dev/null || true
        fi
        log_event "stopped" "$name" "pid=$pid"
    else
        # Fallback: match by port in case pid file is stale/missing
        local proc
        proc="$(pgrep -f "python3 -m llama_cpp.server.*--port $port" || true)"
        if [[ -n "$proc" ]]; then
            info "Stopping $name (PID $proc, by port $port)..."
            log_event "stopping" "$name" "pid=$proc via-port"
            kill $proc 2>/dev/null || true
            sleep 1
            kill -9 $proc 2>/dev/null || true
            log_event "stopped" "$name" "pid=$proc via-port"
        fi
    fi
    rm -f "$pid_file"
}

# ── Status ──────────────────────────────────────────────────────────────────
status() {
    echo -e "${YELLOW}Native-gguf server status:${NC}"
    for entry in "extractor 1234" "reasoner 1235"; do
        set -- $entry
        local name=$1 port=$2
        local pid_file="$LOG_DIR/${name}.pid"
        local pid="" state="STOPPED"

        if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
            pid="$(cat "$pid_file")"; state="RUNNING"
        else
            local proc
            proc="$(pgrep -f "python3 -m llama_cpp.server.*--port $port" || true)"
            if [[ -n "$proc" ]]; then pid=$proc; state="RUNNING (pid-file stale)"; fi
        fi

        printf "  %-10s port %-4s %-8s PID %s\n" "$name" "$port" "$state" "${pid:--}"
        if [[ "$state" == RUNNING* ]]; then
            local health
            health="$(curl -s --max-time 2 "http://127.0.0.1:$port/v1/models" >/dev/null 2>&1 && echo OK || echo DOWN)"
            echo "      health: $health"
            if [[ -r "/proc/$pid/status" ]]; then
                local rss swap
                rss="$(awk '/VmRSS/{print int($2/1024)}' /proc/$pid/status 2>/dev/null)"
                swap="$(awk '/VmSwap/{print int($2/1024)}' /proc/$pid/status 2>/dev/null)"
                printf "      memory: RSS %s MB  Swap %s MB\n" "${rss:-0}" "${swap:-0}"
            fi
        fi
    done
}

# ── Main dispatch ───────────────────────────────────────────────────────────
CMD="${1:-start}"

case "$CMD" in
    start)
        check_models
        start_server 1234 "$EXTRACTOR_MODEL" "extractor"
        start_server 1235 "$REASONER_MODEL" "reasoner"
        info "All servers started. Logs in $LOG_DIR"
        info "Health checks:"
        info "  curl http://127.0.0.1:1234/v1/models"
        info "  curl http://127.0.0.1:1235/v1/models"
        ;;
    stop)
        stop_server "extractor" 1234
        stop_server "reasoner" 1235
        info "Native-gguf servers stopped; models unloaded from RAM."
        ;;
    restart)
        stop_server "extractor" 1234
        stop_server "reasoner" 1235
        check_models
        start_server 1234 "$EXTRACTOR_MODEL" "extractor"
        start_server 1235 "$REASONER_MODEL" "reasoner"
        info "Native-gguf servers restarted."
        ;;
    status)
        status
        ;;
    *)
        err "Unknown subcommand: $CMD"
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
