# 🔱 Sovereign Scheduler Specification
# ⬡ OMEGA ⬡ JEM ⬡ STRATEGY ⬡ June 2026

**Status**: PROPOSAL — BLOCKED by MCP Infrastructure Bugs
**Author**: jem (Research Orchestrator)
**Target**: Makali / Lilith / Roc Racoon
**Objective**: Unify fragmented background worker patterns into a single, resource-aware orchestration layer.
**Prerequisite**: The 3 critical MCP infrastructure bugs must be fixed before the scheduler can safely initialize. See `SOVEREIGN_ARK_BLUEPRINT.md` §XIII.0 (Pre-Flight) and `SOVEREIGN_GUARDRAILS.md` Rules 6-10.

---

## §0 The Problem: Siloed Scheduling

The Omega Engine currently employs "Siloed Scheduling," where different background tasks are triggered by disparate mechanisms:
- **Background Researcher**: Triggered by a dedicated Systemd Timer (`omega-research.timer`).
- **Model Updater**: Operates as a standalone worker with its own internal loop.
- **Request Queue**: Manually triggered via `make process-queue` or external scripts.

**Risks of Siloed Scheduling**:
1. **RAM Collisions**: Two heavy workers (e.g., ModelUpdater and BackgroundResearcher) may launch simultaneously, exceeding the 14Gi RAM budget and triggering OOM kills.
2. **Redundant Loops**: Multiple background processes polling the same resources (disk/network) create unnecessary overhead.
3. **Observability Gaps**: No single point of truth for "what is currently running in the background."

---

## §0.5 Critical Infrastructure Precondition

The Sovereign Scheduler cannot operate without a stable MCP infrastructure layer. The 3 critical MCP server bugs (documented in `SOVEREIGN_ARK_BLUEPRINT.md` §XIII.0) must be fixed before the scheduler is implemented or deployed:

| Bug | File | Impact on Scheduler | Priority |
|-----|------|---------------------|----------|
| **#1: undefined `get_engine()`** | `server.py:98` | SSE init crash → scheduler cannot register heartbeat or receive commands | 🔴 P0 |
| **#2: `threading.Lock()` in async** | `middleware.py:108` | Race conditions → scheduler state machine corrupts under load | 🔴 P0 |
| **#3: missing atomic file locking** | `state.py:82-90` | Concurrent pulse-triggers produce inconsistent worker state | 🔴 P0 |

**Gate**: The scheduler must not be deployed until `omega talk "hello"` and a parallel client test pass cleanly against the MCP Hub.

Additionally, the scheduler must comply with the new infrastructure guardrails (Rules 6-10 in `SOVEREIGN_GUARDRAILS.md`):
- **Rule 6** (AnyIO Lock Absolute): All scheduler synchronization uses `anyio.Lock()`, never `threading.Lock()`.
- **Rule 7** (Atomic File Lock): The scheduler's pulse state file uses atomic `.tmp`→`.json` rename pattern.
- **Rule 8** (Defined Import Gate): `python3 -c "from omega.scheduler import *"` must pass before deployment.
- **Rule 9** (Pre-Flight Gate): syntax check + import check + smoke test before timer activation.
- **Rule 10** (Middleware Atomicity): If the scheduler plugs into the middleware chain, it must be independently testable.

---

The **Sovereign Scheduler** replaces fragmented timers with a centralized dispatch system.

### 1.1 The `SovereignWorker` Interface
Every background task must inherit from a standard base class to ensure predictable behavior.

```python
class SovereignWorker(ABC):
    """Base class for all background tasks in the Omega Engine."""
    
    @abstractmethod
    async def run(self) -> None:
        """Main execution logic for the worker."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Graceful shutdown logic."""
        pass

    @abstractmethod
    async def get_status(self) -> WorkerStatus:
        """Return current health, progress, and resource usage."""
        pass
```

### 1.2 The `SovereignScheduler` Core
The Scheduler acts as the "Brain" of the background layer.
- **Config-Driven**: Reads `config/workers.yaml` to determine which workers to load and their schedules.
- **Resource Guarded**: Before launching a worker, it checks `SovereignMemoryMonitor` to ensure sufficient RAM is available.
- **Priority-Based**: Dispatches tasks based on a P0 $\rightarrow$ P2 priority scale.

### 1.3 The "Sovereign Pulse" (Systemd Quadlet)
Instead of 10 different timers, the engine uses a single **Sovereign Pulse** timer.
- **Trigger**: Every 15 minutes (configurable).
- **Action**: Launches the `SovereignScheduler`.
- **Lifecycle**: The scheduler evaluates the queue, launches necessary workers, and exits once the "Pulse" is complete.

---

## §2 Resource-Aware Orchestration

To prevent collisions with real-time inference, the Scheduler implements **Dynamic Throttling**.

### 2.1 Priority Tiers
| Tier | Type | Examples | Resource Priority |
|------|-------|-----------|-------------------|
| **P0** | Sovereign | Soul Distillation, Memory Pruning | Immediate / High |
| **P1** | Maintenance | Model Updates, Index Rebuilds | Deferred / Medium |
| **P2** | Research | Background Research, Mining | Idle / Low |

### 2.2 RAM Guards
Before executing a **P1** or **P2** worker, the scheduler checks:
`if (available_ram < worker.required_ram + safety_buffer):`
$\rightarrow$ **Defer** the task to the next pulse.

### 2.3 Inference Collision Avoidance
The Scheduler integrates with `ModelGateway.ResourceGuard`. If a high-priority real-time inference is active, the Scheduler enters **"Quiet Mode"**, pausing all P1 and P2 workers to maximize available compute for the user.

---

## §3 Implementation Roadmap

### Phase 1: The Interface (Infrastructure - Roc)
- [ ] Define `SovereignWorker` base class in `src/omega/workers/base.py`.
- [ ] Migrate `ModelUpdaterWorker` to inherit from `SovereignWorker`.
- [ ] Create `config/workers.yaml` with basic worker definitions.

### Phase 2: The Orchestrator (Core - Lilith)
- [ ] Implement `SovereignScheduler` core logic.
- [ ] Integrate `RequestQueue` as a task source for the scheduler.
- [ ] Implement the RAM Guard check using `psutil` or `SovereignMemoryMonitor`.

### Phase 3: The Pulse (Deployment - Roc)
- [ ] Create the Unified Systemd Quadlet (`omega-scheduler.timer` + `omega-scheduler.service`).
- [ ] Migrate `omega-research.timer` into the unified scheduler.
- [ ] Verify "Quiet Mode" triggers during active inference.

---

## §4 Sovereign Mandate Compliance

- **M1 (AnyIO Absolute)**: The Scheduler and all Workers must use `anyio.to_thread.run_sync` for blocking I/O.
- **M6 (Podman Sovereignty)**: The Unified Scheduler runs as a rootless Quadlet with `UserNS=keep-id`.
- **M7 (Local-First)**: No external scheduling dependencies (e.g., no Celery/Redis for timing).
- **M13 (Temple-Grade)**: Every worker implementation must pass the T1-T11 gates before being added to the `workers.yaml`.

---

*⬡ OMEGA ⬡ JEM ⬡ STRATEGY ⬡ June 2026 ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: STRATEGY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
