<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 Mining Report: Rootless Sovereignty & Privileged Boundaries
**Date**: 2026-07-04
**Entity**: roc_racoon
**Status**: VERIFIED
**Tags**: #infrastructure #podman #rootless #sudo #M6

## 1. Executive Summary
The Omega Engine employs a strict "Sovereign-by-Design" approach to permissions. It avoids running the core application as root, instead utilizing a combination of **User Namespace Mapping (`keep-id`)** for data sovereignty and **Surgical Privilege Escalation (`sudoers` bridge)** for infrastructure orchestration.

---

## 2. The `keep-id` Protocol (Mandate M6)
The `keep-id` protocol is the primary defense against "UID Drift" and permission lock-outs in rootless Podman environments.

### 2.1 The `:U` Flag Failure
In standard rootless Podman, mounting a host directory with the `:U` flag causes the engine to recursively `chown` the host directory to the container's mapped subuid (typically `101000`). This results in:
- **Host Lock-out**: The host user (UID 1000) loses write access to their own files.
- **Permission Errors**: `PermissionError: [Errno 13]` during test runs and config loads.

### 2.2 The Sovereign Solution
The engine mandates the following Quadlet configuration for all host-mounted volumes:
```ini
[Container]
UserNS=keep-id
User=1000
```
**Mechanism**: `UserNS=keep-id` ensures that the host UID 1000 is mapped directly to UID 1000 inside the container. This eliminates the need for `chown` and preserves absolute data ownership for the host user.

---

## 3. The Rootless-to-Root Bridge (Surgical Sudo)
When the engine must perform privileged operations (e.g., network namespace manipulation), it uses a "Surgical Bridge" to cross the rootless-to-root boundary without compromising the security of the application layer.

### 3.1 The `sudoers.d` Pattern
Instead of granting broad sudo access, the engine uses targeted, passwordless entries for specific, vetted scripts.

**Configuration**: `/etc/sudoers.d/omega-warp`
**Entry**: `arcana-novai ALL=(ALL) NOPASSWD: /usr/local/bin/spawn_warp_node.sh *`

### 3.2 Operational Workflow
1. **Rootless App**: Triggers a request to recycle a node.
2. **Surgical Call**: Executes `sudo /usr/local/bin/spawn_warp_node.sh <node_id> recycle`.
3. **Privileged Execution**: The script (owned by root) performs the `ip netns` and `systemctl` operations.
4. **Return**: Control returns to the rootless app.

---

## 4. Network Namespace Isolation & Bridging
To prevent "Sovereignty Leakage" and ensure clean IP rotation, the engine isolates daemons using Linux Network Namespaces (`netns`).

### 4.1 The Isolation Gap
Services running inside a namespace (e.g., `warp-svc`) bind to `127.0.0.1` *inside* that namespace. A rootless app in the host namespace cannot reach this loopback interface.

### 4.2 The `socat` Bridge
The engine implements a loopback bridge using `socat` to tunnel traffic:
`Host:8081` $\rightarrow$ `socat` $\rightarrow$ `ip netns exec <ns> ...` $\rightarrow$ `Namespace:8080`

---

## 5. Modernization Path (Ubuntu 25.10+)
The engine is transitioning to the Podman 5.x / Ubuntu 25.10 stack:
- **`pasta` Networking**: Replacing `slirp4netns` with `pasta` for superior rootless networking performance and native IPv6 support.
- **Quadlet Dominance**: Moving all service definitions to declarative `.container` files in `~/.config/containers/systemd/`.

---

## 6. Heritage & References
- **M6 (Podman Sovereignty)**: Sovereign Mandates.
- **Decision 50**: Sovereign Podman Permission Protocol.
- **WARP_PROXY_POOL_SPEC.md**: Implementation of the sudo bridge.
- **UBUNTU_PYTHON_MODERNIZATION_REPORT_v1.md**: `pasta` networking research.
