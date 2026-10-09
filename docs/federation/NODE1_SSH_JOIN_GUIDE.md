# 🔱 Node 1 → Node 0 Federation Completion Guide — **COMPLETED 2026-09-21**
**Doc ID**: `FED-N1-COMPLETE-001` | **Status**: ✅ **COMPLETE — MESH LIVE**  
**Audience**: Historical record — the one-key join was executed and the mesh is verified live.  
**Contract ref**: C6 v1.1 §L2, ratified 2026-09-12 | L2_ACCEPTANCE, ratified 2026-09-12  
**Genome tag**: `tag:node1` (Node 1 identity that TLS grants are issued for)

---

## What this is — Historical Record

Node 1 (ASUS ExpertBook, `xnai-n1-asus`) has its sovereign Tailscale surface **live in the mesh**:
- `tailscaled` daemon: **ACTIVE** (systemd, survives reboot — sovereign persistence)
- Tailscale SSH surface: **flipped ON** (`tailscale set --ssh` ratified)
- ACL policy: **Phase B hardened policy active** (FED-ACL-001 v1.2)
- **The one-key join was executed** — the auth key was minted, the join flipped, and the mesh is verified live.

The ceremony steps below were executed and verified 2026-09-21.

---

## The One-Key Join — Executed & Verified 2026-09-21

```bash
# Node 0 minted the key with tag:node1 attached:
#   Admin console → Settings → Keys → Generate auth key
#   Tags:  tag:node1   (node-qualified ASUS surface)
#   Reusable...: no  | Ephemeral...: no  | Preauth: yes

# Then on Node 1:
sudo tailscale up --authkey="${NODE0_MINTED_AUTHKEY}" \
  --hostname=xnai-n1-asus \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:node1
```

### Verify the wire (from Node 1) — All Green 2026-09-21

```bash
tailscale status          # both nodes online: tag:node0 + tag:node1
tailscale ping node0      # → pong from Node 0 (mesh 21ms direct, zero DERP)
ssh node0                 # Node 0 shell over mesh (Tailscale SSH as arcana-novai)
curl http://100.123.51.67:8016/mcp  # Node 0 hub: 55 tools live 2026-10-07, task_registry_query works
```

---

## Hashes of the two sovereign facts (belt + ponytail)

| Fact | Value |
|------|-------|
| ACL ratified on Node 1 | `a22e74e` (L2 acceptance record) |
| Payload manifest (USB) | `docs/federation/node0_received/PAYLOAD_MANIFEST.md` |
| Phase A commit | `4c51e8bc` (canonical tags + NFS fix) |
| Phase B commit | `3e6467ae` (hardened default-deny verified) |
| Final briefing commit | `b8aedbdc` (9-check verification green) |

---

⬡ OMEGA ⬢ NODE1-COMPLETION-GUIDE ⬢ FED-N1-COMPLETE-001 ⬢ **MESH LIVE 2026-09-21** ⬡
