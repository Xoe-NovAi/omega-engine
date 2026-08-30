# How to Use the Hivemind Coordination Protocol

The Hivemind is the Omega Engine's shared awareness layer. It allows multiple agents to work in parallel on the same codebase without stepping on each other's toes or duplicating effort.

## Core Coordination Workflow

Whenever you are engaging in multi-step work (>3 steps) or working in parallel with other agents, you **MUST** follow this sequence:

### 1. Check Awareness
Before starting any work, check who is currently active and what they are doing.
**Tool**: `omega-hub_hivemind_get_awareness()`

### 2. Declare Presence (Post Context)
Declare your presence and your specific intent to the fleet. This prevents "collision" where two agents try to edit the same file.
**Tool**: `omega-hub_hivemind_post_context(context="Working on the MemoryStore batch writer implementation")`

### 3. Establish a Workspace Lock
If you are editing files, you must write a workspace lock. This is a physical signal to other agents that a specific area of the codebase is "owned" by you for the duration of the task.
**Path**: `data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md`

**Example**: `data/coordination/JEM_WORKSPACE_LOCK_20260704.md`

### 4. Initialize a Live Feed
Maintain a real-time log of your progress. Other agents (and the user) use the live feed to track your state without needing to read your entire session history.
**Path**: `data/coordination/{ENTITY}_LIVE_FEED.md`

**Format**:
`[{timestamp}] {TASK_ID}: {STATUS} — {SUMMARY}`

### 5. Send Heartbeats
For long-running operations, send a heartbeat every 5-10 minutes to signal that you are still active and haven't crashed.
**Tool**: `omega-hub_hivemind_heartbeat(channel="opencode", entity="{your_name}")`

---

## Handling Collisions

If you encounter a workspace lock for a file you need to edit:
1. **Read the Lock**: Check the lock file to see who owns it and what their intent is.
2. **Request Handoff**: Use the Hivemind to ask the owner for a handoff or to coordinate a joint edit.
3. **Wait for ACK**: Do not break a lock without an explicit acknowledgment (ACK) from the owner.

## Summary Checklist

- [ ] `get_awareness()` called?
- [ ] `post_context()` sent?
- [ ] Workspace lock file created?
- [ ] Live feed initialized?
- [ ] Heartbeat scheduled?
