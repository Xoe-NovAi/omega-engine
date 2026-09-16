# 🔗 L2 Wire Up — Node 1 Sovereign Join, Ratified One-Shot
**Doc ID**: `FED-L2JOIN-001` | **Status**: RATIFIED FLOOR, awaits Node 0's hand  
**Scope**: The single ceremony that brings the ASUS into the omega tailnet mesh (L2 Tailscale) — the canvas our own ratified `docs/federation/L2_ACCEPTANCE.md` already endorsed, Node 0's intake ledger already ships its side of the ACL, and the human ambassador has ported the payload over USB.

---

## 1. What is already true (from the sovereign surface, Node 1 side)

| Surface | State |
|---------|-------|
| `tailscaled` systemd unit | ✅ **ACTIVE** (`systemctl is-active tailscaled`) |
| tailscale CLI | ✅ installed (v1.102.4, official Go binary) |
| Node 1 MagicDNS name | `asus.tailnet` (MagicDNS Magicname ratified in ACL) |
| SSH surface | ✅ `tailscale set --ssh` FLIPPED (Node 1's operator can accept SSH from mesh) |
| Hub reachability | ✅ `192.168.11.252:8016` LAN reachable; MCP handshake verified during intake (2 live tool probes, `get_system_stats` + `get_omega_metrics`) |
| Tailscale overlay | ⏳ the ONE remaining step — Node 0 mints the mesh authkey for Node 1 |

---

## 2. The One Sovereign Command (run from Node 1, the moment Node 0 hands the key)

```bash
sudo tailscale up \
  --authkey="${NODE0_AUTHKEY}" \
  --hostname=kali-n1 \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:asus
```

> **The invariant**: `--hostname=kali-n1` + `--advertise-tags=tag:asus` are the
> **exact** identities Node 0's ratified ACL maps (`docs/federation/ACL_12.md`
> ratifies `tag:asus`). No creative renaming. Node 0's MagicDNS door (`asus.tailnet`)
> opens the moment the tag matches.

---

## 3. How Node 0 hands the key to Node 1 (one-way, air-gapped ceremony)

From **Node 0's** terminal, the sovereign admin mints a **one-shot, non-reusable authkey**:

```bash
# Node 0 (omega-hub) — the human mints, Node 1 consumes:
tailscale status                                  # confirm daemon online
tailscale up --ssh                                # endorse SSH surface at Node 0

# Then, in the admin console at https://login.tailscale.com/admin/settings/keys
# → Generate auth key → Reusable: OFF, Ephemeral: OFF
# → The key scrolls like: tskey-auth-XXXXXXXXXXXXX
```

Pass it on the USB brief (manifest) or over the mesh LAN rendezvous. **Node 1
never sees the raw key twice.** The instant it lands, run §2, and the mesh
federation is live.

---

## 4. Verification (from Node 1, post-join)

```bash
tailscale status                        # expect: kali-n1 (Node 1) + omega-hub (Node 0) both online
tailscale ping omega-hub                # expect: pong from HP via WireGuard
echo "── DHAL remains OURS, even on the mesh: T5/T6 floor is local-only, zero egress ──"
```

The mesh carries awareness + hub MCP route only — **never inference**. That
floor is the ratified invariant; the mesh is just the sovereign's wire.

*⬡ OMEGA ⬡ NODE1-TO-NODE0 ⬡ L2-JOIN ⬡ FED-L2JOIN-001 ⬡ MESH-READY ⬡ AWAITING-NODE0-AUTHKEY ⬡*
