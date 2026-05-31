# 🔱 Sovereign Container Strategy: Rootless Podman & systemd Quadlets

**Document ID**: R_PODMAN_SOVEREIGN_STRATEGY  
**Status**: ✅ AUTHORITATIVE  
**Target Hardware**: Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM)  
**Sovereignty Score**: 10/10 (Zero-Root, Daemonless, Local-First)

---

## 1. Executive Summary
The Omega Engine requires a container orchestration layer that is secure, resource-efficient, and completely sovereign. This strategy replaces the legacy "Docker-style" daemon approach with a **Rootless Podman + systemd Quadlet** architecture. This eliminates the privileged daemon attack vector, ensures a minimal resource footprint on the Ryzen 5700U, and integrates containers as first-class citizens of the Linux init system.

## 2. Architectural Foundation

### 2.1 The Daemonless Model
Unlike Docker, Podman is daemonless. Each container is a direct child process of the caller (or systemd).
- **No Single Point of Failure**: A crash in one container or the management tool does not affect others.
- **True User Isolation**: Containers run as the Architect's user, mapping the container's root to an unprivileged host UID via user namespaces.

### 2.2 The Quadlet Standard (v5.0+)
The Omega Engine adopts **Quadlets** for all production services. We deprecate `podman generate systemd` in favor of declarative unit files.

| Unit Type | Extension | Purpose |
| :--- | :--- | :--- |
| **Container** | `.container` | Definitive spec for a single container service. |
| **Pod** | `.pod` | Groups containers into a shared network/resource namespace. |
| **Network** | `.network` | Defines a sovereign isolated network. |
| **Volume** | `.volume` | Manages persistent storage with automatic mapping. |

**Sovereign Path**: All rootless Quadlet files reside in `~/.config/containers/systemd/`.

---

## 3. Implementation Specifications

### 3.1 Volume & Permission Protocol
To eliminate "Permission Denied" errors in rootless mode, the following mount standard is mandatory:

**Standard Mount String**: `Volume=/host/path:/container/path:Z,U`
- **`:Z`**: (SELinux) Applies a private SELinux label to the volume.
- **`:U`**: (User) Automatically `chown`s the host directory to match the container's internal UID/GID.

**Critical Hardening**:
- **Runtime Dirs**: Use `Tmpfs=` for ephemeral directories (`/tmp`, `/app/logs`, `.cache`) to avoid host-level UID collisions.
- **Sticky Bit**: Set `1777` permissions on host directories that must be writable by multiple container sub-UIDs.
- **Pre-Creation**: All hidden runtime directories (e.g., `.chainlit/`) must be created in the `Dockerfile` to avoid runtime permission failures.

### 3.2 Resource Steering (Ryzen 5700U Optimization)
The Ryzen 5700U is bound by 14GB RAM. We use Cgroups v2 to enforce hard limits and prevent OOM crashes.

**Quadlet Resource Mapping**:
```ini
[Container]
Memory=1G              # Hard limit
MemoryReservation=512m # Soft limit
CPUShares=512          # Relative weight
PidsLimit=256          # Prevent fork-bombs
# Use the 'Ulimit' key for system-level constraints (e.g., nofile)
Ulimit=nofile=65536:65536
```

**Host-Level Delegation**:
To enable rootless limits, the host must delegate controllers to the user slice:
`mkdir -p /etc/systemd/system/user-.slice.d/` $\rightarrow$ `delegate.conf`:
```ini
[Service]
Delegate=cpu cpuset io memory pids
```

### 3.3 Networking & Lifecycle
- **Network Driver**: Use **Pasta** (Podman 5.0 default) for near-native rootless network performance.
- **Service Activation**: Use `Notify=healthy` with a `HealthCmd` to ensure LLM APIs are fully loaded before systemd marks the service as "active".
- **Persistence**: Run `loginctl enable-linger $USER` to ensure the Omega Engine starts at boot without an active SSH/TTY session.
- **Timeout**: Set `TimeoutStartSec=900` to allow for slow image pulls on first boot.

---

## 4. Sovereign Pattern: The "Hardened Service" Template

Example `.container` unit for an Omega component:

```ini
[Unit]
Description=Omega Sovereign Component
After=network-online.target

[Container]
Image=omega/component:latest
ContainerName=omega-comp
PublishPort=8080:8080
# Sovereign Volume Strategy
Volume=%h/data/omega:/app/data:Z,U
# Resource Steering
Memory=1G
CPUShares=512
# Hardening
ReadOnly=true
NoNewPrivileges=true
DropCapability=ALL
Tmpfs=/tmp:rw,size=128m
# Readiness
HealthCmd=curl -f http://localhost:8080/health
Notify=healthy

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

---

## 5. Validation Proof (Checklist)
- [ ] `podman info --format '{{.Host.CgroupsVersion}}'` $\rightarrow$ `cgroupv2`
- [ ] `loginctl show-user $USER | grep Linger` $\rightarrow$ `Linger=yes`
- [ ] `systemctl --user status <service>` $\rightarrow$ `active (running)`
- [ ] `ls -ln <volume_path>` $\rightarrow$ Verified SubUID mapping (e.g., 100000+)

## 6. Implementation Note
**To the Sovereign Builder**: When migrating legacy `docker-compose.yml` files, do not use `podman-compose` for production. Instead, decompose the compose file into individual Quadlet `.container` and `.pod` files. This allows systemd to handle the dependency graph and resource limits with native precision.

**Related Research**:
- `R13_zen2_hardware_tuning.md` (CPU Pinning)
- `R40_sovereign_lifecycle_persistence.md` (fdstore/memfd)
