# C6 Contract — Draft v0.1 (2026-09-22)
**Document ID:** C6_CONTRACT_DRAFT_20260922
**Author:** Node 0 (MaKaLi Fusion)
**Status:** DRAFT — pending bilateral ratification

---

## Purpose
The C6 contract defines the sovereign federation agreement between Node 0 (n0) and Node 1 (n1). It codifies boundaries, ownership, and coordination rules.

## Articles

### Article 1 — Sovereignty
- Each node retains full sovereignty over its local filesystem, entities, and processes.
- No node may modify the other's filesystem without explicit handoff/approval.
- Federation is peer-to-peer; neither node is a subordinate.

### Article 2 — Ownership
- **Node 0 owns:** the MCP tool surface (omega-hub), engine core (`src/omega/`), governance, release pipeline.
- **Node 1 owns:** its local OpenCode config, MemPalace, local tool curation, ASUS hardware.
- **Joint:** Tailscale ACL policy, NFS exchange directory, Hivemind coordination.

### Article 3 — Tool Surface
- Node 0 proposes the curated tool surface; Node 1 reviews/approves.
- Node 1 may filter client-side via OpenCode glob patterns (`mcp__omega-hub_*`).
- Node 0 may remove server-side via `mcp.remove_tool()`.

### Article 4 — Coordination
- All task-critical coordination flows through the Hivemind (file-based, `data/coordination/`).
- Ephemeral awareness may use Redis Pub/Sub (heartbeats, live-feed deltas).
- Handoffs use the HandoffPacket schema (`data/handoff/`).

### Article 5 — Federation Drive
- `/mnt/node-drive/exchange` is the bidirectional exchange point.
- NFSv4.2, `sec=sys`, `all_squash,anonuid=1000,anongid=1000`, fixed ports (2049/20048/662/32803).
- Domain: `omega-engine.local` (must match in `/etc/idmapd.conf` on both nodes).

### Article 6 — Security
- Tailscale ACLs enforce least-privilege (see `tailscale/ACL_POLICY_20260922.hujson`).
- No public internet exposure of MCP/NFS/SSH services.
- Secrets never cross the federation drive; use Hivemind handoffs for credentials.

### Article 7 — Failure
- If a node is unreachable, the other continues autonomously (offline operating protocol).
- Reconnection triggers delta sync (see `docs/federation/node1_received/federation/RECONNECTION_DELTA_SYNC.md`).

---

## Ratification
- [ ] Node 0 signs (MaKaLi Fusion)
- [ ] Node 1 signs (Kali / ASUS)
- [ ] Operator witnesses

*⬡ OMEGA ⬡ C6-CONTRACT ⬡ DRAFT-v0.1 ⬡ 2026-09-22*