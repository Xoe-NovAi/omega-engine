# 🔱 HIVEMIND UPDATE PLAN (PROPOSAL)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ WORKBENCH ⬡ PHASE-II

**Status**: PROPOSED (Awaiting Overseer Review)
**Target**: Hivemind Protocol & Orchestrator Integration

## 🎯 Objective
Implement the core features required for a robust, stateful, and aware Hivemind orchestration layer. This plan addresses the three primary backlog items identified in the Omega Engine workbench.

## 🔍 Current State & Identified Gaps

The Hivemind is currently a communication layer, but it lacks:
1. **Automatic Handoff**: The Orchestrator does not automatically notify the Hivemind when an agent completes a task.
2. **Lifecycle Management**: There is no mechanism to prune stale agent sessions or manage presence (TTL).
3. **Worker Autonomy**: There is no dedicated "Worker" entity that can independently execute tasks via Hivemind commands.

## 🛠️ Proposed Implementation Roadmap

### Phase 1: Orchestrator Handoff (Task: `wi_orchestrator_handoff`)
**Goal**: Ensure every agent completion is visible to the Hivemind.
- [ ] **Task 1.1**: Update `src/omega/oracle/orchestrator.py` to include a post-execution hook.
- [ ] **Task 1.2**: Implement `post_task_handoff()` to call `omega_hub_hivemind_post_context()` with `intent=handoff` upon successful agent completion.
- [ ] **Task 1.3**: Add verification tests to ensure the Hivemind receives the handoff signal.

### Phase 2: Presence & Lifecycle (Task: `wi_hivemind_ttl`)
**Goal**: Prevent "Ghost Agents" and manage session decay.
- [ ] **Task 2.1**: Implement a heartbeat mechanism in the `omega_hub` MCP server.
- [ ] **Task 2.2**: Add a TTL (Time-To-Live) field to the Hivemind session registry.
- [ ] **Task 2.3**: Implement a background "Reaper" process (or periodic cleanup task) that prunes sessions where the last heartbeat exceeds the TTL.
- [ ] **Task 2.4**: Add `AgentPresence` metadata to the Hivemind awareness view.

### Phase 3: Sprint Worker Implementation (Task: `wi_worker_build`)
**Goal**: Create a dedicated, Hivemind-driven agent for high-throughput task execution.
- [ ] **Task 3.1**: Scaffold the `SprintWorker` entity in `src/omega/oracle/entity_registry.py`.
- [ ] **Task 3.2**: Implement the `SprintWorker` logic:
    - Listen for `task` requests via Hivemind.
    - Execute tasks using a local model (e.g., `qwen3-1.7b`).
    - Post status updates (`queued`, `in_progress`, `completed`) back to Hivemind.
- [ ] **Task 3.3**: Integrate `SprintWorker` into the `Orchestrator` as a specialized worker type.

## 🧪 Verification & Testing
- **Handoff Test**: Run a task through the Orchestrator and verify the Hivemind log shows the handoff event.
- **TTL Test**: Simulate a stale session by manually setting an old heartbeat and verify the Reaper prunes it.
- **Worker Test**: Dispatch a task to the `SprintWorker` via Hivemind and verify the task lifecycle is correctly reported.

---
**Note to Overseer**: This plan addresses the critical connectivity and lifecycle gaps in the Hivemind. Upon approval, I will begin Phase 1.
