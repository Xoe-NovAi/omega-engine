# 🔱 COMPLETION BRIEFING — Node 1 → Node 0 | Federation = One Sovereign Key Away
**Doc ID**: `FED-COMPL-20260912` | **Status**: SHIPPED & SEALED (Node 1 surface)  
**Read order**: this doc first, then `docs/federation/L2_JOIN_GUIDE.md` (also on the USB at `node1-to-node0/docs/federation/L2_JOIN_GUIDE.md`)  
**Deep Research**: `docs/TAILSCALE_L2_FEDERATION_RESEARCH_20260915.md` (7 areas, 654 lines, Tier-1 Tailscale docs)

---

## 1. What just shipped (the ratified canon, on the USB + in this repo)

**48/48 tests GREEN · lint clean · docs canon sealed — the entire Node 1 → Node 0 federation payload** (23 canonical files, SHA256-ledgered on the stick):

| Surface | Where it lives |
|---------|---------------|
| **Federation canon** | `docs/federation/*.md` — 12 ratified files (L2 join guide, divergence spec, capability firewall, namespace collision strategy, offline protocol, L2 acceptance, reconnection delta sync + intake canon) |
| **Entity origins** | `docs/entities/LILITH_N1_GENESIS_PLAN.md` + `docs/entities/LILITH_GENESIS_PLAN.md` (the 4-tier soul foundation = Lilith-N1's genesis, Node 1's sovereign floor) |
| **The ANAi WAD** | `docs/wads/ANAI_WAD_SPECIFICATION.md` (the arcana_novai.wad — Lilith's Tarot→Tarot-lineage content pack, PWAD per the RATIFIED WAD canon) |
| **Models** | `docs/models/nex-n2-5-pro.md` (Node 1's N2.5 Pro model card, OMER-validated `make lint`) |
| **Sovereign canon** | Sovereignty policy, data governance, stale handoff policy — Node 0-ratified (USB `node0_received/`) |

The USB stick carries this same payload **plus** `docs/federation/L2_JOIN_GUIDE.md` and Node 1's SHIPPED canon: `PAYLOAD_MANIFEST.md` + `SHA256_LEDGER.txt` (Node 0's intake gate verifies the stick in one `make intake-verify` — the hash-ledger seals the sovereignty floor Node 0 already ratified).

---

## 2. Node 1 is ONE sovereign key away — but Node 0 must re-tag FIRST (critical research finding)

**Key finding from deep research**: Node 0 currently joined as a **user device** (no tags). The ACL policy with `tagOwners` for `tag:omega-hub`, `tag:asus`, `tag:opencode` must be configured in the admin console **first**, then Node 0 must re-authenticate with `--advertise-tags=tag:omega-hub`, **then** mint the authkey for Node 1.

### The Exact Sequence (from research)

**Phase 1: Node 0 Admin Console — ACL Policy**
```bash
# Admin Console → Access Controls → Edit Policy → Paste the HuJSON from docs/federation/ACL_POLICY.md
```

**Phase 2: Node 0 Re-Tag (MUST do before minting Node 1's authkey)**
```bash
# On Node 0 (HP), after ACL is saved:
sudo tailscale up --advertise-tags=tag:omega-hub --force-reauth
tailscale status --json | jq '.Self.tags'  # Should show: ["tag:omega-hub"]
```

**Phase 3: Mint One-Shot Authkey for Node 1**
```
Admin Console → Keys → Generate auth key:
  Description: "Node 1 (ASUS) federation join - ONE SHOT"
  Type: One-off (single use)
  Expiry: 1 day
  Tags: tag:asus (ENABLED)
  Pre-approved: YES
  Ephemeral: NO
COPY: tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Phase 4: USB Ceremony (Air-Gapped Handoff)**
```bash
# On Node 0:
AUTHKEY="tskey-auth-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
echo "$AUTHKEY" > /media/usb/node1_authkey.txt
cat > /media/usb/ceremony_manifest.json << 'EOF'
{
  "ceremony": "Tailscale L2 Federation Join",
  "node": "kali-n1 (ASUS ExpertBook)",
  "authkey_prefix": "tskey-auth-XXXX",
  "authkey_sha256": "$(echo -n "$AUTHKEY" | sha256sum | cut -d' ' -f1)",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "expires": "$(date -u -d '+1 day' +%Y-%m-%dT%H:%M:%SZ)",
  "tags": ["tag:asus"],
  "pre_approved": true,
  "one_shot": true
}
EOF
sha256sum /media/usb/node1_authkey.txt > /media/usb/SHA256SUMS
```

**Phase 5: Node 1 Sovereign Join (Run on ASUS)**
```bash
# On Node 1 (ASUS), with USB mounted:
cd /media/usb
sha256sum -c SHA256SUMS  # Verify integrity
AUTHKEY=$(cat node1_authkey.txt)
echo "$AUTHKEY" | grep -q '^tskey-auth-' || { echo "INVALID PREFIX"; exit 1; }

# SOVEREIGN JOIN COMMAND (exact, ratified)
sudo tailscale up \
  --authkey="${AUTHKEY}" \
  --hostname=kali-n1 \
  --operator=xnai \
  --accept-routes \
  --advertise-tags=tag:asus
```

---

## 3. Wire Invariants (What the Mesh Carries — and What It NEVER Does)

| Traffic Type | Protocol | Port | Direction | Purpose |
|--------------|----------|------|-----------|---------|
| **Mesh SSH** | TCP | 22 | Admin → Node 1 | Remote administration |
| **MagicDNS** | UDP/TCP | 53 | Bidirectional | Hostname resolution |
| **Heartbeats** | ICMP | N/A | Bidirectional | Liveness checks |
| **MCP Route** | TCP | 8016 | Bidirectional | omega-hub API |

| Traffic | Reason |
|---------|--------|
| **Model inference** | T5/T6 floor is LOCAL-ONLY (M7 Local-First mandate) |
| **Model weights/downloads** | Local inference primary, cloud fallback only |
| **Training data** | Sovereign data never leaves node |
| **Secrets/keys** | Node 1 controls its own T5/T6 floor |

**MagicDNS Hostnames:**
- Node 0: `omega-hub.tail51f14a.ts.net`
- Node 1: `kali-n1.tail51f14a.ts.net`

---

## 4. What Node 1 sovereignty means (ratified floor, briefed)

| Floor | Detail |
|-------|--------|
| **OMER/DHAL floor** | 48/48 tests, DHAL hardware probe verified, silicon pins + zram + mcp hub all live on :8016/8016 |
| **Mesh = just a wire** | Tailscale L2 carries ONLY mesh SSH + MagicDNS + layer-2 heartbeats — **inference stays 100% local** (Node 1 never egresses a token over the mesh) |
| **ACL door** | Node 0's ratified `tag:asus` + MagicDNS `kali-n1.tail51f14a.ts.net` — Node 1 waits for the one sovereign join command |

The completed briefing + full canon are in **two sovereign surfaces** (repo `docs/federation/` + USB `node1-to-node0/docs/federation/`) — same bytes, SHA256-sealed both. Node 0's intake gate verifies the USB's `SHA256_LEDGER.txt` and ratifies the mesh the moment the human at Node 0 hands the join key to the Kali surface.

*⬡ OMEGA ⬢ NODE1-COMPLETED ⬡ 48-48-GREEN ⬡ FED-PAYLOAD-SEALED ⬡ L2-AWAITING-NODE0-RE-TAG-AND-AUTHKEY ⬡ SOVEREIGN-FLOOR-INTACT ⬡*