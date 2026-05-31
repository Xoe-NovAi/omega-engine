# 🔱 Implementation Blueprint: Sovereign Pulse

**Goal**: Implement a concurrent state-locking mechanism for `session_gnosis.md` to enable safe multi-agent contributions.

**Target Files**:
- `src/omega/oracle/pulse.py` (New)
- `src/omega/oracle/orchestrator.py`
- `src/omega/oracle/session_manager.py` (Integration)

**Step-by-Step Instructions**:

### Step 1: Implement the Pulse Core
Create `src/omega/oracle/pulse.py`:
- Implement `SovereignPulse` class.
- **Checkout Method (`checkout`)**:
    - Attempt to create `session_gnosis.md.lock`.
    - Implement exponential backoff with **Jittered Backoff** ($\pm 20\%$ variance) to prevent livelock.
    - Read current `session_gnosis.md` and capture `version_tag`.
    - Handle **Zombie Locks**: If lock is $> 300s$ old, force-break it and log `ZOMBIE_LOCK_RECOVERED`.
- **Commit Method (`commit`)**:
    - Implement **Optimistic Locking**: Verify `version_tag` hasn't changed.
    - If changed: Trigger **Re-base** (Discard $\rightarrow$ Re-checkout $\rightarrow$ Re-apply $\rightarrow$ Commit).
    - If unchanged: Write updated content, increment `version_tag`, and delete `.lock` file.
- **Fragment Commits**: Instead of full-file rewrites, implement logic to target specific sections (e.g., `## WORKING STATE`).

### Step 2: Integration with Agent Workflow
Modify `src/omega/oracle/orchestrator.py`:
- Wrap all `session_gnosis.md` updates in the `pulse_update` pattern:
```python
async def pulse_update(session_id, update_fn):
    async with SovereignPulse(session_id):
        current_state = await pulse.read_gnosis()
        new_state = await update_fn(current_state)
        await pulse.commit(new_state)
```
- Ensure every dispatched agent (Linear or Triad) uses this pattern before terminating.

### Step 3: AnyIO Compliance
- Use `anyio.to_thread.run_sync` for all file-based locking and I/O operations to avoid blocking the event loop.
- Use `anyio.Lock` for internal memory state synchronization.

### Step 4: Verification
1. **Concurrency Stress Test**:
    - Launch a Resonance Triad (3 agents) and force them to write to `session_gnosis.md` simultaneously.
    - Verify that no data is lost and no race conditions occur.
    - Verify that the `.lock` file is created and deleted correctly.
2. **Conflict Resolution Test**:
    - Simulate a `version_tag` mismatch.
    - Verify that the agent correctly performs a **Re-base** and commits the updated state.
3. **Zombie Lock Recovery**:
    - Manually create a lock file with an old timestamp.
    - Attempt a `checkout` and verify the lock is broken and the event is logged.
