#!/bin/bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# OpenCode Wrapper with Compaction Resilience
# M15: Sovereign Continuity — wraps OpenCode to inject session preservation

set -euo pipefail

SESSION_ID="${OPENCODE_SESSION_ID:-$(uuidgen 2>/dev/null || date +%s%N)}"
export OPENCODE_SESSION_ID="$SESSION_ID"

GNosis_DIR="$HOME/.config/opencode/session_gnosis"
mkdir -p "$GNosis_DIR"

# Pre-hydration: check for existing gnosis
if [[ -f "$GNosis_DIR/$SESSION_ID.md" ]]; then
    echo "[opencode-wrapper] Found existing session gnosis for $SESSION_ID" >&2
fi

# Run OpenCode with compaction monitoring
# Note: OpenCode doesn't expose compaction hooks directly
# This wrapper provides best-effort preservation via signal handling

cleanup() {
    local exit_code=$?
    echo "[opencode-wrapper] Session $SESSION_ID ending (exit: $exit_code)" >&2
    
    # Capture final context (best effort)
    cat > "$GNosis_DIR/$SESSION_ID.md" << GNOSIS_EOF
# SESSION GNOSIS — $SESSION_ID
**Captured**: $(date -Iseconds)
**Reason**: Session end (exit code: $exit_code)

## Context
Session ended. Manual gnosis capture recommended.

## Continuation Notes
Run \`opencode-hydration $SESSION_ID\` to restore context.
GNOSIS_EOF
    
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Execute OpenCode
exec opencode "$@"