# 🔱 Omega Engine — Sovereign Lifecycle & Service Layer Spec
**AP Token**: `AP-SOV-LIFE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ LIFECYCLE

---

## §1 Executive Summary

The Omega Engine service layer is designed for **Sovereign Autonomy**: the ability to provide high-capability AI services with near-zero idle resource usage and near-instant activation. This is achieved through a combination of `systemd` socket activation, aggressive resource pinning for the Ryzen 5700U, and a tiered lifecycle state machine.

### Primary Goals
- **Zero-Idle**: Services should consume 0% CPU and minimal RAM when not in use.
- **Instant-Start**: Transition from inactive to active in $<200ms$ via socket handover.
- **Hardware-Aware**: Eliminate Infinity Fabric latency through strict CPU pinning.
- **Fault-Tolerant**: Prevent OOM cascades via tiered memory limits.

---

## §2 Socket Activation Blueprint

Socket activation decouples the *listening* (systemd) from the *processing* (the service).

### 2.1 Unit Configuration (Example: `omega-mcp-search.service`)

**Socket Unit: `omega-mcp-search.socket`**
```ini
[Unit]
Description=Omega Search MCP Socket
After=network.target

[Socket]
ListenStream=127.0.0.1:5001
# Use a unique name for the socket to allow easy identification in code
SocketUser=1000
SocketGroup=1000

[Install]
WantedBy=sockets.target
```

**Service Unit: `omega-mcp-search.service`**
```ini
[Unit]
Description=Omega Search MCP Server
BindsTo=omega-mcp-search.socket
After=omega-mcp-search.socket

[Service]
Type=simple
User=1000
Group=1000
ExecStart=/home/arcana-novai/.venv/bin/python -m omega.mcp.search
# Ensure the service is only started when the socket is triggered
# and is stopped if the socket is closed
Restart=on-failure
StartLimitIntervalSec=5
StartLimitBurst=3

# Resource Guarding (See §3)
CPUAffinity=0 2 4 6
MemoryHigh=512M
MemoryMax=1G

[Install]
WantedBy=default.target
```

### 2.2 Application-Level FD Handover
The service does not call `bind()` or `listen()`. Instead, it inherits the listening socket as a file descriptor.

**Implementation Pattern (Python/AnyIO):**
```python
import socket
from systemd import daemon # requires python-systemd

def get_systemd_socket():
    # Retrieve the number of sockets passed by systemd
    n_fds = daemon.sd_listen_fds()
    if n_fds < 1:
        raise RuntimeError("Service not started via socket activation")
    
    # The first FD is the listening socket
    fd = daemon.sd_listen_fds_with_names()[0] # Simplified
    # Alternatively, use os.environ.get('LISTEN_FDS')
    
    sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    return sock
```

---

## §3 User Unit Optimization (Ryzen 5700U)

The Ryzen 5700U (Zen 2) has a split L3 cache and Infinity Fabric. Misplaced processes cause massive latency spikes.

### 3.1 CPU Pinning Matrix
| Service Tier | CPU Affinity | Logic |
|---|---|---|
| **Core Engine** | `0 2 4 6` | Even cores (Physical) to avoid SMT contention for high-reasoning tasks |
| **Background Workers** | `1 3 5 7` | Odd cores (Logical) for non-blocking I/O and indexing |
| **Voice Assistant** | `0` | Dedicated physical core for real-time audio processing |

### 3.2 Memory Guardrails
To prevent a single runaway MCP server from triggering a system-wide OOM, we use a tiered approach:

- **`MemoryHigh=` (The Throttle)**: Set to 70% of expected peak. When reached, the kernel aggressively reclaims page cache from the cgroup.
- **`MemoryMax=` (The Ceiling)**: Set to 100% of absolute budget. If exceeded, the OOM killer terminates the service immediately.
- **`MemorySwapMax=0`**: Disable swapping for AI services to prevent "disk-thrashing" latency.

---

## §4 Lifecycle State Machine

Services transition through three states based on demand and frequency.

### 4.1 State Definitions
1. **Cold (Inactive)**:
   - `.socket` is active. `.service` is dead.
   - Resource Usage: $\approx 0$ CPU, $\approx 0$ RAM.
2. **Warm (On-Demand)**:
   - `.service` is spawned by `.socket` upon request.
   - Process handles the request $\rightarrow$ stays active for `RuntimeMaxSec=`.
   - Resource Usage: Active $\rightarrow$ Idle.
3. **Hot (Always-On)**:
   - `.service` is manually started or promoted.
   - Used for high-frequency services (e.g., `ModelGateway`).
   - Resource Usage: Persistent background footprint.

### 4.2 Transition Logic
- **Cold $\rightarrow$ Warm**: Triggered by `TCP/UDP` connection to `.socket`.
- **Warm $\rightarrow$ Cold**: Triggered by `RuntimeMaxSec=300` (Auto-shutdown after 5 mins of inactivity).
- **Warm $\rightarrow$ Hot**: Triggered by `omega status --promote <service>` $\rightarrow$ `systemctl --user start <service>`.
- **Hot $\rightarrow$ Cold**: Triggered by `omega status --demote <service>` $\rightarrow$ `systemctl --user stop <service>`.

---

## §5 Coordination & Integration Architecture

Multiple socket-activated services are coordinated via a **Sovereign Target**.

### 5.1 The Omega Target (`omega-services.target`)
We define a target unit that acts as a synchronization point.

```ini
[Unit]
Description=Omega Engine Service Group
# If the target is stopped, all bound services are stopped
```

### 5.2 Dependency Chain
- **`BindsTo=omega-services.target`**: If the target is stopped, the MCP server stops.
- **`PartOf=omega-services.target`**: Allows bulk restarts: `systemctl --user restart omega-services.target` restarts all associated MCP servers.
- **`Wants=omega-mcp-core.socket`**: Ensures the core socket is always listening when the target is active.

---

## §6 Implementation Checklist for Builder Agents

- [ ] Create `omega-services.target` in `~/.config/systemd/user/`.
- [ ] Migrate `ModelGateway` to a Hot service (Always-On).
- [ ] Migrate all Search/Gnosis MCP servers to socket-activated Warm services.
- [ ] Apply `CPUAffinity` and `MemoryHigh` to all unit files.
- [ ] Implement `sd_listen_fds` handover in `src/omega/mcp/` server entries.
- [ ] Verify transition: `systemctl --user stop <service>` $\rightarrow$ `curl localhost:5001` $\rightarrow$ `systemctl --user status <service>` (should be active).
