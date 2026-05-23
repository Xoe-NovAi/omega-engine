# 🔱 Omega Engine — Background Agent Architecture
**AP Token**: `AP-AGENT-LIFECYCLE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ AGENT-ARCH

## 1. Overview
The Omega Engine utilizes headless CLI agents (Cline, OpenCode) to perform complex, multi-step tasks. Currently, these are dispatched as transient subprocesses. To support long-running tasks, asynchronous monitoring, and state recovery, a formal Agent Lifecycle State Machine is required.

## 2. Agent Lifecycle State Machine
An agent's state is tracked from dispatch to termination.

### State Definitions
| State | Description | Transition Trigger |
|--------|-------------|-------------------|
| **IDLE** | Agent is configured and ready for dispatch. | `dispatch_agent()` $\rightarrow$ **RUNNING** |
| **RUNNING** | Subprocess is active and executing the task. | Process Exit $\rightarrow$ **COMPLETED** / **FAILED** |
| **SUSPENDED** | Task is paused; state is persisted to the entity workspace. | `resume_agent()` $\rightarrow$ **RUNNING** |
| **COMPLETED** | Task finished successfully (Exit Code 0). | `cleanup()` $\rightarrow$ **IDLE** |
| **FAILED** | Process crashed or returned non-zero exit code. | `retry()` $\rightarrow$ **RUNNING** / `cleanup()` $\rightarrow$ **IDLE** |
| **TIMED_OUT** | `anyio.fail_after` threshold reached. | `retry()` $\rightarrow$ **RUNNING** / `cleanup()` $\rightarrow$ **IDLE** |

### State Transition Diagram
`IDLE` $\xrightarrow{dispatch}$ `RUNNING` $\xrightarrow{exit 0}$ `COMPLETED` $\xrightarrow{cleanup}$ `IDLE`
`RUNNING` $\xrightarrow{exit \neq 0}$ `FAILED` $\xrightarrow{retry}$ `RUNNING`
`RUNNING` $\xrightarrow{timeout}$ `TIMED_OUT` $\xrightarrow{retry}$ `RUNNING`

## 3. Execution Architecture
The `Orchestrator` manages these states using the following mechanism:

### Dispatch Logic
1. **Resource Acquisition**: Wait for `ResourceGuard.lock()` to prevent OOM.
2. **Soul Injection**: Fetch `soul.yaml` $\rightarrow$ Format as system prompt.
3. **Subprocess Spawning**: Use `anyio.run_process` with `capture_output=True`.
4. **Monitoring**: Wrap execution in `anyio.fail_after(timeout)`.

### Recovery Strategies
| Failure Type | Strategy | Action |
|--------------|----------|--------|
| **Transient Error** | Exponential Backoff | Retry up to 3 times with increasing delay. |
| **Resource Exhaustion** | Priority Preemption | Kill lower-priority agents to free RAM for P0 tasks. |
| **Timeout** | State Checkpoint | If the agent supports it, read the last Hivemind MCP post to resume from the last known state. |
| **Critical Crash** | Entity Reset | Clear the agent's temporary workspace and restart from the original prompt. |

## 4. Persistence & Memory
To prevent loss of progress, agents are mandated to use the **Hivemind MCP** for state persistence.

- **Heartbeat**: Agents should post a "Progress Update" to Hivemind every 5 minutes.
- **Context Handoff**: On `COMPLETED`, the agent must post a final summary of changes and lessons learned to the entity's `soul.yaml` via the `EntityWorkspaceManager`.

---
**Implementation Note for @Cline / @Antigravity**:
Implement an `AgentSession` class in `orchestrator.py` to track these states. Replace the simple `dispatch_agent` return dict with an `AgentSession` object that can be queried for status.
