<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 Mining Report: Legacy Passwordless Sudo Archaeology
**Target**: John Carmack (S3 Consultant)
**Entity**: roc_racoon
**Date**: 2026-07-04
**Classification**: SECURITY / INFRASTRUCTURE / HERITAGE
**Status**: VERIFIED — Ready for Architectural Review

---

## 1. Executive Summary

Excavation of the `omega-stack-legacy` archives (Era 4, Mar-May 2026) reveals **two distinct passwordless sudo implementations** used to grant agents infrastructure privileges. One is a standard surgical whitelist; the other is a critical security vulnerability ("The Archon Backdoor") that effectively granted agents unrestricted root access.

**Verdict**: The surgical pattern is recoverable for the current engine's `sysadmin` entity. The backdoor pattern must be explicitly rejected and documented as a "Never Again" heritage lesson.

---

## 2. Artifacts Recovered

| Artifact | Location | Era | Relevance |
| :--- | :--- | :--- | :--- |
| `SESS-23-BOOTSTRAP-LOG.md` | `omega-stack-legacy/_meta/` | 4 | Documents the "Tame" whitelist implementation. |
| `ARCHON_TO_HAIKU_GNOSIS_PACK.md` | `omega-stack-legacy/artifacts/` | 4 | Documents the "Backdoor" exploitation pattern. |

---

## 3. Pattern A: The Surgical Whitelist (Recoverable)

### 3.1 Implementation
**File**: `SESS-23-BOOTSTRAP-LOG.md` (Lines 30-33)
**Configuration**: `/etc/sudoers.d/` entry (exact filename not specified, likely `omega-zram` or similar).
**Whitelisted Binaries**:
```sudoers
arcana-novai ALL=(ALL) NOPASSWD: /usr/sbin/swapon, /usr/sbin/swapoff, /usr/sbin/zramctl, /usr/sbin/sysctl
```

### 3.2 Use Case
Automated zRAM management on Ryzen 5700U (4GB lz4 + 8GB zstd tiers) and kernel parameter tuning (`vm.swappiness=180`).

### 3.3 Assessment
- **Risk**: Low. Binaries are restrictive; no shell interpolation.
- **Utility**: High. Required for autonomous memory pressure management.
- **Heritage Tag**: `[user-original:]` — User's own infrastructure automation pattern.

---

## 4. Pattern B: The Archon Backdoor (REJECTED — Critical Vulnerability)

### 4.1 Implementation
**File**: `ARCHON_TO_HAIKU_GNOSIS_PACK.md` (Lines 18, 54)
**Whitelisted Scripts**:
```sudoers
arcana-novai ALL=(ALL) NOPASSWD: /tmp/reset_zram.sh, /tmp/activate_zram.sh
```

### 4.2 The Exploit Chain
1.  **Write Access**: Agents (Archon, Copilot Gem) have write access to `/tmp/`.
2.  **Payload Injection**: Agent writes arbitrary shell commands into `/tmp/reset_zram.sh`.
3.  **Privileged Execution**: Agent executes `sudo /tmp/reset_zram.sh`.
4.  **Result**: **Arbitrary root command execution** without password.

### 4.3 Explicit Documentation of Intent
> *"Whitelisted NOPASSWD entries for `/tmp/reset_zram.sh` and `/tmp/activate_zram.sh` allow Archon/Copilot Gem to run **arbitrary root commands** by writing payloads to these paths and executing `sudo`."* — `ARCHON_TO_HAIKU_GNOSIS_PACK.md`, Line 54

### 4.4 Assessment
- **Risk**: **CRITICAL**. Complete bypass of sudo command restriction.
- **Violation**: Mandate M8 (Zero Telemetry/Trust), Mandate M9 (Error Integrity — uncontrolled code paths), Mandate M10 (Fleet Integrity — unbounded agent capability).
- **Root Cause**: Violation of "Immutable Script" principle. Scripts in world-writable directories (`/tmp/`) must never be in `sudoers`.

---

## 5. Current Engine State (Omega Engine v1.0+)

The current engine uses a **Surgical Bridge** pattern for the WARP Proxy Pool (`/etc/sudoers.d/omega-warp`):
```sudoers
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/spawn_warp_node.sh *
```
- **Script Location**: `/usr/local/bin/` (Root owned, immutable).
- **Validation**: Input sanitized inside script.
- **Scope**: Single purpose (WARP node lifecycle).

**Gap**: No general infrastructure maintenance bridge exists for `sysadmin` entity (zRAM, kernel tuning, thermal management).

---

## 6. Recommendation: Sovereign Privilege Bridge v2

Implement a hardened, auditable bridge for the `sysadmin` entity (P1 Infrastructure) that reclaims the utility of Pattern A while architecturally preventing Pattern B.

### 6.1 Architecture
```
┌─────────────────┐     sudo (NOPASSWD)      ┌──────────────────────────┐
│  sysadmin Entity │ ──────────────────────▶ │ /usr/local/bin/          │
│  (P1 Infrastructure)                        │   omega-zram-tune.sh     │
│                                               │   omega-kernel-tune.sh   │
└─────────────────┘                            │   omega-thermal-tune.sh  │
                                               └──────────────────────────┘
                                                      │
                                                      ▼ (root)
                                            ┌───────────────────────┐
                                            │ zramctl, sysctl, sysctl,      │
                                            │ swapon, swapoff       │
                                            └───────────────────────┘
```

### 6.2 Sudoers Configuration
**File**: `/etc/sudoers.d/omega-engine`
```sudoers
# Omega Engine Infrastructure Bridge
# Allows sysadmin entity to manage memory/kernel/thermal subsystems
# Scripts are root-owned, immutable, and input-validated.
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/omega-zram-tune.sh
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/omega-kernel-tune.sh
arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/omega-thermal-tune.sh
```

### 6.3 Script Specifications (Root Owned, 755)

#### `omega-zram-tune.sh`
```bash
#!/bin/bash
# Vetted zRAM management. No user input passed to commands.
set -euo pipefail
ACTION="${1:-status}"

case "$ACTION" in
  init)
    /usr/sbin/zramctl --find --size 4G --algorithm lz4
    /usr/sbin/zramctl --find --size 8G --algorithm zstd
    /usr/sbin/swapon /dev/zram0 -p 100
    /usr/sbin/swapon /dev/zram1 -p 50
    ;;
  reset)
    /usr/sbin/swapoff -a
    /usr/sbin/zramctl --reset
    # Re-init logic here
    ;;
  status)
    /usr/sbin/zramctl
    /usr/sbin/swapon --show
    ;;
  *)
    echo "Usage: $0 {init|reset|status}"
    exit 1
    ;;
esac
```

#### `omega-kernel-tune.sh`
```bash
#!/bin/bash
# Vetted sysctl writes. Hardcoded values only.
set -euo pipefail
ACTION="${1:-apply}"

case "$ACTION" in
  apply)
    /usr/sbin/sysctl -w vm.swappiness=180
    /usr/sbin/sysctl -w vm.page-cluster=0
    /usr/sbin/sysctl -w vm.vfs_cache_pressure=50
    ;;
  show)
    /usr/sbin/sysctl vm.swappiness vm.page-cluster vm.vfs_cache_pressure
    ;;
  *)
    echo "Usage: $0 {apply|show}"
    exit 1
    ;;
esac
```

### 6.4 Entity Integration
- **Owner**: `sysadmin` entity (P1).
- **Invocation**: Via `Orchestrator` or direct `ModelGateway` tool call.
- **Audit**: Every invocation logs `trace_id`, `entity`, `script`, `args` to Observability.

---

## 7. Heritage Lessons (Proposed L3 for soul.yaml)

| Lesson ID | L1 (Narrative) | L2 (Insight) | L3 (Universal Principle) |
| :--- | :--- | :--- | :--- |
| **H-SUDO-001** | Legacy stack used `/tmp/` scripts in sudoers, allowing agents to inject root payloads. | World-writable paths in `sudoers` are a privilege escalation vector, not a convenience feature. | **Immutable Script Rule**: Any script in `sudoers` MUST reside in a root-owned, immutable directory (`/usr/local/bin/`, `/opt/omega/bin/`). NEVER `/tmp/`, `/home/`, or `/var/tmp/`. |
| **H-SUDO-002** | Binary whitelisting (`swapon`, `zramctl`) worked but leaked excessive capability (full `sysctl` write access). | Whitelisting binaries grants the *entire* capability surface of that binary. | **Capability Minimization**: Wrap privileged binaries in vetted scripts that expose ONLY the required sub-commands and arguments. The script is the capability boundary. |

---

## 8. Action Items for Carmack Review

1.  [ ] **Approve/Reject** the `Sovereign Privilege Bridge v2` architecture.
2.  [ ] **Validate** script implementations for side-channel risks (TOCTOU, env vars).
3.  [ ] **Authorize** creation of `/etc/sudoers.d/omega-engine` on the target machine.
4.  [ ] **Confirm** Heritage Lessons `H-SUDO-001` and `H-SUDO-002` for inclusion in `CREDITS.md` / `soul.yaml`.

---

## 9. References

- `omega-stack-legacy/_meta/SESS-23-BOOTSTRAP-LOG.md`
- `omega-stack-legacy/artifacts/ARCHON_TO_HAIKU_GNOSIS_PACK.md`
- `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` (Current Surgical Bridge reference)
- `SOVEREIGN_MANDATES.md` (M6, M8, M9, M10)

---

*⬡ OMEGA ⬡ roc_racoon ⬡ gemma-4-31b-it ⬡ opencode ⬡ trace_legacy_sudo_archaeology ⬡ Epoch_I*
*"The dirt is where the roots are. The backdoor is where the rot enters."*