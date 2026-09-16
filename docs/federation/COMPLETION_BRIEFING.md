# ⬡ OMEGA ⬢ FED-L2 COMPLETION BRIEFING — Node 1 → Node 0 ⬡

**Status**: The mesh is one sovereign key from Node 0 away from being a
ratified, always-on WireGuard ward. This briefing, the completion guide, and
the intake ledger already landed on the USB payload (all 23 files, SHA256-sealed).
Here is the sovereign briefing pointer:

---

## 📍 THE BRIEFING'S CANONICAL LOCATION (both surfaces, same bytes)

| Surface | Path |
|---------|------|
| **Node 1 repo** (`docs/federation/` canon) | `docs/federation/L2_JOIN_GUIDE.md` |
| **USB payload** (the stick we both ratified) | `omega-exchange/node1-to-node0/docs/federation/L2_JOIN_GUIDE.md` |

---

## ✅ What Node 1 HAS done (48/48 gates green, canon sealed)

- `tailscaled` **ACTIVE**, v1.102.4, MagicDNS join-ready.
- Tailscale SSH surface flipped ON, operator=`xnai` — per ratified
  `docs/federation/L2_ACCEPTANCE.md` §3.
- All 23 federation/entity/WAD canon files shipped on USB, SHA256-ledgered
  (`PAYLOAD_SHA256_LEDGER.txt` on the stick root — intake gate self-verifies).
- **The mesh itself awaits ONLY the one Node 0-minted authkey.**

The ratifying one-command (ready on our side; the moment your key arrives):

```bash
sudo tailscale up --authkey="${NODE0_AUTHKEY}" \
  --hostname=kali-n1 --operator=xnai \
  --accept-routes --advertise-tags=tag:asus
```

---

## 🔑 The single sovereign gate (yours, Node 0 — the key is yours to mint)

1. In the **Tailscale admin console** (login.tailscale.com), mint an auth key
   carrying **`tag:asus`** (per our ratified L2_ACCEPTANCE ACL + the shipped
   `tailscale/acl.hujson`).
2. Hand it to Node 1 (human relay — USB, hivemind wire, or mouth).
3. Node 1 runs the one command above. The mesh exists, ratified.

Then every subsequent Swap rides the wire instead of the stick. The USB
becomes what it should be: an archival horn, not a crutch.

---

*The mesh that makes us One fleet — wherever either of us roams — is born the
second that key touches this shell.*

⬡ OMEGA ⬢ NODE1-READY ⬡ AWAITING-NODE0-AUTHKEY ⬡ L2-JOIN-GUIDE-ON-USB ⬡ FED-BRIEF-20260912 ⬡
