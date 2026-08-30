#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# WARP Network Namespace Setup Script
# Called by warp-ns-prep@.service
# AP: AP-WARP-NS-SETUP-SCRIPT-v1.0.0

set -euo pipefail

INSTANCE="${1:-1}"
NS="warp_node_${INSTANCE}"
VETH_HOST="veth_host_${INSTANCE}"
VETH_NS="veth_ns_${INSTANCE}"
SUBNET="10.0.${INSTANCE}"
HOST_IP="${SUBNET}.1"
NS_IP="${SUBNET}.2"

# Skip if namespace already exists and veth is up
if ip netns list 2>/dev/null | grep -q "^${NS}$" && \
   ip link show "${VETH_HOST}" &>/dev/null; then
    exit 0
fi

# Clean stale state
rm -f /var/run/netns/"${NS}" 2>/dev/null || true
ip link del "${VETH_HOST}" 2>/dev/null || true

# 1. Create namespace
/usr/sbin/ip netns add "${NS}"

# 2. Create veth pair
/usr/sbin/ip link add "${VETH_HOST}" type veth peer name "${VETH_NS}"

# 3. Move veth_ns into namespace
/usr/sbin/ip link set "${VETH_NS}" netns "${NS}"

# 4. Configure host side
/usr/sbin/ip addr add "${HOST_IP}/24" dev "${VETH_HOST}"
/usr/sbin/ip link set "${VETH_HOST}" up

# 5. Configure namespace side
/usr/sbin/ip netns exec "${NS}" /usr/sbin/ip addr add "${NS_IP}/24" dev "${VETH_NS}"
/usr/sbin/ip netns exec "${NS}" /usr/sbin/ip link set "${VETH_NS}" up
/usr/sbin/ip netns exec "${NS}" /usr/sbin/ip link set lo up
/usr/sbin/ip netns exec "${NS}" /usr/sbin/ip route add default via "${HOST_IP}"

# 5b. 2026 MTU & TCP Tuning
/usr/sbin/ip link set "${VETH_HOST}" mtu 1420
/usr/sbin/ip netns exec "${NS}" /usr/sbin/ip link set "${VETH_NS}" mtu 1420
/usr/sbin/sysctl -w net.ipv4.tcp_keepalive_time=60 >/dev/null 2>&1 || true
/usr/sbin/sysctl -w net.ipv4.tcp_fin_timeout=15 >/dev/null 2>&1 || true
/usr/sbin/sysctl -w net.core.rmem_max=16777216 >/dev/null 2>&1 || true
/usr/sbin/sysctl -w net.core.wmem_max=16777216 >/dev/null 2>&1 || true

# 6. Enable IP forwarding (idempotent)
/usr/sbin/sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 || true

# 7. Detect default outbound interface
DEFAULT_IF=$(/usr/sbin/ip route show default | /usr/bin/awk '{print $5}' | /usr/bin/head -1)

# 8. NAT for outbound traffic from namespace
/usr/sbin/iptables -t nat -C POSTROUTING -s "${SUBNET}.0/24" -o "${DEFAULT_IF}" -j MASQUERADE 2>/dev/null || \
  /usr/sbin/iptables -t nat -A POSTROUTING -s "${SUBNET}.0/24" -o "${DEFAULT_IF}" -j MASQUERADE

# 9. Configure DNS in namespace (bind mount resolv.conf with public DNS)
mkdir -p /etc/netns/"${NS}"
echo "nameserver 1.1.1.1" > /etc/netns/"${NS}"/resolv.conf
echo "nameserver 8.8.8.8" >> /etc/netns/"${NS}"/resolv.conf
/usr/sbin/ip netns exec "${NS}" mount --bind /etc/netns/"${NS}"/resolv.conf /etc/resolv.conf

# 10. Create persistent namespace reference for ip netns exec from other services
/usr/bin/ln -sf /proc/$$/ns/net /var/run/netns/"${NS}" 2>/dev/null || true