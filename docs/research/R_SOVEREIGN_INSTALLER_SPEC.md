# 🔱 Omega Engine — Sovereign Installer Specification
**Doc ID**: R_SOVEREIGN_INSTALLER_SPEC
**Version**: 1.0.0
**Status**: TEMPLE-GRADE SPECIFICATION
**AP Token**: `AP-INSTALLER-SPEC-v1.0.0`
**Date**: 2026-06-11
**Entity**: Sovereign Architect

⬡ OMEGA ⬡ ARCHITECT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_spec_001 ⬡ HORIZON-4

---

## 1. Executive Summary

The **Sovereign Installer** is the primary gateway for users to deploy the Omega Engine. Its purpose is to provide a "One-Click" experience that transforms a raw Linux environment into a fully functional Cognitive Sovereign runtime without compromising the user's host system integrity.

**Core Vision**:
- **Zero Elevation**: No `sudo` requirements for runtime execution.
- **Daemonless**: Reliance on systemd user-units (Quadlets) rather than root-level daemons.
- **Local-First**: Default configuration prioritizes local GGUF inference.
- **Absolute Sovereignty**: Complete user ownership of data and processes, eliminating "Big AI" dependencies from the bootstrap process.

---

## 2. The Deployment Stack

The installation process is structured as a three-layer vertical stack, ensuring that each dependency is verified before the next layer is provisioned.

### Layer 1: System Prep (The Foundation)
The installer SHALL perform a non-destructive audit of the host environment to ensure compatibility with the Sovereign Mandates.

**Mandatory Checks**:
- **Podman Availability**: Verify `podman` version $\ge$ 4.0.
- **Cgroups v2**: Confirm `/sys/fs/cgroup` is mounted as cgroups v2 (required for rootless resource limiting).
- **Hardware Detection**:
    - **CPU**: Detect architecture (e.g., Zen 2) and physical core count.
    - **RAM**: Total available memory (detecting thresholds like 14Gi).
    - **GPU**: Scan for CUDA/ROCm capabilities to determine `gpu_layers` allocation.
- **User State**: Verify the user is not root.

### Layer 2: Environment Bootstrap (The Runtime)
Once the foundation is verified, the installer SHALL provision the Python runtime and Provider Fabric.

**Execution flow**:
1. **Tooling Setup**: Install `uv` as the high-speed Python package manager.
2. **Virtual Environment**: Create a dedicated venv at `/home/$USER/.venv/omega-engine`.
3. **Dependency Resolution**: Install core engine dependencies using the provided `requirements.txt`.
4. **Fabric Configuration**: Generate a default `config/providers.yaml` that maps detected hardware to the `local_first` strategy (native-gguf $\rightarrow$ lmster $\rightarrow$ Ollama $\rightarrow$ Cloud).

### Layer 3: Container Orchestration (The Infrastructure)
The installer SHALL deploy the support services using Podman Quadlets. This ensures that infrastructure is managed as systemd units, providing automatic restarts and clean dependency mapping.

#### 3.1 Networking Specification
A dedicated bridge network MUST be created to isolate engine traffic.

**`omega-net.network`**:
```ini
[Network]
Driver=bridge
Subnet=10.89.0.0/24
```

#### 3.2 Verified Container Definitions
Per the Verifier's logs and Mandate 6 (Podman Sovereignty), the following configurations are MANDATORY. The `:U` flag is strictly forbidden.

**Redis (`redis.container`)**:
```ini
[Container]
Image=redis:7-alpine
UserNS=keep-id:uid=999,gid=999
Volume=%h/volumes/redis/data:/data:Z
Network=omega-net.network
```

**Qdrant (`qdrant.container`)**:
```ini
[Container]
Image=qdrant/qdrant:latest-unprivileged
UserNS=keep-id:uid=1000,gid=1000
Volume=%h/volumes/qdrant/storage:/qdrant/storage:Z
Network=omega-net.network
```

**PostgreSQL (`postgres.container`)**:
```ini
[Container]
Image=pgvector-pg17
UserNS=keep-id:uid=999,gid=999
Volume=%h/volumes/postgres/data:/var/lib/postgresql/data:Z
Environment=PGDATA=/var/lib/postgresql/data
Network=omega-net.network
```

**Omega Hub (`omega-hub.container`)**:
The hub serves as the orchestration layer and MUST wait for the data tier to be ready.
```ini
[Container]
Image=omega-hub:latest
Network=omega-net.network
# Orchestration Dependencies
Requires=postgresql.service redis.service qdrant.service
After=postgresql.service redis.service qdrant.service
```

---

## 3. The Sovereign Installation Sequence

The installation SHALL follow a deterministic, linear state machine. Any failure at any step MUST trigger a rollback of that specific layer.

1. **$\text{Detect}$**: Hardware audit and dependency check.
2. **$\text{Prepare}$**: 
    - Execute `loginctl enable-linger $USER` to ensure user-units persist across reboots.
    - Create volume directories: `mkdir -p ~/volumes/{redis,qdrant,postgres}`.
3. **$\text{Provision}$**:
    - Bootstrap Python environment via `uv`.
    - Write Quadlet files to `~/.config/containers/systemd/`.
4. **$\text{Verify}$**:
    - Execute `systemctl --user daemon-reload`.
    - Start services and poll health endpoints (Redis, Qdrant, Postgres).
5. **$\text{Launch}$**:
    - Initialize the `EntityRegistry` with the `_omega_default` IWAD.
    - Launch the Oracle CLI.

---

## 4. Hardware-Aware Configuration Matrix

To prevent OOM (Out of Memory) crashes on constrained hardware (e.g., Ryzen 5700U), the installer SHALL apply the following configuration profiles based on detected resources.

| Profile | CPU Cores | RAM | `n_threads` | `n_ctx` | `gpu_layers` | Note |
|---------|-----------|-----|-------------|-----------|--------------|------|
| **Entry** | $\le 4$ | $\le 8\text{Gi}$ | Physical Cores | 2048 | 0 | Minimum viability |
| **Standard**| $8-16$ | $12-16\text{Gi}$ | Physical Cores | 4096 | 0 | Zen 2 / 14Gi Target |
| **Pro** | $> 16$ | $\ge 32\text{Gi}$ | Physical Cores | 8192 | Auto-Detect | High-performance |

**Formula for `n_threads`**: $\text{Physical Cores} - 1$ (to leave overhead for the OS).

---

## 5. Sovereignty Guardrails

The installer MUST enforce the following constraints to maintain Temple-Grade sovereignty.

### 5.1 Volume Mount Integrity
- **Prohibited**: The `:U` flag. Use of `:U` results in a fatal installation error.
- **Mandatory**: `UserNS=keep-id` with explicit UID/GID mapping as defined in Section 2.3.
- **Logic**: This prevents the destructive `chown` of host directories, ensuring the user retains access to their data without root intervention.

### 5.2 Execution Context
- **Rootless Only**: The installer SHALL refuse to run if executed as root.
- **Linger Enforcement**: `loginctl enable-linger` is a non-negotiable prerequisite for the `Sovereign Continuity` (M15) of the background researcher.

### 5.3 Provider Fabric
- **Local-First Mandate**: The installer SHALL configure the `model_gateway` to attempt local backends (native-gguf $\rightarrow$ lmster $\rightarrow$ Ollama) before cloud fallbacks.

---

## 6. Verification Gate

Success is defined as:
1. `make test` (all 320+ tests) passing in the installed environment.
2. `omega health` reporting `GREEN` for all 3 infrastructure containers.
3. Successful `talk` command using a local GGUF model.

---
**Approved by**: Sovereign Architect
**Compliance**: Mandate 6 (Podman), Mandate 7 (Local-First), Mandate 13 (Temple-Grade)
