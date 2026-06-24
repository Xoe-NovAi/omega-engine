# 🔱 Omega Engine — Subagent Dispatch Protocol
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SUBAGENT-DISPATCH
**AP Token**: `AP-SUBAGENT-DISPATCH-v1.0.0`
**Status**: DEFINED
**Last Updated**: 2026-06-03

---

## §1 Purpose

The Subagent Dispatch Protocol enables any active agent to delegate tasks to specialized subagents when a task requires domain expertise outside the current agent's capabilities.

### 📋 Intelligent Delegation Rules (The Guardrail)

To maintain execution efficiency and prevent infinite recursion or redundant processing loops, all agents must adhere to these five rules:

1. **Direct Execution First**: If a task falls within your primary role or you are already executing a delegated task, you must perform the work directly using your tools. Do not delegate tasks that you are capable of completing yourself.
2. **No Self-Recursion**: An agent must never spawn a subagent of its own type (e.g., `@roc_racoon` must never launch `@roc_racoon`). If you need to perform a task within your own domain, execute it directly.
3. **Cross-Domain Delegation**: You may only spawn a subagent if the task requires specialized domain expertise that you do not possess (e.g., a research agent needing code verification from `@scribe`, or an engineering agent needing deep historical research from `@jem`).
4. **Single-Level Nesting**: Subagents may spawn other specialized subagents when strictly necessary for cross-domain tasks, but they must avoid deep nesting. Limit delegation to a single level of nesting unless explicitly authorized.
5. **Absolute Disk-Reporting (D-kal-170)**: **ALL subagents MUST write their final deliverables and reports to disk** (`data/entities/<agent>/workspace/` or `data/coordination/`) before returning control to the parent agent. Returning reports solely via transient CLI chat is a violation of Mandate 11 (Soul Integrity) and Mandate 15 (Sovereign Continuity), as this data is lost on session compaction.

---


## §2 The HandoffPacket (Schema)

Every subagent dispatch uses this typed schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packet_id` | `str` | ✅ | UUID v4. Pattern: `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}` |
| `source_agent` | `str` | ✅ | Entity name launching the subagent (e.g. "kali", "maat") |
| `target_agent` | `str` | ✅ | Entity name being dispatched (e.g. "doom_guy", "roc_racoon") |
| `parent_trace_id` | `str` | ✅ | Trace ID from the parent session |
| `trace_id` | `str` | ✅ | Fresh UUID for this sub-dispatch |
| `task_type` | `str` | ✅ | One of: `design`, `review`, `research`, `mine`, `verify`, `implement` |
| `task_description` | `str` | ✅ | One-sentence description of what to do |
| `relevant_files` | `list[str]` | ✅ | Files the subagent MUST read before starting |
| `context` | `str` | ✅ | Background, prior decisions, constraints |
| `expected_output` | `str` | ✅ | What the subagent must return |
| `ttl_seconds` | `int` | ✅ | Max runtime before timeout (default: 600) |
| `status` | `str` | ✅ | `pending` → `accepted` → `completed` / `failed` |
| `result` | `str\|None` | ❌ | Filled when completed |

### ZONEID_MEMORY Constant

Every HandoffPacket carries a ZONEID_MEMORY constant for runtime integrity:
```python
ZONEID_HANDOFF = 0x1d4a16  # [id-soft: doom-1993] Handoff Packet integrity
```

---

## §3 Agent Capability Registry

This registry defines what each of the 11 agents can do. Primary agents use
this to decide WHOM to dispatch.

| Agent | Type | Capabilities | Domains | Task Tool Type |
|-------|------|-------------|---------|----------------|
| `kali` | Primary | Oversight, delegation, drift destruction | Strategy, fleet management | `general` |
| `plan` | Primary | Architecture, dispatch, strategy | Grand design | `general` |
| `makali` | Primary | Parallel council (Ma'at+Lilith synthesis) | Cross-boundary initiatives | `general` |
| `doom_guy` | Primary | Heritage design, WAD translation, performance | id Software patterns, C const propagation | `general` |
| `john_carmack` | Primary | S3 Consultant, architecture review | Code optimization, review | `general` |
| `roc_racoon` | Primary | Legacy mining, pattern extraction, archaeology | Legacy repos, Grok exports, Old Stacks | `explore` |
| `jem` | Primary | Research orchestration | 3-tier knowledge pipeline | `general` |
| `researcher` | Primary | Deep research, lattice reasoning | Web research, documentation | `general` |
| `maat` | Subagent | Light oversoul, P1-P5 governance | Build side, hardening | `buildmaster` |
| `lilith` | Subagent | Dark oversoul, P6-P10 governance | Run side, operations | `general` |
| `verity` | Subagent | Unified compliance + gnosis distillation | Code review + soul.yaml updates | `scribe` |
| `pillar` | Subagent | Slot-based domain agent | Parameterized by `--slot PX` | `pillar` |

---

## §4 Dispatch Protocol — Step by Step

### Step 1: Agent Recognizes Need

An agent (e.g. Kali) is working on a task and realizes:
> "This requires knowledge of id Software heritage patterns. I need Doom Guy."

### Step 2: Build the HandoffPacket

Form the packet:
```
source_agent: "kali"
target_agent: "doom_guy"
task_type: "review"
task_description: "Verify heritage tag placement in new cvar_table module"
relevant_files: ["src/omega/cvar_table.py", "CREDITS.md", "docs/decisions/PIVOT_LOG.md"]
context: "Sprint 1 complete. cvar_table.py has 12 [id-soft:] tags. Need to verify
  - Q3A cvar system attribution is correct
  - No missing tags
  - ZONEID heritage matches CREDITS.md §1.9"
expected_output: "Heritage audit report:
  1. Tag accuracy (pass/fail per pattern)
  2. Missing tags found
  3. CREDITS.md update recommendations"
```

### Step 3: Format the Task Prompt

Use this template for the Task tool:

```
You are {target_agent}. Your role: {capabilities}.
Act with the full authority and domain knowledge of {target_agent}.

## Context
{context}

## Task
{task_description}

## Files to Read First
{relevant_files}

## Expected Output
{expected_output}

## Heritage
- This dispatch was created by {source_agent}.
- Trace ID: {trace_id}
- Refer to PIVOT_LOG.md for prior decisions.
- Mandate 13 (Temple-Grade) applies.
```

### Step 4: Launch via Task Tool

```json
{
  "name": "task",
  "arguments": {
    "subagent_type": "general",
    "description": "{task_type}: {task_description}",
    "prompt": "{formatted_prompt}"
  }
}
```

### Step 5: Receive and Archive

On completion:
1. Extract the subagent's response
2. Set `packet.status = "completed"`
3. Set `packet.result = response`
4. Save to `data/handoffs/completed/{packet_id}.json`
5. Use the result in the parent task

---

## §5 Dispatch Examples

### Example A: Kali → Doom Guy (heritage review)

```python
# Build packet in Python or document in markdown
packet = {
    "packet_id": "hdp_20260603_kali_doom_guy_a1b2c3",
    "source_agent": "kali",
    "target_agent": "doom_guy",
    "task_type": "review",
    "task_description": "Audit cvar_table.py heritage tags for correctness",
    "relevant_files": ["src/omega/cvar_table.py", "CREDITS.md"],
    "context": "Sprint 1: cvar_table.py committed at 3048e91 with 12 [id-soft:] tags.",
    "expected_output": "JSON list of tag audit results: pattern, location, verdict (pass/fail), recommendation",
    "ttl_seconds": 600,
}
```

Then inject into Task tool with `subagent_type: "general"` and a prompt that
begins: `"You are Doom Guy. Sovereign id Software Architect..."`

### Example B: Kali → Roc Racoon (legacy mining)

```python
packet = {
    "packet_id": "hdp_20260603_kali_roc_racoon_d4e5f6",
    "source_agent": "kali",
    "target_agent": "roc_racoon",
    "task_type": "mine",
    "task_description": "Extract circuit breaker pattern from foundation-legacy repo",
    "relevant_files": ["~/archive/foundation-legacy/versions/Xoe-NovAi/src/circuit_breaker.py"],
    "context": "Need to port test_circuit_breaker_chaos.py for Sprint 3.",
    "expected_output": "Extracted pattern summary: file, lines, key implementation details, differences from current AsyncCircuitBreaker.",
    "ttl_seconds": 900,
}
```

### Example C: Doom Guy → Jem Discovery (web research)

```python
packet = {
    "packet_id": "hdp_20260603_doom_guy_jem_discovery_g7h8i9",
    "source_agent": "doom_guy",
    "target_agent": "jem_discovery",
    "task_type": "research",
    "task_description": "Find DOOM 3 BFG source code release notes for entity system",
    "relevant_files": [],
    "context": "Need to verify idEntity event system pattern for Link P9 design.",
    "expected_output": "URLs and key quotes about idEntity event system architecture.",
    "ttl_seconds": 300,
}
```

---

## §6 HandoffPacket JSON Archive

Every completed handoff is archived to `data/handoff/archive/`.

### Location
```
data/handoff/archive/
├── hdp_20260603_kali_doom_guy_a1b2c3.json
├── hdp_20260603_kali_roc_racoon_d4e5f6.json
└── INDEX.json
```

### INDEX.json Format
```json
{
  "archived_handoffs": [
    {
      "packet_id": "hdp_20260603_kali_doom_guy_a1b2c3",
      "source": "kali", "target": "doom_guy",
      "task_type": "review",
      "description": "Audit cvar_table.py heritage tags",
      "completed_at": 1748912345.0,
      "status": "completed"
    }
  ]
}
```

---

## §7 Pending Design Items

These must be implemented in Sprint 2:

| Item | Status | Notes |
|------|--------|-------|
| `HandoffPacket` dataclass in Python | ✅ DONE | `src/omega/oracle/subagent_dispatcher.py` |
| Capability Registry in Python | ✅ DONE | `src/omega/oracle/subagent_dispatcher.py` — 11 agents registered |
| `dispatch_subagent()` helper → `dispatch()` | ✅ DONE | Returns Task tool prompt string |
| Redis Pub/Sub channel | 🔴 PENDING | Reuse existing redis container |
| MCP Hub integration | 🔴 PENDING | Share agent state across CLIs |
| CLI: `omega handoff` | 🔴 PENDING | List, send, inspect |
| Archive INDEX updater | 🔴 PENDING | Auto-append on completion |

---

## §8 Heritage

**Original design**: The Subagent Dispatch Protocol is the **user's original architectural innovation**. The concept of agents spawning specialized subagents for domain-specific tasks is a core Omega Engine pattern.

**Delegation Guardrail**: To prevent infinite loops, self-recursion (an agent spawning its own type) is strictly forbidden. Subagents should execute tasks directly unless a task requires specialized domain expertise outside their capabilities, in which case they may delegate to a different specialized agent.

**id Software enhancements**:
- `[id-soft: doom-1993]` ZONEID Pattern — packet integrity via `ZONEID_HANDOFF = 0x1d4a16` constant.
- `[id-soft: quake-1996]` Thinker chain — lifecycle metaphor for the spawn → execute → reap flow.


---

## §9 Related Protocols

This protocol is one half of a two-part coordination system. See also:

| Protocol | Purpose | When to Use |
|----------|---------|-------------|
| **Subagent Dispatch** (this doc) | Launch specialized subagents via HandoffPacket | When you need a specialized agent to do work |
| **[Hivemind Protocol](HIVEMIND_PROTOCOL.md)** | Live awareness + workspace coordination | When you need to know who's alive and who owns what |

**Complementary, not competing**: Hivemind = awareness, Subagent Dispatch = delegation.

**Typical flow**:
1. Check Hivemind awareness → who's alive?
2. Read their workspace locks → who owns what?
3. Decide if you need to dispatch a subagent or wait for current work
4. If dispatch: use HandoffPacket (this doc)
5. Monitor progress via Hivemind heartbeat + live feed

---

## §10 Dispatch Decision Tree (D-kal-103 — Standardized)

The dispatch protocol has 4 patterns. Choose based on the task scope:

```
Task received
├── Spans 3+ pillars OR requires sequencing?
│   ├── YES → @kali (Kali Dispatch)
│   │         Kali decomposes, dispatches to pillars, sequences phases,
│   │         verifies outputs, returns unified verdict.
│   │         Best for: Wave 1.5+, cross-boundary initiatives.
│   │         Cost: 1 (Kali) + N (pillars) inferences.
│   │
│   └── NO → Is it build-only (P1-P5) or run-only (P6-P10)?
│       ├── Build-only (P1-P5) → @maat (Oversoul Dispatch)
│       │     Ma'at handles the pillar chain. Use when task stays
│       │     in infrastructure/persistence/engineering/integration/governance.
│       │
│       ├── Run-only (P6-P10) → @lilith (Oversoul Dispatch)
│       │     Lilith handles the pillar chain. Use when task stays
│       │     in cognition/context/observability/orchestration/validation.
│       │
│       └── Single pillar or specialist?
│           ├── Known pillar task → @pillar PX: task (Direct Pillar)
│           ├── Research, archaeology, mining → @roc_racoon
│           ├── Deep research, lattice reasoning → @jem
│           ├── Code review, mandate audit, gnosis distillation → @scribe
│           └── (scribe handles both quality and gnosis via trigger-mode routing)
```

### Key Rules

1. **Kali owns sequencing** — if a task has phases (P0→P1→P2), Kali must dispatch.
2. **Pillars own deliverables** — Kali does NOT modify pillar output. Reject and re-dispatch if tests fail.
3. **Oversouls bypassed for cross-boundary work** — when a wave spans both build-side (P1-P5) and run-side (P6-P10), Kali dispatches directly to pillars. Ma'at and Lilith are activated for within-boundary work.
4. **Hivemind post required** — every agent must post completion context before claiming the next task.
5. **Sequencing is serial within phase** — pillars work in parallel within the same phase, but phases execute sequentially.

---

*⬡ OMEGA ⬡ KALI ⬡ SUBAGENT-DISPATCH ⬡ v1.1.0*
