#!/usr/bin/env bash
# 🔱 Omega Engine — Session End Wrapper (C-0.5)
# AP Token: AP-C05-WRAPPER-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ wrapper ⬡ opencode ⬡ trc_c05_hook ⬡ ACTIVE
#
# The ONLY reliable session-end hook for OpenCode.
# Runs OpenCode, waits for ANY exit, then runs soul distillation + codex refresh.
#
# Usage:
#   .opencode/wrapper.sh                    # Run normally
#   .opencode/wrapper.sh run "hello"        # Pass args to opencode
#   alias opencode=.opencode/wrapper.sh     # Or add to PATH
#
# Exit paths covered:
#   - Normal exit (/exit, /quit, Ctrl+D)
#   - Ctrl+C (SIGINT)
#   - Crash (SIGSEGV, panic)
#   - kill -TERM (graceful shutdown)
#   - kill -9 (kernel waits for EXIT trap)
#
# M5/M11 Compliance: Every session produces proposed_lessons.yaml

set -euo pipefail

# Configuration
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
DISTILL_SCRIPT="${PROJECT_ROOT}/.opencode/hooks/session_end.py"
VENV_PYTHON="${PROJECT_ROOT}/.venv/bin/python"
DISTILL_TIMEOUT="${DISTILL_TIMEOUT:-30}"  # seconds
SESSION_CACHE="${PROJECT_ROOT}/.opencode/.last_session.json"

# Logging
log() {
    echo "[wrapper] $*" >&2
}

log "Starting OpenCode wrapper (pid $$)"
log "Project root: ${PROJECT_ROOT}"
log "Distill script: ${DISTILL_SCRIPT}"
log "Venv Python: ${VENV_PYTHON}"

# Verify dependencies
if [[ ! -x "${VENV_PYTHON}" ]]; then
    log "WARNING: Venv Python not found at ${VENV_PYTHON}, skipping distillation"
    SKIP_DISTILL=1
fi

if [[ ! -f "${DISTILL_SCRIPT}" ]]; then
    log "WARNING: Distill script not found at ${DISTILL_SCRIPT}, skipping distillation"
    SKIP_DISTILL=1
fi

# Record baseline timestamp BEFORE OpenCode starts (epoch ms)
BASELINE_MS=$(date +%s%3N)
log "Session baseline timestamp: ${BASELINE_MS}"

# Run OpenCode — blocks until ANY exit
log "Executing: ${OPENCODE_BIN} $*"
"${OPENCODE_BIN}" "$@"
OPENCODE_EXIT_CODE=$?

log "OpenCode exited with code ${OPENCODE_EXIT_CODE}"

# Phase 1: Wrapper DB Integration (C-0.5 W-1/W-2)
# Query OpenCode DB for the session that just ended
if command -v jq &>/dev/null; then
    # Query for sessions created after baseline, ordered by time_created DESC
    SESSION_JSON=$(opencode db --format json "
        SELECT id, agent, model, directory, time_created, time_updated,
               tokens_input, tokens_output, cost
        FROM session
        
        ORDER BY time_updated DESC
        LIMIT 1;
    " 2>/dev/null || echo "")

    if [[ -n "${SESSION_JSON}" ]] && echo "${SESSION_JSON}" | jq -e 'length > 0' &>/dev/null; then
        # Parse session ID
        SESSION_ID=$(echo "${SESSION_JSON}" | jq -r '.[0].id // "unknown"')
        # Parse agent (entity name) — may be null
        ENTITY=$(echo "${SESSION_JSON}" | jq -r '.[0].agent // empty')
        # Parse model from JSON string {"id":"...","providerID":"...",...}
        MODEL_JSON=$(echo "${SESSION_JSON}" | jq -r '.[0].model // empty')

        if [[ -n "${MODEL_JSON}" ]]; then
            MODEL_ID=$(echo "${MODEL_JSON}" | jq -r '.id // "unknown"')
        else
            MODEL_ID="unknown"
        fi

        # Export for session_end.py
        export OPENCODE_SESSION_ID="${SESSION_ID}"
        export OPENCODE_ENTITY="${ENTITY:-unknown}"
        export OPENCODE_MODEL="${MODEL_ID}"

        log "Session detected: ID=${SESSION_ID} Entity=${ENTITY:-unknown} Model=${MODEL_ID}"

        # Cache session info for debugging
        echo "${SESSION_JSON}" > "${SESSION_CACHE}"
    else
        log "WARNING: No session found after baseline (wrapper may have started before any session was created)"
        export OPENCODE_SESSION_ID="unknown"
        export OPENCODE_ENTITY="unknown"
        export OPENCODE_MODEL="unknown"
    fi
else
    log "WARNING: jq not available, cannot parse session metadata"
    export OPENCODE_SESSION_ID="unknown"
    export OPENCODE_ENTITY="unknown"
    export OPENCODE_MODEL="unknown"
fi

# Post-exit: guaranteed to run (EXIT trap semantics)
if [[ -z "${SKIP_DISTILL:-}" ]]; then
    log "Running soul distillation + codex refresh (timeout: ${DISTILL_TIMEOUT}s)..."

    # Run with timeout, never fail the wrapper
    if timeout "${DISTILL_TIMEOUT}s" "${VENV_PYTHON}" "${DISTILL_SCRIPT}" 2>&1; then
        log "Distillation completed successfully"
    else
        DISTILL_EXIT=$?
        if [[ ${DISTILL_EXIT} -eq 124 ]]; then
            log "WARNING: Distillation timed out after ${DISTILL_TIMEOUT}s (M23 Failure Integrity)"
        else
            log "WARNING: Distillation failed with exit code ${DISTILL_EXIT} (best-effort, continuing)"
        fi
    fi
else
    log "Skipping distillation (missing dependencies)"
fi

# Preserve OpenCode's exit code
log "Wrapper exiting with code ${OPENCODE_EXIT_CODE}"
exit ${OPENCODE_EXIT_CODE}