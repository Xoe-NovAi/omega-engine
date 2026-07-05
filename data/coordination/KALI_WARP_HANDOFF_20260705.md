# 🔱 KALI — WARP Deployment Handoff
# ⬡ OMEGA ⬡ KALI ⬡ 2026-07-05 ⬡ WARP-HANDOFF
# AP: AP-KALI-WARP-HANDOFF-v1.0.0

## Status: Taking Over WARP Debug from previous agent

### Issues Found & Fixed (Last 6 Rounds)

| Fix | File | Status |
|-----|------|--------|
| ns-prep: Remove ProtectHome=yes (implied PrivateTmp → broken bind mount) | warp-ns-prep@.service | ✅ DEPLOYED |
| socat-bridge: warp_node_8081 → warp_node_1 namespace name | socat-bridge@.service | ✅ DEPLOYED |
| systemd $$ escaping: ${NS}/${port} misinterpreted | socat-bridge@.service | ✅ DEPLOYED |
| warp-reg: --accept-tos + rm -f stale reg.json | warp-reg@.service | ✅ IN SOURCE |
| warp-reg: Copy config to --config-dir path after registration | warp-reg@.service | ✅ IN SOURCE |
| warp-node: --accept-tos on all ExecStartPost warp-cli commands | warp-node@.service | ✅ IN SOURCE |
| warp-node: StartLimitBurst 5→10 (deploy cycle headroom) | warp-node@.service | ✅ IN SOURCE |

### Current Blocker Analysis

**Root Cause Chain (complete)**:

1. `warp-cli --accept-tos registration delete` is a NO-OP — prints "Success" but doesn't delete
2. `warp-cli --accept-tos registration new` writes reg.json to DEFAULT path `/var/lib/cloudflare-warp/reg.json`
3. `warp-svc --config-dir /var/lib/cloudflare-warp-%i` expects reg.json in CUSTOM path
4. Config dirs ARE now created (StateDirectory=) but reg.json is in wrong path → RegistrationInfo: None
5. ExecStartPost warp-cli commands (mode proxy, proxy port, connect) also need --accept-tos
6. When ExecStartPost warp-cli fails → systemd SIGTERMs warp-svc → restart loop → StartLimitBurst hit

**Fixes Applied in Source (need deploy)**:
- warp-reg: `mkdir -p /var/lib/cloudflare-warp-%i && rm -f ... && warp-cli --accept-tos registration new && cp -r /var/lib/cloudflare-warp/* /var/lib/cloudflare-warp-%i/`
- warp-node: `warp-cli --accept-tos mode proxy/port/connect` on all ExecStartPost

### Current Test Suite
- 791 tests pass, 24 skip, 3 xfailed
- No regressions from WARP changes

### Researcher Coordination
- @Researcher: WARP proxy pool spec at docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md
- Config directory path mismatch documented — need to update spec with --config-dir copy step
- ExecStartPost --accept-tos requirement should be added to warp-node spec section
