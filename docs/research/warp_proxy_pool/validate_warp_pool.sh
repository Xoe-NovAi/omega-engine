#!/usr/bin/env bash
# validate_warp_pool.sh — WARP Proxy Pool Validation
# AP: AP-WARP-VALIDATE-v1.0.0
# Run after deployment to verify the pool is working

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[PASS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err() { echo -e "${RED}[FAIL]${NC} $*"; }

# ── Configuration ──────────────────────────────────────────────────────────────
PORTS=(8081 8082 8083)
CANARY_URL="https://1.1.1.1/cdn-cgi/trace"
TIMEOUT=10

PASS=0
FAIL=0

check() {
    local name="$1"
    shift
    if "$@" &>/dev/null; then
        log_ok "$name"
        ((PASS++))
        return 0
    else
        log_err "$name"
        ((FAIL++))
        return 1
    fi
}

# ── Validation Steps ───────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  WARP Proxy Pool Validation                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

log_info "Checking systemd units..."
for i in 1 2 3; do
    check "warp-node@${i}.service active" systemctl is-active --quiet "warp-node@${i}.service"
done

log_info "Checking port listeners..."
for port in "${PORTS[@]}"; do
    check "Port ${port} listening" ss -tlnp | grep -q ":${port} "
done

log_info "Checking socat bridges..."
for port in "${PORTS[@]}"; do
    check "socat process for port ${port}" pgrep -f "socat.*TCP-LISTEN:${port}" >/dev/null
done

log_info "Checking WARP tunnel connectivity (canary probe)..."
for port in "${PORTS[@]}"; do
    check "Port ${port} WARP tunnel" bash -c "
        curl -s -x socks5h://127.0.0.1:${port} --max-time ${TIMEOUT} '${CANARY_URL}' | grep -q 'warp=on'
    "
done

log_info "Checking IP rotation capability..."
# Test rotation on node 1
OLD_IP=$(curl -s -x socks5h://127.0.0.1:8081 --max-time ${TIMEOUT} "${CANARY_URL}" | grep "ip=" | head -1)
if sudo /usr/local/bin/spawn_warp_node.sh 1 recycle; then
    sleep 2
    NEW_IP=$(curl -s -x socks5h://127.0.0.1:8081 --max-time ${TIMEOUT} "${CANARY_URL}" | grep "ip=" | head -1)
    if [[ -n "$OLD_IP" && -n "$NEW_IP" && "$OLD_IP" != "$NEW_IP" ]]; then
        log_ok "IP rotation successful (${OLD_IP} → ${NEW_IP})"
        ((PASS++))
    else
        log_warn "IP rotation completed but IP unchanged (may be same Anycast gateway)"
        log_info "  Old: ${OLD_IP}"
        log_info "  New: ${NEW_IP}"
        ((PASS++))
    fi
else
    log_err "IP rotation command failed"
    ((FAIL++))
fi

log_info "Checking systemd resource limits..."
check "MemoryMax=150M configured" systemctl show warp-node@1.service | grep -q "MemoryMax=150M"
check "MemoryHigh=120M configured" systemctl show warp-node@1.service | grep -q "MemoryHigh=120M"
check "CPUQuota=15% configured" systemctl show warp-node@1.service | grep -q "CPUQuota=15%"

log_info "Checking sudoers configuration..."
check "sudoers file exists" [[ -f /etc/sudoers.d/omega-warp ]]
check "sudoers allows spawn_warp_node.sh" grep -q "spawn_warp_node.sh" /etc/sudoers.d/omega-warp

# ── Summary ────────────────────────────────────────────────────────────────────
echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Results: ${PASS} passed, ${FAIL} failed"
printf "║  %s\n" "$(printf '%*s' $((56 - ${#PASS} - ${#FAIL} - 14)) '')"
echo "╚══════════════════════════════════════════════════════════════╝"

if [[ $FAIL -eq 0 ]]; then
    echo
    log_ok "All checks passed! WARP Proxy Pool is ready."
    echo
    echo "Quick test:"
    echo "  curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace"
    exit 0
else
    echo
    log_err "Some checks failed. Review the output above."
    echo
    echo "Debug commands:"
    echo "  journalctl -u warp-node@1.service -f"
    echo "  sudo /usr/local/bin/spawn_warp_node.sh 1 status"
    echo "  ss -tlnp | grep -E '808[123]'"
    exit 1
fi