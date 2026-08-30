# 🔱 Omega Engine — WARP Proxy Pool Validation Strategy
⬡ OMEGA ⬡ RESEARCHER ⬡ validation ⬡ netns ⬡ trc_core ⬡ VALIDATION-SPEC

**AP Token**: `AP-WARP-VALIDATION-v1.0.0`
**Status**: READY FOR EXECUTION | **Last Updated**: 2026-07-04
**Source**: Google Search Assistant (Gemini) + MiMo-V2.5 Review

---

## §0 Purpose

This document provides a comprehensive end-to-end validation strategy for the Multi-Namespace WARP Proxy Pool. Execute these tests **before** production deployment to verify the system works as designed.

---

## §1 Namespace Isolation Verification

### §1.1 Socket Visibility Isolation
Verify that sockets bound inside a specific namespace are completely invisible to other namespaces.

```bash
# This MUST show the internal proxy port (e.g., 8081)
sudo ip netns exec warp_node_1 ss -tlnp

# This must NOT show port 8081
sudo ip netns exec warp_node_2 ss -tlnp
```

**Expected Result**: Port 8081 appears only in `warp_node_1`, not in `warp_node_2`.

### §1.2 Active Traffic Capture
Bind `tcpdump` to the virtual interface inside the namespace to trace outbound packets.

**Terminal 1** (start capture):
```bash
sudo ip netns exec warp_node_1 tcpdump -nn -i any port 443
```

**Terminal 2** (generate traffic):
```bash
curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace
```

**Expected Result**: Traffic appears only in `warp_node_1`'s dump; `warp_node_2` remains silent.

---

## §2 Socat Bridge Connectivity Test

Execute `curl` with verbose output to trace the full loopback-to-namespace transaction chain:

```bash
curl -v -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace
```

**Key Detail**: Using `socks5h://` instead of `socks5://` forces DNS resolution to happen remotely through the WARP exit node, preventing local DNS leaks.

**Expected Output**:
- SOCKS5 handshake succeeds
- TLS negotiation completes
- Response contains `warp=on`

---

## §3 IP Rotation Validation

Query `https://1.1.1.1/cdn-cgi/trace` sequentially (before and after) to confirm a true path mutation:

```bash
# Capture old IP
old_ip=$(curl -s -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace | grep "ip=")

# Trigger rotation
sudo /usr/local/bin/spawn_warp_node.sh 1 recycle

# Capture new IP
new_ip=$(curl -s -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace | grep "ip=")

# Compare
echo -e "Old Vector: $old_ip\nNew Vector: $new_ip"
```

**Expected Result**: If the IP string matches, the tunnel re-established to the same Anycast gateway. If it shifts, rotation successfully triggered a new edge node assignment.

---

## §4 Canary Probe Reliability

### §4.1 The `colo=` Field (Informational Only)
The `colo=` field returns a 3-letter IATA airport code (e.g., MIA, ORD) representing the active Cloudflare data center.

**Important**: Because your machine sits in a fixed geographic location, Cloudflare's Anycast routing will almost always route to the same physical ingress datacenter. A change in `colo` means traffic switched physical paths completely, but a successful rotation frequently assigns a new IP within the same local datacenter block.

**Implementation**: Do **not** reject a probe just because `colo` remains identical. Use `colo` purely as informational telemetry. Rely strictly on `ip=` changes to confirm true rotation.

### §4.2 Current Canary Probe (Production)
```python
async def _run_canary_probe(self, port: int) -> Optional[str]:
    """Returns exit IP if successful, None otherwise."""
    proxy_url = f"socks5://127.0.0.1:{port}"
    timeout = httpx.Timeout(2.5)
    limits = httpx.Limits(max_keepalive_connections=0, max_connections=1, keepalive_expiry=0.0)
    
    await anyio.sleep(0.5)
    
    try:
        async with httpx.AsyncClient(proxies=proxy_url, limits=limits, timeout=timeout) as client:
            response = await client.get("https://1.1.1.1/cdn-cgi/trace")
            if response.status_code == 200:
                lines = response.text.split("\n")
                trace_data = {k: v for line in lines if "=" in line for k, v in [line.split("=", 1)]}
                
                if trace_data.get("warp") == "on" and "ip" in trace_data:
                    return trace_data["ip"]
    except Exception as e:
        logger.debug(f"Canary probe failed on port {port}: {e!r}")
    return None
```

---

## §5 Systemd Resource Limits Validation

### §5.1 Static Manifest Check
Verify that systemd has integrated the configuration profile:

```bash
systemctl show warp-node@1.service | grep -E "Memory(Current|Max|High)|CPUQuota"
```

**Expected Output**:
```
MemoryCurrent=45M  # (or similar, below 120M)
MemoryMax=150M
MemoryHigh=120M
CPUQuota=15%
```

### §5.2 Dynamic Telemetry Tracking
Monitor live control group utilization under stress:

```bash
# Real-time monitoring
systemd-cgtop

# Or monitor specific unit
systemctl status warp-node@1.service
```

---

## §6 Performance Benchmarks

### §6.1 Latency Overhead
The socat bridge overhead is typically < 0.5 milliseconds for simple streaming socket descriptor bridging.

**Measurement Command**:
```bash
time curl -w "Connect: %{time_connect}s\nTotal: %{time_total}s\n" \
    -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace
```

**Expected Results**:
| Metric | Good | Degraded |
|--------|------|----------|
| Total execution time | < 150ms | > 600ms |
| `time_connect` (SOCKS handshake) | < 5ms | > 50ms |

**Degraded Signals**: Local SOCKS descriptor exhaustion or severe buffer bloat on upstream Cloudflare route.

---

## §7 Failure Recovery Test

### §7.1 Detection Mechanics
When socat dies:
1. Port listener drops instantly
2. Next Python request throws `httpx.ConnectError` or `ConnectionRefusedError`
3. `try/except` catches error, triggers `signal_rotation(port)`
4. Port passed to `_background_reset_worker`

### §7.2 Safe Simulation
```bash
# 1. Kill the active host bridge process
sudo kill -9 $(cat /run/cloudflare-warp-1/socat_bridge.pid)

# 2. Check Python runtime logs (should see):
#    "[Omega-Engine] Sockets snapped or timed out via port 8081..."
#    "[Omega-Proxy] Recycling Warp Node ID: 1 (Port 8081)..."

# 3. Verify automatic recovery
#    The shell script's recycle block will automatically redeploy the socat listener
```

### §7.3 Validation Script
```bash
#!/usr/bin/env bash
# validate_failure_recovery.sh
set -euo pipefail

NODE_ID=${1:-1}
PORT=$((8080 + NODE_ID))
PID_FILE="/run/cloudflare-warp-${NODE_ID}/socat_bridge.pid"

echo "=== Failure Recovery Test: Node $NODE_ID ==="

# Capture initial state
echo "[1/4] Initial state:"
ss -tlnp | grep ":${PORT} " || echo "  Port ${PORT} not listening"

# Kill the bridge
echo "[2/4] Killing socat bridge..."
sudo kill -9 $(cat "$PID_FILE") 2>/dev/null || true
sleep 0.5

# Verify port is down
echo "[3/4] Port status after kill:"
ss -tlnp | grep ":${PORT} " || echo "  Port ${PORT} correctly DOWN"

# Trigger recovery via recycle
echo "[4/4] Triggering recovery..."
sudo /usr/local/bin/spawn_warp_node.sh $NODE_ID recycle

# Verify recovery
echo "Port status after recycle:"
ss -tlnp | grep ":${PORT} " && echo "  Port ${PORT} correctly RECOVERED" || echo "  Port ${PORT} FAILED to recover"
```

---

## §8 Concurrent Load Testing

### §8.1 Why Standard Tools Fail
`ab` and `wrk` are designed for raw HTTP/HTTPS protocols, not SOCKS5 handshakes.

### §8.2 Correct Tools
- **`iperf3`**: Inside the namespace for raw interface metrics
- **`k6`**: With native SOCKS5 proxy transport extension modules

### §8.3 File Descriptor Limit (Critical)
Each concurrent connection occupies 3 distinct sockets (App → Socat → Warp-Svc → Internet). Ensure the `arcana-novai` user has maximum file open limit bumped to at least 65535:

```bash
# Check current limit
ulimit -n

# Set permanent limit
echo "arcana-novai soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "arcana-novai hard nofile 65535" | sudo tee -a /etc/security/limits.conf
```

### §8.4 Systemd Override (Alternative)
```bash
sudo mkdir -p /etc/systemd/system/warp-node@.service.d/
cat <<EOF | sudo tee /etc/systemd/system/warp-node@.service.d/limits.conf
[Service]
LimitNOFILE=65535
EOF
sudo systemctl daemon-reload
```

---

## §9 Master Validation Script

```bash
#!/usr/bin/env bash
# validate_warp_pool.sh — Complete end-to-end validation
set -euo pipefail

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Omega Engine WARP Proxy Pool — End-to-End Validation      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

NODES=${1:-3}
PASS=0
FAIL=0

check() {
    if eval "$2" &>/dev/null; then
        echo "  ✅ $1"
        ((PASS++))
    else
        echo "  ❌ $1"
        ((FAIL++))
    fi
}

echo ""
echo "=== §1 Dependency Check ==="
check "socat installed" "command -v socat"
check "iproute2 installed" "command -v ip"
check "cloudflare-warp installed" "command -v warp-cli"

echo ""
echo "=== §2 Namespace Isolation ==="
for i in $(seq 1 $NODES); do
    check "Node $i namespace exists" "ip netns list | grep -q warp_node_$i"
    check "Node $i service running" "systemctl is-active warp-node@$i.service"
done

echo ""
echo "=== §3 Socat Bridge Connectivity ==="
for i in $(seq 1 $NODES); do
    PORT=$((8080 + i))
    check "Port $PORT listening" "ss -tlnp | grep -q ':${PORT} '"
done

echo ""
echo "=== §4 Proxy Functionality ==="
for i in $(seq 1 $NODES); do
    PORT=$((8080 + i))
    check "Port $PORT SOCKS5 working" "curl -s -x socks5h://127.0.0.1:$PORT https://1.1.1.1/cdn-cgi/trace | grep -q 'warp=on'"
done

echo ""
echo "=== §5 IP Rotation ==="
OLD_IP=$(curl -s -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace | grep "ip=")
sudo /usr/local/bin/spawn_warp_node.sh 1 recycle
NEW_IP=$(curl -s -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace | grep "ip=")
if [ "$OLD_IP" != "$NEW_IP" ]; then
    echo "  ✅ IP rotation successful"
    ((PASS++))
else
    echo "  ⚠️  IP unchanged (may be same Anycast gateway)"
fi

echo ""
echo "=== §6 Systemd Resource Limits ==="
check "MemoryMax configured" "systemctl show warp-node@1.service | grep -q 'MemoryMax=150M'"
check "CPUQuota configured" "systemctl show warp-node@1.service | grep -q 'CPUQuota=15%'"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Results: $PASS passed, $FAIL failed                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"

exit $FAIL
```

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ VALIDATION ⬡ PRODUCTION-READY ⬡ 2026-07-04*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: validation | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
