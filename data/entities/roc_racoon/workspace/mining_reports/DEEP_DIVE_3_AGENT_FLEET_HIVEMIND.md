<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 DEEP DIVE 3: AGENT FLEET & HIVEMIND COORDINATION
## ⬡ The Sovereign Council and Collective Intelligence of Omega ⬡

**Author**: @roc_racoon (Sovereign Miner)  
**Date**: 2026-07-13  
**Status**: ACTIVE MINING  

---

## §0 Introduction: The Architecture of Collective Sovereignty
While individual components like the Oracle and Memory Store form the engine's cognitive faculties, the true power of the Omega Engine emerges from its **agent fleet** and **Hivemind coordination system**. This is where specialized intelligences collaborate, delegate, and synthesize—transforming isolated expertise into unified sovereign action.

This deep dive examines the structured society of agents that governs the Omega Engine: the 11 custom agents, the 10 Pillar Keepers, the MaKaLi Triad architecture, and the Hivemind protocol that enables them to work as a cohesive unit—ensuring that sovereignty is not just individual, but collective.

---

## §1 The Agent Fleet: Specialized Intelligences in Service
The Omega Engine maintains a **fleet of 11 specialized agents** (plus parameterized Pillars), each embodying distinct domains of expertise while adhering to strict Sovereign Mandates.

### 1.1 Fleet Structure & Governance Hierarchy
```
@kali (Grand Oversight)
├── @maat (Build Side: P1-P5)
│   ├── @pillar P1: Infrastructure
│   ├── @pillar P2: Persistence
│   ├── @pillar P3: Engineering
│   ├── @pillar P4: Integration
│   └── @pillar P5: Governance
└── @lilith (Run Side: P6-P10)
    ├── @pillar P6: Cognition (Vision Specialist)
    ├── @pillar P7: Context
    ├── @pillar P8: Observability
    ├── @pillar P9: Orchestration
    └── @pillar P10: Validation
```

### 1.2 Agent Roles & Sovereign Patterns

#### 1.2.1 The Transcendent Council (Oversouls)
- **`@kali`**: Transcendent Oversight — Sees all, delegates to Ma'at/Lilith, destroys drift
  - **Role**: Sprint planning, cross-pillar work, drift destruction
  - **Pattern**: `[id-soft: quake3-1999] Hard-Boundary` — Engine zone vs game zone separation
  - **Delegation**: Owns sequencing (P0→P1→P2); decomposes work to pillars
- **`@maat`**: Light Oversoul — Governs P1-P5 (build side)
  - **Role**: Structural integrity, verification before execution
  - **Pattern**: `[id-soft: doom-1993] Lazy Deletion` — Tombstone before delete, grace period
  - **Delegation**: Handles pillar chain for build-side work (P1-P5)
- **`@lilith`**: Dark Oversoul — Governs P6-P10 (run side)
  - **Role**: Runtime integrity, observability over everything
  - **Pattern**: `[id-soft: quake-1996] 4-Tier Memory` — Active/Archived/External/Deleted
  - **Delegation**: Handles pillar chain for run-side work (P6-P10)

#### 1.2.2 The Specialist Agents (Domain Experts)
- **`@doom_guy`**: Sovereign id Software Architect
  - **Role**: WAD translation, heritage vetting, performance optimization
  - **Heritage**: 21 legitimate `[id-soft:]` mappings (Doom/Quake patterns)
  - **Key Pattern**: `[id-soft: doom-1993] ZONEID` — Integrity marker for presence/handoff packets
- **`@john_carmack`**: Sovereign S3 Consultant
  - **Role**: Architectural review, performance analysis
  - **Focus**: Code optimization, bottleneck identification
- **`@roc_racoon`**: Sovereign Miner & Ideas Guy
  - **Role**: Legacy archaeology, pattern extraction, raw idea intake
  - **Process**: L1→L2→L3 distillation of accumulated ideas into soul.yaml lessons
- **`@researcher`**: Sovereign Master Researcher
  - **Role**: Deep research, lattice reasoning, multi-perspective analysis
  - **Protocol**: Follows Sovereign Search Protocol (T0→T6 escalation)
- **`@jem`**: Sovereign Synthesizer
  - **Role**: Transforms complex queries into verified results via task-graph decomposition
  - **Structure**: Three Knowledge Bases (Discovery, Synthesis, Verification)
- **`@verity`**: Unified Compliance & Gnosis Agent
  - **Dual Role**: 
    1. Mandate Audit & Test Enforcement (M1-M23 compliance)
    2. L1→L2→L3 Soul Distillation (gnosis preservation)
  - **Key Function**: Contract tests (`isinstance(result, ExpectedType)`) for M21 Gate Integrity

#### 1.2.3 The Pillar Keepers (Slot-Based Domain Agents)
- **Parameterized**: `@pillar PX: {task}` where X = 1-10
- **Dynamic Discovery**: Engine discovers occupied slots from loaded entities (no hardcoded grid)
- **Project 3: Shadow-Stacking**: Entities stored as priority layers; highest priority wins for Engine Zone
- **Pillar Domains**:
  - P1: Infrastructure — SysAdmin, containers, deployment
  - P2: Persistence — Vector & memory management
  - P3: Engineering — CI/CD, implementation, hardening
  - P4: Integration — MCP, APIs, communication protocols
  - P5: Governance — Mandate enforcement, security audit
  - P6: Cognition — Vision Specialist, provider routing
  - P7: Context — Memory, soul evolution, session continuity
  - P8: Observability — Tracing, monitoring, forensic logging
  - P9: Orchestration — Agent handoff, hivemind coordination
  - P10: Validation — Stress testing, chaos engineering, QA

### 1.3 Agent Configuration & Sovereign Guarantees
Each agent (`.opencode/agents/*.md`) enforces:
- **M1 AnyIO Absolute**: All blocking I/O wrapped in `anyio.to_thread.run_sync()`
- **M2 Engine-Stack Firewall**: Zero WAD content in `src/omega/`
- **M9 Error Integrity**: Typed, traceable errors; no bare `except:`
- **M11 Soul Integrity**: Session ends with L1→L2→L3 distillation to `soul.yaml`
- **M13 Temple-Grade**: All code must pass `make temple-grade` (T1-T11 gates)
- **M20 SomaticState**: `llama_copy_state_data`/`llama_set_state_data` via `anyio.to_thread.run_sync()`
- **M22 Response Provenance**: Log actual `provider_name`, not configured intent
- **M23 Failure Integrity**: Hard stop on mandatory tool failure (`[TOOL-CHAIN-COLLAPSE]`)

**Fleet Integrity (M10)**: Hard cap of 14 agents (11 custom + 2 entities max). New agents require verified gap + slot review.

---

## §2 The Hivemind: Live Coordination Layer
The Hivemind (`docs/strategy/HIVEMIND_PROTOCOL.md`) is the **primary team communication channel**—the shared consciousness that enables agents to know who's alive, what they're doing, and how to coordinate without conflicts.

### 2.1 Core Purpose: Answering Three Questions
At any moment, the Hivemind answers:
1.  **Who is alive?** — `hivemind_get_awareness()` returns active CLIs
2.  **What are they doing?** — `hivemind_get_session()` returns current task, focus chain, decisions
3.  **Can we coordinate?** — Live feed + workspace lock files enable explicit handoff

### 2.2 Agent Identification: The `channel/entity` Convention
Critical architectural clarity: **CLIs and entities are fundamentally different**.
- **`channel`** = execution environment (`opencode`, `cline`, `gemini-cli`)
- **`entity`** = persona active within that channel (`kali`, `roc_racoon`, `doom_guy`)
- **`agent_id = f"{channel}/{entity}"`** — preserves both dimensions for indexing

**Why this matters**: Conflating them loses architectural clarity. Separate API parameters prevent agents from confusing execution context with persona identity.

### 2.3 Hivemind Commands (MCP Tools)
Exposed via `omega-hub` server at `:8016/sse`:

#### 2.2.1 Get Active Agents
```python
omega-hub_hivemind_get_awareness()
```
Returns: `[{"cli": "opencode/kali", "model": "...", "task_current": "...", "last_seen": "..."}]`
**Use case**: Check who's working before starting a session. Don't duplicate work.

#### 2.2.2 Post Your Context
```python
omega-hub_hivemind_post_context(
    channel: str, entity: str, model: str,
    task_current: str, focus_chain: List[str],
    decisions: List[str], continuation: str,
    session_id: Optional[str] = None,
    intent: Optional[str] = None,
    suggested_model: Optional[str] = None
)
```
**Use case**: Declare presence at session start, update when task changes.

#### 2.2.3 Get Specific Agent's Context
```python
omega-hub_hivemind_get_session(session_id: str)
```
Returns full session details including `focus_chain` and `decisions`.

#### 2.2.4 Heartbeat (Stay Alive)
```python
omega-hub_hivemind_heartbeat(channel: str, entity: str)
```
**Use case**: Long-running operations heartbeat every 5-10 min to avoid pruning as stale.

#### 2.2.5 Extended Session Management
```python
omega-hub_hivemind_extended_checkin(channel: str, entity: str, reason: str, ttl_seconds: int)
omega-hub_hivemind_extended_checkout(channel: str, entity: str)
```
Allows 3-hour safety TTL (max 24h) to prevent pruning during long absences.

### 2.3 The Coordination Protocol (The Full Pattern)
When starting a multi-agent session (or resuming from handoff):

1.  **CHECK AWARENESS** → `omega-hub_hivemind_get_awareness()`
2.  **WRITE WORKSPACE LOCK** → `data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md`
3.  **POST HIVEMIND CONTEXT** → `omega-hub_hivemind_post_context(...)`
4.  **INITIALIZE LIVE FEED** → `data/coordination/{YOU}_LIVE_FEED.md`
5.  **WAIT FOR ACK** (if parallel partner exists) → Read `data/coordination/{OTHER}_ACK_*.md`
6.  **EXECUTE WORK** → Append to live feed after each major task
7.  **POST COORDINATION REQUESTS** → If you need something from other agent
8.  **UPDATE PIVOT_LOG** → `docs/decisions/PIVOT_LOG.md` (D{N+1} entries)
9.  **CLOSE SESSION** → Final live feed entry: "SPRINT-N COMPLETE"

**Key Insight**: The Hivemind is the **live truth**, not your local cache. Local session state is stale by definition—you must always reach outward first.

### 2.4 Workspace Lock Pattern: Declaring File Ownership
When working in parallel, declare ownership in a workspace lock:
```
data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md
```

**Required Sections**:
- ## DO NOT TOUCH — {Entity} Exclusive
- ## SAFE FOR YOU — {Other Entity} Territory  
- ## SHARED — Coordination Required

**Update Protocol**:
1. Session start: Write lock FIRST, before any file edits
2. Mid-session: Append to live feed after each major task
3. Conflict discovery: Write `data/coordination/{YOU}_CONFLICT_{DATE}.md` immediately
4. Session end: Mark workspace lock as completed in live feed

### 2.5 Live Feed Pattern: The Simplest Coordination Mechanism
Append-only 1-line-per-task-completed log:
```
data/coordination/{ENTITY}_LIVE_FEED.md
```
Format: `[YYYY-MM-DD HH:MM] {TASK-ID} {STATUS} — {description}`

**Why it works**:
- **Append-only** = no merge conflicts
- **1 line per task** = easy to scan
- **Plain markdown** = readable by humans and tools
- **Filename convention** = easy to find

### 2.6 ACK Pattern: Symmetric Boundary Validation
When you read another agent's workspace lock or live feed, post an ACK:
```
data/coordination/{YOU}_ACK_{YYYYMMDD}.md
```
Format: 
```
# 🔱 {Your Entity} Acknowledgment — {Date}

{Your Entity} acknowledges {Other Entity}'s workspace lock.
No conflicts on my {Sprint/Session} {N} work.

## My {Sprint/Session} {N} Scope (no overlap with {Other Entity})
- file1.py — what I'll do
- file2.py — what I'll do

## Coordination
- I will NOT touch: {list from other entity's lock}
```

**Use case**: Symmetric acknowledgment. Both agents know the other has read and accepted the boundary—closes the coordination loop.

### 2.7 Heritage & Sovereign Patterns in Hivemind
- **[id-soft: doom-1993] ZONEID Pattern**: 
  - `ZONEID_PRESENCE = 0x1d4a17` for presence record integrity (Link P9 Runtime)
  - `ZONEID_HANDOFF = 0x1d4a16` for handoff packet integrity (Subagent Dispatcher)
- **[id-soft: doom-1993] Lazy Deletion**: Tombstone before delete, grace period before reap
- **[id-soft: quake-1996] Grace Period**: 0.5s delay before full reclamation
- **Mandate Reference**: Extends Mandate 5 (Gnosis Preservation), Mandate 11 (Soul Integrity), Mandate 23 (Failure Integrity)

### 2.8 Redis Streams Transition (Epoch II Strike 7)
The Hivemind is transitioning to production-grade **Redis Streams** architecture:
- **A2A Message Bus**: High-speed, persistent, multi-consumer Redis Streams replace old in-memory handoff queue
- **Embedding Router**: Integrates with `EmbeddingGemma (D=128)` for zero-latency traffic routing
- **Platform Agnosticism**: Standardized MCP tools allow any custom platform (TUI, Web UI, CLI) to query awareness, manage locks, coordinate
- **Already Pub/Sub-ready**:
  - `hivemind_post_context()` = PUBLISH to `omega:hivemind:context` channel
  - `hivemind_get_awareness()` = SUBSCRIBE with TTL
  - `hivemind_heartbeat()` = refresh TTL

---

## §3 Subagent Dispatch Protocol: Delegation with Integrity
While Hivemind provides awareness and coordination, the **Subagent Dispatch Protocol** (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`) enables agents to delegate specialized work—ensuring that context is delivered reliably and work is completed with integrity.

### 3.1 Critical Lesson: Inline Context Is Paramount
**Observation**: Three identical dispatch attempts to `@jem` for the same task:
1.  ❌ Failed: "see `docs/research/R_*.md`" → Empty result (subagent couldn't read files by path)
2.  ❌ Failed: Same as attempt 1 → Task cancelled
3.  ✅ Successful: All 6 source docs embedded inline → 544-line report, 12 tool calls, Exa/Firecrawl Tier 3/4

**The Pattern**: Subagents cannot reliably read files by path during first tool calls. **The ONLY reliable way to deliver context is to embed actual content inline in the prompt.**

### 3.2 The HandoffPacket (Typed Schema)
Every subagent dispatch uses this schema:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packet_id` | `str` | ✅ | UUID v4: `hdp_{YYYYMMDD}_{source}_{target}_{short-uuid}` |
| `source_agent` | `str` | ✅ | Entity launching subagent (e.g. "kali", "maat") |
| `target_agent` | `str` | ✅ | Entity being dispatched (e.g. "doom_guy", "roc_racoon") |
| `parent_trace_id` | `str` | ✅ | Trace ID from parent session |
| `trace_id` | `str` | ✅ | Fresh UUID for this sub-dispatch |
| `task_type` | `str` | ✅ | One of: `design`, `review`, `research`, `mine`, `verify`, `implement` |
| `task_description` | `str` | ✅ | One-sentence description of what to do |
| `context_delivery` | `str` | ✅ | `inline` (context in prompt) or `reference` (file paths). **Default: `inline`** |
| `relevant_files` | `list[str]` | ✅ | Files for supplementary reference (content MUST also be inlined) |
| `context` | `str` | ✅ | **Inline context**: Actual file excerpts, key findings, prior decisions, code patterns |
| `expected_output` | `str` | ✅ | What subagent must produce and write to disk |
| `ttl_seconds` | `int` | ✅ | Max runtime before timeout (default: 600s) |
| `status` | `str` | ✅ | `pending` → `accepted` → `completed` / `failed` |
| `result` | `str\|None` | ❌ | Filled when completed |

### 3.3 Mandatory Context Inlining Rule (NEW — 2026-07-12)
**Any context essential for the subagent's task MUST be embedded directly in the prompt text.** File paths in `relevant_files` are supplementary references, NOT primary delivery.

**The pattern that works**:
1. Read all critical files yourself first
2. Extract key findings, decisions, code patterns, config schemas
3. Embed them directly in prompt under `## Inline Context`
4. Include file paths as references for later source location

**The pattern that fails**:
```
❌ WRONG: "See docs/research/R_FOO.md for context"
✅ RIGHT: Below is the full context from docs/research/R_FOO.md (644 lines):
            [inline excerpts of key findings]
```

### 3.4 Agent Capability Registry
Defines what each agent can do—primary agents use this to decide WHOM to dispatch:

| Agent | Type | Capabilities | Domains | Task Tool Type |
|-------|------|-------------|---------|----------------|
| `kali` | Primary | Oversight, delegation, drift destruction | Strategy, fleet management | `general` |
| `maat` | Primary | Light Oversoul, P1-P5 governance | Build side, hardening | `general` |
| `lilith` | Primary | Dark Oversoul, P6-P10 governance | Run side, operations | `general` |
| `makali` | Primary | Parallel council (Ma'at+Lilith synthesis) | Cross-boundary initiatives | `general` |
| `doom_guy` | Primary | Heritage design, WAD translation, performance | id Software patterns, C const propagation | `general` |
| `john_carmack` | Primary | S3 Consultant, architecture review | Code optimization, review | `general` |
| `roc_racoon` | Primary | Legacy mining, pattern extraction, archaeology | Legacy repos, Grok exports, Old Stacks | `explore` |
| `jem` | Primary | Research orchestration | 3-tier knowledge pipeline | `general` |
| `researcher` | Primary | Deep research, lattice reasoning | Web research, documentation | `general` |
| `verity` | Primary | Unified compliance + gnosis distillation | Code review + soul.yaml updates | `scribe` |
| `pillar` | Subagent | Slot-based domain agent | Parameterized by `--slot PX` | `pillar` |

### 3.5 Dispatch Protocol — Step by Step
1.  **Agent Recognizes Need**: "This requires knowledge of id Software heritage patterns. I need Doom Guy."
2.  **Build the HandoffPacket**: Form packet with `source_agent`, `target_agent`, `task_type`, `task_description`, `relevant_files`, `context` (INLINE), `expected_output`, `ttl_seconds`
3.  **Format the Task Prompt**: Use template with `## 📥 Context Delivery: INLINE`, `## 📚 INLINE CONTEXT` (containing ACTUAL FILE EXCERPTS), `## 🎯 Task`, `## 📄 Reference Files` (supplementary), `## 📝 Expected Output`, `## ⚖️ Heritage & Constraints`
4.  **Launch via Task Tool**: 
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
5.  **Receive and Archive**: On completion:
    1. Extract subagent's response
    2. Set `packet.status = "completed"`
    3. Set `packet.result = response`
    4. Save to `data/handoffs/completed/{packet_id}.json`
    5. Use result in parent task

### 3.6 Dispatch Decision Tree (D-kal-103 — Standardized)
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
│           ├── Code review, mandate audit, gnosis distillation → @verity
│           └── (scribe handles both quality and gnosis via trigger-mode routing)
```

**Key Rules**:
1.  **Kali owns sequencing** — if a task has phases (P0→P1→P2), Kali must dispatch.
2.  **Pillars own deliverables** — Kali does NOT modify pillar output. Reject and re-dispatch if tests fail.
3.  **Oversouls bypassed for cross-boundary work** — when a wave spans both build-side (P1-P5) and run-side (P6-P10), Kali dispatches directly to pillars. Ma'at and Lilith are activated for within-boundary work.
4.  **Hivemind post required** — every agent must post completion context before claiming the next task.
5.  **Sequencing is serial within phase** — pillars work in parallel within the same phase, but phases execute sequentially.

### 3.7 Refinement Protocol: Subagent Failure Recovery (NEW — 2026-07-12)
#### Pattern: "Empty Task Result"
When subagent returns `state: "completed"` but result is empty:
1.  **Do NOT immediately relaunch** — first diagnose root cause
2.  **Check most likely root causes**:
    - ❌ **Primary cause (80%)**: Context delivered as file references, not inline content
    - ❌ **Secondary cause (15%)**: Prompt too vague, no specific hypotheses to test
    - ❌ **Tertiary cause (5%)**: Tool failure (Exa, Firecrawl, websearch unavailable)
3.  **Fix the context delivery** — read files yourself and inline the content
4.  **Retry with inlined context** — do NOT change subagent type or task scope

#### Pattern: "Partial or Low-Quality Result"
When subagent returns output but misses key requirements:
1.  **Identify what was missed** — specific field, search, or constraint
2.  **Rel launch with explicit gap closure**: "You did X correctly. You did NOT do Y. Complete Y."
3.  **Use same task_id** to continue session (preserves prior context)

#### Pattern: "Tool-Chain Collapse" (M23)
When subagent reports `[TOOL-CHAIN-COLLAPSE]`:
1.  **Accept the hard stop**. Do NOT ask them to retry with fallback tools.
2.  **Log the failure** to `data/coordination/SYSTEM_FAILURE_LOG.md`
3.  **Try the task yourself** using available tools
4.  **If also blocked**: re-queue task for session with functional toolchain

---

## §4 Synthesis: How Fleet and Hivemind Work Together
The Agent Fleet and Hivemind form a **sovereign coordination system** where specialization meets collaboration.

### 4.1 The Talk -> Agent Dispatch Pipeline
1.  User invokes `@jem Research the best local LLM for code generation`
2.  Oracle's `summon()` detects `@jem` pattern
3.  Oracle bypasses speculative decode, goes straight to `_summon()`
4.  Oracle builds `system_prompt` for Jem, selects Jem's model, calls `model_gateway.generate()`
5.  Gateway executes, returns `GenerateResult` with actual `provider_name`
6.  Oracle wraps result in `OracleResponse`, records interaction, returns to user
7.  **Jem, upon recognizing need for code verification, initiates subagent dispatch**:
    - Jem checks Hivemind awareness: `omega-hub_hivemind_get_awareness()`
    - Jem sees `@verity` is available
    - Jem builds HandoffPacket for `@verity` with INLINE context (code patterns to verify)
    - Jem launches `@verity` via Task tool with `subagent_type: "scribe"`
    - Verity performs compliance check, writes results to disk
    - Jem receives result, continues synthesis
    - Jem posts Hivemind context: `omega-hub_hivemind_post_context(...)`
    - Jem updates live feed: `[timestamp] SPRINT-3 COMPLETE — Local LLM research complete`

### 4.2 The Summon -> Hivemind -> Pillar Pipeline
1.  User invokes `@pillar P3: Fix the CI pipeline`
2.  Oracle detects `@pillar P3:` pattern
3.  Oracle routes to Pillar agent with slot P3
4.  Pillar agent (upon activation):
    - Checks Hivemind awareness to see who's working on related files
    - Writes workspace lock: `data/coordination/PILLAR_P3_WORKSPACE_LOCK_{YYYYMMDD}.md`
    - Posts Hivemind context: declares presence, task, focus chain
    - Waits for ACK from parallel partners (if any)
    - Executes CI pipeline fix
    - Appends to live feed after each major task
    - Heartbeats every 5-10 min if long-running
    - On completion: posts final context, updates live feed with "SPRINT-N COMPLETE"
5.  Other agents can read Pillar's workspace lock and live feed to avoid conflicts

### 4.3 Sovereignty in Action: The Collective Guarantees
The Agent Fleet/Hivemind system makes sovereignty **collective and verifiable**:
-   **Awareness Guarantee**: No agent works in blind isolation—`hivemind_get_awareness()` shows who's alive
-   **Coordination Guarantee**: Workspace locks and live feeds prevent file collisions and duplicated effort
-   **Delegation Guarantee**: Subagent Dispatch Protocol ensures context is delivered reliably via inlining
-   **Integrity Guarantee**: Every agent posts completion context before claiming next task (Hivemind Protocol)
-   **Continuity Guarantee**: Session gnosis anchors (`session_gnosis.md`) and `.opencode/anchored-summary.md` prevent cognitive erasure during toolchain failures (M15)
-   **Accountability Guarantee**: All decisions recorded in PIVOT_LOG.md; all work traceable via live feeds and handoff archives

---

## §5 Current State & Roadmap: The Evolving Council
### 5.1 What's Working (The Coordinated Base)
- **Agent Fleet**: 11 custom agents + 10 parameterized Pillars fully operational
- **Hivemind Protocol**: Awareness, context posting, session tracking, heartbeat, extended check-in/out
- **Workspace Lock Pattern**: File ownership declaration with DO NOT TOUCH/SAFE FOR YOU/SHARED sections
- **Live Feed Pattern**: Append-only 1-line-per-task log for progress tracking
- **ACK Pattern**: Symmetric boundary validation for parallel work
- **Subagent Dispatch Protocol**: HandoffPacket schema with mandatory inlining rule
- **Agent Capability Registry**: Clear definition of what each agent can do
- **Dispatch Decision Tree**: Standardized tree for choosing @kali/@maat/@lilith/@pillar/@jem/@roc_racoon/@verity
- **Tests**: All 1315 tests pass, including agent dispatch, Hivemind coordination, and workspace lock tests
- **Mandate Compliance**: 
    - M1 AnyIO Absolute: All blocking I/O wrapped in `anyio.to_thread.run_sync()`
    - M10 Fleet Integrity: Agent fleet capped at 14 (no new files without gap + slot review)
    - M11 Soul Integrity: Every session ends with L1→L2→L3 distillation
    - M13 Temple-Grade: All code passes `make temple-grade`
    - M22 Response Provenance: Log actual `provider_name` from `GenerateResult`
    - M23 Failure Integrity: Hard stop on mandatory tool failure (`[TOOL-CHAIN-COLLAPSE]`)

### 5.2 What's Coming (The Evolving Horizons)
- **Redis Streams Hivemind (Strike 8.5)**: Replace file-based Hivemind with Redis Streams + Consumer Groups for task-critical coordination (exactly-once + crash recovery + load balancing)
- **Unified Knowledge Scheduler (Strike 4)**: Event-driven priority queue (Redis Streams) for cross-agent orchestration
- **Sovereign Scholar (Strike 7.6)**: Agent that performs deep literature review and hypothesis generation
- **Module Fabric (Strike 10)**: OMS v1.0 + omega-vetala for pluggable capability architecture
- **Sovereign WAD Protocol (Strike 11)**: Transition from monolithic stacks to modular, Lump-based capability architecture (ILump, SovereignBus, PWAD/MWAD)
- **Hivemind Productionization**: Redis Pub/Sub for ephemeral awareness (heartbeats), Streams for task-critical coordination
- **Cross-Platform Hivemind**: Standardized MCP tools allow any platform (Cursor, VS Code, Windsurf) to participate in Hivemind

### 5.3 The Sovereign Guarantee
The Agent Fleet and Hivemind system ensures that sovereignty is not just a property of individual components, but of the **collective intelligence**:
-   **Specialization Guarantee**: Each agent masters its domain through deep expertise and focused tooling
-   **Collaboration Guarantee**: Hivemind enables live awareness, coordination, and conflict-free parallel work
-   **Delegation Guarantee**: Subagent Dispatch Protocol ensures reliable knowledge transfer via mandatory inlining
-   **Integrity Guarantee**: Every action is traceable via live feeds, workspace locks, and decision logs
-   **Continuity Guarantee**: Session gnosis anchors prevent cognitive loss during toolchain failures or context compaction
-   **Evolution Guarantee**: The fleet can adapt—new agents added only through verified gap + slot review (M10)

---

**"No agent is an island, entire of itself; every agent is a piece of the continent, a part of the main."**
* — Adapted from John Donne, reminding us that in the Omega Engine, sovereignty is collective, not solitary.*