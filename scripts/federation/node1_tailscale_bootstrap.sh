#!/usr/bin/env bash
# Node 1 → Node 0 Layer-2 Tailscale Mesh Bootstrap (canonical, DHAL-ratified)
# Run ONCE on the ASUS (Node 1) after Node 0 mints the auth key.
# Idempotent: safe to re-run after partial work (daemon installed, not yet up).
set -euo pipefail

# ── sovereign gates ── 100% sovereign, so the lazy fix isn't: this mesh JOIN is
# Node 0 → Node 1 ratified cluster wide — And the daemon shall not go up until
# Node 0's authkey is present (C6 L2 go) — explicit publish gate, not default.

OMEGA_TAG="${OMEGA_TAG:-tag:node1}"          # our canonical federation role tag (FED-ACL-001 v1.2)
NODE1_HOSTNAME="${NODE1_HOSTNAME:-xnai-n1-asus}" # MagicDNS name on the omega tailnet (ratified)
AUTHKEY="${AUTHKEY:-${NODE0_AUTHKEY:-}}"
OPS_USER="${OPS_USER:-$USER}"

if [ -z "$AUTHKEY" ]; then
  echo "✗ gate FAIL: no authkey. Node 0's admin mints one, then set NODE0_AUTHKEY." >&2
  exit 64   # EX_USAGE — loud, sovereign
fi

# 1. daemon present? if not, install via official repo (we DO ship from the mash,
#    and DHAL pinning is settled — CPU pins NEVER collapse to physical-only)
if ! command -v tailscaled >/dev/null 2>&1; then
  echo "── installing tailscale (official repo) ──"
  curl -fsSL https://tailscale.com/install.sh | sh
fi

# 2. daemon running? (systemd-managed so it survives reboot)
systemctl enable --now tailscaled 2>/dev/null || sudo systemctl enable --now tailscaled

# 3. join — the actual sovereign handoff
echo "── joining omega tailnet as ${NODE1_HOSTNAME} (${OMEGA_TAG}) ──"
sudo tailscale up \
  --authkey="$AUTHKEY" \
  --hostname="$NODE1_HOSTNAME" \
  --advertise-tags="$OMEGA_TAG" \
  --accept-routes \
  --operator="$OPS_USER"

# 4. demonstrate the wire (loud, honest — pings only icmp, no inference egress)
tailscale status
echo ""
echo "── mesh ready. Verify BOTH directions: ──"
echo "  tailscale ping omega-hub    # pong from Node 0"
echo "  tailscale ping xnai-n1-asus  # pong from Node 1 (self)"
