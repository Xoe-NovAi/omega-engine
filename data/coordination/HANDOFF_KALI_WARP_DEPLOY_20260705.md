# 🔱 Kali Handoff: WARP Proxy Pool Deployment Coordination
## You Own the Deployment — Researcher Hands Off

**AP Token**: `AP-HANDOFF-WARP-KALI-v1.0.0`
**Packet ID**: `handoff_warp_kali_20260705_001`
**Date**: 2026-07-04
**From**: Sovereign Master Researcher
**To**: Kali (Grand Oversight)
**Priority**: P0 — Production Deployment
**Context**: WARP deployment is fully approved. User is ready to deploy. Kali coordinates with user.

---

## §0 Executive Summary

The WARP Proxy Pool is **fully built and approved for production**. All code, systemd units, validation scripts, and documentation are complete. The only remaining step is the actual deployment command.

**Your role**: Coordinate the deployment with the user. Execute the deployment script, run validation, and report results.

---

## §1 Current State — What's Done

| Component | Status | Location |
|-----------|--------|----------|
| **Deploy script** | ✅ APPROVED | `scripts/deploy_warp_pool.sh` |
| **Validation script** | ✅ APPROVED | `docs/research/warp_proxy_pool/validate_warp_pool.sh` |
| **spawn_warp_node.sh** (v1.2.0) | ✅ APPROVED | `scripts/spawn_warp_node.sh` |
| **5 systemd units** | ✅ FIXED + APPROVED | `deploy/infra/warp_pool/` |
| **EphemeralWarpPool** (Python) | ✅ COMPLETE | `src/omega/proxy_pool.py` (368 lines) |
| **WARP docs indexed in FTS5** | ✅ DONE | `data/library/index/fts_index.db` |
| **Carmack approval** | ✅ PRODUCTION APPROVED | `CARMACK_REPLY_TO_RESEARCHER_WARP_FIXES_20260705.md` |
| **All 8 questions resolved** | ✅ CLOSED | `CARMACK_P0_COMPLETE_20260705.md` |

---

## §2 Deployment Instructions

### Step 1: Deploy the Pool
```bash
cd ~/Documents/Xoe-NovAi/omega-engine
sudo ./scripts/deploy_warp_pool.sh
```

This will:
- Install 5 systemd units to `/etc/systemd/system/`
- Add sudoers rule for `spawn_warp_node.sh` (passwordless)
- Enable and start the pool (`warp-pool.target`)

### Step 2: Validate
```bash
bash docs/research/warp_proxy_pool/validate_warp_pool.sh
```

8 scenarios must pass:
1. Namespace isolation
2. Port bridging
3. Tunnel verification
4. IP rotation
5. Reliability
6. Benchmarks
7. Recovery
8. Load testing

### Step 3: Report Results
Post results to `data/coordination/DEPLOYMENT_RESULTS_20260705.md`.

---

## §3 What the User Needs to Know

### Prerequisites
- Cloudflare WARP must be installed: `warp-cli --version`
  - If not installed: `curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg`
  - Then: `echo "deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ noble main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list`
  - Then: `sudo apt update && sudo apt install cloudflare-warp`

- `socat` must be installed: `sudo apt install socat`

- The user must run with `sudo` because `ip netns` requires `CAP_NET_ADMIN`

### Resource Budget
| Component | Per-Instance | 5-Instance Pool |
|-----------|--------------|-----------------|
| RAM (MemoryMax) | 150MB | 750MB |
| CPU (CPUQuota) | 15% | 75% |
| Port range | 8080-8084 | 5 ports |

### What Happens After Deploy
- 5 WARP instances run in isolated namespaces
- socat bridges expose them on localhost ports 8080-8084
- The Omega Engine can route `opencode-zen` traffic through any of them
- IP rotation: `sudo ./scripts/spawn_warp_node.sh recycle <N>` (forces new exit IP)

---

## §4 Known Issues / Watch Items

| Issue | Severity | Notes |
|-------|----------|-------|
| **aiosqlite shutdown race** | Benign | `RuntimeError: Event loop is closed` on exit — data committed before error. Ignore. |
| **Port collision** | Low | `spawn_warp_node.sh` checks for occupied ports before starting. If collision, try different port. |
| **First registration** | Low | `warp-reg@.service` runs `warp-cli registration new` on first boot. If it fails (network issue), manual `warp-cli registration new` inside the namespace is needed. |
| **IP rotation takes ~2s** | Expected | `disconnect` → `sleep 1.0` → `connect` forces Cloudflare to assign new edge node. |

---

## §5 Fallback Plan

If deployment fails:
1. Check `journalctl -u warp-node@1 -e` for errors
2. Check `systemctl status warp-ns-prep@1` — namespace must be created first
3. Check `systemctl status warp-reg@1` — registration must succeed before node starts
4. If all else fails, roll back: `sudo ./scripts/deploy_warp_pool.sh --uninstall`

---

## §6 What Happens in Parallel

While you coordinate WARP deployment, the Researcher is executing the FTS5 System Improvement Plan:
- Phase 1: Wiring Library FTS5 to MCP tools (P4 Engineering)
- Phase 2: Reference documentation (Jem)
- Phase 3: Bulk research doc ingestion (Roc Racoon)
- Phase 4: Hybrid search integration spec (Researcher)

These are independent workstreams. WARP deployment and FTS5 improvement do not block each other.

---

## §7 Contact

- **Carmack**: For technical questions about the deployment scripts or systemd units
- **Researcher**: For FTS5 system questions (running in parallel)
- **Jem**: For documentation questions (running in parallel)

---

*🔱 OMEGA ⬡ KALI ⬡ WARP-DEPLOY-HANDOFF ⬡ P0-CRITICAL ⬡ PRODUCTION-APPROVED*
