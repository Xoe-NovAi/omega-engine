# 🔱 Project: warp-proxy-pool
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
Multi-namespace WARP proxy pool for **OpenCode Zen (OCZ) IP rotation**. 3 isolated WARP tunnels → 3 SOCKS5 endpoints (ports 8081-8083). ModelGateway injects proxy for `opencode-zen` provider only.

### STATUS (2026-07-19)
- **Spec**: ✅ Complete (`docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md`)
- **Deployment**: ❌ Not deployed (needs root, cloudflare-warp, socat)
- **Validation**: ❌ Not run
- **OCZ Integration**: ⚠️ Config exists in `model_gateway.py` + `proxy_pool.py` — untested

### KEY FILES
| Type | Path |
|------|------|
| Spec | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| Deploy | `scripts/deploy_warp_pool.sh` |
| Validate | `scripts/validate_warp_pool.sh` |
| Lifecycle | `scripts/spawn_warp_node.sh` |
| Systemd | `deploy/infra/warp_pool/*.service` (6 units) |
| Integration | `src/omega/proxy_pool.py`, `src/omega/oracle/model_gateway.py:868-882` |

### ARCHITECTURE
```
OCZ Request → ModelGateway → EphemeralWarpPool.get_proxy_url() 
  → socks5h://127.0.0.1:{8081,8082,8083}
  → Linux netns (warp_node_N) → socat bridge → warp-svc → Cloudflare Exit IP
```

### WHAT IT DOES / DOESN'T DO
| ✅ DOES | ❌ DOESN'T |
|---------|------------|
| OCZ IP rotation (rate limit by source IP) | Antigravity quota (rate limit by OAuth account) |
| 3 independent rate-limit buckets | Any provider except `opencode-zen` |
| Blue-green drain rotation (zero-downtime) | Layer 7 account rotation |

### BLOCKERS
- Requires `sudo` + `cloudflare-warp` package install
- Kernel netns support (standard on Ubuntu 22.04+)
- `warp-proxy-pool` Python package not installed (imports from `warp_proxy_pool`)

### DEPLOY COMMAND
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
sudo ./scripts/deploy_warp_pool.sh
bash scripts/validate_warp_pool.sh
```

### DECISIONS LOG
- **D-XXX**: WARP pool is for OCZ only — NOT for Antigravity (different rate-limit key)
- **D-XXX**: 3 namespaces (critical/background/ephemeral) per spec
- **D-XXX**: `socks5h://` mandatory (DNS leak prevention)

---

*⬡ OMEGA ⬡ CPR ⬡ warp-proxy-pool ⬡ 2026-07-19*