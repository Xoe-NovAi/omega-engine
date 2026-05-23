#!/bin/bash
# 🔱 Omega Engine — OpenCode Launch Wrapper
# Sources .env from project root before launching OpenCode
# This ensures all ${VAR_NAME} substitutions in MCP server configs resolve.
#
# Usage:
#   ./scripts/opencode.sh         # Starts interactive OpenCode session
#   ./scripts/opencode.sh <args>  # Passes args through to OpenCode
#
# Install as default:
#   alias opencode='~/Documents/Xoe-NovAi/omega-engine/scripts/opencode.sh'
#   # or add to ~/.bashrc:
#   # source <(grep -E '^(EXA|BRAVE|TAVILY|GOOGLE|OPENROUTER)_' .env)

set -a  # automatically export all sourced variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
    echo "⬡ Omega: Loaded .env ($(grep -cE '^[A-Z].*=.' "$PROJECT_DIR/.env") vars)" >&2
else
    echo "⬡ Omega: WARNING — No .env found at $PROJECT_DIR/.env" >&2
fi
set +a

exec opencode "$@"
