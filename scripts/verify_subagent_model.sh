#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# verify_subagent_model.sh — Verify a subagent session is on the configured (or inherited) model
# Per PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md
#
# Usage: ./scripts/verify_subagent_model.sh <agent_name> <session_id>
#
# Example: ./scripts/verify_subagent_model.sh verity ses_fb94afd01ffe1jvUmQVQfqaDu1
#
# Behavior:
#   - If the agent .md has no 'model:' field (the recommended default per v2),
#     the script REPORTS the actual model and PASSES. The subagent inherited
#     from the parent's active model, which is the natural, recommended behavior.
#   - If the agent .md has a 'model:' field, the script compares the actual
#     model to the configured one. PASS = match; FAIL = mismatch.
#
# This script does NOT impose any model. It only reports and verifies.

set -euo pipefail

AGENT="${1:-}"
SESSION="${2:-}"

if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; NC=''
fi

if [[ -z "$AGENT" || -z "$SESSION" ]]; then
  echo -e "${YELLOW}Usage${NC}: $0 <agent_name> <session_id>"
  echo "Example: $0 verity ses_fb94afd01ffe1jvUmQVQfqaDu1"
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENT_FILE="$REPO_ROOT/.opencode/agents/${AGENT}.md"

if [[ ! -f "$AGENT_FILE" ]]; then
  echo -e "${RED}ERROR${NC}: $AGENT_FILE not found"
  exit 2
fi

# Get the agent's configured model from the .md file (if any)
EXPECTED_MODEL=$(grep "^model:" "$AGENT_FILE" 2>/dev/null | head -1 | sed 's/^model:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '\r' || echo "")

# Get the session's actual model from opencode.db
ACTUAL_OUTPUT=$(python3 -c "
import sqlite3, json, sys
sid = sys.argv[1]
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
c.execute('SELECT data FROM message WHERE session_id = ? ORDER BY time_created DESC LIMIT 10', (sid,))
for r in c.fetchall():
    d = json.loads(r[0])
    if d.get('role') == 'assistant' and d.get('modelID'):
        print(f'{d.get(\"providerID\")}/{d.get(\"modelID\")}')
        sys.exit(0)
print('NO_MESSAGE')
" "$SESSION" 2>&1)
ACTUAL_MODEL="$ACTUAL_OUTPUT"

if [[ "$ACTUAL_MODEL" == "NO_MESSAGE" || -z "$ACTUAL_MODEL" ]]; then
  echo -e "${RED}ERROR${NC}: no assistant message found for session $SESSION"
  echo "  Session may not exist or may not have any assistant messages yet"
  exit 2
fi

echo "Agent:       $AGENT"
if [[ -n "$EXPECTED_MODEL" ]]; then
  echo "Configured:  $EXPECTED_MODEL (from $AGENT_FILE)"
else
  echo "Configured:  (no model: field — inherits from parent's active model)"
fi
echo "Session:     $SESSION"
echo "Actual:      $ACTUAL_MODEL (from opencode.db)"
echo

# Verification logic
if [[ -z "$EXPECTED_MODEL" ]]; then
  # No model: field — pass-through (the subagent inherits, which is the design per v2)
  echo -e "${GREEN}✅ PASS${NC}: no model: field configured; subagent inherited the parent's model (natural behavior)"
  echo "  To override, add 'model: provider/model' to $AGENT_FILE"
  exit 0
elif [[ "$ACTUAL_MODEL" == "$EXPECTED_MODEL" ]]; then
  echo -e "${GREEN}✅ PASS${NC}: session is on the configured model"
  exit 0
else
  echo -e "${RED}❌ FAIL${NC}: session is on a DIFFERENT model than configured"
  echo "  Expected: $EXPECTED_MODEL"
  echo "  Actual:   $ACTUAL_MODEL"
  echo "  Either: (1) the agent was launched before the .md was updated, or"
  echo "           (2) the .md was changed but the session was not restarted."
  exit 1
fi
