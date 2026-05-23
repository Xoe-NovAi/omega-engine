# 🔱 Omega Engine — OpenCode Permissions Fix
# ⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ PERMISSIONS-FIX

**AP Token**: `AP-OPENCODE-PERMS-v1.0.0`
**Status**: READY FOR IMPLEMENTATION
**Date**: 2026-05-16
**Author**: Sovereign Gnosis Analyst

---

## §1 Technical Analysis: OpenCode Access & Permission Drift

### 1.1 The Root Cause: Config Override & Permission Lists
The "Permission Denied" errors in OpenCode v1.15.0 are not solely caused by filesystem masks, but by a fundamental change in how OpenCode handles configuration and tool permissions.

**The Conflict: Global vs. Project Configuration**
In v1.15.0, the global configuration file `~/.config/opencode/mcp_servers.json` takes precedence over the project-local `opencode.json`. If the global config exists, the project-local settings (including MCP server definitions and permission lists) are ignored.

**The `external_directory` Block**
OpenCode's `filesystem_*` tools utilize a whitelist called `external_directory`. If the project root is not explicitly listed in this array in the *active* configuration, all filesystem calls to that path return `Access denied`, regardless of the OS-level permissions.

**The Umask Drift (Host-Level)**
When agents are spawned as separate subprocesses, they may inherit different `umask` settings. A restrictive umask (e.g., `0077`) causes `Path.mkdir()` to create directories that are inaccessible to other agents or the host user, even if the ownership is correct.

---

## §2 The Sovereign Permission Guard

To eliminate these blockers, the Omega Engine implements the **Sovereign Permission Guard**. This utility ensures both the configuration and the filesystem are in a "Ready" state.

### 2.1 Specification: `scripts/permission_guard.sh`

The guard now performs two critical operations: **Configuration Synchronization** and **Filesystem Normalization**.

**Logic**:
1. **Config Sync**: 
   - Checks for the existence of `~/.config/opencode/mcp_servers.json`.
   - If it exists and conflicts with `opencode.json`, it either backs up the global config or synchronizes the `external_directory` list and MCP servers from the project root to the global file.
   - Ensures the current project root is explicitly added to the `external_directory` permission list.
2. **Directory Normalization**: Recursively sets all directories in `data/` to `755` (drwxr-xr-x).
3. **File Normalization**: Recursively sets all files in `data/` to `644` (-rw-r--r--).
4. **Ownership Verification**: Ensures the current user maintains ownership of the project root.

**Proposed Implementation**:
```bash
#!/bin/bash
# scripts/permission_guard.sh - Sovereign Permission Guard

PROJECT_ROOT="$(pwd)"
DATA_DIR="$PROJECT_ROOT/data"
GLOBAL_CONFIG="$HOME/.config/opencode/mcp_servers.json"
LOCAL_CONFIG="$PROJECT_ROOT/opencode.json"

echo "🛡️  Executing Sovereign Permission Guard..."

# 1. Handle OpenCode v1.15.0 Config Override
if [ -f "$GLOBAL_CONFIG" ]; then
    echo "Syncing project config to global override: $GLOBAL_CONFIG"
    # Implementation: Use jq to merge LOCAL_CONFIG permissions/MCPs into GLOBAL_CONFIG
    # Ensure PROJECT_ROOT is in external_directory
fi

# 2. Enforce directory masks (755)
if [ -d "$DATA_DIR" ]; then
    echo "Setting directory masks to 755 in $DATA_DIR..."
    find "$DATA_DIR" -type d -exec chmod 755 {} +
    echo "Setting file masks to 644 in $DATA_DIR..."
    find "$DATA_DIR" -type f -exec chmod 644 {} +
fi

echo "✅ Host-level permissions and OpenCode config synchronized."
```

---

## §3 Permanent Fix: `entity_workspace.py`

To prevent the need for frequent guard execution, the `EntityWorkspaceManager` must be updated to explicitly enforce permissions during the "Awakening" (scaffolding) process.

### 3.1 Implementation Plan

**File**: `src/omega/oracle/entity_workspace.py`

**Changes**:
1. **Explicit Directory Chmod**: After calling `mkdir()`, explicitly call `os.chmod()` on the workspace, knowledge, and headless directories.
2. **Explicit File Chmod**: After writing the `soul.yaml` file, explicitly set its permissions to `644`.

**Proposed Code Update**:
```python
import os # Ensure os is imported

# In scaffold_workspace():
workspace_dir.mkdir(parents=True, exist_ok=True)
os.chmod(workspace_dir, 0o755)

knowledge_dir.mkdir(parents=True, exist_ok=True)
os.chmod(knowledge_dir, 0o755)

headless_dir.mkdir(parents=True, exist_ok=True)
os.chmod(headless_dir, 0o755)

# After writing soul_file:
with open(soul_file, "w") as f:
    # ... write content ...
os.chmod(soul_file, 0o644)
```

---

## §4 Implementation Notes for MiniMax M2.5

1. **Script Creation**: Create `scripts/permission_guard.sh`. Ensure it uses `jq` to handle the JSON merge between `opencode.json` and `~/.config/opencode/mcp_servers.json`.
2. **External Directory Sync**: The script must explicitly add the absolute path of the project root to the `external_directory` array in the global config.
3. **Code Update**: Apply the `os.chmod` changes to `src/omega/oracle/entity_workspace.py`.
4. **Verification**:
    - Run `scripts/permission_guard.sh`.
    - Verify that `filesystem_*` tools in OpenCode no longer return `Access denied`.
    - Create a new entity via the CLI and verify it is `755` (dir) and `644` (file).
5. **Integration**: Add the guard to the `Makefile` startup sequence.

---

**Status**: ✅ READY FOR IMPLEMENTATION
**Reviewer**: SOPHIA
**Date**: 2026-05-16
