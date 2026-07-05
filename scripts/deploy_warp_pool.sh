#!/usr/bin/env bash
# deploy_warp_pool.sh — WARP Proxy Pool System Deployment
# AP: AP-WARP-DEPLOY-v1.4.0
# Run with: sudo ./deploy_warp_pool.sh
# Idempotent: safe to run multiple times. Cleans up stale state.

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()   { echo -e "${RED}[ERR]${NC} $*"; }
log_step()  { echo -e "${CYAN}[STEP]${NC} $*"; }

# ── Configuration ──────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_SOURCE="${REPO_ROOT}/scripts/spawn_warp_node.sh"
SERVICE_SOURCE_DIR="${REPO_ROOT}/deploy/infra/warp_pool"
SYSTEMD_DIR="/etc/systemd/system"
SUDOERS_DIR="/etc/sudoers.d"
SCRIPT_DEST="/usr/local/bin/spawn_warp_node.sh"
SUDOERS_FILE="${SUDOERS_DIR}/omega-warp"

# All 5 systemd units to deploy
SERVICE_UNITS=(
    "warp-ns-prep@.service"
    "warp-reg@.service"
    "warp-node@.service"
    "socat-bridge@.service"
    "warp-pool.target"
)

# Number of WARP nodes to run
NODE_COUNT=3

# ── Pre-flight Checks ──────────────────────────────────────────────────────────
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_err "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_source_files() {
    local missing=0
    if [[ ! -f "${SCRIPT_SOURCE}" ]]; then
        log_err "Missing: ${SCRIPT_SOURCE}"
        missing=1
    fi
    for unit in "${SERVICE_UNITS[@]}"; do
        if [[ ! -f "${SERVICE_SOURCE_DIR}/${unit}" ]]; then
            log_err "Missing: ${SERVICE_SOURCE_DIR}/${unit}"
            missing=1
        fi
    done
    if [[ $missing -eq 1 ]]; then
        log_err "Run from the omega-engine repository root"
        exit 1
    fi
    log_ok "All source files present"
}

check_dependencies() {
    local missing=0
    local install_pkgs=()

    # Required: iproute2 (provides 'ip')
    if ! command -v ip &>/dev/null; then
        log_err "Missing: ip (iproute2)"
        install_pkgs+=("iproute2")
        missing=1
    fi

    # Required: systemctl (systemd)
    if ! command -v systemctl &>/dev/null; then
        log_err "Missing: systemctl — cannot proceed without systemd"
        exit 1
    fi

    # Required: socat (host-to-namespace bridge)
    if ! command -v socat &>/dev/null; then
        log_err "Missing: socat"
        install_pkgs+=("socat")
        missing=1
    fi

    # Required: warp-svc and warp-cli (Cloudflare WARP)
    if ! command -v warp-svc &>/dev/null; then
        log_err "Missing: warp-svc (cloudflare-warp)"
        log_info "Install: curl -fsSL https://pkg.cloudflareclient.com/install.sh | sudo bash"
        missing=1
    fi
    if ! command -v warp-cli &>/dev/null; then
        log_err "Missing: warp-cli (cloudflare-warp)"
        log_info "Install: curl -fsSL https://pkg.cloudflareclient.com/install.sh | sudo bash"
        missing=1
    fi

    # Recommended: curl (for WARP validation)
    if ! command -v curl &>/dev/null; then
        log_warn "Missing: curl (recommended for WARP tunnel validation)"
        install_pkgs+=("curl")
    fi

    if [[ $missing -eq 1 ]]; then
        log_err "Cannot proceed. Install missing packages:"
        [[ ${#install_pkgs[@]} -gt 0 ]] && log_info "  sudo apt install -y ${install_pkgs[*]}"
        exit 1
    fi

    [[ ${#install_pkgs[@]} -gt 0 ]] && log_warn "Recommended: sudo apt install -y ${install_pkgs[*]}"
    log_ok "All dependencies satisfied"
}

check_kernel_support() {
    if ! ip netns list &>/dev/null; then
        log_err "Network namespace support unavailable — check CONFIG_NET_NS=y in kernel"
        exit 1
    fi
    log_ok "Kernel namespace support verified"
}

detect_deploy_user() {
    DEPLOY_USER="${SUDO_USER:-}"
    if [[ -z "${DEPLOY_USER}" ]]; then
        DEPLOY_USER="$(logname 2>/dev/null || echo "")"
    fi
    if [[ -z "${DEPLOY_USER}" ]]; then
        log_warn "Cannot detect non-root user — defaulting sudoers to 'arcana-novai'"
        DEPLOY_USER="arcana-novai"
    fi
    log_info "Deploy user: ${DEPLOY_USER}"
}

# ── Cleanup (idempotent) ──────────────────────────────────────────────────────
cleanup_stale_state() {
    log_step "Cleaning up stale state..."

    # Stop host warp-svc (must NOT be running — it holds registration in memory)
    systemctl stop warp-svc 2>/dev/null || true
    systemctl disable warp-svc 2>/dev/null || true
    log_info "  Stopped/disabled host warp-svc (prevents IPC registration conflicts)"

    # Stop pool target if running
    systemctl stop warp-pool.target 2>/dev/null || true

    # Stop all node services and reset failure counts
    for i in $(seq 1 "${NODE_COUNT}"); do
        for unit in "warp-node@${i}" "warp-reg@${i}" "warp-ns-prep@${i}" "socat-bridge@${i}"; do
            systemctl stop "${unit}.service" 2>/dev/null || true
            systemctl reset-failed "${unit}.service" 2>/dev/null || true
        done
    done

    # Also stop old-format socat-bridge instances (port-based, pre-v1.2)
    for port in 8081 8082 8083; do
        systemctl stop "socat-bridge@${port}.service" 2>/dev/null || true
        systemctl reset-failed "socat-bridge@${port}.service" 2>/dev/null || true
    done

    # Remove stale network namespace bind mounts
    for i in $(seq 1 "${NODE_COUNT}"); do
        # Remove stale bind mount file if leftover from unclean shutdown
        rm -f "/var/run/netns/warp_node_${i}" 2>/dev/null || true

        # Also try proper namespace deletion
        if ip netns list 2>/dev/null | grep -q "warp_node_${i}"; then
            ip netns del "warp_node_${i}" 2>/dev/null || true
            log_info "  Removed stale namespace: warp_node_${i}"
        fi
    done

    # Nuke ALL host WARP registration state (warp-cli has no --config-dir flag)
    rm -f /var/lib/cloudflare-warp/reg.json \
          /var/lib/cloudflare-warp/conf.json \
          /var/lib/cloudflare-warp/warp.db \
          /var/lib/cloudflare-warp/settings.json \
          /var/lib/cloudflare-warp/final-overrides-settings.json
    log_info "  Cleared host WARP registration files"

    log_ok "Stale state cleaned"
}

# ── Deployment Steps ───────────────────────────────────────────────────────────
deploy_script() {
    log_step "Deploying spawn_warp_node.sh..."
    cp "${SCRIPT_SOURCE}" "${SCRIPT_DEST}"
    chmod 755 "${SCRIPT_DEST}"
    log_ok "  ${SCRIPT_DEST}"
}

deploy_systemd_units() {
    log_step "Deploying ${#SERVICE_UNITS[@]} systemd units..."
    for unit in "${SERVICE_UNITS[@]}"; do
        cp "${SERVICE_SOURCE_DIR}/${unit}" "${SYSTEMD_DIR}/"
        log_ok "  ${SYSTEMD_DIR}/${unit}"
    done
}

configure_sudoers() {
    log_step "Configuring sudoers for ${DEPLOY_USER}..."
    cat > "${SUDOERS_FILE}" <<EOF
# Omega Engine WARP Proxy Pool — auto-generated by deploy_warp_pool.sh
# Allows ${DEPLOY_USER} to manage WARP node services without password
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl start warp-node@*, /usr/bin/systemctl stop warp-node@*, /usr/bin/systemctl restart warp-node@*, /usr/bin/systemctl status warp-node@*
${DEPLOY_USER} ALL=(ALL) NOPASSWD: ${SCRIPT_DEST} *
EOF
    chmod 440 "${SUDOERS_FILE}"
    log_ok "  ${SUDOERS_FILE}"
}

reload_systemd() {
    log_step "Reloading systemd daemon..."
    systemctl daemon-reload
    log_ok "Daemon reloaded"
}

enable_and_start_pool() {
    log_step "Enabling and starting warp-pool.target (${NODE_COUNT} nodes)..."
    systemctl enable warp-pool.target
    systemctl start warp-pool.target
    log_ok "Pool target started"
}

wait_for_nodes() {
    log_step "Waiting for WARP nodes to become active (up to 120s)..."
    local max_wait=120
    local waited=0

    while [[ $waited -lt $max_wait ]]; do
        local ready=0
        for i in $(seq 1 "${NODE_COUNT}"); do
            if systemctl is-active --quiet "warp-node@${i}.service" 2>/dev/null; then
                ((ready++))
            fi
        done

        if [[ $ready -eq "${NODE_COUNT}" ]]; then
            echo
            log_ok "All ${NODE_COUNT} WARP nodes active"
            return 0
        fi

        sleep 3
        ((waited += 3))
        echo -n "."
    done

    echo
    log_warn "Timeout after ${max_wait}s — ${ready}/${NODE_COUNT} nodes active"
    echo
    diagnose_failures
    return 1
}

diagnose_failures() {
    log_info "Diagnosing failed nodes..."
    for i in $(seq 1 "${NODE_COUNT}"); do
        local state sub
        state=$(systemctl show "warp-node@${i}.service" --property=ActiveState --value 2>/dev/null || echo "unknown")
        sub=$(systemctl show "warp-node@${i}.service" --property=SubState --value 2>/dev/null || echo "unknown")

        if [[ "${state}" == "active" && "${sub}" == "running" ]]; then
            log_ok "  warp-node@${i}: active/running"
            continue
        fi

        log_warn "  warp-node@${i}: ${state}/${sub}"

        # Check if namespace exists
        if ip netns list 2>/dev/null | grep -q "warp_node_${i}"; then
            log_info "    Namespace: EXISTS"
        else
            log_err "    Namespace: MISSING"
        fi

        # Check ns-prep dependency
        local ns_state
        ns_state=$(systemctl show "warp-ns-prep@${i}.service" --property=ActiveState --value 2>/dev/null || echo "unknown")
        if [[ "${ns_state}" != "active" ]]; then
            log_err "    warp-ns-prep@${i}: ${ns_state} — namespace creation failed"
        fi

        # Check reg dependency
        local reg_state
        reg_state=$(systemctl show "warp-reg@${i}.service" --property=ActiveState --value 2>/dev/null || echo "unknown")
        if [[ "${reg_state}" != "active" ]]; then
            log_warn "    warp-reg@${i}: ${reg_state} — registration may need first-boot"
        fi

        # Show last 5 journal lines
        log_info "    Last log lines:"
        journalctl -u "warp-node@${i}.service" -n 5 --no-pager 2>/dev/null | sed 's/^/      /' || true
        echo
    done
}

# ── Validation ─────────────────────────────────────────────────────────────────
run_validation() {
    log_step "Running validation..."
    local validation_script="${REPO_ROOT}/docs/research/warp_proxy_pool/validate_warp_pool.sh"

    if [[ -f "${validation_script}" ]]; then
        chmod +x "${validation_script}"
        if bash "${validation_script}"; then
            log_ok "Validation PASSED"
            return 0
        else
            log_err "Validation FAILED"
            return 1
        fi
    fi

    log_warn "Validation script not found — running manual checks..."
    manual_validation
}

manual_validation() {
    local all_ok=1
    local active_nodes=0

    # Check nodes
    for i in $(seq 1 "${NODE_COUNT}"); do
        if systemctl is-active --quiet "warp-node@${i}.service" 2>/dev/null; then
            log_ok "warp-node@${i}.service: ACTIVE"
            ((active_nodes++))
        else
            log_err "warp-node@${i}.service: INACTIVE"
            all_ok=0
        fi
    done

    # Check ports for active nodes
    for i in $(seq 1 "${NODE_COUNT}"); do
        local port=$((8080 + i))
        if ss -tlnp 2>/dev/null | grep -q ":${port} "; then
            log_ok "Port ${port}: LISTENING"
        else
            log_warn "Port ${port}: NOT LISTENING (socat bridge may need manual start)"
        fi
    done

    # WARP tunnel check on active nodes
    for i in $(seq 1 "${NODE_COUNT}"); do
        local port=$((8080 + i))
        local trace
        trace=$(curl -s -x "socks5h://127.0.0.1:${port}" --max-time 10 "https://1.1.1.1/cdn-cgi/trace" 2>/dev/null || echo "")
        if echo "${trace}" | grep -q "warp=on"; then
            local ip
            ip=$(echo "${trace}" | grep "^ip=" | cut -d= -f2)
            log_ok "Port ${port}: WARP verified (exit: ${ip})"
        else
            log_warn "Port ${port}: WARP tunnel not ready (may still be connecting)"
        fi
    done

    echo
    log_info "Active nodes: ${active_nodes}/${NODE_COUNT}"
    return $all_ok
}

# ── Summary ────────────────────────────────────────────────────────────────────
print_summary() {
    echo
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  WARP Proxy Pool — Deployment Complete                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo
    echo "Deployed:"
    echo "  ${SCRIPT_DEST}"
    for unit in "${SERVICE_UNITS[@]}"; do
        echo "  ${SYSTEMD_DIR}/${unit}"
    done
    echo "  ${SUDOERS_FILE}"
    echo
    echo "Node Map:"
    for i in $(seq 1 "${NODE_COUNT}"); do
        echo "  Node ${i}: socks5h://127.0.0.1:$((8080 + i))"
    done
    echo
    echo "Service Management:"
    echo "  Status:  systemctl status warp-pool.target"
    echo "  Logs:    journalctl -u warp-node@1.service -f"
    echo "  Restart: systemctl restart warp-pool.target"
    echo "  Stop:    systemctl stop warp-pool.target"
    echo
    echo "Manual Node Control (as root or via sudo):"
    echo "  Recycle node 1:  ${SCRIPT_DEST} 1 recycle"
    echo "  Status node 1:   ${SCRIPT_DEST} 1 status"
    echo "  Destroy node 1:  ${SCRIPT_DEST} 1 destroy"
    echo
    echo "Quick Test:"
    echo "  curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace"
    echo
    echo "Omega Engine Integration:"
    echo "  config/providers.yaml → opencode-zen → extra → proxy_url: socks5h://127.0.0.1:8081"
    echo "  Then: omega talk 'test' — check logs for 'WARP proxy injected'"
    echo
}

# ── Main ───────────────────────────────────────────────────────────────────────
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  WARP Proxy Pool — System Deployment (v1.3.0)               ║"
    echo "║  Idempotent — safe to run multiple times                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo

    # ── Phase 1: Pre-flight ──
    check_root
    check_source_files
    check_dependencies
    check_kernel_support
    detect_deploy_user

    echo
    # ── Phase 2: Cleanup stale state ──
    cleanup_stale_state

    echo
    # ── Phase 3: Deploy ──
    deploy_script
    deploy_systemd_units
    configure_sudoers
    reload_systemd
    enable_and_start_pool

    echo
    # ── Phase 4: Wait + Validate ──
    if wait_for_nodes; then
        run_validation
        print_summary
        exit 0
    else
        log_err "Some nodes failed to start. See diagnosis above."
        log_info "Retry: sudo ./scripts/deploy_warp_pool.sh"
        exit 1
    fi
}

main "$@"
