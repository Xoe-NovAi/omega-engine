#!/usr/bin/env bash
# probe_free_models.sh — Periodic availability probe for free OpenRouter models
# Usage: run via cron every 30 min; logs to data/metrics/free_model_probes.jsonl
# Probes: GLM-5.2 (free), MiniMax M3 (free), MiMo V2.5 (OpenCode Zen)
# Outputs: JSONL with timestamp, model, success, latency_ms, http_status, rate_limit headers

set -euo pipefail

LOG_DIR="${HOME}/Documents/Xoe-NovAi/omega-engine/data/metrics"
LOG_FILE="${LOG_DIR}/free_model_probes.jsonl"
OPENROUTER_KEY="${OPENROUTER_API_KEY:-}"

# Read key from auth.json if not in env
if [[ -z "$OPENROUTER_KEY" ]]; then
    AUTH_FILE="${HOME}/.local/share/opencode/auth.json"
    if [[ -f "$AUTH_FILE" ]]; then
        OPENROUTER_KEY=$(python3 -c "
import json, sys
with open('$AUTH_FILE') as f:
    d = json.load(f)
print(d.get('openrouter', {}).get('apiKey', ''))
" 2>/dev/null || echo "")
    fi
fi

mkdir -p "$LOG_DIR"

probe_model() {
    local model_id="$1"
    local label="$2"
    local start_ms=$(date +%s%3N)
    local http_status=""
    local body=""
    
    if [[ -n "$OPENROUTER_KEY" ]]; then
        # Non-streaming probe: single-turn, max 32 tokens
        response=$(curl -s -w "\n%{http_code}" \
            --max-time 30 \
            -X POST "https://openrouter.ai/api/v1/chat/completions" \
            -H "Authorization: Bearer $OPENROUTER_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"model\": \"$model_id\",
                \"messages\": [{\"role\": \"user\", \"content\": \"Reply with exactly: PING_OK\"}],
                \"max_tokens\": 32,
                \"temperature\": 0
            }" 2>/dev/null) || true
        
        http_status=$(echo "$response" | tail -1)
        body=$(echo "$response" | sed '$d')
    else
        http_status="NO_KEY"
        body='{"error": "no OpenRouter API key found"}'
    fi
    
    local end_ms=$(date +%s%3N)
    local latency_ms=$((end_ms - start_ms))
    
    # Extract rate-limit headers from response (if available)
    local rate_limit_remaining=""
    local rate_limit_limit=""
    
    # Parse JSON body for error message
    local error_msg=""
    if [[ "$http_status" != "200" ]]; then
        error_msg=$(echo "$body" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    e = d.get('error', {})
    if isinstance(e, dict):
        print(e.get('message', str(e)))
    else:
        print(str(e))
except:
    print('parse_error')
" 2>/dev/null || echo "parse_error")
    fi
    
    # Write JSONL
    python3 -c "
import json, sys
from datetime import datetime, timezone
print(json.dumps({
    'ts': datetime.now(timezone.utc).isoformat(),
    'model': '$model_id',
    'label': '$label',
    'http_status': int('$http_status') if '$http_status'.isdigit() else '$http_status',
    'success': '$http_status' == '200',
    'latency_ms': $latency_ms,
    'error': '''$error_msg'''[:200] if '$http_status' != '200' else None
}))
" >> "$LOG_FILE"
    
    echo "[$label] $model_id → HTTP $http_status (${latency_ms}ms) $([ "$http_status" = "200" ] && echo "✅" || echo "❌ $error_msg")"
}

echo "=== Free Model Probe $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

# Probe 1: GLM-5.2 free
probe_model "z-ai/glm-5.2:free" "glm52"

# Probe 2: MiniMax M3 free
probe_model "minimax/minimax-m3:free" "minimax_m3"

# Probe 3: Nemotron 3 Ultra free (control — known stable)
probe_model "nvidia/nemotron-3-ultra-free" "nemotron_ctrl"

echo ""
echo "Log: $LOG_FILE ($(wc -l < "$LOG_FILE") entries)"
echo "=== Probe complete ==="
