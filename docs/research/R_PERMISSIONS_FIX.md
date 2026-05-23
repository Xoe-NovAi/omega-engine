# 🔱 Omega Engine — Sovereign Permission Fix
# ⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ PERMISSIONS-FIX

## Executive Summary
The Omega Engine employs a hybrid architecture where headless agents (running as the host user) and Podman containers (running as mapped users) both interact with the same `data/` directories. In rootless Podman, this creates a "UID Mismatch" problem: files created by the host user are often inaccessible to the container user, and vice versa, unless specific user namespace mappings and volume flags are used.

This document specifies the **Sovereign Permission Guard** and the **Scaffolding Fix** to ensure seamless read/write access across the host-container boundary.

---

## 1. Technical Analysis: The Rootless Podman Gap

### 1.1 User Namespace Mapping
In rootless Podman, the host user (e.g., UID 1000) is mapped to UID 0 (root) inside the container. However, if the container runs as a non-root user (e.g., UID 1000 inside), that ID is mapped to a **subordinate UID** on the host (defined in `/etc/subuid`).

**The Conflict**:
- **Host Agent** $\rightarrow$ creates `data/entities/sophia/` as UID 1000.
- **Container Agent** $\rightarrow$ attempts to write to `data/entities/sophia/` as UID 1000 (internal), which is UID 100999 (host).
- **Result**: `Permission Denied`.

### 1.2 The Solution Matrix

| Tool/Flag | Effect | Recommendation |
|---|---|---|
| `--userns=keep-id` | Maps host UID 1000 $\rightarrow$ container UID 1000. | **Mandatory** for all containers writing to `data/`. |
| `:U` flag | Recursively changes host volume ownership to match container user. | **Mandatory** for all volume mounts. |
| `:Z` flag | Relabels SELinux context for private container volume. | **Mandatory** on Fedora/RHEL/CentOS. |
| `podman unshare` | Executes command in the container's user namespace on the host. | Used for manual permission fixes. |

---

## 2. The Sovereign Permission Guard

To prevent "permission drift" and ensure a clean state, the Omega Engine implements a **Sovereign Permission Guard**. This is a maintenance utility that enforces the correct ownership and masks for the project root.

### 2.1 Specification: `scripts/permission_guard.sh`

**Logic**:
1.  **Ownership Reset**: Ensure the current host user owns the entire project root.
2.  **Directory Mask**: Set all directories in `data/` to `755` (drwxr-xr-x).
3.  **File Mask**: Set all files in `data/` to `644` (-rw-r--r--).
4.  **Podman Alignment**: If `podman` is present, use `podman unshare` to ensure the subordinate UID range is accessible.

**Proposed Bash Implementation**:
```bash
#!/bin/bash
# scripts/permission_guard.sh - Sovereign Permission Guard

PROJECT_ROOT=$(pwd)
DATA_DIR="$PROJECT_ROOT/data"

echo "🛡️  Executing Sovereign Permission Guard..."

# 1. Reset ownership to current user
echo "Updating ownership to $(id -un)..."
chown -R $(id -u):$(id -g) "$PROJECT_ROOT"

# 2. Enforce directory masks (755)
echo "Setting directory masks (755)..."
find "$DATA_DIR" -type d -exec chmod 755 {} +

# 3. Enforce file masks (644)
echo "Setting file masks (644)..."
find "$DATA_DIR" -type f -exec chmod 644 {} +

# 4. Podman User Namespace Alignment
if command -v podman &> /dev/null; then
    echo "Aligning Podman user namespaces..."
    # Ensure the container-mapped root can access the data
    podman unshare chown -R 0:0 "$DATA_DIR" 2>/dev/null || true
fi

echo "✅ Permissions synchronized."
```

---

## 3. Scaffolding Fix: `entity_workspace.py`

The current `scaffold_workspace` method uses default `mkdir` behavior. To ensure consistency, we must explicitly set the mode and handle the creation process to be "Podman-friendly".

### 3.1 Implementation Plan

**File**: `src/omega/oracle/entity_workspace.py`

**Changes**:
1.  **Explicit Mode**: Use `mode=0o755` in `mkdir`.
2.  **Atomic File Creation**: Use `os.chmod` after creating the `soul.yaml` to ensure `644`.

**Proposed Code Update**:
```python
# In scaffold_workspace:
workspace_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
knowledge_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
headless_dir.mkdir(parents=True, exist_ok=True, mode=0o755)

# After writing soul_file:
soul_file.chmod(0o644)
```

---

## 4. Permanent Runtime Requirements

To eliminate permission issues permanently, all Omega Engine deployment manifests (Dockerfiles, Podman Compose, systemd units) MUST adhere to the following:

1.  **Volume Mounts**: Use the `:U` and `:Z` flags.
    - Example: `-v /home/user/omega-engine/data:/data:U,Z`
2.  **User Namespace**: Use the `--userns=keep-id` flag.
    - Example: `podman run --userns=keep-id ...`
3.  **Startup Hook**: Run `scripts/permission_guard.sh` as part of the `make start-infra` or `make start-iris` sequence.

---

## Implementation Note for MiniMax M2.5
- Create `scripts/permission_guard.sh` and make it executable.
- Update `src/omega/oracle/entity_workspace.py` with the explicit `mode` and `chmod` calls.
- Update `Makefile` to include `permission_guard` in the startup sequence.
- Verify by creating a new entity via CLI and checking if the `iris` container can write to its workspace.

---
**Status**: ✅ READY FOR IMPLEMENTATION
**Reviewer**: SOPHIA
**Date**: 2026-05-16
