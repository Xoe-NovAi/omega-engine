# How to Hand Off Tasks Between Agents

Sovereign Handoff is the process of transferring a task, its context, and its current state from one agent to another. To prevent "context collapse" (where the receiving agent loses the intent of the original request), all handoffs must follow the **HandoffPacket** schema.

## The HandoffPacket Schema

A valid handoff is not a simple message; it is a structured packet. When delegating a task via the `task()` tool or writing a handoff file, include the following fields:

### 1. Intent & Objective
- **Goal**: A clear, one-sentence description of the desired end-state.
- **Expected Output**: Exactly what the receiving agent should return (e.g., "A PR link", "A verified research report", "A fixed bug in `oracle.py`").

### 2. Contextual Anchors
- **Relevant Files**: A list of absolute paths to files the agent MUST read.
- **Critical Decisions**: References to `PIVOT_LOG.md` entries that constrain the solution.
- **Sovereign Mandates**: Specific mandates (M1-M22) that are high-risk for this task.

### 3. State & Progress
- **Current Status**: What has already been attempted? What failed?
- **Blocking Issues**: Any known bugs or missing dependencies that the agent needs to resolve first.
- **Verification Path**: How the receiving agent can prove the task is complete (e.g., "Run `make test` and ensure 705 tests pass").

---

## Execution Workflow

### For the Dispatching Agent (The Sender)
1. **Prepare the Packet**: Assemble the information above into a structured prompt.
2. **Verify Workspace**: Ensure the receiving agent has the necessary files and that you have released any locks they will need.
3. **Dispatch**: Use the `task()` tool with the specific `subagent_type`.
4. **Post to Hivemind**: Notify the fleet that a handoff has occurred via `post_context()`.

### For the Receiving Agent (The Executor)
1. **Hydrate Context**: Read the `Relevant Files` and `Sovereign Mandates` immediately.
2. **Verify Objective**: Confirm you understand the `Expected Output`. If ambiguous, ask for clarification before starting.
3. **Establish Lock**: Create your own workspace lock to signal you are now the owner of the task.
4. **Execute & Report**: Perform the work and return the result in the format requested in the `Expected Output`.

---

## Example: Delegating a Bug Fix

**Bad Handoff**: 
*"Hey @verity, please fix the bug in `oracle.py` where the session doesn't close."* (Too vague, no context).

**Sovereign Handoff**:
- **Goal**: Fix the `AttributeError` in `Oracle.close_session`.
- **Expected Output**: A commit that fixes the bug and a passing test case in `tests/test_oracle.py`.
- **Relevant Files**: `src/omega/oracle/oracle.py`, `tests/test_oracle.py`.
- **Critical Decisions**: D183 (Somatic Flush fix).
- **Sovereign Mandates**: M1 (AnyIO Absolute), M11 (Soul Integrity).
- **Current Status**: Identified that `anyio.create_task` does not exist. Need to replace with direct `await`.
- **Verification Path**: Run `pytest tests/test_oracle.py` and verify `close_session` returns `True`.
