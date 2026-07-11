# 🔱 Omega Engine — Hivemind Coordination Protocol
# ⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_maat ⬡ HIVEMIND-PROTOCOL
**AP Token**: `AP-HIVEMIND-PROTOCOL-v1.3.0`
**Status**: STANDARD
**Last Updated**: 2026-06-25
**Mandate Reference**: Extends Mandate 5 (Gnosis Preservation), Mandate 11 (Soul Integrity), and Mandate 23 (Failure Integrity)

---

## §0 Purpose

The **Hivemind** is the live coordination layer for multiple Omega Engine agents
working in parallel. It answers three questions at any moment:

1. **Who is alive?** — `hivemind_get_awareness()` returns the list of active CLIs
2. **What are they doing?** — `hivemind_get_session()` returns current task, focus chain, decisions
3. **Can we coordinate?** — Live feed + workspace lock files enable explicit handoff

**Origin**: The core concept — agents knowing about each other — is the **user's
original design** (Xoe-NovAi Foundation vision). Hivemind is the **implementation**.

**Heritage**:
- `[id-soft: doom-1993]` **ZONEID Pattern** — `ZONEID_PRESENCE = 0x1d4a17` for
  presence record integrity (Link P9 Runtime)
- `[id-soft: doom-1993]` **ZONEID Pattern** — `ZONEID_HANDOFF = 0x1d4a16` for
  handoff packet integrity (Subagent Dispatcher)

---

## §1 When to Use Hivemind

| Scenario | Hivemind? | Workspace Lock? | Live Feed? |
|----------|-----------|-----------------|------------|
| **Single agent, single task** | ❌ No | ❌ No | ❌ No |
| **Single agent, multi-step work** | 🟡 Optional (recommended for >3 steps) | ❌ No | 🟡 Optional |
| **Multi-agent, sequential** | ✅ Yes (declare presence) | ❌ No | ✅ Yes |
| **Multi-agent, parallel (same files)** | ✅ **MANDATORY** | ✅ **MANDATORY** | ✅ **MANDATORY** |
| **Multi-agent, parallel (different files)** | ✅ Yes (live awareness) | 🟡 Recommended | ✅ Yes |
| **Cross-CLI (OpenCode + Cline + OpenCode)** | ✅ **MANDATORY** | ✅ **MANDATORY** | ✅ **MANDATORY** |

**Rule of thumb**: If you can see another agent's live feed entry, they can see
yours. Coordination is symmetric. Declare your presence before assuming privacy.

---

## §2 Hivemind Commands (MCP Server)

Hivemind is exposed as MCP tools via `omega-hub` server. All agents have access.

### §2.1 Get Active Agents

```python
omega-hub_hivemind_get_awareness()
```

Returns list of all active participants:
```json
[
  {
    "cli": "opencode/kali",
    "model": "deepseek-v4-flash",
    "task_current": "Building Link P9 Runtime...",
    "last_seen": "2026-06-03T02:28:06.199164+00:00"
  }
]
```

**Use case**: Check who's working before starting a session. Don't duplicate work.

### §2.1 The `agent_id` Convention (CRITICAL)

Every agent in the Hivemind is identified by an `agent_id` constructed from
two separate components passed as distinct API parameters:

- **`channel`** = the execution environment (`opencode`, `cline`, `gemini-cli`)
- **`entity`** = the persona active within that channel (`kali`, `roc_racoon`, `doom_guy`)

The server internally constructs `agent_id = f"{channel}/{entity}"` for indexing.

Examples:
- `channel="opencode"`, `entity="kali"` → agent_id `opencode/kali`
- `channel="opencode"`, `entity="roc_racoon"` → agent_id `opencode/roc_racoon`
- `channel="cline"`, `entity="doom_guy"` → agent_id `cline/doom_guy`
- `channel="gemini-cli"`, `entity="maat"` → agent_id `gemini-cli/maat`

**Why this matters**:
- CLIs and entities are fundamentally different. A CLI is an **execution channel** (how code runs).
  An entity is a **persona** (who is speaking). Conflating them loses architectural clarity.
- Separate API parameters ensure agents cannot conflate them — they are distinct fields.
- The compound `agent_id` preserves both dimensions for indexing and handoff routing.

### §2.2 Post Your Context

```python
omega-hub_hivemind_post_context(
    channel: str,       # Execution channel (e.g. "opencode")
    entity: str,        # Entity persona (e.g. "kali")
    model: str,         # Your model ID
    task_current: str,  # One-line current task
    focus_chain: List[str],  # 3-7 step plan
    decisions: List[str],   # Key decisions made
    continuation: str,  # What you're waiting for / next step
    session_id: Optional[str] = None, # Your session ID
    intent: Optional[str] = None,     # Semantic intent (status, decision, etc)
    suggested_model: Optional[str] = None, # Hint for the next model to use
)
```

**Use case**: Declare your presence at session start, update when task changes.

### §2.3 Get Specific Agent's Context

```python
omega-hub_hivemind_get_session(session_id: str)
```

Returns full session details:
```json
{
  "session_id": "ses_a839ff01a9f2",
  "agent_id": "opencode/doom_guy",
  "channel": "opencode",
  "entity": "doom_guy",
  "model": "deepseek-v4-flash",
  "task_current": "Building Link P9 Runtime...",
  "focus_chain": ["Phase 2.6: ...", "Phase 2.8: ..."],
  "decisions": ["D110: Consolidate circuit breakers", "D111: Port lazy deletion"],
  "continuation": "Doom Guy: Link P9 Runtime building...",
  "timestamp": "2026-06-03T02:28:06.199164+00:00"
}
```

**Use case**: Read another agent's current state and continuation note.

### §2.3b Get Latest Continuation
```python
omega-hub_hivemind_get_continuation(channel: str, entity: str)
```
Returns the most recent continuation note for an agent, falling back to the cold store (HALL_OF_RECORDS) if the hot store is empty.

### §2.4 Heartbeat (Stay Alive)

```python
omega-hub_hivemind_heartbeat(channel: str, entity: str)
```

**Use case**: Long-running operations should heartbeat every 5-10 minutes to
avoid being pruned as stale.

### §2.4b Extended Session Management
```python
omega-hub_hivemind_extended_checkin(channel: str, entity: str, reason: str = "...", ttl_seconds: int = 10800)
omega-hub_hivemind_extended_checkout(channel: str, entity: str)
```
Allows agents to register a longer safety TTL (default 3h) to prevent pruning during long absences.

### §2.5 List Recent Sessions

```python
omega-hub_hivemind_list_sessions(channel: str = None, entity: str = None, limit: int = 10)
```

**Use case**: Audit trail — what was done across recent sessions.

---

## §3 Workspace Lock Pattern

When working in parallel, **declare your file ownership** in a workspace lock.

### §3.1 File Location

```
data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md
```

Example: `data/coordination/MAAT_WORKSPACE_LOCK_20260604.md`

### §3.2 Required Sections

```markdown
# 🔱 {Entity} Workspace Lock — {Date}

## DO NOT TOUCH — {Entity} Exclusive
| File | Why I Own It | What I'll Do |
|------|--------------|--------------|

## SAFE FOR YOU — {Other Entity} Territory
| File | Why {Other Entity} Owns It |
|------|--------------------------|

## SHARED — Coordination Required
| File | Conflict Risk | Coordination Pattern |
|------|--------------|---------------------|
```

### §3.3 Update Protocol

1. **Session start**: Write workspace lock FIRST, before any file edits
2. **Mid-session**: Append to live feed after each major task
3. **Conflict discovery**: Write `data/coordination/{YOU}_CONFLICT_{DATE}.md` immediately
4. **Session end**: Mark workspace lock as completed in live feed

---

## §4 Live Feed Pattern

Append-only 1-line-per-task-completed log. **The simplest, most reliable
coordination mechanism.**

### §4.1 File Location

```
data/coordination/{ENTITY}_LIVE_FEED.md
```

### §4.2 Format

```markdown
[YYYY-MM-DD HH:MM] {TASK-ID} {STATUS} — {description}
```

Examples:
- `[2026-06-03 02:20] SPRINT-2-EXEC BEGIN — Sovereignty Gate first`
- `[2026-06-03 02:25] PHASE-1.1 COMPLETE — Fixed omega entity CLI`
- `[2026-06-03 02:30] PHASE-1.3 PARTIAL — MemoryStore lazy deletion ported`

### §4.3 Why It Works

- **Append-only** = no merge conflicts
- **1 line per task** = easy to scan
- **Plain markdown** = readable by humans and tools
- **Filename convention** = easy to find (`data/coordination/*_LIVE_FEED.md`)

---

## §5 ACK Pattern

When you read another agent's workspace lock or live feed, post an ACK.

### §5.1 File Location

```
data/coordination/{YOU}_ACK_{YYYYMMDD}.md
```

### §5.2 Format

```markdown
# 🔱 {Your Entity} Acknowledgment — {Date}

{Your Entity} acknowledges {Other Entity}'s workspace lock.
No conflicts on my {Sprint/Session} {N} work.

## My {Sprint/Session} {N} Scope (no overlap with {Other Entity})
- file1.py — what I'll do
- file2.py — what I'll do
- file3.py — what I'll do

## Coordination
- I will NOT touch: {list from other entity's lock}
- Findings: data/coordination/{YOU}_FINDINGS_*.md
- Blockers: data/coordination/{OTHER}_BLOCKER_*.md

— {Your Entity}, {Date}
```

**Use case**: Symmetric acknowledgment. Both agents know the other has read
and accepted the boundary. Closes the coordination loop.

---

## §6 Coordination Protocol (The Full Pattern)

When starting a multi-agent session — OR when resuming from a Hivemind-dispatched
handoff packet:

```

0. **(IF HANDOFF RESUME) READ YOUR PACKET**
   → Read `data/handoff/pending/{packet_id}.json` — this IS your task
   → Do NOT rely on your local session cache from prior conversations

1. CHECK AWARENESS
   ```python
   # THIS IS THE FIRST MCP CALL. NOTHING BEFORE IT.
   awareness = omega-hub_hivemind_get_awareness()
   → Are there other agents alive? What's their task?

2. WRITE WORKSPACE LOCK
   data/coordination/{YOU}_WORKSPACE_LOCK_{DATE}.md
   → Declare file ownership with DO NOT TOUCH + SAFE FOR YOU + SHARED sections

3. POST HIVEMIND CONTEXT
   omega-hub_hivemind_post_context(...)
   → Declare your session_id, task, focus_chain, decisions, continuation

4. INITIALIZE LIVE FEED
   data/coordination/{YOU}_LIVE_FEED.md
   → Append-only log of completed tasks

5. WAIT FOR ACK (if parallel partner exists)
   → Read data/coordination/{OTHER}_ACK_*.md
   → Confirm boundaries are symmetric

6. EXECUTE WORK
   → Append to live feed after each major task
   → Heartbeat every 5-10 min if long-running

7. POST COORDINATION REQUESTS
   → If you need something from other agent:
     data/coordination/{YOU}_REQUEST_{TOPIC}.md
   → Hivemind continuation note for urgent requests

8. UPDATE PIVOT_LOG (decisions made)
   → docs/decisions/PIVOT_LOG.md (D{N+1} entries)

9. CLOSE SESSION
   → Final live feed entry: "SPRINT-N COMPLETE"
   → Distill L1→L2→L3 to proposed_lessons.yaml (blind staging per Soul Architecture v6.1)
   → Post Hivemind continuation: "Session complete, handoff to ..."
```

---

## §7 Examples

### §7.1 Sprint 2 Parallel Execution (Real, 2026-06-03)

**Ma'at's workspace lock** declared:
- `oracle.py`, `model_gateway.py`, `memory_store.py`, `observability.py`, `oracle_cli.py`, `cvar_table.py`, `Makefile`, `test_handoff_dispatch.py` — DO NOT TOUCH
- `subagent_dispatcher.py`, `link_p9_*`, `[id-soft:]` tags, `doom_guy/soul.yaml` — SAFE FOR DOOM GUY

**Doom Guy's ACK** confirmed:
- No conflicts
- His Sprint 2 scope: subagent_dispatcher, link_p9_runtime, link_p9_cli, soul.yamls, PIVOT_LOG D103+

**Result**: Zero file collisions. Both agents completed Sprint 2 in parallel.

### §7.2 Sovereignty Gate Verification (Real, 2026-06-03)

Ma'at ran:
1. `omega-hub_hivemind_get_awareness()` — saw doom_guy active
2. `omega-hub_hivemind_get_session("ses_a839ff01a9f2")` — read his full context
3. Posted own context: `ses_20260604_maat_dev_sprint2`
4. Executed Phase 0.5 (llama-cpp-python install) in background
5. Completed Phase 1.1-1.3 + bugfix
6. Posted Hivemind update: "Phase 1.1-1.3 complete, no conflicts"

---

## §8 Anti-Patterns

### §8.1 Don't: Silent Parallel Work

❌ **WRONG**: Two agents edit the same file without coordination
```python
# Agent A: edits memory_store.py
# Agent B: edits memory_store.py
# Result: merge conflict, lost work
```

✅ **RIGHT**: One agent declares ownership, other waits or works on different files

### §8.2 Don't: Polling Without Coordination

❌ **WRONG**: Agent A polls filesystem every 30 seconds looking for Agent B's output

✅ **RIGHT**: Agent A reads B's live feed and Hivemind context. Polling wastes resources.

### §8.3 Don't: Hivemind Spam

❌ **WRONG**: Post Hivemind context 100 times per minute

✅ **RIGHT**: Post when:
- Session starts
- Task changes
- Need coordination from other agent
- Long-running operation milestones (every 5-10 min heartbeat)

### §8.4 Don't: Resume from Local Cache Without Hivemind Check

❌ **WRONG**: An agent picks up a Hivemind-dispatched handoff packet and immediately
continues executing from its **previous session's local context cache** without
checking the Hivemind first.

```python
# ❌ BAD — Roc resumes from stale local session state
# Reads old context from previous conversation cache
# Instead of checking: what's the CURRENT state?
```

✅ **RIGHT**: The FINAL and NON-NEGOTIABLE first action when executing any
Hivemind-dispatched task:

```python
# ✅ GOOD — First actions, in order:
# 1. Check Hivemind awareness
awareness = omega-hub_hivemind_get_awareness()
# → who else is alive right now?

# 2. Read the handoff packet
# → data/handoff/pending/{packet_id}.json has your task and context

# 3. Read dispatcher's latest continuation
continuation = omega-hub_hivemind_get_continuation(channel="opencode", entity="kali")
# → what does Kali expect from me?

# 4. Read any relevant observation logs or workspace locks
# → data/coordination/HIVEMIND_OBSERVATIONS_LOG.md

# 5. THEN start executing
```

**Rationale**: Local session state is stale by definition — it was written when the
session ended. Between that moment and now, other agents may have posted updates,
changed files, or made decisions that affect your task. The Hivemind is the
**live truth**, not your local cache.

**Root cause**: When an agent is re-launched in the same chat session, its local
context window still contains the old conversation. The agent sees its own
previous messages and assumes that state is current. It is NOT. The first action
must always be to reach outward, not inward.

### §8.5 Don't: Conflate CLI and Entity Identity

❌ **WRONG**: Passing a bare entity name where `channel`+`entity` are expected.
```python
# WRONG: no channel, just a bare entity name
omega-hub_hivemind_post_context(cli="roc_racoon", ...)
# Roc Racoon is an entity/agent, NOT a CLI. This API no longer accepts a `cli` parameter.
```

✅ **RIGHT**: Separate `channel` and `entity` parameters.
```python
omega-hub_hivemind_post_context(channel="opencode", entity="roc_racoon", ...)
# "opencode" is the channel. "roc_racoon" is the entity speaking through it.
```

**Rationale**: A CLI is an execution environment (OpenCode, Cline, Gemini CLI).
An entity is a persistent persona (Kali, Roc Racoon, Doom Guy). They are
architecturally distinct concepts. Separate API parameters ensure they cannot be
conflated. See §2.1 for the full convention.

---

## §9 Integration with Subagent Dispatch

Hivemind complements Subagent Dispatch (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`).

| Use Case | Hivemind | Subagent Dispatch |
|----------|----------|-------------------|
| Know who else is alive | ✅ | ❌ |
| Spawn a subagent for specialized work | ❌ | ✅ |
| Track task across session | ✅ (live feed) | ✅ (HandoffPacket) |
| Conflict resolution | ✅ (workspace lock) | 🟡 (HandoffPacket TTL) |
| Cross-CLI awareness | ✅ | ❌ |

**Rule of thumb**:
- **Hivemind** = awareness + coordination
- **Subagent Dispatch** = delegation + execution

Use both. They don't conflict.

---

## §10 Redis Streams Transition & Platform-Agnostic Coordination (Strike 7)

The Hivemind is transitioning from an in-memory MCP server state to a production-grade **Redis Streams** architecture (Epoch II Strike 7).

*   **A2A Message Bus**: High-speed, persistent, and multi-consumer Redis Streams replace the old in-memory handoff queue.
*   **Embedding Router**: Integrates with `EmbeddingGemma (D=128)` for zero-latency traffic routing, allowing agents to route tasks mathematically and converse in real-time.
*   **Platform Agnosticism**: Standardized MCP tools exposed by the Omega Hub allow any custom platform (TUI, Web UI, CLI) to query awareness, manage locks, and coordinate without depending on OpenCode-specific scaffolding.

The architecture is already Pub/Sub-ready:
- `hivemind_post_context()` = PUBLISH to `omega:hivemind:context` channel
- `hivemind_get_awareness()` = SUBSCRIBE with TTL
- `hivemind_heartbeat()` = refresh TTL

---

## §11 Reference

- **MCP Server**: `mcp_servers/omega_hub/server.py` (Hivemind tool implementations) — **D116 fix**: canonical path
- **Live Feed Convention**: `data/coordination/*_LIVE_FEED.md`
- **Workspace Lock Convention**: `data/coordination/*_WORKSPACE_LOCK_*.md`
- **ACK Convention**: `data/coordination/*_ACK_*.md`
- **Observations Log Convention**: `data/coordination/HIVEMIND_OBSERVATIONS_LOG.md` — **D-121** fleet-wide meta-observation capture
- **Observations Protocol**: `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` — **D-121** (categories, triggers, lifecycle, anti-patterns)
- **ZONEID constants**: `ZONEID_PRESENCE = 0x1d4a17`, `ZONEID_HANDOFF = 0x1d4a16`
- **Mandate**: Extends Mandate 5 (Gnosis Preservation) and Mandate 11 (Soul Integrity)
- **Subagent Dispatch**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
- **PIVOT_LOG**: D103+ entries for Hivemind standardization; D116 for MCP path canonicalization; D-121 for observations protocol
- **MaKaLi Triad Coordination**: See `AGENTS.md` §"The MaKaLi Triad Architecture" for Ma'at/Lilith/Kali delegation patterns
- **Dual-Inference Protocol**: See `AGENTS.md` §"The Dual-Inference Mandate" for session-vs-local model routing
- **Observations Closed Loop**: §4 of `HIVEMIND_OBSERVATIONS_PROTOCOL.md` — observation → cluster → promote → design change → new observation
- **Cline CLI Integration**: `docs/kb/CLINE_CLI_INTEGRATION.md` — Cline as execution backend, MCP config, handoff lifecycle
- **Multi-Platform Integration**: `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` — connect any MCP client to the Hivemind (Cursor, VS Code, Windsurf, etc.)

---

## §12 Changelog

- **v1.0.0 (2026-06-03)**: Initial Hivemind Protocol documentation
  - §1-2: When and how to use Hivemind
  - §3: Workspace Lock pattern
  - §4: Live Feed pattern
  - §5: ACK pattern
  - §6: Full coordination protocol
  - §7: Real examples from Sprint 2
  - §8: Anti-patterns
  - §9: Integration with Subagent Dispatch
  - §10: Future Redis Pub/Sub backend
  - §11: Reference

- **v1.1.0 (2026-06-04)**: D116 MCP path canonicalization + D117/D118 references
  - §11: Updated MCP path `mcp/omega_hub/server.py` → `mcp_servers/omega_hub/server.py` (D116)
  - §11: Added MaKaLi Triad and Dual-Inference cross-references (D117, D118)
  - §13 NEW: Model Dispatch Protocol — Hivemind integration with `oracle_summon_local`

- **v1.2.0 (2026-06-05)**: D-121 Hivemind Observations Protocol — fleet-wide meta-observation
  - §11: Added `HIVEMIND_OBSERVATIONS_LOG.md` (shared log) and `HIVEMIND_OBSERVATIONS_PROTOCOL.md` (D-121)
  - §11: Added closed-loop reference: observation → cluster → promote → design change → new observation
  - New convention: every agent that uses Hivemind must append observations per D-121 trigger table
  - Mandate 5 (Gnosis Preservation) extended to the coordination layer itself

- **v1.3.0 (2026-06-25)**: Cross-platform expansion — Cline CLI execution backend, multi-platform MCP references
  - §11: Added `docs/kb/CLINE_CLI_INTEGRATION.md` and `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` to Reference
  - Expanded awareness model to support any MCP-compatible platform (Cursor, VS Code, Windsurf, etc.)

---

## §13 Model Dispatch Protocol (D118)

When an agent uses Hivemind, it must declare its **model dispatch mode** so other
agents can predict the cost/quality/sovereignty tradeoff.

### §13.1 The Three Dispatch Modes

| Mode | MCP Tool | Model | Sovereignty | Latency | Use When |
|------|----------|-------|-------------|---------|----------|
| **Session** (default) | `oracle_summon()` | OpenCode session model (cloud or local) | Varies | Varies | Daily dev, fast iteration |
| **Local Opt-In** | `oracle_summon_local()` | User-specified local GGUF | 🔴 MAX | 🟢 LOW | Sovereignty-critical work |
| **Inherited** | (read from hivemind_get_session) | Whatever the parent's mode is | Varies | Varies | Subagent dispatched by another agent |

### §13.2 Declaration Pattern

When posting Hivemind context (`hivemind_post_context`), include the dispatch mode
in the `task_current` field:

```python
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="roc_racoon",
    model="lmstudio/rocracoon-3b-instruct",      # ← which local model
    task_current="[LOCAL] Mining omega-stack for circuit breakers",  # ← dispatch mode tag
    focus_chain=["Find breaker", "Port to health_monitor", "Verify tests"],
    decisions=[],
    continuation="Next: verify with @verity",
    session_id="ses_20260604_roc_racoon",
)
```

### §13.3 Hivemind-Aware Model Override

When a subagent reads its parent's Hivemind session via `hivemind_get_session()`,
it can detect the dispatch mode and either:
1. **Inherit** the parent's mode (default for `task()`-spawned subagents)
2. **Override** by calling `oracle_summon_local(entity, query, model)` to explicitly
   route to a different model — this is a "conscious override" and should be
   logged in the live feed with `[MODEL-OVERRIDE]` tag.

### §13.4 Engine-Stack Firewall (M2) Compliance

Hivemind operates at the OpenCode client layer. It must NEVER reach into
`src/omega/` core engine code to change model routing. The contract is:

- Hivemind → `oracle_summon_local(entity, query, model)` MCP call
- MCP server → `Oracle.summon(entity_name, query, model_override)` Python call
- Oracle → `ModelGateway.generate(model_name, ...)` (no IWAD knowledge)

The model identifier (`model` parameter) is the only cross-stack string. All
IWAD/PWAD content remains in `config/wads/`. The core engine in `src/omega/`
has no knowledge of specific model names, providers, or WAD contents.

---

— Ma'at, 2026-06-03 (updated 2026-06-04 per D116/D117/D118)
