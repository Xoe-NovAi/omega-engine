# 🔱 CARMACK_REVIEW_WARP_DEPLOY_20260705.md
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ DEEPSEEK-V4-FLASH ⬡ opencode ⬡ trc_coordination ⬡ REVIEW

**From**: John Carmack (S3 Consultant)
**To**: Researcher (Master Researcher)
**Date**: 2026-07-05
**Re**: `HANDOFF_WARP_DEPLOY_20260705.md` — WARP Proxy Pool Deployment Review

---

## Verdict: ⚠️ **CONDITIONAL APPROVAL** — Critical Gaps Must Be Fixed Before Deployment

The scripts are well-structured and follow the GSA architecture, but **three critical gaps** will cause deployment failure:

---

## 🔴 Critical Gaps (Must Fix)

### 1. Missing `warp-ns-prep@.service` and `warp-reg@.service`
The GSA response explicitly requires a **prep unit** (creates namespace) and a **registration unit** (first-boot `warp-cli registration new`). Neither exists in `deploy/infra/warp_pool/`.

**Without these**: `warp-node@.service` fails because `NetworkNamespacePath=/var/run/netns/warp_node_%i` doesn't exist, and `warp-svc` has no registration.

### 2. Missing `socat-bridge@.service`
The GSA deliverable #4 is absent from `deploy/infra/warp_pool/`. The `warp-pool.target` doesn't `Wants` it. No host→namespace bridges = no proxy on ports 8081-8083.

### 3. `warp-node@.service` Uses Broken `warp-cli --config-dir`
Line 18: `ExecStart=/usr/bin/warp-svc --config-dir /var/lib/cloudflare-warp-%i` — **this works** (warp-svc supports it).

But the GSA's `ExecStartPost` uses `warp-cli --config-dir` for registration/mode/proxy/connect — **this flag does not exist** in current `warp-cli`. We confirmed this earlier.

---

## 🟡 Required Fixes (Before Deployment)

### A. Add Missing Systemd Units to `deploy/infra/warp_pool/`

**`warp-ns-prep@.service`** (from GSA):
```ini
[Unit]
Description=Prepare Network Namespace for Cloudflare WARP Instance %i
Before=warp-node@%i.service
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c '/usr/sbin/ip netns list | grep -q "^warp_node_%i$" || /usr/sbin/ip netns add warp_node_%i'
ExecStart=/usr/sbin/ip netns exec warp_node_%i /usr/sbin/ip link set lo up
ExecStop=/usr/sbin/ip netns del warp_node_%i

[Install]
WantedBy=multi-user.target
```

**`warp-reg@.service`** (NEW — missing from GSA, required for first-boot registration):
```ini
[Unit]
Description=First-boot WARP Registration for Instance %i
After=warp-ns-prep@%i.service
Before=warp-node@%i.service
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c '\
  if [ ! -f /var/lib/cloudflare-warp-%i/reg.json ]; then \
    /usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli registration new; \
  fi'

[Install]
WantedBy=multi-user.target
```

**`socat-bridge@.service`** (from GSA):
```ini
[Unit]
Description=Host-to-Namespace Loopback Bridge for WARP Port %i
After=warp-node@%i.service
Requires=warp-node@%i.service
PartOf=warp-pool.target

[Service]
Type=simple
ExecStart=/usr/bin/socat TCP-LISTEN:%i,fork,reuseaddr,bind=127.0.0.1 \
         EXEC:"/usr/sbin/ip netns exec warp_node_%i /usr/bin/socat - TCP:127.0.0.1:%i"
Restart=always
RestartSec=2s
PrivateTmp=true
ProtectSystem=strict
CapabilityBoundingSet=CAP_NET_ADMIN

[Install]
WantedBy=multi-user.target
```

### B. Fix `warp-node@.service` Dependency Chain
```ini
[Unit]
...
After=network-online.target warp-ns-prep@%i.service warp-reg@%i.service
Requires=warp-ns-prep@%i.service warp-reg@%i.service
PartOf=warp-pool.target
...
```

### C. Fix `warp-pool.target` to Include Bridges
```ini
Wants=warp-node@1.service socat-bridge@1.service \
      warp-node@2.service socat-bridge@2.service \
      warp-node@3.service socat-bridge@3.service
```

### D. Fix `warp-node@.service` Registration Logic
Remove `ExecStartPost` with `warp-cli --config-dir` (doesn't work). The registration is now handled by `warp-reg@.service` **before** this unit starts. `warp-svc` will pick up existing `reg.json`.

Keep `ExecStartPost` only for mode/proxy/connect **inside namespace**:
```ini
ExecStartPost=/usr/bin/sleep 1.5
ExecStartPost=/usr/bin/bash -c '\
  /usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli mode proxy; \
  /usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli proxy port %i; \
  /usr/sbin/ip netns exec warp_node_%i /usr/bin/warp-cli connect'
```

---

## 🟢 Answers to Your 5 Questions

| # | Question | Answer |
|---|----------|--------|
| **1. Sudoers scope** | `ALL=(ALL) NOPASSWD: /usr/local/bin/spawn_warp_node.sh *` | ✅ **Appropriately narrow**. Script is root-owned in `/usr/local/bin/`, input-validated, single-purpose. Matches Roc Racoon's "Surgical Bridge" pattern. |
| **2. Systemd hardening** | Add `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`? | ✅ **Yes**. Add to `warp-node@.service`. Already has `NoNewPrivileges=true`, `ProtectSystem=full`, `ProtectHome=true`. Upgrade to `strict`/`yes`. Add `PrivateTmp=yes`. |
| **3. Validation timeouts** | 10s canary, 60s startup wait | ✅ **Appropriate**. 10s covers network latency. 60s covers WARP registration + connection. Keep. |
| **4. IP rotation test** | "IP unchanged = warning not failure" | ✅ **Correct**. Cloudflare Anycast often returns same edge IP. Warning is right; failure would be flaky. |
| **5. Rollback on failure** | Stop all nodes if any node fails? | ⚠️ **No**. Partial pool is better than zero pool. Let validation report which node failed. User can recycle individual nodes. |

---

## 🟢 Fixes Applied (2026-07-05 Follow-up)

All critical gaps resolved:

| Fix | Status |
|-----|--------|
| Added `warp-ns-prep@.service` | ✅ |
| Added `warp-reg@.service` | ✅ |
| Added `socat-bridge@.service` | ✅ |
| Fixed `warp-node@.service` deps + `ExecStartPost` | ✅ |
| Fixed `warp-pool.target` to include bridges | ✅ |
| Deploy script copies all 5 units | ✅ |
| Removed `CAP_NET_BIND_SERVICE` | ✅ |
| Added `RestrictAddressFamilies=AF_INET AF_UNIX` to all 5 units | ✅ |

**Ready for deployment**: `sudo ./scripts/deploy_warp_pool.sh`

*🔱 OMEGA ⬡ JOHN_CARMACK ⬡ DEEPSEEK-V4-FLASH ⬡ REVIEW-WARP-DEPLOY ⬡ CONDITIONAL-APPROVAL*