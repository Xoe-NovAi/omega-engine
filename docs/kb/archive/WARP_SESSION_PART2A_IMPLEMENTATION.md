# 🔱 WARP Proxy Pool — Session Knowledge Capture (Part 2a: Implementation Patterns)
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ 2026-07-05

---

## §1 Systemd Service Patterns

### Template Units with Instance Parameters
```systemd
# warp-node@.service uses %i for instance-specific config
ExecStart=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-svc --config-dir /var/lib/cloudflare-warp-%i
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos mode proxy
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos proxy port %i
ExecStartPost=/usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli --accept-tos connect
```

### Oneshot Services with RemainAfterExit
```systemd
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c '...setup commands...'
ExecStop=/usr/bin/bash -c '...cleanup commands...'
```

### Sequential Execution via flock
```systemd
ExecStart=/usr/bin/flock -x /run/warp-reg-global.lock -c '...serialized commands...'
```

### Capability Bounding for Network Namespaces
```systemd
CapabilityBoundingSet=CAP_NET_ADMIN CAP_SYS_ADMIN
RestrictAddressFamilies=AF_INET AF_UNIX AF_NETLINK
NoNewPrivileges=true
```

### Resource Limits
```systemd
MemoryHigh=120M
MemoryMax=150M
CPUQuota=15%
```

---

## §2 Bash Patterns in ExecStart

### Multi-line Script with Proper Escaping
```systemd
ExecStart=/usr/bin/bash -c '\
  set -e; \
  VAR="value"; \
  command1 && \
  command2; \
'
```

### Systemd Variable Escaping
- `$$` → `$` (for bash variables)
- `%i` → instance number (1, 2, 3)
- `$${VAR}` → `${VAR}` in bash

### Background Process with Cleanup Trap
```bash
command & \
PID=$!; \
trap "kill $PID 2>/dev/null || true; wait $PID 2>/dev/null || true" EXIT;
```

### Polling Loop with Timeout
```bash
for i in $(seq 1 60); do
  if command &>/dev/null; then break; fi
  sleep 0.5
done
```

### Aggressive File Cleanup
```bash
chattr -i file1 file2 2>/dev/null || true
rm -rf file1 file2 file3-wal file3-shm
```

---

## §3 Network Namespace Operations

### Create Namespace + Veth Pair
```bash
ip netns add warp_node_1
ip link add veth_host_1 type veth peer name veth_ns_1
ip link set veth_ns_1 netns warp_node_1
```

### Configure Interfaces
```bash
# Host side
ip addr add 10.0.1.1/24 dev veth_host_1
ip link set veth_host_1 up

# Namespace side
ip netns exec warp_node_1 ip addr add 10.0.1.2/24 dev veth_ns_1
ip netns exec warp_node_1 ip link set veth_ns_1 up
ip netns exec warp_node_1 ip link set lo up
ip netns exec warp_node_1 ip route add default via 10.0.1.1
```

### NAT with iptables
```bash
DEFAULT_IF=$(ip route show default | awk '{print $5}' | head -1)
iptables -t nat -A POSTROUTING -s 10.0.1.0/24 -o "$DEFAULT_IF" -j MASQUERADE
```

### DNS in Namespace
```bash
mkdir -p /etc/netns/warp_node_1
echo "nameserver 1.1.1.1" > /etc/netns/warp_node_1/resolv.conf
echo "nameserver 8.8.8.8" >> /etc/netns/warp_node_1/resolv.conf
ip netns exec warp_node_1 mount --bind /etc/netns/warp_node_1/resolv.conf /etc/resolv.conf
```

---

## §4 WARP CLI Commands

### Registration Flow
```bash
# Must have warp-svc running first
warp-cli --accept-tos status          # Check IPC readiness
warp-cli --accept-tos settings reset  # Clear daemon memory
warp-cli --accept-tos registration new # Create new license
```

### Proxy Configuration
```bash
warp-cli --accept-tos mode proxy
warp-cli --accept-tos proxy port 8081
warp-cli --accept-tos connect
```

### Status Checks
```bash
warp-cli --accept-tos status          # IPC + connection status
warp-cli --accept-tos settings        # View current settings
```

---

## §5 Deploy Script Patterns

### Idempotent Cleanup
```bash
cleanup_stale_state() {
  # Stop host_warn "Cleaning stale state..."
  systemctl stop warp-svc 2>/dev/null || true
  pkill -9 warp-svc 2>/dev/null || true
  
  for i in $(seq 1 "$NODE_COUNT"); do
    rm -f "/var/run/netns/warp_node_${i}" 2>/dev/null || true
    ip netns del "warp_node_${i}" 2>/dev/null || true
  done
  
  rm -f /var/lib/cloudflare-warp/{reg,conf,warp.db,settings,final-overrides-settings}.json
  rm -f /var/lib/cloudflare-warp/warp.db{,-wal,-shm}
}
```

### Sequential Wait with Progress
```bash
wait_for_nodes() {
  local max_wait=300
  local waited=0
  while [[ $waited -lt $max_wait ]]; do
    local ready=0
    for i in $(seq 1 "$NODE_COUNT"); do
      systemctl is-active --quiet "warp-node@${i}.service" && ((ready++))
    done
    [[ $ready -eq "$NODE_COUNT" ]] && return 0
    sleep 3; ((waited += 3)); echo -n "."
  done
  return 1
}
```

### Per-Node Diagnostics
```bash
diagnose_node() {
  local i=$1
  echo "=== warp-node@${i} ==="
  systemctl status "warp-node@${i}.service" --no-pager -n 5
  echo "=== warp-reg@${i} ==="
  journalctl -u "warp-reg@${i}.service" --since "5 min ago" --no-pager -n 10
}
```

---

*Part 2a of 3 — Implementation Patterns*
*Next: Part 2b — Debugging Techniques & Lessons Learned*