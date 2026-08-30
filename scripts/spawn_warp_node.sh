#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Multi-Namespace WARP Lifecycle Automation Script
# [id-soft: doom-1993] Sovereign-Siloing Pattern adapted to network namespaces
# AP: AP-WARP-LIFECYCLE-v2.0.0
# Dependencies: systemctl, iproute2

set -euo pipefail

# ── Input Validation ──────────────────────────────────────────────────────────
NODE_ID="${1:?Usage: $0 [node_id] [start|recycle|stop|destroy|status]}"
ACTION="${2:-start}"

if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]] || [ "$NODE_ID" -lt 1 ] || [ "$NODE_ID" -gt 65535 ]; then
    echo "[ERROR] Node ID must be an integer between 1 and 65535." >&2
    exit 1
fi

# ── Configuration Constants ───────────────────────────────────────────────────
NS_NAME="warp_node_${NODE_ID}"
PROXY_PORT=$((8080 + NODE_ID))

# ── Actions ──────────────────────────────────────────────────────────────────
case "$ACTION" in
    "start")
        echo "[System Config] Starting Node $NODE_ID..."
        # Trigger the full dependency chain: prep -> reg -> node -> bridge
        sudo systemctl start "socat-bridge@${NODE_ID}.service"
        echo "[System Config] Node $NODE_ID active on SOCKS5 port $PROXY_PORT"
        ;;
        
    "recycle")
        echo "[System Config] Recycling Node $NODE_ID (Graceful Drain)..."
        
        # 1. Stop the bridge to prevent new connections
        sudo systemctl stop "socat-bridge@${NODE_ID}.service"
        
        # 2. Drain existing connections using conntrack
        DRAIN_TIMEOUT=30
        ELAPSED=0
        echo -n "Draining active connections"
        while [ $ELAPSED -lt $DRAIN_TIMEOUT ]; do
            # Check for active TCP connections on the proxy port
            if ! sudo conntrack -L | grep -q ":$PROXY_PORT "; then
                echo " [DONE]"
                break
            fi
            echo -n "."
            sleep 1
            ELAPSED=$((ELAPSED + 1))
        done
        if [ $ELAPSED -eq $DRAIN_TIMEOUT ]; then
            echo " [TIMEOUT] Forcing rotation"
        fi
        echo ""

        # 3. Restart the node to rotate exit IP
        sudo systemctl restart "warp-node@${NODE_ID}.service"
        
        # 4. Restore the bridge
        sudo systemctl start "socat-bridge@${NODE_ID}.service"
        echo "[System Config] Tunnel recycled and bridge restored. New exit IP assigned."
        ;;
        
    "stop")
        echo "[System Config] Stopping Node $NODE_ID..."
        sudo systemctl stop "socat-bridge@${NODE_ID}.service" "warp-node@${NODE_ID}.service"
        echo "[System Config] Node $NODE_ID stopped."
        ;;
        
    "destroy")
        echo "[System Config] Destroying Node $NODE_ID and all associated state..."
        sudo systemctl stop "socat-bridge@${NODE_ID}.service" "warp-node@${NODE_ID}.service" "warp-reg@${NODE_ID}.service"
        # Stopping the prep service triggers the ExecStop cleanup (namespace/veth deletion)
        sudo systemctl stop "warp-ns-prep@${NODE_ID}.service"
        echo "[System Config] Node $NODE_ID fully destroyed."
        ;;
        
    "status")
        echo "=== Node $NODE_ID Status ==="
        if ip netns list | grep -q "$NS_NAME"; then
            echo "  Namespace: EXISTS"
            systemctl is-active --quiet "warp-node@${NODE_ID}.service" && echo "  Service:   ACTIVE" || echo "  Service:   INACTIVE"
            systemctl is-active --quiet "socat-bridge@${NODE_ID}.service" && echo "  Bridge:    RUNNING" || echo "  Bridge:    STOPPED"
            echo "  Port:      $PROXY_PORT"
        else
            echo "  Namespace: DOES NOT EXIST"
        fi
        ;;
        
    *)
        echo "Usage: $0 [node_id] [start|recycle|stop|destroy|status]"
        echo ""
        echo "Actions:"
        echo "  start    - Initialize and start the node"
        echo "  recycle  - High-speed tunnel reset to rotate exit IP"
        echo "  stop     - Stop the node without destroying state"
        echo "  destroy  - Stop and remove all state (namespace, config, PID files)"
        echo "  status   - Display current node status"
        exit 1
        ;;
esac
