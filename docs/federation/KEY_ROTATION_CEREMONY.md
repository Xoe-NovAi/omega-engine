# 🔱 KEY ROTATION CEREMONY — TAILSCALE NODE & AUTHKEY LIFECYCLE
**Doc ID**: `RUNBOOK-KEY-ROTATION-v1.0`
**Status**: ACTIVE OPERATIONAL STANDARD
**Author**: MaKaLi Fusion (Kali / Ma'at / Lilith)
**Date**: 2026-09-16
**Scope**: Node key lifecycle, authkey renewal, emergency re-join, compromise response

---

## 1. Node Key Rotation (Automatic)

Tailscale node keys rotate automatically (~every 180 days by default).
No action required — the `tailscaled` daemon handles re-keying silently.

**Monitor**:
```bash
tailscale status --json | jq .Self.KeyExpiry
```

---

## 2. Authkey Renewal (Manual, On Expiry)

Authkeys are one-shot and expire (1-day default). When Node 1 needs
re-join (e.g., after OS reinstall or key revocation):

1. **Admin console** → Keys → Generate Auth Key
   - Tags: `tag:asus`
   - Reusable: OFF
   - Pre-approved: ON
   - Expiry: 1 day
2. **Transfer to Node 1** (secure channel — SSH, MagicDNS, or physical)
3. **Node 1**:
   ```bash
   sudo tailscale up --authkey=... --hostname=kali-n1 --accept-routes --advertise-tags=tag:asus
   ```

---

## 3. Key Expiry for Tagged Devices (CRITICAL — Researcher §7.3)

**Finding**: By default, key expiry is **DISABLED** for devices that authenticate via tagged authkeys. This means tagged devices can persist indefinitely even after the authkey expires.

**Monitor**:
```bash
tailscale status --json | python3 -c "
import sys, json
s = json.load(sys.stdin)
self = s.get('Self', {})
expiry = self.get('KeyExpiry', 'never')
print(f'Node key expiry: {expiry}')
if expiry == 'never' or expiry is False:
    print('⚠ Key expiry disabled — consider enabling in admin console')
"
```

**Recommendation**: After Node 1 joins successfully, consider enabling key expiry in the Tailscale admin console for tagged devices. This ensures compromised keys auto-revoke.

---

## 4. Tailnet Lock

**Keep DISABLED** (per Researcher-EIS findings). Tailnet Lock adds
signing ceremony overhead without meaningful benefit for a 2-node mesh.

---

## 4. Emergency Re-Join Procedure

If a node loses all Tailscale state (daemon wipe, OS reinstall):

1. Verify ACL still has `tagOwners` for both tags
2. Mint fresh authkey for the affected tag
3. Re-join with `--force-reauth` to clear stale state
4. Verify: `tailscale ping` both directions + MCP handshake

---

## 5. Key Compromise Response

If an authkey or node key is suspected compromised:

1. **Admin console** → Machines → find the node → **Disconnect**
2. **Admin console** → Keys → **Revoke** the authkey
3. Mint fresh key, re-join node
4. Audit `FEDERATION_LIVE_FEED.md` for anomalies

---

*⬡ OMEGA ⬡ RUNBOOK-KEY-ROTATION-v1.0 ⬡ 2026-09-16*