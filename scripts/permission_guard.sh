#!/bin/bash
# 🔱 Omega Engine — Permission Guard Script
# Synchronizes external_directory whitelist and resolves "Permission Denied" conflicts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OPENCODE_JSON="$PROJECT_ROOT/opencode.json"
GLOBAL_CONFIG="$HOME/.config/opencode/mcp_servers.json"

echo "🔧 Omega Engine Permission Guard"
echo "================================"
echo "Project: $PROJECT_ROOT"
echo ""

# Function to extract external_directory whitelist from opencode.json
get_local_whitelist() {
    if [ -f "$OPENCODE_JSON" ]; then
        # Use jq if available, otherwise fallback to grep/sed
        if command -v jq &> /dev/null; then
            jq -r '.permission.external_directory | to_entries | .[] | .key' "$OPENCODE_JSON" 2>/dev/null | grep -v '^$' || true
        else
            grep -o '".*"' "$OPENCODE_JSON" | grep -A1 -B1 'external_directory' | grep -o '".*"' | sed 's/"//g' | grep -v 'external_directory' || true
        fi
    fi
}

# Function to ensure the global config has the filesystem server with correct type and args
ensure_global_filesystem_config() {
    if [ ! -f "$GLOBAL_CONFIG" ]; then
        echo "Creating global MCP config at $GLOBAL_CONFIG"
        mkdir -p "$(dirname "$GLOBAL_CONFIG")"
        cat > "$GLOBAL_CONFIG" <<EOF
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$PROJECT_ROOT"
      ],
      "env": {}
    }
  }
}
EOF
    else
        # Update or add filesystem server
        if command -v jq &> /dev/null; then
            # Check if filesystem server exists
            if jq '.mcpServers.filesystem' "$GLOBAL_CONFIG" &> /dev/null; then
                # Update existing
                jq --argjson args "[\"-y\", \"@modelcontextprotocol/server-filesystem\", \"$PROJECT_ROOT\"]" \
                   '.mcpServers.filesystem.args = $args |
                    .mcpServers.filesystem.type = "stdio"' "$GLOBAL_CONFIG" > "$GLOBAL_CONFIG.tmp" && mv "$GLOBAL_CONFIG.tmp" "$GLOBAL_CONFIG"
            else
                # Add new
                jq --argjson fs "{\"type\":\"stdio\",\"command\":\"npx\",\"args\":[\"-y\",\"@modelcontextprotocol/server-filesystem\",\"$PROJECT_ROOT\"],\"env\":{}}" \
                   '.mcpServers.filesystem = $fs' "$GLOBAL_CONFIG" > "$GLOBAL_CONFIG.tmp" && mv "$GLOBAL_CONFIG.tmp" "$GLOBAL_CONFIG"
            fi
        else
            # Fallback: rewrite entire file (simple case)
            cat > "$GLOBAL_CONFIG" <<EOF
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "$PROJECT_ROOT"
      ],
      "env": {}
    }
  }
}
EOF
        fi
    fi
    echo "✓ Global filesystem MCP server configured for $PROJECT_ROOT"
}

# Function to verify the whitelist covers the project root
verify_whitelist() {
    local whitelist
    whitelist=$(get_local_whitelist)
    if [ -z "$whitelist" ]; then
        echo "⚠️  No external_directory whitelist found in $OPENCODE_JSON"
        return 1
    fi

    local covered=0
    while IFS= read -r pattern; do
        # Convert glob pattern to regex for matching (simple check)
        if [[ "$PROJECT_ROOT" == $pattern ]] || [[ "$PROJECT_ROOT/" == $pattern* ]] || [[ "$PROJECT_ROOT" == ${pattern%\**} ]]; then
            covered=1
            break
        fi
    done <<< "$whitelist"

    if [ $covered -eq 1 ]; then
        echo "✓ Project root $PROJECT_ROOT is covered by whitelist"
        return 0
    else
        echo "⚠️  Project root $PROJECT_ROOT may not be covered by whitelist:"
        echo "    Whitelist patterns:"
        echo "$whitelist"
        return 1
    fi
}

# Main execution
echo "1. Ensuring global MCP filesystem server config..."
ensure_global_filesystem_config

echo ""
echo "2. Checking local opencode.json whitelist..."
verify_whitelist

echo ""
echo "3. Restarting affected systemd user services (if any)..."
# List omega-related services that might need restart
SERVICES="omega-hub omega-research omega-stats omega-hivemind omega-mcp-watchdog"
for service in $SERVICES; do
    if systemctl --user is-active "$service" &> /dev/null; then
        echo "   Restarting $service..."
        systemctl --user restart "$service"
    fi
done

echo ""
echo "🔍 Verification:"
echo "   - Test filesystem tools now: try reading a file in $PROJECT_ROOT"
echo "   - Check server status: systemctl --user status omega-hub"
echo "   - Check MCP server processes: ps aux | grep -E 'npx|filesystem|tavily' | grep -v grep"

echo ""
echo "✅ Permission guard completed."