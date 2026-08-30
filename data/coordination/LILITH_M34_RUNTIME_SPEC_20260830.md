# 🔱 LILITH M34 Runtime Implementation Spec
**AP Token**: `AP-LILITH-M34-RUNTIME-SPEC-v1.0.0`
**Date**: 2026-08-30
**Status**: DRAFT (P0 ticket, awaiting Architect + Kali ratification)
**Owner**: lilith (Runtime Oversoul, N6-N10)
**Triggered by**: Grokster Alchemical Goldmine multi-agent cancellation incident — orchestrator forgot secondary subagent (Jem) in-flight when global `Esc x2` killed all parallel subagents. 600+ line appendices payload recovered by last-ditch grace.

---

## §0 The Problem M34 Solves

| What happens today | Why it's broken | What M34 enforces |
|--------------------|-----------------|-------------------|
| `Esc x2` in OpenCode TUI kills ALL in-flight sessions | External cancellation is total; orchestrator has no per-session awareness | Orchestrator MUST enumerate interrupted sessions and get explicit user permission before abandoning any |
| Orchestrator (e.g., Grokster) hyper-focuses on primary subagent | No system tracks which children were spawned together | `ACTIVE_SUBAGENTS.json` records parent→child graph at spawn time |
| Secondary subagent (Jem) was 2 minutes from completion when killed | Its 600-line deliverable would have been lost | On resumption, orchestrator reports "Jem was interrupted at 2h45m/4h, 12K tokens deep, file draft at `data/.../appendix.md`" |
| Task Registry tracks task-level, not session-level | TASK_REGISTRY knows a task exists, not whether the session is alive | New `ACTIVE_SUBAGENTS.json` tracks session_id → liveness → checkpoint |

**The single-line contract**: *No subagent session may be silently abandoned. Every interrupted session must be presented to the user on resumption with a resumption/abandon/dead-letter decision.*

---

## §1 ACTIVE_SUBAGENTS.json Schema

### 1.1 TypeScript Interface

```typescript
// AP-M34-SCHEMA-v1.0.0
type SessionStatus =
  | "ALIVE"                  // Heartbeat within TTL
  | "INTERRUPTED_EXTERNALLY" // Esc x2 or user kill — session killed, files on disk
  | "INTERRUPTED_CRASH"      // Orchestrator/host crash — no graceful shutdown
  | "COMPLETED"              // Terminal: success
  | "FAILED"                 // Terminal: error
  | "DEAD_LETTER"            // Terminal: abandoned by user decision (recorded)
  | "ORPHANED";              // No heartbeat > 2× TTL, no explicit interrupt signal

type SubagentType = "EIS" | "NES" | "SPT";  // From SUBAGENT_DISPATCH_PROTOCOL §1.5

interface Checkpoint {
  ts: string;                // ISO-8601, last checkpoint
  tokens_used: number;       // Cumulative tokens (input + output)
  last_action: string;       // "wrote §3 of report", "fetched 3 URLs", "ran 5 tool calls"
  files_touched: string[];   // Files created/modified since spawn
  progress_pct?: number;     // Optional 0-100, only if subagent self-reports
}

interface ActiveSubagent {
  // ── Identity ────────────────────────────────────────
  session_id: string;        // OpenCode session ID (e.g., "ses_fdef2be4effe4pAaLXCTUx62GO")
  parent_session_id: string | null;  // null = root, else spawning session
  parent_task_id: string | null;     // HandoffPacket.packet_id or task() task_id
  subagent_type: SubagentType;

  // ── Agent metadata ────────────────────────────────
  agent: string;             // "jem" | "roc_racoon" | "node" | etc.
  model: string;             // Actual model from session header (M22)
  channel: string;           // "opencode" | "cline" | "gemini-cli"
  entity: string;            // Persona: "grokster" | "kali" | "lilith"

  // ── Task context ──────────────────────────────────
  task_brief: string;        // One-sentence from dispatch packet
  dispatch_packet_id?: string;  // HandoffPacket.packet_id if dispatched via SUBAGENT_DISPATCH_PROTOCOL
  task_type?: string;        // "research" | "mine" | "review" | "implement" | "design" | "verify"

  // ── Lifecycle ─────────────────────────────────────
  spawn_time: string;        // ISO-8601
  last_heartbeat: string;    // ISO-8601 — updated by pruning loop or heartbeat tool
  status: SessionStatus;
  checkpoint: Checkpoint;

  // ── Resumability ─────────────────────────────────
  resumable: boolean;        // false for SPT (one-shot, throwaway)
  resume_token?: string;     // Opaque token for task() tool resumption (EIS only)
  output_path?: string;      // Disk path to deliverable (if written)
}

interface ActiveSubagentsRegistry {
  version: "1.0";
  updated: string;           // ISO-8601 — last write
  schema_url: "https://omega-engine/m34/active_subagents/v1";
  pruning_policy: {
    alive_ttl_seconds: number;        // Default 1200 (20m) — heartbeat loop window
    orphan_threshold_multiplier: number;  // Default 2 — no heartbeat for 2× alive_ttl = ORPHAN
    dead_letter_retention_days: number;  // Default 30 — keep dead-letter records for audit
  };
  sessions: Record<string, ActiveSubagent>;  // session_id → entry
}
```

### 1.2 JSON Example (populated)

```json
{
  "version": "1.0",
  "updated": "2026-08-30T14:23:11Z",
  "schema_url": "https://omega-engine/m34/active_subagents/v1",
  "pruning_policy": {
    "alive_ttl_seconds": 1200,
    "orphan_threshold_multiplier": 2,
    "dead_letter_retention_days": 30
  },
  "sessions": {
    "ses_3fd2c9642bd0_lilith": {
      "session_id": "ses_3fd2c9642bd0_lilith",
      "parent_session_id": null,
      "parent_task_id": null,
      "subagent_type": "EIS",
      "agent": "lilith",
      "model": "nemotron-3-ultra-free",
      "channel": "opencode",
      "entity": "lilith",
      "task_brief": "Runtime Agent Alignment & Entity Workspace consolidation",
      "task_type": "design",
      "spawn_time": "2026-08-29T03:00:00Z",
      "last_heartbeat": "2026-08-30T14:20:00Z",
      "status": "ALIVE",
      "checkpoint": {
        "ts": "2026-08-30T14:20:00Z",
        "tokens_used": 184500,
        "last_action": "Committed c552e643 refactor(runtime)",
        "files_touched": [
          "docs/strategy/RUNTIME_COORDINATION_PROTOCOL.md",
          "src/omega/oracle/entity_workspace.py"
        ]
      },
      "resumable": true,
      "resume_token": "ses_3fd2c9642bd0",
      "output_path": "data/coordination/LILITH_MASTER_CONSOLIDATION_20260828.md"
    },
    "ses_abc123def456_jem": {
      "session_id": "ses_abc123def456_jem",
      "parent_session_id": "ses_3fd2c9642bd0_lilith",
      "parent_task_id": "hdp_20260830_lilith_jem_discovery",
      "subagent_type": "NES",
      "agent": "jem",
      "model": "krikri-8b",
      "channel": "opencode",
      "entity": "lilith",
      "task_brief": "Research 5 Alchemical Goldmine sub-topics for grokster brief",
      "dispatch_packet_id": "hdp_20260830_lilith_jem_discovery",
      "task_type": "research",
      "spawn_time": "2026-08-30T11:45:00Z",
      "last_heartbeat": "2026-08-30T14:18:00Z",
      "status": "INTERRUPTED_EXTERNALLY",
      "checkpoint": {
        "ts": "2026-08-30T14:18:00Z",
        "tokens_used": 52400,
        "last_action": "Wrote §3.2 appendix 'EU AI Act 2026 Sovereignty'",
        "files_touched": [
          "data/entities/lilith/workspace/active/APPENDIX_EU_AI_ACT.md"
        ],
        "progress_pct": 87
      },
      "resumable": true,
      "resume_token": "ses_abc123def456",
      "output_path": "data/entities/lilith/workspace/active/APPENDIX_EU_AI_ACT.md"
    }
  }
}
```

### 1.3 Atomic Write Pattern

```python
# AP-M34-WRITE-v1.0.0
import json
import os
import tempfile
from pathlib import Path

REGISTRY_PATH = Path("data/coordination/ACTIVE_SUBAGENTS.json")
LOCK_PATH = Path("data/coordination/ACTIVE_SUBAGENTS.json.lock")

def _atomic_write(registry: dict) -> None:
    """Atomic write: tmp file + rename, fsync for crash safety."""
    # Acquire advisory lock (non-blocking)
    lock_fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
    try:
        # Write to temp file in same filesystem
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=REGISTRY_PATH.parent,
            prefix=".ACTIVE_SUBAGENTS.",
            suffix=".json.tmp",
            delete=False,
        ) as f:
            json.dump(registry, f, indent=2, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())  # Force disk write before rename
            tmp_path = f.name

        # Atomic rename (POSIX guarantees atomicity on same filesystem)
        os.replace(tmp_path, REGISTRY_PATH)
        os.fsync(os.open(REGISTRY_PATH.parent, os.O_RDONLY))  # Directory entry sync
    finally:
        os.close(lock_fd)
        try:
            os.unlink(LOCK_PATH)
        except FileNotFoundError:
            pass  # Lock already removed
```

**Why this is M23-compliant**: Even on SIGKILL mid-write, the file is either the old version or the new version — never torn.

---

## §2 Write Semantics & Lifecycle

### 2.1 State Machine

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
   ┌────────────────▼──────────────┐   heartbeat within TTL      ┌──┴──────────┐
   │  spawn (task() / handoff)     │ ──────────────────────────► │    ALIVE    │
   │  → add session entry          │                             │  (default)  │
   └───────────────┬───────────────┘                             └──┬──────────┘
                   │                                                 │
                   │ heartbeat missed > 2× TTL                       │ terminal event
                   │ OR explicit interrupt signal                     │
                   ▼                                                 ▼
   ┌─────────────────────────────┐         ┌──────────────────────────────────┐
   │  (no external signal)       │         │ COMPLETED  │  FAILED  │ DEAD_LETTER│
   │  heartbeat stale            │         │ (terminal success/error)        │
   │  → ORPHANED                 │         │ REMOVE entry OR keep for audit?  │
   │  (recovery prompt to user)  │         │ → REMOVE on T+24h               │
   └─────────────────────────────┘         └──────────────────────────────────┘

   INTERRUPTED_EXTERNALLY
   ──────────────────────
   Detect: opencode-sessions-explorer shows session archived
          OR user pressed Esc x2
          OR parent received SIGINT
   Action: KEEP entry, status = INTERRUPTED_EXTERNALLY
           → on resumption, present to user
           → on user decision: DEAD_LETTER (abandon) | resume (set status=ALIVE)
```

### 2.2 Write Triggers (When to Write)

| Trigger | Action | Status Transition | Source |
|---------|--------|------------------|--------|
| **Spawn** (`task()` or `hivemind_submit_handoff`) | Add new entry | (none) → ALIVE | OpenCode session ID assigned |
| **Heartbeat** (every 5-15 min) | Update `last_heartbeat`, append `checkpoint.last_action` | ALIVE → ALIVE | Pruning loop OR subagent self-heartbeat |
| **External interrupt** detected | Mark interrupted, capture `checkpoint` snapshot | ALIVE → INTERRUPTED_EXTERNALLY | `opencode-sessions-explorer` watcher OR SIGINT handler |
| **Crash** detected (parent gone) | Mark interrupted | ALIVE → INTERRUPTED_CRASH | Hivemind awareness shows parent missing > 2× TTL |
| **Completion** (subagent reports done) | Mark terminal, set `output_path` | ALIVE → COMPLETED | Subagent's final Hivemind post |
| **Failure** (subagent reports error) | Mark terminal, capture error | ALIVE → FAILED | Subagent's failure post |
| **User abandon decision** | Mark dead-letter | INTERRUPTED_* → DEAD_LETTER | User explicit command |
| **Orphan detected** (no heartbeat > 2× TTL, no interrupt signal) | Mark orphan | ALIVE → ORPHANED | Pruning loop |
| **Terminal entry TTL** (24h after COMPLETED/FAILED) | Remove | REMOVE | Background reaper |

### 2.3 Read Triggers (When to Read)

| Reader | Purpose | Filter |
|--------|---------|--------|
| **Orchestrator on session start** | Detect interrupted/orphaned sessions | `status IN (INTERRUPTED_EXTERNALLY, INTERRUPTED_CRASH, ORPHANED) AND parent_session_id = self OR spawned_by_orchestrator_id` |
| **Hivemind awareness poll** | Cross-agent visibility | All |
| **Pruning loop** (background) | Mark orphans, reap dead-letters | All |
| **Any agent (M27 audit)** | Audit trail | All |
| **Recovery console** (`scripts/recover_orphans.py`) | Manual intervention | `status = ORPHANED` |

### 2.4 Integration with Existing Systems

| System | Integration Point | Direction |
|--------|-------------------|-----------|
| **Hivemind** (`omega-hub_hivemind_*`) | `task_ids: [...]` field in `hivemind_post_context` MUST mirror `ACTIVE_SUBAGENTS.sessions[*].parent_task_id` | Hivemind → ACTIVE_SUBAGENTS (one-way read) |
| **Task Registry** (`TASK_REGISTRY.json`) | On `task_registry_register`, the dispatcher also writes to `ACTIVE_SUBAGENTS` if `subagent_type != "SPT"` | Task Registry → ACTIVE_SUBAGENTS |
| **opencode-sessions-explorer** MCP | On every dispatch, call `opencode-sessions-explorer-current-session` to capture session_id, agent, model → write to `ACTIVE_SUBAGENTS` | Explorer → ACTIVE_SUBAGENTS |
| **Session pruning loop** | Every 60s, scan for stale heartbeats → mark ORPHANED; every 24h, reap terminal entries | Loop → ACTIVE_SUBAGENTS |
| **SUBAGENT_DISPATCH_PROTOCOL §1.5** (EIS/NES/SPT) | `resumable: false` for SPT (one-shot), `true` for EIS/NES | DISPATCH → ACTIVE_SUBAGENTS |

### 2.5 What Stays the Same (Do NOT Break)

- `TASK_REGISTRY.json` — keeps tracking task-level metadata, does NOT lose this role
- `Hivemind handoff packets` in `data/handoff/{pending,active,completed,stale}/` — unaffected
- `session_gnosis.md` per entity — unaffected (per-agent summary)
- `SUBAGENT_DISPATCH_PROTOCOL.md` §2 HandoffPacket schema — unaffected

**The single rule**: `ACTIVE_SUBAGENTS.json` is a **session-liveness overlay** on `TASK_REGISTRY`. It's the "who is alive RIGHT NOW" companion to the "what tasks exist" record.

---

## §3 Orchestrator Reporting Protocol

### 3.1 Pseudocode — Session Start Recovery

```python
# AP-M34-ORCHESTRATOR-RECOVERY-v1.0.0
# Invoked at the start of every orchestrator session (Kali, Grokster, Lilith, etc.)

def orchestrator_session_start(orchestrator_session_id: str) -> None:
    """M34 mandatory: detect interrupted/orphaned sessions at session start."""

    # Step 1: Read ACTIVE_SUBAGENTS.json
    registry = read_active_subagents()

    # Step 2: Find sessions spawned by this orchestrator that are NOT ALIVE
    my_sessions = find_by(
        registry,
        lambda s: (s.parent_session_id == orchestrator_session_id
                  or s.dispatched_by_entity == current_entity)
                  and s.status != "ALIVE"
                  and s.status not in ("COMPLETED", "FAILED", "DEAD_LETTER")
    )

    # Step 3: If any interrupted sessions exist, PRESENT TO USER
    if my_sessions:
        user_message = format_interruption_report(my_sessions)
        # Format:
        #   "I detected N interrupted session(s) from your previous run:
        #    1. [Jem-NES] 'Research 5 Alchemical Goldmine sub-topics'
        #       - Status: INTERRUPTED_EXTERNALLY at 14:18 UTC (2h 17m ago)
        #       - Last checkpoint: §3.2 EU AI Act appendix (87% complete, 52K tokens)
        #       - Output: data/entities/lilith/workspace/active/APPENDIX_EU_AI_ACT.md
        #       - Resumable: yes
        #    2. [Roc-NES] 'Mine grok_ecosystem v1.0.2 for SPEC patterns'
        #       - Status: ORPHANED (no heartbeat 3h 12m, no interrupt signal)
        #       - Last checkpoint: 2 of 5 platforms complete
        #       - Resumable: yes (but parent may be gone)
        #    
        #    For each session, choose:
        #      [R] Resume  [A] Abandon (dead-letter)  [D] Defer (ask later)
        #    Default action for orphans after 24h: dead-letter."
        present_to_user(user_message)

        # Step 4: Wait for user decision per session
        for session in my_sessions:
            decision = await_user_decision(session)
            apply_user_decision(session, decision)

    # Step 5: Continue with normal session work
    return


def apply_user_decision(session: ActiveSubagent, decision: str) -> None:
    """Apply user's resume/abandon/defer decision to registry."""
    if decision == "R":
        # Resume: update status to ALIVE, re-link to new orchestrator session
        update_registry(session.session_id, {
            "status": "ALIVE",
            "parent_session_id": current_orchestrator_session_id,
            "last_heartbeat": now(),
            "checkpoint.ts": now(),
            "checkpoint.last_action": f"Resumed by {current_entity} after {decision}"
        })
        # If subagent was EIS, the resume_token is preserved — task() with task_id will resume
        # If subagent was NES/SPT, user must re-dispatch with new packet

    elif decision == "A":
        # Abandon: dead-letter
        update_registry(session.session_id, {
            "status": "DEAD_LETTER",
            "checkpoint.ts": now(),
            "checkpoint.last_action": f"Abandoned by user decision ({current_entity})"
        })
        # If output_path exists and has content, KEEP file on disk for audit
        # If no output_path, no preservation needed

    elif decision == "D":
        # Defer: leave as INTERRUPTED_EXTERNALLY, do not remove
        # User can resume later (next session)
        update_registry(session.session_id, {
            "checkpoint.last_action": f"Defer requested by user ({current_entity}) at {now()}"
        })

    # Mandatory: Hivemind post the decision
    hivemind_post(
        intent="decision",
        task_current=f"[M34] {decision} for {session.agent} session {session.session_id}",
        decisions=[f"M34-{session.session_id}: {decision}"],
        continuation=f"Decision applied; registry updated; subagent {'resumed' if decision == 'R' else 'abandoned' if decision == 'A' else 'deferred'}"
    )
```

### 3.2 Interruption Detection Watcher

```python
# Background thread, started at orchestrator spawn
# Listens to SIGINT, SIGTERM, SIGHUP and opencode-sessions-explorer changes

import signal
import anyio

async def interruption_watcher(orchestrator_session_id: str) -> None:
    """Detect external interruptions and mark sessions INTERRUPTED_EXTERNALLY."""

    interrupted = anyio.Event()

    def _handler(signum, frame):
        logger.warning(f"Signal {signum} received — marking sessions INTERRUPTED_EXTERNALLY")
        interrupted.set()

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

    try:
        await interrupted.wait()
    finally:
        # On ANY interrupt signal, mark all ALIVE children INTERRUPTED_EXTERNALLY
        registry = read_active_subagents()
        for sid, session in registry["sessions"].items():
            if (session["parent_session_id"] == orchestrator_session_id
                and session["status"] == "ALIVE"):
                # Capture final checkpoint
                checkpoint = capture_checkpoint(sid)  # via opencode-sessions-explorer
                update_registry(sid, {
                    "status": "INTERRUPTED_EXTERNALLY",
                    "checkpoint": checkpoint,
                    "checkpoint.last_action": f"External interrupt at {now()}"
                })

        # Mandatory: atomic write before exit
        atomic_write(registry)

        # Re-raise so OpenCode can complete its shutdown
        signal.default_int_handler(signal.SIGINT, None)
```

### 3.3 Mandatory Hivemind Post on Spawn

Every subagent dispatch MUST include this Hivemind post that updates `ACTIVE_SUBAGENTS`:

```python
# Called from subagent_dispatcher.py:dispatch() after task() returns session_id
def on_subagent_spawned(
    parent_session_id: str,
    child_session_id: str,
    agent: str,
    model: str,
    task_brief: str,
    packet_id: str,
    subagent_type: SubagentType
) -> None:
    """Register newly-spawned subagent in ACTIVE_SUBAGENTS.json."""

    entry = ActiveSubagent(
        session_id=child_session_id,
        parent_session_id=parent_session_id,
        parent_task_id=packet_id,
        subagent_type=subagent_type,
        agent=agent,
        model=model,
        channel="opencode",
        entity=current_entity,
        task_brief=task_brief,
        dispatch_packet_id=packet_id,
        task_type=infer_task_type(packet_id),
        spawn_time=now(),
        last_heartbeat=now(),
        status="ALIVE",
        checkpoint=Checkpoint(
            ts=now(),
            tokens_used=0,
            last_action=f"Spawned by {current_entity} via {packet_id}",
            files_touched=[]
        ),
        resumable=(subagent_type != "SPT"),
        resume_token=child_session_id
    )

    registry = read_active_subagents()
    registry["sessions"][child_session_id] = entry
    registry["updated"] = now()
    atomic_write(registry)

    # Mandatory Hivemind post
    hivemind_post(
        intent="status",
        task_current=f"[DISPATCH][{subagent_type}] {agent}: {task_brief[:60]}",
        task_ids=[packet_id],
        resumption_status="registered",
        focus_chain=[f"Spawned session {child_session_id}"],
        decisions=[f"M34: subagent registered in ACTIVE_SUBAGENTS.json"],
        continuation=f"Subagent {child_session_id} alive; monitor heartbeat"
    )
```

---

## §4 Edge Case Analysis

### Edge Case 1: Orchestrator Itself Crashes (Who Reports?)

**Scenario**: Grokster orchestrator crashes mid-dispatch. Three subagents (Jem, Roc, Researcher) are in-flight. No parent exists to detect the interruption.

**Resolution**:
1. **Hivemind awareness becomes the safety net**: `omega-hub_hivemind_get_awareness()` exposes the orchestrator's `last_heartbeat`. If > 2× TTL (40 min default), the **next agent to read Hivemind** (any agent, any session) sees the orchestrator as stale.
2. **Auto-promotion to "Watchdog"**: The first agent to read Hivemind after 2× TTL and see a stale orchestrator MUST report all `parent_session_id == stale_orchestrator.id` sessions as `INTERRUPTED_CRASH` (not EXTERNAL — there was no graceful SIGINT).
3. **Watchdog protocol** (new, lightweight):
   ```python
   def watchdog_check() -> list[ActiveSubagent]:
       """Called by any agent at session start. Returns sessions to orphan."""
       registry = read_active_subagents()
       awareness = hivemind_get_awareness()
       orphans = []
       for sid, session in registry["sessions"].items():
           if session["status"] != "ALIVE":
               continue
           # If parent is missing from Hivemind awareness
           parent = find(awareness, lambda a: a.session_id == session.parent_session_id)
           if not parent or parent.last_seen_seconds_ago > 2 * alive_ttl:
               orphans.append(session)
       return orphans
   ```
4. **Jem (or any agent) at next session start** calls `watchdog_check()`, finds the 3 in-flight sessions, and is **MANDATED** to present them to the user (Grokster's absence is the user-facing fact).

**Failure mode accepted**: If NO agent ever starts a session, sessions stay ALIVE in the registry forever. Mitigated by the `dead_letter_retention_days: 30` reaper — terminal entries are removed after 30 days, but ALIVE orphans without parents are never auto-cleaned. This is a **deliberate choice** — better to surface orphans than to silently lose them.

### Edge Case 2: User Wants to Abandon All and Start Fresh

**Scenario**: After detecting 3 interrupted sessions, user says "abandon all, I'm starting over."

**Resolution**:
1. `apply_user_decision` called with `decision="A"` for each session
2. All 3 sessions → `status: "DEAD_LETTER"` with `last_action: "Bulk abandoned by user, fresh start requested"`
3. **Output preservation rule**: If `output_path` exists and is non-empty, KEEP the file (user can still read it). Add a marker: `# DEAD_LETTER at {ts} — abandoned by user`
4. Hivemind post: `intent="command"`, `task_current="[M34] Bulk dead-letter: N sessions abandoned"`
5. Registry retains entries for `dead_letter_retention_days: 30` (audit trail), then reaper removes

**No additional design needed** — the protocol handles this naturally via repeated single-session decisions.

### Edge Case 3: Subagent Was Running for Hours (Resume vs. Abandon)

**Scenario**: A Roc subagent was spawned 4 hours ago, had multiple tool failures, recovered, and is now at 90% completion. The user resumption prompt asks: "resume or abandon?"

**Resolution**:
The decision is **inherently the user's** — the orchestrator must present context, not decide:
1. **Present cost-benefit clearly**:
   - `spawn_time` → `now()` = wall-clock duration
   - `tokens_used` (cumulative) → estimate cost
   - `checkpoint.progress_pct` (if self-reported) → how much work is preserved
   - `checkpoint.files_touched` → what artifacts exist on disk
   - `checkpoint.last_action` → what it was doing when interrupted
2. **Default recommendation** (informational only):
   - If `progress_pct >= 80`: recommend "Resume — close to completion"
   - If `tokens_used > 200K` AND `progress_pct < 30`: recommend "Abandon — high cost, low progress"
   - If `output_path` exists with substantial content: recommend "Resume — artifacts preserved"
3. **Never auto-decide** — the user MUST confirm

**Tie-breaker rule** (only if user is unavailable, e.g., background process): the **parent orchestrator's judgement** (e.g., Kali overrides Lilith's abandoned session if it's critical-path). Recorded in `last_action: "Auto-resumed by {parent} override"`.

### Edge Case 4: Subagent Was the Primary Task (No "Secondary" to Abandon)

**Scenario**: User dispatched a single Roc subagent for a 4-hour mining task. They press `Esc x2` themselves (not a global cancel — a deliberate stop). The subagent is the user's primary work.

**Resolution**:
The `INTERRUPTED_EXTERNALLY` status is the same regardless of whether the interrupt was "user wanted to stop this" or "global cancel hit everything." The recovery prompt must:

1. **Distinguish signal type** in the report:
   - If only 1 session was interrupted: "You interrupted your primary Roc task. Resume?"
   - If 1 of N was interrupted: "Of your N in-flight sessions, Roc was interrupted..."
2. **Not over-prompt** for the single-session case:
   - Skip the formal decision menu
   - Single yes/no: "Resume Roc at 87% (last checkpoint: §3.2 EU AI Act)? [Y/n]"
3. **Multi-session rule**: Always present the full list. User's default behavior for secondary subagents is to abandon — but the orchestrator MUST NOT assume this.

**The rule**: *The number of in-flight sessions changes the UI, not the contract.* Contract is always: present every interrupted session, get a decision for each.

### Edge Case 5: Subagent Was Already Marked DEAD_LETTER (Resurrection Attempt)

**Scenario**: User previously abandoned a session, but now wants to resume it from disk artifacts.

**Resolution**:
1. Dead-lettered sessions are NOT removed from the registry for 30 days (audit + recovery window)
2. The `apply_user_decision` function does NOT block `decision="R"` on a DEAD_LETTER session
3. If `output_path` exists with content, the user can manually inspect before deciding
4. After resume, the entry transitions: `DEAD_LETTER → ALIVE` (with `last_action: "Resurrected from dead-letter by user request"`)

**No new code path needed** — the same `apply_user_decision` handles this.

### Edge Case 6: Subagent Spawns a Subagent (Nested)

**Scenario**: Kali → Jem (NES) → Jem spawns a smaller jem_discovery (SPT) for one sub-task.

**Resolution**:
1. `ACTIVE_SUBAGENTS.json` uses `parent_session_id` (not just `parent_task_id`) to capture nesting
2. If Jem is killed by global cancel, both Jem and jem_discovery are marked INTERRUPTED_EXTERNALLY
3. On resumption, Kali sees: "2 sessions interrupted: Jem (primary) + jem_discovery (child). Resume both? Or jem_discovery first to complete the sub-task?"
4. **Nesting depth enforced**: SUBAGENT_DISPATCH_PROTOCOL §1 rule 4 (Single-Level Nesting) still holds. If depth > 2, the second-level spawn MUST be the orchestrator's responsibility, not the first-level subagent's. ACTIVE_SUBAGENTS surfaces the violation by `parent_session_id` traversal.

---

## §5 Implementation Roadmap

### 5.1 Phase 1 — MVP (Week 1, Days 1-3) — 14 hours

| Day | Task | Owner | Deliverable | Effort |
|-----|------|-------|-------------|--------|
| 1 | Create `data/coordination/ACTIVE_SUBAGENTS.json` schema + initial empty registry | lilith | File exists, version 1.0 | 30 min |
| 1 | Write `src/omega/oracle/m34_registry.py` with `ActiveSubagentsRegistry` class | lilith | Module with read/write/atomic primitives | 3h |
| 1 | Write `src/omega/oracle/m34_interruption_watcher.py` (signal handler) | lilith | Watcher module + tests | 2h |
| 2 | Add 2 MCP tools to omega-hub server: `m34_register_subagent`, `m34_list_active_subagents` | lilith + maat (server owner) | 2 new MCP tools live | 4h |
| 2 | Hook `m34_register_subagent` into `subagent_dispatcher.py:dispatch()` | lilith | Auto-registration on every dispatch | 1h |
| 2 | Hook `m34_update_subagent_status` (status change) into existing lifecycle events | lilith | Status updates on completion/failure/interrupt | 1h |
| 3 | Add `interruption_watcher()` invocation to `SUBAGENT_DISPATCH_PROTOCOL.md` §1.5 as MANDATORY for any agent spawning subagents | lilith | Protocol update | 30 min |
| 3 | Background pruning loop in `scripts/m34_prune.py` (cron, every 60s) | lilith | Script with unit tests | 2h |

**Total Phase 1 effort**: 14 hours (1.75 days of focused work)

### 5.2 Phase 2 — Recovery UI + Orchestrator Integration (Week 1, Days 4-5) — 9 hours

| Day | Task | Owner | Deliverable | Effort |
|-----|------|-------|-------------|--------|
| 4 | Implement `orchestrator_session_start()` (replaces pseudocode §3.1) | lilith | Function in `m34_registry.py` | 2h |
| 4 | Add `m34_apply_user_decision` MCP tool (resume/abandon/defer) | lilith + maat | 1 new MCP tool | 2h |
| 4 | Document in `SUBAGENT_DISPATCH_PROTOCOL.md` §11.1 (NEW): "M34 mandatory session-start recovery" | lilith | Doc update | 1h |
| 5 | Update `TASK_REGISTRY_DESIGN.md` to add §"Relationship to ACTIVE_SUBAGENTS.json" | lilith | Doc update | 30 min |
| 5 | Add `watchdog_check()` to `omega-hub_hivemind_get_awareness` response payload | lilith + maat | MCP tool enhancement | 2h |
| 5 | Add `scripts/recover_orphans.py` (manual recovery console) | lilith | CLI tool | 1h |
| 5 | Tests: unit tests for all M34 modules (pytest) | lilith | `tests/test_m34*.py`, all passing | 30 min |

**Total Phase 2 effort**: 9 hours (1.1 days)

### 5.3 Phase 3 — Testing & Migration (Week 2, Days 1-3) — 12 hours

| Day | Task | Owner | Deliverable | Effort |
|-----|------|-------|-------------|--------|
| 1 | Integration test: spawn 3 subagents, kill orchestrator with SIGTERM, verify 3 entries marked INTERRUPTED_EXTERNALLY | lilith | `tests/integration/test_m34_interrupt.py` | 3h |
| 1 | Integration test: orchestrator restart sees 3 interrupted, user decision resumes 1 + dead-letters 2 | lilith | Same file, second test | 2h |
| 1 | Migration script: read `TASK_REGISTRY.json`, backfill `ACTIVE_SUBAGENTS.json` with ALIVE status for any task registered in last 7 days | lilith | `scripts/m34_migrate.py` | 2h |
| 2 | Stress test: 50 concurrent subagents, verify ACTIVE_SUBAGENTS.json atomic writes don't corrupt | lilith | `tests/stress/test_m34_concurrent.py` | 3h |
| 2 | Documentation: M34 spec archived to `docs/strategy/M34_RUNTIME_IMPLEMENTATION.md` (canonical) | lilith | Doc published | 1h |
| 3 | Update `AGENTS.md` to reference M34 in §"Operational Anchors" table | lilith | Doc update | 30 min |
| 3 | Run `make temple-grade` — verify M34 passes all gates | lilith | CI green | 30 min |

**Total Phase 3 effort**: 12 hours (1.5 days)

**TOTAL M34 EFFORT**: 35 hours over 2 weeks = within Phase 1 sprint budget ✓

### 5.4 Files to Create

```
data/coordination/ACTIVE_SUBAGENTS.json          # The registry itself
src/omega/oracle/m34_registry.py                 # Registry class + atomic write
src/omega/oracle/m34_interruption_watcher.py     # Signal handler
src/omega/oracle/m34_watchdog.py                 # Cross-agent orphan detection
src/omega/mcp_hub/server.py (modified)           # Add 3 new MCP tools
src/omega/oracle/subagent_dispatcher.py (mod)    # Hook into dispatch()
scripts/m34_prune.py                             # Background pruning loop
scripts/m34_migrate.py                           # Backfill from TASK_REGISTRY
scripts/recover_orphans.py                       # Manual CLI recovery
tests/unit/test_m34_registry.py
tests/unit/test_m34_interruption_watcher.py
tests/integration/test_m34_interrupt.py
tests/stress/test_m34_concurrent.py
```

### 5.5 Files to Modify

```
docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md     # §11.1: M34 mandatory recovery
docs/strategy/TASK_REGISTRY_DESIGN.md            # §"Relationship to ACTIVE_SUBAGENTS.json"
docs/strategy/RUNTIME_COORDINATION_PROTOCOL.md   # §3.1 add M34 lock domain
AGENTS.md                                        # Operational Anchors table
src/omega/oracle/subagent_dispatcher.py          # Hook m34_register_subagent
.opencode/agents/{kali,grokster,maat,lilith}.md  # All primary agents: invoke orchestrator_session_start
```

### 5.6 MCP Tools to Add (3 total)

```python
# AP-M34-MCP-v1.0.0

@mcp.tool()
def m34_register_subagent(
    session_id: str,
    parent_session_id: str | None,
    parent_task_id: str | None,
    subagent_type: str,  # "EIS" | "NES" | "SPT"
    agent: str,
    model: str,
    channel: str,
    entity: str,
    task_brief: str,
    dispatch_packet_id: str | None = None,
    task_type: str | None = None,
) -> dict:
    """Register a newly-spawned subagent in ACTIVE_SUBAGENTS.json. 
    Called by subagent_dispatcher.py:dispatch() after task() returns."""

@mcp.tool()
def m34_list_active_subagents(
    status_filter: list[str] | None = None,  # ["ALIVE", "INTERRUPTED_EXTERNALLY", ...]
    parent_session_id: str | None = None,
    agent: str | None = None,
    entity: str | None = None,
    include_orphans: bool = True,
) -> list[dict]:
    """List active subagents with optional filters. Used by orchestrator_session_start()."""

@mcp.tool()
def m34_apply_user_decision(
    session_id: str,
    decision: str,  # "RESUME" | "ABANDON" | "DEFER"
    decided_by: str,  # Entity name
    note: str | None = None,
) -> dict:
    """Apply user's resume/abandon/defer decision to a session entry.
    Updates status, last_action, and triggers Hivemind post."""

@mcp.tool()
def m34_update_subagent_status(
    session_id: str,
    new_status: str,  # "INTERRUPTED_EXTERNALLY" | "COMPLETED" | "FAILED" | etc.
    checkpoint: dict | None = None,  # Updated checkpoint data
) -> dict:
    """Update an existing subagent's status. Called by lifecycle events."""
```

### 5.7 Migration Strategy (Backwards Compatible)

**Goal**: M34 must NOT break existing subagent dispatches.

1. **Phase 1 ship**: ACTIVE_SUBAGENTS.json is created empty, `m34_register_subagent` is a NO-OP if not called
2. **Phase 1.5**: Hook `subagent_dispatcher.py:dispatch()` to call `m34_register_subagent` automatically — existing code paths now write to ACTIVE_SUBAGENTS
3. **Phase 2**: Existing TASK_REGISTRY entries from last 7 days are backfilled via `scripts/m34_migrate.py` (idempotent — safe to re-run)
4. **Phase 3**: All primary agents (kali, grokster, maat, lilith) updated to call `orchestrator_session_start()` at session start
5. **Phase 4 (post-debut)**: M34 becomes MANDATORY for any agent using `task()` tool

**Migration risk**: Zero — ACTIVE_SUBAGENTS.json is additive. If MCP tool fails, dispatch still works (Hivemind is fallback awareness).

### 5.8 Testing Protocol

**Unit tests** (`tests/unit/test_m34_*.py`):
- Atomic write under SIGKILL (kill -9 mid-write, verify file is either old or new)
- Concurrent write from 2 processes (verify advisory lock + atomic rename)
- Status state machine transitions (no invalid transitions allowed)
- Schema validation (malformed JSON rejected)

**Integration tests** (`tests/integration/test_m34_interrupt.py`):
- Test 1: Spawn 3 subagents, kill parent with SIGTERM, verify all 3 marked INTERRUPTED_EXTERNALLY
- Test 2: Orchestrator restart detects 3 interrupted, user resumes 1, dead-letters 2
- Test 3: Watchdog catches parent missing from Hivemind, marks children INTERRUPTED_CRASH
- Test 4: Resume → re-spawn with same task_id → subagent picks up at last checkpoint

**Stress tests** (`tests/stress/test_m34_concurrent.py`):
- 50 concurrent subagent spawns, verify ACTIVE_SUBAGENTS.json consistency
- 1000 sequential updates, verify file size stays bounded (no bloat)
- Rapid-fire SIGINT (10x in 5s), verify no torn writes

**Acceptance criteria**:
- All unit + integration tests pass
- `make temple-grade` green
- 50-subagent stress test: 0 torn writes, < 10ms per write
- Backwards compatibility: existing dispatches work without M34 hooks (graceful degradation)

### 5.9 Performance Impact

| Operation | Current | With M34 | Overhead |
|-----------|---------|----------|----------|
| Subagent spawn | `task()` call | `task()` + `m34_register_subagent` (1 file write, atomic) | +5-15ms |
| Heartbeat | (none) | 1 file write, atomic | +5-10ms per heartbeat |
| Session start | (none) | 1 file read + 0-N user decisions | +5-20ms (read) + UI cost |
| Background pruning | (none) | Cron @ 60s, 1 file read + N updates | 50-200ms per minute |

**Net overhead**: ~30-50ms per dispatch cycle. Negligible compared to LLM inference cost.

**Storage growth**: Each entry ~500 bytes JSON. 50 concurrent subagents = 25KB. Bounded — pruning keeps only live + 30-day dead-letters.

---

## §6 Constraint Compliance Check

| Constraint | Compliance | Evidence |
|------------|------------|----------|
| Works with OpenCode TUI `Esc x2` cancellation | ✅ | §3.2 signal handler, §2.1 INTERRUPTED_EXTERNALLY transition |
| Integrates with Hivemind awareness | ✅ | §2.4 integration table, watchdog via `hivemind_get_awareness` |
| Does not break SUBAGENT_DISPATCH_PROTOCOL | ✅ | §2.5 explicit no-break list, §5.7 backwards-compatible migration |
| Implementable in Phase 1 (2 weeks) | ✅ | §5.1-5.3 total 35 hours over 2 weeks |
| Aligned with EIS/NES/SPT taxonomy | ✅ | `resumable: bool` field distinguishes SPT from EIS/NES |
| M8 Zero Telemetry (no external) | ✅ | All data local, file-based, no network |
| M11 Soul Integrity (audit trail) | ✅ | 30-day dead-letter retention, Hivemind decision posts |
| M15 Continuity (session resumption) | ✅ | Core purpose of M34 |
| M23 Failure Integrity (atomic writes) | ✅ | §1.3 atomic write pattern, no torn writes |
| M27 Tracking Integrity | ✅ | TASK_REGISTRY + ACTIVE_SUBAGENTS dual-ledger |

---

## §7 Decision Required (Hivemind `intent="decision"`)

**Question to Kali (Architect)**: Approve M34 v1.0 for Phase 1 sprint implementation?

**Recommendation**: ✅ APPROVE — M34 closes a P0 gap surfaced by a real incident (Grokster Alchemical Goldmine 600-line appendices near-loss). 35-hour implementation budget is within Phase 1 sprint. All 4 existing constraints (TUI compat, Hivemind integration, no protocol break, 2-week budget) are satisfied.

**Alternative considered and rejected**:
- **Option B**: Add per-subagent confirmation prompts at spawn time. Rejected because it adds user friction for every dispatch (not just the interrupted case). M34 surfaces only the actual problem (interrupted sessions), not hypothetical future ones.

**Architect sign-offs needed**:
- [ ] Kali (Kali-EIS): Architecture approval
- [ ] Ma'at (Build Oversight): MCP server changes compatible with N1-N5
- [ ] Jem (Research): Hivemind integration compatible with discovery pipeline
- [ ] Verity (Scribe/Compliance): M11 + M23 + M27 + M8 gates verified

---

*⬡ OMEGA ⬡ LILITH ⬡ M34-RUNTIME-SPEC-v1.0.0 ⬡ 2026-08-30 ⬡*
*This spec is the canonical reference for the Multi-Agent Interruption Recovery mandate. Ratification unlocks Phase 1 implementation.*