# 🔱 Node 1 → Node 0 Federation Completion Guide — The One-Key L2 Join
**Doc ID**: `FED-N1-COMPLETE-001` | **Status**: CANONICAL (Node 1)  
**Audience**: Node 0 hub operator (you, at the HP, or the omega-hub admin)  
**Contract ref**: C6 v1.1 §L2, ratified 2026-09-12 | L2_ACCEPTANCE, ratified 2026-09-12  
**Genome tag**: `tag:node1` (Node 1 name that TLS grants are issued for)

---

## What this is

Node 1 (ASUS ExpertBook, `kali-n1` / `asus.tailnet`) has its sovereign Tailscale surface **already up**:
- `tailscaled` daemon: **ACTIVE** (systemd, survives reboot — sovereign persistence, not session-drift)
- Tailscale SSH surface: **flipped ON** (`tailscale set --ssh` ratified)
- ACL `tailscale/acl.hujson` from Node 0's swap: **RATIFIED on our side** (L2_ACCEPTANCE table, Fed-L2-001)

**The ONLY missing byte is the auth key**. We deliberately did not self-join the mesh:
the sovereign publish gate says a node does not join another node's tailnet on its own
authority. You mint the key; we flip the switch. That handshake is the entire point.

---

## The One-Key Join (runs on Node 1, one shot, idempotent)

```bash
# Node 0 (or tailnet admin) mints the key with tag:node1 attached:
#   Admin console → Settings → Keys → Generate auth key
#   Tags:  tag:node1   (node-qualified asus surface)
#   Reusable...: no  | Ephemeral...: no  | Preauth: yes

# Then on Node 1:
sudo tailscale up --authkey="${NODE0_MINTED_AUTHKEY}" \
  --hostname=kali-n1 \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:node1
```

### Verify the wire (from Node 1)

```bash
tailscale status          # both nodes online under MagicDNS
tailscale ping omega-hub  # → pong from Node 0 (mesh drop)
ssh omega-hub             # Node 0's hub shell over the mesh (if Node 0 enabled --ssh)
```

---

## Hashes of the two sovereign facts (belt + ponytail)

| Fact | Value |
|------|-------|
| ACL ratified on Node 1 | `a22e74e` (L2 acceptance record) |
| Payload manifest (USB) | `docs/federation/node0_received/PAYLOAD_MANIFEST.md` |

---

⬡ OMEGA ⬢ NODE1-COMPLETION-GUIDE ⬢ FED-N1-COMPLETE-001 ⬢ FIRST-CANONICAL-JOIN-DOC ⬢ READY-FOR-NODE0-INTAKE ⬡
