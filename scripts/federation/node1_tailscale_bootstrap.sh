#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0
#
# NODE 1 (ASUS / kali-n1) TAILSCALE BOOTSTRAP
# Run this ON NODE 1 (ASUS ExpertBook)
#
# Node 0 (omega-hub) is already connected at 100.123.51.67
# Tailnet: xoe.nova.ai@gmail.com
# MagicDNS suffix: tail51f14a.ts.net

set -euo pipefail

echo "=== Node 1 Tailscale Bootstrap ==="
echo ""

# 1. Verify tailscale installed
if ! command -v tailscale >/dev/null 2>&1; then
    echo "[1/4] Tailscale not found — installing..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "[1/4] Tailscale already installed: $(tailscale version | head -1)"
fi

# 2. Start daemon
echo "[2/4] Ensuring tailscaled is active..."
sudo systemctl enable --now tailscaled
sleep 2
systemctl is-active tailscaled

# 3. Join the tailnet
echo "[3/4] Joining tailnet..."
echo ""
echo ">>> A login URL will appear. Visit it in your browser and authenticate"
echo ">>> with the SAME account as Node 0: xoe.nova.ai@gmail.com"
echo ""

# Interactive login (no tags — tags require ACL setup first)
sudo tailscale up --hostname=kali-n1 --operator="${USER}"

# 4. Verify
echo ""
echo "[4/4] Verification:"
tailscale status
echo ""
echo "Node 1 Tailscale IP: $(tailscale ip -4)"
echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "Next: On Node 0, run: tailscale status"
echo "You should see both 'omega-hub' and 'kali-n1' online."
echo ""
echo "Then test the wire from Node 1:"
echo "  tailscale ping omega-hub"
echo "  curl -s http://omega-hub.tail51f14a.ts.net:8016/mcp -o /dev/null -w '%{http_code}\\n'"
