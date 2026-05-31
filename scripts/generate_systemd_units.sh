#!/bin/bash
# 🔱 Omega Engine — Systemd Unit Generator (Rootless)
# AP: AP-MCP-SYSTEMD-GEN-v1.1.0

set -e

USER_SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$USER_SERVICE_DIR"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"

# Port Mappings
declare -A PORTS
PORTS["omega-hub"]=8016
PORTS["omega-research"]=8011
PORTS["omega-stats"]=8012

# 0. Cleanup retired services
RETIRED=("omega-hivemind" "omega-oracle" "omega-library")
for svc in "${RETIRED[@]}"; do
    if [ -f "$USER_SERVICE_DIR/$svc.service" ]; then
        echo "🗑️  Removing retired service: $svc"
        systemctl --user stop "$svc.service" || true
        systemctl --user disable "$svc.service" || true
        rm "$USER_SERVICE_DIR/$svc.service"
    fi
done

# 1. Generate MCP Services
for mcp in "${!PORTS[@]}"; do
    PORT=${PORTS[$mcp]}
    
    # Path resolution
    if [ "$mcp" == "omega-hub" ]; then
        SERVER_PATH="$REPO_ROOT/mcp/omega_hub/server.py"
    else
        SERVER_PATH="$REPO_ROOT/mcp/$mcp/server.py"
    fi

    cat <<EOF > "$USER_SERVICE_DIR/$mcp.service"
[Unit]
Description=Omega MCP Service - $mcp
After=network.target

[Service]
Type=simple
WorkingDirectory=$REPO_ROOT
ExecStart=$VENV_PYTHON $SERVER_PATH
Restart=on-failure
RestartSec=5
Environment=PYTHONPATH=$REPO_ROOT/src
Environment=OMEGA_MCP_TRANSPORT=sse
Environment=OMEGA_MCP_PORT=$PORT
Environment=OMEGA_MCP_HOST=127.0.0.1
Environment=EXA_API_KEY=${EXA_API_KEY}
Environment=BRAVE_API_KEY=${BRAVE_API_KEY}
Environment=TAVILY_API_KEY=${TAVILY_API_KEY}
# Environment=GEMINI_API_KEY=your_key_here

[Install]
WantedBy=default.target
EOF
done

# 2. Generate Podman Infrastructure Unit
cat <<EOF > "$USER_SERVICE_DIR/omega-infra.service"
[Unit]
Description=Omega Infrastructure (Podman Compose)
After=network.target

[Service]
Type=simple
WorkingDirectory=$REPO_ROOT
ExecStart=/usr/bin/podman-compose -f deploy/infra/docker-compose.yml up
ExecStop=/usr/bin/podman-compose -f deploy/infra/docker-compose.yml down
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# 3. Generate MCP Watchdog Service
cat <<EOF > "$USER_SERVICE_DIR/omega-mcp-watchdog.service"
[Unit]
Description=Omega MCP Watchdog Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$REPO_ROOT
ExecStart=$VENV_PYTHON $REPO_ROOT/scripts/mcp_watchdog.py
Restart=on-failure
RestartSec=10
Environment=PYTHONPATH=$REPO_ROOT/src
Environment=EXA_API_KEY=${EXA_API_KEY}
Environment=BRAVE_API_KEY=${BRAVE_API_KEY}
Environment=TAVILY_API_KEY=${TAVILY_API_KEY}

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
echo "✅ Systemd units generated in $USER_SERVICE_DIR"
echo "👉 Run 'systemctl --user enable --now omega-*' to start the stack."
