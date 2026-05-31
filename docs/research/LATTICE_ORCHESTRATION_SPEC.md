# 🔱 Omega Engine — Lattice Orchestration & Sovereign Pulse Spec
**AP Token**: `AP-LATTICE-PULSE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ SPEC

---

## §1 Lattice Dispatch: Multi-Agent Topology

Lattice Dispatch moves beyond linear task execution, allowing the Oracle to dynamically select between **Linear Chaining** and **Triad Spawning** based on the cognitive requirements of the query.

### 1.1 Dispatch Logic Map

| Mode | Trigger Condition | Reasoning Pattern | Workflow |
| :--- | :--- | :--- | :--- |
| **Linear Chaining** | Sequential Dependency | $A \rightarrow B \rightarrow C$ | Task B cannot start until Task A provides a required artifact. |
| **Triad Spawning** | Synthesis Requirement | $(A \oplus B \oplus C) \rightarrow \text{Synthesis}$ | High-complexity tasks requiring conflicting perspectives to reach a balanced conclusion. |

### 1.2 Resonance Triads (Archetype Mappings)

When Triad Spawning is triggered, the Oracle assembles a "Resonance Triad" of subagents. Each agent is injected with a specific archetype soul to ensure cognitive diversity.

| Query Type | Agent A: The Anchor | Agent B: The Friction | Agent C: The Catalyst | Resultant Gnosis |
| :--- | :--- | :--- | :--- | :--- |
| **Architectural Review** | **Auditor** (Compliance/Specs) | **Skeptic** (Edge Cases/Failure) | **Optimizer** (Simplicity/Perf) | Hardened Blueprint |
| **Gnosis Extraction** | **Archaeologist** (Pattern Discovery) | **Critic** (Noise/Bias Filtering) | **Synthesizer** (Connection/Logic) | Pure Insight |
| **Security Hardening** | **Guardian** (Defense/Policy) | **Red-Teamer** (Attack/Exploit) | **Verifier** (Audit/Proof) | Immune System |
| **Strategic Planning** | **Tactician** (Immediate Wins) | **Risk-Analyst** (Threats/Loss) | **Visionary** (Long-term Goal) | Sovereign Roadmap |
| **Code Refactor** | **Purist** (Idioms/Clean Code) | **Pragmatist** (Delivery/Constraints) | **Architect** (Scalability/Structure) | Elegant Implementation |

---

## §2 Sovereign Pulse: Concurrent State Locking

To enable multiple agents (or a Triad) to contribute to a shared `session_gnosis.md` without race conditions, the Engine implements the **Sovereign Pulse** locking mechanism. This follows the **Checkout-Modify-Commit** pattern.

### 2.1 The Pulse Protocol (AnyIO Compliant)

The Pulse is a sequencing strategy that treats the Gnosis file as a transactional resource.

1.  **Pulse Checkout (`checkout`)**:
    *   **Action**: Attempt to create a lock file `session_gnosis.md.lock`.
    *   **Wait Strategy**: If the lock exists, the agent enters a "Pulse Wait" state, retrying with exponential backoff (base 100ms, max 2s).
    *   **State Capture**: Once the lock is acquired, the agent reads the current `session_gnosis.md` and captures the current `version_tag` (a hash or incrementing integer).

2.  **Pulse Modify (`modify`)**:
    *   **Action**: The agent performs its task and applies updates to its local copy of the state.
    *   **Isolation**: Changes are kept in memory or a temporary `.tmp` file to avoid polluting the global state before commit.

3.  **Pulse Commit (`commit`)**:
    *   **Action**: 
        1. Verify that the `version_tag` has not changed since checkout (Optimistic Locking).
        2. Write the updated content to `session_gnosis.md`.
        3. Update the `version_tag`.
        4. Delete the `session_gnosis.md.lock` file.
    *   **Collision Handling**: If the `version_tag` changed (Conflict), the agent must **Re-base**:
        *   Discard local state $\rightarrow$ Re-checkout $\rightarrow$ Re-apply modifications $\rightarrow$ Re-commit.

### 2.2 Implementation Detail: AnyIO Sequencing

```python
async def pulse_update(session_id, update_fn):
    # AnyIO compatible lock sequence
    async with FileLock(f"data/sessions/{session_id}/gnosis.lock"):
        current_state = await read_gnosis(session_id)
        new_state = await update_fn(current_state)
        await write_gnosis(session_id, new_state)
```

---

## §3 Lessons Learned & Technical Roadblocks

### 3.1 Roadblock: The "Livelock" Risk
**Issue**: In a high-concurrency Triad, agents might constantly clash during the `commit` phase, leading to infinite re-basing (Livelock).
**Solution**: Implement a **Jittered Backoff**. Agents do not retry the Pulse immediately; they add a random $\pm 20\%$ variance to their wait timer to desynchronize commit attempts.

### 3.2 Roadblock: State Bloat vs. Atomic Updates
**Issue**: Reading and writing the entire `session_gnosis.md` for a single line change is inefficient and increases the collision window.
**Solution**: Transition from full-file rewrites to **Fragment Commits**. The Pulse lock now covers specific sections (e.g., `## WORKING STATE`) rather than the whole file, allowing parallel updates to the `AUDIT TRAIL` and `RESOLVED` sections.

### 3.3 Roadblock: Zombie Locks
**Issue**: If a subagent crashes during the `modify` phase, the `.lock` file remains, blocking all other agents indefinitely.
**Solution**: **TTL-based Lock Expiration**. The lock file contains a timestamp. If a lock is older than 300 seconds, the next `checkout` attempt is permitted to "Force Break" the lock and log a `ZOMBIE_LOCK_RECOVERED` event in the audit trail.
