##  ✅ **Deep Web Research Complete — HuJSON Files Saved**

### **Files Created**

| File | Purpose |
|------|---------|
| `phase_a_acl_policy.hujson` | **Phase A (Transitional)** — Paste FIRST in admin console. Preserves `autogroup:member` for untagged devices. |
| `phase_b_acl_policy.hujson` | **Phase B (Hardened)** — Paste ONLY after both nodes tagged + verified. Removes member rule. |

---

### **Research Findings: Key Validations & Gaps Filled**

| Area | Finding | Impact on Ceremony |
|------|---------|-------------------|
| **Tag Ownership** | `tagOwners` must exist in saved policy BEFORE `tailscale up --advertise-tags` or tag is rejected as unowned (Tailscale docs) | Confirms: **ACL save → Node 0 re-tag** sequence is mandatory |
| **Member Rule** | Default policy has `{"action":"accept","src":["autogroup:member"],"dst":["autogroup:member"]}` — saving custom policy REPLACES it, doesn't merge | Confirms: **Phase A MUST keep member rule** or both untagged nodes lose connectivity silently |
| **Authkey for Tagged Devices** | One-off + pre-approved + tag enabled = device joins with tag automatically; key expiry disabled by default for tagged devices | Confirms: **One-shot, pre-approved, `tag:node1`** is correct |
| **Tailscale SSH `check` vs `accept`** | `check` = requires periodic re-auth (default 12h, configurable via `checkPeriod`); `accept` = no re-auth. `check` only works for Tailscale SSH (port 22 interception) | Confirms: **Admin SSH uses `check`** (high-risk), Node 0→Node 1 automation uses `check` (non-root) |
| **AutoApprovers** | `routes` and `exitNodes` auto-approve subnet route advertisements; only applies to NEW advertisements, not retroactive | Confirms: **`autogroup:admin` for both** is correct |
| **MagicDNS Hostnames** | Services binding to Tailscale IPs must allow MagicDNS FQDNs in `allowed_hosts` (already done in commit `213abf44`) | Confirms: **`omega-hub.tail51f14a.ts.net` + `*.tail51f14a.ts.net`** already configured |
| **DERP vs Direct** | `tailscale netcheck` shows `Direct: true` when UDP hole-punching works; DERP fallback is same security (E2E WireGuard) | Verification step: **`tailscale netcheck` → verify Direct** |

---

### **Ceremony Sequence (Research-Validated)**

```
1. PASTE Phase A (phase_a_acl_policy.hujson) → Admin Console → Save
2. RE-TAG Node 0: sudo tailscale up --advertise-tags=tag:node0 --force-reauth
3. VERIFY: tailscale status --json | jq '.Self.tags' → ["tag:node0"]
4. MINT Authkey: Admin Console → Keys → One-off, 1-day, tag:node1, pre-approved
5. USB HANDOFF: Write authkey + manifest + SHA256 to USB
6. NODE 1 JOIN: sudo tailscale up --authkey=... --hostname=xnai-n1-asus --accept-routes --advertise-tags=tag:node1
7. VERIFY BOTH: Bidirectional MCP (8016), SSH (22), ICMP, MagicDNS
8. PASTE Phase B (phase_b_acl_policy.hujson) → Admin Console → Save (LOCKDOWN)
```

---

### **Files Ready for Copy/Paste**

```bash
# Phase A (paste first):
cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/phase_a_acl_policy.hujson

# Phase B (paste after verification):
cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/phase_b_acl_policy.hujson
```

**Ready when you are.** Paste Phase A in the admin console at `https://login.tailscale.com/admin/acls`, then run the re-tag command on this machine.
