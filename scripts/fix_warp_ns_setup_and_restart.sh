#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 W-1 full bring-up — fix truncated warp-ns-setup + start 3-node WARP pool
# AP: AP-WARP-NS-SETUP-FIX-v1.1.0
# Ticket: W-1 — docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md
#
# Requires ONE sudo password (unless already cached). Safe to re-run.
# After success: SOCKS5 on 127.0.0.1:8081, 8082, 8083
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${WARP_NS_SETUP_SRC:-/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh}"
TARGET="${WARP_NS_SETUP_DST:-/usr/local/bin/warp-ns-setup}"
BACKUP="/usr/local/bin/warp-ns-setup.bak.$(date +%Y%m%d%H%M%S)"
NODES=(1 2 3)
FULL_CHAIN="${WARP_FULL_CHAIN:-1}"  # set 0 to only fix script + prep

die() { echo "ERROR: $*" >&2; exit 1; }

if [[ ! -f "$SOURCE" ]]; then
  die "source script missing: $SOURCE"
fi
bash -n "$SOURCE" || die "source fails bash -n: $SOURCE"

echo "═══════════════════════════════════════════════════════════"
echo " W-1 WARP Proxy Pool Bring-Up"
echo "═══════════════════════════════════════════════════════════"

echo "[1/6] Install good warp-ns-setup + units from source repo"
if [[ -f "$TARGET" ]]; then
  sudo cp -a "$TARGET" "$BACKUP"
  echo "      backup: $BACKUP"
fi
sudo cp "$SOURCE" "$TARGET"
sudo chmod 755 "$TARGET"
sudo bash -n "$TARGET"
echo "      warp-ns-setup: $(wc -l < "$TARGET") lines"

# Also sync systemd units from source repo if present (canonical units live there now)
DEPLOY_SRC="${WARP_DEPLOY_SRC:-$(dirname "$SOURCE")/../deploy/infra/warp_pool}"
if [[ -d "$DEPLOY_SRC" ]]; then
  echo "      syncing systemd units from $DEPLOY_SRC"
  sudo cp "$DEPLOY_SRC"/*.service "$DEPLOY_SRC"/*.target /etc/systemd/system/ 2>/dev/null || true
  sudo systemctl daemon-reload
fi

echo "[2/6] Reset failed units"
for i in "${NODES[@]}"; do
  sudo systemctl reset-failed "warp-ns-prep@${i}" "warp-node@${i}" "warp-reg@${i}" \
    "warp-bridge@${i}" "socat-bridge@${i}" 2>/dev/null || true
done

echo "[3/6] Start warp-ns-prep@1..3 (namespace + veth + NAT)"
for i in "${NODES[@]}"; do
  sudo systemctl start "warp-ns-prep@${i}"
done
for i in "${NODES[@]}"; do
  st=$(systemctl is-active "warp-ns-prep@${i}" || true)
  echo "      warp-ns-prep@${i}: $st"
  [[ "$st" == "active" ]] || die "prep failed for node $i — journalctl -u warp-ns-prep@${i} -n 30"
done

if [[ "$FULL_CHAIN" != "1" ]]; then
  echo "[W-1] FULL_CHAIN=0 — stopped after prep. Start reg/node/bridge manually."
  exit 0
fi

echo "[4/6] Start warp-node@1..3 (warp-svc inside netns)"
for i in "${NODES[@]}"; do
  sudo systemctl start "warp-node@${i}" || true
done
# brief settle for warp-svc sockets
sleep 3

echo "[5/6] WARP registration + proxy mode (per node)"
# Host unit order is messy historically: reg After=node. Start reg after node is up.
for i in "${NODES[@]}"; do
  echo "      registering node $i..."
  if sudo systemctl start "warp-reg@${i}"; then
    echo "      warp-reg@${i}: ok"
  else
    echo "      warp-reg@${i}: FAILED — trying inline registration"
    # Fallback: same commands as unit ExecStart (needs working netns + silo bind)
    PORT=$((8080 + i))
    NS="warp_node_${i}"
    sudo ip netns exec "$NS" warp-cli --accept-tos registration delete 2>/dev/null || true
    sudo ip netns exec "$NS" warp-cli --accept-tos registration new
    sudo ip netns exec "$NS" warp-cli --accept-tos mode proxy
    sudo ip netns exec "$NS" warp-cli --accept-tos proxy port "$PORT"
    sudo ip netns exec "$NS" warp-cli --accept-tos connect
  fi
done
sleep 2

echo "[5.5/6] Patch known bridge unit bugs (so no manual sed needed)"
WARP_BRIDGE_UNIT="/etc/systemd/system/warp-bridge@.service"
if [[ -f "$WARP_BRIDGE_UNIT" ]] && grep -q 'warp-bridge-helper warp_node_%i 8081' "$WARP_BRIDGE_UNIT"; then
  echo "      patching warp-bridge@.service hardcoded internal port 8081 -> 808%i"
  sudo sed -i 's/warp-bridge-helper warp_node_%i 8081/warp-bridge-helper warp_node_%i 808%i/' "$WARP_BRIDGE_UNIT"
fi

SOCAT_BRIDGE_UNIT="/etc/systemd/system/socat-bridge@.service"
if [[ -f "$SOCAT_BRIDGE_UNIT" ]] && grep -q 'SystemCallFilter=~@privileged' "$SOCAT_BRIDGE_UNIT"; then
  echo "      patching socat-bridge@.service SystemCallFilter (was blocking setns/ip netns exec)"
  sudo sed -i '/^SystemCallFilter=~@privileged/d' "$SOCAT_BRIDGE_UNIT"
fi

WARP_NODE_UNIT="/etc/systemd/system/warp-node@.service"
if [[ -f "$WARP_NODE_UNIT" ]] && grep -q 'SystemCallFilter=~@privileged' "$WARP_NODE_UNIT"; then
  echo "      patching warp-node@.service SystemCallFilter (was blocking setns/ip netns exec)"
  sudo sed -i '/^SystemCallFilter=~@privileged/d' "$WARP_NODE_UNIT"
fi

if [[ -f "$WARP_BRIDGE_UNIT" ]] || [[ -f "$SOCAT_BRIDGE_UNIT" ]] || [[ -f "$WARP_NODE_UNIT" ]]; then
  sudo systemctl daemon-reload
fi

echo "[6/6] Start SOCKS bridges (warp-bridge@ and/or socat-bridge@)"
for i in "${NODES[@]}"; do
  if systemctl cat "warp-bridge@${i}.service" &>/dev/null; then
    sudo systemctl start "warp-bridge@${i}" || true
  fi
  if systemctl cat "socat-bridge@${i}.service" &>/dev/null; then
    sudo systemctl start "socat-bridge@${i}" || true
  fi
done

echo
echo "── Status ──"
for i in "${NODES[@]}"; do
  port=$((8080 + i))
  prep=$(systemctl is-active "warp-ns-prep@${i}" 2>/dev/null || echo n/a)
  node=$(systemctl is-active "warp-node@${i}" 2>/dev/null || echo n/a)
  br=$(systemctl is-active "warp-bridge@${i}" 2>/dev/null || echo n/a)
  sb=$(systemctl is-active "socat-bridge@${i}" 2>/dev/null || echo n/a)
  echo "  node $i  port=$port  prep=$prep  node=$node  warp-bridge=$br  socat-bridge=$sb"
done

echo
echo "── Listening ports ──"
ss -lntp 2>/dev/null | rg '808[1-3]' || echo "  (none on 8081-8083 yet)"

VALIDATE="$REPO_ROOT/docs/research/warp_proxy_pool/validate_warp_pool.sh"
if [[ -x "$VALIDATE" ]] || [[ -f "$VALIDATE" ]]; then
  echo
  echo "── Validate ──"
  bash "$VALIDATE" || echo "  validate script reported issues (see above)"
fi

echo
echo "── Python pool ──"
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  "$REPO_ROOT/.venv/bin/python" - <<'PY' || true
import anyio
from warp_proxy_pool import EphemeralWarpPool
async def main():
    p = EphemeralWarpPool()
    print("  ports:", p.ports)
    print("  active_port:", await p.get_active_port())
    h = await p.get_healthy_port()
    print("  healthy_port:", h)
anyio.run(main)
PY
fi

echo
echo "═══════════════════════════════════════════════════════════"
echo " W-1 bring-up finished. If ports still down, run:"
echo "   journalctl -u 'warp-ns-prep@1' -u 'warp-node@1' -u 'warp-reg@1' -n 50 --no-pager"
echo "═══════════════════════════════════════════════════════════"
