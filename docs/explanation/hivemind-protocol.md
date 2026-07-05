# Explanation: The Hivemind Coordination Protocol

The Hivemind is the Omega Engine's shared awareness layer. It transforms a collection of independent agents into a coordinated fleet by providing a real-time, shared state of "who is doing what."

## The Problem: Agent Collision

In a multi-agent system, "collision" occurs when two agents attempt to modify the same resource (e.g., a file or a database record) simultaneously. Without coordination, this leads to:
- **Race Conditions**: One agent overwrites the other's changes.
- **Redundant Effort**: Two agents spend tokens solving the same problem.
- **Context Drift**: Agents operate on stale versions of the codebase.

## The Solution: Shared Awareness

The Hivemind solves this using a set of MCP tools that implement a "Declare $\rightarrow$ Lock $\rightarrow$ Log" pattern.

### 1. The Awareness Layer (`get_awareness`)
Instead of polling every agent, agents query the Hivemind to see a snapshot of all active tasks. This provides immediate visibility into the fleet's current focus.

### 2. The Intent Layer (`post_context`)
Before starting a task, an agent posts its intent. This acts as a "soft lock," signaling to other agents that a specific domain is currently being handled.

### 3. The Physical Lock (`WORKSPACE_LOCK`)
For file edits, the Hivemind uses a **Physical Lock** pattern. An agent writes a lock file to `data/coordination/`. This is a hard signal that the filesystem area is owned. Other agents are mandated to respect this lock and request a handoff before proceeding.

### 4. The Live Feed (`LIVE_FEED`)
Every agent maintains a live feed. This is a high-frequency, low-latency log of progress. It allows the user (and other agents) to monitor the "heartbeat" of a task without interrupting the agent's flow.

---

## The Coordination Cycle

```
[Query] 
     │
     ▼
[Check Awareness] ──▶ (Who is active?)
     │
     ▼
[Post Intent] ──▶ (I am working on X)
     │
     ▼
[Acquire Lock] ──▶ (Lock file created)
     │
     ▼
[Execute & Log] ──▶ (Update Live Feed)
     │
     ▼
[Release Lock] ──▶ (Delete lock file)
     │
     ▼
[Final ACK] ──▶ (Notify Hivemind of completion)
```

## Sovereign Benefits

- **Zero Telemetry**: All Hivemind data is stored locally in `data/coordination/`. No external coordination servers are used.
- **Resilience**: Because locks and feeds are files, the coordination state survives agent crashes or toolchain restarts.
- **Transparency**: The user can see exactly how the fleet is decomposing a complex problem in real-time.
