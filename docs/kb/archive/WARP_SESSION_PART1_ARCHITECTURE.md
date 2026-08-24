# 🔱 WARP Proxy Pool — Session Knowledge Capture (Part 1: Architecture & Root Causes)
# ⬡ OMEGA ⬡ KALI ⬡ WARP-KB ⬡ 2026-07-05
# Session: 321K context — WARP multi-instance deployment via network namespaces

---

## §1 Executive Summary

**Goal**: Deploy 3 independent Cloudflare WARP instances in Linux network namespaces, each with unique exit IP, exposed as SOCKS5 proxies on host loopback (ports 8081-8083).

**Final State**: 2/3 nodes active (warp-node@1, warp-node@3), warp-node@2 pending registration. Sequential flock-based registration working. Log permission issue blocking warp-svc startup.

**Key Insight**: The WARP architecture requires a running `warp-svc` daemon for `warp-cli` IPC communication. Multi-instance deployment requires careful orchestration of daemon lifecycle, config directories, and namespace isolation.

---

## §2 Architecture (Final Working Design)

```
Host Applications (Omega Engine)
    ↓ socks5h://127.0.0.1:8081-8083
socat-bridge@ (TCP proxy, host → namespace)
    ↓ ip netns exec
Network Namespace (warp_node_1/2/3)
    ↓ veth pair + NAT
Host Default Route (wlo1)
    ↓ Internet
Cloudflare Edge (WARP tunnel exit)
```

**Service Dependency Chain**:
```
warp-ns-prep@%i.service  → Creates namespace + veth + NAT + DNS
    ↓
warp-reg@%i.service      → Sequential registration via flock lock
    ↓ (copies config to /var/lib/cloudflare-warp-%i/)
warp-node@%i.service     → Permanent warp-svc with --config-dir
    ↓
socat-bridge@%i.service  → Bridges host loopback to namespace proxy
    ↓
warp-pool.target         → Coordinates all 3 node instances
```

---

## §3 Critical Root Causes Discovered

### RC1: `warp-cli` has NO `--config-dir` flag
- **Discovery**: `warp-cli --config-dir /tmp/test` → `error: unexpected argument '--config-dir' found`
- **Impact**: `warp-cli` ALWAYS reads from `/var/lib/cloudflare-warp/` (system default)
- **Workaround**: Register in default path, then `cp -r` all files to custom `--config-dir` path for `warp-svc`

### RC2: `warp-cli` requires running `warp-svc` for IPC
- **Discovery**: `warp-cli` communicates with `warp-svc` via Unix socket at `/run/cloudflare-warp/warp_service`
- **Impact**: Registration fails with "Unable to connect to daemon" if `warp-svc` not running
- **Fix**: Start temporary `warp-svc` on host before registration, kill after

### RC3: Host `warp-svc` conflicts with namespace instances
- **Discovery**: Single daemon manages IPC socket; multiple instances fight for `/run/cloudflare-warp/warp_service`
- **Impact**: "Address already in use" / "Unix socket already bound"
- **Fix**: Stop host `warp-svc` before registration; use `flock` for sequential execution

### RC4: Daemon internal state persists across file cleanup
- **Discovery**: Even after `rm -rf` all registration files, daemon memory retains "old registration"
- **Error**: "Old registration is still around" / "RegistrationMissing(DaemonStartup)"
- **Fix**: `warp-cli --accept-tos settings reset` before registration

### RC5: `warp-svc` log directory permission denied
- **Error**: `to create rolling file appender: Os { code: 13, kind: PermissionDenied }`
- **Cause**: `warp-svc` expects `LogsDirectory=cloudflare-warp` via systemd; background process lacks this
- **Fix**: `LOGS_DIRECTORY=/var/log/cloudflare-warp` env var + `mkdir -p /var/log/cloudflare-warp && chmod 755`

### RC6: Namespace DNS resolution failure
- **Error**: `Failed to resolve API endpoint IP using DNS error=Timeout host="api.cloudflareclient.com."`
- **Cause**: Namespace inherits no DNS resolver; host uses systemd-resolved (127.0.0.53) inaccessible from namespace
- **Fix**: Bind mount `/etc/netns/warp_node_%i/resolv.conf` with `nameserver 1.1.1.1` + `8.8.8.8`

### RC7: NAT rules lost on service restart
- **Cause**: `ns-prep` ExecStop removed iptables MASQUERADE rules
- **Fix**: Remove NAT cleanup from ExecStop; add NAT setup in deploy script's `enable_and_start_pool()`

### RC8: Sequential registration required
- **Cause**: 3 parallel `warp-reg` instances conflict on host daemon + DEFAULT path
- **Fix**: `flock -x /run/warp-reg-global.lock` ensures strict serialization

---

## §4 Service Files (Final Versions)

### warp-ns-prep@.service
- Creates namespace `warp_node_%i`
- Creates veth pair `veth_host_%i` / `veth_ns_%i`
- Configures subnet `10.0.%i.0/24` (host .1, ns .2)
- Adds default route in namespace via veth
- Enables IP forwarding
- Adds iptables MASQUERADE for subnet
- Configures DNS via bind mount to `/etc/netns/warp_node_%i/resolv.conf`
- **ExecStop**: Only cleans veth + namespace (keeps NAT rules)

### warp-reg@.service (Sequential via flock)
```bash
flock -x /run/warp-reg-global.lock -c '
  # Stop host warp-svc, kill processes, clean socket
  # Aggressive file cleanup (chattr -i + rm -rf all reg files + WAL/SHM)
  # mkdir -p /var/lib/cloudflare-warp-%i
  # mkdir -p /var/lib/cloudflare-warp /run/cloudflare-warp /var/log/cloudflare-warp
  # chmod 755 /var/log/cloudflare-warp
  # LOGS_DIRECTORY=/var/log/cloudflare-warp warp-svc &
  # Wait for IPC readiness (60x 0.5s)
  # warp-cli --accept-tos settings reset
  # warp-cli --accept-tos registration new
  # cp -r /var/lib/cloudflare-warp/* /var/lib/cloudflare-warp-%i/
'
```

### warp-node@.service
- Runs `warp-svc --config-dir /var/lib/cloudflare-warp-%i` inside namespace
- ExecStartPost: `warp-cli --accept-tos mode proxy`, `proxy port %i`, `connect`
- Memory limits: 120M/150M, CPU 15%

### socat-bridge@.service
- `socat TCP-LISTEN:8080+%i,fork,reuseaddr,bind=127.0.0.1 EXEC:"ip netns exec warp_node_%i socat - TCP:127.0.0.1:8080+%i"`

---

## §5 Deploy Script Enhancements

- `cleanup_stale_state()`: Stops host warp-svc, kills processes, removes namespaces, nukes ALL registration files
- `enable_and_start_pool()`: Adds NAT rules for each subnet via detected default interface
- Wait timeout: 300s (sequential registration takes ~150s for 3 instances)
- Per-node diagnostics with journalctl tail

---

## §6 Key Files Modified

| File | Purpose |
|------|---------|
| `deploy/infra/warp_pool/warp-ns-prep@.service` | Namespace + veth + NAT + DNS |
| `deploy/infra/warp_pool/warp-reg@.service` | Sequential registration via flock |
| `deploy/infra/warp_pool/warp-node@.service` | Permanent warp-svc per namespace |
| `deploy/infra/warp_pool/socat-bridge@.service` | Host ↔ namespace SOCKS bridge |
| `scripts/deploy_warp_pool.sh` | Idempotent deploy with cleanup + NAT |
| `docs/kb/WARP_PROXY_POOL_KB.md` | 12 lessons learned + troubleshooting |

---

## §7 Current Blockers (as of session end)

1. **warp-svc log permission**: `LOGS_DIRECTORY` env var helps but rolling file appender still fails — need to verify `/var/log/cloudflare-warp` writable by warp-svc user
2. **warp-node@2 registration pending**: Sequential flock works; instance 2 waiting for lock release
3. **Timeout tuning**: 300s wait may still be tight for 3 sequential registrations

---

## §8 Research Sources Consulted

- Cloudflare Community: "Warp-Cli in arch linux: cannot start warp-svc.service" (permission denied fix)
- Stack Overflow: "How to change warp-svc's log directory" (LOGS_DIRECTORY env var)
- aleskxyz/warp-svc Docker: Multi-instance pattern via filesystem isolation
- Arch Linux forums: nftables requirement, systemd-resolved DNS issues
- vopono project: "Don't run warp-svc outside... stop/disable systemd service, run only via vopono"

---

*Part 1 of 3 — Architecture & Root Causes*
*Next: Part 2 — Implementation Details & Code Patterns*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: WARP-KB | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
