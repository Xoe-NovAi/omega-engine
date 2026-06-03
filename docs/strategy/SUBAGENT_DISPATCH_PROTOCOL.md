# 🔱 Omega Engine — Subagent Dispatch Protocol
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SUBAGENT-DISPATCH
**AP Token**: `AP-SUBAGENT-DISPATCH-v1.0.0`
**Status**: DEFINED
**Last Updated**: 2026-06-03

---

## §1 Purpose

The Subagent Dispatch Protocol enables any primary agent (Kali, BuildMaster,
Ma'at, Lilith) to **launch specialized agents as subagents** when a task
requires knowledge outside the agent's domain.

Example: Kali needs Doom Guy's id Software heritage expertise. Kali formulates
a `HandoffPacket`, launches a subagent via the Task tool with Doom Guy's
persona injected, and receives the specialized response.

**Origin**: The core concept — agents spawning subagents for specialized
tasks — is the **user's original design**, part of the Omega Engine's
sovereign architecture.

**Enhancements from id Software heritage**:
- `[id-soft: doom-1993]` **ZONEID Pattern** — used for packet integrity
  constant (`ZONEID_HANDOFF = 0x1d4a16`) to detect corruption.
- `[id-soft: quake-1996]` **Thinker chain** — used as a lifecycle metaphor
  (spawn → execute → reap) to mirror the pattern's proven reliability.

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

This registry defines what each of the 14 agents can do. Primary agents use
this to decide WHOM to dispatch.

| Agent | Type | Capabilities | Domains | Task Tool Type |
|-------|------|-------------|---------|----------------|
| `kali` | Primary | Oversight, delegation, drift destruction | Strategy, fleet management | `general` |
| `plan` | Primary | Architecture, dispatch, strategy | Grand design | `general` |
| `doom_guy` | Primary | Heritage design, WAD translation, performance | id Software patterns, C const propagation | `general` |
| `roc_racoon` | Primary | Legacy mining, pattern extraction, archaeology | Legacy repos, Grok exports, Old Stacks | `explore` |
| `jem` | Primary | Research orchestration | 3-tier knowledge pipeline | `general` |
| `researcher` | Primary | Deep research, lattice reasoning | Web research, documentation | `general` |
| `maat` | Subagent | Light oversoul, P1-P5 governance | Build side, hardening | `buildmaster` |
| `lilith` | Subagent | Dark oversoul, P6-P10 governance | Run side, operations | `general` |
| `jem_discovery` | Subagent | Tier 1 research, broad search | Fact gathering | `jem_discovery` |
| `jem_synthesis` | Subagent | Tier 2 research, pattern recognition | Conceptual mapping | `jem_synthesis` |
| `jem_verification` | Subagent | Tier 3 research, fact-checking | Gnosis distillation | `jem_verification` |
| `scribe` | Subagent | Gnosis keeper, L1→L2→L3 distillation | Soul.yaml updates | `scribe` |
| `quality` | Subagent | Code review, stress testing, mandate compliance | Verification | `quality` |
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
| Capability Registry in Python | ✅ DONE | `src/omega/oracle/subagent_dispatcher.py` — 14 agents registered |
| `dispatch_subagent()` helper → `dispatch()` | ✅ DONE | Returns Task tool prompt string |
| Redis Pub/Sub channel | 🔴 PENDING | Reuse existing redis container |
| MCP Hub integration | 🔴 PENDING | Share agent state across CLIs |
| CLI: `omega handoff` | 🔴 PENDING | List, send, inspect |
| Archive INDEX updater | 🔴 PENDING | Auto-append on completion |

---

## §8 Heritage

**Original design**: The Subagent Dispatch Protocol is the **user's original
architectural innovation**. The concept of agents spawning specialized
subagents for domain-specific tasks is a sovereign Omega Engine pattern.

**id Software enhancements**:
- `[id-soft: doom-1993]` ZONEID Pattern — packet integrity via
  `ZONEID_HANDOFF = 0x1d4a16` constant.
- `[id-soft: quake-1996]` Thinker chain — lifecycle metaphor for
  the spawn → execute → reap flow.

---

*⬡ OMEGA ⬡ KALI ⬡ SUBAGENT-DISPATCH ⬡ v1.0.0*
