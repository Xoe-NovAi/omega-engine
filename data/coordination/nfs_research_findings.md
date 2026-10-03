# 🔱 NFS-over-Tailscale: Web Research Findings & Applied Corrections
**Date**: 2026-09-25
**Researcher**: Antigravity IDE (Claude Sonnet 4.6 Thinking)
**Status**: 8 additional gaps found, all corrected below.

---

## Research Summary — What Was Discovered

### Finding 1 — `soft` mount is DANGEROUS. Use `hard` instead. ⚠️

**Our current script tells Node 1 to use `-o soft,timeo=15,retrans=3`.**

This is wrong per 2024 Linux NFS best practice. Research confirmed:

| Option | On Timeout | Data Integrity Risk |
|---|---|---|
| `hard` | Retries indefinitely | **Lowest** ✅ |
| `soft` | Returns `EIO` | **High** — silent write corruption possible |
| `softerr` | Returns `ETIMEDOUT` | **High** — same risk as soft |

`soft` can cause **silent data corruption** — the application receives no error but the write never landed. For the `exchange/` directory (which carries WAD contracts and federation payloads), this is unacceptable.

The correct approach for WAN/VPN:
- **Use `hard`** for integrity.
- **Add `x-systemd.mount-timeout=30`** to prevent boot hangs (this handles the zombie problem at the systemd level, not by degrading write integrity).
- **The Automount Zombie problem is prevented by `_netdev` + `x-systemd.requires=tailscaled.service`**, not by `soft`.

**Corrected Node 1 mount options:**
```bash
sudo mount -t nfs4 -o hard,timeo=600,retrans=3,rsize=32768,wsize=32768 \
  n0.tail51f14a.ts.net:/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange \
  /mnt/omega_exchange
```

---

### Finding 2 — `/etc/nfs.conf.d/` drop-in is safer than editing `nfs.conf` directly

**Our current script appends to `/etc/nfs.conf` directly.**

Best practice on Ubuntu 22.04/24.04 is to use drop-in files at `/etc/nfs.conf.d/` — the same pattern that resolved the `nfs.conf` timing race in the `DEFINITIVE_RESOLUTION_GUIDE`. It:
- Survives package upgrades without merge conflicts
- Is isolated and trackable
- Can be verified with `nfsconf --dump`

**Corrected approach in script:**
```bash
sudo mkdir -p /etc/nfs.conf.d/
cat <<EOF | sudo tee /etc/nfs.conf.d/omega-nfsv4-only.conf > /dev/null
[nfsd]
vers2=n
vers3=n
vers4=y
vers4.1=y
vers4.2=y
EOF
```

---

### Finding 3 — rpcbind should be fully MASKED for NFSv4-only

**Our script disables NFSv3 but leaves `rpcbind` running.**

Research confirmed: rpcbind is required ONLY for NFSv3. In NFSv4-only mode, masking it (not just stopping it) prevents it from being auto-restarted by dependency chains.

```bash
sudo systemctl stop rpcbind.service rpcbind.socket
sudo systemctl mask rpcbind.service rpcbind.socket
```

> [!CAUTION]
> Only do this after confirming nothing else on Node 0 uses rpcbind (e.g., no other NFS v3 clients, no legacy RPC services). Run `rpcinfo -p` first to inspect what's registered.

---

### Finding 4 — idmapd domain mismatch causes `nobody:nobody` ownership

**Not mentioned in any previous session document.**

On NFSv4, the `idmapd` daemon maps user identities using a domain string. If Node 0 and Node 1 have different DNS domains (or unconfigured domains), all files on Node 1 will appear owned by `nobody:nobody` (UID 65534), regardless of `anonuid` settings.

**Fix — must be applied on BOTH nodes:**
```bash
# On both Node 0 and Node 1:
sudo nano /etc/idmapd.conf
```
Set the same arbitrary domain string on both:
```ini
[General]
Domain = omega.internal
```
Then on Node 1 after mounting:
```bash
sudo nfsidmap -c  # clears the kernel identity cache
```

---

### Finding 5 — MTU tuning: `rsize`/`wsize` should be 32KB over Tailscale

**Not in original script.**

Tailscale's tunnel MTU is 1280 bytes. Default NFS block sizes (1MB+) trigger excessive fragmentation over this tunnel. Research recommends **32768 (32KB)** as the optimal rsize/wsize for the Tailscale MTU, providing the best balance of throughput vs. fragmentation overhead.

```bash
# Add rsize=32768,wsize=32768 to all mount options
```

---

### Finding 6 — `nconnect` option available for free throughput improvement (kernel 5.3+)

**Not in original script.**

`nconnect` allows multiple TCP connections per NFS mount, parallelizing I/O across CPU cores. Since this is a two-node P2P setup (not a cloud-scale cluster), `nconnect=4` is a reasonable starting point.

```bash
sudo mount -t nfs4 -o hard,timeo=600,retrans=3,rsize=32768,wsize=32768,nconnect=4 \
  n0.tail51f14a.ts.net:/path/to/exchange /mnt/omega_exchange
```

Verify kernel supports it: `uname -r` — any kernel ≥ 5.3 is fine.

---

### Finding 7 — fstab MUST use `x-systemd.requires=tailscaled.service` to prevent shutdown hangs

**Our fstab template was missing this.**

The `nofail` flag alone does NOT prevent shutdown hangs when Tailscale stops before the NFS mount is unmounted. Research confirms the critical addition is `x-systemd.requires=tailscaled.service`, which creates a systemd dependency causing the mount to be torn down **before** Tailscale exits.

**Corrected fstab line for Node 1:**
```
n0.tail51f14a.ts.net:/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange /mnt/omega_exchange nfs4 hard,timeo=600,retrans=3,rsize=32768,wsize=32768,nconnect=4,nofail,_netdev,x-systemd.requires=tailscaled.service,x-systemd.automount,x-systemd.mount-timeout=30,x-systemd.idle-timeout=5min 0 0
```

---

### Finding 8 — DERP relay vs Direct connection: MUST verify before assuming NFS will work

**Not in any previous session document.**

The single biggest NFS-over-Tailscale risk is Tailscale falling back to DERP relay instead of establishing a direct peer-to-peer connection. DERP relay caps throughput to a few MB/s (vs wire speed), making NFS operations sluggish or timing out entirely.

**Must verify BEFORE considering the shared drive operational:**
```bash
# On Node 0 or Node 1:
tailscale status        # check if peer shows "direct" or "relay"
tailscale ping <node1-tailscale-ip>  # look for "direct" in output
```

If it shows `relay`, ensure **UDP port 41641** is open on both routers/firewalls to enable WireGuard hole-punching for direct peer-to-peer.

---

## Fully Corrected `setup_nfs_share.sh`

```bash
#!/bin/bash

# 🔱 OMEGA ENGINE — NFS Shared Drive Setup (Node 0 / Bastion)
# Research-hardened version: NFSv4-only, drop-in config, rpcbind masked, idmapd configured.

set -euo pipefail

EXCHANGE_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/exchange"
TAILSCALE_CIDR="100.64.0.0/10"
IDMAPD_DOMAIN="omega.internal"
EXPORT_ENTRY="${EXCHANGE_DIR} ${TAILSCALE_CIDR}(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)"

echo "=> Step 1: Exchange directory permissions..."
sudo mkdir -p "${EXCHANGE_DIR}"
sudo chown -R 1000:1000 "${EXCHANGE_DIR}"
sudo chmod -R 0775 "${EXCHANGE_DIR}"

echo "=> Step 2: NFSv4-only via /etc/nfs.conf.d/ drop-in (upgrade-safe)..."
sudo mkdir -p /etc/nfs.conf.d/
cat <<EOF | sudo tee /etc/nfs.conf.d/omega-nfsv4-only.conf > /dev/null
[nfsd]
vers2=n
vers3=n
vers4=y
vers4.1=y
vers4.2=y
EOF
echo "   => Drop-in written. Verify with: nfsconf --dump"

echo "=> Step 3: idmapd domain alignment (prevents nobody:nobody ownership)..."
if ! grep -q "^Domain" /etc/idmapd.conf 2>/dev/null; then
    echo "" | sudo tee -a /etc/idmapd.conf > /dev/null
    echo "[General]" | sudo tee -a /etc/idmapd.conf > /dev/null
    echo "Domain = ${IDMAPD_DOMAIN}" | sudo tee -a /etc/idmapd.conf > /dev/null
    echo "   => idmapd domain set to: ${IDMAPD_DOMAIN}"
else
    echo "   => Domain already set in idmapd.conf. Verify it matches Node 1."
fi

echo "=> Step 4: Configuring NFS Export..."
if grep -qF "${EXCHANGE_DIR}" /etc/exports 2>/dev/null; then
    echo "   => Existing entry found. Replacing..."
    sudo sed -i "\|^${EXCHANGE_DIR}|d" /etc/exports
fi
echo "${EXPORT_ENTRY}" | sudo tee -a /etc/exports > /dev/null
echo "   => /etc/exports updated."

echo "=> Step 5: Masking rpcbind (not needed in NFSv4-only mode)..."
echo "   [WARNING] This will break any existing NFSv3 clients or RPC services."
echo "   Checking for active RPC registrations first..."
if rpcinfo -p 2>/dev/null | grep -v "^   program" | grep -qv "portmapper"; then
    echo "   => Other RPC services detected. Skipping rpcbind mask. Review manually."
else
    sudo systemctl stop rpcbind.service rpcbind.socket 2>/dev/null || true
    sudo systemctl mask rpcbind.service rpcbind.socket 2>/dev/null || true
    echo "   => rpcbind masked."
fi

echo "=> Step 6: Restarting NFS server..."
sudo systemctl restart nfs-kernel-server 2>/dev/null \
  || sudo systemctl restart nfs-server 2>/dev/null \
  || { echo "ERROR: NFS not installed. Run: sudo apt install nfs-kernel-server"; exit 1; }
sudo exportfs -ra

echo "=> Step 7: Verifying connection type (DERP vs Direct)..."
echo "   Run: tailscale status"
echo "   Ensure Node 1 shows 'direct' — DERP relay will severely degrade NFS performance."
echo "   If relay: ensure UDP 41641 is open on both nodes' routers."

echo ""
echo "================================================================"
echo "✅ NFS Share configured on Node 0 (Bastion)."
echo "   Exported: ${EXCHANGE_DIR}"
echo "   Accessible to: ${TAILSCALE_CIDR}"
echo "   NFSv4 only: YES (NFSv2/3 disabled)"
echo "   idmapd domain: ${IDMAPD_DOMAIN}"
echo ""
echo "ON NODE 1 — run these in order:"
echo "---"
echo "1. Set matching idmapd domain:"
echo "   sudo sed -i 's/^#Domain.*//' /etc/idmapd.conf"
echo "   echo 'Domain = ${IDMAPD_DOMAIN}' | sudo tee -a /etc/idmapd.conf"
echo "   sudo systemctl restart nfs-idmapd"
echo ""
echo "2. Mount manually:"
echo "   sudo mkdir -p /mnt/omega_exchange"
echo "   sudo mount -t nfs4 -o hard,timeo=600,retrans=3,rsize=32768,wsize=32768,nconnect=4 \\"
echo "     n0.tail51f14a.ts.net:${EXCHANGE_DIR} /mnt/omega_exchange"
echo ""
echo "3. Verify ownership (should show arcana-novai or uid 1000, NOT nobody):"
echo "   ls -la /mnt/omega_exchange/"
echo "   sudo nfsidmap -c  # clear cache if showing nobody:nobody"
echo ""
echo "4. For PERSISTENT mount — add to /etc/fstab on Node 1:"
echo "   n0.tail51f14a.ts.net:${EXCHANGE_DIR} /mnt/omega_exchange nfs4 hard,timeo=600,retrans=3,rsize=32768,wsize=32768,nconnect=4,nofail,_netdev,x-systemd.requires=tailscaled.service,x-systemd.automount,x-systemd.mount-timeout=30,x-systemd.idle-timeout=5min 0 0"
echo ""
echo "5. Verify Tailscale connection type:"
echo "   tailscale ping <node0-tailscale-ip>"
echo "   # Must show 'direct' — DERP relay = slow NFS"
echo "================================================================"
```

---

## Pre-Flight Checklist Before Running

- [ ] Run `tailscale status` on Node 0 — confirm Node 1 is a known peer
- [ ] Run `tailscale ping <node1-ip>` — confirm `direct` (not relay)
- [ ] If relay: open UDP 41641 on router, or temporarily set an exit node
- [ ] Apply the updated `.hujson` ACLs (bidirectional 2049) to tailnet admin panel
- [ ] Run `uname -r` on Node 1 — confirm kernel ≥ 5.3 before using `nconnect`
- [ ] Run `nfsconf --dump` after script completes — verify `vers3=n`

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ SONNET-4.6 ⬡ RESEARCH-COMPLETE ⬡ 2026-09-25*
