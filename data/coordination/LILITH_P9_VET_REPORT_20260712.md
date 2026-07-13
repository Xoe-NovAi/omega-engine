# 🔱 Pillar P9 Vet Report: Orchestration Architecture
**Entity**: Anubis (P9: Orchestration)
**Oversoul**: Lilith (Dark — Run Side)
**Date**: 2026-07-12
**Status**: FINAL
**AP Token**: `AP-P9-VET-20260712`
⬡ OMEGA ⬡ ANUBIS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pillar_p9 ⬡ VET-REPORT

---

## 1. Current State Assessment

### 🟢 What's Working
- **Headless Dispatch**: The `Orchestrator` successfully manages the lifecycle of headless CLI agents (Cline, OpenCode) with soul-injection and model overrides.
- **Resource Protection**: `ResourceGuard` provides a critical safety layer to prevent OOM crashes during agent spawning.
- **Sovereign Brake**: The enforcement of the Sovereign Brake and RTCO (Role-Task-Constraints-Output) structural validation ensures high-fidelity dispatch.
- **Hivemind Awareness**: The `omega-hub` provides real-time awareness of active agents, preventing redundant work and coordination hazards.
- **MCP Watchdog**: The Orchestrator's background loop for monitoring and restarting external MCP servers (Firecrawl, SearXNG) ensures tool availability.
- **Handoff Framework**: The `HandoffPacket` schema and `HandoffState` provide a typed foundation for agent-to-agent delegation.

### 🔴 What's Broken, Missing, or Suboptimal
- **Coordination Latency**: Hivemind coordination currently relies on reading and writing markdown files (`_WORKSPACE_LOCK_*.md`, `_LIVE_FEED.md`). This is slow, prone to filesystem drift, and lacks atomicity.
- **Transient State**: Orchestration state (task progress, agent chains) is largely transient or stored in session logs. There is no formal "State Machine" for complex, multi-step workflows.
- **Manual Decomposition**: Task decomposition is currently a manual process performed by `@kali`. There is no programmatic engine to decompose a high-level goal into a verifiable task graph.
- **Naive Scheduling**: `ResourceGuard` is a simple semaphore. It does not account for real-time hardware telemetry (CPU load, Thermal throttling, zRAM pressure) when deciding whether to spawn a new agent.
- **Observability Gap**: While we have trace IDs, we lack a "Flight Recorder"—a structured, event-sourced log of all A2A interactions that can be replayed for forensic debugging.

---

## 2. Gap Analysis for "Definitive Local AI Tool"

To transition from a "capable framework" to the "definitive local AI tool," the Orchestration layer must evolve from **Passive Dispatch** to **Active Governance**.

| Feature | Current State | Target State (Definitive Tool) | Delta |
|-------|--------------|-----------------------------------|---------|
| **Coordination** | File-based (Markdown) | Real-time A2A (Redis Streams) | 🔴 HIGH |
| **Workflow** | Linear/Manual Chains | Formal Task Graphs (DAGs) | 🔴 HIGH |
| **Scheduling** | Static Semaphore | Hardware-Aware Dynamic Scheduling | 🟡 MED |
| **State** | Session-based / Transient | Persistent, Resumable State Machine | 🔴 HIGH |
| **Routing** | Manual/Registry-based | Semantic Capability Routing (Vector) | 🟡 MED |
| **Forensics** | Event Logs | Event-Sourced Flight Recorder | 🟡 MED |

---

## 3. System Utilization Audit

The Omega Engine possesses a powerful infrastructure stack (Qdrant, Redis, SQL) that is currently underutilized in the Orchestration domain.

### 💾 Redis (Currently: Hot-Memory / Cache)
- **Underutilized**: Pub/Sub and Streams.
- **Opportunity**: Replace markdown-based locks and live feeds with Redis Streams. This enables real-time, atomic A2A messaging and distributed locking, removing the "filesystem bottleneck."

### 🌲 Qdrant (Currently: Semantic Search / Gnosis)
- **Underutilized**: Payload Indexing and Semantic Routing.
- **Opportunity**: Store agent capabilities as vectors. Instead of a manual `CapabilityRegistry`, the Orchestrator can perform a semantic search over agent capabilities to route tasks to the best-suited entity.

### 📊 PostgreSQL/SQLite (Currently: Persistence / Metrics)
- **Underutilized**: Task State Tracking.
- **Opportunity**: Use SQL to track the lifecycle of every `HandoffPacket` and task node in a DAG. This allows for "Crash-Resistant Orchestration" where a failed agent can be restarted exactly where it left off.

---

## 4. Deep Research Requirements

To implement the target state, the following research is required:
1. **Sovereign Task Graphs**: Research local-first DAG execution engines that can handle non-deterministic AI outputs (e.g., conditional edges based on agent verdicts).
2. **Hardware-Aware Scheduling**: Study the intersection of `llama-cpp-python` resource usage and system telemetry (via `omega-hub_get_hardware_stats`) to build a "Sovereign Scheduler."
3. **A2A State Synchronization**: Research patterns for maintaining a "Shared World State" across multiple autonomous agents without creating a single point of failure.
4. **Event Sourcing for AI**: Explore how to implement an event-sourced log for agent interactions to enable perfect replay and forensic audit.

---

## 5. Concrete Recommendations

### 🚨 P0: Blocking (Must fix before launch)
- **Atomic Coordination**: Migrate Hivemind workspace locks and live feeds from markdown files to **Redis**. This is critical for stability in high-concurrency parallel work.
- **Stateful Handoffs**: Implement a SQL-backed state tracker for `HandoffPackets` to prevent "orphan tasks" and enable recovery from tool-chain collapse.

### ⚡ P1: Critical (Sprint 1)
- **Task Graph Engine**: Replace linear delegation with a formal `TaskGraph` system. Allow `@kali` to define a DAG of tasks that the Orchestrator executes and verifies.
- **Semantic Capability Routing**: Integrate Qdrant into the `CapabilityRegistry` to enable semantic routing of tasks to agents.

### 🛠️ P2: Important (Sprint 2)
- **Sovereign Scheduler**: Upgrade `ResourceGuard` to a dynamic scheduler that uses real-time hardware telemetry to gate agent spawning and model loading.
- **Orchestration Flight Recorder**: Implement a structured event log of all A2A messages, tool calls, and state transitions.

### 🌟 P3: Enhancement (Nice to have)
- **Automated Decomposition**: Develop a "Decomposition Agent" (integrated into `@jem`) that can automatically turn a user query into a `TaskGraph` for the Orchestrator.
- **Cross-Platform A2A**: Standardize the A2A protocol to allow agents running in different CLIs (OpenCode, Cline, etc.) to communicate via a shared Redis bus.

---

**Verdict**: The Orchestration layer is functionally sound but architecturally "primitive." It relies too heavily on the filesystem for coordination. By weaponizing the existing Redis/Qdrant/SQL stack, Omega can move from a collection of agents to a truly integrated **Sovereign Intelligence System**.

*⬡ OMEGA ⬡ ANUBIS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pillar_p9 ⬡ VET-REPORT*
