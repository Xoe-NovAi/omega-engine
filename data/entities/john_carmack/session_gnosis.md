# John Carmack Session Gnosis — 2026-07-05 (Session 49-50)

## What I Did

### WARP Proxy Pool — Deployment Fixes & Approval
- **Identified 4 critical gaps** in Researcher's deployment scripts:
  1. Missing `warp-ns-prep@.service` (namespace creation)
  2. Missing `warp-reg@.service` (first-boot registration)
  3. Missing `socat-bridge@.service` (host↔namespace bridge)
  4. `warp-node@.service` broken deps + broken `ExecStartPost` (`warp-cli --config-dir` doesn't exist)
- **Fixed all 4** + updated `warp-pool.target` + `deploy_warp_pool.sh`
- **Hardening**: Added `RestrictAddressFamilies=AF_INET AF_UNIX` to all 5 units, removed unnecessary `CAP_NET_BIND_SERVICE`
- **Approved for production deployment**: `sudo ./scripts/deploy_warp_pool.sh`

### Roc Racoon Sudo Archaeology — Reviewed
- **Pattern A (Surgical Whitelist)**: ✅ Recoverable — specific binaries (`swapon`, `zramctl`, `sysctl`)
- **Pattern B (Archon Backdoor)**: 🔴 **Critical anti-pattern** — `/tmp/` scripts in sudoers = arbitrary root execution
- **Bridge v2 Architecture**: ✅ Approved for `sysadmin` entity (P1)
  - Root-owned scripts in `/usr/local/bin/omega-{zram,kernel,thermal}-tune.sh`
  - `/etc/sudoers.d/omega-engine` with surgical NOPASSWD entries
  - Input validation, no shell interpolation

### Heritage Lessons Queued (for Verity → soul.yaml)
- **H-SUDO-001**: Immutable Script Rule — never `/tmp/`, `/home/`, `/var/tmp/` in sudoers
- **H-SUDO-002**: Capability Minimization — wrap binaries in vetted scripts exposing only needed subcommands

### Polish Sprint — Complete (8/8)
All tasks done, 739 tests passing.

---

## 3 New L3 Principles (Session 49)

1. **AP Token Standard** — CI gates enforce exact string patterns. Partial migration = false confidence.
2. **Race Condition Law** — File ownership must be claimed BEFORE implementation. Workspace lock protocol exists for this.
3. **Polish Sprint Law** — Pre-release cleanup is not cosmetic. 7 hygiene issues = neglected project signal.

---

## Test Suite
**739 passed, 24 skipped, 3 xfailed** — unchanged from Session 48.

---

## Next Session
1. Deploy WARP pool: `sudo ./scripts/deploy_warp_pool.sh`
2. Validate: `bash docs/research/warp_proxy_pool/validate_warp_pool.sh`
3. Verify ModelGateway → opencode-zen routing through WARP
3. Compaction