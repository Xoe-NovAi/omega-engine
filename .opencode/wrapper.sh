#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

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

# Logging — persistent (stderr AND .opencode/logs/wrapper.log) so post-exit
# failures are diagnosable after the terminal closes [2026-08-25 jem fix]
LOG_DIR="${PROJECT_ROOT}/.opencode/logs"
mkdir -p "${LOG_DIR}" 2>/dev/null || true
LOG_FILE="${LOG_DIR}/wrapper.log"
log() {
    echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] [wrapper] $*" | tee -a "${LOG_FILE}" >&2
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

# Record baseline BEFORE OpenCode starts (epoch ms) + snapshot existing
# session IDs [2026-08-24 parallel-instance fix]. Under 2-3 concurrent
# OpenCode instances, "most recently updated session" fleet-wide is often
# ANOTHER instance's active session — wrong-session soul distillation is
# an M11 integrity violation. Set-diff attribution: sessions that EXIST at
# exit but did NOT exist at launch were created by THIS instance.
BASELINE_MS=$(date +%s%3N)
log "Session baseline timestamp: ${BASELINE_MS}"

BASELINE_IDS=""
if command -v jq &>/dev/null; then
    # NOTE: `opencode db` output truncates nondeterministically when piped
    # (verified 2026-08-24: file redirect 3/3 valid, pipe 0/3). Stage through
    # a temp file, always.
    _base_tmp=$(mktemp)
    if opencode db --format json "SELECT id FROM session ORDER BY time_created;" > "${_base_tmp}" 2>/dev/null \
        && jq -e 'length > 0' "${_base_tmp}" &>/dev/null; then
        BASELINE_IDS=$(jq -r '.[].id' "${_base_tmp}" | sort | tr '\n' ',')
        log "Baseline session count: $(echo "${BASELINE_IDS}" | tr ',' '\n' | grep -c . || echo 0)"
    else
        log "WARNING: baseline session snapshot failed — attribution falls back to directory scoping"
    fi
    rm -f "${_base_tmp}"
fi

# Run OpenCode — blocks until ANY exit
# [2026-08-25 jem fix] `set -e` + bare invocation killed this wrapper BEFORE
# distillation whenever opencode exited non-zero (crash / SIGINT / kill).
# Every such session silently skipped codex refresh. Capture the code instead.
OPENCODE_EXIT_CODE=0
log "Executing: ${OPENCODE_BIN} $*"
"${OPENCODE_BIN}" "$@" || OPENCODE_EXIT_CODE=$?

log "OpenCode exited with code ${OPENCODE_EXIT_CODE}"

# Phase 1: Wrapper DB Integration (C-0.5 W-1/W-2) — parallel-safe attribution
# Strategy [2026-08-24]: set-diff of session IDs (this instance created the
# new ones) scoped to this project directory; timestamp ordering is only a
# tiebreaker among THIS instance's new sessions, never a fleet-wide pick.
if command -v jq &>/dev/null; then
    _after_tmp=$(mktemp)
    opencode db --format json "
        SELECT id, agent, model, directory, time_created, time_updated,
               tokens_input, tokens_output, cost
        FROM session
        WHERE time_updated >= ${BASELINE_MS}
        ORDER BY time_updated DESC;
    " > "${_after_tmp}" 2>/dev/null || true

    if jq -e 'length > 0' "${_after_tmp}" &>/dev/null; then
        # Sessions this instance CREATED (present now, absent at baseline)
        MINE_JSON=$(jq -c --arg base ",${BASELINE_IDS}" --arg dir "${PROJECT_ROOT}" '
            [ .[] | .id as $id | select(
                ((($base + ",") | contains("," + $id + ",")) | not)
                and (.directory // "") == $dir
            ) ]' "${_after_tmp}")

        COUNT=$(echo "${MINE_JSON}" | jq 'length')
        if [[ "${COUNT}" -eq 0 ]]; then
            # Fallback: no brand-new sessions (e.g., resumed one) — scope by
            # directory + baseline time instead of fleet-wide recency.
            log "No new sessions; falling back to directory-scoped recent"
            MINE_JSON=$(jq -c --arg dir "${PROJECT_ROOT}" '
                [ .[] | select((.directory // "") == $dir) ]' "${_after_tmp}")
        fi

        SESSION_JSON=$(echo "${MINE_JSON}" | jq -c '[.[0]]')

        rm -f "${_after_tmp}"
        if [[ -n "${SESSION_JSON}" ]] && echo "${SESSION_JSON}" | jq -e 'length > 0' &>/dev/null; then
            SESSION_ID=$(echo "${SESSION_JSON}" | jq -r '.[0].id // "unknown"')
            ENTITY=$(echo "${SESSION_JSON}" | jq -r '.[0].agent // empty')
            MODEL_JSON=$(echo "${SESSION_JSON}" | jq -r '.[0].model // empty')

            if [[ -n "${MODEL_JSON}" ]]; then
                MODEL_ID=$(echo "${MODEL_JSON}" | jq -r '.id // "unknown"')
            else
                MODEL_ID="unknown"
            fi

            export OPENCODE_SESSION_ID="${SESSION_ID}"
            export OPENCODE_ENTITY="${ENTITY:-unknown}"
            export OPENCODE_MODEL="${MODEL_ID}"

            log "Session detected: ID=${SESSION_ID} Entity=${ENTITY:-unknown} Model=${MODEL_ID} (${COUNT} candidate(s) from this instance)"

            # Cache for debugging — includes attribution metadata
            echo "${SESSION_JSON}" | jq -c --arg ts "$(date +%s%3N)" --arg n "${COUNT}"                 '. + [{_wrapper: {attributed_at: ($ts | tonumber), candidates: ($n | tonumber)}}]' > "${SESSION_CACHE}"
        else
            log "WARNING: No session attributable to this instance (directory=${PROJECT_ROOT})"
            export OPENCODE_SESSION_ID="unknown"
            export OPENCODE_ENTITY="unknown"
            export OPENCODE_MODEL="unknown"
        fi
    else
        log "WARNING: No sessions updated after baseline"
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

# Concurrent-exit guard: serialize distillation across instances so two
# wrappers never interleave writes to proposed_lessons.yaml (M11 race).
DISTILL_LOCK="${PROJECT_ROOT}/.opencode/.distill.lock"

# Post-exit: guaranteed to run (EXIT trap semantics)
if [[ -z "${SKIP_DISTILL:-}" ]]; then
    log "Running soul distillation + codex refresh (timeout: ${DISTILL_TIMEOUT}s)..."

    # Run with timeout, never fail the wrapper; flock serializes concurrent
    # instance exits so proposed_lessons.yaml appends never interleave (M11)
    if timeout "${DISTILL_TIMEOUT}s" flock -w 45 "${DISTILL_LOCK}"         "${VENV_PYTHON}" "${DISTILL_SCRIPT}" 2>&1; then
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