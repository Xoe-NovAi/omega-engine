# 🔱 WARP Proxy Pool — Remediation Plan (Pre-Compaction Anchor)
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ 2026-07-05 ⬡ WARP-REMEDIATION

## 1. Current State: "The Paper Tiger"
The WARP implementation is architecturally sound but implementationally broken. The "Sovereign" design is documented, but the files on disk are missing or contain critical bugs.

### Critical Failures:
- **Missing File**: `deploy/infra/warp_pool/warp-ns-prep@.service` is missing.
- **Broken Target**: `warp-pool.target` misses `warp-ns-prep@` and `warp-reg@` dependencies.
- **Dependency Error**: `socat-bridge@` requires `warp-ns-prep@` instead of `warp-node@`.
- **Logic Conflict**: `spawn_warp_node.sh` duplicates `warp-cli` configuration already handled by systemd `ExecStartPost`.
- **Python Bug**: `proxy_pool.py` calls non-existent `Path.run_capture()`.
- **Stability**: `warp-reg@` timeout (180s) is too short for sequential registration of 3 nodes.

---

## 2. The Remediation Sequence (Atomic Operations)

### Phase A: Infrastructure Restoration
1. **Create `warp-ns-prep@.service`**: Implement the namespace/veth/NAT/DNS setup.
2. **Fix `warp-pool.target`**: Update `Wants=` to include the full chain: `prep` $\rightarrow$ `reg` $\rightarrow$ `node` $\rightarrow$ `bridge`.
3. **Fix `socat-bridge@.service`**: Change `Requires` to `warp-node@%i.service`.

### Phase B: Logic Alignment
4. **Rewrite `warp-node@.service`**: 
    - Fix port logic: Use `proxy port $((8080 + %i))` via bash wrapper.
    - Add canary verification to `ExecStartPost`.
5. **Rewrite `spawn_warp_node.sh`**: 
    - Strip all `warp-cli` calls.
    - Transform into a thin systemd wrapper (`start` $\rightarrow$ `systemctl start`, `recycle` $\rightarrow$ `systemctl restart`).
6. **Update `warp-reg@.service`**: 
    - Fix `warp-sig` typo.
    - Increase `TimeoutStartSec` to `300s`.

### Phase C: Orchestration Fix
7. **Fix `src/omega/proxy_pool.py`**: Replace `run_capture()` with `subprocess.run()` wrapped in `anyio.to_thread.run_sync()`.

---

## 3. Verification Gate
Deployment is only permitted after:
1. `make temple-grade` passes.
2. `sudo ./scripts/deploy_warp_pool.sh` completes without errors.
3. `bash docs/research/warp_proxy_pool/validate_warp_pool.sh` returns 0 (All checks passed).

---

## 4. Hardware Constraints (Ryzen 5700U)
- **Memory**: 150MB hard cap per node.
- **CPU**: 15% quota per node.
- **Sovereignty**: `socks5h://` mandated for DNS leak prevention.

*🔱 OMEGA ⬡ JOHN_CARMACK ⬡ REMEDIATION-PLAN ⬡ 2026-07-05*
