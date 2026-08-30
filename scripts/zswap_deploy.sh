#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ZS-1: zswap + NVMe Swap Subsystem Deployment
# Per ADR-2026-08-10-001, D-526/D-581/D-584 ratified
# Config: max_pool_percent=25, compressor=lzo_rle, zpool=zsmalloc, swappiness=100
# zRAM DISABLED, 16GB NVMe swap file (ZS-2)

set -euo pipefail

echo "=== ZS-1: zswap Runtime Configuration ==="

# 1. Enable zswap at runtime (requires root)
echo "Enabling zswap..."
echo 1 > /sys/module/zswap/parameters/enabled
echo "zswap.enabled = $(cat /sys/module/zswap/parameters/enabled)"

# 2. Set max_pool_percent=25
echo "Setting max_pool_percent=25..."
echo 25 > /sys/module/zswap/parameters/max_pool_percent
echo "max_pool_percent = $(cat /sys/module/zswap/parameters/max_pool_percent)"

# 3. Set compressor=lzo_rle
echo "Setting compressor=lzo_rle..."
echo lzo_rle > /sys/module/zswap/parameters/compressor
echo "compressor = $(cat /sys/module/zswap/parameters/compressor)"

# 4. Verify zpool=zsmalloc (already set)
echo "zpool = $(cat /sys/module/zswap/parameters/zpool)"

# 5. Set swappiness=100 (runtime + persistent)
echo "Setting vm.swappiness=100..."
sysctl -w vm.swappiness=100
echo "vm.swappiness = $(cat /proc/sys/vm/swappiness)"

# 6. Persist swappiness
cat > /etc/sysctl.d/99-omega-zswap.conf << 'SYSCTL_EOF'
# Omega Engine zswap subsystem (ZS-1)
# Per ADR-2026-08-10-001, D-526/D-581/D-584
vm.swappiness = 100
SYSCTL_EOF
echo "Persisted to /etc/sysctl.d/99-omega-zswap.conf"

echo ""
echo "=== ZS-1 Runtime Config Complete ==="
echo "Current zswap state:"
cat /sys/module/zswap/parameters/enabled
cat /sys/module/zswap/parameters/max_pool_percent
cat /sys/module/zswap/parameters/compressor
cat /sys/module/zswap/parameters/zpool
echo "swappiness: $(cat /proc/sys/vm/swappiness)"

echo ""
echo "=== ZS-1 Kernel Cmdline (Persistent - Requires Reboot) ==="
echo "Add to GRUB_CMDLINE_LINUX_DEFAULT in /etc/default/grub:"
echo '  zswap.enabled=1 zswap.max_pool_percent=25 zswap.compressor=lzo_rle zswap.zpool=zsmalloc'
echo ""
echo "Then run: update-grub && reboot"
echo ""
echo "=== ZS-2 (Next): 16GB NVMe Swap File ==="
echo "See scripts/zswap_nvme_swap.sh for ZS-2 (swap file + systemd unit)"
