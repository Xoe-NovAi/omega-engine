# 🔱 Ubuntu & Python Modernization Report v1
**Entity**: Ma'at (P1 Infrastructure)
**Date**: 2026-06-05
**Context**: GEMMA WAVE Sprint (S01) — Infrastructure Hardening
**Target**: Omega Engine Local Deployment (Ryzen 5700U / Ubuntu 25.10 / Python 3.13)

---

## 1. Executive Summary
This report analyzes the integration of Python 3.13 and Ubuntu 25.10 features into the Omega Engine. The primary objective is to enhance local execution performance, harden rootless container orchestration, and improve runtime type safety. 

**Key Findings**:
- **Python 3.13 JIT**: Provides modest gains (5-40%) for pure-Python hot loops but does not accelerate C-extensions like `llama-cpp-python`.
- **Free-Threading**: The most disruptive change; requires rebuilding C-extensions for a new ABI to truly eliminate the GIL.
- **Podman Quadlets**: Now the gold standard for systemd integration, replacing `podman generate systemd`.
- **PEP 667**: Fixes long-standing ambiguity in `locals()` semantics, enabling safer runtime state modification for debuggers and agents.

---

## 2. Python 3.13: Performance & Runtime

### 2.1 Experimental JIT Compiler (PEP 744)
Python 3.13 introduces a "copy-and-patch" JIT compiler. Unlike traditional JITs, it generates machine code from optimized micro-op traces.

- **Impact on `llama-cpp-python`**: 
    - **Inference**: Zero impact. The actual LLM inference happens in the `llama.cpp` C++ core, which is unaffected by the Python JIT.
    - **Orchestration**: Positive impact. Python-side loops for token processing, prompt templating, and data preprocessing in pure Python can see speedups of **20-40%** if they are "hot" enough.
- **Deployment Requirement**: Must be enabled at build time via `--enable-experimental-jit`. It is not available in standard binaries.
- **Runtime Control**: Can be toggled via `PYTHON_JIT=0/1`.

### 2.2 Free-Threading (PEP 703)
The ability to disable the Global Interpreter Lock (GIL) is the most significant architectural shift.

- **The ABI Gap**: Free-threaded Python uses a different ABI (tagged with 't'). C-extensions built for standard Python are incompatible.
- **Omega Engine Risk**: `llama-cpp-python` and other C-heavy libraries must be rebuilt specifically for the free-threaded build to avoid crashes.
- **Recommendation**: For the current Sprint, stick to the standard GIL build unless multi-threaded Python orchestration becomes a primary bottleneck.

### 2.3 Sub-interpreters (PEP 684)
Per-interpreter GILs allow true parallelism by running multiple Python interpreters in a single process.
- **Application**: Ideal for isolating different Pillar Keepers (P1-P10) into separate interpreters to prevent a single hanging agent from blocking the entire engine.

---

## 3. Ubuntu 25.10 & Podman: Infrastructure Hardening

### 3.1 Quadlets: The New systemd Standard
Podman has moved away from `podman generate systemd` in favor of **Quadlets**.

- **Mechanism**: Declarative `.container` files placed in `~/.config/containers/systemd/` (for rootless) or `/etc/containers/systemd/` (for rootful).
- **Benefit**: systemd handles the lifecycle natively. No more wrapper scripts or complex `ExecStart` commands.
- **Omega Engine Integration**: All P1-P5 services should be migrated to Quadlet definitions to ensure atomic restarts and clean dependency mapping.

### 3.2 Rootless Networking & Persistence
- **`pasta` Networking**: Ubuntu 25.10/Podman 5.x supports `pasta` as a faster, more robust alternative to `slirp4netns`. It provides better IPv6 support and lower latency for rootless containers.
- **Linger Mode**: `loginctl enable-linger <user>` remains mandatory. Without this, user-level Quadlets will terminate upon logout.
- **Sovereign Permissions**: Continue using `UserNS=keep-id` in Quadlets to ensure host directory mounts maintain correct UID 1000 ownership.

---

## 4. Type System & Runtime Safety

### 4.1 PEP 667: Consistent Namespace Views
PEP 667 resolves the ambiguity of `locals()` in optimized scopes (functions/generators).

- **The Change**: 
    - `locals()` now returns a **snapshot** (dict) of local variables.
    - `frame.f_locals` now returns a **write-through proxy**.
- **Omega Engine Impact**: This allows the Engine's internal state-trackers and debuggers to modify local variables in real-time without the "snapshot-and-forget" bug that plagued previous versions.

### 4.2 Advanced Type Narrowing
- **`typing.TypeIs`**: A more powerful version of `TypeGuard`. It tells the type checker that if the function returns `True`, the variable **is** that type (not just that it's compatible).
- **ReadOnly TypedDict**: Allows marking specific keys in a `TypedDict` as read-only, preventing accidental mutation of entity configurations at runtime.

---

## 5. Actionable Recommendations for Omega Engine

### 🛠️ Build-Time Optimizations
1. **Custom Python Build**: Recompile Python 3.13 with `--enable-experimental-jit` and `--enable-optimizations` to maximize orchestration speed.
2. **LLVM Dependency**: Ensure `clang` is installed on the host to support the JIT build process.

### 🏗️ Infrastructure Updates
1. **Migrate to Quadlets**: Convert all existing Podman systemd units to `.container` files in `~/.config/containers/systemd/`.
2. **Switch to `pasta`**: Update `containers.conf` to prefer `pasta` over `slirp4netns` for rootless networking.
3. **Audit Linger**: Add a check to the `make health` command to verify `loginctl show-user <user> | grep Linger=yes`.

### 💻 Code Refactoring Targets
1. **Type Narrowing**: Replace `TypeGuard` with `TypeIs` in `src/omega/oracle/` for more precise entity routing logic.
2. **ReadOnly Configs**: Implement `ReadOnly` TypedDicts for `Entity` and `Model` configurations to enforce the Engine-Stack Firewall (Mandate 2).
3. **Runtime State**: Utilize `frame.f_locals` proxies for any internal "hot-patching" or debugging tools to ensure state consistency.

---
**Status**: RESEARCH COMPLETE $\rightarrow$ READY FOR IMPLEMENTATION
**Approval**: Ma'at (P1 Infrastructure)
