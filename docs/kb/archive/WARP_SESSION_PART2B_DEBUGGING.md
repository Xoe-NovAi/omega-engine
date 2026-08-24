# 🔱 WARP Proxy Pool — Session Knowledge Capture (Part 2b: Debugging & Lessons)
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ 2026-07-05

---

## §1 Debugging Techniques

### Journalctl for Service Debugging
```bash
# Follow live logs
journalctl -u warp-reg@1.service -f

# Since specific time
journalctl -u warp-reg@1.service --since "12:17" --no-pager

# Last N lines with context
journalctl -u warp-reg@1.service -n 100 --no-pager | tail -50

# Filter for errors
journalctl -u warp-reg@1.service --since "1 hour ago" | grep -i error
```

### Namespace Inspection
```bash
# List namespaces
ip netns list

# Execute in namespace
ip netns exec warp_node_1 ip addr show
ip netns exec warp_node_1 ip route show
ip netns exec warp_node_1 cat /etc/resolv.conf
ip netns exec warp_node_1 nslookup api.cloudflareclient.com

# Check veth pairs
ip link show | grep veth

# Check NAT rules
iptables -t nat -L POSTROUTING -n -v | grep 10.0
```

### WARP Daemon Debugging
```bash
# Check if warp-svc running
systemctl status warp-svc
ps aux | grep warp-svc

# Test IPC connectivity
warp-cli --accept-tos status

# View daemon logs
journalctl -u warp-svc -f

# Manual daemon start with debug
RUST_BACKTRACE=1 LOGS_DIRECTORY=/var/log/cloudflare-warp warp-svc
```

### Socket & IPC Inspection
```bash
# Check warp_service socket
ls -la /run/cloudflare-warp/warp_service

# Check listening ports
ss -tlnp | grep warp

# Test SOCKS proxy
curl -x socks5h://127.0.0.1:8081 https://1.1.1.1/cdn-cgi/trace
```

---

## §2 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Unable to connect to daemon` | warp-svc not running | Start warp-svc before warp-cli |
| `Address already in use` | Multiple warp-svc on same socket | Stop host warp-svc; use flock |
| `Old registration is still around` | Daemon memory retains state | `warp-cli settings reset` |
| `Permission denied` (logs) | warp-svc can't write logs | `LOGS_DIRECTORY=/var/log/cloudflare-warp` + chmod 755 |
| `DNS timeout` | No resolver in namespace | Bind mount resolv.conf with 1.1.1.1 |
| `Unix socket already bound` | Host warp-svc running | `systemctl stop warp-svc` |
| `RegistrationMissing(DaemonStartup)` | Daemon not fully initialized | Wait for IPC + `settings reset` |
| `start operation timed out` | Registration takes >180s | Increase TimeoutStartSec |

---

## §3 Key Lessons Learned

### L1: WARP Architecture is Daemon-Centric
- `warp-cli` is just an IPC client; all state lives in `warp-svc`
- No daemon = no registration, no connection, no nothing
- Background daemon must be managed explicitly in scripts

### L2: Config Directory Semantics
- `warp-cli`: NO `--config-dir` flag → always uses `/var/lib/cloudflare-warp/`
- `warp-svc`: HAS `--config-dir` → can run multiple instances
- Registration writes to DEFAULT; copy to custom for multi-instance

### L3: Daemon State Persistence
- Files on disk ≠ daemon state
- `rm -rf` all files ≠ clean slate
- Must `settings reset` to clear daemon memory
- SQLite WAL/SHM files (`-wal`, `-shm`) also hold state

### L4: Namespace Isolation Requires Full Stack
- Network namespace alone = no internet
- Need: veth pair + IP config + default route + NAT + DNS
- Missing any piece = silent failure (timeout, not error)

### L5: Sequential > Parallel for Shared Resources
- 3 parallel registrations = 3x conflicts on single daemon
- `flock` serialization = deterministic, debuggable, reliable
- Lock file at `/run/warp-reg-global.lock` survives reboots

### L6: Systemd Service Design Matters
- `RemainAfterExit=yes` for oneshot setup services
- `ExecStop` must NOT clean resources needed by dependent services
- `CapabilityBoundingSet` must include CAP_SYS_ADMIN for mount/ip netns
- `LogsDirectory`/`StateDirectory` only work for systemd-managed services

### L7: Deploy Script Must Be Idempotent
- Cleanup runs before every deploy
- NAT rules must persist across service restarts
- Wait timeouts must accommodate sequential operations
- Per-node diagnostics essential for debugging

---

## §4 Performance Characteristics

| Operation | Typical Time | Max Observed |
|-----------|-------------|--------------|
| Namespace + veth creation | <1s | 2s |
| NAT rule setup | <1s | 1s |
| warp-svc startup (IPC ready) | 5-15s | 30s |
| warp-svc tunnel connection | 30-90s | 120s |
| Registration (after IPC) | 2-5s | 10s |
| Config copy | <1s | 1s |
| **Total per instance (sequential)** | **~45-120s** | **~150s** |

---

## §5 Security Considerations

### Capabilities Required
- `CAP_NET_ADMIN`: veth, routes, iptables
- `CAP_SYS_ADMIN`: mount, ip netns, chattr
- `CAP_DAC_OVERRIDE`: chattr -i (remove immutable flag)

### Network Isolation
- Each namespace has own routing table
- Only outbound via veth → NAT → host default route
- No inbound from internet (no port forwarding)
- SOCKS proxy only on host loopback (127.0.0.1)

### File Permissions
- `/var/lib/cloudflare-warp-%i/`: root:root, 755
- `/run/cloudflare-warp/`: root:root, 755
- `/var/log/cloudflare-warp/`: root:root, 755
- Registration files: root:root, 644

---

## §6 Future Improvements

1. **Health Checks**: Add `ExecStartPost` health verification for warp-node
2. **Auto-Rotation**: Periodic re-registration for IP diversity
3. **Metrics Export**: Prometheus exporter for warp-node status
4. **Config Validation**: Pre-deploy validation of all service files
5. **Rollback**: Automatic rollback on registration failure
6. **Multi-Host**: Extend to multiple physical hosts for geo-diversity

---

*Part 2b of 3 — Debugging & Lessons*
*Next: Part 3 — Complete Service Files & Deploy Script*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: WARP-KB | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
