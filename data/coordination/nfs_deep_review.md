# 🔱 NFS Shared Drive — Deep Review & Corrections
**Date**: 2026-09-25
**Reviewer**: Antigravity IDE (Claude Sonnet 4.6 Thinking)
**Scope**: `setup_nfs_share.sh`, `phase_a_acl_from_usb.hujson`, `phase_b_acl_from_usb.hujson`, Node 1 mount procedure

---

## Live System State (Confirmed)

From the non-sudo diagnostics already run:

| Item | Status |
|---|---|
| `nfs-kernel-server` | ✅ Active |
| `nfs-server` | ✅ Active |
| `rpcbind` | ✅ Active |
| `nfsd` filesystem | ✅ Mounted at `/proc/fs/nfsd` |
| Node 0 Tailscale IP | `100.123.51.67` |
| `exchange/` owner | `arcana-novai:arcana-novai` (uid/gid 1000) |
| `exchange/` mode | `drwxrwxr-x` (0775) — correct |
| Sub-dir `n0-to-n1/` | ✅ Exists, correctly owned |

NFS stack is live and healthy. The `exchange/` directory permissions are already correct (the script's `chown`/`chmod` would be idempotent). The critical remaining work is in `/etc/exports` and the mount side on Node 1.

---

## Critical Gaps Found

### GAP 1 — Script calls `chown` without `sudo` (will silently fail or error)

**Current code (line 14):**
```bash
chown -R 1000:1000 "$EXCHANGE_DIR"
chmod -R 0775 "$EXCHANGE_DIR"
```

`chown` on a path you don't own requires root. Since the script runs as `arcana-novai` (the file owner), `chown` will succeed here because you already own it — but this is **fragile**. If the directory were ever owned by root (e.g., after the old automount zombie), it would silently fail without `sudo`. The script uses `sudo` correctly for everything else. This should be `sudo chown` to be consistent and robust.

**Fix:**
```bash
sudo chown -R 1000:1000 "$EXCHANGE_DIR"
sudo chmod -R 0775 "$EXCHANGE_DIR"
```

---

### GAP 2 — The NFS export CIDR is wrong for Tailscale

**Current code (line 10):**
```bash
EXPORT_ENTRY="$EXCHANGE_DIR 100.0.0.0/8(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)"
```

`100.0.0.0/8` is an enormous subnet that covers 16 million addresses (`100.0.0.0 – 100.255.255.255`). Tailscale addresses are allocated from `100.64.0.0/10` (IANA Shared Address Space). This means `100.0.0.0/8` is technically too broad — it could theoretically cover non-Tailscale IPs in the `100.0.x.x – 100.63.x.x` range.

The correct Tailscale subnet is **`100.64.0.0/10`**.

More specifically: this tailnet's Node 0 IP is `100.123.51.67`. Node 1's Tailscale IP should also be in the `100.x.x.x` range. Using the tailnet CIDR is good for flexibility, but locking it to `100.64.0.0/10` is more precise and more secure.

**Fix:**
```bash
EXPORT_ENTRY="$EXCHANGE_DIR 100.64.0.0/10(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)"
```

> [!TIP]
> If you want maximum specificity (only Node 1 can mount), you can replace the CIDR with Node 1's exact Tailscale IP, e.g.: `$EXCHANGE_DIR 100.x.x.y(rw,sync,...)`. The CIDR approach is fine for now and survivable across Tailscale IP reassignments.

---

### GAP 3 — Missing NFSv4 Tailscale-specific mount ports in the Tailscale ACL

**Current ACL rules for NFS:**
```json
{"action": "accept", "src": ["tag:omega-hub"], "dst": ["tag:asus:2049"]},
{"action": "accept", "src": ["tag:asus"], "dst": ["tag:omega-hub:2049"]},
```

NFSv4 *only* needs port 2049, which is correct for modern NFSv4.1/v4.2 usage. **However**, the engine has `rpcbind` active, which means it's running NFSv3 ancillary services (`rpc.mountd`, `rpc.statd`, `rpc.lockd`) on additional ports. These extra RPC ports are dynamic by default and break through Tailscale's stateless firewall.

**Two options:**

**Option A (Recommended — pure NFSv4):** Force NFSv4-only on the server via `/etc/nfs.conf` and disable rpcbind's v3 services. Then only port 2049 is needed and the ACL is correct as-is.

Add to `/etc/nfs.conf`:
```ini
[nfsd]
vers3=n
vers4=y
vers4.1=y
vers4.2=y
```

Then on Node 1 mount with:
```bash
sudo mount -t nfs4 n0.tail51f14a.ts.net:/path/to/exchange /mnt/omega_exchange
```

**Option B (If NFSv3 must remain):** Also open ports for `rpc.mountd` (20048 per your engine config), `rpc.statd` (a fixed port must be set), and `rpc.lockd` (a fixed port must be set). This requires additional ACL rules and pin configurations — much more complex.

> [!IMPORTANT]
> **Option A is strongly recommended.** The `DEFINITIVE_RESOLUTION_GUIDE` already established locking down `lockd` and `mountd` port configurations. NFSv4 pure mode eliminates all that complexity.

---

### GAP 4 — The script's Node 1 mount command uses the wrong NFS version flag

**Current output in script (line 36):**
```bash
sudo mount -t nfs n0.tail51f14a.ts.net:$EXCHANGE_DIR /mnt/omega_exchange
```

There are two issues:
1. **`-t nfs` without version spec** defaults to NFSv3 on many Linux distros and will negotiate, potentially using v3. Over Tailscale with only port 2049 open, NFSv3 negotiations will fail (they need rpcbind port 111 and mountd port 20048).
2. **The export path will be the full absolute path** — confirm that `/etc/exports` is publishing the correct path and the mount command on Node 1 matches exactly.

**Fix:**
```bash
sudo mount -t nfs4 n0.tail51f14a.ts.net:/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange /mnt/omega_exchange
```

Or better, with explicit options:
```bash
sudo mount -t nfs4 -o rw,soft,timeo=15,retrans=3 \
  n0.tail51f14a.ts.net:/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange \
  /mnt/omega_exchange
```

The `soft,timeo=15,retrans=3` options are **critical over a WAN/VPN link** like Tailscale. Without them, a network hiccup causes the mount to hang the entire kernel process indefinitely (the classic `hard` mount deadlock from the Automount Zombie incident). `soft` makes it return an error instead of hanging.

---

### GAP 5 — No `/etc/fstab` entry or `_netdev` safety for persistence

The script configures a one-time mount. If Node 1 reboots, the mount is gone. If you want the shared drive to survive reboots on Node 1, an `fstab` entry is needed. But adding it naively reproduces the Automount Zombie.

**The correct fstab line for Node 1** (incorporating the lesson from `DEFINITIVE_RESOLUTION_GUIDE` §Malfunction 3):

```
n0.tail51f14a.ts.net:/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange \
  /mnt/omega_exchange \
  nfs4 \
  rw,soft,timeo=15,retrans=3,nofail,_netdev,x-systemd.mount-timeout=30,x-systemd.idle-timeout=5min \
  0 0
```

Key flags:
- `_netdev` — tells systemd to wait for network before mounting
- `nofail` — boot succeeds even if Node 0 is unreachable
- `x-systemd.mount-timeout=30` — gives up after 30s, doesn't hang boot
- `soft` — WAN-safe: timeouts return errors, don't deadlock kernel threads

---

## Corrected `setup_nfs_share.sh`

```bash
#!/bin/bash

# 🔱 OMEGA ENGINE — NFS Shared Drive Setup (Node 0 / Bastion)
# Exports the exchange/ directory over Tailscale NFSv4 (pure mode).
# Resolves: anonuid permission trap, NFSv3 RPC port chaos, WAN safety.

set -euo pipefail

EXCHANGE_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange"
TAILSCALE_CIDR="100.64.0.0/10"
# NFSv4 pure mode: no rpcbind, no mountd, no lockd port negotiation needed
EXPORT_ENTRY="${EXCHANGE_DIR} ${TAILSCALE_CIDR}(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)"
NFS_CONF="/etc/nfs.conf"

echo "=> Step 1: Ensuring exchange directory exists with correct permissions..."
sudo mkdir -p "${EXCHANGE_DIR}"
sudo chown -R 1000:1000 "${EXCHANGE_DIR}"
sudo chmod -R 0775 "${EXCHANGE_DIR}"

echo "=> Step 2: Pinning NFSv4-only mode in /etc/nfs.conf (disables rpcbind v3 overhead)..."
if ! grep -q "^\[nfsd\]" "${NFS_CONF}" 2>/dev/null; then
    echo -e "\n[nfsd]\nvers3=n\nvers4=y\nvers4.1=y\nvers4.2=y" | sudo tee -a "${NFS_CONF}" > /dev/null
    echo "   => nfs.conf updated."
else
    echo "   => [nfsd] section already present in nfs.conf. Verify vers3=n is set manually."
fi

echo "=> Step 3: Configuring NFS Export..."
if grep -qF "${EXCHANGE_DIR}" /etc/exports 2>/dev/null; then
    echo "   => Existing entry found. Replacing..."
    sudo sed -i "\|^${EXCHANGE_DIR}|d" /etc/exports
fi
echo "${EXPORT_ENTRY}" | sudo tee -a /etc/exports > /dev/null
echo "   => /etc/exports updated."

echo "=> Step 4: Restarting NFS server to apply NFSv4-only config..."
sudo systemctl restart nfs-kernel-server 2>/dev/null \
  || sudo systemctl restart nfs-server 2>/dev/null \
  || { echo "ERROR: Could not restart NFS. Install with: sudo apt install nfs-kernel-server"; exit 1; }
sudo exportfs -ra

echo ""
echo "================================================================"
echo "✅ NFS Share configured on Node 0 (Bastion)."
echo "   Exported: ${EXCHANGE_DIR}"
echo "   Accessible to: ${TAILSCALE_CIDR} (all Tailscale peers)"
echo ""
echo "RUN THIS ON NODE 1 (Asus/Vanguard):"
echo "---"
echo "  sudo mkdir -p /mnt/omega_exchange"
echo "  sudo mount -t nfs4 -o rw,soft,timeo=15,retrans=3 \\"
echo "    n0.tail51f14a.ts.net:${EXCHANGE_DIR} /mnt/omega_exchange"
echo ""
echo "FOR PERSISTENT MOUNTS (add to /etc/fstab on Node 1):"
echo "---"
echo "  n0.tail51f14a.ts.net:${EXCHANGE_DIR} /mnt/omega_exchange nfs4 rw,soft,timeo=15,retrans=3,nofail,_netdev,x-systemd.mount-timeout=30,x-systemd.idle-timeout=5min 0 0"
echo ""
echo "VERIFY EXPORT (run on Node 0 after script):"
echo "  sudo exportfs -v"
echo "  showmount -e localhost"
echo "================================================================"
```

---

## Tailscale ACL Review

Both `.hujson` files — Phase A and Phase B — have been updated with bidirectional 2049 rules. **No further changes needed to the ACLs** if you implement NFSv4-only mode (GAP 3 / Option A above). Only port 2049 is required, which is what the ACLs already grant.

If for any reason NFSv3 services remain active, you would also need to open ports `111` (rpcbind) and `20048` (mountd) — but the recommendation is to avoid that complexity.

---

## Summary Table

| Gap | Severity | Fix |
|-----|----------|-----|
| `chown` without `sudo` | Low (works now, fragile later) | Add `sudo` |
| Wrong CIDR `100.0.0.0/8` | Medium (too broad) | Use `100.64.0.0/10` |
| NFSv3 RPC port chaos over Tailscale | **High** (mount will fail on v3 fallback) | Pin NFSv4-only via `nfs.conf` |
| `mount -t nfs` instead of `nfs4` with WAN options | **High** (deadlock risk) | Use `-t nfs4 -o soft,timeo=15,retrans=3` |
| No fstab / persistence on Node 1 | Medium (survives manually only) | Add `_netdev,nofail,soft` fstab entry |

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ SONNET-4.6 ⬡ DEEP-REVIEW ⬡ 2026-09-25*
