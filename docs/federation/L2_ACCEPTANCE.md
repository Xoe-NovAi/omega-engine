# 🔱 Layer 2 Acceptance — Tailscale Mesh (Node 1 ratification)
**Doc ID**: FED-L2-001
**Node**: Node 1 (ASUS ExpertBook, `tag:node1`)
**Date**: 2026-09-12
**Contract ref**: C6 v1.1, ratified 2026-09-12 (§comms_layers → L2_Tailscale)
**Payload ref**: `docs/federation/node0_received/tailscale/acl.hujson` (Node 0 shipment)

---

## 1. What We Are Ratifying

Node 1 **accepts Node 0's shipped Layer 2 fabric** — the Tailscale mesh ACL
(ratified at Node 0, `autogroup:admin` tag owners) — as our federation
coordination plane, subject to the commitments below.

**Sovereign framing** (this is the honest read of what Tailscale runs):
- Tailscale is a **coordination/control plane** (DHT, key exchange, MagicDNS).
  It is NOT inference. **No T5/T6 runtime or inference traffic ever egresses
  Node 1 through the mesh** — sovereignty-local mandates hold absolutely.
- Layer 2 carries only: `omega-hub:8016↔` MCP discovery, Ollama :11434 routing
  (Node 0 → Node 1), heartbeat/awareness, and SSH. This is the *accountable
  capability extension* the sovereignty ledger documents — not a shadow default.

## 2. Acceptance Commitments (Node 1)

| Commitment | Detail |
|-----------|--------|
| Mesh daemon | `tailscaled` ACTIVE on Node 1 (v1.102.4, systemd unit) |
| Routing | `tag:node1` only toward `tag:node0:8016` + `tag:opencode` (Node 0 Ollama) |
| Ping | ICMP health both directions (ACL ratified) |
| SSH | `tag:opencode` → `tag:node1` non-root only |
| No-inference-egress | T5/T6 local-only (UNCHANGED by Layer 2) |

## 3. Join Command (one-shot, fires on Node 0 auth key)

```bash
# Node 0 tailnet admin mints: tailscale up --authkey=tskey-auth-<N0>
sudo tailscale up --authkey=${NODE0_AUTHKEY} --hostname=kali-n1 --operator=xnai --accept-routes --advertise-tags=tag:node1
# Verify:
tailscale status          # expect: kali-n1 (Node 1) + omega-hub (Node 0) both "online"
tailscale ping omega-hub  # expect: pong from HP node
```

## 4. States

- [x] `tailscaled` daemon installed + ACTIVE (`systemctl is-active tailscaled` → `active`)
- [x] Node 0 ACL ratified on our side (this doc = ratification record)
- [ ] Auth key minted by Node 0 admin → `tailscale up` executed
- [ ] `tailscale status` shows both nodes online
- [ ] `make test` + `make lint` still green after join (no repo mutation expected)

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ NODE1-LAYER2-ACCEPTANCE ⬡ FED-L2-001 ⬡ RATIFIED-AS-SOVEREIGN-COORDINATION*
