#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# probe_free_models.sh — Periodic availability probe for OpenRouter free models
# Version: v3.0 (probe-report-actions-20260827 — Actions 1+2)
# Usage: run via cron every 30 min; logs to data/metrics/free_model_probes.jsonl
# Probes: 16 free tier models (canonical list)
# Outputs: JSONL with ts, model, success, latency_ms, http_status, error,
#          quality_check { valid_json, has_completion, content_length },
#          key_source, key_health, window
#
# Changes from v2.0:
#   - 3-key rotation: try or-key.md → Cline secrets → auth.json; rotate on 401
#   - Pre-flight key health check (1 cheap /auth call per cycle, cached)
#   - Fixed stale model IDs (removed `nvidia/nemotron-3-ultra-free` and
#     `nvidia/nemotron-3-ultra` which returned 401/400)
#   - Quality checks: JSON validity, completion presence, content length
#   - Window field: "off_peak" (00-06 UTC), "moderate" (06-12 UTC),
#     "poor" (12-18 UTC), "worst" (18-24 UTC)
#   - Per-model try up to 2 keys before giving up (transient 401 recovery)

set -uo pipefail

LOG_DIR="${HOME}/Documents/Xoe-NovAi/omega-engine/data/metrics"
LOG_FILE="${LOG_DIR}/free_model_probes.jsonl"
STATE_FILE="${LOG_DIR}/model_state.json"
QUALITY_SUMMARY="${LOG_DIR}/probe_quality_summary.json"

mkdir -p "$LOG_DIR"

# === KEY RESOLUTION (3-key rotation) =========================================
# Returns: "key1:value1|key2:value2|key3:value3" pipe-separated.
# The probe_model function iterates through them on 401 errors.

KEY_OR_FILE="${HOME}/Documents/Xoe-NovAi/omega-engine/or-key.md"
KEY_CLINE_FILE="${HOME}/.cline/data/secrets.json"
KEY_AUTH_FILE="${HOME}/.local/share/opencode/auth.json"

get_keys() {
    local keys=""
    # 1. or-key.md
    if [[ -f "$KEY_OR_FILE" ]]; then
        local k=$(tr -d '[:space:]' < "$KEY_OR_FILE" 2>/dev/null)
        if [[ -n "$k" && "$k" == sk-or-v1-* ]]; then
            keys="${keys}|or_key:${k}"
        fi
    fi
    # 2. Cline secrets
    if [[ -f "$KEY_CLINE_FILE" ]]; then
        local k=$(python3 -c "
import json
try:
    with open('$KEY_CLINE_FILE') as f: d=json.load(f)
    print(d.get('openRouterApiKey',''))
except: pass
" 2>/dev/null)
        if [[ -n "$k" && "$k" == sk-or-v1-* ]]; then
            keys="${keys}|cline:${k}"
        fi
    fi
    # 3. opencode auth.json
    if [[ -f "$KEY_AUTH_FILE" ]]; then
        local k=$(python3 -c "
import json
try:
    with open('$KEY_AUTH_FILE') as f: d=json.load(f)
    print(d.get('openrouter',{}).get('key','') or d.get('openrouter',{}).get('apiKey',''))
except: pass
" 2>/dev/null)
        if [[ -n "$k" && "$k" == sk-or-v1-* ]]; then
            keys="${keys}|auth:${k}"
        fi
    fi
    # Strip leading pipe
    echo "${keys#|}"
}

# === KEY HEALTH CHECK ========================================================
# Pre-flight: send a tiny /api/v1/auth/key + a tiny /chat/completions probe.
# Cached per-run. /auth/key may return 200 for keys that fail inference with
# "User not found" (observed 2026-08-26), so we also test the inference path.
# Returns: "ok:src1,src2" / "inference_only:src1" / "all_unhealthy" / "no_keys"

KEY_HEALTH_FILE="${LOG_DIR}/.key_health_cache"
KEY_HEALTH_TTL=300  # 5 min

check_key_health() {
    local keys=$(get_keys)
    if [[ -z "$keys" ]]; then
        echo "no_keys"
        return 1
    fi
    # Check cache first
    if [[ -f "$KEY_HEALTH_FILE" ]]; then
        local age=$(( $(date +%s) - $(stat -c %Y "$KEY_HEALTH_FILE" 2>/dev/null || echo 0) ))
        if [[ $age -lt $KEY_HEALTH_TTL ]]; then
            cat "$KEY_HEALTH_FILE"
            return 0
        fi
    fi
    # Test each key: /auth/key (passes for valid cred) + /chat/completions
    # with a known-working model (openrouter/free router, near-universal).
    IFS='|' read -ra KEY_ARRAY <<< "$keys"
    local healthy_auth=""
    local healthy_inference=""
    for entry in "${KEY_ARRAY[@]}"; do
        local src="${entry%%:*}"
        local k="${entry#*:}"
        if [[ -z "$k" ]]; then continue; fi
        # /auth/key
        local auth_status=$(curl -s -o /dev/null -w "%{http_code}" \
            --max-time 8 \
            "https://openrouter.ai/api/v1/auth/key" \
            -H "Authorization: Bearer $k" 2>/dev/null || echo "000")
        if [[ "$auth_status" == "200" ]]; then
            healthy_auth="${healthy_auth}${src},"
        fi
        # /chat/completions — lightweight probe with a near-universal model
        local inf_body=$(curl -s --max-time 15 \
            -X POST "https://openrouter.ai/api/v1/chat/completions" \
            -H "Authorization: Bearer $k" \
            -H "Content-Type: application/json" \
            -d "{\"model\":\"openrouter/free\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":4,\"temperature\":0}" 2>/dev/null || echo "")
        # Healthy inference: 200 status AND body has choices[0].message.content
        # (NOT just 200 — or-key.md returns 200 with error body for some models)
        if echo "$inf_body" | grep -q '"choices"'; then
            healthy_inference="${healthy_inference}${src},"
        fi
    done
    if [[ -z "$healthy_inference" ]]; then
        echo "all_unhealthy"
        echo "all_unhealthy" > "$KEY_HEALTH_FILE"
        return 2
    fi
    local result="ok:${healthy_inference%,}"
    if [[ -n "$healthy_auth" && "$healthy_auth" != "$healthy_inference" ]]; then
        result="ok:${healthy_inference%,} (auth_only:${healthy_auth%,})"
    fi
    echo "$result" > "$KEY_HEALTH_FILE"
    echo "$result"
    return 0
}

# === WINDOW DETECTION ========================================================
# Returns the quota window name for the current UTC hour.
# 00-06 off_peak | 06-12 moderate | 12-18 poor | 18-24 worst

get_window() {
    local h=$(date -u +%H)
    if [[ $h -ge 0 && $h -lt 6 ]]; then echo "off_peak"
    elif [[ $h -ge 6 && $h -lt 12 ]]; then echo "moderate"
    elif [[ $h -ge 12 && $h -lt 18 ]]; then echo "poor"
    else echo "worst"
    fi
}

# === QUALITY CHECK ===========================================================
# Args: $1=body, $2=http_status
# Outputs "valid_json:0|1 has_completion:0|1 content_length:N"
# CRITICAL: HTTP 200 with error body ("User not found") is NOT a valid response.
# The or-key.md key has been observed to return 200+error (2026-08-26 incident).
# Such responses are marked valid_json=0 so they're distinguishable.
quality_check() {
    local body="$1"
    local status="$2"
    if [[ "$status" != "200" ]]; then
        echo "valid_json:0 has_completion:0 content_length:0"
        return
    fi
    python3 <<PYEOF 2>/dev/null
import json, sys
try:
    d = json.loads('''$body''')
    # HTTP 200 with error body is NOT a valid response (observed or-key.md bug)
    if isinstance(d, dict) and 'error' in d and 'choices' not in d:
        print("valid_json:0 has_completion:0 content_length:0")
        sys.exit(0)
    valid = 1
    choices = d.get('choices', [])
    if choices and isinstance(choices, list):
        msg = choices[0].get('message', {})
        content = msg.get('content', '') or ''
        has_c = 1 if content and len(str(content)) > 0 else 0
        clen = len(str(content))
    else:
        has_c = 0
        clen = 0
    print(f"valid_json:{valid} has_completion:{has_c} content_length:{clen}")
except Exception as e:
    print("valid_json:0 has_completion:0 content_length:0")
PYEOF
}

# === PROBE FUNCTION ==========================================================
# Args: $1=model_id, $2=label
# Writes one JSONL line to LOG_FILE. Echoes one summary line.
# Tries each available key in order on 401.

probe_model() {
    local model_id="$1"
    local label="$2"
    local keys=$(get_keys)
    local start_ms=$(date +%s%3N)
    local http_status=""
    local body=""
    local key_src="none"
    local key_health=$(cat "$KEY_HEALTH_FILE" 2>/dev/null || echo "unknown")
    local window=$(get_window)
    local qc="valid_json:0 has_completion:0 content_length:0"
    
    if [[ -z "$keys" ]]; then
        http_status="NO_KEY"
        body='{"error": {"message": "no OpenRouter API key found"}}'
        key_src="none"
    else
        IFS='|' read -ra KEY_ARRAY <<< "$keys"
        local tried_any=0
        for entry in "${KEY_ARRAY[@]}"; do
            local src="${entry%%:*}"
            local k="${entry#*:}"
            if [[ -z "$k" ]]; then continue; fi
            
            response=$(curl -s -w "\n%{http_code}" \
                --max-time 30 \
                -X POST "https://openrouter.ai/api/v1/chat/completions" \
                -H "Authorization: Bearer $k" \
                -H "Content-Type: application/json" \
                -H "HTTP-Referer: https://xoe-nov.ai" \
                -H "X-Title: Omega Engine" \
                -d "{
                    \"model\": \"$model_id\",
                    \"messages\": [{\"role\": \"user\", \"content\": \"Reply with exactly: PING_OK\"}],
                    \"max_tokens\": 32,
                    \"temperature\": 0
                }" 2>/dev/null) || response=$'\n000'
            
            http_status=$(echo "$response" | tail -1)
            body=$(echo "$response" | sed '$d')
            tried_any=1
            key_src="$src"
            
        # If 200 AND body has choices (real completion), we're done.
        # If 200 with error body (or-key.md observed bug), try next key.
        # If 401, try next key. 429/402/400 stop (real model errors, not key).
        if [[ "$http_status" == "200" ]] && echo "$body" | grep -q '"choices"'; then
            break
        fi
        if [[ "$http_status" == "200" ]] && echo "$body" | grep -q '"error"'; then
            # 200 with error body → key auth issue, try next key
            continue
        fi
        if [[ "$http_status" == "429" || "$http_status" == "402" || "$http_status" == "400" ]]; then
            break
        fi
        # 401, 403, 5xx, 000 (network) → try next key
    done
        if [[ $tried_any -eq 0 ]]; then
            http_status="NO_KEY"
            body='{"error": {"message": "all keys failed pre-flight"}}'
        fi
        
        # Quality check on 200 responses
        if [[ "$http_status" == "200" ]]; then
            qc=$(quality_check "$body" "$http_status")
        fi
    fi
    
    local end_ms=$(date +%s%3N)
    local latency_ms=$((end_ms - start_ms))
    
    # Parse error message
    local error_msg=""
    if [[ "$http_status" != "200" ]]; then
        error_msg=$(python3 -c "
import json, sys
try:
    d = json.loads('''$body''')
    e = d.get('error', {})
    if isinstance(e, dict):
        print(e.get('message', str(e))[:200])
    else:
        print(str(e)[:200])
except:
    print('parse_error')
" 2>/dev/null || echo "parse_error")
    fi
    
    # Quality check fields parsed
    local qc_valid=$(echo "$qc" | grep -oE 'valid_json:[01]' | cut -d: -f2)
    local qc_completion=$(echo "$qc" | grep -oE 'has_completion:[01]' | cut -d: -f2)
    local qc_clen=$(echo "$qc" | grep -oE 'content_length:[0-9]+' | cut -d: -f2)
    
    # Write JSONL atomically
    python3 <<PYEOF >> "$LOG_FILE"
import json
from datetime import datetime, timezone
entry = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "model": "$model_id",
    "label": "$label",
    "http_status": int("$http_status") if "$http_status".isdigit() else "$http_status",
    "success": "$http_status" == "200",
    "latency_ms": $latency_ms,
    "error": """$error_msg""" if "$http_status" != "200" else None,
    "quality_check": {
        "valid_json": bool(int("${qc_valid:-0}")),
        "has_completion": bool(int("${qc_completion:-0}")),
        "content_length": int("${qc_clen:-0}")
    },
    "key_source": "$key_src",
    "key_health": "$key_health",
    "window": "$window"
}
print(json.dumps(entry, ensure_ascii=False))
PYEOF
    
    local status_icon="❌"
    [[ "$http_status" == "200" ]] && status_icon="✅"
    [[ "$http_status" == "429" ]] && status_icon="🚫"
    echo "[$label] $model_id → HTTP $http_status (${latency_ms}ms) $status_icon key=$key_src qc=$qc $error_msg"
}

# === MODEL REGISTRY (canonical 16 free models) ===============================
# Note: Removed stale `nvidia/nemotron-3-ultra-free` (missing -550b-a55b).
# Note: Removed `nvidia/nemotron-3-ultra` (no :free suffix, returned 400).

echo "=== Model Probe $(date -u '+%Y-%m-%d %H:%M:%S UTC') | window=$(get_window) ==="

# Pre-flight: key health
echo "--- KEY HEALTH PRE-CHECK ---"
key_health=$(check_key_health)
echo "key_health: $key_health"
if [[ $? -ne 0 && "$key_health" == "no_keys" ]]; then
    echo "FATAL: No OpenRouter API keys found in any source."
    echo "  Checked: $KEY_OR_FILE, $KEY_CLINE_FILE, $KEY_AUTH_FILE"
    exit 1
fi

# Probe 16 canonical free models
echo "--- FREE TIER (16 models) ---"

probe_model "z-ai/glm-5.2:free" "glm52"
probe_model "minimax/minimax-m2.7:free" "minimax_m27"
probe_model "minimax/minimax-m3:free" "minimax_m3"
probe_model "google/gemma-4-31b-it:free" "gemma4_31b"
probe_model "google/gemma-4-26b-a4b-it:free" "gemma4_26a4b"
probe_model "nvidia/nemotron-3-ultra-550b-a55b:free" "nemotron_ctrl"
probe_model "nvidia/nemotron-3.5-lightning:free" "nemotron35_lightning"
probe_model "nvidia/nemotron-3-super-120b-a12b:free" "nemotron3_super"
probe_model "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free" "nemotron3_nano_omni"
probe_model "nvidia/nemotron-3.5-content-safety:free" "nemotron35_safety"
probe_model "cohere/north-mini-code:free" "cohere_north_mini_code"
probe_model "poolside/laguna-xs-2.1:free" "poolside_laguna_xs"
probe_model "poolside/laguna-s-2.1:free" "poolside_laguna_s"
probe_model "liquid/lfm-2.5-2.6b:free" "liquid_lfm_25"
probe_model "dots-studio/dots-3-note-preview:free" "dots3_note"
probe_model "openrouter/free" "openrouter_free_router"

echo ""
echo "Log: $LOG_FILE ($(wc -l < "$LOG_FILE") entries)"
echo "=== Probe complete ==="
