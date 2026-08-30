<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: warp-proxy-pool
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
Multi-namespace WARP proxy pool for **OpenCode Zen (OCZ) IP rotation**. 3 isolated WARP tunnels → 3 SOCKS5 endpoints. ModelGateway injects proxy for `opencode-zen` provider only.

### STATUS (2026-07-22 — UPDATED)
| Item | State |
|------|--------|
| Spec | ✅ `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| Python package | ✅ editable install in omega `.venv` (`warp-proxy-pool` pyproject TOML fixed) |
| Host `warp-svc` | ✅ running |
| `warp-ns-prep@{1,2,3}` | ❌ **failed** — syntax error in installed setup script |
| Root cause | `/usr/local/bin/warp-ns-setup` **truncated** at line 49 (`awk '{print` broken) |
| Good source | `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh` |
| SOCKS 8081–8083 | ❌ not listening |
| Ticket | **W-1** — `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` |
| Ark | D-381, D-379 |

### KEY FILES
| Type | Path |
|------|------|
| Critical path | `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` |
| Spec | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` |
| Deploy | `scripts/deploy_warp_pool.sh` |
| Validate | `docs/research/warp_proxy_pool/validate_warp_pool.sh` |
| Lifecycle | `scripts/spawn_warp_node.sh` |
| Systemd (repo) | `deploy/infra/warp_pool/*.service` |
| Setup script (source) | `../warp-proxy-pool/scripts/warp-ns-setup.sh` |
| Integration | `src/omega/proxy_pool.py`, ModelGateway OCZ proxy inject |
| Install helper | `scripts/fix_warp_ns_setup_and_restart.sh` |

### ARCHITECTURE
```
OCZ Request → ModelGateway → EphemeralWarpPool.get_proxy_url()
  → socks5h://127.0.0.1:{8081,8082,8083}
  → Linux netns (warp_node_N) → socat bridge → warp-svc → Cloudflare Exit IP
```

### WHAT IT DOES / DOESN'T DO
| ✅ DOES | ❌ DOESN'T |
|---------|------------|
| OCZ IP rotation (rate limit by source IP) | Antigravity quota (OAuth account) |
| 3 independent rate-limit buckets | Google AI Studio free-tier TPM (project/key) |
| Blue-green drain rotation | Fix free Gemma 16k cliff |

### BLOCKERS (ordered)
1. **Architect sudo**: copy good `warp-ns-setup.sh` → `/usr/local/bin/warp-ns-setup`
2. Restart `warp-ns-prep@1..3` → `warp-reg@` → `warp-node@` → `warp-bridge@` / `warp-pool.target`
3. Host `warp-cli` registration missing (expected until per-node reg completes)
4. Validate three distinct exit IPs

### DEPLOY / FIX (Architect)
```bash
# One-shot helper (prompts for sudo):
bash /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/fix_warp_ns_setup_and_restart.sh

# Or manual:
sudo cp /home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh /usr/local/bin/warp-ns-setup
sudo chmod 755 /usr/local/bin/warp-ns-setup
sudo bash -n /usr/local/bin/warp-ns-setup
sudo systemctl reset-failed 'warp-ns-prep@*'
sudo systemctl start warp-ns-prep@1 warp-ns-prep@2 warp-ns-prep@3
# then reg + node + bridge per CRITICAL_PATH W-1 section
```

### DECISIONS
- WARP = OCZ / IP-keyed only (D-379)
- Complementary to Antigravity multi-account (account-keyed)
- G-1 workhorse ≠ W-1 WARP (parallel unlocks)

---

*⬡ OMEGA ⬡ CPR ⬡ warp-proxy-pool ⬡ 2026-07-22*
