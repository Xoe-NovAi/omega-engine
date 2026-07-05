#!/usr/bin/env bash
# 🔱 Omega Engine — Multi-Namespace WARP Lifecycle Automation Script
# [id-soft: doom-1993] Sovereign-Siloing Pattern adapted to network namespaces
# AP: AP-WARP-LIFECYCLE-v1.2.0
# Dependencies: socat, iproute2, cloudflare-warp, systemctl

set -euo pipefail

# ── Input Validation ──────────────────────────────────────────────────────────
NODE_ID="${1:?Usage: $0 [node_id] [start|recycle|stop]}"
ACTION="${2:-start}"

if ! [[ "$NODE_ID" =~ ^[0-9]+$ ]] || [ "$NODE_ID" -lt 1 ] || [ "$NODE_ID" -gt 65535 ]; then
    echo "[ERROR] Node ID must be an integer between 1 and 65535." >&2
    exit 1
fi

# ── Dependency Check ──────────────────────────────────────────────────────────
for cmd in socat ip warp-cli systemctl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "[ERROR] Required command '$cmd' not found in PATH." >&2
        exit 1
    fi
done

# ── Configuration Constants ───────────────────────────────────────────────────
NS_NAME="warp_node_${NODE_ID}"
CONF_DIR="/var/lib/cloudflare-warp-${NODE_ID}"
PROXY_PORT=$((8080 + NODE_ID))
PID_DIR="/run/cloudflare-warp-${NODE_ID}"
PID_FILE="${PID_DIR}/socat_bridge.pid"
STATE_FILE="${PID_DIR}/exit_ip.txt"

# ── Helper: Validate port availability ────────────────────────────────────────
check_port_available() {
    if ss -tlnp | grep -q ":${PROXY_PORT} "; then
        echo "[ERROR] Port ${PROXY_PORT} is already in use." >&2
        return 1
    fi
}

# ── Helper: Kill existing socat bridge safely ────────────────────────────────
kill_existing_bridge() {
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
        if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
            echo "[System Config] Stopping existing socat bridge (PID: ${old_pid})..."
            kill "$old_pid" 2>/dev/null || true
            wait "$old_pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
}

# ── Core: Setup Network Namespace ────────────────────────────────────────────
setup_namespace() {
    if ! ip netns list | grep -q "$NS_NAME"; then
        echo "[System Config] Creating isolated network namespace: $NS_NAME"
        ip netns add "$NS_NAME"
        ip netns exec "$NS_NAME" ip link set lo up
    fi
    
    mkdir -p "$CONF_DIR" "$PID_DIR"
    chmod 0750 "$CONF_DIR"
    chmod 0755 "$PID_DIR"
}

# ── Core: Configure WARP Client ──────────────────────────────────────────────
configure_warp_client() {
    echo "[System Config] Configuring warp-cli inside $NS_NAME on port $PROXY_PORT"
    
    ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" mode proxy
    ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" proxy port "$PROXY_PORT"
    
    if [ ! -f "${CONF_DIR}/reg.json" ]; then
        echo "[System Config] Registering new device identity..."
        ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" registration new
    fi
    
    ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" connect
}

# ── Core: Start socat Loopback Bridge ────────────────────────────────────────
start_socat_bridge() {
    kill_existing_bridge
    check_port_available || exit 1
    
    echo "[System Config] Launching socat bridge: host 127.0.0.1:${PROXY_PORT} → namespace ${NS_NAME}"
    socat TCP-LISTEN:${PROXY_PORT},fork,reuseaddr,bind=127.0.0.1 \
          EXEC:"ip netns exec ${NS_NAME} socat - TCP:127.0.0.1:${PROXY_PORT}" &
    local socat_pid=$!
    echo "$socat_pid" > "$PID_FILE"
    
    # Verify the bridge started successfully
    sleep 0.3
    if ! kill -0 "$socat_pid" 2>/dev/null; then
        echo "[ERROR] socat bridge failed to start on port ${PROXY_PORT}" >&2
        exit 1
    fi
}

# ── Core: Stop socat Bridge ──────────────────────────────────────────────────
stop_socat_bridge() {
    kill_existing_bridge
}

# ── Core: Disconnect WARP Tunnel ─────────────────────────────────────────────
disconnect_warp() {
    if ip netns list | grep -q "$NS_NAME"; then
        ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" disconnect >/dev/null 2>&1 || true
        sleep 0.5  # Allow Cloudflare to fully release the tunnel
    fi
}

# ── Core: Cleanup Namespace ──────────────────────────────────────────────────
cleanup_namespace() {
    if ip netns list | grep -q "$NS_NAME"; then
        disconnect_warp
        ip netns del "$NS_NAME" 2>/dev/null || true
        echo "[System Config] Namespace $NS_NAME deleted."
    fi
    rm -rf "$CONF_DIR" "$PID_DIR"
}

# ── Actions ──────────────────────────────────────────────────────────────────
case "$ACTION" in
    "start")
        setup_namespace
        systemctl start "warp-node@${NODE_ID}.service"
        sleep 1.5
        configure_warp_client
        start_socat_bridge
        echo "[System Config] Node $NODE_ID active on SOCKS5 port $PROXY_PORT"
        ;;
        
    "recycle")
        echo "[System Config] Recycling Node $NODE_ID (high-speed tunnel reset)..."
        if ip netns list | grep -q "$NS_NAME"; then
            # Stop socat bridge during reset
            stop_socat_bridge
            
            # Force Cloudflare to assign new exit IP
            ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" disconnect >/dev/null 2>&1 || true
            sleep 1.0  # Critical: Cloudflare needs time to fully release
            
            ip netns exec "$NS_NAME" warp-cli --config-dir "$CONF_DIR" connect >/dev/null 2>&1 || true
            sleep 1.0  # Allow new tunnel to establish
            
            # Restart socat bridge
            start_socat_bridge
            echo "[System Config] Tunnel recycled. New exit IP assigned."
        else
            echo "[System Config] Namespace $NS_NAME missing. Initializing from scratch..."
            $0 "$NODE_ID" "start"
        fi
        ;;
        
    "stop")
        echo "[System Config] Shutting down Node $NODE_ID..."
        stop_socat_bridge
        disconnect_warp
        systemctl stop "warp-node@${NODE_ID}.service" 2>/dev/null || true
        echo "[System Config] Node $NODE_ID stopped."
        ;;
        
    "destroy")
        echo "[System Config] Destroying Node $NODE_ID and all associated state..."
        stop_socat_bridge
        systemctl stop "warp-node@${NODE_ID}.service" 2>/dev/null || true
        cleanup_namespace
        echo "[System Config] Node $NODE_ID fully destroyed."
        ;;
        
    "status")
        echo "=== Node $NODE_ID Status ==="
        if ip netns list | grep -q "$NS_NAME"; then
            echo "  Namespace: EXISTS"
            if systemctl is-active "warp-node@${NODE_ID}.service" &>/dev/null; then
                echo "  Service:   ACTIVE"
            else
                echo "  Service:   INACTIVE"
            fi
            if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
                echo "  Bridge:    RUNNING (PID: $(cat "$PID_FILE"))"
            else
                echo "  Bridge:    STOPPED"
            fi
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