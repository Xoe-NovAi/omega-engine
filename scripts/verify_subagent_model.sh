#!/usr/bin/env bash
# verify_subagent_model.sh — Verify a subagent session is on the correct model
# Per PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md
#
# Usage: ./scripts/verify_subagent_model.sh <agent_name> <session_id>
#
# Example: ./scripts/verify_subagent_model.sh verity ses_fb94afd01ffe1jvUmQVQfqaDu1

set -euo pipefail

AGENT="${1:-}"
SESSION="${2:-}"

# Colors (if terminal)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; NC=''
fi

if [[ -z "$AGENT" || -z "$SESSION" ]]; then
  echo -e "${YELLOW}Usage${NC}: $0 <agent_name> <session_id>"
  echo "Example: $0 verity ses_fb94afd01ffe1jvUmQVQfqaDu1"
  exit 2
fi

# Find the agent's .md file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENT_FILE="$REPO_ROOT/.opencode/agents/${AGENT}.md"

if [[ ! -f "$AGENT_FILE" ]]; then
  echo -e "${RED}ERROR${NC}: $AGENT_FILE not found"
  exit 2
fi

# Get the agent's configured model from the .md file
EXPECTED_MODEL=$(grep "^model:" "$AGENT_FILE" | head -1 | sed 's/^model:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '\r')
if [[ -z "$EXPECTED_MODEL" ]]; then
  echo -e "${RED}ERROR${NC}: $AGENT_FILE has no 'model:' field"
  echo "  Subagent will inherit parent's model — this is the bug the protocol fixes"
  echo "  Add 'model: openrouter/minimax/minimax-m3:free' to $AGENT_FILE"
  exit 2
fi

# Get the session's actual model from opencode.db
ACTUAL_OUTPUT=$(python3 -c "
import sqlite3, json, sys
sid = sys.argv[1]
db = sqlite3.connect('/home/arcana-novai/.local/share/opencode/opencode.db')
c = db.cursor()
# Get the most recent assistant message's model (ordered by time_created DESC)
c.execute('SELECT data FROM message WHERE session_id = ? ORDER BY time_created DESC LIMIT 10', (sid,))
rows = c.fetchall()
for r in rows:
    d = json.loads(r[0])
    if d.get('role') == 'assistant' and d.get('modelID'):
        provider = d.get('providerID', '?')
        model = d.get('modelID', '?')
        print(f'{provider}/{model}')
        sys.exit(0)
print('NO_MESSAGE')
" "$SESSION" 2>&1)
ACTUAL_MODEL="$ACTUAL_OUTPUT"

if [[ "$ACTUAL_MODEL" == "NO_MESSAGE" || -z "$ACTUAL_MODEL" ]]; then
  echo -e "${RED}ERROR${NC}: no assistant message found for session $SESSION"
  echo "  Session may not exist or may not have any assistant messages yet"
  exit 2
fi

# Compare
echo "Agent:       $AGENT"
echo "Config:      $EXPECTED_MODEL (from $AGENT_FILE)"
echo "Session:     $SESSION"
echo "Actual:      $ACTUAL_MODEL (from opencode.db)"
echo

if [[ "$ACTUAL_MODEL" == "$EXPECTED_MODEL" ]]; then
  echo -e "${GREEN}✅ PASS${NC}: session is on the configured model"
  exit 0
else
  echo -e "${RED}❌ FAIL${NC}: session is on a DIFFERENT model than configured"
  echo "  Expected: $EXPECTED_MODEL"
  echo "  Actual:   $ACTUAL_MODEL"
  echo
  echo "  This means the subagent inherited from the parent (or used the global default)."
  echo "  Per PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md, the agent's .md should override"
  echo "  the parent's model. Verify that the agent was launched AFTER the .md was updated."
  exit 1
fi
