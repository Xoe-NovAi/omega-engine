#!/bin/bash
# 🔱 Omega Engine — IDE MCP Sync
# AP: AP-IDE-MCP-SYNC-v1.0.0

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_SRC="$REPO_ROOT/config/mcp_servers.json"

# List of target settings files
TARGETS=(
    "$HOME/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    "$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    "$HOME/.antigravity/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
)

echo "🔄 Centralizing MCP settings from $CONFIG_SRC"

for target in "${TARGETS[@]}"; do
    if [ -f "$target" ]; then
        echo "✅ Updating $target"
        # We use python to merge the JSON to avoid overwriting other settings (like custom servers)
        # However, for total centralization, we can just replace mcpServers block or the whole file
        # Given the "centralized" mandate, we will ensure these servers exist in the target.
        python3 -c "
import json, sys
src = json.load(open('$CONFIG_SRC'))
try:
    dst = json.load(open('$target'))
except:
    dst = {'mcpServers': {}}

if 'mcpServers' not in dst:
    dst['mcpServers'] = {}

# Update with Omega servers
dst['mcpServers'].update(src['mcpServers'])

with open('$target', 'w') as f:
    json.dump(dst, f, indent=2)
"
    else
        echo "⏭️  Target not found: $target"
    fi
done

echo "🚀 IDE MCP synchronization complete."
