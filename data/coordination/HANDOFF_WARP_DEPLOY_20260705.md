# 🔱 Handoff Packet — WARP Proxy Pool Deployment Scripts
⬡ OMEGA ⬡ RESEARCHER ⬡ MIMO-V2.5-FREE ⬡ opencode ⬡ trc_handoff ⬡ HANDOFF-PACKET

---

## §1 Packet Metadata

| Field | Value |
|-------|-------|
| **Packet ID** | `handoff_warp_deploy_20260705_001` |
| **From** | Researcher (Sovereign Master Researcher) |
| **To** | John Carmack (S3 Consultant) |
| **Date** | 2026-07-05 |
| **Priority** | 🔴 P0 — Pre-deployment review required |
| **Status** | 📤 SENT — Awaiting review |

---

## §2 Deliverables for Review

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `scripts/deploy_warp_pool.sh` | System deployment automation | 180 | ✅ Ready |
| `docs/research/warp_proxy_pool/validate_warp_pool.sh` | Standalone validation | 122 | ✅ Ready |

---

## §3 What Needs Review

### 3.1 Deployment Script (`deploy_warp_pool.sh`)
**Purpose**: One-command deployment of WARP Proxy Pool to production system.

**Key areas for Carmack review:**
1. **Systemd unit deployment** — Correct paths, permissions, daemon-reload sequence
2. **Sudoers configuration** — Security implications of passwordless `spawn_warp_node.sh`
3. **Service startup sequence** — `enable` → `start` → wait for readiness
4. **Error handling** — Timeout logic, rollback on failure
5. **Resource limit verification** — Confirms MemoryMax/MemoryHigh/CPUQuota applied

### 3.2 Validation Script (`validate_warp_pool.sh`)
**Purpose**: Post-deployment verification of all pool components.

**Key areas for Carmack review:**
1. **Canary probe reliability** — `cdn-cgi/trace` parsing, timeout values
2. **IP rotation test** — Recycle command, wait time, IP comparison logic
3. **Systemd resource limit checks** — Correct `systemctl show` queries
4. **Sudoers verification** — Confirms deployment succeeded
5. **Exit codes** — Proper 0/1 for CI integration

---

## §4 Context for Reviewer

### Architecture Summary
- **3 WARP nodes** in isolated Linux Network Namespaces (`warp_node_1/2/3`)
- **Ports**: 8081 (ns_background), 8082/8083 (ns_ephemeral)
- **Bridge**: `socat` host↔namespace loopback (no veth pairs)
- **Integration**: `ModelGateway` routes `opencode-zen` through pool via `EphemeralWarpPool`

### Security Considerations
- `spawn_warp_node.sh` requires root (CAP_NET_ADMIN for `ip netns`)
- Passwordless sudo scoped to single script with args
- `socat` bridges only bind to `127.0.0.1` (no external exposure)
- `socks5h://` forces DNS through WARP exit node (no local DNS leaks)

### Resource Budget (Ryzen 5700U / 12GiB)
| Component | Per Instance | 3-Node Pool |
|-----------|--------------|-------------|
| `MemoryMax` | 150 MB | 450 MB |
| `MemoryHigh` | 120 MB | 360 MB |
| `CPUQuota` | 15% | 45% |
| `warp-svc` RSS | ~45-75 MB | ~135-225 MB |

---

## §5 Specific Questions for Carmack

1. **Sudoers scope**: Is `arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/spawn_warp_node.sh *` appropriately narrow? Should we restrict to specific args (`start|recycle|stop|destroy|status`)?

2. **Systemd hardening**: Should we add `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes` to `warp-node@.service`?

3. **Validation timeouts**: 10s canary timeout, 60s node startup wait — appropriate for production?

3. **IP rotation test**: Current test recycles node 1 and compares IPs. If same Anycast gateway, IP may not change. Is "IP unchanged = warning not failure" correct?

4. **Rollback on deploy failure**: If node 2 fails to start, should we stop nodes 1 and 3 and exit 1?

5. **CI integration**: Should validation script output JUnit XML or TAP for CI consumption?

---

## §6 Related Files (Reference)

| File | Purpose |
|------|---------|
| `scripts/spawn_warp_node.sh` | Lifecycle script being deployed (v1.2.0) |
| `deploy/infra/warp_pool/warp-node@.service` | Systemd template (v1.1.0) |
| `deploy/infra/warp_pool/warp-pool.target` | Systemd target (v1.0.0) |
| `src/omega/proxy_pool.py` | Python orchestration (already integrated) |
| `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` | Full specification (v1.2.0) |

---

## §7 Acceptance Criteria

Carmack's review should verify:

- [ ] Deployment script is idempotent (safe to re-run)
- [ ] Sudoers configuration follows least-privilege
- [ ] Systemd units have appropriate hardening flags
- [ ] Validation script catches real failures (not false positives)
- [ ] Error messages are actionable for debugging
- [ ] Scripts follow project coding standards (AP tokens, heritage tags)
- [ ] No shell injection vulnerabilities
- [ ] Proper cleanup on interrupt (SIGINT/SIGTERM)

---

## §8 Handoff Protocol

**Next Steps:**
1. Carmack reviews both scripts
2. Carmack writes `CARMACK_REVIEW_WARP_DEPLOY_20260705.md` with findings
3. Researcher applies fixes if needed
4. User executes deployment after approval

**Communication Channel**: `data/coordination/` directory

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ HANDOFF ⬡ TO-CARMACK ⬡ P0-REVIEW-REQUIRED ⬡ 2026-07-05*