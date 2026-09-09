# 🔱 Omega Engine — Subagent Dispatch Protocol
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SUBAGENT-DISPATCH
**AP Token**: `AP-SUBAGENT-DISPATCH-v2.0.0`
**Status**: DEFINED
**Last Updated**: 2026-07-12

---

## §0 Critical Lesson: Inline Context Is the Difference Between Empty Results and Temple-Grade Work

**Observation from 2026-07-12 Jenm Deep Research Dispatch**

Three identical dispatch attempts to the same subagent (`jem`) for the same task:

| Attempt | Context Delivery Method | Task Result | Output Quality |
|---------|------------------------|-------------|----------------|
| 1 (failed) | All files referenced by path — "see `docs/research/R_*.md`" | **Empty result** (task completed with no output) | ❌ Failure |
| 2 (failed) | Same as attempt 1 | **Empty result** (task cancelled) | ❌ Failure |
| 3 (successful) | All 6 source documents read and **embedded inline** in the prompt text | **544-line report**, 12 tool calls, Exa/Firecrawl Tier 3/4, 11 L3 proposals | ✅ Temple-Grade |

**The pattern is clear**: Subagents cannot reliably read files by path during their first tool calls. The `relevant_files` field in the HandoffPacket is frequently ignored or fails silently. The ONLY reliable way to deliver context to a subagent is to **embed the actual content inline in the prompt text**.

**This is now a mandatory practice**: Before dispatching any subagent, the parent MUST read all critical source files and embed their relevant content directly in the prompt. File paths are supplementary — they provide reference for locating the document later, but the content itself must be in the prompt.

**Exceptions**:
- Very large files (>500 lines) — summarize the key findings inline, provide the path for reference
- Binary files (images, models) — cannot be inlined, use paths
- Files the subagent MUST modify — provide both inline understanding and the path for edits

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

## §1.5 Session Type Taxonomy (EIS / NES / SPT)

**Ratified 2026-08-29** by Architect. All sessions MUST be classified by type:

| Acronym | Full Name | Characteristics | Dispatch Method |
|---------|-----------|-----------------|-----------------|
| **EIS** | Expert Interactive Session | Resumable, Architect can steer, persistent context, long-running | `task` tool with existing `task_id` (session ID) |
| **NES** | Non-interactive Expert Session | Autonomous, runs to completion, delivers report, no Architect dialog | `task` tool without `task_id` (expert page) |
| **SPT** | Spawned (subagent) Task | One-shot, fresh context, not resumable, throwaway | `task` tool without `task_id` (fresh spawn) |

**Examples**:
- **EIS**: Roc-EIS (`ses_ff78b71ebffeDNuypPTT1RL3hH`), Researcher-EIS (`ses_fd81c19dcffe1nkbPqFg5kRt2v`), Kali-EIS (`ses_fdef2be4effe4pAaLXCTUx62GO`)
- **NES**: A research task that runs autonomously and delivers a 60KB report
- **SPT**: "Read this file and tell me its contents" — fresh, one-shot, throwaway

**Token Savings**: ~900 tokens/week across 50 uses (trivial in absolute terms)
**Real-World Benefits**: Cognitive precision, protocol enforcement, registry queries, handoff clarity, tool integration, onboarding, audit trail, single vocabulary

**Paging vs Handoff vs Spawn** (clarification, 2026-08-29):
- **Paging** = `task` tool with `task_id` set to an existing session ID → resumes that session
- **Handoff** = file posted to `data/handoff/pending/` → target agent picks up on own initiative
- **Spawn** = `task` tool without `task_id` → launches a fresh new session

These three terms are NOT interchangeable. Use them precisely.

---


## §2 The HandoffPacket (Schema)

Every subagent dispatch uses this typed schema:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `packet_id` | `str` | ✅ | — | UUID v4. Pattern: `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}` |
| `source_agent` | `str` | ✅ | — | Entity name launching the subagent (e.g. "kali", "maat") |
| `target_agent` | `str` | ✅ | — | Entity name being dispatched (e.g. "doom_guy", "roc_racoon") |
| `parent_trace_id` | `str` | ✅ | — | Trace ID from the parent session |
| `trace_id` | `str` | ✅ | — | Fresh UUID for this sub-dispatch |
| `task_type` | `str` | ✅ | — | One of: `design`, `review`, `research`, `mine`, `verify`, `implement` |
| `task_description` | `str` | ✅ | — | One-sentence description of what to do |
| `context_delivery` | `str` | ✅ | `inline` | **`inline`** (context embedded in prompt) or **`reference`** (context via file paths). Default is `inline`. See §0 for critical lesson. |
| `relevant_files` | `list[str]` | ✅ | — | Files for supplementary reference. Content MUST also be summarized inline. |
| `context` | `str` | ✅ | — | **Inline context**: Actual file excerpts, key findings, prior decisions, code patterns. DO NOT write "see file X" — embed the content. |
| `expected_output` | `str` | ✅ | — | What the subagent must produce and write to disk |
| `ttl_seconds` | `int` | ✅ | 14400 | Max runtime before timeout. 4h default (PENDING_TTL). |
| `resolver_strategy` | `str` | ❌ | `"escalate"` | One of: `terminate`, `escalate`, `fallback`, `retry`. Default `escalate` — on failure, escalate to Kali. |
| `resolved_by` | `str\|None` | ❌ | — | Entity name that resolved the packet (e.g. "kali" on escalation). |
| `status` | `str` | ✅ | `pending` | Lifecycle: `pending` → `active` → `completed` / `stale`. Aligned with MCP handoff directory model. |
| `result` | `str\|None` | ❌ | — | Filled when completed |

### Mandatory Context Inlining Rule (NEW — 2026-07-12)

**Any context that is essential for the subagent's task MUST be embedded directly in the prompt text.** File paths in `relevant_files` are supplementary references, NOT the primary delivery mechanism.

**The pattern that works**:
1. Read all critical files yourself first
2. Extract the key findings, decisions, code patterns, and config schemas
3. Embed them directly in the prompt under a clear section like `## Inline Context`
4. Include file paths as references so the subagent can find the source if needed

**The pattern that fails**:
```
❌ WRONG: "See docs/research/R_FOO.md for context"
✅ RIGHT: Below is the full context from docs/research/R_FOO.md (644 lines):
           [inline excerpts of key findings]
```

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
| `maat` | Primary | Build Oversight (N1-N5) | Build side, hardening | `general` |
| `lilith` | Primary | Run Oversight (N6-N10) | Run side, operations | `general` |
| `makali` | Primary | Parallel council (Ma'at+Lilith synthesis) | Cross-boundary initiatives | `general` |
| `doom_guy` | Primary | Heritage design, WAD translation, performance | id Software patterns, C const propagation | `general` |
| `john_carmack` | Primary | S3 Consultant, architecture review | Code optimization, review | `general` |
| `roc_racoon` | Primary | Legacy mining, pattern extraction, archaeology | Legacy repos, Grok exports, Old Stacks | `explore` |
| `jem` | Primary | Research orchestration | 3-tier knowledge pipeline | `general` |
| `researcher` | Primary | Deep research, lattice reasoning | Web research, documentation | `general` |
| `verity` | Primary | Unified compliance + gnosis distillation | Code review + soul.yaml updates | `scribe` |
| `pillar` | Subagent | Slot-based domain agent | Parameterized by `--slot PX` | `pillar` |

---

## §4 Dispatch Protocol — Step by Step

### Step 1: Agent Recognizes Need

An agent (e.g. Ma'at) is working on a task and realizes:
> "This requires knowledge of id Software heritage patterns. I need Doom Guy."

### Step 2: Build the HandoffPacket

Form the packet:
```
source_agent: "maat"
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

Use this template for the Task tool. **CRITICAL: All essential context must be inlined, not referenced by path.**

```
# 🔱 {target_agent} — Dispatch from {source_agent}
**AP Token**: `AP-{source_agent}-DISPATCH-{packet_id}`
⬡ OMEGA ⬡ {target_agent} ⬡ {model_hint} ⬡ opencode ⬡ trc_{task_type} ⬡ ACTIVE

---

## 📥 Context Delivery: INLINE

All essential context is embedded below. File paths in `## Reference Files` are
supplementary — you do NOT need to read them unless the inline excerpts are
insufficient.

---

## 📚 INLINE CONTEXT

{context — containing ACTUAL FILE EXCERPTS, not file paths}

Example good format:
```
### Source: docs/research/R_FOO.md (lines 45-120)

Key finding: [verbatim quote or concise summary]

Decision D-142: Chose X over Y because [reason].

Config schema for implementation:
```yaml
field: value
```
```

---

## 🎯 Task

{task_description}

---

## 📄 Reference Files (Supplementary — not required to read)

{relevant_files — paths only, context already inlined above}

---

## 📝 Expected Output

{expected_output}

**Mandate**: Write output to disk at `{output_path}` before returning control.

---

## ⚖️ Heritage & Constraints

- This dispatch was created by {source_agent}.
- Trace ID: {trace_id}
- Refer to PIVOT_LOG.md for prior decisions.
- Mandate 13 (Temple-Grade) applies.
- Mandate 11 (Soul Integrity): End with L1→L2→L3 distillation.
- Mandate 18 (Token Efficiency): Every search/tool call must have a purpose.
```

**Inline Context Quality Checklist** (run before dispatch):
- [ ] Every critical file was read and its key findings extracted
- [ ] No prompt says "see file" without summarizing the content
- [ ] Decision IDs (D-NNN) are stated explicitly, not referenced
- [ ] Code/config patterns are shown as inline examples, not file paths
- [ ] If research: the specific gaps/hypotheses to validate are listed
- [ ] If implementation: the exact files to modify and patterns to follow

**M27 Pre-Flight Check (mandatory before ANY dispatch):**
- [ ] Read `data/coordination/HMC_COLLABORATION_HUB.md` `NEXT_ACTION` — confirm this dispatch maps to a Tier-0 task in `ACTIVE_SPRINT.json`
- [ ] If research dispatch references a gap (R-XX): **verify the Gap ID exists in `data/coordination/GAP_REGISTRY.json`** — never assign or reuse a gap number not in the registry
- [ ] Include the Tier-0 task ID as the `task_id` prefix per STRP Rule 2 (e.g., `QW-2-context-gauge-review-20260814`)

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
    "ttl_seconds": 14400,
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

## §8 Refinement Protocol: Subagent Failure Recovery (NEW — 2026-07-12)

### Pattern: "Empty Task Result"

When a subagent task returns `state: "completed"` but the result is empty:

1. **Do NOT immediately relaunch** — first diagnose the root cause
2. **Check the most likely root causes**:
   - ❌ **Primary cause (80%)**: Context delivered as file references, not inline content
   - ❌ **Secondary cause (15%)**: Prompt too vague, no specific hypotheses to test
   - ❌ **Tertiary cause (5%)**: Tool failure (Exa, Firecrawl, websearch unavailable)
3. **Fix the context delivery** — read the files yourself and inline the content
4. **Retry with the inlined context** — do NOT change the subagent type or task scope

### Pattern: "Partial or Low-Quality Result"

When a subagent returns output but misses key requirements:

1. **Identify what was missed** — specific field, search, or constraint
2. **Rel launch with explicit gap closure**: "You did X correctly. You did NOT do Y. Complete Y."
3. **Use the same task_id** to continue the session (preserves prior context)

### Pattern: "Tool-Chain Collapse" (M23)

When a subagent reports `[TOOL-CHAIN-COLLAPSE]`:

1. **Accept the hard stop**. Do NOT ask them to retry with fallback tools.
2. **Log the failure** to `data/coordination/SYSTEM_FAILURE_LOG.md`
3. **Try the task yourself** using available tools
4. **If also blocked**: re-queue the task for a session with functional toolchain

---

## §8a Experience Table: Context Delivery Patterns

The following table documents real dispatches and their outcomes. Use it to predict which context delivery method will succeed for your next dispatch.

| Date | Source | Target | Context Delivery | Task Type | Result | Lines Output | Root Cause |
|------|--------|--------|-----------------|-----------|--------|-------------|------------|
| 2026-07-12 | Kali | Jem | **Reference only**: "see docs/research/R_*.md" | Deep research (5 gaps) | ❌ Empty task result | 0 | Subagent couldn't read files by path |
| 2026-07-12 | Kali | Jem | **Reference only**: "see files at paths" | Deep research (5 gaps) | ❌ Task cancelled | 0 | Same — repeated the same pattern |
| 2026-07-12 | Kali | Jem | **Inline**: All 6 source docs embedded in prompt text | Deep research (5 gaps) | ✅ Temple-Grade | 544 + 11 L3 proposals | Inline content enabled proper tool use |

### How This Translates to Your Next Dispatch

| Your Context Size | Recommended Delivery | Why |
|-------------------|---------------------|-----|
| < 1000 lines | **Full inline** — embed everything | Subagent has full context immediately |
| 1000-3000 lines | **Inline excerpts + file paths** — summarize key findings, provide paths for nuance | Balance: critical context inline, depth available on request |
| > 3000 lines | **Inline executive summary + strategic excerpts** — subagent reads specific sections if needed | Full inline would exceed prompt limits |
| Binary/non-text | **File reference only** — subagent uses tool to read | Cannot be inlined |

---

## §9 Heritage

**Original design**: The Subagent Dispatch Protocol is the **user's original architectural innovation**. The concept of agents spawning specialized subagents for domain-specific tasks is a core Omega Engine pattern.

**Delegation Guardrail**: To prevent infinite loops, self-recursion (an agent spawning its own type) is strictly forbidden. Subagents should execute tasks directly unless a task requires specialized domain expertise outside their capabilities, in which case they may delegate to a different specialized agent.

**id Software enhancements**:
- `[id-soft: doom-1993]` ZONEID Pattern — packet integrity via `ZONEID_HANDOFF = 0x1d4a16` constant.
- `[id-soft: quake-1996]` Thinker chain — lifecycle metaphor for the spawn → execute → reap flow.

---

## §10 Related Protocols

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

## §11 Dispatch Decision Tree (D-kal-103 — Standardized)

The dispatch protocol has 4 patterns. Choose based on the task scope:

```
Task received
├── Spans 3+ pillars OR requires sequencing?
│   ├── YES → @kali (Kali Dispatch)
│   │         Kali decomposes, dispatches to pillars, sequences phases,
│   │         verifies outputs, returns unified verdict.
│   │         Best for: Wave 1.5+, cross-boundary initiatives.
│   │         Cost: 1 (Kali) + N (nodes) inferences.
│   │
│   └── NO → Is it build-only (N1-N5) or run-only (N6-N10)?
│       ├── Build-only (N1-N5) → @maat (Build Oversight Dispatch)
│       │     Ma'at handles the node chain. Use when task stays
│       │     in infrastructure/persistence/engineering/integration/governance.
│       │
│       ├── Run-only (P6-P10) → @lilith (Oversoul Dispatch)
│       │     Lilith handles the pillar chain. Use when task stays
│       │     in cognition/context/observability/orchestration/validation.
│       │
│       └── Single node or specialist?
│           ├── Known node task → @node NX: task (Direct Node)
│           ├── Research, archaeology, mining → @roc_racoon
│           ├── Deep research, lattice reasoning → @jem
│           ├── Code review, mandate audit, gnosis distillation → @scribe
│           └── (scribe handles both quality and gnosis via trigger-mode routing)
```

### Key Rules

1. **Kali owns sequencing** — if a task has phases (P0→P1→P2), Kali must dispatch.
2. **Nodes own deliverables** — Kali does NOT modify node output. Reject and re-dispatch if tests fail.
3. **Oversouls bypassed for cross-boundary work** — when a wave spans both build-side (N1-N5) and run-side (N6-N10), Kali dispatches directly to nodes. Ma'at and Lilith are activated for within-boundary work.
4. **Hivemind post required** — every agent must post completion context before claiming the next task.
5. **Sequencing is serial within phase** — pillars work in parallel within the same phase, but phases execute sequentially.

---

## §12 L2.5 Synthesis Layer & Dual-Artifact Rule (NEW — 2026-08-16)

### The Problem: Execution-Model Contamination

**Validated by F821 Study (AP-L25-SYNTHESIS-STUDY-v1.0.0)**: When an execution agent (e.g., Nemotron 3 Ultra, Qwen3-1.7B) is given multiple plan documents (tactical + strategic), they:
1. **Copy instructional markers** into production code (`# <-- ADD THIS LINE`, `# CHANGE THIS`)
2. **Merge superseded documents** — implement "according to both" even when one supersedes the other
3. **Cannot resolve document hierarchy** — lack the contextual judgment to know which plan wins

**Root cause**: Execution models are literal constraint-satisfaction engines. They treat pedagogical scaffolding as artifact, and cannot distinguish "instruction to reader" from "code to write."

### The Solution: L2.5 Synthesis Layer + Dual-Artifact Rule

When a task triggers a Crucible run (L3 Frontier Review) and MULTIPLE frontier planners produce documents (e.g., Sonnet tactical + Opus strategic), the orchestrator (Kali) MUST:

1. **Invoke L2.5 Synthesis**: Dispatch a cheaper synthesizing model (DeepSeek-class) to read ALL planner outputs + execution observations
2. **Emit exactly two artifacts**:
   - **Artifact A (Cognitive Guide)**: Unified forensic analysis, teaching patterns, anti-patterns, decision records. Read by humans and the DPO extractor. **Execution agents are FORBIDDEN from reading it.**
   - **Artifact B (Machine Patch)**: Single, comment-free, unambiguous machine-executable plan. The **ONLY** document the executing agent reads.
3. **Handoff ONLY Artifact B** to the execution agent with explicit prohibition: *"Read ONLY this file. Do not read any other document in this sprint directory."*

### Mandatory Protocol for Crucible Runs

| Step | Action | Responsible |
|------|--------|-------------|
| 1 | L1 Local draft (if applicable) | Local model |
| 2 | L2 Interrogation Gate — assess blast radius | Kali |
| 3 | L3a Frontier Tactical Plan (Sonnet-class) | Tactical planner |
| 4 | L3b Frontier Strategic Guide (Opus-class) | Strategic planner |
| **5** | **L2.5 Synthesis — read ALL above + execution logs → emit Artifact A + B** | **Synthesizer (DeepSeek-class)** |
| 6 | L4 Integration — hand off Artifact B ONLY to executor | Kali |
| 7 | Execute from Artifact B only | Execution agent |
| 8 | L5 Distill → DPO extraction from Artifact A | Scribe/Verity |

### Artifact B Requirements (Machine Patch)

Artifact B MUST be:
- **Comment-free** — no `# <-- ADD THIS LINE`, `# CHANGE THIS`, `# TODO(plan)` markers
- **Conflict-free** — all planner conflicts resolved (documented in Artifact A)
- **Single-source** — no references to other documents
- **Structured** — YAML frontmatter + numbered operations (OP-01..OP-N) with exact before/after states
- **Self-contained** — includes all prohibitions, verification gates, commit contract

### Handoff Template Update

When dispatching an execution agent for a Crucible run, the handoff prompt MUST include:

```
## 🔱 CRUCIBLE EXECUTION HANDOFF

**Artifact B (Machine Patch)**: `docs/sprints/<sprint>/AGENT_EXECUTION_PLAN.md`

**PROHIBITIONS — VIOLATIONS ARE FAILURES**:
1. Do NOT read any other file in this sprint directory. Artifact B is the only source of truth.
2. Do NOT copy instructional markers into code. No comment containing "<--", "ADD", "CHANGE", or "TODO(plan)" may be written.
3. Do NOT use regex, sed, or scripted import injection. Use the edit tool only.
4. Do NOT add "# noqa" or "# type: ignore" suppressions.
5. Do NOT add a top-level import when Artifact B specifies an inline import.
6. Do NOT add an import when Artifact B specifies a call-site rename.
7. Do NOT modify any file not listed in Artifact B.

**VERIFICATION**: All gates in Artifact B must pass. Commit contract in Artifact B must be followed exactly.
```

### Token Economics Justification

| Approach | Cost | Contamination Risk |
|----------|------|-------------------|
| Multiple planners → direct to executor | High (Opus × N) | **Critical** — observed 6/6 failure modes |
| Multiple planners → L2.5 Synthesis (DeepSeek) → Artifact B → executor | Low (Opus × 2 + DeepSeek × 1) | **Zero** — Artifact B is single, clean, conflict-free |

The synthesis layer costs ~1-2% of Opus regeneration and **eliminates execution-model contamination entirely**.

### Reference Implementation

- **Study**: `docs/strategy/L2_SYNTHESIS_VALIDATION_STUDY.md`
- **Artifact A (F821)**: `docs/sprints/f821-remediation/HYBRID_STRATEGIC_GUIDE.md`
- **Artifact B (F821)**: `docs/sprints/f821-remediation/AGENT_EXECUTION_PLAN.md`
- **DPO Extractor**: `scripts/extract_dpo_pairs.py` (format-tolerant)
- **DPO Dataset**: `data/training/dpo_dataset.jsonl` (14 pairs)

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ SUBAGENT-DISPATCH ⬡ v3.0.0*

<!-- PROVENANCE-CORRECTED 2026-09-09T05:13:35Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: VERIFIED
actual_models(Tier0): nemotron-3-ultra-free, x-preview-f-free, minimax/minimax-m3:free, mimo-v2.5-free, big-pickle, gemini-3.8-flash
first_audit: 2026-09-07T03:03:09Z | updated: 2026-09-09T05:13:35Z
-->





