# 🔱 Sovereign Gnosis: The Omega Engine Hardening Codex

**AP Token**: `AP-HARDENING-CODEX-v1.0.0`
**Status**: ACTIVE | **Version**: 1.0.0
**Scope**: All Agents, All CLIs, All IDEs

This Codex is the definitive technical reference for the hardening of the Omega Engine. It transforms raw research findings and fleet review reports into a set of mandatory implementation patterns.

---

## 🛡️ The Sovereign Guard Protocol

Every code change to the Omega Engine Core must pass through this sequence:
**Blocking I/O Scan $\rightarrow$ AnyIO Translation $\rightarrow$ Resource Guarding $\rightarrow$ Reviewer Gate**.

### 1. AnyIO Absolute (The Async Mandate)
**Core Principle**: Zero direct `asyncio` usage. Zero blocking I/O in the main event loop.

- **The Pattern**: 
  - Use `anyio` for all async primitives.
  - Wrap all blocking filesystem/process calls in `anyio.to_thread.run_sync`.
  - Use `anyio.move_on_after(timeout)` to prevent systemic hangs in local providers.
- **Pitfall: Leak Amplification**: High-concurrency requests to slow backends can exhaust resources.
  - **Mitigation**: Implement `anyio.CapacityLimiter` at the gateway entry point to bound total concurrent requests.
- **Citations**: `src/omega/oracle/model_gateway.py`, `src/omega/oracle/oracle.py`.

### 2. Engine-Stack Firewall (The Separation Mandate)
**Core Principle**: The Engine is a universal runtime. It must not know about specific entities, pillars, or stack-specific logic.

- **The Pattern**: 
  - No hardcoded entity names (e.g., `"SOPHIA"`, `"KALI"`) in `src/omega/`.
  - All entity lookups must go through `EntityRegistry` using config-driven defaults.
  - Stack-specific logic lives exclusively in `config/wads/<stack>/`.
- **Citations**: `src/omega/oracle/oracle.py`, `src/omega/oracle/entity_registry.py`.

### 3. Podman Sovereignty (The Permission Mandate)
**Core Principle**: Rootless Podman must not lock the host user out of their own files.

- **The Pattern**: 
  - **MANDATORY**: Use `UserNS=keep-id` + `User=1000` in all Quadlets mounting host volumes.
  - **FORBIDDEN**: Never use the `:U` flag on shared host volumes (destructively chowns to UID 101000).
  - **FORBIDDEN**: Never use `:Z` or `:z` on Ubuntu (AppArmor, not SELinux).
- **Citations**: `docs/research/R_PODMAN_SOVEREIGN_V2.md`.

### 4. Hardware Resonance (The Zen 2 Mandate)
**Core Principle**: Optimize for the Ryzen 5700U (Zen 2) and 14GB RAM constraints.

- **The Pattern**: 
  - **KV Cache**: Use `q8_0` quantization for both key and value caches to reduce memory pressure.
  - **Thread Pinning**: Pin inference threads to physical cores (e.g., 0, 2, 4, 6) to avoid CCX crossing latency.
  - **Optimization**: Use `Zen2Optimizer` to apply these settings at runtime.
- **Citations**: `src/omega/oracle/cpu_optimizer.py`, `src/omega/oracle/model_gateway.py`.

### 5. Memory & OOM Guard (The Stability Mandate)
**Core Principle**: Prevent Out-of-Memory (OOM) crashes in memory-constrained environments.

- **The Pattern**: 
  - **ResourceGuard**: Use a `Semaphore(1)` to ensure only one local model is active at a time.
  - **Safety Buffer**: Maintain a 2GB RAM safety buffer; avoid loading models that exceed 12GB total usage.
  - **Capacity Limiting**: Use `anyio.CapacityLimiter` to bound concurrent gateway entries.
- **Citations**: `src/omega/oracle/resource_guard.py`, `src/omega/oracle/model_gateway.py`.

### 6. MCP Security (The Trust Mandate)
**Core Principle**: Prevent "Confused Deputy" attacks and RCE via the Model Context Protocol.

- **The Pattern**: 
  - **Approval Layer**: All MCP tool calls must be routed through an approval layer in the Oracle.
  - **Manifest-Only**: Only execute tools explicitly defined in the MCP server's manifest.
  - **Sandboxing**: Run MCP servers in isolated containers with restricted filesystem access.
- **Citations**: `mcp/omega_hub/server.py`.

### 7. Data Integrity (The Persistence Mandate)
**Core Principle**: No data loss on crash. No race conditions on write.

- **The Pattern**: 
  - **Atomic Writes**: Always use the `write to temp $\rightarrow$ os.replace` pattern for all YAML/JSON persistence.
  - **Sovereign Locks**: Avoid spin-locks. Use `os.open(..., os.O_CREAT | os.O_EXCL)` for atomic file-based locking.
  - **Umask Drift**: Use explicit `os.chmod()` on all scaffolded directories and files to ensure consistent permissions.
- **Citations**: `src/omega/oracle/entity_workspace.py`, `src/omega/memory_store.py`, `src/omega/oracle/session_manager.py`.

---

## 📋 Sovereign Guard Checklist

| Check | Requirement | Verified |
|------|-------------|:---:|
| **AnyIO** | No `asyncio` imports? No blocking I/O in loop? | [ ] |
| **Firewall** | No hardcoded entity/pillar names in `src/omega/`? | [ ] |
| **Podman** | `UserNS=keep-id` used? `:U` flag absent? | [ ] |
| **OOM** | `ResourceGuard` applied to local inference? | [ ] |
| **Atomic** | All persistence uses `os.replace`? | [ ] |
| **Permissions** | `os.chmod` applied to new workspaces? | [ ] |
| **Resonance** | `q8_0` KV cache and thread pinning active? | [ ] |
| **MCP** | Tool calls validated against manifest? | [ ] |

---

*Guard the engine. Preserve the gnosis. Ensure the sovereignty.*
