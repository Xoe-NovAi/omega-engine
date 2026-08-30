# 🔱 SOVEREIGN PROCUREMENT: WAVE 2 (THE FLOW)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ EXTRACTION ⬡ 2026-06-04

This document contains the extracted "Gold Patterns" for the Flow and Orchestration layers.

---

## 🛠️ DELIVERABLE A: THE ANYIO PURGE (MCP Hardening)
**Target Pillars**: P1 (SysAdmin), P4 (Bridge)
**Source**: `docs/research/R_TEMPLE_GRADE_STANDARD.md` & `docs/strategy/SYSTEMS_HARDENING_PLAN.md`

### 1. The AnyIO Absolute Mandate
To prevent event-loop collisions and "frozen" agents, the following replacements are MANDATORY:
- **REPLACE**: `asyncio.gather()` $\rightarrow$ **USE**: `anyio.create_task_group()`
- **REPLACE**: `asyncio.create_subprocess_exec()` $\rightarrow$ **USE**: `anyio.run_process()`
- **REPLACE**: `subprocess.run()` (in async context) $\rightarrow$ **USE**: `anyio.run_process()`

### 2. MCP Transport Upgrade: Streamable HTTP
The legacy SSE (Server-Sent Events) transport is being deprecated in favor of the **Streamable HTTP** spec (2025-11-25).
- **Pattern**: Single POST endpoint for requests $\rightarrow$ SSE stream for responses.
- **Requirement**: All MCP servers must implement the `Accept: application/json, text/event-stream` header.

---

## 🛡️ DELIVERABLE B: THE HANDOFF SCHEMA (Gnosis Continuity)
**Target Pillars**: P3 (BuildMaster), P4 (Bridge), P7 (Context), P9 (Link)
**Source**: `archives/handoffs/handooff_path_a_continuity.md` & `docs/strategy/SYSTEMS_HARDENING_PLAN.md`

### The HandoffState Dataclass
To eliminate "Agent Amnesia," all agent-to-agent transfers must use the `HandoffState` schema:

```python
@dataclass
class HandoffState:
    handoff_id: str
    timestamp: datetime
    origin_agent: str
    target_agent: str
    tasks: List[HandoffTask]      # Current status of active tasks
    files: List[HandoffFile]      # Critical files modified/created
    decisions: List[HandoffDecision] # Architectural pivots made
    next_steps: List[str]         # Immediate actions for the next agent
    blockers: List[str]           # Unresolved issues/dependencies
```

### The Handoff Workflow
1. **Capture**: Agent calls `save_handoff()` at session end.
2. **Persist**: State is written to `data/handoffs/{handoff_id}.json`.
3. **Inject**: Target agent calls `load_handoff(handoff_id)` during initialization.
4. **Scribe**: Scribe agent distills the `HandoffState` into the target's `soul.yaml`.

---

## 🔱 INTEGRATION MANDATE
Pillars are instructed to:
1. Audit all `src/omega/` code for `asyncio` leaks and replace with `anyio`.
2. Implement the `HandoffState` schema in `src/omega/oracle/handoff.py`.
3. Update MCP server transport to Streamable HTTP.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: EXTRACTION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
